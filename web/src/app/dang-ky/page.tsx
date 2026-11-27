// Trang đăng ký tài khoản (email + mật khẩu >= 8 ký tự); đã đăng nhập thì chuyển sang trang tài khoản.
import type { Metadata } from "next";
import { redirect } from "next/navigation";
import { Suspense } from "react";
import { FormXacThuc } from "@/components/form-xac-thuc";
import { layPhien } from "@/lib/session";

export const metadata: Metadata = { title: "Đăng ký" };

export default async function Page() {
  if (await layPhien()) redirect("/tai-khoan");
  return <Suspense><FormXacThuc kieu="dang-ky" /></Suspense>;
}
