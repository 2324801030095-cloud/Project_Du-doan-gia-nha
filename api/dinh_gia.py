"""Định giá bằng các mô hình đã huấn luyện trong notebook (models/*.joblib, models/*.json).

- Nhà phố: Random Forest (mô hình cuối, Phần A) + khoảng 80% theo nhóm + giải thích đóng góp theo đường đi trên cây.
- Căn hộ: mô hình đầy đủ của notebook căn hộ (.joblib) + khoảng 80% theo phân khúc.
- Đất: mô hình rút gọn (Ridge trên đơn giá phường) trong models/mo_hinh_gia_dat.json.
- Giá thuê: giá × tỷ suất cho thuê trung vị (phường / dự án) trong models/gia_thue_web.json.
Cách dựng hàng đặc trưng giống hệt hàm du_doan_gia / du_doan_gia_can_ho trong notebook."""
import json
import sys
from functools import lru_cache
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from scipy import sparse

GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC / "src"))            # lớp mô hình (MoHinhGia...) phải nạp được khi đọc .joblib
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


def _json(ten):
    return json.loads((MODELS / ten).read_text(encoding="utf-8"))


@lru_cache
def du_lieu_web():
    return _json("du_lieu_web.json")


@lru_cache
def _nha():
    goi = joblib.load(MODELS / "mo_hinh_gia_nha.joblib")
    df = pd.read_csv(PROC / "nha_da_xu_ly.csv", low_memory=False)
    xy_duong = df[df["toa_do_rieng"] == 1].groupby(["quan", "duong"])[["lat", "lon"]].median()
    xy_phuong = df.dropna(subset=["lat"]).groupby(["quan", "phuong"])[["lat", "lon"]].median()
    return goi, xy_duong, xy_phuong


@lru_cache
def _can_ho():
    goi = joblib.load(MODELS / "mo_hinh_gia_can_ho.joblib")
    df = pd.read_csv(PROC / "can_ho_da_xu_ly.csv", low_memory=False)
    return goi, df, df.groupby("du_an")[["lat", "lon", "quan", "phuong"]].first()


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


def _ty_suat_nha(phuong):
    th = du_lieu_web()["THUE"]
    return (th.get("ty_suat_phuong_nha") or {}).get(phuong) or th["ty_suat_tv"]["nha_tdm"]


def dinh_gia_nha(dt_dat, ngang=None, dai=None, so_tang=None, dt_san=None, phong_ngu=None, so_wc=None, mat_tien_duong=0,
                 cap_loi_vao=None, hem_rong=None, duong=None, phuong="phu hoa", quan="thu dau mot", lat=None, lon=None, mo_ta=""):
    goi, xy_duong, xy_phuong = _nha()
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
    ys = _ty_suat_nha(phuong)
    kq["thue_trieu_thang"], kq["ty_suat_pt"] = round(gia * 1000 * ys / 100 / 12, 1), round(ys, 2)
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
    goi, df, xy_du_an = _can_ho()
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
    th = du_lieu_web()["THUE"]
    ys = (th.get("ty_suat_du_an") or {}).get(ma) or th["ty_suat_tv"]["can_ho"]
    return {"gia_ty": round(gia, 3), "khoang_80_ty": _khoang(p, q), "don_gia_trieu_m2": round(gia * 1000 / dt_su_dung, 1),
            "du_an_nhan_ra": ma in xy_du_an.index, "mo_hinh": goi["ten"],
            "thue_trieu_thang": round(gia * 1000 * ys / 100 / 12, 1), "ty_suat_pt": round(ys, 2)}


def dinh_gia_dat(dt, phuong="thu dau mot|phu hoa", ngang=None, cap_loi_vao=None, hem_rong=None, nen_du_an=False, tho_cu_toan_bo=None, so_rieng=None):
    """Mô hình rút gọn cho đất (giống trang demo): log đơn giá = đơn giá nền của phường + điều chỉnh Ridge."""
    M = du_lieu_web()["DAT_MODEL"]
    ph = next((x for x in M["phuong"] if x["ma"] == phuong), None)
    nen = ph["log_don_gia"] if ph else M["quan"].get(phuong.split("|")[0], M["toan_vung"])
    x = [np.log(dt), min(ngang, M["clip"]["ngang"]) if ngang is not None else None, cap_loi_vao,
         min(hem_rong, M["clip"]["hem_rong"]) if hem_rong is not None else None, 1.0 if nen_du_an else 0.0, tho_cu_toan_bo, so_rieng]
    adj = M["intercept"] + sum(((v if v is not None else M["medians"][i]) - M["scaler"]["mean"][i]) / M["scaler"]["scale"][i] * M["coef"][i]
                               for i, v in enumerate(x))
    don_gia = float(np.exp(nen + adj)) * 1000            # triệu/m²
    gia, q = don_gia * dt / 1000, M["phan_vi_sai_so"]
    return {"gia_ty": round(gia, 3), "khoang_80_ty": (round(gia * float(np.exp(q["q10"])), 3), round(gia * float(np.exp(q["q90"])), 3)),
            "don_gia_trieu_m2": round(don_gia, 1), "don_gia_nen_phuong": round(float(np.exp(nen)) * 1000, 1),
            "phuong_co_du_lieu": ph is not None, "mo_hinh": "Ridge rút gọn (đơn giá phường + thông số lô)"}


def _chuan_hoa_cau(s):
    # giống chuan_hoa của notebook trợ lý: bỏ dấu, chữ thường, mọi số thành "0", chỉ giữ chữ/số
    import re
    import unicodedata
    s = str(s).replace("đ", "d").replace("Đ", "d")
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").lower()
    s = re.sub(r"\d+(?:[.,]\d+)*", "0", s)
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


@lru_cache
def _tro_ly():
    return joblib.load(MODELS / "tro_ly_y_dinh.joblib")


def y_dinh(cau):
    """Phân loại ý định câu hỏi bằng mô hình TF-IDF + Logistic Regression của notebook trợ lý."""
    goi = _tro_ly()
    X = goi["dac_trung"].transform([_chuan_hoa_cau(cau)])
    p = goi["mo_hinh"].predict_proba(X)[0]
    lop = goi["mo_hinh"].classes_
    thu_tu = np.argsort(-p)[:3]
    return {"y_dinh": str(lop[thu_tu[0]]), "xac_suat": round(float(p[thu_tu[0]]), 3), "chac_chan": bool(p[thu_tu[0]] >= goi["nguong"]),
            "ung_vien": [{"y_dinh": str(lop[i]), "xac_suat": round(float(p[i]), 3)} for i in thu_tu]}
