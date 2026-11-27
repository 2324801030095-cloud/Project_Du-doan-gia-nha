"""Dịch vụ mô hình (FastAPI): đọc dữ liệu và mô hình do notebook sinh ra, trả JSON cho ứng dụng web.
Chạy:  uvicorn main:app --app-dir api --port 8000      (tài liệu API tự sinh: http://localhost:8000/docs)
Không có đăng nhập ở đây: dịch vụ chỉ mở trong mạng nội bộ của Docker; web (Next.js) kiểm tra phiên người dùng."""
from typing import Literal

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

import dinh_gia as DG

app = FastAPI(title="API định giá nhà Phú Hòa", version="1.0",
              description="Mô hình học máy của đề tài: nhà phố Phú Hòa (Random Forest, bài chính); căn hộ, giá thuê, trợ lý ý định (mở rộng).")


def _web():
    """Dữ liệu web (models/du_lieu_web.json) của bộ đang phục vụ; chưa có bộ hợp lệ -> LoiNapBo -> 503."""
    return DG.bo()["web"]


def _kiem_endpoint(B):
    """Chạy thử đường xử lý của các endpoint dữ liệu trên bộ ỨNG VIÊN trước khi API chuyển sang bộ đó (dinh_gia.KIEM_BO)."""
    _health(B); _tong_quan(B); _ban_do(B["web"]); _danh_muc(B["web"]); _can_ho_ds(B["web"])
    ds = _nha_ds(B["web"])
    _loc(ds, "g", "dt", None, None, None, None, None, "chan_doan", "a", ("t", "duong"), "re_nhat", 1, 12)


@app.exception_handler(DG.LoiNapBo)
def _loi_nap(_: Request, e: DG.LoiNapBo):
    """Mọi LoiNapBo (chưa có bộ hợp lệ, thiếu phần mở rộng) -> HTTP 503 kèm lý do, thay cho 500."""
    return JSONResponse(status_code=503, content={"detail": str(e)})


@app.get("/health")
def health():
    """Bộ tệp ĐANG phục vụ (đã nạp xong, kể cả Random Forest): mã bộ = id của models/phien_ban.json đã công bố,
    mã băm từng tệp, thời điểm nạp; loi_nap_moi_nhat khác null nghĩa là bản kê mới nhất KHÔNG nạp được (đang giữ bộ cũ)."""
    try:
        B = DG.bo()
    except DG.LoiNapBo as e:                     # chưa có bộ hợp lệ nào
        return JSONResponse(status_code=503, content={"ok": False, "loi_nap_moi_nhat": str(e)})
    tt = DG.trang_thai()
    return {**_health(B), "nguon": tt["nguon"], "loi_nap_moi_nhat": tt["loi_nap"]}


def _health(B):
    """Thông tin bộ tệp B: mã bộ (phien_ban), mã băm rút gọn từng tệp, thời điểm công bố / nạp, tên mô hình, ngày dữ liệu."""
    return {"ok": True, "phien_ban": B["id"], "tep": B["tep"], "cong_bo_luc": B["cong_bo_luc"], "nap_luc": B["nap_luc"] if "nap_luc" in B else None,
            "mo_hinh": B["nha"][0]["ten"], "ngay_du_lieu": B["web"]["SO_LIEU"]["NGAY"]}


@app.get("/tong-quan")
def tong_quan():
    """Các con số tóm tắt cho trang chủ và trang mô hình."""
    return _tong_quan(DG.bo())


def _tong_quan(B):
    """Số liệu tóm tắt lấy từ bộ B (dùng chung cho endpoint và cho bước chạy thử bộ ứng viên)."""
    w, dg = B["web"], B["danh_gia"]
    return {"so_lieu": w["SO_LIEU"], "do_phu_test_80": dg.get("do_phu_test_80"), "chat_luong_du_lieu": dg.get("chat_luong_du_lieu"), "bang_mo_hinh": [dict(zip(["mo_hinh", "mae_ty", "mape", "r2"], r)) for r in w["MODEL_TABLE"]],
            "giai_thich": w["GT_META"], "web_model": {k: w["MODEL"][k] for k in ("model", "cv_mape", "mo_hinh_day_du", "mo_hinh_day_du_mape_cv_phu_hoa")},
            "can_ho": {k: w["CH_MODEL"].get(k) for k in ("mo_hinh_day_du", "mo_hinh_day_du_mape", "cv_mape", "so_can")},
            "thue": {k: w["THUE"].get(k) for k in ("mape", "so_tin", "ty_suat_tv")}}


@app.get("/danh-gia")
def danh_gia():
    """Bảng đánh giá của notebook nhà phố (bài chính) và căn hộ (mở rộng): kiểm định chéo, tập test, chọn mô hình."""
    # căn hộ là phần mở rộng: chỉ trả nếu notebook căn hộ đã chạy
    B = DG.bo()
    return {"nha_pho": B["danh_gia"], **({"can_ho": B["danh_gia_can_ho"]} if B["danh_gia_can_ho"] else {})}


# ---------------- danh sách tin ----------------
CHAN_DOAN = Literal["Rẻ hơn thị trường", "Hợp lý", "Cao hơn thị trường"]


def _loc(ds, khoa_gia, khoa_dt, gia_min, gia_max, dt_min, dt_max, chan_doan, khoa_cd, tu_khoa, khoa_chu, sap_xep, trang, so_dong):
    """Lọc + sắp xếp + phân trang danh sách tin.
    khoa_gia / khoa_dt: tên trường giá (tỷ đồng) và diện tích (m²) trong từng tin; chan_doan: 'Rẻ hơn thị trường' /
    'Hợp lý' / 'Cao hơn thị trường' (so giá rao với khoảng 80% của mô hình); tu_khoa tìm không phân biệt hoa thường
    trong các trường khoa_chu; sap_xep 're_nhat' = lệch âm nhiều nhất (giá rao thấp nhất so với giá mô hình) trước."""
    ra = [x for x in ds
          if (gia_min is None or x[khoa_gia] >= gia_min) and (gia_max is None or x[khoa_gia] <= gia_max)
          and (dt_min is None or x[khoa_dt] >= dt_min) and (dt_max is None or x[khoa_dt] <= dt_max)
          and (chan_doan is None or x.get(khoa_cd) == chan_doan)
          and (not tu_khoa or any(tu_khoa.lower() in str(x.get(k) or "").lower() for k in khoa_chu))]
    khoa = {"gia_tang": (khoa_gia, False), "gia_giam": (khoa_gia, True), "dt_giam": (khoa_dt, True),
            "re_nhat": ("_lech", False)}[sap_xep]
    if khoa[0] == "_lech":
        ra.sort(key=lambda x: x["_lech"])
    else:
        ra.sort(key=lambda x: x[khoa[0]], reverse=khoa[1])
    return {"tong": len(ra), "trang": trang, "so_dong": so_dong, "ket_qua": ra[(trang - 1) * so_dong: trang * so_dong]}


def _nha_ds(w=None):
    """Danh sách tin nhà phố còn rao ở kỳ thu thập mới nhất. Trường g = giá rao (tỷ), dt = diện tích đất (m²),
    ai_full = giá mô hình (tỷ); _lech = g / ai_full - 1 (âm = rao rẻ hơn giá mô hình) dùng để sắp xếp."""
    return [{**x, "id": str(x["id"]), "_lech": x["g"] / x["ai_full"] - 1} for x in (w or _web())["LISTINGS"]]


SAP_XEP = Literal["gia_tang", "gia_giam", "dt_giam", "re_nhat"]


@app.get("/nha-pho")
def nha_pho(gia_min: float | None = None, gia_max: float | None = None, dt_min: float | None = None, dt_max: float | None = None,
            chan_doan: CHAN_DOAN | None = None, q: str | None = None, sap_xep: SAP_XEP = "re_nhat",
            trang: int = Query(1, ge=1), so_dong: int = Query(12, ge=1, le=200)):
    """Tin nhà phố Phú Hòa còn rao ở kỳ thu thập mới nhất, kèm giá ước lượng, khoảng 80%, chẩn đoán."""
    return _loc(_nha_ds(), "g", "dt", gia_min, gia_max, dt_min, dt_max, chan_doan, "chan_doan", q, ("t", "duong"), sap_xep, trang, so_dong)


@app.get("/nha-pho/{ma}")
def nha_pho_chi_tiet(ma: str):
    """Một tin nhà phố theo mã; tin đã gỡ ở kỳ mới nhất -> 404."""
    x = next((x for x in _nha_ds() if x["id"] == ma), None)
    if x is None:
        raise HTTPException(404, "Không có tin này (có thể đã gỡ ở kỳ thu thập mới nhất)")
    return x


@app.get("/nha-pho-theo-ma")
def nha_pho_theo_ma(ma: list[str] = Query(default=[])):
    """Nhiều tin cùng lúc (trang yêu thích, so sánh)."""
    tap = set(ma)
    return [x for x in _nha_ds() if x["id"] in tap]


def _can_ho_ds(w):
    """Danh sách tin căn hộ (mở rộng); diff = độ lệch giá rao so với giá mô hình, dùng để sắp xếp như nhà phố."""
    return [{**x, "_lech": x["diff"]} for x in w["CH_LIST"]]


@app.get("/can-ho")
def can_ho(gia_min: float | None = None, gia_max: float | None = None, dt_min: float | None = None, dt_max: float | None = None,
           chan_doan: CHAN_DOAN | None = None, q: str | None = None, sap_xep: SAP_XEP = "re_nhat",
           trang: int = Query(1, ge=1), so_dong: int = Query(12, ge=1, le=200)):
    """Tin căn hộ (phần mở rộng) với cùng bộ lọc như /nha-pho; bộ chỉ có bài chính thì danh sách rỗng."""
    return _loc(_can_ho_ds(_web()), "g", "dt", gia_min, gia_max, dt_min, dt_max, chan_doan, "cd", q, ("da", "ph"), sap_xep, trang, so_dong)


@app.get("/ban-do")
def ban_do():
    """Điểm trên bản đồ: [lat, lon, đơn giá triệu/m², loại, giá, tiêu đề, link] (nhà phố, cho thuê) + tòa căn hộ."""
    return _ban_do(_web())


def _ban_do(w):
    """Điểm bản đồ (bỏ điểm đất nền của phiên bản cũ) + tòa căn hộ (bỏ danh sách căn chi tiết cho nhẹ)."""
    return {"diem": [d for d in w["MAP_PTS"] if d[3] != "dat"], "toa_can_ho": [{k: v for k, v in t.items() if k != "can"} for t in w["CH_TOA"]]}


@app.get("/xu-huong")
def xu_huong():
    """Chỉ số giá theo kỳ thu thập và dự báo (phần mở rộng; rỗng nếu chưa chạy notebook xu hướng)."""
    return _web()["TREND"]


@app.get("/danh-muc")
def danh_muc():
    """Danh mục cho các ô chọn của form: dự án và phường (căn hộ), tuyến đường Phú Hòa."""
    return _danh_muc(_web())


def _danh_muc(w):
    """Danh mục cho ô chọn của form từ bộ dữ liệu web w."""
    return {"du_an": [{k: d[k] for k in ("ma", "ten", "so_tin", "quan", "phuong")} for d in w["CH_MODEL"].get("du_an", [])],
            "phuong_can_ho": w["CH_PHUONG"],
            "duong_phu_hoa": ["Nguyễn Thị Minh Khai", "Lê Hồng Phong", "Phú Lợi", "Nguyễn Thái Bình", "30/4", "Đại lộ Bình Dương", "Trần Văn Ơn", "Huỳnh Thị Hiếu"]}


# ---------------- định giá ----------------
class NhaPho(BaseModel):
    """Đầu vào định giá nhà phố. Diện tích m², chiều dài m; giới hạn để chặn số vô lý (lỗi 422).
    Trường để trống = không biết: mô hình điền trung vị đã học, không coi là 0."""
    dt_dat: float = Field(gt=10, le=5000, description="Diện tích đất (m²)")
    ngang: float | None = Field(None, gt=0, le=200)
    dai: float | None = Field(None, gt=0, le=500)
    so_tang: float | None = Field(None, ge=1, le=10)
    dt_san: float | None = Field(None, gt=0, le=20000)
    phong_ngu: float | None = Field(None, ge=0, le=30)
    so_wc: float | None = Field(None, ge=0, le=30)
    mat_tien_duong: int = Field(0, ge=0, le=1)
    cap_loi_vao: float | None = Field(None, ge=1, le=5, description="1 hẻm nhỏ … 5 mặt tiền đường lớn")
    hem_rong: float | None = Field(None, gt=0, le=60)
    duong: str | None = Field(None, max_length=80)
    phuong: str = Field("phu hoa", max_length=60)
    mo_ta: str = Field("", max_length=4000)


class CanHo(BaseModel):
    """Đầu vào định giá căn hộ (mở rộng): dt_su_dung = diện tích sử dụng (m²); nha_o_xa_hoi 0/1."""
    dt_su_dung: float = Field(gt=15, le=500)
    du_an: str | None = Field(None, max_length=120)
    phong_ngu: float | None = Field(None, ge=0, le=6)
    so_wc: float | None = Field(None, ge=0, le=6)
    tang: float | None = Field(None, ge=0, le=60)
    so_hong: int | None = Field(None, ge=0, le=1)
    noi_that_cap: float | None = Field(None, ge=0, le=3)
    nha_o_xa_hoi: int = Field(0, ge=0, le=1)
    phuong: str = Field("phu hoa", max_length=60)
    mo_ta: str = Field("", max_length=4000)


@app.post("/dinh-gia/nha-pho")
def dinh_gia_nha_pho(x: NhaPho):
    """Random Forest (mô hình cuối của đề tài) + khoảng 80% + giải thích theo nhóm yếu tố + giá thuê ước tính."""
    return DG.dinh_gia_nha(**x.model_dump())


@app.post("/dinh-gia/can-ho")
def dinh_gia_can_ho(x: CanHo):
    """Định giá căn hộ (mở rộng); bộ không có mô hình căn hộ -> 503."""
    return DG.dinh_gia_can_ho(**x.model_dump())


class Cau(BaseModel):
    """Câu hỏi gửi trợ lý (1–500 ký tự)."""
    cau: str = Field(min_length=1, max_length=500)


@app.post("/tro-ly/y-dinh")
def tro_ly_y_dinh(x: Cau):
    """Ý định của câu hỏi theo mô hình TF-IDF + Logistic Regression (notebook trợ lý)."""
    return DG.y_dinh(x.cau)


DG.KIEM_BO.append(_kiem_endpoint)
