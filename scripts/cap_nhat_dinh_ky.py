"""Cập nhật dữ liệu hằng ngày (Task Scheduler gọi lúc 07:00, xem scripts/lich_tu_dong.bat).

1. Chạy lại 2 script thu thập tự động (Chợ Tốt, alonhadat) -> ghi đè dataset/raw/*_raw.csv bằng dữ liệu mới nhất.
2. Lưu một bản sao có ghi ngày vào dataset/history/ (ví dụ dataset/history/chotot_2026-11-14.csv).
3. Chạy lại toàn bộ đề tài (scripts/chay_toan_bo.py): notebook, trang web, README, kiểm thử -> mọi số liệu theo dữ liệu mới nhất.
   Notebook xu hướng tính MỖI TUẦN là một kỳ (ảnh chụp mới nhất của tuần), nên ảnh chụp hằng ngày không làm sai chỉ số xu hướng.

Mỗi bản sao là một "ảnh chụp" thị trường thật tại ngày đó. Notebook du_doan_xu_huong_gia.ipynb đọc tất cả
ảnh chụp trong dataset/history/ để dựng chỉ số giá theo thời gian (cùng một tin xuất hiện ở nhiều ảnh chụp
cho biết người bán đã tăng hay giảm giá). Càng nhiều ảnh chụp, dự báo xu hướng càng có cơ sở.

Cách dùng (từ thư mục đề tài):  python scripts/cap_nhat_dinh_ky.py
Chỉ lưu ảnh chụp, không thu thập lại:  python scripts/cap_nhat_dinh_ky.py --chi-luu
Thu thập nhưng không chạy lại notebook:  python scripts/cap_nhat_dinh_ky.py --khong-chay-lai
Chỉ nguồn nhà ở (bài chính):            thêm --chi-nha
"""
import datetime as dt
import sys as _sys

_sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # in được tiếng Việt trên mọi console Windows
import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LS = ROOT / "dataset" / "history"
LS.mkdir(parents=True, exist_ok=True)
NGUON = {"chotot": ("chotot", "chotot_binh_duong_raw.csv"),              # tham số cho src/thu_thap.py
         "alonhadat": ("alonhadat", "alonhadat_tdm_raw.csv"),
         "chotot_can_ho": ("chotot --can-ho", "chotot_can_ho_raw.csv"),
         "alonhadat_can_ho": ("alonhadat --can-ho", "alonhadat_can_ho_tdm_raw.csv")}
if "--chi-nha" in sys.argv:          # scripts/chay_toan_bo.py --nha-pho --thu-thap: chỉ nguồn nhà ở của bài chính
    NGUON = {k: v for k, v in NGUON.items() if k in ("chotot", "alonhadat")}
# Đất nền đã bỏ khỏi đề tài (chỉ định giá nhà ở): không thu thập đất định kỳ nữa. Dữ liệu đất cũ giữ ở dataset/raw, dataset/history
# để truy xuất; muốn thu lại thì chạy tay: python src/thu_thap.py chotot --dat / alonhadat --dat

import time

loi = []
for ten, (tham_so, csv) in NGUON.items():
    if "--chi-luu" not in sys.argv:
        print(f"== Thu thập {ten} ...", flush=True)
        kq = subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "src" / "thu_thap.py"), *tham_so.split()], cwd=ROOT)   # -X utf8: in được tiếng Việt
        if kq.returncode != 0:
            # một nguồn lỗi không làm dừng các nguồn khác; nguồn lỗi không có ảnh chụp mới cho kỳ này
            loi.append(ten); print(f"   LỖI khi thu thập {ten} (mã {kq.returncode}) - bỏ qua ảnh chụp kỳ này", flush=True); continue
        if "alonhadat" in ten:
            time.sleep(20)      # nghỉ giữa các lượt alonhadat để không bị chặn tạm (429)
    src = ROOT / "dataset" / "raw" / csv
    if not src.exists():
        continue
    import pandas as pd
    ngay = str(pd.read_csv(src, usecols=["ngay_thu_thap"])["ngay_thu_thap"].iloc[0])
    dst = LS / f"{ten}_{ngay}.csv"
    # Cảnh báo khi số tin tụt mạnh so với kỳ trước: thường do trang đổi giao diện/API hoặc bị chặn một phần,
    # chứ không phải thị trường thật sự giảm một nửa số tin trong vài ngày.
    truoc = [p for p in sorted(LS.glob(f"{ten}_20*.csv")) if p != dst]
    n_moi = len(pd.read_csv(src, usecols=["ngay_thu_thap"]))
    if truoc:
        n_cu = len(pd.read_csv(truoc[-1], usecols=["ngay_thu_thap"]))
        if n_moi < 0.7 * n_cu:
            loi.append(f"{ten} (số tin giảm bất thường)")
            print(f"   CẢNH BÁO {ten}: chỉ {n_moi} tin, kỳ trước {truoc[-1].name} có {n_cu} tin (giảm > 30%) - kiểm tra lại script thu thập", flush=True)
    shutil.copyfile(src, dst)
    print(f"   đã lưu ảnh chụp: {dst.relative_to(ROOT)} ({n_moi} tin)")

# guland không có API công khai: sau khi chạy guland_thu_thap.js trong trình duyệt, đặt file vào dataset/raw/ rồi
# chép tay thành dataset/history/guland_<ngày>.csv
g = ROOT / "dataset" / "raw" / "nha_phu_hoa_guland_raw.csv"
if g.exists():
    import pandas as pd
    ngay = str(pd.read_csv(g, usecols=["ngay_thu_thap"])["ngay_thu_thap"].iloc[0])
    if not (LS / f"guland_{ngay}.csv").exists():
        shutil.copyfile(g, LS / f"guland_{ngay}.csv")
    # guland chặn trình duyệt tự động (Cloudflare "Just a moment...", 403 cả với Chrome headless) nên không thể đưa vào lịch tự động.
    # Phần lớn tin Phú Hòa đến từ guland: nhắc thu thập tay khi ảnh chụp đã cũ.
    tuoi = (dt.date.today() - dt.date.fromisoformat(ngay)).days
    if tuoi >= 14:
        loi.append(f"guland cũ {tuoi} ngày")
        print(f"   NHẮC: dữ liệu guland (nguồn chính của Phú Hòa) đã {tuoi} ngày - chạy scripts/guland_thu_thap.js trong trình duyệt "
              "rồi chép file thành dataset/raw/nha_phu_hoa_guland_raw.csv", flush=True)
import re

import pandas as pd

bang = [(m[1], m[2], len(pd.read_csv(p, usecols=["ngay_thu_thap"]))) for p in LS.glob("*.csv")
        if (m := re.match(r"(.+)_(\d{4}-\d{2}-\d{2})\.csv$", p.name))]
print("Số tin theo kỳ và nguồn:\n" + pd.DataFrame(bang, columns=["nguon", "ky", "so_tin"]).pivot(index="ky", columns="nguon", values="so_tin").to_string())
print("Ngày cập nhật:", dt.date.today().isoformat(), "| nguồn lỗi:", loi or "không")
# Kỳ của chỉ số xu hướng = tuần (ISO); đủ 8 tuần thì notebook xu hướng tự kiểm định lùi Holt
so_tuan = len({dt.date.fromisoformat(p.stem[-10:]).isocalendar()[:2] for p in LS.glob("chotot_20*.csv")})
print(f"Ảnh chụp nhà ở: {so_tuan}/8 tuần (đủ 8 tuần, notebook xu hướng tự kiểm định lùi mô hình dự báo)")
# Chạy lại toàn bộ để notebook, mô hình, trang web và README dùng dữ liệu vừa thu
if not {"--chi-luu", "--khong-chay-lai"} & set(sys.argv):
    print("== Chạy lại toàn bộ đề tài với dữ liệu mới", flush=True)
    if subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "scripts" / "chay_toan_bo.py")], cwd=ROOT, check=False).returncode != 0:
        loi.append("chạy lại đề tài (xem các dòng DỪNG ở trên)")
sys.exit(1 if loi else 0)
