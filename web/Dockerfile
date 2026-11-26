# Ứng dụng web Next.js – build nhiều tầng
FROM node:24-alpine AS deps
WORKDIR /app
RUN corepack enable
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile

FROM deps AS build
COPY . .
# Khóa giả CHỈ cho bước build (Better Auth kiểm tra khi Next thu thập dữ liệu trang); lúc chạy dùng BETTER_AUTH_SECRET thật từ .env
ENV NEXT_TELEMETRY_DISABLED=1 BETTER_AUTH_SECRET=chi-dung-luc-build-khong-dung-luc-chay-0000000000
RUN pnpm exec next typegen && pnpm build

# Tầng khởi tạo CSDL: chạy migration + tạo admin rồi thoát (dịch vụ "migrate" trong docker-compose)
FROM deps AS migrate
COPY drizzle ./drizzle
COPY scripts ./scripts
CMD ["node", "scripts/khoi-tao-db.mjs"]

# Tầng chạy: chỉ bản standalone (server + phụ thuộc đã lọc), không có mã nguồn
FROM node:24-alpine AS run
WORKDIR /app
ENV NODE_ENV=production NEXT_TELEMETRY_DISABLED=1 PORT=3000 HOSTNAME=0.0.0.0
RUN addgroup -S web && adduser -S web -G web
COPY --from=build --chown=web:web /app/.next/standalone ./
COPY --from=build --chown=web:web /app/.next/static ./.next/static
COPY --from=build --chown=web:web /app/public ./public
USER web
EXPOSE 3000
CMD ["node", "server.js"]
