import { useState, useEffect, useCallback } from 'react'
import * as api from '../api'
import { useTranslation } from '../i18n/I18nContext'
import { TrendingUp, Play, BarChart3, Brain, Target, Sparkles } from 'lucide-react'
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Line } from 'recharts'
import { PageHeader, Stat, StatGrid, Panel, Grid, Loading, Empty, AskCopilot, fmtNum } from '../components/ui'

const TIP = { background: 'var(--surface-2)', border: '1px solid var(--border-2)', borderRadius: 8, fontSize: '.78rem', color: 'var(--text)' }
const AXIS = { fontSize: 11, fill: 'var(--text-3)' }

function ForecastChart({ forecast, t }) {
  const hist = (forecast.historical || []).map(h => ({ period: h.period || h.month_tag, value: h.value ?? h.actual }))
  const fc = (forecast.forecast || []).map(f => {
    const lower = f.lower, upper = f.upper
    return {
      period: f.period || f.month_tag, value: f.predicted ?? f.value, lower, upper,
      // Ranged datum [lower, upper] → a single shaded Monte-Carlo band region.
      band: (lower != null && upper != null) ? [lower, upper] : undefined,
    }
  })
  const data = [...hist, ...fc]
  if (!data.length) return <Empty text="No forecast data." />
  const hasCI = fc.some(f => f.lower != null && f.upper != null)
  return (
    <div style={{ height: 300 }}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 5, right: 10, left: -10, bottom: 0 }}>
          <defs>
            <linearGradient id="fc" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="var(--primary-2)" stopOpacity={0.32} /><stop offset="100%" stopColor="var(--primary-2)" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="mcBand" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="var(--accent)" stopOpacity={0.24} /><stop offset="100%" stopColor="var(--accent)" stopOpacity={0.05} />
            </linearGradient>
            <linearGradient id="fcLine" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor="#4f46e5" /><stop offset="55%" stopColor="#2563eb" /><stop offset="100%" stopColor="#22d3ee" />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
          <XAxis dataKey="period" tick={AXIS} axisLine={false} tickLine={false} />
          <YAxis tick={AXIS} axisLine={false} tickLine={false} width={52} />
          <Tooltip contentStyle={TIP} />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          {/* Monte-Carlo confidence band — semi-transparent ranged fill behind the projection */}
          {hasCI && <Area type="monotone" dataKey="band" stroke="none" fill="url(#mcBand)" name={t('confidenceBand') || 'Confidence band'} connectNulls isAnimationActive={false} />}
          {/* main projection — brand gradient stroke + soft cyan fill */}
          <Area type="monotone" dataKey="value" stroke="url(#fcLine)" strokeWidth={2.4} fill="url(#fc)" name={t('predicted') || 'Projection'} />
          {/* dashed CI bounds in the band accent */}
          {hasCI && <Line type="monotone" dataKey="upper" stroke="var(--accent)" strokeWidth={1} strokeDasharray="4 4" dot={false} legendType="none" name="" connectNulls />}
          {hasCI && <Line type="monotone" dataKey="lower" stroke="var(--accent)" strokeWidth={1} strokeDasharray="4 4" dot={false} legendType="none" name="" connectNulls />}
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}

export default function ForecastingPage() {
  const { t } = useTranslation()
  const [metrics, setMetrics] = useState([])
  const [metric, setMetric] = useState('')
  const [periods, setPeriods] = useState(6)
  const [forecast, setForecast] = useState(null)
  const [loading, setLoading] = useState(false)
  const [init, setInit] = useState(true)

  useEffect(() => {
    api.getMetrics().then(r => { const l = r.data?.metrics || []; setMetrics(l); if (l[0]) setMetric(l[0]) })
      .catch(() => {}).finally(() => setInit(false))
  }, [])

  const run = useCallback(async () => {
    if (!metric) return
    setLoading(true)
    try { setForecast((await api.runForecast(metric, periods)).data) }
    catch (e) { setForecast({ error: e.response?.data?.detail || 'Forecast failed' }) }
    setLoading(false)
  }, [metric, periods])

  if (init) return <Loading label={t('loadingMetrics') || 'Loading metrics…'} />

  return (
    <div>
      <PageHeader icon={TrendingUp} title={t('navForecasting') || 'Forecasting'}
        subtitle={t('fcSubtitle') || 'Monte-Carlo projections with confidence intervals'}
        actions={metric && <AskCopilot q={`Forecast ${metric} and explain the trend, drivers and confidence.`} />} />

      <Panel title={t('configureForecast') || 'Configure forecast'} icon={Brain}>
        <div style={{ display: 'flex', gap: 14, alignItems: 'flex-end', flexWrap: 'wrap' }}>
          <div style={{ flex: 1, minWidth: 220 }}>
            <label className="form-label">{t('metric') || 'Metric'}</label>
            <select className="form-input" value={metric} onChange={e => setMetric(e.target.value)}>
              {metrics.map(m => <option key={m} value={m}>{m}</option>)}
            </select>
          </div>
          <div style={{ minWidth: 140 }}>
            <label className="form-label">{t('periodsAhead') || 'Periods ahead'}</label>
            <select className="form-input" value={periods} onChange={e => setPeriods(Number(e.target.value))}>
              {[3, 6, 9, 12].map(n => <option key={n} value={n}>{n} {t('months') || 'months'}</option>)}
            </select>
          </div>
          <button className="btn btn-primary" onClick={run} disabled={loading || !metric}>
            {loading ? (t('running') || 'Running…') : <><Play size={14} /> {t('runForecast') || 'Run forecast'}</>}
          </button>
        </div>
      </Panel>

      {forecast?.error && <div className="alert alert-danger" style={{ marginTop: 18 }}>⚠️ {forecast.error}</div>}

      {forecast && !forecast.error && (
        <>
          <StatGrid style={{ marginTop: 18 }}>
            <Stat label={t('metric') || 'Metric'} value={forecast.metric || metric} icon={BarChart3} />
            <Stat label={t('model') || 'Model'} value={forecast.model || 'Linear'} icon={Brain} accent="var(--accent)" />
            <Stat label={t('r2Score') || 'R² score'} value={forecast.r2 != null ? forecast.r2.toFixed(3) : '—'} icon={Target} accent="var(--ok)" />
            <Stat label={t('forecastPeriods') || 'Periods'} value={fmtNum(forecast.forecast?.length || periods)} icon={Sparkles} />
          </StatGrid>

          <Panel title={t('forecastChart') || 'Forecast'} icon={TrendingUp} style={{ marginTop: 18 }}>
            <ForecastChart forecast={forecast} t={t} />
          </Panel>

          <Panel title={t('forecast') || 'Projected values'} icon={Sparkles} style={{ marginTop: 18 }}>
            <table className="table">
              <thead><tr><th>{t('period') || 'Period'}</th><th>{t('predicted') || 'Predicted'}</th><th>{t('lower') || 'Lower'}</th><th>{t('upper') || 'Upper'}</th></tr></thead>
              <tbody>
                {(forecast.forecast || []).map((f, i) => (
                  <tr key={i}>
                    <td>{f.period || f.month_tag}</td>
                    <td style={{ fontWeight: 600, fontFamily: 'var(--font-mono)' }}>{fmtNum(f.predicted ?? f.value)}</td>
                    <td style={{ color: 'var(--text-3)' }}>{fmtNum(f.lower)}</td>
                    <td style={{ color: 'var(--text-3)' }}>{fmtNum(f.upper)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Panel>
        </>
      )}

      {!forecast && (
        <Panel style={{ marginTop: 18, textAlign: 'center', padding: 40 }}>
          <Sparkles size={38} style={{ color: 'var(--primary)', margin: '0 auto 12px' }} />
          <p style={{ color: 'var(--text-2)' }}>{t('forecastPrompt') || 'Pick a metric and run a forecast.'}</p>
        </Panel>
      )}
    </div>
  )
}
