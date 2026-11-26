import "server-only";
import { and, eq } from "drizzle-orm";
import { db } from "./db";
import { yeuThich } from "./db/schema";

// Tập mã tin người dùng đã lưu (theo loại) để tô trái tim trên danh sách
export async function maDaLuu(userId: string | undefined, loai: string) {
  if (!userId) return new Set<string>();
  const ds = await db.select({ m: yeuThich.maTin }).from(yeuThich).where(and(eq(yeuThich.userId, userId), eq(yeuThich.loai, loai)));
  return new Set(ds.map((x) => x.m));
}
