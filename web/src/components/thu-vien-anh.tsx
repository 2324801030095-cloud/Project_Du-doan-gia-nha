"use client";
import Image from "next/image";
import Link from "next/link";
import { useState } from "react";

// Ảnh minh họa của tin: ảnh lớn + 3 ảnh nhỏ để chọn
export function ThuVienAnh({ anh, tieuDe }: { anh: string[]; tieuDe: string }) {
  const [chon, setChon] = useState(0);
  return (
    <div className="space-y-2">
      <div className="relative aspect-[16/9] overflow-hidden rounded-2xl bg-navy-50">
        <Image src={anh[chon]} alt={`Ảnh minh họa – ${tieuDe}`} fill priority sizes="(min-width: 1024px) 66vw, 100vw" className="object-cover" />
        <Link href="/nguon-anh" className="absolute bottom-3 left-3 rounded-md bg-black/55 px-2.5 py-1 text-xs text-white hover:bg-black/70">
          Ảnh minh họa, không phải ảnh của căn này · nguồn ảnh
        </Link>
      </div>
      <div className="grid grid-cols-3 gap-2">
        {anh.map((a, i) => (
          <button key={a} onClick={() => setChon(i)} aria-label={`Xem ảnh ${i + 1}`} aria-pressed={chon === i}
            className={`relative aspect-[16/10] overflow-hidden rounded-xl ring-2 transition ${chon === i ? "ring-gold-500" : "ring-transparent opacity-70 hover:opacity-100"}`}>
            <Image src={a} alt="" fill sizes="20vw" className="object-cover" />
          </button>
        ))}
      </div>
    </div>
  );
}
