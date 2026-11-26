"use client";
import { LoaderCircle } from "lucide-react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";
import { signIn, signUp } from "@/lib/auth-client";

// Chỉ cho chuyển hướng tới đường dẫn nội bộ (chống open redirect qua ?tiep=)
const anToan = (u: string | null) => (u && u.startsWith("/") && !u.startsWith("//") ? u : "/tai-khoan");

export function FormXacThuc({ kieu }: { kieu: "dang-nhap" | "dang-ky" }) {
  const router = useRouter();
  const tiep = anToan(useSearchParams().get("tiep"));
  const [loi, setLoi] = useState("");
  const [dang, setDang] = useState(false);

  async function gui(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const f = new FormData(e.currentTarget);
    const email = String(f.get("email")).trim(), password = String(f.get("password"));
    setDang(true); setLoi("");
    const { error } = kieu === "dang-ky"
      ? await signUp.email({ email, password, name: String(f.get("name")).trim() })
      : await signIn.email({ email, password });
    setDang(false);
    if (error) {
      const m: Record<string, string> = {
        INVALID_EMAIL_OR_PASSWORD: "Email hoặc mật khẩu không đúng.",
        USER_ALREADY_EXISTS: "Email này đã có tài khoản.",
        PASSWORD_TOO_SHORT: "Mật khẩu cần ít nhất 8 ký tự.",
        BANNED_USER: "Tài khoản đã bị khóa.",
      };
      setLoi(m[error.code ?? ""] ?? error.message ?? "Không thực hiện được, thử lại.");
      return;
    }
    router.push(tiep);
    router.refresh();
  }

  return (
    <div className="mx-auto max-w-md">
      <div className="the p-8">
        <h1 className="text-2xl font-bold">{kieu === "dang-nhap" ? "Đăng nhập" : "Tạo tài khoản"}</h1>
        <p className="mt-1 text-sm text-slate-500">
          {kieu === "dang-nhap" ? "Để lưu tin yêu thích và lịch sử định giá." : "Miễn phí. Mật khẩu được băm, không lưu dạng gốc."}
        </p>
        <form onSubmit={gui} className="mt-6 space-y-4">
          {kieu === "dang-ky" && (
            <label className="block"><span className="nhan">Họ tên</span><input name="name" required maxLength={80} autoComplete="name" className="o-nhap" /></label>
          )}
          <label className="block"><span className="nhan">Email</span><input name="email" type="email" required autoComplete="email" className="o-nhap" /></label>
          <label className="block">
            <span className="nhan">Mật khẩu</span>
            <input name="password" type="password" required minLength={8} maxLength={128} autoComplete={kieu === "dang-ky" ? "new-password" : "current-password"} className="o-nhap" />
          </label>
          {loi && <p className="rounded-lg bg-rose-50 p-3 text-sm text-rose-700" role="alert">{loi}</p>}
          <button className="nut-chinh w-full py-3" disabled={dang}>
            {dang && <LoaderCircle size={18} className="animate-spin" />} {kieu === "dang-nhap" ? "Đăng nhập" : "Đăng ký"}
          </button>
        </form>
        <p className="mt-6 text-center text-sm text-slate-500">
          {kieu === "dang-nhap" ? (
            <>Chưa có tài khoản? <Link href={`/dang-ky?tiep=${encodeURIComponent(tiep)}`} className="font-semibold text-navy-700">Đăng ký</Link></>
          ) : (
            <>Đã có tài khoản? <Link href={`/dang-nhap?tiep=${encodeURIComponent(tiep)}`} className="font-semibold text-navy-700">Đăng nhập</Link></>
          )}
        </p>
      </div>
    </div>
  );
}
