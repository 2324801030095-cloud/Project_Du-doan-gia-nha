import type { Metadata } from "next";
import { Bang } from "@/components/bang";
import { goiApi, type TongQuan } from "@/lib/api";

export const metadata: Metadata = { title: "Mô hình" };

type Dong = Record<string, unknown> & { "Mô hình": string };
type DanhGia = { nha_pho: Record<string, Dong[] | string | unknown>; can_ho: Record<string, unknown> };

const COT = ["Mô hình", "MAPE (%)", "MAPE thấp (95%)", "MAPE cao (95%)", "MdAPE (%)", "Trong ±20% (%)", "R²", "Số căn"];
const gon = (ds: unknown) => ((ds as Dong[]) ?? []).map((d) => Object.fromEntries(COT.filter((c) => c in d).map((c) => [c, d[c]])));

const BUOC = [
  ["1. Thu thập", "Tin rao thật từ Chợ Tốt Nhà (API công khai), alonhadat, guland; ẩn danh người đăng; lưu ảnh chụp mỗi kỳ."],
  ["2. Tiền xử lý", "Hợp nhất nguồn, trích 21 từ khóa từ mô tả, xử lý thiếu, loại trùng, loại ngoại lai theo 15 căn lân cận, gom tin đăng lại."],
  ["3. Khám phá", "Phân phối giá, tương quan, phân cụm K-means theo vị trí và đơn giá."],
  ["4. Mô hình (Phần A)", "6 mô hình của môn học: hồi quy tuyến tính, cây quyết định, KNN, SVM, mạng nơ-ron MLP, Random Forest; chọn bằng kiểm định chéo theo nhóm → Random Forest."],
  ["5. Đánh giá (Phần B)", "Kiểm định chéo lặp 3 lần, khoảng tin cậy bootstrap, tập test giữ riêng, so với mô hình đối chứng LightGBM + giá khu vực."],
  ["6. Ứng dụng", "Khoảng giá 80% đã kiểm chứng độ phủ, chẩn đoán rẻ / hợp lý / cao từng tin, giải thích yếu tố, web này."],
];

export default async function Page() {
  const [dg, tq] = await Promise.all([goiApi<DanhGia>("/danh-gia"), goiApi<TongQuan>("/tong-quan")]);
  const n = dg.nha_pho;
  const s = tq.so_lieu;
  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-3xl font-bold">Mô hình và cách đánh giá</h1>
        <p className="mt-2 max-w-3xl text-slate-600">
          Mô hình nhà phố: <b>{String(n.ten_mo_hinh)}</b>, tốt nhất trong 6 mô hình của môn học. Mọi con số dưới đây đọc trực tiếp từ kết quả
          notebook (dữ liệu đến {s.NGAY}), không viết tay.
        </p>
      </header>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[["MAPE tập test Phú Hòa", `${s.TEST_MAPE}%`, `KTC 95%: ${s.TEST_LO}–${s.TEST_HI}% · ${s.TEST_N} căn`],
          ["MAPE kiểm định chéo Phú Hòa", `${s.T_MAPE}%`, `KTC 95%: ${s.T_LO}–${s.T_HI}%`],
          ["Baseline (đơn giá phường)", `${s.B_MAPE}%`, "Mốc tối thiểu phải vượt"],
          ["Dữ liệu sau làm sạch", `${s.N_ALL} căn`, `${s.N_RAW} tin thô · ${s.PH_ALL_N} căn Phú Hòa`]].map(([k, v, p]) => (
          <div key={k} className="the p-5"><p className="nhan">{k}</p><p className="text-2xl font-bold text-navy-900">{v}</p><p className="text-xs text-slate-500">{p}</p></div>
        ))}
      </div>
      <section className="the p-6">
        <h2 className="mb-4 text-xl font-semibold">Quy trình học máy</h2>
        <ol className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {BUOC.map(([t, m]) => <li key={t} className="rounded-xl bg-navy-50 p-4"><p className="font-semibold text-navy-900">{t}</p><p className="mt-1 text-sm text-slate-600">{m}</p></li>)}
        </ol>
      </section>
      <section className="the p-6">
        <h2 className="mb-1 text-xl font-semibold">Tập test giữ riêng – Phú Hòa (kết quả chính)</h2>
        <p className="mb-3 text-sm text-slate-500">Chấm một lần duy nhất trên các căn chưa dùng ở bước nào. Tập test nhỏ nên khoảng tin cậy rộng.</p>
        <Bang dong={gon(n.test_phu_hoa)} />
      </section>
      <div className="grid gap-6 lg:grid-cols-2">
        <section className="the p-6">
          <h2 className="mb-3 text-xl font-semibold">Tập test – toàn Thủ Dầu Một</h2>
          <Bang dong={gon(n.test_tdm)} />
        </section>
        <section className="the p-6">
          <h2 className="mb-3 text-xl font-semibold">Kiểm định chéo lặp – Phú Hòa</h2>
          <Bang dong={gon(n.kiem_dinh_cheo_phu_hoa)} />
        </section>
      </div>
      <section className="the p-6">
        <h2 className="mb-1 text-xl font-semibold">Mô hình cuối so với đối chứng ngoài bài giảng</h2>
        <p className="mb-3 text-sm text-slate-500">Chênh lệch sai số % trên cùng từng căn; khoảng tin cậy chứa 0 nghĩa là chưa có bằng chứng đối chứng tốt hơn.</p>
        <Bang dong={(n.chon_mo_hinh as Dong[]) ?? []} />
      </section>
      <section className="the p-6">
        <h2 className="mb-3 text-xl font-semibold">Mở rộng – căn hộ, tập test ({String(dg.can_ho.ten_mo_hinh)})</h2>
        <Bang dong={gon(dg.can_ho.test)} />
      </section>
      <section className="the p-6 text-sm text-slate-600">
        <h2 className="mb-2 text-xl font-semibold text-navy-900">Hạn chế cần biết</h2>
        <ul className="list-disc space-y-1 pl-5">
          <li>Mô hình ước lượng <b>giá rao</b>, không phải giá giao dịch công chứng.</li>
          <li>Phần lớn tin chỉ có vị trí tới tuyến đường hoặc phường; không có số nhà.</li>
          <li>Không có thông tin chất lượng xây dựng thật, chỉ đọc gián tiếp qua mô tả tin.</li>
          <li>Ô định giá dùng mô hình đầy đủ trên máy chủ; con số có thể khác vài % so với bản tĩnh chạy offline (dùng Ridge rút gọn).</li>
        </ul>
      </section>
    </div>
  );
}
