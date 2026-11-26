"use client";
import { LoaderCircle, Send, Sparkles } from "lucide-react";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";

type TinNhan = { role: "user" | "assistant"; content: string; phu?: string };

const GOI_Y = [
  "Nhà 80m² 1 trệt 1 lầu hẻm xe hơi ở Phú Hòa giá bao nhiêu?",
  "Tìm nhà dưới 4 tỷ rẻ hơn thị trường",
  "Căn hộ 2PN 68m² Happy One Central giá bao nhiêu?",
  "Mô hình của đề tài sai số bao nhiêu?",
];

// Markdown tối giản và an toàn: chỉ in đậm, nghiêng, gạch đầu dòng, link nội bộ / https. Không chèn HTML thô.
function Md({ chu }: { chu: string }) {
  const dong = chu.split("\n");
  const inline = (s: string, k: number) => {
    const phan: React.ReactNode[] = [];
    const re = /\*\*\[([^\]]+)\]\(([^)]+)\)\*\*|\[([^\]]+)\]\(([^)]+)\)|\*\*([^*]+)\*\*|\*([^*]+)\*/g;
    let i = 0, m: RegExpExecArray | null;
    while ((m = re.exec(s))) {
      if (m.index > i) phan.push(s.slice(i, m.index));
      const ten = m[1] ?? m[3], href = m[2] ?? m[4];
      if (ten && href) {
        const ok = href.startsWith("/") || href.startsWith("https://");
        phan.push(ok ? <Link key={`${k}-${m.index}`} href={href} className="font-semibold text-navy-700 underline">{ten}</Link> : ten);
      } else if (m[5]) phan.push(<b key={`${k}-${m.index}`}>{m[5]}</b>);
      else if (m[6]) phan.push(<i key={`${k}-${m.index}`}>{m[6]}</i>);
      i = m.index + m[0].length;
    }
    phan.push(s.slice(i));
    return phan;
  };
  return (
    <div className="space-y-1.5">
      {dong.map((d, k) => {
        const t = d.trim();
        if (!t) return null;
        if (/^[-*•]\s/.test(t)) return <p key={k} className="pl-4 -indent-3">• {inline(t.replace(/^[-*•]\s/, ""), k)}</p>;
        if (/^\|/.test(t)) return <p key={k} className="font-mono text-xs">{t}</p>;
        return <p key={k}>{inline(t.replace(/^#+\s*/, ""), k)}</p>;
      })}
    </div>
  );
}

export function KhungChat({ coAI }: { coAI: boolean }) {
  const [ds, setDs] = useState<TinNhan[]>([{ role: "assistant", content: "Chào bạn! Mình giúp **định giá**, **tìm nhà đang rao** và giải thích **mô hình** của đề tài. Hỏi gì cũng được nhé." }]);
  const [cau, setCau] = useState("");
  const [dang, setDang] = useState(false);
  const cuoi = useRef<HTMLDivElement>(null);
  useEffect(() => cuoi.current?.scrollIntoView({ behavior: "smooth", block: "end" }), [ds, dang]);

  async function gui(noiDung: string) {
    const q = noiDung.trim();
    if (!q || dang) return;
    const moi: TinNhan[] = [...ds, { role: "user", content: q }];
    setDs(moi); setCau(""); setDang(true);
    try {
      const r = await fetch("/api/chat", {
        method: "POST", headers: { "content-type": "application/json" },
        body: JSON.stringify({ messages: moi.slice(1).slice(-20).map(({ role, content }) => ({ role, content })) }),
      });
      const j = await r.json();
      const phu = j.che_do === "ai" ? `AI · ${j.mo_hinh}${j.cong_cu?.length ? ` · công cụ: ${j.cong_cu.join(", ")}` : ""}` : j.che_do === "ngoai_tuyen" ? "Trợ lý ngoại tuyến (mô hình ý định)" : undefined;
      setDs([...moi, { role: "assistant", content: r.ok ? j.tra_loi : (j.loi ?? "Có lỗi, thử lại."), phu }]);
    } catch {
      setDs([...moi, { role: "assistant", content: "Mất kết nối tới máy chủ, thử lại sau." }]);
    } finally {
      setDang(false);
    }
  }

  return (
    <div className="the flex h-[70vh] flex-col">
      <div className="flex-1 space-y-4 overflow-y-auto p-5" aria-live="polite">
        {ds.map((m, i) => (
          <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
            <div className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${m.role === "user" ? "bg-navy-800 text-white" : "bg-navy-50 text-slate-800"}`}>
              {m.role === "user" ? m.content : <Md chu={m.content} />}
              {m.phu && <p className="mt-2 text-[11px] text-slate-400">{m.phu}</p>}
            </div>
          </div>
        ))}
        {dang && <div className="flex items-center gap-2 text-sm text-slate-500"><LoaderCircle size={16} className="animate-spin" /> Đang trả lời…</div>}
        <div ref={cuoi} />
      </div>
      {ds.length <= 1 && (
        <div className="flex flex-wrap gap-2 px-5 pb-3">
          {GOI_Y.map((g) => <button key={g} onClick={() => gui(g)} className="rounded-full border border-navy-200 px-3 py-1.5 text-xs text-navy-700 hover:bg-navy-50">{g}</button>)}
        </div>
      )}
      <form onSubmit={(e) => { e.preventDefault(); gui(cau); }} className="flex gap-2 border-t border-navy-100 p-3">
        <span className="hidden items-center pl-2 text-gold-500 sm:flex" title={coAI ? "Chế độ AI" : "Ngoại tuyến"}><Sparkles size={18} /></span>
        <input value={cau} onChange={(e) => setCau(e.target.value)} maxLength={500} placeholder="Hỏi về giá nhà, căn hộ, đất…" className="o-nhap" aria-label="Câu hỏi" />
        <button className="nut-chinh" disabled={dang || !cau.trim()} aria-label="Gửi"><Send size={16} /></button>
      </form>
    </div>
  );
}
