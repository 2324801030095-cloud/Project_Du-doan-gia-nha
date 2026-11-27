# Sinh tài liệu bàn giao

Chạy sau `python scripts/chay_toan_bo.py` (và `docker compose up -d` nếu muốn có kết quả kiểm thử web và kiểm chứng API đang chạy; không có thì hai mục đó ghi SKIPPED kèm lý do):

```
cd scripts/tai_lieu
npm install
python so_lieu_ban_giao.py ../..                      # gom số liệu + chạy lại mọi bộ kiểm thử -> so_lieu_ban_giao.json
node tao_ban_giao.js ../../docs/Tai_lieu_ban_giao_<ngày>.docx so_lieu_ban_giao.json
```
Ghi ra **file mới** (đặt ngày vào tên), không ghi đè tài liệu đã có. Mở file trong Word, bấm chuột phải vào Mục lục → Update Field để cập nhật số trang.
Mọi con số trong tài liệu đọc từ `so_lieu_ban_giao.json`, không gõ tay. Kiểm thử ghi PASS / FAIL / SKIPPED theo mã thoát; `so_lieu_ban_giao.py` thoát khác 0 nếu có FAIL.
