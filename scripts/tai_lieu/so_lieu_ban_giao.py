"""Gom MỌI số liệu cho tài liệu bàn giao từ CÙNG một lần chạy (models/*.json, dataset/, results/, notebook đã chạy,
gọi API mô hình thật, chạy các bộ kiểm thử). Ghi ra so_lieu_ban_giao.json cho tao_ban_giao.js.
Chạy: python so_lieu_ban_giao.py "<thư mục đề tài>" """
import json
import re
import subprocess
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
GOC = Path(sys.argv[1])
J = lambda *p: json.loads(GOC.joinpath(*p).read_text(encoding="utf-8"))
dg, ch, web = J("models", "danh_gia_mo_hinh.json"), J("models", "danh_gia_mo_hinh_can_ho.json"), J("models", "du_lieu_web.json")
S = {"so_lieu_web": web["SO_LIEU"], "danh_gia": dg, "can_ho": {k: ch[k] for k in ("ten_mo_hinh", "test", "kiem_dinh_cheo")}}

# ---- notebook chính: chữ in ra ----
nb = json.loads((GOC / "notebooks" / "2324801030095.ipynb").read_text(encoding="utf-8"))
chu, bang = [], []
for c in nb["cells"]:
    for o in c.get("outputs", []):
        chu.append("".join(o.get("text", "")))
        t = "".join(o.get("data", {}).get("text/plain", ""))
        if t:
            bang.append(t)
chu = "\n".join(chu)
tim = lambda pat: (re.search(pat, chu) or [None, None])[1]
S["nb"] = {
    "loc": tim(r"(Ngoài phạm vi: .*)"), "con_lai": tim(r"(Còn \d+ căn \| .*?)\s+\(danh"), "nhom": tim(r"(Nhóm gần trùng: .*)"),
    "ro_ri": tim(r"(Kiểm tra rò rỉ: .*)"), "chia": tim(r"(So sánh: chia ngẫu nhiên .*)"),
    "svr": tim(r"SVR chọn được: (.*)"), "mlp": tim(r"MLP chọn được: (.*)"), "rf": tim(r"Random Forest chọn được: (.*)"),
    "do_sau": tim(r"Độ sâu cây tốt nhất: (\d+)"), "k": tim(r"số láng giềng tốt nhất: k = (\d+)"),
    "phu_tdm": tim(r"(test TDM: \d+/\d+ căn trong khoảng \(\d+%\), p = [\d.]+)"),
    "phu_ph": tim(r"(test Phú Hòa: \d+/\d+ căn trong khoảng \(\d+%\), p = [\d.]+)"),
    "phu_all": tim(r"Độ phủ khoảng 80% trên toàn bộ (\d+ căn Phú Hòa: [\d.]+%)"),
    "chenh": re.findall(r"MAPE của '(.*?)' trừ MAPE cách chính: ([+-][\d.]+) điểm % \(KTC 95%: ([+-][\d.]+) … ([+-][\d.]+)\)", chu),
}
# bảng Phần A (kiểm định chéo 5-fold)
pa = next(t for t in bang if "MAE log – kiểm định" in t and "MAE ≈ sai số %" in t)
dong_pa = []
for l in pa.splitlines()[1:]:
    m = re.match(r"(.+?)\s{2,}(NaN|[\d.]+)\s+([\d.]+)\s+([\d.]+)\s*$", l)
    if m:
        dong_pa.append([m[1].strip(), m[2], m[3], m[4]])
S["phan_a"] = dong_pa
# độ nhạy ngưỡng lọc
ng = next((t for t in bang if "Số căn dùng để học" in t), "")
S["nguong"] = [re.split(r"\s{2,}", l.strip()) for l in ng.splitlines()[2:] if l.strip()]

# ---- mô hình đã lưu ----
sys.path.insert(0, str(GOC / "src"))
import joblib  # noqa: E402
goi = joblib.load(GOC / "models" / "mo_hinh_gia_nha.joblib")
rf = goi["model"].m_[-1]
S["mo_hinh"] = {"ten": goi["ten"], "dac_trung": list(goi["model"].features), "n_estimators": rf.n_estimators, "max_features": rf.max_features,
                "min_samples_leaf": rf.min_samples_leaf, "so_can_hoc": goi["so_can"], "ngay": goi["ngay_du_lieu"]}

# ---- dữ liệu ----
d = pd.read_csv(GOC / "dataset" / "processed" / "nha_da_xu_ly.csv", low_memory=False)
ph = d[d["phu_hoa"] == 1]
S["du_lieu"] = {"tong": len(d), "tdm": int(d["tdm"].sum()), "ph": len(ph), "so_nhom": int(d["nhom"].nunique()),
                "theo_nguon": d["nguon"].value_counts().to_dict(), "ph_theo_tap": ph["tap"].value_counts().to_dict(),
                "tdm_theo_tap": d[d["tdm"] == 1]["tap"].value_counts().to_dict(),
                "gia_ph": {k: round(float(v), 2) for k, v in ph["gia_ty"].describe(percentiles=[.25, .5, .75])[["min", "25%", "50%", "75%", "max"]].items()},
                "dt_ph": {k: round(float(v), 1) for k, v in ph["dt_dat"].describe(percentiles=[.5])[["min", "50%", "max"]].items()}}
loai = pd.read_csv(GOC / "dataset" / "processed" / "tin_bi_loai.csv")
S["bi_loai"] = loai["ly_do_loai"].value_counts().to_dict()
la_dat = loai["ly_do_loai"].str.contains("bán đất|Bán đất|Bán đất để xây mới", regex=True)
S["bi_loai_dat"] = loai[la_dat][["nguon", "tieu_de", "gia_ty", "ly_do_loai"]].to_dict("records")
# tin tiêu đề "bán đất…" nhưng được GIỮ vì mô tả một căn nhà ở được
sys.path.insert(0, str(GOC / "src"))
from mo_hinh_gia import khong_dau  # noqa: E402
td = d["tieu_de"].fillna("").map(khong_dau)
S["giu_dat"] = d[td.str.contains(r"\bban (?:gap )?(?:lo |nen )?dat\b|\bdat tang\b", regex=True)][["nguon", "tieu_de", "gia_ty", "so_tang", "phong_ngu"]].to_dict("records")
S["nhan_tay"] = {"so_cap": len(pd.read_csv(GOC / "dataset" / "labeled" / "cap_tin_gan_trung.csv"))}

# ---- danh sách file (số dòng, cột, KB) ----
tep = []
for thu_muc in ["dataset/raw", "dataset/processed", "dataset/labeled", "models", "results"]:
    for f in sorted((GOC / thu_muc).glob("*")):
        if f.is_file():
            r = c_ = None
            if f.suffix == ".csv":
                x = pd.read_csv(f, low_memory=False); r, c_ = len(x), x.shape[1]
            elif f.suffix == ".jsonl":
                r = sum(1 for l in f.open(encoding="utf-8") if l.strip())
            tep.append([f"{thu_muc}/{f.name}", r, c_, round(f.stat().st_size / 1024)])
S["tep"] = tep
S["so_anh_chup"] = len(list((GOC / "dataset" / "history").glob("*.csv")))

# ---- ví dụ đầu vào -> đầu ra thật (API mô hình chạy trong tiến trình) ----
sys.path.insert(0, str(GOC / "api"))
from fastapi.testclient import TestClient  # noqa: E402
import main  # noqa: E402
cl = TestClient(main.app)
VD = [("Nhà cấp 4, 100 m² (5×20), hẻm xe hơi 4 m", dict(dt_dat=100, ngang=5, dai=20, so_tang=1, dt_san=100, phong_ngu=2, so_wc=1, cap_loi_vao=2, hem_rong=4, mo_ta="nhà cấp 4 hẻm xe hơi sổ riêng")),
      ("Nhà 1 trệt 1 lầu, 80 m², hẻm xe tải 6 m, khu dân cư", dict(dt_dat=80, ngang=4.5, so_tang=2, dt_san=160, phong_ngu=3, so_wc=2, cap_loi_vao=3, hem_rong=6, mo_ta="1 trệt 1 lầu kdc hẻm 6m sổ hồng riêng")),
      ("Nhà 1 trệt 2 lầu, 120 m², mặt tiền Nguyễn Thị Minh Khai", dict(dt_dat=120, ngang=6, dai=20, so_tang=3, dt_san=300, phong_ngu=4, so_wc=4, mat_tien_duong=1, cap_loi_vao=5, hem_rong=20, duong="Nguyễn Thị Minh Khai", mo_ta="mặt tiền kinh doanh"))]
S["vi_du"] = [{"ten": t, "vao": v, "ra": cl.post("/dinh-gia/nha-pho", json=v).json()} for t, v in VD]
# vài tin test Phú Hòa thật: giá rao so với giá mô hình (dự đoán ngoài-fold, mô hình không học tin đó)
t_ = ph[ph["tap"] == "test"].assign(lech=lambda x: (x["gia_uoc_luong_ty"] / x["gia_ty"] - 1) * 100).sort_values("lech", key=abs).reset_index(drop=True)
idx = [0, len(t_) // 2, len(t_) - 1]
S["tin_that"] = [{"tieu_de": str(t_.loc[i, "tieu_de"])[:70], "dt": float(t_.loc[i, "dt_dat"]), "gia_rao": float(t_.loc[i, "gia_ty"]),
                  "gia_mh": round(float(t_.loc[i, "gia_uoc_luong_ty"]), 2), "lech": round(float(t_.loc[i, "lech"]), 1)} for i in idx]

# ---- kiểm thử: chạy thật, lấy dòng tổng kết ----
def chay(lenh):
    r = subprocess.run(lenh, cwd=GOC, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return (re.findall(r"(\d+/\d+ phép kiểm đạt)", r.stdout) or ["LỖI: " + (r.stdout + r.stderr)[-200:]])[-1]
PY = sys.executable
S["kiem_thu"] = {
    "kiem_tra_mo_hinh.py": chay([PY, "-X", "utf8", "tests/kiem_tra_mo_hinh.py"]),
    "kiem_tra_api.py": chay([PY, "-X", "utf8", "tests/kiem_tra_api.py"]),
    "kiem_tra_tro_ly.js": chay(["node", "tests/kiem_tra_tro_ly.js"]),
    "kiem_tra_web.mjs": chay(["node", "tests/kiem_tra_web.mjs"]),
}
S["moi_truong"] = {"python": sys.version.split()[0], "node": subprocess.run(["node", "--version"], capture_output=True, text=True).stdout.strip(),
                   "commit": subprocess.run(["git", "log", "-1", "--format=%h"], cwd=GOC, capture_output=True, text=True).stdout.strip()}
json.dump(S, open(Path(__file__).parent / "so_lieu_ban_giao.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
print("ok", {k: S["kiem_thu"][k] for k in S["kiem_thu"]}, S["nb"]["phu_ph"])
