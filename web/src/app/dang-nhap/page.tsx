import type { Metadata } from "next";
import { redirect } from "next/navigation";
import { Suspense } from "react";
import { FormXacThuc } from "@/components/form-xac-thuc";
import { layPhien } from "@/lib/session";

export const metadata: Metadata = { title: "Đăng nhập" };

export default async function Page() {
  if (await layPhien()) redirect("/tai-khoan");
  return <Suspense><FormXacThuc kieu="dang-nhap" /></Suspense>;
}
