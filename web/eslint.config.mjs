// ESLint cho web: bộ luật Core Web Vitals + TypeScript của Next.js (chạy: pnpm lint; CI chạy mỗi lần đẩy code).
import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

const eslintConfig = defineConfig([
  ...nextVitals,
  ...nextTs,
  // Ghi đè danh sách bỏ qua mặc định của eslint-config-next (giữ nguyên các mục mặc định):
  globalIgnores([
    ".next/**",
    "out/**",
    "build/**",
    "next-env.d.ts",
  ]),
]);

export default eslintConfig;
