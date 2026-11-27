// Thành phần hiển thị tin rao: nhãn chẩn đoán, thanh khoảng 80%, thẻ tin trong danh sách.
import { ExternalLink, Images } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { MAU_CHAN_DOAN, so, ty } from "@/lib/format";
import { NutYeuThich } from "./nut-yeu-thich";

/** Nhãn chẩn đoán giá rao: Rẻ hơn thị trường / Hợp lý / Cao hơn thị trường. */
export function ChanDoan({ cd }: { cd: string }) {
  return <span className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-semibold ring-1 ring-inset ${MAU_CHAN_DOAN[cd] ?? ""}`}>{cd}</span>;
}

// Thanh khoảng 80%: vạch xám = khoảng, chấm vàng = giá ước lượng, chấm xanh = giá rao
export function KhoangGia({ lo, hi, uoc, rao }: { lo: number; hi: number; uoc: number; rao?: number }) {
  const a = Math.min(lo, rao ?? lo) * 0.92, b = Math.max(hi, rao ?? hi) * 1.05;
  const x = (v: number) => `${((v - a) / (b - a)) * 100}%`;
  return (
    <div className="mt-2" aria-label={`Khoảng 80% từ ${ty(lo)} đến ${ty(hi)}`}>
      <div className="relative h-2 rounded-full bg-navy-50">
        <div className="absolute h-2 rounded-full bg-navy-200" style={{ left: x(lo), width: `calc(${x(hi)} - ${x(lo)})` }} />
        <div className="absolute -top-1 size-4 -translate-x-1/2 rounded-full border-2 border-white bg-gold-500 shadow" style={{ left: x(uoc) }} title="Giá ước lượng" />
        {rao !== undefined && <div className="absolute -top-0.5 size-3 -translate-x-1/2 rounded-full border-2 border-white bg-navy-800 shadow" style={{ left: x(rao) }} title="Giá rao" />}
      </div>
      <div className="mt-1 flex justify-between text-[11px] text-slate-500"><span>{ty(lo)}</span><span>Khoảng tham khảo 80%</span><span>{ty(hi)}</span></div>
    </div>
  );
}

/** Dữ liệu một thẻ tin: gia = giá rao, uoc = giá mô hình, lo / hi = khoảng 80% (đều tỷ đồng); cd = chẩn đoán. */
export type TheTin = {
  loai: "nha_pho" | "can_ho";
  id: string; tieuDe: string; phu: string; gia: number; uoc: number; lo: number; hi: number; cd: string; url: string; href?: string;
  daLuu?: boolean; dangNhap: boolean; anh?: string; soAnh?: number;
};

export function TheTinRao({ x }: { x: TheTin }) {
  const lech = (x.gia / x.uoc - 1) * 100;
  return (
    <article className="the flex flex-col overflow-hidden transition hover:shadow-md">
      {x.anh && (
        <div className="relative aspect-[16/10] bg-navy-50">
          <Image src={x.anh} alt={`Ảnh minh họa – ${x.tieuDe}`} fill sizes="(min-width: 1024px) 33vw, (min-width: 640px) 50vw, 100vw" className="object-cover" />
          <span className="absolute bottom-2 left-2 rounded-md bg-black/55 px-2 py-0.5 text-[11px] text-white">Ảnh minh họa</span>
          {x.soAnh && x.soAnh > 1 && <span className="absolute bottom-2 right-2 flex items-center gap-1 rounded-md bg-black/55 px-2 py-0.5 text-[11px] text-white"><Images size={12} />{x.soAnh}</span>}
        </div>
      )}
      <div className="flex flex-1 flex-col p-5">
      <div className="flex items-start justify-between gap-3">
        <ChanDoan cd={x.cd} />
        <NutYeuThich loai={x.loai} maTin={x.id} daLuu={x.daLuu ?? false} dangNhap={x.dangNhap} />
      </div>
      <h3 className="mt-3 line-clamp-2 min-h-12 font-semibold">
        {x.href ? <Link href={x.href} className="hover:text-navy-500">{x.tieuDe}</Link> : x.tieuDe}
      </h3>
      <p className="mt-1 text-sm text-slate-500">{x.phu}</p>
      <div className="mt-4 grid grid-cols-2 gap-3">
        <div><p className="nhan">Giá rao trong tin</p><p className="text-lg font-bold text-navy-900">{ty(x.gia)}</p></div>
        <div><p className="nhan">Giá mô hình ước tính</p><p className="text-lg font-bold text-gold-600">{ty(x.uoc)}</p></div>
      </div>
      <p className="mt-1 text-xs text-slate-500">Giá rao {lech >= 0 ? "cao" : "thấp"} hơn ước lượng {so(Math.abs(lech), 0)}%</p>
      <KhoangGia lo={x.lo} hi={x.hi} uoc={x.uoc} rao={x.gia} />
      <div className="mt-4 flex items-center justify-between border-t border-navy-50 pt-3 text-sm">
        {x.href ? <Link href={x.href} className="font-semibold text-navy-700 hover:text-navy-900">Xem chi tiết →</Link> : <span />}
        <a href={x.url} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 text-slate-500 hover:text-navy-800">
          Tin gốc <ExternalLink size={14} />
        </a>
      </div>
      </div>
    </article>
  );
}

// Bộ lọc dùng form GET thuần: chạy cả khi chưa tải JavaScript, URL chia sẻ được
export function BoLoc({ thamSo, goiYTim }: { thamSo: Record<string, string | undefined>; goiYTim: string }) {
  return (
    <form method="get" className="the grid gap-3 p-4 sm:grid-cols-2 lg:grid-cols-7">
      <div className="lg:col-span-2">
        <label className="nhan" htmlFor="q">Tìm</label>
        <input id="q" name="q" defaultValue={thamSo.q} placeholder={goiYTim} className="o-nhap" />
      </div>
      <div>
        <label className="nhan" htmlFor="gia_min">Giá từ (tỷ)</label>
        <input id="gia_min" name="gia_min" type="number" step="0.1" min="0" defaultValue={thamSo.gia_min} className="o-nhap" />
      </div>
      <div>
        <label className="nhan" htmlFor="gia_max">đến (tỷ)</label>
        <input id="gia_max" name="gia_max" type="number" step="0.1" min="0" defaultValue={thamSo.gia_max} className="o-nhap" />
      </div>
      <div>
        <label className="nhan" htmlFor="chan_doan">Chẩn đoán</label>
        <select id="chan_doan" name="chan_doan" defaultValue={thamSo.chan_doan ?? ""} className="o-nhap">
          <option value="">Tất cả</option>
          <option>Rẻ hơn thị trường</option>
          <option>Hợp lý</option>
          <option>Cao hơn thị trường</option>
        </select>
      </div>
      <div>
        <label className="nhan" htmlFor="sap_xep">Sắp xếp</label>
        <select id="sap_xep" name="sap_xep" defaultValue={thamSo.sap_xep ?? "re_nhat"} className="o-nhap">
          <option value="re_nhat">Rẻ nhất so với thị trường</option>
          <option value="gia_tang">Giá tăng dần</option>
          <option value="gia_giam">Giá giảm dần</option>
          <option value="dt_giam">Diện tích lớn nhất</option>
        </select>
      </div>
      <div className="flex items-end"><button className="nut-chinh w-full">Lọc</button></div>
    </form>
  );
}

export function PhanTrang({ tong, trang, soDong, thamSo, duong }: { tong: number; trang: number; soDong: number; thamSo: Record<string, string | undefined>; duong: string }) {
  const soTrang = Math.max(1, Math.ceil(tong / soDong));
  const link = (t: number) => {
    const p = new URLSearchParams(Object.entries(thamSo).filter(([, v]) => v) as [string, string][]);
    p.set("trang", String(t));
    return `${duong}?${p}`;
  };
  if (soTrang <= 1) return null;
  return (
    <nav className="mt-8 flex items-center justify-center gap-2" aria-label="Phân trang">
      {trang > 1 && <Link className="nut-vien" href={link(trang - 1)}>← Trước</Link>}
      <span className="px-3 text-sm text-slate-600">Trang {trang} / {soTrang}</span>
      {trang < soTrang && <Link className="nut-vien" href={link(trang + 1)}>Sau →</Link>}
    </nav>
  );
}
