# Dự đoán giá nhà Phú Hòa – Thủ Dầu Một

Đề tài môn Học máy · MSSV 2324801030095 · Nguyễn Quang Long · Lớp D23KTPM01

Học máy có giám sát ước lượng **mặt bằng giá rao** của nhà phố, căn hộ, đất nền và giá thuê ở Thủ Dầu Một (trọng tâm phường
Phú Hòa), kèm khoảng giá 80%, chẩn đoán giá rao rẻ / hợp lý / cao, phân tích xu hướng và trang web demo có trợ lý hỏi đáp.
Dữ liệu là tin rao thật (Chợ Tốt Nhà, alonhadat, guland), đã ẩn danh. **Giá rao không phải giá giao dịch.**

**Báo cáo bàn giao chi tiết (Word): [docs/Bao_cao_ban_giao_ky_thuat.docx](docs/Bao_cao_ban_giao_ky_thuat.docx)** – cấu trúc, công nghệ, thuật toán, logic dữ liệu, đầu vào/đầu ra, huấn luyện, web demo, kiểm thử, hạn chế, checklist.

## Bắt đầu nhanh

```
pip install -r requirements.txt          # Python 3.14; kiểm thử trang web cần thêm Node.js >= 18
python tests/kiem_tra_mo_hinh.py         # 10/10 phép kiểm
node tests/kiem_tra_tro_ly.js            # 27/27 phép kiểm
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
docs/           Bao_cao_ban_giao_ky_thuat.docx
```

## Chạy lại toàn bộ (đúng thứ tự, ~30 phút)

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
Lý do của thứ tự và các bẫy thường gặp: báo cáo bàn giao, mục 8.4.

## Kết quả chính (dữ liệu 17/11/2026)

| | Nhà phố – Phú Hòa | Căn hộ | Đất nền – TDM |
|---|---|---|---|
| Mô hình | LightGBM | LightGBM Huber + chữ | Ridge |
| MAPE tập test (kết quả chính) | 27,5% (KTC 20,8–35,7; 40 căn) | 10,6% | 30,2% (KTC 22,3–39,8; 72 lô) |
| MAPE kiểm định chéo theo nhóm | 23,2% | 12,0% | 26,0% |
| Baseline (đơn giá khu vực) | 28,9% | 15,5% | 38,4% |
