import { useState, useEffect, useCallback, useRef } from 'react'
import * as api from '../api'
import { useTranslation } from '../i18n/I18nContext'
import {
  Activity, Cpu, HardDrive, MemoryStick, Clock, Wifi, WifiOff,
  RefreshCcw, Users, MessageSquare, Zap, AlertTriangle, Server,
  Database, Bot, Gauge
} from 'lucide-react'

function MetricCard({ icon: Icon, label, value, unit, color = 'blue', percent }) {
  return (
    <div className="kpi-card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <div className="kpi-label">{label}</div>
          <div className="kpi-value">{value}{unit ? <span style={{ fontSize: '0.7em', color: 'var(--text-muted)' }}> {unit}</span> : ''}</div>
        </div>
        <div className={`kpi-icon-wrap ${color}`}>
          <Icon size={20} />
        </div>
      </div>
      {percent !== undefined && (
        <div style={{ marginTop: 8 }}>
          <div style={{ height: 4, borderRadius: 2, background: 'var(--border)', overflow: 'hidden' }}>
            <div style={{
              height: '100%', borderRadius: 2, width: `${Math.min(100, percent)}%`,
              background: percent > 85 ? 'var(--danger)' : percent > 65 ? 'var(--warning)' : 'var(--success)',
              transition: 'width 0.5s ease',
            }} />
          </div>
        </div>
      )}
    </div>
  )
}

function ServiceRow({ name, online, t }) {
  return (
    <div style={{
      display: 'flex', justifyContent: 'space-between', alignItems: 'center',
      padding: '10px 0', borderBottom: '1px solid var(--border)',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <Server size={16} style={{ color: 'var(--text-muted)' }} />
        <span style={{ fontWeight: 500 }}>{name}</span>
      </div>
      <span className={`badge badge-${online ? 'success' : 'danger'}`}>
        {online ? <><Wifi size={12} /> {t('online')}</> : <><WifiOff size={12} /> {t('offline')}</>}
      </span>
    </div>
  )
}

export default function MonitoringPage() {
  const { t } = useTranslation()
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [autoRefresh, setAutoRefresh] = useState(false)
  const intervalRef = useRef(null)

  const fetchStats = useCallback(async (silent = false) => {
    if (!silent) setLoading(true)
    else setRefreshing(true)
    try {
      const res = await api.getMonitoringStats()
      setStats(res.data)
    } catch { /* silent */ }
    setLoading(false)
    setRefreshing(false)
  }, [])

  useEffect(() => { fetchStats() }, [fetchStats])

  useEffect(() => {
    if (autoRefresh) {
      intervalRef.current = setInterval(() => fetchStats(true), 15000)
    } else {
      clearInterval(intervalRef.current)
    }
    return () => clearInterval(intervalRef.current)
  }, [autoRefresh, fetchStats])

  const fmt = (v) => {
    if (v === null || v === undefined) return '—'
    if (typeof v === 'number') return v % 1 === 0 ? v.toString() : v.toFixed(1)
    return v
  }

  if (loading) {
    return <div className="text-center" style={{ padding: 60 }}>{t('loading')}</div>
  }

  const services = [
    { name: 'FastAPI Server', online: true },
    { name: 'PostgreSQL', online: (stats?.total_users ?? 0) > 0 },
    { name: 'DuckDB Analytics', online: true },
    { name: 'ChromaDB Vector Store', online: true },
    { name: 'Groq LLM', online: true },
    { name: 'n8n Automations', online: !!stats?.n8n_connected },
    { name: 'Prometheus', online: !!stats?.prometheus_connected },
    { name: 'Grafana', online: !!stats?.grafana_connected },
  ]

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title"><Activity size={24} /> {t('monitoring')}</h1>
        <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.8rem', cursor: 'pointer', color: 'var(--text-secondary)' }}>
            <input type="checkbox" checked={autoRefresh} onChange={e => setAutoRefresh(e.target.checked)} />
            {t('autoRefresh')} (15s)
          </label>
          <button className="btn btn-outline btn-sm" onClick={() => fetchStats(true)} disabled={refreshing}>
            <RefreshCcw size={14} className={refreshing ? 'spin' : ''} />
            {refreshing ? t('refreshing') : t('refresh')}
          </button>
        </div>
      </div>

      {/* Usage Metrics */}
      <div className="kpi-grid" style={{ marginBottom: 24 }}>
        <MetricCard icon={Users} label={t('totalUsers')} value={fmt(stats?.total_users)} color="blue" />
        <MetricCard icon={MessageSquare} label={t('totalSessions')} value={fmt(stats?.total_sessions)} color="purple" />
        <MetricCard icon={MessageSquare} label={t('totalMessages')} value={fmt(stats?.total_messages)} color="cyan" />
        <MetricCard icon={Zap} label={t('todayMessages')} value={fmt(stats?.today_messages)} color="green" />
      </div>

      {/* System Resources */}
      <div className="kpi-grid" style={{ marginBottom: 24 }}>
        <MetricCard icon={Cpu} label={t('cpuUsage')} value={fmt(stats?.cpu_percent)} unit="%" color="blue" percent={stats?.cpu_percent} />
        <MetricCard icon={MemoryStick} label={t('memoryUsage')} value={fmt(stats?.memory_percent)} unit="%" color="purple" percent={stats?.memory_percent} />
        <MetricCard icon={HardDrive} label={t('diskUsage')} value={fmt(stats?.disk_percent)} unit="%" color="cyan" percent={stats?.disk_percent} />
        <MetricCard icon={AlertTriangle} label={t('errorRate')} value={fmt(stats?.error_rate)} unit="%" color="red" />
      </div>

      {/* Performance & AI */}
      <div className="kpi-grid" style={{ marginBottom: 24 }}>
        <MetricCard icon={Clock} label={t('avgLatency')} value={fmt(stats?.avg_latency)} unit="ms" color="blue" />
        <MetricCard icon={Gauge} label={t('totalRequests')} value={fmt(stats?.total_requests)} color="purple" />
        <MetricCard icon={Bot} label={t('aiTokens')} value={fmt(stats?.ai_tokens)} color="cyan" />
      </div>

      {/* Service Status */}
      <div className="card">
        <h3 className="card-title"><Server size={16} /> {t('serviceStatus')}</h3>
        {services.map((s, i) => (
          <ServiceRow key={i} name={s.name} online={s.online} t={t} />
        ))}
      </div>
    </div>
  )
}
