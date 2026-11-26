import type { Metadata } from "next";
import { FormDinhGia } from "@/components/form-dinh-gia";
import { goiApi, type DanhMuc } from "@/lib/api";
import { layPhien } from "@/lib/session";

export const metadata: Metadata = { title: "Định giá" };

export default async function Page(props: PageProps<"/dinh-gia">) {
  const { loai } = (await props.searchParams) as { loai?: string };
  const [dm, phien] = await Promise.all([goiApi<DanhMuc>("/danh-muc"), layPhien()]);
  return (
    <div className="space-y-5">
      <header>
        <h1 className="text-3xl font-bold">Định giá bằng mô hình học máy</h1>
        <p className="mt-2 max-w-3xl text-slate-600">
          Nhập thông số bạn biết, ô nào không biết cứ để trống. Kết quả do mô hình của đề tài tính trên máy chủ, kèm <b>khoảng 80%</b> đã kiểm
          chứng trên tập test.{phien ? " Mỗi lần định giá được lưu vào lịch sử tài khoản của bạn." : " Đăng nhập để lưu lịch sử định giá."}
        </p>
      </header>
      <FormDinhGia danhMuc={dm} loaiBanDau={loai === "can-ho" || loai === "dat" ? loai : "nha-pho"} />
    </div>
  );
}
