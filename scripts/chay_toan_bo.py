"""Chạy lại toàn bộ đề tài ĐÚNG THỨ TỰ (~8 phút; notebook nhà phố ~5 phút), dừng ngay ở bước lỗi đầu tiên.
Chạy từ thư mục gốc đề tài:
    python scripts/chay_toan_bo.py               # sinh + chạy notebook -> dựng trang -> cập nhật README -> kiểm thử
    python scripts/chay_toan_bo.py --thu-thap    # thu thập dữ liệu mới trước
    python scripts/chay_toan_bo.py --tu <tên>    # chạy tiếp từ một bước, ví dụ --tu du_doan_gia_thue
    python scripts/chay_toan_bo.py --xu-huong    # chỉ notebook xu hướng + dựng lại trang (dùng sau mỗi kỳ thu thập)
    python scripts/chay_toan_bo.py --nha-pho     # chỉ bài chính: notebook nhà phố -> dữ liệu cho API -> README -> kiểm thử
                                                 # (chỉ cần dữ liệu nhà ở; không dựng trang HTML tĩnh demo/)
    python scripts/chay_toan_bo.py --readme      # chỉ ghi lại bảng "Kết quả chính" của README từ models/*.json
Vì sao thứ tự này:
- giá thuê ghi thêm 2 cột vào dataset/processed/{nha,can_ho}_da_xu_ly.csv -> phải chạy SAU nhà phố và căn hộ;
- đất dùng tọa độ tuyến đường của nhà phố -> sau nhà phố;
- notebook trợ lý chạy luật của trang qua Node -> cần trang đã dựng; xong thì dựng lại trang để nhúng mô hình trợ lý.
Mỗi notebook được SINH LẠI từ scripts/sinh_notebook/<tên>.py trước khi chạy (sửa notebook ở đó, không sửa .ipynb)."""
import json
import pathlib
import re
import shutil
import subprocess
import sys
import time

GOC = pathlib.Path(__file__).resolve().parent.parent
PY = sys.executable
nb = lambda ten: [PY, "-m", "jupyter", "nbconvert", "--to", "notebook", "--execute", "--inplace",
                  "--ExecutePreprocessor.timeout=3600", f"notebooks/{ten}.ipynb"]
TRANG = [PY, "-X", "utf8", "demo/build/build_site.py"]                      # dữ liệu web + trang HTML tĩnh (cần đủ phần mở rộng)
DU_LIEU_WEB = [PY, "-X", "utf8", "demo/build/build_site.py", "--chi-du-lieu"]  # chỉ models/du_lieu_web.json cho API (đủ với bài chính)
BUOC = [
    ("2324801030095", nb("2324801030095")),
    ("du_doan_gia_can_ho", nb("du_doan_gia_can_ho")),
    ("du_doan_gia_thue", nb("du_doan_gia_thue")),
    ("du_doan_xu_huong_gia", nb("du_doan_xu_huong_gia")),
    ("build_site", TRANG),
    ("tro_ly_y_dinh", nb("tro_ly_y_dinh")),
    ("build_site_lan_2", TRANG),
    ("xuat_du_lieu_web", DU_LIEU_WEB),
    ("cap_nhat_readme", [PY, "-X", "utf8", "scripts/chay_toan_bo.py", "--readme"]),     # bảng kết quả README lấy từ models/*.json
    ("kiem_tra_mo_hinh", [PY, "-X", "utf8", "tests/kiem_tra_mo_hinh.py"]),
    ("kiem_tra_api", [PY, "-X", "utf8", "tests/kiem_tra_api.py"]),
    ("kiem_tra_tro_ly", ["node", "tests/kiem_tra_tro_ly.js"]),
]
# notebook -> file sinh ra nó trong scripts/sinh_notebook/
SINH = {"2324801030095": "chinh", "du_doan_gia_can_ho": "can_ho", "du_doan_gia_thue": "gia_thue",
        "du_doan_xu_huong_gia": "xu_huong", "tro_ly_y_dinh": "tro_ly"}


def chay(buoc):
    for ten, lenh in buoc:
        t = time.time()
        print(f"== {ten} ...", flush=True)
        if ten in SINH and subprocess.run([PY, "-X", "utf8", f"scripts/sinh_notebook/{SINH[ten]}.py", f"notebooks/{ten}.ipynb"], cwd=GOC).returncode != 0:
            sys.exit(f"DỪNG: không sinh được notebook '{ten}' từ scripts/sinh_notebook/{SINH[ten]}.py")
        if subprocess.run(lenh, cwd=GOC).returncode != 0:
            sys.exit(f"DỪNG: bước '{ten}' lỗi. Sửa xong chạy tiếp bằng: python scripts/chay_toan_bo.py --tu {ten}")
        print(f"   xong ({time.time() - t:.0f} giây)", flush=True)


def kiem_api_dang_chay(url="http://127.0.0.1:8000/health"):
    """Nếu API mô hình đang chạy (docker compose): kiểm chứng nó ĐANG phục vụ đúng mô hình / dữ liệu vừa sinh.
    API tự nạp lại khi file đổi (bộ nhớ đệm theo thời điểm sửa file); /health trả mã băm của file đang dùng để so với file trên đĩa."""
    import hashlib
    import urllib.request
    try:
        pb = json.loads(urllib.request.urlopen(url, timeout=10).read())["phien_ban"]
    except Exception as e:
        print(f"(API mô hình không chạy hoặc chưa có /health phiên bản: {type(e).__name__}) – bỏ qua bước kiểm chứng phiên bản")
        return
    tren_dia = {t: hashlib.sha256((GOC / "models" / t).read_bytes()).hexdigest()[:12] for t in pb}
    lech = {t: (pb[t], tren_dia[t]) for t in pb if pb[t] != tren_dia[t]}
    if lech:
        sys.exit(f"DỪNG: API đang phục vụ bản cũ {lech} (API / trên đĩa). Kiểm tra volume models/ trong docker-compose.yml")
    print("API mô hình đang phục vụ đúng bản vừa sinh:", tren_dia)


def cap_nhat_readme():
    """Ghi lại bảng "Kết quả chính" trong README.md từ models/danh_gia_mo_hinh*.json (kết quả notebook vừa chạy)."""
    vn = lambda x, d=1: f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    J = lambda f: json.loads((GOC / "models" / f"{f}.json").read_text(encoding="utf-8"))
    dong = lambda d, k, ten: next(r for r in d[k] if r["Mô hình"] == ten)
    baseline = lambda d, k: next(r for r in d[k] if r["Mô hình"].startswith("Baseline"))
    pa = lambda d, k: next((f"{r['Mô hình'].removeprefix('Phần A – ')}: {vn(r['MAPE (%)'])}%" for r in d[k] if r["Mô hình"].startswith("Phần A")), "chính là mô hình cuối")
    N, C = J("danh_gia_mo_hinh"), J("danh_gia_mo_hinh_can_ho")
    n, c = N["ten_mo_hinh"], C["ten_mo_hinh"]
    tn, tc = dong(N, "test_phu_hoa", n), dong(C, "test", c)
    bn, bc = baseline(N, "test_phu_hoa"), baseline(C, "test")
    phu = N.get("do_phu_test_80", {}).get("test Phú Hòa")
    phu_s = f"{phu['trong']}/{phu['tong']} căn ({vn(phu['trong'] / phu['tong'] * 100, 0)}%)" if phu else "–"
    # Mô hình và mốc so sánh đặt trên CÙNG một tập test (không đặt số kiểm định chéo cạnh số test)
    bang = f"""| | Nhà phố – Phú Hòa (bài chính) | Căn hộ (mở rộng) |
|---|---|---|
| Mô hình | {n} | {c} |
| Tập test giữ riêng | {int(tn['Số căn'])} căn | {int(tc['Số căn'])} căn |
| MAPE mô hình trên test | {vn(tn['MAPE (%)'])}% (KTC 95% {vn(tn['MAPE thấp (95%)'])}–{vn(tn['MAPE cao (95%)'])}) | {vn(tc['MAPE (%)'])}% |
| MAE mô hình trên test | {vn(tn['MAE (tỷ)'], 2)} tỷ đồng | {vn(tc['MAE (tỷ)'], 2)} tỷ đồng |
| Mốc so sánh trên cùng tập test | {bn['Mô hình']}: MAPE {vn(bn['MAPE (%)'])}%, MAE {vn(bn['MAE (tỷ)'], 2)} tỷ | {bc['Mô hình']}: MAPE {vn(bc['MAPE (%)'])}%, MAE {vn(bc['MAE (tỷ)'], 2)} tỷ |
| Kiểm định chéo trên tập train (mô hình / mốc) | {vn(dong(N, 'kiem_dinh_cheo_phu_hoa', n)['MAPE (%)'])}% / {vn(baseline(N, 'kiem_dinh_cheo_phu_hoa')['MAPE (%)'])}% | {vn(dong(C, 'kiem_dinh_cheo', c)['MAPE (%)'])}% / {vn(baseline(C, 'kiem_dinh_cheo')['MAPE (%)'])}% |
| Khoảng giá 80%: độ phủ đo trên test | {phu_s} | – |"""
    p = GOC / "README.md"
    s = p.read_text(encoding="utf-8")
    i = s.index("| | Nhà phố – Phú Hòa")
    cuoi = "| Khoảng giá 80%" if "| Khoảng giá 80%" in s[i:i + 4000] else "| Phần A (mô hình môn học"
    j = s.index("\n", s.index(cuoi, i))
    s = s[:i] + bang + s[j:]
    ngay = J("du_lieu_web")["SO_LIEU"]["NGAY"]          # ngày của kỳ thu thập mới nhất (dd/mm/yyyy)
    s = re.sub(r"## Kết quả chính \(dữ liệu [^)]*\)", f"## Kết quả chính (dữ liệu đến {ngay})", s)
    p.write_text(s, encoding="utf-8")
    print("Đã cập nhật bảng kết quả trong README.md")


if __name__ == "__main__":
    if "--readme" in sys.argv:
        cap_nhat_readme()
        sys.exit(0)
    if not shutil.which("node"):
        sys.exit("Cần Node.js >= 18 (notebook trợ lý và kiểm thử trang dùng Node).")
    if "--nha-pho" in sys.argv:          # chỉ luồng bài chính: notebook nhà phố -> dữ liệu web/API -> README -> kiểm thử
        # Chỉ cần đầu vào / đầu ra của bài chính: không dựng trang HTML tĩnh (cần kết quả căn hộ, xu hướng...).
        chay([b for b in BUOC if b[0] in ("2324801030095", "xuat_du_lieu_web", "cap_nhat_readme", "kiem_tra_mo_hinh", "kiem_tra_api")])
        kiem_api_dang_chay()
        sys.exit(0)
    if "--xu-huong" in sys.argv:
        chay([b for b in BUOC if b[0] in ("du_doan_xu_huong_gia", "build_site_lan_2")])
        sys.exit(0)
    buoc = BUOC
    if "--tu" in sys.argv:
        ten = sys.argv[sys.argv.index("--tu") + 1]
        ten_cac_buoc = [b[0] for b in BUOC]
        assert ten in ten_cac_buoc, f"không có bước '{ten}'; các bước: {ten_cac_buoc}"
        buoc = BUOC[ten_cac_buoc.index(ten):]
    if "--thu-thap" in sys.argv:
        subprocess.run([PY, "-X", "utf8", "scripts/cap_nhat_dinh_ky.py", "--khong-chay-lai"], cwd=GOC)   # nguồn lỗi thì vẫn chạy tiếp với dữ liệu cũ
    chay(buoc)
    kiem_api_dang_chay()
    print("HOÀN TẤT: mọi notebook, trang demo và kiểm thử đã chạy lại.")
