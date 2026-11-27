"""Dựng lại trang demo sau khi chạy lại 2 notebook:  python demo/build/build_site.py
Đọc: models/mo_hinh_gia_nha.json (mô hình Ridge rút gọn cho trình duyệt), models/danh_gia_mo_hinh.json,
     models/xu_huong_gia.json, dataset/processed/*_da_xu_ly.csv (+ các file dataset/raw/*_raw.csv để lấy tên đường/hướng có dấu).
Ghi: demo/index.html (bản tĩnh chạy offline) và models/du_lieu_web.json (dữ liệu cho web/ và api/)"""
import json
import os
import re
import sys

import numpy as np
import pandas as pd

S = os.path.dirname(os.path.abspath(__file__)); DEMO = os.path.dirname(S); ROOT = os.path.dirname(DEMO)
J = lambda *p: os.path.join(ROOT, *p)
tpl = open(os.path.join(S, "template.html"), encoding="utf-8").read()
MODEL = json.load(open(J("models", "mo_hinh_gia_nha.json"), encoding="utf-8"))
DG = json.load(open(J("models", "danh_gia_mo_hinh.json"), encoding="utf-8"))
# Bắt buộc: kết quả notebook nhà phố. Tùy chọn (phần mở rộng): căn hộ, xu hướng, giá thuê, đất (lưu trữ), trợ lý.
# Thiếu phần nào thì phần đó để trống -> chạy được khi chỉ có đầu vào / đầu ra của bài chính (scripts/chay_toan_bo.py --nha-pho).
CHI_DU_LIEU = "--chi-du-lieu" in sys.argv        # chỉ xuất models/du_lieu_web.json cho API, không dựng trang HTML tĩnh
doc = lambda *p: json.load(open(J(*p), encoding="utf-8")) if os.path.exists(J(*p)) else None
TREND = doc("models", "xu_huong_gia.json") or {}
df = pd.read_csv(J("dataset", "processed", "nha_da_xu_ly.csv"), dtype={"id": str})

# ---- thông tin hiển thị có dấu, lấy từ dữ liệu gốc ----
g = pd.read_csv(J("dataset", "raw", "nha_phu_hoa_guland_raw.csv"), dtype={"id": str}).set_index("id")
c = pd.read_csv(J("dataset", "raw", "chotot_binh_duong_raw.csv"), dtype={"id": str}).set_index("id")
a = pd.read_csv(J("dataset", "raw", "alonhadat_tdm_raw.csv"), dtype={"id": str}).set_index("id")
HUONG_CT = {1: "Đông", 2: "Tây", 3: "Nam", 4: "Bắc", 5: "Đông Bắc", 6: "Đông Nam", 7: "Tây Bắc", 8: "Tây Nam"}
def nv(v):
    return None if v is None or (isinstance(v, float) and np.isnan(v)) else v
def hien_thi(r):
    i, n = r["id"], r["nguon"]
    if n == "guland" and i in g.index:
        x = g.loc[i]; return dict(duong=nv(x["duong"]), huong=nv(x["huong"]), so=nv(x["loai_so"]), cn=nv(x["cap_nhat"]), hd=nv(x["hien_trang_duong"]))
    if n == "chotot" and i in c.index:
        x = c.loc[i]; return dict(duong=nv(x["duong"]), huong=HUONG_CT.get(nv(x["huong"])), so=nv(x["phap_ly"]),
                                  cn="Đăng " + pd.to_datetime(x["ngay_dang"]).strftime("%d/%m/%Y"), hd=None)
    if n == "alonhadat" and i in a.index:
        x = a.loc[i]; return dict(duong=str(x["dia_chi_cu"]).split(",")[0], huong=nv(x["huong"]), so=None,
                                  cn="Đăng " + pd.to_datetime(x["ngay_dang"]).strftime("%d/%m/%Y"), hd=None)
    return dict(duong=None, huong=None, so=None, cn=None, hd=None)

# Notebook học trên MỌI kỳ thu thập (gồm cả tin đã gỡ); trang chỉ hiển thị tin CÒN RAO ở kỳ mới nhất của từng nguồn
con_rao = lambda d: (d["ngay_thu_thap"].astype(str) == d.groupby("nguon")["ngay_thu_thap"].transform("max").astype(str)) if "ngay_thu_thap" in d else pd.Series(True, index=d.index)
ph_tat_ca = df[df["phuong"] == "phu hoa"].copy()
ph = ph_tat_ca[con_rao(ph_tat_ca)].copy()
L = []
for _, r in ph.iterrows():
    num = lambda k, d=1: None if pd.isna(r[k]) else round(float(r[k]), d)
    st = None if pd.isna(r["so_tang"]) else min(float(r["so_tang"]), 4.0)
    vt = None if pd.isna(r["cap_loi_vao"]) else int(np.floor(r["cap_loi_vao"]))
    duong = str(r["duong"] or "")
    o = {"id": int(re.sub(r"\D", "", str(r["id"]))[:12] or 0), "t": str(r["tieu_de"])[:90], "g": round(float(r["gia_ty"]), 3),
         "dt": round(float(r["dt_dat"]), 1), "mt": num("ngang"), "st": st, "san": num("dt_san", 0), "pn": num("phong_ngu", 0),
         "wc": num("so_wc", 0), "vt": vt, "hr": num("hem_rong"), "ntmk": int("minh khai" in duong), "lhp": int("le hong phong" in duong),
         "nt": int(r["noi_that"] == 1), "url": r["url"], "nguon": r["nguon"],
         "ai_full": round(float(r["gia_uoc_luong_ty"]), 3), "lo80": round(float(r["khoang80_thap"]), 2), "hi80": round(float(r["khoang80_cao"]), 2),
         "chan_doan": r["chan_doan"]}
    o.update(hien_thi(r))
    L.append(o)

cv = [[m["Mô hình"], m["MAE (tỷ)"], m["MAPE (%)"], m["R²"]] for m in DG["kiem_dinh_cheo_phu_hoa"]]
best = DG["ten_mo_hinh"]
cv.sort(key=lambda x: (x[0] != best, x[2]))          # mô hình được chọn lên đầu
data = ["const MODEL = " + json.dumps(MODEL, ensure_ascii=False) + ";",
        "const LISTINGS = " + json.dumps(L, ensure_ascii=False) + ";",
        "const MODEL_TABLE = " + json.dumps(cv, ensure_ascii=False) + ";",
        "const TREND = " + json.dumps(TREND, ensure_ascii=False) + ";"]

# ---- số liệu trong nội dung tĩnh: lấy từ kiểm định chéo lặp (chia theo nhóm) trên các căn Phú Hòa ----
cvp = {m["Mô hình"]: m for m in DG["kiem_dinh_cheo_phu_hoa"]}
bl = cvp["Baseline (đơn giá phường)"]
v1 = next(m for m in DG["kiem_chung_phu_hoa"] if m["Mô hình"].startswith("Cách làm phiên bản 1"))
te = next(m for m in DG["test_phu_hoa"] if m["Mô hình"] == best)
vn = lambda v, d=1: f"{v:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")
raw_n = sum(len(pd.read_csv(J("dataset", "raw", f))) for f in ["nha_phu_hoa_guland_raw.csv", "alonhadat_tdm_raw.csv"]) + int((c["loai_tin"] == "ban").sum())
TOK = {"BEST": best, "N_PH": str(len(ph)), "N_ALL": vn(len(df), 0), "N_RAW": vn(raw_n, 0),
       "NGAY": pd.to_datetime(c["ngay_thu_thap"].iloc[0]).strftime("%d/%m/%Y"),
       "T_MAPE": vn(cvp[best]["MAPE (%)"]), "T_LO": vn(cvp[best]["MAPE thấp (95%)"]), "T_HI": vn(cvp[best]["MAPE cao (95%)"]),
       "B_MAPE": vn(bl["MAPE (%)"]), "V1_MAPE": vn(v1["MAPE (%)"]),
       "T_MDAPE": vn(cvp[best]["MdAPE (%)"]), "B_MDAPE": vn(bl["MdAPE (%)"]), "V1_MDAPE": vn(v1["MdAPE (%)"]),
       "T_W20": vn(cvp[best]["Trong ±20% (%)"], 0), "B_W20": vn(bl["Trong ±20% (%)"], 0), "WEB_MAPE": vn(MODEL["cv_mape"]),
       "TEST_N": str(int(te["Số căn"])), "TEST_MAPE": vn(te["MAPE (%)"]), "TEST_LO": vn(te["MAPE thấp (95%)"]), "TEST_HI": vn(te["MAPE cao (95%)"])}
# ---- căn hộ chung cư (notebook du_doan_gia_can_ho.ipynb – phần mở rộng, tùy chọn) ----
CO_CH = all(os.path.exists(J(*f)) for f in [("models", "mo_hinh_gia_can_ho.json"), ("models", "danh_gia_mo_hinh_can_ho.json"),
                                            ("dataset", "processed", "can_ho_da_xu_ly.csv"), ("dataset", "raw", "chotot_can_ho_raw.csv")])
if CO_CH:
    CH, CH_DG = doc("models", "mo_hinh_gia_can_ho.json"), doc("models", "danh_gia_mo_hinh_can_ho.json")
    chd = pd.read_csv(J("dataset", "processed", "can_ho_da_xu_ly.csv"), dtype={"id": str})
    raw_ch = pd.read_csv(J("dataset", "raw", "chotot_can_ho_raw.csv"))
else:
    CH, CH_DG = {"phuong": {}}, {"so_can": {"tat_ca": 0, "du_an": 0}}
    chd = pd.DataFrame(columns=["id", "quan", "phuong", "du_an", "du_an_goc", "dt_dat", "phong_ngu", "gia_ty", "gia_uoc_luong_ty",
                                "khoang80_thap", "khoang80_cao", "chan_doan", "url", "lat", "lon", "muc_toa_do", "tieu_de"])
    raw_ch = pd.DataFrame(columns=["phuong", "ngay_thu_thap"])
    print("Không có kết quả notebook căn hộ: bỏ qua phần căn hộ.")
sys.path.insert(0, J("src"))
from mo_hinh_gia import ten_phuong as _tp

ten_ph = {}
for w in raw_ch["phuong"].dropna().unique():
    ten_ph.setdefault(_tp(w), re.sub(r"^(Phường|Xã|Thị trấn)\s*", "", w))
CH_PHUONG = sorted([{"k": k, "ten": ten_ph.get(k.split("|")[1], k.split("|")[1].title())} for k in CH["phuong"]
                    if (chd["quan"] + "|" + chd["phuong"].astype(str) == k).sum() >= 2], key=lambda p: (p["k"].split("|")[0] != "thu dau mot", p["ten"]))
tdm_ch = chd[chd["quan"] == "thu dau mot"]
CH_LIST = [{"da": nv(r["du_an_goc"]) or (r["du_an"].title() if isinstance(r["du_an"], str) else None),
            "ph": ten_ph.get(r["phuong"], str(r["phuong"]).title()), "dt": float(r["dt_dat"]),
            "pn": None if pd.isna(r["phong_ngu"]) else int(r["phong_ngu"]), "g": round(float(r["gia_ty"]), 3),
            "ai": round(float(r["gia_uoc_luong_ty"]), 3), "lo": round(float(r["khoang80_thap"]), 2), "hi": round(float(r["khoang80_cao"]), 2),
            "diff": round(float(r["gia_ty"] / r["gia_uoc_luong_ty"] - 1), 4), "cd": r["chan_doan"], "url": r["url"]} for _, r in tdm_ch.iterrows()]
data += ["const CH_MODEL = " + json.dumps(CH, ensure_ascii=False) + ";", "const CH_PHUONG = " + json.dumps(CH_PHUONG, ensure_ascii=False) + ";",
         "const CH_LIST = " + json.dumps(CH_LIST, ensure_ascii=False) + ";",
         f"const TONG_NHA = {len(df)};   // số căn nhà phố trong dữ liệu huấn luyện (trợ lý dùng khi trả lời)"]
if CO_CH:
    TOK.update({"CH_N": vn(CH_DG["so_can"]["tat_ca"], 0), "CH_DA": str(CH_DG["so_can"]["du_an"]),
                "CH_NGAY": pd.to_datetime(raw_ch["ngay_thu_thap"].iloc[0]).strftime("%d/%m/%Y"),
                "CH_WEB": vn(CH["cv_mape"]), "CH_FULL": vn(CH["mo_hinh_day_du_mape"])})

# ---- giá thuê, đất nền, giải thích mô hình, bản đồ (notebook du_doan_gia_thue / du_doan_gia_dat) ----
THUE = doc("models", "gia_thue_web.json") or {}
DAT = doc("models", "mo_hinh_gia_dat.json") or {}
GT = doc("models", "giai_thich_nha.json") or {}
gt_can = GT.get("can", {})
# Giá thuê ước tính lấy từ kết quả riêng của notebook giá thuê (results/ty_suat_cho_thue.csv), nên chạy lại riêng
# notebook nhà phố (scripts/chay_toan_bo.py --nha-pho) không làm mất giá thuê trên web.
THUE_TIN = {}
if os.path.exists(J("results", "ty_suat_cho_thue.csv")):
    for _, t in pd.read_csv(J("results", "ty_suat_cho_thue.csv"), dtype={"id": str}).iterrows():
        THUE_TIN[(t["loai"], str(t["id"]))] = (round(float(t["thue_trieu"]), 1), round(float(t["ty_suat_pt"]), 2))
def gan_thue(o, r, loai):
    if (loai, str(r["id"])) in THUE_TIN:
        o["thue"], o["ys"] = THUE_TIN[(loai, str(r["id"]))]
    elif "thue_uoc_luong_trieu" in r and pd.notna(r["thue_uoc_luong_trieu"]):
        o["thue"] = round(float(r["thue_uoc_luong_trieu"]), 1); o["ys"] = round(float(r["ty_suat_cho_thue_pt"]), 2)
for o, (_, r) in zip(L, ph.iterrows()):           # L và ph cùng thứ tự
    gan_thue(o, r, "Nhà phố")
    if str(r["id"]) in gt_can:
        o["gt"] = gt_can[str(r["id"])]
    o["lat"], o["lon"] = round(float(r["lat"]), 5), round(float(r["lon"]), 5)
for o, (_, r) in zip(CH_LIST, tdm_ch.iterrows()):
    o["id"] = str(r["id"])
    gan_thue(o, r, "Căn hộ")
DAT_LIST = []
if os.path.exists(J("results", "output_dat.csv")):
    raw_dat = pd.read_csv(J("dataset", "raw", "chotot_dat_raw.csv"))
    for w in raw_dat["phuong"].dropna().unique():
        ten_ph.setdefault(_tp(w), re.sub(r"^(Phường|Xã|Thị trấn)\s*", "", w))
    od = pd.read_csv(J("results", "output_dat.csv"), dtype={"id": str})
    duong_goc = raw_dat.assign(id=raw_dat["id"].astype(str)).set_index("id")["duong"].to_dict()   # tên đường có dấu
    ten_duong_hien = lambda r: nv(duong_goc.get(str(r["id"]))) or (nv(r["duong"]) and str(r["duong"]).title())
    DAT_LIST = [{"id": str(r["id"]), "ph": ten_ph.get(r["phuong"], str(r["phuong"]).title()) if pd.notna(r["phuong"]) else "Thủ Dầu Một (không rõ phường)", "duong": ten_duong_hien(r),
                 "dt": round(float(r["dt_dat"]), 1), "mt": None if pd.isna(r["ngang"]) else round(float(r["ngang"]), 1),
                 "g": round(float(r["gia_ty"]), 3), "ai": round(float(r["gia_du_doan_ty"]), 3), "lo": round(float(r["khoang_thap_ty"]), 2),
                 "hi": round(float(r["khoang_cao_ty"]), 2), "diff": round(float(r["gia_ty"] / r["gia_du_doan_ty"] - 1), 4), "cd": r["chan_doan"], "url": r["url"]}
                for _, r in od.iterrows()]
# điểm cho bản đồ: [lat, lon, đơn giá, loại, giá, nhãn, url]; chỉ tin có tọa độ riêng hoặc theo tuyến đường (tâm phường thì không chính xác)
PTS = []
def them(d, loai, gia_col, don_gia, nhan, chinh_xac):
    for _, r in d[chinh_xac].iterrows():
        PTS.append([round(float(r["lat"]), 5), round(float(r["lon"]), 5), round(float(don_gia(r)), 1), loai, round(float(r[gia_col]), 3), str(nhan(r))[:70], r["url"]])
cx = lambda d: d["muc_toa_do"].astype(str).str[:1].isin(["1", "2"]) & d["lat"].notna()
them(df, "nha", "gia_ty", lambda r: r["gia_ty"] * 1000 / r["dt_dat"], lambda r: r["tieu_de"], cx(df) & con_rao(df))
# Căn hộ: 1 chấm cho mỗi dự án / tòa (tọa độ trung vị các tin của dự án), kèm danh sách căn trong tòa.
# Căn không rõ dự án đứng riêng 1 chấm. Tin chỉ có tọa độ tâm phường thì không vẽ (vị trí không chính xác).
def can_ho_web(r):
    so = lambda k, d=2: None if pd.isna(r.get(k)) else round(float(r[k]), d)
    return {"id": str(r["id"]), "da": nv(r["du_an_goc"]) or (r["du_an"].title() if isinstance(r["du_an"], str) else None),
            "ph": ten_ph.get(r["phuong"], str(r["phuong"]).title()), "t": str(r["tieu_de"])[:90], "dt": float(r["dt_dat"]),
            "pn": None if pd.isna(r["phong_ngu"]) else int(r["phong_ngu"]), "g": round(float(r["gia_ty"]), 3),
            "ai": so("gia_uoc_luong_ty", 3), "lo": so("khoang80_thap"), "hi": so("khoang80_cao"), "cd": nv(r["chan_doan"]),
            "thue": so("thue_uoc_luong_trieu", 1), "ys": so("ty_suat_cho_thue_pt"), "url": r["url"]}
ch_ve = chd[chd["lat"].notna() & (chd["muc_toa_do"] != "tâm phường")]
CH_TOA = []
for k, g_ in ch_ve.groupby(ch_ve["du_an"].fillna("id:" + ch_ve["id"].astype(str)), sort=False):
    can = sorted((can_ho_web(r) for _, r in g_.iterrows()), key=lambda c: c["g"])
    CH_TOA.append({"ten": can[0]["da"] or can[0]["t"][:60], "co_du_an": not k.startswith("id:"), "ph": can[0]["ph"],
                   "lat": round(float(g_["lat"].median()), 5), "lon": round(float(g_["lon"].median()), 5), "n": len(can),
                   "dg": round(float((g_["gia_ty"] * 1000 / g_["dt_dat"]).median()), 1), "g_tv": round(float(g_["gia_ty"].median()), 3), "can": can})
if os.path.exists(J("dataset", "processed", "dat_da_xu_ly.csv")):
    dd_ = pd.read_csv(J("dataset", "processed", "dat_da_xu_ly.csv"), dtype={"id": str})
    them(dd_, "dat", "gia_ty", lambda r: r["don_gia"], lambda r: r["tieu_de"], cx(dd_))
if os.path.exists(J("dataset", "processed", "thue_da_xu_ly.csv")):
    th_ = pd.read_csv(J("dataset", "processed", "thue_da_xu_ly.csv"), dtype={"id": str})
    cnt = th_.groupby(["lat", "lon"])["id"].transform("size")
    them(th_, "thue", "thue_trieu_thang", lambda r: r["thue_trieu_thang"] * 1000 / r["dt_dat"], lambda r: r["tieu_de"], th_["lat"].notna() & (cnt <= 3))
# L và CH_LIST vừa được bổ sung trường (thuê, giải thích, tọa độ, id) -> ghi lại bản mới vào dữ liệu trang
data = [x for x in data if not x.startswith(("const LISTINGS = ", "const CH_LIST = "))]
data += ["const LISTINGS = " + json.dumps(L, ensure_ascii=False) + ";", "const CH_LIST = " + json.dumps(CH_LIST, ensure_ascii=False) + ";"]
# Mô hình ý định của trợ lý (notebook tro_ly_y_dinh.ipynb): TF-IDF + Logistic Regression -> tham số cho trình duyệt
TL = None
if os.path.exists(J("models", "tro_ly_y_dinh.joblib")):
    import joblib
    goi_tl = joblib.load(J("models", "tro_ly_y_dinh.joblib"))
    clf, phan, cot = goi_tl["mo_hinh"], [], 0
    for ten, vec in goi_tl["dac_trung"].transformer_list:
        tu = sorted(vec.vocabulary_.items(), key=lambda kv: kv[1])
        phan.append({"kieu": "char_wb" if vec.analyzer == "char_wb" else "word", "n": list(vec.ngram_range),
                     "tu_dien": {g: j for g, j in tu}, "idf": [round(float(x), 4) for x in vec.idf_],
                     "he_so": [[round(float(w), 4) for w in clf.coef_[:, cot + j]] for _, j in tu]})
        cot += len(tu)
    TL = {"lop": list(clf.classes_), "chan": [round(float(b), 4) for b in clf.intercept_], "phan": phan,
          "chien_luoc": goi_tl["chien_luoc"], "nguong": goi_tl["nguong"], "vi_du": goi_tl["vi_du"], "mau": goi_tl["mau"]}
data += ["const TL_MODEL = " + json.dumps(TL, ensure_ascii=False) + ";"]
data += ["const THUE = " + json.dumps(THUE, ensure_ascii=False) + ";", "const DAT_MODEL = " + json.dumps(DAT, ensure_ascii=False) + ";",
         "const DAT_LIST = " + json.dumps(DAT_LIST, ensure_ascii=False) + ";",
         "const GT_META = " + json.dumps({k: GT.get(k) for k in ("nen_log", "muc_tieu", "mo_hinh", "nhom")}, ensure_ascii=False) + ";",
         "const MAP_PTS = " + json.dumps(PTS, ensure_ascii=False) + ";", "const CH_TOA = " + json.dumps(CH_TOA, ensure_ascii=False) + ";"]
TOK.update({"DAT_N": vn(DAT.get("so_lo", 0), 0), "DAT_TDM": vn(DAT.get("so_lo_tdm", 0), 0), "DAT_WEB": vn(DAT.get("cv_mape_tdm", 0)),
            "DAT_FULL": vn(DAT.get("mo_hinh_day_du_mape_tdm", 0)), "N_MAP": vn(len(PTS) + sum(t["n"] for t in CH_TOA), 0),
            "THUE_N": vn(sum((THUE.get("so_tin") or {}).values()), 0)})

# Bằng chứng (3): dự đoán chéo theo nhóm trên TOÀN BỘ căn Phú Hòa (notebook nhà phố, Bước 10)
from mo_hinh_gia import ktc_bootstrap as _ktc

_ape = (ph_tat_ca["gia_uoc_luong_ty"] / ph_tat_ca["gia_ty"] - 1).abs().to_numpy() * 100
_lo, _hi = _ktc(_ape, ph_tat_ca["nhom"].to_numpy())
TOK.update({"PH_ALL_N": str(len(ph_tat_ca)), "PH_ALL_MAPE": vn(_ape.mean()), "PH_ALL_LO": vn(_lo), "PH_ALL_HI": vn(_hi)})

for k, v in TOK.items():
    tpl = tpl.replace(f"@@{k}@@", v)

# ---- ảnh minh họa & icon (giữ như bản trước) ----
cred = json.load(open(os.path.join(S, "credits.json"), encoding="utf-8"))
for x in cred:
    x["cropped"] = x["key"] in ("hero", "h1-b"); x.pop("size", None)
    x["site"] = {"flickr": "Flickr", "rawpixel": "Rawpixel"}.get(x["site"], x["site"])
USED = set(re.findall(r"assets/img/([a-z0-9-]+)\.jpg", tpl))
for arr in re.findall(r"const (?:EXT|INT) = (.*?);", tpl): USED |= set(re.findall(r'"([a-z0-9]+-[a-z0-9-]+)"', arr))
cred = [x for x in cred if x["key"] in USED]
data.append("const CREDITS = " + json.dumps(cred, ensure_ascii=False) + ";")
used = sorted(set(re.findall(r"#i-([a-z0-9-]+)", tpl)) | set(re.findall(r'icon\("([a-z0-9-]+)"', tpl)) |
              set(re.findall(r'\["([a-z0-9-]+)", "', tpl)) | {"trending-down", "trending-up", "check", "circle-alert", "minus"})
syms = []
for n in used:
    p = os.path.join(S, "icons", n + ".svg")
    if not os.path.exists(p): continue
    inner = re.search(r"<svg[^>]*>(.*)</svg>", open(p, encoding="utf-8").read(), re.DOTALL).group(1)
    syms.append(f'<symbol id="i-{n}" viewBox="0 0 24 24">' + re.sub(r"\s*\n\s*", "", inner).replace(" />", "/>") + "</symbol>")
sprite = '<svg width="0" height="0" style="position:absolute" aria-hidden="true">' + "".join(syms) + "</svg>"
if not CHI_DU_LIEU:
    out = tpl.replace("<!--@@ICONS@@-->", "<!-- Icon: Lucide (ISC) -->\n" + sprite).replace("/*@@DATA@@*/", "\n".join(data))
    assert "@@" not in out.replace("<!--@@", "").replace("/*@@", ""), re.findall(r"@@\w+@@", out)
    open(os.path.join(DEMO, "index.html"), "w", encoding="utf-8").write(out)
    print("written", len(out), "| listings:", len(L), "| tokens:", TOK)

# ---- cùng dữ liệu đó cho ứng dụng web (web/ + api/): models/du_lieu_web.json ----
du_lieu = {}
for x in data:
    m = re.match(r"const (\w+) = (.*);$", x, re.DOTALL)
    if m:
        du_lieu[m.group(1)] = json.loads(m.group(2))
du_lieu["SO_LIEU"] = TOK                                # các con số tĩnh của trang (số căn, MAPE...)
json.dump(du_lieu, open(J("models", "du_lieu_web.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print("models/du_lieu_web.json:", sorted(du_lieu))
