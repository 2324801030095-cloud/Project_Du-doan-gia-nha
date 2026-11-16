"""Ẩn danh hóa dữ liệu đã thu thập: bỏ thông tin người đăng tin, che số điện thoại trong tiêu đề / mô tả.
Chạy từ thư mục gốc đề tài:  python cong_cu/an_danh_du_lieu.py
- JSONL Chợ Tốt: xóa các trường định danh người bán (tên, mã tài khoản, ảnh đại diện, seller_info...).
- Mọi CSV/JSONL trong data/: thay số điện thoại trong văn bản bằng "[SĐT]".
Không đổi bất kỳ cột số liệu nào (giá, diện tích, tọa độ...), nên kết quả mô hình không phụ thuộc vào việc chạy script này.
Các script thu thập (thu_thap/) đã tự làm việc này cho dữ liệu tải mới.
"""
import glob, json, os, re, sys

TRUONG_NGUOI_BAN = {"account_id", "account_name", "account_oid", "avatar", "full_name", "seller_info", "facebook_id",
                    "shop_alias", "store_id", "contact_name", "phone", "phone_hidden"}
SDT = re.compile(r"(?<!\d)(?:\+?84|0)(?:[\s.\-]?\d){8,10}(?!\d)")
COT_CHU = ("mo_ta", "tieu_de", "body", "subject")


def che_sdt(s):
    return SDT.sub("[SĐT]", s) if isinstance(s, str) else s


def dong_jsonl(obj):
    """Một bản ghi JSONL an toàn: giữ tiếng Việt nguyên dạng nhưng thoát U+2028 / U+2029 (ký tự ngắt dòng Unicode
    có thể nằm trong mô tả tin). Không thoát thì công cụ tách dòng kiểu Unicode (str.splitlines, nhiều trình đọc JSONL)
    sẽ cắt đôi bản ghi."""
    return json.dumps(obj, ensure_ascii=False).replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")


def an_danh_tin(a):
    """Một tin Chợ Tốt (dict) -> bản không còn thông tin người đăng, số điện thoại bị che."""
    for k in TRUONG_NGUOI_BAN:
        a.pop(k, None)
    for k in ("body", "subject"):
        if k in a:
            a[k] = che_sdt(a[k])
    return a


if __name__ == "__main__":
    import pandas as pd
    goc = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for f in glob.glob(os.path.join(goc, "data", "**", "*.jsonl"), recursive=True):
        dong = [dong_jsonl(an_danh_tin(json.loads(l))) for l in open(f, encoding="utf-8", newline="").read().split("\n") if l.strip()]
        open(f, "w", encoding="utf-8").write("\n".join(dong) + "\n")
        print("JSONL:", os.path.relpath(f, goc), len(dong), "tin")
    for f in glob.glob(os.path.join(goc, "data", "**", "*.csv"), recursive=True) + glob.glob(os.path.join(goc, "ket_qua", "*.csv")):
        d = pd.read_csv(f, dtype=str, keep_default_na=False)
        cot = [c for c in d.columns if c in COT_CHU]
        n = sum(int(d[c].str.contains(SDT).sum()) for c in cot)
        if n:
            for c in cot:
                d[c] = d[c].map(che_sdt)
            d.to_csv(f, index=False, encoding="utf-8-sig")
            print("CSV :", os.path.relpath(f, goc), "che", n, "ô có số điện thoại")
    sys.exit(0)
