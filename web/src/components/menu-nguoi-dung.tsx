"use client";
import { ChevronDown, LogOut, Shield, User } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { signOut } from "@/lib/auth-client";

export function MenuNguoiDung({ nguoi }: { nguoi: { ten: string; email: string; admin: boolean } }) {
  const [mo, setMo] = useState(false);
  const router = useRouter();
  return (
    <div className="relative">
      <button className="nut-vien" onClick={() => setMo(!mo)} aria-expanded={mo}>
        <span className="grid size-6 place-items-center rounded-full bg-navy-800 text-xs text-white">{nguoi.ten.slice(0, 1).toUpperCase()}</span>
        <span className="hidden max-w-32 truncate sm:inline">{nguoi.ten}</span>
        <ChevronDown size={14} />
      </button>
      {mo && (
        <div className="the absolute right-0 mt-2 w-60 p-2 shadow-lg" onMouseLeave={() => setMo(false)}>
          <p className="truncate px-3 py-2 text-xs text-slate-500">{nguoi.email}</p>
          <Link href="/tai-khoan" className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm hover:bg-navy-50" onClick={() => setMo(false)}>
            <User size={16} /> Tài khoản của tôi
          </Link>
          {nguoi.admin && (
            <Link href="/admin" className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm hover:bg-navy-50" onClick={() => setMo(false)}>
              <Shield size={16} /> Quản trị
            </Link>
          )}
          <button
            className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-sm text-rose-700 hover:bg-rose-50"
            onClick={async () => {
              await signOut();
              router.push("/");
              router.refresh();
            }}
          >
            <LogOut size={16} /> Đăng xuất
          </button>
        </div>
      )}
    </div>
  );
}
