import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useTranslation } from '../i18n/I18nContext'
import { useQuery } from '@tanstack/react-query'
import * as api from '../api'
import {
  LayoutDashboard, DollarSign, TrendingDown, Users, Landmark,
  TrendingUp, Bot, Activity, ShieldAlert, ArrowUpRight, ArrowDownRight
} from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

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

function SparklineChart({ data, color }) {
  if (!data || data.length < 2) return null

  const chartData = data.map(d => ({
    period: d.period || d.date || '',
    value: d.value || 0
  }))

  return (
    <div style={{ height: 60 }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="0" vertical={false} />
          <XAxis 
            dataKey="period" 
            hide 
          />
          <YAxis 
            hide 
            domain={['dataMin - 5', 'dataMax + 5']}
          />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: 'var(--card-bg)', 
              border: '1px solid var(--border)',
              borderRadius: '4px',
              fontSize: '0.75rem'
            }}
            itemStyle={{ color: 'var(--text)' }}
          />
          <Line 
            type="monotone" 
            dataKey="value" 
            stroke={color || 'var(--primary)'} 
            strokeWidth={2}
            dot={false}
            activeDot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

function KPICard({ label, value, change, category, history }) {
  const isPositive = change >= 0
  const Icon = ICON_MAP[category] || ICON_MAP.default
  const color = COLOR_MAP[category] || COLOR_MAP.default
  const colorVar = {
    blue: 'var(--primary)',
    red: '#ef4444',
    purple: '#a855f7',
    cyan: '#06b6d4'
  }[color] || 'var(--primary)'

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
      {history && history.length > 0 && (
        <SparklineChart data={history.slice(-6)} color={colorVar} />
      )}
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

  // Use React Query for cached data fetching with automatic retries and stale-time management
  const { data: kpis = [], isLoading: kpisLoading, error: kpisError } = useQuery({
    queryKey: ['kpis'],
    queryFn: () => api.getKPIs().then(res => res.data?.metrics || []),
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 1,
  })

  const { data: health, isLoading: healthLoading } = useQuery({
    queryKey: ['health'],
    queryFn: () => api.getHealth().then(res => res.data),
    staleTime: 2 * 60 * 1000, // 2 minutes
    retry: 1,
  })

  const { data: summary, isLoading: summaryLoading } = useQuery({
    queryKey: ['summary'],
    queryFn: () => api.getSummary().then(res => res.data),
    staleTime: 10 * 60 * 1000, // 10 minutes
    retry: 1,
  })

  const { data: risks = [], isLoading: risksLoading } = useQuery({
    queryKey: ['risks'],
    queryFn: () => api.getRisk().then(res => res.data?.risks || []),
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 1,
  })

  const loading = kpisLoading || healthLoading || summaryLoading || risksLoading

  const formatValue = (val) => {
    if (typeof val !== 'number') return val || '—'
    if (Math.abs(val) >= 1e6) return `$${(val / 1e6).toFixed(1)}M`
    if (Math.abs(val) >= 1e3) return `$${(val / 1e3).toFixed(1)}K`
    return val.toFixed(1)
  }

  // Group KPIs by metric name and get history for each
  const kpiHistory = {}
  kpis.forEach(k => {
    const name = k.metric_name || k.name || 'Unknown'
    if (!kpiHistory[name]) {
      kpiHistory[name] = []
    }
    kpiHistory[name].push({
      period: k.period,
      value: k.value,
      category: k.category
    })
  })

  // Sort history by period and take last 6
  Object.keys(kpiHistory).forEach(name => {
    kpiHistory[name].sort((a, b) => (a.period || '').localeCompare(b.period || ''))
    kpiHistory[name] = kpiHistory[name].slice(-6)
  })

  const topKPIs = kpis.slice(0, 6).map(k => ({
    label: k.metric_name || k.name || 'Metric',
    value: formatValue(k.value),
    change: k.change_pct,
    category: k.category || 'default',
    history: kpiHistory[k.metric_name || k.name] || []
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
