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
│   ├── tro_ly_y_dinh.ipynb           Huấn luyện mô hình hiểu câu hỏi cho trợ lý (TF-IDF + Logistic Regression)
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
│   ├── lich_su/                  Ảnh chụp dữ liệu theo ngày, dùng cho phân tích xu hướng
│   ├── tro_ly/                   Câu hỏi có gán nhãn ý định để huấn luyện / kiểm tra trợ lý
│   └── kiem_tra_tay/             Mẫu cặp tin để gán nhãn tay việc gom tin trùng (notebook nhà phố, Bước 11)
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
├── cong_cu/                      Script sinh lại 6 notebook + an_danh_du_lieu.py (bỏ thông tin người đăng, che số điện thoại)
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

# 4. trợ lý: mô hình hiểu câu hỏi (cần Node.js để so sánh với luật cũ)
jupyter nbconvert --to notebook --execute --inplace notebooks/tro_ly_y_dinh.ipynb

# 5. dựng lại trang demo
python demo/_build/build_site.py
```

```
# 6. kiểm thử tự động (nên chạy sau mỗi lần sửa)
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
| **Tập test giữ riêng (kết quả chính)** | **27,5%** (KTC 20,8–35,7; 40 căn) | **10,6%** | **30,2%** (KTC 22,3–39,8; 72 lô) | căn hộ 16,0% · nhà 29,1% |
| Kiểm định chéo lặp, chia theo nhóm tin gần trùng (bổ trợ) | 23,2% (KTC 20,6–26,3) | 12,0% (11,0–13,2) | 26,0% | căn hộ 18,4% · nhà 27,7% |
| Dự đoán chéo theo nhóm trên toàn bộ căn Phú Hòa (bổ trợ) | 24,5% (KTC 21,6–27,7; 220 căn, 169 nhóm) | | | |
| Khoảng giá 80% (độ phủ kiểm tra trên test) | có | có | 79% | – |

Tập test là **kết quả chính** vì là bằng chứng sạch nhất; nó nhỏ (40 căn) nên khoảng tin cậy rộng. Hai con số còn lại để bổ trợ: test là bằng chứng sạch nhất nhưng bất định; con số trên toàn bộ 220 căn có khoảng tin cậy hẹp hơn nhưng có thể lạc quan nhẹ vì phần lớn các căn đó đã tham gia bước chọn mô hình.
**Kiểm tra độ tin cậy** (notebook nhà phố, cuối Bước 11): sai số theo nguồn tương đương nhau (22,6–26,2%); tin **thiếu thông số**
sai 29% so với 21% ở tin đủ thông số; tọa độ tâm phường sai hơn tọa độ riêng một chút (24,1% so với 21,7%); nhóm giá rẻ nhất sai
nhiều nhất (30,5%); đổi ngưỡng lọc đơn giá (2, 3, 5 lần, không lọc) chỉ làm MAPE đổi trong 21,7–22,4%. Việc gom tin trùng chờ
gán nhãn tay 50 cặp trong `data/kiem_tra_tay/cap_tin_gan_trung.csv`.
Khoảng 80% là khoảng hiệu chỉnh thực nghiệm từ sai số ngoài-fold (ý tưởng conformal), không phải bảo đảm lý thuyết.
Xu hướng giá theo kỳ hạn (1, 3, 6, 12, 18, 24 tháng; trang demo cho chọn 1–12, 18, 24 tháng) = biên mỗi tháng × số tháng, là **kịch bản tham khảo**, chưa phải dự báo đã kiểm định lùi: hiện có 3 kỳ ảnh chụp, tin rao chỉ có ngày đăng trong khoảng 2 tháng gần nhất, nên chưa đủ dữ liệu để kiểm định trung thực. Mã kiểm định lùi (`kiem_dinh_lui` trong `src/mo_hinh_gia.py`) đã có kiểm thử tự động và sẽ tự chạy khi đủ 8 kỳ, dự kiến khoảng cuối tháng 12/2026 theo lịch thu thập hằng tuần.

Số liệu chi tiết, khoảng tin cậy và giới hạn: xem phần kết luận của từng notebook.

## Trợ lý hỏi đáp trên trang demo

Bấm bong bóng **"Hỏi trợ lý"** ở góc phải dưới (hoặc mục *Trợ lý* trên menu) để mở trang hỏi đáp `#/tro-ly`.

- **Hiểu câu hỏi bằng mô hình học máy**: notebook `notebooks/tro_ly_y_dinh.ipynb` huấn luyện mô hình phân loại 19 ý định
  (TF-IDF n-gram ký tự + từ, Logistic Regression) trên `data/tro_ly/cau_hoi_huan_luyen.csv`, đánh giá trên tập kiểm tra viết
  riêng `data/tro_ly/cau_hoi_kiem_tra.csv` (câu không dấu, viết tắt, diễn đạt khác). Trên tập kiểm tra: luật từ khóa cũ đúng
  74,7% và bỏ sót 24,7% số câu; trợ lý hiện tại đúng khoảng 92%, chỉ còn vài phần trăm câu không nhận ra.
- **Kết hợp với luật cũ** theo chiến lược chọn bằng kiểm định chéo (luật nhận ra thì theo luật, không thì theo mô hình);
  luật vẫn trích con số (diện tích, giá, số tầng…) và nhận biết câu hỏi tiếp ("nếu là mặt tiền thì sao?").
- **Không chắc thì hỏi lại**: mô hình chắc dưới 40% thì trợ lý đưa 2–3 gợi ý "Có phải bạn muốn hỏi…"; câu ngoài phạm vi
  (thời tiết, giá vàng…) được từ chối lịch sự.
- Chạy hoàn toàn trên trình duyệt, không gửi câu hỏi đi đâu, không cần khóa API. Câu trả lời lấy từ dữ liệu và mô hình
  định giá của đề tài. Trợ lý **không tự sinh văn bản tự do** như mô hình ngôn ngữ lớn: nó phân loại ý định rồi trả lời bằng
  các hàm có sẵn.
- Hạn chế: câu huấn luyện do người làm đề tài viết, chưa có câu hỏi thật của người dùng; trên tập kiểm tra, mô hình đơn lẻ
  còn tốt hơn chiến lược kết hợp đã chọn (xem notebook) → nên có thêm tập kiểm định riêng để chọn lại chiến lược.

Sửa câu hỏi huấn luyện xong thì chạy lại notebook rồi `python demo/_build/build_site.py`.

## Gợi ý trình bày khi bảo vệ (thời gian ngắn)
1. **Bài toán chính – nhà phố Phú Hòa** (notebook `2324801030095.ipynb`): dữ liệu thật → làm sạch → đặc trưng → so sánh mô hình với baseline → **tập test** (MAPE 27,5%, có khoảng tin cậy). Giải thích MAPE bằng bảng ví dụ căn thật ở Bước 8.
2. **Vì sao tin tưởng được con số:** chia train/test theo nhóm tin gần trùng (chống rò rỉ), chọn mô hình bằng quy tắc thống kê, khoảng giá 80% có kiểm tra độ phủ.
3. **Giới hạn:** giá rao ≠ giá giao dịch; tập test nhỏ; xu hướng mới là kịch bản tham khảo.
4. **Mở rộng (nếu còn thời gian):** căn hộ, đất nền, giá thuê dùng lại cùng quy trình; demo web và trợ lý.

## Trang demo: các chức năng
- **Nhà phố** (trang chủ, `#/dinh-gia`): định giá, khoảng 80%, giá thuê + tỷ suất ước tính; chi tiết từng tin có
  **"Vì sao căn này có giá như vậy"** (đóng góp SHAP của mô hình LightGBM đầy đủ, gom theo nhóm yếu tố).
- **Căn hộ** (`#/can-ho`), **Đất nền** (`#/dat`): định giá + bảng tin đang rao ở Thủ Dầu Một kèm chẩn đoán.
- **Bản đồ giá** (`#/ban-do`): điểm tin rao có tọa độ đủ chính xác, màu theo đơn giá; lọc nhà phố / căn hộ / đất / cho thuê.
  Dùng Leaflet + nền OpenStreetMap (cần Internet); không có mạng thì vẽ sơ đồ điểm thay thế.
- **Yêu thích & so sánh** (`#/so-sanh`): lưu tin (trái tim), so sánh 2–3 tin cạnh nhau. Chỉ lưu trên trình duyệt (localStorage).
- **Trợ lý** (`#/tro-ly`): thêm câu hỏi về giá thuê / hoàn vốn và định giá đất.

## Thu thập định kỳ
`thu_thap/bat_lich_tu_dong.bat` đăng ký tác vụ Windows *PhuHoaHome_ThuThapDinhKy* (08:00 Chủ nhật hằng tuần). Mỗi lần chạy
thêm một kỳ ảnh chụp vào `data/lich_su/`; khi đủ ≥ 8 kỳ, notebook xu hướng tự huấn luyện và kiểm định lùi mô hình dự báo.
Nguồn bị chặn tạm thời (HTTP 429) thì giữ nguyên file cũ, ghi lỗi vào nhật ký và vẫn thu các nguồn còn lại.
Nếu số tin của một nguồn **giảm hơn 30% so với kỳ trước** (thường do trang đổi giao diện hoặc bị chặn một phần), nhật ký ghi
CẢNH BÁO và tác vụ kết thúc với mã lỗi. Cuối mỗi lần chạy, nhật ký in bảng số tin theo kỳ và theo nguồn.
Gỡ lịch: `thu_thap/tat_lich_tu_dong.bat`.

## Riêng tư dữ liệu
Script thu thập **không lưu** tên, mã tài khoản, ảnh đại diện của người đăng và **che số điện thoại** trong tiêu đề / mô tả
(`cong_cu/an_danh_du_lieu.py`; chạy lại script này nếu có dữ liệu cũ).
