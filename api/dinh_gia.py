"""Định giá bằng các mô hình đã huấn luyện trong notebook (models/*.joblib, models/*.json).

- Nhà phố: Random Forest (mô hình cuối, Phần A) + khoảng 80% theo nhóm + giải thích đóng góp theo đường đi trên cây.
- Căn hộ: mô hình đầy đủ của notebook căn hộ (.joblib) + khoảng 80% theo phân khúc.
- Giá thuê: giá × tỷ suất cho thuê trung vị (phường / dự án) trong models/gia_thue_web.json.
Cách dựng hàng đặc trưng giống hệt hàm du_doan_gia / du_doan_gia_can_ho trong notebook."""
import datetime as dt
import hashlib
import io
import json
import os
import shutil
import sys
import threading
import time
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from scipy import sparse

# Thư mục chứa models/ và dataset/ (đặt PHH_GOC để chạy trên một bộ tệp khác, ví dụ khi kiểm thử)
GOC = Path(os.environ.get("PHH_GOC") or Path(__file__).resolve().parent.parent)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))   # lớp mô hình (MoHinhGia...) để đọc .joblib
from mo_hinh_gia import khong_dau, nhom_khoang, phan_vi_cho, ten_du_an, trich_dac_trung_chu  # noqa: E402

MODELS, PROC = GOC / "models", GOC / "dataset" / "processed"
TRUNG_TAM_TDM = (10.9805, 106.6520)           # chợ Thủ Dầu Một (như notebook)
# Nhóm đặc trưng để giải thích (như notebook nhà phố, Bước 12)
NHOM_GT = {
    "Vị trí (tọa độ, khoảng cách trung tâm)": ["lat", "lon", "kc_trung_tam_km"],
    "Diện tích và kích thước lô": ["log_dt", "ngang", "dai"],
    "Tầng, diện tích sàn, phòng, nội thất": ["so_tang", "dt_san", "ty_le_san", "phong_ngu", "so_wc", "noi_that", "t_cap4", "t_nha_moi", "t_nha_nat", "t_thang_may", "t_biet_thu"],
    "Lối vào (mặt tiền, hẻm)": ["mat_tien_duong", "cap_loi_vao", "hem_rong", "t_hem_xe_hoi", "t_hem_nho", "t_mat_tien", "t_goc", "t_kinh_doanh"],
    "Pháp lý": ["so_chung", "t_so_rieng", "t_so_chung", "t_chua_hc"],
}


# ======================= Bộ tệp được công bố (models/phien_ban.json) =======================
# Notebook và build_site ghi các tệp ở những bước khác nhau. API KHÔNG đọc thẳng từng tệp khi chúng đổi, mà chỉ chuyển sang
# bộ mới khi pipeline CÔNG BỐ bản kê (sau khi mọi tệp đã ghi xong): bản kê liệt kê SHA-256 của từng tệp API dùng.
# Khi nạp: mỗi tệp đọc đúng 1 lần (bytes), so mã băm với bản kê rồi mới giải mã, thử định giá 1 căn mẫu, rồi mới thay bộ cũ.
# Lỗi (thiếu tệp, tệp hỏng, mã băm lệch vì đang ghi dở) -> GIỮ bộ cũ đang phục vụ và báo lỗi qua /health.
# Công bố = CHÉP các tệp đã kiểm vào models/cong_bo/<mã bộ>/ rồi mới ghi bản kê trỏ tới đó: pipeline ghi đè tệp làm việc
# (hoặc chạy lỗi giữa chừng) thì API khởi động lại vẫn nạp được bộ đã công bố. Giữ bộ hiện tại + bộ trước đó.
# Tệp làm việc (models/*.joblib, du_lieu_web.json..., do notebook ghi) KHÔNG BAO GIỜ được phục vụ trực tiếp, trừ khi bật
# tường minh PHH_UNG_VIEN=1 (kiểm thử bộ ỨNG VIÊN trước khi công bố). Thiếu bản kê cục bộ (clone mới) -> bộ BÀN GIAO
# models/ban_giao/ (có trong git, đã xác thực, pipeline không ghi vào; cập nhật bằng: python api/dinh_gia.py --ban-giao).
MANIFEST = "models/phien_ban.json"
THU_MUC_CONG_BO = "models/cong_bo"
DAU_CONG_BO = "da_cong_bo.json"      # dấu trong models/cong_bo/<mã>/: bộ này ĐÃ được công bố (không phải ứng viên công bố lỗi)
BAN_GIAO = "models/ban_giao"
TEP_BAT_BUOC = ["models/mo_hinh_gia_nha.joblib", "models/du_lieu_web.json", "models/danh_gia_mo_hinh.json",
                "dataset/processed/nha_da_xu_ly.csv"]                  # CSV nhà phố: API dùng để suy tọa độ theo đường / phường
TEP_TUY_CHON = ["models/mo_hinh_gia_can_ho.joblib", "dataset/processed/can_ho_da_xu_ly.csv",
                "models/danh_gia_mo_hinh_can_ho.json", "models/tro_ly_y_dinh.joblib"]   # phần mở rộng: có thì nạp
_sha = lambda b: hashlib.sha256(b).hexdigest()


def tao_ban_ke(goc=None):
    """Bản kê của bộ tệp hiện có trên đĩa (pipeline gọi sau khi sinh xong). Thiếu tệp bắt buộc -> FileNotFoundError."""
    goc = Path(goc or GOC)
    thieu = [t for t in TEP_BAT_BUOC if not (goc / t).exists()]
    if thieu:
        raise FileNotFoundError(f"thiếu tệp bắt buộc: {thieu}")
    tep = {t: _sha((goc / t).read_bytes()) for t in TEP_BAT_BUOC + [t for t in TEP_TUY_CHON if (goc / t).exists()]}
    return {"id": _sha(json.dumps(tep, sort_keys=True).encode())[:12], "tep": tep,
            "cong_bo_luc": dt.datetime.now().isoformat(timespec="seconds")}


def cong_bo(goc=None, kiem=True):
    """Chép bộ tệp làm việc vào models/cong_bo/<mã>/, (kiem=True) nạp thử ĐÚNG bản chép đó như API sẽ nạp, rồi ghi bản kê
    NGUYÊN TỬ (tệp tạm + os.replace). Nạp thử lỗi -> LoiNapBo, bản kê đang phục vụ giữ nguyên.
    kiem=False chỉ dùng trong kiểm thử để mô phỏng một bộ hỏng lọt qua công bố."""
    goc = Path(goc or GOC)
    bk = tao_ban_ke(goc)
    dich = goc / THU_MUC_CONG_BO / bk["id"]
    if not dich.exists():
        tam = dich.with_name(bk["id"] + ".tam")
        shutil.rmtree(tam, ignore_errors=True)
        for t, h in bk["tep"].items():
            b = (goc / t).read_bytes()
            if _sha(b) != h:
                raise LoiNapBo(f"{t} đổi trong lúc công bố, chạy lại bước cong_bo")
            (tam / t).parent.mkdir(parents=True, exist_ok=True)
            (tam / t).write_bytes(b)
        os.replace(tam, dich)
    bk["thu_muc"] = f"{THU_MUC_CONG_BO}/{bk['id']}"
    if kiem:
        try:
            _nap_bo(bk, goc)
        except LoiNapBo:
            raise
        except Exception as e:                           # tệp không giải mã được (JSON/joblib/CSV hỏng)
            raise LoiNapBo(f"bộ tệp không nạp được ({type(e).__name__}: {e})") from e
    dau = _cac_dau(goc)                              # các bộ ĐÃ công bố, mới nhất trước (nguồn duy nhất cho phục hồi)
    bk["cong_bo_ns"] = max([time.time_ns()] + [d["cong_bo_ns"] + 1 for d in dau if isinstance(d.get("cong_bo_ns"), int)])
    _ghi_nguyen_tu(goc / MANIFEST, bk)                  # ĐIỂM CAM KẾT: lỗi trước/tại đây -> chưa công bố, không có dấu mới
    try:
        _ghi_nguyen_tu(dich / DAU_CONG_BO, bk)          # bằng chứng phục hồi chỉ ghi SAU khi bản kê đã trỏ tới bộ này
    except OSError as e:
        raise LoiNapBo(f"bản kê đã trỏ tới bộ {bk['id']} nhưng chưa ghi được dấu phục hồi ({e}); "
                       "chạy lại: python api/dinh_gia.py --cong-bo") from e
    giu = {bk["id"]} | ({dau[0]["id"]} if dau else set())   # giữ bộ vừa công bố + bộ công bố trước đó
    for d in (goc / THU_MUC_CONG_BO).iterdir():
        if d.name not in giu:
            shutil.rmtree(d, ignore_errors=True)
    return bk


def _ghi_nguyen_tu(f, du_lieu):
    tam = f.with_name(f.name + ".tam")
    tam.write_text(json.dumps(du_lieu, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tam, f)


def _cac_dau(goc=None):
    """Bản kê của các bộ ĐÃ công bố (dấu da_cong_bo.json, chỉ ghi sau điểm cam kết), mới nhất trước theo cong_bo_ns
    (số tăng ngặt; dấu kiểu cũ chưa có thì xếp sau, theo cong_bo_luc). Dấu hỏng / không phải object -> bỏ qua."""
    ds = []
    thu_muc = Path(goc or GOC) / THU_MUC_CONG_BO
    for d in (thu_muc.iterdir() if thu_muc.exists() else []):
        try:
            bk = json.loads((d / DAU_CONG_BO).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(bk, dict) and bk.get("id") == d.name:
            ds.append(bk)
    return sorted(ds, key=lambda b: (b.get("cong_bo_ns") if isinstance(b.get("cong_bo_ns"), int) else 0,
                                     str(b.get("cong_bo_luc") or "")), reverse=True)


def tao_ban_giao(goc=None):
    """Đưa bộ ĐANG công bố (models/phien_ban.json) thành bộ bàn giao models/ban_giao/ (commit vào git): clone mới chạy
    docker compose / uvicorn là dùng được ngay. Nạp thử trước, thay thư mục nguyên tử; lỗi -> giữ bộ bàn giao cũ."""
    goc = Path(goc or GOC)
    bk = json.loads((goc / MANIFEST).read_text(encoding="utf-8"))
    nguon, dich = goc / bk.get("thu_muc", ""), goc / BAN_GIAO
    tam, cu = dich.with_name("ban_giao.tam"), dich.with_name("ban_giao.cu")
    shutil.rmtree(tam, ignore_errors=True); shutil.rmtree(cu, ignore_errors=True)
    for t, h in bk["tep"].items():
        b = (nguon / t).read_bytes()
        if _sha(b) != h:
            raise LoiNapBo(f"{t}: bộ đang công bố không khớp mã băm")
        (tam / t).parent.mkdir(parents=True, exist_ok=True)
        (tam / t).write_bytes(b)
    moi = {**bk, "thu_muc": BAN_GIAO}
    try:
        _nap_bo({**moi, "thu_muc": "models/ban_giao.tam"}, goc)
    except LoiNapBo:
        raise
    except Exception as e:
        raise LoiNapBo(f"bộ bàn giao không nạp được ({type(e).__name__}: {e})") from e
    (tam / "phien_ban.json").write_text(json.dumps(moi, ensure_ascii=False, indent=1), encoding="utf-8")
    if dich.exists():
        os.replace(dich, cu)
    os.replace(tam, dich)
    shutil.rmtree(cu, ignore_errors=True)
    return moi


class LoiNapBo(Exception):
    pass


def _nap_bo(bk, goc=None):
    tep = bk.get("tep") or {}
    nen = Path(goc or GOC) / bk.get("thu_muc", "")        # bản kê cũ (không có thu_muc) -> đọc tệp làm việc
    for t in TEP_BAT_BUOC:
        if t not in tep:
            raise LoiNapBo(f"bản kê thiếu tệp bắt buộc {t}")

    def doc(t):
        f = nen / t
        if not f.exists():
            raise LoiNapBo(f"{t}: không có trên đĩa")
        b = f.read_bytes()
        if _sha(b) != tep[t]:
            raise LoiNapBo(f"{t}: mã băm khác bản kê (tệp đang ghi dở hoặc đã đổi sau khi công bố)")
        return b

    goi = joblib.load(io.BytesIO(doc("models/mo_hinh_gia_nha.joblib")))
    df = pd.read_csv(io.BytesIO(doc("dataset/processed/nha_da_xu_ly.csv")), low_memory=False)
    bo = {"id": bk["id"], "cong_bo_luc": bk.get("cong_bo_luc"), "tep": {t: h[:12] for t, h in tep.items()},
          "web": json.loads(doc("models/du_lieu_web.json")), "danh_gia": json.loads(doc("models/danh_gia_mo_hinh.json")),
          "nha": (goi, df[df["toa_do_rieng"] == 1].groupby(["quan", "duong"])[["lat", "lon"]].median(),
                  df.dropna(subset=["lat"]).groupby(["quan", "phuong"])[["lat", "lon"]].median()),
          "can_ho": None, "danh_gia_can_ho": None, "tro_ly": None}
    if "models/mo_hinh_gia_can_ho.joblib" in tep and "dataset/processed/can_ho_da_xu_ly.csv" in tep:
        g = joblib.load(io.BytesIO(doc("models/mo_hinh_gia_can_ho.joblib")))
        d = pd.read_csv(io.BytesIO(doc("dataset/processed/can_ho_da_xu_ly.csv")), low_memory=False)
        bo["can_ho"] = (g, d, d.groupby("du_an")[["lat", "lon", "quan", "phuong"]].first())
    if "models/danh_gia_mo_hinh_can_ho.json" in tep:
        bo["danh_gia_can_ho"] = json.loads(doc("models/danh_gia_mo_hinh_can_ho.json"))
    if "models/tro_ly_y_dinh.joblib" in tep:
        bo["tro_ly"] = joblib.load(io.BytesIO(doc("models/tro_ly_y_dinh.joblib")))
    _kiem_bo(bo)
    bo["nap_luc"] = dt.datetime.now().isoformat(timespec="seconds")
    return bo


# Kiểm tra trước khi chuyển bộ: tệp đúng cú pháp chưa đủ (JSON hợp lệ nhưng thiếu khóa vẫn làm endpoint lỗi 500 sau khi
# bộ đã được nhận). Kiểm cấu trúc + kiểu của mọi phần endpoint thật sự đọc, rồi CHẠY THỬ đường xử lý của từng endpoint.
KIEM_BO = []          # main.py đăng ký hàm chạy thử các endpoint dữ liệu (tổng quan, danh sách tin, bản đồ, danh mục, health)


def _can(dk, ten):
    if not dk:
        raise LoiNapBo(f"bộ tệp sai cấu trúc: {ten}")


def _kieu(d, khoa, kieu, noi):
    _can(isinstance(d, dict) and khoa in d and isinstance(d[khoa], kieu), f"{noi}['{khoa}'] thiếu hoặc không phải {kieu}")
    return d[khoa]


def _kiem_bo(bo):
    w, dg, goi = bo["web"], bo["danh_gia"], bo["nha"][0]
    so = lambda x: isinstance(x, (int, float)) and not isinstance(x, bool)
    for k, kieu in (("SO_LIEU", dict), ("MODEL", dict), ("MODEL_TABLE", list), ("GT_META", dict), ("LISTINGS", list),
                    ("MAP_PTS", list), ("CH_MODEL", dict), ("CH_LIST", list), ("CH_PHUONG", list), ("CH_TOA", list),
                    ("TREND", dict), ("THUE", dict)):          # phần mở rộng (CH_*, TREND, THUE) được phép rỗng nhưng phải đúng kiểu
        _kieu(w, k, kieu, "du_lieu_web.json")
    _kieu(w["SO_LIEU"], "NGAY", str, "du_lieu_web.json SO_LIEU")
    for k in ("model", "cv_mape", "mo_hinh_day_du", "mo_hinh_day_du_mape_cv_phu_hoa"):
        _can(k in w["MODEL"], f"du_lieu_web.json MODEL thiếu '{k}'")
    _can(len(w["LISTINGS"]) > 0, "du_lieu_web.json LISTINGS rỗng")
    for x in w["LISTINGS"]:
        _can(isinstance(x, dict) and "id" in x and so(x.get("g")) and so(x.get("dt")) and so(x.get("ai_full")) and x["ai_full"] > 0,
             f"du_lieu_web.json LISTINGS: tin {x.get('id') if isinstance(x, dict) else x!r} thiếu id / g / dt / ai_full hợp lệ")
    _can(all(isinstance(d, list) and len(d) >= 4 for d in w["MAP_PTS"]), "du_lieu_web.json MAP_PTS: mỗi điểm phải là mảng >= 4 phần tử")
    _kieu(dg, "ten_mo_hinh", str, "danh_gia_mo_hinh.json"); _kieu(dg, "test_phu_hoa", list, "danh_gia_mo_hinh.json")
    _can(isinstance(goi, dict) and all(k in goi for k in ("model", "ten", "khoang_theo_muc")), "mo_hinh_gia_nha.joblib thiếu model / ten / khoang_theo_muc")
    try:                                              # chạy thử: mô hình mới phải định giá được và các endpoint dữ liệu chạy được
        _dinh_gia_nha(bo, dt_dat=80, so_tang=2)
        if bo["can_ho"] is not None:
            _dinh_gia_can_ho(bo, dt_su_dung=60, phong_ngu=2)
        if bo["danh_gia_can_ho"] is not None:
            _can(isinstance(bo["danh_gia_can_ho"], dict), "danh_gia_mo_hinh_can_ho.json không phải object")
        if bo["tro_ly"] is not None:
            _y_dinh(bo["tro_ly"], "nhà 80m2 giá bao nhiêu")
        for f in KIEM_BO:
            f(bo)
    except LoiNapBo:
        raise
    except Exception as e:
        raise LoiNapBo(f"bộ tệp không dùng được (chạy thử lỗi {type(e).__name__}: {e})") from e


_HIEN, _TT, _KHOA = None, {"moc": None, "loi_nap": None, "nguon": None}, threading.Lock()


def _du_phong():
    """Nguồn phục hồi khi không dùng được bản kê hiện tại: bộ ĐÃ công bố gần nhất, rồi bộ bàn giao trong git.
    Bộ chép vào models/cong_bo/ nhưng công bố lỗi (chưa qua điểm cam kết) không có dấu nên không bao giờ được chọn."""
    ds = [("bộ đã công bố gần nhất " + bk["id"], bk) for bk in _cac_dau()]
    try:
        ds.append(("bộ bàn giao " + BAN_GIAO, json.loads((GOC / BAN_GIAO / "phien_ban.json").read_text(encoding="utf-8"))))
    except (OSError, ValueError):
        pass
    return ds


def _moc_ban_ke():
    if os.environ.get("PHH_UNG_VIEN") == "1":        # CHỈ khi bật tường minh: kiểm thử bộ ứng viên = tệp làm việc
        return ("ung_vien",) + tuple((GOC / t).stat().st_mtime_ns if (GOC / t).exists() else 0 for t in TEP_BAT_BUOC + TEP_TUY_CHON)
    f = GOC / MANIFEST
    if f.exists():
        return ("ban_ke", f.stat().st_mtime_ns)
    return ("khong_ban_ke",)                         # tệp làm việc KHÔNG bao giờ được phục vụ khi thiếu bản kê


def _ung_vien_nap(moc):
    """Danh sách (nguồn, hàm lấy bản kê) theo trạng thái moc. Bản kê hiện tại lỗi (JSON hỏng, bộ không nạp được) khi API
    CHƯA có bộ nào -> thử tiếp các nguồn phục hồi; đang có bộ thì bo() giữ bộ đó (danh sách chỉ dùng khi chưa có bộ)."""
    if moc[0] == "ung_vien":
        return [("tệp làm việc (PHH_UNG_VIEN=1)", tao_ban_ke)]
    du_phong = [(nguon, (lambda b=bk: b)) for nguon, bk in _du_phong()]
    if moc[0] == "ban_ke":
        return [(MANIFEST, lambda: json.loads((GOC / MANIFEST).read_text(encoding="utf-8")))] +             [("phục hồi (bản kê hiện tại lỗi): " + n, f) for n, f in du_phong]
    return du_phong


def bo():
    """Bộ tệp ĐANG phục vụ; chỉ chuyển bộ khi bản kê models/phien_ban.json đổi (= pipeline công bố sau khi kiểm thử đạt).
    Chưa có bộ hợp lệ nào -> LoiNapBo (mọi endpoint trả 503, không 500)."""
    global _HIEN
    moc = _moc_ban_ke()
    if moc == _TT["moc"]:                            # trạng thái này đã xử lý (thành công hay lỗi): không nạp lại
        if _HIEN is None:
            raise LoiNapBo(f"chưa có bộ tệp hợp lệ: {_TT['loi_nap']}")
        return _HIEN
    with _KHOA:
        if moc != _TT["moc"]:
            if _TT["moc"] and _TT["moc"][0] == "ung_vien":
                _HIEN = None                         # bộ ứng viên (tệp làm việc) không bao giờ được giữ sang chế độ thường
            if moc[0] == "khong_ban_ke" and _HIEN is not None and _TT["moc"][0] == "ban_ke":
                # bản kê biến mất khi đang chạy: bộ đang phục vụ là bộ công bố hợp lệ cuối cùng -> giữ, báo lỗi
                _TT["loi_nap"] = f"không còn {MANIFEST}; giữ bộ đang phục vụ {_HIEN['id']}"
            else:
                thu, loi = _ung_vien_nap(moc), []
                if moc[0] == "ban_ke" and _HIEN is not None:
                    thu = thu[:1]                   # đang phục vụ: chỉ thử bản kê mới, lỗi thì GIỮ bộ đang phục vụ
                for nguon, lay in thu:
                    try:
                        moi = _nap_bo(lay())
                    except Exception as e:
                        loi.append(f"{nguon}: {type(e).__name__}: {e}")
                        continue
                    _HIEN, _TT["nguon"] = moi, nguon
                    if nguon in (MANIFEST, "tệp làm việc (PHH_UNG_VIEN=1)"):
                        loi = []                    # nguồn chính nạp được: không còn lỗi
                    break
                else:
                    if not thu:
                        loi.append(f"không có bộ đã công bố trong {THU_MUC_CONG_BO}/ hay bộ bàn giao {BAN_GIAO}/")
                _TT["loi_nap"] = "; ".join(loi) or None
            _TT["moc"] = moc
        if _HIEN is None:
            raise LoiNapBo(f"chưa có bộ tệp hợp lệ: {_TT['loi_nap']}")
    return _HIEN


def trang_thai():
    return dict(_TT)


def du_lieu_web():
    return bo()["web"]


def _khoang(p, q):
    return round(float(np.exp(p + q["q10"])), 3), round(float(np.exp(p + q["q90"])), 3)


def _dong_gop(goi_mh, can):
    """Đóng góp log của từng đặc trưng (phương pháp Saabas, trung bình trên các cây). None nếu không phải mô hình cây."""
    pipe = goi_mh.m_
    est = pipe[-1] if hasattr(pipe, "steps") else pipe
    cac_cay = list(getattr(est, "estimators_", [])) or ([est] if hasattr(est, "tree_") else [])
    if not cac_cay or getattr(goi_mh, "khong_gian", True):
        return None, None
    Z = goi_mh._Z(can)
    cot = list(pipe[:-1].get_feature_names_out()) if hasattr(pipe, "steps") else list(Z.columns)
    Z = np.asarray(pipe[:-1].transform(Z) if hasattr(pipe, "steps") else Z, dtype=np.float32)
    nen, C = 0.0, np.zeros(Z.shape)
    for t in cac_cay:
        tr = t.tree_; v = tr.value[:, 0, 0]
        cha = np.full(tr.node_count, -1)
        nut = np.where(tr.children_left >= 0)[0]
        cha[tr.children_left[nut]] = nut; cha[tr.children_right[nut]] = nut
        con = np.where(cha >= 0)[0]
        M = sparse.csr_matrix((v[con] - v[cha[con]], (con, tr.feature[cha[con]])), shape=(tr.node_count, Z.shape[1]))
        C += (t.decision_path(Z) @ M).toarray(); nen += v[0]
    return nen / len(cac_cay), pd.Series(C[0] / len(cac_cay), index=cot)


def _ty_suat_nha(B, phuong):
    th = B["web"].get("THUE") or {}
    return (th.get("ty_suat_phuong_nha") or {}).get(phuong) or (th.get("ty_suat_tv") or {}).get("nha_tdm")


def dinh_gia_nha(**kw):
    B = bo()
    return {**_dinh_gia_nha(B, **kw), "phien_ban": B["id"]}


def _dinh_gia_nha(B, dt_dat, ngang=None, dai=None, so_tang=None, dt_san=None, phong_ngu=None, so_wc=None, mat_tien_duong=0,
                  cap_loi_vao=None, hem_rong=None, duong=None, phuong="phu hoa", quan="thu dau mot", lat=None, lon=None, mo_ta=""):
    goi, xy_duong, xy_phuong = B["nha"]
    if lat is None or lon is None:
        k = (quan, khong_dau(duong)) if duong else None
        if k is not None and k in xy_duong.index:
            lat, lon = xy_duong.loc[k].values
        elif (quan, phuong) in xy_phuong.index:
            lat, lon = xy_phuong.loc[(quan, phuong)].values
        else:
            lat, lon = xy_phuong.loc[("thu dau mot", "phu hoa")].values
    can = pd.DataFrame([{"dt_dat": dt_dat, "ngang": ngang, "dai": dai, "so_tang": so_tang, "dt_san": dt_san,
                         "phong_ngu": phong_ngu, "so_wc": so_wc, "mat_tien_duong": mat_tien_duong, "cap_loi_vao": cap_loi_vao,
                         "hem_rong": hem_rong, "so_chung": np.nan, "noi_that": np.nan, "quan": quan, "phuong": phuong,
                         "duong": khong_dau(duong) if duong else None, "lat": lat, "lon": lon, "van_ban": khong_dau(mo_ta or "")}])
    can = pd.concat([can, trich_dac_trung_chu(can["van_ban"])], axis=1)
    can["log_dt"] = np.log(can["dt_dat"]); can["ty_le_san"] = can["dt_san"] / can["dt_dat"]
    can["kc_trung_tam_km"] = np.hypot((lat - TRUNG_TAM_TDM[0]) * 110.6, (lon - TRUNG_TAM_TDM[1]) * 109.3)
    can = can.astype({c: float for c in ["ngang", "dai", "so_tang", "dt_san", "phong_ngu", "so_wc", "cap_loi_vao", "hem_rong"]})
    p = float(goi["model"].predict(can)[0])
    q = {k: float(v[0]) for k, v in phan_vi_cho(nhom_khoang(p, goi["khoang_theo_muc"]["nguong"], phuong == "phu hoa"), goi["khoang_theo_muc"]).items()}
    gia = float(np.exp(p))
    kq = {"gia_ty": round(gia, 3), "khoang_80_ty": _khoang(p, q), "khoang_50_ty": (round(float(np.exp(p + q["q25"])), 3), round(float(np.exp(p + q["q75"])), 3)),
          "don_gia_trieu_m2": round(gia * 1000 / dt_dat, 1), "mo_hinh": goi["ten"], "ngay_du_lieu": goi.get("ngay_du_lieu"), "giai_thich": None}
    ys = _ty_suat_nha(B, phuong)
    kq["thue_trieu_thang"], kq["ty_suat_pt"] = (round(gia * 1000 * ys / 100 / 12, 1), round(ys, 2)) if ys else (None, None)
    nen, dg = _dong_gop(goi["model"], can)
    if dg is not None:
        nhom, da_dung = {}, set()
        for ten, cols in NHOM_GT.items():
            cc = [c for c in cols if c in dg.index]; da_dung |= set(cc); nhom[ten] = float(dg[cc].sum())
        nhom["Thông tin khác trong mô tả tin"] = float(dg[[c for c in dg.index if c not in da_dung]].sum())
        kq["giai_thich"] = {"nen_ty": round(float(np.exp(nen)), 3),
                            "nhom": [{"nhom": k, "log": round(v, 4), "phan_tram": round((np.exp(v) - 1) * 100, 1)} for k, v in sorted(nhom.items(), key=lambda kv: -abs(kv[1]))]}
    return kq


def dinh_gia_can_ho(dt_su_dung, du_an=None, phong_ngu=None, so_wc=None, tang=None, so_hong=None, noi_that_cap=None,
                    nha_o_xa_hoi=0, quan="thu dau mot", phuong="phu hoa", mo_ta=""):
    B = bo()
    if B["can_ho"] is None:
        raise LoiNapBo("chưa có mô hình căn hộ (phần mở rộng)")
    return _dinh_gia_can_ho(B, dt_su_dung, du_an, phong_ngu, so_wc, tang, so_hong, noi_that_cap, nha_o_xa_hoi, quan, phuong, mo_ta)


def _dinh_gia_can_ho(B, dt_su_dung, du_an=None, phong_ngu=None, so_wc=None, tang=None, so_hong=None, noi_that_cap=None,
                     nha_o_xa_hoi=0, quan="thu dau mot", phuong="phu hoa", mo_ta=""):
    goi, df, xy_du_an = B["can_ho"]
    ma = ten_du_an(du_an) if du_an else None
    if ma in xy_du_an.index:
        lat, lon, quan, phuong = xy_du_an.loc[ma].values
    else:
        g = df[(df["quan"] == quan) & (df["phuong"] == phuong)]
        lat, lon = (g["lat"].median(), g["lon"].median()) if len(g) else (df["lat"].median(), df["lon"].median())
    if not (mo_ta or "").strip():   # mô hình chữ học trên tin luôn có tiêu đề: tạo tiêu đề ngắn từ thông số (như notebook)
        mo_ta = f"Bán căn hộ {du_an or ''} {dt_su_dung:g}m2" + (f" {phong_ngu:g}PN" if phong_ngu else "") + (f" {so_wc:g}WC" if so_wc else "")
    can = pd.DataFrame([{"dt_dat": dt_su_dung, "phong_ngu": phong_ngu, "so_wc": so_wc, "tang_so": tang, "so_hong": so_hong,
                         "noi_that_cap": noi_that_cap, "noxh": float(nha_o_xa_hoi), "loai_dac_biet": 0.0, "can_ho_dich_vu": 0.0,
                         "da_ban_giao": np.nan, "quan": quan, "phuong": phuong, "du_an": ma, "duong": ma, "lat": lat, "lon": lon,
                         "van_ban": khong_dau(mo_ta)}])
    can = pd.concat([can, trich_dac_trung_chu(can["van_ban"])], axis=1)
    for k in ["t_view", "t_tang_cao", "t_so_cap", "t_noxh"]:
        can[k] = 0
    can["log_dt"] = np.log(can["dt_dat"]); can["kc_trung_tam_km"] = np.hypot((lat - TRUNG_TAM_TDM[0]) * 110.6, (lon - TRUNG_TAM_TDM[1]) * 109.3)
    can = can.astype({c: float for c in ["phong_ngu", "so_wc", "tang_so", "so_hong", "noi_that_cap", "da_ban_giao"]})
    p = float(goi["model"].predict(can)[0])
    q = goi["khoang_theo_phan_khuc"]["nhom"].get("noxh" if nha_o_xa_hoi else "thuong_mai", goi["phan_vi_sai_so"])
    gia = float(np.exp(p))
    th = B["web"].get("THUE") or {}
    ys = (th.get("ty_suat_du_an") or {}).get(ma) or (th.get("ty_suat_tv") or {}).get("can_ho")
    return {"gia_ty": round(gia, 3), "khoang_80_ty": _khoang(p, q), "don_gia_trieu_m2": round(gia * 1000 / dt_su_dung, 1),
            "du_an_nhan_ra": ma in xy_du_an.index, "mo_hinh": goi["ten"],
            "thue_trieu_thang": round(gia * 1000 * ys / 100 / 12, 1) if ys else None, "ty_suat_pt": round(ys, 2) if ys else None,
            "phien_ban": B["id"]}


def _chuan_hoa_cau(s):
    # giống chuan_hoa của notebook trợ lý: bỏ dấu, chữ thường, mọi số thành "0", chỉ giữ chữ/số
    import re
    import unicodedata
    s = str(s).replace("đ", "d").replace("Đ", "d")
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").lower()
    s = re.sub(r"\d+(?:[.,]\d+)*", "0", s)
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def y_dinh(cau):
    """Phân loại ý định câu hỏi bằng mô hình TF-IDF + Logistic Regression của notebook trợ lý."""
    goi = bo()["tro_ly"]
    if goi is None:
        raise LoiNapBo("chưa có mô hình trợ lý (phần mở rộng)")
    return _y_dinh(goi, cau)


def _y_dinh(goi, cau):
    X = goi["dac_trung"].transform([_chuan_hoa_cau(cau)])
    p = goi["mo_hinh"].predict_proba(X)[0]
    lop = goi["mo_hinh"].classes_
    thu_tu = np.argsort(-p)[:3]
    return {"y_dinh": str(lop[thu_tu[0]]), "xac_suat": round(float(p[thu_tu[0]]), 3), "chac_chan": bool(p[thu_tu[0]] >= goi["nguong"]),
            "ung_vien": [{"y_dinh": str(lop[i]), "xac_suat": round(float(p[i]), 3)} for i in thu_tu]}


if __name__ == "__main__":
    # python api/dinh_gia.py --cong-bo   -> ghi models/phien_ban.json cho bộ tệp hiện có (scripts/chay_toan_bo.py gọi)
    sys.stdout.reconfigure(encoding="utf-8")
    # python api/dinh_gia.py --ban-giao  -> chép bộ đang công bố thành bộ bàn giao models/ban_giao/ (rồi commit)
    if {"--cong-bo", "--ban-giao"} & set(sys.argv):
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import dinh_gia as DG   # noqa: E402  (module thật, không phải __main__: main.py đăng ký phép chạy thử endpoint vào đây)
        import main  # noqa: E402,F401
        if "--cong-bo" in sys.argv:
            b = DG.cong_bo()
            print(f"Đã công bố bộ tệp {b['id']}: " + ", ".join(f"{t} {h[:12]}" for t, h in b["tep"].items()))
        else:
            b = DG.tao_ban_giao()
            print(f"Bộ bàn giao {DG.BAN_GIAO}/ = bộ {b['id']} ({len(b['tep'])} tệp); commit thư mục này để clone mới chạy được.")
