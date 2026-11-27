// Danh sách tin căn hộ (phần mở rộng) với bộ lọc trên URL (?gia_min=…); lọc / phân trang làm ở API.
import type { Metadata } from "next";
import Link from "next/link";
import { BoLoc, PhanTrang, TheTinRao } from "@/components/tin";
import { anhKhuVuc } from "@/lib/anh";
import { goiApi, qs, type CanHo, type Trang } from "@/lib/api";
import { so } from "@/lib/format";
import { layPhien } from "@/lib/session";
import { maDaLuu } from "@/lib/yeu-thich";

export const metadata: Metadata = { title: "Căn hộ" };
const SO_DONG = 12;

export default async function Page(props: PageProps<"/can-ho">) {
  const t = (await props.searchParams) as Record<string, string | undefined>;
  const trang = Math.max(1, Number(t.trang) || 1);
  const [ds, phien] = await Promise.all([goiApi<Trang<CanHo>>("/can-ho" + qs({ ...t, trang, so_dong: SO_DONG })), layPhien()]);
  const luu = await maDaLuu(phien?.user.id, "can_ho");
  return (
    <div className="space-y-6">
      <header className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold">Căn hộ Thủ Dầu Một</h1>
          <p className="mt-2 max-w-3xl text-slate-600">{so(ds.tong, 0)} căn hộ đang rao, so với giá mô hình căn hộ (dự án là yếu tố quyết định giá).</p>
        </div>
        <Link href="/dinh-gia?loai=can-ho" className="nut-vang">Định giá căn hộ</Link>
      </header>
      <BoLoc thamSo={t} goiYTim="Tên dự án, phường…" />
      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {ds.ket_qua.map((x) => (
          <TheTinRao
            key={x.id}
            x={{
              loai: "can_ho", id: x.id, tieuDe: x.da ?? `Căn hộ ${so(x.dt)} m² – ${x.ph}`, gia: x.g, uoc: x.ai, lo: x.lo, hi: x.hi, cd: x.cd, url: x.url,
              anh: anhKhuVuc("can_ho", x.id), daLuu: luu.has(x.id), dangNhap: Boolean(phien),
              phu: [`${so(x.dt)} m²`, x.pn && `${x.pn} PN`, x.ph, x.thue && `thuê ≈ ${so(x.thue)} tr/tháng`].filter(Boolean).join(" · "),
            }}
          />
        ))}
      </div>
      <PhanTrang tong={ds.tong} trang={trang} soDong={SO_DONG} thamSo={t} duong="/can-ho" />
    </div>
  );
}
