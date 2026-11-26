import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Trang nào cũng đọc phiên đăng nhập hoặc dữ liệu từ API mô hình tại thời điểm yêu cầu,
  // nên dùng mô hình kết xuất động quen thuộc (không bật Cache Components).
  cacheComponents: false,
  output: "standalone", // gói gọn để chạy trong Docker
  turbopack: {
    rules: {
      "*.css": { loaders: ["@tailwindcss/turbopack"], as: "*.css" },
    },
  },
};

export default nextConfig;
