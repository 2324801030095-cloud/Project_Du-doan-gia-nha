import { and, eq } from "drizzle-orm";
import { NextResponse } from "next/server";
import { z } from "zod";
import { db } from "@/lib/db";
import { yeuThich } from "@/lib/db/schema";
import { layPhien } from "@/lib/session";

const Tin = z.object({ loai: z.enum(["nha_pho", "can_ho"]), maTin: z.string().min(1).max(40) });

// Bật / tắt lưu tin. POST = lưu, DELETE = bỏ lưu. Cần đăng nhập.
async function xuLy(req: Request, them: boolean) {
  const phien = await layPhien();
  if (!phien) return NextResponse.json({ loi: "Cần đăng nhập để lưu tin" }, { status: 401 });
  const p = Tin.safeParse(await req.json().catch(() => null));
  if (!p.success) return NextResponse.json({ loi: "Dữ liệu không hợp lệ" }, { status: 400 });
  const { loai, maTin } = p.data;
  if (them) await db.insert(yeuThich).values({ userId: phien.user.id, loai, maTin }).onConflictDoNothing();
  else await db.delete(yeuThich).where(and(eq(yeuThich.userId, phien.user.id), eq(yeuThich.loai, loai), eq(yeuThich.maTin, maTin)));
  return NextResponse.json({ ok: true, da_luu: them });
}

export const POST = (req: Request) => xuLy(req, true);
export const DELETE = (req: Request) => xuLy(req, false);
