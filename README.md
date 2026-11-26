# Dự đoán giá nhà Phú Hòa – Thủ Dầu Một

Đề tài môn Học máy · MSSV 2324801030095 · Nguyễn Quang Long · Lớp D23KTPM01

Học máy có giám sát ước lượng **mặt bằng giá rao** của nhà phố, căn hộ, đất nền và giá thuê ở Thủ Dầu Một (trọng tâm phường
Phú Hòa), kèm khoảng giá 80%, chẩn đoán giá rao rẻ / hợp lý / cao, phân tích xu hướng và trang web demo có trợ lý hỏi đáp (có chế độ AI dùng Groq – miễn phí, Claude hoặc Gemini).
Dữ liệu là tin rao thật (Chợ Tốt Nhà, alonhadat, guland), đã ẩn danh. **Giá rao không phải giá giao dịch.**

**Tài liệu kỹ thuật tổng hợp (Word): [docs/Tai_lieu_ky_thuat_tong_hop.docx](docs/Tai_lieu_ky_thuat_tong_hop.docx)** – cấu trúc, cài đặt, công nghệ, thuật toán, logic dữ liệu, đầu vào/đầu ra, huấn luyện và kết quả, web demo, trợ lý, kiểm thử, hạn chế, checklist, câu hỏi bảo vệ.

## Bắt đầu nhanh

```
pip install -r requirements.txt          # Python 3.14; kiểm thử trang web cần thêm Node.js >= 18
python tests/kiem_tra_mo_hinh.py         # 12 phép kiểm, phải đạt hết
node tests/kiem_tra_tro_ly.js            # 46 phép kiểm, phải đạt hết
```
Xem demo: mở `demo/trang_ban_nha.html` bằng trình duyệt (bản đồ cần Internet).

## Cấu trúc

```
notebooks/      6 notebook đã chạy: 2324801030095 (nhà phố, bài chính), du_doan_gia_can_ho, du_doan_gia_dat,
                du_doan_gia_thue, du_doan_xu_huong_gia, tro_ly_y_dinh
cong_cu/        script SINH các notebook (sửa ở đây rồi sinh lại) + an_danh_du_lieu.py
src/            mo_hinh_gia.py – mã dùng chung (đặc trưng, mô hình, đánh giá, khoảng giá, kiểm định lùi)
thu_thap/       script tải tin, chạy định kỳ, đăng ký / gỡ lịch Task Scheduler
data/           raw (gốc) · processed (đã làm sạch) · lich_su (ảnh chụp theo ngày) · tro_ly · kiem_tra_tay
model/          mô hình (.joblib), mô hình rút gọn và số liệu cho web (.json), kết quả đánh giá
ket_qua/        bảng định giá, chẩn đoán, tỷ suất cho thuê
demo/           trang_ban_nha.html + _build/ (mẫu trang, build_site.py)
tests/          kiểm thử mô hình (Python) và trang web / trợ lý (Node)
docs/           Tai_lieu_ky_thuat_tong_hop.docx
```

## Chạy lại toàn bộ (đúng thứ tự, ~6 phút)

Một lệnh: `python cong_cu/chay_toan_bo.py` (thêm `--thu-thap` để tải dữ liệu mới trước, `--tu <bước>` để chạy tiếp từ bước lỗi). Các lệnh nó chạy, theo thứ tự:

```
python thu_thap/cap_nhat_dinh_ky.py                                                  # tùy chọn: dữ liệu mới
jupyter nbconvert --to notebook --execute --inplace notebooks/2324801030095.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/du_doan_gia_can_ho.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/du_doan_gia_thue.ipynb     # sau nhà phố + căn hộ
jupyter nbconvert --to notebook --execute --inplace notebooks/du_doan_gia_dat.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/du_doan_xu_huong_gia.ipynb
python demo/_build/build_site.py
jupyter nbconvert --to notebook --execute --inplace notebooks/tro_ly_y_dinh.ipynb        # cần Node.js
python demo/_build/build_site.py
python tests/kiem_tra_mo_hinh.py && node tests/kiem_tra_tro_ly.js
```
Lý do của thứ tự và các bẫy thường gặp: tài liệu kỹ thuật tổng hợp, mục 8.4.
GitHub Actions (`.github/workflows/kiem_thu.yml`) chạy 2 bộ kiểm thử mỗi lần đẩy code.

**Trợ lý – chế độ AI:** trên trang `#/tro-ly`, bấm **Chế độ AI**, dán khóa **Groq** (gsk_…, **miễn phí**, tạo ở console.groq.com/keys), **Claude** (sk-ant-…, platform.claude.com) hoặc **Gemini** (aistudio.google.com) – trang tự nhận loại khóa. Groq mặc định openai/gpt-oss-120b (gói miễn phí ~8.000 token/phút mỗi mô hình; hết hạn mức thì trang tự chuyển sang gpt-oss-20b hoặc chờ rồi gửi lại); Claude mặc định Opus 5.5; Gemini tự chọn Flash ổn định mới nhất. Mô hình ngôn ngữ hiểu câu hỏi tự nhiên, nhớ hội thoại và gọi các hàm định giá, tìm nhà, giá thuê, xu hướng của trang như công cụ, nên con số vẫn là của mô hình đề tài. Chỉ cần nhập khóa **một lần**: khóa được ghi nhớ trên trình duyệt đó (mặc định), lần sau mở trang chế độ AI tự bật; nút "Tắt và xóa khóa" để gỡ. Khóa không nằm trong file trang; khi bật, câu hỏi được gửi tới nhà cung cấp của khóa (Groq, Anthropic hoặc Google). **Khóa mặc định trên máy riêng:** đặt khóa vào `demo/khoa_ai.local.js` (`window.PHH_KHOA_MAC_DINH = "gsk_...";`) thì trang tự bật chế độ AI, không cần nhập; file này nằm trong `.gitignore` nên không lên GitHub – xóa nó trước khi gửi thư mục cho người khác. Không có khóa, mất mạng hay lỗi API thì trợ lý tự quay về chế độ ngoại tuyến (chạy hoàn toàn trên trình duyệt).

**Thu thập định kỳ:** chạy `thu_thap/bat_lich_tu_dong.bat` một lần (tự xin quyền Administrator) để đăng ký tác vụ 07:00 hằng ngày, chạy cả khi không đăng nhập. Mỗi lần chạy: thu tin mới nhất → lưu ảnh chụp có ghi ngày vào `data/lich_su/` → chạy lại toàn bộ notebook, trang web, README và kiểm thử (không tự commit hay đẩy lên GitHub). Chỉ số xu hướng lấy mỗi tuần một kỳ. Khi đủ 8 kỳ tuần, notebook xu hướng tự kiểm định lùi mô hình dự báo. Chợ Tốt và alonhadat thu tự động; **guland** (nguồn chính của tin Phú Hòa) chặn trình duyệt tự động nên phải thu tay: mở trang guland Phú Hòa trong trình duyệt, chạy `thu_thap/guland_thu_thap.js` trong Console, chép file tải về thành `data/raw/nha_phu_hoa_guland_raw.csv`. Tác vụ ghi nhắc vào nhật ký khi dữ liệu guland cũ quá 14 ngày.

## Kết quả chính (dữ liệu đến 26/11/2026)

| | Nhà phố – Phú Hòa | Căn hộ | Đất nền – TDM |
|---|---|---|---|
| Mô hình | Random Forest (300 cây) | LightGBM Huber + chữ | Ridge |
| MAPE tập test (kết quả chính) | 26,4% (KTC 19,5–38,7; 44 căn) | 13,7% | 26,8% (KTC 19,7–36,7; 68 lô) |
| MAPE kiểm định chéo theo nhóm | 23,5% | 12,6% | 26,1% |
| Baseline (đơn giá khu vực), kiểm định chéo | 30,7% | 16,1% | 36,6% |
| Phần A (mô hình môn học tốt nhất), tập test | chính là mô hình cuối | Random Forest (300 cây): 14,0% | Random Forest (300 cây): 21,7% |

**Nhà phố – mô hình cuối:** mô hình tốt nhất trong các mô hình của môn học (Phần A, chọn bằng kiểm định chéo), dùng đúng đặc trưng của Phần A. Phần B chỉ so nó với một mô hình đối chứng ngoài bài giảng (LightGBM + giá khu vực) và đo độ tin cậy (kiểm định chéo lặp, bootstrap, khoảng giá 80%).
