"""Các lớp mô hình dùng chung cho notebook 2324801030095.ipynb và du_doan_xu_huong_gia.ipynb.

Đặt trong tệp .py (không viết trong notebook) để mô hình lưu bằng joblib có thể nạp lại ở notebook khác.
Mọi lớp theo chuẩn scikit-learn: fit(X, y) / predict(X), dùng được với KFold, cross_val_predict.
Biến mục tiêu y luôn là log(giá tỷ đồng).
"""
import re
import unicodedata

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, RegressorMixin, TransformerMixin, clone
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.model_selection import GroupKFold, KFold, cross_val_predict
from sklearn.neighbors import BallTree
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


def khong_dau(s):
    """'Hẻm xe hơi' -> 'hem xe hoi' (chữ thường, bỏ dấu) để so khớp từ khóa ổn định."""
    s = unicodedata.normalize("NFD", str(s).lower()).replace("đ", "d")
    return "".join(ch for ch in s if unicodedata.category(ch) != "Mn")


def ten_phuong(s):
    """'Phường Phú Hòa' -> 'phu hoa'"""
    return None if pd.isna(s) else re.sub(r"^(phuong|xa|thi tran)\s*", "", khong_dau(s).strip()).strip()


def ten_quan(s):
    """'Thành phố Thủ Dầu Một' -> 'thu dau mot'"""
    return re.sub(r"^(thanh pho|thi xa|huyen)\s+", "", khong_dau(s))


def ten_duong(s):
    """Chuẩn hóa tên đường để so khớp giữa các nguồn: 'Hẻm 453 Lê Hồng Phong' -> 'le hong phong'."""
    if pd.isna(s):
        return None
    s = re.sub(r"^(duong|d\.)\s+", "", khong_dau(s).strip())
    s = re.sub(r"\s*-\s*duong loai.*$", "", s).replace("30 thang 4", "30/4").replace("dt 743", "dt743")
    s = re.sub(r"^hem\s+\S+\s+", "", s)
    return s.strip(" .,") or None


# Từ khóa đọc từ tiêu đề + mô tả tin (đã bỏ dấu). Mỗi mục -> 1 cột 0/1.
TU_KHOA = {
    "t_hem_xe_hoi": r"\bhxh\b|hem xe hoi|hem oto|hem o to|xe hoi (?:vao|do|toi|ra vao)|oto (?:vao|do|toi)|o to (?:vao|do|toi)|hem xe tai|hem thong",
    "t_hem_nho": r"hem xe may|hem nho|hem cut|hem 2m\b|hem 2,5m|hem 3m\b|hem ba gac",
    "t_mat_tien": r"mat tien duong|nha mat tien|\bmt duong|mat duong|mat tien kinh doanh|mat tien nhua",
    "t_kdc": r"\bkdc\b|khu dan cu|khu do thi|\bkdt\b|khu nha o|khu tai dinh cu|\btdc\b",
    "t_noi_bo": r"duong noi bo|\b[dn]\s?\d{1,2}\b",
    "t_cap4": r"cap 4|cap4|cap bon",
    "t_nha_nat": r"nha nat|nha cu|tien dat|gia dat|tang nha",
    "t_nha_moi": r"moi xay|moi 100|nha moi|xay moi|moi tinh|moi hoan thien|chua o",
    "t_so_rieng": r"so rieng|\bshr\b|so hong rieng|so san|so do",
    "t_so_chung": r"so chung|vi bang|giay tay|giay to tay",
    "t_chua_hc": r"chua hoan cong",
    "t_goc": r"can goc|nha goc|lo goc|2 mat tien|hai mat tien|2 mt\b|3 mat tien",
    "t_kinh_doanh": r"kinh doanh|buon ban",
    "t_tro": r"day tro|phong tro|nha tro|thu nhap|dong tien",
    "t_ban_gap": r"ngop|cat lo|ban gap|can tien|ket tien|giam gia|ha gia|giam sau|re hon|duoi gia|bat day|gia re",
    "t_noi_that": r"noi that",
    "t_no_hau": r"no hau",
    "t_tho_cu": r"tho cu|\bodt\b|full tc|100% tc",
    "t_thang_may": r"thang may",
    "t_biet_thu": r"biet thu|villa",
    "t_trung_tam": r"trung tam|gan cho|becamex|ubnd|uy ban",
}


def trich_dac_trung_chu(van_ban):
    """van_ban: Series chữ đã bỏ dấu. Trả về DataFrame các cột t_* (cờ 0/1 và số đo đọc được)."""
    F = pd.DataFrame(index=van_ban.index)
    for ten, mau in TU_KHOA.items():
        F[ten] = van_ban.str.contains(mau, regex=True).astype(int)

    def lay_so(mau, lo, hi):
        v = pd.to_numeric(van_ban.str.extract(mau, expand=False).str.replace(",", "."), errors="coerce").astype(float)
        return v.where(v.between(lo, hi))

    F["t_hem_rong"] = lay_so(r"(?:hem|duong|lo gioi|duong truoc nha|duong nhua|duong be tong)\s*(?:nhua|be tong|xe hoi|rong|thong)?\s*(\d{1,2}(?:[.,]\d)?)\s*m(?![2\d²])", 2, 40)
    F["t_ngang"] = lay_so(r"(?:ngang|mat tien|mt)\s*:?\s*(\d{1,2}(?:[.,]\d+)?)\s*m", 2.5, 40)
    kt = van_ban.str.extract(r"(\d{1,2}(?:[.,]\d+)?)\s*[x\*]\s*(\d{1,3}(?:[.,]\d+)?)\s*m?")
    kt = kt.apply(lambda s: pd.to_numeric(s.str.replace(",", "."), errors="coerce").astype(float))
    F["t_kt_ngang"] = kt[0].where(kt[0].between(2.5, 40))
    F["t_kt_dai"] = kt[1].where(kt[1].between(5, 150))
    tl = van_ban.str.extract(r"(\d)?\s*tret\s*,?\s*(\d)\s*(?:lau|lung)")
    F["t_so_tang"] = (1 + pd.to_numeric(tl[1], errors="coerce").astype(float)).where(tl[1].notna())
    F.loc[F["t_so_tang"].isna() & van_ban.str.contains(r"tret\s*,?\s*lau|1 lau 1 tret"), "t_so_tang"] = 2
    F.loc[F["t_so_tang"].isna() & van_ban.str.contains(r"gac lung|gac duc|\blung\b"), "t_so_tang"] = 1.5
    F.loc[F["t_so_tang"].isna() & (F["t_cap4"] == 1), "t_so_tang"] = 1
    F["t_pn"] = lay_so(r"(\d{1,2})\s*(?:pn\b|phong ngu)", 1, 15)
    F["t_wc"] = lay_so(r"(\d{1,2})\s*(?:wc\b|toilet|ve sinh|vs\b)", 1, 15)
    F["t_dt_san"] = lay_so(r"(?:dtsd|dien tich su dung|dt su dung|tong dien tich san|dt san|tong san)\s*:?\s*(\d{2,4}(?:[.,]\d+)?)", 30, 3000)
    F["t_dt_tho_cu"] = lay_so(r"(\d{2,4}(?:[.,]\d+)?)\s*m2?\s*(?:tho cu|tc\b|odt)", 10, 2000)
    return F


# ----------------------------------------------------------------------------------------------
# Đặc trưng không gian
# ----------------------------------------------------------------------------------------------
class GiaLangGieng(BaseEstimator, TransformerMixin):
    """Đặc trưng "giá khu vực" học từ TẬP TRAIN:
    - lg_knn, lg_knn_med: log đơn giá (triệu/m²) của k căn gần nhất (trung bình theo nghịch đảo khoảng cách, trung vị);
    - kc_knn_km: khoảng cách trung bình tới k căn đó (khu càng thưa thì thông tin càng kém chắc chắn);
    - lg_phuong, lg_duong: log đơn giá trung bình của cùng phường / cùng tuyến đường, co về trung bình chung
      khi ít mẫu (target encoding có làm trơn).
    Khi gọi fit_transform trên tập train, mỗi căn được tính KHÔNG có chính nó (leave-one-out),
    nên mô hình không "nhìn thấy" giá của chính căn đang học -> không rò rỉ nhãn."""

    def __init__(self, k=12, tang_bac=False):
        # tang_bac=True (dùng cho căn hộ): đơn giá dự án co về đơn giá PHƯỜNG (thay vì toàn vùng) khi dự án ít tin,
        # và thêm cột n_duong = số tin của dự án trong tập học, để mô hình tự quyết định tin con số đó đến đâu.
        self.k, self.tang_bac = k, tang_bac

    def fit(self, X, y):
        self.xy_ = np.radians(X[["lat", "lon"]].to_numpy(float))
        self.u_ = np.asarray(y, float) - np.log(X["dt_dat"].to_numpy(float)) + np.log(1000)
        self.tree_ = BallTree(self.xy_, metric="haversine")
        self.g_ = float(np.median(self.u_))
        self.phuong_ = pd.DataFrame({"k": self._kp(X), "u": self.u_}).groupby("k")["u"].agg(["sum", "count"])
        self.duong_ = pd.DataFrame({"k": self._kd(X), "u": self.u_}).groupby("k")["u"].agg(["sum", "count"])
        return self

    def _kp(self, X):
        k = X["quan"].astype(str) + "|" + X["phuong"].astype(str)
        if getattr(self, "tang_bac", False) and "noxh" in X:      # getattr: mô hình lưu từ phiên bản cũ không có thuộc tính này
            # căn hộ: tách nhà ở xã hội và thương mại thành hai "phường" riêng -> giá trị nền đúng phân khúc
            k = k + "|" + X["noxh"].fillna(0).astype(int).astype(str)
        return k.to_numpy()

    @staticmethod
    def _kd(X):
        return (X["quan"].astype(str) + "|" + X["duong"].fillna("?").astype(str)).to_numpy()

    def _ma_hoa(self, keys, bang, own=None, m=5.0, nen=None):
        s = bang.reindex(keys)
        tong, n = s["sum"].fillna(0).to_numpy(), s["count"].fillna(0).to_numpy()
        if own is not None:
            tong, n = tong - own, n - 1
        nen = self.g_ if nen is None else nen
        return (tong + m * nen) / (n + m)

    def _tinh(self, X, loo):
        q = np.radians(X[["lat", "lon"]].to_numpy(float))
        k = min(self.k + int(loo), len(self.u_))
        dist, idx = self.tree_.query(q, k=k)
        if loo:
            # bỏ đúng chính căn đó (không chỉ bỏ cột đầu, vì có thể có căn khác trùng tọa độ)
            self_pos = np.arange(len(X))
            keep = idx != self_pos[:, None]
            idx = np.array([r[m][: self.k] for r, m in zip(idx, keep)])
            dist = np.array([r[m][: self.k] for r, m in zip(dist, keep)])
        u = self.u_[idx]
        w = 1.0 / (dist * 6371 + 0.3)
        out = pd.DataFrame(index=X.index)
        out["lg_knn"] = (u * w).sum(1) / w.sum(1)
        out["lg_knn_med"] = np.median(u, 1)
        out["kc_knn_km"] = dist.mean(1) * 6371
        own = self.u_ if loo else None
        out["lg_phuong"] = self._ma_hoa(self._kp(X), self.phuong_, own)
        if getattr(self, "tang_bac", False):
            out["lg_duong"] = self._ma_hoa(self._kd(X), self.duong_, own, m=3.0, nen=out["lg_phuong"].to_numpy())
            n = self.duong_.reindex(self._kd(X))["count"].fillna(0).to_numpy() - (1 if loo else 0)
            out["n_duong"] = np.where(X["duong"].isna().to_numpy(), 0, np.maximum(n, 0))
        else:
            out["lg_duong"] = self._ma_hoa(self._kd(X), self.duong_, own, m=3.0)
        return out

    def fit_transform(self, X, y):
        return self.fit(X, y)._tinh(X, loo=True)

    def transform(self, X):
        return self._tinh(X, loo=False)


# ----------------------------------------------------------------------------------------------
# Các mô hình
# ----------------------------------------------------------------------------------------------
class MoHinhGia(BaseEstimator, RegressorMixin):
    """Bọc một mô hình hồi quy: ghép đặc trưng căn nhà (features) + đặc trưng giá khu vực (GiaLangGieng).
    chuan_hoa=True: thêm điền thiếu + chuẩn hóa (cho mô hình tuyến tính).
    muc_tieu='don_gia': học log(đơn giá) rồi cộng lại log(diện tích); 'gia': học thẳng log(giá)."""

    def __init__(self, est, features, khong_gian=True, chuan_hoa=False, muc_tieu="gia", tang_bac=False):
        self.est, self.features, self.khong_gian, self.chuan_hoa, self.muc_tieu = est, features, khong_gian, chuan_hoa, muc_tieu
        self.tang_bac = tang_bac

    def _Z(self, X, y=None):
        Z = X[list(self.features)].astype(float)
        if self.khong_gian:
            K = self.kg_.fit_transform(X, y) if y is not None else self.kg_.transform(X)
            Z = pd.concat([Z, K], axis=1)
        return Z

    def fit(self, X, y):
        y = np.asarray(y, float)
        self.kg_ = GiaLangGieng(tang_bac=getattr(self, "tang_bac", False))
        Z = self._Z(X, y)
        self.columns_ = list(Z.columns)
        t = y - np.log(X["dt_dat"].to_numpy(float)) if self.muc_tieu == "don_gia" else y
        if self.chuan_hoa:
            self.m_ = make_pipeline(SimpleImputer(strategy="median", add_indicator=True), StandardScaler(), clone(self.est))
        else:
            self.m_ = clone(self.est)
        self.m_.fit(Z, t)
        return self

    def predict(self, X):
        p = self.m_.predict(self._Z(X))
        return p + np.log(X["dt_dat"].to_numpy(float)) if self.muc_tieu == "don_gia" else p


class XepChongChu(BaseEstimator, RegressorMixin):
    """Stacking với mô hình chữ: TF-IDF (n-gram ký tự) + Ridge đọc tiêu đề + mô tả tin để ước lượng log(đơn giá).
    Dự đoán ngoài-fold (out-of-fold) của nó được thêm thành cột 't_chu' cho mô hình chính.
    Dùng OOF khi huấn luyện để mô hình chính không học trên dự đoán đã 'thuộc bài'."""

    def __init__(self, base, alpha=3.0):
        self.base, self.alpha = base, alpha

    def _mo_hinh_chu(self):
        return make_pipeline(TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=3,
                                             sublinear_tf=True, max_features=40000), Ridge(alpha=self.alpha))

    def chu_ngoai_fold(self, X, u):
        """Dự đoán của mô hình chữ cho từng tin khi tin đó KHÔNG nằm trong tập học của mô hình chữ.
        Chia THEO NHÓM tin gần trùng (cột 'nhom') giống vòng đánh giá bên ngoài: nếu chia ngẫu nhiên, một tin đăng lại
        gần như y hệt sẽ nằm ở phần học, mô hình chữ "thuộc" luôn giá của tin đang dự đoán -> cột t_chu đẹp giả tạo,
        mô hình chính học cách tin quá mức vào nó. Không có cột 'nhom' (ví dụ dự đoán căn mới) thì chia ngẫu nhiên."""
        if "nhom" in X and X["nhom"].nunique() >= 5:
            cv = list(GroupKFold(5, shuffle=True, random_state=1).split(X, groups=X["nhom"]))
        else:
            cv = KFold(5, shuffle=True, random_state=1)
        return cross_val_predict(self._mo_hinh_chu(), X["van_ban"], u, cv=cv)

    def fit(self, X, y):
        u = np.asarray(y, float) - np.log(X["dt_dat"].to_numpy(float))
        oof = self.chu_ngoai_fold(X, u)
        self.chu_ = self._mo_hinh_chu().fit(X["van_ban"], u)
        self.m_ = clone(self.base).fit(X.assign(t_chu=oof), y)
        return self

    def predict(self, X):
        return self.m_.predict(X.assign(t_chu=self.chu_.predict(X["van_ban"])))


class TrungBinhMoHinh(BaseEstimator, RegressorMixin):
    """Ensemble: trung bình dự đoán (trên thang log) của nhiều mô hình."""

    def __init__(self, models):
        self.models = models

    def fit(self, X, y):
        self.fitted_ = [clone(m).fit(X, y) for m in self.models]
        return self

    def predict(self, X):
        return np.mean([m.predict(X) for m in self.fitted_], axis=0)


class BaselineDonGiaPhuong(BaseEstimator, RegressorMixin):
    """Mốc so sánh: giá = đơn giá trung vị của phường (trên tập train) × diện tích đất."""

    def fit(self, X, y):
        u = np.asarray(y, float) - np.log(X["dt_dat"].to_numpy(float))
        self.g_ = float(np.median(u))
        self.p_ = pd.Series(u).groupby((X["quan"].astype(str) + "|" + X["phuong"].astype(str)).to_numpy()).median()
        return self

    def predict(self, X):
        k = X["quan"].astype(str) + "|" + X["phuong"].astype(str)
        return k.map(self.p_).fillna(self.g_).to_numpy() + np.log(X["dt_dat"].to_numpy(float))


def chi_so_danh_gia(y_log, p_log):
    """Đổi về tỷ đồng rồi tính: MAPE, MdAPE (sai số % trung vị), tỷ lệ căn sai trong ±10% / ±20%, MAE, R²."""
    t, d = np.exp(np.asarray(y_log)), np.exp(np.asarray(p_log))
    ape = np.abs(d - t) / t * 100
    return {"MAE (tỷ)": np.mean(np.abs(d - t)), "MAPE (%)": ape.mean(), "MdAPE (%)": np.median(ape),
            "Trong ±10% (%)": (ape <= 10).mean() * 100, "Trong ±20% (%)": (ape <= 20).mean() * 100,
            "R²": 1 - ((t - d) ** 2).sum() / ((t - t.mean()) ** 2).sum(), "Số căn": len(t)}


# ----------------------------------------------------------------------------------------------
# Chống rò rỉ khi đánh giá: gom các tin "gần trùng" (nhiều khả năng là CÙNG MỘT CĂN đăng lại) thành nhóm
# ----------------------------------------------------------------------------------------------
def nhom_gan_trung(df, sai_dt=0.03, sai_gia=0.12, nguong_chu=0.45, dung_vi_tri=True):
    """Trả về mã nhóm cho từng dòng. Hai tin vào cùng nhóm khi: cùng quận, diện tích lệch <= 3%, giá lệch <= 12%
    VÀ có thêm một bằng chứng: mô tả giống nhau (cosine TF-IDF >= 0,45), hoặc cùng phường và cùng kích thước ngang x dài,
    hoặc cùng phường và cùng tuyến đường. Khi chia train/test, cả nhóm luôn nằm về một phía (GroupKFold),
    nên mô hình không được "gặp lại" chính căn nhà đang kiểm tra dưới một tin rao khác.
    Thà gom thừa còn hơn bỏ sót: gom thừa chỉ làm kết quả đánh giá khắt khe hơn.
    dung_vi_tri=False (dùng cho CĂN HỘ): chỉ gom khi mô tả giống nhau. Một dự án chung cư có rất nhiều căn cùng mẫu
    (cùng diện tích, giá gần nhau) nhưng là các căn KHÁC nhau; gom chúng lại sẽ giấu cả dự án khỏi tập học."""
    d = df.reset_index(drop=True)
    V = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=2, sublinear_tf=True).fit_transform(d["van_ban"])
    cha = np.arange(len(d))

    def goc(i):
        while cha[i] != i:
            cha[i] = cha[cha[i]]
            i = cha[i]
        return i

    for _, g in d.groupby("quan"):
        ix = g.index.to_numpy()
        a, p = g["dt_dat"].to_numpy(float), g["gia_ty"].to_numpy(float)
        ph, du = g["phuong"].to_numpy(), g["duong"].to_numpy()
        ng, da = g["ngang"].to_numpy(float), g["dai"].to_numpy(float)
        for k in range(len(ix)):
            m = (np.abs(a - a[k]) / a[k] <= sai_dt) & (np.abs(p - p[k]) / p[k] <= sai_gia)
            m[: k + 1] = False
            for j in np.where(m)[0]:
                cung_phuong = ph[j] == ph[k]
                cung_kt = abs(ng[j] - ng[k]) <= 0.11 and abs(da[j] - da[k]) <= 0.6          # NaN -> False
                cung_duong = isinstance(du[k], str) and du[j] == du[k]
                if (dung_vi_tri and cung_phuong and (cung_kt or cung_duong)) or V[ix[k]].multiply(V[ix[j]]).sum() >= nguong_chu:
                    cha[goc(ix[j])] = goc(ix[k])
    return np.array([goc(i) for i in range(len(d))])


# ----------------------------------------------------------------------------------------------
# Đánh giá: kiểm định chéo LẶP, chia theo NHÓM; khoảng tin cậy bằng bootstrap theo nhóm
# ----------------------------------------------------------------------------------------------
def du_doan_cheo_lap(tao_mo_hinh, d, so_lan=3, theo_nhom=True, seed=0):
    """Kiểm định chéo 5-fold lặp `so_lan` lần với các cách chia khác nhau.
    Trả về ma trận (so_lan x số căn): dự đoán log(giá) của mỗi căn khi căn đó KHÔNG nằm trong tập học.
    theo_nhom=True: các tin gần trùng (cột 'nhom') luôn ở cùng một fold -> không rò rỉ."""
    from sklearn.model_selection import GroupKFold
    d = d.reset_index(drop=True)
    P = np.zeros((so_lan, len(d)))
    for r in range(so_lan):
        if theo_nhom:
            chia = GroupKFold(5, shuffle=True, random_state=seed + r).split(d, groups=d["nhom"])
        else:
            chia = KFold(5, shuffle=True, random_state=seed + r).split(d)
        for tr, va in chia:
            P[r, va] = tao_mo_hinh().fit(d.iloc[tr], d["y"].iloc[tr]).predict(d.iloc[va])
    return P


def sai_so_tung_can(d, P):
    """Sai số % tuyệt đối của từng căn, lấy trung bình qua các lần lặp."""
    g = d["gia_ty"].to_numpy(float)
    return (np.abs(np.exp(np.atleast_2d(P)) - g) / g * 100).mean(axis=0)


def ktc_bootstrap(gia_tri, nhom, ham=np.mean, B=2000, seed=0):
    """Khoảng tin cậy 95% của ham(gia_tri) bằng bootstrap THEO NHÓM (lấy mẫu lại cả nhóm tin gần trùng,
    vì các tin trong một nhóm không độc lập với nhau)."""
    rng = np.random.default_rng(seed)
    gia_tri, nhom = np.asarray(gia_tri, float), np.asarray(nhom)
    ids, inv = np.unique(nhom, return_inverse=True)
    vi_tri = [np.where(inv == k)[0] for k in range(len(ids))]
    kq = [ham(gia_tri[np.concatenate([vi_tri[k] for k in rng.integers(0, len(ids), len(ids))])]) for _ in range(B)]
    return tuple(np.percentile(kq, [2.5, 97.5]))


def bang_danh_gia(d, du_doan, mask):
    """du_doan: {tên mô hình: ma trận dự đoán lặp}. Trả về bảng chỉ số trên các căn thuộc `mask`,
    kèm khoảng tin cậy 95% của MAPE."""
    rows = {}
    m = np.asarray(mask)
    for ten, P in du_doan.items():
        P = np.atleast_2d(P)
        cs = pd.DataFrame([chi_so_danh_gia(d["y"].to_numpy()[m], p[m]) for p in P]).mean()
        lo, hi = ktc_bootstrap(sai_so_tung_can(d, P)[m], d["nhom"].to_numpy()[m])
        cs["MAPE thấp (95%)"], cs["MAPE cao (95%)"] = lo, hi
        rows[ten] = cs
    cot = ["MAPE (%)", "MAPE thấp (95%)", "MAPE cao (95%)", "MdAPE (%)", "Trong ±10% (%)", "Trong ±20% (%)", "MAE (tỷ)", "R²", "Số căn"]
    return pd.DataFrame(rows).T[cot]


# ----------------------------------------------------------------------------------------------
# Căn hộ chung cư
# ----------------------------------------------------------------------------------------------
def ten_du_an(s):
    """Chuẩn hóa tên dự án để so khớp: 'Căn hộ Happy One - Central' -> 'happy one central'."""
    if pd.isna(s) or not str(s).strip():
        return None
    s = khong_dau(s)
    s = re.sub(r"^(can ho|chung cu|du an|nha o xa hoi)\s+", "", s)
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"\s*(binh duong|thu dau mot|di an|thuan an)$", "", s).strip()
    return s or None


class BaselineDonGiaDuAn(BaseEstimator, RegressorMixin):
    """Mốc so sánh cho căn hộ: giá = đơn giá trung vị của DỰ ÁN (nếu dự án có >= 3 căn trong tập học),
    nếu không thì của phường, nhân diện tích sử dụng."""

    def fit(self, X, y):
        u = pd.Series(np.asarray(y, float) - np.log(X["dt_dat"].to_numpy(float)), index=X.index)
        self.g_ = float(u.median())
        da = u.groupby(X["du_an"])
        self.da_ = da.median()[da.size() >= 3]
        self.ph_ = u.groupby(X["quan"].astype(str) + "|" + X["phuong"].astype(str)).median()
        return self

    def predict(self, X):
        k = X["quan"].astype(str) + "|" + X["phuong"].astype(str)
        return (X["du_an"].map(self.da_).fillna(k.map(self.ph_)).fillna(self.g_).to_numpy(float)
                + np.log(X["dt_dat"].to_numpy(float)))


# ----------------------------------------------------------------------------------------------
# Khoảng giá 80%: hiệu chỉnh từ sai số ngoài-fold THEO NHÓM (ý tưởng Mondrian conformal; độ phủ chỉ được
# kiểm chứng thực nghiệm trên tập test, không phải bảo đảm lý thuyết)
# ----------------------------------------------------------------------------------------------
PHAN_VI = {"q10": 0.10, "q25": 0.25, "q75": 0.75, "q90": 0.90}


def hieu_chinh_khoang(sai_so, nhom, toi_thieu=40):
    """Tính phân vị của sai số log (giá thật − giá dự đoán) RIÊNG cho từng nhóm.
    Một biên độ chung cho mọi căn sẽ quá hẹp với nhóm khó đoán (nhà đắt, nhà ở xã hội) và quá rộng với nhóm dễ đoán.
    Nhóm có ít hơn `toi_thieu` sai số thì dùng phân vị chung. Trả về {"chung": {...}, "nhom": {tên nhóm: {...}}}."""
    sai_so, nhom = np.asarray(sai_so, float).ravel(), np.asarray(nhom).ravel()
    pv = lambda x: {k: float(np.quantile(x, q)) for k, q in PHAN_VI.items()}
    bang = {"chung": pv(sai_so), "nhom": {}}
    for g in pd.unique(nhom):
        x = sai_so[nhom == g]
        if len(x) >= toi_thieu:
            bang["nhom"][str(g)] = pv(x)
    return bang


def phan_vi_cho(nhom, bang):
    """Phân vị sai số cho từng căn theo nhóm của căn đó -> dict {q10: mảng, q25: mảng, ...}."""
    nhom = np.atleast_1d(np.asarray(nhom)).astype(str)
    return {k: np.array([bang["nhom"].get(g, bang["chung"])[k] for g in nhom]) for k in PHAN_VI}


def muc_gia(p_log, nguong):
    """Xếp một dự đoán log(giá) vào mức giá 0..len(nguong) theo các ngưỡng (tứ phân vị)."""
    return np.digitize(np.atleast_1d(p_log), nguong)


# ----------------------------------------------------------------------------------------------
# Xu hướng: dự báo Holt và kiểm định lùi (dùng khi đã có đủ kỳ ảnh chụp dữ liệu thật)
# ----------------------------------------------------------------------------------------------
def holt(y, a=0.5, b=0.3):
    """Làm trơn hàm mũ có xu hướng (Holt) trên chuỗi y -> (mức, xu hướng) ở kỳ cuối."""
    y = np.asarray(y, float)
    l, t = y[0], (y[1] - y[0]) if len(y) > 1 else 0.0
    for v in y[1:]:
        l_moi = a * v + (1 - a) * (l + t)
        t = b * (l_moi - l) + (1 - b) * t
        l = l_moi
    return l, t


def kiem_dinh_lui(y, bat_dau=4):
    """Kiểm định lùi dự báo 1 kỳ tới: tại mỗi kỳ t, Holt CHỈ được dùng y[0..t] để dự báo y[t+1];
    so với baseline "không đổi" (dự báo y[t+1] = y[t]). Trả về dict sai số tuyệt đối từng kỳ và kết luận.
    Holt chỉ được coi là tốt hơn khi sai số trung bình THẤP HƠN baseline trên các kỳ kiểm tra."""
    y = np.asarray(y, float)
    assert np.isfinite(y).all(), "chuỗi chỉ số có kỳ rỗng (NaN) - kiểm tra ảnh chụp trong data/lich_su"
    loi_holt, loi_khong_doi = [], []
    for t in range(bat_dau, len(y) - 1):
        l, xh = holt(y[: t + 1])
        loi_holt.append(abs(l + xh - y[t + 1]))
        loi_khong_doi.append(abs(y[t] - y[t + 1]))
    if not loi_holt:
        return {"so_ky_kiem_tra": 0, "holt_tot_hon": False}
    return {"so_ky_kiem_tra": len(loi_holt), "mae_holt": float(np.mean(loi_holt)), "mae_khong_doi": float(np.mean(loi_khong_doi)),
            "holt_tot_hon": bool(np.mean(loi_holt) < np.mean(loi_khong_doi))}
