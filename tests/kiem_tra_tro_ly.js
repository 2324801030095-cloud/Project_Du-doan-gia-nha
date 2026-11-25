// Kiểm thử tự động cho trợ lý hỏi đáp trên trang demo (demo/trang_ban_nha.html).
// Chạy từ thư mục gốc đề tài:  node tests/kiem_tra_tro_ly.js
// 1) Hiểu đúng ý định với nhiều cách hỏi (có dấu, không dấu, viết tắt)  2) trích đúng thông tin
// 3) con số trả lời khớp đúng mô hình  4) nhớ ngữ cảnh khi hỏi tiếp.
const T = require("./nap_trang_demo.js");
const kq = [];
const kiem = (ten, f) => { try { const loi = f(); kq.push([ten, !loi, loi || ""]); } catch (e) { kq.push([ten, false, "LỖI " + e.message]); } };

// ---------- 1. ý định ----------
const Y_DINH = [
  ["nha 80m2 hem xe hoi gia bao nhieu", "dinh_gia"], ["Nhà 4x20 1 trệt 2 lầu bao nhiêu tiền", "dinh_gia"], ["định giá giúp mình căn nhà 100 mét vuông mặt tiền", "dinh_gia"],
  ["nhà cấp 4 90m2 thì khoảng bao nhiêu", "dinh_gia"], ["nha 5x25 hxh 2 tang", "dinh_gia"], ["can nha 120m2 duong NTMK", "dinh_gia"], ["nhà 70 m2 3 lầu", "dinh_gia"],
  ["nhà 100m2 trị giá nhiêu", "dinh_gia"], ["mình có căn nhà 85m2 hẻm 4m muốn bán thì nên rao bao nhiêu", "dinh_gia"],
  ["tìm nhà tầm 3 tỷ", "tim"], ["có căn nào dưới 2.5 tỷ không", "tim"], ["nhà nào rẻ nhất ở phú hòa", "tim"], ["gợi ý nhà khoảng 4 tỷ 2 lầu", "tim"], ["ngân sách 3 tỷ mua được nhà nào", "tim"],
  ["mua căn hộ 1.5 tỷ ở đâu", "tim"], ["co nha mat tien nao duoi 7 ty", "tim"], ["nhà 3 tỷ 500", "tim"], ["tầm 2-3 tỷ có nhà nào", "tim"], ["nhà 60m2 trên 3 tỷ", "tim"],
  ["chung cư c skyview 2 phòng ngủ 60m2", "dinh_gia"], ["can ho the maison 70m2", "dinh_gia"], ["giá căn hộ k home new city", "dinh_gia"], ["căn hộ 2pn 65m2 phú hòa giá", "dinh_gia"],
  ["giá nhà có giảm không", "xu_huong"], ["năm sau nhà đất tăng không", "xu_huong"], ["có nên mua nhà lúc này", "xu_huong"], ["thị trường bất động sản đang thế nào", "xu_huong"],
  ["giá căn hộ có tăng nữa không", "xu_huong"],
  ["khu nào ở tdm rẻ nhất", "phuong"], ["giá nhà phú lợi", "phuong"], ["so sánh giá các phường", "phuong"],
  ["danh sách dự án chung cư thủ dầu một", "du_an"], ["chung cư nào rẻ ở tdm", "du_an"],
  ["sổ hồng là gì", "faq_phap_ly"], ["mua nhà vi bằng có rủi ro không", "faq_phap_ly"], ["điều kiện mua nhà ở xã hội", "faq_noxh"], ["AI tính giá như thế nào", "faq_mo_hinh"],
  ["dữ liệu lấy ở đâu", "faq_du_lieu"], ["có trả giá được không", "faq_thuong_luong"], ["kinh nghiệm mua nhà lần đầu", "faq_luu_y"], ["khoảng 80% nghĩa là gì", "faq_khoang"],
  ["nhà mặt tiền với nhà hẻm chênh bao nhiêu", "loi_vao"], ["chào bạn", "chao"], ["bạn giúp được gì", "gioi_thieu"], ["thanks", "cam_on"],
  ["nhà 80m2 cho thuê được bao nhiêu", "thue"], ["căn hộ c skyview 2pn 60m2 cho thuê bao nhiêu một tháng", "thue"], ["mua nhà 3 tỷ cho thuê mấy năm hoàn vốn", "thue"],
  ["căn hộ nào cho thuê tỷ suất cao", "thue"], ["lô đất 5x20 hẻm xe hơi phú hòa giá bao nhiêu", "dat"], ["đất nền 100m2 mặt tiền hiệp thành", "dat"],
  ["giá đất thổ cư 120m2 chánh mỹ", "dat"], ["mua đất 150m2 ở tdm hết bao nhiêu", "dat"], ["giá nhà đất năm sau tăng không", "xu_huong"],
  ["nhà mặt tiền đắt hơn nhà hẻm bao nhiêu", "loi_vao"],
  ["con mèo của tôi tên gì", null],
];
let dung = 0; const sai = [];
for (const [q, y] of Y_DINH) { const r = T.hoi(q); if (r.y === y) dung++; else sai.push(`"${q}" → ${r.y} (cần ${y})`); }
kiem(`Hiểu đúng ý định: ${dung}/${Y_DINH.length} câu (yêu cầu ≥ 95%)`, () => (dung / Y_DINH.length >= 0.95 ? "" : sai.join(" | ")));

// ---------- 2. trích thông tin ----------
const E = (q) => T.hoi(q).e;
kiem("Trích kích thước 5x20 → 100 m², ngang 5", () => { const e = E("nhà 5x20 giá bao nhiêu"); return e.dt === 100 && e.ngang === 5 ? "" : JSON.stringify(e); });
kiem("Trích '1 trệt 2 lầu' → 3 tầng; 'cấp 4' → 1 tầng", () => (E("nhà 80m2 1 trệt 2 lầu").st === 3 && E("nhà cấp 4 80m2").st === 1 ? "" : "sai số tầng"));
kiem("Trích giá '3 tỷ 500' = 3,5 tỷ; '850 triệu' = 0,85 tỷ", () => (Math.abs(E("nhà 3 tỷ 500").gia - 3.5) < 1e-9 && Math.abs(E("nhà 850 triệu").gia - 0.85) < 1e-9 ? "" : "sai giá"));
kiem("Trích khoảng giá '2–3 tỷ' (gạch dài) và 'dưới 2,5 tỷ'", () => { const a = E("tìm nhà 2–3 tỷ"), b = E("nhà dưới 2,5 tỷ"); return a.gmin === 2 && a.gmax === 3 && b.gmax === 2.5 ? "" : JSON.stringify([a, b]); });
kiem("Trích lối vào: hxh → hẻm xe hơi, mặt tiền → 5, hẻm 6m → hẻm xe tải", () => (E("nhà hxh 80m2").vt === 2 && E("nhà mặt tiền 80m2").vt === 5 && E("nhà hẻm 6m 80m2").vt === 3 ? "" : "sai lối vào"));
kiem("Nhận đúng dự án dài trước dự án ngắn (Happy One Central ≠ Happy One)", () => { const e = E("căn hộ happy one central 2pn 68m2"); return e.du_an && e.du_an.ten === "Happy One Central" ? "" : e.du_an?.ten; });
kiem("'xe hơi' không bị hiểu là 'rẻ'", () => (E("nhà hẻm xe hơi 80m2").re ? "bị hiểu là rẻ" : ""));

// ---------- 3. số liệu khớp mô hình ----------
kiem("Giá nhà phố trợ lý trả về = mô hình web (predict)", () => {
  const r = T.hoi("nhà 80m2 1 trệt 1 lầu hẻm xe hơi");
  const p = T.predict(T.presetVec({ dt_dat: "80", mat_tien: "", dt_san: "", phong_ngu: "", so_wc: "", hem_rong: "", so_tang: "2", vi_tri: "2", truc: "khac", noi_that: false })).price;
  const so = r.text.match(/(\d+,\d+) tỷ/); return so && Math.abs(parseFloat(so[1].replace(",", ".")) - p) < 0.006 ? "" : `${so && so[1]} ≠ ${p.toFixed(2)}`;
});
kiem("Giá căn hộ trợ lý trả về = mô hình căn hộ (bảng dự án + Ridge)", () => {
  const r = T.hoi("căn hộ C SkyView 2pn 60m2"), M = T.CH_MODEL, d = M.du_an.find((x) => x.ten === "C SkyView");
  const x = [Math.log(60), 2, NaN, NaN, NaN, NaN, 0];
  const adj = M.intercept + x.reduce((s, v, i) => s + ((Number.isFinite(v) ? v : M.medians[i]) - M.scaler.mean[i]) / M.scaler.scale[i] * M.coef[i], 0);
  const p = Math.exp(d.log_don_gia + adj) * 60, so = r.text.match(/(\d+,\d+) tỷ/);
  return so && Math.abs(parseFloat(so[1].replace(",", ".")) - p) < 0.006 ? "" : `${so && so[1]} ≠ ${p.toFixed(2)}`;
});
kiem("Tìm nhà 'dưới 3 tỷ': mọi căn liệt kê đều < 3 tỷ", () => {
  const r = T.hoi("tìm nhà dưới 3 tỷ"); const gia = [...r.html.matchAll(/<b>(\d+,\d+) tỷ<\/b>/g)].map((m) => parseFloat(m[1].replace(",", ".")));
  return gia.length && gia.every((g) => g < 3) ? "" : JSON.stringify(gia);
});
kiem("Không có căn khớp → vẫn gợi ý căn có giá gần nhất", () => (/giá gần nhất/.test(T.hoi("nhà 850 triệu").text) ? "" : "không có gợi ý"));
kiem("Nhà ở xã hội dùng khoảng 80% rộng hơn căn hộ thương mại", () => {
  const M = T.CH_MODEL; if (!M.phan_vi_sai_so_noxh) return "thiếu phan_vi_sai_so_noxh";
  return M.phan_vi_sai_so_noxh.q90 - M.phan_vi_sai_so_noxh.q10 > M.phan_vi_sai_so.q90 - M.phan_vi_sai_so.q10 ? "" : "khoảng NOXH không rộng hơn";
});

kiem("Giá đất trợ lý trả về = mô hình đất nền web (đơn giá phường + Ridge)", () => {
  const r = T.hoi("lô đất 5x20 hẻm xe hơi phú hòa giá bao nhiêu");
  const p = T.datDuDoan({ ph: "thu dau mot|phu hoa", dt: 100, ng: 5, vt: 2, hr: NaN, kdc: false, tc: NaN, so: NaN }).price;
  const so = r.text.match(/(\d+,\d+) tỷ/); return so && Math.abs(parseFloat(so[1].replace(",", ".")) - p) < 0.006 ? "" : `${so && so[1]} ≠ ${p.toFixed(2)}`;
});
kiem("Đất nền: mặt tiền đắt hơn hẻm, khoảng 80% bao quanh giá", () => {
  const b = { ph: "thu dau mot|phu hoa", dt: 100, ng: 5, hr: NaN, kdc: false, tc: NaN, so: NaN };
  const h = T.datDuDoan({ ...b, vt: 2 }), m = T.datDuDoan({ ...b, vt: 5 });
  return m.price > h.price && h.lo < h.price && h.price < h.hi ? "" : JSON.stringify([h, m]);
});
kiem("Cho thuê: tiền thuê = giá × tỷ suất phường / 12, tỷ suất trong 1–12%/năm", () => {
  const r = T.hoi("mua nhà 3 tỷ ở phú hòa cho thuê được bao nhiêu"), ys = T.ysNha("phu hoa");
  const so = r.text.match(/(\d+,\d) triệu\/tháng/);
  return ys > 1 && ys < 12 && so && Math.abs(parseFloat(so[1].replace(",", ".")) - 3000 * ys / 100 / 12) < 0.06 ? "" : `${so && so[1]} / ys ${ys}`;
});
kiem("Căn hộ cho tỷ suất cho thuê cao hơn nhà phố (đúng kết luận notebook)", () => (T.THUE.ty_suat_tv.can_ho > T.THUE.ty_suat_tv.nha_tdm ? "" : JSON.stringify(T.THUE.ty_suat_tv)));
kiem("Hỏi tiếp đất nền: 'nếu là mặt tiền thì sao' vẫn định giá đất, giá tăng", () => {
  const a = T.hoi("lô đất 5x20 hẻm xe hơi phú hòa giá bao nhiêu"), b = T.hoi("nếu là mặt tiền thì sao?", true);
  const g = (r) => parseFloat((r.text.match(/(\d+,\d+) tỷ/) || [0, "0"])[1].replace(",", "."));
  return /mặt bằng đơn giá đất/i.test(b.text) && g(b) > g(a) ? "" : b.text.slice(0, 150);
});
kiem("Bản đồ: mọi điểm nằm trong Bình Dương cũ, có đơn giá dương", () => (T.MAP_PTS.length > 500 && T.MAP_PTS.every((p) => p[0] > 10.8 && p[0] < 11.7 && p[1] > 106.3 && p[1] < 107 && p[2] > 0) ? "" : `${T.MAP_PTS.length} điểm`));
kiem("Giải thích SHAP của mô hình đầy đủ hiển thị trong chi tiết tin", () => {
  const o = T.LISTINGS.find((x) => x.gt); if (!o) return "không có tin nào có giải thích";
  return /Vì sao căn này/.test(T.whyBlock(o)) ? "" : "không hiển thị";
});

kiem("Bản đồ căn hộ: mỗi dự án đúng 1 chấm, đủ căn, căn ngoài TDM vẫn lưu được", () => {
  const ds = T.CH_TOA.filter((t) => t.co_du_an), ten = ds.map((t) => t.ten), tong = T.CH_TOA.reduce((s, t) => s + t.n, 0);
  // so với số căn hộ sạch notebook đã lưu (dữ liệu đổi theo kỳ); chỉ căn có tọa độ ở tâm phường bị bỏ khỏi bản đồ
  const n_sach = JSON.parse(require("fs").readFileSync(require("path").join(__dirname, "..", "model", "danh_gia_mo_hinh_can_ho.json"), "utf8")).so_can.tat_ca;
  if (tong < 0.95 * n_sach) return `chỉ có ${tong}/${n_sach} căn hộ trên bản đồ`;
  if (T.CH_TOA.some((t) => t.n !== t.can.length || !(t.lat > 10.8 && t.lat < 11.7 && t.lon > 106.3 && t.lon < 107))) return "số căn hoặc tọa độ tòa sai";
  const ngoai = T.CH_TOA.flatMap((t) => t.can).find((c) => !T.CH_LIST.some((x) => x.id === c.id));
  return ngoai && T.favItem("c" + ngoai.id) ? "" : "căn ngoài Thủ Dầu Một không lưu được";
});

// ---------- mô hình phân loại ý định (notebooks/tro_ly_y_dinh.ipynb) ----------
kiem("Trình duyệt tính xác suất ý định giống Python (TF-IDF + Logistic Regression)", () => {
  if (!T.TL_MODEL) return "chưa có mô hình: chạy notebook tro_ly_y_dinh.ipynb rồi build_site.py";
  for (const m of T.TL_MODEL.mau) {
    const r = T.tlDuDoan(m.cau), p = T.TL_MODEL.lop.map((l) => r.top.find((x) => x.y === l).p);
    const lech = Math.max(...p.map((x, k) => Math.abs(x - m.p[k])));
    if (lech > 0.005) return `"${m.cau}": lệch xác suất ${lech.toFixed(4)}`;
  }
  return "";
});
const kiemTra = require("fs").readFileSync(require("path").join(__dirname, "..", "data", "tro_ly", "cau_hoi_kiem_tra.csv"), "utf8")
  .split(/\r?\n/).slice(1).filter(Boolean).map((l) => l.match(/^([^,]+),"(.*)"$/)).map((m) => [m[2], m[1] === "ngoai_pham_vi" ? null : m[1]]);
kiem("Tập kiểm tra viết riêng: trợ lý hiểu đúng ≥ 90% và hơn luật cũ", () => {
  let moi = 0, cu = 0;
  for (const [q, y] of kiemTra) { const { t, e } = T.botTrich(q); if (T.botYDinh(t, e) === y) moi++; if (T.botYDinhLuat(t, e) === y) cu++; }
  const a = moi / kiemTra.length, b = cu / kiemTra.length;
  return a >= 0.9 && a > b ? "" : `trợ lý ${(a * 100).toFixed(1)}% · luật cũ ${(b * 100).toFixed(1)}%`;
});
kiem("Câu ngoài phạm vi / mơ hồ: từ chối hoặc hỏi lại, không trả lời bừa", () => {
  const a = T.hoi("tỷ giá đô la hôm nay bao nhiêu"), b = T.hoi("cái đó sao");
  return /ngoài phạm vi/.test(a.text) && /chưa (chắc|hiểu)/.test(b.text) ? "" : a.text.slice(0, 80) + " || " + b.text.slice(0, 80);
});

kiem("Xu hướng theo kỳ hạn: '3 tháng', 'nửa năm', '2 năm' đứng đầu bảng; 6 và 12 tháng giữ đúng số notebook; > 24 tháng không đưa số", () => {
  const dau = (q) => (T.hoi(q).text.match(/: (\d+ (?:tháng|năm)) tới/) || [])[1];
  const a = dau("giá nhà 3 tháng tới thế nào"), b = dau("nửa năm nữa giá nhà ra sao"), c = dau("2 năm nữa giá nhà thế nào");
  const sau = T.hoi("giá nhà 6 tháng tới").text, f6 = T.TREND.du_bao_so.h6;
  const so6 = (sau.match(/6 tháng tới (\S+) … (\S+)/) || []).slice(1).map((x) => parseFloat(x.replace("−", "-").replace(",", ".")));
  const xa = /quá xa/.test(T.hoi("dự báo giá nhà 5 năm tới").text);
  return a === "3 tháng" && b === "6 tháng" && c === "2 năm" && Math.abs(so6[0] - f6.lo) < 0.06 && Math.abs(so6[1] - f6.hi) < 0.06 && xa ? "" : JSON.stringify([a, b, c, so6, f6, xa]);
});

// ---------- 4. ngữ cảnh ----------
kiem("Hỏi tiếp giữ ngữ cảnh: '80m² 1 trệt 1 lầu' → 'nếu là mặt tiền' → 'còn 120m²'", () => {
  T.hoi("nhà 80m2 1 trệt 1 lầu hẻm xe hơi giá bao nhiêu"); T.hoi("nếu là nhà mặt tiền thì sao?", true); const r = T.hoi("còn 120m2 thì sao", true);
  return /120 m² đất/.test(r.text) && /1 trệt 1 lầu/.test(r.text) && /mặt tiền đường/.test(r.text) ? "" : r.text.slice(0, 160);
});
kiem("Hỏi tiếp sau tìm nhà: 'rẻ hơn thị trường thôi' giữ khoảng giá", () => {
  T.hoi("tìm nhà 2-3 tỷ"); const r = T.hoi("rẻ hơn thị trường thôi", true); return /2,0–3,0 tỷ/.test(r.text) && /rẻ hơn thị trường/.test(r.text) ? "" : r.text.slice(0, 160);
});


// ---------- 5. chế độ AI (Claude gọi công cụ của trang) – dùng client giả lập, không gọi API thật, không tốn phí ----------
const kiemSau = [];   // phép kiểm bất đồng bộ
const kiemAsync = (ten, f) => kiemSau.push([ten, f]);
const giaTy = (s) => { const m = /(\d+,\d+) tỷ/.exec(s); return m ? parseFloat(m[1].replace(",", ".")) : NaN; };
const chuCua = (html) => html.replace(/<[^>]+>/g, " ").replace(/&amp;/g, "&").replace(/\s+/g, " ").trim();
kiem("Chế độ AI: công cụ định giá trả ĐÚNG số của mô hình (giống trợ lý ngoại tuyến)", () => {
  const cap = [
    [T.AI_CONG_CU.dinh_gia_nha_pho({ dien_tich_m2: 80, so_tang: 2, loi_vao: "hem_xe_hoi" }), "nhà 80m2 1 trệt 1 lầu hẻm xe hơi giá bao nhiêu"],
    [T.AI_CONG_CU.dinh_gia_can_ho({ du_an: "Happy One Central", dien_tich_m2: 68, phong_ngu: 2 }), "căn hộ Happy One Central 2PN 68m2 giá bao nhiêu"],
    [T.AI_CONG_CU.dinh_gia_dat({ dien_tich_m2: 100, ngang_m: 5, loi_vao: "hem_xe_hoi" }), "lô đất 5x20 hẻm xe hơi phú hòa giá bao nhiêu"],
  ];
  for (const [r, cau] of cap) {
    const a = giaTy(chuCua(r.html)), b = giaTy(T.hoi(cau).text);
    if (!(a > 0) || a !== b) return `${cau}: công cụ ${a} tỷ, trợ lý ngoại tuyến ${b} tỷ`;
  }
  return "";
});
kiem("Chế độ AI: lược đồ công cụ hợp lệ; tham số sai bị chặn trước khi chạy", () => {
  const tools = T.aiTools();
  if (tools.length !== Object.keys(T.AI_CONG_CU).length) return "số công cụ khác số hàm thực thi";
  for (const t of tools) {
    if (!T.AI_CONG_CU[t.name]) return `thiếu hàm cho ${t.name}`;
    if (t.input_schema.additionalProperties !== false || !t.eager_input_streaming) return `${t.name}: thiếu additionalProperties/eager_input_streaming`;
  }
  const sc = tools.find((t) => t.name === "dinh_gia_nha_pho").input_schema;
  const sai = [{}, { dien_tich_m2: "80" }, { dien_tich_m2: 80, loi_vao: "san_bay" }, { dien_tich_m2: 80, x: 1 }, { dien_tich_m2: 80, phong_ngu: 2.5 }, { dien_tich_m2: -5 }];
  for (const a of sai) if (!T.kiemThamSo(sc, a)) return "không chặn " + JSON.stringify(a);
  return T.kiemThamSo(sc, { dien_tich_m2: 80, so_tang: 2, loi_vao: "mat_tien", phuong: "Phú Hòa" }) || "";
});
kiem("Chế độ AI: khóa API không nằm trong file trang; câu trả lời của Claude được escape", () => {
  const html = require("fs").readFileSync(require("path").join(__dirname, "..", "demo", "trang_ban_nha.html"), "utf8");
  if (/sk-ant-[A-Za-z0-9_-]{10}/.test(html)) return "file trang chứa chuỗi giống khóa API";
  const h = T.aiMd("<img src=x onerror=alert(1)> **3,2 tỷ**\n- ý 1");
  return /<img/.test(h) || !/<b>3,2 tỷ<\/b>/.test(h) || !/<li>ý 1<\/li>/.test(h) ? h : "";
});

kiem("Mọi phần tử mã trang gọi bằng $('id') đều có trong HTML (DOM giả của kiểm thử không bắt được lỗi này)", () => {
  const h = require("fs").readFileSync(require("path").join(__dirname, "..", "demo", "trang_ban_nha.html"), "utf8");
  const ids = new Set([...h.matchAll(/id="([^"$]+)"/g)].map((m) => m[1]));
  const thieu = [...new Set([...h.matchAll(/\$\("([a-z0-9_-]+)"\)/g)].map((m) => m[1]))].filter((x) => !ids.has(x));
  return thieu.length ? "thiếu id: " + thieu.join(", ") : "";
});
kiem("Chế độ AI: nhập khóa một lần – mở lại trang tự bật (ghi nhớ mặc định); tắt thì xóa sạch", () => {
  const kho = () => { const m = new Map(); return { getItem: (k) => m.get(k) ?? null, setItem: (k, v) => m.set(k, String(v)), removeItem: (k) => m.delete(k) }; };
  const cu = [global.localStorage, global.sessionStorage];
  global.localStorage = kho(); global.sessionStorage = kho();
  try {
    T.AI.key = "sk-ant-thu"; T.AI.model = "claude-sonnet-5-5"; T.aiLuuCaiDat(true);
    T.AI.key = ""; T.AI.model = "claude-opus-5-5";                       // như vừa mở lại trang
    const noi = T.aiDocCaiDat();
    if (noi !== "localStorage" || T.AI.key !== "sk-ant-thu" || T.AI.model !== "claude-sonnet-5-5") return `đọc lại: ${noi} ${T.AI.key} ${T.AI.model}`;
    T.AI.key = ""; T.aiLuuCaiDat(false);                                    // nút "Tắt và xóa khóa"
    T.AI.model = "claude-opus-5-5";
    return T.aiDocCaiDat() === null && T.AI.key === "" ? "" : "tắt rồi vẫn còn khóa";
  } finally { [global.localStorage, global.sessionStorage] = cu; T.AI.key = ""; }
});
// Client Claude giả lập: trả lần lượt các tin nhắn soạn sẵn, ghi lại yêu cầu
function claudeGia(kichBan, loi) {
  class APIError extends Error { constructor(status, m) { super(m); this.status = status; } }
  class AuthenticationError extends APIError {}
  const yeuCau = [];
  const stream = (yc) => {
    yeuCau.push(JSON.parse(JSON.stringify(yc)));
    let onText = null;
    return { on(ev, f) { if (ev === "text") onText = f; return this; },
      async finalMessage() {
        if (loi) throw new AuthenticationError(401, "invalid x-api-key");
        const m = kichBan.shift(); if (!m) throw new Error("hết kịch bản");
        for (const b of m.content) if (b.type === "text" && onText) for (const d of b.text.match(/.{1,7}/gs)) onText(d);   // từng đoạn như streaming
        return m;
      } };
  };
  class Client { constructor(o) { this.o = o; Client.tuyChon = o; this.messages = { stream }; this.beta = { messages: { stream } }; } }
  return { mod: { default: Client, APIError, AuthenticationError }, yeuCau, Client };
}
function uiGia() { const u = { chu: "", the: [] }; u.chu_ = (d) => { u.chu += d; }; return { u, ui: { chu: (d) => u.chu_(d), the: (h) => u.the.push(h) } }; }

kiemAsync("Chế độ AI: vòng lặp công cụ – Claude gọi định giá, trang chạy hàm thật, Claude trả lời; hội thoại nhớ ngữ cảnh", async () => {
  const kb = [
    { stop_reason: "tool_use", content: [{ type: "thinking", thinking: "", signature: "s1" }, { type: "text", text: "Để mình tính." },
      { type: "tool_use", id: "tu_1", name: "dinh_gia_nha_pho", input: { dien_tich_m2: 80, so_tang: 2, loi_vao: "hem_xe_hoi" } }] },
    { stop_reason: "end_turn", content: [{ type: "text", text: "Căn này khoảng **X tỷ**." }] },
  ];
  const g = claudeGia(kb); T.AI.sdk = g.mod; T.AI.key = "khoa-thu"; T.AI.model = "claude-opus-5-5"; T.AI.msgs = [];
  const { u, ui } = uiGia();
  const kq = await T.aiTraLoi("nhà 80m2 1 trệt 1 lầu hẻm xe hơi bao nhiêu", ui);
  const yc = g.yeuCau[0], m = T.AI.msgs;
  const kt = [
    [kq.xong, "không kết thúc"], [g.Client.tuyChon.apiKey === "khoa-thu" && g.Client.tuyChon.dangerouslyAllowBrowser === true, "client không nhận khóa người dùng"],
    [yc.model === "claude-opus-5-5" && yc.tools.length === 11 && yc.system === T.AI_HE_THONG, "yêu cầu sai mô hình/công cụ/system"],
    [yc.fallbacks === "default" && yc.betas.includes("server-side-fallback-2026-07-01"), "thiếu fallbacks khi Claude từ chối"],
    [yc.cache_control?.type === "ephemeral" && yc.output_config?.effort === "medium", "thiếu cache_control/effort"],
    [u.chu === "Để mình tính.Căn này khoảng **X tỷ**.", "chữ streaming sai: " + u.chu], [u.the.length === 1 && /tỷ/.test(u.the[0]), "không hiện thẻ kết quả công cụ"],
    [m.length === 4 && m[1].content[0].type === "thinking" && m[2].content[0].type === "tool_result" && m[2].content[0].tool_use_id === "tu_1", "lịch sử sai cấu trúc"],
    [giaTy(m[2].content[0].content) === giaTy(T.hoi("nhà 80m2 1 trệt 1 lầu hẻm xe hơi giá bao nhiêu").text), "kết quả gửi Claude khác số của mô hình"],
    [g.yeuCau[1].messages.length === 3, "lượt 2 không gửi kèm kết quả công cụ"],
  ];
  const sai = kt.find(([ok]) => !ok); if (sai) return sai[1];
  // câu hỏi tiếp: lịch sử cũ được gửi lại nguyên vẹn
  kb.push({ stop_reason: "end_turn", content: [{ type: "text", text: "Mặt tiền đắt hơn." }] });
  await T.aiTraLoi("nếu là mặt tiền thì sao?", uiGia().ui);
  const yc3 = g.yeuCau[2];
  return yc3.messages.length === 5 && yc3.messages[0].content === "nhà 80m2 1 trệt 1 lầu hẻm xe hơi bao nhiêu" ? "" : "lượt sau không mang theo hội thoại cũ";
});
kiemAsync("Chế độ AI: tham số sai thì trả lỗi cho Claude, không chạy công cụ; Haiku không gửi fallbacks", async () => {
  const kb = [
    { stop_reason: "tool_use", content: [{ type: "tool_use", id: "tu_2", name: "dinh_gia_nha_pho", input: { dien_tich_m2: "tám mươi" } }] },
    { stop_reason: "end_turn", content: [{ type: "text", text: "Bạn cho mình diện tích nhé." }] },
  ];
  const g = claudeGia(kb); T.AI.sdk = g.mod; T.AI.model = "claude-haiku-5-5"; T.AI.msgs = [];
  const { u, ui } = uiGia();
  await T.aiTraLoi("nhà bao nhiêu", ui);
  const tr = T.AI.msgs[2].content[0];
  T.AI.model = "claude-opus-5-5";
  return tr.is_error && /không hợp lệ/.test(tr.content) && u.the.length === 0 && g.yeuCau[0].fallbacks === undefined ? "" : JSON.stringify(tr).slice(0, 160);
});
kiemAsync("Chế độ AI: lỗi API (khóa sai) báo lỗi và KHÔNG làm hỏng lịch sử hội thoại", async () => {
  const g = claudeGia([], true); T.AI.sdk = g.mod; T.AI.msgs = [{ role: "user", content: "cũ" }, { role: "assistant", content: [{ type: "text", text: "ok" }] }];
  let bat = null; try { await T.aiTraLoi("câu mới", uiGia().ui); } catch (e) { bat = e; }
  return bat instanceof g.mod.AuthenticationError && T.AI.msgs.length === 2 ? "" : `lỗi ${bat} · lịch sử ${T.AI.msgs.length} tin`;
});
kiemAsync("Chế độ AI: Claude từ chối thì bỏ cả lượt, trang dùng trợ lý ngoại tuyến", async () => {
  const g = claudeGia([{ stop_reason: "refusal", content: [] }]); T.AI.sdk = g.mod; T.AI.msgs = [];
  const kq = await T.aiTraLoi("câu bị từ chối", uiGia().ui);
  return kq.tuChoi && T.AI.msgs.length === 0 ? "" : JSON.stringify(kq);
});

// ---------- 6. chế độ AI với Gemini – fetch giả lập, không gọi API thật ----------
const traVe = (status, data) => ({ ok: status >= 200 && status < 300, status, json: async () => data });
function geminiGia(kichBan) {   // kichBan: mảng [status, data] theo thứ tự yêu cầu
  const yeuCau = [];
  const goi = async (url, init) => { yeuCau.push({ url, headers: init.headers, body: init.body ? JSON.parse(init.body) : null }); const [st, d] = kichBan.shift(); return traVe(st, d); };
  return { goi, yeuCau };
}
kiem("Gemini: nhận đúng loại khóa; lược đồ công cụ hợp lệ với Gemini (không additionalProperties, công cụ không tham số bỏ parameters)", () => {
  if (T.nhaCuaKhoa("sk-ant-api03-x") !== "claude" || T.nhaCuaKhoa("AQ.Ab8x") !== "gemini" || T.nhaCuaKhoa("AIzaSyx") !== "gemini") return "nhận sai loại khóa";
  const g = T.geminiTools(), s = JSON.stringify(g);
  if (g.length !== 11 || /additionalProperties|eager_input_streaming|input_schema/.test(s)) return "lược đồ còn trường Gemini không nhận";
  if (g.find((t) => t.name === "ty_suat_thue_du_an").parameters || !g.find((t) => t.name === "dinh_gia_nha_pho").parameters.required.includes("dien_tich_m2")) return "parameters sai";
  return "";
});
kiem("Gemini: mô hình mặc định là Flash ổn định mới nhất (bỏ preview, lite)", () => {
  const a = T.geminiMacDinh(["gemini-3-flash-preview", "gemini-3.6-flash", "gemini-3.8-flash", "gemini-3.5-flash-lite", "gemini-3.1-pro-preview"]);
  const b = T.geminiMacDinh(["gemini-3.1-pro-preview", "gemini-flash-latest"]);
  return a === "gemini-3.8-flash" && b === "gemini-flash-latest" ? "" : `${a} / ${b}`;
});
kiemAsync("Gemini: bật bằng khóa – gọi models.list kiểm khóa, lọc mô hình trò chuyện, lưu; khóa sai thì giữ nguyên trạng thái cũ", async () => {
  const kho = () => { const m = new Map(); return { getItem: (k) => m.get(k) ?? null, setItem: (k, v) => m.set(k, String(v)), removeItem: (k) => m.delete(k) }; };
  const cu = [global.localStorage, global.sessionStorage]; global.localStorage = kho(); global.sessionStorage = kho();
  try {
    const ds = { models: [["gemini-3.8-flash", ["generateContent"]], ["gemini-3.1-flash-image", ["generateContent"]], ["gemini-3.8-flash-tts", ["generateContent"]],
      ["text-embedding-005", ["embedContent"]], ["gemini-3.5-flash-lite", ["generateContent", "countTokens"]]].map(([n, m]) => ({ name: "models/" + n, supportedGenerationMethods: m })) };
    const g = geminiGia([[200, ds]]); T.AI.goi = g.goi; T.AI.key = ""; T.AI.nha = "claude";
    await T.aiBat("AQ.khoa-gia", "", true);
    if (T.AI.nha !== "gemini" || T.AI.model !== "gemini-3.8-flash" || T.AI.dsGemini.join() !== "gemini-3.8-flash,gemini-3.5-flash-lite") return `bật: ${T.AI.nha} ${T.AI.model} ${T.AI.dsGemini}`;
    if (!/\/v1beta\/models\?pageSize=1000$/.test(g.yeuCau[0].url) || g.yeuCau[0].headers["x-goog-api-key"] !== "AQ.khoa-gia") return "gọi models.list sai";
    T.AI.key = ""; T.AI.model = "x"; if (T.aiDocCaiDat() !== "localStorage" || T.AI.nha !== "gemini" || T.AI.model !== "gemini-3.8-flash") return "không lưu được để mở lại trang";
    const g2 = geminiGia([[400, { error: { code: 400, message: "API key not valid. Please pass a valid API key.", status: "INVALID_ARGUMENT" } }]]); T.AI.goi = g2.goi;
    let loi = null; try { await T.aiBat("AQ.khoa-sai", "", true); } catch (e) { loi = e; }
    return loi instanceof T.LoiGemini && T.AI.key === "AQ.khoa-gia" && T.AI.model === "gemini-3.8-flash" ? "" : `khóa sai: ${loi} · ${T.AI.key}`;
  } finally { [global.localStorage, global.sessionStorage] = cu; T.AI.key = ""; T.AI.nha = "claude"; T.AI.model = "claude-opus-5-5"; T.AI.goi = null; }
});
kiemAsync("Gemini: vòng lặp công cụ – gửi đúng yêu cầu, chạy hàm thật, trả functionResponse kèm id, giữ nguyên thoughtSignature", async () => {
  const goi = { functionCall: { id: "fc_1", name: "dinh_gia_nha_pho", args: { dien_tich_m2: 80, so_tang: 2, loi_vao: "hem_xe_hoi" } }, thoughtSignature: "chu_ky_1" };
  const g = geminiGia([
    [200, { candidates: [{ content: { role: "model", parts: [{ text: "Tóm tắt suy nghĩ", thought: true }, goi] }, finishReason: "STOP" }] }],
    [200, { candidates: [{ content: { role: "model", parts: [{ text: "Căn này khoảng **X tỷ**.", thoughtSignature: "chu_ky_2" }] }, finishReason: "STOP" }] }],
  ]);
  Object.assign(T.AI, { goi: g.goi, key: "AQ.khoa-gia", nha: "gemini", model: "gemini-3.8-flash", msgs: [] });
  const { u, ui } = uiGia();
  try {
    const kq = await T.aiTraLoiGemini("nhà 80m2 1 trệt 1 lầu hẻm xe hơi bao nhiêu", ui);
    const y = g.yeuCau[0], m = T.AI.msgs, fr = m[2].parts[0].functionResponse;
    const kt = [
      [kq.xong, "không kết thúc"], [/\/v1beta\/models\/gemini-3\.8-flash:generateContent$/.test(y.url) && y.headers["x-goog-api-key"] === "AQ.khoa-gia", "URL/khóa sai"],
      [y.body.systemInstruction.parts[0].text === T.AI_HE_THONG && y.body.tools[0].functionDeclarations.length === 11 && y.body.toolConfig.functionCallingConfig.mode === "AUTO", "thân yêu cầu sai"],
      [u.chu === "Căn này khoảng **X tỷ**." && u.the.length === 1, "hiện cả phần suy nghĩ hoặc thiếu thẻ: " + u.chu],
      [m[1].role === "model" && m[1].parts[1].thoughtSignature === "chu_ky_1" && m[3].parts[0].thoughtSignature === "chu_ky_2", "mất thoughtSignature"],
      [m[2].role === "user" && fr.id === "fc_1" && fr.name === "dinh_gia_nha_pho", "functionResponse thiếu id/name"],
      [giaTy(fr.response.result) === giaTy(T.hoi("nhà 80m2 1 trệt 1 lầu hẻm xe hơi giá bao nhiêu").text), "số gửi Gemini khác số mô hình"],
      [JSON.stringify(g.yeuCau[1].body.contents[1]) === JSON.stringify(m[1]), "lượt 2 không gửi lại nguyên phần của mô hình"],
    ];
    const sai = kt.find(([ok]) => !ok); return sai ? sai[1] : "";
  } finally { T.AI.goi = null; }
});
kiemAsync("Gemini: bị chặn vì an toàn thì bỏ lượt; lỗi 429 báo lỗi và giữ nguyên lịch sử", async () => {
  Object.assign(T.AI, { key: "AQ.khoa-gia", nha: "gemini", model: "gemini-3.8-flash", msgs: [] });
  try {
    T.AI.goi = geminiGia([[200, { promptFeedback: { blockReason: "SAFETY" }, candidates: [] }]]).goi;
    const kq = await T.aiTraLoiGemini("câu bị chặn", uiGia().ui);
    if (!kq.tuChoi || T.AI.msgs.length !== 0) return "không xử lý chặn an toàn";
    T.AI.msgs = [{ role: "user", parts: [{ text: "cũ" }] }, { role: "model", parts: [{ text: "ok" }] }];
    T.AI.goi = geminiGia([[429, { error: { code: 429, message: "Resource exhausted", status: "RESOURCE_EXHAUSTED" } }]]).goi;
    let loi = null; try { await T.aiTraLoiGemini("câu mới", uiGia().ui); } catch (e) { loi = e; }
    return loi instanceof T.LoiGemini && loi.status === 429 && T.AI.msgs.length === 2 ? "" : `${loi} · ${T.AI.msgs.length}`;
  } finally { T.AI.goi = null; T.AI.nha = "claude"; T.AI.model = "claude-opus-5-5"; T.AI.key = ""; T.AI.msgs = []; }
});

(async () => {
  for (const [ten, f] of kiemSau) { try { const loi = await f(); kq.push([ten, !loi, loi || ""]); } catch (e) { kq.push([ten, false, "LỖI " + e.message]); } }
  for (const [ten, ok, loi] of kq) console.log((ok ? "ĐẠT       " : "KHÔNG ĐẠT ") + ten + (ok ? "" : `
           -> ${loi}`));
  console.log(`
${kq.filter((x) => x[1]).length}/${kq.length} phép kiểm đạt`);
  process.exit(kq.every((x) => x[1]) ? 0 : 1);
})();
