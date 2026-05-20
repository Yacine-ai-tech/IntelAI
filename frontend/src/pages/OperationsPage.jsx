import { useState, useEffect, useCallback } from 'react'
import * as api from '../api'
import { useTranslation } from '../i18n/I18nContext'
import {
  Settings2, BarChart3, CheckCircle2, Factory, HardHat,
  Gauge, TrendingUp, Timer, ArrowDown, DollarSign, Target, ShieldAlert, Zap, Recycle,
  Microscope, Crosshair, RefreshCcw, FileText, Search,
  ClipboardList, Cog, Trash2, Wrench, Users,
  AlertTriangle, Bandage, TriangleAlert, Calendar, BookOpen, Activity, CircleDot
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

export default function OperationsPage() {
  const { t } = useTranslation()
  const [summary, setSummary] = useState(null)
  const [quality, setQuality] = useState(null)
  const [production, setProduction] = useState(null)
  const [safety, setSafety] = useState(null)
  const [health, setHealth] = useState(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('overview')

  const fetchData = useCallback(async () => {
    setLoading(true)
    const [s, q, p, sf, h] = await Promise.allSettled([
      api.getOpsSummary(), api.getOpsQuality(),
      api.getOpsProduction(), api.getOpsSafety(), api.getOpsHealth(),
    ])
    if (s.status === 'fulfilled') setSummary(s.value.data)
    if (q.status === 'fulfilled') setQuality(q.value.data)
    if (p.status === 'fulfilled') setProduction(p.value.data)
    if (sf.status === 'fulfilled') setSafety(sf.value.data)
    if (h.status === 'fulfilled') setHealth(h.value.data)
    setLoading(false)
  }, [])

  useEffect(() => { fetchData() }, [fetchData])

  const fmt = (v) => {
    if (v === null || v === undefined) return '—'
    if (typeof v === 'number') {
      if (Math.abs(v) >= 1e6) return `${(v / 1e6).toFixed(1)}M`
      if (Math.abs(v) >= 1e3) return `${(v / 1e3).toFixed(1)}K`
      return v % 1 === 0 ? v.toString() : v.toFixed(1)
    }
    return v
  }

  const tabs = [
    { id: 'overview', label: t('overview'), Icon: BarChart3 },
    { id: 'quality', label: t('quality'), Icon: CheckCircle2 },
    { id: 'production', label: t('production'), Icon: Factory },
    { id: 'safety', label: t('safety'), Icon: HardHat },
  ]

  if (loading) return <div className="text-center" style={{ padding: 60 }}>{t('loadingOps')}</div>

  return (
    <div>
      <h1 className="page-title" style={{ marginBottom: 20 }}><Settings2 size={24} /> {t('operations')}</h1>

      <div className="tab-bar">
        {tabs.map(tab => (
          <button key={tab.id} className={`tab-btn${activeTab === tab.id ? ' active' : ''}`}
            onClick={() => setActiveTab(tab.id)}>
            <tab.Icon size={15} /> {tab.label}
          </button>
        ))}
      </div>

      {activeTab === 'overview' && summary && (
        <>
          <div className="kpi-grid">
            <StatCard label={t('oee')} value={fmt(summary.oee)} unit="%" icon={Gauge} color="blue" />
            <StatCard label={t('capacityUtil')} value={fmt(summary.capacity_utilization)} unit="%" icon={Factory} color="purple" />
            <StatCard label={t('qualityRate')} value={fmt(summary.quality_rate)} unit="%" icon={CheckCircle2} color="green" />
            <StatCard label={t('defectRate')} value={fmt(summary.defect_rate)} unit="%" icon={CircleDot} color="red" />
            <StatCard label={t('throughput')} value={fmt(summary.throughput)} unit="units" icon={TrendingUp} color="cyan" />
            <StatCard label={t('cycleTime')} value={fmt(summary.cycle_time)} unit="hrs" icon={Timer} color="purple" />
            <StatCard label={t('downtime')} value={fmt(summary.downtime_hours)} unit="hrs" icon={ArrowDown} color="red" />
            <StatCard label={t('costPerUnit')} value={`$${fmt(summary.cost_per_unit)}`} icon={DollarSign} color="blue" />
            <StatCard label={t('onTimeCompletion')} value={fmt(summary.on_time_completion)} unit="%" icon={Target} color="green" />
            <StatCard label={t('safetyIncidents')} value={fmt(summary.safety_incidents)} icon={ShieldAlert} color="red" />
            <StatCard label={t('energyEfficiency')} value={fmt(summary.energy_efficiency)} unit="%" icon={Zap} color="cyan" />
            <StatCard label={t('wasteReduction')} value={fmt(summary.waste_reduction)} unit="%" icon={Recycle} color="green" />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: 20, marginTop: 20 }}>
            {health && (
              <div className="card" style={{ textAlign: 'center' }}>
                <h3 className="card-title">{t('opsHealthScore')}</h3>
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
              <h3 className="card-title">{t('operationsTrends')}</h3>
              {summary.trends && summary.trends.length > 0 ? (
                <table className="table">
                  <thead><tr><th>Period</th><th>OEE</th><th>Quality</th><th>Throughput</th></tr></thead>
                  <tbody>
                    {summary.trends.slice(-8).map((t, i) => (
                      <tr key={i}>
                        <td>{t.period}</td>
                        <td>{fmt(t.oee)}%</td>
                        <td>{fmt(t.quality)}%</td>
                        <td>{fmt(t.throughput)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : <p style={{ color: 'var(--text-muted)' }}>No trend data available</p>}
            </div>
          </div>
        </>
      )}

      {activeTab === 'quality' && quality && (
        <div className="kpi-grid">
          <StatCard label={t('qualityRate')} value={fmt(quality.quality_rate)} unit="%" icon={CheckCircle2} color="green" />
          <StatCard label={t('defectPPM')} value={fmt(quality.defect_ppm)} icon={Microscope} color="red" />
          <StatCard label={t('firstPassYield')} value={fmt(quality.first_pass_yield)} unit="%" icon={Crosshair} color="green" />
          <StatCard label={t('reworkRate')} value={fmt(quality.rework_rate)} unit="%" icon={RefreshCcw} color="purple" />
          <StatCard label={t('complaints')} value={fmt(quality.customer_complaints)} icon={FileText} color="blue" />
          <StatCard label={t('costOfQuality')} value={`$${fmt(quality.cost_of_quality)}`} icon={DollarSign} color="red" />
          <StatCard label={t('inspectionPass')} value={fmt(quality.inspection_pass_rate)} unit="%" icon={Search} color="cyan" />
        </div>
      )}

      {activeTab === 'production' && production && (
        <div className="kpi-grid">
          <StatCard label={t('dailyOutput')} value={fmt(production.daily_output)} unit="units" icon={Factory} color="blue" />
          <StatCard label={t('capacity')} value={fmt(production.capacity_utilization)} unit="%" icon={Gauge} color="purple" />
          <StatCard label={t('oee')} value={fmt(production.oee)} unit="%" icon={Cog} color="cyan" />
          <StatCard label={t('plannedVsActual')} value={fmt(production.planned_vs_actual)} unit="%" icon={ClipboardList} color="blue" />
          <StatCard label={t('changeoverTime')} value={fmt(production.changeover_time)} unit="hrs" icon={RefreshCcw} color="purple" />
          <StatCard label={t('scrapRate')} value={fmt(production.scrap_rate)} unit="%" icon={Trash2} color="red" />
          <StatCard label={t('maintenanceCompl')} value={fmt(production.maintenance_compliance)} unit="%" icon={Wrench} color="green" />
          <StatCard label={t('laborProductivity')} value={fmt(production.labor_productivity)} unit="%" icon={Users} color="cyan" />
        </div>
      )}

      {activeTab === 'safety' && safety && (
        <div className="kpi-grid">
          <StatCard label={t('totalIncidents')} value={fmt(safety.total_incidents)} icon={AlertTriangle} color="red" />
          <StatCard label={t('lostTimeInjuries')} value={fmt(safety.lost_time_injuries)} icon={Bandage} color="red" />
          <StatCard label={t('nearMisses')} value={fmt(safety.near_misses)} icon={TriangleAlert} color="purple" />
          <StatCard label={t('daysSinceIncident')} value={fmt(safety.days_since_last_incident)} icon={Calendar} color="green" />
          <StatCard label={t('safetyTraining')} value={fmt(safety.safety_training_completion)} unit="%" icon={BookOpen} color="blue" />
          <StatCard label={t('trir')} value={fmt(safety.trir)} icon={Activity} color="cyan" />
          <StatCard label={t('severityRate')} value={fmt(safety.severity_rate)} icon={CircleDot} color="red" />
        </div>
      )}
    </div>
  )
}
