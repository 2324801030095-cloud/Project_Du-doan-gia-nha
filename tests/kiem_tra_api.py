"""Kiểm thử dịch vụ mô hình (api/): chạy trong tiến trình bằng TestClient, không cần Docker.
Chạy từ thư mục gốc đề tài:  python tests/kiem_tra_api.py
Chế độ bài chính:  python tests/kiem_tra_api.py --nha-pho  -> chỉ cần dữ liệu/mô hình nhà phố; phép kiểm phần mở rộng
(căn hộ, trợ lý, dự báo xu hướng) được BỎ QUA có ghi lý do. Kiểm thử công bố bộ tệp: tests/kiem_tra_cong_bo.py"""
import json
import os
import sys
import warnings
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
warnings.filterwarnings("ignore")
GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC / "api"))
os.environ.setdefault("PHH_UNG_VIEN", "1")    # kiểm bộ tệp làm việc (ỨNG VIÊN) trên đĩa, không phải bộ đã công bố
from fastapi.testclient import TestClient  # noqa: E402

import main  # noqa: E402

c = TestClient(main.app)
NHA_PHO = "--nha-pho" in sys.argv
KQ = []           # (tên, "ĐẠT" | "KHÔNG ĐẠT" | "BỎ QUA", chi tiết)


def kiem(ten, mo_rong=False):
    """mo_rong=True: phép kiểm của phần mở rộng -> bỏ qua ở chế độ --nha-pho."""
    def boc(f):
        if mo_rong and NHA_PHO:
            KQ.append((ten, "BỎ QUA", "phần mở rộng, không thuộc chế độ --nha-pho")); return f
        try:
            f(); KQ.append((ten, "ĐẠT", ""))
        except Exception as e:
            KQ.append((ten, "KHÔNG ĐẠT", f"{type(e).__name__}: {e}"))
        return f
    return boc


NHA = {"dt_dat": 80, "ngang": 4.5, "so_tang": 2, "dt_san": 160, "phong_ngu": 3, "so_wc": 2, "cap_loi_vao": 3, "hem_rong": 6,
       "mo_ta": "1 trệt 1 lầu kdc hẻm 6m sổ hồng riêng"}


@kiem("Định giá nhà phố dùng đúng mô hình cuối (Random Forest) của notebook, khoảng 80% chứa giá, giải thích cộng lại đúng dự đoán")
def _():
    r = c.post("/dinh-gia/nha-pho", json=NHA).json()
    dg = json.loads((GOC / "models" / "danh_gia_mo_hinh.json").read_text(encoding="utf-8"))
    assert r["mo_hinh"] == dg["ten_mo_hinh"], r["mo_hinh"]
    assert r["phien_ban"] == c.get("/health").json()["phien_ban"]
    lo, hi = r["khoang_80_ty"]
    assert lo < r["gia_ty"] < hi and r["khoang_50_ty"][0] >= lo and r["khoang_50_ty"][1] <= hi
    import math
    tong = math.log(r["giai_thich"]["nen_ty"]) + sum(x["log"] for x in r["giai_thich"]["nhom"])
    assert abs(math.exp(tong) - r["gia_ty"]) / r["gia_ty"] < 0.01, (math.exp(tong), r["gia_ty"])
    if not NHA_PHO:                      # tiền thuê ước tính cần notebook giá thuê (phần mở rộng)
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


@kiem("Căn hộ (mở rộng): nhận ra dự án có trong dữ liệu; nhà ở xã hội rẻ hơn căn thương mại cùng thông số", mo_rong=True)
def _():
    r = c.post("/dinh-gia/can-ho", json={"dt_su_dung": 68, "du_an": "Happy One Central", "phong_ngu": 2, "so_wc": 2}).json()
    assert r["du_an_nhan_ra"] and r["khoang_80_ty"][0] < r["gia_ty"] < r["khoang_80_ty"][1]
    tm = c.post("/dinh-gia/can-ho", json={"dt_su_dung": 50, "phong_ngu": 2}).json()["gia_ty"]
    xh = c.post("/dinh-gia/can-ho", json={"dt_su_dung": 50, "phong_ngu": 2, "nha_o_xa_hoi": 1}).json()["gia_ty"]
    assert xh < tm, (xh, tm)


@kiem("Phạm vi đề tài: định giá đất nền độc lập đã bỏ khỏi API (đề tài định giá nhà); bản đồ không còn lớp đất")
def _():
    assert c.post("/dinh-gia/dat", json={"dt": 100}).status_code == 404 and c.get("/dat").status_code == 404
    assert all(d[3] != "dat" for d in c.get("/ban-do").json()["diem"])
    assert "dat" not in c.get("/danh-gia").json() and "phuong_dat" not in c.get("/danh-muc").json()


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


@kiem("Trợ lý (mở rộng): mô hình ý định phân loại đúng câu hỏi định giá và lời chào", mo_rong=True)
def _():
    assert c.post("/tro-ly/y-dinh", json={"cau": "nhà 80m2 hẻm xe hơi giá bao nhiêu"}).json()["y_dinh"] == "dinh_gia"
    assert c.post("/tro-ly/y-dinh", json={"cau": "xin chào"}).json()["y_dinh"] == "chao"


@kiem("Endpoint bài chính trả đủ phần: health (bộ tệp đang phục vụ), tổng quan, đánh giá nhà phố, bản đồ, danh mục")
def _():
    h = c.get("/health").json()
    assert h["ok"] and h["loi_nap_moi_nhat"] is None and "models/mo_hinh_gia_nha.joblib" in h["tep"], h
    tq = c.get("/tong-quan").json()
    assert tq["so_lieu"]["BEST"]
    phu = tq["do_phu_test_80"]["test Phú Hòa"]
    assert 0 < phu["trong"] <= phu["tong"] and tq["chat_luong_du_lieu"]["so_tin_phu_hoa"] > 0
    assert "nha_pho" in c.get("/danh-gia").json()
    assert len(c.get("/ban-do").json()["diem"]) > 100
    assert c.get("/xu-huong").status_code == 200 and c.get("/danh-muc").status_code == 200
    if NHA_PHO:                          # thiếu phần mở rộng: API báo 503 rõ ràng, không 500
        for duong, body in (("/dinh-gia/can-ho", {"dt_su_dung": 60}), ("/tro-ly/y-dinh", {"cau": "xin chào"})):
            r = c.post(duong, json=body)
            assert r.status_code in (200, 503), (duong, r.status_code)


@kiem("Endpoint phần mở rộng: đánh giá căn hộ, dự báo xu hướng, danh mục dự án", mo_rong=True)
def _():
    assert set(c.get("/danh-gia").json()) == {"nha_pho", "can_ho"}
    assert c.get("/xu-huong").json()["du_bao"] and c.get("/danh-muc").json()["du_an"]


for ten, tt, ct in KQ:
    print(f"{tt:<10}{ten}" + (f"\n           -> {ct}" if ct else ""))
dat, bo_qua = sum(t == "ĐẠT" for _, t, _ in KQ), sum(t == "BỎ QUA" for _, t, _ in KQ)
print(f"\n{dat}/{len(KQ) - bo_qua} phép kiểm đạt, {bo_qua} bỏ qua" + (" (chế độ --nha-pho)" if NHA_PHO else ""))
sys.exit(0 if all(t != "KHÔNG ĐẠT" for _, t, _ in KQ) else 1)
