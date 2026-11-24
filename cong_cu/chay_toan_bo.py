"""Chạy lại toàn bộ đề tài ĐÚNG THỨ TỰ (~30 phút), dừng ngay ở bước lỗi đầu tiên.
Chạy từ thư mục gốc đề tài:
    python cong_cu/chay_toan_bo.py               # notebook -> dựng trang -> kiểm thử
    python cong_cu/chay_toan_bo.py --thu-thap    # thu thập dữ liệu mới trước
    python cong_cu/chay_toan_bo.py --tu <tên>    # chạy tiếp từ một bước, ví dụ --tu du_doan_gia_thue
    python cong_cu/chay_toan_bo.py --xu-huong    # chỉ notebook xu hướng + dựng lại trang (dùng sau mỗi kỳ thu thập)
Vì sao thứ tự này:
- giá thuê ghi thêm 2 cột vào data/processed/{nha,can_ho}_da_xu_ly.csv -> phải chạy SAU nhà phố và căn hộ;
- đất dùng tọa độ tuyến đường của nhà phố -> sau nhà phố;
- notebook trợ lý chạy luật của trang qua Node -> cần trang đã dựng; xong thì dựng lại trang để nhúng mô hình trợ lý."""
import pathlib, shutil, subprocess, sys, time

GOC = pathlib.Path(__file__).resolve().parent.parent
PY = sys.executable
nb = lambda ten: [PY, "-m", "jupyter", "nbconvert", "--to", "notebook", "--execute", "--inplace",
                  "--ExecutePreprocessor.timeout=3600", f"notebooks/{ten}.ipynb"]
TRANG = [PY, "-X", "utf8", "demo/_build/build_site.py"]
BUOC = [
    ("2324801030095", nb("2324801030095")),
    ("du_doan_gia_can_ho", nb("du_doan_gia_can_ho")),
    ("du_doan_gia_thue", nb("du_doan_gia_thue")),
    ("du_doan_gia_dat", nb("du_doan_gia_dat")),
    ("du_doan_xu_huong_gia", nb("du_doan_xu_huong_gia")),
    ("build_site", TRANG),
    ("tro_ly_y_dinh", nb("tro_ly_y_dinh")),
    ("build_site_lan_2", TRANG),
    ("kiem_tra_mo_hinh", [PY, "-X", "utf8", "tests/kiem_tra_mo_hinh.py"]),
    ("kiem_tra_tro_ly", ["node", "tests/kiem_tra_tro_ly.js"]),
]


def chay(buoc):
    for ten, lenh in buoc:
        t = time.time()
        print(f"== {ten} ...", flush=True)
        if subprocess.run(lenh, cwd=GOC).returncode != 0:
            sys.exit(f"DỪNG: bước '{ten}' lỗi. Sửa xong chạy tiếp bằng: python cong_cu/chay_toan_bo.py --tu {ten}")
        print(f"   xong ({time.time() - t:.0f} giây)", flush=True)


if __name__ == "__main__":
    if not shutil.which("node"):
        sys.exit("Cần Node.js >= 18 (notebook trợ lý và kiểm thử trang dùng Node).")
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
        subprocess.run([PY, "-X", "utf8", "thu_thap/cap_nhat_dinh_ky.py"], cwd=GOC)   # nguồn lỗi thì vẫn chạy tiếp với dữ liệu cũ
    chay(buoc)
    print("HOÀN TẤT: mọi notebook, trang demo và kiểm thử đã chạy lại.")
