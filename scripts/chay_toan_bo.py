"""Chạy lại đề tài ĐÚNG THỨ TỰ, dừng ngay ở bước lỗi đầu tiên. Chạy từ thư mục gốc đề tài:
    python scripts/chay_toan_bo.py                     # đầy đủ (~9 phút): mọi notebook -> trang HTML tĩnh -> README -> kiểm thử đầy đủ -> công bố
    python scripts/chay_toan_bo.py --nha-pho           # chỉ bài chính (~6 phút), chỉ cần dữ liệu nhà ở:
                                                       #   notebook nhà phố -> dữ liệu cho API -> README -> kiểm thử nhà phố -> công bố
    python scripts/chay_toan_bo.py [--nha-pho] --tu <bước>   # chạy tiếp từ một bước của chế độ đó (in danh sách bước nếu sai tên)
    python scripts/chay_toan_bo.py [--nha-pho] --thu-thap    # thu thập trước (với --nha-pho: chỉ nguồn nhà ở)
    python scripts/chay_toan_bo.py --xu-huong          # chỉ notebook xu hướng + dựng lại trang -> kiểm thử -> công bố
                                                       #   (không dùng chung với --nha-pho, --tu, --thu-thap: bị từ chối trước khi chạy)
    python scripts/chay_toan_bo.py --readme            # chỉ ghi lại bảng "Kết quả chính" của README từ models/*.json
CÔNG BỐ LÀ BƯỚC CUỐI: API chỉ chuyển sang bộ tệp mới sau khi MỌI bộ kiểm thử của chế độ đó đạt (kiểm thử chạy trên tệp làm
việc = bộ ỨNG VIÊN). Một bộ kiểm thử lỗi -> dừng trước công bố: bản kê không đổi, API tiếp tục phục vụ bộ cũ. --tu <bước> bỏ qua
bước kiểm thử nào thì bước công bố vẫn chạy lại đủ kiểm thử trước khi công bố. Bước công bố còn tự nạp thử bộ (như API) và từ chối bộ hỏng.
Sau khi chạy: nếu API mô hình đang chạy (PHH_API_URL, mặc định http://127.0.0.1:8000) thì kiểm chứng nó phục vụ đúng bộ tệp
vừa công bố (so mã bộ với models/phien_ban.json) và định giá thật một căn. API tắt -> bỏ qua có ghi rõ; API lỗi / lệch -> DỪNG.
Vì sao thứ tự này:
- giá thuê ghi thêm 2 cột vào dataset/processed/{nha,can_ho}_da_xu_ly.csv -> phải chạy SAU nhà phố và căn hộ;
- notebook trợ lý chạy luật của trang qua Node -> cần trang đã dựng; xong thì dựng lại trang để nhúng mô hình trợ lý.
Mỗi notebook được SINH LẠI từ scripts/sinh_notebook/<tên>.py trước khi chạy (sửa notebook ở đó, không sửa .ipynb)."""
import json
import os
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
CONG_BO = [PY, "-X", "utf8", "api/dinh_gia.py", "--cong-bo"]               # ghi models/phien_ban.json SAU khi mọi kiểm thử đạt
README = [PY, "-X", "utf8", "scripts/chay_toan_bo.py", "--readme"]          # bảng kết quả README lấy từ models/*.json
BUOC = [
    ("2324801030095", nb("2324801030095")),
    ("du_doan_gia_can_ho", nb("du_doan_gia_can_ho")),
    ("du_doan_gia_thue", nb("du_doan_gia_thue")),
    ("du_doan_xu_huong_gia", nb("du_doan_xu_huong_gia")),
    ("build_site", TRANG),
    ("tro_ly_y_dinh", nb("tro_ly_y_dinh")),
    ("build_site_lan_2", TRANG),
    ("cap_nhat_readme", README),
    ("kiem_tra_mo_hinh", [PY, "-X", "utf8", "tests/kiem_tra_mo_hinh.py"]),
    ("kiem_tra_api", [PY, "-X", "utf8", "tests/kiem_tra_api.py"]),
    ("kiem_tra_cong_bo", [PY, "-X", "utf8", "tests/kiem_tra_cong_bo.py"]),
    ("kiem_tra_tro_ly", ["node", "tests/kiem_tra_tro_ly.js"]),
    ("cong_bo", CONG_BO),
]
# Bài chính: chỉ cần dataset/raw + dataset/history của nhà ở; kiểm thử ở chế độ --nha-pho (bỏ qua có ghi rõ phần mở rộng)
BUOC_NHA_PHO = [
    ("2324801030095", nb("2324801030095")),
    ("xuat_du_lieu_web", DU_LIEU_WEB),
    ("cap_nhat_readme", README),
    ("kiem_tra_mo_hinh", [PY, "-X", "utf8", "tests/kiem_tra_mo_hinh.py", "--nha-pho"]),
    ("kiem_tra_api", [PY, "-X", "utf8", "tests/kiem_tra_api.py", "--nha-pho"]),
    ("kiem_tra_cong_bo", [PY, "-X", "utf8", "tests/kiem_tra_cong_bo.py"]),
    ("cong_bo", CONG_BO),
]
# notebook -> file sinh ra nó trong scripts/sinh_notebook/
SINH = {"2324801030095": "chinh", "du_doan_gia_can_ho": "can_ho", "du_doan_gia_thue": "gia_thue",
        "du_doan_xu_huong_gia": "xu_huong", "tro_ly_y_dinh": "tro_ly"}


def chay(buoc, che_do):
    """che_do: danh sách đủ bước của chế độ; trước 'cong_bo' mọi bước kiem_tra_* của chế độ phải đã chạy đạt TRONG lần này."""
    da_chay = set()
    for ten, lenh in buoc:
        if ten == "cong_bo":
            thieu = [b for b in che_do if b[0].startswith("kiem_tra_") and b[0] not in da_chay]
            if thieu:
                print(f"== (trước khi công bố phải kiểm thử bộ ứng viên: chạy {[b[0] for b in thieu]})", flush=True)
                chay(thieu, che_do); da_chay |= {b[0] for b in thieu}
        t = time.time()
        print(f"== {ten} ...", flush=True)
        if ten in SINH and subprocess.run([PY, "-X", "utf8", f"scripts/sinh_notebook/{SINH[ten]}.py", f"notebooks/{ten}.ipynb"], cwd=GOC).returncode != 0:
            sys.exit(f"DỪNG: không sinh được notebook '{ten}' từ scripts/sinh_notebook/{SINH[ten]}.py")
        if subprocess.run(lenh, cwd=GOC).returncode != 0:
            sys.exit(f"DỪNG: bước '{ten}' lỗi" + (" (chưa công bố: API giữ bộ đang phục vụ)" if ten != "cong_bo" else "") +
                     f". Sửa xong chạy tiếp bằng: python scripts/chay_toan_bo.py{' --nha-pho' if che_do is BUOC_NHA_PHO else ''} --tu {ten}")
        print(f"   xong ({time.time() - t:.0f} giây)", flush=True)
        da_chay.add(ten)


def kiem_api_dang_chay(url=None, goc=None):
    """Kiểm chứng API mô hình ĐANG chạy phục vụ đúng bộ tệp đã công bố (models/phien_ban.json) và định giá được.
    Trả ("BỎ QUA", lý do) khi API tắt; ("ĐẠT", chi tiết); ("LỖI", lý do) khi API trả lỗi / thiếu trường / lệch phiên bản."""
    import urllib.error
    import urllib.request
    url = (url or os.environ.get("PHH_API_URL") or "http://127.0.0.1:8000").rstrip("/")
    goc = pathlib.Path(goc or GOC)
    try:
        bk = json.loads((goc / "models" / "phien_ban.json").read_text(encoding="utf-8"))
    except Exception as e:
        return "LỖI", f"không đọc được bản kê models/phien_ban.json ({type(e).__name__}: {e}) – chưa chạy bước cong_bo?"
    tep_ky_vong = set(bk["tep"])

    def goi(duong, du_lieu=None):
        """Gọi API (GET khi du_lieu=None, POST JSON khi có) và trả JSON; lỗi HTTP / mạng để người gọi phân loại."""
        req = urllib.request.Request(url + duong, data=json.dumps(du_lieu).encode() if du_lieu is not None else None,
                                     headers={"content-type": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())

    h = None
    for lan in range(6):            # API nạp bộ mới khi nhận yêu cầu kế tiếp: cho vài giây
        try:
            h = goi("/health")
        except urllib.error.HTTPError as e:
            return "LỖI", f"/health trả HTTP {e.code}: {e.read()[:300].decode('utf-8', 'replace')}"
        except (urllib.error.URLError, ConnectionError, TimeoutError) as e:
            ly_do = getattr(e, "reason", e)
            if lan == 0 and isinstance(ly_do, (ConnectionRefusedError, OSError)) and not isinstance(ly_do, TimeoutError):
                return "BỎ QUA", f"API mô hình không chạy ở {url} ({ly_do}); chưa kiểm chứng phiên bản đang phục vụ"
            return "LỖI", f"không gọi được {url}/health: {ly_do}"
        thieu = [k for k in ("ok", "phien_ban", "tep", "mo_hinh", "loi_nap_moi_nhat") if k not in h]
        if thieu:
            return "LỖI", f"/health thiếu trường {thieu} (API chạy mã cũ? cần build lại image api)"
        if h["phien_ban"] == bk["id"]:
            break
        time.sleep(2)
    if h["phien_ban"] != bk["id"]:
        return "LỖI", f"API phục vụ bộ {h['phien_ban']}, đã công bố {bk['id']}; lỗi nạp: {h['loi_nap_moi_nhat']}"
    if set(h["tep"]) != tep_ky_vong:
        return "LỖI", f"API phục vụ tập tệp khác bản kê: thiếu {sorted(tep_ky_vong - set(h['tep']))}, thừa {sorted(set(h['tep']) - tep_ky_vong)}"
    lech = [t for t in tep_ky_vong if h["tep"][t] != bk["tep"][t][:12]]
    if lech:
        return "LỖI", f"mã băm tệp khác bản kê: {lech}"
    try:
        kq = goi("/dinh-gia/nha-pho", {"dt_dat": 80, "so_tang": 2, "cap_loi_vao": 3, "hem_rong": 6})
    except Exception as e:
        return "LỖI", f"POST /dinh-gia/nha-pho lỗi: {e}"
    if kq.get("phien_ban") != bk["id"] or not (kq.get("gia_ty") or 0) > 0:
        return "LỖI", f"POST /dinh-gia/nha-pho trả {kq.get('gia_ty')} tỷ với bộ {kq.get('phien_ban')} (kỳ vọng {bk['id']})"
    return "ĐẠT", f"API phục vụ bộ {bk['id']} ({len(tep_ky_vong)} tệp, mô hình {h['mo_hinh']}); định giá thử 80 m² = {kq['gia_ty']} tỷ"


def bao_cao_api():
    """In kết quả kiểm chứng API đang chạy; chỉ LỖI mới dừng pipeline (BỎ QUA = API tắt, không coi là lỗi)."""
    tt, chi_tiet = kiem_api_dang_chay()
    print(f"Kiểm chứng API đang chạy: {tt} – {chi_tiet}")
    if tt == "LỖI":
        sys.exit("DỪNG: API mô hình không phục vụ đúng bộ tệp vừa công bố.")


def cap_nhat_readme():
    """Ghi lại bảng "Kết quả chính" trong README.md từ models/danh_gia_mo_hinh*.json (kết quả notebook vừa chạy)."""
    vn = lambda x, d=1: "–" if x != x else f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    J = lambda f: json.loads((GOC / "models" / f"{f}.json").read_text(encoding="utf-8"))
    dong = lambda d, k, ten: next(r for r in d[k] if r["Mô hình"] == ten)
    baseline = lambda d, k: next(r for r in d[k] if r["Mô hình"].startswith("Baseline"))
    pa = lambda d, k: next((f"{r['Mô hình'].removeprefix('Phần A – ')}: {vn(r['MAPE (%)'])}%" for r in d[k] if r["Mô hình"].startswith("Phần A")), "chính là mô hình cuối")
    N = J("danh_gia_mo_hinh")
    co_ch = (GOC / "models" / "danh_gia_mo_hinh_can_ho.json").exists()      # căn hộ là phần mở rộng: có thể chưa chạy
    n, tn, bn = N["ten_mo_hinh"], dong(N, "test_phu_hoa", N["ten_mo_hinh"]), baseline(N, "test_phu_hoa")
    if co_ch:
        C = J("danh_gia_mo_hinh_can_ho"); c = C["ten_mo_hinh"]; tc, bc = dong(C, "test", c), baseline(C, "test")
    else:
        C = {"kiem_dinh_cheo": [{"Mô hình": "–", "MAPE (%)": float("nan")}]}; c = "– (chưa chạy notebook căn hộ)"
        tc = bc = {"Mô hình": "–", "Số căn": 0, "MAPE (%)": float("nan"), "MAE (tỷ)": float("nan")}
    phu = N.get("do_phu_test_80", {}).get("test Phú Hòa")
    phu_s = f"{phu['trong']}/{phu['tong']} căn ({vn(phu['trong'] / phu['tong'] * 100, 0)}%)" if phu else "–"
    # so sánh cặp (cùng các căn test): chỉ nói "tốt hơn" khi KTC của chênh lệch không chứa 0
    cap = {r["Chỉ số"]: r for r in N.get("so_sanh_cap_test", []) if r["Vùng"] == "Phú Hòa"}
    kl = lambda r: "mô hình tốt hơn có ý nghĩa" if r["KTC cao"] < 0 else "mốc tốt hơn có ý nghĩa" if r["KTC thấp"] > 0 else "KTC chứa 0: chưa đủ bằng chứng"
    cap_s = "; ".join(f"{k.split()[0]} {vn(r['Chênh (cuối − baseline)'], d)}{dv} (KTC {vn(r['KTC thấp'], d)} đến {vn(r['KTC cao'], d)}) – {kl(r)}"
                      for k, d, dv in (("MAPE (%)", 1, " điểm %"), ("MAE (tỷ)", 2, " tỷ")) if (r := cap.get(k))) or "–"
    # Mô hình và mốc so sánh đặt trên CÙNG một tập test (không đặt số kiểm định chéo cạnh số test)
    bang = f"""| | Nhà phố – Phú Hòa (bài chính) | Căn hộ (mở rộng) |
|---|---|---|
| Mô hình | {n} | {c} |
| Tập test giữ riêng | {int(tn['Số căn'])} căn | {int(tc['Số căn'])} căn |
| MAPE mô hình trên test | {vn(tn['MAPE (%)'])}% (KTC 95% {vn(tn['MAPE thấp (95%)'])}–{vn(tn['MAPE cao (95%)'])}) | {vn(tc['MAPE (%)'])}% |
| MAE mô hình trên test | {vn(tn['MAE (tỷ)'], 2)} tỷ đồng | {vn(tc['MAE (tỷ)'], 2)} tỷ đồng |
| Mốc so sánh trên cùng tập test | {bn['Mô hình']}: MAPE {vn(bn['MAPE (%)'])}%, MAE {vn(bn['MAE (tỷ)'], 2)} tỷ | {bc['Mô hình']}: MAPE {vn(bc['MAPE (%)'])}%, MAE {vn(bc['MAE (tỷ)'], 2)} tỷ |
| Chênh mô hình − mốc trên từng căn test (so sánh cặp) | {cap_s} | – |
| Kiểm định chéo trên tập train (mô hình / mốc) | {vn(dong(N, 'kiem_dinh_cheo_phu_hoa', n)['MAPE (%)'])}% / {vn(baseline(N, 'kiem_dinh_cheo_phu_hoa')['MAPE (%)'])}% | {(vn(dong(C, 'kiem_dinh_cheo', c)['MAPE (%)']) + '% / ' + vn(baseline(C, 'kiem_dinh_cheo')['MAPE (%)']) + '%') if co_ch else '–'} |
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


def chon_buoc(ds, ten):
    """Các bước của chế độ `ds` bắt đầu từ bước `ten` (dùng cho --tu); sai tên -> thoát, in danh sách bước hợp lệ."""
    ten_cac_buoc = [b[0] for b in ds]
    if ten not in ten_cac_buoc:
        sys.exit(f"Không có bước '{ten}' trong chế độ này; các bước: {ten_cac_buoc}")
    return ds[ten_cac_buoc.index(ten):]


if __name__ == "__main__":
    co = set(a for a in sys.argv[1:] if a.startswith("--"))
    if "--readme" in co:
        cap_nhat_readme()
        sys.exit(0)
    if "--nha-pho" in co and "--xu-huong" in co:
        sys.exit("--nha-pho và --xu-huong là hai chế độ khác nhau, chọn một.")
    if "--xu-huong" in co and co & {"--tu", "--thu-thap"}:
        sys.exit("--xu-huong không dùng chung với --tu / --thu-thap (chế độ này chỉ chạy lại notebook xu hướng với dữ liệu hiện có). "
                 "Thu thập trước: chạy scripts/cap_nhat_dinh_ky.py --khong-chay-lai rồi --xu-huong.")
    la_biet = {"--readme", "--nha-pho", "--xu-huong", "--tu", "--thu-thap"}
    if co - la_biet:
        sys.exit(f"Cờ không hỗ trợ: {sorted(co - la_biet)}; các cờ: {sorted(la_biet)}")
    la_nha_pho = "--nha-pho" in co
    if not la_nha_pho and not shutil.which("node"):
        sys.exit("Cần Node.js >= 18 (notebook trợ lý và kiểm thử trang dùng Node). Chỉ chạy bài chính: thêm --nha-pho.")
    if "--xu-huong" in co:
        chay([b for b in BUOC if b[0] in ("du_doan_xu_huong_gia", "build_site_lan_2", "cap_nhat_readme", "cong_bo")], BUOC)
        bao_cao_api()
        sys.exit(0)
    buoc = BUOC_NHA_PHO if la_nha_pho else BUOC
    if "--tu" in co:
        vt = sys.argv.index("--tu")
        if vt + 1 >= len(sys.argv) or sys.argv[vt + 1].startswith("--"):
            sys.exit(f"--tu cần tên bước; các bước: {[b[0] for b in buoc]}")
        buoc = chon_buoc(buoc, sys.argv[vt + 1])
        if "--thu-thap" in co and buoc[0][0] != "2324801030095":
            sys.exit("--thu-thap chỉ có tác dụng khi chạy lại từ notebook 2324801030095 (dữ liệu mới vào mô hình ở bước đó); "
                     "bỏ --tu hoặc bỏ --thu-thap.")
    if "--thu-thap" in co:
        # nguồn lỗi thì vẫn chạy tiếp với dữ liệu cũ; --nha-pho chỉ thu nguồn nhà ở
        subprocess.run([PY, "-X", "utf8", "scripts/cap_nhat_dinh_ky.py", "--khong-chay-lai"] + (["--chi-nha"] if la_nha_pho else []), cwd=GOC)
    chay(buoc, BUOC_NHA_PHO if la_nha_pho else BUOC)
    bao_cao_api()
    print("HOÀN TẤT" + (" (bài chính nhà phố)." if la_nha_pho else ": mọi notebook, trang demo và kiểm thử đã chạy lại."))
