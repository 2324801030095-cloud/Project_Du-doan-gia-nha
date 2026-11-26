"use client";
import { Menu, X } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";

export function NavLinks({ muc }: { muc: { href: string; ten: string }[] }) {
  const p = usePathname();
  const [mo, setMo] = useState(false);
  const lop = (href: string) =>
    `rounded-lg px-3 py-2 text-sm font-medium transition ${p.startsWith(href) ? "bg-navy-100 text-navy-900" : "text-slate-600 hover:bg-navy-50 hover:text-navy-900"}`;
  return (
    <>
      <nav className="hidden items-center gap-1 lg:flex" aria-label="Chính">
        {muc.map((m) => <Link key={m.href} href={m.href} className={lop(m.href)}>{m.ten}</Link>)}
      </nav>
      <button className="nut-vien px-2.5 lg:hidden" onClick={() => setMo(!mo)} aria-label="Mở menu" aria-expanded={mo}>
        {mo ? <X size={18} /> : <Menu size={18} />}
      </button>
      {mo && (
        <nav className="absolute inset-x-0 top-16 grid gap-1 border-b border-navy-100 bg-white p-3 shadow-lg lg:hidden" onClick={() => setMo(false)}>
          {muc.map((m) => <Link key={m.href} href={m.href} className={lop(m.href)}>{m.ten}</Link>)}
        </nav>
      )}
    </>
  );
}
