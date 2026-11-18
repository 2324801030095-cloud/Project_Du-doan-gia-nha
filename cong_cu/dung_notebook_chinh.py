"""Sinh notebook notebooks/2324801030095.ipynb (nội dung markdown + code nằm trong script này).
Chạy từ thư mục gốc đề tài:  python cong_cu/dung_notebook_chinh.py notebooks/2324801030095.ipynb
Sau đó chạy notebook:       jupyter nbconvert --to notebook --execute --inplace notebooks/2324801030095.ipynb
"""
import sys
import nbformat as nbf

cells = []
md = lambda s: cells.append(nbf.v4.new_markdown_cell(s.strip()))
code = lambda s: cells.append(nbf.v4.new_code_cell(s.strip()))

md(r"""
# ĐỀ TÀI: MÔ HÌNH AI DỰ ĐOÁN GIÁ NHÀ Ở PHƯỜNG PHÚ HÒA, TP. THỦ DẦU MỘT (phiên bản 2)

**Mã sinh viên:** 2324801030095
**Họ và tên:** Nguyễn Quang Long
**Lớp:** D23KTPM01
**Môn:** Học máy

**Bài toán học máy** (theo định nghĩa trong bài giảng: chương trình học từ kinh nghiệm **E** để làm nhiệm vụ **T** tốt hơn theo độ đo **P**):
- **T (nhiệm vụ):** dự đoán giá rao bán (tỷ đồng) của một căn nhà từ các thông số của nó → **học có giám sát, hồi quy**.
- **E (kinh nghiệm):** các tin rao bán thật đã biết giá (dữ liệu huấn luyện).
- **P (độ đo):** sai số phần trăm trung bình **MAPE** trên những căn mô hình **chưa từng thấy** (tập test).

**Mô tả:** cho thông tin một căn nhà (diện tích, kích thước, số tầng, số phòng, lối vào, vị trí, mô tả tin), mô hình dự đoán **giá bán (tỷ đồng)** kèm **khoảng giá tin cậy**, rồi **chẩn đoán** giá rao đang rẻ, hợp lý hay cao so với mặt bằng thị trường. Đây là bài toán **học có giám sát – hồi quy**.

**Phiên bản 2 khắc phục các hạn chế của phiên bản 1** (bản cũ lưu ở `luu_tru/`):

| Hạn chế ở phiên bản 1 | Cách khắc phục trong phiên bản 2 |
|---|---|
| Chỉ 170 căn, 1 nguồn (guland) | Thu thập thêm **Chợ Tốt Nhà** (API công khai, toàn Bình Dương cũ) và **alonhadat** (Thủ Dầu Một): ~1.500 căn sau làm sạch, Phú Hòa ~220 căn |
| Không có vị trí chi tiết | Tọa độ từ Chợ Tốt; tin không có tọa độ được gán theo **tuyến đường** → tính **giá khu vực** (k căn gần nhất, phường, tuyến đường) |
| Chưa khai thác phần mô tả tin | Đọc **từ khóa** (khu dân cư, hẻm xe hơi, sổ riêng/sổ chung, nhà nát, dãy trọ, bán gấp…) và **mô hình chữ TF‑IDF** xếp chồng (stacking) |
| Tin rác lẫn vào dữ liệu | Quy tắc làm sạch có giải thích: tin cho thuê, nhà lắp ghép, nhà ở xã hội, giá mồi ("2 tỷ xxx"), đất chưa thổ cư, đơn giá lệch > 3 lần khu vực; **sửa** diện tích nhập nhầm |
| Chỉ có 1 con số dự đoán | **Khoảng giá 80%** hiệu chỉnh từ sai số ngoài-fold (ý tưởng conformal), có kiểm tra độ phủ trên tập test |
| Đánh giá trên 1 lần chia, 34 căn test | **Kiểm định chéo lặp 3 lần, chia theo nhóm tin gần trùng** (không rò rỉ), kèm khoảng tin cậy 95%; tập test giữ riêng chỉ để kiểm tra lần cuối |
| Chỉ thử mô hình mặc định | So sánh 6 mô hình + baseline; chọn **mô hình đơn giản nhất không kém mô hình tốt nhất một cách có ý nghĩa thống kê** |

**Phạm vi:** notebook này định giá **nhà gắn liền với đất** (nhà phố, nhà hẻm, liền kề, biệt thự). **Căn hộ chung cư** được định giá theo cơ chế khác (theo dự án và m² sử dụng), nên nằm ở notebook riêng `du_doan_gia_can_ho.ipynb`, dùng chung quy trình đánh giá.

**Toàn bộ dữ liệu là tin rao thật (guland 12/11/2026; Chợ Tốt và alonhadat: lần thu thập mới nhất, xem bảng ở Bước 1). Không có dữ liệu mô phỏng.**

**Cấu trúc notebook:**

| Phần | Các bước | Liên hệ tài liệu môn học |
|---|---|---|
| **PHẦN A – CƠ BẢN** | 1. Thu thập → 2. Hợp nhất → 3. Trích đặc trưng từ văn bản → 4. Làm sạch → 5. Khám phá dữ liệu → 6. Chia train/test → 7. Mô hình cơ bản: hồi quy tuyến tính, **cây quyết định** (quá khớp và chọn độ sâu) | Bài giảng: định nghĩa bài toán học máy, học từ ví dụ, cây quyết định. Thực hành: tiền xử lý dữ liệu (TH4), dữ liệu văn bản (TH6) |
| **PHẦN B – NÂNG CAO VÀ MỞ RỘNG** | 8. Giá khu vực, boosting, stacking, kiểm định chéo lặp + bootstrap, quy tắc chọn mô hình → 9. Kiểm tra trên test, giải thích sai số → 10. Khoảng giá 80% → 11. Chẩn đoán từng căn → 12. Lưu mô hình, giải thích SHAP | Kiến thức ngoài bài giảng, dùng để tăng độ chính xác và đo độ tin cậy của kết quả |

Các notebook khác (`du_doan_gia_can_ho`, `du_doan_gia_dat`, `du_doan_gia_thue`, `du_doan_xu_huong_gia`) đều thuộc **phần mở rộng**.

> Chạy lần lượt các ô từ trên xuống (Restart & Run All, khoảng 10 phút do có CatBoost và kiểm định chéo lặp). Các lớp mô hình nằm trong `src/mo_hinh_gia.py` để mô hình đã lưu nạp lại được ở notebook khác.
""")

md(r"""
---
# PHẦN A – CƠ BẢN (theo bài giảng và các bài thực hành)
---

## Bước 1: Thu thập dữ liệu

| Nguồn | Script | Phạm vi | Thông tin đặc biệt |
|---|---|---|---|
| guland.vn | `thu_thap/guland_thu_thap.js` (chạy trong trình duyệt) | Phường Phú Hòa | Bảng thông số chi tiết: loại hẻm, độ rộng hẻm, diện tích sàn |
| Chợ Tốt Nhà (nhatot.com) | `thu_thap/chotot_thu_thap.py` | Toàn Bình Dương cũ, loại "Nhà ở" | **Tọa độ**, ngang × dài, số tầng, phòng, WC, loại nhà, pháp lý, **giá gốc lúc đăng** |
| alonhadat.com.vn | `thu_thap/alonhadat_thu_thap.py` | TP. Thủ Dầu Một, loại nhà | Địa chỉ cũ kèm phường, kích thước, đường trước nhà, ngày đăng |

**Vì sao lấy cả khu vực ngoài Phú Hòa?** Mô hình học được quy luật chung (diện tích, số tầng, hẻm/mặt tiền… ảnh hưởng giá ra sao) từ nhiều căn hơn. Khác biệt về vị trí được mô hình xử lý bằng đặc trưng "giá khu vực". Bước 8 kiểm chứng điều này: huấn luyện trên toàn vùng cho sai số **trên chính các căn Phú Hòa** thấp hơn so với chỉ học trên Phú Hòa.

**Giới hạn:** giá là **giá rao bán**, chưa phải giá giao dịch. Không lưu tên, số điện thoại người đăng.
""")

code(r"""
import re
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from IPython.display import display

import sys
# Thư mục gốc của đề tài: notebook nằm trong notebooks/, mã dùng chung ở src/, dữ liệu ở data/
GOC = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
sys.path.insert(0, str(GOC / "src"))
RAW, PROC, LICH_SU = GOC / "data" / "raw", GOC / "data" / "processed", GOC / "data" / "lich_su"
MODEL_DIR, KET_QUA = GOC / "model", GOC / "ket_qua"
MODEL_DIR.mkdir(exist_ok=True); KET_QUA.mkdir(exist_ok=True); PROC.mkdir(parents=True, exist_ok=True)
from mo_hinh_gia import (khong_dau, ten_phuong, ten_quan, ten_duong, trich_dac_trung_chu, nhom_gan_trung,
                         MoHinhGia, XepChongChu, TrungBinhMoHinh, BaselineDonGiaPhuong, chi_so_danh_gia)

warnings.filterwarnings("ignore")
sns.set_theme(style="whitegrid", context="notebook")
pd.set_option("display.max_columns", 40)
pd.set_option("display.width", 200)

RANDOM_STATE = 42

raw_guland = pd.read_csv(RAW / "nha_phu_hoa_guland_raw.csv")
raw_guland = raw_guland[raw_guland["loai_bds"] == "Nhà phố"].reset_index(drop=True)   # script thu thập mới trả về mọi loại BĐS
raw_chotot = pd.read_csv(RAW / "chotot_binh_duong_raw.csv")
raw_alon = pd.read_csv(RAW / "alonhadat_tdm_raw.csv")
pd.DataFrame({
    "Số tin": [len(raw_guland), len(raw_chotot), len(raw_alon)],
    "Ngày thu thập": [raw_guland["ngay_thu_thap"].iloc[0], raw_chotot["ngay_thu_thap"].iloc[0], raw_alon["ngay_thu_thap"].iloc[0]],
}, index=["guland (Phú Hòa)", "Chợ Tốt (Bình Dương cũ)", "alonhadat (Thủ Dầu Một)"])
""")

code(r"""
print("Chợ Tốt - loại tin:", raw_chotot["loai_tin"].value_counts().to_dict())
print("Chợ Tốt - tin bán theo quận/huyện:")
raw_chotot[raw_chotot["loai_tin"] == "ban"]["quan_huyen"].value_counts().to_frame("Số tin bán")
""")

md(r"""
**Quan sát:** Chợ Tốt trả về cả **tin cho thuê** (giá theo tháng). Các tin này phải loại ngay, nếu không mô hình sẽ học nhầm giá thuê 5 triệu/tháng là giá bán. Tin bán tập trung ở Thủ Dầu Một, Dĩ An, Thuận An.

## Bước 2: Hợp nhất 3 nguồn về cùng một bảng
Mỗi nguồn đặt tên cột và đơn vị khác nhau. Ta đưa về một lược đồ chung (giá tỷ đồng, diện tích m², ngang/dài m, tên phường và tên đường viết thường không dấu để so khớp).
""")

code(r"""
def so(x):
    # '5,5m' -> 5.5
    if pd.isna(x):
        return np.nan
    m = re.search(r"\d+(?:[.,]\d+)?", str(x))
    return float(m.group().replace(",", ".")) if m else np.nan

# ten_phuong, ten_quan, ten_duong (chuẩn hóa tên để so khớp giữa các nguồn) nằm trong mo_hinh_gia.py

# --- guland ---
g = raw_guland
MA_VI_TRI = {"Hẻm nhỏ, sâu, cụt (< 2,5m)": 0, "Hẻm xe máy (2,5m ≤ rộng < 3,5m)": 1, "Hẻm 1 xe hơi (3,5m ≤ rộng < 5m)": 2,
             "Hẻm xe tải, 2 ô tô tránh (5m ≤ rộng < 7m)": 3, "Hẻm rất lớn, 2 xe tải tránh nhau (7m ≤ rộng < 10m)": 4,
             "Mặt đường chính": 5}
def tang_guland(r):
    k = r["tret_lau_mota"]
    if isinstance(k, str):
        if k == "cap4": return 1.0
        if k == "gac": return 1.5
        if k.startswith("1+"): return 1 + int(k[2:])
    return r["so_tang"]
G = pd.DataFrame({
    "nguon": "guland", "id": g["id"].astype(str), "url": g["url"], "ngay_dang": g["ngay_thu_thap"],
    "tieu_de": g["tieu_de"], "mo_ta": g["mo_ta"].fillna("") if "mo_ta" in g.columns else "",   # bản thu thập mới của guland có mô tả
    "gia_ty": g["gia"] / 1e9, "dt_dat": g["dt_dat"],
    "ngang": g["mat_tien"].replace(0, np.nan), "dai": g["chieu_dai"].replace(0, np.nan),
    "so_tang": g.apply(tang_guland, axis=1), "dt_san": g["dt_san"].replace(0, np.nan),
    "phong_ngu": g["phong_ngu"].fillna(g["pn_mota"]), "so_wc": g["phong_tam"].fillna(g["wc_mota"]),
    "mat_tien_duong": (g["vi_tri"] == "Mặt đường chính").astype(float).where(g["vi_tri"].notna()),
    "cap_loi_vao": g["vi_tri"].map(MA_VI_TRI), "hem_rong": g["hem_rong"].replace(0, np.nan),
    "quan": "thu dau mot", "phuong": "phu hoa", "duong": g["duong"].map(ten_duong),
    "lat": np.nan, "lon": np.nan, "toa_do_rieng": 0, "so_chung": np.nan,
    "noi_that": g["noi_that"].isin(["Đầy đủ nội thất", "Nội thất cơ bản"]).astype(float), "form_dac_diem": "",
})

# --- Chợ Tốt: chỉ tin bán ---
c = raw_chotot[raw_chotot["loai_tin"] == "ban"]
so_tin_cung_toa_do = c.groupby(["lat", "lon"])["id"].transform("size")
C = pd.DataFrame({
    "nguon": "chotot", "id": c["id"].astype(str), "url": c["url"], "ngay_dang": c["ngay_dang"],
    "tieu_de": c["tieu_de"], "mo_ta": c["mo_ta"].fillna(""), "gia_ty": c["gia"] / 1e9, "dt_dat": c["dt_dat"],
    "ngang": c["ngang"], "dai": c["dai"], "so_tang": c["so_tang"], "dt_san": c["dt_su_dung"],
    "phong_ngu": c["phong_ngu"], "so_wc": c["so_wc"],
    "mat_tien_duong": (c["loai_nha"] == "Nhà mặt tiền").astype(float),
    "cap_loi_vao": np.where(c["loai_nha"] == "Nhà mặt tiền", 5, np.nan), "hem_rong": np.nan,
    "quan": c["quan_huyen"].map(ten_quan), "phuong": c["phuong"].map(ten_phuong), "duong": c["duong"].map(ten_duong),
    "lat": c["lat"], "lon": c["lon"],
    # tọa độ "riêng" = gắn với 1 đối tượng bản đồ (osm) hoặc không bị dùng chung bởi nhiều tin (không phải tâm phường)
    "toa_do_rieng": (c["dia_chi_ma_vi_tri"].astype(str).str.startswith("osm") | (so_tin_cung_toa_do <= 3)).astype(int),
    "so_chung": c["phap_ly"].isin(["Sổ chung / công chứng vi bằng", "Giấy tờ viết tay"]).astype(float).where(c["phap_ly"].notna()),
    "noi_that": c["noi_that"].isin(["Nội thất đầy đủ", "Nội thất cao cấp"]).astype(float).where(c["noi_that"].notna()),
    "form_dac_diem": c["dac_diem"].fillna(""),
})

# --- alonhadat ---
a = raw_alon
kt = a["kich_thuoc"].fillna("").str.replace(",", ".").str.extract(r"([\d.]+)\s*x\s*([\d.]+)").astype(float)
dc = a["dia_chi_cu"].fillna("").str.split(",")
A = pd.DataFrame({
    "nguon": "alonhadat", "id": a["id"].astype(str), "url": a["url"], "ngay_dang": a["ngay_dang"],
    "tieu_de": a["tieu_de"], "mo_ta": a["mo_ta"].fillna(""), "gia_ty": pd.to_numeric(a["gia"]) / 1e9,
    "dt_dat": a["dt_dat"].map(so), "ngang": kt[0], "dai": kt[1], "so_tang": a["so_tang"].map(so), "dt_san": np.nan,
    "phong_ngu": a["phong_ngu"], "so_wc": np.nan,
    "mat_tien_duong": (a["loai_nha"] == "nha-mat-tien").astype(float),
    "cap_loi_vao": np.where(a["loai_nha"] == "nha-mat-tien", 5, np.nan), "hem_rong": a["duong_rong"].map(so),
    "quan": "thu dau mot", "phuong": dc.map(lambda p: ten_phuong(p[1]) if len(p) > 2 else None),
    "duong": dc.map(lambda p: ten_duong(p[0]) if len(p) > 2 else None),
    "lat": np.nan, "lon": np.nan, "toa_do_rieng": 0, "so_chung": np.nan, "noi_that": np.nan, "form_dac_diem": "",
})

df = pd.concat([G, C, A], ignore_index=True)
# Tọa độ nằm ngoài Bình Dương cũ (người đăng ghim nhầm sang tỉnh khác) -> coi như không có tọa độ
ngoai_vung = df["lat"].notna() & ~(df["lat"].between(10.82, 11.65) & df["lon"].between(106.30, 106.95))
df.loc[ngoai_vung, ["lat", "lon"]] = np.nan
df.loc[ngoai_vung, "toa_do_rieng"] = 0
print("Tin có tọa độ ngoài vùng (đã bỏ tọa độ):", int(ngoai_vung.sum()))
df["van_ban"] = (df["tieu_de"].fillna("") + " . " + df["mo_ta"].fillna("")).map(khong_dau)
print("Bảng hợp nhất:", df.shape)
df.groupby("nguon")[["dt_dat", "ngang", "dai", "so_tang", "dt_san", "phong_ngu", "so_wc", "hem_rong", "duong"]] \
  .agg(lambda s: s.notna().mean() * 100).round(0).T.rename_axis("% có dữ liệu")
""")

md(r"""
**Quan sát:** Mỗi nguồn mạnh ở một chỗ: guland có diện tích sàn và độ rộng hẻm; Chợ Tốt có số WC, diện tích sử dụng; alonhadat gần như luôn có kích thước và đường trước nhà. Phần còn thiếu sẽ được bổ sung từ **mô tả tin** ở Bước 3.

## Bước 3: Trích đặc trưng từ tiêu đề và mô tả tin
Người đăng thường viết thông tin quan trọng trong phần mô tả chứ không điền vào ô thông số: "hẻm xe hơi 6m", "1 trệt 2 lầu", "khu dân cư", "sổ riêng", "bán gấp"… Hàm `trich_dac_trung_chu` (trong `src/mo_hinh_gia.py`) dùng biểu thức chính quy trên văn bản đã bỏ dấu để tạo:
- **Cờ 0/1:** hẻm xe hơi, hẻm nhỏ, mặt tiền, khu dân cư, đường nội bộ, nhà cấp 4, nhà nát, nhà mới, sổ riêng, sổ chung/vi bằng, chưa hoàn công, căn góc, kinh doanh được, dãy trọ, bán gấp, nội thất, nở hậu, thổ cư, thang máy, biệt thự, gần trung tâm.
- **Số đo:** độ rộng hẻm/đường, ngang, kích thước "5x20", số tầng (từ "x trệt y lầu"), phòng ngủ, WC, diện tích sàn, diện tích thổ cư.
""")

code(r"""
T = trich_dac_trung_chu(df["van_ban"])
df = pd.concat([df, T], axis=1)

# Ô thông số trống -> lấy số đọc từ mô tả. Giá trị vô lý (ví dụ 30 tầng, 50 phòng ngủ) coi là thiếu.
df["ngang"] = df["ngang"].fillna(df["t_ngang"]).fillna(df["t_kt_ngang"])
df["dai"] = df["dai"].fillna(df["t_kt_dai"])
df["so_tang"] = df["so_tang"].where(df["so_tang"].between(1, 8)).fillna(df["t_so_tang"])
df["phong_ngu"] = df["phong_ngu"].where(df["phong_ngu"].between(1, 15)).fillna(df["t_pn"])
df["so_wc"] = df["so_wc"].where(df["so_wc"].between(1, 15)).fillna(df["t_wc"])
df["dt_san"] = df["dt_san"].fillna(df["t_dt_san"])
df["hem_rong"] = df["hem_rong"].where(df["hem_rong"].between(1.5, 60)).fillna(df["t_hem_rong"])
df["mat_tien_duong"] = df["mat_tien_duong"].fillna(df["t_mat_tien"])
df["so_chung"] = df["so_chung"].fillna(df["t_so_chung"])
df["noi_that"] = df["noi_that"].fillna(df["t_noi_that"])
f = df["form_dac_diem"]
df["t_hem_xe_hoi"] = (df["t_hem_xe_hoi"].astype(bool) | f.str.contains("Hẻm xe hơi")).astype(int)
df["t_no_hau"] = (df["t_no_hau"].astype(bool) | f.str.contains("nở hậu")).astype(int)
df["t_chua_hc"] = (df["t_chua_hc"].astype(bool) | f.str.contains("chưa hoàn công")).astype(int)
df["t_nha_nat"] = (df["t_nha_nat"].astype(bool) | f.str.contains("Nhà nát")).astype(int)

# Cấp lối vào 0..5 thống nhất cho mọi nguồn: hẻm nhỏ (0) ... mặt đường chính (5)
tu_do_rong = pd.cut(df["hem_rong"], [0, 2.5, 3.5, 5, 7, 10, 100], labels=[0, 1, 2, 3, 4, 4.5], right=False).astype(float)
cap = df["cap_loi_vao"].where(df["cap_loi_vao"].notna(), np.where(df["mat_tien_duong"] == 1, 5, np.nan))
cap = cap.fillna(tu_do_rong)
cap = cap.where(cap.notna(), np.where(df["t_hem_xe_hoi"] == 1, 2, np.where(df["t_hem_nho"] == 1, 0.5, np.nan)))
df["cap_loi_vao"] = cap

CO_CHU = [c for c in T.columns if T[c].dtype.kind == "i"]
(df[CO_CHU].mean() * 100).sort_values(ascending=False).round(1).to_frame("% số tin có nhắc tới").T
""")

md(r"""
**Quan sát:** Gần một nửa số tin nhắc tới "thổ cư", khoảng 1/4 nhắc "khu dân cư" và "sổ riêng", 1/6 có dấu hiệu "bán gấp / giảm giá". Đây là những thông tin phiên bản 1 chưa dùng tới (phiên bản 1 chỉ ra hạn chế: "chưa có đặc trưng khu dân cư").

## Bước 4: Làm sạch dữ liệu

### 4.1 Sửa diện tích nhập nhầm
Một số tin Chợ Tốt ghi **chiều dài vào ô diện tích** (ví dụ tiêu đề "5x28" nhưng diện tích = 28 m², đơn giá thành 70 triệu/m² ở vùng giá 15 triệu/m²). Nếu diện tích **trùng đúng** chiều dài (hoặc chiều ngang) và nhỏ hơn hẳn ngang × dài, ta sửa thành ngang × dài. Các trường hợp mơ hồ khác giữ nguyên.
""")

code(r"""
nd = df["ngang"] * df["dai"]
ghi_nham = ((df["dt_dat"] - df["dai"]).abs() <= 1) | ((df["dt_dat"] - df["ngang"]).abs() <= 0.5)
sua = nd.between(25, 1000) & (df["dt_dat"].isna() | (ghi_nham & (df["dt_dat"] < 0.6 * nd)))
display(df.loc[sua, ["nguon", "tieu_de", "gia_ty", "dt_dat", "ngang", "dai"]].head(6))
df.loc[sua, "dt_dat"] = nd[sua]
print(f"Đã sửa diện tích cho {sua.sum()} tin")
""")

md(r"""
### 4.2 Lọc phạm vi nhà ở dân dụng và loại tin trùng
- Giữ giá 0,5–60 tỷ, diện tích đất 25–1.000 m², đơn giá 5–250 triệu/m².
- **Tin trùng:** cùng một căn thường được đăng ở nhiều trang hoặc đăng lại. Coi là trùng nếu cùng quận, cùng giá (làm tròn 10 triệu) và cùng diện tích (làm tròn 1 m²). Mỗi nhóm trùng chỉ giữ 1 dòng, **ô nào trống thì lấy từ bản trùng khác** (ví dụ lấy tọa độ từ Chợ Tốt, độ rộng hẻm từ guland).
""")

code(r"""
n0 = len(df)
df = df[df["gia_ty"].between(0.5, 60) & df["dt_dat"].between(25, 1000)].copy()
df["don_gia"] = df["gia_ty"] * 1000 / df["dt_dat"]           # triệu/m² đất
df = df[df["don_gia"].between(5, 250)].copy()
n1 = len(df)
uu_tien = {"chotot": 0, "guland": 1, "alonhadat": 2}         # bản giữ lại ưu tiên nguồn có tọa độ
df = df.sort_values("nguon", key=lambda s: s.map(uu_tien), kind="stable")   # sắp xếp ổn định -> chạy lại cho cùng kết quả
df["nhom_trung"] = df.groupby(["quan", (df["gia_ty"] * 100).round(), df["dt_dat"].round()]).ngroup()
df["so_ban_trung"] = df.groupby("nhom_trung")["id"].transform("size")
df["cac_nguon"] = df.groupby("nhom_trung")["nguon"].transform(lambda s: "+".join(sorted(set(s))))
df = df.groupby("nhom_trung", as_index=False).first()
print(f"Ngoài phạm vi: {n0 - n1} tin | Trùng: {n1 - len(df)} tin | Còn lại: {len(df)} căn")
df["cac_nguon"].value_counts().head(6).to_frame("Số căn")
""")

md(r"""
**Quan sát:** Có nhiều tin trùng: cùng một căn được môi giới đăng ở cả Chợ Tốt, alonhadat và guland. Nếu không gộp lại, căn đó có thể vừa nằm trong tập train vừa nằm trong tập test, làm kết quả đánh giá **đẹp giả tạo**. Bước này chỉ bắt được tin trùng **khớp hẳn** giá và diện tích; các tin *gần trùng* (cùng căn nhưng đăng lại với giá khác vài %) được xử lý ở mục 4.4 bằng cách gom nhóm.

### 4.3 Gán tọa độ
Tọa độ là đầu vào cho đặc trưng "giá khu vực". Thứ tự ưu tiên:
1. Tọa độ riêng của tin trên Chợ Tốt (gắn với đối tượng bản đồ);
2. Tọa độ trung vị của **tuyến đường** đó (tính từ các tin Chợ Tốt có tọa độ riêng trên cùng đường). Nếu tin chưa ghi tên đường, tìm tên đường trong tiêu đề/mô tả (kể cả viết tắt NTMK, LHP);
3. Tâm **phường**; 4. Tâm quận.

Chỉ dùng vị trí, không dùng giá, nên bước này không làm rò rỉ nhãn.
""")

code(r"""
co_xy = df[df["toa_do_rieng"] == 1]
xy_duong = co_xy.groupby(["quan", "duong"])[["lat", "lon"]].median()
xy_phuong = df.dropna(subset=["lat"]).groupby(["quan", "phuong"])[["lat", "lon"]].median()
xy_quan = df.dropna(subset=["lat"]).groupby("quan")[["lat", "lon"]].median()

ds_duong = sorted({d for d in xy_duong.index.get_level_values(1) if isinstance(d, str) and len(d) >= 6},
                  key=lambda d: (-len(d), d))        # tên dài trước; cùng độ dài thì theo ABC -> chạy lại luôn cho cùng kết quả
VIET_TAT = {"ntmk": "nguyen thi minh khai", "lhp": "le hong phong", "dt743": "dt743"}
def tim_duong(t):
    for k, v in VIET_TAT.items():
        if re.search(rf"\b{k}\b", t):
            return v
    return next((d for d in ds_duong if d in t), None)
df["duong"] = df["duong"].fillna(df["van_ban"].map(tim_duong))

muc = []
for i, r in df.iterrows():
    if r["toa_do_rieng"] == 1:
        muc.append("1. tọa độ riêng"); continue
    if (r["quan"], r["duong"]) in xy_duong.index:
        df.loc[i, ["lat", "lon"]] = xy_duong.loc[(r["quan"], r["duong"])].values; muc.append("2. theo tuyến đường")
    elif (r["quan"], r["phuong"]) in xy_phuong.index:
        df.loc[i, ["lat", "lon"]] = xy_phuong.loc[(r["quan"], r["phuong"])].values; muc.append("3. tâm phường")
    else:
        df.loc[i, ["lat", "lon"]] = xy_quan.loc[r["quan"]].values; muc.append("4. tâm quận")
df["muc_toa_do"] = muc
TRUNG_TAM_TDM = (10.9805, 106.6520)       # chợ Thủ Dầu Một
df["kc_trung_tam_km"] = np.hypot((df["lat"] - TRUNG_TAM_TDM[0]) * 110.6, (df["lon"] - TRUNG_TAM_TDM[1]) * 109.3)
pd.crosstab(df["nguon"], df["muc_toa_do"])
""")

md(r"""
### 4.4 Loại tin không phản ánh giá nhà thị trường
Phân tích sai số ở bản nháp cho thấy phần lớn sai số rất lớn đến từ các tin **không phải giá một căn nhà ở bình thường**. Các quy tắc sau áp dụng như nhau cho mọi tin (cả train lẫn test), mỗi tin bị loại đều ghi lý do:

| Quy tắc | Lý do |
|---|---|
| Nhà gỗ lắp ghép, nhà tiền chế, "hoàn thiện toàn quốc" | Giá thi công, không phải giá bất động sản |
| Nhà ở xã hội | Giá do Nhà nước quy định, thị trường riêng |
| Tiêu đề là bán **căn hộ chung cư** (không nhắc "nhà", "mặt tiền") | Căn hộ đăng nhầm mục nhà; định giá ở notebook căn hộ |
| Giá mồi: "2 tỷ xxx", "giá 1,5 - 2 tỷ" | Số giá trên tin thấp hơn giá thật |
| Diện tích thổ cư < 50% diện tích đất | Phần lớn là đất nông nghiệp, đơn giá thấp hơn hẳn |
| Đơn giá lệch hơn **3 lần** so với trung vị 15 căn gần nhất | Gần như chắc chắn là lỗi nhập (sai đơn vị, nhầm diện tích) |
""")

code(r"""
from sklearn.neighbors import BallTree

ly_do = pd.Series("", index=df.index)
def danh_dau(mask, s):
    ly_do[mask & (ly_do == "")] = s
v = df["van_ban"]
danh_dau(v.str.contains(r"\bnha go\b[^.\n]{0,20}(?:hien dai|lap|tam hop|thi cong)|lap ghep|tien che|toan quoc|nha container|thi cong tron goi|khung thep"),
         "Nhà lắp ghép / thi công")
danh_dau(v.str.contains(r"nha o xa hoi|\bnoxh\b"), "Nhà ở xã hội")
tieu_de_kd = df["tieu_de"].fillna("").map(khong_dau)
danh_dau(tieu_de_kd.str.contains(r"can ho|chung cu|\bcan (?:happy|c sky|the )") & ~tieu_de_kd.str.contains(r"\bnha\b|mat tien|mini|day tro"),
         "Căn hộ chung cư đăng nhầm mục nhà")
danh_dau(v.str.contains(r"\d\s*(?:ty|t)\s*x{2,}|gia[^\n\d]{0,12}\d+(?:[.,]\d+)?\s*(?:ty)?\s*-\s*\d+(?:[.,]\d+)?\s*ty\b"), "Giá mồi / không rõ ràng")
danh_dau(df["t_dt_tho_cu"] / df["dt_dat"] < 0.5, "Thổ cư < 50% diện tích")
xy = np.radians(df[["lat", "lon"]].to_numpy())
u = np.log(df["don_gia"].to_numpy())
_, idx = BallTree(xy, metric="haversine").query(xy, k=16)
df["lech_log"] = np.abs(u - np.median(u[idx[:, 1:]], axis=1))       # |log đơn giá − log trung vị 15 căn gần nhất|
danh_dau(df["lech_log"] > np.log(3), "Đơn giá lệch > 3 lần khu vực")
df["ly_do_loai"] = ly_do
df_truoc_loc = df.copy()                       # giữ lại để thử các ngưỡng lọc khác (Bước 11, kiểm tra độ nhạy)

bang_loai = df[ly_do != ""].groupby("ly_do_loai").agg(so_tin=("id", "size"), don_gia_tv=("don_gia", "median"))
display(bang_loai.round(1))
# Quy tắc lọc có loại tin của một nguồn nhiều bất thường không? (nếu có, pipeline đang thiên lệch theo website)
theo_nguon = pd.crosstab(df["nguon"], ly_do.replace("", "Giữ lại"))
theo_nguon["Tỷ lệ bị loại (%)"] = (1 - theo_nguon["Giữ lại"] / theo_nguon.sum(axis=1)) * 100
print("Tin bị loại theo nguồn và lý do:"); display(theo_nguon.round(1))
df[ly_do != ""][["nguon", "url", "tieu_de", "gia_ty", "dt_dat", "don_gia", "ly_do_loai"]].to_csv(
    PROC / "tin_bi_loai.csv", index=False, encoding="utf-8-sig")
df = df[ly_do == ""].reset_index(drop=True)
df["y"] = np.log(df["gia_ty"])
df["log_dt"] = np.log(df["dt_dat"])
df["ty_le_san"] = df["dt_san"] / df["dt_dat"]
df["nhom"] = nhom_gan_trung(df)          # nhóm tin gần trùng, dùng khi chia train/test (Bước 6)
df["phu_hoa"] = (df["phuong"] == "phu hoa").astype(int)
df["tdm"] = (df["quan"] == "thu dau mot").astype(int)
print(f"Còn {len(df)} căn | Thủ Dầu Một: {df['tdm'].sum()} | Phú Hòa: {df['phu_hoa'].sum()}  (danh sách tin bị loại: data/processed/tin_bi_loai.csv)")
kich_co = df["nhom"].map(df["nhom"].value_counts())
print(f"Nhóm gần trùng: {df['nhom'].nunique()} nhóm cho {len(df)} căn; {int((kich_co > 1).sum())} căn nằm trong nhóm có từ 2 tin trở lên")
""")

md(r"""
**Quan sát:** Số tin bị loại nhỏ so với tổng, nhưng đây là những điểm có thể làm lệch mô hình mạnh nhất (ví dụ nhà lắp ghép 720 triệu được đăng như "bán nhà"). Danh sách tin bị loại và lý do được lưu ra `data/processed/tin_bi_loai.csv` để có thể kiểm tra lại.

**Nhóm tin gần trùng (cột `nhom`).** Hàm `nhom_gan_trung` gom các tin nhiều khả năng là **cùng một căn** đăng lại: cùng quận, diện tích lệch ≤ 3%, giá lệch ≤ 12%, và có thêm một bằng chứng (mô tả giống nhau, hoặc cùng phường và cùng kích thước ngang × dài, hoặc cùng phường và cùng tuyến đường). Dữ liệu vẫn giữ nguyên các tin này, nhưng khi đánh giá, **cả nhóm luôn nằm về một phía** (cùng train hoặc cùng test). Quy tắc cố ý gom rộng: gom thừa chỉ làm kết quả đánh giá khắt khe hơn, còn bỏ sót thì kết quả đẹp giả.

## Bước 5: Khám phá dữ liệu
""")

code(r"""
tdm = df[df["tdm"] == 1]
bang = (tdm.groupby("phuong").agg(so_can=("y", "size"), gia_tv_ty=("gia_ty", "median"), don_gia_tv=("don_gia", "median"),
                                   dt_tv=("dt_dat", "median"))
        .query("so_can >= 8").sort_values("don_gia_tv", ascending=False))
bang.round(1)
""")

code(r"""
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
ax = axes[0]
sc = ax.scatter(df["lon"], df["lat"], c=np.log(df["don_gia"]), cmap="viridis", s=12, alpha=0.7)
ph = df[df["phu_hoa"] == 1]
ax.scatter(ph["lon"], ph["lat"], facecolors="none", edgecolors="red", s=40, lw=0.8, label="Phú Hòa")
cb = plt.colorbar(sc, ax=ax); cb.set_label("log(đơn giá triệu/m²)")
ax.set(title="Vị trí và đơn giá các căn (Bình Dương cũ)", xlabel="Kinh độ", ylabel="Vĩ độ"); ax.legend()
ax = axes[1]
nhom = np.where(df["phu_hoa"] == 1, "Phú Hòa", np.where(df["tdm"] == 1, "Phường khác của TDM", "Huyện/TP khác"))
sns.boxplot(x=nhom, y=df["don_gia"], ax=ax, showfliers=False, order=["Phú Hòa", "Phường khác của TDM", "Huyện/TP khác"])
ax.set(title="Đơn giá theo khu vực", ylabel="Đơn giá (triệu/m²)", xlabel="")
plt.tight_layout(); plt.show()
""")

md(r"""
**Quan sát:** Đơn giá phụ thuộc mạnh vào vị trí: cao ở lõi Thủ Dầu Một, Dĩ An, Thuận An (gần TP.HCM) và giảm dần về phía bắc (Bến Cát, Bàu Bàng). Phú Hòa nằm ở lõi Thủ Dầu Một, đơn giá trung vị cao hơn mặt bằng các phường khác. Vì vậy mô hình cần đặc trưng **giá khu vực** chứ không chỉ "tên phường".
""")

code(r"""
fig, axes = plt.subplots(1, 3, figsize=(16, 4.5))
sns.scatterplot(data=df, x="dt_dat", y="gia_ty", hue=nhom, alpha=0.5, s=15, ax=axes[0])
axes[0].set(xscale="log", yscale="log", title="Giá theo diện tích (log–log)", xlabel="Diện tích đất (m²)", ylabel="Giá (tỷ)")
lv = df.dropna(subset=["cap_loi_vao"]).assign(cap=lambda d: d["cap_loi_vao"].round().astype(int))
sns.boxplot(data=lv[lv["tdm"] == 1], x="cap", y="don_gia", showfliers=False, ax=axes[1], color="#8fb3d9")
axes[1].set(title="Thủ Dầu Một: đơn giá theo cấp lối vào", xlabel="0 = hẻm nhỏ … 5 = mặt đường", ylabel="triệu/m²")
anh_huong = {}
for c_ in ["t_kdc", "t_hem_xe_hoi", "t_so_rieng", "t_nha_moi", "t_cap4", "t_tro", "t_ban_gap", "t_so_chung", "t_kinh_doanh", "t_goc"]:
    co_, khong_ = tdm[tdm[c_] == 1]["don_gia"].median(), tdm[tdm[c_] == 0]["don_gia"].median()
    anh_huong[c_] = (co_ / khong_ - 1) * 100
pd.Series(anh_huong).sort_values().plot.barh(ax=axes[2], color="#4C72B0")
axes[2].set(title="TDM: chênh đơn giá trung vị khi tin có nhắc tới…", xlabel="% so với tin không nhắc")
plt.tight_layout(); plt.show()
""")

md(r"""
**Quan sát:**
- Giá theo diện tích vẫn gần tuyến tính trên thang log–log → học trên **log(giá)** là hợp lý (sai số được đo theo tỷ lệ %).
- Đơn giá tăng theo cấp lối vào: hẻm nhỏ < hẻm xe hơi < mặt đường.
- Từ khóa trong mô tả có liên hệ rõ với đơn giá. Đây chỉ là so sánh thô (chưa tách ảnh hưởng của diện tích, vị trí), nên mô hình ở Bước 7–8 sẽ ước lượng tác động thật sự.

## Bước 6: Chia tập huấn luyện (train) và tập kiểm tra (test)
Như bài giảng: mô hình học trên tập **train**, rồi được chấm trên tập **test** gồm những căn nó **chưa từng thấy**. Chấm trên chính dữ liệu đã học sẽ cho kết quả đẹp giả (mô hình chỉ "nhớ bài").

- **Tập test** = 20% số căn ở Thủ Dầu Một, giữ riêng, không dùng cho bất kỳ quyết định nào (chọn mô hình, chọn tham số).
- **Không rò rỉ:** cùng một căn thường được đăng nhiều lần. Các tin gần trùng (cột `nhom`, Bước 4) luôn được chia **về cùng một phía**, nếu không mô hình sẽ "gặp lại" căn đang kiểm tra dưới một tin khác.
""")

code(r"""
from sklearn.model_selection import GroupShuffleSplit

idx_tdm = df.index[df["tdm"] == 1].to_numpy()
_, vt_test = next(GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=RANDOM_STATE).split(idx_tdm, groups=df.loc[idx_tdm, "nhom"]))
df["tap"] = np.where(df.index.isin(idx_tdm[vt_test]), "test", "train")
train, test = df[df["tap"] == "train"].reset_index(drop=True), df[df["tap"] == "test"].reset_index(drop=True)
assert not set(train["nhom"]) & set(test["nhom"])            # không nhóm nào nằm ở cả hai tập
pd.crosstab(df["tap"], np.where(df["phu_hoa"] == 1, "Phú Hòa", np.where(df["tdm"] == 1, "TDM khác", "Ngoài TDM")))
""")

md(r"""
## Bước 7: Mô hình cơ bản – hồi quy tuyến tính và cây quyết định
Hai mô hình trong phạm vi môn học, cùng một mốc so sánh tối thiểu:

| Mô hình | Ý tưởng |
|---|---|
| Baseline – đơn giá phường | Giá = đơn giá trung vị của phường × diện tích. Mô hình học máy phải vượt mốc này mới có ý nghĩa |
| Hồi quy tuyến tính | log(giá) = tổng có trọng số của các đặc trưng |
| **Cây quyết định** (bài giảng chương 3) | Chia dữ liệu bằng các câu hỏi if-then trên đặc trưng; mỗi lá cho một mức giá |

**Đặc trưng:** thông số căn nhà (log diện tích, ngang, dài, số tầng, diện tích sàn, phòng ngủ, WC, mặt tiền, cấp lối vào, độ rộng hẻm, sổ chung, nội thất), vị trí (vĩ độ, kinh độ, khoảng cách tới trung tâm) và 21 từ khóa đọc từ mô tả (Bước 3). Mục tiêu là **log(giá)**, vì với giá nhà sai số tính theo % mới có ý nghĩa (Bước 5). Ô thiếu được điền bằng trung vị **của tập train** (như bài thực hành tiền xử lý).

**Quá khớp (overfitting) và cắt tỉa cây.** Cây càng sâu càng khớp tập train, nhưng tới một mức thì sai số trên dữ liệu mới **tăng lên**: cây bắt đầu học thuộc nhiễu. Ta chọn độ sâu bằng **tập kiểm định** (validation) tách từ tập train, đúng ý tưởng cắt tỉa trong bài giảng, không dùng tập test.
""")

code(r"""
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor, export_text
from mo_hinh_gia import bang_danh_gia

DT_CO_BAN = ["log_dt", "ngang", "dai", "so_tang", "dt_san", "ty_le_san", "phong_ngu", "so_wc", "mat_tien_duong",
             "cap_loi_vao", "hem_rong", "so_chung", "noi_that", "lat", "lon", "kc_trung_tam_km"] + CO_CHU
Xtr, ytr = train[DT_CO_BAN].astype(float), train["y"].to_numpy()
Xte = test[DT_CO_BAN].astype(float)
cay = lambda d: make_pipeline(SimpleImputer(strategy="median"), DecisionTreeRegressor(max_depth=d, min_samples_leaf=5, random_state=0))

# Chọn độ sâu: kiểm định chéo 5-fold trên tập train (chia theo nhóm tin gần trùng), đo MAE trên log(giá)
DO_SAU = list(range(1, 16))
loi_train, loi_val = [], []
for d in DO_SAU:
    tr_, va_ = [], []
    for a, b in GroupKFold(5, shuffle=True, random_state=RANDOM_STATE).split(Xtr, groups=train["nhom"]):
        m = cay(d).fit(Xtr.iloc[a], ytr[a])
        tr_.append(np.mean(np.abs(m.predict(Xtr.iloc[a]) - ytr[a]))); va_.append(np.mean(np.abs(m.predict(Xtr.iloc[b]) - ytr[b])))
    loi_train.append(np.mean(tr_)); loi_val.append(np.mean(va_))
DO_SAU_TOT = DO_SAU[int(np.argmin(loi_val))]

fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(DO_SAU, loi_train, "o-", label="Sai số trên tập train"); ax.plot(DO_SAU, loi_val, "o-", label="Sai số trên tập kiểm định")
ax.axvline(DO_SAU_TOT, color="k", ls="--", lw=0.8)
ax.set(title=f"Cây quyết định: quá khớp khi cây quá sâu (chọn độ sâu = {DO_SAU_TOT})", xlabel="Độ sâu tối đa của cây", ylabel="MAE trên log(giá)"); ax.legend()
plt.show()
print(f"Độ sâu tốt nhất theo tập kiểm định: {DO_SAU_TOT}")
""")

code(r"""
cay_tot = cay(DO_SAU_TOT).fit(Xtr, ytr)
tuyen_tinh = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), LinearRegression()).fit(Xtr, ytr)
p_co_ban = {"Baseline (đơn giá phường)": BaselineDonGiaPhuong().fit(train, ytr).predict(test),
            "Hồi quy tuyến tính": tuyen_tinh.predict(Xte),
            f"Cây quyết định (độ sâu {DO_SAU_TOT})": cay_tot.predict(Xte)}
print("TẬP TEST – các căn Phú Hòa:"); display(bang_danh_gia(test, p_co_ban, (test["phu_hoa"] == 1).to_numpy()).round(2))
print("TẬP TEST – toàn bộ Thủ Dầu Một:"); display(bang_danh_gia(test, p_co_ban, np.ones(len(test), bool)).round(2))
print("Ba tầng đầu của cây quyết định, dạng luật if-then (giá trị lá = log giá dự đoán):")
print(export_text(cay_tot.named_steps["decisiontreeregressor"], feature_names=DT_CO_BAN, max_depth=2))
""")

md(r"""
**Đọc kết quả phần cơ bản:**
- Đường cong cho thấy đúng hiện tượng **quá khớp** trong bài giảng: sai số trên train giảm mãi khi cây sâu thêm, còn sai số trên tập kiểm định giảm rồi đi ngang hoặc tăng. Độ sâu được chọn ở điểm sai số kiểm định thấp nhất.
- Các luật if-then ở gốc cây cho biết mô hình "hỏi" gì đầu tiên: thường là **diện tích** và **vị trí**, khớp với phần khám phá dữ liệu.
- So với baseline trên tập test (thước đo **P**): **hồi quy tuyến tính** giảm được sai số rõ. **Một cây quyết định đơn lẻ** thì gần như không hơn baseline và khoảng tin cậy rất rộng: cây đơn có **phương sai cao**, chỉ cần dữ liệu train đổi một chút là cấu trúc cây đổi hẳn. Đây là điểm yếu đã biết của cây quyết định, và là lý do phần B dùng **nhiều cây kết hợp** (Random Forest: trung bình nhiều cây; gradient boosting: cây sau sửa lỗi cây trước).

**Kết thúc phần cơ bản.** Phần B dưới đây dùng các kỹ thuật ngoài bài giảng để giảm sai số thêm và đo độ tin cậy của kết quả chặt chẽ hơn.
""")

md(r"""
---
# PHẦN B – NÂNG CAO VÀ MỞ RỘNG (kiến thức ngoài bài giảng)
---

## Bước 8: So sánh và chọn mô hình nâng cao

**Cách đánh giá chặt chẽ hơn phần A:** thay vì một lần chia, dùng **kiểm định chéo 5-fold lặp 3 lần** (3 cách chia khác nhau), mỗi căn được dự đoán 3 lần bởi mô hình không học nó. Mỗi chỉ số kèm **khoảng tin cậy 95%** (bootstrap theo nhóm): với khoảng 175 căn Phú Hòa, MAPE dao động vài điểm % chỉ do may rủi, nên chênh lệch nhỏ hơn mức đó **không có nghĩa**. Tập test vẫn chỉ dùng một lần, ở Bước 9.

**Đặc trưng đầu vào** (tất cả lấy được từ tin rao):
- Căn nhà: log(diện tích đất), ngang, dài, số tầng, diện tích sàn, tỷ lệ sàn/đất, phòng ngủ, WC, mặt tiền đường, cấp lối vào, độ rộng hẻm, sổ chung, nội thất.
- Vị trí: vĩ độ, kinh độ, khoảng cách tới trung tâm TDM, **giá khu vực** (đơn giá của 12 căn gần nhất, của cùng phường, cùng tuyến đường).
- 21 từ khóa trong mô tả (Bước 3); với mô hình "+ chữ" có thêm **t_chu**: log(đơn giá) mà mô hình chữ đọc được từ tiêu đề + mô tả.

**Giải thích nhanh các kỹ thuật dùng trong bài** (để trình bày):

| Kỹ thuật | Nói ngắn gọn | Vì sao cần |
|---|---|---|
| Học trên log(giá) | Mô hình dự đoán log của giá rồi đổi ngược bằng `exp` | Giá lệch phải; sai số được đo theo % chứ không theo tỷ đồng |
| Giá khu vực (`GiaLangGieng`) | Với mỗi căn, lấy đơn giá trung bình của 12 căn gần nhất / cùng phường / cùng đường **trong tập học** | Đưa "vị trí" vào mô hình bằng con số có nghĩa. Mỗi căn không được dùng giá của chính nó, nên không lộ đáp án |
| Gradient boosting (LightGBM, CatBoost) | Nhiều cây quyết định nhỏ học nối tiếp, cây sau sửa lỗi cây trước | Bắt được quan hệ phi tuyến; tự xử lý ô thiếu |
| Hàm mất mát Huber | Lỗi nhỏ phạt bình phương, lỗi lớn chỉ phạt tuyến tính | Vài tin rao giá "ảo" không kéo lệch cả mô hình |
| Mô hình chữ TF-IDF + Ridge | Đếm các cụm ký tự trong mô tả, hồi quy tuyến tính ra đơn giá | Tận dụng thông tin người đăng viết bằng lời |
| Stacking (xếp chồng) | Dự đoán của mô hình chữ trở thành **một cột** cho mô hình chính; khi huấn luyện dùng dự đoán ngoài-fold **chia theo nhóm tin gần trùng** (tin đăng lại không lọt vào phần học của mô hình chữ) | Ghép hai nguồn thông tin mà không học vẹt |
| GroupKFold | Chia fold sao cho các tin cùng nhóm không bị tách ra | Chống rò rỉ từ tin đăng lại |
| Bootstrap | Lấy mẫu lại dữ liệu nhiều lần để xem chỉ số dao động bao nhiêu | Biết chênh lệch nào là thật, chênh lệch nào do may rủi |
| Khoảng hiệu chỉnh từ sai số ngoài-fold (ý tưởng conformal) | Lấy phân vị của sai số ngoài-fold làm biên của khoảng giá | Khoảng giá có độ phủ kiểm chứng được trên test (thực nghiệm, không phải bảo đảm lý thuyết) |

**Các mô hình so sánh** (xếp từ đơn giản đến phức tạp):

| # | Mô hình | Ý tưởng |
|---|---|---|
| 0 | Baseline – đơn giá phường | Giá = đơn giá trung vị của phường × diện tích. Mốc tối thiểu phải vượt |
| 1 | Ridge | Hồi quy tuyến tính có phạt L2 |
| 2 | LightGBM | Gradient boosting |
| 3 | Random Forest | Trung bình nhiều cây độc lập |
| 4 | CatBoost | Gradient boosting với cây đối xứng |
| 5 | LightGBM Huber + chữ | LightGBM với hàm mất mát Huber + cột t_chu từ mô hình chữ |
| 6 | Ensemble + chữ | Trung bình của LightGBM Huber, CatBoost và Ridge, cùng cột t_chu |

**Chỉ số** (tính trên giá tỷ đồng): **MAPE** – sai số % trung bình; **MdAPE** – sai số % trung vị; **Trong ±10% / ±20%** – tỷ lệ căn đoán đúng trong biên độ đó; **R²**.
""")

code(r"""
from sklearn.model_selection import KFold, GroupKFold
from sklearn.linear_model import RidgeCV, Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from lightgbm import LGBMRegressor
from catboost import CatBoostRegressor
from mo_hinh_gia import du_doan_cheo_lap, sai_so_tung_can, ktc_bootstrap, bang_danh_gia

DAC_TRUNG = ["log_dt", "ngang", "dai", "so_tang", "dt_san", "ty_le_san", "phong_ngu", "so_wc", "mat_tien_duong",
             "cap_loi_vao", "hem_rong", "so_chung", "noi_that", "lat", "lon", "kc_trung_tam_km"] + CO_CHU
DAC_TRUNG_CHU = DAC_TRUNG + ["t_chu"]

lgb = lambda **k: LGBMRegressor(n_estimators=600, learning_rate=0.02, num_leaves=15, min_child_samples=10, subsample=0.8,
                                subsample_freq=1, colsample_bytree=0.6, reg_lambda=1.0, verbose=-1, random_state=0, n_jobs=1, **k)
cat = lambda: CatBoostRegressor(iterations=800, learning_rate=0.05, depth=6, l2_leaf_reg=5, verbose=0, random_seed=0, thread_count=4,
                                allow_writing_files=False)   # không sinh thư mục catboost_info
ridge = lambda f: MoHinhGia(RidgeCV(alphas=np.logspace(-2, 3, 30)), f, chuan_hoa=True, muc_tieu="don_gia")

# Thứ tự trong từ điển = thứ tự từ đơn giản đến phức tạp (dùng cho quy tắc chọn mô hình)
MO_HINH = {
    "Baseline (đơn giá phường)": lambda: BaselineDonGiaPhuong(),
    "Ridge": lambda: ridge(DAC_TRUNG),
    "LightGBM": lambda: MoHinhGia(lgb(), DAC_TRUNG),
    "Random Forest": lambda: MoHinhGia(make_pipeline(SimpleImputer(strategy="median"),
                                       RandomForestRegressor(300, min_samples_leaf=2, max_features=0.4, n_jobs=-1, random_state=0)), DAC_TRUNG),
    "CatBoost": lambda: MoHinhGia(cat(), DAC_TRUNG, muc_tieu="don_gia"),
    "LightGBM Huber + chữ": lambda: XepChongChu(MoHinhGia(lgb(objective="huber", alpha=0.25), DAC_TRUNG_CHU)),
    "Ensemble + chữ": lambda: XepChongChu(TrungBinhMoHinh([MoHinhGia(lgb(objective="huber", alpha=0.25), DAC_TRUNG_CHU),
                                                         MoHinhGia(cat(), DAC_TRUNG_CHU, muc_tieu="don_gia"),
                                                         ridge(DAC_TRUNG_CHU)])),
}
SO_LAN = 3
OOF = {}
for ten, tao in MO_HINH.items():
    OOF[ten] = du_doan_cheo_lap(tao, train, so_lan=SO_LAN)       # 5-fold x 3 lần, chia theo nhóm
    print("xong:", ten)

la_ph, la_tdm = (train["phu_hoa"] == 1).to_numpy(), (train["tdm"] == 1).to_numpy()
bang_cv_ph = bang_danh_gia(train, OOF, la_ph).sort_values("MAPE (%)")
bang_cv_tdm = bang_danh_gia(train, OOF, la_tdm).sort_values("MAPE (%)")
print(f"Kiểm định chéo lặp {SO_LAN} lần – các căn PHÚ HÒA trong tập train:"); display(bang_cv_ph.round(2))
print(f"Kiểm định chéo lặp {SO_LAN} lần – các căn THỦ DẦU MỘT trong tập train:"); display(bang_cv_tdm.round(2))
""")

code(r"""
fig, axes = plt.subplots(1, 2, figsize=(14, 4.2))
for ax, (ten, b) in zip(axes, [("Phú Hòa", bang_cv_ph), ("Thủ Dầu Một", bang_cv_tdm)]):
    b = b.sort_values("MAPE (%)", ascending=False)
    ax.barh(b.index, b["MAPE (%)"], color="#4C72B0",
            xerr=[b["MAPE (%)"] - b["MAPE thấp (95%)"], b["MAPE cao (95%)"] - b["MAPE (%)"]], capsize=3, ecolor="#333")
    ax.set(title=f"MAPE kiểm định chéo – {ten} (thanh ngang = khoảng tin cậy 95%)", xlabel="%")
plt.tight_layout(); plt.show()
""")

md(r"""
**Quan sát:** Mọi mô hình học máy đều vượt rõ baseline. Giữa các mô hình học máy, khoảng tin cậy **chồng lên nhau nhiều**: thứ hạng trong bảng không đủ để kết luận mô hình nào tốt hơn. Vì vậy không chọn theo kiểu "ai đứng đầu bảng", mà dùng quy tắc dưới đây.

### Quy tắc chọn mô hình: đơn giản nhất mà không kém có ý nghĩa
1. Tìm mô hình có MAPE trung bình (Phú Hòa và Thủ Dầu Một) thấp nhất.
2. So từng mô hình khác với nó **trên cùng từng căn** (so sánh cặp, bootstrap theo nhóm, trên các căn Thủ Dầu Một vì nhiều mẫu hơn). Nếu khoảng tin cậy 95% của chênh lệch MAPE **chứa 0**, coi như hai mô hình ngang nhau.
3. Trong các mô hình "ngang với mô hình tốt nhất", chọn mô hình **đơn giản nhất**.

Mô hình đơn giản hơn thì dễ giải thích, chạy nhanh và ít rủi ro quá khớp hơn; chỉ nên trả giá cho độ phức tạp khi nó mang lại cải thiện đo được.
""")

code(r"""
APE = {ten: sai_so_tung_can(train, P) for ten, P in OOF.items()}          # sai số % của từng căn, trung bình 3 lần lặp
ung_vien = [t for t in MO_HINH if not t.startswith("Baseline")]
diem = pd.Series({t: (APE[t][la_ph].mean() + APE[t][la_tdm].mean()) / 2 for t in ung_vien})
tot_nhat = diem.idxmin()
so_sanh = []
for t in ung_vien:
    d_ = APE[t] - APE[tot_nhat]
    lo, hi = (0.0, 0.0) if t == tot_nhat else ktc_bootstrap(d_[la_tdm], train["nhom"].to_numpy()[la_tdm])
    so_sanh.append({"Mô hình": t, "Độ phức tạp (thứ tự)": ung_vien.index(t) + 1, "MAPE TB (PH, TDM)": diem[t],
                    "Chênh so với tốt nhất (TDM)": d_[la_tdm].mean(), "KTC thấp": lo, "KTC cao": hi, "Ngang mô hình tốt nhất": lo <= 0})
so_sanh = pd.DataFrame(so_sanh).set_index("Mô hình")
display(so_sanh.round(2))
ten_tot_nhat = so_sanh[so_sanh["Ngang mô hình tốt nhất"]]["Độ phức tạp (thứ tự)"].idxmin()
print(f"MAPE thấp nhất: {tot_nhat}  →  mô hình được chọn (đơn giản nhất trong nhóm ngang nhau): {ten_tot_nhat}")
""")

md(r"""
**Có cần tinh chỉnh siêu tham số không?** (cho mô hình LightGBM) Thử 12 cấu hình LightGBM chọn ngẫu nhiên (số cây, tốc độ học, số lá, số mẫu tối thiểu mỗi lá, tỷ lệ cột, mức phạt L2, học giá hay đơn giá), so với cấu hình đang dùng bằng cùng kiểm định chéo chia theo nhóm (2 lần lặp cho nhanh).
""")

code(r"""
rng_ts = np.random.default_rng(1)
cau_hinh = {"Đang dùng": {}}
for i in range(12):
    cau_hinh[f"Thử {i + 1}"] = dict(n_estimators=int(rng_ts.choice([400, 800, 1200])), learning_rate=float(rng_ts.choice([0.01, 0.02, 0.04])),
                                    num_leaves=int(rng_ts.choice([7, 15, 31])), min_child_samples=int(rng_ts.choice([5, 10, 20, 40])),
                                    colsample_bytree=float(rng_ts.choice([0.4, 0.6, 0.8])), reg_lambda=float(rng_ts.choice([0, 1, 5, 20])),
                                    muc_tieu=str(rng_ts.choice(["gia", "don_gia"])))
MAC_DINH = lgb().get_params()                    # tham số của cấu hình đang dùng; mỗi cấu hình thử ghi đè một phần
kq_ts = []
for ten_ts, ch in cau_hinh.items():
    ch = dict(ch); mt = ch.pop("muc_tieu", "gia")
    tao_ts = lambda ch=ch, mt=mt: MoHinhGia(LGBMRegressor(**{**MAC_DINH, **ch}), DAC_TRUNG, muc_tieu=mt)
    a_ = sai_so_tung_can(train, du_doan_cheo_lap(tao_ts, train, so_lan=2))
    kq_ts.append({"Cấu hình": ten_ts, "MAPE Phú Hòa": a_[la_ph].mean(), "MAPE TDM": a_[la_tdm].mean(), **cau_hinh[ten_ts]})
kq_ts = pd.DataFrame(kq_ts).assign(**{"MAPE TB": lambda t: (t["MAPE Phú Hòa"] + t["MAPE TDM"]) / 2}).sort_values("MAPE TB")
display(kq_ts.round(2).head(6))
print("Cấu hình tốt nhất:", kq_ts.iloc[0]["Cấu hình"], f"(MAPE TB {kq_ts.iloc[0]['MAPE TB']:.2f}%; cấu hình đang dùng: {kq_ts.set_index('Cấu hình').loc['Đang dùng', 'MAPE TB']:.2f}%)")
""")

md(r"""
**Đọc kết quả:** nếu "Đang dùng" đứng đầu hoặc chỉ kém vài phần mười điểm %, tinh chỉnh thêm không mang lại cải thiện đáng kể, và cấu hình hiện tại được giữ nguyên. Với dữ liệu giá rao, giới hạn độ chính xác nằm ở chất lượng dữ liệu (giá ảo, thiếu thông tin) hơn là ở siêu tham số.

**Ba phép kiểm chứng cho mô hình được chọn** (đều bằng kiểm định chéo lặp trên tập train):
- **Rò rỉ có ảnh hưởng không?** So MAPE khi chia fold ngẫu nhiên (tin gần trùng có thể nằm ở cả train lẫn test) với khi chia theo nhóm.
- **Học trên toàn vùng có hơn chỉ học trên Phú Hòa?**
- **So với cách làm của phiên bản 1** (Ridge trên 9 thông số, chỉ học các căn Phú Hòa).
""")

code(r"""
P_thuong = du_doan_cheo_lap(MO_HINH[ten_tot_nhat], train, so_lan=SO_LAN, theo_nhom=False)
ph_train = train[la_ph].reset_index(drop=True)
P_chi_ph = du_doan_cheo_lap(MO_HINH[ten_tot_nhat], ph_train, so_lan=SO_LAN)

class PhienBan1:
    # Cách làm phiên bản 1: Ridge trên 9 thông số căn nhà
    COT = ["dt_dat", "ngang", "so_tang", "dt_san", "phong_ngu", "so_wc", "cap_loi_vao", "hem_rong", "noi_that"]
    def fit(self, X, y):
        self.m_ = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), Ridge(alpha=3.0)).fit(X[self.COT], y); return self
    def predict(self, X):
        return self.m_.predict(X[self.COT])
P_v1 = du_doan_cheo_lap(PhienBan1, ph_train, so_lan=SO_LAN)

ape_chon = APE[ten_tot_nhat][la_ph]
kiem_chung = pd.DataFrame({
    f"{ten_tot_nhat} – học toàn vùng, chia theo nhóm (cách đánh giá chính)": bang_danh_gia(train, {"x": OOF[ten_tot_nhat]}, la_ph).iloc[0],
    f"{ten_tot_nhat} – học toàn vùng, chia NGẪU NHIÊN (có rò rỉ)": bang_danh_gia(train, {"x": P_thuong}, la_ph).iloc[0],
    f"{ten_tot_nhat} – chỉ học trên Phú Hòa": bang_danh_gia(ph_train, {"x": P_chi_ph}, np.ones(len(ph_train), bool)).iloc[0],
    "Cách làm phiên bản 1 (Ridge 9 thông số, chỉ Phú Hòa)": bang_danh_gia(ph_train, {"x": P_v1}, np.ones(len(ph_train), bool)).iloc[0],
}).T
display(kiem_chung.round(2))
nh = train["nhom"].to_numpy()[la_ph]
for nhan, ape_khac in [("chia ngẫu nhiên", sai_so_tung_can(train, P_thuong)[la_ph]), ("chỉ học Phú Hòa", sai_so_tung_can(ph_train, P_chi_ph)),
                       ("phiên bản 1", sai_so_tung_can(ph_train, P_v1))]:
    lo, hi = ktc_bootstrap(ape_khac - ape_chon, nh)
    print(f"MAPE của '{nhan}' trừ MAPE cách chính: {np.mean(ape_khac - ape_chon):+.2f} điểm % (KTC 95%: {lo:+.2f} … {hi:+.2f})")
""")

md(r"""
**Đọc kết quả** (xem các dòng in phía trên; chênh lệch có khoảng tin cậy không chứa 0 thì mới coi là thật):
- **Rò rỉ:** nếu MAPE khi chia ngẫu nhiên thấp hơn khi chia theo nhóm, phần chênh đó là mức "đẹp giả" do tin đăng lại. Con số báo cáo của đề tài là con số **chia theo nhóm**.
- **Phạm vi dữ liệu:** học trên toàn vùng so với chỉ học trên Phú Hòa cho biết việc mở rộng thu thập có ích tới đâu.
- **So với phiên bản 1:** cho biết toàn bộ cải tiến (dữ liệu + đặc trưng + mô hình) mang lại bao nhiêu trên chính các căn Phú Hòa.

## Bước 9: Kiểm tra lần cuối trên tập test
Tập test chưa được dùng ở bất kỳ bước nào. Vì chỉ có vài chục căn Phú Hòa, con số trên test **dao động mạnh** (xem khoảng tin cậy). Đây là **kết quả chính** của đề tài vì là bằng chứng sạch nhất; con số kiểm định chéo ở Bước 8 dùng để bổ trợ.
""")

code(r"""
mo_hinh_tot = MO_HINH[ten_tot_nhat]().fit(train, train["y"])
baseline = BaselineDonGiaPhuong().fit(train, train["y"])
v1 = PhienBan1().fit(ph_train, ph_train["y"])
p_test = {ten_tot_nhat: mo_hinh_tot.predict(test), "Baseline (đơn giá phường)": baseline.predict(test),
          "Cách làm phiên bản 1 (Ridge, chỉ Phú Hòa)": v1.predict(test)}
m_ph, m_tdm = (test["phu_hoa"] == 1).to_numpy(), np.ones(len(test), bool)
bang_test_ph, bang_test_tdm = bang_danh_gia(test, p_test, m_ph), bang_danh_gia(test, p_test, m_tdm)
print("TẬP TEST – các căn Phú Hòa:"); display(bang_test_ph.round(2))
print("TẬP TEST – toàn bộ Thủ Dầu Một:"); display(bang_test_tdm.round(2))
cv_, te_ = bang_cv_ph.loc[ten_tot_nhat], bang_test_ph.loc[ten_tot_nhat]
print(f"Phú Hòa – kiểm định chéo: MAPE {cv_['MAPE (%)']:.1f}% (KTC {cv_['MAPE thấp (95%)']:.1f}–{cv_['MAPE cao (95%)']:.1f}) | "
      f"test: {te_['MAPE (%)']:.1f}% (KTC {te_['MAPE thấp (95%)']:.1f}–{te_['MAPE cao (95%)']:.1f}) → "
      + ("hai khoảng tin cậy chồng nhau: test không mâu thuẫn với kiểm định chéo (nhưng tập test nhỏ, khoảng tin cậy rộng)." if te_['MAPE thấp (95%)'] <= cv_['MAPE cao (95%)'] and cv_['MAPE thấp (95%)'] <= te_['MAPE cao (95%)']
         else "hai khoảng tin cậy KHÔNG chồng nhau: cần xem lại."))
""")

md(r"""
### MAPE trên tập test nghĩa là gì, minh họa bằng chính các căn Phú Hòa trong tập test
MAPE là **sai lệch trung bình tính theo %** giữa giá mô hình ước lượng và giá rao. Ví dụ MAPE 27% với một căn rao 4 tỷ nghĩa là trung bình mô hình lệch khoảng ±1,1 tỷ. Đây là **trung bình**: phần lớn căn lệch ít hơn (xem trung vị), còn vài căn lệch rất nhiều kéo con số lên. Bảng dưới lấy các căn **thật** của tập test ở các mức lệch khác nhau.
""")

code(r"""
ph_te = test[m_ph].assign(gia_du_doan_ty=np.exp(p_test[ten_tot_nhat][m_ph]))
ph_te["lech_pt"] = (ph_te["gia_du_doan_ty"] / ph_te["gia_ty"] - 1) * 100
ph_te = ph_te.sort_values("lech_pt", key=np.abs).reset_index(drop=True)
n_ = len(ph_te)
vi_du = ph_te.iloc[[0, n_ // 4, n_ // 2, 3 * n_ // 4, n_ - 1]]                  # tốt nhất, 25%, giữa, 75%, tệ nhất
vi_du.insert(0, "Mức", ["Lệch ít nhất", "25% số căn lệch ít hơn", "Căn ở giữa (trung vị)", "75% số căn lệch ít hơn", "Lệch nhiều nhất"])
display(vi_du[["Mức", "tieu_de", "dt_dat", "gia_ty", "gia_du_doan_ty", "lech_pt"]].rename(columns={
    "tieu_de": "Tin rao", "dt_dat": "Đất (m²)", "gia_ty": "Giá rao (tỷ)", "gia_du_doan_ty": "Mô hình (tỷ)", "lech_pt": "Lệch (%)"}).round(2))
lech_ty = (ph_te["gia_du_doan_ty"] - ph_te["gia_ty"]).abs()
print(f"{n_} căn Phú Hòa trong tập test: một nửa số căn lệch ≤ {ph_te['lech_pt'].abs().median():.0f}% "
      f"(≤ {lech_ty.median():.2f} tỷ); {(ph_te['lech_pt'].abs() <= 20).mean() * 100:.0f}% số căn lệch ≤ 20%. "
      f"MAPE = trung bình mức lệch = {ph_te['lech_pt'].abs().mean():.1f}%, bị kéo lên bởi vài căn lệch nhiều.")
""")

code(r"""
gia_that, gia_dd = test["gia_ty"].to_numpy(), np.exp(p_test[ten_tot_nhat])
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
ax = axes[0]
ax.scatter(gia_that[~m_ph], gia_dd[~m_ph], alpha=0.5, label="TDM khác")
ax.scatter(gia_that[m_ph], gia_dd[m_ph], alpha=0.85, color="crimson", label="Phú Hòa")
lim = [0.8, max(gia_that.max(), gia_dd.max()) * 1.1]
ax.plot(lim, lim, "k-", lw=1); ax.plot(lim, [v * 1.2 for v in lim], "k--", lw=0.7); ax.plot(lim, [v / 1.2 for v in lim], "k--", lw=0.7)
ax.set(xscale="log", yscale="log", xlim=lim, ylim=lim, xlabel="Giá rao thật (tỷ)", ylabel="Giá dự đoán (tỷ)",
       title=f"{ten_tot_nhat}: dự đoán vs thực tế (tập test, nét đứt = ±20%)"); ax.legend()
sai_so = (gia_dd - gia_that) / gia_that * 100
sns.histplot(sai_so, bins=30, ax=axes[1], color="#C44E52"); axes[1].axvline(0, color="k")
axes[1].set(title="Phân bố sai số trên tập test", xlabel="(dự đoán − thật) / thật × 100 (%)", ylabel="Số căn")
plt.tight_layout(); plt.show()
""")

md(r"""
**Con số nên trình bày:** MAPE trên tập test kèm khoảng tin cậy (kết quả chính), cùng MAPE kiểm định chéo ở Bước 8 (bổ trợ). Sai số cỡ 20–25% là mức thường gặp với **giá rao bán**: cùng một căn, các môi giới rao chênh nhau 5–15%, người bán còn để "phần thương lượng". Phần sai số này nằm ở chính dữ liệu, mô hình không thể loại bỏ.

### Mô hình có định giá lệch theo loại nhà không?
Kiểm tra **sai lệch có dấu** của dự đoán ngoài-fold (dương = mô hình đoán cao hơn giá rao) theo loại lối vào và theo mức giá. Nếu mô hình lệch có hệ thống với một loại nhà, trung vị sai lệch của loại đó sẽ xa 0.
""")

code(r"""
tr_tdm = train[la_tdm].copy()
tr_tdm["lech_pt"] = (np.exp(OOF[ten_tot_nhat].mean(0)[la_tdm] - tr_tdm["y"]) - 1) * 100
tr_tdm["Loại"] = np.where(tr_tdm["mat_tien_duong"] == 1, "Mặt tiền đường", "Trong hẻm")
tr_tdm["Mức giá"] = pd.qcut(tr_tdm["gia_ty"], 4, labels=["Rẻ nhất 25%", "25–50%", "50–75%", "Đắt nhất 25%"])
tk = lambda g: g["lech_pt"].describe(percentiles=[.1, .5, .9])[["count", "10%", "50%", "90%"]]
display(tr_tdm.groupby("Loại").apply(tk).round(1)); display(tr_tdm.groupby("Mức giá", observed=True).apply(tk).round(1))
""")

md(r"""
**Quan sát:**
- **Theo loại lối vào:** trung vị sai lệch của nhà mặt tiền và nhà trong hẻm đều gần 0, hai phân bố gần giống nhau → mô hình **không định giá lệch có hệ thống** với nhà mặt tiền.
- **Theo mức giá:** nhóm rao đắt nhất bị đoán thấp, nhóm rao rẻ nhất bị đoán cao. Đây là hiện tượng **co về trung bình**, có ở mọi mô hình khi chia nhóm theo chính giá rao: một căn rao rất cao một phần vì nó tốt thật, một phần vì người bán "hét giá", và mô hình chỉ thấy phần thứ nhất. Hệ quả: các căn bị chẩn đoán "cao hơn thị trường" ở Bước 11 gồm cả căn rao giá ảo lẫn căn có ưu điểm mô hình không thấy; cần xem tận nơi để phân biệt.

### Đặc trưng nào quan trọng?
Dùng **permutation importance theo nhóm** trên tập test: xáo trộn cùng lúc một nhóm cột rồi đo MAE trên log(giá) tăng bao nhiêu.
""")

code(r"""
def mae_log(model, X):
    return np.mean(np.abs(model.predict(X) - X["y"].to_numpy()))

NHOM_DT = {
    "Diện tích đất": ["log_dt", "dt_dat"], "Kích thước (ngang, dài)": ["ngang", "dai"],
    "Số tầng, sàn, phòng, WC": ["so_tang", "dt_san", "ty_le_san", "phong_ngu", "so_wc"],
    "Lối vào (mặt tiền, hẻm)": ["mat_tien_duong", "cap_loi_vao", "hem_rong", "t_hem_xe_hoi", "t_hem_nho", "t_mat_tien"],
    "Vị trí (tọa độ, phường, đường)": ["lat", "lon", "kc_trung_tam_km", "phuong", "duong"],
    "Mô tả tin (từ khóa + văn bản)": [c for c in CO_CHU if c not in ("t_hem_xe_hoi", "t_hem_nho", "t_mat_tien")] + ["van_ban", "so_chung", "noi_that"],
}
goc = mae_log(mo_hinh_tot, test)
rng = np.random.default_rng(0)
pi = {}
for ten, cols in NHOM_DT.items():
    tang_ = []
    for _ in range(5):
        Xp = test.copy()
        perm = rng.permutation(len(Xp))
        for c_ in cols:
            Xp[c_] = Xp[c_].to_numpy()[perm]
        tang_.append(mae_log(mo_hinh_tot, Xp) - goc)
    pi[ten] = np.mean(tang_)
ax = pd.Series(pi).sort_values().plot.barh(color="#8172B2", figsize=(8, 4))
ax.set(title="Permutation importance theo nhóm (tập test)", xlabel="Mức tăng MAE trên log(giá) khi xáo trộn")
plt.show()
""")

md(r"""
**Quan sát:** Diện tích đất là yếu tố số một. Nhóm **vị trí** (đưa vào mô hình qua đặc trưng giá khu vực) đứng thứ hai. Các nhóm còn lại đóng góp nhỏ hơn. Lưu ý: tin guland chỉ có tiêu đề nên nhóm "mô tả tin" chưa phát huy hết ở Phú Hòa.

## Bước 10: Khoảng giá 80% (hiệu chỉnh từ sai số ngoài-fold)
Một con số dự đoán đơn lẻ chưa đủ để ra quyết định. Ta muốn khoảng [thấp, cao] **chứa giá rao thật của khoảng 80% số căn**.

**Cách làm:** lấy sai số ngoài-fold của mô hình trên **các căn Thủ Dầu Một** trong tập train (cả 3 lần lặp), r = log(giá thật) − log(giá dự đoán). Phân vị 10% và 90% của r cho biên dưới/biên trên: khoảng = dự đoán × [e^q10, e^q90].

**Về tên gọi:** cách làm này mượn ý tưởng của *conformal prediction* (dùng phân vị sai số trên dữ liệu mô hình chưa thấy làm biên khoảng), nhưng **không phải** conformal "chuẩn" có bảo đảm lý thuyết: sai số lấy từ kiểm định chéo (ngoài-fold) trong khi khoảng được áp cho mô hình cuối huấn luyện trên toàn bộ dữ liệu, và dữ liệu có thể không hoán đổi được (tin đăng theo thời gian, theo khu). Vì vậy ta gọi đây là **khoảng hiệu chỉnh thực nghiệm** và chỉ tin vào nó qua **độ phủ quan sát được trên tập test riêng** (kèm kiểm định nhị thức), không tuyên bố bảo đảm 80%.

**Biên độ riêng theo mức giá (hiệu chỉnh theo nhóm, giống ý tưởng Mondrian conformal).** Nếu dùng một biên độ chung cho mọi căn, độ phủ trung bình đúng 80% nhưng **không đều**: nhà giá cao dao động mạnh hơn nên khoảng quá hẹp, nhà rẻ thì khoảng thừa rộng. Vì vậy chia các căn thành 4 mức theo **giá dự đoán** (tứ phân vị) và tính phân vị sai số riêng cho từng mức. Phân nhóm theo giá **dự đoán** (không theo giá thật) để dùng được cho căn mới chưa biết giá. Ô dưới so độ phủ từng nhóm giữa hai cách.
""")

code(r"""
from mo_hinh_gia import hieu_chinh_khoang, phan_vi_cho, muc_gia
P_tdm, Y_tdm = OOF[ten_tot_nhat][:, la_tdm], train["y"].to_numpy()[la_tdm]
NGUONG = np.quantile(P_tdm.mean(axis=0), [0.25, 0.5, 0.75]).tolist()          # ngưỡng 4 mức giá (log tỷ)
r = (Y_tdm - P_tdm).ravel()
KHOANG = hieu_chinh_khoang(r, muc_gia(P_tdm.ravel(), NGUONG))
KHOANG["nguong"] = NGUONG
Q = KHOANG["chung"]                                                           # biên độ chung (để so sánh)

ten_muc = ["Rẻ nhất 25%", "25–50%", "50–75%", "Đắt nhất 25%"]
m_all = muc_gia(P_tdm.ravel(), NGUONG)
q_rieng = phan_vi_cho(m_all, KHOANG)
so_sanh_kh = pd.DataFrame({
    "Số căn": [int((muc_gia(P_tdm.mean(0), NGUONG) == k).sum()) for k in range(4)],
    "Độ phủ – biên độ chung (%)": [np.mean(((r >= Q["q10"]) & (r <= Q["q90"]))[m_all == k]) * 100 for k in range(4)],
    "Độ phủ – biên độ theo mức (%)": [np.mean(((r >= q_rieng["q10"]) & (r <= q_rieng["q90"]))[m_all == k]) * 100 for k in range(4)],
    "Biên độ 80% theo mức": [f"{(np.exp(KHOANG['nhom'][str(k)]['q10']) - 1) * 100:+.0f}% … {(np.exp(KHOANG['nhom'][str(k)]['q90']) - 1) * 100:+.0f}%" for k in range(4)],
}, index=ten_muc)
display(so_sanh_kh.round(1))

q_test = phan_vi_cho(muc_gia(p_test[ten_tot_nhat], NGUONG), KHOANG)
lo80, hi80 = p_test[ten_tot_nhat] + q_test["q10"], p_test[ten_tot_nhat] + q_test["q90"]
lo50, hi50 = p_test[ten_tot_nhat] + q_test["q25"], p_test[ten_tot_nhat] + q_test["q75"]
yt = test["y"].to_numpy()
pd.DataFrame({
    "Khoảng 80%": [np.mean((yt >= lo80) & (yt <= hi80)) * 100, np.mean(((yt >= lo80) & (yt <= hi80))[m_ph]) * 100],
    "Khoảng 50%": [np.mean((yt >= lo50) & (yt <= hi50)) * 100, np.mean(((yt >= lo50) & (yt <= hi50))[m_ph]) * 100],
}, index=[f"Độ phủ trên test TDM ({len(test)} căn, %)", f"Độ phủ trên test Phú Hòa ({int(m_ph.sum())} căn, %)"]).round(1)
""")

code(r"""
# Độ phủ đo trên vài chục căn dao động nhiều. Kiểm định nhị thức: nếu khoảng thật sự phủ 80%,
# xác suất thấy độ phủ thấp như trên test là bao nhiêu? Đồng thời đo độ phủ trên tập lớn hơn:
# dự đoán ngoài-fold của TẤT CẢ căn TDM (mỗi căn được dự đoán bởi mô hình không học nó).
from scipy.stats import binomtest
trong = (yt >= lo80) & (yt <= hi80)
for nhan, m_ in [("test TDM", m_tdm), ("test Phú Hòa", m_ph)]:
    k, n = int(trong[m_].sum()), int(m_.sum())
    p_ = binomtest(k, n, 0.8, alternative="less").pvalue
    print(f"{nhan}: {k}/{n} căn trong khoảng ({k / n * 100:.0f}%), p = {p_:.2f} → "
          + ("không đủ bằng chứng để nói khoảng quá hẹp (p ≥ 0,05)" if p_ >= 0.05 else "khoảng có thể quá hẹp (p < 0,05)"))
# Độ phủ theo mức giá TRÊN TẬP TEST (chưa dùng để tính biên độ) – kiểm tra cách chia theo mức có giữ được trên dữ liệu mới
m_te = muc_gia(p_test[ten_tot_nhat], NGUONG)
q_chung_lo, q_chung_hi = p_test[ten_tot_nhat] + Q["q10"], p_test[ten_tot_nhat] + Q["q90"]
display(pd.DataFrame({"Số căn test": [int((m_te == k).sum()) for k in range(4)],
                      "Biên độ chung (%)": [np.mean(((yt >= q_chung_lo) & (yt <= q_chung_hi))[m_te == k]) * 100 for k in range(4)],
                      "Biên độ theo mức (%)": [np.mean(trong[m_te == k]) * 100 for k in range(4)]}, index=ten_muc).round(0))
""")

md(r"""
**Quan sát:**
- Với biên độ chung, nhóm nhà đắt nhất bị phủ thiếu rõ rệt; biên độ theo mức đưa độ phủ của cả 4 nhóm về gần 80% (bảng đầu). Bảng độ phủ trên tập test (dữ liệu chưa dùng để tính biên độ) cho thấy cải thiện này giữ được trên dữ liệu mới; mỗi nhóm test chỉ vài chục căn nên dao động vài điểm %.
- Đọc độ phủ cùng kết quả kiểm định nhị thức: chỉ khi p < 0,05 mới có cơ sở nói khoảng giá quá hẹp.
- Khoảng 80% khá rộng và **lệch lên trên** vì có những tin rao cao hơn hẳn mặt bằng. Đó là mức bất định thật của giá rao, báo cáo cần nêu rõ thay vì chỉ đưa một con số.

## Bước 11: Chẩn đoán giá từng căn ở Phú Hòa
Với **mỗi tin rao Phú Hòa**, so giá rao với giá thị trường mô hình ước lượng. Giá ước lượng của một căn được tính bằng mô hình **không học căn đó và không học các tin gần trùng với nó** (kiểm định chéo theo nhóm trên toàn bộ dữ liệu, trung bình 3 lần lặp).
- **Rẻ hơn thị trường:** giá rao thấp hơn biên dưới khoảng 80%.
- **Cao hơn thị trường:** giá rao cao hơn biên trên khoảng 80%.
- **Hợp lý:** nằm trong khoảng.
""")

code(r"""
oof_all = du_doan_cheo_lap(MO_HINH[ten_tot_nhat], df, so_lan=SO_LAN, seed=7).mean(axis=0)
df["gia_uoc_luong_ty"] = np.exp(oof_all)
q_all = phan_vi_cho(muc_gia(oof_all, NGUONG), KHOANG)                       # biên độ theo mức giá của từng căn
df["khoang80_thap"] = np.exp(oof_all + q_all["q10"]); df["khoang80_cao"] = np.exp(oof_all + q_all["q90"])
df["chenh_lech_pt"] = (df["gia_ty"] / df["gia_uoc_luong_ty"] - 1) * 100
df["chan_doan"] = np.select([df["gia_ty"] < df["khoang80_thap"], df["gia_ty"] > df["khoang80_cao"]],
                            ["Rẻ hơn thị trường", "Cao hơn thị trường"], "Hợp lý")
ph = df[df["phu_hoa"] == 1]
display(ph["chan_doan"].value_counts().to_frame("Số căn Phú Hòa").assign(**{"%": lambda t: (t["Số căn Phú Hòa"] / len(ph) * 100).round(1)}))
cot = ["nguon", "tieu_de", "dt_dat", "so_tang", "gia_ty", "gia_uoc_luong_ty", "khoang80_thap", "khoang80_cao", "chenh_lech_pt"]
print("5 căn giá rao thấp nhất so với thị trường:"); display(ph.sort_values("chenh_lech_pt")[cot].head(5).round(2))
print("5 căn giá rao cao nhất so với thị trường:"); display(ph.sort_values("chenh_lech_pt")[cot].tail(5).round(2))
""")

code(r"""
xuat = ph.assign(dien_tich_m2=ph["dt_dat"]).rename(columns={"id": "ma_tin", "url": "link_tin", "gia_ty": "gia_rao_ty"})
xuat[["ma_tin", "nguon", "link_tin", "tieu_de", "dien_tich_m2", "ngang", "so_tang", "phong_ngu", "so_wc", "cap_loi_vao",
      "hem_rong", "duong", "t_kdc", "t_hem_xe_hoi", "t_so_rieng", "t_ban_gap"]].to_csv(KET_QUA / "input.csv", index=False, encoding="utf-8-sig")
xuat.assign(gia_du_doan_ty=xuat["gia_uoc_luong_ty"].round(3),
            khoang_80_ty=xuat["khoang80_thap"].round(2).astype(str) + " - " + xuat["khoang80_cao"].round(2).astype(str),
            chenh_lech_pt=xuat["chenh_lech_pt"].round(1), mo_hinh=ten_tot_nhat)[
    ["ma_tin", "nguon", "dien_tich_m2", "gia_rao_ty", "gia_du_doan_ty", "khoang_80_ty", "chenh_lech_pt", "chan_doan", "mo_hinh"]
].to_csv(KET_QUA / "output.csv", index=False, encoding="utf-8-sig")
print("Đã ghi ket_qua/input.csv (thông số", len(xuat), "căn Phú Hòa) và ket_qua/output.csv (giá ước lượng, khoảng 80%, chẩn đoán)")
""")

md(r"""
**Quan sát:** Phần lớn căn Phú Hòa có giá rao "hợp lý" theo mô hình; theo cách dựng khoảng 80%, mỗi phía kỳ vọng khoảng 10% số căn. Nhóm "cao hơn thị trường" gồm tin rao kỳ vọng cao và căn có yếu tố mô hình không thấy (nhà mới xây cao cấp, vị trí đặc biệt), xem phân tích co về trung bình ở Bước 9. Nhóm "rẻ hơn" là ứng viên đáng xem (thường có tin "bán gấp/ngộp"), nhưng cũng cần kiểm tra pháp lý và hiện trạng. Kết quả là **gợi ý sàng lọc**, không thay thế thẩm định thực tế.

""")

md(r"""
### Kiểm tra độ tin cậy của dữ liệu và kết quả
Một con số MAPE chung có thể che giấu chỗ mô hình yếu. Ba phép kiểm dưới đây trả lời: mô hình sai nhiều hơn ở đâu, kết quả có phụ thuộc vào quy tắc lọc không, và việc gom tin trùng có đúng không.

**1. Sai số theo nhóm.** Dùng dự đoán chéo theo nhóm của **mọi** căn (ở trên). Nhóm dưới 20 căn ghi "chưa đủ mẫu" thay vì đưa ra con số dễ gây hiểu nhầm.
""")

code(r"""
d_ = df.assign(ape=np.abs(df["gia_uoc_luong_ty"] / df["gia_ty"] - 1) * 100,
               thong_so=np.where(df[["dt_san", "so_tang", "ngang", "cap_loi_vao"]].notna().sum(axis=1) >= 3,
                                 "Đủ thông số (≥ 3 trong 4: sàn, tầng, ngang, lối vào)", "Thiếu thông số (≤ 2 trong 4)"),
               muc_gia=pd.qcut(df["gia_ty"], 4, labels=["Rẻ nhất 25%", "25–50%", "50–75%", "Đắt nhất 25%"]))
def sai_so_theo(cot, ten, du_lieu=d_):
    dong = []
    for k, g in du_lieu.groupby(cot, observed=True):
        if len(g) < 20:
            dong.append({ten: k, "Số căn": len(g), "MAPE (%)": np.nan, "KTC 95%": "chưa đủ mẫu"}); continue
        lo, hi = ktc_bootstrap(g["ape"].to_numpy(), g["nhom"].to_numpy())
        dong.append({ten: k, "Số căn": len(g), "MAPE (%)": round(g["ape"].mean(), 1), "KTC 95%": f"{lo:.1f} – {hi:.1f}"})
    return pd.DataFrame(dong).set_index(ten)
for cot, ten in [("nguon", "Nguồn tin"), ("muc_toa_do", "Mức chính xác của tọa độ"), ("thong_so", "Thông số căn nhà"), ("muc_gia", "Mức giá rao")]:
    display(sai_so_theo(cot, ten))
display(sai_so_theo("phuong", "Phường (Thủ Dầu Một)", d_[d_["tdm"] == 1]).sort_values("Số căn", ascending=False))
""")

md(r"""
**2. Độ nhạy theo ngưỡng lọc "đơn giá lệch quá xa khu vực".** Quy tắc này có thể loại nhầm căn cao cấp hay vị trí hiếm có đơn giá cao thật. Ta học lại mô hình với 4 ngưỡng (giữ nguyên các quy tắc lọc khác), rồi chấm **trên cùng một tập căn**: những căn được giữ lại ở **mọi** ngưỡng. Chấm trên cùng tập thì so sánh mới công bằng; nếu chấm trên tập của từng ngưỡng, ngưỡng lỏng sẽ "bị phạt" chỉ vì phải đoán cả các tin giá bất thường.
""")

code(r"""
NGUONG_LECH = {"Chặt hơn: lệch > 2 lần": np.log(2), "Đang dùng: lệch > 3 lần": np.log(3),
               "Lỏng hơn: lệch > 5 lần": np.log(5), "Không lọc theo đơn giá": np.inf}
qua_quy_tac_khac = df_truoc_loc["ly_do_loai"].isin(["", "Đơn giá lệch > 3 lần khu vực"]).to_numpy()
DU_DOAN_NG = {}
for ten, t in NGUONG_LECH.items():
    d = df_truoc_loc[qua_quy_tac_khac & (df_truoc_loc["lech_log"] <= t).to_numpy()].copy()
    d["y"], d["log_dt"], d["ty_le_san"] = np.log(d["gia_ty"]), np.log(d["dt_dat"]), d["dt_san"] / d["dt_dat"]
    d["phu_hoa"], d["tdm"] = (d["phuong"] == "phu hoa").astype(int), (d["quan"] == "thu dau mot").astype(int)
    d = d.reset_index(names="goc")
    d["nhom"] = nhom_gan_trung(d)
    DU_DOAN_NG[ten] = (pd.Series(du_doan_cheo_lap(MO_HINH[ten_tot_nhat], d, so_lan=1)[0], index=d["goc"]), len(d))
chung = sorted(set.intersection(*[set(p.index) for p, _ in DU_DOAN_NG.values()]))
goc_ = df_truoc_loc.loc[chung]
nhom_chung = nhom_gan_trung(goc_.reset_index(drop=True))          # nhóm gần trùng trên tập chấm chung (cho khoảng tin cậy)
dong = []
for ten, (p, n) in DU_DOAN_NG.items():
    ape = np.abs(np.exp(p.loc[chung].to_numpy()) / goc_["gia_ty"].to_numpy() - 1) * 100
    m_ph, m_tdm = (goc_["phuong"] == "phu hoa").to_numpy(), (goc_["quan"] == "thu dau mot").to_numpy()
    lo, hi = ktc_bootstrap(ape[m_tdm], nhom_chung[m_tdm])
    dong.append({"Ngưỡng lọc": ten, "Số căn dùng để học": n, "MAPE Phú Hòa (%)": round(ape[m_ph].mean(), 1),
                 "MAPE Thủ Dầu Một (%)": round(ape[m_tdm].mean(), 1), "KTC 95% (TDM)": f"{lo:.1f} – {hi:.1f}"})
print(f"Chấm trên {len(chung)} căn được giữ ở mọi ngưỡng (Phú Hòa {int((goc_['phuong'] == 'phu hoa').sum())}, TDM {int((goc_['quan'] == 'thu dau mot').sum())}); kiểm định chéo theo nhóm 5-fold:")
display(pd.DataFrame(dong).set_index("Ngưỡng lọc"))
""")

md(r"""
**3. Kiểm tra tay việc gom tin trùng.** Quy tắc gom tin gần trùng chỉ được kiểm thử trên ví dụ dựng sẵn; muốn biết nó đúng đến đâu trên dữ liệu thật thì **người phải xem từng cặp**. Ô dưới xuất 25 cặp **đã gom** và 25 cặp **gần giống nhưng không gom** (cùng quận, diện tích lệch ≤ 3%, giá lệch ≤ 12%) ra `data/kiem_tra_tay/cap_tin_gan_trung.csv`, xáo thứ tự để người gán nhãn không biết cặp nào đã gom. Mở file, xem hai tin (tiêu đề, giá, diện tích, phường, đường, link), điền cột `cung_mot_can`: **1** = cùng một căn, **0** = hai căn khác nhau. Chạy lại notebook thì ô này tính:
- **Gom đúng** = trong các cặp đã gom, bao nhiêu % thật sự cùng một căn;
- **Bỏ sót** = trong các cặp không gom, bao nhiêu % thật ra là cùng một căn (tin trùng lọt qua → kết quả đánh giá có thể đẹp giả).

File đã có thì không bị ghi đè, để không mất nhãn đã điền.
""")

code(r"""
CAP = GOC / "data" / "kiem_tra_tay" / "cap_tin_gan_trung.csv"
if not CAP.exists():
    rng_cap = np.random.default_rng(0)
    da_gom = [tuple(g.index[:2]) for _, g in df.groupby("nhom") if len(g) >= 2]
    gan_khong_gom = []
    for _, g in df.groupby("quan"):
        a, p, ix, nh = g["dt_dat"].to_numpy(), g["gia_ty"].to_numpy(), g.index.to_numpy(), g["nhom"].to_numpy()
        for k in range(len(g)):
            m = (np.abs(a - a[k]) / a[k] <= 0.03) & (np.abs(p - p[k]) / p[k] <= 0.12) & (nh != nh[k])
            m[: k + 1] = False
            gan_khong_gom += [(ix[k], ix[j]) for j in np.where(m)[0]]
    cap = [(c, "đã gom") for c in (da_gom[i] for i in rng_cap.choice(len(da_gom), min(25, len(da_gom)), replace=False))] + \
          [(c, "không gom") for c in (gan_khong_gom[i] for i in rng_cap.choice(len(gan_khong_gom), min(25, len(gan_khong_gom)), replace=False))]
    rng_cap.shuffle(cap)
    cot = ["tieu_de", "gia_ty", "dt_dat", "phuong", "duong", "nguon", "url"]
    dong = [{"ma_cap": n + 1, **{f"{c}_1": df.loc[i, c] for c in cot}, **{f"{c}_2": df.loc[j, c] for c in cot},
             "cung_mot_can": "", "quy_tac_da_gom": loai} for n, ((i, j), loai) in enumerate(cap)]
    CAP.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(dong).to_csv(CAP, index=False, encoding="utf-8-sig")
    print(f"Đã xuất {len(dong)} cặp ra {CAP.relative_to(GOC)}: điền cột cung_mot_can (1/0) rồi chạy lại notebook.")
else:
    nhan = pd.read_csv(CAP)
    da_dien = nhan[nhan["cung_mot_can"].isin([0, 1])]
    if len(da_dien) < len(nhan):
        print(f"{CAP.relative_to(GOC)}: mới điền {len(da_dien)}/{len(nhan)} cặp. Điền cột cung_mot_can (1 = cùng căn, 0 = khác căn) cho mọi cặp rồi chạy lại.")
    else:
        gom, khong = da_dien[da_dien["quy_tac_da_gom"] == "đã gom"], da_dien[da_dien["quy_tac_da_gom"] == "không gom"]
        print(f"Gom đúng: {gom['cung_mot_can'].mean() * 100:.0f}% ({int(gom['cung_mot_can'].sum())}/{len(gom)} cặp đã gom thật sự cùng một căn)")
        print(f"Bỏ sót: {khong['cung_mot_can'].mean() * 100:.0f}% ({int(khong['cung_mot_can'].sum())}/{len(khong)} cặp không gom thật ra là cùng một căn)")
""")

md(r"""
**Đọc kết quả ba phép kiểm** (số liệu lần chạy 17/11/2026):
- **Theo nguồn:** alonhadat, Chợ Tốt, guland có MAPE 22,6% / 23,2% / 26,2%, khoảng tin cậy chồng nhau → **không thấy mô hình kém hẳn với nguồn nào**. Guland hơi cao hơn vì tin guland chỉ có tiêu đề. Tỷ lệ tin bị lọc theo nguồn cũng không chênh lớn (2,7% / 6,9% / 10,4%): quy tắc lọc không thiên lệch theo một website.
- **Thiếu thông số là yếu tố ảnh hưởng mạnh nhất:** tin thiếu từ 2 trong 4 thông số (sàn, tầng, ngang, lối vào) sai 29,4%, tin đủ thông số sai 21,4%, hai khoảng tin cậy **không chồng nhau**. Vì vậy trang demo hiện nhãn "Thiếu vài thông số" khi người dùng nhập thiếu.
- **Độ chính xác tọa độ:** tọa độ riêng 21,7%, theo tuyến đường 23,7%, tâm phường 24,1%. Sai số tăng dần khi vị trí kém chính xác nhưng chênh nhỏ, khoảng tin cậy chồng nhau. Có tọa độ chính xác sẽ giúp nhưng không phải nguồn sai số chính.
- **Theo mức giá:** nhóm rẻ nhất sai nhiều nhất (30,5%), nhóm giữa ít nhất (18–20%). Tin rẻ bất thường thường là giá mồi, nhà nát, đất chưa thổ cư mà quy tắc lọc chưa bắt hết.
- **Theo phường:** chênh nhiều (Hiệp An 13%, Phú Mỹ 17% … Chánh Mỹ 35%); 9 phường dưới 20 căn ghi "chưa đủ mẫu", không nên kết luận về các phường này.
- **Ngưỡng lọc đơn giá:** chấm trên cùng 1.355 căn, MAPE Thủ Dầu Một của 4 ngưỡng chỉ trong khoảng 21,7–22,4%, khoảng tin cậy chồng nhau → **kết quả không phụ thuộc đáng kể vào ngưỡng lọc**. Lọc chặt hơn (loại thêm 134 tin) không làm mô hình tốt hơn, nên giữ ngưỡng 3 lần.
- **Gom tin trùng:** chờ gán nhãn tay 50 cặp trong `data/kiem_tra_tay/cap_tin_gan_trung.csv`.
""")

md(r"""
## Bước 12: Lưu mô hình và hàm dự đoán
- Huấn luyện lại mô hình đã chọn trên **toàn bộ** dữ liệu sạch → `model/mo_hinh_gia_nha.joblib` (kèm phân vị sai số để tính khoảng tin cậy).
- `model/mo_hinh_gia_nha.json`: **mô hình rút gọn** (Ridge, 11 thông số người dùng nhập được) cho trang demo `demo/trang_ban_nha.html` tính ngay trên trình duyệt. Mô hình này huấn luyện lại trên dữ liệu Phú Hòa mới, các thông số được **chặn trên ở phân vị 97%** để mô hình tuyến tính không ngoại suy quá đà. Sai số kiểm định chéo của nó được ghi kèm để trang demo hiển thị trung thực.
- `data/processed/nha_da_xu_ly.csv`: dữ liệu sạch + giá ước lượng (notebook xu hướng dùng lại).
""")

code(r"""
import json, joblib

mo_hinh_cuoi = MO_HINH[ten_tot_nhat]().fit(df, df["y"])
mo_hinh_cuoi_muc_tieu = getattr(getattr(mo_hinh_cuoi, "m_", None) if hasattr(mo_hinh_cuoi, "chu_") else mo_hinh_cuoi, "muc_tieu", "gia")
joblib.dump({"model": mo_hinh_cuoi, "ten": ten_tot_nhat, "phan_vi_sai_so": Q, "khoang_theo_muc": KHOANG, "dac_trung": DAC_TRUNG,
             "ngay_du_lieu": str(raw_chotot["ngay_thu_thap"].iloc[0]), "so_can": len(df)}, MODEL_DIR / "mo_hinh_gia_nha.joblib")

# --- mô hình rút gọn cho trang demo (cùng 11 đặc trưng như phiên bản 1) ---
ph_all = df[df["phu_hoa"] == 1].copy()
ph_all["duong_ntmk"] = ph_all["duong"].fillna("").str.contains("minh khai").astype(int)
ph_all["duong_lhp"] = ph_all["duong"].fillna("").str.contains("le hong phong").astype(int)
DEMO = {"dt_dat": "dt_dat", "mat_tien_x": "ngang", "so_tang_x": "so_tang", "dt_san_x": "dt_san", "phong_ngu_x": "phong_ngu",
        "so_wc": "so_wc", "vi_tri_cap": "cap_loi_vao", "hem_rong_x": "hem_rong", "duong_ntmk": "duong_ntmk",
        "duong_lhp": "duong_lhp", "noi_that_x": "noi_that"}
Xd = ph_all[list(DEMO.values())].astype(float); Xd.columns = list(DEMO)
# Mô hình tuyến tính ngoại suy rất sai với giá trị cực lớn (sàn 2.000 m², hẻm 60 m) -> chặn trên ở phân vị 97%.
# Trang web áp dụng đúng ngưỡng này trước khi tính (MODEL.clip_max).
CLIP = Xd.quantile(0.97)
Xd = Xd.clip(upper=CLIP, axis=1)
demo = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), Ridge(alpha=3.0))
p_demo = np.zeros(len(Xd))
for tr, va in GroupKFold(5, shuffle=True, random_state=RANDOM_STATE).split(Xd, groups=ph_all["nhom"]):     # cũng chia theo nhóm
    p_demo[va] = demo.fit(Xd.iloc[tr], ph_all["y"].iloc[tr]).predict(Xd.iloc[va])
cv_demo = chi_so_danh_gia(ph_all["y"], p_demo)
demo.fit(Xd, ph_all["y"])
imp, sc, rg = demo.named_steps["simpleimputer"], demo.named_steps["standardscaler"], demo.named_steps["ridge"]
json.dump({"features": list(DEMO), "medians": imp.statistics_.tolist(), "model": "Ridge (rút gọn cho web)",
           "scaler": {"mean": sc.mean_.tolist(), "scale": sc.scale_.tolist()}, "type": "linear",
           "coef": rg.coef_.tolist(), "intercept": float(rg.intercept_), "cv_mape": round(cv_demo["MAPE (%)"], 1),
           "clip_max": CLIP.round(3).tolist(),
           "n_samples": int(len(Xd)), "mo_hinh_day_du": ten_tot_nhat,
           "mo_hinh_day_du_mape_cv_phu_hoa": round(float(bang_cv_ph.loc[ten_tot_nhat, "MAPE (%)"]), 1)},
          open(MODEL_DIR / "mo_hinh_gia_nha.json", "w", encoding="utf-8"), ensure_ascii=False)

ghi = lambda b: b.round(3).reset_index(names="Mô hình").to_dict("records")
json.dump({"ten_mo_hinh": ten_tot_nhat, "mo_hinh_mape_thap_nhat": tot_nhat, "so_lan_lap": SO_LAN,
           "kiem_dinh_cheo_phu_hoa": ghi(bang_cv_ph), "kiem_dinh_cheo_tdm": ghi(bang_cv_tdm),
           "kiem_chung_phu_hoa": ghi(kiem_chung), "chon_mo_hinh": ghi(so_sanh.astype(float)),
           "test_phu_hoa": ghi(bang_test_ph), "test_tdm": ghi(bang_test_tdm),
           "phan_vi_sai_so_log": Q, "khoang_theo_muc": KHOANG, "do_phu_theo_muc": so_sanh_kh.round(2).reset_index(names="Mức giá").to_dict("records"), "mo_hinh_web": {"MAPE (%)": round(cv_demo["MAPE (%)"], 2), "Số căn": len(Xd)},
           "so_can": {"tat_ca": len(df), "tdm": int(df["tdm"].sum()), "phu_hoa": int(df["phu_hoa"].sum()), "so_nhom": int(df["nhom"].nunique())}},
          open(MODEL_DIR / "danh_gia_mo_hinh.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

luu = [c for c in df.columns if c not in ("van_ban", "mo_ta", "form_dac_diem")]
df[luu].to_csv(PROC / "nha_da_xu_ly.csv", index=False, encoding="utf-8-sig")
print("Mô hình web (Ridge rút gọn) – kiểm định chéo trên Phú Hòa:", {k: round(v, 2) for k, v in cv_demo.items()})
print("Đã lưu:", sorted(p.name for p in MODEL_DIR.iterdir()))
""")

md(r"""
### Giải thích dự đoán của mô hình đầy đủ cho từng căn
Permutation importance (Bước 9) cho biết nhóm đặc trưng nào quan trọng **trên toàn bộ dữ liệu**. Người xem một căn cụ thể cần câu trả lời khác: *vì sao căn **này** được định giá như vậy?*

LightGBM tính được **đóng góp của từng đặc trưng vào từng dự đoán** (giá trị SHAP theo cây, `pred_contrib=True`): dự đoán log = giá trị nền (trung bình dữ liệu) + tổng đóng góp. Vì mô hình học trên log, mỗi đóng góp đổi ra **% làm tăng/giảm giá** so với căn trung bình. Ta cộng đóng góp theo nhóm dễ hiểu (giá khu vực, lối vào, diện tích…).

Với căn nằm trong dữ liệu học, đặc trưng "giá khu vực" được tính **không có chính căn đó** (như khi huấn luyện), nên lời giải thích không bị giá rao của chính căn làm lệch.
""")

code(r"""
NHOM_GT = {
    "Giá khu vực (căn lân cận, phường, tuyến đường)": ["lg_knn", "lg_knn_med", "kc_knn_km", "lg_phuong", "lg_duong", "n_duong"],
    "Vị trí chi tiết (tọa độ, khoảng cách trung tâm)": ["lat", "lon", "kc_trung_tam_km"],
    "Diện tích và kích thước lô": ["log_dt", "ngang", "dai"],
    "Tầng, diện tích sàn, phòng, nội thất": ["so_tang", "dt_san", "ty_le_san", "phong_ngu", "so_wc", "noi_that", "t_cap4", "t_nha_moi", "t_nha_nat", "t_thang_may", "t_biet_thu"],
    "Lối vào (mặt tiền, hẻm)": ["mat_tien_duong", "cap_loi_vao", "hem_rong", "t_hem_xe_hoi", "t_hem_nho", "t_mat_tien", "t_goc", "t_kinh_doanh"],
    "Pháp lý": ["so_chung", "t_so_rieng", "t_so_chung", "t_chua_hc"],
}
def giai_thich(goi_mh, X):
    # Trả về (giá trị nền, DataFrame đóng góp log theo nhóm) – chỉ cho mô hình cây LightGBM
    m = goi_mh.m_ if hasattr(goi_mh, "chu_") else goi_mh
    if not hasattr(m, "kg_") or not isinstance(m.m_, LGBMRegressor):
        return None, None
    Xz = X.copy()
    if hasattr(goi_mh, "chu_"):        # mô hình xếp chồng: cột t_chu tính ngoài-fold như lúc huấn luyện
        u = Xz["y"].to_numpy() - np.log(Xz["dt_dat"].to_numpy())
        Xz["t_chu"] = goi_mh.chu_ngoai_fold(Xz, u)
    Z = pd.concat([Xz[list(m.features)].astype(float), m.kg_._tinh(Xz, loo=True)], axis=1)[m.columns_]
    C = m.m_.predict(Z, pred_contrib=True)
    dong_gop = pd.DataFrame(C[:, :-1], columns=m.columns_, index=X.index)
    nhom = {}
    da_dung = set()
    for ten, cols in NHOM_GT.items():
        cc = [c for c in cols if c in dong_gop]; da_dung |= set(cc); nhom[ten] = dong_gop[cc].sum(axis=1)
    nhom["Thông tin khác trong mô tả tin"] = dong_gop[[c for c in dong_gop if c not in da_dung]].sum(axis=1)
    return float(C[0, -1]), pd.DataFrame(nhom)

nen, GT = giai_thich(mo_hinh_cuoi, df)
if GT is None:
    print("Mô hình được chọn không phải LightGBM: bỏ qua phần giải thích theo SHAP.")
else:
    don_vi = "đơn giá (triệu/m²)" if mo_hinh_cuoi_muc_tieu == "don_gia" else "giá (tỷ)"
    print(f"Giá trị nền của mô hình (trung bình dữ liệu, thang log {don_vi}): {nen:.3f}")
    vd = df.index[(df["phu_hoa"] == 1)][np.argmax(np.abs(GT.loc[df["phu_hoa"] == 1].sum(axis=1)).to_numpy())]
    hieu_ung = (np.exp(GT.loc[vd]) - 1) * 100
    ax = hieu_ung.sort_values().plot.barh(color=np.where(hieu_ung.sort_values() > 0, "#C44E52", "#4C72B0"), figsize=(9, 3.8))
    ax.axvline(0, color="k", lw=0.8)
    ax.set(title=f"Vì sao căn này có giá như vậy? ({df.loc[vd, 'dt_dat']:.0f} m², rao {df.loc[vd, 'gia_ty']:.2f} tỷ)", xlabel="% làm tăng (+) / giảm (−) giá so với căn trung bình")
    plt.show()
    print("Đóng góp trung bình tuyệt đối theo nhóm (Phú Hòa, % giá):")
    display(((np.exp(GT.loc[df["phu_hoa"] == 1].abs()) - 1) * 100).mean().sort_values(ascending=False).round(1).to_frame("% trung bình"))
    gt_ph = {str(df.loc[i, "id"]): {k: round(float(v), 4) for k, v in GT.loc[i].items()} for i in df.index[df["phu_hoa"] == 1]}
    json.dump({"nen_log": round(nen, 4), "muc_tieu": mo_hinh_cuoi_muc_tieu, "mo_hinh": ten_tot_nhat, "nhom": list(GT.columns), "can": gt_ph},
              open(MODEL_DIR / "giai_thich_nha.json", "w", encoding="utf-8"), ensure_ascii=False)
    print("Đã lưu model/giai_thich_nha.json cho", len(gt_ph), "căn Phú Hòa")
""")

md(r"""
**Đọc biểu đồ:** cột đỏ là yếu tố làm căn này **đắt hơn** căn trung bình trong dữ liệu, cột xanh làm **rẻ hơn**. Nhóm "giá khu vực" thường lớn nhất: căn ở khu đắt thì giá cao, bất kể các thông số khác. Trang demo hiển thị đúng phân tích này trong phần chi tiết của từng tin.
""")

md(r"""
Hàm dự đoán cho một căn nhà mới. Thông số nào không biết thì để `None`. Nếu không có tọa độ, hàm dùng tọa độ trung vị của tuyến đường (hoặc của phường Phú Hòa). Có thể dán **mô tả tin** vào `mo_ta` để mô hình đọc thêm thông tin.
""")

code(r"""
goi = joblib.load(MODEL_DIR / "mo_hinh_gia_nha.joblib")

def du_doan_gia(dt_dat, ngang=None, dai=None, so_tang=None, dt_san=None, phong_ngu=None, so_wc=None,
                mat_tien_duong=0, cap_loi_vao=None, hem_rong=None, duong=None, phuong="phu hoa", quan="thu dau mot",
                lat=None, lon=None, mo_ta=""):
    van_ban = khong_dau(mo_ta)
    if lat is None:
        if duong and (quan, khong_dau(duong)) in xy_duong.index:
            lat, lon = xy_duong.loc[(quan, khong_dau(duong))].values
        else:
            lat, lon = xy_phuong.loc[(quan, phuong)].values
    can = pd.DataFrame([{"dt_dat": dt_dat, "ngang": ngang, "dai": dai, "so_tang": so_tang, "dt_san": dt_san,
                         "phong_ngu": phong_ngu, "so_wc": so_wc, "mat_tien_duong": mat_tien_duong, "cap_loi_vao": cap_loi_vao,
                         "hem_rong": hem_rong, "so_chung": np.nan, "noi_that": np.nan, "quan": quan, "phuong": phuong,
                         "duong": khong_dau(duong) if duong else None, "lat": lat, "lon": lon, "van_ban": van_ban}])
    can = pd.concat([can, trich_dac_trung_chu(can["van_ban"])], axis=1)
    can["log_dt"] = np.log(can["dt_dat"]); can["ty_le_san"] = can["dt_san"] / can["dt_dat"]
    can["kc_trung_tam_km"] = np.hypot((lat - TRUNG_TAM_TDM[0]) * 110.6, (lon - TRUNG_TAM_TDM[1]) * 109.3)
    can = can.astype({c_: float for c_ in ["ngang", "dai", "so_tang", "dt_san", "phong_ngu", "so_wc", "cap_loi_vao", "hem_rong"]})
    p = float(goi["model"].predict(can)[0])
    q = {k_: float(v[0]) for k_, v in phan_vi_cho(muc_gia(p, goi["khoang_theo_muc"]["nguong"]), goi["khoang_theo_muc"]).items()}
    return {"gia_du_doan_ty": round(np.exp(p), 2), "khoang_80_ty": (round(np.exp(p + q["q10"]), 2), round(np.exp(p + q["q90"]), 2))}

vi_du = {
    "Nhà cấp 4, 100 m² (5x20), hẻm xe hơi 4m": dict(dt_dat=100, ngang=5, dai=20, so_tang=1, dt_san=100, phong_ngu=2, so_wc=1,
                                                     cap_loi_vao=2, hem_rong=4, mo_ta="nhà cấp 4 hẻm xe hơi sổ riêng"),
    "Nhà 1 trệt 1 lầu, 80 m², hẻm xe tải 6m, khu dân cư": dict(dt_dat=80, ngang=4.5, so_tang=2, dt_san=160, phong_ngu=3, so_wc=2,
                                                                cap_loi_vao=3, hem_rong=6, mo_ta="1 trệt 1 lầu kdc hẻm 6m sổ hồng riêng"),
    "Nhà 1 trệt 2 lầu, 120 m², mặt tiền Nguyễn Thị Minh Khai": dict(dt_dat=120, ngang=6, dai=20, so_tang=3, dt_san=300, phong_ngu=4,
                                                                     so_wc=4, mat_tien_duong=1, cap_loi_vao=5, hem_rong=20,
                                                                     duong="Nguyễn Thị Minh Khai", mo_ta="mặt tiền kinh doanh"),
}
pd.DataFrame({k: du_doan_gia(**v) for k, v in vi_du.items()}).T
""")

md(r"""
## Kết luận

**Kết quả đạt được**
- **Phần A (cơ bản):** hồi quy tuyến tính và cây quyết định (độ sâu chọn bằng tập kiểm định, minh họa quá khớp) được so với baseline trên tập test (Bước 7).
- Dữ liệu **thật** từ 3 nguồn (guland, Chợ Tốt Nhà, alonhadat). Sau khi hợp nhất, sửa lỗi, loại trùng và loại tin không phải giá thị trường còn khoảng 1.470 căn, trong đó Phú Hòa khoảng 220 căn. Không dùng dữ liệu mô phỏng.
- Đánh giá bằng **kiểm định chéo lặp, chia theo nhóm tin gần trùng**, mọi chỉ số có khoảng tin cậy 95%. Mô hình được chọn theo quy tắc "đơn giản nhất mà không kém có ý nghĩa" (Bước 8). Con số trình bày gồm **ba cách đo** trên các căn Phú Hòa: kiểm định chéo (Bước 8), tập test giữ riêng (Bước 9) và dự đoán chéo theo nhóm trên toàn bộ căn Phú Hòa (Bước 11), mỗi số kèm khoảng tin cậy và cách đọc (bảng ngay dưới phần kết luận).
- So với cách làm của phiên bản 1 và baseline đơn giá phường: xem bảng kiểm chứng ở Bước 8, có kèm khoảng tin cậy của chênh lệch.
- Mỗi dự đoán có **khoảng giá 80%** đã kiểm chứng độ phủ, và mỗi tin Phú Hòa có **chẩn đoán** rẻ / hợp lý / cao so với thị trường (`ket_qua/output.csv`).
- Yếu tố quyết định giá: diện tích đất, **vị trí** (giá khu vực), sau đó là lối vào và thông tin trong mô tả tin.

**Những gì đã thử nhưng không cải thiện (đã gỡ khỏi quy trình)**
- Định vị tuyến đường bằng OpenStreetMap: chỉ áp dụng được cho khoảng 45 tin, không giảm sai số đo được. Nguyên nhân: tin rao không có số nhà, nên biết tuyến đường cũng chỉ định vị tới mức "đâu đó trên đường".
- Đặc trưng "giá các căn gần nhất cùng loại lối vào": không giảm sai số; mô hình vốn không lệch có hệ thống với nhà mặt tiền (Bước 9).

**Hạn chế còn lại (cần nêu khi trình bày)**
- Mô hình ước lượng **mặt bằng giá rao**, không phải giá giao dịch: vẫn là **giá rao bán**, chưa phải giá giao dịch công chứng (dữ liệu này không công khai). Sai số 20–25% phần lớn đến từ độ "ảo" của giá rao.
- **Sai số không đều:** tin thiếu thông số sai 29% so với 21% ở tin đủ thông số; nhóm giá rẻ nhất sai nhiều nhất; vài phường chưa đủ mẫu (Bước 11, kiểm tra độ tin cậy).
- **Tập test Phú Hòa nhỏ** (vài chục căn): MAPE test cao hơn MAPE kiểm định chéo và khoảng tin cậy của nó rất rộng. Hai khoảng tin cậy chồng nhau nên kết quả không mâu thuẫn, nhưng **chưa đủ để khẳng định độ chính xác ổn định ở riêng Phú Hòa**; cần thêm tin Phú Hòa độc lập qua các kỳ thu thập định kỳ.
- Vị trí chỉ chính xác tới **tuyến đường hoặc phường** với phần lớn tin; muốn tốt hơn cần số nhà hoặc tọa độ do người đăng ghim.
- Tin guland (phần lớn dữ liệu Phú Hòa) hiện chỉ có tiêu đề. Script `thu_thap/guland_thu_thap.js` đã được sửa để lưu cả mô tả; lần thu thập tới notebook tự dùng cột này.
- Không có thông tin chất lượng xây dựng thật (vật liệu, tuổi nhà); chỉ đọc được gián tiếp qua mô tả.
- **Căn hộ chung cư** không nằm trong mô hình này: xem notebook `du_doan_gia_can_ho.ipynb` (cùng quy trình đánh giá, đặc trưng riêng: dự án, tầng, pháp lý, nhà ở xã hội).
- Mô hình phản ánh thị trường **tháng 11/2026**; cần cập nhật dữ liệu định kỳ (`thu_thap/cap_nhat_dinh_ky.py`). Xu hướng giá được phân tích ở notebook `du_doan_xu_huong_gia.ipynb`.
""")

code(r"""
# Con số cần trình bày: 3 cách đo trên các căn Phú Hòa, mỗi số kèm khoảng tin cậy 95% (bootstrap theo nhóm tin gần trùng)
cv_, te_ = bang_cv_ph.loc[ten_tot_nhat], bang_test_ph.loc[ten_tot_nhat]
ph_all_ = df[df["phu_hoa"] == 1]
ape_all = np.abs(ph_all_["gia_uoc_luong_ty"] / ph_all_["gia_ty"] - 1).to_numpy() * 100     # dự đoán chéo theo nhóm ở Bước 11
lo_all, hi_all = ktc_bootstrap(ape_all, ph_all_["nhom"].to_numpy())
phu_all = ((ph_all_["gia_ty"] >= ph_all_["khoang80_thap"]) & (ph_all_["gia_ty"] <= ph_all_["khoang80_cao"])).mean() * 100
TOM_TAT = pd.DataFrame({
    "Cách đo": ["KẾT QUẢ CHÍNH – Tập test giữ riêng: căn Phú Hòa chưa dùng ở bất kỳ bước nào",
                "Bổ trợ – Kiểm định chéo lặp theo nhóm: căn Phú Hòa trong tập train",
                "Bổ trợ – Dự đoán chéo theo nhóm trên TOÀN BỘ căn Phú Hòa (Bước 11)"],
    "Số căn": [int(te_["Số căn"]), int(cv_["Số căn"]), len(ph_all_)],
    "MAPE (%)": [round(te_["MAPE (%)"], 1), round(cv_["MAPE (%)"], 1), round(ape_all.mean(), 1)],
    "KTC 95%": [f"{te_['MAPE thấp (95%)']:.1f} – {te_['MAPE cao (95%)']:.1f}", f"{cv_['MAPE thấp (95%)']:.1f} – {cv_['MAPE cao (95%)']:.1f}", f"{lo_all:.1f} – {hi_all:.1f}"],
}).set_index("Cách đo")
display(TOM_TAT)
print(f"Độ phủ khoảng 80% trên toàn bộ {len(ph_all_)} căn Phú Hòa: {phu_all:.1f}%")
print("Cách đọc: tập test là KẾT QUẢ CHÍNH vì là bằng chứng sạch nhất (căn chưa từng dùng ở bất kỳ bước nào), nhưng chỉ vài chục căn nên khoảng tin cậy rộng. "
      "Dòng cuối dùng mọi căn Phú Hòa, mỗi căn được dự đoán bởi mô hình không học căn đó và các tin gần trùng, nên khoảng tin cậy hẹp hơn nhiều; "
      "nhưng các căn của tập train đã tham gia bước CHỌN mô hình, nên nó có thể lạc quan nhẹ và chỉ dùng để bổ trợ, không thay thế tập test. Ba con số nhất quán với nhau "
      "thì mới kết luận sai số ở Phú Hòa vào khoảng giữa các giá trị này.")
""")

nb = nbf.v4.new_notebook()
nb["cells"] = cells
nb["metadata"]["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
nbf.write(nb, sys.argv[1])
print("written", len(cells), "cells")
