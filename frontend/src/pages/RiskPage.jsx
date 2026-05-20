import { useState, useEffect, useCallback } from 'react'
import * as api from '../api'
import { useTranslation } from '../i18n/I18nContext'
import { ShieldAlert, Search, Lightbulb, Activity, CheckCircle2 } from 'lucide-react'

function StatCard({ label, value, unit, icon }) {
  return (
    <div className="kpi-card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <div className="kpi-label">{label}</div>
          <div className="kpi-value">{value}{unit ? <span style={{ fontSize: '0.7em', color: 'var(--text-muted)' }}> {unit}</span> : ''}</div>
        </div>
        <span style={{ fontSize: '1.5rem' }}>{icon}</span>
      </div>
    </div>
  )
}

export default function RiskPage() {
  const { t } = useTranslation()
  const [risk, setRisk] = useState(null)
  const [anomalies, setAnomalies] = useState(null)
  const [health, setHealth] = useState(null)
  const [loading, setLoading] = useState(true)

  const fetchData = useCallback(async () => {
    setLoading(true)
    const [r, a, h] = await Promise.allSettled([
      api.getRisk(), api.getAnomalies(), api.getHealth(),
    ])
    if (r.status === 'fulfilled') setRisk(r.value.data)
    if (a.status === 'fulfilled') setAnomalies(a.value.data)
    if (h.status === 'fulfilled') setHealth(h.value.data)
    setLoading(false)
  }, [])

  useEffect(() => { fetchData() }, [fetchData])

  const fmt = (v) => {
    if (v === null || v === undefined) return '—'
    if (typeof v === 'number') {
      if (Math.abs(v) >= 1e6) return `${(v / 1e6).toFixed(1)}M`
      if (Math.abs(v) >= 1e3) return `${(v / 1e3).toFixed(1)}K`
      return v % 1 === 0 ? v.toString() : v.toFixed(2)
    }
    return v
  }

  if (loading) return <div className="text-center" style={{ padding: 60 }}>{t('loading')}</div>

  const riskScore = risk?.risk_score ?? risk?.score ?? 0
  const riskColor = riskScore <= 30 ? '#22c55e' : riskScore <= 60 ? '#eab308' : '#ef4444'
  const riskLabel = riskScore <= 30 ? t('lowRisk') : riskScore <= 60 ? t('mediumRisk') : t('highRisk')

  return (
    <div>
      <h1 className="page-title" style={{ marginBottom: 20 }}><ShieldAlert size={24} /> {t('riskRadar')}</h1>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 20, marginBottom: 20 }}>
        {/* Risk Score Gauge */}
        <div className="card" style={{ textAlign: 'center' }}>
          <h3 className="card-title">{t('riskScore')}</h3>
          <div style={{
            width: 130, height: 130, borderRadius: '50%',
            border: `8px solid ${riskColor}`,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            flexDirection: 'column', margin: '16px auto'
          }}>
            <div style={{ fontSize: '2rem', fontWeight: 700, color: riskColor }}>{riskScore}</div>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>/100</div>
          </div>
          <div style={{ fontWeight: 600, color: riskColor }}>{riskLabel}</div>
        </div>

        {/* Health Index */}
        {health && (
          <div className="card" style={{ textAlign: 'center' }}>
            <h3 className="card-title">{t('healthIndex')}</h3>
            <div style={{
              width: 130, height: 130, borderRadius: '50%',
              border: `8px solid ${(health.health_index || 0) >= 70 ? '#22c55e' : '#eab308'}`,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              flexDirection: 'column', margin: '16px auto'
            }}>
              <div style={{ fontSize: '2rem', fontWeight: 700, color: (health.health_index || 0) >= 70 ? '#22c55e' : '#eab308' }}>
                {fmt(health.health_index)}
              </div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>/100</div>
            </div>
            <div style={{ fontWeight: 600, color: (health.health_index || 0) >= 70 ? '#22c55e' : '#eab308' }}>
              {(health.health_index || 0) >= 70 ? t('healthy') : t('needsAttention')}
            </div>
          </div>
        )}

        {/* Risk Summary Stats */}
        <div className="card">
          <h3 className="card-title">{t('riskFactors')}</h3>
          {risk?.volatility !== undefined && (
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid var(--border)' }}>
              <span>{t('revenueVolatility')}</span>
              <span style={{ fontWeight: 600 }}>{fmt(risk.volatility)}</span>
            </div>
          )}
          {risk?.concentration_risk !== undefined && (
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid var(--border)' }}>
              <span>{t('concentration')}</span>
              <span style={{ fontWeight: 600 }}>{fmt(risk.concentration_risk)}</span>
            </div>
          )}
          {risk?.burn_ratio !== undefined && (
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid var(--border)' }}>
              <span>{t('burnRatio')}</span>
              <span style={{ fontWeight: 600 }}>{fmt(risk.burn_ratio)}</span>
            </div>
          )}
          {risk?.growth_deceleration !== undefined && (
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0' }}>
              <span>{t('growthDeceleration')}</span>
              <span style={{ fontWeight: 600 }}>{fmt(risk.growth_deceleration)}</span>
            </div>
          )}
          {risk?.factors && (
            <div style={{ marginTop: 8 }}>
              {Object.entries(risk.factors).map(([k, v]) => (
                <div key={k} style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0', fontSize: '0.85rem' }}>
                  <span style={{ textTransform: 'capitalize' }}>{k.replace(/_/g, ' ')}</span>
                  <span style={{ fontWeight: 600 }}>{fmt(v)}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Anomalies */}
      <div className="card">
        <h3 className="card-title"><Search size={16} /> {t('anomaliesDetected')}</h3>
        {anomalies && anomalies.anomalies && anomalies.anomalies.length > 0 ? (
          <table className="table">
            <thead>
              <tr>
                <th>Metric</th>
                <th>Period</th>
                <th>Value</th>
                <th>Z-Score</th>
                <th>Severity</th>
              </tr>
            </thead>
            <tbody>
              {anomalies.anomalies.map((a, i) => (
                <tr key={i}>
                  <td style={{ fontWeight: 600 }}>{a.metric}</td>
                  <td>{a.period}</td>
                  <td>{fmt(a.value)}</td>
                  <td>{fmt(a.z_score)}</td>
                  <td>
                    <span style={{
                      padding: '2px 8px', borderRadius: 12, fontSize: '0.75rem', fontWeight: 600,
                      background: (a.severity === 'high' || (a.z_score && Math.abs(a.z_score) > 3)) ? 'rgba(239,68,68,0.15)' : 'rgba(234,179,8,0.15)',
                      color: (a.severity === 'high' || (a.z_score && Math.abs(a.z_score) > 3)) ? '#ef4444' : '#eab308',
                    }}>
                      {a.severity || (Math.abs(a.z_score || 0) > 3 ? 'High' : 'Medium')}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div style={{ textAlign: 'center', padding: 30, color: 'var(--text-muted)' }}>
            <div style={{ marginBottom: 8 }}><CheckCircle2 size={32} color="#22c55e" /></div>
            <p>{t('noAnomalies')}</p>
          </div>
        )}
      </div>

      {/* Recommendations */}
      {risk?.recommendations && risk.recommendations.length > 0 && (
        <div className="card" style={{ marginTop: 20 }}>
          <h3 className="card-title"><Lightbulb size={16} /> {t('riskRecommendations')}</h3>
          <ul style={{ paddingLeft: 20, margin: 0 }}>
            {risk.recommendations.map((r, i) => (
              <li key={i} style={{ padding: '6px 0', lineHeight: 1.5 }}>{r}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
