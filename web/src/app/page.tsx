// Trang chủ (máy chủ kết xuất mỗi lần yêu cầu): số liệu tóm tắt từ /tong-quan và 3 tin "rẻ hơn thị trường".
// Mọi con số lấy từ API mô hình (kết quả notebook), không gõ tay trong trang.
import { BarChart3, Bot, Calculator, Map, ShieldCheck, TrendingUp } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { TheTinRao } from "@/components/tin";
import { anhNhaPho } from "@/lib/anh";
import { goiApi, qs, type NhaPho, type TongQuan, type Trang } from "@/lib/api";
import { so } from "@/lib/format";
import { layPhien } from "@/lib/session";
import { maDaLuu } from "@/lib/yeu-thich";

const TINH_NANG = [
  { href: "/dinh-gia", icon: Calculator, ten: "Định giá tức thì", mo: "Random Forest trên máy chủ, kèm khoảng 80% và giải thích yếu tố." },
  { href: "/nha-pho", icon: ShieldCheck, ten: "Chẩn đoán tin rao", mo: "Mỗi tin đang rao được xếp rẻ / hợp lý / cao so với thị trường." },
  { href: "/ban-do", icon: Map, ten: "Bản đồ giá", mo: "Nhà phố, căn hộ, cho thuê trên bản đồ Thủ Dầu Một." },
  { href: "/xu-huong", icon: TrendingUp, ten: "Xu hướng", mo: "Tín hiệu đổi giá cùng một căn và kịch bản theo kỳ hạn." },
  { href: "/mo-hinh", icon: BarChart3, ten: "Minh bạch mô hình", mo: "Sai số trên tập test, khoảng tin cậy, so sánh đối chứng." },
  { href: "/tro-ly", icon: Bot, ten: "Trợ lý AI", mo: "Hỏi bằng tiếng Việt tự nhiên; số liệu lấy từ mô hình của đề tài." },
];

export default async function Home() {
  const [tq, re, phien] = await Promise.all([
    goiApi<TongQuan>("/tong-quan"),
    goiApi<Trang<NhaPho>>("/nha-pho" + qs({ chan_doan: "Rẻ hơn thị trường", so_dong: 3 })),
    layPhien(),
  ]);
  const luu = await maDaLuu(phien?.user.id, "nha_pho");
  const s = tq.so_lieu;
  return (
    <div className="space-y-12">
      <section className="relative overflow-hidden rounded-3xl bg-navy-900 text-white">
        <Image src="/img/aerial.jpg" alt="Khu đô thị nhìn từ trên cao" fill priority className="object-cover opacity-30" sizes="100vw" />
        <div className="relative grid gap-8 p-8 sm:p-12 lg:grid-cols-5">
          <div className="lg:col-span-3">
            <p className="text-sm font-semibold uppercase tracking-widest text-gold-400">Đề tài Học máy · Thủ Dầu Một</p>
            <h1 className="mt-3 text-4xl font-bold leading-tight text-white sm:text-5xl">Biết giá thị trường của một căn nhà ở Phú Hòa trước khi xuống tiền</h1>
            <p className="mt-4 max-w-xl text-navy-100">
              Mô hình học trên {s.N_ALL} tin rao thật (dữ liệu đến {s.NGAY}), cho giá ước lượng, khoảng 80% đã kiểm chứng và lý do vì sao.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link href="/dinh-gia" className="nut-vang px-6 py-3 text-base">Định giá ngay</Link>
              <Link href="/nha-pho" className="nut border border-white/30 px-6 py-3 text-base text-white hover:bg-white/10">Xem tin đang rao</Link>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3 self-end lg:col-span-2">
            {[["Mô hình", s.BEST], ["Sai số test Phú Hòa", `${s.TEST_MAPE}%`], ["Tin Phú Hòa đang rao", s.N_PH], ["Baseline (đơn giá phường)", `${s.B_MAPE}%`]].map(([k, v]) => (
              <div key={k} className="rounded-2xl bg-white/10 p-4 backdrop-blur">
                <p className="text-xs text-navy-100">{k}</p><p className="mt-1 text-lg font-bold">{v}</p>
              </div>
            ))}
          </div>
        </div>
        <p className="relative px-8 pb-3 text-[10px] text-navy-200 sm:px-12">Ảnh: Khudothi, Wikimedia Commons, CC BY-SA 4.0</p>
      </section>

      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {TINH_NANG.map((t) => (
          <Link key={t.href} href={t.href} className="the group p-6 transition hover:-translate-y-0.5 hover:shadow-md">
            <span className="grid size-11 place-items-center rounded-xl bg-navy-100 text-navy-800 group-hover:bg-gold-400"><t.icon size={20} /></span>
            <h2 className="mt-4 text-lg font-semibold">{t.ten}</h2>
            <p className="mt-1 text-sm text-slate-600">{t.mo}</p>
          </Link>
        ))}
      </section>

      <section>
        <div className="mb-4 flex items-end justify-between">
          <div>
            <h2 className="text-2xl font-bold">Đang rao rẻ hơn thị trường</h2>
            <p className="text-slate-600">{so(re.tong, 0)} tin Phú Hòa có giá rao dưới khoảng 80% của mô hình.</p>
          </div>
          <Link href="/nha-pho?chan_doan=R%E1%BA%BB+h%C6%A1n+th%E1%BB%8B+tr%C6%B0%E1%BB%9Dng" className="nut-vien">Xem tất cả</Link>
        </div>
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {re.ket_qua.map((x) => (
            <TheTinRao key={x.id} x={{ loai: "nha_pho", id: x.id, tieuDe: x.t, gia: x.g, uoc: x.ai_full, lo: x.lo80, hi: x.hi80, cd: x.chan_doan, url: x.url,
              anh: anhNhaPho(x.id, x.st, x.vt)[0], soAnh: 3, href: `/nha-pho/${x.id}`, daLuu: luu.has(x.id), dangNhap: Boolean(phien), phu: [`${so(x.dt)} m²`, x.duong].filter(Boolean).join(" · ") }} />
          ))}
        </div>
      </section>
    </div>
  );
}
