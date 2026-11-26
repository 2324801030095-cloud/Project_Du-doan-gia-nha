import { toNextJsHandler } from "better-auth/next-js";
import { auth } from "@/lib/auth";

// Toàn bộ endpoint đăng ký / đăng nhập / đăng xuất / quản trị người dùng của Better Auth: /api/auth/*
export const { GET, POST } = toNextJsHandler(auth);
