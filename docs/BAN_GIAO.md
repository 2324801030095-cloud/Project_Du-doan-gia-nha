# Báo cáo bàn giao kỹ thuật – Dự đoán giá nhà Phú Hòa

Ngày lập: 24/11/2026 · Dữ liệu hiện hành: tin rao thu thập 17/11/2026 · Repo: `2324801030095-cloud/Project_Du-doan-gia-nha` (public, nhánh `main`)

Tài liệu này giải thích **logic của toàn bộ hệ thống** để người nhận có thể đọc, kiểm tra lại và tiếp tục phát triển. Đọc theo thứ tự: mục 1 (tóm tắt) → 2 (kiến trúc) → 9 (checklist kiểm tra), các mục còn lại tra cứu khi cần.

---

## 1. Tóm tắt

**Hệ thống làm gì.** Ước lượng **mặt bằng giá rao** của bất động sản ở Thủ Dầu Một (trọng tâm phường Phú Hòa) bằng học máy có giám sát, gồm 4 mô hình (nhà phố, căn hộ, đất nền, giá thuê), một phân tích xu hướng giá, một trợ lý hỏi đáp và một trang web demo chạy hoàn toàn trên trình duyệt.

**Điều quan trọng nhất cần nhớ:** dữ liệu là **giá rao bán** trên các trang tin, không phải giá giao dịch. Mọi kết quả phải đọc là "so với mặt bằng giá rao".

**Tình trạng lúc bàn giao**

| Hạng mục | Trạng thái |
|---|---|
| 6 notebook | Chạy trọn từ đầu tới cuối, không ô lỗi, còn đủ output |
| Kiểm thử | `tests/kiem_tra_mo_hinh.py` 10/10 · `tests/kiem_tra_tro_ly.js` 27/27 |
| Môi trường | Python 3.14.7, Node 24; phiên bản thư viện đã cài **khớp đúng** `requirements.txt` |
| Thu thập định kỳ | Tác vụ Windows đã đăng ký, chạy 08:00 Chủ nhật. **Lần 22/11 bị ngắt giữa chừng** (xem mục 3.4) |
| Dữ liệu | Đã ẩn danh (không còn thông tin người đăng, số điện thoại đã che) |

**Kết quả chính** (MAPE = sai số phần trăm trung bình; KTC = khoảng tin cậy 95% bootstrap theo nhóm tin gần trùng)

| Mô hình | Mô hình được chọn | Tập test giữ riêng (kết quả chính) | Kiểm định chéo theo nhóm | Baseline |
|---|---|---|---|---|
| Nhà phố – Phú Hòa | LightGBM | **27,5%** (KTC 20,8–35,7; 40 căn) | 23,2% (20,6–26,3) | 28,9% |
| Căn hộ | LightGBM Huber + mô hình chữ | **10,6%** | 12,0% (11,0–13,2) | 15,5% |
| Đất nền – TDM | Ridge | **30,2%** (KTC 22,3–39,8; 72 lô) | 26,0% | 38,4% |
| Giá thuê | Ridge | căn hộ 16,0% · nhà 29,1% | căn hộ 18,4% · nhà 27,7% | – |
| Trợ lý (phân loại ý định) | Logistic Regression + luật | 93,7% đúng (158 câu) | – | luật cũ 74,7% |

**5 rủi ro lớn nhất** (chi tiết ở mục 8): giá rao ≠ giá giao dịch; dữ liệu theo thời gian mới có 3 kỳ trong 1 tuần nên xu hướng chưa kiểm định được; 50% nhà phố chỉ có tọa độ tâm phường; tập test Phú Hòa chỉ 40 căn; căn hộ gần như chỉ từ một nguồn (Chợ Tốt).

---

## 2. Kiến trúc và luồng dữ liệu

```
thu_thap/ (script tải tin)          data/raw/ (dữ liệu gốc, đã ẩn danh)        data/lich_su/ (ảnh chụp theo ngày)
        │                                   │                                          │
        └──────────────► notebooks/ (6 notebook, sinh từ cong_cu/*.py, dùng src/mo_hinh_gia.py)
                                            │
             ┌──────────────────────────────┼───────────────────────────────┐
     data/processed/ (dữ liệu sạch)   model/ (.joblib đầy đủ + .json cho web)   ket_qua/ (bảng kết quả .csv)
             └──────────────────────────────┼───────────────────────────────┘
                                            ▼
                         demo/_build/build_site.py + template.html
                                            ▼
                         demo/trang_ban_nha.html (1 file, nhúng sẵn dữ liệu và tham số mô hình)
```

### 2.1 Thư mục

| Thư mục | Nội dung | Ai ghi |
|---|---|---|
| `thu_thap/` | Script tải tin Chợ Tốt, alonhadat, guland; chạy định kỳ; file .bat đăng ký/gỡ lịch | người |
| `data/raw/` | Dữ liệu gốc tải về. **Không sửa tay.** Script thu thập ghi đè khi tải thành công | script thu thập |
| `data/lich_su/` | Ảnh chụp có ghi ngày của dữ liệu gốc + nhật ký thu thập | `cap_nhat_dinh_ky.py` |
| `data/processed/` | Dữ liệu đã làm sạch, danh sách tin bị loại (kèm lý do) | notebook |
| `data/tro_ly/` | Câu hỏi có gán nhãn ý định (huấn luyện / kiểm tra) | người |
| `data/kiem_tra_tay/` | 50 cặp tin chờ gán nhãn tay để kiểm tra việc gom tin trùng | notebook nhà phố (không ghi đè) |
| `src/mo_hinh_gia.py` | Mã dùng chung: đặc trưng, lớp mô hình, đánh giá, khoảng giá, kiểm định lùi | người |
| `cong_cu/` | Script **sinh** 6 notebook + `an_danh_du_lieu.py` | người |
| `notebooks/` | 6 notebook đã chạy (bài làm chính) | sinh từ `cong_cu/`, rồi chạy |
| `model/` | Mô hình đầy đủ (`.joblib`), mô hình rút gọn và số liệu cho web (`.json`), kết quả đánh giá | notebook |
| `ket_qua/` | Bảng định giá, chẩn đoán, tỷ suất cho thuê | notebook |
| `demo/` | `trang_ban_nha.html` (trang web), `assets/` (ảnh), `_build/` (mẫu trang, script dựng, icon, nguồn ảnh) | `build_site.py` |
| `tests/` | Kiểm thử mô hình (Python) và trợ lý/trang web (Node) | người |

### 2.2 Thứ tự chạy và phụ thuộc (quan trọng)

| # | Lệnh | Cần có trước | Ghi ra |
|---|---|---|---|
| 0 | `python thu_thap/cap_nhat_dinh_ky.py` (tùy chọn) | mạng | `data/raw/*`, `data/lich_su/*` |
| 1 | notebook nhà phố `2324801030095.ipynb` | `data/raw` | `processed/nha_da_xu_ly.csv`, `tin_bi_loai.csv`, `model/mo_hinh_gia_nha.*`, `danh_gia_mo_hinh.json`, `giai_thich_nha.json`, `ket_qua/input.csv`, `output.csv`, `data/kiem_tra_tay/*` |
| 2 | `du_doan_gia_can_ho.ipynb` | `data/raw` | `processed/can_ho_*`, `model/mo_hinh_gia_can_ho.*`, `ket_qua/output_can_ho.csv` |
| 3 | `du_doan_gia_thue.ipynb` | **1 và 2** | `model/mo_hinh_gia_thue.joblib`, `gia_thue_web.json`, `ket_qua/ty_suat_cho_thue.csv`, `processed/thue_da_xu_ly.csv`; **ghi thêm 2 cột giá thuê vào `nha_da_xu_ly.csv` và `can_ho_da_xu_ly.csv`** |
| 4 | `du_doan_gia_dat.ipynb` | 1 (dùng tọa độ tuyến đường của nhà phố) | `processed/dat_*`, `model/mo_hinh_gia_dat.*`, `ket_qua/output_dat.csv` |
| 5 | `du_doan_xu_huong_gia.ipynb` | 1, `data/lich_su` | `model/xu_huong_gia.json` |
| 6 | `python demo/_build/build_site.py` | 1–5 | `demo/trang_ban_nha.html` |
| 7 | `tro_ly_y_dinh.ipynb` | **6** (chạy luật của trang qua Node để so sánh) | `model/tro_ly_y_dinh.joblib` |
| 8 | `python demo/_build/build_site.py` lần nữa | 7 | nhúng mô hình trợ lý vào trang |
| 9 | `python tests/kiem_tra_mo_hinh.py` và `node tests/kiem_tra_tro_ly.js` | tất cả | – |

**Bẫy thường gặp:**
- Chạy lại notebook 1 hoặc 2 sẽ **xóa** 2 cột giá thuê trong file processed → phải chạy lại notebook 3, rồi dựng lại trang.
- Notebook được **sinh từ** `cong_cu/dung_notebook_*.py`. Sửa trực tiếp trong notebook rồi sinh lại thì mất phần đã sửa. Quy ước: sửa script trong `cong_cu/`, sinh lại (`python cong_cu/dung_notebook_chinh.py notebooks/2324801030095.ipynb`), rồi chạy (`jupyter nbconvert --to notebook --execute --inplace ...`).
- Notebook 7 cần **Node.js**; không có Node thì bỏ qua phần so sánh với luật và dùng chiến lược "chỉ mô hình".

---

## 3. Dữ liệu

### 3.1 Nguồn và cách thu thập

| Nguồn | Script | Phạm vi | Ghi chú |
|---|---|---|---|
| Chợ Tốt Nhà | `chotot_thu_thap.py` (`--can-ho`, `--dat`) | Bình Dương cũ (`region_v2=2011`); nhà ở `cg=1020`, căn hộ `1010`, đất `1040` | API công khai `gateway.chotot.com`; lưu cả JSON gốc (`.jsonl`) và bảng phẳng (`.csv`); nghỉ 1 giây/trang |
| alonhadat | `alonhadat_thu_thap.py` (`--can-ho`, `--dat`) | TP Thủ Dầu Một | Đọc HTML; hay bị chặn HTTP 429 → tự chờ 30·2^k giây; tải không trọn vẹn thì **không ghi đè** file cũ |
| guland | `guland_thu_thap.js` | Phường Phú Hòa | Chạy trong trình duyệt (trang chặn truy cập tự động); lần thu thập 12/11/2026 |

Mã nhãn của Chợ Tốt (loại nhà, pháp lý, nội thất…) được **học từ chính dữ liệu**, không đoán tay. Tin cho thuê và tin bán được tách theo trường `type`.

### 3.2 Quy mô sau làm sạch (17/11/2026)

| Bộ dữ liệu | Số dòng | Theo nguồn | Tin bị loại |
|---|---|---|---|
| Nhà phố (`nha_da_xu_ly.csv`) | 1.489 (TDM 608, Phú Hòa 220) | Chợ Tốt 1.196 · alonhadat 147 · guland 146 | 110 (`tin_bi_loai.csv`) |
| Căn hộ (`can_ho_da_xu_ly.csv`) | 613 (84 dự án, TDM 138) | Chợ Tốt 610 · alonhadat 3 | 65 |
| Đất ở (`dat_da_xu_ly.csv`) | 930 (TDM 387) | Chợ Tốt 755 · alonhadat 175 | 287 |
| Cho thuê (`thue_da_xu_ly.csv`) | 717 | căn hộ 484 · nhà 233 | – |

### 3.3 Riêng tư

- `cong_cu/an_danh_du_lieu.py`: xóa các trường người đăng (tên, mã tài khoản, ảnh đại diện, `seller_info`…) khỏi JSONL; che số điện thoại trong tiêu đề/mô tả của mọi CSV/JSONL bằng `[SĐT]`. Hai script thu thập tự làm việc này cho dữ liệu mới.
- JSONL ghi ký tự U+2028/U+2029 ở dạng thoát, để mỗi dòng luôn là đúng một bản ghi với mọi cách tách dòng.
- Lịch sử git đã được viết lại (17/11/2026) để bỏ dữ liệu chưa ẩn danh. Hai commit cũ `990e482`, `e1983ce` vẫn truy cập được trên GitHub nếu biết mã SHA cho tới khi GitHub dọn; muốn xóa ngay cần gửi yêu cầu cho GitHub Support.
- Kiểm thử `kiem_tra_mo_hinh.py` có phép kiểm tự động: không còn trường người đăng và số điện thoại trong `data/`.

### 3.4 Thu thập định kỳ

- `thu_thap/bat_lich_tu_dong.bat` đăng ký tác vụ `PhuHoaHome_ThuThapDinhKy` (08:00 Chủ nhật, chạy bù nếu máy tắt lúc đó); `tat_lich_tu_dong.bat` gỡ.
- `cap_nhat_dinh_ky.py` thu 6 nguồn, mỗi nguồn lỗi thì bỏ qua và ghi vào nhật ký `data/lich_su/nhat_ky_thu_thap.txt`; **cảnh báo** nếu số tin của một nguồn giảm > 30% so với kỳ trước; cuối lần chạy in bảng số tin theo kỳ và nguồn.
- **Sự cố cần xử lý:** lần chạy 22/11/2026 13:22 kết thúc với mã `0xC000013A` (tiến trình bị đóng, thường do tắt máy/đăng xuất) khi đang tải trang thứ 3 của Chợ Tốt. Dữ liệu **không bị ảnh hưởng** (script chỉ ghi khi tải xong), nhưng kỳ này không có ảnh chụp. Tác vụ hiện chỉ chạy khi người dùng đang đăng nhập; nên đổi sang "Run whether user is logged on or not" trong Task Scheduler (cần mật khẩu Windows) hoặc chạy tay `thu_thap/chay_dinh_ky.bat`.

### 3.5 Chất lượng dữ liệu đã đo (notebook nhà phố)

- Tỷ lệ thiếu: diện tích sàn 58%, độ rộng hẻm 59%, số WC 33%, số tầng 17%, ngang 15%. Ô thiếu được điền từ mô tả tin (biểu thức chính quy) trước khi mô hình xử lý; phần còn thiếu để LightGBM tự xử lý, Ridge điền trung vị.
- Mức chính xác tọa độ nhà phố: tọa độ riêng 355 · theo tuyến đường 389 · **tâm phường 739** · tâm quận 6. Đất: tâm phường 534/930.
- Tỷ lệ tin bị lọc theo nguồn: guland 2,7%, Chợ Tốt 6,9%, alonhadat 10,4% (không thiên lệch theo website).

---

## 4. Logic chi tiết từng notebook

### 4.1 Nhà phố – `notebooks/2324801030095.ipynb` (sinh từ `cong_cu/dung_notebook_chinh.py`)

Notebook chia **Phần A – cơ bản** (theo bài giảng: định nghĩa bài toán T/P/E, tiền xử lý, cây quyết định) và **Phần B – nâng cao**.

**Phần A**
1. **Thu thập** (Bước 1): đọc 3 nguồn; guland chỉ giữ loại "Nhà phố"; Chợ Tốt chỉ giữ tin bán.
2. **Hợp nhất** (Bước 2): đưa về một lược đồ (giá tỷ đồng, diện tích m², tên phường/đường viết thường không dấu để so khớp). Tọa độ ngoài Bình Dương cũ coi như không có.
3. **Đặc trưng văn bản** (Bước 3, `trich_dac_trung_chu`): 21 cờ từ khóa (hẻm xe hơi, khu dân cư, sổ riêng, bán gấp…) và các số đọc từ mô tả (độ rộng hẻm, ngang, "5x20", "1 trệt 2 lầu", phòng, WC, diện tích sàn, diện tích thổ cư). Ô thông số trống được điền bằng số đọc từ mô tả; giá trị vô lý (30 tầng…) coi là thiếu. Cấp lối vào 0–5 thống nhất mọi nguồn.
4. **Làm sạch** (Bước 4):
   - Sửa diện tích nhập nhầm: diện tích bằng đúng chiều dài/ngang và nhỏ hơn hẳn ngang × dài → thay bằng ngang × dài.
   - Giữ giá 0,5–60 tỷ, đất 25–1.000 m², đơn giá 5–250 triệu/m².
   - Tin trùng khớp hẳn (cùng quận, giá làm tròn 10 triệu, diện tích làm tròn 1 m²) gộp thành 1 dòng, ô trống lấy từ bản trùng khác.
   - Gán tọa độ theo thứ tự ưu tiên: tọa độ riêng của tin → trung vị tuyến đường → tâm phường → tâm quận (chỉ dùng vị trí, không dùng giá nên không rò rỉ nhãn).
   - Loại tin không phải giá nhà thị trường, có ghi lý do: nhà lắp ghép/thi công, nhà ở xã hội, căn hộ đăng nhầm mục nhà, giá mồi ("2 tỷ xxx", khoảng giá), thổ cư < 50% diện tích, đơn giá lệch > 3 lần trung vị 15 căn gần nhất.
   - **Gom tin gần trùng** (`nhom_gan_trung`): cùng quận, diện tích lệch ≤ 3%, giá lệch ≤ 12% **và** một bằng chứng (mô tả giống nhau theo TF-IDF ≥ 0,45, hoặc cùng phường + cùng kích thước, hoặc cùng phường + cùng đường). Cố ý gom rộng: gom thừa chỉ làm đánh giá khắt khe hơn. Kết quả: 1.245 nhóm cho 1.489 căn.
5. **Khám phá** (Bước 5): đơn giá theo phường, bản đồ, giá theo diện tích (log–log → học trên log giá).
6. **Chia train/test** (Bước 6): test = 20% số **nhóm** ở Thủ Dầu Một (`GroupShuffleSplit`), không dùng cho bất kỳ quyết định nào.
7. **Mô hình cơ bản** (Bước 7): baseline đơn giá phường, hồi quy tuyến tính, cây quyết định (độ sâu chọn bằng kiểm định chéo theo nhóm trên train, có đường cong quá khớp và luật if-then). Trên test Phú Hòa: baseline 35,3%, tuyến tính 28,8%, cây đơn 35,4% → cây đơn phương sai cao, là lý do Phần B dùng nhiều cây.

**Phần B**
8. **Đặc trưng giá khu vực** (`GiaLangGieng`): log đơn giá của 12 căn gần nhất (trung bình theo nghịch đảo khoảng cách và trung vị), khoảng cách trung bình tới chúng, mã hóa trung bình có co (shrinkage) theo phường và theo tuyến đường. **Tính trên tập học và theo kiểu bỏ-một (leave-one-out)**: mỗi căn không bao giờ thấy giá của chính nó.
9. **So sánh mô hình** (Bước 8): baseline, Ridge, LightGBM, Random Forest, CatBoost, LightGBM Huber + chữ, Ensemble + chữ. "+ chữ" = xếp chồng (stacking) với mô hình TF-IDF n-gram ký tự + Ridge đọc tiêu đề/mô tả; dự đoán ngoài-fold của mô hình chữ **chia theo nhóm** để không rò rỉ. Đánh giá bằng kiểm định chéo 5-fold lặp 3 lần chia theo nhóm, mỗi chỉ số có KTC bootstrap theo nhóm.
10. **Quy tắc chọn mô hình:** tìm mô hình có MAPE trung bình (Phú Hòa + TDM) thấp nhất; so từng mô hình với nó **trên cùng từng căn** (bootstrap theo nhóm, trên TDM); trong các mô hình mà KTC của chênh lệch chứa 0, chọn **đơn giản nhất**. Lần chạy hiện tại: tốt nhất là Ensemble + chữ; Ridge kém có ý nghĩa (+2,67 điểm, KTC 1,47–4,08) → chọn **LightGBM** (chênh +0,61, KTC −0,33…1,61).
11. **Tinh chỉnh siêu tham số:** 12 cấu hình ngẫu nhiên của LightGBM; cấu hình đang dùng không kém có ý nghĩa.
12. **Kiểm chứng:** chia ngẫu nhiên so với chia theo nhóm (đo mức rò rỉ), học toàn vùng so với chỉ Phú Hòa, so với cách làm phiên bản 1.
13. **Tập test** (Bước 9): bảng kết quả, ví dụ căn thật ở 5 mức lệch (giải thích MAPE), độ lệch có dấu theo loại lối vào và mức giá, permutation importance theo nhóm đặc trưng.
14. **Khoảng giá 80%** (Bước 10): phân vị 10% và 90% của sai số ngoài-fold (log) trên các căn TDM, **tính riêng cho 4 mức giá dự đoán** (ý tưởng Mondrian conformal). Đây là khoảng hiệu chỉnh thực nghiệm, **không** phải bảo đảm lý thuyết; độ phủ được kiểm tra trên test bằng kiểm định nhị thức.
15. **Chẩn đoán từng căn Phú Hòa** (Bước 11): giá ước lượng = dự đoán chéo theo nhóm trên toàn bộ dữ liệu (căn đó và tin gần trùng không nằm trong tập học), trung bình 3 lần lặp; rẻ/cao hơn thị trường = giá rao nằm ngoài khoảng 80%.
16. **Kiểm tra độ tin cậy** (cuối Bước 11): sai số theo nguồn, mức chính xác tọa độ, mức đủ thông số, mức giá, phường (< 20 căn ghi "chưa đủ mẫu"); độ nhạy theo 4 ngưỡng lọc đơn giá (chấm trên cùng 1.355 căn: 21,7–22,4%); xuất 50 cặp tin cho gán nhãn tay.
17. **Lưu mô hình** (Bước 12): `mo_hinh_gia_nha.joblib` (mô hình đầy đủ + khoảng theo mức giá); `mo_hinh_gia_nha.json` = **mô hình rút gọn cho web**: Ridge 11 thông số người dùng nhập được, học trên Phú Hòa, chặn trên ở phân vị 97% để không ngoại suy (MAPE kiểm định chéo theo nhóm 25,2%). Giải thích SHAP (`pred_contrib` của LightGBM, gom theo nhóm yếu tố) cho từng căn Phú Hòa → `giai_thich_nha.json`.

### 4.2 Căn hộ – `du_doan_gia_can_ho.ipynb`

- Định giá theo **m² sử dụng** và theo **dự án** (tên dự án chuẩn hóa bằng `ten_du_an`; tin không ghi dự án thì dò tên dự án trong mô tả).
- Loại tin "giá chỉ từ", "bảng giá"/bán nhiều căn; **giữ** nhà ở xã hội nhưng gắn cờ.
- Gom tin trùng **chỉ theo mô tả** (`dung_vi_tri=False`): cùng dự án có nhiều căn cùng mẫu là căn khác nhau thật.
- Giá khu vực phân tầng (`tang_bac=True`): đơn giá dự án co về đơn giá phường của **cùng phân khúc** (nhà ở xã hội tách riêng), thêm số tin của dự án làm đặc trưng.
- Chọn: LightGBM Huber + chữ. Khoảng 80% tính riêng cho nhà ở xã hội và thương mại.
- Phân tích pháp lý: tổng thể căn HĐMB có đơn giá cao hơn căn sổ hồng (khác dự án, khác thời điểm); trong cùng dự án, chênh khoảng −2,5%.
- Web: `CanHoWeb` = đơn giá dự án (co về phường) + Ridge 7 thông số (MAPE 13,8%).

### 4.3 Đất nền – `du_doan_gia_dat.ipynb`

- Chỉ **đất ở** (thổ cư, nền dự án); đất nông nghiệp/công nghiệp quá ít và là thị trường khác nên loại.
- Giữ giá 0,2–100 tỷ, diện tích 40–3.000 m², đơn giá 1–200 triệu/m². Loại: bán nhiều lô/"giá từ", thổ cư < 50%, có nhà trên đất, đơn giá lệch > 3 lần khu vực.
- Tọa độ tin alonhadat lấy theo tuyến đường của dữ liệu nhà phố và đất có tọa độ riêng.
- Chọn: **Ridge** (đơn giản nhất không kém LightGBM có ý nghĩa). Test TDM 30,2%, độ phủ khoảng 80% trên test 79,2%.
- Chẩn đoán dùng cùng quy tắc khoảng 80% như nhà phố; **lô > 1.000 m² không chẩn đoán** (quá ít mẫu, mô hình ngoại suy sai).
- Web: `DatWeb` = đơn giá phường (co về quận) + Ridge 7 thông số (MAPE TDM 28,6%).

### 4.4 Giá thuê và tỷ suất – `du_doan_gia_thue.ipynb`

- Dữ liệu: tin **cho thuê** của Chợ Tốt (trước đây bị bỏ). Loại thuê phòng/ở ghép/ngắn hạn/sang nhượng, giá ngoài 1,5–150 (nhà) hoặc 1,5–60 (căn hộ) triệu/tháng, giá thuê/m² vô lý.
- **Không dùng mô tả tin** làm đặc trưng, vì mô hình áp dụng cho tin **bán** (lời văn khác hẳn tin thuê).
- Chọn Ridge cho cả căn hộ và nhà. Áp mô hình cho từng căn đang bán: tỷ suất gộp = 12 × giá thuê / giá bán; hoàn vốn = giá bán / (12 × giá thuê).
- **Kiểm chứng chéo:** ở 14 dự án có ≥ 5 tin bán và ≥ 5 tin thuê, tỷ suất của mô hình tương quan 0,94 với tỷ suất tính thẳng từ dữ liệu.
- Tỷ suất trung vị: căn hộ 3,6%/năm, nhà phố TDM 2,9%/năm. Tỷ suất là **gộp** (chưa trừ chi phí, thời gian trống).

### 4.5 Xu hướng giá – `du_doan_xu_huong_gia.ipynb`

- Không có lịch sử giá nhiều năm → **không huấn luyện mô hình chuỗi thời gian**; dùng tín hiệu đo được:
  - Đổi giá trên **cùng một tin** (`gia_goc_luc_dang` so với `gia`): ở TDM 83% số lần đổi giá là giảm, trung vị −5,1%.
  - Độ dốc giá rao theo tuần đăng (có thiên lệch tin tồn); tỷ lệ tin "bán gấp"; số liệu DKRA đã công bố (có link nguồn).
  - Giá một "căn chuẩn" ở trung tâm mỗi phường (mô hình nhà phố định giá cùng một căn ở các vị trí).
- **Kịch bản theo kỳ hạn:** biên 6 tháng = [mức giảm trung vị người bán đang áp dụng; mức tăng quý gần nhất theo DKRA] = −5,1% … +2,0%. Kỳ hạn h tháng = (biên 6 tháng / 6) × h. Bảng 1/3/6/12/18/24 tháng, mỗi kỳ hạn có nhãn độ tin cậy; trên 12 tháng là "chỉ minh họa". Đây là **kịch bản có điều kiện, chưa kiểm định lùi**.
- **Chỉ số theo ảnh chụp:** thay đổi giá của các tin có mặt ở 2 kỳ liên tiếp → chỉ số lặp lại. Khi đủ **8 kỳ**, `kiem_dinh_lui` (Holt so với baseline "giữ nguyên", có kiểm thử chống nhìn trước tương lai, báo lỗi nếu chuỗi có kỳ rỗng) tự chạy. Hiện có 3 kỳ; dự kiến đủ khoảng 20/12/2026 nếu lịch chạy đều.

### 4.6 Trợ lý – `tro_ly_y_dinh.ipynb`

- 410 câu huấn luyện / 158 câu kiểm tra viết riêng (không trùng sau chuẩn hóa, có phép kiểm), 19 ý định gồm "ngoài phạm vi". Câu do người làm đề tài **viết tay**.
- Chuẩn hóa: bỏ dấu, số → "0", bỏ ký tự đặc biệt (trang web dùng đúng quy tắc này).
- Đặc trưng TF-IDF n-gram ký tự (2–4) + từ (1–2); so sánh Naive Bayes / Logistic Regression / SVM bằng kiểm định chéo → triển khai Logistic Regression (cần xác suất).
- Chiến lược kết hợp với luật cũ được chọn trên dự đoán ngoài-fold của tập huấn luyện (loại 40 câu luật đã được viết theo): **luật trước, không nhận ra thì dùng mô hình**. Trên web, mô hình chắc < 40% thì **hỏi lại** bằng gợi ý; câu ngoài phạm vi thì từ chối.
- Lưu ý trung thực: trên tập kiểm tra, mô hình đơn lẻ (98,7%) tốt hơn chiến lược kết hợp đã chọn (93,7%) vì luật bắt nhầm từ khóa. Không đổi chiến lược theo tập kiểm tra (sẽ thành dùng test để chọn). Cần một tập kiểm định riêng để chọn lại.
- Trợ lý **chỉ phân loại ý định** rồi trả lời bằng các hàm có sẵn, lấy số từ dữ liệu và mô hình; không sinh văn bản tự do.

---

## 5. Mã dùng chung – `src/mo_hinh_gia.py`

| Hàm / lớp | Việc làm | Bất biến cần giữ |
|---|---|---|
| `khong_dau`, `ten_phuong`, `ten_quan`, `ten_duong`, `ten_du_an` | Chuẩn hóa tên để so khớp giữa các nguồn | – |
| `trich_dac_trung_chu(van_ban)` | 21 cờ từ khóa + các số đọc từ mô tả | Biểu thức chính quy có ranh giới từ (tránh "nhà gồm" khớp "nhà gỗ") |
| `GiaLangGieng(k=12, tang_bac=False)` | Đặc trưng giá khu vực | `fit_transform` trên train = **leave-one-out**; `transform` dùng toàn bộ train |
| `MoHinhGia(est, features, khong_gian, chuan_hoa, muc_tieu)` | Ghép đặc trưng căn nhà + giá khu vực rồi học; `muc_tieu="don_gia"` học log đơn giá | Đầu ra luôn là **log giá** |
| `XepChongChu(base)` | Stacking với mô hình chữ TF-IDF + Ridge | Ngoài-fold **theo nhóm** (`chu_ngoai_fold`) |
| `TrungBinhMoHinh`, `BaselineDonGiaPhuong`, `BaselineDonGiaDuAn` | Ensemble trung bình; baseline | – |
| `nhom_gan_trung(df, dung_vi_tri=True)` | Gom tin gần trùng (union-find) | Gom thừa hơn bỏ sót |
| `du_doan_cheo_lap(tao, d, so_lan, theo_nhom)` | Kiểm định chéo 5-fold lặp, trả ma trận (số lần × số căn) | `GroupKFold` theo cột `nhom` |
| `sai_so_tung_can`, `ktc_bootstrap`, `bang_danh_gia`, `chi_so_danh_gia` | Chỉ số và KTC bootstrap theo nhóm | Bootstrap lấy mẫu theo **nhóm**, không theo dòng |
| `hieu_chinh_khoang`, `phan_vi_cho`, `muc_gia` | Khoảng 80% theo nhóm (Mondrian) | Nhóm < `toi_thieu` mẫu dùng phân vị chung |
| `holt`, `kiem_dinh_lui` | Dự báo Holt và kiểm định lùi | Kỳ t chỉ dùng dữ liệu tới t; NaN → báo lỗi |

Các mô hình đã lưu (`.joblib`) phụ thuộc vào các lớp trong file này: đổi tên lớp/thuộc tính sẽ làm hỏng việc nạp lại mô hình cũ (đã có xử lý `getattr` cho `tang_bac`).

---

## 6. Trang web demo – `demo/trang_ban_nha.html`

- **Dựng:** `build_site.py` đọc `model/*.json`, `model/tro_ly_y_dinh.joblib`, `data/processed/*.csv` (và vài cột hiển thị có dấu từ `data/raw`) rồi thay vào `demo/_build/template.html` → **một file HTML** nhúng sẵn dữ liệu (~1,6 MB). Không cần máy chủ.
- **Trang (định tuyến bằng `#`):** `#/` trang chủ + danh sách nhà Phú Hòa · `#/dinh-gia` (và `#/dinh-gia/<mã tin>`) định giá nhà · `#/can-ho` · `#/dat` · `#/ban-do` · `#/tro-ly` · `#/so-sanh` yêu thích & so sánh · `#/nguon-anh`.
- **Định giá trên trình duyệt** dùng các mô hình rút gọn (Ridge/bảng đơn giá) trong `model/*.json`. Khi định giá một tin có sẵn, trang **neo** vào giá của mô hình đầy đủ trong notebook và chỉ dùng mô hình rút gọn để tính tỷ lệ thay đổi khi người dùng sửa thông số.
- **Chi tiết tin:** giá ước tính + khoảng 80%, giá thuê và tỷ suất, "vì sao căn này có giá như vậy" (SHAP), nút lưu.
- **Bản đồ:** Leaflet 1.9.4 (cdnjs) + nền **Esri World Street Map** (OpenStreetMap chặn khi mở bằng `file://`, CARTO đòi khóa API). Chỉ vẽ tin có tọa độ riêng/theo tuyến đường. Căn hộ: **mỗi vị trí 1 chấm**, gộp các dự án trùng tọa độ, bấm để xem danh sách căn. Không có mạng thì vẽ sơ đồ điểm thay thế.
- **Xu hướng:** thẻ ở trang định giá hiện 1/3/6/12 tháng và ô chọn kỳ hạn 1–12, 18, 24 tháng (cùng công thức notebook).
- **Yêu thích/so sánh:** lưu trong `localStorage` của trình duyệt (có `try/catch`, không có cũng chạy).
- **Phụ thuộc bên ngoài:** chỉ Leaflet và nền bản đồ (cần Internet). Câu hỏi trợ lý không gửi đi đâu.

---

## 7. Kiểm thử

**`python tests/kiem_tra_mo_hinh.py`** (10 phép):
1. Giá khu vực không dùng giá của chính căn đó (leave-one-out).
2. Kiểm định chéo theo nhóm: không nhóm nào ở cả hai phía.
3. Gom tin gần trùng: tin đăng lại được gom; căn khác cùng dự án thì không.
4. Chỉ số đánh giá đúng trên ví dụ biết trước.
5. Khoảng theo nhóm phủ ~80% ở cả nhóm dễ và khó.
6. Dữ liệu sạch: không có tin thuê/giá vô lý; test không chung nhóm với train.
7. Mô hình đã lưu nạp lại được, dự đoán hợp lý.
8. Khoảng 80% nhà phố: mức giá đắt có biên rộng hơn mức rẻ.
9. Kiểm định lùi: không nhìn trước tương lai; Holt không thắng trên chuỗi ngẫu nhiên; NaN báo lỗi.
10. Dữ liệu gốc đọc lại được và đã ẩn danh.

**`node tests/kiem_tra_tro_ly.js`** (27 phép): nạp JavaScript của trang với DOM giả lập (`tests/nap_trang_demo.js`) rồi kiểm tra hiểu ý định (≥ 95% trên 56 câu), trích thông tin (diện tích, giá, số tầng, lối vào, dự án), số liệu trợ lý **khớp đúng** mô hình (nhà, căn hộ, đất, thuê), ngữ cảnh hỏi tiếp, bản đồ (điểm trong vùng, mỗi dự án đúng 1 chấm), SHAP hiển thị, xác suất trợ lý **khớp Python**, tập kiểm tra ≥ 90% và hơn luật cũ, hỏi lại khi mơ hồ, xu hướng theo kỳ hạn.

`tests/y_dinh_luat.js`: không phải kiểm thử; notebook trợ lý gọi để lấy dự đoán của luật cũ.

---

## 8. Hạn chế đã biết và rủi ro (xếp theo mức ảnh hưởng)

| # | Hạn chế | Ảnh hưởng | Hướng xử lý |
|---|---|---|---|
| 1 | Giá rao ≠ giá giao dịch | Kết quả là mặt bằng giá rao, không phải giá mua bán | Cần nguồn giao dịch thật (không công khai) |
| 2 | Chỉ 3 kỳ ảnh chụp trong 1 tuần; ngày đăng tin chỉ 16/8–17/11 | Xu hướng chưa kiểm định; kỳ hạn dài chỉ minh họa | Giữ lịch thu thập; kiểm định lùi tự chạy khi đủ 8 kỳ; lấy một giai đoạn mới làm test tương lai |
| 3 | 50% nhà phố, 57% đất chỉ có tọa độ tâm phường | Đặc trưng giá khu vực kém chính xác (tâm phường 24,1% so với tọa độ riêng 21,7%) | Lấy tọa độ chính xác hơn (số nhà, ghim của người đăng) |
| 4 | Tập test Phú Hòa 40 căn | KTC test rộng (20,8–35,7%) | Thêm tin Phú Hòa qua các kỳ; trình bày kèm KTC |
| 5 | Tin thiếu thông số sai 29,4% so với 21,4% | Định giá kém khi người dùng nhập thiếu | Trang đã cảnh báo "thiếu vài thông số" |
| 6 | Căn hộ gần như chỉ từ Chợ Tốt; alonhadat hay chặn (429) | Không kiểm tra được thiên lệch theo nguồn cho căn hộ | Thêm nguồn căn hộ |
| 7 | Gom tin trùng chưa kiểm tay | Chưa biết tỷ lệ gom đúng/bỏ sót | Gán nhãn 50 cặp trong `data/kiem_tra_tay/` rồi chạy lại notebook 1 |
| 8 | Trợ lý: câu tự soạn; chiến lược kết hợp kém mô hình đơn lẻ trên test | Một số câu bị luật hiểu nhầm | Thu thập câu hỏi thật; thêm tập kiểm định riêng để chọn lại chiến lược |
| 9 | Lịch thu thập phụ thuộc máy bật và đăng nhập (lần 22/11 bị ngắt) | Mất kỳ dữ liệu | Đổi cấu hình tác vụ (mục 3.4) |
| 10 | Pipeline chạy tay theo thứ tự ở mục 2.2; chưa có CI | Dễ chạy sai thứ tự (ví dụ mất cột giá thuê) | Viết script chạy toàn bộ + GitHub Actions chạy kiểm thử |
| 11 | Giảng viên có thể không cho dùng file JSON (chưa xác nhận) | Phải chuyển `model/*.json` sang cách khác | Hỏi lại giảng viên; nếu cần, `build_site.py` đọc thẳng `.joblib`/CSV |

---

## 9. Checklist cho người nhận kiểm tra

Chạy từ thư mục gốc đề tài.

| # | Việc | Lệnh | Kết quả mong đợi |
|---|---|---|---|
| 1 | Cài môi trường | `pip install -r requirements.txt` (Python 3.14), Node ≥ 18 | Không lỗi |
| 2 | Kiểm thử mô hình | `python tests/kiem_tra_mo_hinh.py` | `10/10 phép kiểm đạt` |
| 3 | Kiểm thử trang + trợ lý | `node tests/kiem_tra_tro_ly.js` | `27/27 phép kiểm đạt` |
| 4 | Mở demo | mở `demo/trang_ban_nha.html` bằng trình duyệt | Trang chủ có 220 căn Phú Hòa; mục Bản đồ có điểm ở cả 4 loại |
| 5 | Chạy lại một notebook | `jupyter nbconvert --to notebook --execute --inplace notebooks/du_doan_gia_dat.ipynb` | Không lỗi; MAPE test TDM ≈ 30,2% |
| 6 | Kiểm tra số liệu bàn giao | so mục 1 với `model/danh_gia_mo_hinh*.json` | Khớp |
| 7 | Kiểm tra quy tắc chọn mô hình | notebook nhà phố, Bước 8, bảng so sánh cặp | Ridge "Ngang mô hình tốt nhất" = False; LightGBM = True |
| 8 | Kiểm tra mức rò rỉ do tin đăng lại | notebook nhà phố, Bước 8, bảng kiểm chứng | Chia ngẫu nhiên 23,0% so với chia theo nhóm 23,2%: mức "đẹp giả" đo được rất nhỏ; số báo cáo dùng cách chia theo nhóm |
| 9 | Kiểm tra lịch thu thập | Task Scheduler → `PhuHoaHome_ThuThapDinhKy` | Có lịch 08:00 Chủ nhật; xem nhật ký `data/lich_su/nhat_ky_thu_thap.txt` |

Chạy lại **toàn bộ** theo thứ tự mục 2.2 mất khoảng 30 phút (notebook nhà phố ~15 phút).

---

## 10. Việc tồn đọng (ưu tiên)

1. Gán nhãn tay 50 cặp tin (`data/kiem_tra_tay/cap_tin_gan_trung.csv`, cột `cung_mot_can`: 1/0), chạy lại notebook nhà phố.
2. Đổi cấu hình tác vụ thu thập để chạy cả khi không đăng nhập; kiểm tra lần chạy 29/11.
3. Viết script chạy toàn bộ pipeline đúng thứ tự + CI chạy 2 bộ kiểm thử.
4. Khi đủ 8 kỳ ảnh chụp (~20/12/2026): chạy lại notebook xu hướng để có kiểm định lùi thật.
5. Trợ lý: thêm tập kiểm định riêng (câu hỏi của người dùng thật) để chọn lại chiến lược kết hợp.
6. Xác nhận với giảng viên về việc dùng file JSON.
7. Gửi yêu cầu GitHub Support xóa 2 commit cũ chứa dữ liệu chưa ẩn danh (`990e482`, `e1983ce`).
