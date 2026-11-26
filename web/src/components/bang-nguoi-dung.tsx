"use client";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { authClient } from "@/lib/auth-client";

type Nguoi = { id: string; name: string; email: string; role: string | null; banned: boolean | null; createdAt: string; soDinhGia: number };

// Đổi vai trò / khóa tài khoản qua API admin của Better Auth (máy chủ tự kiểm tra quyền admin)
export function BangNguoiDung({ nguoi, toiLa }: { nguoi: Nguoi[]; toiLa: string }) {
  const router = useRouter();
  const [loi, setLoi] = useState("");
  async function lam(f: () => Promise<{ error: { message?: string } | null }>) {
    setLoi("");
    const { error } = await f();
    if (error) setLoi(error.message ?? "Không thực hiện được");
    router.refresh();
  }
  return (
    <div className="overflow-x-auto">
      {loi && <p className="mb-3 rounded-lg bg-rose-50 p-3 text-sm text-rose-700">{loi}</p>}
      <table className="w-full min-w-[720px] text-sm">
        <thead className="text-left text-xs uppercase text-slate-500">
          <tr><th className="py-2">Họ tên</th><th>Email</th><th>Vai trò</th><th>Định giá</th><th>Tạo lúc</th><th className="text-right">Thao tác</th></tr>
        </thead>
        <tbody className="divide-y divide-navy-50">
          {nguoi.map((n) => (
            <tr key={n.id} className={n.banned ? "opacity-50" : ""}>
              <td className="py-3 font-medium">{n.name}</td>
              <td>{n.email}</td>
              <td><span className={`rounded-full px-2 py-0.5 text-xs font-semibold ${n.role === "admin" ? "bg-gold-400/30 text-gold-600" : "bg-navy-50 text-slate-600"}`}>{n.role ?? "user"}</span>{n.banned && " · đã khóa"}</td>
              <td>{n.soDinhGia}</td>
              <td>{new Date(n.createdAt).toLocaleDateString("vi-VN")}</td>
              <td className="space-x-2 py-2 text-right">
                {n.id !== toiLa && (
                  <>
                    <button className="nut-vien px-3 py-1.5 text-xs" onClick={() => lam(() => authClient.admin.setRole({ userId: n.id, role: n.role === "admin" ? "user" : "admin" }))}>
                      {n.role === "admin" ? "Bỏ admin" : "Cấp admin"}
                    </button>
                    <button className="nut-vien px-3 py-1.5 text-xs text-rose-700" onClick={() => lam(() => (n.banned ? authClient.admin.unbanUser({ userId: n.id }) : authClient.admin.banUser({ userId: n.id, banReason: "Khóa bởi quản trị viên" })))}>
                      {n.banned ? "Mở khóa" : "Khóa"}
                    </button>
                  </>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
