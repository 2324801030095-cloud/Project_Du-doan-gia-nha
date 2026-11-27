# Dự đoán giá nhà Phú Hòa – Thủ Dầu Một

Đề tài môn Học máy · MSSV 2324801030095 · Nguyễn Quang Long · Lớp D23KTPM01

Học máy có giám sát ước lượng **giá rao bán** của **nhà ở (nhà + đất) tại phường Phú Hòa**, Thủ Dầu Một – bài chính.
Phần mở rộng: căn hộ, giá thuê, xu hướng, trợ lý. Kèm khoảng giá 80%, chẩn đoán giá rao rẻ / hợp lý / cao, phân tích xu hướng, và **ứng dụng web đầy đủ** (đăng nhập, định giá bằng mô hình thật trên máy chủ, lưu tin, lịch sử, quản trị, trợ lý AI).
Dữ liệu là tin rao thật (Chợ Tốt Nhà, alonhadat, guland), đã ẩn danh. **Giá rao không phải giá giao dịch**: giá giao dịch là mức hai bên chốt sau thương lượng, còn tổng chi phí người mua có thể gồm thêm thuế, phí. Mọi con số của đề tài là **giá rao bán ước tính**.

**Phạm vi:** đề tài định giá NHÀ. Tin có tiêu đề "bán đất" (kể cả "bán đất tặng nhà") được **giữ** nếu có thông tin căn nhà (số tầng, diện tích sàn, số phòng ngủ, hoặc mô tả trệt/lầu/phòng/cấp 4/nhà vườn); bị **loại** (có ghi lý do trong `dataset/processed/tin_bi_loai.csv`) nếu kèm dãy trọ / phòng trọ / ki-ốt / kho, nếu nhà sẽ đập bỏ hoặc xây mới, hoặc nếu không có thông tin căn nhà nào. Định giá lô đất trống đã bỏ khỏi bài chính, API và ứng dụng web Next.js; notebook và kết quả cũ để ở `notebooks/luu_tru/` để truy xuất.
**Ranh giới web:** ứng dụng web (`web/` Next.js + `api/` FastAPI) là sản phẩm chính và **không** còn định giá đất. Bản tĩnh `demo/index.html` là bản demo cũ chạy offline, **vẫn còn** trang đất nền của phiên bản trước; nó không phải sản phẩm bàn giao chính và không được dùng cho số liệu báo cáo.

**Tài liệu bàn giao (Word, số liệu đọc tự động từ lần chạy bàn giao): [docs/Tai_lieu_ban_giao_2026-11-28.docx](docs/Tai_lieu_ban_giao_2026-11-28.docx)** – dataset, mô hình, kết quả (kèm so sánh cặp với baseline), kiến trúc, kiểm thử (ĐẠT / KHÔNG ĐẠT / BỎ QUA theo mã thoát thật), chia việc nhóm, câu hỏi bảo vệ. Bản bàn giao trước [docs/Tai_lieu_ban_giao.docx](docs/Tai_lieu_ban_giao.docx) giữ nguyên để đối chiếu. Tài liệu cũ (chi tiết kỹ thuật, một số số liệu của lần chạy trước): [docs/Tai_lieu_ky_thuat_tong_hop.docx](docs/Tai_lieu_ky_thuat_tong_hop.docx) – cấu trúc, cài đặt, công nghệ, thuật toán, logic dữ liệu, đầu vào/đầu ra, huấn luyện và kết quả, web demo, trợ lý, kiểm thử, hạn chế, checklist, câu hỏi bảo vệ.

## Bắt đầu nhanh

**Ứng dụng web** (cần Docker Desktop):
```
copy .env.example .env                   # rồi điền mật khẩu CSDL, BETTER_AUTH_SECRET, tài khoản admin, (tùy chọn) GROQ_API_KEY
docker compose up -d --build             # db + api + migrate + web
```
Mở http://localhost:3000 · đăng nhập admin bằng ADMIN_EMAIL / ADMIN_PASSWORD trong `.env` · tài liệu API mô hình: http://localhost:8000/docs

**Mô hình và kiểm thử** (Python 3.14, Node.js >= 18). Kiểm thử chạy trên **máy** (không chạy trong container `api`: image đó chỉ cài `api/requirements.txt`, không có thư viện kiểm thử như `httpx2`). Cài `requirements.txt` vào **đúng** trình thông dịch sẽ chạy kiểm thử (ví dụ `.venv`: `.venv\Scripts\python -m pip install -r requirements.txt`; thiếu bước này thì `kiem_tra_api.py` báo thiếu `fastapi`).
```
pip install -r requirements.txt
python tests/kiem_tra_mo_hinh.py         # mã mô hình, dữ liệu, số liệu notebook/README  (--nha-pho: chỉ bài chính)
python tests/kiem_tra_api.py             # API mô hình chạy trong tiến trình             (--nha-pho: chỉ bài chính)
python tests/kiem_tra_cong_bo.py         # công bố bộ tệp cho API: nạp A -> công bố B, tệp hỏng/thiếu, API tắt/lỗi (trên bản sao tạm)
node tests/kiem_tra_tro_ly.js            # bản tĩnh + trợ lý
node tests/kiem_tra_web.mjs              # đầu-cuối, cần web đang chạy: đăng ký/đăng nhập thật, phân quyền, lịch sử...
```
Mỗi bộ in từng phép ĐẠT / KHÔNG ĐẠT / BỎ QUA (kèm lý do) và trả mã thoát khác 0 nếu có phép không đạt. Ở chế độ `--nha-pho`, phép kiểm phần mở rộng (căn hộ, trợ lý, dự báo xu hướng) được BỎ QUA chứ không tính là đạt.
Bản tĩnh chạy offline (không cần máy chủ): mở `demo/index.html` (bản demo cũ, xem "Ranh giới web" ở trên).

## Ứng dụng web

| Thành phần | Công nghệ | Vai trò |
|---|---|---|
| `web/` | Next.js 16 (App Router, React 19, TypeScript), Tailwind CSS 4, Leaflet, Recharts | Giao diện + backend-for-frontend: trang, route handler, kiểm tra phiên ở máy chủ |
| Đăng nhập | Better Auth (email + mật khẩu băm scrypt, phiên trong CSDL, cookie httpOnly, giới hạn tần suất, plugin admin) | Đăng ký, đăng nhập, đăng xuất, vai trò user/admin, khóa tài khoản |
| CSDL | PostgreSQL 17 + Drizzle ORM (migration trong `web/drizzle/`) | Người dùng, phiên, tin yêu thích, lịch sử định giá |
| `api/` | FastAPI (Python) | Nạp mô hình `.joblib` của notebook: định giá nhà phố (Random Forest + khoảng 80% + giải thích), căn hộ, ý định trợ lý; danh sách tin, bản đồ, xu hướng |
| Trợ lý | Groq (openai/gpt-oss-120b, gọi công cụ = API mô hình) phía máy chủ; không có khóa thì dùng mô hình ý định | Hỏi đáp tiếng Việt, số liệu luôn do mô hình đề tài tính |
| Triển khai | Docker Compose (db, api, migrate, web) | Chạy được trên máy hoặc VPS bất kỳ có Docker |

Trang: trang chủ, định giá (nhà phố / căn hộ), nhà phố Phú Hòa + chi tiết từng tin (giải thích yếu tố, bản đồ, giá thuê), căn hộ, bản đồ giá, xu hướng, mô hình (bảng đánh giá đọc từ notebook), trợ lý, đăng ký / đăng nhập, tài khoản (tin đã lưu + so sánh, lịch sử định giá), quản trị (thống kê, cấp/bỏ admin, khóa tài khoản).
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
  du_doan_gia_can_ho / du_doan_gia_thue / du_doan_xu_huong_gia / tro_ly_y_dinh   (mở rộng)
  luu_tru/                  du_doan_gia_dat (đất nền – đã bỏ khỏi bài chính, giữ để truy xuất, không chạy lại)
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
tests/                      kiem_tra_mo_hinh.py, kiem_tra_api.py, kiem_tra_cong_bo.py (Python) · kiem_tra_tro_ly.js, nap_trang_demo.js, kiem_tra_web.mjs (Node)
docs/                       Tai_lieu_ban_giao_2026-11-28.docx (bàn giao, sinh bằng scripts/tai_lieu/), Tai_lieu_ban_giao.docx (bản trước), Tai_lieu_ky_thuat_tong_hop.docx
```

## Chạy lại toàn bộ (đúng thứ tự, ~8 phút)

Một lệnh: `python scripts/chay_toan_bo.py` (chỉ bài chính nhà phố: `--nha-pho`; thêm `--thu-thap` để tải dữ liệu mới trước, `--tu <bước>` để chạy tiếp từ bước lỗi). Mỗi notebook được sinh lại từ `scripts/sinh_notebook/` rồi chạy, theo thứ tự:

```
python src/thu_thap.py chotot | alonhadat [--can-ho | --dat]                       # tùy chọn: dữ liệu mới
jupyter nbconvert --to notebook --execute --inplace notebooks/2324801030095.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/du_doan_gia_can_ho.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/du_doan_gia_thue.ipynb     # sau nhà phố + căn hộ
jupyter nbconvert --to notebook --execute --inplace notebooks/du_doan_xu_huong_gia.ipynb
python demo/build/build_site.py
jupyter nbconvert --to notebook --execute --inplace notebooks/tro_ly_y_dinh.ipynb        # cần Node.js
python demo/build/build_site.py
python scripts/chay_toan_bo.py --readme
python tests/kiem_tra_mo_hinh.py && python tests/kiem_tra_api.py && python tests/kiem_tra_cong_bo.py && node tests/kiem_tra_tro_ly.js
python api/dinh_gia.py --cong-bo                                                          # CUỐI CÙNG, chỉ khi mọi kiểm thử đạt
```
**Công bố là bước cuối.** Kiểm thử chạy trên tệp làm việc vừa sinh (bộ **ứng viên**; `kiem_tra_api.py` đặt `PHH_UNG_VIEN=1` để API trong tiến trình bỏ qua bản kê). Chỉ khi mọi bộ kiểm thử của chế độ đạt, bước `cong_bo` mới chép bộ tệp vào `models/cong_bo/<mã bộ>/`, nạp thử đúng bản chép đó như API (cấu trúc dữ liệu + chạy thử định giá, danh sách tin, tổng quan, bản đồ, danh mục, health), rồi ghi `models/phien_ban.json` trỏ tới nó. Một kiểm thử lỗi -> lệnh dừng trước công bố, bản kê không đổi, API vẫn phục vụ bộ cũ. `--tu <bước>` bỏ qua bước kiểm thử nào thì trước khi công bố pipeline vẫn chạy lại các bước đó. `models/phien_ban.json` và `models/cong_bo/` là trạng thái của từng máy (không lên git, không vào image); chỉ giữ bộ đang phục vụ và bộ trước đó.
Cuối lệnh, pipeline gọi API đang chạy (`PHH_API_URL`, mặc định http://127.0.0.1:8000) và in một trong ba kết quả: **ĐẠT** (API phục vụ đúng bộ vừa công bố: cùng mã bộ, cùng tập tệp và mã băm, POST /dinh-gia/nha-pho trả đúng mã bộ), **BỎ QUA** (API không chạy) hoặc **LỖI** (HTTP lỗi, /health thiếu trường vì image cũ, lệch bộ, nạp lỗi) – LỖI làm lệnh thoát khác 0. Không cần restart container `api`: nó tự nạp khi bản kê đổi.

**Bài chính tách riêng (`--nha-pho`):** chỉ cần `dataset/raw` + `dataset/history` của nhà ở, `src/`, `scripts/`, `api/`, `demo/build/`, `tests/`; không cần dữ liệu hay mô hình căn hộ, thuê, xu hướng, trợ lý, cũng không cần Node.js. Các bước: notebook `2324801030095` → `xuat_du_lieu_web` (`build_site.py --chi-du-lieu`, chỉ ghi `models/du_lieu_web.json`, không sinh trang tĩnh) → `cap_nhat_readme` → kiểm thử `--nha-pho` + `kiem_tra_cong_bo` → `cong_bo`. `--thu-thap` đi với `--nha-pho` chỉ thu nguồn nhà ở (Chợ Tốt, alonhadat); `--thu-thap` kèm `--tu` một bước sau notebook bị từ chối (dữ liệu mới chỉ vào mô hình ở bước notebook). `--xu-huong` (notebook xu hướng → dựng trang → README → kiểm thử → công bố) không dùng chung với `--nha-pho`, `--tu`, `--thu-thap`; tổ hợp không hỗ trợ và cờ lạ bị từ chối trước khi chạy bất cứ bước nào.

**API chạy với bộ tệp nào:** API không đọc thẳng từng tệp khi chúng đổi; nó chỉ chuyển bộ khi `models/phien_ban.json` đổi: đọc mỗi tệp của bản chép một lần, so mã băm, kiểm cấu trúc và kiểu của mọi phần endpoint dùng (kể cả tệp mở rộng nếu bản kê có), chạy thử các endpoint rồi mới thay bộ cũ. Lỗi (thiếu tệp, tệp hỏng, JSON đúng cú pháp nhưng thiếu khóa, mã băm lệch) thì **giữ bộ đang phục vụ** và báo ở `/health` (`loi_nap_moi_nhat`); chưa có bộ hợp lệ nào thì mọi endpoint dữ liệu và định giá trả **503** (không 500). `/health` và mỗi kết quả định giá có trường `phien_ban` = mã bộ. Chưa công bố lần nào (bản sao mới) thì API tự lập bản kê từ tệp làm việc. Chạy API chỉ với bài chính: `uvicorn main:app --app-dir api` khi chỉ có 4 tệp bắt buộc (mô hình nhà, `du_lieu_web.json`, `danh_gia_mo_hinh.json`, `nha_da_xu_ly.csv`) – endpoint căn hộ / trợ lý trả 503; image Docker cũng build được khi thiếu CSV căn hộ.

Lý do của thứ tự và các bẫy thường gặp: tài liệu kỹ thuật tổng hợp, mục 8.4.
GitHub Actions (`.github/workflows/kiem_thu.yml`) chạy kiểm thử mô hình và API (đủ và `--nha-pho`), kiểm thử công bố, bản tĩnh/trợ lý, rồi typecheck/lint/build web mỗi lần đẩy code.

**Trợ lý của bản tĩnh (demo/) – chế độ AI:** trên trang `#/tro-ly`, bấm **Chế độ AI**, dán khóa **Groq** (gsk_…, **miễn phí**, tạo ở console.groq.com/keys), **Claude** (sk-ant-…, platform.claude.com) hoặc **Gemini** (aistudio.google.com) – trang tự nhận loại khóa. Groq mặc định openai/gpt-oss-120b (gói miễn phí ~8.000 token/phút mỗi mô hình; hết hạn mức thì trang tự chuyển sang gpt-oss-20b hoặc chờ rồi gửi lại); Claude mặc định Opus 5.5; Gemini tự chọn Flash ổn định mới nhất. Mô hình ngôn ngữ hiểu câu hỏi tự nhiên, nhớ hội thoại và gọi các hàm định giá, tìm nhà, giá thuê, xu hướng của trang như công cụ, nên con số vẫn là của mô hình đề tài. Chỉ cần nhập khóa **một lần**: khóa được ghi nhớ trên trình duyệt đó (mặc định), lần sau mở trang chế độ AI tự bật; nút "Tắt và xóa khóa" để gỡ. Khóa không nằm trong file trang; khi bật, câu hỏi được gửi tới nhà cung cấp của khóa (Groq, Anthropic hoặc Google). **Khóa mặc định trên máy riêng:** đặt khóa vào `demo/khoa_ai.local.js` (`window.PHH_KHOA_MAC_DINH = "gsk_...";`) thì trang tự bật chế độ AI, không cần nhập; file này nằm trong `.gitignore` nên không lên GitHub – xóa nó trước khi gửi thư mục cho người khác. Không có khóa, mất mạng hay lỗi API thì trợ lý tự quay về chế độ ngoại tuyến (chạy hoàn toàn trên trình duyệt).

**Thu thập định kỳ:** chạy `scripts/lich_tu_dong.bat` một lần (tự xin quyền Administrator; `lich_tu_dong.bat tat` để gỡ) để đăng ký tác vụ 07:00 hằng ngày, chạy cả khi không đăng nhập. Mỗi lần chạy: thu tin mới nhất → lưu ảnh chụp có ghi ngày vào `dataset/history/` → chạy lại toàn bộ notebook, trang web, README và kiểm thử (không tự commit hay đẩy lên GitHub). Chỉ số xu hướng lấy mỗi tuần một kỳ. Khi đủ 8 kỳ tuần, notebook xu hướng tự kiểm định lùi mô hình dự báo. Chợ Tốt và alonhadat thu tự động; **guland** (nguồn chính của tin Phú Hòa) chặn trình duyệt tự động nên phải thu tay: mở trang guland Phú Hòa trong trình duyệt, chạy `scripts/guland_thu_thap.js` trong Console, chép file tải về thành `dataset/raw/nha_phu_hoa_guland_raw.csv`. Tác vụ ghi nhắc vào nhật ký khi dữ liệu guland cũ quá 14 ngày.

## Kết quả chính (dữ liệu đến 26/11/2026)

| | Nhà phố – Phú Hòa (bài chính) | Căn hộ (mở rộng) |
|---|---|---|
| Mô hình | Random Forest (300 cây) | LightGBM Huber + chữ |
| Tập test giữ riêng | 43 căn | 110 căn |
| MAPE mô hình trên test | 25,1% (KTC 95% 18,8–35,4) | 13,7% |
| MAE mô hình trên test | 1,75 tỷ đồng | 0,27 tỷ đồng |
| Mốc so sánh trên cùng tập test | Baseline (đơn giá phường): MAPE 25,9%, MAE 1,69 tỷ | Baseline (đơn giá dự án): MAPE 15,2%, MAE 0,33 tỷ |
| Chênh mô hình − mốc trên từng căn test (so sánh cặp) | MAPE -0,8 điểm % (KTC -9,9 đến 5,8) – KTC chứa 0: chưa đủ bằng chứng; MAE 0,06 tỷ (KTC -0,49 đến 0,59) – KTC chứa 0: chưa đủ bằng chứng | – |
| Kiểm định chéo trên tập train (mô hình / mốc) | 24,1% / 31,5% | 12,6% / 16,1% |
| Khoảng giá 80%: độ phủ đo trên test | 32/43 căn (74%) | – |

**Nhà phố – mô hình cuối:** mô hình tốt nhất trong các mô hình của môn học (Phần A, chọn bằng kiểm định chéo), dùng đúng đặc trưng của Phần A. Phần B chỉ so nó với một mô hình đối chứng ngoài bài giảng (LightGBM + giá khu vực) và đo độ tin cậy (kiểm định chéo lặp, bootstrap, khoảng giá 80%).
