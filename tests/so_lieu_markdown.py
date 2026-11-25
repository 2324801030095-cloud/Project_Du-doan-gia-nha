"""Markdown của notebook không được chứa số KẾT QUẢ viết tay.
Số kết quả (MAPE, độ phủ, số căn...) phải được in ra từ biến trong ô code (hàm nx), nên khi dữ liệu cập nhật thì chữ tự đúng.
Trong ô markdown, các số sau bị coi là số kết quả viết tay:
  1. số có phần thập phân (23,9) hoặc có dấu % (26,5% / 80%) mà KHÔNG phải một giá trị cố định trong mã nguồn
     (ngưỡng lọc, tham số, mức 80% của khoảng giá...), tức mã của notebook hoặc src/mo_hinh_gia.py;
  2. số đếm có đơn vị (N căn / tin / lô / dự án / cặp / nhóm) không phải giá trị cố định trong mã;
  3. mọi số ước chừng: đứng sau "~", "≈" hoặc "khoảng" (trừ mức 80% / 95% của khoảng giá và khoảng tin cậy).
Giới hạn còn lại: một số kết quả trùng đúng một hằng số trong mã (ví dụ 0,6 trùng tham số 0.6) mà không đứng sau "khoảng/~/≈"
thì không phân biệt được; các nhận xét có số đã được chuyển sang nx nên trường hợp này chỉ còn ở các ngưỡng thật sự cố định.
Dùng: python tests/so_lieu_markdown.py notebooks/2324801030095.ipynb   -> in các số kết quả còn viết tay."""
import json, re, sys
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
DON_VI = r"căn|tin|lô|dự án|cặp|nhóm"
MUC_CO_DINH = {80.0, 95.0}          # mức của khoảng giá 80% và khoảng tin cậy 95%


def _so(chuoi):
    return {float(x) for x in re.findall(r"\d+(?:\.\d+)?", chuoi)}


def kiem(duong_dan):
    nb = json.load(open(duong_dan, encoding="utf-8"))
    ma = "\n".join("".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code")
    ma += (GOC / "src" / "mo_hinh_gia.py").read_text(encoding="utf-8")
    co_dinh = _so(ma)
    co_dinh |= {round(x * 100, 6) for x in co_dinh if x <= 1}          # 0.8 trong mã <-> "80%" trong chữ
    sai = []
    for i, c in enumerate(nb["cells"]):
        if c["cell_type"] != "markdown":
            continue
        md = "".join(c["source"])
        for m in re.finditer(rf"(?<![\w.,])(\d+(?:[.,]\d+)*)(\s*%|\s+(?:{DON_VI})\b)?", md):
            so, duoi = m.group(1), m.group(2) or ""
            if "." in so and not re.fullmatch(r"\d{1,3}(\.\d{3})+", so):
                continue                      # số mục (4.4, 5.1), không phải số liệu
            x =float(so.replace(".", "").replace(",", ".")) if re.fullmatch(r"\d{1,3}(\.\d{3})+", so) else float(so.replace(",", "."))
            truoc = md[max(0, m.start() - 8):m.start()]
            uoc_chung = re.search(r"(~|≈|khoảng)\s*$", truoc) and x not in MUC_CO_DINH
            if not uoc_chung:
                if "," not in so and "." not in so and not duoi:
                    continue                  # số nguyên trơn (số bước, số kỳ, năm, tên lớp...) không kiểm
                if x in co_dinh:
                    continue
            sai.append((i, md[max(0, m.start() - 60):m.end() + 20].replace("\n", " ")))
    return sai


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    s = kiem(sys.argv[1])
    for i, t in s:
        print(f"ô {i}: …{t}…")
    print(len(s), "số kết quả viết tay trong markdown")
