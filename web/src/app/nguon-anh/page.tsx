import type { Metadata } from "next";
import Image from "next/image";
import nguon from "@/lib/nguon-anh.json";

export const metadata: Metadata = { title: "Nguồn ảnh & giấy phép" };

export default function Page() {
  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-3xl font-bold">Nguồn ảnh & giấy phép</h1>
        <p className="mt-2 max-w-3xl text-slate-600">
          Ảnh nhà trên các tin rao là <b>ảnh minh họa</b>, chọn theo số tầng và loại lối vào, <b>không phải ảnh của căn được rao</b>
          (ảnh thật của tin thuộc bản quyền người đăng; xem bằng nút <i>Tin gốc</i>). Tất cả ảnh lấy từ Wikimedia Commons và Openverse theo
          giấy phép Creative Commons hoặc phạm vi công cộng; ảnh có ghi “đã cắt” được cắt khung, không chỉnh nội dung.
        </p>
      </header>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {nguon.map((x) => (
          <figure key={x.key} className="the overflow-hidden">
            <div className="relative aspect-[16/10] bg-navy-50">
              <Image src={`/img/${x.key}.jpg`} alt={x.title} fill sizes="(min-width: 1024px) 33vw, 50vw" className="object-cover" />
            </div>
            <figcaption className="p-4 text-sm">
              <p className="line-clamp-1 font-medium">{x.title}</p>
              <p className="text-slate-500">
                {x.author} · {x.license}{x.cropped ? " · đã cắt" : ""} ·{" "}
                <a href={x.source} target="_blank" rel="noopener noreferrer" className="text-navy-700 underline">{x.site}</a>
              </p>
            </figcaption>
          </figure>
        ))}
      </div>
    </div>
  );
}
