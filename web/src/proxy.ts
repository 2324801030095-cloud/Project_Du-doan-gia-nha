import { getSessionCookie } from "better-auth/cookies";
import { NextResponse, type NextRequest } from "next/server";

// Kiểm tra lạc quan: chưa có cookie phiên thì chuyển ngay tới trang đăng nhập.
// Kiểm tra thật (phiên còn hạn, quyền admin) vẫn làm ở máy chủ trong từng trang (lib/session.ts).
export function proxy(req: NextRequest) {
  if (!getSessionCookie(req)) {
    const url = new URL("/dang-nhap", req.url);
    url.searchParams.set("tiep", req.nextUrl.pathname);
    return NextResponse.redirect(url);
  }
  return NextResponse.next();
}

export const config = { matcher: ["/tai-khoan/:path*", "/admin/:path*"] };
