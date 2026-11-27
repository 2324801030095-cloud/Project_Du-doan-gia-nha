// Dựng TÀI LIỆU BÀN GIAO (Word). Chạy: node tao_ban_giao.js <file .docx ra> so_lieu_ban_giao.json
// Chạy: node tao_bao_cao.js <đường dẫn file .docx ra> <tep_du_lieu.json>
const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, ShadingType, AlignmentType,
  HeadingLevel, LevelFormat, BorderStyle, PageBreak, TableOfContents, Footer, PageNumber, Header, TableLayoutType,
} = require("docx");

const OUT = process.argv[2], D = JSON.parse(fs.readFileSync(process.argv[3], "utf8"));
const FONT = "Arial", MONO = "Consolas";
const W = 9026;                         // bề rộng vùng chữ A4 với lề 1 inch (DXA)

// ---------- trợ giúp ----------
// **đậm** và `mã` trong một dòng chữ
function runs(text, base = {}) {
  const out = [];
  const re = /(\*\*[^*]+\*\*|`[^`]+`)/g; let i = 0, m;
  while ((m = re.exec(text))) {
    if (m.index > i) out.push(new TextRun({ text: text.slice(i, m.index), ...base }));
    const t = m[0];
    out.push(t.startsWith("**") ? new TextRun({ text: t.slice(2, -2), bold: true, ...base })
                                : new TextRun({ text: t.slice(1, -1), font: MONO, size: 19, ...base }));
    i = m.index + t.length;
  }
  if (i < text.length) out.push(new TextRun({ text: text.slice(i), ...base }));
  return out;
}
const P = (t, o = {}) => new Paragraph({ children: runs(t), spacing: { after: 120 }, ...o });
const H1 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(t)] });
const H2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(t)] });
const H3 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun(t)] });
const B = (items, level = 0) => items.map((t) => new Paragraph({ numbering: { reference: "cham", level }, children: runs(t), spacing: { after: 60 } }));
let soDs = 0;
const N = (items) => { const ref = "so" + (soDs++ % 40); return items.map((t) => new Paragraph({ numbering: { reference: ref, level: 0 }, children: runs(t), spacing: { after: 60 } })); };
const CODE = (lines) => lines.map((l, k) => new Paragraph({
  children: [new TextRun({ text: l || " ", font: MONO, size: 18 })],
  shading: { type: ShadingType.CLEAR, fill: "F2F4F7", color: "auto" }, spacing: { after: k === lines.length - 1 ? 160 : 0 },
  indent: { left: 120, right: 120 },
}));
const LUU_Y = (t) => new Paragraph({
  children: runs(t), spacing: { before: 60, after: 160 }, indent: { left: 240 },
  border: { left: { style: BorderStyle.SINGLE, size: 18, color: "C9A227", space: 8 } },
  shading: { type: ShadingType.CLEAR, fill: "FBF5E6", color: "auto" },
});
function TB(header, rows, ti, co = 19) {   // co = cỡ chữ trong bảng (nửa point)          // ti = tỷ lệ cột, tổng = 1
  const cols = ti.map((x) => Math.round(x * W)); cols[cols.length - 1] = W - cols.slice(0, -1).reduce((a, b) => a + b, 0);
  const vien = { style: BorderStyle.SINGLE, size: 4, color: "BFC7D1" };
  const o = (t, i, dau) => new TableCell({
    width: { size: cols[i], type: WidthType.DXA }, borders: { top: vien, bottom: vien, left: vien, right: vien },
    shading: dau ? { type: ShadingType.CLEAR, fill: "1F3A5F", color: "auto" } : undefined,
    margins: { top: 60, bottom: 60, left: 100, right: 100 },
    children: String(t ?? "").split("\n").map((d) => new Paragraph({ children: runs(d, dau ? { bold: true, color: "FFFFFF", size: co } : { size: co }) })),
  });
  return [new Table({
    width: { size: W, type: WidthType.DXA }, columnWidths: cols, layout: TableLayoutType.FIXED,
    rows: [new TableRow({ tableHeader: true, children: header.map((h, i) => o(h, i, true)) }),
           ...rows.map((r) => new TableRow({ cantSplit: true, children: r.map((c, i) => o(c, i, false)) }))],
  }), new Paragraph({ spacing: { after: 120 }, children: [] })];
}
const vn = (x) => (x == null ? "–" : x.toLocaleString("vi-VN"));

const C = [];
const add = (...x) => x.flat().forEach((e) => C.push(e));
const HOI = (q, a) => new Paragraph({ spacing: { after: 140 }, children: [new TextRun({ text: q + " ", bold: true }), ...runs(a)] });

// Nội dung tài liệu bàn giao. Mọi con số lấy từ D (so_lieu_ban_giao.json) – cùng một lần chạy, không gõ tay.
// Được nạp bởi tao_ban_giao.js (cung cấp các hàm H1, H2, P, B, N, CODE, LUU_Y, TB, HOI, add, Paragraph, TextRun...).
// làm tròn giống Python (README, notebook) để cùng một số hiển thị như nhau ở mọi nơi
const s = (x, d = 1) => (x == null || Number.isNaN(Number(x)) ? "–" : (Math.round(Number(x) * 10 ** d) / 10 ** d).toLocaleString("vi-VN", { minimumFractionDigits: d, maximumFractionDigits: d }));
const s0 = (x) => s(x, 0);
const DG = D.danh_gia, SL = D.so_lieu_web, MH = D.mo_hinh, DL = D.du_lieu, NB = D.nb;
const dong = (bang, ten) => bang.find((r) => r["Mô hình"] === ten);
const ten = DG.ten_mo_hinh;
const BL = "Baseline (đơn giá phường)", DC = DG.test_phu_hoa.map((r) => r["Mô hình"]).find((m) => m.startsWith("Đối chứng")),
  V1 = DG.test_phu_hoa.map((r) => r["Mô hình"]).find((m) => m.startsWith("Cách làm phiên bản 1"));
const tPH = dong(DG.test_phu_hoa, ten), bPH = dong(DG.test_phu_hoa, BL), tT = dong(DG.test_tdm, ten), bT = dong(DG.test_tdm, BL);
const cvPH = dong(DG.kiem_dinh_cheo_phu_hoa, ten), cvBPH = dong(DG.kiem_dinh_cheo_phu_hoa, BL);
const phu = DG.do_phu_test_80 || {}, pPH = phu["test Phú Hòa"], pT = phu["test TDM"];
const pVal = (x) => (x ? (x.match(/p = ([\d.]+)/) || [])[1] : null);
const CL = DG.chat_luong_du_lieu;
const ngay = SL.NGAY;
const chinh = (bang) => bang.filter((r) => r["Mô hình"] === ten || r["Mô hình"] === BL);   // phần chính: mô hình + mốc
const hang = (r) => [r["Mô hình"], s(r["MAPE (%)"]), `${s(r["MAPE thấp (95%)"])}–${s(r["MAPE cao (95%)"])}`, s(r["MdAPE (%)"]), `${s0(r["Trong ±20% (%)"])}%`, s(r["MAE (tỷ)"], 2), s(r["R²"], 2), s0(r["Số căn"])];
const COT_KQ = ["Mô hình", "MAPE (%)", "KTC 95%", "MdAPE (%)", "Trong ±20%", "MAE (tỷ)", "R²", "Số căn"], TI_KQ = [0.3, 0.09, 0.12, 0.1, 0.1, 0.1, 0.07, 0.12];
const thangPH = tPH["MAPE (%)"] < bPH["MAPE (%)"], chongPH = tPH["MAPE thấp (95%)"] <= bPH["MAPE cao (95%)"] && bPH["MAPE thấp (95%)"] <= tPH["MAPE cao (95%)"];
const thangT = tT["MAPE cao (95%)"] < bT["MAPE thấp (95%)"];

// ================= Bìa =================
add(new Paragraph({ spacing: { before: 2200, after: 240 }, alignment: AlignmentType.CENTER, children: [new TextRun({ text: "TÀI LIỆU BÀN GIAO", bold: true, size: 44, color: "1F3A5F" })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 240 }, children: [new TextRun({ text: "Mô hình học máy ước tính giá rao bán nhà ở phường Phú Hòa – Thủ Dầu Một", size: 28, color: "1F3A5F" })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 600 }, children: [new TextRun({ text: "Dataset · mô hình · kết quả · cách chạy · kiểm thử · chia việc nhóm", size: 22, italics: true, color: "1F3A5F" })] }),
  ...[["Môn học", "Học máy"], ["Sinh viên", "Nguyễn Quang Long – MSSV 2324801030095 – Lớp D23KTPM01"], ["Ngày lập", "27/11/2026"],
      ["Lần chạy bàn giao", `dữ liệu đến ${ngay}; mã nguồn commit ${D.moi_truong.commit}; Python ${D.moi_truong.python}, Node ${D.moi_truong.node}`],
      ["Tài liệu cũ", "docs/Tai_lieu_ky_thuat_tong_hop.docx (giữ nguyên để đối chiếu; tài liệu này thay thế khi bàn giao)"]]
    .map(([k, v]) => new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 100 }, children: [new TextRun({ text: k + ": ", bold: true }), new TextRun(v)] })),
  new Paragraph({ spacing: { before: 700 }, alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Mọi con số trong tài liệu được đọc tự động từ kết quả của CÙNG một lần chạy (models/*.json, dataset/, notebook đã chạy, API, kiểm thử).", italics: true, size: 20 })] }),
  new Paragraph({ children: [new PageBreak()] }));
add(new Paragraph({ children: [new TextRun({ text: "Mục lục", bold: true, size: 32, color: "1F3A5F" })], spacing: { after: 200 } }),
  new TableOfContents("Mục lục", { hyperlink: true, headingStyleRange: "1-2" }), new Paragraph({ children: [new PageBreak()] }));

// ================= 1. Tóm tắt =================
add(H1("1. Tóm tắt – bốn câu hỏi của giảng viên"),
  ...TB(["Câu hỏi", "Trả lời ngắn (chi tiết ở mục)"], [
    ["Dataset có gì?", `${s0(DL.tong)} tin rao bán nhà ở thật (nhà + đất) ở Bình Dương cũ, từ Chợ Tốt Nhà, alonhadat, guland, đã ẩn danh; ${s0(DL.tdm)} tin ở Thủ Dầu Một, ${s0(DL.ph)} tin ở Phú Hòa. Mỗi dòng là một tin rao; mục tiêu là giá rao (tỷ đồng). (Mục 3)`],
    ["Dùng mô hình nào?", `${ten}: tốt nhất trong 6 mô hình của môn học (hồi quy tuyến tính, cây quyết định, KNN, SVM, MLP, Random Forest), chọn bằng kiểm định chéo trên tập train. Mốc so sánh: đơn giá trung vị của phường × diện tích. (Mục 4)`],
    ["Mô hình dùng dữ liệu gì, hoạt động ra sao?", `Đầu vào X: ${MH.dac_trung.length} đặc trưng của căn nhà (diện tích, kích thước, tầng, sàn, phòng, lối vào, hẻm, pháp lý, tọa độ, khoảng cách tới trung tâm, 21 từ khóa trong mô tả). Đầu ra y = log(giá rao). Rừng gồm ${MH.n_estimators} cây quyết định, mỗi cây học trên một mẫu bootstrap và một phần đặc trưng; dự đoán = trung bình các cây trên thang log, đổi về tỷ đồng. (Mục 4)`],
    ["Kết quả số liệu?", `Trên ${s0(tPH["Số căn"])} căn test Phú Hòa (giữ riêng khỏi bước huấn luyện và chọn mô hình, sau khi áp dụng quy tắc làm sạch): MAPE ${s(tPH["MAPE (%)"])}%, MAE ${s(tPH["MAE (tỷ)"], 2)} tỷ; mốc đơn giá phường MAPE ${s(bPH["MAPE (%)"])}%, MAE ${s(bPH["MAE (tỷ)"], 2)} tỷ. Trên ${s0(tT["Số căn"])} căn test Thủ Dầu Một: ${s(tT["MAPE (%)"])}% so với ${s(bT["MAPE (%)"])}%. (Mục 5)`],
  ], [0.24, 0.76]),
  H2("1.1 Kết quả chính (mô hình và mốc trên CÙNG một tập test)"),
  ...TB(["Tập test giữ riêng", "Số căn", "Random Forest: MAPE / MAE", "Mốc đơn giá phường: MAPE / MAE", "KTC 95% MAPE của Random Forest"], [
    ["Phú Hòa", s0(tPH["Số căn"]), `${s(tPH["MAPE (%)"])}% / ${s(tPH["MAE (tỷ)"], 2)} tỷ`, `${s(bPH["MAPE (%)"])}% / ${s(bPH["MAE (tỷ)"], 2)} tỷ`, `${s(tPH["MAPE thấp (95%)"])}–${s(tPH["MAPE cao (95%)"])}%`],
    ["Toàn Thủ Dầu Một", s0(tT["Số căn"]), `${s(tT["MAPE (%)"])}% / ${s(tT["MAE (tỷ)"], 2)} tỷ`, `${s(bT["MAPE (%)"])}% / ${s(bT["MAE (tỷ)"], 2)} tỷ`, `${s(tT["MAPE thấp (95%)"])}–${s(tT["MAPE cao (95%)"])}%`],
  ], [0.2, 0.1, 0.25, 0.25, 0.2]),
  P(`Bằng chứng bổ trợ (kiểm định chéo lặp trên tập train, ${s0(cvPH["Số căn"])} căn Phú Hòa): Random Forest ${s(cvPH["MAPE (%)"])}% so với mốc ${s(cvBPH["MAPE (%)"])}%. Con số kiểm định chéo **không** đặt cạnh con số test trong cùng một so sánh, vì hai cách đo dùng tập căn khác nhau.`),
  LUU_Y(`**Kết luận trung thực:** ${thangT ? "trên toàn Thủ Dầu Một, Random Forest tốt hơn mốc rõ ràng (khoảng tin cậy không chồng nhau)." : "trên toàn Thủ Dầu Một, khoảng tin cậy của Random Forest và mốc còn chồng nhau."} Ở riêng Phú Hòa trên tập test này, Random Forest ${thangPH ? "có MAPE thấp hơn" : "có MAPE cao hơn"} mốc${(tPH["MAE (tỷ)"] < bPH["MAE (tỷ)"]) !== thangPH ? (thangPH ? " nhưng MAE cao hơn" : " nhưng MAE thấp hơn") + ` (MAE ${s(tPH["MAE (tỷ)"], 2)} so với ${s(bPH["MAE (tỷ)"], 2)} tỷ: hai thước đo xếp hạng ngược nhau)` : ""}${chongPH ? `; khoảng tin cậy chồng nhau: ${s0(tPH["Số căn"])} căn test quá ít để khẳng định mô hình hơn mốc ở riêng Phú Hòa` : ""}. Ở lần chạy ngày 26/11/2026 (trước khi rà quy tắc lọc tin đất), cùng phép đo cho Random Forest 26,4% và mốc 26,1%: thứ hạng đổi theo cách chia tập, đúng như khoảng tin cậy rộng cho thấy. Kiểm định chéo (nhiều căn hơn) lần nào cũng xếp Random Forest trên mốc. **Phạm vi kết luận:** tin rao nhà ở **đã qua làm sạch** (mục 3.6).`));

// ================= 2. Phạm vi =================
add(H1("2. Phạm vi và cách hiểu con số"),
  ...B([
    "**Bài toán:** học có giám sát, hồi quy. Ước tính **giá rao bán** của một căn **nhà ở (nhà + đất)** tại phường Phú Hòa từ thông số và mô tả của tin rao.",
    "**Giá rao, không phải giá giao dịch.** Nguồn dữ liệu (Chợ Tốt, alonhadat, guland) là tin rao công khai, truy xuất được. Giá giao dịch là mức hai bên chốt sau thương lượng; tổng chi phí người mua còn có thể gồm thuế, phí. Mọi con số của đề tài vì vậy là **giá rao bán ước tính**.",
    "**Nhà + đất:** diện tích đất, kích thước lô, lối vào và vị trí là đặc trưng có ích, nên giữ. Tin có tiêu đề \"bán đất\" (kể cả \"bán đất tặng nhà\") **vẫn giữ** nếu tin mô tả một căn nhà ở được (số tầng, diện tích sàn, phòng ngủ, trệt / lầu, nhà cấp 4): đối tượng bán thực tế là nhà + đất. Chỉ loại khi công trình kèm theo **không phải nhà để ở** (dãy trọ, ki-ốt, kho), tin nói rõ **để xây mới**, hoặc tin **không có thông tin căn nhà** (mục 3.4).",
    "**Đất nền độc lập đã bỏ khỏi bài chính:** không còn trong pipeline, API, web và **lịch thu thập hằng ngày** (dữ liệu đất không được tải mới). Notebook cũ ở notebooks/luu_tru/du_doan_gia_dat.ipynb; dữ liệu gốc, ảnh chụp và kết quả cũ giữ nguyên để truy xuất.",
    "**Bản HTML tĩnh (demo/index.html)** là bản minh họa cũ chạy offline, **không thuộc bài chính**: vẫn có tab đất nền dùng dữ liệu lưu trữ, và tính giá nhập mới bằng Ridge rút gọn. Bản minh họa chính là web Next.js (mục 6).",
    `**Thu thập cả vùng, đánh giá riêng Phú Hòa:** Phú Hòa chỉ có ${s0(DL.ph)} tin; học trên toàn vùng (${s0(DL.tong)} tin) giúp mô hình nắm quy luật chung (diện tích, tầng, hẻm), rồi đánh giá riêng trên các căn Phú Hòa. Học chỉ trên Phú Hòa sai nhiều hơn (mục 5.3).`,
    "**Phần mở rộng** (chạy được độc lập, không cần cho bài chính): căn hộ, giá thuê, xu hướng, trợ lý hỏi đáp.",
  ]));

// ================= 3. Dataset =================
// chỉ file gốc của NHÀ Ở (bài chính); file căn hộ / đất thuộc phần mở rộng / lưu trữ
const nguonRaw = D.tep.filter(([f]) => ["chotot_binh_duong_raw.csv", "alonhadat_tdm_raw.csv", "nha_phu_hoa_guland_raw.csv"].some((x) => f.endsWith("/" + x)));
add(H1("3. Dataset"),
  H2("3.1 Nguồn và quy mô"),
  P("File gốc của nhà ở (Chợ Tốt: toàn Bình Dương cũ, gồm cả tin cho thuê; alonhadat: Thủ Dầu Một; guland: Phú Hòa, mọi loại bất động sản – notebook chỉ lấy loại Nhà phố):"),
  ...TB(["File gốc (dataset/raw)", "Số dòng", "Số cột"], nguonRaw.map(([f, r, c]) => [f.replace("dataset/raw/", ""), s0(r), s0(c)]), [0.6, 0.2, 0.2]),
  P(`${NB.loc}. Sau làm sạch: ${NB.con_lai}. Hợp nhất mọi kỳ thu thập (${s0(D.so_anh_chup)} ảnh chụp có ghi ngày trong dataset/history), mỗi tin giữ bản mới nhất. Theo nguồn: ${Object.entries(DL.theo_nguon).map(([k, v]) => `${k} ${s0(v)}`).join(", ")}.`),
  P(`Giá rao ở Phú Hòa: thấp nhất ${s(DL.gia_ph.min, 2)} tỷ, trung vị ${s(DL.gia_ph["50%"], 2)} tỷ (nửa giữa ${s(DL.gia_ph["25%"], 2)}–${s(DL.gia_ph["75%"], 2)} tỷ), cao nhất ${s(DL.gia_ph.max, 2)} tỷ. Diện tích đất trung vị ${s(DL.dt_ph["50%"])} m².`),
  H2("3.2 Mỗi dòng là gì, mỗi cột dùng vào việc gì"),
  P("**Mỗi dòng** của dataset/processed/nha_da_xu_ly.csv là một tin rao bán nhà ở đã làm sạch. File chứa ba nhóm cột, cần tách bạch khi đọc:"),
  ...TB(["Nhóm cột", "Cột", "Đơn vị", "Vai trò"], [
    ["Mục tiêu", "gia_ty → y = log(gia_ty)", "tỷ đồng", "Giá trị mô hình học để dự đoán"],
    ["Đặc trưng căn nhà", "dt_dat (→ log_dt), ngang, dai, so_tang, dt_san, ty_le_san, phong_ngu, so_wc", "m², m, tầng, phòng", "Đầu vào X"],
    ["Đặc trưng lối vào, pháp lý", "mat_tien_duong, cap_loi_vao (1 hẻm nhỏ … 5 mặt tiền lớn), hem_rong, so_chung, noi_that", "0/1, cấp, m", "Đầu vào X"],
    ["Đặc trưng vị trí", "lat, lon, kc_trung_tam_km", "độ, km", "Đầu vào X (tọa độ có thể suy từ tuyến đường / tâm phường: cột muc_toa_do)"],
    ["Đặc trưng văn bản", "21 cờ t_* (hẻm xe hơi, khu dân cư, sổ riêng, nhà mới, bán gấp...)", "0/1", "Đầu vào X, đọc từ tiêu đề + mô tả"],
    ["Kỹ thuật", "nhom (tin gần trùng), tap (train/test), phuong, quan, duong", "–", "Chia tập, suy tọa độ, tính mốc; không đưa vào X"],
    ["Sinh SAU dự đoán", "gia_uoc_luong_ty, khoang80_thap/cao, chenh_lech_pt, chan_doan, thue_uoc_luong_trieu", "tỷ, %, triệu", "Kết quả của mô hình (Bước 11); KHÔNG dùng để học"],
  ], [0.18, 0.42, 0.14, 0.26], 17),
  H2("3.3 Chất lượng dữ liệu ở Phú Hòa"),
  ...TB(["Chỉ tiêu", "Giá trị"], [
    ["Số tin Phú Hòa", s0(CL.so_tin_phu_hoa)],
    ["Theo nguồn", Object.entries(CL.nguon).map(([k, v]) => `${k}: ${v}`).join(" · ")],
    ["Độ chính xác vị trí", Object.entries(CL.muc_toa_do).sort().map(([k, v]) => `${k.slice(3)}: ${v} tin`).join(" · ")],
    ["Tỷ lệ thiếu (Phú Hòa)", Object.entries(CL.thieu_pt).map(([k, v]) => `${k} ${s(v)}%`).join(" · ")],
    ["Xử lý ô thiếu", "Điền trung vị của TẬP TRAIN (không nhìn tập test); cờ từ khóa bù một phần thông tin thiếu"],
  ], [0.28, 0.72]),
  H2("3.4 Làm sạch: tin bị loại và lý do"),
  ...TB(["Lý do loại", "Số tin"], Object.entries(D.bi_loai).map(([k, v]) => [k, s0(v)]), [0.75, 0.25]),
  P("Danh sách đầy đủ (nguồn, link, tiêu đề, giá, lý do): dataset/processed/tin_bi_loai.csv."),
  P("**Tin \"bán đất\": tiêu chí quyết định.** Đọc cả tiêu đề, mô tả và các trường số tầng / diện tích sàn / phòng ngủ. **Giữ** nếu tin mô tả một căn nhà ở được; **loại** nếu công trình kèm theo là dãy trọ / ki-ốt / kho, nếu tin nói rõ mua đất để xây mới, hoặc nếu tin không có bất kỳ thông tin nào về căn nhà. Các tiêu đề chưa cho biết phần nhà đóng góp bao nhiêu vào giá rao; quy tắc chỉ xác định **đối tượng được chào bán** có phải nhà ở hay không."),
  ...TB(["Quyết định", "Tin", "Giá", "Lý do"], [
    ...D.bi_loai_dat.map((r) => ["Loại", `${r.nguon}: ${String(r.tieu_de).slice(0, 80)}`, `${s(r.gia_ty, 2)} tỷ`, r.ly_do_loai]),
    ...D.giu_dat.map((r) => ["Giữ", `${r.nguon}: ${String(r.tieu_de).slice(0, 80)}`, `${s(r.gia_ty, 2)} tỷ`, "Mô tả một căn nhà ở được" + (r.so_tang ? ` (${s0(r.so_tang)} tầng)` : r.phong_ngu ? ` (${s0(r.phong_ngu)} phòng ngủ)` : "")]),
  ], [0.1, 0.5, 0.1, 0.3], 16),
  H2("3.5 Tin trùng và cách chia tập"),
  ...B([
    `${NB.nhom}. Các tin gần trùng (cùng một căn đăng lại) luôn nằm **cùng một phía** khi chia train/test và khi chia fold.`,
    `Tập test = 1/5 số căn Thủ Dầu Một (StratifiedGroupKFold, phân tầng theo Phú Hòa): ${s0(DL.tdm_theo_tap.test)} căn TDM, trong đó ${s0(DL.ph_theo_tap.test)} căn Phú Hòa. ${NB.chia}`,
    `${NB.ro_ri}`,
    `Quy tắc gom tin trùng được kiểm tay trên ${D.nhan_tay.so_cap} cặp (dataset/labeled/cap_tin_gan_trung.csv). **Nhãn do Claude gán**, có ghi lý do từng cặp; **cần một người trong nhóm rà lại** các cặp khó trước khi coi là đã xác nhận.`,
  ]),
  H2("3.6 Bộ lọc \"đơn giá lệch quá xa khu vực\""),
  P("Bộ lọc so đơn giá của một tin với 15 căn lân cận và dùng **giá** của chính tin đó, áp **trước** khi chia train/test. Vì vậy không thể nói mọi bước xử lý đều độc lập với giá của tập test: tập test là các tin được **giữ riêng khỏi huấn luyện và chọn mô hình, sau khi làm sạch**. Notebook học lại với 4 ngưỡng (kể cả không lọc) và chấm trên **các tin được giữ ở mọi ngưỡng**:"),
  ...(D.nguong.length ? TB(["Ngưỡng lọc", "Số căn học", "MAPE Phú Hòa (%)", "MAPE TDM (%)", "KTC 95% (TDM)"], D.nguong.map((r) => r.slice(0, 5)), [0.32, 0.15, 0.17, 0.16, 0.2]) : []),
  LUU_Y("**Phép thử này đo được gì:** đổi ngưỡng ảnh hưởng thế nào **trên phần dữ liệu chung**. Nó **không** đo sai số trên chính các tin bị lọc. Vì vậy kết quả của đề tài áp dụng cho **tin rao đã qua làm sạch**. Muốn đánh giá trên tin mới bất kỳ ngoài thị trường, cần giữ riêng một tập đủ điều kiện theo loại nhà và đánh giá cả các mức giá bất thường đã xác minh."));

// ================= 4. Mô hình =================
add(H1("4. Mô hình"),
  H2("4.1 Đầu vào X, đầu ra y"),
  P(`**y = log(giá rao, tỷ đồng).** Mô hình **huấn luyện trên log giá** (giá lệch phải; trên thang log, chênh lệch giữa căn rẻ và căn đắt được đối xử theo tỷ lệ). **MAPE, MAE tính sau khi đổi dự đoán về tỷ đồng.** **X gồm ${MH.dac_trung.length} cột:** \`${MH.dac_trung.join(", ")}\`.`),
  H2("4.2 Random Forest hoạt động thế nào"),
  ...N([
    `Rừng gồm **${MH.n_estimators} cây quyết định hồi quy**. Mỗi cây học trên một **mẫu bootstrap** (rút ngẫu nhiên có hoàn lại từ tập train) và mỗi lần tách nút chỉ xét ${MH.max_features * 100}% số đặc trưng; lá có tối thiểu ${MH.min_samples_leaf} căn (siêu tham số chọn bằng GridSearchCV: ${NB.rf}).`,
    "Mỗi cây chia dữ liệu theo câu hỏi kiểu \"diện tích ≤ 85 m²?\", \"lối vào ≥ hẻm xe tải?\" sao cho phương sai log giá trong mỗi nhóm nhỏ nhất (cây hồi quy dùng phương sai thay cho entropy của ID3).",
    "Dự đoán của rừng = **trung bình** dự đoán của các cây trên thang log, rồi đổi về tỷ đồng bằng exp. Trung bình nhiều cây học trên mẫu khác nhau làm giảm phương sai so với một cây đơn.",
    "Ô thiếu được điền trung vị của tập train trước khi đưa vào cây (SimpleImputer).",
  ]),
  H2("4.3 Chọn mô hình (Phần A – các mô hình của môn học)"),
  P(`Random Forest là mô hình có sai số kiểm định chéo thấp nhất trong 6 mô hình của môn học (hồi quy tuyến tính, cây quyết định, KNN, SVM, MLP, Random Forest), chọn chỉ trên tập train bằng kiểm định chéo 5-fold chia theo nhóm. Bảng so sánh 6 mô hình và cách dò siêu tham số ở **Phụ lục B**.`),
  H2("4.4 Mốc so sánh"),
  P(`**Mốc (baseline):** giá = đơn giá trung vị của phường (tính trên tập train) × diện tích đất. Mô hình chỉ có giá trị khi thắng mốc này. Hai phép so sánh phụ (mô hình đối chứng ngoài bài giảng LightGBM và cách làm phiên bản 1 bằng Ridge) ở **Phụ lục B**.`),
  H2("4.5 Khoảng giá tham khảo 80%"),
  P("Lấy sai số ngoài-fold (log giá thật − log giá dự đoán) của tập train, chia nhóm (Phú Hòa riêng; căn khác theo 4 mức giá dự đoán), lấy phân vị 10% và 90%: khoảng = dự đoán × [e^q10, e^q90]. Mục tiêu là 80% căn tương tự có giá rao trong khoảng; **đây không phải bảo đảm cho từng căn**. Độ phủ thực tế đo trên tập test ở mục 5.4."),
  H2("4.6 Giải thích từng căn"),
  P("Đóng góp theo đường đi trên cây (phương pháp Saabas): mỗi lần cây tách theo một đặc trưng, phần thay đổi giá trị nút được ghi cho đặc trưng đó; nền + tổng đóng góp = dự đoán (có phép tự kiểm). Mỗi căn trong dữ liệu được giải thích bởi mô hình **không học căn đó**."),
  H2("4.7 Mô hình chấm test và mô hình triển khai là hai bản khác nhau"),
  P(`Số liệu test (mục 5) là của mô hình cùng cấu hình **chỉ học tập train**. File models/mo_hinh_gia_nha.joblib (web và API dùng) được **học lại trên toàn bộ ${s0(MH.so_can_hoc)} căn** sau khi đánh giá, nên không còn tập \"chưa thấy\" để chấm riêng nó. Đây là cách làm thông thường. Khi người dùng nhập thông số trùng một tin có sẵn, web vẫn trả **giá mô hình dự đoán**; giá rao của tin đó hiển thị dưới nhãn riêng (\"Giá rao trong tin\").`));

// ================= 5. Kết quả =================
const vdRows = D.vi_du.map((v) => [v.ten, `${s(v.ra.gia_ty, 2)} tỷ`, `${s(v.ra.khoang_80_ty[0], 2)}–${s(v.ra.khoang_80_ty[1], 2)} tỷ`, `${s(v.ra.don_gia_trieu_m2)} tr/m²`, `${s(v.ra.thue_trieu_thang)} tr/tháng`]);
add(H1("5. Kết quả"),
  H2("5.1 Tập test giữ riêng – Phú Hòa (kết quả chính)"),
  ...TB(COT_KQ, chinh(DG.test_phu_hoa).map(hang), TI_KQ, 17),
  H2("5.2 Tập test giữ riêng – toàn Thủ Dầu Một"),
  ...TB(COT_KQ, chinh(DG.test_tdm).map(hang), TI_KQ, 17),
  H2("5.3 Kiểm định chéo lặp trên tập train và các phép kiểm chứng"),
  ...TB(COT_KQ, chinh(DG.kiem_dinh_cheo_phu_hoa).map(hang), TI_KQ, 17),
  ...TB(["Phép kiểm (Phú Hòa, kiểm định chéo)", "Chênh MAPE so với cách chính (điểm %)", "KTC 95%"], NB.chenh.map(([k, c, lo, hi]) => [k, c, `${lo} … ${hi}`]), [0.5, 0.25, 0.25]),
  P("Khoảng tin cậy không chứa 0 thì chênh lệch mới có ý nghĩa: \"chia ngẫu nhiên\" đo phần rò rỉ còn lại do tin đăng lại; \"chỉ học Phú Hòa\" cho thấy học toàn vùng có lợi hay không."),
  H2("5.4 Khoảng giá 80%: mục tiêu và độ phủ đo được"),
  ...TB(["Tập", "Mục tiêu", "Đo được", "Kiểm định nhị thức (H0: phủ 80%)"], [
    ["Test Phú Hòa", "80%", pPH ? `${pPH.trong}/${pPH.tong} căn (${s0(pPH.trong / pPH.tong * 100)}%)` : "–", pVal(NB.phu_ph) ? `p = ${s(Number(pVal(NB.phu_ph)), 2)}` : "–"],
    ["Test toàn TDM", "80%", pT ? `${pT.trong}/${pT.tong} căn (${s0(pT.trong / pT.tong * 100)}%)` : "–", pVal(NB.phu_tdm) ? `p = ${s(Number(pVal(NB.phu_tdm)), 2)}` : "–"],
    ["Toàn bộ căn Phú Hòa (dự đoán chéo)", "80%", NB.phu_all || "–", "–"],
  ], [0.3, 0.14, 0.28, 0.28]),
  P(Number(pVal(NB.phu_ph)) < 0.05 ? "Ở test Phú Hòa, p < 0,05: khoảng **hơi hẹp** ở Phú Hòa trong lần chạy này (nhiều căn rao cao hơn dải trên). Web ghi cả mục tiêu và số đo thực tế cạnh khoảng giá." : "Kiểm định nhị thức chưa bác bỏ mức 80%; web ghi cả mục tiêu và số đo thực tế cạnh khoảng giá."),
  H2("5.5 MAE nói bằng tiền"),
  P(`MAE ${s(tPH["MAE (tỷ)"], 2)} tỷ trên test Phú Hòa (tính sau khi đổi dự đoán về tỷ đồng) nghĩa là: trung bình, giá mô hình lệch khỏi giá rao khoảng ${s0(tPH["MAE (tỷ)"] * 1000)} triệu đồng mỗi căn (giá rao trung vị ở Phú Hòa ${s(DL.gia_ph["50%"], 2)} tỷ). MdAPE ${s(tPH["MdAPE (%)"])}%: một nửa số căn lệch ít hơn mức này; ${s0(tPH["Trong ±20% (%)"])}% số căn lệch không quá ±20%.`),
  H2("5.6 Ví dụ đầu vào → đầu ra (API mô hình, lần chạy này)"),
  ...TB(["Đầu vào", "Giá ước tính", "Khoảng 80%", "Đơn giá", "Thuê ước tính"], vdRows, [0.38, 0.14, 0.18, 0.15, 0.15]),
  P("Ba tin **thật** trong tập test Phú Hòa (giá mô hình = dự đoán của mô hình không học tin đó): lệch ít nhất, ở giữa và nhiều nhất."),
  ...TB(["Tin rao", "Đất (m²)", "Giá rao", "Giá mô hình", "Lệch"], D.tin_that.map((t) => [t.tieu_de, s(t.dt), `${s(t.gia_rao, 2)} tỷ`, `${s(t.gia_mh, 2)} tỷ`, `${s(t.lech)}%`]), [0.46, 0.1, 0.14, 0.15, 0.15], 17));

// ================= 6. Kiến trúc =================
add(H1("6. Kiến trúc, cách chạy và web"),
  H2("6.1 Luồng dữ liệu"),
  ...CODE(["src/thu_thap.py ──► dataset/raw/ ──► scripts/sinh_notebook/chinh.py ──► notebooks/2324801030095.ipynb",
           "                                                                         │ (làm sạch, chia tập, học, đánh giá)",
           "                     dataset/processed/nha_da_xu_ly.csv  ◄────────────────┤",
           "                     models/mo_hinh_gia_nha.joblib, danh_gia_mo_hinh.json ◄┘",
           "                                  │  demo/build/build_site.py ──► models/du_lieu_web.json (+ bản tĩnh demo/index.html)",
           "                                  ▼",
           "                     api/ (FastAPI) ──► web/ (Next.js) ──► người dùng (http://localhost:3000)",
           "                                         └─► PostgreSQL (tài khoản, phiên, tin đã lưu, lịch sử định giá)"]),
  H2("6.2 Thành phần"),
  ...TB(["Thư mục", "Công nghệ", "Vai trò"], [
    ["scripts/sinh_notebook/chinh.py → notebooks/2324801030095.ipynb", "Python, scikit-learn, Jupyter", "Bài chính: sửa ở file .py rồi sinh lại notebook (không sửa .ipynb)"],
    ["src/mo_hinh_gia.py, src/thu_thap.py", "Python", "Mã dùng chung: đặc trưng, mô hình, đánh giá; thu thập + ẩn danh"],
    ["api/", "FastAPI", "Nạp models/*.joblib, định giá, danh sách tin, bản đồ, xu hướng (http://localhost:8000/docs)"],
    ["web/", "Next.js 16, React 19, TypeScript, Tailwind 4, Better Auth, Drizzle ORM", "Bản minh họa chính: định giá, tin rao, bản đồ, mô hình, trợ lý, đăng nhập, quản trị"],
    ["PostgreSQL 17", "Docker", "Người dùng (mật khẩu băm), phiên, tin đã lưu, lịch sử định giá"],
    ["demo/", "HTML tĩnh", "Bản cũ chạy offline, KHÔNG thuộc bài chính: vẫn có tab đất nền (dữ liệu lưu trữ); tính giá nhập mới bằng Ridge rút gọn, khác web chính"],
  ], [0.3, 0.27, 0.43], 17),
  H2("6.3 Lệnh chạy"),
  ...CODE(["python scripts/chay_toan_bo.py --nha-pho   # chỉ bài chính (chỉ cần dữ liệu nhà ở): notebook -> dữ liệu cho API -> README -> kiểm thử",
           "python scripts/chay_toan_bo.py             # toàn bộ (gồm phần mở rộng)",
           "copy .env.example .env                      # điền mật khẩu CSDL, BETTER_AUTH_SECRET, tài khoản admin",
           "docker compose up -d --build                # db + api + migrate + web -> http://localhost:3000"]),
  P("**API tự nạp bản mới:** dịch vụ mô hình đọc lại mô hình / dữ liệu khi file thay đổi (bộ nhớ đệm theo thời điểm sửa file), và /health trả mã băm của file đang phục vụ. Sau khi chạy, scripts/chay_toan_bo.py so mã băm đó với file trên đĩa và dừng báo lỗi nếu API còn phục vụ bản cũ. Lệnh --nha-pho chỉ cần dữ liệu nhà ở: bước xuất dữ liệu cho API (build_site.py --chi-du-lieu) bỏ qua phần mở rộng còn thiếu; trang HTML tĩnh chỉ dựng khi chạy toàn bộ."),
  P("Web: đăng ký / đăng nhập bằng email + mật khẩu (Better Auth, phiên trong CSDL, cookie httpOnly); tài khoản admin tạo tự động từ ADMIN_EMAIL / ADMIN_PASSWORD trong .env. Trợ lý dùng Groq phía máy chủ nếu có GROQ_API_KEY, không có thì dùng mô hình ý định của đề tài; giới hạn 20 câu hỏi / phút mỗi IP."));

// ================= 7. Kiểm thử =================
add(H1("7. Kiểm thử của lần chạy bàn giao"),
  ...TB(["Bộ kiểm thử", "Lệnh", "Kết quả thực tế"], [
    ["Mô hình, dữ liệu, số liệu notebook/README", "python tests/kiem_tra_mo_hinh.py", D.kiem_thu["kiem_tra_mo_hinh.py"]],
    ["API mô hình (trong tiến trình)", "python tests/kiem_tra_api.py", D.kiem_thu["kiem_tra_api.py"]],
    ["Bản tĩnh + trợ lý (luật)", "node tests/kiem_tra_tro_ly.js", D.kiem_thu["kiem_tra_tro_ly.js"]],
    ["Web đầu-cuối (cần docker compose up)", "node tests/kiem_tra_web.mjs", D.kiem_thu["kiem_tra_web.mjs"]],
  ], [0.34, 0.36, 0.3]),
  P(`Môi trường: Python ${D.moi_truong.python}, Node ${D.moi_truong.node}, Windows 11 + Docker Desktop; commit ${D.moi_truong.commit}. Phụ thuộc kiểm thử khai báo trong requirements.txt (gồm starlette và httpx2 cho TestClient của FastAPI). Kiểm thử web gồm: mọi trang trả 200, trang đất nền trả 404, đăng ký / đăng nhập thật, sai mật khẩu bị từ chối, phân quyền user / admin, lịch sử định giá, lưu tin, đăng xuất hủy phiên, trợ lý.`));

// ================= 8. Hạn chế =================
add(H1("8. Hạn chế cần nêu khi trình bày"),
  ...B([
    "Mô hình ước tính **giá rao**, không phải giá giao dịch. Một phần sai số có thể đến từ chính giá rao (cùng căn nhiều giá, phần thương lượng), nhưng đề tài **chưa đo** được tỷ lệ này (cần giá giao dịch thật để tách).",
    "Kết quả áp dụng cho **tin rao đã qua làm sạch** (mục 3.6); sai số trên các tin bị bộ lọc đơn giá loại ra chưa được đo.",
    `Tập test Phú Hòa chỉ ${s0(tPH["Số căn"])} căn: khoảng tin cậy rộng, thứ hạng mô hình – mốc có thể đổi giữa các lần chia (mục 1.1).`,
    `Vị trí: chỉ ${CL.muc_toa_do["1. tọa độ riêng"] || 0} tin Phú Hòa có tọa độ riêng; còn lại suy từ tuyến đường hoặc tâm phường.`,
    `Nhiều ô thiếu: ${Object.entries(CL.thieu_pt).slice(0, 4).map(([k, v]) => `${k} ${s(v)}%`).join(", ")} ở Phú Hòa.`,
    "Bộ lọc đơn giá theo lân cận dùng giá trước khi chia tập (mục 3.6); nhãn kiểm tra gom tin trùng do Claude gán, cần người rà lại.",
    "Khoảng 80% là mục tiêu, không phải bảo đảm cho từng căn; độ phủ đo được ở mục 5.4.",
  ]));

// ================= 9. Mở rộng =================
const chT = dong(D.can_ho.test, D.can_ho.ten_mo_hinh);
add(H1("9. Phần mở rộng (không thuộc bài chính)"),
  ...B([
    `**Căn hộ:** ${D.can_ho.ten_mo_hinh}, MAPE ${s(chT["MAPE (%)"])}% trên ${s0(chT["Số căn"])} căn test. Việc phụ: kiểm tra lại với giá trong tiêu đề / mô tả được che (một số tin có cụm số tiền, có nguy cơ lộ đáp án, chưa đo mức ảnh hưởng).`,
    "**Giá thuê:** API ước tính = giá ước tính × tỷ suất cho thuê trung vị theo phường / dự án (đo từ tin cho thuê thật), không phải mô hình thuê riêng cho từng căn.",
    "**Xu hướng:** kịch bản có điều kiện từ tín hiệu đổi giá cùng một căn; chưa đủ kỳ dữ liệu để kiểm định lùi.",
    "**Trợ lý:** mô hình ý định TF-IDF + Logistic Regression; chế độ AI (Groq) phía máy chủ gọi công cụ là API mô hình.",
    "**Đất nền:** đã bỏ (mục 2); notebook lưu ở notebooks/luu_tru/.",
  ]));

// ================= 10. Chia việc =================
add(H1("10. Chia việc để cả nhóm nắm dự án"),
  ...TB(["Người phụ trách", "Phần đọc và bàn giao", "Câu phải trả lời được"], [
    ["Dữ liệu", "Nguồn, CSV, từ điển cột (3.2), quy tắc giữ / loại tin (3.4), thống kê Phú Hòa (3.3)", "Mỗi dòng là gì, giá lấy từ đâu, dữ liệu thiếu gì, vì sao giữ tin này?"],
    ["Mô hình", "Notebook chính, cách chia tập (3.5), thuật toán (4), mốc so sánh, bảng kết quả (5)", "Mô hình học từ những cột nào, dự đoán ra sao, sai bao nhiêu trên tin chưa học?"],
    ["API và web", "Cách nạp mô hình, đường đi form → API (6), kết quả demo", "Khi nhập thông số, con số đến từ đâu và khác giá rao trong tin thế nào?"],
    ["Báo cáo và tích hợp", "Đối chiếu CSV, JSON, notebook, README và tài liệu này (7)", "Mọi số liệu và lệnh chạy có khớp phiên bản bàn giao không?"],
  ], [0.18, 0.42, 0.4]),
  P("**Điều kiện bàn giao:** notebook chính chạy từ đầu đến cuối trên dữ liệu đã chốt; web gọi được mô hình vừa xuất; các bộ kiểm thử có kết quả thực tế (mục 7); tài liệu dùng đúng số liệu của cùng lần chạy (tự động, xem bìa)."));

// ================= 11. Câu hỏi bảo vệ =================
add(H1("11. Câu hỏi bảo vệ thường gặp"),
  HOI("Vì sao huấn luyện trên log(giá)?", "Giá lệch phải; trên thang log, chênh lệch giữa căn rẻ và căn đắt được đối xử theo tỷ lệ, nên vài căn rất đắt không chi phối mô hình. Khi đánh giá, dự đoán được đổi về tỷ đồng rồi mới tính MAPE, MAE."),
  HOI("Vì sao chọn Random Forest?", `Tốt nhất trong 6 mô hình của môn học theo kiểm định chéo trên tập train (mục 4.3). Đối chứng ngoài bài giảng (${DC}) không tốt hơn rõ, nên giữ mô hình của môn học: dễ giải thích, không cần đặc trưng giá khu vực.`),
  HOI("Mô hình có thắng mốc đơn giản không?", `Trên toàn Thủ Dầu Một: ${s(tT["MAPE (%)"])}% so với ${s(bT["MAPE (%)"])}%${thangT ? ", khác biệt rõ" : ""}. Riêng ${s0(tPH["Số căn"])} căn Phú Hòa: MAPE ${s(tPH["MAPE (%)"])}% so với ${s(bPH["MAPE (%)"])}%, MAE ${s(tPH["MAE (tỷ)"], 2)} so với ${s(bPH["MAE (tỷ)"], 2)} tỷ${chongPH ? ", khoảng tin cậy chồng nhau nên chưa khẳng định được" : ""}. Phú Hòa khá đồng đều nên đơn giá phường đã là ước lượng tốt.`),
  HOI("Vì sao chia train/test theo nhóm?", `Cùng một căn thường đăng nhiều lần; nếu một tin ở train và tin kia ở test, mô hình \"thấy đáp án\". ${NB.ro_ri}`),
  HOI("Khoảng 80% có bảo đảm không?", `Không. Đó là mục tiêu dựng từ sai số ngoài-fold; đo trên test Phú Hòa: ${pPH ? `${pPH.trong}/${pPH.tong} căn` : "–"} (mục 5.4).`),
  HOI("Vì sao bỏ định giá đất nền?", "Đề tài định giá nhà ở. Lô đất trống là đối tượng khác. Tin \"bán đất tặng nhà\" vẫn giữ nếu mô tả căn nhà ở được; chỉ loại khi công trình không phải nhà để ở, khi tin để xây mới, hoặc không có thông tin nhà. Notebook đất cũ vẫn lưu để truy xuất."),
  HOI("Web lấy con số từ đâu?", "Form → route handler Next.js → API FastAPI → models/mo_hinh_gia_nha.joblib (Random Forest học lại trên toàn bộ dữ liệu sạch). Giá rao của tin (nếu có) hiện dưới nhãn riêng."));

// ================= Phụ lục =================
add(H1("Phụ lục A. Danh sách file dữ liệu và kết quả"),
  ...TB(["File", "Dòng", "Cột", "KB"], D.tep.map(([f, r, c, kb]) => [f, r == null ? "–" : s0(r), c == null ? "–" : s0(c), s0(kb)]), [0.62, 0.13, 0.1, 0.15], 16),
  H1("Phụ lục B. Quá trình chọn mô hình và các phép so sánh phụ"),
  P(`**6 mô hình của môn học** (kiểm định chéo 5-fold chia theo nhóm, chỉ trên tập train). Siêu tham số: độ sâu cây ${NB.do_sau}, k = ${NB.k} của KNN theo đường cong quá khớp; SVR ${NB.svr}; MLP ${NB.mlp}; Random Forest ${NB.rf}.`),
  ...TB(["Mô hình", "MAE log – phần học", "MAE log – kiểm định", "≈ sai số %"], D.phan_a.map(([m, a, b, c]) => [m, a === "NaN" ? "–" : s(Number(a), 3), s(Number(b), 3), `${s(Number(c))}%`]), [0.46, 0.18, 0.18, 0.18]),
  P(`**So sánh phụ trên cùng tập test:** đối chứng ngoài bài giảng (${DC}) và cách làm phiên bản 1 (Ridge 9 thông số, chỉ học Phú Hòa).`),
  ...TB(COT_KQ, DG.test_phu_hoa.map(hang), TI_KQ, 16),
  ...TB(COT_KQ, DG.test_tdm.map(hang), TI_KQ, 16),
  P("Kiểm định chéo trên tập train (đủ các mô hình):"),
  ...TB(COT_KQ, DG.kiem_dinh_cheo_phu_hoa.map(hang), TI_KQ, 16),
  H1("Phụ lục C. Thay đổi so với tài liệu cũ"),
  ...B([
    "Bỏ định giá đất nền khỏi bài chính, API, web, lịch thu thập; quy tắc tin \"bán đất\": giữ nếu mô tả nhà ở được, loại nếu công trình không phải nhà để ở / để xây mới / không có thông tin nhà.",
    "Phần chính chỉ trình bày Random Forest và mốc đơn giá phường; bảng nhiều thuật toán, LightGBM, Ridge ở Phụ lục B.",
    "Câu chữ: tập test \"giữ riêng khỏi huấn luyện và chọn mô hình, sau khi làm sạch\"; phạm vi phép thử ngưỡng lọc; MAPE tính sau khi đổi về tỷ đồng; bỏ nhận định chưa đo về độ \"ảo\" của giá rao.",
    "Thêm từ điển cột, bảng chất lượng dữ liệu Phú Hòa, kiểm tra rò rỉ train/test in ra trong notebook.",
    "Bảng kết quả chính đặt mô hình và mốc trên cùng tập test (MAE, MAPE, số căn); kiểm định chéo để riêng.",
    "Ghi rõ khoảng 80% là mục tiêu, kèm độ phủ đo được; phân biệt mô hình chấm test với file triển khai.",
    "Kiến trúc mới: web Next.js + API FastAPI + PostgreSQL là bản minh họa chính; bản tĩnh ở demo/.",
    "Mọi số liệu đọc tự động từ cùng một lần chạy.",
  ]));

// ---------- tài liệu ----------
const cauHinhSo = Array.from({ length: 40 }, (_, i) => ({ reference: "so" + i, levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 300 } } } }] }));
const doc = new Document({
  creator: "Nguyễn Quang Long", title: "Tài liệu bàn giao – Dự đoán giá nhà Phú Hòa",
  styles: {
    default: { document: { run: { font: FONT, size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 32, bold: true, color: "1F3A5F" }, paragraph: { spacing: { before: 360, after: 160 }, keepNext: true, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 26, bold: true, color: "1F3A5F" }, paragraph: { spacing: { before: 240, after: 120 }, keepNext: true, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 23, bold: true }, paragraph: { spacing: { before: 200, after: 100 }, keepNext: true, outlineLevel: 2 } },
    ],
  },
  numbering: { config: [
    { reference: "cham", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 300 } } } },
                                   { level: 1, format: LevelFormat.BULLET, text: "–", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 1080, hanging: 300 } } } }] },
    ...cauHinhSo] },
  features: { updateFields: true },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 } } },
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: "Tài liệu bàn giao – Dự đoán giá nhà Phú Hòa", size: 16, color: "8A94A6" })] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: ["Trang ", PageNumber.CURRENT, " / ", PageNumber.TOTAL_PAGES], size: 16, color: "8A94A6" })] })] }) },
    children: C,
  }],
});
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(OUT, buf); console.log("Đã ghi", OUT, buf.length, "byte"); });
