// Minh họa trang trí cho khung kết quả định giá: ngôi nhà, tờ tiền và đồng xu (SVG tự vẽ, không cần ảnh/GIF ngoài).
// Chuyển động bằng CSS (globals.css: .xu-troi, .xu-xoay, .tien-lac); tự tắt khi người dùng bật "giảm chuyển động".
export function MinhHoaTien({ dangTinh = false, className = "" }: { dangTinh?: boolean; className?: string }) {
  return (
    <svg viewBox="0 0 220 160" className={className} role="img" aria-label="Minh họa: ngôi nhà, tiền và đồng xu">
      <defs>
        <linearGradient id="vang" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#f3d27c" />
          <stop offset="1" stopColor="#c99a3b" />
        </linearGradient>
        <linearGradient id="xanh" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#6fcf97" />
          <stop offset="1" stopColor="#2f9e63" />
        </linearGradient>
      </defs>
      {/* bóng nền */}
      <ellipse cx="110" cy="146" rx="86" ry="9" fill="#12203a" opacity="0.12" />
      {/* ngôi nhà */}
      <g>
        <rect x="78" y="70" width="64" height="72" rx="4" fill="#ffffff" stroke="#22385e" strokeWidth="3" />
        <path d="M70 74 L110 40 L150 74" fill="none" stroke="#22385e" strokeWidth="5" strokeLinecap="round" strokeLinejoin="round" />
        <rect x="100" y="108" width="20" height="34" rx="2" fill="#c99a3b" />
        <rect x="86" y="84" width="14" height="13" rx="2" fill="#c3d0e6" />
        <rect x="120" y="84" width="14" height="13" rx="2" fill="#c3d0e6" />
      </g>
      {/* tờ tiền (lắc nhẹ) */}
      <g className={dangTinh ? "tien-lac nhanh" : "tien-lac"} style={{ transformOrigin: "40px 118px" }}>
        <rect x="8" y="100" width="64" height="36" rx="5" fill="url(#xanh)" stroke="#1f7a4b" strokeWidth="2" />
        <circle cx="40" cy="118" r="9" fill="none" stroke="#e8fff1" strokeWidth="2" />
        <text x="40" y="122" textAnchor="middle" fontSize="11" fontWeight="700" fill="#e8fff1">₫</text>
      </g>
      {/* chồng xu */}
      <g>
        {[0, 1, 2].map((i) => (
          <g key={i}>
            <ellipse cx="178" cy={136 - i * 9} rx="22" ry="7" fill="#a97c25" />
            <ellipse cx="178" cy={132 - i * 9} rx="22" ry="7" fill="url(#vang)" stroke="#a97c25" strokeWidth="1.5" />
          </g>
        ))}
      </g>
      {/* đồng xu bay */}
      <g className={dangTinh ? "xu-xoay" : "xu-troi"} style={{ transformOrigin: "176px 62px" }}>
        <circle cx="176" cy="62" r="16" fill="url(#vang)" stroke="#a97c25" strokeWidth="2" />
        <text x="176" y="67" textAnchor="middle" fontSize="15" fontWeight="800" fill="#7a5a18">₫</text>
      </g>
      <g className={dangTinh ? "xu-xoay cham" : "xu-troi tre"} style={{ transformOrigin: "42px 58px" }}>
        <circle cx="42" cy="58" r="11" fill="url(#vang)" stroke="#a97c25" strokeWidth="2" />
        <text x="42" y="62" textAnchor="middle" fontSize="11" fontWeight="800" fill="#7a5a18">₫</text>
      </g>
      {/* lấp lánh */}
      <g fill="#e2b75a" className="lap-lanh">
        <path d="M150 28 l3 7 7 3 -7 3 -3 7 -3 -7 -7 -3 7 -3z" />
        <path d="M60 24 l2 5 5 2 -5 2 -2 5 -2 -5 -5 -2 5 -2z" />
      </g>
    </svg>
  );
}
