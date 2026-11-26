"use client";
import "leaflet/dist/leaflet.css";
import { CircleMarker, MapContainer, Popup, TileLayer } from "react-leaflet";

export type Diem = { lat: number; lon: number; mau: string; ban_kinh?: number; tieu_de: string; dong: string[]; url?: string };

// Dùng CircleMarker (vẽ SVG) thay cho marker ảnh: không phụ thuộc file icon của Leaflet khi đóng gói
export default function BanDoLeaflet({ diem, tam, zoom, cao }: { diem: Diem[]; tam: [number, number]; zoom: number; cao: number }) {
  return (
    <MapContainer center={tam} zoom={zoom} style={{ height: cao, width: "100%" }} scrollWheelZoom={false} preferCanvas>
      <TileLayer attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      {diem.map((d, i) => (
        <CircleMarker key={i} center={[d.lat, d.lon]} radius={d.ban_kinh ?? 6} pathOptions={{ color: "#fff", weight: 1, fillColor: d.mau, fillOpacity: 0.85 }}>
          <Popup>
            <p style={{ fontWeight: 600, margin: 0 }}>{d.tieu_de}</p>
            {d.dong.map((x) => <p key={x} style={{ margin: "2px 0" }}>{x}</p>)}
            {d.url && <a href={d.url} target={d.url.startsWith("http") ? "_blank" : undefined} rel="noopener noreferrer">Xem tin →</a>}
          </Popup>
        </CircleMarker>
      ))}
    </MapContainer>
  );
}
