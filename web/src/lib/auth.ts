import "server-only";
import { betterAuth } from "better-auth";
import { drizzleAdapter } from "better-auth/adapters/drizzle";
import { nextCookies } from "better-auth/next-js";
import { admin } from "better-auth/plugins";
import { db } from "./db";
import { schema } from "./db/schema";

// Đăng nhập email + mật khẩu; phiên lưu trong bảng session (cookie httpOnly), mật khẩu băm scrypt.
// Plugin admin: cột role (user/admin), khóa tài khoản, quản lý người dùng.
export const auth = betterAuth({
  appName: "Giá nhà Phú Hòa",
  baseURL: process.env.BETTER_AUTH_URL,
  secret: process.env.BETTER_AUTH_SECRET,
  database: drizzleAdapter(db, { provider: "pg", schema }),
  emailAndPassword: { enabled: true, minPasswordLength: 8, autoSignIn: true },
  session: { expiresIn: 60 * 60 * 24 * 7, updateAge: 60 * 60 * 24 },
  rateLimit: { enabled: true, window: 60, max: 30 },
  plugins: [admin(), nextCookies()],
});

export type Session = typeof auth.$Infer.Session;
