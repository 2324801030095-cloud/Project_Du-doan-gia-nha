"""Kiểm thử tự động cho mã dùng chung (src/mo_hinh_gia.py) và kết quả đã sinh ra.
Chạy từ thư mục gốc đề tài:  python tests/kiem_tra_mo_hinh.py
Mỗi phép kiểm in ĐẠT / KHÔNG ĐẠT; mã thoát khác 0 nếu có phép kiểm không đạt."""
import sys, traceback, warnings
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

@kiem("Đặc trưng giá khu vực không dùng giá của CHÍNH căn đó khi học (leave-one-out)")
def _():
    d = du_lieu_gia(); y = d["y"].to_numpy().copy()
    a = M.GiaLangGieng().fit_transform(d, y)
    y2 = y.copy(); y2[0] += 5.0                      # đổi hẳn giá căn số 0
    b = M.GiaLangGieng().fit_transform(d, y2)
    for c in ["lg_knn", "lg_knn_med", "lg_phuong", "lg_duong"]:
        assert abs(a[c].iloc[0] - b[c].iloc[0]) < 1e-9, f"{c} của căn 0 thay đổi khi đổi giá căn 0"

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

@kiem("Dữ liệu gốc đọc lại được và đã ẩn danh: mỗi dòng JSONL là 1 bản ghi hợp lệ (kể cả khi tách dòng kiểu Unicode), không còn thông tin người đăng / số điện thoại")
def _():
    import json, re
    sys.path.insert(0, str(GOC / "cong_cu"))
    from an_danh_du_lieu import TRUONG_NGUOI_BAN, SDT
    for f in sorted((GOC / "data").rglob("*.jsonl")):
        dong = [l for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]
        for i, l in enumerate(dong):
            a = json.loads(l)                                   # lỗi -> phép kiểm không đạt
            assert not (TRUONG_NGUOI_BAN & set(a)), f"{f.name} dòng {i + 1}: còn trường người đăng {TRUONG_NGUOI_BAN & set(a)}"
            assert not SDT.search(str(a.get("body", "")) + " " + str(a.get("subject", ""))), f"{f.name} dòng {i + 1}: còn số điện thoại"
    for f in sorted((GOC / "data").rglob("*.csv")):
        d = pd.read_csv(f, dtype=str, keep_default_na=False)
        for c in [c for c in d.columns if c in ("mo_ta", "tieu_de")]:
            assert not d[c].str.contains(SDT).any(), f"{f.name}: cột {c} còn số điện thoại"

for ten, ok, loi in KQ:
    print(("ĐẠT       " if ok else "KHÔNG ĐẠT ") + ten + ("" if ok else f"\n           -> {loi}"))
print(f"\n{sum(ok for _, ok, _ in KQ)}/{len(KQ)} phép kiểm đạt")
sys.exit(0 if all(ok for _, ok, _ in KQ) else 1)
