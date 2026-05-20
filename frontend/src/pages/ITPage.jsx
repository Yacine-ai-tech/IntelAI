import { useState, useEffect, useCallback } from 'react'
import * as api from '../api'
import { useTranslation } from '../i18n/I18nContext'
import {
  Monitor, BarChart3, Ticket, Lock, Server, Rocket,
  CircleDot, Timer, Flame, ClipboardList, Shield, HardDrive, Cloud,
  FolderOpen, Wrench, CheckCircle2, MessageSquare, ArrowUpCircle,
  Unlock, Bug, Fish, Ban, FlaskConical, DatabaseBackup,
  Cpu, Brain, Globe, User, Zap, XCircle, Activity
} from 'lucide-react'

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

export default function ITPage() {
  const { t } = useTranslation()
  const [overview, setOverview] = useState(null)
  const [tickets, setTickets] = useState(null)
  const [security, setSecurity] = useState(null)
  const [infra, setInfra] = useState(null)
  const [devops, setDevops] = useState(null)
  const [health, setHealth] = useState(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('overview')

  const fetchData = useCallback(async () => {
    setLoading(true)
    const [o, t, s, inf, d, h] = await Promise.allSettled([
      api.getITOverview(), api.getITTickets(), api.getITSecurity(),
      api.getITInfrastructure(), api.getITDevOps(), api.getITHealth(),
    ])
    if (o.status === 'fulfilled') setOverview(o.value.data)
    if (t.status === 'fulfilled') setTickets(t.value.data)
    if (s.status === 'fulfilled') setSecurity(s.value.data)
    if (inf.status === 'fulfilled') setInfra(inf.value.data)
    if (d.status === 'fulfilled') setDevops(d.value.data)
    if (h.status === 'fulfilled') setHealth(h.value.data)
    setLoading(false)
  }, [])

  useEffect(() => { fetchData() }, [fetchData])

  const fmt = (v) => {
    if (v === null || v === undefined) return '—'
    if (typeof v === 'number') {
      if (Math.abs(v) >= 1e6) return `$${(v / 1e6).toFixed(1)}M`
      if (Math.abs(v) >= 1e3) return `$${(v / 1e3).toFixed(1)}K`
      return v % 1 === 0 ? v.toString() : v.toFixed(1)
    }
    return v
  }

  const tabs = [
    { id: 'overview', label: t('overview'), Icon: BarChart3 },
    { id: 'tickets', label: t('tickets'), Icon: Ticket },
    { id: 'security', label: t('security'), Icon: Lock },
    { id: 'infra', label: t('infrastructure'), Icon: Server },
    { id: 'devops', label: t('devops'), Icon: Rocket },
  ]

  if (loading) return <div className="text-center" style={{ padding: 60 }}>{t('loadingIT')}</div>

  return (
    <div>
      <h1 className="page-title" style={{ marginBottom: 20 }}><Monitor size={24} /> {t('itOperations')}</h1>

      <div className="tab-bar">
        {tabs.map(tab => (
          <button key={tab.id} className={`tab-btn${activeTab === tab.id ? ' active' : ''}`}
            onClick={() => setActiveTab(tab.id)}>
            <tab.Icon size={15} /> {tab.label}
          </button>
        ))}
      </div>

      {activeTab === 'overview' && overview && (
        <>
          <div className="kpi-grid">
            <StatCard label={t('systemUptime')} value={fmt(overview.uptime_pct)} unit="%" icon={CircleDot} color="green" />
            <StatCard label={t('openTickets')} value={fmt(overview.open_tickets)} icon={Ticket} color="blue" />
            <StatCard label={t('mttr')} value={fmt(overview.mttr_hours)} unit="hrs" icon={Timer} color="purple" />
            <StatCard label={t('incidents')} value={fmt(overview.incidents_month)} icon={Flame} color="red" />
            <StatCard label={t('slaCompliance')} value={fmt(overview.sla_compliance)} unit="%" icon={ClipboardList} color="cyan" />
            <StatCard label={t('securityScore')} value={fmt(overview.security_score)} unit="/100" icon={Lock} color="green" />
            <StatCard label={t('activeServers')} value={fmt(overview.active_servers)} icon={Server} color="blue" />
            <StatCard label={t('cloudSpend')} value={fmt(overview.cloud_spend)} icon={Cloud} color="purple" />
            <StatCard label={t('deployFrequency')} value={fmt(overview.deployment_frequency)} unit="/mo" icon={Rocket} color="cyan" />
            <StatCard label={t('changeFailure')} value={fmt(overview.change_failure_rate)} unit="%" icon={Activity} color="red" />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: 20, marginTop: 20 }}>
            {health && (
              <div className="card" style={{ textAlign: 'center' }}>
                <h3 className="card-title">{t('itHealthScore')}</h3>
                <div style={{
                  width: 120, height: 120, borderRadius: '50%',
                  border: `6px solid ${health.color}`,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  flexDirection: 'column', margin: '16px auto'
                }}>
                  <div style={{ fontSize: '1.8rem', fontWeight: 700, color: health.color }}>{health.score}</div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>/100</div>
                </div>
                <div style={{ fontWeight: 600, color: health.color }}>{health.rating}</div>
                {health.factors && (
                  <div style={{ marginTop: 16, textAlign: 'left' }}>
                    {Object.entries(health.factors).map(([k, v]) => (
                      <div key={k} style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0', fontSize: '0.85rem' }}>
                        <span style={{ textTransform: 'capitalize' }}>{k.replace(/_/g, ' ')}</span>
                        <span style={{ fontWeight: 600 }}>{v}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
            <div className="card">
              <h3 className="card-title">{t('monthlyTrends')}</h3>
              {overview.trends && overview.trends.length > 0 ? (
                <table className="table">
                  <thead><tr><th>Period</th><th>Uptime</th><th>Tickets</th><th>Incidents</th></tr></thead>
                  <tbody>
                    {overview.trends.slice(-8).map((t, i) => (
                      <tr key={i}>
                        <td>{t.period}</td>
                        <td>{fmt(t.uptime)}%</td>
                        <td>{fmt(t.tickets)}</td>
                        <td>{fmt(t.incidents)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : <p style={{ color: 'var(--text-muted)' }}>No trend data available</p>}
            </div>
          </div>
        </>
      )}

      {activeTab === 'tickets' && tickets && (
        <>
          <div className="kpi-grid">
            <StatCard label={t('ticketOpen')} value={fmt(tickets.open)} icon={FolderOpen} color="blue" />
            <StatCard label={t('ticketInProgress')} value={fmt(tickets.in_progress)} icon={Wrench} color="purple" />
            <StatCard label={t('ticketResolved')} value={fmt(tickets.resolved)} icon={CheckCircle2} color="green" />
            <StatCard label={t('avgResolution')} value={fmt(tickets.avg_resolution_time)} unit="hrs" icon={Timer} color="cyan" />
            <StatCard label={t('firstResponse')} value={fmt(tickets.first_response_time)} unit="hrs" icon={MessageSquare} color="blue" />
            <StatCard label={t('escalationRate')} value={fmt(tickets.escalation_rate)} unit="%" icon={ArrowUpCircle} color="red" />
          </div>
          {tickets.by_priority && (
            <div className="card" style={{ marginTop: 20 }}>
              <h3 className="card-title">{t('byPriority')}</h3>
              <table className="table">
                <thead><tr><th>{t('priority')}</th><th>{t('count')}</th></tr></thead>
                <tbody>
                  {Object.entries(tickets.by_priority).map(([k, v]) => (
                    <tr key={k}><td>{k}</td><td>{v}</td></tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          {tickets.by_category && (
            <div className="card" style={{ marginTop: 20 }}>
              <h3 className="card-title">{t('byCategory')}</h3>
              <table className="table">
                <thead><tr><th>{t('category')}</th><th>{t('count')}</th></tr></thead>
                <tbody>
                  {Object.entries(tickets.by_category).map(([k, v]) => (
                    <tr key={k}><td style={{ textTransform: 'capitalize' }}>{k.replace(/_/g, ' ')}</td><td>{v}</td></tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}

      {activeTab === 'security' && security && (
        <div className="kpi-grid">
          <StatCard label={t('securityScore')} value={fmt(security.security_score)} unit="/100" icon={Shield} color="green" />
          <StatCard label={t('vulnerabilities')} value={fmt(security.open_vulnerabilities)} icon={Unlock} color="red" />
          <StatCard label={t('patchesPending')} value={fmt(security.patches_pending)} icon={Wrench} color="purple" />
          <StatCard label={t('phishingBlocked')} value={fmt(security.phishing_attempts_blocked)} icon={Fish} color="cyan" />
          <StatCard label={t('failedLogins')} value={fmt(security.failed_login_attempts)} icon={Ban} color="red" />
          <StatCard label={t('compliance')} value={fmt(security.compliance_rate)} unit="%" icon={ClipboardList} color="blue" />
          <StatCard label={t('penTestPass')} value={fmt(security.pen_test_pass_rate)} unit="%" icon={FlaskConical} color="green" />
          <StatCard label={t('backupSuccess')} value={fmt(security.backup_success_rate)} unit="%" icon={DatabaseBackup} color="purple" />
        </div>
      )}

      {activeTab === 'infra' && infra && (
        <div className="kpi-grid">
          <StatCard label={t('cpuUtil')} value={fmt(infra.cpu_utilization)} unit="%" icon={Cpu} color="blue" />
          <StatCard label={t('memUsage')} value={fmt(infra.memory_usage)} unit="%" icon={Brain} color="purple" />
          <StatCard label={t('diskUsagePct')} value={fmt(infra.disk_usage)} unit="%" icon={HardDrive} color="cyan" />
          <StatCard label={t('networkUsage')} value={fmt(infra.network_usage)} unit="%" icon={Globe} color="blue" />
          <StatCard label={t('activeUsers')} value={fmt(infra.active_users)} icon={User} color="green" />
          <StatCard label={t('apiLatency')} value={fmt(infra.api_latency)} unit="ms" icon={Zap} color="purple" />
          <StatCard label={t('errorRate')} value={fmt(infra.error_rate)} unit="%" icon={XCircle} color="red" />
          <StatCard label={t('uptime')} value={fmt(infra.uptime)} unit="%" icon={CircleDot} color="green" />
        </div>
      )}

      {activeTab === 'devops' && devops && (
        <>
          <h3 style={{ marginBottom: 12 }}>{t('doraMetrics')}</h3>
          <div className="kpi-grid">
            <StatCard label={t('deployFrequency')} value={fmt(devops.deployment_frequency)} unit="/mo" icon={Rocket} color="cyan" />
            <StatCard label={t('leadTime')} value={fmt(devops.lead_time_hours)} unit="hrs" icon={Timer} color="blue" />
            <StatCard label={t('changeFailure')} value={fmt(devops.change_failure_rate)} unit="%" icon={Activity} color="red" />
            <StatCard label={t('mttr')} value={fmt(devops.mttr_hours)} unit="hrs" icon={Wrench} color="purple" />
            <StatCard label={t('codeCoverage')} value={fmt(devops.code_coverage)} unit="%" icon={FlaskConical} color="green" />
            <StatCard label={t('buildSuccess')} value={fmt(devops.build_success_rate)} unit="%" icon={CheckCircle2} color="green" />
          </div>
        </>
      )}
    </div>
  )
}
