import { useState, useMemo, Component, useCallback } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import * as Recharts from 'recharts'
const {
  ComposedChart, AreaChart, Area, LineChart, Line, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  ReferenceLine, Cell,
} = Recharts
import * as api from '../api'
import { useAuth } from '../context/AuthContext'
import { useTranslation } from '../i18n/I18nContext'
import {
  BarChart3, Hash, Calendar, Layers, FolderKanban, TrendingUp,
  AlertTriangle, Search, Filter, ArrowUpRight, ArrowDownRight,
  Minus, ChevronDown, Database, Zap, Target, Activity,
  Play, RefreshCw, Info, CheckCircle, Clock,
} from 'lucide-react'
import {
  PageHeader, Stat, StatGrid, fmtNum, Loading, Grid,
  AskCopilot, AreaTrend, Panel, Empty,
} from '../components/ui'

/* ─── chart tokens ─────────────────────────────────────────────── */
const TIP = {
  background: 'var(--surface-2)', border: '1px solid var(--border-2)',
  borderRadius: 8, fontSize: '.78rem', color: 'var(--text)', boxShadow: '0 4px 20px rgba(0,0,0,.4)',
}
const AXIS = { fontSize: 11, fill: 'var(--text-3)' }
const DOMAIN_COLORS = {
  Finance: '#4f46e5', Growth: '#22d3ee', People: '#a855f7',
  Operations: '#f59e0b', IT: '#10b981', Logistics: '#f97316',
  ESG: '#22c55e', Risk: '#ef4444', default: 'var(--primary)',
}

/* ─── local error boundary ──────────────────────────────────────── */
class AnalyticsErrorBoundary extends Component {
  constructor(props) { super(props); this.state = { hasError: false, error: null } }
  static getDerivedStateFromError(error) { return { hasError: true, error } }
  componentDidCatch(error, info) { console.error('AnalyticsPage error:', error, info) }
  render() {
    if (this.state.hasError) return (
      <div style={{ padding: '60px', textAlign: 'center' }}>
        <AlertTriangle size={40} style={{ color: '#f59e0b', marginBottom: 16, display: 'block', margin: '0 auto 16px' }} />
        <h2 style={{ color: 'var(--text)', marginBottom: 8 }}>Analytics Unavailable</h2>
        <p style={{ color: 'var(--text-2)', marginBottom: 20 }}>{this.state.error?.message || 'The analytics panel encountered an error.'}</p>
        <button className="btn btn-primary" onClick={() => this.setState({ hasError: false, error: null })}>Retry</button>
      </div>
    )
    return this.props.children
  }
}

export default function AnalyticsPage() {
  return <AnalyticsErrorBoundary><AnalyticsInner /></AnalyticsErrorBoundary>
}

/* ─── trend chip ────────────────────────────────────────────────── */
function TrendChip({ pct }) {
  if (pct == null) return <span style={{ color: 'var(--text-3)', fontSize: '.75rem' }}>—</span>
  const up = pct >= 0
  const Icon = up ? ArrowUpRight : ArrowDownRight
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: 2, fontSize: '.72rem', fontWeight: 600,
      color: up ? 'var(--ok)' : 'var(--bad)', background: up ? 'rgba(34,197,94,.12)' : 'rgba(239,68,68,.12)',
      borderRadius: 4, padding: '1px 5px',
    }}>
      <Icon size={11} />{Math.abs(pct).toFixed(1)}%
    </span>
  )
}

/* ─── mini sparkline ────────────────────────────────────────────── */
function Sparkline({ data, color = 'var(--primary)' }) {
  if (!data?.length) return null
  return (
    <ResponsiveContainer width={80} height={32}>
      <LineChart data={data} margin={{ top: 2, right: 2, left: 2, bottom: 2 }}>
        <Line type="monotone" dataKey="value" stroke={color} strokeWidth={1.8} dot={false} isAnimationActive={false} />
      </LineChart>
    </ResponsiveContainer>
  )
}

/* ─── forecast mini chart ───────────────────────────────────────── */
function ForecastMini({ historical, forecast }) {
  const hist = (historical || []).map(h => ({ period: h.month_tag || h.period, value: h.actual ?? h.value, type: 'historical' }))
  const fc = (forecast || []).map(f => ({ period: f.month_tag || f.period, value: f.forecast ?? f.predicted, lower: f.lower_bound, upper: f.upper_bound, type: 'forecast' }))
  const data = [...hist.slice(-12), ...fc]
  if (!data.length) return <Empty text="No forecast data" />
  const splitIdx = hist.slice(-12).length
  return (
    <div style={{ height: 220 }}>
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={data} margin={{ top: 5, right: 8, left: -10, bottom: 0 }}>
          <defs>
            <linearGradient id="ah" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="var(--primary)" stopOpacity={0.2} />
              <stop offset="95%" stopColor="var(--primary)" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="af" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="var(--accent)" stopOpacity={0.25} />
              <stop offset="95%" stopColor="var(--accent)" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
          <XAxis dataKey="period" tick={AXIS} axisLine={false} tickLine={false} interval="preserveStartEnd" />
          <YAxis tick={AXIS} axisLine={false} tickLine={false} width={44} />
          <Tooltip contentStyle={TIP} />
          {splitIdx > 0 && <ReferenceLine x={data[splitIdx - 1]?.period} stroke="var(--border-2)" strokeDasharray="4 4" label={{ value: 'Now', fill: 'var(--text-3)', fontSize: 10 }} />}
          <Area type="monotone" dataKey="value" stroke="var(--primary)" strokeWidth={2} fill="url(#ah)" dot={false} name="Historical" connectNulls isAnimationActive={false} />
          <Area type="monotone" dataKey={(d) => d.type === 'forecast' ? d.value : undefined} stroke="var(--accent)" strokeWidth={2} strokeDasharray="5 3" fill="url(#af)" dot={false} name="Forecast" connectNulls isAnimationActive={false} />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  )
}

/* ─── main component ────────────────────────────────────────────── */
function AnalyticsInner() {
  const { hasAction } = useAuth()
  const { t } = useTranslation()
  const [metric, setMetric] = useState('')
  const [fcMetric, setFcMetric] = useState('')
  const [fcPeriods, setFcPeriods] = useState(6)
  const [search, setSearch] = useState('')
  const [catFilter, setCatFilter] = useState('all')

  const { data: kpis = [], isLoading } = useQuery({
    queryKey: ['kpis'], queryFn: () => api.getKPIs().then(r => r.data?.metrics || []), staleTime: 300_000,
  })
  const { data: periods = [] } = useQuery({
    queryKey: ['periods'], queryFn: () => api.getPeriods().then(r => r.data?.periods || []), staleTime: 600_000,
  })
  const { data: metricNames = [] } = useQuery({
    queryKey: ['metrics'], queryFn: () => api.getMetrics().then(r => r.data?.metrics || []), staleTime: 600_000,
  })

  const forecast = useMutation({ mutationFn: (m) => api.runForecast(m, fcPeriods).then(r => r.data) })

  const categories = useMemo(() => ['all', ...new Set(kpis.map(k => k.category).filter(Boolean))], [kpis])
  const selected = metric || metricNames[0] || ''

  /* per-metric latest values + trend history */
  const metricMap = useMemo(() => {
    const m = {}
    kpis.forEach(k => {
      const n = k.metric_name || k.name
      if (!m[n]) m[n] = { latest: k, history: [], category: k.category }
      m[n].history.push({ period: k.period, value: k.value })
      if ((k.period || '') > (m[n].latest.period || '')) m[n].latest = k
    })
    Object.values(m).forEach(v => v.history.sort((a, b) => (a.period || '').localeCompare(b.period || '')))
    return m
  }, [kpis])

  const series = useMemo(() => (metricMap[selected]?.history || [])
    .map(k => ({ period: k.period, value: Math.round((k.value || 0) * 100) / 100 })), [metricMap, selected])

  /* filtered table */
  const filteredMetrics = useMemo(() => {
    return Object.entries(metricMap)
      .filter(([name, v]) => {
        if (catFilter !== 'all' && v.category !== catFilter) return false
        if (search && !name.toLowerCase().includes(search.toLowerCase())) return false
        return true
      })
      .slice(0, 80)
  }, [metricMap, catFilter, search])

  const fc = forecast.data

  if (isLoading && kpis.length === 0) return <Loading />
  if (!isLoading && kpis.length === 0) return (
    <div>
      <PageHeader icon={BarChart3} title={t('navAnalytics') || 'Analytics'} subtitle="Cross-domain KPI explorer" />
      <Panel style={{ marginTop: 24, textAlign: 'center', padding: '60px 40px' }}>
        <Database size={48} style={{ color: 'var(--text-3)', display: 'block', margin: '0 auto 16px' }} />
        <h3 style={{ color: 'var(--text)', marginBottom: 8 }}>No Analytics Data</h3>
        <p style={{ color: 'var(--text-2)', maxWidth: 400, margin: '0 auto' }}>
          Ingest KPI data via the <a href="/data-hub" style={{ color: 'var(--primary)' }}>Data Hub</a> to unlock analytics.
        </p>
      </Panel>
    </div>
  )

  const selectedColor = DOMAIN_COLORS[metricMap[selected]?.category] || DOMAIN_COLORS.default

  return (
    <div>
      <PageHeader icon={BarChart3} title={t('navAnalytics') || 'Analytics'}
        subtitle={t('analyticsSubtitle') || 'Cross-domain KPI explorer & forecasting'}
        actions={<AskCopilot q={t('askCopilot_AnalyticsPage_WhatAreThe') || 'What are our top performing KPIs and where do we see anomalies?'} />} />

      {/* ── headline stats ── */}
      <StatGrid>
        <Stat label={t('totalMetrics') || 'Distinct Metrics'} value={fmtNum(metricNames.length)} icon={Hash} hint="Unique KPI names tracked" />
        <Stat label={t('timePeriods') || 'Time Periods'} value={fmtNum(periods.length)} icon={Calendar} />
        <Stat label={t('dataPoints') || 'Total Data Points'} value={fmtNum(kpis.length)} icon={Layers} />
        <Stat label={t('categories') || 'Domains Covered'} value={fmtNum(categories.length - 1)} icon={FolderKanban} />
      </StatGrid>

      {/* ── metric explorer ── */}
      <Panel title={t('metricExplorer') || 'Metric Explorer'} icon={TrendingUp} style={{ marginTop: 18 }}
        actions={
          <select className="form-input" style={{ width: 260 }} value={selected} onChange={e => setMetric(e.target.value)}>
            {metricNames.map((m, i) => (
              <option key={i} value={m}>{m}{metricMap[m] ? ` · ${metricMap[m].category}` : ''}</option>
            ))}
          </select>
        }>
        {/* metric meta row */}
        {metricMap[selected] && (
          <div style={{ display: 'flex', gap: 24, marginBottom: 16, flexWrap: 'wrap', alignItems: 'center' }}>
            <span style={{ background: 'var(--surface-2)', borderRadius: 6, padding: '4px 10px', fontSize: '.8rem', color: selectedColor, fontWeight: 600, border: `1px solid ${selectedColor}40` }}>
              {metricMap[selected]?.category}
            </span>
            <span style={{ fontSize: '.82rem', color: 'var(--text-2)' }}>
              <strong style={{ color: 'var(--text)' }}>{fmtNum(metricMap[selected]?.latest?.value)}</strong> latest value
            </span>
            <span style={{ fontSize: '.82rem', color: 'var(--text-2)' }}>
              {series.length} <strong style={{ color: 'var(--text)' }}>periods</strong>
            </span>
            <span style={{ fontSize: '.82rem', color: 'var(--text-2)' }}>
              Latest period: <strong style={{ color: 'var(--text)' }}>{metricMap[selected]?.latest?.period || '—'}</strong>
            </span>
          </div>
        )}
        {series.length > 0 ? (
          <div style={{ height: 260 }}>
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={series} margin={{ top: 5, right: 8, left: -10, bottom: 0 }}>
                <defs>
                  <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={selectedColor} stopOpacity={0.28} />
                    <stop offset="95%" stopColor={selectedColor} stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                <XAxis dataKey="period" tick={AXIS} axisLine={false} tickLine={false} interval="preserveStartEnd" />
                <YAxis tick={AXIS} axisLine={false} tickLine={false} width={52} />
                <Tooltip contentStyle={TIP} formatter={(v) => [fmtNum(v), selected]} />
                <Area type="monotone" dataKey="value" stroke={selectedColor} strokeWidth={2.4} fill="url(#areaGrad)" dot={false} activeDot={{ r: 5, fill: selectedColor }} />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <Empty text="Select a metric to view its trend." />
        )}
      </Panel>

      {/* ── forecast panel ── */}
      {hasAction('forecast') && (
        <Panel title="Forecasting" icon={Zap} style={{ marginTop: 18 }}>
          <div style={{ display: 'flex', gap: 10, marginBottom: 18, flexWrap: 'wrap', alignItems: 'flex-end' }}>
            <div style={{ flex: 1, minWidth: 200 }}>
              <label className="form-label">Metric to forecast</label>
              <select className="form-input" value={fcMetric} onChange={e => setFcMetric(e.target.value)}>
                <option value="">Select a metric…</option>
                {metricNames.map((m, i) => <option key={i} value={m}>{m}</option>)}
              </select>
            </div>
            <div style={{ minWidth: 130 }}>
              <label className="form-label">Periods ahead</label>
              <select className="form-input" value={fcPeriods} onChange={e => setFcPeriods(Number(e.target.value))}>
                {[3, 6, 9, 12].map(n => <option key={n} value={n}>{n} months</option>)}
              </select>
            </div>
            <button
              className="btn btn-primary"
              disabled={!fcMetric || forecast.isPending}
              onClick={() => forecast.mutate(fcMetric)}
              style={{ display: 'flex', alignItems: 'center', gap: 6 }}
            >
              {forecast.isPending ? <><RefreshCw size={14} style={{ animation: 'spin 1s linear infinite' }} /> Running…</> : <><Play size={14} /> Run Forecast</>}
            </button>
          </div>

          {/* forecast results */}
          {fc && !fc.error && (
            <>
              {/* result stats */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(140px,1fr))', gap: 12, marginBottom: 16 }}>
                {[
                  { label: 'Metric', value: fc.metric || fcMetric, icon: Target },
                  { label: 'Model', value: fc.model || 'Linear Regression', icon: Activity },
                  { label: 'R² Score', value: fc.explanation?.r_squared != null ? fc.explanation.r_squared.toFixed(3) : '—', icon: CheckCircle },
                  { label: 'Forecast Periods', value: fc.forecast?.length || fcPeriods, icon: Clock },
                ].map(s => (
                  <div key={s.label} style={{ background: 'var(--surface-2)', borderRadius: 8, padding: '10px 14px', border: '1px solid var(--border)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 4 }}>
                      <s.icon size={13} style={{ color: 'var(--primary)' }} />
                      <span style={{ fontSize: '.72rem', color: 'var(--text-3)', textTransform: 'uppercase', letterSpacing: '.04em' }}>{s.label}</span>
                    </div>
                    <div style={{ fontSize: '.95rem', fontWeight: 600, color: 'var(--text)' }}>{String(s.value)}</div>
                  </div>
                ))}
              </div>

              {/* interpretation hint */}
              {fc.explanation && (
                <div style={{ background: 'rgba(79,70,229,.08)', border: '1px solid rgba(79,70,229,.2)', borderRadius: 8, padding: '10px 14px', marginBottom: 16, fontSize: '.8rem', color: 'var(--text-2)', display: 'flex', gap: 8, alignItems: 'flex-start' }}>
                  <Info size={14} style={{ color: 'var(--primary)', flexShrink: 0, marginTop: 1 }} />
                  <span>
                    <strong style={{ color: 'var(--text)' }}>Trend:</strong>{' '}
                    {fc.explanation.trend_direction === 'increasing' ? '↑ Upward trend' : fc.explanation.trend_direction === 'decreasing' ? '↓ Downward trend' : '→ Flat'} —{' '}
                    slope {fc.explanation.slope?.toFixed(3) ?? '?'}/period.{' '}
                    {fc.explanation.r_squared >= 0.8 ? 'High predictability (R² ≥ 0.8).' : fc.explanation.r_squared >= 0.5 ? 'Moderate predictability.' : 'Low predictability — treat projections cautiously.'}
                  </span>
                </div>
              )}

              <ForecastMini historical={fc.historical} forecast={fc.forecast} />

              {/* projection table */}
              <div style={{ marginTop: 14, maxHeight: 220, overflowY: 'auto' }}>
                <table className="table">
                  <thead>
                    <tr>
                      <th>Period</th><th>Forecast</th><th>Lower (95%)</th><th>Upper (95%)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(fc.forecast || []).map((f, i) => (
                      <tr key={i}>
                        <td style={{ fontFamily: 'var(--font-mono)', fontSize: '.82rem' }}>{f.month_tag || f.period}</td>
                        <td style={{ fontWeight: 600, color: 'var(--accent)' }}>{fmtNum(f.forecast ?? f.predicted ?? f.value)}</td>
                        <td style={{ color: 'var(--text-3)', fontSize: '.82rem' }}>{fmtNum(f.lower_bound ?? f.lower)}</td>
                        <td style={{ color: 'var(--text-3)', fontSize: '.82rem' }}>{fmtNum(f.upper_bound ?? f.upper)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}
          {fc?.error && <div className="alert alert-danger" style={{ marginTop: 8 }}>⚠️ {fc.error}</div>}
          {!fc && !forecast.isPending && (
            <div style={{ textAlign: 'center', padding: '30px 0', color: 'var(--text-3)', fontSize: '.85rem' }}>
              <Zap size={28} style={{ display: 'block', margin: '0 auto 10px', opacity: .4 }} />
              Select a metric and click <strong>Run Forecast</strong> to generate Monte-Carlo projections.
            </div>
          )}
        </Panel>
      )}

      {/* ── all metrics table ── */}
      <Panel title={t('allMetrics') || 'All Metrics'} icon={Layers} style={{ marginTop: 18 }}>
        {/* filter bar */}
        <div style={{ display: 'flex', gap: 10, marginBottom: 14, flexWrap: 'wrap' }}>
          <div style={{ position: 'relative', flex: 1, minWidth: 180 }}>
            <Search size={14} style={{ position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-3)' }} />
            <input
              className="form-input"
              placeholder="Search metrics…"
              value={search}
              onChange={e => setSearch(e.target.value)}
              style={{ paddingLeft: 32 }}
            />
          </div>
          <div style={{ position: 'relative' }}>
            <Filter size={14} style={{ position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-3)' }} />
            <select className="form-input" value={catFilter} onChange={e => setCatFilter(e.target.value)} style={{ paddingLeft: 30, minWidth: 160 }}>
              {categories.map(c => <option key={c} value={c}>{c === 'all' ? 'All Domains' : c}</option>)}
            </select>
          </div>
          <span style={{ fontSize: '.8rem', color: 'var(--text-3)', alignSelf: 'center' }}>
            {filteredMetrics.length} metric{filteredMetrics.length !== 1 ? 's' : ''}
          </span>
        </div>

        <div style={{ maxHeight: 400, overflowY: 'auto' }}>
          <table className="table">
            <thead>
              <tr>
                <th>Metric</th>
                <th>Domain</th>
                <th style={{ textAlign: 'right' }}>Latest Value</th>
                <th>Latest Period</th>
                <th>Trend (last 6)</th>
              </tr>
            </thead>
            <tbody>
              {filteredMetrics.map(([name, v]) => {
                const color = DOMAIN_COLORS[v.category] || DOMAIN_COLORS.default
                const hist6 = v.history.slice(-6)
                const lastVal = v.latest?.value
                const prevVal = hist6.length >= 2 ? hist6[hist6.length - 2]?.value : null
                const pct = prevVal != null && prevVal !== 0 ? ((lastVal - prevVal) / Math.abs(prevVal)) * 100 : null
                return (
                  <tr key={name} style={{ cursor: 'pointer' }} onClick={() => setMetric(name)}>
                    <td>
                      <button
                        style={{ background: 'none', border: 'none', color: 'var(--text)', cursor: 'pointer', fontSize: '.88rem', fontWeight: 500, textAlign: 'left', padding: 0 }}
                        onClick={() => setMetric(name)}
                      >
                        {name}
                      </button>
                    </td>
                    <td><span style={{ background: `${color}18`, color, borderRadius: 4, padding: '2px 7px', fontSize: '.72rem', fontWeight: 600 }}>{v.category || '—'}</span></td>
                    <td style={{ textAlign: 'right', fontFamily: 'var(--font-mono)', fontSize: '.88rem', fontWeight: 600 }}>
                      {fmtNum(lastVal)} <TrendChip pct={pct} />
                    </td>
                    <td style={{ color: 'var(--text-3)', fontSize: '.8rem' }}>{v.latest?.period || '—'}</td>
                    <td><Sparkline data={hist6} color={color} /></td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </Panel>
    </div>
  )
}
