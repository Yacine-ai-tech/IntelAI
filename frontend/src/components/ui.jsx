import { useState, Component } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useTranslation } from '../i18n/I18nContext'
import * as Recharts from "recharts";
const { AreaChart, Area, BarChart, Bar, LineChart, Line, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer, Cell, } = Recharts;
import { Sparkles, ArrowUpRight, ArrowDownRight, FileText, X, Globe, AlertTriangle } from 'lucide-react'

// ── formatters ───────────────────────────────────────────────
export const fmtNum = (v) => {
  if (v == null || isNaN(v)) return '—'
  const a = Math.abs(v)
  if (a >= 1e9) return (v / 1e9).toFixed(2) + 'B'
  if (a >= 1e6) return (v / 1e6).toFixed(2) + 'M'
  if (a >= 1e3) return (v / 1e3).toFixed(1) + 'K'
  return Number.isInteger(v) ? String(v) : v.toFixed(1)
}
// Currency presentation (mirrors backend src/services/insights.py). Configure the display
// currency at build time with VITE_CURRENCY (ISO 4217: USD|EUR|GBP|JPY|XOF/FCFA|…) and the
// locale with VITE_LANGUAGE (en|fr). Presentation only — no FX conversion.
const CURRENCIES = {
  USD: ['$', false], CAD: ['$', false], AUD: ['$', false], EUR: ['€', false],
  GBP: ['£', false], JPY: ['¥', false], CNY: ['¥', false], INR: ['₹', false],
  NGN: ['₦', false], XOF: ['FCFA', true], XAF: ['FCFA', true],
}
const CCY_CODE = (import.meta.env.VITE_CURRENCY || 'USD').toUpperCase()
const [CCY_SYM, CCY_WORD] = CURRENCIES[CCY_CODE] || [CCY_CODE, true]
const IS_FR = (import.meta.env.VITE_LANGUAGE || 'en').toLowerCase() === 'fr'

export const fmtMoney = (v) => fmtCurrency(v, CCY_CODE)

// Format a value in a SPECIFIC ISO 4217 currency, regardless of the deployer's configured
// display currency (VITE_CURRENCY). Needed because a KPI row's own `unit` can legitimately
// be a different currency than the rest of the dashboard — e.g. OmniIntelOS reports most
// Finance metrics in USD but also carries one statutory "Chiffre d'affaires (XOF)" row in
// its real functional/local currency (West African CFA franc). Previously any non-USD unit
// fell through to the generic unitless fmtNum(), so that XOF figure rendered as a bare huge
// number sitting right next to $-labeled USD figures — confusing, and not obviously either
// currency. Labeling it "FCFA" explicitly (instead of mislabeling it "$") fixes that without
// guessing at conversion.
export const fmtCurrency = (v, code) => {
  if (v == null || isNaN(v)) return '—'
  const [sym, isWord] = CURRENCIES[String(code || CCY_CODE).toUpperCase()] || [code, true]
  let n = fmtNum(v)                           // e.g. "3.60M" / "850"
  if (IS_FR) {
    n = n.replace('.', ',').replace('B', ' Md').replace('M', ' M').replace('K', ' k')
    // word currencies get a space ("3,60 M FCFA"); symbol currencies attach ("3,60 M€" / "850 €")
    return isWord ? `${n} ${sym}` : (n.includes(' ') ? `${n}${sym}` : `${n} ${sym}`)
  }
  return isWord ? `${n} ${sym}` : `${sym}${n}`           // EN: "$3.60M" / "3.60M FCFA"
}
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

// ── domain hero band (per-domain health headline) ───────────
export function DomainHero({ health, accent = 'var(--primary)' }) {
  if (!health) return null
  const s = Math.round(health.score ?? 0)
  const color = health.color || (s >= 80 ? 'var(--ok)' : s >= 60 ? 'var(--warn)' : 'var(--bad)')
  const factors = Array.isArray(health.factors)
    ? health.factors
    : Object.entries(health.factors || {}).map(([label, value]) => ({ label, value }))
  return (
    <div className="domain-hero" style={{ '--dh': color }}>
      <div className="dh-gauge">
        <div className="dh-cap">{health.captionLabel || 'Health index'}</div>
        <div className="dh-score" style={{ color }}>{s}<span className="dh-slash">/100</span></div>
        <div className="dh-rating" style={{ color }}>{health.rating || health.label || '—'}</div>
      </div>
      {factors.length > 0 && (
        <div className="dh-factors">
          {factors.slice(0, 4).map((f, i) => {
            const v = Math.round(Number(f.value) || 0)
            return (
              <div key={i} className="dh-factor">
                <div className="dh-factor-top"><span>{f.label}</span><b>{v}</b></div>
                <div className="dh-bar"><div style={{ width: `${Math.min(Math.max(v, 0), 100)}%` }} /></div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

// ── stat tile ────────────────────────────────────────────────
export function Stat({ label, value, unit, icon: Icon, accent = 'var(--primary)', trend, good, hint, history, hasAnomaly, onClick }) {
  const up = trend != null && trend >= 0
  const trendGood = good == null ? up : (good === 'up' ? up : !up)
  const sparkColor = accent || 'var(--primary)'
  const sparkId = `sparkG-${label.replace(/\\s+/g, '')}`

  return (
    <div className={`kpi-card${onClick ? ' clickable' : ''}`} onClick={onClick}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div style={{ minWidth: 0 }}>
          <div className="kpi-label truncate" style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            {label}
            {hasAnomaly && (
              <span className="anomaly-dot" title="Anomaly detected">
                <Sparkles size={11} fill="currentColor" />
              </span>
            )}
          </div>
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
      {Array.isArray(history) && history.length >= 2 && (
        <div style={{ height: 60, marginTop: 12, marginLeft: -18, marginRight: -18, marginBottom: -18 }}>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={history}>
              <defs>
                <linearGradient id={sparkId} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor={sparkColor} stopOpacity={0.3} />
                  <stop offset="100%" stopColor={sparkColor} stopOpacity={0} />
                </linearGradient>
              </defs>
              <YAxis hide domain={['dataMin', 'dataMax']} />
              <Area type="monotone" dataKey="value" stroke={sparkColor} strokeWidth={2} fill={`url(#${sparkId})`} dot={false} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}
      {hint && !history && <div style={{ fontSize: '.72rem', color: 'var(--text-3)', marginTop: 6 }}>{hint}</div>}
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
// A request that actually failed (401/500/timeout) was previously visually
// indistinguishable from "this domain has no data yet" — every page destructured
// `data` with a `{}`/`[]` default and rendered straight through with isLoading as the
// only gate, so a confident-looking all-zero dashboard was the same UI as a genuine
// backend error. Confirmed live on several domain pages.
export function ErrorState({ text = 'Could not load this data.' }) {
  return (
    <div className="card" style={{ color: 'var(--bad)', textAlign: 'center', padding: 30, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8 }}>
      <AlertTriangle size={22} />
      <span>{text}</span>
    </div>
  )
}

// A first-time visitor with no stored login token skips the auth check entirely (there's
// nothing to check yet) and lands straight on a normal-looking login form — even when the
// backend is completely unreachable. They'd only discover that after typing credentials and
// watching the request silently fail. This tells a cold/unreachable backend apart from
// "just not logged in yet" before the login form ever renders.
export function WakingBackend({ waking = true, onRetry }) {
  return (
    <div style={{ display: 'flex', minHeight: '60vh', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 16, textAlign: 'center', padding: 24 }}>
      <div style={{ fontSize: 15, fontWeight: 600, color: 'var(--text)' }}>
        {waking ? 'Waking the backend…' : 'Backend unreachable'}
      </div>
      <div style={{ maxWidth: 320, fontSize: 13, color: 'var(--text-3)' }}>
        {waking
          ? 'The free-tier service sleeps when idle. First start can take up to a minute.'
          : 'Could not reach the API. It may still be starting.'}
      </div>
      {waking ? <div className="spinner" /> : (
        <button className="btn btn-secondary" onClick={onRetry}>Retry</button>
      )}
    </div>
  )
}

// ── crash containment ──────────────────────────────────────────
// React only lets class components catch render errors (no hook equivalent). Without one
// anywhere in the tree, ANY uncaught error thrown while rendering — e.g. from a chat
// message/citation click handler triggering a re-render — unmounts the whole app (a blank,
// totally unresponsive page: "hard freeze, nothing clickable"), matching the floating
// Copilot widget's reported crash-on-citation-click behavior exactly regardless of which
// specific line throws. Wrap any risky subtree (the floating widget in particular, since
// it's reported to crash and previously had zero fault isolation from the rest of the app)
// so a bug there degrades to a small inline error card instead of taking down the page.
export class ErrorBoundary extends Component {
  constructor(props) { super(props); this.state = { error: null } }
  static getDerivedStateFromError(error) { return { error } }
  componentDidCatch(error, info) { console.error('ErrorBoundary caught:', error, info) }
  render() {
    if (this.state.error) {
      return this.props.fallback ? this.props.fallback(this.state.error, () => this.setState({ error: null }))
        : (
          <div className="card" style={{ color: 'var(--bad)', padding: 16, display: 'flex', flexDirection: 'column', gap: 8 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}><AlertTriangle size={16} /> Something went wrong.</div>
            <button className="btn btn-ghost btn-sm" onClick={() => this.setState({ error: null })}>Retry</button>
          </div>
        )
    }
    return this.props.children
  }
}

// ── charts ───────────────────────────────────────────────────
// Brand gradient stops reused by chart strokes/fills (Deep Blue → Cyan).
const BRAND_STOPS = [['0%', '#4f46e5'], ['55%', '#2563eb'], ['100%', '#22d3ee']]

export function AreaTrend({ data, x = 'period', y, color = 'var(--primary)', height = 220 }) {
  if (!Array.isArray(data) || data.length === 0) return <Empty text="No trend data." />
  const id = 'g' + y, sid = 's' + y
  return (
    <div style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 5, right: 8, left: -16, bottom: 0 }}>
          <defs>
            <linearGradient id={id} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={color} stopOpacity={0.34} /><stop offset="100%" stopColor={color} stopOpacity={0} />
            </linearGradient>
            <linearGradient id={sid} x1="0" y1="0" x2="1" y2="0">
              {BRAND_STOPS.map(([o, c]) => <stop key={o} offset={o} stopColor={c} />)}
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
          <XAxis dataKey={x} tick={CHART_AXIS} axisLine={false} tickLine={false} />
          <YAxis tick={CHART_AXIS} axisLine={false} tickLine={false} width={48} />
          <Tooltip contentStyle={TIP} />
          <Area type="monotone" dataKey={y} stroke={`url(#${sid})`} strokeWidth={2.4} fill={`url(#${id})`} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}

export function MiniBars({ data, x = 'period', y, color = 'var(--primary)', height = 220 }) {
  if (!Array.isArray(data) || data.length === 0) return <Empty text="No data." />
  const bid = 'b' + y
  return (
    <div style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 5, right: 8, left: -16, bottom: 0 }}>
          <defs><linearGradient id={bid} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#22d3ee" /><stop offset="100%" stopColor="#2563eb" stopOpacity={0.85} />
          </linearGradient></defs>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
          <XAxis dataKey={x} tick={CHART_AXIS} axisLine={false} tickLine={false} />
          <YAxis tick={CHART_AXIS} axisLine={false} tickLine={false} width={48} />
          <Tooltip contentStyle={TIP} cursor={{ fill: 'var(--hover)' }} />
          <Bar dataKey={y} fill={`url(#${bid})`} radius={[5, 5, 0, 0]} />
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
export function AskCopilot({ q, label, size = 'sm' }) {
  const { user } = useAuth()
  const { t } = useTranslation()
  const navigate = useNavigate()
  
  const labelText = label || t('askAssistant') || 'Ask Copilot'

  return (
    <button
      className={`btn btn-primary btn-${size}`}
      style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}
      onClick={() => window.dispatchEvent(new CustomEvent('open-copilot', { detail: { q } }))}
    >
      <Sparkles size={14} />
      {labelText}
    </button>
  )
}

// ── Citations — robust, deduped, numbered source chips (used everywhere) ──────
export function Citations({ sources, label = 'Sources' }) {
  const [preview, setPreview] = useState(null)

  if (!sources || !sources.length) return null
  // Defensive client-side normalisation: accept strings or objects, dedupe by title.
  const seen = new Set()
  const list = []
  sources.forEach((s, i) => {
    const o = typeof s === 'string' ? { title: s } : (s || {})
    const title = (o.title || o.source || 'source').toString().trim()
    const key = title.toLowerCase()
    if (!title || seen.has(key)) return
    seen.add(key)
    let rel = o.relevance
    if (typeof rel === 'string') rel = parseFloat(rel.replace('%', ''))
    if (typeof rel === 'number' && rel > 1) rel = rel / 100
    list.push({ id: o.id ?? list.length + 1, title, type: o.type || 'knowledge', snippet: o.snippet || o.preview || o.content, rel: typeof rel === 'number' && !isNaN(rel) ? Math.round(rel * 100) : null, source: o.source || o.url || '' })
  })
  if (!list.length) return null

  return (
    <>
      <div className="citations">
        <span className="citations-label">{label}</span>
        {list.map((s) => {
          const isHttp = s.source?.startsWith('http')
          return (
            <a key={s.id} href={isHttp ? s.source : '#'} target={isHttp ? '_blank' : '_self'} rel="noreferrer" 
               className={`citation-chip${s.type === 'kpi' ? ' kpi' : ''}`} title={s.snippet || s.title} style={{ textDecoration: 'none', cursor: 'pointer' }}
               onClick={(e) => {
                 if (!isHttp) {
                   e.preventDefault()
                   setPreview(s)
                 }
               }}>
              <span className="cite-n">{s.id}</span>
              {s.type === 'kpi' ? <Sparkles size={11} /> : s.type === 'web' ? <Globe size={11} /> : <FileText size={11} />} {s.title}
              {s.rel != null && <em className="cite-rel">{s.rel}%</em>}
            </a>
          )
        })}
      </div>

      {preview && (
        <div className="drawer-overlay" onClick={() => setPreview(null)} style={{ justifyContent: 'center', alignItems: 'center', zIndex: 1000 }}>
          <div className="card" onClick={e => e.stopPropagation()} style={{ maxWidth: 760, width: '90%', maxHeight: '80vh', overflowY: 'auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 }}>
              <h3 className="card-title" style={{ margin: 0 }}><FileText size={16} /> {preview.title || 'Document'}</h3>
              <button className="btn btn-ghost btn-icon" onClick={() => setPreview(null)}><X size={18} /></button>
            </div>
            <div style={{ whiteSpace: 'pre-wrap', lineHeight: 1.6, color: 'var(--text-2)', fontSize: '.9rem' }}>
              {preview.snippet || preview.text || 'No detailed content available.'}
            </div>
            {preview.source && <div style={{ marginTop: 14, fontSize: '.78rem', color: 'var(--text-3)' }}>Source: {preview.source}</div>}
          </div>
        </div>
      )}
    </>
  )
}

// Brand-forward categorical palette (Deep Blue → Cyan → Indigo, + anomaly violet)
export const PIE = ['#38bdf8', '#22d3ee', '#6366f1', '#2563eb', '#818cf8', '#c084fc', '#2dd4bf']
export { Cell, LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer }
