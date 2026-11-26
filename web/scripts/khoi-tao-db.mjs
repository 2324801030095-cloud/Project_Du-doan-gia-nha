// Chạy mỗi lần container web khởi động (trước server):
// 1. Áp các migration SQL trong drizzle/ (đã áp thì bỏ qua) -> tạo / cập nhật bảng.
// 2. Nếu đặt ADMIN_EMAIL + ADMIN_PASSWORD mà chưa có tài khoản đó: tạo tài khoản admin (mật khẩu băm như Better Auth).
import { randomUUID } from "node:crypto";
import { fileURLToPath } from "node:url";
import { hashPassword } from "better-auth/crypto";
import { drizzle } from "drizzle-orm/node-postgres";
import { migrate } from "drizzle-orm/node-postgres/migrator";
import pg from "pg";

const pool = new pg.Pool({ connectionString: process.env.DATABASE_URL });
for (let lan = 1; ; lan++) {
  // CSDL có thể chưa sẵn sàng ngay khi container khởi động
  try {
    await pool.query("select 1");
    break;
  } catch (e) {
    if (lan >= 30) throw e;
    console.log(`Chờ PostgreSQL (${lan})…`);
    await new Promise((r) => setTimeout(r, 2000));
  }
}
await migrate(drizzle(pool), { migrationsFolder: fileURLToPath(new URL("../drizzle", import.meta.url)) });
console.log("Đã áp migration.");

const email = process.env.ADMIN_EMAIL?.trim().toLowerCase(), matKhau = process.env.ADMIN_PASSWORD;
if (email && matKhau) {
  if (matKhau.length < 8) throw new Error("ADMIN_PASSWORD cần ít nhất 8 ký tự");
  const { rows } = await pool.query('select id, role from "user" where email = $1', [email]);
  if (rows.length === 0) {
    const id = randomUUID();
    await pool.query('insert into "user" (id, name, email, email_verified, role) values ($1, $2, $3, true, $4)', [id, "Quản trị viên", email, "admin"]);
    await pool.query("insert into account (id, account_id, provider_id, user_id, password) values ($1, $2, 'credential', $2, $3)", [randomUUID(), id, await hashPassword(matKhau)]);
    console.log(`Đã tạo tài khoản admin ${email}.`);
  } else if (rows[0].role !== "admin") {
    await pool.query('update "user" set role = $1 where email = $2', ["admin", email]);
    console.log(`Đã cấp quyền admin cho ${email}.`);
  }
}
await pool.end();
