// Lược đồ CSDL (PostgreSQL, Drizzle ORM).
// 4 bảng đầu là bảng chuẩn của Better Auth (+ cột của plugin admin); 2 bảng cuối là dữ liệu của ứng dụng.
import { boolean, index, integer, jsonb, pgTable, text, timestamp, uniqueIndex } from "drizzle-orm/pg-core";

export const user = pgTable("user", {
  id: text("id").primaryKey(),
  name: text("name").notNull(),
  email: text("email").notNull().unique(),
  emailVerified: boolean("email_verified").notNull().default(false),
  image: text("image"),
  createdAt: timestamp("created_at").notNull().defaultNow(),
  updatedAt: timestamp("updated_at").notNull().defaultNow(),
  role: text("role").default("user"),
  banned: boolean("banned").default(false),
  banReason: text("ban_reason"),
  banExpires: timestamp("ban_expires"),
});

export const session = pgTable("session", {
  id: text("id").primaryKey(),
  expiresAt: timestamp("expires_at").notNull(),
  token: text("token").notNull().unique(),
  createdAt: timestamp("created_at").notNull().defaultNow(),
  updatedAt: timestamp("updated_at").notNull().defaultNow(),
  ipAddress: text("ip_address"),
  userAgent: text("user_agent"),
  userId: text("user_id").notNull().references(() => user.id, { onDelete: "cascade" }),
  impersonatedBy: text("impersonated_by"),
});

export const account = pgTable("account", {
  id: text("id").primaryKey(),
  accountId: text("account_id").notNull(),
  providerId: text("provider_id").notNull(),
  userId: text("user_id").notNull().references(() => user.id, { onDelete: "cascade" }),
  accessToken: text("access_token"),
  refreshToken: text("refresh_token"),
  idToken: text("id_token"),
  accessTokenExpiresAt: timestamp("access_token_expires_at"),
  refreshTokenExpiresAt: timestamp("refresh_token_expires_at"),
  scope: text("scope"),
  password: text("password"), // băm bởi Better Auth (scrypt), không bao giờ lưu mật khẩu gốc
  createdAt: timestamp("created_at").notNull().defaultNow(),
  updatedAt: timestamp("updated_at").notNull().defaultNow(),
});

export const verification = pgTable("verification", {
  id: text("id").primaryKey(),
  identifier: text("identifier").notNull(),
  value: text("value").notNull(),
  expiresAt: timestamp("expires_at").notNull(),
  createdAt: timestamp("created_at").notNull().defaultNow(),
  updatedAt: timestamp("updated_at").notNull().defaultNow(),
});

// Tin người dùng lưu lại (loai: nha_pho | can_ho | dat)
export const yeuThich = pgTable(
  "yeu_thich",
  {
    id: integer("id").primaryKey().generatedAlwaysAsIdentity(),
    userId: text("user_id").notNull().references(() => user.id, { onDelete: "cascade" }),
    loai: text("loai").notNull(),
    maTin: text("ma_tin").notNull(),
    ghiChu: text("ghi_chu"),
    createdAt: timestamp("created_at").notNull().defaultNow(),
  },
  (t) => [uniqueIndex("yeu_thich_duy_nhat").on(t.userId, t.loai, t.maTin)],
);

// Lịch sử định giá của người dùng: thông số nhập và kết quả mô hình trả về
export const lichSuDinhGia = pgTable(
  "lich_su_dinh_gia",
  {
    id: integer("id").primaryKey().generatedAlwaysAsIdentity(),
    userId: text("user_id").notNull().references(() => user.id, { onDelete: "cascade" }),
    loai: text("loai").notNull(),
    dauVao: jsonb("dau_vao").notNull(),
    ketQua: jsonb("ket_qua").notNull(),
    giaTy: text("gia_ty"),
    createdAt: timestamp("created_at").notNull().defaultNow(),
  },
  (t) => [index("lich_su_theo_nguoi").on(t.userId, t.createdAt)],
);

export const schema = { user, session, account, verification, yeuThich, lichSuDinhGia };
