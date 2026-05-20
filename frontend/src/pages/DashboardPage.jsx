import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useTranslation } from '../i18n/I18nContext'
import * as api from '../api'
import {
  LayoutDashboard, DollarSign, TrendingDown, Users, Landmark,
  TrendingUp, Bot, Activity, ShieldAlert, ArrowUpRight, ArrowDownRight
} from 'lucide-react'

const ICON_MAP = {
  revenue: DollarSign,
  cost: TrendingDown,
  hr: Users,
  default: Activity,
}

const COLOR_MAP = {
  revenue: 'blue',
  cost: 'red',
  hr: 'purple',
  default: 'cyan',
}

function KPICard({ label, value, change, category }) {
  const isPositive = change >= 0
  const Icon = ICON_MAP[category] || ICON_MAP.default
  const color = COLOR_MAP[category] || COLOR_MAP.default

  return (
    <div className="kpi-card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <div className="kpi-label">{label}</div>
          <div className="kpi-value">{value}</div>
        </div>
        <div className={`kpi-icon-wrap ${color}`}>
          <Icon size={20} />
        </div>
      </div>
      {change !== undefined && (
        <div className={`kpi-change ${isPositive ? 'positive' : 'negative'}`}>
          {isPositive ? <ArrowUpRight size={13} /> : <ArrowDownRight size={13} />}
          {Math.abs(change).toFixed(1)}%
        </div>
      )}
    </div>
  )
}

function HealthGauge({ score, t }) {
  const color = score >= 80 ? 'var(--success)' : score >= 60 ? 'var(--warning)' : 'var(--danger)'
  const label = score >= 80 ? t('excellent') : score >= 60 ? t('moderate') : t('atRisk')
  return (
    <div className="card" style={{ textAlign: 'center' }}>
      <h3 className="card-title"><Activity size={16} /> {t('healthIndex')}</h3>
      <div className="health-gauge" style={{ border: `6px solid ${color}` }}>
        <div className="health-gauge-value" style={{ color }}>{score}</div>
        <div className="health-gauge-label">/100</div>
      </div>
      <div className="health-gauge-rating" style={{ color }}>{label}</div>
    </div>
  )
}

export default function DashboardPage() {
  const { user } = useAuth()
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [kpis, setKpis] = useState([])
  const [health, setHealth] = useState(null)
  const [summary, setSummary] = useState(null)
  const [risks, setRisks] = useState([])
  const [loading, setLoading] = useState(true)

  const fetchDashboard = useCallback(async () => {
    setLoading(true)
    try {
      const [kpiRes, healthRes, summaryRes, riskRes] = await Promise.allSettled([
        api.getKPIs(),
        api.getHealth(),
        api.getSummary(),
        api.getRisk(),
      ])

      if (kpiRes.status === 'fulfilled') setKpis(kpiRes.value.data?.metrics || [])
      if (healthRes.status === 'fulfilled') setHealth(healthRes.value.data)
      if (summaryRes.status === 'fulfilled') setSummary(summaryRes.value.data)
      if (riskRes.status === 'fulfilled') setRisks(riskRes.value.data?.risks || [])
    } catch {
      // silent
    }
    setLoading(false)
  }, [])

  useEffect(() => { fetchDashboard() }, [fetchDashboard])

  const formatValue = (val) => {
    if (typeof val !== 'number') return val || '—'
    if (Math.abs(val) >= 1e6) return `$${(val / 1e6).toFixed(1)}M`
    if (Math.abs(val) >= 1e3) return `$${(val / 1e3).toFixed(1)}K`
    return val.toFixed(1)
  }

  const topKPIs = kpis.slice(0, 6).map(k => ({
    label: k.metric_name || k.name || 'Metric',
    value: formatValue(k.value),
    change: k.change_pct,
    category: k.category || 'default',
  }))

  if (topKPIs.length === 0 && !loading) {
    topKPIs.push(
      { label: 'Revenue', value: '—', category: 'revenue' },
      { label: 'Net Margin', value: '—', category: 'revenue' },
      { label: 'Employees', value: '—', category: 'hr' },
      { label: 'Cash Runway', value: '—', category: 'default' },
    )
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">
            <LayoutDashboard size={24} />
            {t('welcome')}, {user?.full_name || user?.username}
          </h1>
          <p className="page-subtitle">
            {new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
          </p>
        </div>
        <button className="btn btn-primary" onClick={() => navigate('/chat')}>
          <Bot size={16} /> {t('askAssistant')}
        </button>
      </div>

      {loading ? (
        <div className="loading-overlay">
          <div className="spinner" style={{ width: 32, height: 32 }} />
          <span>{t('loadingDashboard')}</span>
        </div>
      ) : (
        <>
          <div className="kpi-grid">
            {topKPIs.map((kpi, i) => (
              <KPICard key={i} {...kpi} />
            ))}
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: 20, marginTop: 20 }}>
            <HealthGauge score={health?.health_index ?? health?.score ?? 72} t={t} />

            <div className="card">
              <h3 className="card-title"><TrendingUp size={16} /> {t('executiveSummary')}</h3>
              {summary?.summary ? (
                <p style={{ lineHeight: 1.7, color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                  {summary.summary}
                </p>
              ) : (
                <p style={{ color: 'var(--text-muted)' }}>
                  {t('noSummary')}
                </p>
              )}
            </div>
          </div>

          {risks.length > 0 && (
            <div className="card" style={{ marginTop: 20 }}>
              <h3 className="card-title"><ShieldAlert size={16} /> {t('riskIndicators')}</h3>
              <table className="table">
                <thead>
                  <tr>
                    <th>{t('risk')}</th>
                    <th>{t('severity')}</th>
                    <th>{t('score')}</th>
                  </tr>
                </thead>
                <tbody>
                  {risks.slice(0, 5).map((r, i) => (
                    <tr key={i}>
                      <td>{r.name || r.description || 'Unknown'}</td>
                      <td>
                        <span className={`badge badge-${r.severity === 'high' ? 'danger' : r.severity === 'medium' ? 'warning' : 'success'}`}>
                          {r.severity || 'medium'}
                        </span>
                      </td>
                      <td>{r.score ?? '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </div>
  )
}
