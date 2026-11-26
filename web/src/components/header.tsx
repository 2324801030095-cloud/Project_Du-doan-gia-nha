import { House } from "lucide-react";
import Link from "next/link";
import { layPhien } from "@/lib/session";
import { MenuNguoiDung } from "./menu-nguoi-dung";
import { NavLinks } from "./nav-links";

export const MUC_MENU = [
  { href: "/dinh-gia", ten: "Định giá" },
  { href: "/nha-pho", ten: "Nhà phố" },
  { href: "/can-ho", ten: "Căn hộ" },
  { href: "/dat", ten: "Đất nền" },
  { href: "/ban-do", ten: "Bản đồ" },
  { href: "/xu-huong", ten: "Xu hướng" },
  { href: "/mo-hinh", ten: "Mô hình" },
  { href: "/tro-ly", ten: "Trợ lý" },
];

export async function Header() {
  const phien = await layPhien();
  const nguoi = phien ? { ten: phien.user.name, email: phien.user.email, admin: phien.user.role === "admin" } : null;
  return (
    <header className="sticky top-0 z-[1000] border-b border-navy-100 bg-white/90 backdrop-blur">
      <div className="mx-auto flex h-16 max-w-7xl items-center gap-6 px-4 sm:px-6">
        <Link href="/" className="flex shrink-0 items-center gap-2 font-bold text-navy-900">
          <span className="grid size-9 place-items-center rounded-xl bg-navy-800 text-gold-400"><House size={18} /></span>
          <span className="hidden sm:inline">Giá nhà Phú Hòa</span>
        </Link>
        <NavLinks muc={MUC_MENU} />
        <div className="ml-auto flex items-center gap-2">
          {nguoi ? (
            <MenuNguoiDung nguoi={nguoi} />
          ) : (
            <>
              <Link href="/dang-nhap" className="nut-vien hidden sm:inline-flex">Đăng nhập</Link>
              <Link href="/dang-ky" className="nut-chinh">Đăng ký</Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
