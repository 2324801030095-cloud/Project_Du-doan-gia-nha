"""Ẩn danh hóa dữ liệu đã thu thập: bỏ thông tin người đăng tin, che số điện thoại ở mọi cột/trường chữ.
Chạy từ thư mục gốc đề tài:  python cong_cu/an_danh_du_lieu.py
- JSONL Chợ Tốt: xóa các trường định danh người bán (tên, mã tài khoản, ảnh đại diện, seller_info...).
- Mọi CSV/JSONL trong data/ và ket_qua/: thay số điện thoại ở mọi cột chữ (kể cả địa chỉ, tên đường) bằng "[SĐT]".
Không đổi bất kỳ cột số liệu nào (giá, diện tích, tọa độ...), nên kết quả mô hình không phụ thuộc vào việc chạy script này.
Các script thu thập (thu_thap/) đã tự làm việc này cho dữ liệu tải mới.
"""
import glob, json, os, re, sys

TRUONG_NGUOI_BAN = {"account_id", "account_name", "account_oid", "avatar", "full_name", "seller_info", "facebook_id",
                    "shop_alias", "store_id", "contact_name", "phone", "phone_hidden"}
SDT = re.compile(r"(?<!\d)(?:\+?84|0)(?:[\s.\-]?\d){8,10}(?!\d)")


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


LA_SO = r"^-?\d+(?:\.\d+)?$"


def an_danh_bang(d):
    """Che số điện thoại ở mọi cột chữ của một bảng đọc bằng dtype=str. Trả về (bảng, số ô đã che).
    Ô mà bản thân là một con số (giá 840000000.0) thì không bao giờ che, kể cả khi cột lẫn chữ."""
    n = 0
    for c in cot_chu(d):
        m = d[c].str.contains(SDT, na=False) & ~d[c].str.match(LA_SO, na=False)
        n += int(m.sum())
        d.loc[m, c] = d.loc[m, c].map(che_sdt)
    return d, n


if __name__ == "__main__":
    import pandas as pd
    goc = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for f in glob.glob(os.path.join(goc, "data", "**", "*.jsonl"), recursive=True):
        dong = [dong_jsonl(an_danh_tin(json.loads(l))) for l in open(f, encoding="utf-8", newline="").read().split("\n") if l.strip()]
        open(f, "w", encoding="utf-8").write("\n".join(dong) + "\n")
        print("JSONL:", os.path.relpath(f, goc), len(dong), "tin")
    for f in glob.glob(os.path.join(goc, "data", "**", "*.csv"), recursive=True) + glob.glob(os.path.join(goc, "ket_qua", "*.csv")):
        d, n = an_danh_bang(pd.read_csv(f, dtype=str, keep_default_na=False))
        if n:
            d.to_csv(f, index=False, encoding="utf-8-sig")
            print("CSV :", os.path.relpath(f, goc), "che", n, "ô có số điện thoại")
    sys.exit(0)
