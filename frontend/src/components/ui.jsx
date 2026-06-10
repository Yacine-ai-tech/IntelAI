import { useNavigate } from 'react-router-dom'
import {
  AreaChart, Area, BarChart, Bar, LineChart, Line, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer, Cell,
} from 'recharts'
import { Sparkles, ArrowUpRight, ArrowDownRight } from 'lucide-react'

// ── formatters ───────────────────────────────────────────────
export const fmtNum = (v) => {
  if (v == null || isNaN(v)) return '—'
  const a = Math.abs(v)
  if (a >= 1e9) return (v / 1e9).toFixed(2) + 'B'
  if (a >= 1e6) return (v / 1e6).toFixed(2) + 'M'
  if (a >= 1e3) return (v / 1e3).toFixed(1) + 'K'
  return Number.isInteger(v) ? String(v) : v.toFixed(1)
}
export const fmtMoney = (v) => (v == null || isNaN(v) ? '—' : '$' + fmtNum(v))
export const fmtPct = (v) => (v == null || isNaN(v) ? '—' : (Math.round(v * 10) / 10) + '%')

const CHART_AXIS = { fontSize: 11, fill: 'var(--text-3)' }
const TIP = { background: 'var(--surface-2)', border: '1px solid var(--border-2)', borderRadius: 8, fontSize: '.78rem', color: 'var(--text)' }

// ── page header ──────────────────────────────────────────────
export function PageHeader({ icon: Icon, title, subtitle, accent = 'var(--primary)', actions }) {
  return (
    <div className="page-header">
      <div style={{ display: 'flex', gap: 14, alignItems: 'center' }}>
        {Icon && (
          <div className="kpi-icon-wrap" style={{ width: 44, height: 44, margin: 0, borderRadius: 13,
            background: `color-mix(in srgb, ${accent} 16%, transparent)`, color: accent }}>
            <Icon size={22} />
          </div>
        )}
        <div>
          <h1 className="page-title" style={{ margin: 0 }}>{title}</h1>
          {subtitle && <p className="page-subtitle">{subtitle}</p>}
        </div>
      </div>
      {actions && <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>{actions}</div>}
    </div>
  )
}

// ── stat tile ────────────────────────────────────────────────
export function Stat({ label, value, unit, icon: Icon, accent = 'var(--primary)', trend, good, hint }) {
  const up = trend != null && trend >= 0
  // "good" = direction where higher is better ('up'/'down'); colours the trend accordingly
  const trendGood = good == null ? up : (good === 'up' ? up : !up)
  return (
    <div className="kpi-card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div style={{ minWidth: 0 }}>
          <div className="kpi-label truncate">{label}</div>
          <div className="kpi-value">{value}{unit ? <span style={{ fontSize: '.9rem', color: 'var(--text-3)', marginLeft: 3 }}>{unit}</span> : null}</div>
        </div>
        {Icon && (
          <div className="kpi-icon-wrap" style={{ margin: 0, background: `color-mix(in srgb, ${accent} 15%, transparent)`, color: accent }}>
            <Icon size={17} />
          </div>
        )}
      </div>
      {trend != null && !isNaN(trend) && (
        <div className="kpi-trend" style={{ color: trendGood ? 'var(--ok)' : 'var(--bad)' }}>
          {up ? <ArrowUpRight size={13} /> : <ArrowDownRight size={13} />}{Math.abs(trend).toFixed(1)}%
        </div>
      )}
      {hint && <div style={{ fontSize: '.72rem', color: 'var(--text-3)', marginTop: 6 }}>{hint}</div>}
    </div>
  )
}

export function StatGrid({ children }) { return <div className="kpi-grid">{children}</div> }

// ── panel (titled card) ──────────────────────────────────────
export function Panel({ title, icon: Icon, actions, children, style, span }) {
  return (
    <div className="card" style={{ ...(span ? { gridColumn: `span ${span}` } : {}), ...style }}>
      {(title || actions) && (
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
          {title && <h3 className="card-title" style={{ margin: 0 }}>{Icon && <Icon size={16} />}{title}</h3>}
          {actions}
        </div>
      )}
      {children}
    </div>
  )
}

export function Grid({ children, min = 300, style }) {
  return <div style={{ display: 'grid', gridTemplateColumns: `repeat(auto-fit,minmax(${min}px,1fr))`, gap: 18, ...style }}>{children}</div>
}

// ── states ───────────────────────────────────────────────────
export function Loading({ label = 'Loading…' }) {
  return <div style={{ display: 'flex', alignItems: 'center', gap: 12, color: 'var(--text-2)', padding: 40 }}><div className="spinner" /> {label}</div>
}
export function Empty({ text = 'No data available.' }) {
  return <div className="card" style={{ color: 'var(--text-3)', textAlign: 'center', padding: 30 }}>{text}</div>
}

// ── charts ───────────────────────────────────────────────────
export function AreaTrend({ data, x = 'period', y, color = 'var(--primary)', height = 220 }) {
  if (!data?.length) return <Empty text="No trend data." />
  const id = 'g' + y
  return (
    <div style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 5, right: 8, left: -16, bottom: 0 }}>
          <defs><linearGradient id={id} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity={0.35} /><stop offset="100%" stopColor={color} stopOpacity={0} />
          </linearGradient></defs>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
          <XAxis dataKey={x} tick={CHART_AXIS} axisLine={false} tickLine={false} />
          <YAxis tick={CHART_AXIS} axisLine={false} tickLine={false} width={48} />
          <Tooltip contentStyle={TIP} />
          <Area type="monotone" dataKey={y} stroke={color} strokeWidth={2} fill={`url(#${id})`} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}

export function MiniBars({ data, x = 'period', y, color = 'var(--primary)', height = 220 }) {
  if (!data?.length) return <Empty text="No data." />
  return (
    <div style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 5, right: 8, left: -16, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
          <XAxis dataKey={x} tick={CHART_AXIS} axisLine={false} tickLine={false} />
          <YAxis tick={CHART_AXIS} axisLine={false} tickLine={false} width={48} />
          <Tooltip contentStyle={TIP} cursor={{ fill: 'var(--hover)' }} />
          <Bar dataKey={y} fill={color} radius={[5, 5, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

// horizontal labelled bars (for breakdowns / factor lists)
export function BarList({ items }) {
  if (!items?.length) return <Empty text="No data." />
  const max = Math.max(...items.map(i => Math.abs(i.value) || 0), 1)
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
      {items.map((it, i) => (
        <div key={i}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '.8rem', marginBottom: 5 }}>
            <span style={{ color: 'var(--text-2)' }}>{it.label}</span>
            <span style={{ fontFamily: 'var(--font-mono)', color: it.color || 'var(--text)' }}>{it.display ?? it.value}</span>
          </div>
          <div style={{ height: 6, background: 'var(--bg-2)', borderRadius: 99, overflow: 'hidden' }}>
            <div style={{ width: `${(Math.abs(it.value) / max) * 100}%`, height: '100%', background: it.color || 'var(--gradient)', borderRadius: 99 }} />
          </div>
        </div>
      ))}
    </div>
  )
}

// ── ask-copilot deep link ────────────────────────────────────
export function AskCopilot({ q, label = 'Ask Copilot', size = 'sm' }) {
  const navigate = useNavigate()
  return (
    <button className={`btn btn-outline${size === 'sm' ? ' btn-sm' : ''}`} onClick={() => navigate(`/chat?q=${encodeURIComponent(q)}`)}>
      <Sparkles size={size === 'sm' ? 13 : 15} /> {label}
    </button>
  )
}

export const PIE = ['#2dd4bf', '#22d3ee', '#38bdf8', '#a78bfa', '#f472b6', '#fbbf24', '#34d399']
export { Cell, LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer }
