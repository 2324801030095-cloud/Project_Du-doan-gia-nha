"""Ghi lại bảng "Kết quả chính" trong README.md từ model/danh_gia_mo_hinh*.json (kết quả notebook vừa chạy).
Chạy từ thư mục gốc đề tài: python cong_cu/cap_nhat_readme.py   (cong_cu/chay_toan_bo.py tự gọi sau khi chạy notebook)."""
import json, pathlib

GOC = pathlib.Path(__file__).resolve().parent.parent
vn = lambda x, d=1: f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")
J = lambda f: json.loads((GOC / "model" / f"{f}.json").read_text(encoding="utf-8"))
dong = lambda d, k, ten: next(r for r in d[k] if r["Mô hình"] == ten)
baseline = lambda d, k: next(r for r in d[k] if r["Mô hình"].startswith("Baseline"))

N, C, D = J("danh_gia_mo_hinh"), J("danh_gia_mo_hinh_can_ho"), J("danh_gia_mo_hinh_dat")
n, c, dd = N["ten_mo_hinh"], C["ten_mo_hinh"], D["ten_mo_hinh"]
tn, tc, td = dong(N, "test_phu_hoa", n), dong(C, "test", c), dong(D, "test_tdm", dd)
BANG = f"""| | Nhà phố – Phú Hòa | Căn hộ | Đất nền – TDM |
|---|---|---|---|
| Mô hình | {n} | {c} | {dd} |
| MAPE tập test (kết quả chính) | {vn(tn['MAPE (%)'])}% (KTC {vn(tn['MAPE thấp (95%)'])}–{vn(tn['MAPE cao (95%)'])}; {int(tn['Số căn'])} căn) | {vn(tc['MAPE (%)'])}% | {vn(td['MAPE (%)'])}% (KTC {vn(td['MAPE thấp (95%)'])}–{vn(td['MAPE cao (95%)'])}; {int(td['Số căn'])} lô) |
| MAPE kiểm định chéo theo nhóm | {vn(dong(N, 'kiem_dinh_cheo_phu_hoa', n)['MAPE (%)'])}% | {vn(dong(C, 'kiem_dinh_cheo', c)['MAPE (%)'])}% | {vn(dong(D, 'kiem_dinh_cheo_tdm', dd)['MAPE (%)'])}% |
| Baseline (đơn giá khu vực), kiểm định chéo | {vn(baseline(N, 'kiem_dinh_cheo_phu_hoa')['MAPE (%)'])}% | {vn(baseline(C, 'kiem_dinh_cheo')['MAPE (%)'])}% | {vn(baseline(D, 'kiem_dinh_cheo_tdm')['MAPE (%)'])}% |"""

if __name__ == "__main__":
    p = GOC / "README.md"
    s = p.read_text(encoding="utf-8")
    i = s.index("| | Nhà phố – Phú Hòa | Căn hộ | Đất nền – TDM |")
    j = s.index("\n", s.index("| Baseline (đơn giá khu vực)", i))
    p.write_text(s[:i] + BANG + s[j:], encoding="utf-8")
    print("Đã cập nhật bảng kết quả trong README.md")
