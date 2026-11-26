# Sinh tài liệu bàn giao

Chạy sau `python scripts/chay_toan_bo.py` (và `docker compose up -d` nếu muốn có kết quả kiểm thử web):

```
cd scripts/tai_lieu
npm install
python so_lieu_ban_giao.py ../..                      # gom số liệu của lần chạy vừa xong -> so_lieu_ban_giao.json
node tao_ban_giao.js ../../docs/Tai_lieu_ban_giao.docx so_lieu_ban_giao.json
```
Mở file trong Word, bấm chuột phải vào Mục lục → Update Field để cập nhật số trang.
Mọi con số trong tài liệu đọc từ `so_lieu_ban_giao.json`, không gõ tay.
