import "server-only";

// Gọi dịch vụ mô hình (FastAPI, thư mục api/). Chỉ chạy phía máy chủ: trình duyệt không gọi thẳng API mô hình.
const API = process.env.MODEL_API_URL ?? "http://localhost:8000";

export class LoiApi extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

export async function goiApi<T>(duong: string, init?: RequestInit): Promise<T> {
  const r = await fetch(API + duong, { ...init, cache: "no-store", headers: { "content-type": "application/json", ...init?.headers } });
  if (!r.ok) {
    let msg = `API mô hình lỗi ${r.status}`;
    try {
      const j = await r.json();
      msg = typeof j.detail === "string" ? j.detail : JSON.stringify(j.detail ?? j);
    } catch {}
    throw new LoiApi(r.status, msg);
  }
  return r.json() as Promise<T>;
}

export const qs = (o: Record<string, string | number | undefined | null | string[]>) => {
  const p = new URLSearchParams();
  for (const [k, v] of Object.entries(o)) {
    if (Array.isArray(v)) v.forEach((x) => p.append(k, x));
    else if (v !== undefined && v !== null && v !== "") p.set(k, String(v));
  }
  const s = p.toString();
  return s ? "?" + s : "";
};

// ---------- kiểu dữ liệu trả về ----------
export type ChanDoan = "Rẻ hơn thị trường" | "Hợp lý" | "Cao hơn thị trường";
export type NhaPho = {
  id: string; t: string; g: number; dt: number; mt: number | null; st: number | null; san: number | null; pn: number | null; wc: number | null;
  vt: number | null; hr: number | null; url: string; nguon: string; ai_full: number; lo80: number; hi80: number; chan_doan: ChanDoan;
  duong: string | null; huong: string | null; so: string | null; cn: string | null; hd: string | null; lat: number | null; lon: number | null;
  thue: number | null; ys: number | null; gt: Record<string, number> | null; _lech: number;
};
export type CanHo = { id: string; da: string | null; ph: string; dt: number; pn: number | null; g: number; ai: number; lo: number; hi: number; diff: number; cd: ChanDoan; url: string; thue: number | null; ys: number | null };
export type Dat = { id: string; ph: string; duong: string | null; dt: number; mt: number | null; g: number; ai: number; lo: number; hi: number; diff: number; cd: ChanDoan; url: string };
export type Trang<T> = { tong: number; trang: number; so_dong: number; ket_qua: T[] };
export type GiaiThich = { nen_ty: number; nhom: { nhom: string; log: number; phan_tram: number }[] };
export type KetQuaNha = {
  gia_ty: number; khoang_80_ty: [number, number]; khoang_50_ty: [number, number]; don_gia_trieu_m2: number; mo_hinh: string;
  ngay_du_lieu: string; giai_thich: GiaiThich | null; thue_trieu_thang: number; ty_suat_pt: number;
};
export type KetQuaCanHo = { gia_ty: number; khoang_80_ty: [number, number]; don_gia_trieu_m2: number; du_an_nhan_ra: boolean; mo_hinh: string; thue_trieu_thang: number; ty_suat_pt: number };
export type KetQuaDat = { gia_ty: number; khoang_80_ty: [number, number]; don_gia_trieu_m2: number; don_gia_nen_phuong: number; phuong_co_du_lieu: boolean; mo_hinh: string };
export type TongQuan = {
  so_lieu: Record<string, string>;
  bang_mo_hinh: { mo_hinh: string; mae_ty: number; mape: number; r2: number }[];
  giai_thich: { nen_log: number; mo_hinh: string; nhom: string[] };
  web_model: Record<string, string | number>;
  can_ho: Record<string, string | number>;
  dat: Record<string, string | number>;
  thue: { mape: Record<string, number>; so_tin: Record<string, number>; ty_suat_tv: Record<string, number> };
};
export type DanhMuc = {
  phuong_dat: { ma: string; ten: string; quan: string; so_lo: number }[];
  du_an: { ma: string; ten: string; so_tin: number; quan: string; phuong: string }[];
  phuong_can_ho: { k: string; ten: string }[];
  duong_phu_hoa: string[];
};
