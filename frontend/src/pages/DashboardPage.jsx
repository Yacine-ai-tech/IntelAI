import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useTranslation } from '../i18n/I18nContext'
import { useQuery } from '@tanstack/react-query'
import * as api from '../api'
import {
  DollarSign, TrendingDown, Users, Monitor, Settings2, Package, Leaf,
  TrendingUp, Sparkles, Activity, ShieldAlert, ArrowUpRight, ArrowDownRight,
} from 'lucide-react'
import { LineChart, Line, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

// category → { icon, accent, route } so a KPI card both reads its domain and links to it.
const CAT = {
  finance:   { icon: DollarSign, accent: 'var(--p-cfo)',     route: '/financial' },
  revenue:   { icon: DollarSign, accent: 'var(--p-cfo)',     route: '/financial' },
  cost:      { icon: TrendingDown, accent: 'var(--p-risk)',  route: '/financial' },
  hr:        { icon: Users,      accent: 'var(--p-chro)',    route: '/hr' },
  it:        { icon: Monitor,    accent: 'var(--p-cto)',     route: '/it' },
  operations:{ icon: Settings2,  accent: 'var(--p-coo)',     route: '/operations' },
  logistics: { icon: Package,    accent: 'var(--p-coo)',     route: '/logistics' },
  esg:       { icon: Leaf,       accent: 'var(--p-esg)',     route: '/esg' },
  default:   { icon: Activity,   accent: 'var(--primary)',   route: '/analytics' },
}
const catOf = (c) => CAT[(c || '').toLowerCase()] || CAT.default

function Sparkline({ data, color }) {
  if (!data || data.length < 2) return <div style={{ height: 42 }} />
  return (
    <div style={{ height: 42, marginTop: 10 }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data.map(d => ({ value: d.value || 0 }))}>
          <defs><linearGradient id="spark" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="#4f46e5" /><stop offset="100%" stopColor="#22d3ee" />
          </linearGradient></defs>
          <YAxis hide domain={['dataMin', 'dataMax']} />
          <Tooltip contentStyle={{ background: 'var(--surface-2)', border: '1px solid var(--border-2)', borderRadius: 8, fontSize: '.75rem' }}
            itemStyle={{ color: 'var(--text)' }} labelStyle={{ display: 'none' }} />
          <Line type="monotone" dataKey="value" stroke={color === 'var(--primary)' ? 'url(#spark)' : color} strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

function KPICard({ label, value, change, category, history, isAnomaly }) {
  const navigate = useNavigate()
  const { icon: Icon, accent, route } = catOf(category)
  
  return (
    <Stat 
      label={label}
      value={value}
      trend={change}
      icon={Icon}
      accent={accent}
      history={history || []}
      hasAnomaly={isAnomaly}
      onClick={() => navigate(route)}
    />
  )
}

function HealthGauge({ score, t }) {
  const s = Math.round(score)
  const color = s >= 80 ? 'var(--ok)' : s >= 60 ? 'var(--warn)' : 'var(--bad)'
  const label = s >= 80 ? t('excellent') : s >= 60 ? t('moderate') : t('atRisk')
  return (
    <div className="card health-gauge">
      <h3 className="card-title" style={{ justifyContent: 'center' }}><Activity size={16} /> {t('healthIndex')}</h3>
      <div className="health-gauge-value" style={{ color }}>{s}<span style={{ fontSize: '1rem', color: 'var(--text-3)' }}>/100</span></div>
      <div className="health-gauge-rating" style={{ color }}>{label}</div>
    </div>
  )
}

function FactorBar({ label, value, invert }) {
  const v = Math.round(value || 0)
  const good = invert ? v < 40 : v > 60
  const color = good ? 'var(--ok)' : v > 40 ? 'var(--warn)' : 'var(--bad)'
  return (
    <div style={{ marginBottom: 12 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '.78rem', marginBottom: 5 }}>
        <span style={{ color: 'var(--text-2)' }}>{label}</span>
        <span style={{ fontFamily: 'var(--font-mono)', color }}>{v}</span>
      </div>
      <div style={{ height: 6, background: 'var(--bg-2)', borderRadius: 99, overflow: 'hidden' }}>
        <div style={{ width: `${v}%`, height: '100%', background: color, borderRadius: 99 }} />
      </div>
    </div>
  )
}

export default function DashboardPage() {
  const { user } = useAuth()
  const { t } = useTranslation()
  const navigate = useNavigate()

  const { data: kpis = [], isLoading: kpisLoading } = useQuery({
    queryKey: ['kpis'], queryFn: () => api.getKPIs().then(r => r.data?.metrics || []),
    staleTime: 300_000, retry: 1,
  })
  const { data: health, isLoading: healthLoading } = useQuery({
    queryKey: ['health'], queryFn: () => api.getHealth().then(r => r.data),
    staleTime: 120_000, retry: 1,
  })
  const { data: summary, isLoading: summaryLoading } = useQuery({
    queryKey: ['summary'], queryFn: () => api.getSummary().then(r => r.data),
    staleTime: 600_000, retry: 1,
  })
  const { data: risk } = useQuery({
    queryKey: ['risk'], queryFn: () => api.getRisk().then(r => r.data),
    staleTime: 300_000, retry: 1,
  })
  const { data: anomalies = [] } = useQuery({
    queryKey: ['anomalies'], queryFn: () => api.getAnomalies().then(r => r.data?.anomalies || []),
    staleTime: 300_000, retry: 1,
  })

  const loading = kpisLoading || healthLoading || summaryLoading

  const fmt = (val) => {
    if (typeof val !== 'number') return val || '—'
    if (Math.abs(val) >= 1e6) return `${(val / 1e6).toFixed(1)}M`
    if (Math.abs(val) >= 1e3) return `${(val / 1e3).toFixed(1)}K`
    return val.toFixed(1)
  }

  // Build per-metric history (last 6 periods), then take the latest reading per metric.
  const hist = {}
  kpis.forEach(k => {
    const name = k.metric_name || k.name || 'Unknown'
    ;(hist[name] = hist[name] || []).push({ period: k.period, value: k.value })
  })
  Object.keys(hist).forEach(n => { hist[n].sort((a, b) => (a.period || '').localeCompare(b.period || '')); hist[n] = hist[n].slice(-6) })

  const seen = new Set()
  const topKPIs = kpis.filter(k => {
    const n = k.metric_name || k.name
    if (seen.has(n)) return false; seen.add(n); return true
  }).slice(0, 8).map(k => {
    const n = k.metric_name || k.name || 'Metric'
    const isAnomaly = anomalies.some(a => (a.metric_name || a.name) === n)
    return {
      label: n, value: fmt(k.value),
      change: k.change_pct, isAnomaly, category: k.category || 'default', history: hist[n] || [],
    }
  })

  const riskScore = risk?.score
  const askChips = ['What is our overall business health?', 'What risks should I watch right now?', 'Summarize this period’s key metrics']

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">{t('welcome')}, {user?.full_name || user?.username}</h1>
          <p className="page-subtitle">
            {new Date().toLocaleDateString(undefined, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
          </p>
        </div>
        <button className="btn btn-primary" onClick={() => navigate('/chat')}>
          <Sparkles size={16} /> {t('askAssistant') || 'Ask Copilot'}
        </button>
      </div>

      {loading ? (
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, color: 'var(--text-2)', padding: 40 }}>
          <div className="spinner" /> {t('loadingDashboard') || 'Loading…'}
        </div>
      ) : (
        <>
          <div className="kpi-grid">
            {topKPIs.length ? topKPIs.map((k, i) => <KPICard key={i} {...k} />)
              : <div className="card" style={{ gridColumn: '1/-1', color: 'var(--text-3)' }}>{t('noData') || 'No KPI data available.'}</div>}
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'minmax(220px,1fr) 2fr', gap: 18, marginTop: 18 }}>
            <HealthGauge score={health?.score ?? health?.health_index ?? 0} t={t} />
            <div className="card">
              <h3 className="card-title"><TrendingUp size={16} /> {t('executiveSummary') || 'Executive Summary'}</h3>
              <p style={{ lineHeight: 1.7, color: 'var(--text-2)', fontSize: '.9rem' }}>
                {summary?.summary || t('noSummary') || 'No summary available yet.'}
              </p>
              <button className="btn btn-outline btn-sm" style={{ marginTop: 14 }} onClick={() => navigate('/chat')}>
                <Sparkles size={14} /> {t('askAssistant') || 'Ask Copilot'}
              </button>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(300px,1fr))', gap: 18, marginTop: 18 }}>
            {risk && (
              <div className="card clickable" onClick={() => navigate('/risk')}>
                <h3 className="card-title"><ShieldAlert size={16} /> {t('riskIndicators') || 'Risk Overview'}</h3>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: 10, marginBottom: 16 }}>
                  <span style={{ fontFamily: 'var(--font-mono)', fontSize: '2rem', fontWeight: 700,
                    color: riskScore >= 70 ? 'var(--ok)' : riskScore >= 50 ? 'var(--warn)' : 'var(--bad)' }}>
                    {Math.round(riskScore ?? 0)}
                  </span>
                  <span className="badge">{risk.label}</span>
                </div>
                <FactorBar label={t('liquidity') || 'Liquidity'} value={risk.liquidity_score} />
                <FactorBar label={t('execution') || 'Execution'} value={risk.execution_score} />
                <FactorBar label={t('concentration') || 'Concentration'} value={risk.concentration_score} invert />
                <FactorBar label={t('anomalies') || 'Anomalies'} value={risk.anomaly_score} invert />
              </div>
            )}

            <div className="card" style={{ display: 'flex', flexDirection: 'column' }}>
              <h3 className="card-title"><Sparkles size={16} /> {t('askAssistant') || 'Ask the Copilot'}</h3>
              <p style={{ color: 'var(--text-2)', fontSize: '.86rem', marginBottom: 14 }}>
                {t('copilotHint') || 'Grounded answers over your live KPIs — scoped to your role, with sources.'}
              </p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {askChips.map((q, i) => (
                  <button key={i} className="prompt-card" style={{ textAlign: 'left' }}
                    onClick={() => navigate(`/chat?q=${encodeURIComponent(q)}`)}>{q}</button>
                ))}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
