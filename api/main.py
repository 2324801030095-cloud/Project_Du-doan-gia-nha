"""Dịch vụ mô hình (FastAPI): đọc dữ liệu và mô hình do notebook sinh ra, trả JSON cho ứng dụng web.
Chạy:  uvicorn main:app --app-dir api --port 8000      (tài liệu API tự sinh: http://localhost:8000/docs)
Không có đăng nhập ở đây: dịch vụ chỉ mở trong mạng nội bộ của Docker; web (Next.js) kiểm tra phiên người dùng."""
import json
from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

import dinh_gia as DG

app = FastAPI(title="API định giá nhà Phú Hòa", version="1.0",
              description="Mô hình học máy của đề tài: nhà phố Phú Hòa (Random Forest, bài chính); căn hộ, giá thuê, trợ lý ý định (mở rộng).")


def _web():
    return DG.du_lieu_web()


@app.get("/health")
def health():
    """ngay_du_lieu + phien_ban (mã băm mô hình / dữ liệu ĐANG phục vụ) để kiểm chứng API đã nạp bản mới nhất."""
    return {"ok": True, "ngay_du_lieu": _web()["SO_LIEU"]["NGAY"], "phien_ban": DG.phien_ban()}


@app.get("/tong-quan")
def tong_quan():
    """Các con số tóm tắt cho trang chủ và trang mô hình."""
    w = _web()
    dg = json.loads((DG.MODELS / "danh_gia_mo_hinh.json").read_text(encoding="utf-8"))
    return {"so_lieu": w["SO_LIEU"], "do_phu_test_80": dg.get("do_phu_test_80"), "chat_luong_du_lieu": dg.get("chat_luong_du_lieu"), "bang_mo_hinh": [dict(zip(["mo_hinh", "mae_ty", "mape", "r2"], r)) for r in w["MODEL_TABLE"]],
            "giai_thich": w["GT_META"], "web_model": {k: w["MODEL"][k] for k in ("model", "cv_mape", "mo_hinh_day_du", "mo_hinh_day_du_mape_cv_phu_hoa")},
            "can_ho": {k: w["CH_MODEL"].get(k) for k in ("mo_hinh_day_du", "mo_hinh_day_du_mape", "cv_mape", "so_can")},
            "thue": {k: w["THUE"].get(k) for k in ("mape", "so_tin", "ty_suat_tv")}}


@app.get("/danh-gia")
def danh_gia():
    """Bảng đánh giá của notebook nhà phố (bài chính) và căn hộ (mở rộng): kiểm định chéo, tập test, chọn mô hình."""
    # căn hộ là phần mở rộng: chỉ trả nếu notebook căn hộ đã chạy
    return {k: json.loads((DG.MODELS / f"danh_gia_mo_hinh{s}.json").read_text(encoding="utf-8"))
            for k, s in (("nha_pho", ""), ("can_ho", "_can_ho")) if (DG.MODELS / f"danh_gia_mo_hinh{s}.json").exists()}


# ---------------- danh sách tin ----------------
CHAN_DOAN = Literal["Rẻ hơn thị trường", "Hợp lý", "Cao hơn thị trường"]


def _loc(ds, khoa_gia, khoa_dt, gia_min, gia_max, dt_min, dt_max, chan_doan, khoa_cd, tu_khoa, khoa_chu, sap_xep, trang, so_dong):
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


def _nha_ds():
    return [{**x, "id": str(x["id"]), "_lech": x["g"] / x["ai_full"] - 1} for x in _web()["LISTINGS"]]


SAP_XEP = Literal["gia_tang", "gia_giam", "dt_giam", "re_nhat"]


@app.get("/nha-pho")
def nha_pho(gia_min: float | None = None, gia_max: float | None = None, dt_min: float | None = None, dt_max: float | None = None,
            chan_doan: CHAN_DOAN | None = None, q: str | None = None, sap_xep: SAP_XEP = "re_nhat",
            trang: int = Query(1, ge=1), so_dong: int = Query(12, ge=1, le=200)):
    """Tin nhà phố Phú Hòa còn rao ở kỳ thu thập mới nhất, kèm giá ước lượng, khoảng 80%, chẩn đoán."""
    return _loc(_nha_ds(), "g", "dt", gia_min, gia_max, dt_min, dt_max, chan_doan, "chan_doan", q, ("t", "duong"), sap_xep, trang, so_dong)


@app.get("/nha-pho/{ma}")
def nha_pho_chi_tiet(ma: str):
    x = next((x for x in _nha_ds() if x["id"] == ma), None)
    if x is None:
        raise HTTPException(404, "Không có tin này (có thể đã gỡ ở kỳ thu thập mới nhất)")
    return x


@app.get("/nha-pho-theo-ma")
def nha_pho_theo_ma(ma: list[str] = Query(default=[])):
    """Nhiều tin cùng lúc (trang yêu thích, so sánh)."""
    tap = set(ma)
    return [x for x in _nha_ds() if x["id"] in tap]


@app.get("/can-ho")
def can_ho(gia_min: float | None = None, gia_max: float | None = None, dt_min: float | None = None, dt_max: float | None = None,
           chan_doan: CHAN_DOAN | None = None, q: str | None = None, sap_xep: SAP_XEP = "re_nhat",
           trang: int = Query(1, ge=1), so_dong: int = Query(12, ge=1, le=200)):
    ds = [{**x, "_lech": x["diff"]} for x in _web()["CH_LIST"]]
    return _loc(ds, "g", "dt", gia_min, gia_max, dt_min, dt_max, chan_doan, "cd", q, ("da", "ph"), sap_xep, trang, so_dong)


@app.get("/ban-do")
def ban_do():
    """Điểm trên bản đồ: [lat, lon, đơn giá triệu/m², loại, giá, tiêu đề, link] (nhà phố, cho thuê) + tòa căn hộ."""
    w = _web()
    return {"diem": [d for d in w["MAP_PTS"] if d[3] != "dat"], "toa_can_ho": [{k: v for k, v in t.items() if k != "can"} for t in w["CH_TOA"]]}


@app.get("/xu-huong")
def xu_huong():
    return _web()["TREND"]


@app.get("/danh-muc")
def danh_muc():
    """Danh mục cho các ô chọn của form: dự án và phường (căn hộ), tuyến đường Phú Hòa."""
    w = _web()
    return {"du_an": [{k: d[k] for k in ("ma", "ten", "so_tin", "quan", "phuong")} for d in w["CH_MODEL"].get("du_an", [])],
            "phuong_can_ho": w["CH_PHUONG"],
            "duong_phu_hoa": ["Nguyễn Thị Minh Khai", "Lê Hồng Phong", "Phú Lợi", "Nguyễn Thái Bình", "30/4", "Đại lộ Bình Dương", "Trần Văn Ơn", "Huỳnh Thị Hiếu"]}


# ---------------- định giá ----------------
class NhaPho(BaseModel):
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
    if not (DG.MODELS / "mo_hinh_gia_can_ho.joblib").exists():
        raise HTTPException(503, "Chưa có mô hình căn hộ (phần mở rộng): chạy notebook du_doan_gia_can_ho")
    return DG.dinh_gia_can_ho(**x.model_dump())


class Cau(BaseModel):
    cau: str = Field(min_length=1, max_length=500)


@app.post("/tro-ly/y-dinh")
def tro_ly_y_dinh(x: Cau):
    """Ý định của câu hỏi theo mô hình TF-IDF + Logistic Regression (notebook trợ lý)."""
    return DG.y_dinh(x.cau)
