"""Kiểm thử tự động cho mã dùng chung (src/mo_hinh_gia.py) và kết quả đã sinh ra.
Chạy từ thư mục gốc đề tài:  python tests/kiem_tra_mo_hinh.py
Mỗi phép kiểm in ĐẠT / KHÔNG ĐẠT; mã thoát khác 0 nếu có phép kiểm không đạt."""
import sys, warnings
sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # in được tiếng Việt cả trên PowerShell / cmd mặc định
from pathlib import Path
warnings.filterwarnings("ignore")
GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC / "src"))
import numpy as np, pandas as pd
from sklearn.base import BaseEstimator, RegressorMixin
import mo_hinh_gia as M

KQ = []
def kiem(ten):
    def boc(f):
        try:
            f(); KQ.append((ten, True, ""))
        except Exception as e:
            KQ.append((ten, False, f"{type(e).__name__}: {e}"))
        return f
    return boc

def du_lieu_gia(n=300, seed=0):
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
        def fit(self, X, y): self.nhom_ = set(X["nhom"]); return self
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

@kiem("Dữ liệu sạch: không có tin cho thuê / giá vô lý; tập test không chung nhóm với tập train")
def _():
    for f, cot_dt in [("nha_da_xu_ly.csv", "dt_dat"), ("can_ho_da_xu_ly.csv", "dt_dat")]:
        d = pd.read_csv(GOC / "data" / "processed" / f)
        assert d["gia_ty"].between(0.3, 60).all(), f"{f}: có giá ngoài phạm vi"
        assert (d["gia_ty"] * 1000 / d[cot_dt]).between(5, 250).all(), f"{f}: có đơn giá vô lý"
        if "tap" in d:
            assert not set(d.loc[d["tap"] == "train", "nhom"]) & set(d.loc[d["tap"] == "test", "nhom"]), f"{f}: nhóm chung giữa train và test"

@kiem("Mô hình đã lưu nạp lại được và dự đoán ra số hợp lý")
def _():
    import joblib
    from mo_hinh_gia import khong_dau
    for f, du_lieu in [("mo_hinh_gia_nha.joblib", "nha_da_xu_ly.csv"), ("mo_hinh_gia_can_ho.joblib", "can_ho_da_xu_ly.csv")]:
        goi = joblib.load(GOC / "model" / f)
        d = pd.read_csv(GOC / "data" / "processed" / du_lieu).head(20)
        d["van_ban"] = d["tieu_de"].fillna("").map(khong_dau)
        p = np.exp(goi["model"].predict(d))
        assert np.isfinite(p).all() and (p > 0.1).all() and (p < 100).all(), f"{f}: dự đoán bất thường"
        sai = np.median(np.abs(p / d["gia_ty"] - 1))
        assert sai < 0.5, f"{f}: sai số trung vị trên dữ liệu học {sai:.0%} – mô hình có vẻ hỏng"

@kiem("Khoảng 80% đã lưu cho nhà phố theo mức giá: nhà đắt có biên độ rộng hơn nhà rẻ")
def _():
    import joblib
    k = joblib.load(GOC / "model" / "mo_hinh_gia_nha.joblib")["khoang_theo_muc"]
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
    sys.path.insert(0, str(GOC / "cong_cu"))
    from an_danh_du_lieu import TRUONG_NGUOI_BAN, an_danh_tin, an_danh_bang
    for f in sorted((GOC / "data").rglob("*.jsonl")):
        dong = [l for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]
        for i, l in enumerate(dong):
            a = json.loads(l)                                   # lỗi -> phép kiểm không đạt
            assert not (TRUONG_NGUOI_BAN & set(a)), f"{f.name} dòng {i + 1}: còn trường người đăng {TRUONG_NGUOI_BAN & set(a)}"
            # ẩn danh thêm lần nữa mà không đổi gì = không còn SĐT ở bất kỳ trường chữ nào
            assert an_danh_tin(json.loads(l)) == a, f"{f.name} dòng {i + 1}: còn số điện thoại"
    for f in sorted((GOC / "data").rglob("*.csv")) + sorted((GOC / "ket_qua").glob("*.csv")):
        n = an_danh_bang(pd.read_csv(f, dtype=str, keep_default_na=False))[1]
        assert n == 0, f"{f.name}: còn {n} ô có số điện thoại"

@kiem("Số liệu viết trong notebook chính và README khớp kết quả đã lưu (không lệch sau khi chạy lại với dữ liệu mới)")
def _():
    # Phần nhận xét là markdown viết tay; dữ liệu cập nhật định kỳ thì số liệu thật đổi. Phép kiểm này bắt chỗ quên sửa chữ.
    import json
    dg = json.loads((GOC / "model" / "danh_gia_mo_hinh.json").read_text(encoding="utf-8"))
    vn = lambda x, d=1: f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    chon = dg["ten_mo_hinh"]
    te_ph = next(m for m in dg["test_phu_hoa"] if m["Mô hình"] == chon)
    te_tdm = next(m for m in dg["test_tdm"] if m["Mô hình"] == chon)
    cv_ph = next(m for m in dg["kiem_dinh_cheo_phu_hoa"] if m["Mô hình"] == chon)
    can = {"tên mô hình được chọn": chon, "số căn sau làm sạch": vn(dg["so_can"]["tat_ca"], 0),
           "MAPE test Phú Hòa": vn(te_ph["MAPE (%)"]), "MAPE test Thủ Dầu Một": vn(te_tdm["MAPE (%)"])}
    nb = json.loads((GOC / "notebooks" / "2324801030095.ipynb").read_text(encoding="utf-8"))
    md = "\n".join("".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "markdown")
    thieu = [f"{k} = {v}" for k, v in can.items() if v not in md]
    assert not thieu, "markdown notebook chính chưa cập nhật: " + "; ".join(thieu)
    readme = (GOC / "README.md").read_text(encoding="utf-8")
    can_rm = {"tên mô hình": chon, "MAPE test Phú Hòa": vn(te_ph["MAPE (%)"]), "MAPE kiểm định chéo Phú Hòa": vn(cv_ph["MAPE (%)"])}
    thieu = [f"{k} = {v}" for k, v in can_rm.items() if v not in readme]
    assert not thieu, "README chưa cập nhật: " + "; ".join(thieu)

for ten, ok, loi in KQ:
    print(("ĐẠT       " if ok else "KHÔNG ĐẠT ") + ten + ("" if ok else f"\n           -> {loi}"))
print(f"\n{sum(ok for _, ok, _ in KQ)}/{len(KQ)} phép kiểm đạt")
sys.exit(0 if all(ok for _, ok, _ in KQ) else 1)
