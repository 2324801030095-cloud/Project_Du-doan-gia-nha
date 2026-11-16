# Dự đoán giá nhà Phú Hòa – Thủ Dầu Một

Đề tài môn Học máy · MSSV 2324801030095 · Nguyễn Quang Long · Lớp D23KTPM01

Mô hình học máy ước lượng **mặt bằng giá rao** của **nhà phố**, **căn hộ chung cư** và **đất nền**, chẩn đoán giá rao rẻ / hợp lý / cao,
ước lượng **giá thuê và tỷ suất cho thuê**, và phân tích xu hướng giá.
Lưu ý: dữ liệu là **giá rao bán**, không phải giá giao dịch; mọi kết quả cần đọc là "so với mặt bằng giá rao".
Toàn bộ dữ liệu là tin rao bán thật (guland, Chợ Tốt Nhà, alonhadat); không dùng dữ liệu mô phỏng.

## Cấu trúc thư mục

```
├── notebooks/                    BÀI LÀM CHÍNH – mở các notebook này để xem / trình bày
│   ├── 2324801030095.ipynb           Định giá nhà phố (nhà gắn liền với đất)
│   ├── du_doan_gia_can_ho.ipynb      Định giá căn hộ chung cư
│   ├── du_doan_gia_dat.ipynb         Định giá đất nền / đất thổ cư
│   ├── du_doan_gia_thue.ipynb        Giá thuê, tỷ suất cho thuê, số năm hoàn vốn
│   └── du_doan_xu_huong_gia.ipynb    Phân tích xu hướng giá (kịch bản tham khảo, chưa phải dự báo đã kiểm định)
│
├── src/
│   └── mo_hinh_gia.py            Mã dùng chung: trích đặc trưng, các lớp mô hình, hàm đánh giá
│
├── thu_thap/                     Script thu thập dữ liệu thật
│   ├── chotot_thu_thap.py            Chợ Tốt Nhà (nhà ở; --can-ho căn hộ; --dat đất)
│   ├── alonhadat_thu_thap.py         alonhadat (nhà ở; --can-ho; --dat)
│   ├── guland_thu_thap.js            guland (chạy trong trình duyệt, vì trang chặn truy cập tự động)
│   ├── cap_nhat_dinh_ky.py           Thu thập lại 6 nguồn + lưu ảnh chụp có ghi ngày vào data/lich_su/
│   ├── chay_dinh_ky.bat              Chạy cap_nhat_dinh_ky.py, ghi nhật ký data/lich_su/nhat_ky_thu_thap.txt
│   ├── bat_lich_tu_dong.bat          Đăng ký Task Scheduler: 08:00 mỗi Chủ nhật (bù khi máy tắt)
│   └── tat_lich_tu_dong.bat          Gỡ lịch tự động
│
├── data/
│   ├── raw/                      Dữ liệu gốc tải về – KHÔNG sửa tay
│   ├── processed/                Dữ liệu đã làm sạch + danh sách tin bị loại (do notebook sinh ra)
│   └── lich_su/                  Ảnh chụp dữ liệu theo ngày, dùng cho phân tích xu hướng
│
├── model/                        Mô hình đã huấn luyện (.joblib) + mô hình rút gọn cho web (.json) + kết quả đánh giá
│
├── ket_qua/                      Kết quả dạng bảng (thêm output_dat.csv, ty_suat_cho_thue.csv)
│   ├── input.csv                     Thông số các căn nhà phố Phú Hòa
│   ├── output.csv                    Giá ước lượng, khoảng 80%, chẩn đoán – nhà phố Phú Hòa
│   └── output_can_ho.csv             Giá ước lượng, khoảng 80%, chẩn đoán – căn hộ Thủ Dầu Một
│
├── demo/                         Trang web demo
│   ├── trang_ban_nha.html            Mở file này bằng trình duyệt (có trợ lý hỏi đáp: bong bóng góc phải)
│   ├── du_doan_gia_nha.html          Lối tắt tới mục định giá
│   ├── assets/                       Ảnh minh họa
│   └── _build/                       Mẫu trang + script dựng trang từ kết quả trong model/ và data/
│
├── cong_cu/                      Script sinh lại 5 notebook + an_danh_du_lieu.py (bỏ thông tin người đăng, che số điện thoại)
│
├── tests/                        Kiểm thử tự động (mô hình + trợ lý hỏi đáp)
├── requirements.txt              Thư viện Python cần cài (đúng phiên bản đã kiểm chứng)
│
└── luu_tru/                      Phiên bản cũ, chỉ để đối chiếu, không dùng nữa
    ├── v1/                           Bản 1 (Ridge trên guland, lịch sử giá mô phỏng)
    ├── v2/                           Bản 2 (trước khi chia nhóm tin gần trùng)
    └── demo/                         Các bản trang demo cũ
```

## Cài đặt

```
pip install -r requirements.txt          # Python 3.14
```
Kiểm thử trợ lý cần thêm Node.js (≥ 18).

## Chạy lại toàn bộ

Chạy từ thư mục gốc đề tài, theo đúng thứ tự (bước sau dùng kết quả của bước trước):

```
# 1. (tùy chọn) cập nhật dữ liệu mới nhất
python thu_thap/cap_nhat_dinh_ky.py

# 2. định giá nhà phố (~10 phút) và căn hộ (~4 phút)
jupyter nbconvert --to notebook --execute --inplace notebooks/2324801030095.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/du_doan_gia_can_ho.ipynb

# 2b. giá thuê (dùng kết quả bước 2) và đất nền
jupyter nbconvert --to notebook --execute --inplace notebooks/du_doan_gia_thue.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/du_doan_gia_dat.ipynb

# 3. xu hướng giá (dùng kết quả của bước 2)
jupyter nbconvert --to notebook --execute --inplace notebooks/du_doan_xu_huong_gia.ipynb

# 4. dựng lại trang demo
python demo/_build/build_site.py
```

```
# 5. kiểm thử tự động (nên chạy sau mỗi lần sửa)
python tests/kiem_tra_mo_hinh.py         # chống rò rỉ, gom tin trùng, khoảng tin cậy, nạp mô hình, dữ liệu sạch
node tests/kiem_tra_tro_ly.js            # trợ lý: hiểu ý định, trích thông tin, số liệu khớp mô hình, nhớ ngữ cảnh
```

Mở notebook trong Jupyter thì chạy **Restart & Run All**; notebook tự tìm thư mục gốc dù mở từ `notebooks/` hay từ thư mục gốc.

Muốn sửa nội dung notebook: sửa trực tiếp trong notebook, hoặc sửa script trong `cong_cu/` rồi sinh lại
(`python cong_cu/dung_notebook_chinh.py notebooks/2324801030095.ipynb`). Sinh lại sẽ ghi đè notebook.

## Kết quả chính (dữ liệu 17/11/2026, sai số MAPE trên giá rao)

| | Nhà phố (Phú Hòa) | Căn hộ chung cư | Đất nền (TDM) | Giá thuê |
|---|---|---|---|---|
| Mô hình được chọn | LightGBM | LightGBM Huber + chữ | Ridge | Ridge (căn hộ, nhà) |
| Kiểm định chéo lặp, chia theo nhóm tin gần trùng | 23,2% (KTC 20,6–26,3) | 12,0% (11,0–13,2) | 26,0% | căn hộ 18,4% · nhà 27,7% |
| Tập test giữ riêng | 27,5% (KTC 20,8–35,7; 40 căn) | 10,6% | 30,2% (KTC 22,3–39,8; 72 lô) | căn hộ 16,0% · nhà 29,1% |
| Khoảng giá 80% (độ phủ kiểm tra trên test) | có | có | 79% | – |

Tập test Phú Hòa nhỏ nên khoảng tin cậy rộng; cần trình bày **cả hai** con số kiểm định chéo và test.
Khoảng 80% là khoảng hiệu chỉnh thực nghiệm từ sai số ngoài-fold (ý tưởng conformal), không phải bảo đảm lý thuyết.
Xu hướng giá 6–12 tháng là **kịch bản tham khảo**, chưa phải dự báo đã kiểm định lùi (mới có vài kỳ dữ liệu).

Số liệu chi tiết, khoảng tin cậy và giới hạn: xem phần kết luận của từng notebook.

## Trợ lý hỏi đáp trên trang demo

Bấm bong bóng **"Hỏi trợ lý"** ở góc phải dưới (hoặc mục *Trợ lý* trên menu) để mở trang hỏi đáp `#/tro-ly`.
Trợ lý chạy hoàn toàn trên trình duyệt, không gửi câu hỏi đi đâu và không cần khóa API. Nó hiểu câu hỏi tiếng Việt
(nhận diện ý định + trích diện tích, giá, số tầng, hẻm/mặt tiền, dự án, phường) rồi trả lời **từ chính dữ liệu và mô hình
của đề tài**: định giá nhà phố / căn hộ, tìm nhà theo ngân sách, xu hướng giá, so sánh phường, dự án căn hộ, kiến thức
pháp lý – nhà ở xã hội – lưu ý khi mua. Có nhớ ngữ cảnh để hỏi tiếp ("nếu là mặt tiền thì sao?").
Mã nằm trong `demo/_build/template.html` (phần "Trợ lý hỏi đáp").

## Trang demo: các chức năng
- **Nhà phố** (trang chủ, `#/dinh-gia`): định giá, khoảng 80%, giá thuê + tỷ suất ước tính; chi tiết từng tin có
  **"Vì sao căn này có giá như vậy"** (đóng góp SHAP của mô hình LightGBM đầy đủ, gom theo nhóm yếu tố).
- **Căn hộ** (`#/can-ho`), **Đất nền** (`#/dat`): định giá + bảng tin đang rao ở Thủ Dầu Một kèm chẩn đoán.
- **Bản đồ giá** (`#/ban-do`): điểm tin rao có tọa độ đủ chính xác, màu theo đơn giá; lọc nhà phố / căn hộ / đất / cho thuê.
  Dùng Leaflet + nền OpenStreetMap (cần Internet); không có mạng thì vẽ sơ đồ điểm thay thế.
- **Yêu thích & so sánh** (`#/so-sanh`): lưu tin (trái tim), so sánh 2–3 tin cạnh nhau. Chỉ lưu trên trình duyệt (localStorage).
- **Trợ lý** (`#/tro-ly`): thêm câu hỏi về giá thuê / hoàn vốn và định giá đất.

## Thu thập định kỳ
`thu_thapat_lich_tu_dong.bat` đăng ký tác vụ Windows *PhuHoaHome_ThuThapDinhKy* (08:00 Chủ nhật hằng tuần). Mỗi lần chạy
thêm một kỳ ảnh chụp vào `data/lich_su/`; khi đủ ≥ 8 kỳ, notebook xu hướng tự huấn luyện và kiểm định lùi mô hình dự báo.
Nguồn bị chặn tạm thời (HTTP 429) thì giữ nguyên file cũ, ghi lỗi vào nhật ký và vẫn thu các nguồn còn lại.
Gỡ lịch: `thu_thap	at_lich_tu_dong.bat`.

## Riêng tư dữ liệu
Script thu thập **không lưu** tên, mã tài khoản, ảnh đại diện của người đăng và **che số điện thoại** trong tiêu đề / mô tả
(`cong_cu/an_danh_du_lieu.py`; chạy lại script này nếu có dữ liệu cũ).
