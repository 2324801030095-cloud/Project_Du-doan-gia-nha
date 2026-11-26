import { defineConfig } from "drizzle-kit";

// pnpm db:generate -> sinh file SQL migration vào drizzle/ từ src/lib/db/schema.ts
export default defineConfig({
  schema: "./src/lib/db/schema.ts",
  out: "./drizzle",
  dialect: "postgresql",
  dbCredentials: { url: process.env.DATABASE_URL ?? "postgres://phuhoa:phuhoa@localhost:5432/phuhoa" },
});
