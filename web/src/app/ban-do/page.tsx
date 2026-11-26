import type { Metadata } from "next";
import { BanDoLon } from "@/components/ban-do-nho";
import type { Diem } from "@/components/ban-do-leaflet";
import { goiApi } from "@/lib/api";
import { so } from "@/lib/format";

export const metadata: Metadata = { title: "Bản đồ giá" };

type DuLieu = { diem: [number, number, number, string, number, string, string][]; toa_can_ho: { ten: string; ph: string; lat: number; lon: number; n: number; dg: number; g_tv: number }[] };
const LOAI: Record<string, { ten: string; mau: string; donVi: string }> = {
  nha: { ten: "Nhà phố", mau: "#22385e", donVi: "tỷ" },
  thue: { ten: "Cho thuê", mau: "#059669", donVi: "triệu/tháng" },
  can_ho: { ten: "Tòa căn hộ", mau: "#be123c", donVi: "tỷ" },
};

export default async function Page() {
  const d = await goiApi<DuLieu>("/ban-do");
  const diem: Diem[] = [
    ...d.diem.map(([lat, lon, dg, loai, gia, t, url]) => ({
      lat, lon, mau: LOAI[loai]?.mau ?? "#64748b", tieu_de: t, url,
      dong: [`${LOAI[loai]?.ten}: ${so(gia, 2)} ${LOAI[loai]?.donVi}`, `${so(dg)} ${loai === "thue" ? "nghìn/m²/tháng" : "triệu/m²"}`],
    })),
    ...d.toa_can_ho.map((t) => ({ lat: t.lat, lon: t.lon, mau: LOAI.can_ho.mau, ban_kinh: 7 + Math.min(t.n, 10), tieu_de: t.ten,
      dong: [`${t.n} căn đang rao · ${t.ph}`, `Đơn giá trung vị ${so(t.dg)} triệu/m²`, `Giá trung vị ${so(t.g_tv, 2)} tỷ`] })),
  ];
  return (
    <div className="space-y-4">
      <header>
        <h1 className="text-3xl font-bold">Bản đồ giá rao</h1>
        <p className="mt-2 text-slate-600">{so(diem.length, 0)} điểm có tọa độ chính xác (tọa độ riêng hoặc theo tuyến đường). Bấm vào điểm để xem giá.</p>
      </header>
      <div className="flex flex-wrap gap-4 text-sm">
        {Object.values(LOAI).map((l) => <span key={l.ten} className="flex items-center gap-2"><span className="size-3 rounded-full" style={{ background: l.mau }} />{l.ten}</span>)}
      </div>
      <div className="the p-2"><BanDoLon diem={diem} cao={640} /></div>
    </div>
  );
}
