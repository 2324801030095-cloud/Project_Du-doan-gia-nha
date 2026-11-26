"""Kiểm thử dịch vụ mô hình (api/): chạy trong tiến trình bằng TestClient, không cần Docker.
Chạy từ thư mục gốc đề tài:  python tests/kiem_tra_api.py"""
import json
import sys
import warnings
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
warnings.filterwarnings("ignore")
GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC / "api"))
from fastapi.testclient import TestClient  # noqa: E402

import main  # noqa: E402

c = TestClient(main.app)
KQ = []


def kiem(ten):
    def boc(f):
        try:
            f(); KQ.append((ten, True, ""))
        except Exception as e:
            KQ.append((ten, False, f"{type(e).__name__}: {e}"))
        return f
    return boc


NHA = {"dt_dat": 80, "ngang": 4.5, "so_tang": 2, "dt_san": 160, "phong_ngu": 3, "so_wc": 2, "cap_loi_vao": 3, "hem_rong": 6,
       "mo_ta": "1 trệt 1 lầu kdc hẻm 6m sổ hồng riêng"}


@kiem("Định giá nhà phố dùng đúng mô hình cuối (Random Forest) của notebook, khoảng 80% chứa giá, giải thích cộng lại đúng dự đoán")
def _():
    r = c.post("/dinh-gia/nha-pho", json=NHA).json()
    dg = json.loads((GOC / "models" / "danh_gia_mo_hinh.json").read_text(encoding="utf-8"))
    assert r["mo_hinh"] == dg["ten_mo_hinh"], r["mo_hinh"]
    lo, hi = r["khoang_80_ty"]
    assert lo < r["gia_ty"] < hi and r["khoang_50_ty"][0] >= lo and r["khoang_50_ty"][1] <= hi
    import math
    tong = math.log(r["giai_thich"]["nen_ty"]) + sum(x["log"] for x in r["giai_thich"]["nhom"])
    assert abs(math.exp(tong) - r["gia_ty"]) / r["gia_ty"] < 0.01, (math.exp(tong), r["gia_ty"])
    assert r["thue_trieu_thang"] > 0


@kiem("Định giá hợp lý theo hướng: diện tích lớn hơn, mặt tiền -> giá cao hơn; thông số thiếu vẫn định giá được")
def _():
    gia = lambda **k: c.post("/dinh-gia/nha-pho", json={**NHA, **k}).json()["gia_ty"]
    assert gia(dt_dat=160, dt_san=320) > gia()
    assert gia(cap_loi_vao=5, mat_tien_duong=1, hem_rong=20) > gia(cap_loi_vao=1, hem_rong=2)
    assert c.post("/dinh-gia/nha-pho", json={"dt_dat": 70}).status_code == 200


@kiem("Kiểm tra đầu vào: diện tích vô lý, kiểu sai, chuỗi quá dài bị từ chối (422)")
def _():
    for sai in ({"dt_dat": 5}, {"dt_dat": "abc"}, {"dt_dat": 80, "mo_ta": "x" * 5000}, {"dt_dat": 80, "cap_loi_vao": 9}, {}):
        assert c.post("/dinh-gia/nha-pho", json=sai).status_code == 422, sai


@kiem("Căn hộ: nhận ra dự án có trong dữ liệu; nhà ở xã hội rẻ hơn căn thương mại cùng thông số")
def _():
    r = c.post("/dinh-gia/can-ho", json={"dt_su_dung": 68, "du_an": "Happy One Central", "phong_ngu": 2, "so_wc": 2}).json()
    assert r["du_an_nhan_ra"] and r["khoang_80_ty"][0] < r["gia_ty"] < r["khoang_80_ty"][1]
    tm = c.post("/dinh-gia/can-ho", json={"dt_su_dung": 50, "phong_ngu": 2}).json()["gia_ty"]
    xh = c.post("/dinh-gia/can-ho", json={"dt_su_dung": 50, "phong_ngu": 2, "nha_o_xa_hoi": 1}).json()["gia_ty"]
    assert xh < tm, (xh, tm)


@kiem("Đất: khớp mô hình rút gọn của trang tĩnh (cùng công thức, cùng tham số) và phường lạ dùng giá nền của quận")
def _():
    r = c.post("/dinh-gia/dat", json={"dt": 100}).json()
    assert r["phuong_co_du_lieu"] and abs(r["don_gia_trieu_m2"] * 100 / 1000 - r["gia_ty"]) < 0.01
    assert not c.post("/dinh-gia/dat", json={"dt": 100, "phuong": "thu dau mot|khong co"}).json()["phuong_co_du_lieu"]


@kiem("Danh sách tin: lọc theo chẩn đoán, khoảng giá và phân trang nhất quán; tin lẻ và nhiều tin theo mã")
def _():
    d = c.get("/nha-pho", params={"chan_doan": "Rẻ hơn thị trường", "so_dong": 200}).json()
    assert d["tong"] == len(d["ket_qua"]) and all(x["chan_doan"] == "Rẻ hơn thị trường" for x in d["ket_qua"])
    g = c.get("/nha-pho", params={"gia_min": 3, "gia_max": 5, "so_dong": 200}).json()["ket_qua"]
    assert all(3 <= x["g"] <= 5 for x in g)
    t1, t2 = c.get("/nha-pho", params={"so_dong": 5, "trang": 1}).json(), c.get("/nha-pho", params={"so_dong": 5, "trang": 2}).json()
    assert not {x["id"] for x in t1["ket_qua"]} & {x["id"] for x in t2["ket_qua"]}
    ma = [x["id"] for x in t1["ket_qua"][:2]]
    assert c.get(f"/nha-pho/{ma[0]}").json()["id"] == ma[0] and c.get("/nha-pho/khong-co").status_code == 404
    assert {x["id"] for x in c.get("/nha-pho-theo-ma", params={"ma": ma}).json()} == set(ma)


@kiem("Trợ lý: mô hình ý định phân loại đúng câu hỏi định giá và lời chào")
def _():
    assert c.post("/tro-ly/y-dinh", json={"cau": "nhà 80m2 hẻm xe hơi giá bao nhiêu"}).json()["y_dinh"] == "dinh_gia"
    assert c.post("/tro-ly/y-dinh", json={"cau": "xin chào"}).json()["y_dinh"] == "chao"


@kiem("Các endpoint dữ liệu trả đủ phần: tổng quan, đánh giá 3 notebook, bản đồ, xu hướng, danh mục")
def _():
    assert c.get("/tong-quan").json()["so_lieu"]["BEST"]
    assert set(c.get("/danh-gia").json()) == {"nha_pho", "can_ho", "dat"}
    assert len(c.get("/ban-do").json()["diem"]) > 100
    assert c.get("/xu-huong").json()["du_bao"] and c.get("/danh-muc").json()["du_an"]


for ten, ok, loi in KQ:
    print(("ĐẠT       " if ok else "KHÔNG ĐẠT ") + ten + ("" if ok else f"\n           -> {loi}"))
print(f"\n{sum(ok for _, ok, _ in KQ)}/{len(KQ)} phép kiểm đạt")
sys.exit(0 if all(ok for _, ok, _ in KQ) else 1)
