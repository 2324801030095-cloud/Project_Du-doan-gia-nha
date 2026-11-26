"use client";
import { Area, CartesianGrid, ComposedChart, Line, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

// Kịch bản xu hướng: vùng = biên độ thấp…cao theo kỳ hạn (%), đường = điểm giữa
export function BieuDoKichBan({ du_lieu }: { du_lieu: { thang: number; lo: number; hi: number }[] }) {
  const d = [{ thang: 0, lo: 0, hi: 0 }, ...du_lieu].map((x) => ({ ten: x.thang === 0 ? "Nay" : `${x.thang} th`, vung: [x.lo, x.hi] as [number, number], giua: (x.lo + x.hi) / 2 }));
  return (
    <ResponsiveContainer width="100%" height={300}>
      <ComposedChart data={d} margin={{ top: 10, right: 16, left: -10, bottom: 0 }}>
        <CartesianGrid stroke="#e1e8f3" strokeDasharray="3 3" />
        <XAxis dataKey="ten" tick={{ fontSize: 12 }} />
        <YAxis tickFormatter={(v) => `${v}%`} tick={{ fontSize: 12 }} />
        <Tooltip formatter={(v) => (Array.isArray(v) ? `${Number(v[0]).toFixed(1)}% … ${Number(v[1]).toFixed(1)}%` : `${Number(v).toFixed(1)}%`)} />
        <Area dataKey="vung" name="Biên độ" stroke="none" fill="#c99a3b" fillOpacity={0.25} />
        <Line dataKey="giua" name="Điểm giữa" stroke="#22385e" strokeWidth={2} dot />
      </ComposedChart>
    </ResponsiveContainer>
  );
}
