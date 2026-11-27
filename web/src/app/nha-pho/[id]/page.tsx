// Chi tiết một tin nhà phố: giá rao so với giá mô hình + khoảng 80%, giải thích theo nhóm yếu tố,
// bản đồ vị trí gần đúng, giá thuê ước tính (nếu có). Tin đã gỡ ở kỳ mới nhất -> 404.
import { ExternalLink } from "lucide-react";
import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { GiaiThich } from "@/components/giai-thich";
import { BanDoNho } from "@/components/ban-do-nho";
import { ThuVienAnh } from "@/components/thu-vien-anh";
import { anhNhaPho } from "@/lib/anh";
import { ChanDoan, KhoangGia } from "@/components/tin";
import { NutYeuThich } from "@/components/nut-yeu-thich";
import { goiApi, LoiApi, type NhaPho } from "@/lib/api";
import { LOI_VAO, so, ty } from "@/lib/format";
import { layPhien } from "@/lib/session";
import { maDaLuu } from "@/lib/yeu-thich";

async function layTin(id: string) {
  try {
    return await goiApi<NhaPho>(`/nha-pho/${encodeURIComponent(id)}`);
  } catch (e) {
    if (e instanceof LoiApi && e.status === 404) notFound();
    throw e;
  }
}

export async function generateMetadata(props: PageProps<"/nha-pho/[id]">): Promise<Metadata> {
  const x = await layTin((await props.params).id);
  return { title: x.t.slice(0, 60) };
}

export default async function Page(props: PageProps<"/nha-pho/[id]">) {
  const { id } = await props.params;
  const [x, phien] = await Promise.all([layTin(id), layPhien()]);
  const luu = await maDaLuu(phien?.user.id, "nha_pho");
  const thongSo: [string, string | null][] = [
    ["Diện tích đất", `${so(x.dt)} m²`], ["Mặt tiền (ngang)", x.mt ? `${so(x.mt)} m` : null], ["Số tầng", x.st ? so(x.st, 0) : null],
    ["Diện tích sàn", x.san ? `${so(x.san, 0)} m²` : null], ["Phòng ngủ", x.pn ? so(x.pn, 0) : null], ["WC", x.wc ? so(x.wc, 0) : null],
    ["Lối vào", x.vt ? LOI_VAO[x.vt] : null], ["Hẻm / đường rộng", x.hr ? `${so(x.hr)} m` : null], ["Đường", x.duong],
    ["Hướng", x.huong], ["Pháp lý", x.so], ["Nguồn", x.nguon], ["Cập nhật", x.cn],
  ];
  return (
    <div className="space-y-6">
      <nav className="text-sm text-slate-500"><Link href="/nha-pho" className="hover:text-navy-800">← Nhà phố Phú Hòa</Link></nav>
      <header className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div className="max-w-3xl">
          <div className="flex items-center gap-3"><ChanDoan cd={x.chan_doan} /><NutYeuThich loai="nha_pho" maTin={x.id} daLuu={luu.has(x.id)} dangNhap={Boolean(phien)} /></div>
          <h1 className="mt-3 text-2xl font-bold sm:text-3xl">{x.t}</h1>
        </div>
        <a href={x.url} target="_blank" rel="noopener noreferrer" className="nut-vien shrink-0">Xem tin gốc <ExternalLink size={16} /></a>
      </header>

      <div className="grid gap-6 lg:grid-cols-3">
        <section className="the p-6 lg:col-span-2">
          <div className="mb-6"><ThuVienAnh anh={anhNhaPho(x.id, x.st, x.vt)} tieuDe={x.t} /></div>
          <div className="grid gap-6 sm:grid-cols-3">
            <div><p className="nhan">Giá rao</p><p className="text-3xl font-bold text-navy-900">{ty(x.g)}</p><p className="text-sm text-slate-500">{so((x.g * 1000) / x.dt)} triệu/m²</p></div>
            <div><p className="nhan">Mô hình ước lượng</p><p className="text-3xl font-bold text-gold-600">{ty(x.ai_full)}</p><p className="text-sm text-slate-500">Random Forest, không học tin này</p></div>
            <div><p className="nhan">Cho thuê ước tính</p><p className="text-3xl font-bold text-navy-900">{x.thue ? `${so(x.thue)} tr` : "–"}</p><p className="text-sm text-slate-500">/tháng{x.ys ? ` · tỷ suất ${so(x.ys)}%/năm` : ""}</p></div>
          </div>
          <div className="mt-6"><KhoangGia lo={x.lo80} hi={x.hi80} uoc={x.ai_full} rao={x.g} /></div>
          <p className="mt-4 rounded-xl bg-navy-50 p-4 text-sm text-slate-700">
            Giá rao {x._lech >= 0 ? "cao" : "thấp"} hơn giá mô hình ước lượng <b>{so(Math.abs(x._lech * 100), 0)}%</b>.{" "}
            {x.chan_doan === "Rẻ hơn thị trường" && "Giá rao nằm dưới khoảng 80%: ứng viên đáng xem, nhưng cần kiểm tra pháp lý và hiện trạng."}
            {x.chan_doan === "Cao hơn thị trường" && "Giá rao nằm trên khoảng 80%: có thể là giá kỳ vọng cao hoặc căn có ưu điểm mô hình không thấy."}
            {x.chan_doan === "Hợp lý" && "Giá rao nằm trong khoảng 80% của mô hình."}
          </p>
          {x.gt && (
            <div className="mt-8">
              <h2 className="mb-4 text-lg font-semibold">Vì sao căn này có giá như vậy</h2>
              <GiaiThich nhom={Object.entries(x.gt).map(([nhom, log]) => ({ nhom, log }))}
                chuThich="Đóng góp của từng nhóm yếu tố so với căn trung bình trong dữ liệu, tính theo đường đi trên các cây của Random Forest (mô hình không học căn này)." />
            </div>
          )}
        </section>
        <aside className="space-y-6">
          <section className="the p-6">
            <h2 className="mb-3 text-lg font-semibold">Thông số</h2>
            <dl className="divide-y divide-navy-50 text-sm">
              {thongSo.filter(([, v]) => v).map(([k, v]) => (
                <div key={k} className="flex justify-between gap-4 py-2"><dt className="text-slate-500">{k}</dt><dd className="text-right font-medium">{v}</dd></div>
              ))}
            </dl>
          </section>
          {x.lat && x.lon && (
            <section className="the overflow-hidden p-2"><BanDoNho lat={x.lat} lon={x.lon} nhan={ty(x.g)} /></section>
          )}
        </aside>
      </div>
    </div>
  );
}
