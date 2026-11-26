"use client";
import { Heart } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState, useTransition } from "react";

export function NutYeuThich({ loai, maTin, daLuu, dangNhap }: { loai: string; maTin: string; daLuu: boolean; dangNhap: boolean }) {
  const [luu, setLuu] = useState(daLuu);
  const [dang, startTransition] = useTransition();
  const router = useRouter();
  return (
    <button
      type="button"
      aria-pressed={luu}
      aria-label={luu ? "Bỏ lưu tin" : "Lưu tin"}
      title={dangNhap ? (luu ? "Bỏ lưu" : "Lưu tin") : "Đăng nhập để lưu tin"}
      disabled={dang}
      className={`rounded-full p-2 transition ${luu ? "bg-rose-50 text-rose-600" : "text-slate-400 hover:bg-navy-50 hover:text-rose-500"}`}
      onClick={() => {
        if (!dangNhap) return router.push(`/dang-nhap?tiep=${encodeURIComponent(location.pathname)}`);
        const moi = !luu;
        setLuu(moi); // cập nhật ngay, hoàn tác nếu máy chủ lỗi
        startTransition(async () => {
          const r = await fetch("/api/yeu-thich", { method: moi ? "POST" : "DELETE", headers: { "content-type": "application/json" }, body: JSON.stringify({ loai, maTin }) });
          if (!r.ok) setLuu(!moi);
          router.refresh();
        });
      }}
    >
      <Heart size={18} fill={luu ? "currentColor" : "none"} />
    </button>
  );
}
