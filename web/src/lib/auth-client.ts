"use client";
// Better Auth phía trình duyệt: hàm đăng nhập / đăng ký / đăng xuất và hook phiên (gọi /api/auth/*).
import { adminClient } from "better-auth/client/plugins";
import { createAuthClient } from "better-auth/react";

export const authClient = createAuthClient({ plugins: [adminClient()] });
export const { signIn, signUp, signOut, useSession } = authClient;
