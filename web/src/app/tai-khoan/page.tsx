import { desc, eq } from "drizzle-orm";
import type { Metadata } from "next";
import Link from "next/link";
import { ChanDoan } from "@/components/tin";
import { NutYeuThich } from "@/components/nut-yeu-thich";
import { goiApi, qs, type NhaPho } from "@/lib/api";
import { db } from "@/lib/db";
import { lichSuDinhGia, yeuThich } from "@/lib/db/schema";
import { so, ty } from "@/lib/format";
import { canDangNhap } from "@/lib/session";

export const metadata: Metadata = { title: "Tài khoản" };
const TEN_LOAI: Record<string, string> = { "nha-pho": "Nhà phố", "can-ho": "Căn hộ", dat: "Đất", nha_pho: "Nhà phố", can_ho: "Căn hộ" };

export default async function Page() {
  const { user } = await canDangNhap("/tai-khoan");
  const [luu, lichSu] = await Promise.all([
    db.select().from(yeuThich).where(eq(yeuThich.userId, user.id)).orderBy(desc(yeuThich.createdAt)),
    db.select().from(lichSuDinhGia).where(eq(lichSuDinhGia.userId, user.id)).orderBy(desc(lichSuDinhGia.createdAt)).limit(30),
  ]);
  const maNha = luu.filter((x) => x.loai === "nha_pho").map((x) => x.maTin);
  const nha = maNha.length ? await goiApi<NhaPho[]>("/nha-pho-theo-ma" + qs({ ma: maNha })) : [];
  const conLai = luu.filter((x) => x.loai !== "nha_pho");

  return (
    <div className="space-y-8">
      <header>
        <h1 className="text-3xl font-bold">Xin chào, {user.name}</h1>
        <p className="mt-1 text-slate-600">{user.email}{user.role === "admin" && " · Quản trị viên"}</p>
      </header>

      <section className="the p-6">
        <h2 className="text-xl font-semibold">Nhà phố đã lưu – so sánh</h2>
        {nha.length === 0 ? (
          <p className="mt-3 text-slate-500">Chưa lưu tin nào. Bấm trái tim ở <Link href="/nha-pho" className="font-semibold text-navy-700">danh sách nhà phố</Link>.</p>
        ) : (
          <div className="mt-4 overflow-x-auto">
            <table className="w-full min-w-[720px] text-sm">
              <thead className="text-left text-xs uppercase text-slate-500">
                <tr><th className="py-2 pr-3">Tin</th><th>Diện tích</th><th>Giá rao</th><th>Ước lượng</th><th>Khoảng 80%</th><th>Đơn giá</th><th>Chẩn đoán</th><th /></tr>
              </thead>
              <tbody className="divide-y divide-navy-50">
                {nha.map((x) => (
                  <tr key={x.id}>
                    <td className="max-w-64 py-3 pr-3"><Link href={`/nha-pho/${x.id}`} className="line-clamp-2 font-medium hover:text-navy-500">{x.t}</Link></td>
                    <td>{so(x.dt)} m²</td><td className="font-semibold">{ty(x.g)}</td><td className="text-gold-600">{ty(x.ai_full)}</td>
                    <td>{ty(x.lo80)} – {ty(x.hi80)}</td><td>{so((x.g * 1000) / x.dt)} tr/m²</td>
                    <td><ChanDoan cd={x.chan_doan} /></td>
                    <td><NutYeuThich loai="nha_pho" maTin={x.id} daLuu dangNhap /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {maNha.length > nha.length && <p className="mt-3 text-xs text-slate-500">{maNha.length - nha.length} tin đã lưu không còn rao ở kỳ thu thập mới nhất.</p>}
        {conLai.length > 0 && (
          <p className="mt-4 text-sm text-slate-600">
            Ngoài ra đã lưu {conLai.length} tin căn hộ / đất: {conLai.map((x) => `${TEN_LOAI[x.loai]} #${x.maTin}`).join(", ")}.
          </p>
        )}
      </section>

      <section className="the p-6">
        <h2 className="text-xl font-semibold">Lịch sử định giá</h2>
        {lichSu.length === 0 ? (
          <p className="mt-3 text-slate-500">Chưa có. <Link href="/dinh-gia" className="font-semibold text-navy-700">Định giá một căn</Link>.</p>
        ) : (
          <ul className="mt-4 divide-y divide-navy-50">
            {lichSu.map((h) => {
              const v = h.dauVao as Record<string, unknown>, k = h.ketQua as { gia_ty: number; khoang_80_ty: [number, number] };
              const dt = v.dt_dat ?? v.dt_su_dung ?? v.dt;
              return (
                <li key={h.id} className="flex flex-col gap-1 py-3 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <p className="font-medium">{TEN_LOAI[h.loai]} · {so(Number(dt))} m²{v.so_tang ? ` · ${v.so_tang} tầng` : ""}{v.du_an ? ` · ${v.du_an}` : ""}</p>
                    <p className="text-xs text-slate-500">{h.createdAt.toLocaleString("vi-VN", { timeZone: "Asia/Ho_Chi_Minh" })}</p>
                  </div>
                  <p className="text-sm"><b className="text-navy-900">{ty(k.gia_ty)}</b> <span className="text-slate-500">(80%: {ty(k.khoang_80_ty[0])} – {ty(k.khoang_80_ty[1])})</span></p>
                </li>
              );
            })}
          </ul>
        )}
      </section>
    </div>
  );
}
