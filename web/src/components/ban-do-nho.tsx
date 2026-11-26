"use client";
import dynamic from "next/dynamic";
import type { Diem } from "./ban-do-leaflet";

const BanDo = dynamic(() => import("./ban-do-leaflet"), { ssr: false, loading: () => <div className="h-full animate-pulse rounded-2xl bg-navy-50" /> });

export function BanDoNho({ lat, lon, nhan }: { lat: number; lon: number; nhan: string }) {
  return (
    <div style={{ height: 260 }}>
      <BanDo diem={[{ lat, lon, mau: "#c99a3b", ban_kinh: 10, tieu_de: nhan, dong: ["Vị trí gần đúng (theo tọa độ trong tin)"] }]} tam={[lat, lon]} zoom={15} cao={260} />
    </div>
  );
}

export function BanDoLon({ diem, cao = 600 }: { diem: Diem[]; cao?: number }) {
  return (
    <div style={{ height: cao }}>
      <BanDo diem={diem} tam={[10.99, 106.66]} zoom={12} cao={cao} />
    </div>
  );
}
