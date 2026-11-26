import { phanTram } from "@/lib/format";

// Thanh đóng góp của từng nhóm yếu tố (log giá) -> % làm tăng (xanh) / giảm (đỏ) giá so với căn trung bình
export function GiaiThich({ nhom, chuThich }: { nhom: { nhom: string; log: number }[]; chuThich: string }) {
  const ds = [...nhom].sort((a, b) => Math.abs(b.log) - Math.abs(a.log));
  const lon = Math.max(...ds.map((x) => Math.abs(x.log)), 0.01);
  return (
    <div>
      <ul className="space-y-2.5">
        {ds.map((x) => {
          const p = (Math.exp(x.log) - 1) * 100, rong = (Math.abs(x.log) / lon) * 50, tang = x.log >= 0;
          return (
            <li key={x.nhom} className="grid grid-cols-[minmax(0,10rem)_1fr_3.5rem] items-center gap-3 text-sm sm:grid-cols-[minmax(0,16rem)_1fr_4rem]">
              <span className="truncate text-slate-700" title={x.nhom}>{x.nhom}</span>
              <span className="relative h-3 rounded-full bg-navy-50">
                <span className="absolute inset-y-0 left-1/2 w-px bg-navy-200" />
                <span className={`absolute inset-y-0 rounded-full ${tang ? "bg-emerald-500" : "bg-rose-500"}`}
                  style={tang ? { left: "50%", width: `${rong}%` } : { left: `${50 - rong}%`, width: `${rong}%` }} />
              </span>
              <span className={`text-right font-semibold tabular-nums ${tang ? "text-emerald-700" : "text-rose-700"}`}>{phanTram(p)}</span>
            </li>
          );
        })}
      </ul>
      <p className="mt-3 text-xs text-slate-500">{chuThich}</p>
    </div>
  );
}
