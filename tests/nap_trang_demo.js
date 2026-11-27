// Nạp phần JavaScript của demo/index.html vào Node với một DOM giả lập tối thiểu,
// để kiểm thử tự động trợ lý hỏi đáp và các hàm định giá mà không cần mở trình duyệt.
// Dùng: const T = require("./nap_trang_demo.js");  T.hoi("nhà 80m2 hẻm xe hơi")  -> { y, e, text }
// Chạy trực tiếp: node tests/nap_trang_demo.js dataset/labeled/cau_hoi_kiem_tra.csv
//   -> in ý định do LUẬT TỪ KHÓA của trợ lý (botYDinhLuat) nhận ra cho từng câu (cột y_dinh, cau_hoi), "null" = không nhận ra.
//   Notebook tro_ly_y_dinh.ipynb dùng để so sánh luật với mô hình học máy trên cùng bộ câu hỏi.
const fs = require("fs"), path = require("path");
const html = fs.readFileSync(path.join(__dirname, "..", "demo", "index.html"), "utf8");
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map((m) => m[1]);
// Phần tử DOM giả: mọi thuộc tính / phương thức đều tồn tại (Proxy) để mã của trang chạy được trong Node
function el() {
  const store = { innerHTML: "", textContent: "", value: "", hidden: false, checked: false, dataset: {}, style: { setProperty() {} }, scrollTop: 0, scrollHeight: 0 };
  return new Proxy(store, {
    get(t, k) {
      if (k in t) return t[k];
      if (k === "classList") return { toggle() {}, add() {}, remove() {}, contains() { return false; } };
      if (k === "querySelectorAll") return () => [];
      if (k === "querySelector" || k === "closest") return () => null;
      if (k === "getBoundingClientRect") return () => ({ width: 600, height: 300, left: 0, top: 0, right: 600 });
      if (typeof k === "symbol") return undefined;
      return () => el();
    },
    set(t, k, v) { t[k] = v; return true; },
  });
}
const els = {};
global.document = { getElementById: (id) => (els[id] ??= el()), querySelectorAll: () => [], querySelector: () => el(),
  addEventListener() {}, createElement: () => el(), body: el(), title: "" };
global.window = { addEventListener() {}, scrollTo() {}, matchMedia: () => ({ matches: false, addEventListener() {} }) };
global.location = { hash: "#/", replace() {} };
global.history = { replaceState() {} };
global.localStorage = { getItem: () => null, setItem() {} };
global.requestAnimationFrame = (f) => f();
global.IntersectionObserver = class { observe() {} };
global.setTimeout = (f) => 0;    // không chạy hiệu ứng "đang trả lời"
const api = new Function(scripts.join("\n;\n") + `
;return { botTrich, botYDinh, botYDinhLuat, botTraLoi, BOT, predict, presetVec, MODEL, CH_MODEL, LISTINGS, CH_LIST, TREND, THUE, DAT_MODEL, DAT_LIST, datDuDoan, ysNha, ysCanHo, MAP_PTS, whyBlock, favItem, CH_TOA, TL_MODEL, tlDuDoan,
         AI, aiTraLoi, aiTools, AI_CONG_CU, kiemThamSo, htmlRaChu, aiMd, AI_HE_THONG, aiLuuCaiDat, aiDocCaiDat,
         aiTraLoiGemini, geminiTools, geminiMacDinh, aiBat, nhaCuaKhoa, LoiGemini, aiThongBaoLoi,
         aiTraLoiGroq, groqMacDinh, LoiGroq, aiMd: aiMd, aiKhoaMacDinh };`)();
api.hoi = (q, giuNguCanh = false) => {
  if (!giuNguCanh) api.BOT.ctx = null;
  const { t, e } = api.botTrich(q);
  const y = api.botYDinh(t, e);
  const r = api.botTraLoi(q);
  const text = r.html.replace(/<[^>]+>/g, " ").replace(/&amp;/g, "&").replace(/\s+/g, " ").trim();
  return { y, e, text, html: r.html, goi_y: r.goi_y };
};
module.exports = api;

if (require.main === module) {
  const dong = fs.readFileSync(process.argv[2], "utf8").split(/\r?\n/).slice(1).filter(Boolean);
  for (const l of dong) {
    const m = l.match(/^[^,]+,"(.*)"$/);
    if (!m) throw new Error("dòng CSV không đúng dạng: " + l);
    const { t, e } = api.botTrich(m[1]);
    console.log(api.botYDinhLuat(t, e) ?? "null");
  }
}
