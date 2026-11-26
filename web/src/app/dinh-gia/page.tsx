import type { Metadata } from "next";
import { FormDinhGia } from "@/components/form-dinh-gia";
import { goiApi, type DanhMuc, type TongQuan } from "@/lib/api";
import { layPhien } from "@/lib/session";

export const metadata: Metadata = { title: "Định giá" };

export default async function Page(props: PageProps<"/dinh-gia">) {
  const { loai } = (await props.searchParams) as { loai?: string };
  const [dm, tq, phien] = await Promise.all([goiApi<DanhMuc>("/danh-muc"), goiApi<TongQuan>("/tong-quan"), layPhien()]);
  return (
    <div className="space-y-5">
      <header>
        <h1 className="text-3xl font-bold">Định giá bằng mô hình học máy</h1>
        <p className="mt-2 max-w-3xl text-slate-600">
          Nhập thông số bạn biết, ô nào không biết cứ để trống. Kết quả là <b>giá rao bán ước tính</b> do mô hình của đề tài tính trên máy chủ, kèm <b>khoảng giá tham khảo 80%</b>
          (độ phủ thực tế đo trên tập test được ghi cạnh kết quả).{phien ? " Mỗi lần định giá được lưu vào lịch sử tài khoản của bạn." : " Đăng nhập để lưu lịch sử định giá."}
        </p>
      </header>
      <FormDinhGia danhMuc={dm} loaiBanDau={loai === "can-ho" ? "can-ho" : "nha-pho"} doPhu={tq.do_phu_test_80?.["test Phú Hòa"]} />
    </div>
  );
}
