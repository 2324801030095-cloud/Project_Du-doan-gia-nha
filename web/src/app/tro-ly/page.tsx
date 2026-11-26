import type { Metadata } from "next";
import { connection } from "next/server";
import { KhungChat } from "@/components/khung-chat";

export const metadata: Metadata = { title: "Trợ lý" };

export default async function Page() {
  await connection(); // đọc biến môi trường lúc chạy (không phải lúc build)
  const coAI = Boolean(process.env.GROQ_API_KEY);
  return (
    <div className="mx-auto max-w-3xl space-y-4">
      <header>
        <h1 className="text-3xl font-bold">Trợ lý hỏi đáp</h1>
        <p className="mt-2 text-slate-600">
          {coAI
            ? "Mô hình ngôn ngữ (Groq) hiểu câu hỏi tự nhiên và gọi chính mô hình định giá của đề tài để trả lời, nên con số là của mô hình học máy."
            : "Chưa cấu hình khóa AI trên máy chủ: trợ lý dùng mô hình phân loại ý định của đề tài (TF-IDF + Logistic Regression) để hướng dẫn."}
        </p>
      </header>
      <KhungChat coAI={coAI} />
    </div>
  );
}
