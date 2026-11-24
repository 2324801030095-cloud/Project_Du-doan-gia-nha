"""Sinh notebook notebooks/du_doan_gia_thue.ipynb (giá thuê + tỷ suất cho thuê).
Chạy từ thư mục gốc đề tài:  python cong_cu/dung_notebook_gia_thue.py notebooks/du_doan_gia_thue.ipynb
Cần chạy SAU notebook nhà phố và căn hộ (dùng data/processed/*_da_xu_ly.csv để tính tỷ suất cho thuê).
"""
import sys
import nbformat as nbf

cells = []
md = lambda s: cells.append(nbf.v4.new_markdown_cell(s.strip()))
code = lambda s: cells.append(nbf.v4.new_code_cell(s.strip()))

md(r"""
# GIÁ THUÊ VÀ TỶ SUẤT CHO THUÊ – NHÀ PHỐ VÀ CĂN HỘ (Thủ Dầu Một và vùng lân cận)

**Mã sinh viên:** 2324801030095
**Họ và tên:** Nguyễn Quang Long
**Lớp:** D23KTPM01
**Môn:** Học máy

Hai notebook định giá trả lời *"căn này đáng giá bao nhiêu?"*. Người mua để đầu tư còn hỏi: **cho thuê được bao nhiêu mỗi tháng, và bao nhiêu năm thì hoàn vốn?** Notebook này:

1. Xây **mô hình dự đoán giá thuê** (triệu đồng/tháng) cho căn hộ và nhà phố, từ **tin cho thuê thật** trên Chợ Tốt Nhà (dữ liệu tải cùng lúc với tin bán, trước đây bị bỏ đi).
2. Dùng mô hình giá thuê để ước lượng giá thuê của **từng căn đang rao bán**, rồi tính **tỷ suất cho thuê gộp** = 12 × giá thuê / giá bán và **số năm hoàn vốn** = giá bán / (12 × giá thuê).
3. **Kiểm chứng chéo** tỷ suất của mô hình với tỷ suất tính thẳng từ dữ liệu ở những dự án có cả tin bán lẫn tin cho thuê.

**Lưu ý phương pháp:** mô hình giá thuê **không dùng mô tả tin**, chỉ dùng thông số căn nhà và vị trí. Lý do: mô hình sẽ được áp dụng cho tin **rao bán**, mà lời văn của tin bán khác hẳn tin cho thuê. Dùng mô tả sẽ làm dự đoán lệch một cách khó kiểm soát.

> Chạy sau 2 notebook định giá (cần `data/processed/nha_da_xu_ly.csv`, `can_ho_da_xu_ly.csv`). Khoảng 3 phút.
""")

md(r"""
**Phạm vi kiến thức** (toàn bộ notebook này là **phần mở rộng** của đề tài; notebook chính `2324801030095.ipynb` mới là bài làm theo môn học):

| Trong môn học (bài giảng / thực hành) | Ngoài môn học (nâng cao) |
|---|---|
| Làm sạch tin cho thuê (TH4); hồi quy tuyến tính có phạt (Ridge, mô hình được chọn); kiểm định chéo K-fold; MAE, MAPE | LightGBM để so sánh; chia fold theo nhóm; dùng mô hình học trên tin thuê để ước lượng cho tin bán (chuyển miền) |
""")


code(r"""
import re, sys, warnings
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from IPython.display import display

GOC = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
sys.path.insert(0, str(GOC / "src"))
RAW, PROC, MODEL_DIR, KET_QUA = GOC / "data" / "raw", GOC / "data" / "processed", GOC / "model", GOC / "ket_qua"
from mo_hinh_gia import (khong_dau, ten_phuong, ten_quan, ten_duong, ten_du_an, trich_dac_trung_chu, nhom_gan_trung,
                         MoHinhGia, du_doan_cheo_lap, sai_so_tung_can, ktc_bootstrap, bang_danh_gia, hieu_chinh_khoang)
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.linear_model import RidgeCV
from sklearn.model_selection import GroupShuffleSplit
from lightgbm import LGBMRegressor

warnings.filterwarnings("ignore")
sns.set_theme(style="whitegrid", context="notebook")
pd.set_option("display.width", 200); pd.set_option("display.max_columns", 30)
RANDOM_STATE, SO_LAN = 42, 3

raw_nha = pd.read_csv(RAW / "chotot_binh_duong_raw.csv")
raw_ch = pd.read_csv(RAW / "chotot_can_ho_raw.csv")
thue_nha, thue_ch = raw_nha[raw_nha["loai_tin"] == "cho_thue"].copy(), raw_ch[raw_ch["loai_tin"] == "cho_thue"].copy()
print(f"Tin cho thuê nhà: {len(thue_nha)} | tin cho thuê căn hộ: {len(thue_ch)} (Chợ Tốt, thu thập {raw_nha['ngay_thu_thap'].iloc[0]})")
pd.DataFrame({"Nhà": thue_nha["quan_huyen"].value_counts(), "Căn hộ": thue_ch["quan_huyen"].value_counts()}).fillna(0).astype(int)
""")

md(r"""
## Bước 1: Làm sạch tin cho thuê
Giá trên tin cho thuê là **đồng/tháng**. Các quy tắc loại bỏ:
- **Không phải thuê nguyên căn**: phòng trọ, ở ghép, thuê theo phòng, homestay, thuê theo ngày/giờ, sang nhượng.
- **Giá ghi sai đơn vị hoặc vô lý**: ngoài 1,5–150 triệu/tháng (nhà) hoặc 1,5–60 triệu/tháng (căn hộ); giá thuê theo m² ngoài khoảng hợp lý.
- **Tin trùng khớp hẳn** (cùng quận, cùng giá, cùng diện tích): giữ 1. Tin **gần trùng** được gom nhóm để đánh giá không rò rỉ (như hai notebook định giá).

Cột `gia_ty` ở đây chứa **giá thuê tính bằng triệu đồng/tháng**, để dùng lại được các hàm đánh giá chung.
""")

code(r"""
LOAI_BO = r"phong tro|o ghep|\bghep\b|thue phong|cho thue phong|homestay|theo ngay|theo gio|ngan han|sang nhuong|sang lai|\bsang\b quan|ky tuc|giuong"
NOI_THAT = {"Nội thất cao cấp": 3, "Nội thất đầy đủ": 2, "Hoàn thiện cơ bản": 1, "Bàn giao thô": 0, "Nhà trống": 0}

def chuan_bi(t, can_ho):
    d = pd.DataFrame({
        "id": t["id"].astype(str), "url": t["url"], "tieu_de": t["tieu_de"], "mo_ta": t["mo_ta"].fillna(""),
        "gia_ty": t["gia"] / 1e6,                                               # TRIỆU đồng / tháng
        "dt_dat": (t["dt_su_dung"] if can_ho else t["dt_dat"]).astype(float),
        "phong_ngu": t["phong_ngu"], "so_wc": t["so_wc"], "quan": t["quan_huyen"].map(ten_quan), "phuong": t["phuong"].map(ten_phuong),
        "lat": t["lat"], "lon": t["lon"], "noi_that_cap": t["noi_that"].map(NOI_THAT),
    })
    d["van_ban"] = (d["tieu_de"].fillna("") + " . " + d["mo_ta"]).map(khong_dau)
    if can_ho:
        d["du_an"] = t["du_an"].map(ten_du_an).values; d["du_an_goc"] = t["du_an"].values
        d["tang_so"] = pd.to_numeric(t["tang_so"], errors="coerce").values
        d["noxh"] = (t["loai_can_ho"] == "Nhà ở xã hội").astype(float).values
        ds = sorted({x for x in d["du_an"].dropna() if len(x) >= 5}, key=lambda x: (-len(x), x))
        d["du_an"] = d["du_an"].fillna(d["van_ban"].map(lambda s: next((x for x in ds if x in s), None)))
        d["duong"] = d["du_an"]
    else:
        d["ngang"], d["dai"] = t["ngang"].values, t["dai"].values
        d["so_tang"] = t["so_tang"].where(t["so_tang"].between(1, 8)).values
        d["dt_san"] = t["dt_su_dung"].values
        d["mat_tien_duong"] = (t["loai_nha"] == "Nhà mặt tiền").astype(float).values
        d["duong"] = t["duong"].map(ten_duong).values
        d["noi_that"] = (d["noi_that_cap"] >= 2).astype(float).where(d["noi_that_cap"].notna())
    T = trich_dac_trung_chu(d["van_ban"])
    d = pd.concat([d, T], axis=1)
    d["phong_ngu"] = d["phong_ngu"].where(d["phong_ngu"].between(0, 10)).fillna(d["t_pn"])
    d["so_wc"] = d["so_wc"].where(d["so_wc"].between(1, 10)).fillna(d["t_wc"])
    if not can_ho:
        d["ngang"] = d["ngang"].fillna(d["t_ngang"]).fillna(d["t_kt_ngang"]); d["dai"] = d["dai"].fillna(d["t_kt_dai"])
        nd = d["ngang"] * d["dai"]
        sai_dt = nd.between(25, 1000) & (d["dt_dat"].isna() | ((((d["dt_dat"] - d["dai"]).abs() <= 1) | ((d["dt_dat"] - d["ngang"]).abs() <= 0.5)) & (d["dt_dat"] < 0.6 * nd)))
        d.loc[sai_dt, "dt_dat"] = nd[sai_dt]
        d["so_tang"] = d["so_tang"].fillna(d["t_so_tang"])
        d["hem_rong"] = d["t_hem_rong"]
        tu_rong = pd.cut(d["hem_rong"], [0, 2.5, 3.5, 5, 7, 10, 100], labels=[0, 1, 2, 3, 4, 4.5], right=False).astype(float)
        cap = pd.Series(np.where(d["mat_tien_duong"] == 1, 5, np.nan), index=d.index).fillna(tu_rong)
        d["cap_loi_vao"] = cap.where(cap.notna(), np.where(d["t_hem_xe_hoi"] == 1, 2, np.where(d["t_hem_nho"] == 1, 0.5, np.nan)))
        d["ty_le_san"] = d["dt_san"] / d["dt_dat"]
    else:
        tang = pd.to_numeric(d["van_ban"].str.extract(r"\btang (\d{1,2})\b", expand=False), errors="coerce")
        d["tang_so"] = d["tang_so"].where(d["tang_so"].between(1, 60)).fillna(tang.where(tang.between(1, 60)))
        d["noi_that_cap"] = d["noi_that_cap"].fillna(pd.Series(np.where(d["t_noi_that"] == 1, 2.0, np.nan), index=d.index))
    return d

def lam_sach(d, can_ho):
    n0 = len(d)
    ly_do = pd.Series("", index=d.index)
    ly_do[d["van_ban"].str.contains(LOAI_BO)] = "Không phải thuê nguyên căn / ngắn hạn"
    gmax = 60 if can_ho else 150
    ly_do[(ly_do == "") & ~d["gia_ty"].between(1.5, gmax)] = "Giá ngoài phạm vi"
    ly_do[(ly_do == "") & ~d["dt_dat"].between(20, 250 if can_ho else 1000)] = "Diện tích thiếu / ngoài phạm vi"
    don_gia = d["gia_ty"] * 1000 / d["dt_dat"]                                       # nghìn đồng / m² / tháng
    ly_do[(ly_do == "") & ~don_gia.between(30 if can_ho else 15, 600 if can_ho else 800)] = "Giá thuê theo m² vô lý"
    print(("Căn hộ" if can_ho else "Nhà") + ": loại", (ly_do != "").sum(), "/", n0, ly_do[ly_do != ""].value_counts().to_dict())
    d = d[ly_do == ""].copy()
    d = d.groupby(["quan", (d["gia_ty"] * 10).round(), d["dt_dat"].round()], as_index=False).first()   # trùng khớp hẳn
    d = d[d["lat"].between(10.82, 11.65) & d["lon"].between(106.30, 106.95)].reset_index(drop=True)
    d["y"] = np.log(d["gia_ty"]); d["log_dt"] = np.log(d["dt_dat"])
    d["tdm"] = (d["quan"] == "thu dau mot").astype(int); d["phu_hoa"] = (d["phuong"] == "phu hoa").astype(int)
    d["kc_trung_tam_km"] = np.hypot((d["lat"] - 10.9805) * 110.6, (d["lon"] - 106.6520) * 109.3)
    if can_ho:
        d["ngang"] = np.nan; d["dai"] = np.nan
    d["nhom"] = nhom_gan_trung(d, dung_vi_tri=not can_ho)
    return d

ch = lam_sach(chuan_bi(thue_ch, True), True)
nha = lam_sach(chuan_bi(thue_nha, False), False)
print(f"Còn lại: căn hộ {len(ch)} tin ({ch['du_an'].nunique()} dự án, TDM {ch['tdm'].sum()}) | nhà {len(nha)} tin (TDM {nha['tdm'].sum()})")
""")

md(r"""
## Bước 2: Khám phá giá thuê
""")

code(r"""
fig, axes = plt.subplots(1, 3, figsize=(17, 4.3))
sns.boxplot(x=ch["phong_ngu"].clip(upper=3).map({0: "Studio", 1: "1 PN", 2: "2 PN", 3: "3+ PN"}), y=ch["gia_ty"], order=["Studio", "1 PN", "2 PN", "3+ PN"],
            ax=axes[0], showfliers=False, color="#8fb3d9"); axes[0].set(title="Căn hộ: giá thuê theo số phòng ngủ", xlabel="", ylabel="triệu đồng / tháng")
noi_that = ch["noi_that_cap"].map({0: "Thô", 1: "Cơ bản", 2: "Đầy đủ", 3: "Cao cấp"}).fillna("Không rõ")
sns.boxplot(x=noi_that, y=ch["gia_ty"] * 1000 / ch["dt_dat"], order=["Thô", "Cơ bản", "Đầy đủ", "Cao cấp", "Không rõ"], ax=axes[1], showfliers=False, color="#b6d7a8")
axes[1].set(title="Căn hộ: giá thuê/m² theo nội thất", xlabel="", ylabel="nghìn đồng / m² / tháng")
loai = np.where(nha["mat_tien_duong"] == 1, "Mặt tiền", "Trong hẻm / khác")
sns.boxplot(x=loai, y=nha["gia_ty"], ax=axes[2], showfliers=False, color="#f4cccc"); axes[2].set(title="Nhà: giá thuê theo lối vào", xlabel="", ylabel="triệu đồng / tháng")
plt.tight_layout(); plt.show()
print("Giá thuê trung vị – căn hộ:", round(ch["gia_ty"].median(), 1), "triệu/tháng | nhà:", round(nha["gia_ty"].median(), 1), "triệu/tháng")
""")

md(r"""
**Quan sát:** giá thuê căn hộ tăng theo số phòng ngủ và mức nội thất (căn đầy đủ nội thất cho thuê đắt hơn rõ). Nhà mặt tiền cho thuê đắt hơn nhà trong hẻm (trung vị khoảng 10 so với 8,5 triệu/tháng) vì có thể dùng để **kinh doanh**.

## Bước 3: Mô hình giá thuê
Cùng quy trình hai notebook định giá: tập test giữ riêng 20% số nhóm; kiểm định chéo 5-fold lặp 3 lần **chia theo nhóm** trên tập train; chọn mô hình **đơn giản nhất không kém mô hình tốt nhất một cách có ý nghĩa**.

| Mô hình | Ý tưởng |
|---|---|
| Baseline | Giá thuê/m² trung vị của dự án (căn hộ) hoặc của phường (nhà) × diện tích |
| Ridge | Hồi quy tuyến tính trên log(giá thuê/m²) |
| LightGBM | Gradient boosting |

Đặc trưng: diện tích, phòng ngủ, WC, nội thất, (căn hộ: tầng, nhà ở xã hội; nhà: số tầng, ngang, dài, mặt tiền, lối vào, độ rộng hẻm), tọa độ, khoảng cách trung tâm, **giá thuê khu vực** (12 căn gần nhất, cùng phường, cùng dự án / tuyến đường – chỉ tính trên tập học).
""")

code(r"""
class BaselineThue(BaseEstimator, RegressorMixin):
    # giá thuê/m² trung vị của dự án (nếu >= 3 tin) -> của phường -> toàn bộ, nhân diện tích
    def fit(self, X, y):
        u = pd.Series(np.asarray(y) - np.log(X["dt_dat"].to_numpy()), index=X.index); self.g_ = u.median()
        g = u.groupby(X["duong"]); self.d_ = g.median()[g.size() >= 3]
        self.p_ = u.groupby(X["quan"] + "|" + X["phuong"].astype(str)).median(); return self
    def predict(self, X):
        k = X["quan"] + "|" + X["phuong"].astype(str)
        return X["duong"].map(self.d_).fillna(k.map(self.p_)).fillna(self.g_).to_numpy() + np.log(X["dt_dat"].to_numpy())

DT_CH = ["log_dt", "phong_ngu", "so_wc", "tang_so", "noi_that_cap", "noxh", "lat", "lon", "kc_trung_tam_km"]
DT_NHA = ["log_dt", "ngang", "dai", "so_tang", "dt_san", "ty_le_san", "phong_ngu", "so_wc", "mat_tien_duong", "cap_loi_vao", "hem_rong",
          "noi_that", "lat", "lon", "kc_trung_tam_km"]
lgb = lambda: LGBMRegressor(n_estimators=500, learning_rate=0.03, num_leaves=15, min_child_samples=10, subsample=0.8, subsample_freq=1,
                            colsample_bytree=0.7, verbose=-1, random_state=0, n_jobs=1)

def mo_hinh(dt, tang_bac):
    return {"Baseline (giá thuê/m² khu vực)": lambda: BaselineThue(),
            "Ridge": lambda: MoHinhGia(RidgeCV(alphas=np.logspace(-2, 3, 30)), dt, chuan_hoa=True, muc_tieu="don_gia", tang_bac=tang_bac),
            "LightGBM": lambda: MoHinhGia(lgb(), dt, muc_tieu="don_gia", tang_bac=tang_bac)}

def danh_gia(d, ten_loai, dt, tang_bac):
    _, vt = next(GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=RANDOM_STATE).split(d, groups=d["nhom"]))
    d = d.assign(tap=np.where(d.index.isin(vt), "test", "train"))
    tr, te = d[d["tap"] == "train"].reset_index(drop=True), d[d["tap"] == "test"].reset_index(drop=True)
    MH = mo_hinh(dt, tang_bac)
    OOF = {k: du_doan_cheo_lap(f, tr, so_lan=SO_LAN) for k, f in MH.items()}
    bang = bang_danh_gia(tr, OOF, np.ones(len(tr), bool)).rename(columns={"MAE (tỷ)": "MAE (triệu/tháng)"}).sort_values("MAPE (%)")
    print(f"== {ten_loai}: kiểm định chéo lặp {SO_LAN} lần ({len(tr)} tin train)"); display(bang.round(2))
    APE = {k: sai_so_tung_can(tr, P) for k, P in OOF.items()}
    uv = [k for k in MH if not k.startswith("Baseline")]
    tot = min(uv, key=lambda k: APE[k].mean())
    chon = tot
    for k in uv:                                   # đơn giản nhất mà không kém có ý nghĩa
        lo, _ = ktc_bootstrap(APE[k] - APE[tot], tr["nhom"].to_numpy()) if k != tot else (0, 0)
        if lo <= 0:
            chon = k; break
    lo, hi = ktc_bootstrap(APE["Baseline (giá thuê/m² khu vực)"] - APE[chon], tr["nhom"].to_numpy())
    print(f"Chọn: {chon} (MAPE thấp nhất: {tot}). So với baseline: giảm {np.mean(APE['Baseline (giá thuê/m² khu vực)'] - APE[chon]):.2f} điểm % (KTC 95% {lo:+.2f} … {hi:+.2f})")
    m = MH[chon]().fit(tr, tr["y"])
    bt = bang_danh_gia(te, {chon: m.predict(te), "Baseline": MH["Baseline (giá thuê/m² khu vực)"]().fit(tr, tr["y"]).predict(te)}, np.ones(len(te), bool))
    print(f"Tập test ({len(te)} tin):"); display(bt.rename(columns={"MAE (tỷ)": "MAE (triệu/tháng)"}).round(2))
    R = tr["y"].to_numpy() - OOF[chon]
    return {"ten": chon, "MH": MH, "bang": bang, "test": bt, "khoang": hieu_chinh_khoang(R.ravel(), np.zeros(R.size, int)), "d": d}

KQ_CH = danh_gia(ch, "CĂN HỘ cho thuê", DT_CH, True)
KQ_NHA = danh_gia(nha, "NHÀ cho thuê", DT_NHA, False)
""")

md(r"""
**Đọc kết quả:** giá thuê dễ dự đoán hơn giá bán, nhất là căn hộ: giá thuê ít bị "ảo" hơn giá rao bán, và căn hộ trong cùng dự án cho thuê giá khá đồng đều. Nhà phố cho thuê đa dạng hơn (nhà ở, mặt bằng kinh doanh), nên sai số lớn hơn.

## Bước 4: Tỷ suất cho thuê của các căn đang rao bán
Huấn luyện lại mô hình giá thuê đã chọn trên **toàn bộ** tin cho thuê, rồi ước lượng giá thuê cho **mỗi căn đang rao bán** (dữ liệu sạch của 2 notebook định giá).
- **Tỷ suất cho thuê gộp (gross yield)** = 12 × giá thuê ước tính / giá rao bán. Chưa trừ chi phí (thuế, sửa chữa, thời gian trống), nên tỷ suất thực nhận thấp hơn.
- **Số năm hoàn vốn** = giá rao bán / (12 × giá thuê).
""")

code(r"""
m_ch = KQ_CH["MH"][KQ_CH["ten"]]().fit(ch, ch["y"])
m_nha = KQ_NHA["MH"][KQ_NHA["ten"]]().fit(nha, nha["y"])

ban_ch = pd.read_csv(PROC / "can_ho_da_xu_ly.csv", dtype={"id": str})
ban_nha = pd.read_csv(PROC / "nha_da_xu_ly.csv", dtype={"id": str})
ban_ch["duong"] = ban_ch["du_an"]
ban_nha["noi_that"] = ban_nha["noi_that"].fillna(0)
ban_ch["thue_trieu"] = np.exp(m_ch.predict(ban_ch))
ban_nha["thue_trieu"] = np.exp(m_nha.predict(ban_nha))
for d in (ban_ch, ban_nha):
    d["ty_suat_pt"] = d["thue_trieu"] * 12 / (d["gia_ty"] * 1000) * 100
    d["hoan_von_nam"] = d["gia_ty"] * 1000 / (d["thue_trieu"] * 12)

tom = pd.DataFrame({
    "Căn hộ – toàn vùng": ban_ch["ty_suat_pt"].describe(percentiles=[.25, .5, .75]),
    "Căn hộ – Thủ Dầu Một": ban_ch.loc[ban_ch["tdm"] == 1, "ty_suat_pt"].describe(percentiles=[.25, .5, .75]),
    "Nhà phố – Thủ Dầu Một": ban_nha.loc[ban_nha["tdm"] == 1, "ty_suat_pt"].describe(percentiles=[.25, .5, .75]),
    "Nhà phố – Phú Hòa": ban_nha.loc[ban_nha["phu_hoa"] == 1, "ty_suat_pt"].describe(percentiles=[.25, .5, .75]),
}).T[["count", "25%", "50%", "75%"]].rename(columns={"count": "Số căn", "25%": "25% (%/năm)", "50%": "Trung vị (%/năm)", "75%": "75% (%/năm)"})
tom["Hoàn vốn trung vị (năm)"] = 100 / tom["Trung vị (%/năm)"]
display(tom.round(2))
""")

md(r"""
**Kiểm chứng chéo:** với các dự án căn hộ có **cả tin bán lẫn tin cho thuê**, tính tỷ suất **thẳng từ dữ liệu** = 12 × giá thuê/m² trung vị / giá bán/m² trung vị, rồi so với tỷ suất trung vị mà mô hình ước lượng cho các căn đang bán của dự án đó. Nếu hai con số gần nhau, mô hình giá thuê áp dụng cho tin bán là đáng tin.
""")

code(r"""
thue_m2 = ch.groupby("du_an").agg(n_thue=("y", "size"), thue_m2=("gia_ty", lambda s: np.median(s / ch.loc[s.index, "dt_dat"])))
ban_m2 = ban_ch.groupby("du_an").agg(n_ban=("y", "size"), ban_m2=("don_gia", "median"), ty_suat_mo_hinh=("ty_suat_pt", "median"))
kc = thue_m2.join(ban_m2, how="inner").query("n_thue >= 5 and n_ban >= 5")
kc["ty_suat_du_lieu"] = kc["thue_m2"] * 12 / kc["ban_m2"] * 100
kc = kc.sort_values("ty_suat_du_lieu", ascending=False)
display(kc[["n_thue", "n_ban", "ty_suat_du_lieu", "ty_suat_mo_hinh"]].round(2))
r_ = np.corrcoef(kc["ty_suat_du_lieu"], kc["ty_suat_mo_hinh"])[0, 1]
print(f"{len(kc)} dự án có ≥ 5 tin bán và ≥ 5 tin thuê | tương quan giữa hai cách tính: {r_:.2f} | "
      f"chênh trung vị (mô hình − dữ liệu): {np.median(kc['ty_suat_mo_hinh'] - kc['ty_suat_du_lieu']):+.2f} điểm %")
""")

md(r"""
**Đọc kết quả:** nếu tương quan cao và chênh lệch trung vị nhỏ, tỷ suất do mô hình ước lượng cho từng căn đang bán khớp với thực tế thị trường cho thuê của dự án đó.

## Bước 5: Tỷ suất cho thuê theo khu vực và dự án
""")

code(r"""
ten_ph = {ten_phuong(p): re.sub(r"^(Phường|Xã|Thị trấn)\s*", "", p) for p in pd.concat([raw_nha["phuong"], raw_ch["phuong"]]).dropna().unique()}
ph_nha = (ban_nha[ban_nha["tdm"] == 1].groupby("phuong").agg(so_can=("y", "size"), gia_tv=("gia_ty", "median"), thue_tv=("thue_trieu", "median"), ty_suat=("ty_suat_pt", "median"))
          .query("so_can >= 8").sort_values("ty_suat", ascending=False))
ph_nha.index = ph_nha.index.map(lambda k: ten_ph.get(k, k))
print("Nhà phố – Thủ Dầu Một, theo phường:"); display(ph_nha.round(2))
da = (ban_ch.groupby("du_an").agg(ten=("du_an_goc", lambda s: s.dropna().mode()[0] if s.notna().any() else None), quan=("quan", "first"), so_can=("y", "size"),
                                 gia_tv=("gia_ty", "median"), thue_tv=("thue_trieu", "median"), ty_suat=("ty_suat_pt", "median"))
      .query("so_can >= 5").sort_values("ty_suat", ascending=False))
print("Căn hộ, theo dự án (≥ 5 căn đang bán):"); display(da.head(12).round(2))

fig, axes = plt.subplots(1, 2, figsize=(15, 4.5))
sns.histplot(ban_ch["ty_suat_pt"], bins=40, ax=axes[0], color="#4C72B0", label="Căn hộ", stat="density", alpha=0.6)
sns.histplot(ban_nha.loc[ban_nha["tdm"] == 1, "ty_suat_pt"], bins=40, ax=axes[0], color="#C44E52", label="Nhà phố TDM", stat="density", alpha=0.6)
axes[0].set(title="Phân bố tỷ suất cho thuê gộp", xlabel="% / năm"); axes[0].legend()
axes[1].scatter(ban_ch["gia_ty"], ban_ch["ty_suat_pt"], s=10, alpha=0.4, label="Căn hộ")
axes[1].scatter(ban_nha.loc[ban_nha["tdm"] == 1, "gia_ty"], ban_nha.loc[ban_nha["tdm"] == 1, "ty_suat_pt"], s=10, alpha=0.4, color="#C44E52", label="Nhà phố TDM")
axes[1].set(xscale="log", title="Tỷ suất cho thuê theo giá bán", xlabel="Giá rao bán (tỷ, log)", ylabel="% / năm"); axes[1].legend()
plt.tight_layout(); plt.show()
""")

md(r"""
**Quan sát:**
- **Căn hộ cho tỷ suất cho thuê cao hơn nhà phố**: căn hộ dễ cho thuê (gần khu công nghiệp, khu đô thị), còn giá nhà phố chủ yếu nằm ở **giá trị đất**, giá thuê không theo kịp.
- **Căn càng đắt thì tỷ suất càng thấp** (tương quan hạng giữa giá bán và tỷ suất: khoảng −0,6 với nhà phố, −0,7 với căn hộ): giá bán tăng nhanh hơn giá thuê. Người mua nhà phố đắt tiền chủ yếu kỳ vọng **tăng giá đất**, không phải dòng tiền cho thuê.
- Tỷ suất ở đây là **gộp**. Sau khi trừ thuế cho thuê, phí quản lý, sửa chữa và thời gian nhà trống, tỷ suất thực nhận thường thấp hơn 1–2 điểm %.

## Bước 6: Lưu mô hình và kết quả
- `model/mo_hinh_gia_thue.joblib`: hai mô hình giá thuê + phân vị sai số (khoảng 80%).
- `model/gia_thue_web.json`: bảng giá thuê/m² theo dự án và phường (cho trang demo, trợ lý hỏi đáp).
- `ket_qua/ty_suat_cho_thue.csv`: giá thuê ước tính, tỷ suất, số năm hoàn vốn của từng căn đang rao bán ở Thủ Dầu Một.
""")

code(r"""
import json, joblib
joblib.dump({"can_ho": m_ch, "nha": m_nha, "ten": {"can_ho": KQ_CH["ten"], "nha": KQ_NHA["ten"]},
             "khoang": {"can_ho": KQ_CH["khoang"], "nha": KQ_NHA["khoang"]}, "ngay_du_lieu": str(raw_nha["ngay_thu_thap"].iloc[0])},
            MODEL_DIR / "mo_hinh_gia_thue.joblib")

# Bảng cho web: log giá thuê/m² theo dự án (co về phường khi ít tin) và theo phường; tỷ suất trung vị theo dự án/phường
def bang_m2(d, khoa, m=3.0):
    u = np.log(d["gia_ty"] / d["dt_dat"]); g = float(u.median())
    ph = u.groupby(d["quan"] + "|" + d["phuong"].astype(str)).agg(["sum", "count"]); ph_v = ((ph["sum"] + m * g) / (ph["count"] + m)).to_dict()
    out = {"toan_vung": round(g, 4), "phuong": {k: round(v, 4) for k, v in ph_v.items()}}
    if khoa:
        dd = pd.DataFrame({"u": u, "k": d[khoa], "ph": d["quan"] + "|" + d["phuong"].astype(str)}).dropna(subset=["k"])
        out["du_an"] = {k: round(float((x["u"].sum() + m * ph_v.get(x["ph"].mode()[0], g)) / (len(x) + m)), 4) for k, x in dd.groupby("k")}
        out["so_tin_du_an"] = dd.groupby("k").size().astype(int).to_dict()
    return out
web = {"can_ho": bang_m2(ch, "du_an"), "nha": bang_m2(nha, None),
       "ty_suat_tv": {"can_ho": round(float(ban_ch["ty_suat_pt"].median()), 2), "nha_tdm": round(float(ban_nha.loc[ban_nha["tdm"] == 1, "ty_suat_pt"].median()), 2)},
       "ty_suat_phuong_nha": {k: round(float(v), 2) for k, v in ban_nha[ban_nha["tdm"] == 1].groupby("phuong")["ty_suat_pt"].median().items()},
       "ty_suat_du_an": {k: round(float(v), 2) for k, v in ban_ch.groupby("du_an")["ty_suat_pt"].median().items()},
       "mape": {"can_ho": round(float(KQ_CH["bang"].loc[KQ_CH["ten"], "MAPE (%)"]), 1), "nha": round(float(KQ_NHA["bang"].loc[KQ_NHA["ten"], "MAPE (%)"]), 1)},
       "so_tin": {"can_ho": len(ch), "nha": len(nha)}, "ngay_du_lieu": str(raw_nha["ngay_thu_thap"].iloc[0])}
json.dump(web, open(MODEL_DIR / "gia_thue_web.json", "w", encoding="utf-8"), ensure_ascii=False)

cot = ["id", "nguon", "url", "phuong", "gia_ty", "thue_trieu", "ty_suat_pt", "hoan_von_nam"]
pd.concat([ban_nha.loc[ban_nha["tdm"] == 1, cot].assign(loai="Nhà phố", du_an=None, dien_tich_m2=ban_nha["dt_dat"]),
           ban_ch.loc[ban_ch["tdm"] == 1, cot + ["du_an_goc"]].rename(columns={"du_an_goc": "du_an"}).assign(loai="Căn hộ", dien_tich_m2=ban_ch["dt_dat"])]) \
  .round({"thue_trieu": 2, "ty_suat_pt": 2, "hoan_von_nam": 1}).to_csv(KET_QUA / "ty_suat_cho_thue.csv", index=False, encoding="utf-8-sig")
# lưu giá thuê ước tính vào dữ liệu đã xử lý để trang demo dùng
for d, f in [(ban_nha, "nha_da_xu_ly.csv"), (ban_ch, "can_ho_da_xu_ly.csv")]:
    goc = pd.read_csv(PROC / f, dtype={"id": str})
    goc["thue_uoc_luong_trieu"] = d["thue_trieu"].round(2).values; goc["ty_suat_cho_thue_pt"] = d["ty_suat_pt"].round(2).values
    goc.to_csv(PROC / f, index=False, encoding="utf-8-sig")
cot_t = ["id", "url", "tieu_de", "gia_ty", "dt_dat", "phong_ngu", "quan", "phuong", "lat", "lon", "duong"]
pd.concat([ch[cot_t].assign(loai="Căn hộ"), nha[cot_t].assign(loai="Nhà")]).rename(columns={"gia_ty": "thue_trieu_thang"})   .to_csv(PROC / "thue_da_xu_ly.csv", index=False, encoding="utf-8-sig")
print("Đã lưu:", "model/mo_hinh_gia_thue.joblib, model/gia_thue_web.json, ket_qua/ty_suat_cho_thue.csv, data/processed/thue_da_xu_ly.csv")
""")

md(r"""
## Kết luận
- Mô hình giá thuê học trên **tin cho thuê thật** (căn hộ và nhà phố), đánh giá bằng cùng quy trình khắt khe như hai mô hình định giá (sai số ở Bước 3).
- Áp mô hình cho từng căn đang rao bán cho ra **tỷ suất cho thuê gộp** và **số năm hoàn vốn**. Tỷ suất của mô hình được kiểm chứng chéo với tỷ suất tính thẳng từ dữ liệu ở các dự án có cả tin bán lẫn tin thuê.
- Kết luận đầu tư từ dữ liệu: căn hộ cho tỷ suất cho thuê cao hơn nhà phố; nhà phố đắt tiền chủ yếu là kênh giữ giá trị đất, ít sinh dòng tiền.

**Hạn chế:** giá thuê cũng là **giá rao**; tỷ suất là **gộp** (chưa trừ chi phí, thời gian trống); tin cho thuê nhà phố lẫn cả mặt bằng kinh doanh.
""")

nb = nbf.v4.new_notebook()
nb["cells"] = cells
nb["metadata"]["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
nbf.write(nb, sys.argv[1])
print("written", len(cells), "cells")
