import { count, desc, sql } from "drizzle-orm";
import type { Metadata } from "next";
import { BangNguoiDung } from "@/components/bang-nguoi-dung";
import { goiApi, type TongQuan } from "@/lib/api";
import { db } from "@/lib/db";
import { lichSuDinhGia, user, yeuThich } from "@/lib/db/schema";
import { so } from "@/lib/format";
import { canAdmin } from "@/lib/session";

export const metadata: Metadata = { title: "Quản trị" };

export default async function Page() {
  const phien = await canAdmin();
  const [[nd], [dg], [yt], theoLoai, nguoi, tq] = await Promise.all([
    db.select({ n: count() }).from(user),
    db.select({ n: count() }).from(lichSuDinhGia),
    db.select({ n: count() }).from(yeuThich),
    db.select({ loai: lichSuDinhGia.loai, n: count() }).from(lichSuDinhGia).groupBy(lichSuDinhGia.loai),
    db.select({
      id: user.id, name: user.name, email: user.email, role: user.role, banned: user.banned, createdAt: user.createdAt,
      soDinhGia: sql<number>`(select count(*) from lich_su_dinh_gia l where l.user_id = "user"."id")`.mapWith(Number),
    }).from(user).orderBy(desc(user.createdAt)).limit(100),
    goiApi<TongQuan>("/tong-quan"),
  ]);
  const the = [
    ["Người dùng", so(nd.n, 0)], ["Lượt định giá đã lưu", so(dg.n, 0)], ["Tin được lưu", so(yt.n, 0)],
    ["Dữ liệu đến", tq.so_lieu.NGAY], ["Mô hình nhà phố", tq.so_lieu.BEST], ["MAPE test Phú Hòa", `${tq.so_lieu.TEST_MAPE}%`],
  ];
  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold">Quản trị</h1>
      <div className="grid gap-4 sm:grid-cols-3 lg:grid-cols-6">
        {the.map(([k, v]) => <div key={k} className="the p-4"><p className="nhan">{k}</p><p className="text-lg font-bold text-navy-900">{v}</p></div>)}
      </div>
      <p className="text-sm text-slate-600">Định giá theo loại: {theoLoai.map((x) => `${x.loai} ${x.n}`).join(" · ") || "chưa có"}.</p>
      <section className="the p-6">
        <h2 className="mb-4 text-xl font-semibold">Người dùng</h2>
        <BangNguoiDung nguoi={nguoi.map((x) => ({ ...x, createdAt: x.createdAt.toISOString() }))} toiLa={phien.user.id} />
      </section>
    </div>
  );
}
