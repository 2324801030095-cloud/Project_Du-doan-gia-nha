"""Kiểm thử tự động cho mã dùng chung (src/mo_hinh_gia.py) và kết quả đã sinh ra.
Chạy từ thư mục gốc đề tài:  python tests/kiem_tra_mo_hinh.py
Mỗi phép kiểm in ĐẠT / KHÔNG ĐẠT / BỎ QUA; mã thoát khác 0 nếu có phép kiểm không đạt.
Chế độ bài chính (chỉ cần dữ liệu và mô hình nhà phố):  python tests/kiem_tra_mo_hinh.py --nha-pho
  -> các phép kiểm phần mở rộng (căn hộ...) được BỎ QUA có ghi lý do; chế độ mặc định chạy đủ và đòi đủ tệp.
Xem các số kết quả còn viết tay trong markdown của một notebook:
    python tests/kiem_tra_mo_hinh.py --markdown notebooks/2324801030095.ipynb"""
import sys
import warnings

sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # in được tiếng Việt cả trên PowerShell / cmd mặc định
from pathlib import Path

warnings.filterwarnings("ignore")
GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC / "src"))
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, RegressorMixin

import mo_hinh_gia as M

# ---------- Số liệu viết tay trong markdown ----------
# Markdown của notebook không được chứa số KẾT QUẢ viết tay.
# Số kết quả (MAPE, độ phủ, số căn...) phải được in ra từ biến trong ô code (hàm nx), nên khi dữ liệu cập nhật thì chữ tự đúng.
# Trong ô markdown, các số sau bị coi là số kết quả viết tay:
#   1. số có phần thập phân (23,9) hoặc có dấu % (26,5% / 80%) mà KHÔNG phải một giá trị cố định trong mã nguồn
#      (ngưỡng lọc, tham số, mức 80% của khoảng giá...), tức mã của notebook hoặc src/mo_hinh_gia.py;
#   2. số đếm có đơn vị (N căn / tin / lô / dự án / cặp / nhóm) không phải giá trị cố định trong mã;
#   3. mọi số ước chừng: đứng sau "~", "≈" hoặc "khoảng" (trừ mức 80% / 95% của khoảng giá và khoảng tin cậy).
#   4. mọi khoảng "a–b%".
# Phần chữ cố định trong các nhận xét nx(f'''...''') (bỏ các biểu thức {…}) được kiểm như markdown.
# Giới hạn còn lại: một số kết quả trùng đúng một hằng số trong mã (ví dụ 0,6 trùng tham số 0.6) mà không đứng sau "khoảng/~/≈"
# thì không phân biệt được; các nhận xét có số đã được chuyển sang nx nên trường hợp này chỉ còn ở các ngưỡng thật sự cố định.
# Dùng: python tests/kiem_tra_mo_hinh.py --markdown <notebook>

import json
import re
DON_VI = r"căn|tin|lô|dự án|cặp|nhóm"
MUC_CO_DINH = {80.0, 95.0}          # mức của khoảng giá 80% và khoảng tin cậy 95%


def _so(chuoi):
    """Tập mọi số (dạng 12 hoặc 12.5) xuất hiện trong chuỗi."""
    return {float(x) for x in re.findall(r"\d+(?:\.\d+)?", chuoi)}


NX = re.compile(r"nx\(f'''(.*?)'''\)", re.DOTALL)


def _chu_tinh(nx_f):
    """Phần chữ cố định của một nhận xét nx(f'''...'''): bỏ các biểu thức {…} (lồng tối đa 1 cấp)."""
    return re.sub(r"\{(?:[^{}]|\{[^{}]*\})*\}", "{…}", nx_f)


def kiem_markdown(duong_dan):
    """Tìm số VIẾT TAY trong chữ markdown của notebook: mọi con số kết quả phải được in từ biến (nhận xét nx(f'''...''')),
    chỉ hằng số có thật trong mã (ngưỡng, tham số) mới được gõ thẳng trong chữ. Trả về các đoạn vi phạm."""
    nb = json.load(open(duong_dan, encoding="utf-8"))
    ma = "\n".join("".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code")
    ma = NX.sub("", ma)                     # chữ của nhận xét không phải hằng số của mã
    ma += (GOC / "src" / "mo_hinh_gia.py").read_text(encoding="utf-8")
    co_dinh = _so(ma)
    co_dinh |= {round(x * 100, 6) for x in co_dinh if x <= 1}          # 0.8 trong mã <-> "80%" trong chữ
    sai = []
    for i, c in enumerate(nb["cells"]):
        nguon = "".join(c["source"])
        if c["cell_type"] == "markdown":
            cac_doan = [nguon]
        else:                               # chữ cố định trong nx(...) cũng là chữ người đọc thấy
            cac_doan = [_chu_tinh(m.group(1)) for m in NX.finditer(nguon)]
        for md in cac_doan:
            sai += _so_viet_tay(i, md, co_dinh)
    return sai


def _so_viet_tay(i, md, co_dinh):
    # khoảng "a–b%" là nhận định về kết quả (ngưỡng cố định luôn là một số); không tra hằng số vì 0.25 trong mã trùng "25%"
    """Các số trong ô markdown thứ i không phải hằng số của mã (co_dinh) và không phải năm / số thứ tự -> nghi viết tay."""
    sai = [(i, md[max(0, m.start() - 60):m.end() + 20].replace("\n", " "))
           for m in re.finditer(r"(?<![\w.,{])\d+(?:,\d+)?\s*[–-]\s*\d+(?:,\d+)?\s*%", md)]
    for m in re.finditer(rf"(?<![\w.,{{])(\d+(?:[.,]\d+)*)(\s*%|\s+(?:{DON_VI})\b)?", md):
        so, duoi = m.group(1), m.group(2) or ""
        if "." in so and not re.fullmatch(r"\d{1,3}(\.\d{3})+", so):
            continue                      # số mục (4.4, 5.1), không phải số liệu
        x = float(so.replace(".", "").replace(",", ".")) if re.fullmatch(r"\d{1,3}(\.\d{3})+", so) else float(so.replace(",", "."))
        truoc = md[max(0, m.start() - 8):m.start()]
        uoc_chung = re.search(r"(~|≈|khoảng)\s*$", truoc) and x not in MUC_CO_DINH
        if not uoc_chung:
            if "," not in so and "." not in so and not duoi:
                continue                  # số nguyên trơn (số bước, số kỳ, năm, tên lớp...) không kiểm
            if x in co_dinh:
                continue
        sai.append((i, md[max(0, m.start() - 60):m.end() + 20].replace("\n", " ")))
    return sai


if "--markdown" in sys.argv:
    s = kiem_markdown(sys.argv[sys.argv.index("--markdown") + 1])
    for i, t in s:
        print(f"ô {i}: …{t}…")
    print(len(s), "số kết quả viết tay trong markdown")
    sys.exit(0)

NHA_PHO = "--nha-pho" in sys.argv
KQ = []           # (tên, "ĐẠT" | "KHÔNG ĐẠT" | "BỎ QUA", chi tiết)
def kiem(ten, mo_rong=False):
    """mo_rong=True: phép kiểm của phần mở rộng (căn hộ...) -> bỏ qua ở chế độ --nha-pho."""
    def boc(f):
        """Chạy hàm kiểm f ngay khi khai báo và ghi kết quả (ĐẠT / KHÔNG ĐẠT kèm lỗi, hoặc BỎ QUA cho phần mở rộng ở chế độ --nha-pho)."""
        if mo_rong and NHA_PHO:
            KQ.append((ten, "BỎ QUA", "phần mở rộng, không thuộc chế độ --nha-pho")); return f
        try:
            f(); KQ.append((ten, "ĐẠT", ""))
        except Exception as e:
            KQ.append((ten, "KHÔNG ĐẠT", f"{type(e).__name__}: {e}"))
        return f
    return boc

def du_lieu_gia(n=300, seed=0):
    """Dữ liệu giả lập n căn quanh Thủ Dầu Một để kiểm lớp mô hình (giá ≈ 0,04 tỷ/m² × diện tích, nhiễu log 0,1)."""
    rng = np.random.default_rng(seed)
    d = pd.DataFrame({"lat": 10.95 + rng.random(n) * 0.05, "lon": 106.65 + rng.random(n) * 0.05, "dt_dat": rng.uniform(50, 200, n),
                      "quan": "thu dau mot", "phuong": rng.choice(["a", "b", "c"], n), "duong": rng.choice(["x", "y", None], n)})
    d["y"] = np.log(d["dt_dat"] * 0.04) + rng.normal(0, 0.1, n)
    return d

@kiem("Đặc trưng giá khu vực không dùng giá của CHÍNH căn đó và các tin cùng nhóm khi học (leave-group-out)")
def _():
    d = du_lieu_gia(); y = d["y"].to_numpy().copy()
    a = M.GiaLangGieng().fit_transform(d, y)
    y2 = y.copy(); y2[0] += 5.0                      # đổi hẳn giá căn số 0
    b = M.GiaLangGieng().fit_transform(d, y2)
    for c in ["lg_knn", "lg_knn_med", "lg_phuong", "lg_duong"]:
        assert abs(a[c].iloc[0] - b[c].iloc[0]) < 1e-9, f"{c} của căn 0 thay đổi khi đổi giá căn 0"
    # leave-group-out: căn 1 là tin đăng lại của căn 0 (cùng nhóm) -> đổi giá căn 1 cũng không được ảnh hưởng căn 0
    d["nhom"] = np.arange(len(d)); d.loc[1, "nhom"] = 0
    vi_tri = ["quan", "phuong", "duong", "lat", "lon"]
    d.loc[1, vi_tri] = d.loc[0, vi_tri].to_numpy()       # tin đăng lại: cùng phường, đường, tọa độ
    a = M.GiaLangGieng().fit_transform(d, y)
    y3 = y.copy(); y3[1] += 5.0
    b = M.GiaLangGieng().fit_transform(d, y3)
    for c in ["lg_knn", "lg_knn_med", "lg_phuong", "lg_duong"]:
        assert abs(a[c].iloc[0] - b[c].iloc[0]) < 1e-9, f"{c} của căn 0 thay đổi khi đổi giá tin cùng nhóm (căn 1)"
    # nhưng căn ngoài nhóm thì vẫn được dùng: đổi giá căn 2 phải làm đổi giá khu vực của ít nhất vài căn
    y4 = y.copy(); y4[2] += 5.0
    assert not np.allclose(M.GiaLangGieng().fit_transform(d, y4)["lg_knn"], a["lg_knn"]), "giá khu vực không dùng căn nào khác"

@kiem("Kiểm định chéo theo nhóm: không nhóm nào vừa ở tập học vừa ở tập kiểm tra")
def _():
    d = du_lieu_gia(); d["nhom"] = np.arange(len(d)) // 3
    vi_pham = []
    class Ghi(BaseEstimator, RegressorMixin):
        """Mô hình "gián điệp": nhớ các nhóm đã học, khi dự đoán ghi lại nhóm nào xuất hiện cả ở tập học (= rò rỉ)."""
        def fit(self, X, y): self.nhom_ = set(X["nhom"]); return self   # chỉ ghi nhóm của tập học
        def predict(self, X):
            vi_pham.extend(set(X["nhom"]) & self.nhom_); return np.zeros(len(X))
    M.du_doan_cheo_lap(Ghi, d, so_lan=2)
    assert not vi_pham, f"{len(vi_pham)} nhóm bị rò rỉ"

@kiem("Gom tin gần trùng: cùng một căn đăng lại (mô tả giống) được gom; căn khác cùng dự án thì không (chế độ căn hộ)")
def _():
    d = pd.DataFrame({"quan": ["q"] * 3, "phuong": ["p"] * 3, "duong": ["du an a"] * 3, "ngang": np.nan, "dai": np.nan,
                      "dt_dat": [70, 70.5, 70], "gia_ty": [2.40, 2.45, 2.30],
                      "van_ban": ["ban can ho du an a 2pn 70m2 view song tang cao full noi that so hong",
                                  "ban can ho du an a 2pn 70m2 view song tang cao full noi that so hong rieng",
                                  "chu nha can tien ban gap can goc huong dong nam ban giao tho"]})
    g = M.nhom_gan_trung(d, dung_vi_tri=False)
    assert g[0] == g[1], "hai tin cùng nội dung không bị gom"
    assert g[2] != g[0], "căn khác (mô tả khác) bị gom nhầm"

@kiem("Chỉ số đánh giá tính đúng trên ví dụ biết trước")
def _():
    y = np.log([1.0, 2.0, 4.0]); p = np.log([1.08, 2.0, 3.0])          # sai số 8%, 0%, 25%
    cs = M.chi_so_danh_gia(y, p)
    assert abs(cs["MAPE (%)"] - (8 + 0 + 25) / 3) < 1e-6, cs["MAPE (%)"]
    assert abs(cs["Trong ±10% (%)"] - 200 / 3) < 1e-6 and abs(cs["Trong ±20% (%)"] - 200 / 3) < 1e-6, cs

@kiem("Khoảng theo nhóm (Mondrian) phủ đúng ~80% ở CẢ nhóm dễ và nhóm khó")
def _():
    rng = np.random.default_rng(0)
    g = np.r_[np.zeros(4000), np.ones(4000)].astype(int)
    r = np.r_[rng.normal(0, 0.1, 4000), rng.normal(0, 0.4, 4000)]
    bang = M.hieu_chinh_khoang(r[::2], g[::2])                    # học trên nửa, kiểm trên nửa còn lại
    q = M.phan_vi_cho(g[1::2], bang); rr = r[1::2]
    for k in (0, 1):
        m = g[1::2] == k; phu = np.mean((rr[m] >= q["q10"][m]) & (rr[m] <= q["q90"][m]))
        assert 0.77 < phu < 0.83, f"nhóm {k} phủ {phu:.2f}"

def kiem_du_lieu_sach(ds):
    """Kiểm từng tệp CSV đã xử lý: không còn tin cho thuê / giá hay đơn giá vô lý, và train / test không chung nhóm tin gần trùng."""
    for f, cot_dt in ds:
        d = pd.read_csv(GOC / "dataset" / "processed" / f)
        assert d["gia_ty"].between(0.3, 60).all(), f"{f}: có giá ngoài phạm vi"
        assert (d["gia_ty"] * 1000 / d[cot_dt]).between(5, 250).all(), f"{f}: có đơn giá vô lý"
        if "tap" in d:
            assert not set(d.loc[d["tap"] == "train", "nhom"]) & set(d.loc[d["tap"] == "test", "nhom"]), f"{f}: nhóm chung giữa train và test"

@kiem("Dữ liệu sạch nhà phố: không có tin cho thuê / giá vô lý; tập test không chung nhóm với tập train")
def _():
    kiem_du_lieu_sach([("nha_da_xu_ly.csv", "dt_dat")])

@kiem("Dữ liệu sạch căn hộ (mở rộng): không có giá / đơn giá vô lý; train và test không chung nhóm", mo_rong=True)
def _():
    kiem_du_lieu_sach([("can_ho_da_xu_ly.csv", "dt_dat")])

def kiem_mo_hinh_luu(ds):
    """Nạp lại từng mô hình .joblib đã lưu, dự đoán trên dữ liệu học: sai số trung vị phải < 50% (mô hình không hỏng / không lệch cột)."""
    import joblib

    from mo_hinh_gia import khong_dau
    for f, du_lieu in ds:
        goi = joblib.load(GOC / "models" / f)
        d = pd.read_csv(GOC / "dataset" / "processed" / du_lieu).head(20)
        d["van_ban"] = d["tieu_de"].fillna("").map(khong_dau)
        p = np.exp(goi["model"].predict(d))
        assert np.isfinite(p).all() and (p > 0.1).all() and (p < 100).all(), f"{f}: dự đoán bất thường"
        sai = np.median(np.abs(p / d["gia_ty"] - 1))
        assert sai < 0.5, f"{f}: sai số trung vị trên dữ liệu học {sai:.0%} – mô hình có vẻ hỏng"

@kiem("Mô hình nhà phố đã lưu nạp lại được và dự đoán ra số hợp lý")
def _():
    kiem_mo_hinh_luu([("mo_hinh_gia_nha.joblib", "nha_da_xu_ly.csv")])

@kiem("Mô hình căn hộ (mở rộng) đã lưu nạp lại được và dự đoán ra số hợp lý", mo_rong=True)
def _():
    kiem_mo_hinh_luu([("mo_hinh_gia_can_ho.joblib", "can_ho_da_xu_ly.csv")])

@kiem("Khoảng 80% đã lưu cho nhà phố theo mức giá: nhà đắt có biên độ rộng hơn nhà rẻ")
def _():
    import joblib
    k = joblib.load(GOC / "models" / "mo_hinh_gia_nha.joblib")["khoang_theo_muc"]
    rong = lambda g: k["nhom"][g]["q90"] - k["nhom"][g]["q10"]
    assert len(k["nguong"]) == 3 and rong("3") > rong("0"), "biên độ mức đắt nhất không rộng hơn mức rẻ nhất"

@kiem("Kiểm định lùi xu hướng: không nhìn trước tương lai; Holt chỉ thắng 'không đổi' khi chuỗi có xu hướng thật")
def _():
    # chuỗi kiểm tra có tính chất biết trước (đây là kiểm thử MÃ, không phải dữ liệu đưa vào mô hình)
    rng = np.random.default_rng(0)
    y = np.cumsum(rng.normal(0, 0.01, 30))
    a = M.kiem_dinh_lui(y)
    # chuỗi ngẫu nhiên không có xu hướng: Holt đúng không được thắng; bản "nhìn trước" giá kỳ cần đoán sẽ thắng -> bị bắt
    assert not a["holt_tot_hon"], "Holt thắng trên chuỗi ngẫu nhiên: có thể đang dùng dữ liệu của kỳ cần dự báo"
    xu_huong = 0.02 * np.arange(30) + rng.normal(0, 0.002, 30)          # tăng đều 2%/kỳ
    assert M.kiem_dinh_lui(xu_huong)["holt_tot_hon"], "Holt không thắng trên chuỗi có xu hướng rõ"
    assert a["so_ky_kiem_tra"] == 25 and M.kiem_dinh_lui(y[:5])["so_ky_kiem_tra"] == 0
    try:                                             # một kỳ rỗng (NaN) phải báo lỗi, không được ra kết quả "nan"
        M.kiem_dinh_lui(np.r_[np.zeros(4), np.nan, np.zeros(4)]); raise RuntimeError("không báo lỗi khi chuỗi có NaN")
    except AssertionError:
        pass

@kiem("Dữ liệu gốc đọc lại được và đã ẩn danh: mỗi dòng JSONL là 1 bản ghi hợp lệ (kể cả khi tách dòng kiểu Unicode), không còn thông tin người đăng / số điện thoại")
def _():
    import json
    from thu_thap import TRUONG_NGUOI_BAN, an_danh_bang, an_danh_tin
    for f in sorted((GOC / "dataset").rglob("*.jsonl")):
        dong = [l for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]
        for i, l in enumerate(dong):
            a = json.loads(l)                                   # lỗi -> phép kiểm không đạt
            assert not (TRUONG_NGUOI_BAN & set(a)), f"{f.name} dòng {i + 1}: còn trường người đăng {TRUONG_NGUOI_BAN & set(a)}"
            # ẩn danh thêm lần nữa mà không đổi gì = không còn SĐT ở bất kỳ trường chữ nào
            assert an_danh_tin(json.loads(l)) == a, f"{f.name} dòng {i + 1}: còn số điện thoại"
    for f in sorted((GOC / "dataset").rglob("*.csv")) + sorted((GOC / "results").glob("*.csv")):
        n = an_danh_bang(pd.read_csv(f, dtype=str, keep_default_na=False))[1]
        assert n == 0, f"{f.name}: còn {n} ô có số điện thoại"

@kiem("Số liệu trong notebook và README khớp kết quả đã lưu: markdown của MỌI notebook không còn số kết quả viết tay; số chính hiện đúng trong phần in ra của notebook chính và README")
def _():
    # Dữ liệu cập nhật định kỳ thì số liệu thật đổi. Nhận xét có số được in từ biến (nx) nên tự đúng; phép kiểm này bắt
    # (1) số kết quả còn viết tay trong markdown (tests/kiem_tra_mo_hinh.py --markdown), (2) notebook chưa chạy lại sau khi kết quả đổi,
    # (3) README chưa cập nhật.
    import json
    sai = {f.name: len(s) for f in sorted((GOC / "notebooks").glob("*.ipynb")) if (s := kiem_markdown(f))}
    assert not sai, f"còn số kết quả viết tay trong markdown (chạy tests/kiem_tra_mo_hinh.py --markdown <notebook> để xem): {sai}"
    dg = json.loads((GOC / "models" / "danh_gia_mo_hinh.json").read_text(encoding="utf-8"))
    vn = lambda x, d=1: f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    chon = dg["ten_mo_hinh"]
    te_ph = next(m for m in dg["test_phu_hoa"] if m["Mô hình"] == chon)
    te_tdm = next(m for m in dg["test_tdm"] if m["Mô hình"] == chon)
    cv_ph = next(m for m in dg["kiem_dinh_cheo_phu_hoa"] if m["Mô hình"] == chon)
    can = {"tên mô hình được chọn": chon, "số căn sau làm sạch": vn(dg["so_can"]["tat_ca"], 0),
           "MAPE test Phú Hòa": vn(te_ph["MAPE (%)"]), "MAPE test Thủ Dầu Một": vn(te_tdm["MAPE (%)"])}
    nb = json.loads((GOC / "notebooks" / "2324801030095.ipynb").read_text(encoding="utf-8"))
    chu = []                                    # chữ người đọc thấy: markdown + mọi output (bảng, dòng in, nhận xét nx)
    for c in nb["cells"]:
        chu.append("".join(c["source"]) if c["cell_type"] == "markdown" else "")
        for o in c.get("outputs", []):
            chu.append("".join(o.get("text", "")))
            chu += ["".join(v) if isinstance(v, list) else str(v) for k, v in o.get("data", {}).items() if k.startswith("text/")]
    chu = chr(10).join(chu)
    thieu = [f"{k} = {v}" for k, v in can.items() if v not in chu]
    assert not thieu, "notebook chính chưa chạy lại với kết quả mới: " + "; ".join(thieu)
    readme = (GOC / "README.md").read_text(encoding="utf-8")
    can_rm = {"tên mô hình": chon, "MAPE test Phú Hòa": vn(te_ph["MAPE (%)"]), "MAPE kiểm định chéo Phú Hòa": vn(cv_ph["MAPE (%)"])}
    thieu = [f"{k} = {v}" for k, v in can_rm.items() if v not in readme]
    assert not thieu, "README chưa cập nhật: " + "; ".join(thieu)

@kiem("Phần A của notebook mở rộng: chọn siêu tham số bằng kiểm định chéo trên tập train, mô hình tốt nhất đúng là dòng có sai số kiểm định thấp nhất")
def _():
    rng = np.random.default_rng(1); n = 240
    d = pd.DataFrame({"a": rng.normal(size=n), "b": rng.normal(size=n), "nhom": np.arange(n) // 2,
                      "quan": "q", "phuong": rng.choice(["x", "y"], n), "dt_dat": rng.uniform(50, 150, n)})
    d.loc[::7, "b"] = np.nan                                 # có ô thiếu: pipeline phải tự điền
    d["y"] = 0.8 * d["a"] + rng.normal(0, 0.1, n)            # quan hệ tuyến tính: hồi quy tuyến tính phải thắng
    bang, tot, tao = M.mo_hinh_co_ban(d, ["a", "b"], baseline=M.BaselineDonGiaPhuong)
    assert len(tao) == 6 and "Baseline" in bang.index and tot != "Baseline"
    assert tot == bang.drop("Baseline")["MAE log – kiểm định"].idxmin() == "Hồi quy tuyến tính", tot
    assert bang.loc["Baseline", "MAE log – kiểm định"] > bang.loc[tot, "MAE log – kiểm định"]
    assert np.isfinite(tao["Cây quyết định"]().fit(d[["a", "b"]], d["y"]).predict(d[["a", "b"]])).all()

for ten, tt, ct in KQ:
    print(f"{tt:<10}{ten}" + (f"\n           -> {ct}" if ct else ""))
dat, bo_qua = sum(t == "ĐẠT" for _, t, _ in KQ), sum(t == "BỎ QUA" for _, t, _ in KQ)
print(f"\n{dat}/{len(KQ) - bo_qua} phép kiểm đạt, {bo_qua} bỏ qua" + (" (chế độ --nha-pho)" if NHA_PHO else ""))
sys.exit(0 if all(t != "KHÔNG ĐẠT" for _, t, _ in KQ) else 1)
