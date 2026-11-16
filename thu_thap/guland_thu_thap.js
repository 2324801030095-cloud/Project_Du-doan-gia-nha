// Script thu thập tin rao bán nhà đất Phường Phú Hòa (TP. Thủ Dầu Một) trên guland.vn
// Cách dùng: mở https://guland.vn/mua-ban-bat-dong-san-phuong-phu-hoa-thanh-pho-thu-dau-mot-binh-duong
// trong trình duyệt, mở DevTools > Console, dán toàn bộ script rồi Enter.
// Kết quả: tải về file guland_phu_hoa.csv (tất cả loại BĐS; notebook chỉ dùng loại "Nhà phố").
// Sau khi tải: chép file thành data/raw/nha_phu_hoa_guland_raw.csv (lưu bản cũ sang luu_tru/ trước). Notebook tự lọc loại "Nhà phố"
// và tự dùng cột mo_ta (mô tả tin) nếu có.
// Script nghỉ 0,3–0,7 giây giữa các lần tải trang để không gây tải cho máy chủ.
// Ngày chạy để tạo dữ liệu của đề tài: 12/11/2026.

(async () => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const parse = (html) => new DOMParser().parseFromString(html, "text/html");

  // 1) Duyệt các trang danh sách (?page=1, 2, ...) và lấy thông tin trên thẻ tin
  const rows = [];
  const seen = new Set();
  for (let p = 1; p <= 30; p++) {
    const d = parse(await (await fetch(location.origin + location.pathname + "?page=" + p)).text());
    const cards = d.querySelectorAll(".c-sdb-card");
    if (!cards.length) break;
    for (const c of cards) {
      const a = c.querySelector(".c-sdb-card__tle a");
      if (!a) continue;
      const id = (a.href.match(/-(\d+)$/) || [])[1];
      if (seen.has(id)) continue;
      seen.add(id);
      const vals = [...(c.querySelector(".sdb-inf-row")?.querySelectorAll(".sdb-inf-data") || [])].map((x) => x.innerText.trim());
      const adrs = [...c.querySelectorAll(".data-type-adr")].map((x) => x.innerText.trim());
      rows.push({
        id, url: a.href, title: a.innerText.trim(), vals,
        adr: adrs[adrs.length - 1] || "",
        spc: c.querySelector(".c-sdb-card__spc")?.innerText.replace("Đặc điểm BĐS:", "").trim() || "",
        exc: c.querySelector(".c-sdb-card__exc")?.innerText.trim() || "",
      });
    }
    await sleep(700);
  }
  console.log("Số tin trên danh sách:", rows.length);

  // 2) Vào trang chi tiết từng tin, đọc các cặp "Nhãn: giá trị" trong khối "Đặc điểm bất động sản"
  const det = {};
  for (const r of rows) {
    const d = parse(await (await fetch(r.url)).text());
    d.querySelectorAll("script,style").forEach((e) => e.remove());
    const s = d.body.textContent.replace(/[ \t]+/g, " ").replace(/\n\s*\n+/g, "\n");
    const i = s.indexOf("Đặc điểm bất động sản");
    const j = s.indexOf("Mọi thông tin, nội dung");
    const lines = (i >= 0 ? s.slice(i, j > i ? j : i + 3000) : "").split("\n").map((x) => x.trim()).filter(Boolean);
    const f = {};
    for (let k = 0; k < lines.length - 1; k++) {
      if (lines[k].endsWith(":") && lines[k].length < 40) f[lines[k].slice(0, -1)] = lines[k + 1];
    }
    const li = lines.findLastIndex((x) => x.endsWith(":"));
    det[r.id] = {
      f, cat: lines[1] || "",
      upd: (s.match(/Cập nhật ([^\n]+)/) || [])[1] || "",
      desc: li >= 0 ? lines.slice(li + 2).join(" ") : "",
    };
    await sleep(300);
  }

  // 3) Ghép thành bảng CSV
  const K = ["Tổng diện tích đất", "Diện tích thổ cư", "Mặt tiền", "Chiều dài", "Hướng đất", "Hình dáng đất",
    "Loại mặt thoáng", "Diện tích xây dựng", "Số tầng", "Diện tích sàn", "Số phòng ngủ", "Số phòng tắm",
    "Số tầng hầm", "Thời gian đã xây", "Loại công trình", "Vị trí", "Đường/hẻm rộng", "Hiện trạng",
    "Loại sổ", "Tình trạng sổ", "Nội thất"];
  const H = ["id", "tieu_de", "gia", "loai_bds", "dac_diem", "duong", "cap_nhat", "dt_dat", "dt_thocu", "mat_tien",
    "chieu_dai", "huong", "hinh_dang", "mat_thoang", "dt_xaydung", "so_tang", "dt_san", "phong_ngu", "phong_tam",
    "tang_ham", "nam_xay", "loai_ct", "vi_tri", "hem_rong", "hien_trang_duong", "loai_so", "tinh_trang_so",
    "noi_that", "pn_mota", "wc_mota", "tret_lau_mota", "url", "ngay_thu_thap", "mo_ta"];
  const homNay = new Date().toISOString().slice(0, 10);
  const q = (v) => {
    v = (v ?? "").toString().replace(/\s+/g, " ").trim().replace(/ m²$/, "").replace(/^(\d+(\.\d+)?) m$/, "$1");
    return /[",\n]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v;
  };
  const out = [H.join(",")];
  for (const r of rows) {
    const d = det[r.id] || { f: {} };
    const txt = (r.title + " " + r.exc + " " + (d.desc || "")).toLowerCase();
    // Số phòng ngủ / WC / số tầng ghi trong phần mô tả (dùng để bổ sung khi ô thông số bị trống)
    const pn = (txt.match(/(\d+)\s*(?:pn|phòng ngủ|phong ngu)/) || [])[1] || "";
    const wc = (txt.match(/(\d+)\s*(?:wc|toilet|vệ sinh|vs\b)/) || [])[1] || "";
    const tl = txt.match(/(\d*)\s*trệt\s*,?\s*(\d+)\s*(?:lầu|lững|lửng)/) || [];
    const tret_lau = tl.length ? "1+" + tl[2] : /gác lửng|gác lững|gác đúc/.test(txt) ? "gac" : /cấp 4/.test(txt) ? "cap4" : "";
    const duong = r.adr.replace(/,?\s*Phường Phú Hòa, Thành phố Thủ Dầu Một, Bình Dương/, "");
    // (bản 2) lưu tiêu đề đầy đủ + phần mô tả (tối đa 1.500 ký tự) để mô hình đọc được từ khóa: khu dân cư, sổ riêng, bán gấp...
    out.push([r.id, r.title, r.vals[0].replace(" tỷ", "e9").replace(" triệu", "e6"), d.cat,
      r.spc.replace(/\s+/g, " "), duong, d.upd, ...K.map((k) => d.f[k]), pn, wc, tret_lau, r.url, homNay, ((r.exc || "") + " " + (d.desc || "")).slice(0, 1500)].map(q).join(","));
  }
  const blob = new Blob(["﻿" + out.join("\n")], { type: "text/csv" });
  const a = Object.assign(document.createElement("a"), { href: URL.createObjectURL(blob), download: "guland_phu_hoa.csv" });
  a.click();
  console.log("Xong:", out.length - 1, "tin");
})();
