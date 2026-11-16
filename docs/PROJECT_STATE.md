# Project State

Cập nhật: 17/11/2026

- **Kho mã:** GitHub `2324801030095-cloud/Project_Du-doan-gia-nha`, **public**, nhánh `main`.
- **Đã xong:**
  - 5 notebook đã chạy trọn vẹn và còn output: nhà phố, căn hộ, đất nền, giá thuê, xu hướng.
  - Trang demo `demo/trang_ban_nha.html` gồm: định giá, căn hộ, đất nền, bản đồ giá, yêu thích/so sánh, trợ lý.
  - Kiểm thử: `tests/kiem_tra_mo_hinh.py` đạt 9/9, `tests/kiem_tra_tro_ly.js` đạt 22/22.
  - Dữ liệu ở bản mới nhất đã ẩn danh: không còn thông tin người đăng, số điện thoại đã được che. Xem `cong_cu/an_danh_du_lieu.py`.
  - Thu thập định kỳ: tác vụ Windows `PhuHoaHome_ThuThapDinhKy` chạy 08:00 Chủ nhật hằng tuần.
- **Hạn chế đã biết (nêu khi trình bày):**
  - Tập test nhà phố riêng Phú Hòa nhỏ (40 căn). MAPE test 27,5%, khoảng tin cậy 95% là 20,8–35,7%. Cần trình bày cùng MAPE kiểm định chéo 23,2% (20,6–26,3).
  - Xu hướng 6–12 tháng mới là kịch bản tham khảo. Khi có từ 8 kỳ ảnh chụp trở lên trong `data/lich_su/`, notebook xu hướng tự kiểm định lùi.
  - Dữ liệu là giá rao, không phải giá giao dịch.
- **Lịch sử git:** các commit cũ trước `dd4d46b` (gồm `990e482`) còn bản dữ liệu thô chưa ẩn danh. Chỉ bản mới nhất được bảo đảm đã ẩn danh. Muốn gỡ hẳn thì phải viết lại lịch sử và force-push, và việc này cần chủ repo đồng ý.
- **Bước tiếp theo:**
  - Chạy lại notebook xu hướng sau mỗi vài kỳ thu thập.
  - Khi có thêm tin Phú Hòa mới, chạy lại notebook nhà phố để thu hẹp khoảng tin cậy của tập test.
