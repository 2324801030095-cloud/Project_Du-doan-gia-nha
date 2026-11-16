"""Cập nhật dữ liệu định kỳ (nên chạy mỗi tuần hoặc mỗi 2 tuần, ví dụ bằng Task Scheduler của Windows).

1. Chạy lại 2 script thu thập tự động (Chợ Tốt, alonhadat) -> ghi đè data/raw/*_raw.csv bằng dữ liệu mới nhất.
2. Lưu một bản sao có ghi ngày vào data/lich_su/ (ví dụ data/lich_su/chotot_2026-11-14.csv).

Mỗi bản sao là một "ảnh chụp" thị trường thật tại ngày đó. Notebook du_doan_xu_huong_gia.ipynb đọc tất cả
ảnh chụp trong data/lich_su/ để dựng chỉ số giá theo thời gian (cùng một tin xuất hiện ở nhiều ảnh chụp
cho biết người bán đã tăng hay giảm giá). Càng nhiều ảnh chụp, dự báo xu hướng càng có cơ sở.

Cách dùng (từ thư mục đề tài):  python thu_thap/cap_nhat_dinh_ky.py
Chỉ lưu ảnh chụp, không thu thập lại:  python thu_thap/cap_nhat_dinh_ky.py --chi-luu
"""
import datetime as dt
import sys as _sys
_sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # in được tiếng Việt trên mọi console Windows
import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LS = ROOT / "data" / "lich_su"
LS.mkdir(parents=True, exist_ok=True)
NGUON = {"chotot": ("chotot_thu_thap.py", "chotot_binh_duong_raw.csv"),
         "alonhadat": ("alonhadat_thu_thap.py", "alonhadat_tdm_raw.csv"),
         "chotot_can_ho": ("chotot_thu_thap.py --can-ho", "chotot_can_ho_raw.csv"),
         "alonhadat_can_ho": ("alonhadat_thu_thap.py --can-ho", "alonhadat_can_ho_tdm_raw.csv"),
         "chotot_dat": ("chotot_thu_thap.py --dat", "chotot_dat_raw.csv"),
         "alonhadat_dat": ("alonhadat_thu_thap.py --dat", "alonhadat_dat_tdm_raw.csv")}

import time
loi = []
for ten, (script, csv) in NGUON.items():
    if "--chi-luu" not in sys.argv:
        print(f"== Thu thập {ten} ...", flush=True)
        ten_file, *tham_so = script.split()
        kq = subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "thu_thap" / ten_file), *tham_so], cwd=ROOT)   # -X utf8: in được tiếng Việt
        if kq.returncode != 0:
            # một nguồn lỗi không làm dừng các nguồn khác; nguồn lỗi không có ảnh chụp mới cho kỳ này
            loi.append(ten); print(f"   LỖI khi thu thập {ten} (mã {kq.returncode}) - bỏ qua ảnh chụp kỳ này", flush=True); continue
        if "alonhadat" in ten:
            time.sleep(20)      # nghỉ giữa các lượt alonhadat để không bị chặn tạm (429)
    src = ROOT / "data" / "raw" / csv
    if not src.exists():
        continue
    import pandas as pd
    ngay = str(pd.read_csv(src, usecols=["ngay_thu_thap"])["ngay_thu_thap"].iloc[0])
    dst = LS / f"{ten}_{ngay}.csv"
    shutil.copyfile(src, dst)
    print(f"   đã lưu ảnh chụp: {dst.relative_to(ROOT)}")

# guland không có API công khai: sau khi chạy guland_thu_thap.js trong trình duyệt, đặt file vào data/raw/ rồi
# chép tay thành data/lich_su/guland_<ngày>.csv
g = ROOT / "data" / "raw" / "nha_phu_hoa_guland_raw.csv"
if g.exists():
    import pandas as pd
    ngay = str(pd.read_csv(g, usecols=["ngay_thu_thap"])["ngay_thu_thap"].iloc[0])
    if not (LS / f"guland_{ngay}.csv").exists():
        shutil.copyfile(g, LS / f"guland_{ngay}.csv")
print("Các ảnh chụp hiện có:", sorted(p.name for p in LS.glob("*.csv")))
print("Ngày cập nhật:", dt.date.today().isoformat(), "| nguồn lỗi:", loi or "không")
sys.exit(1 if loi else 0)
