// IntelAI brand mark — isometric cube (Deep Blue → Cyan), themeable SVG.
// Mirrors logo_intelai.png so the in-app mark stays crisp on any dark surface.
export function CubeMark({ size = 36, glow = true, className = '' }) {
  const gid = 'im' + size
  return (
    <svg width={size} height={size} viewBox="0 0 40 40" fill="none" className={className}
         style={glow ? { filter: 'drop-shadow(0 4px 14px rgba(34,211,238,.45))' } : undefined}
         role="img" aria-label="IntelAI">
      <defs>
        <linearGradient id={`${gid}a`} x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#6366f1" /><stop offset=".5" stopColor="#2563eb" /><stop offset="1" stopColor="#22d3ee" />
        </linearGradient>
        <linearGradient id={`${gid}b`} x1="0" y1="1" x2="1" y2="0">
          <stop offset="0" stopColor="#4f46e5" /><stop offset="1" stopColor="#22d3ee" />
        </linearGradient>
      </defs>
      {/* isometric cube hexagon */}
      <path d="M20 3.4 L33.3 11 V26 L20 33.6 L6.7 26 V11 Z" stroke={`url(#${gid}a)`} strokeWidth="2.2" strokeLinejoin="round" />
      {/* internal isometric edges */}
      <path d="M20 3.4 V18 M20 18 L6.7 11 M20 18 L33.3 11" stroke={`url(#${gid}a)`} strokeWidth="1.3" opacity=".45" strokeLinejoin="round" />
      {/* up arrow — "intelligence rising" */}
      <path d="M20 27 V13.4 M14.4 19 L20 13.4 L25.6 19" stroke={`url(#${gid}b)`} strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

export default CubeMark
