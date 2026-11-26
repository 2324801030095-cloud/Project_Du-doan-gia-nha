// Kiểm thử đầu-cuối ứng dụng web ĐANG CHẠY (docker compose up): trang, đăng ký / đăng nhập thật, phiên, phân quyền,
// định giá lưu lịch sử, yêu thích, trợ lý. Dùng: node tests/kiem_tra_web.mjs [http://localhost:3000]
// Tài khoản admin đọc từ .env (ADMIN_EMAIL, ADMIN_PASSWORD). Mỗi lần chạy tạo một người dùng thử mới.
import { readFileSync } from "node:fs";

const GOC = process.argv[2] ?? "http://localhost:3000";
const env = Object.fromEntries(readFileSync(new URL("../.env", import.meta.url), "utf8").split(/\r?\n/).filter((l) => l.includes("=")).map((l) => [l.slice(0, l.indexOf("=")), l.slice(l.indexOf("=") + 1)]));
const KQ = [];
async function kiem(ten, f) {
  try { await f(); KQ.push([ten, true, ""]); } catch (e) { KQ.push([ten, false, e.message]); }
}
const ok = (dk, msg) => { if (!dk) throw new Error(msg); };

// Phiên = cookie trả về từ Better Auth
async function goi(duong, { cookie, method = "GET", body, theoChuyen = false } = {}) {
  return fetch(GOC + duong, {
    method, redirect: theoChuyen ? "follow" : "manual",
    headers: { origin: GOC, ...(body ? { "content-type": "application/json" } : {}), ...(cookie ? { cookie } : {}) },
    body: body ? JSON.stringify(body) : undefined,
  });
}
// HTML của React chèn <!-- --> giữa các đoạn chữ liền nhau: bỏ đi trước khi tìm chữ
const chu = async (r) => (await r.text()).replace(/<!-- -->/g, "");
const layCookie = (r) => r.headers.getSetCookie().map((c) => c.split(";")[0]).join("; ");

const email = `thu.${Date.now()}@phuhoa.local`, matKhau = "MatKhau-thu-123";
let ckUser = "", ckAdmin = "", maTin = "";

await kiem("Mọi trang công khai trả 200 và có nội dung tiếng Việt", async () => {
  for (const p of ["/", "/nha-pho", "/can-ho", "/ban-do", "/xu-huong", "/mo-hinh", "/tro-ly", "/dinh-gia", "/dinh-gia?loai=can-ho", "/dang-nhap", "/dang-ky"]) {
    const r = await goi(p);
    ok(r.status === 200, `${p}: ${r.status}`);
    ok((await r.text()).includes("Phú Hòa"), `${p}: thiếu nội dung`);
  }
  const html = await (await goi("/nha-pho")).text();
  maTin = html.match(/href="\/nha-pho\/(\d+)"/)?.[1];
  ok(maTin, "không thấy tin nào");
  ok((await goi(`/nha-pho/${maTin}`)).status === 200, "trang chi tiết lỗi");
  ok((await goi("/nha-pho/khong-ton-tai")).status === 404, "tin không tồn tại phải 404");
  ok((await goi("/dat")).status === 404, "trang đất nền đã bỏ khỏi đề tài nhưng vẫn mở được");
});

await kiem("Chưa đăng nhập: /tai-khoan và /admin chuyển tới đăng nhập; API lưu tin trả 401", async () => {
  for (const p of ["/tai-khoan", "/admin"]) {
    const r = await goi(p);
    ok([307, 308].includes(r.status) && r.headers.get("location").includes("/dang-nhap"), `${p}: ${r.status}`);
  }
  ok((await goi("/api/yeu-thich", { method: "POST", body: { loai: "nha_pho", maTin: "1" } })).status === 401, "lưu tin không cần đăng nhập?");
});

await kiem("Đăng ký tài khoản mới: tạo phiên (cookie httpOnly), email trùng bị từ chối, mật khẩu ngắn bị từ chối", async () => {
  const r = await goi("/api/auth/sign-up/email", { method: "POST", body: { email, password: matKhau, name: "Người dùng thử" } });
  ok(r.status === 200, `đăng ký: ${r.status} ${await r.text()}`);
  ok(r.headers.getSetCookie().some((c) => /httponly/i.test(c)), "cookie phiên không httpOnly");
  ckUser = layCookie(r);
  ok((await goi("/api/auth/sign-up/email", { method: "POST", body: { email, password: matKhau, name: "x" } })).status >= 400, "email trùng vẫn đăng ký được");
  ok((await goi("/api/auth/sign-up/email", { method: "POST", body: { email: "b" + email, password: "123", name: "x" } })).status >= 400, "mật khẩu ngắn vẫn đăng ký được");
});

await kiem("Đăng nhập: sai mật khẩu bị từ chối; đúng thì có phiên và vào được /tai-khoan", async () => {
  ok((await goi("/api/auth/sign-in/email", { method: "POST", body: { email, password: "sai-mat-khau-1" } })).status === 401, "sai mật khẩu vẫn vào");
  const r = await goi("/api/auth/sign-in/email", { method: "POST", body: { email, password: matKhau } });
  ok(r.status === 200, `đăng nhập: ${r.status}`);
  ckUser = layCookie(r);
  const t = await goi("/tai-khoan", { cookie: ckUser });
  ok(t.status === 200 && (await t.text()).includes("Người dùng thử"), `/tai-khoan: ${t.status}`);
});

await kiem("Định giá qua web: có phiên thì lưu lịch sử, không phiên thì không lưu; dữ liệu sai trả 400", async () => {
  const body = { dt_dat: 80, so_tang: 2, cap_loi_vao: 3, hem_rong: 6 };
  const a = await (await goi("/api/dinh-gia/nha-pho", { method: "POST", body, cookie: ckUser })).json();
  ok(a.gia_ty > 0 && a.da_luu === true, JSON.stringify(a).slice(0, 200));
  const b = await (await goi("/api/dinh-gia/nha-pho", { method: "POST", body })).json();
  ok(b.da_luu === false && Math.abs(b.gia_ty - a.gia_ty) < 1e-9, "khách: lưu nhầm hoặc giá khác");
  ok((await goi("/api/dinh-gia/nha-pho", { method: "POST", body: { dt_dat: 2 } })).status === 400, "dữ liệu sai không trả 400");
  ok((await goi("/api/dinh-gia/khong-co", { method: "POST", body })).status === 404, "loại lạ không trả 404");
  ok((await chu(await goi("/tai-khoan", { cookie: ckUser }))).includes("80 m²"), "lịch sử không hiện trên trang tài khoản");
});

await kiem("Lưu tin yêu thích rồi bỏ lưu; trang tài khoản hiện bảng so sánh", async () => {
  ok((await goi("/api/yeu-thich", { method: "POST", body: { loai: "nha_pho", maTin }, cookie: ckUser })).ok, "lưu lỗi");
  ok((await goi("/api/yeu-thich", { method: "POST", body: { loai: "nha_pho", maTin }, cookie: ckUser })).ok, "lưu lần 2 phải không lỗi");
  ok((await (await goi("/tai-khoan", { cookie: ckUser })).text()).includes(`/nha-pho/${maTin}`), "tin đã lưu không hiện");
  ok((await goi("/api/yeu-thich", { method: "DELETE", body: { loai: "nha_pho", maTin }, cookie: ckUser })).ok, "bỏ lưu lỗi");
  ok((await goi("/api/yeu-thich", { method: "POST", body: { loai: "xau", maTin }, cookie: ckUser })).status === 400, "loại sai không trả 400");
});

await kiem("Phân quyền: người dùng thường không vào /admin và không gọi được API quản trị", async () => {
  const r = await goi("/admin", { cookie: ckUser });
  ok([307, 308].includes(r.status) && !r.headers.get("location").includes("/admin"), `/admin cho user: ${r.status}`);
  const a = await goi("/api/auth/admin/list-users", { cookie: ckUser });
  ok(a.status === 401 || a.status === 403, `API admin cho user: ${a.status}`);
});

await kiem("Tài khoản admin (tạo tự động từ .env): vào /admin, thấy người dùng vừa đăng ký, gọi được API quản trị", async () => {
  const r = await goi("/api/auth/sign-in/email", { method: "POST", body: { email: env.ADMIN_EMAIL, password: env.ADMIN_PASSWORD } });
  ok(r.status === 200, `admin đăng nhập: ${r.status}`);
  ckAdmin = layCookie(r);
  const t = await goi("/admin", { cookie: ckAdmin });
  ok(t.status === 200 && (await t.text()).includes(email), `/admin: ${t.status}`);
  ok((await goi("/api/auth/admin/list-users", { cookie: ckAdmin })).status === 200, "admin không gọi được API quản trị");
});

await kiem("Đăng xuất: phiên bị hủy, /tai-khoan lại yêu cầu đăng nhập", async () => {
  ok((await goi("/api/auth/sign-out", { method: "POST", body: {}, cookie: ckUser })).ok, "đăng xuất lỗi");
  const r = await goi("/tai-khoan", { cookie: ckUser });
  ok([307, 308].includes(r.status), `sau đăng xuất /tai-khoan: ${r.status}`);
});

await kiem("Trợ lý trả lời (AI nếu có khóa, nếu không thì mô hình ý định); tin nhắn sai dạng trả 400", async () => {
  const j = await (await goi("/api/chat", { method: "POST", body: { messages: [{ role: "user", content: "xin chào" }] } })).json();
  ok(typeof j.tra_loi === "string" && j.tra_loi.length > 0, JSON.stringify(j).slice(0, 200));
  ok((await goi("/api/chat", { method: "POST", body: { messages: [] } })).status === 400, "tin nhắn rỗng không trả 400");
});

for (const [ten, d, loi] of KQ) console.log((d ? "ĐẠT       " : "KHÔNG ĐẠT ") + ten + (d ? "" : `\n           -> ${loi}`));
console.log(`\n${KQ.filter((x) => x[1]).length}/${KQ.length} phép kiểm đạt`);
process.exit(KQ.every((x) => x[1]) ? 0 : 1);
