import "server-only";
import { drizzle } from "drizzle-orm/node-postgres";
import { Pool } from "pg";
import { schema } from "./schema";

// Một pool cho cả tiến trình (giữ qua hot reload khi chạy dev)
const g = globalThis as unknown as { pool?: Pool };
const pool = (g.pool ??= new Pool({ connectionString: process.env.DATABASE_URL, max: 10 }));

export const db = drizzle(pool, { schema });
