import { useState, useEffect, useCallback } from 'react'
import * as api from '../api'
import { useTranslation } from '../i18n/I18nContext'
import { TrendingUp, Play, BarChart3, Brain, Target, Sparkles } from 'lucide-react'

function StatCard({ label, value, unit, icon: Icon, color = 'blue' }) {
  return (
    <div className="kpi-card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <div className="kpi-label">{label}</div>
          <div className="kpi-value">{value}{unit ? <span style={{ fontSize: '0.7em', color: 'var(--text-muted)' }}> {unit}</span> : ''}</div>
        </div>
        <div className={`kpi-icon-wrap ${color}`}><Icon size={20} /></div>
      </div>
    </div>
  )
}

export default function ForecastingPage() {
  const { t } = useTranslation()
  const [metrics, setMetrics] = useState([])
  const [selectedMetric, setSelectedMetric] = useState('')
  const [periods, setPeriods] = useState(6)
  const [forecast, setForecast] = useState(null)
  const [loading, setLoading] = useState(false)
  const [initLoading, setInitLoading] = useState(true)

  useEffect(() => {
    api.getMetrics().then(res => {
      const list = res.data?.metrics || []
      setMetrics(list)
      if (list.length > 0) setSelectedMetric(list[0])
    }).catch(() => {}).finally(() => setInitLoading(false))
  }, [])

  const runForecast = useCallback(async () => {
    if (!selectedMetric) return
    setLoading(true)
    try {
      const res = await api.runForecast(selectedMetric, periods)
      setForecast(res.data)
    } catch (err) {
      console.error('Forecast error:', err)
      setForecast({ error: err.response?.data?.detail || 'Forecast failed' })
    }
    setLoading(false)
  }, [selectedMetric, periods])

  const fmt = (v) => {
    if (v === null || v === undefined) return '—'
    if (typeof v === 'number') {
      if (Math.abs(v) >= 1e6) return `${(v / 1e6).toFixed(2)}M`
      if (Math.abs(v) >= 1e3) return `${(v / 1e3).toFixed(1)}K`
      return v.toFixed(2)
    }
    return v
  }

  if (initLoading) return <div className="text-center" style={{ padding: 60 }}>{t('loadingMetrics')}</div>

  return (
    <div>
      <h1 className="page-title" style={{ marginBottom: 20 }}><TrendingUp size={24} /> {t('forecasting')}</h1>

      <div className="card" style={{ marginBottom: 20 }}>
        <h3 className="card-title">{t('configureForecast')}</h3>
        <div style={{ display: 'flex', gap: 16, alignItems: 'flex-end', flexWrap: 'wrap' }}>
          <div style={{ flex: 1, minWidth: 200 }}>
            <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: 4, color: 'var(--text-muted)' }}>{t('metric')}</label>
            <select value={selectedMetric} onChange={e => setSelectedMetric(e.target.value)}
              style={{ width: '100%', padding: '8px 12px', borderRadius: 8, border: '1px solid var(--border)', background: 'var(--bg-card)', color: 'var(--text-primary)', fontSize: '0.9rem' }}>
              {metrics.map(m => <option key={m} value={m}>{m}</option>)}
            </select>
          </div>
          <div style={{ minWidth: 120 }}>
            <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: 4, color: 'var(--text-muted)' }}>{t('periodsAhead')}</label>
            <select value={periods} onChange={e => setPeriods(Number(e.target.value))}
              style={{ width: '100%', padding: '8px 12px', borderRadius: 8, border: '1px solid var(--border)', background: 'var(--bg-card)', color: 'var(--text-primary)', fontSize: '0.9rem' }}>
              {[3, 6, 9, 12].map(n => <option key={n} value={n}>{n} {t('months')}</option>)}
            </select>
          </div>
          <button className="btn btn-primary" onClick={runForecast} disabled={loading || !selectedMetric}>
            {loading ? t('running') : <><Play size={14} /> {t('runForecast')}</>}
          </button>
        </div>
      </div>

      {forecast && forecast.error && (
        <div className="card" style={{ borderColor: '#ef4444', background: 'rgba(239,68,68,0.1)' }}>
          <p style={{ color: '#ef4444' }}>⚠️ {forecast.error}</p>
        </div>
      )}

      {forecast && !forecast.error && (
        <>
          <div className="kpi-grid" style={{ marginBottom: 20 }}>
            <StatCard label={t('metric')} value={forecast.metric || selectedMetric} icon={BarChart3} color="blue" />
            <StatCard label={t('model')} value={forecast.model || 'Linear'} icon={Brain} color="purple" />
            <StatCard label={t('r2Score')} value={forecast.r2 !== undefined ? forecast.r2.toFixed(3) : '—'} icon={Target} color="green" />
            <StatCard label={t('forecastPeriods')} value={forecast.forecast?.length || periods} icon={Sparkles} color="cyan" />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
            {forecast.historical && forecast.historical.length > 0 && (
              <div className="card">
                <h3 className="card-title"><TrendingUp size={16} /> {t('historicalData')}</h3>
                <table className="table">
                  <thead><tr><th>Period</th><th>Value</th></tr></thead>
                  <tbody>
                    {forecast.historical.map((h, i) => (
                      <tr key={i}>
                        <td>{h.period || h.month_tag}</td>
                        <td>{fmt(h.value || h.actual)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {forecast.forecast && forecast.forecast.length > 0 && (
              <div className="card">
                <h3 className="card-title"><Sparkles size={16} /> {t('forecast')}</h3>
                <table className="table">
                  <thead><tr><th>{t('period')}</th><th>{t('predicted')}</th><th>{t('lower')}</th><th>{t('upper')}</th></tr></thead>
                  <tbody>
                    {forecast.forecast.map((f, i) => (
                      <tr key={i}>
                        <td>{f.period || f.month_tag}</td>
                        <td style={{ fontWeight: 600 }}>{fmt(f.predicted || f.value)}</td>
                        <td>{fmt(f.lower)}</td>
                        <td>{fmt(f.upper)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      )}

      {!forecast && (
        <div className="card" style={{ textAlign: 'center', padding: 40, color: 'var(--text-muted)' }}>
          <div style={{ marginBottom: 12 }}><Sparkles size={40} /></div>
          <p>{t('forecastPrompt')}</p>
          <p style={{ fontSize: '0.85rem', marginTop: 8 }}>{t('forecastDesc')}</p>
        </div>
      )}
    </div>
  )
}
