import { so } from "@/lib/format";

// Bảng hiển thị danh sách bản ghi (khóa = tiêu đề cột), số tự định dạng kiểu Việt Nam
export function Bang({ dong, an = [] }: { dong: Record<string, unknown>[]; an?: string[] }) {
  if (!dong?.length) return null;
  const cot = Object.keys(dong[0]).filter((c) => !an.includes(c));
  const o = (v: unknown) => {
    if (typeof v === "number") return so(v, Math.abs(v) >= 100 ? 0 : 1);
    if (typeof v === "string" && /^-?\d+\.\d{3,}$/.test(v)) return so(Number(v), 1);
    if (typeof v === "string" && v.startsWith("http")) return <a href={v} target="_blank" rel="noopener noreferrer" className="text-navy-700 underline">nguồn</a>;
    return String(v ?? "–");
  };
  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[560px] text-sm">
        <thead className="text-left text-xs uppercase text-slate-500"><tr>{cot.map((c) => <th key={c} className="py-2 pr-3 font-semibold">{c}</th>)}</tr></thead>
        <tbody className="divide-y divide-navy-50">
          {dong.map((d, i) => <tr key={i}>{cot.map((c) => <td key={c} className="py-2.5 pr-3 align-top">{o(d[c])}</td>)}</tr>)}
        </tbody>
      </table>
    </div>
  );
}
