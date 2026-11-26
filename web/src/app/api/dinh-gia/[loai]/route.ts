import { NextResponse } from "next/server";
import { goiApi, LoiApi } from "@/lib/api";
import { db } from "@/lib/db";
import { lichSuDinhGia } from "@/lib/db/schema";
import { layPhien } from "@/lib/session";

const LOAI = new Set(["nha-pho", "can-ho", "dat"]);

// Chuyển yêu cầu định giá tới API mô hình; nếu đã đăng nhập thì lưu vào lịch sử định giá của người dùng.
export async function POST(req: Request, ctx: RouteContext<"/api/dinh-gia/[loai]">) {
  const { loai } = await ctx.params;
  if (!LOAI.has(loai)) return NextResponse.json({ loi: "Loại không hợp lệ" }, { status: 404 });
  let dauVao: Record<string, unknown>;
  try {
    dauVao = await req.json();
  } catch {
    return NextResponse.json({ loi: "Dữ liệu gửi lên không phải JSON" }, { status: 400 });
  }
  try {
    const kq = await goiApi<{ gia_ty: number }>(`/dinh-gia/${loai}`, { method: "POST", body: JSON.stringify(dauVao) });
    const phien = await layPhien();
    if (phien) {
      await db.insert(lichSuDinhGia).values({ userId: phien.user.id, loai, dauVao, ketQua: kq, giaTy: String(kq.gia_ty) });
    }
    return NextResponse.json({ ...kq, da_luu: Boolean(phien) });
  } catch (e) {
    const status = e instanceof LoiApi ? (e.status === 422 ? 400 : 502) : 502;
    return NextResponse.json({ loi: e instanceof Error ? e.message : "Lỗi định giá" }, { status });
  }
}
