import type { Metadata } from "next";
import { BoLoc, PhanTrang, TheTinRao } from "@/components/tin";
import { goiApi, qs, type NhaPho, type Trang } from "@/lib/api";
import { so } from "@/lib/format";
import { layPhien } from "@/lib/session";
import { maDaLuu } from "@/lib/yeu-thich";

export const metadata: Metadata = { title: "Nhà phố Phú Hòa" };
const SO_DONG = 12;

export default async function Page(props: PageProps<"/nha-pho">) {
  const t = (await props.searchParams) as Record<string, string | undefined>;
  const trang = Math.max(1, Number(t.trang) || 1);
  const [ds, phien] = await Promise.all([
    goiApi<Trang<NhaPho>>("/nha-pho" + qs({ ...t, trang, so_dong: SO_DONG })),
    layPhien(),
  ]);
  const luu = await maDaLuu(phien?.user.id, "nha_pho");
  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-3xl font-bold">Nhà phố Phú Hòa đang rao</h1>
        <p className="mt-2 max-w-3xl text-slate-600">
          {so(ds.tong, 0)} tin còn rao ở kỳ thu thập mới nhất. Mỗi tin có giá Random Forest ước lượng (mô hình không học chính tin đó) và
          khoảng 80%: giá rao dưới khoảng là <b>rẻ hơn thị trường</b>, trên khoảng là <b>cao hơn thị trường</b>.
        </p>
      </header>
      <BoLoc thamSo={t} goiYTim="Tên đường, tiêu đề…" />
      {ds.ket_qua.length === 0 ? (
        <p className="the p-10 text-center text-slate-500">Không có tin phù hợp bộ lọc.</p>
      ) : (
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {ds.ket_qua.map((x) => (
            <TheTinRao
              key={x.id}
              x={{
                loai: "nha_pho", id: x.id, tieuDe: x.t, gia: x.g, uoc: x.ai_full, lo: x.lo80, hi: x.hi80, cd: x.chan_doan, url: x.url,
                href: `/nha-pho/${x.id}`, daLuu: luu.has(x.id), dangNhap: Boolean(phien),
                phu: [`${so(x.dt)} m²`, x.st && `${so(x.st, 0)} tầng`, x.duong, x.nguon].filter(Boolean).join(" · "),
              }}
            />
          ))}
        </div>
      )}
      <PhanTrang tong={ds.tong} trang={trang} soDong={SO_DONG} thamSo={t} duong="/nha-pho" />
    </div>
  );
}
