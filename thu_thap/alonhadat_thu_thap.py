"""Thu thập tin rao bán NHÀ (nhà mặt tiền, nhà trong hẻm, biệt thự/liền kề) ở TP. Thủ Dầu Một
trên alonhadat.com.vn. Chỉ đọc trang danh sách (thẻ tin đã có giá, diện tích, kích thước,
số tầng, phòng ngủ, đường trước nhà, địa chỉ cũ kèm phường, ngày đăng).
KHÔNG lưu tên/số điện thoại người đăng. Nghỉ 1,5 giây giữa các trang.
Cách dùng: python thu_thap/alonhadat_thu_thap.py           -> nhà ở:  data/raw/alonhadat_tdm_raw.csv
           python thu_thap/alonhadat_thu_thap.py --can-ho  -> căn hộ chung cư: data/raw/alonhadat_can_ho_tdm_raw.csv
           python thu_thap/alonhadat_thu_thap.py --dat     -> đất thổ cư, đất nền: data/raw/alonhadat_dat_tdm_raw.csv"""
import datetime as dt
import html
import pathlib
import re
import sys
import sys as _sys
import time
import urllib.request

_sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # in được tiếng Việt trên mọi console Windows
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "cong_cu"))
from an_danh_du_lieu import (  # riêng tư: che số điện thoại trong tin
    an_danh_bang,
    che_sdt,
)

CAN_HO, DAT = "--can-ho" in __import__("sys").argv, "--dat" in __import__("sys").argv
OUT = ROOT / "data" / "raw" / ("alonhadat_can_ho_tdm_raw.csv" if CAN_HO else "alonhadat_dat_tdm_raw.csv" if DAT else "alonhadat_tdm_raw.csv")
BASE = "https://alonhadat.com.vn/nha-dat/can-ban/{loai}/binh-duong/591/thanh-pho-thu-dau-mot{trang}.html"
LOAI = ["can-ho-chung-cu"] if CAN_HO else ["dat-tho-cu-dat-o", "dat-nen-lien-ke-dat-du-an"] if DAT else ["nha-mat-tien", "nha-trong-hem", "biet-thu-nha-lien-ke"]
UA = {"User-Agent": "Mozilla/5.0"}


LOI_TAI = False         # có trang nào tải thất bại hẳn không -> nếu có thì KHÔNG ghi đè dữ liệu cũ


def get(url):
    global LOI_TAI
    for k in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:
            cho = (30 * 2 ** k) if "429" in str(e) else 5 * (k + 1)      # bị chặn tạm (429): chờ lâu dần 30s, 60s, 120s...
            print("retry", k, e, f"- chờ {cho}s", flush=True); time.sleep(cho)
    LOI_TAI = True
    return ""


def txt(pat, s, default=None):
    m = re.search(pat, s, re.DOTALL)
    return html.unescape(re.sub(r"<[^>]+>", " ", m.group(1))).strip() if m else default


rows, seen = [], set()
for loai in LOAI:
    for p in range(1, 60):
        s = get(BASE.format(loai=loai, trang="" if p == 1 else f"/trang--{p}"))
        cards = re.findall(r"<article class='property-item'.*?</article>", s, re.DOTALL)
        new = 0
        for c in cards:
            href = txt(r"<a class='link[^']*'[^>]*href='([^']+)'", c)
            if not href:
                continue
            m = re.search(r"-(\d+)\.html$", href)
            if not m or m.group(1) in seen:
                continue
            seen.add(m.group(1)); new += 1
            rows.append({
                "id": int(m.group(1)), "url": "https://alonhadat.com.vn" + href, "loai_nha": loai,
                "tieu_de": che_sdt(txt(r"<h3[^>]*>(.*?)</h3>", c)), "ngay_dang": txt(r"datetime='([\d-]+)'", c),
                "mo_ta": che_sdt(txt(r"<p class='brief'[^>]*>(.*?)<span class='view-detail'", c)),
                "gia": txt(r"itemprop='price' content='(\d+)'", c),
                "dt_dat": txt(r"class='area'.*?itemprop='value'>([\d.,]+)<", c),
                "kich_thuoc": txt(r"class='size'>KT: <span>([^<]*)<", c),
                "duong_rong": txt(r"class='street-width'>([^<]*)<", c),
                "so_tang": txt(r"class='floors'>([^<]*)<", c),
                "phong_ngu": txt(r"class='bedroom'.*?itemprop='value'>(\d+)<", c),
                "huong": txt(r"class='direction'>Hướng: <span>([^<]*)<", c),
                "dia_chi_cu": txt(r"class='old-address'>\s*<span>([^<]*)<", c),
                "dia_chi_moi": txt(r"class='new-address'[^>]*>(.*?)</p>", c),
            })
        print(loai, "trang", p, "+", new, "tổng", len(rows), flush=True)
        if not cards or new == 0:
            break
        time.sleep(3)

if LOI_TAI or not rows:
    # Không ghi đè: dữ liệu cũ đầy đủ vẫn tốt hơn dữ liệu mới bị thiếu trang
    print(f"CẢNH BÁO: tải không trọn vẹn ({len(rows)} tin) - giữ nguyên {OUT.name} cũ, không ghi đè.", flush=True)
    sys.exit(2)
df = pd.DataFrame(rows)
df["ngay_thu_thap"] = dt.date.today().isoformat()
df["dia_chi_moi"] = df["dia_chi_moi"].str.replace(r"\s+", " ", regex=True)
df = an_danh_bang(df.astype(object).where(df.notna(), "").astype(str))[0]          # che SĐT ở mọi cột chữ (kể cả địa chỉ)
df.to_csv(OUT, index=False, encoding="utf-8-sig")
print("Đã lưu", len(df), "tin ->", OUT)
