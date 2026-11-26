"use client";
import { Banknote, CalendarClock, ChartNoAxesColumn, Info, Ruler } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { so, ty } from "@/lib/format";
import { GiaiThich } from "./giai-thich";
import { MinhHoaTien } from "./minh-hoa-tien";
import { KhoangGia } from "./tin";

export type KetQua = {
  gia_ty: number; khoang_80_ty: [number, number]; khoang_50_ty?: [number, number]; don_gia_trieu_m2: number; mo_hinh: string;
  thue_trieu_thang?: number; ty_suat_pt?: number; giai_thich?: { nhom: { nhom: string; log: number }[] } | null;
  du_an_nhan_ra?: boolean; phuong_co_du_lieu?: boolean; don_gia_nen_phuong?: number; da_luu?: boolean;
};

// Số chạy dần từ 0 lên giá trị (0,8 giây); bỏ hiệu ứng nếu người dùng bật "giảm chuyển động"
function useChayDan(dich: number) {
  const [v, setV] = useState(0);
  useEffect(() => {
    const thoiGian = matchMedia("(prefers-reduced-motion: reduce)").matches ? 0 : 800;
    let khung = 0;
    const t0 = performance.now();
    const buoc = (t: number) => {
      const p = thoiGian ? Math.min(1, (t - t0) / thoiGian) : 1;
      setV(dich * (1 - Math.pow(1 - p, 3)));
      if (p < 1) khung = requestAnimationFrame(buoc);
    };
    khung = requestAnimationFrame(buoc);
    return () => cancelAnimationFrame(khung);
  }, [dich]);
  return v;
}

function O({ icon, nhan, children }: { icon: React.ReactNode; nhan: string; children: React.ReactNode }) {
  return (
    <div className="rounded-2xl border border-navy-100 bg-white p-5">
      <p className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-slate-500"><span className="text-gold-600">{icon}</span>{nhan}</p>
      <div className="mt-2">{children}</div>
    </div>
  );
}

export function KetQuaDinhGia({ kq, loi, dang }: { kq: KetQua | null; loi: string; dang: boolean }) {
  const khung = useRef<HTMLElement>(null);
  const gia = useChayDan(kq?.gia_ty ?? 0);
  // có kết quả mới: cuộn khung kết quả vào tầm nhìn
  useEffect(() => {
    if (kq || loi) khung.current?.scrollIntoView({ behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth", block: "start" });
  }, [kq, loi]);

  return (
    <section ref={khung} aria-live="polite" className="scroll-mt-24">
      {!kq && !loi && (
        <div className="the flex flex-col items-center gap-4 px-6 py-10 text-center sm:flex-row sm:text-left">
          <MinhHoaTien dangTinh={dang} className="h-32 w-44 shrink-0" />
          <div>
            <p className="text-lg font-semibold text-navy-900">{dang ? "Mô hình đang tính giá…" : "Kết quả định giá sẽ hiện ở đây"}</p>
            <p className="mt-1 text-slate-500">
              {dang ? "Random Forest đang duyệt 300 cây quyết định." : <>Nhập thông số ở trên rồi bấm <b>Định giá</b>: giá ước lượng, khoảng 80%, giá thuê và lý do vì sao.</>}
            </p>
          </div>
        </div>
      )}
      {loi && <p className="the border-rose-200 bg-rose-50 p-5 text-rose-700">{loi}</p>}
      {kq && (
        <div className="space-y-5">
          <div className="relative overflow-hidden rounded-3xl bg-navy-800 p-6 text-white sm:p-8">
            <div className="relative flex flex-col items-center gap-6 sm:flex-row">
              <div className="rounded-2xl bg-white/95 p-2 shadow-lg"><MinhHoaTien className="h-28 w-40" /></div>
              <div className="flex-1 text-center sm:text-left">
                <p className="text-sm font-semibold uppercase tracking-widest text-gold-400">Giá ước lượng</p>
                <p className="mt-1 text-5xl font-bold tabular-nums sm:text-6xl">{so(gia, gia >= 10 ? 1 : 2)} <span className="text-2xl font-semibold text-navy-100 sm:text-3xl">tỷ đồng</span></p>
                <p className="mt-2 text-navy-100">Khoảng 80%: <b className="text-white">{ty(kq.khoang_80_ty[0])} – {ty(kq.khoang_80_ty[1])}</b></p>
              </div>
              <div className="flex flex-wrap justify-center gap-2 sm:flex-col sm:items-end">
                <span className="rounded-full bg-white/10 px-3 py-1 text-sm">{so(kq.don_gia_trieu_m2)} triệu/m²</span>
                <span className="rounded-full bg-gold-500/20 px-3 py-1 text-sm text-gold-400">{kq.mo_hinh}</span>
              </div>
            </div>
          </div>

          <div className="grid gap-4 md:grid-cols-3">
            <O icon={<ChartNoAxesColumn size={16} />} nhan="Khoảng giá 80%">
              <p className="text-xl font-bold text-navy-900">{ty(kq.khoang_80_ty[0])} – {ty(kq.khoang_80_ty[1])}</p>
              <KhoangGia lo={kq.khoang_80_ty[0]} hi={kq.khoang_80_ty[1]} uoc={kq.gia_ty} />
              <p className="mt-2 text-xs text-slate-500">8/10 căn tương tự có giá rao nằm trong khoảng này (đã kiểm chứng trên tập test).</p>
            </O>
            <O icon={<Ruler size={16} />} nhan={kq.khoang_50_ty ? "Khoảng 50% (hẹp hơn)" : "Đơn giá"}>
              {kq.khoang_50_ty ? (
                <>
                  <p className="text-xl font-bold text-navy-900">{ty(kq.khoang_50_ty[0])} – {ty(kq.khoang_50_ty[1])}</p>
                  <p className="mt-2 text-xs text-slate-500">Một nửa số căn tương tự rơi vào khoảng này; dùng làm vùng thương lượng.</p>
                </>
              ) : (
                <>
                  <p className="text-xl font-bold text-navy-900">{so(kq.don_gia_trieu_m2)} triệu/m²</p>
                  {kq.don_gia_nen_phuong !== undefined && <p className="mt-2 text-xs text-slate-500">Đơn giá nền của phường: {so(kq.don_gia_nen_phuong)} triệu/m².</p>}
                </>
              )}
            </O>
            <O icon={kq.thue_trieu_thang !== undefined ? <Banknote size={16} /> : <CalendarClock size={16} />} nhan={kq.thue_trieu_thang !== undefined ? "Cho thuê ước tính" : "Dữ liệu"}>
              {kq.thue_trieu_thang !== undefined ? (
                <>
                  <p className="text-xl font-bold text-navy-900">{so(kq.thue_trieu_thang)} triệu/tháng</p>
                  <p className="mt-2 text-xs text-slate-500">Tỷ suất cho thuê {so(kq.ty_suat_pt)}%/năm, từ tin cho thuê thật cùng khu vực.</p>
                </>
              ) : (
                <p className="text-sm text-slate-600">Mô hình rút gọn cho đất, học trên tin rao đất thật ở Thủ Dầu Một.</p>
              )}
            </O>
          </div>

          {(kq.du_an_nhan_ra === false || kq.phuong_co_du_lieu === false) && (
            <p className="flex items-start gap-2 rounded-2xl bg-amber-50 p-4 text-sm text-amber-800">
              <Info size={16} className="mt-0.5 shrink-0" />
              {kq.du_an_nhan_ra === false ? "Không nhận ra dự án: mô hình dùng mặt bằng giá của phường." : "Phường ít dữ liệu: dùng mặt bằng giá của quận."}
            </p>
          )}

          {kq.giai_thich && (
            <div className="the p-6">
              <h2 className="mb-4 text-lg font-semibold">Yếu tố làm giá cao / thấp</h2>
              <GiaiThich nhom={kq.giai_thich.nhom} chuThich="So với căn trung bình trong dữ liệu (đóng góp theo đường đi trên cây của Random Forest)." />
            </div>
          )}
          <p className="text-center text-xs text-slate-400">
            {kq.da_luu ? "Đã lưu vào lịch sử định giá của bạn." : "Đăng nhập để lưu kết quả."} Đây là giá rao ước lượng, không phải giá giao dịch.
          </p>
        </div>
      )}
    </section>
  );
}
