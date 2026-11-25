"""Thu thập tin rao bán NHÀ Ở (cg=1020) khu vực Bình Dương cũ (region_v2=2011) từ API công khai
của Chợ Tốt Nhà (gateway.chotot.com) - chính là API mà trang nhatot.com dùng để hiển thị tin.
Mỗi tin có: giá, diện tích, ngang, dài, số tầng, phòng ngủ, WC, loại nhà, mặt tiền/hẻm,
pháp lý, nội thất, phường, tên đường, TỌA ĐỘ, ngày đăng gốc.
Cách dùng: python thu_thap/chotot_thu_thap.py            -> nhà ở:  data/raw/chotot_binh_duong_raw.jsonl + .csv
           python thu_thap/chotot_thu_thap.py --can-ho   -> căn hộ chung cư (cg=1010): data/raw/chotot_can_ho_raw.jsonl + .csv
           python thu_thap/chotot_thu_thap.py --dat      -> đất (cg=1040): data/raw/chotot_dat_raw.jsonl + .csv
           Căn hộ có thêm: tên dự án, loại căn hộ (chung cư / duplex / penthouse...), tầng, block, tình trạng bàn giao.
Nghỉ 1 giây giữa các lần gọi để không gây tải cho máy chủ."""
import datetime as dt
import json
import pathlib
import sys as _sys
import time
import urllib.request

_sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # in được tiếng Việt trên mọi console Windows
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent
import collections
import sys

CAN_HO, DAT = "--can-ho" in sys.argv, "--dat" in sys.argv
TEN = "chotot_can_ho_raw" if CAN_HO else "chotot_dat_raw" if DAT else "chotot_binh_duong_raw"
OUT_JSONL, OUT_CSV = ROOT / "data" / "raw" / f"{TEN}.jsonl", ROOT / "data" / "raw" / f"{TEN}.csv"
API = "https://gateway.chotot.com/v1/public/ad-listing?cg=" + ("1010" if CAN_HO else "1040" if DAT else "1020") + "&region_v2=2011&limit=50&o={o}&key_param_included=true"
UA = {"User-Agent": "Mozilla/5.0"}


def get(url):
    for k in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            print("retry", k, e); time.sleep(5 * (k + 1))
    print(f"CẢNH BÁO: không tải được {url} - giữ nguyên dữ liệu cũ, không ghi đè.", flush=True)
    sys.exit(2)


ads, seen, o = [], set(), 0
if "--flatten-only" in sys.argv:          # chỉ dựng lại CSV từ JSONL đã tải
    ads = [json.loads(l) for l in open(OUT_JSONL, encoding="utf-8") if l.strip()]
while "--flatten-only" not in sys.argv:      # tải mọi trang cho tới khi hết tin
    d = get(API.format(o=o))
    batch = d.get("ads", [])
    if not batch:
        break
    for a in batch:
        if a["list_id"] not in seen:
            seen.add(a["list_id"]); ads.append(a)
    print(f"o={o}: +{len(batch)} (tổng {len(ads)}/{d.get('total')})", flush=True)
    o += 50
    if o >= d.get("total", 0):
        break
    time.sleep(1)

# Riêng tư: không lưu thông tin người đăng (tên, mã tài khoản, ảnh đại diện) và che số điện thoại trong tin
sys.path.insert(0, str(ROOT / "cong_cu"))
from an_danh_du_lieu import an_danh_bang, an_danh_tin, dong_jsonl

ads = [an_danh_tin(a) for a in ads]
ngay = ads[0].get("_ngay_thu_thap") or dt.date.today().isoformat()
if "--flatten-only" not in sys.argv:
    with open(OUT_JSONL, "w", encoding="utf-8") as f:
        for a in ads:
            a["_ngay_thu_thap"] = ngay
            f.write(dong_jsonl(a) + "\n")          # thoát U+2028/U+2029: mỗi dòng luôn là đúng 1 bản ghi JSON

# Bảng mã -> nhãn chữ: học từ chính các tin có kèm nhãn (không tự đoán mã)
NHAN = collections.defaultdict(collections.Counter)
for a in ads:
    items = (a.get("feature_params") or {}).get("compare", {}).get("items", []) + (a.get("params") or [])
    lab = {i["id"]: i["value"] for i in items}
    for k in ("house_type", "property_legal_document", "furnishing_sell", "apartment_type", "property_status", "apartment_feature", "balconydirection", "direction", "land_type"):
        if k in a and k in lab:
            NHAN[k][(a[k], lab[k])] += 1
    pc = a.get("pty_characteristics") or []
    if len(pc) == 1 and "pty_characteristics" in lab:
        NHAN["pc"][(pc[0], lab["pty_characteristics"])] += 1
MAP = {k: {} for k in NHAN}
for k, c in NHAN.items():
    for (code, label), n in c.most_common():
        MAP[k].setdefault(code, label)
HOUSE_TYPE, LEGAL, FURN, CHAR = (MAP.get(k, {}) for k in ("house_type", "property_legal_document", "furnishing_sell", "pc"))
nhan = lambda k, v: None if v is None else MAP.get(k, {}).get(v, v)
print("Bảng mã học từ dữ liệu:", dict(MAP))

ts = lambda v: dt.datetime.fromtimestamp(v / 1000).date().isoformat() if v else None
rows = [{
    "id": a["list_id"], "url": f"https://www.nhatot.com/{a['list_id']}.htm", "ngay_thu_thap": ngay,
    "ngay_dang": ts(a.get("orig_list_time") or a.get("list_time")), "ngay_cap_nhat": ts(a.get("list_time")),
    "loai_tin": "ban" if a.get("type") == "s" else "cho_thue", "tieu_de": a.get("subject"), "mo_ta": a.get("body"), "gia": a.get("price"), "gia_goc_luc_dang": a.get("original_price"),
    "dt_dat": a.get("size"), "dt_su_dung": a.get("living_size"), "ngang": a.get("width"), "dai": a.get("length"),
    "so_tang": a.get("floors"), "phong_ngu": a.get("rooms"), "so_wc": a.get("toilets"),
    "loai_nha": HOUSE_TYPE.get(a.get("house_type")), "mat_duong_chinh": a.get("is_main_street"),
    "dac_diem": ", ".join(CHAR.get(c, str(c)) for c in a.get("pty_characteristics", []) or []),
    "phap_ly": LEGAL.get(a.get("property_legal_document")), "noi_that": FURN.get(a.get("furnishing_sell")),
    "huong": a.get("direction"), "quan_huyen": a.get("area_name"), "phuong": a.get("ward_name"),
    "duong": a.get("street_name"), "lat": a.get("latitude"), "lon": a.get("longitude"), "dia_chi_ma_vi_tri": a.get("location_id"),
    "du_an": a.get("pty_project_name"), "moi_gioi": a.get("company_ad"), "gia_thay_doi": a.get("price_diff"),
} for a in ads]
if CAN_HO:      # thông tin riêng của căn hộ
    for r, a in zip(rows, ads):
        r.update({"dt_su_dung": a.get("size"), "dt_dat": None, "loai_can_ho": nhan("apartment_type", a.get("apartment_type")),
                  "tinh_trang_ban_giao": nhan("property_status", a.get("property_status")), "dac_diem_can_ho": nhan("apartment_feature", a.get("apartment_feature")),
                  "huong_ban_cong": nhan("balconydirection", a.get("balconydirection")), "tang_so": a.get("floornumber"), "block": a.get("block"),
                  "ma_du_an": a.get("projectid") or a.get("project_oid"), "huong": nhan("direction", a.get("direction"))})
if DAT:          # thông tin riêng của đất
    for r, a in zip(rows, ads):
        r.update({"loai_dat": nhan("land_type", a.get("land_type")), "so_tang": None, "phong_ngu": None, "so_wc": None, "dt_su_dung": None})
pd.DataFrame(rows).pipe(lambda d: an_danh_bang(d.astype(object).where(d.notna(), "").astype(str))[0]).to_csv(OUT_CSV, index=False, encoding="utf-8-sig")   # che SĐT mọi cột chữ
print("Đã lưu", len(rows), "tin ->", OUT_CSV)
