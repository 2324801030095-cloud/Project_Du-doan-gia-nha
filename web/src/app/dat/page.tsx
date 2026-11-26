import type { Metadata } from "next";
import Link from "next/link";
import { BoLoc, PhanTrang, TheTinRao } from "@/components/tin";
import { goiApi, qs, type Dat, type Trang } from "@/lib/api";
import { so } from "@/lib/format";
import { layPhien } from "@/lib/session";
import { maDaLuu } from "@/lib/yeu-thich";

export const metadata: Metadata = { title: "Đất nền" };
const SO_DONG = 12;

export default async function Page(props: PageProps<"/dat">) {
  const t = (await props.searchParams) as Record<string, string | undefined>;
  const trang = Math.max(1, Number(t.trang) || 1);
  const [ds, phien] = await Promise.all([goiApi<Trang<Dat>>("/dat" + qs({ ...t, trang, so_dong: SO_DONG })), layPhien()]);
  const luu = await maDaLuu(phien?.user.id, "dat");
  return (
    <div className="space-y-6">
      <header className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold">Đất nền Thủ Dầu Một</h1>
          <p className="mt-2 max-w-3xl text-slate-600">{so(ds.tong, 0)} lô đất đang rao, so với giá mô hình đất.</p>
        </div>
        <Link href="/dinh-gia?loai=dat" className="nut-vang">Định giá đất</Link>
      </header>
      <BoLoc thamSo={t} goiYTim="Phường, tên đường…" />
      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {ds.ket_qua.map((x) => (
          <TheTinRao
            key={x.id}
            x={{
              loai: "dat", id: x.id, tieuDe: `Đất ${so(x.dt)} m² – ${x.ph}`, gia: x.g, uoc: x.ai, lo: x.lo, hi: x.hi, cd: x.cd, url: x.url,
              daLuu: luu.has(x.id), dangNhap: Boolean(phien),
              phu: [`${so(x.dt)} m²`, x.mt && `ngang ${so(x.mt)} m`, x.duong, `${so((x.g * 1000) / x.dt)} tr/m²`].filter(Boolean).join(" · "),
            }}
          />
        ))}
      </div>
      <PhanTrang tong={ds.tong} trang={trang} soDong={SO_DONG} thamSo={t} duong="/dat" />
    </div>
  );
}
