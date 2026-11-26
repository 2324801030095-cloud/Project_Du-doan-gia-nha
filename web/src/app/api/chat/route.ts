import { NextResponse } from "next/server";
import { z } from "zod";
import { goiApi, qs, type KetQuaNha, type NhaPho, type TongQuan, type Trang } from "@/lib/api";

// Trợ lý: mô hình ngôn ngữ (Groq, chuẩn OpenAI) gọi CÔNG CỤ là API mô hình của đề tài, nên mọi con số đều do mô hình
// học máy của đề tài tính. Khóa GROQ_API_KEY chỉ nằm trên máy chủ (biến môi trường), không bao giờ gửi xuống trình duyệt.
// Không có khóa / lỗi mạng: trả lời bằng mô hình phân loại ý định (TF-IDF + Logistic Regression) của notebook trợ lý.

const GROQ = "https://api.groq.com/openai/v1/chat/completions";
const MO_HINH = ["openai/gpt-oss-120b", "openai/gpt-oss-20b"]; // hết hạn mức mô hình đầu thì dùng mô hình sau

const HE_THONG = `Bạn là trợ lý của đề tài "Dự đoán giá nhà Phú Hòa – Thủ Dầu Một" (môn Học máy). Trả lời tiếng Việt, ngắn gọn, thân thiện.
- Mọi con số về giá phải lấy từ công cụ (mô hình học máy của đề tài), không tự bịa. Nói rõ đây là GIÁ RAO ước lượng, không phải giá giao dịch.
- Khi định giá, gọi công cụ ngay với thông số đã có (mô hình tự xử lý ô thiếu), rồi nêu giá ước lượng và khoảng 80%. Chỉ hỏi lại khi không có diện tích nào.
- Với nhà phố, "80m2" không ghi rõ thì hiểu là DIỆN TÍCH ĐẤT (cách ghi của tin rao); "1 trệt 1 lầu" = 2 tầng; hẻm xe tải ≈ cap_loi_vao 3, hẻm xe hơi 2, hẻm nhỏ 1, mặt tiền 4–5.
- Mô hình nhà phố là Random Forest (tốt nhất trong 6 mô hình của môn học); căn hộ có mô hình riêng. Đề tài KHÔNG định giá lô đất trống: nếu được hỏi, nói rõ và gợi ý định giá căn nhà.
- Có thể gợi ý trang: /dinh-gia (định giá), /nha-pho (danh sách tin), /ban-do, /xu-huong, /mo-hinh.
- Dùng markdown đơn giản (in đậm, gạch đầu dòng). Không trả lời chủ đề ngoài bất động sản / đề tài.`;

const CONG_CU = [
  {
    type: "function",
    function: {
      name: "dinh_gia_nha_pho",
      description: "Định giá nhà phố / nhà trong hẻm ở Thủ Dầu Một (mặc định phường Phú Hòa) bằng Random Forest của đề tài.",
      parameters: {
        type: "object",
        properties: {
          dt_dat: { type: "number", description: "Diện tích đất m²" },
          ngang: { type: "number" }, dai: { type: "number" }, so_tang: { type: "number", description: "Số tầng (1 trệt 1 lầu = 2)" },
          dt_san: { type: "number", description: "Tổng diện tích sàn m²" }, phong_ngu: { type: "number" }, so_wc: { type: "number" },
          mat_tien_duong: { type: "integer", enum: [0, 1] },
          cap_loi_vao: { type: "number", description: "1 hẻm nhỏ, 2 hẻm xe hơi, 3 hẻm xe tải, 4 mặt tiền đường nhỏ, 5 mặt tiền đường lớn" },
          hem_rong: { type: "number", description: "Độ rộng hẻm/đường trước nhà (m)" },
          duong: { type: "string", description: "Tên đường nếu biết" },
          mo_ta: { type: "string", description: "Mô tả thêm (sổ riêng, nhà mới, khu dân cư...)" },
        },
        required: ["dt_dat"],
      },
    },
  },
  {
    type: "function",
    function: {
      name: "dinh_gia_can_ho",
      description: "Định giá căn hộ chung cư ở Bình Dương cũ.",
      parameters: {
        type: "object",
        properties: {
          dt_su_dung: { type: "number" }, du_an: { type: "string" }, phong_ngu: { type: "number" }, so_wc: { type: "number" },
          tang: { type: "number" }, so_hong: { type: "integer", enum: [0, 1] }, nha_o_xa_hoi: { type: "integer", enum: [0, 1] },
        },
        required: ["dt_su_dung"],
      },
    },
  },
  {
    type: "function",
    function: {
      name: "tim_nha_pho",
      description: "Tìm tin nhà phố Phú Hòa đang rao theo khoảng giá (tỷ), diện tích, chẩn đoán so với thị trường.",
      parameters: {
        type: "object",
        properties: {
          gia_min: { type: "number" }, gia_max: { type: "number" }, dt_min: { type: "number" }, dt_max: { type: "number" },
          chan_doan: { type: "string", enum: ["Rẻ hơn thị trường", "Hợp lý", "Cao hơn thị trường"] },
        },
      },
    },
  },
  { type: "function", function: { name: "thong_tin_mo_hinh", description: "Sai số, số căn, mô hình được chọn của đề tài.", parameters: { type: "object", properties: {} } } },
  { type: "function", function: { name: "xu_huong_gia", description: "Tín hiệu và kịch bản xu hướng giá theo kỳ hạn.", parameters: { type: "object", properties: {} } } },
];

async function chayCongCu(ten: string, thamSo: Record<string, unknown>): Promise<unknown> {
  const post = (duong: string) => goiApi(duong, { method: "POST", body: JSON.stringify(thamSo) });
  switch (ten) {
    case "dinh_gia_nha_pho": {
      const k = await goiApi<KetQuaNha>("/dinh-gia/nha-pho", { method: "POST", body: JSON.stringify(thamSo) });
      return { ...k, giai_thich: k.giai_thich?.nhom.slice(0, 4) };
    }
    case "dinh_gia_can_ho": return post("/dinh-gia/can-ho");
    case "tim_nha_pho": {
      const t = await goiApi<Trang<NhaPho>>("/nha-pho" + qs({ ...(thamSo as Record<string, string>), so_dong: 5 }));
      return { tong: t.tong, tin: t.ket_qua.map((x) => ({ ma: x.id, tieu_de: x.t, gia_rao_ty: x.g, dt: x.dt, gia_uoc_luong_ty: x.ai_full, chan_doan: x.chan_doan, link: `/nha-pho/${x.id}` })) };
    }
    case "thong_tin_mo_hinh": {
      const t = await goiApi<TongQuan>("/tong-quan");
      return { so_lieu: t.so_lieu, bang: t.bang_mo_hinh };
    }
    case "xu_huong_gia": {
      const t = await goiApi<Record<string, unknown>>("/xu-huong");
      return { ghi_chu: t.ghi_chu, tin_hieu: t.tin_hieu, du_bao: t.du_bao, ngay: t.ngay_du_lieu };
    }
  }
  throw new Error("Công cụ không tồn tại: " + ten);
}

type TinNhan = { role: "system" | "user" | "assistant" | "tool"; content: string | null; tool_calls?: { id: string; function: { name: string; arguments: string } }[]; tool_call_id?: string };

async function goiGroq(khoa: string, tinNhan: TinNhan[]) {
  for (const model of MO_HINH) {
    const r = await fetch(GROQ, {
      method: "POST",
      headers: { authorization: `Bearer ${khoa}`, "content-type": "application/json" },
      body: JSON.stringify({ model, messages: tinNhan, tools: CONG_CU, tool_choice: "auto", temperature: 0.3, max_tokens: 1200 }),
    });
    if (r.status === 429) continue; // hết hạn mức gói miễn phí của mô hình này: thử mô hình kế
    if (!r.ok) throw new Error(`Groq ${r.status}: ${(await r.text()).slice(0, 200)}`);
    const j = await r.json();
    return { message: j.choices[0].message as TinNhan, model };
  }
  throw new Error("Groq: tất cả mô hình đang hết hạn mức, thử lại sau ít phút");
}

const Yeu = z.object({ messages: z.array(z.object({ role: z.enum(["user", "assistant"]), content: z.string().max(4000) })).min(1).max(30) });

const TRA_LOI_OFFLINE: Record<string, string> = {
  chao: "Chào bạn! Mình giúp định giá nhà phố, căn hộ, đất ở Thủ Dầu Một và tìm tin đang rao. Bạn muốn bắt đầu từ đâu?",
  cam_on: "Không có gì! Cần định giá thêm căn nào cứ hỏi nhé.",
  gioi_thieu: "Đây là web của đề tài **Dự đoán giá nhà Phú Hòa** (môn Học máy): mô hình học trên tin rao thật, cho giá ước lượng, khoảng 80% và chẩn đoán rẻ / hợp lý / cao.",
  dinh_gia: "Bạn có thể định giá ngay ở trang **[Định giá](/dinh-gia)**: nhập diện tích, số tầng, lối vào… mô hình Random Forest trả giá ước lượng và khoảng 80%.",
  loi_vao: "Lối vào ảnh hưởng nhiều tới giá (mặt tiền > hẻm xe hơi > hẻm nhỏ). Thử đổi mục *Lối vào* ở trang **[Định giá](/dinh-gia)** để xem giá thay đổi.",
  tim: "Xem các tin đang rao ở **[Nhà phố Phú Hòa](/nha-pho)**, lọc theo giá, diện tích và chẩn đoán *rẻ hơn thị trường*.",
  phuong: "Đơn giá theo khu vực xem trên **[Bản đồ](/ban-do)**.",
  xu_huong: "Xu hướng giá theo kỳ hạn ở trang **[Xu hướng](/xu-huong)** (kịch bản có điều kiện, chưa đủ dữ liệu để kiểm định lùi).",
  du_an: "Định giá căn hộ theo dự án ở **[Định giá → Căn hộ](/dinh-gia?loai=can-ho)**, danh sách ở **[Căn hộ](/can-ho)**.",
  faq_noxh: "Nhà ở xã hội được tính riêng trong mô hình căn hộ: chọn *Nhà ở xã hội* ở **[Định giá → Căn hộ](/dinh-gia?loai=can-ho)**.",
  dat: "Đề tài định giá **nhà ở** (nhà + đất, căn hộ), không định giá lô đất trống. Bạn có thể **[định giá một căn nhà](/dinh-gia)**.",
  thue: "Mỗi kết quả định giá có kèm **giá thuê ước tính** và tỷ suất cho thuê (từ tin cho thuê thật).",
  faq_mo_hinh: "Mô hình nhà phố là **Random Forest**, tốt nhất trong 6 mô hình của môn học. Chi tiết ở **[Mô hình](/mo-hinh)**.",
  faq_du_lieu: "Dữ liệu là **tin rao thật** từ Chợ Tốt, alonhadat, guland (đã ẩn danh), cập nhật định kỳ. Xem **[Mô hình](/mo-hinh)**.",
  faq_khoang: "**Khoảng 80%**: khoảng giá chứa giá rao thật của khoảng 80% số căn (kiểm chứng trên tập test).",
  faq_luu_y: "Lưu ý: đây là **giá rao ước lượng**, không phải giá giao dịch; luôn kiểm tra pháp lý và hiện trạng thực tế.",
  faq_phap_ly: "Pháp lý (sổ riêng / sổ chung) có trong mô hình qua mô tả tin; hãy ghi \"sổ riêng\" vào ô mô tả khi định giá.",
  faq_thuong_luong: "Giá rao thường có phần thương lượng; căn bị chẩn đoán *cao hơn thị trường* là ứng viên để trả giá.",
  ngoai_pham_vi: "Mình chỉ hỗ trợ về giá nhà đất Thủ Dầu Một và đề tài này thôi nhé.",
};

// Giới hạn tần suất đơn giản theo IP (bộ nhớ của tiến trình): mỗi IP tối đa 20 câu hỏi / phút
const LAN_GOI = new Map<string, number[]>();
function quaTanSuat(req: Request) {
  const ip = req.headers.get("x-forwarded-for")?.split(",")[0].trim() || "local";
  const nay = Date.now(), ds = (LAN_GOI.get(ip) ?? []).filter((t) => nay - t < 60_000);
  ds.push(nay); LAN_GOI.set(ip, ds);
  return ds.length > 20;
}

export async function POST(req: Request) {
  if (quaTanSuat(req)) return NextResponse.json({ loi: "Bạn hỏi quá nhanh, thử lại sau ít giây." }, { status: 429 });
  const p = Yeu.safeParse(await req.json().catch(() => null));
  if (!p.success) return NextResponse.json({ loi: "Tin nhắn không hợp lệ" }, { status: 400 });
  const lichSu = p.data.messages.slice(-12);
  const cauCuoi = lichSu[lichSu.length - 1].content;
  const khoa = process.env.GROQ_API_KEY;
  const congCuDaDung: string[] = [];

  if (khoa) {
    try {
      const tn: TinNhan[] = [{ role: "system", content: HE_THONG }, ...lichSu];
      for (let buoc = 0; buoc < 5; buoc++) {
        const { message, model } = await goiGroq(khoa, tn);
        tn.push({ role: "assistant", content: message.content ?? "", tool_calls: message.tool_calls });
        if (!message.tool_calls?.length) return NextResponse.json({ tra_loi: message.content, che_do: "ai", mo_hinh: model, cong_cu: congCuDaDung });
        for (const tc of message.tool_calls) {
          congCuDaDung.push(tc.function.name);
          let kq: unknown;
          try {
            kq = await chayCongCu(tc.function.name, JSON.parse(tc.function.arguments || "{}"));
          } catch (e) {
            kq = { loi: e instanceof Error ? e.message : String(e) };
          }
          tn.push({ role: "tool", tool_call_id: tc.id, content: JSON.stringify(kq).slice(0, 6000) });
        }
      }
    } catch (e) {
      console.error("chat AI lỗi, chuyển sang ngoại tuyến:", e);
    }
  }
  // Ngoại tuyến: mô hình ý định của đề tài
  try {
    const y = await goiApi<{ y_dinh: string; xac_suat: number; chac_chan: boolean }>("/tro-ly/y-dinh", { method: "POST", body: JSON.stringify({ cau: cauCuoi }) });
    const traLoi = (y.chac_chan && TRA_LOI_OFFLINE[y.y_dinh]) ||
      "Mình chưa chắc bạn muốn hỏi gì. Bạn có thể: **[định giá một căn](/dinh-gia)**, **[xem tin đang rao](/nha-pho)**, **[xem xu hướng](/xu-huong)** hoặc **[tìm hiểu mô hình](/mo-hinh)**.";
    return NextResponse.json({ tra_loi: traLoi, che_do: "ngoai_tuyen", y_dinh: y });
  } catch {
    return NextResponse.json({ loi: "Trợ lý tạm thời không phản hồi" }, { status: 502 });
  }
}
