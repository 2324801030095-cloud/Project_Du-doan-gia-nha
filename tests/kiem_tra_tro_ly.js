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

// ---------- 4. ngữ cảnh ----------
kiem("Hỏi tiếp giữ ngữ cảnh: '80m² 1 trệt 1 lầu' → 'nếu là mặt tiền' → 'còn 120m²'", () => {
  T.hoi("nhà 80m2 1 trệt 1 lầu hẻm xe hơi giá bao nhiêu"); T.hoi("nếu là nhà mặt tiền thì sao?", true); const r = T.hoi("còn 120m2 thì sao", true);
  return /120 m² đất/.test(r.text) && /1 trệt 1 lầu/.test(r.text) && /mặt tiền đường/.test(r.text) ? "" : r.text.slice(0, 160);
});
kiem("Hỏi tiếp sau tìm nhà: 'rẻ hơn thị trường thôi' giữ khoảng giá", () => {
  T.hoi("tìm nhà 2-3 tỷ"); const r = T.hoi("rẻ hơn thị trường thôi", true); return /2,0–3,0 tỷ/.test(r.text) && /rẻ hơn thị trường/.test(r.text) ? "" : r.text.slice(0, 160);
});

for (const [ten, ok, loi] of kq) console.log((ok ? "ĐẠT       " : "KHÔNG ĐẠT ") + ten + (ok ? "" : `\n           -> ${loi}`));
console.log(`\n${kq.filter((x) => x[1]).length}/${kq.length} phép kiểm đạt`);
process.exit(kq.every((x) => x[1]) ? 0 : 1);
