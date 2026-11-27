import "server-only";
import { headers } from "next/headers";
import { redirect } from "next/navigation";
import { auth } from "./auth";

// Lớp truy cập dữ liệu (DAL): mọi kiểm tra đăng nhập / quyền đi qua đây, ở phía máy chủ.
export async function layPhien() {
  return auth.api.getSession({ headers: await headers() });
}

/** Bắt buộc đăng nhập: chưa có phiên -> chuyển tới /dang-nhap?tiep=<trang hiện tại>. */
export async function canDangNhap(tiepTheo = "/tai-khoan") {
  const s = await layPhien();
  if (!s) redirect(`/dang-nhap?tiep=${encodeURIComponent(tiepTheo)}`);
  return s;
}

/** Bắt buộc quyền admin: chưa đăng nhập -> trang đăng nhập; không phải admin -> trang chủ. */
export async function canAdmin() {
  const s = await canDangNhap("/admin");
  if (s.user.role !== "admin") redirect("/");
  return s;
}
