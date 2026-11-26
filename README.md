# Dự đoán giá nhà Phú Hòa – Thủ Dầu Một

Đề tài môn Học máy · MSSV 2324801030095 · Nguyễn Quang Long · Lớp D23KTPM01

Học máy có giám sát ước lượng **mặt bằng giá rao** của nhà phố, căn hộ, đất nền và giá thuê ở Thủ Dầu Một (trọng tâm phường
Phú Hòa), kèm khoảng giá 80%, chẩn đoán giá rao rẻ / hợp lý / cao, phân tích xu hướng, và **ứng dụng web đầy đủ** (đăng nhập, định giá bằng mô hình thật trên máy chủ, lưu tin, lịch sử, quản trị, trợ lý AI).
Dữ liệu là tin rao thật (Chợ Tốt Nhà, alonhadat, guland), đã ẩn danh. **Giá rao không phải giá giao dịch.**

**Tài liệu kỹ thuật tổng hợp (Word): [docs/Tai_lieu_ky_thuat_tong_hop.docx](docs/Tai_lieu_ky_thuat_tong_hop.docx)** – cấu trúc, cài đặt, công nghệ, thuật toán, logic dữ liệu, đầu vào/đầu ra, huấn luyện và kết quả, web demo, trợ lý, kiểm thử, hạn chế, checklist, câu hỏi bảo vệ.

## Bắt đầu nhanh

**Ứng dụng web** (cần Docker Desktop):
```
copy .env.example .env                   # rồi điền mật khẩu CSDL, BETTER_AUTH_SECRET, tài khoản admin, (tùy chọn) GROQ_API_KEY
docker compose up -d --build             # db + api + migrate + web
```
Mở http://localhost:3000 · đăng nhập admin bằng ADMIN_EMAIL / ADMIN_PASSWORD trong `.env` · tài liệu API mô hình: http://localhost:8000/docs

**Mô hình và kiểm thử** (Python 3.14, Node.js >= 18):
```
pip install -r requirements.txt
python tests/kiem_tra_mo_hinh.py         # 12 phép: mã mô hình, dữ liệu, số liệu notebook/README
python tests/kiem_tra_api.py             # 8 phép: API mô hình
node tests/kiem_tra_tro_ly.js            # 46 phép: bản tĩnh + trợ lý
node tests/kiem_tra_web.mjs              # 10 phép đầu-cuối, cần web đang chạy: đăng ký/đăng nhập thật, phân quyền, lịch sử...
```
Bản tĩnh chạy offline (không cần máy chủ): mở `demo/index.html`.

## Ứng dụng web

| Thành phần | Công nghệ | Vai trò |
|---|---|---|
| `web/` | Next.js 16 (App Router, React 19, TypeScript), Tailwind CSS 4, Leaflet, Recharts | Giao diện + backend-for-frontend: trang, route handler, kiểm tra phiên ở máy chủ |
| Đăng nhập | Better Auth (email + mật khẩu băm scrypt, phiên trong CSDL, cookie httpOnly, giới hạn tần suất, plugin admin) | Đăng ký, đăng nhập, đăng xuất, vai trò user/admin, khóa tài khoản |
| CSDL | PostgreSQL 17 + Drizzle ORM (migration trong `web/drizzle/`) | Người dùng, phiên, tin yêu thích, lịch sử định giá |
| `api/` | FastAPI (Python) | Nạp mô hình `.joblib` của notebook: định giá nhà phố (Random Forest + khoảng 80% + giải thích), căn hộ, đất, ý định trợ lý; danh sách tin, bản đồ, xu hướng |
| Trợ lý | Groq (openai/gpt-oss-120b, gọi công cụ = API mô hình) phía máy chủ; không có khóa thì dùng mô hình ý định | Hỏi đáp tiếng Việt, số liệu luôn do mô hình đề tài tính |
| Triển khai | Docker Compose (db, api, migrate, web) | Chạy được trên máy hoặc VPS bất kỳ có Docker |

Trang: trang chủ, định giá (nhà phố / căn hộ / đất), nhà phố Phú Hòa + chi tiết từng tin (giải thích yếu tố, bản đồ, giá thuê), căn hộ, đất nền, bản đồ giá, xu hướng, mô hình (bảng đánh giá đọc từ notebook), trợ lý, đăng ký / đăng nhập, tài khoản (tin đã lưu + so sánh, lịch sử định giá), quản trị (thống kê, cấp/bỏ admin, khóa tài khoản).
Bảo mật: kiểm tra quyền ở máy chủ (`web/src/lib/session.ts`), kiểm tra đầu vào bằng Zod/Pydantic, chống chuyển hướng mở, khóa và mật khẩu chỉ ở `.env` (không lên git), API mô hình và CSDL chỉ mở cho máy này.

## Cấu trúc

Theo quy trình học máy của môn học: **dữ liệu → khám phá, tiền xử lý → mô hình → đánh giá → ứng dụng**.

```
dataset/                    DỮ LIỆU (tin rao thật, đã ẩn danh)
  raw/                      dữ liệu gốc mới nhất của từng nguồn (không sửa tay)
  history/                  ảnh chụp có ghi ngày của mọi kỳ thu thập + nhật ký thu thập
  processed/                dữ liệu đã làm sạch (*_da_xu_ly.csv) và tin bị loại kèm lý do (*_bi_loai.csv)
  labeled/                  dữ liệu gán nhãn tay: câu hỏi cho trợ lý, cặp tin gần trùng
notebooks/                  6 notebook đã chạy, còn output
  2324801030095.ipynb       BÀI CHÍNH – nhà phố Phú Hòa (Phần A theo bài giảng, Phần B đánh giá sâu)
  du_doan_gia_can_ho / du_doan_gia_dat / du_doan_gia_thue / du_doan_xu_huong_gia / tro_ly_y_dinh   (mở rộng)
src/                        mã dùng chung
  mo_hinh_gia.py            đặc trưng, mô hình, kiểm định chéo theo nhóm, khoảng giá, đánh giá
  thu_thap.py               thu thập tự động (Chợ Tốt, alonhadat) + ẩn danh dữ liệu
scripts/                    chạy và tự động hóa
  chay_toan_bo.py           chạy lại toàn bộ đề tài đúng thứ tự (+ cập nhật bảng kết quả README)
  cap_nhat_dinh_ky.py       thu thập hằng ngày, lưu ảnh chụp, chạy lại toàn bộ
  lich_tu_dong.bat          bật / tắt / chạy lịch 07:00 trên Task Scheduler
  guland_thu_thap.js        thu tay guland (chạy trong Console trình duyệt)
  sinh_notebook/            mã sinh từng notebook (sửa notebook ở đây, không sửa .ipynb)
models/                     mô hình đã huấn luyện (.joblib), số liệu đánh giá và mô hình rút gọn cho web (.json)
results/                    kết quả: giá ước lượng, khoảng 80%, chẩn đoán từng căn, tỷ suất cho thuê
web/                        ỨNG DỤNG WEB Next.js: src/app (trang + route handler), src/lib (CSDL, đăng nhập, gọi API), drizzle/ (migration)
api/                        dịch vụ mô hình FastAPI (main.py, dinh_gia.py)
demo/                       bản tĩnh chạy offline: index.html, assets/, build/ (build_site.py sinh index.html + models/du_lieu_web.json)
docker-compose.yml          db + api + migrate + web; bí mật trong .env (mẫu: .env.example)
tests/                      kiem_tra_mo_hinh.py, kiem_tra_api.py (Python) · kiem_tra_tro_ly.js, nap_trang_demo.js, kiem_tra_web.mjs (Node)
docs/                       Tai_lieu_ky_thuat_tong_hop.docx
```

## Chạy lại toàn bộ (đúng thứ tự, ~8 phút)

Một lệnh: `python scripts/chay_toan_bo.py` (thêm `--thu-thap` để tải dữ liệu mới trước, `--tu <bước>` để chạy tiếp từ bước lỗi). Mỗi notebook được sinh lại từ `scripts/sinh_notebook/` rồi chạy, theo thứ tự:

```
python src/thu_thap.py chotot | alonhadat [--can-ho | --dat]                       # tùy chọn: dữ liệu mới
jupyter nbconvert --to notebook --execute --inplace notebooks/2324801030095.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/du_doan_gia_can_ho.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/du_doan_gia_thue.ipynb     # sau nhà phố + căn hộ
jupyter nbconvert --to notebook --execute --inplace notebooks/du_doan_gia_dat.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/du_doan_xu_huong_gia.ipynb
python demo/build/build_site.py
jupyter nbconvert --to notebook --execute --inplace notebooks/tro_ly_y_dinh.ipynb        # cần Node.js
python demo/build/build_site.py
python scripts/chay_toan_bo.py --readme
python tests/kiem_tra_mo_hinh.py && node tests/kiem_tra_tro_ly.js
```
Lý do của thứ tự và các bẫy thường gặp: tài liệu kỹ thuật tổng hợp, mục 8.4.
GitHub Actions (`.github/workflows/kiem_thu.yml`) chạy 2 bộ kiểm thử mỗi lần đẩy code.

**Trợ lý của bản tĩnh (demo/) – chế độ AI:** trên trang `#/tro-ly`, bấm **Chế độ AI**, dán khóa **Groq** (gsk_…, **miễn phí**, tạo ở console.groq.com/keys), **Claude** (sk-ant-…, platform.claude.com) hoặc **Gemini** (aistudio.google.com) – trang tự nhận loại khóa. Groq mặc định openai/gpt-oss-120b (gói miễn phí ~8.000 token/phút mỗi mô hình; hết hạn mức thì trang tự chuyển sang gpt-oss-20b hoặc chờ rồi gửi lại); Claude mặc định Opus 5.5; Gemini tự chọn Flash ổn định mới nhất. Mô hình ngôn ngữ hiểu câu hỏi tự nhiên, nhớ hội thoại và gọi các hàm định giá, tìm nhà, giá thuê, xu hướng của trang như công cụ, nên con số vẫn là của mô hình đề tài. Chỉ cần nhập khóa **một lần**: khóa được ghi nhớ trên trình duyệt đó (mặc định), lần sau mở trang chế độ AI tự bật; nút "Tắt và xóa khóa" để gỡ. Khóa không nằm trong file trang; khi bật, câu hỏi được gửi tới nhà cung cấp của khóa (Groq, Anthropic hoặc Google). **Khóa mặc định trên máy riêng:** đặt khóa vào `demo/khoa_ai.local.js` (`window.PHH_KHOA_MAC_DINH = "gsk_...";`) thì trang tự bật chế độ AI, không cần nhập; file này nằm trong `.gitignore` nên không lên GitHub – xóa nó trước khi gửi thư mục cho người khác. Không có khóa, mất mạng hay lỗi API thì trợ lý tự quay về chế độ ngoại tuyến (chạy hoàn toàn trên trình duyệt).

**Thu thập định kỳ:** chạy `scripts/lich_tu_dong.bat` một lần (tự xin quyền Administrator; `lich_tu_dong.bat tat` để gỡ) để đăng ký tác vụ 07:00 hằng ngày, chạy cả khi không đăng nhập. Mỗi lần chạy: thu tin mới nhất → lưu ảnh chụp có ghi ngày vào `dataset/history/` → chạy lại toàn bộ notebook, trang web, README và kiểm thử (không tự commit hay đẩy lên GitHub). Chỉ số xu hướng lấy mỗi tuần một kỳ. Khi đủ 8 kỳ tuần, notebook xu hướng tự kiểm định lùi mô hình dự báo. Chợ Tốt và alonhadat thu tự động; **guland** (nguồn chính của tin Phú Hòa) chặn trình duyệt tự động nên phải thu tay: mở trang guland Phú Hòa trong trình duyệt, chạy `scripts/guland_thu_thap.js` trong Console, chép file tải về thành `dataset/raw/nha_phu_hoa_guland_raw.csv`. Tác vụ ghi nhắc vào nhật ký khi dữ liệu guland cũ quá 14 ngày.

## Kết quả chính (dữ liệu đến 26/11/2026)

| | Nhà phố – Phú Hòa | Căn hộ | Đất nền – TDM |
|---|---|---|---|
| Mô hình | Random Forest (300 cây) | LightGBM Huber + chữ | Ridge |
| MAPE tập test (kết quả chính) | 26,4% (KTC 19,5–38,7; 44 căn) | 13,7% | 26,8% (KTC 19,7–36,7; 68 lô) |
| MAPE kiểm định chéo theo nhóm | 23,5% | 12,6% | 26,1% |
| Baseline (đơn giá khu vực), kiểm định chéo | 30,7% | 16,1% | 36,6% |
| Phần A (mô hình môn học tốt nhất), tập test | chính là mô hình cuối | Random Forest (300 cây): 14,0% | Random Forest (300 cây): 21,7% |

**Nhà phố – mô hình cuối:** mô hình tốt nhất trong các mô hình của môn học (Phần A, chọn bằng kiểm định chéo), dùng đúng đặc trưng của Phần A. Phần B chỉ so nó với một mô hình đối chứng ngoài bài giảng (LightGBM + giá khu vực) và đo độ tin cậy (kiểm định chéo lặp, bootstrap, khoảng giá 80%).
