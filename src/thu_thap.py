"""Thu thập dữ liệu (dataset/raw) và ẩn danh hóa – mọi nguồn tự động trong một file.

Cách dùng (từ thư mục gốc đề tài):
    python src/thu_thap.py chotot [--can-ho | --dat] [--flatten-only]   Chợ Tốt Nhà (API công khai gateway.chotot.com)
    python src/thu_thap.py alonhadat [--can-ho | --dat]                  alonhadat.com.vn (trang danh sách, TP. Thủ Dầu Một)
    python src/thu_thap.py an-danh                                       ẩn danh lại toàn bộ dataset/ và results/
Không tham số loại = nhà ở; --can-ho = căn hộ chung cư; --dat = đất. guland chặn trình duyệt tự động nên thu tay
bằng scripts/guland_thu_thap.js.

Chợ Tốt: mỗi tin có giá, diện tích, ngang, dài, số tầng, phòng, WC, loại nhà, mặt tiền/hẻm, pháp lý, nội thất,
phường, đường, TỌA ĐỘ, ngày đăng gốc (căn hộ thêm dự án, loại căn, tầng, block, bàn giao). Nghỉ 1 giây giữa các lần gọi.
alonhadat: chỉ đọc thẻ tin trên trang danh sách (giá, diện tích, kích thước, số tầng, phòng ngủ, đường trước nhà,
địa chỉ cũ kèm phường, ngày đăng). Nghỉ 3 giây giữa các trang.
Riêng tư: không lưu thông tin người đăng (tên, mã tài khoản, ảnh đại diện…); số điện thoại ở mọi cột chữ bị thay bằng
"[SĐT]". Không đổi cột số liệu nào (giá, diện tích, tọa độ…), nên kết quả mô hình không phụ thuộc bước ẩn danh.
Tải lỗi giữa chừng thì KHÔNG ghi đè dữ liệu cũ (thoát mã 2)."""
import collections
import datetime as dt
import glob
import html
import json
import os
import pathlib
import re
import sys
import time
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW = ROOT / "dataset" / "raw"
UA = {"User-Agent": "Mozilla/5.0"}

# ------------------------------------------------------------------ ẩn danh
TRUONG_NGUOI_BAN = {"account_id", "account_name", "account_oid", "avatar", "full_name", "seller_info", "facebook_id",
                    "shop_alias", "store_id", "contact_name", "phone", "phone_hidden"}
SDT = re.compile(r"(?<!\d)(?:\+?84|0)(?:[\s.\-]?\d){8,10}(?!\d)")
LA_SO = r"^-?\d+(?:\.\d+)?$"


def che_sdt(s):
    return SDT.sub("[SĐT]", s) if isinstance(s, str) else s


def dong_jsonl(obj):
    """Một bản ghi JSONL an toàn: giữ tiếng Việt nguyên dạng nhưng thoát U+2028 / U+2029 (ký tự ngắt dòng Unicode
    có thể nằm trong mô tả tin). Không thoát thì công cụ tách dòng kiểu Unicode (str.splitlines, nhiều trình đọc JSONL)
    sẽ cắt đôi bản ghi."""
    return json.dumps(obj, ensure_ascii=False).replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")


def _che_moi_chuoi(x, khoa=""):
    # che số điện thoại ở MỌI trường chữ (người đăng hay ghi số vào cả ô địa chỉ, tên đường), trừ đường dẫn
    # và mã định danh (unique_street_id là chuỗi hex, videos[].id là số dài: trông giống SĐT nhưng không phải)
    if isinstance(x, dict):
        return {k: _che_moi_chuoi(v, k) for k, v in x.items()}
    if isinstance(x, list):
        return [_che_moi_chuoi(v, khoa) for v in x]
    la_ma = khoa in ("id", "oid") or khoa.endswith(("_id", "_oid", "id_"))
    if isinstance(x, str) and not (la_ma or "url" in khoa or "image" in khoa or x.startswith("http")):
        return che_sdt(x)
    return x


def an_danh_tin(a):
    """Một tin Chợ Tốt (dict) -> bản không còn thông tin người đăng, số điện thoại bị che ở mọi trường chữ."""
    for k in TRUONG_NGUOI_BAN:
        a.pop(k, None)
    return _che_moi_chuoi(a)


def cot_chu(d):
    """Các cột chữ của bảng (đọc dtype=str): bỏ cột URL và cột mà mọi ô không rỗng đều là số
    (giá 840000000 trông giống số điện thoại nhưng không phải)."""
    import pandas as pd
    so = lambda s: pd.to_numeric(s[s != ""], errors="coerce").notna().all()
    return [c for c in d.columns if "url" not in c and not so(d[c])]


def an_danh_bang(d):
    """Che số điện thoại ở mọi cột chữ của một bảng đọc bằng dtype=str. Trả về (bảng, số ô đã che).
    Ô mà bản thân là một con số (giá 840000000.0) thì không bao giờ che, kể cả khi cột lẫn chữ."""
    n = 0
    for c in cot_chu(d):
        m = d[c].str.contains(SDT, na=False) & ~d[c].str.match(LA_SO, na=False)
        n += int(m.sum())
        d.loc[m, c] = d.loc[m, c].map(che_sdt)
    return d, n


def an_danh_toan_bo():
    """Ẩn danh lại mọi JSONL/CSV trong dataset/ và results/ (dữ liệu tải mới đã tự được ẩn danh)."""
    import pandas as pd
    for f in glob.glob(str(ROOT / "dataset" / "**" / "*.jsonl"), recursive=True):
        dong = [dong_jsonl(an_danh_tin(json.loads(l))) for l in open(f, encoding="utf-8", newline="").read().split("\n") if l.strip()]
        open(f, "w", encoding="utf-8").write("\n".join(dong) + "\n")
        print("JSONL:", os.path.relpath(f, ROOT), len(dong), "tin")
    for f in glob.glob(str(ROOT / "dataset" / "**" / "*.csv"), recursive=True) + glob.glob(str(ROOT / "results" / "*.csv")):
        d, n = an_danh_bang(pd.read_csv(f, dtype=str, keep_default_na=False))
        if n:
            d.to_csv(f, index=False, encoding="utf-8-sig")
            print("CSV :", os.path.relpath(f, ROOT), "che", n, "ô có số điện thoại")


def _bang_an_danh(rows_or_df):
    import pandas as pd
    d = pd.DataFrame(rows_or_df)
    return an_danh_bang(d.astype(object).where(d.notna(), "").astype(str))[0]       # che SĐT ở mọi cột chữ (kể cả địa chỉ)


# ------------------------------------------------------------------ Chợ Tốt
def chotot(loai="nha", chi_dung_lai_csv=False):
    """loai: 'nha' (cg=1020), 'can_ho' (cg=1010), 'dat' (cg=1040); khu vực Bình Dương cũ (region_v2=2011)."""
    ten = {"nha": "chotot_binh_duong_raw", "can_ho": "chotot_can_ho_raw", "dat": "chotot_dat_raw"}[loai]
    out_jsonl, out_csv = RAW / f"{ten}.jsonl", RAW / f"{ten}.csv"
    api = ("https://gateway.chotot.com/v1/public/ad-listing?cg=" + {"nha": "1020", "can_ho": "1010", "dat": "1040"}[loai]
           + "&region_v2=2011&limit=50&o={o}&key_param_included=true")

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
    if chi_dung_lai_csv:                  # chỉ dựng lại CSV từ JSONL đã tải
        ads = [json.loads(l) for l in open(out_jsonl, encoding="utf-8") if l.strip()]
    while not chi_dung_lai_csv:           # tải mọi trang cho tới khi hết tin
        d = get(api.format(o=o))
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

    ads = [an_danh_tin(a) for a in ads]
    ngay = ads[0].get("_ngay_thu_thap") or dt.date.today().isoformat()
    if not chi_dung_lai_csv:
        with open(out_jsonl, "w", encoding="utf-8") as f:
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
    if loai == "can_ho":      # thông tin riêng của căn hộ
        for r, a in zip(rows, ads):
            r.update({"dt_su_dung": a.get("size"), "dt_dat": None, "loai_can_ho": nhan("apartment_type", a.get("apartment_type")),
                      "tinh_trang_ban_giao": nhan("property_status", a.get("property_status")), "dac_diem_can_ho": nhan("apartment_feature", a.get("apartment_feature")),
                      "huong_ban_cong": nhan("balconydirection", a.get("balconydirection")), "tang_so": a.get("floornumber"), "block": a.get("block"),
                      "ma_du_an": a.get("projectid") or a.get("project_oid"), "huong": nhan("direction", a.get("direction"))})
    if loai == "dat":          # thông tin riêng của đất
        for r, a in zip(rows, ads):
            r.update({"loai_dat": nhan("land_type", a.get("land_type")), "so_tang": None, "phong_ngu": None, "so_wc": None, "dt_su_dung": None})
    _bang_an_danh(rows).to_csv(out_csv, index=False, encoding="utf-8-sig")
    print("Đã lưu", len(rows), "tin ->", out_csv)


# ------------------------------------------------------------------ alonhadat
def alonhadat(loai="nha"):
    """loai: 'nha' (mặt tiền, hẻm, biệt thự/liền kề), 'can_ho', 'dat' (thổ cư, đất nền dự án); TP. Thủ Dầu Một."""
    out = RAW / {"nha": "alonhadat_tdm_raw.csv", "can_ho": "alonhadat_can_ho_tdm_raw.csv", "dat": "alonhadat_dat_tdm_raw.csv"}[loai]
    base = "https://alonhadat.com.vn/nha-dat/can-ban/{loai}/binh-duong/591/thanh-pho-thu-dau-mot{trang}.html"
    cac_loai = {"nha": ["nha-mat-tien", "nha-trong-hem", "biet-thu-nha-lien-ke"], "can_ho": ["can-ho-chung-cu"],
                "dat": ["dat-tho-cu-dat-o", "dat-nen-lien-ke-dat-du-an"]}[loai]
    loi_tai = []          # có trang nào tải thất bại hẳn không -> nếu có thì KHÔNG ghi đè dữ liệu cũ

    def get(url):
        for k in range(5):
            try:
                with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                    return r.read().decode("utf-8", "replace")
            except Exception as e:
                cho = (30 * 2 ** k) if "429" in str(e) else 5 * (k + 1)      # bị chặn tạm (429): chờ lâu dần 30s, 60s, 120s...
                print("retry", k, e, f"- chờ {cho}s", flush=True); time.sleep(cho)
        loi_tai.append(url)
        return ""

    def txt(pat, s, default=None):
        m = re.search(pat, s, re.DOTALL)
        return html.unescape(re.sub(r"<[^>]+>", " ", m.group(1))).strip() if m else default

    rows, seen = [], set()
    for l in cac_loai:
        for p in range(1, 60):
            s = get(base.format(loai=l, trang="" if p == 1 else f"/trang--{p}"))
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
                    "id": int(m.group(1)), "url": "https://alonhadat.com.vn" + href, "loai_nha": l,
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
            print(l, "trang", p, "+", new, "tổng", len(rows), flush=True)
            if not cards or new == 0:
                break
            time.sleep(3)

    if loi_tai or not rows:
        # Không ghi đè: dữ liệu cũ đầy đủ vẫn tốt hơn dữ liệu mới bị thiếu trang
        print(f"CẢNH BÁO: tải không trọn vẹn ({len(rows)} tin) - giữ nguyên {out.name} cũ, không ghi đè.", flush=True)
        sys.exit(2)
    import pandas as pd
    df = pd.DataFrame(rows)
    df["ngay_thu_thap"] = dt.date.today().isoformat()
    df["dia_chi_moi"] = df["dia_chi_moi"].str.replace(r"\s+", " ", regex=True)
    _bang_an_danh(df).to_csv(out, index=False, encoding="utf-8-sig")
    print("Đã lưu", len(df), "tin ->", out)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # in được tiếng Việt trên mọi console Windows
    lenh = sys.argv[1] if len(sys.argv) > 1 else ""
    loai = "can_ho" if "--can-ho" in sys.argv else "dat" if "--dat" in sys.argv else "nha"
    if lenh == "chotot":
        chotot(loai, chi_dung_lai_csv="--flatten-only" in sys.argv)
    elif lenh == "alonhadat":
        alonhadat(loai)
    elif lenh == "an-danh":
        an_danh_toan_bo()
    else:
        sys.exit(__doc__)
