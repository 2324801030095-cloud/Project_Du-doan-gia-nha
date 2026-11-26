"use client";
import { Building2, House, LoaderCircle } from "lucide-react";
import { useState } from "react";
import type { DanhMuc } from "@/lib/api";
import { LOI_VAO } from "@/lib/format";
import { KetQuaDinhGia, type KetQua } from "./ket-qua-dinh-gia";

type Loai = "nha-pho" | "can-ho";

const TAB: { k: Loai; ten: string; icon: React.ReactNode }[] = [
  { k: "nha-pho", ten: "Nhà phố", icon: <House size={16} /> },
  { k: "can-ho", ten: "Căn hộ", icon: <Building2 size={16} /> },
];

function O({ ten, children, goiY, rong }: { ten: string; children: React.ReactNode; goiY?: string; rong?: boolean }) {
  return (
    <label className={rong ? "block sm:col-span-full" : "block"}>
      <span className="nhan">{ten}</span>
      {children}
      {goiY && <span className="mt-1 block text-xs text-slate-400">{goiY}</span>}
    </label>
  );
}
const So = (p: { name: string; ph?: string; min?: number; max?: number; step?: number; req?: boolean; def?: number }) => (
  <input name={p.name} type="number" inputMode="decimal" className="o-nhap" placeholder={p.ph && `VD: ${p.ph}`} min={p.min} max={p.max} step={p.step ?? "any"} required={p.req} defaultValue={p.def} />
);

// Đọc form -> JSON: ô trống bỏ qua (mô hình tự điền trung vị), số đổi kiểu số, ô đánh dấu đổi 0/1
function docForm(f: HTMLFormElement) {
  const o: Record<string, unknown> = {};
  new FormData(f).forEach((v, k) => {
    const s = String(v).trim();
    if (s === "") return;
    const el = f.elements.namedItem(k) as HTMLInputElement | null;
    o[k] = el?.type === "number" || el?.dataset.so ? Number(s) : s;
  });
  // ô đánh dấu: có tích = 1 (hoặc true); không tích = bỏ qua -> mô hình coi là "không rõ" thay vì "không có"
  f.querySelectorAll<HTMLInputElement>("input[type=checkbox]").forEach((c) => {
    if (c.checked) o[c.name] = c.dataset.bool ? true : 1;
    else delete o[c.name];
  });
  return o;
}

export function FormDinhGia({ danhMuc, loaiBanDau, doPhu }: { danhMuc: DanhMuc; loaiBanDau: Loai; doPhu?: { trong: number; tong: number } }) {
  const [loai, setLoai] = useState<Loai>(loaiBanDau);
  const [kq, setKq] = useState<KetQua | null>(null);
  const [loi, setLoi] = useState("");
  const [dang, setDang] = useState(false);

  async function gui(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setDang(true); setLoi("");
    try {
      const r = await fetch(`/api/dinh-gia/${loai}`, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(docForm(e.currentTarget)) });
      const j = await r.json();
      if (!r.ok) throw new Error(j.loi ?? "Không định giá được");
      setKq(j);
    } catch (er) {
      setLoi(er instanceof Error ? er.message : "Lỗi"); setKq(null);
    } finally {
      setDang(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="the p-6">
        <div className="mx-auto mb-5 flex max-w-md gap-2 rounded-xl bg-navy-50 p-1" role="tablist">
          {TAB.map((t) => (
            <button key={t.k} role="tab" aria-selected={loai === t.k} onClick={() => { setLoai(t.k); setKq(null); setLoi(""); }}
              className={`flex flex-1 items-center justify-center gap-2 rounded-lg px-3 py-2 text-sm font-semibold transition ${loai === t.k ? "bg-white text-navy-900 shadow-sm" : "text-slate-500 hover:text-navy-800"}`}>
              {t.icon} {t.ten}
            </button>
          ))}
        </div>
        <form key={loai} onSubmit={gui} className="grid gap-x-4 gap-y-3 sm:grid-cols-2 lg:grid-cols-4">
          {loai === "nha-pho" && (
            <>
              <O ten="Diện tích đất (m²) *"><So name="dt_dat" req min={15} max={5000} def={80} /></O>
              <O ten="Ngang (m)"><So name="ngang" ph="4,5" min={1} max={200} /></O>
              <O ten="Dài (m)"><So name="dai" ph="18" min={1} max={500} /></O>
              <O ten="Số tầng" goiY="1 trệt 1 lầu = 2"><So name="so_tang" ph="2" min={1} max={10} step={1} /></O>
              <O ten="Tổng diện tích sàn (m²)"><So name="dt_san" ph="160" min={10} /></O>
              <O ten="Phòng ngủ"><So name="phong_ngu" ph="3" min={0} max={30} step={1} /></O>
              <O ten="WC"><So name="so_wc" ph="2" min={0} max={30} step={1} /></O>
              <O ten="Lối vào">
                <select name="cap_loi_vao" data-so="1" className="o-nhap" defaultValue="">
                  <option value="">Không rõ</option>
                  {Object.entries(LOI_VAO).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
                </select>
              </O>
              <O ten="Hẻm / đường rộng (m)"><So name="hem_rong" ph="6" min={1} max={60} /></O>
              <O ten="Tên đường (Phú Hòa)">
                <input name="duong" list="duong-ph" className="o-nhap" placeholder="Nguyễn Thị Minh Khai" />
                <datalist id="duong-ph">{danhMuc.duong_phu_hoa.map((d) => <option key={d} value={d} />)}</datalist>
              </O>
              <label className="flex items-center gap-2 text-sm sm:col-span-full"><input type="checkbox" name="mat_tien_duong" className="size-4" /> Nhà mặt tiền đường</label>
              <O rong ten="Mô tả thêm (không bắt buộc)" goiY="Mô hình đọc từ khóa: sổ riêng, khu dân cư, nhà mới, hẻm xe hơi…">
                <textarea name="mo_ta" rows={1} maxLength={4000} className="o-nhap" placeholder="1 trệt 1 lầu, khu dân cư, sổ hồng riêng" />
              </O>
            </>
          )}
          {loai === "can-ho" && (
            <>
              <O ten="Diện tích sử dụng (m²) *"><So name="dt_su_dung" req min={16} max={500} def={68} /></O>
              <O ten="Dự án" goiY="Gõ để chọn; dự án quyết định phần lớn giá căn hộ">
                <input name="du_an" list="du-an" className="o-nhap" placeholder="Happy One Central" />
                <datalist id="du-an">{danhMuc.du_an.map((d) => <option key={d.ma} value={d.ten}>{d.so_tin} tin</option>)}</datalist>
              </O>
              <O ten="Phòng ngủ"><So name="phong_ngu" ph="2" min={0} max={6} step={1} /></O>
              <O ten="WC"><So name="so_wc" ph="2" min={0} max={6} step={1} /></O>
              <O ten="Tầng"><So name="tang" ph="12" min={0} max={60} step={1} /></O>
              <O ten="Nội thất">
                <select name="noi_that_cap" data-so="1" className="o-nhap" defaultValue="">
                  <option value="">Không rõ</option><option value="0">Bàn giao thô</option><option value="1">Cơ bản</option><option value="2">Đầy đủ</option><option value="3">Cao cấp</option>
                </select>
              </O>
              <label className="flex items-center gap-2 text-sm"><input type="checkbox" name="so_hong" className="size-4" /> Đã có sổ hồng</label>
              <label className="flex items-center gap-2 text-sm"><input type="checkbox" name="nha_o_xa_hoi" className="size-4" /> Nhà ở xã hội</label>
            </>
          )}
          {/* nút luôn nằm trong tầm nhìn: dính đáy màn hình khi form dài hơn cửa sổ */}
          <div className="sticky bottom-0 z-10 -mx-6 -mb-6 mt-2 border-t border-navy-100 bg-white/95 px-6 py-4 backdrop-blur sm:col-span-full">
            <button className="nut-vang mx-auto flex w-full max-w-md py-3 text-base" disabled={dang}>
              {dang && <LoaderCircle size={18} className="animate-spin" />} Định giá
            </button>
          </div>
        </form>
      </div>

      <KetQuaDinhGia kq={kq} loi={loi} dang={dang} doPhu={loai === "nha-pho" ? doPhu : undefined} />
    </div>
  );
}
