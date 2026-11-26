import type { Metadata } from "next";
import { Bang } from "@/components/bang";
import { BieuDoKichBan } from "@/components/bieu-do-xu-huong";
import { goiApi } from "@/lib/api";

export const metadata: Metadata = { title: "Xu hướng giá" };

type DuBao = { "Kỳ hạn": string; "Xu hướng giá rao nhà phố Phú Hòa / TDM": string; "Biên độ ước tính": string; "Độ tin cậy": string; thang: number };
type XuHuong = {
  ghi_chu: string; ngay_du_lieu: string; can_chuan: string; du_bao: DuBao[]; tin_hieu: Record<string, unknown>[];
  gia_can_chuan_theo_phuong: Record<string, unknown>[]; vi_tri_trong_phu_hoa: Record<string, unknown>[]; boi_canh_cong_bo: Record<string, unknown>[];
};

// "-0.8% … +0.3%" -> [-0.8, 0.3]
const bien = (s: string) => (s.match(/[-+−]?\d+(?:[.,]\d+)?/g) ?? []).map((x) => Number(x.replace("−", "-").replace(",", ".")));

export default async function Page() {
  const t = await goiApi<XuHuong>("/xu-huong");
  const ks = t.du_bao.map((d) => ({ thang: d.thang, lo: bien(d["Biên độ ước tính"])[0], hi: bien(d["Biên độ ước tính"])[1] })).filter((x) => Number.isFinite(x.lo) && Number.isFinite(x.hi));
  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-3xl font-bold">Xu hướng giá rao</h1>
        <p className="mt-2 max-w-3xl text-slate-600">{t.ghi_chu}</p>
        <p className="mt-2 rounded-xl bg-amber-50 p-3 text-sm text-amber-800">
          Đây là <b>kịch bản có điều kiện</b> dựng từ tín hiệu đo được, chưa kiểm định lùi được vì dữ liệu theo thời gian còn ngắn. Trên 12 tháng chỉ mang tính minh họa.
        </p>
      </header>
      <section className="the p-6">
        <h2 className="mb-2 text-xl font-semibold">Kịch bản theo kỳ hạn (giá rao nhà phố Phú Hòa / TDM)</h2>
        <BieuDoKichBan du_lieu={ks} />
        <div className="mt-4"><Bang dong={t.du_bao as unknown as Record<string, unknown>[]} an={["thang"]} /></div>
      </section>
      <section className="the p-6">
        <h2 className="mb-3 text-xl font-semibold">Tín hiệu đo được</h2>
        <Bang dong={t.tin_hieu} />
      </section>
      <div className="grid gap-6 lg:grid-cols-2">
        <section className="the p-6">
          <h2 className="mb-1 text-xl font-semibold">Giá căn chuẩn theo phường</h2>
          <p className="mb-3 text-sm text-slate-500">{t.can_chuan}</p>
          <Bang dong={t.gia_can_chuan_theo_phuong} />
        </section>
        <section className="the p-6">
          <h2 className="mb-3 text-xl font-semibold">Vị trí trong Phú Hòa</h2>
          <Bang dong={t.vi_tri_trong_phu_hoa} />
        </section>
      </div>
      <section className="the p-6">
        <h2 className="mb-3 text-xl font-semibold">Bối cảnh từ số liệu công bố</h2>
        <Bang dong={t.boi_canh_cong_bo} />
      </section>
    </div>
  );
}
