// Xuất ý định do LUẬT TỪ KHÓA của trợ lý (botYDinhLuat) nhận ra cho từng câu trong một file CSV (cột y_dinh, cau_hoi).
// Notebook tro_ly_y_dinh.ipynb gọi script này để so sánh luật với mô hình học máy trên cùng bộ câu hỏi.
// Dùng: node tests/y_dinh_luat.js data/tro_ly/cau_hoi_kiem_tra.csv   -> mỗi dòng một ý định ("null" = không nhận ra)
const fs = require("fs");
const T = require("./nap_trang_demo.js");
const dong = fs.readFileSync(process.argv[2], "utf8").split(/\r?\n/).slice(1).filter(Boolean);
for (const l of dong) {
  const m = l.match(/^[^,]+,"(.*)"$/);
  if (!m) throw new Error("dòng CSV không đúng dạng: " + l);
  const { t, e } = T.botTrich(m[1]);
  console.log(T.botYDinhLuat(t, e) ?? "null");
}
