"""Kiểm thử cơ chế công bố bộ tệp của API (models/phien_ban.json) trên một BẢN SAO TẠM của các tệp nhà phố:
không đụng models/ thật và không ảnh hưởng API / web đang chạy.
  - công bố A -> API phục vụ A; đổi tệp nhưng chưa công bố -> vẫn A; công bố B -> /health và POST /dinh-gia đều là B
  - công bố bộ có tệp hỏng / bản kê lệch mã băm -> GIỮ B, /health báo loi_nap_moi_nhat; thiếu tệp bắt buộc -> không công bố được
  - không có phần mở rộng (căn hộ, trợ lý) -> API vẫn chạy, các endpoint đó trả 503
  - không có bản kê: tệp làm việc KHÔNG được phục vụ (503, hoặc bộ bàn giao models/ban_giao/); PHH_UNG_VIEN=1 mới đọc tệp làm việc;
    bản kê biến mất -> giữ bộ đang phục vụ / khởi động lại dùng bộ đã công bố gần nhất
  - scripts/chay_toan_bo.kiem_api_dang_chay phân biệt: API tắt (BỎ QUA) / lỗi HTTP, thiếu trường (LỖI) / đúng bộ (ĐẠT)
Chạy từ thư mục gốc đề tài:  python tests/kiem_tra_cong_bo.py"""
import http.server
import json
import os
import shutil
import socket
import sys
import tempfile
import threading
import time
import warnings
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
warnings.filterwarnings("ignore")
GOC = Path(__file__).resolve().parent.parent
TAM = Path(tempfile.mkdtemp(prefix="phh_cong_bo_"))
TEP = ["models/mo_hinh_gia_nha.joblib", "models/du_lieu_web.json", "models/danh_gia_mo_hinh.json", "dataset/processed/nha_da_xu_ly.csv"]
for t in TEP:                                   # chỉ bộ tệp bài chính (nhà phố): không có căn hộ / trợ lý
    (TAM / t).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(GOC / t, TAM / t)
_w = json.loads((TAM / "models/du_lieu_web.json").read_text(encoding="utf-8"))
_w["SO_LIEU"]["NGAY"] = "NGAY_GOC"              # ngày gốc cố định: các phép "sửa ngày" luôn đổi nội dung, dù tệp thật mang ngày nào
(TAM / "models/du_lieu_web.json").write_text(json.dumps(_w, ensure_ascii=False), encoding="utf-8")
os.environ["PHH_GOC"] = str(TAM)                # phải đặt TRƯỚC khi nạp api/dinh_gia.py
sys.path[:0] = [str(GOC / "api"), str(GOC / "scripts")]
import uvicorn  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

import chay_toan_bo  # noqa: E402
import dinh_gia as DG  # noqa: E402
import main  # noqa: E402

c = TestClient(main.app)
KQ = []
NHA = {"dt_dat": 80, "so_tang": 2, "cap_loi_vao": 3, "hem_rong": 6}
WEB = TAM / "models/du_lieu_web.json"


def kiem(ten):
    def boc(f):
        try:
            f(); KQ.append((ten, True, ""))
        except Exception as e:
            KQ.append((ten, False, f"{type(e).__name__}: {e}"))
        return f
    return boc


def doi_ngay(ngay):                              # sửa một trường của du_lieu_web.json -> nội dung (và mã băm) khác
    w = json.loads(WEB.read_text(encoding="utf-8")); w["SO_LIEU"]["NGAY"] = ngay
    WEB.write_text(json.dumps(w, ensure_ascii=False), encoding="utf-8")


def cong_bo(kiem=True):
    """kiem=False: mô phỏng một bộ hỏng LỌT qua công bố (để kiểm API giữ bộ cũ)."""
    bk = DG.cong_bo(kiem=kiem); time.sleep(0.05); return bk   # mtime bản kê đổi -> yêu cầu kế tiếp nạp bộ mới


def tu_choi(ly_do):
    """Công bố có kiểm phải TỪ CHỐI bộ hỏng và không đổi bản kê."""
    truoc = (TAM / DG.MANIFEST).read_bytes()
    try:
        DG.cong_bo(); raise AssertionError("cong_bo không từ chối bộ hỏng: " + ly_do)
    except DG.LoiNapBo:
        pass
    assert (TAM / DG.MANIFEST).read_bytes() == truoc, ly_do


def khoi_dong_lai():                             # như tiến trình API mới khởi động
    DG._HIEN = None; DG._TT.update(moc=None, loi_nap=None, nguon=None)


def ngay_tep_lam_viec():
    return json.loads(WEB.read_text(encoding="utf-8"))["SO_LIEU"]["NGAY"]


@kiem("Khởi động KHÔNG có bản kê, không có bộ bàn giao: 503; sửa tệp làm việc hợp lệ (NGAY = 01/01/2099) rồi gọi lại "
      "GET /health và POST -> vẫn 503 (tệp làm việc không bao giờ được phục vụ); chỉ PHH_UNG_VIEN=1 tường minh mới đọc tệp làm việc")
def _():
    goc = WEB.read_bytes()
    assert c.get("/health").status_code == 503 and c.post("/dinh-gia/nha-pho", json=NHA).status_code == 503
    doi_ngay("01/01/2099"); time.sleep(0.05)
    assert c.get("/health").status_code == 503 and c.post("/dinh-gia/nha-pho", json=NHA).status_code == 503
    for gia_tri in ("0", "true", ""):                         # chỉ đúng chuỗi "1" mới bật chế độ ứng viên
        os.environ["PHH_UNG_VIEN"] = gia_tri
        assert c.get("/health").status_code == 503, gia_tri
    os.environ["PHH_UNG_VIEN"] = "1"
    try:
        h = c.get("/health").json()
        assert h["ngay_du_lieu"] == "01/01/2099" and h["nguon"].startswith("tệp làm việc"), h
    finally:
        del os.environ["PHH_UNG_VIEN"]
    assert c.get("/health").status_code == 503                # tắt -> không giữ bộ ứng viên
    WEB.write_bytes(goc)


BG = {}


@kiem("Clone mới (chỉ có bộ bàn giao models/ban_giao/ trong git): phục vụ bộ bàn giao; sửa tệp làm việc hợp lệ rồi gọi lại "
      "GET /health và POST -> vẫn bộ bàn giao, ngày cũ; không có phần mở rộng thì căn hộ / trợ lý 503")
def _():
    BG.update(DG.cong_bo()); DG.tao_ban_giao()                # chuẩn bị bộ bàn giao như khi commit
    (TAM / DG.MANIFEST).unlink(); shutil.rmtree(TAM / DG.THU_MUC_CONG_BO)
    khoi_dong_lai()
    h = c.get("/health").json()
    assert h["phien_ban"] == BG["id"] and h["nguon"].startswith("bộ bàn giao"), h
    ngay = h["ngay_du_lieu"]
    doi_ngay("01/01/2099"); time.sleep(0.05)
    for _ in range(2):
        h = c.get("/health").json()
        assert h["phien_ban"] == BG["id"] and h["ngay_du_lieu"] == ngay != ngay_tep_lam_viec(), h
        assert c.post("/dinh-gia/nha-pho", json=NHA).json()["phien_ban"] == BG["id"]
    khoi_dong_lai()                                            # khởi động lại khi tệp làm việc đã đổi, chưa công bố
    assert c.get("/health").json()["ngay_du_lieu"] == ngay
    assert c.post("/dinh-gia/can-ho", json={"dt_su_dung": 60}).status_code == 503
    assert c.post("/tro-ly/y-dinh", json={"cau": "xin chào"}).status_code == 503
    assert set(c.get("/danh-gia").json()) == {"nha_pho"}
    WEB.write_bytes((TAM / DG.BAN_GIAO / "models/du_lieu_web.json").read_bytes())


A = {}


@kiem("Công bố A -> phục vụ A; đổi tệp nhưng CHƯA công bố -> vẫn A; công bố B -> /health và POST /dinh-gia đều là B")
def _():
    A.update(cong_bo())
    assert c.get("/health").json()["phien_ban"] == A["id"]
    doi_ngay("01/01/2099")
    h = c.get("/health").json()
    assert h["phien_ban"] == A["id"] and h["ngay_du_lieu"] != "01/01/2099", h
    B = cong_bo()
    assert B["id"] != A["id"]
    h = c.get("/health").json()
    assert h["phien_ban"] == B["id"] and h["ngay_du_lieu"] == "01/01/2099" and h["loi_nap_moi_nhat"] is None, h
    assert c.post("/dinh-gia/nha-pho", json=NHA).json()["phien_ban"] == B["id"]
    A["B"] = B["id"]


@kiem("Công bố bộ có tệp hỏng -> GIỮ bộ B đang phục vụ, /health báo lỗi nạp, định giá vẫn chạy")
def _():
    goc = WEB.read_bytes()
    WEB.write_text("{hỏng", encoding="utf-8")
    tu_choi("JSON sai cú pháp")
    cong_bo(kiem=False)
    h = c.get("/health").json()
    assert h["phien_ban"] == A["B"] and "JSONDecodeError" in (h["loi_nap_moi_nhat"] or ""), h
    assert c.post("/dinh-gia/nha-pho", json=NHA).json()["phien_ban"] == A["B"]
    WEB.write_bytes(goc)


@kiem("Bản kê lệch mã băm (tệp đổi sau khi công bố / đang ghi dở) -> GIỮ bộ cũ; công bố lại -> nạp được")
def _():
    bk = DG.tao_ban_ke(); bk["tep"]["models/du_lieu_web.json"] = "0" * 64; bk["id"] = "lechmaba0000"
    (TAM / DG.MANIFEST).write_text(json.dumps(bk), encoding="utf-8"); time.sleep(0.05)
    h = c.get("/health").json()
    assert h["phien_ban"] == A["B"] and "mã băm khác bản kê" in (h["loi_nap_moi_nhat"] or ""), h
    moi = cong_bo()
    h = c.get("/health").json()
    assert h["phien_ban"] == moi["id"] and h["loi_nap_moi_nhat"] is None, h


def dung_duoc(ma):
    """Sau mỗi lần chuyển bộ thành công: health, tổng quan, danh sách tin, chi tiết tin và định giá đều chạy, cùng mã bộ."""
    h = c.get("/health").json()
    assert h["phien_ban"] == ma and h["loi_nap_moi_nhat"] is None, h
    ds = c.get("/nha-pho", params={"so_dong": 3})
    assert ds.status_code == 200 and ds.json()["tong"] > 0, ds.text[:200]
    assert c.get(f"/nha-pho/{ds.json()['ket_qua'][0]['id']}").status_code == 200
    assert c.get("/tong-quan").status_code == 200 and c.get("/ban-do").status_code == 200
    assert c.post("/dinh-gia/nha-pho", json=NHA).json()["phien_ban"] == ma


def sua_web(f):                                  # JSON vẫn ĐÚNG cú pháp nhưng sai cấu trúc
    w = json.loads(WEB.read_text(encoding="utf-8")); f(w)
    WEB.write_text(json.dumps(w, ensure_ascii=False), encoding="utf-8")


@kiem("JSON đúng cú pháp nhưng sai cấu trúc (bỏ LISTINGS / SO_LIEU / ai_full, LISTINGS sai kiểu) -> GIỮ bộ cũ, /health báo lỗi; "
      "danh sách tin và định giá vẫn chạy; công bố bản hợp lệ tiếp theo -> phục hồi")
def _():
    goc = WEB.read_bytes()
    dang = c.get("/health").json()["phien_ban"]
    dung_duoc(dang)
    for ten, f in (("LISTINGS", lambda w: w.pop("LISTINGS")), ("SO_LIEU", lambda w: w.pop("SO_LIEU")),
                   ("ai_full", lambda w: w["LISTINGS"][0].pop("ai_full")), ("LISTINGS", lambda w: w.update(LISTINGS={"a": 1})),
                   ("NGAY", lambda w: w["SO_LIEU"].pop("NGAY")), ("MAP_PTS", lambda w: w.update(MAP_PTS=[[1, 2]]))):
        WEB.write_bytes(goc); sua_web(f); tu_choi(ten); bk = cong_bo(kiem=False)
        h = c.get("/health")
        assert h.status_code == 200 and h.json()["phien_ban"] == dang, (ten, h.status_code, h.text[:200])
        assert ten in (h.json()["loi_nap_moi_nhat"] or ""), (ten, h.json()["loi_nap_moi_nhat"])
        assert bk["id"] != dang
        dung_duoc_cu = c.get("/nha-pho", params={"so_dong": 2}).status_code == 200 and \
            c.post("/dinh-gia/nha-pho", json=NHA).json()["phien_ban"] == dang
        assert dung_duoc_cu, ten
    WEB.write_bytes(goc); moi = cong_bo()
    dung_duoc(moi["id"])


@kiem("Tệp mở rộng được khai báo nhưng hỏng (mô hình trợ lý) -> GIỮ bộ cũ; gỡ tệp đó và công bố lại -> về chế độ 4 tệp nhà phố")
def _():
    dang = c.get("/health").json()["phien_ban"]
    f = TAM / "models/tro_ly_y_dinh.joblib"
    f.write_bytes(b"khong phai joblib"); tu_choi("joblib trợ lý hỏng"); cong_bo(kiem=False)
    h = c.get("/health").json()
    assert h["phien_ban"] == dang and h["loi_nap_moi_nhat"], h
    f.unlink(); moi = cong_bo()
    dung_duoc(moi["id"])
    assert set(c.get("/health").json()["tep"]) == set(TEP)


def phien_ban_sau_khoi_dong(xoa_ban_ke=False):
    """(id /health, id POST dự đoán) ngay sau khi API khởi động lại; xoa_ban_ke: như models/phien_ban.json bị mất."""
    if xoa_ban_ke and (TAM / DG.MANIFEST).exists():
        (TAM / DG.MANIFEST).unlink()
    khoi_dong_lai()
    h = c.get("/health")
    assert h.status_code == 200, h.text[:300]
    return h.json()["phien_ban"], c.post("/dinh-gia/nha-pho", json=NHA).json()["phien_ban"], h.json()


class LoiGhi:
    """Mô phỏng lỗi ghi (PermissionError) ở os.replace có đích kết thúc bằng `duoi`; các os.replace khác chạy bình thường."""
    def __init__(self, duoi):
        self.duoi, self.goc = duoi, os.replace

    def __enter__(self):
        def gia(a, b, *k, **kw):
            if str(b).endswith(self.duoi):
                raise PermissionError(13, "mô phỏng: tệp đang bị khóa", str(b))
            return self.goc(a, b, *k, **kw)
        os.replace = gia

    def __exit__(self, *a):
        os.replace = self.goc


@kiem("HỒI QUY 1 – công bố B lỗi TẠI os.replace bản kê (PermissionError mô phỏng): bản kê vẫn A, B không có dấu phục hồi; "
      "/health + POST là A trước và sau khởi động lại, kể cả khi bản kê bị mất. Lỗi GIỮA hai bước (bản kê đã trỏ B, ghi dấu lỗi): "
      "phục hồi về A an toàn, chạy lại công bố thì B có dấu. Hai lần công bố sát nhau: phục hồi đúng lần sau cùng")
def _():
    goc_web = WEB.read_bytes()
    doi_ngay("01/02/2099"); A = cong_bo()
    assert phien_ban_sau_khoi_dong()[:2] == (A["id"], A["id"])
    doi_ngay("02/02/2099")
    with LoiGhi(DG.MANIFEST.split("/")[-1]):
        try:
            DG.cong_bo(); raise AssertionError("cong_bo không báo lỗi khi không ghi được bản kê")
        except PermissionError:
            pass
    B_id = DG.tao_ban_ke()["id"]
    assert json.loads((TAM / DG.MANIFEST).read_text(encoding="utf-8"))["id"] == A["id"]
    assert (TAM / DG.THU_MUC_CONG_BO / B_id).exists() and not (TAM / DG.THU_MUC_CONG_BO / B_id / DG.DAU_CONG_BO).exists()
    h = c.get("/health").json()
    assert h["phien_ban"] == A["id"] and c.post("/dinh-gia/nha-pho", json=NHA).json()["phien_ban"] == A["id"], h
    assert phien_ban_sau_khoi_dong()[:2] == (A["id"], A["id"])
    hb, post, h = phien_ban_sau_khoi_dong(xoa_ban_ke=True)          # đúng kịch bản Codex: xóa bản kê rồi khởi động lại
    assert (hb, post) == (A["id"], A["id"]) and h["ngay_du_lieu"] == "01/02/2099", h
    # lỗi giữa hai bước: bản kê đã thay (điểm cam kết) nhưng ghi dấu lỗi
    _ghi = DG._ghi_nguyen_tu(TAM / DG.MANIFEST, {**A, "thu_muc": f"{DG.THU_MUC_CONG_BO}/{A['id']}"})  # khôi phục bản kê A
    with LoiGhi(DG.DAU_CONG_BO):
        try:
            DG.cong_bo(); raise AssertionError("cong_bo không báo lỗi khi không ghi được dấu")
        except DG.LoiNapBo as e:
            assert "chạy lại" in str(e), e
    assert json.loads((TAM / DG.MANIFEST).read_text(encoding="utf-8"))["id"] == B_id   # B đã được công bố
    assert phien_ban_sau_khoi_dong()[:2] == (B_id, B_id)
    assert phien_ban_sau_khoi_dong(xoa_ban_ke=True)[:2] == (A["id"], A["id"])         # thiếu dấu B -> về A, không đoán B
    B = cong_bo()                                                                      # chạy lại công bố -> B có dấu
    assert B["id"] == B_id and (TAM / DG.THU_MUC_CONG_BO / B_id / DG.DAU_CONG_BO).exists()
    assert phien_ban_sau_khoi_dong(xoa_ban_ke=True)[:2] == (B_id, B_id)
    # hai lần công bố sát nhau (cùng một giây): thứ tự theo cong_bo_ns tăng ngặt
    cong_bo(); doi_ngay("03/02/2099"); X = DG.cong_bo(); doi_ngay("04/02/2099"); Y = DG.cong_bo()
    assert Y["cong_bo_ns"] > X["cong_bo_ns"]
    assert phien_ban_sau_khoi_dong(xoa_ban_ke=True)[:2] == (Y["id"], Y["id"])
    doi_ngay("03/02/2099"); X2 = DG.cong_bo()                                          # công bố lại X (đã có thư mục)
    assert X2["id"] == X["id"] and phien_ban_sau_khoi_dong(xoa_ban_ke=True)[:2] == (X["id"], X["id"])
    WEB.write_bytes(goc_web); cong_bo()


@kiem("HỒI QUY 2 – bản kê hiện tại có nhưng HỎNG (JSON sai cú pháp; hoặc trỏ tới bộ hỏng): đang chạy -> giữ bộ đã nạp; "
      "khởi động lạnh -> phục hồi bộ đã công bố gần nhất, rồi bộ bàn giao; /health nêu lỗi + nguồn phục hồi; chỉ 503 khi "
      "không còn bộ hợp lệ; công bố thành công sau đó -> hệ thống bình thường")
def _():
    goc_web = WEB.read_bytes()
    doi_ngay("01/03/2099"); P = cong_bo()
    dung_duoc(P["id"])
    (TAM / DG.MANIFEST).write_text("{hỏng", encoding="utf-8"); time.sleep(0.05)
    h = c.get("/health").json()                                                       # đang chạy: giữ P
    assert h["phien_ban"] == P["id"] and "JSONDecodeError" in (h["loi_nap_moi_nhat"] or ""), h
    assert c.post("/dinh-gia/nha-pho", json=NHA).json()["phien_ban"] == P["id"]
    for _ in range(2):                                                                 # khởi động lạnh (2 lần)
        hb, post, h = phien_ban_sau_khoi_dong()
        assert (hb, post) == (P["id"], P["id"]), h
        assert h["nguon"].startswith("phục hồi") and "JSONDecodeError" in h["loi_nap_moi_nhat"], h
        assert c.get("/nha-pho", params={"so_dong": 1}).status_code == 200
    WEB.write_text("{hỏng", encoding="utf-8"); cong_bo(kiem=False)                    # bản kê hợp lệ nhưng trỏ tới bộ hỏng
    hb, post, h = phien_ban_sau_khoi_dong()
    assert (hb, post) == (P["id"], P["id"]) and h["nguon"].startswith("phục hồi"), h
    # không còn bộ đã công bố -> bộ bàn giao; không còn gì -> 503 ở mọi endpoint
    an = [(TAM / DG.THU_MUC_CONG_BO, TAM / "an_cong_bo")]
    shutil.move(*an[0])
    try:
        hb, post, h = phien_ban_sau_khoi_dong()
        assert h["nguon"].startswith("phục hồi (bản kê hiện tại lỗi): bộ bàn giao") and hb == post, h
        shutil.move(TAM / DG.BAN_GIAO, TAM / "an_ban_giao")
        try:
            khoi_dong_lai()
            for _ in range(2):
                for ma in (c.get("/health"), c.get("/tong-quan"), c.get("/nha-pho"), c.get("/nha-pho/1"), c.get("/ban-do"),
                           c.get("/danh-gia"), c.get("/xu-huong"), c.get("/danh-muc"), c.post("/dinh-gia/nha-pho", json=NHA),
                           c.post("/dinh-gia/can-ho", json={"dt_su_dung": 60}), c.post("/tro-ly/y-dinh", json={"cau": "xin chào"})):
                    assert ma.status_code == 503, (ma.url, ma.status_code, ma.text[:200])
        finally:
            shutil.move(TAM / "an_ban_giao", TAM / DG.BAN_GIAO)
    finally:
        shutil.move(TAM / "an_cong_bo", TAM / DG.THU_MUC_CONG_BO)
    WEB.write_bytes(goc_web); Q = cong_bo()                                           # công bố thành công -> bình thường
    dung_duoc(Q["id"])
    assert c.get("/health").json()["nguon"] == DG.MANIFEST
    assert phien_ban_sau_khoi_dong()[:2] == (Q["id"], Q["id"])


@kiem("Công bố chép bộ vào models/cong_bo/<mã>/: pipeline ghi đè tệp làm việc (chưa công bố) rồi API khởi động lại -> "
      "vẫn nạp bộ đã công bố; chỉ giữ bộ hiện tại + bộ trước")
def _():
    A = cong_bo()
    assert (TAM / A["thu_muc"] / "models/mo_hinh_gia_nha.joblib").exists()
    goc = WEB.read_bytes()
    WEB.write_text("{đang ghi dở", encoding="utf-8")                  # pipeline đang chạy / đã lỗi giữa chừng
    khoi_dong_lai() # API khởi động lại
    dung_duoc(A["id"])
    WEB.write_bytes(goc); doi_ngay("03/03/2099"); B = cong_bo(); doi_ngay("04/04/2099"); C = cong_bo()
    con = {d.name for d in (TAM / DG.THU_MUC_CONG_BO).iterdir()}
    assert con == {B["id"], C["id"]}, con
    dung_duoc(C["id"])


@kiem("Bản kê models/phien_ban.json biến mất: đang chạy -> giữ bộ đang phục vụ, /health báo; khởi động lại -> bộ ĐÃ công bố "
      "gần nhất (không phải ứng viên công bố lỗi, không phải bộ bàn giao); công bố hợp lệ tiếp theo -> phục vụ bộ mới")
def _():
    doi_ngay("05/05/2099"); X = cong_bo()
    dung_duoc(X["id"])
    goc = WEB.read_bytes()
    WEB.write_text("{hỏng", encoding="utf-8"); tu_choi("ứng viên hỏng")      # để lại thư mục ứng viên KHÔNG có dấu công bố
    WEB.write_bytes(goc); doi_ngay("06/06/2099")                              # đầu ra mới hợp lệ nhưng chưa công bố
    (TAM / DG.MANIFEST).unlink(); time.sleep(0.05)
    h = c.get("/health").json()
    assert h["phien_ban"] == X["id"] and "không còn" in (h["loi_nap_moi_nhat"] or ""), h
    assert c.post("/dinh-gia/nha-pho", json=NHA).json()["phien_ban"] == X["id"]
    khoi_dong_lai()
    h = c.get("/health").json()
    assert h["phien_ban"] == X["id"] and h["nguon"].startswith("bộ đã công bố") and h["ngay_du_lieu"] == "05/05/2099", h
    dung_duoc(X["id"])
    Y = cong_bo()                                                             # pipeline qua kiểm thử -> công bố
    assert Y["id"] != X["id"]
    dung_duoc(Y["id"])
    assert c.get("/health").json()["ngay_du_lieu"] == "06/06/2099"


@kiem("Thiếu tệp bắt buộc -> không công bố được, bản kê cũ giữ nguyên")
def _():
    truoc = (TAM / DG.MANIFEST).read_text(encoding="utf-8")
    f = TAM / "dataset/processed/nha_da_xu_ly.csv"; tam = f.with_suffix(".bak"); f.rename(tam)
    try:
        DG.cong_bo(); raise AssertionError("cong_bo không báo lỗi khi thiếu tệp")
    except FileNotFoundError:
        pass
    finally:
        tam.rename(f)
    assert (TAM / DG.MANIFEST).read_text(encoding="utf-8") == truoc


def cong_trong():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p


def may_chu_gia(ma, than):                       # máy chủ HTTP giả trả cố định (ma, than) cho mọi yêu cầu
    class H(http.server.BaseHTTPRequestHandler):
        def _tra(self):
            b = json.dumps(than).encode(); self.send_response(ma); self.send_header("content-length", str(len(b)))
            self.end_headers(); self.wfile.write(b)
        do_GET = do_POST = _tra
        log_message = lambda *a: None
    s = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=s.serve_forever, daemon=True).start()
    return s, f"http://127.0.0.1:{s.server_address[1]}"


@kiem("Pipeline phân biệt: API tắt -> BỎ QUA; HTTP 500 -> LỖI; /health thiếu trường (mã cũ) -> LỖI; khác bộ -> LỖI")
def _():
    tt, ct = chay_toan_bo.kiem_api_dang_chay(f"http://127.0.0.1:{cong_trong()}", TAM)
    assert tt == "BỎ QUA", (tt, ct)
    for ma, than, mong in ((500, {"detail": "x"}, "HTTP 500"), (200, {"ok": True, "ngay_du_lieu": "x"}, "thiếu trường"),
                           (200, {"ok": True, "phien_ban": "khac", "tep": {}, "mo_hinh": "RF", "loi_nap_moi_nhat": None}, "phục vụ bộ khac")):
        s, url = may_chu_gia(ma, than)
        try:
            if mong.startswith("phục vụ"):
                chay_toan_bo.time.sleep, ngu = (lambda _: None), chay_toan_bo.time.sleep   # bỏ 6 lần chờ 2 giây
            tt, ct = chay_toan_bo.kiem_api_dang_chay(url, TAM)
        finally:
            if mong.startswith("phục vụ"):
                chay_toan_bo.time.sleep = ngu
            s.shutdown()
        assert tt == "LỖI" and mong in ct, (ma, tt, ct)


@kiem("API thật (uvicorn, chạy trên bản sao) sau khi công bố bộ mới: pipeline kiểm chứng ĐẠT, POST trả đúng mã bộ")
def _():
    p = cong_trong()
    sv = uvicorn.Server(uvicorn.Config(main.app, host="127.0.0.1", port=p, log_level="error"))
    th = threading.Thread(target=sv.run, daemon=True); th.start()
    for _ in range(100):
        if sv.started:
            break
        time.sleep(0.1)
    try:
        doi_ngay("02/02/2099"); bk = cong_bo()
        tt, ct = chay_toan_bo.kiem_api_dang_chay(f"http://127.0.0.1:{p}", TAM)
        assert tt == "ĐẠT" and bk["id"] in ct, (tt, ct)
    finally:
        sv.should_exit = True; th.join(10)


shutil.rmtree(TAM, ignore_errors=True)
for ten, ok, loi in KQ:
    print(("ĐẠT       " if ok else "KHÔNG ĐẠT ") + ten + ("" if ok else f"\n           -> {loi}"))
print(f"\n{sum(ok for _, ok, _ in KQ)}/{len(KQ)} phép kiểm đạt")
sys.exit(0 if all(ok for _, ok, _ in KQ) else 1)
