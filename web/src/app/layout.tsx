import type { Metadata } from "next";
import { Be_Vietnam_Pro } from "next/font/google";
import Link from "next/link";
import { Header } from "@/components/header";
import "./globals.css";

const font = Be_Vietnam_Pro({ variable: "--font-be-vietnam", subsets: ["latin", "vietnamese"], weight: ["400", "500", "600", "700"] });

export const metadata: Metadata = {
  title: { default: "Giá nhà Phú Hòa – định giá bằng học máy", template: "%s · Giá nhà Phú Hòa" },
  description: "Định giá nhà phố, căn hộ, đất ở Thủ Dầu Một bằng mô hình học máy học trên tin rao thật.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="vi" className={`${font.variable} h-full`}>
      <body className="flex min-h-full flex-col">
        <Header />
        <main className="mx-auto w-full max-w-7xl flex-1 px-4 py-8 sm:px-6">{children}</main>
        <footer className="border-t border-navy-100 bg-white">
          <div className="mx-auto flex max-w-7xl flex-col gap-2 px-4 py-6 text-sm text-slate-500 sm:flex-row sm:justify-between sm:px-6">
            <p>Đề tài môn Học máy · MSSV 2324801030095. Giá là <b>giá rao ước lượng</b>, không phải giá giao dịch.</p>
            <p className="flex gap-4">
              <Link href="/mo-hinh" className="hover:text-navy-800">Mô hình</Link>
              <Link href="/tro-ly" className="hover:text-navy-800">Trợ lý</Link>
              <Link href="/nguon-anh" className="hover:text-navy-800">Nguồn ảnh</Link>
            </p>
          </div>
        </footer>
      </body>
    </html>
  );
}
