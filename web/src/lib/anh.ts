// Ảnh MINH HỌA (không phải ảnh thật của tin rao – ảnh thật thuộc bản quyền người đăng):
// ảnh giấy phép Creative Commons / công cộng (web/src/lib/nguon-anh.json), chọn theo số tầng và lối vào,
// cố định theo mã tin để mỗi lần mở cùng một tin thấy cùng ảnh. Cách chọn giống bản tĩnh (demo/).
const NGOAI: Record<string, string[]> = {
  "1": ["h1-b", "h1-a", "in-living-c"], "1.5": ["h1-a", "h1-b", "in-living-a"], "2": ["h2-a", "h2-b", "h2-c", "h3-a"],
  "3": ["h3-a", "h3-b", "h3-c", "h4-a", "h4-b"], "4": ["h4-a", "h4-b", "h4-c"], x: ["h2-a", "h3-b", "h2-c", "h4-a"],
};
const TRONG = ["in-living-a", "in-living-b", "in-living-c", "in-bed", "in-kitchen-a", "in-kitchen-b"];
const KHU = { can_ho: ["area-towers", "aerial"] };

// Băm FNV-1a mã tin -> số nguyên: cùng mã tin luôn ra cùng ảnh
const bam = (id: string) => {
  let h = 2166136261;
  for (const c of id) h = Math.imul(h ^ c.charCodeAt(0), 16777619);
  return h >>> 0;
};
const duong = (k: string) => `/img/${k}.jpg`;

/** 3 ảnh minh họa cho một tin nhà phố: 1 ảnh ngoại thất theo số tầng / lối vào (mặt tiền 2 tầng trở lên dùng ảnh nhà phố lớn) + 2 ảnh nội thất. */
export function anhNhaPho(id: string, soTang: number | null, loiVao: number | null): string[] {
  const nhom = loiVao === 5 && soTang && soTang >= 2 ? NGOAI["4"] : (soTang ? NGOAI[String(Math.min(soTang, 4))] : undefined) ?? NGOAI.x;
  const h = bam(id), ra = [nhom[h % nhom.length]];
  for (let k = 0; ra.length < 3 && k < 12; k++) {
    const c = TRONG[(h + k * 3 + Math.floor(k / 2)) % TRONG.length];
    if (!ra.includes(c)) ra.push(c);
  }
  return ra.map(duong);
}

/** Ảnh minh họa khu vực cho căn hộ. */
export function anhKhuVuc(loai: "can_ho", id: string): string {
  const ds = KHU[loai];
  return duong(ds[bam(id) % ds.length]);
}
