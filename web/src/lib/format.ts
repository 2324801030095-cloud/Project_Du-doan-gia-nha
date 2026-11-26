// Định dạng số kiểu Việt Nam: 1.234,5
export const so = (x: number | null | undefined, d = 1) =>
  x === null || x === undefined || Number.isNaN(x) ? "–" : x.toLocaleString("vi-VN", { maximumFractionDigits: d, minimumFractionDigits: 0 });

export const ty = (x: number | null | undefined) => (x === null || x === undefined ? "–" : `${so(x, x >= 10 ? 1 : 2)} tỷ`);

export const phanTram = (x: number, d = 0) => `${x >= 0 ? "+" : "−"}${so(Math.abs(x), d)}%`;

export const MAU_CHAN_DOAN: Record<string, string> = {
  "Rẻ hơn thị trường": "bg-emerald-100 text-emerald-800 ring-emerald-600/20",
  "Hợp lý": "bg-slate-100 text-slate-700 ring-slate-500/20",
  "Cao hơn thị trường": "bg-rose-100 text-rose-800 ring-rose-600/20",
};

export const LOI_VAO: Record<number, string> = {
  1: "Hẻm nhỏ (xe máy)",
  2: "Hẻm xe hơi",
  3: "Hẻm xe tải / đường nội bộ",
  4: "Mặt tiền đường nhỏ",
  5: "Mặt tiền đường lớn",
};
