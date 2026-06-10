import { useQuery } from '@tanstack/react-query'
import * as api from '../api'
import { useTranslation } from '../i18n/I18nContext'
import { ShieldAlert, Search, Activity, CheckCircle2, HeartPulse } from 'lucide-react'
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer, Tooltip } from 'recharts'
import { PageHeader, Panel, Grid, Loading, AskCopilot, fmtNum } from '../components/ui'

const ACCENT = 'var(--p-risk)'

function Gauge({ label, score, icon: Icon }) {
  const s = Math.round(score ?? 0)
  const color = s >= 70 ? 'var(--ok)' : s >= 50 ? 'var(--warn)' : 'var(--bad)'
  return (
    <Panel style={{ textAlign: 'center' }}>
      <h3 className="card-title" style={{ justifyContent: 'center' }}>{Icon && <Icon size={16} />}{label}</h3>
      <div style={{
        width: 120, height: 120, borderRadius: '50%', margin: '14px auto',
        display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column',
        background: `conic-gradient(${color} ${s * 3.6}deg, var(--surface-3) 0)`,
      }}>
        <div style={{ width: 96, height: 96, borderRadius: '50%', background: 'var(--surface)', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: '1.8rem', fontWeight: 700, color }}>{s}</div>
          <div style={{ fontSize: '.66rem', color: 'var(--text-3)' }}>/100</div>
        </div>
      </div>
    </Panel>
  )
}

export default function RiskPage() {
  const { t } = useTranslation()
  const risk = useQuery({ queryKey: ['risk'], queryFn: () => api.getRisk().then(r => r.data), retry: 1 })
  const anom = useQuery({ queryKey: ['anomalies'], queryFn: () => api.getAnomalies().then(r => r.data?.anomalies || []), retry: 1 })
  const health = useQuery({ queryKey: ['health'], queryFn: () => api.getHealth().then(r => r.data), retry: 1 })

  if (risk.isLoading) return <Loading />
  const r = risk.data || {}
  const radar = [
    { subject: 'Liquidity', value: r.liquidity_score ?? 0 },
    { subject: 'Execution', value: r.execution_score ?? 0 },
    { subject: 'Stability', value: 100 - (r.volatility_score ?? 0) },
    { subject: 'Diversification', value: 100 - (r.concentration_score ?? 0) },
    { subject: 'Anomaly-free', value: 100 - (r.anomaly_score ?? 0) },
  ]

  return (
    <div>
      <PageHeader icon={ShieldAlert} accent={ACCENT} title={t('navRisk') || 'Risk Radar'}
        subtitle={t('riskSubtitle') || 'Composite risk score, factor radar & anomaly watchlist'}
        actions={<AskCopilot q="What are our biggest risks right now and what should I do about the recent anomalies?" />} />

      <Grid min={240}>
        <Gauge label={t('riskScore') || 'Risk Score'} score={r.score} icon={ShieldAlert} />
        <Gauge label={t('healthIndex') || 'Health Index'} score={health.data?.score ?? health.data?.health_index} icon={HeartPulse} />
        <Panel title={t('riskComponents') || 'Risk components'} icon={Activity} style={{ gridColumn: 'span 2' }}>
          <div style={{ height: 220 }}>
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={radar} outerRadius="72%">
                <PolarGrid stroke="var(--border)" />
                <PolarAngleAxis dataKey="subject" tick={{ fontSize: 11, fill: 'var(--text-3)' }} />
                <PolarRadiusAxis angle={90} domain={[0, 100]} tick={{ fontSize: 9, fill: 'var(--text-3)' }} />
                <Tooltip contentStyle={{ background: 'var(--surface-2)', border: '1px solid var(--border-2)', borderRadius: 8, fontSize: '.78rem' }} />
                <Radar name="Score" dataKey="value" stroke={ACCENT} fill={ACCENT} fillOpacity={0.45} strokeWidth={2} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
          <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', marginTop: 8, fontSize: '.82rem', color: 'var(--text-2)' }}>
            <span>Label: <b style={{ color: 'var(--text)' }}>{r.label}</b></span>
            <span>Volatility: <b style={{ color: 'var(--text)' }}>{fmtNum(r.volatility)}%</b></span>
            <span>Anomalies: <b style={{ color: 'var(--text)' }}>{fmtNum(r.anomaly_count)}</b></span>
          </div>
        </Panel>
      </Grid>

      <Panel title={t('anomaliesDetected') || 'Anomaly watchlist'} icon={Search} style={{ marginTop: 18 }}
        actions={<AskCopilot q="Explain each detected anomaly and the likely root cause." label="Explain anomalies" />}>
        {(anom.data || []).length > 0 ? (
          <table className="table">
            <thead><tr><th>Metric</th><th>Category</th><th>Period</th><th>Value</th><th>Z-Score</th><th>Severity</th></tr></thead>
            <tbody>
              {anom.data.map((a, i) => {
                const z = Math.abs(a.z_score ?? a.zscore ?? 0)
                const high = a.severity === 'high' || z > 3
                return (
                  <tr key={i}>
                    <td style={{ fontWeight: 600 }}>{a.metric}</td>
                    <td>{a.category || '—'}</td>
                    <td>{a.period}</td>
                    <td>{fmtNum(a.value)}</td>
                    <td>{fmtNum(a.z_score ?? a.zscore)}</td>
                    <td><span className={`badge ${high ? 'bad' : 'warn'}`}>{a.severity || (z > 3 ? 'high' : 'medium')}</span></td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        ) : (
          <div style={{ textAlign: 'center', padding: 30, color: 'var(--text-3)' }}>
            <CheckCircle2 size={30} style={{ color: 'var(--ok)', marginBottom: 8 }} />
            <p>{t('noAnomalies') || 'No anomalies detected.'}</p>
          </div>
        )}
      </Panel>
    </div>
  )
}
