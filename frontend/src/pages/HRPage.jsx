import { useState, useEffect, useCallback } from 'react'
import * as api from '../api'
import { useTranslation } from '../i18n/I18nContext'
import {
  Users, BarChart3, Building2, ClipboardList, BookOpen,
  UserCheck, RefreshCcw, Smile, Calendar, Megaphone,
  GraduationCap, DollarSign, HeartPulse
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

function HealthScore({ data, t }) {
  if (!data) return null
  return (
    <div className="card" style={{ textAlign: 'center' }}>
      <h3 className="card-title">{t('hrHealthScore')}</h3>
      <div style={{
        width: 120, height: 120, borderRadius: '50%',
        border: `6px solid ${data.color || 'var(--primary-hover)'}`,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        flexDirection: 'column', margin: '16px auto'
      }}>
        <div style={{ fontSize: '1.8rem', fontWeight: 700, color: data.color }}>{data.score}</div>
        <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>/100</div>
      </div>
      <div style={{ fontWeight: 600, color: data.color }}>{data.rating}</div>
      {data.factors && (
        <div style={{ marginTop: 16, textAlign: 'left' }}>
          {Object.entries(data.factors).map(([k, v]) => (
            <div key={k} style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0', fontSize: '0.85rem' }}>
              <span style={{ textTransform: 'capitalize' }}>{k.replace('_', ' ')}</span>
              <span style={{ fontWeight: 600 }}>{v}/25</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default function HRPage() {
  const [summary, setSummary] = useState(null)
  const [departments, setDepartments] = useState([])
  const [recruitment, setRecruitment] = useState(null)
  const [training, setTraining] = useState(null)
  const [health, setHealth] = useState(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('overview')
  const { t } = useTranslation()

  const fetchData = useCallback(async () => {
    setLoading(true)
    const [s, d, r, t, h] = await Promise.allSettled([
      api.getHRSummary(), api.getHRDepartments(),
      api.getHRRecruitment(), api.getHRTraining(), api.getHRHealth(),
    ])
    if (s.status === 'fulfilled') setSummary(s.value.data)
    if (d.status === 'fulfilled') setDepartments(d.value.data?.departments || [])
    if (r.status === 'fulfilled') setRecruitment(r.value.data)
    if (t.status === 'fulfilled') setTraining(t.value.data)
    if (h.status === 'fulfilled') setHealth(h.value.data)
    setLoading(false)
  }, [])

  useEffect(() => { fetchData() }, [fetchData])

  const tabs = [
    { id: 'overview', label: t('overview'), Icon: BarChart3 },
    { id: 'departments', label: t('departments'), Icon: Building2 },
    { id: 'recruitment', label: t('recruitment'), Icon: ClipboardList },
    { id: 'training', label: t('training'), Icon: BookOpen },
  ]

  const fmt = (v, unit = '') => {
    if (v === null || v === undefined) return '—'
    if (typeof v === 'number') {
      if (Math.abs(v) >= 1e6) return `$${(v / 1e6).toFixed(1)}M`
      if (Math.abs(v) >= 1e3) return `$${(v / 1e3).toFixed(1)}K`
      return v % 1 === 0 ? v.toString() : v.toFixed(1)
    }
    return v
  }

  if (loading) return <div className="text-center" style={{ padding: 60 }}>{t('loading')}</div>

  return (
    <div>
      <h1 className="page-title" style={{ marginBottom: 20 }}><Users size={24} /> {t('humanResources')}</h1>

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
            <StatCard label={t('headcount')} value={fmt(summary.headcount)} icon={UserCheck} color="blue" />
            <StatCard label={t('turnoverRate')} value={fmt(summary.turnover_rate)} unit="%" icon={RefreshCcw} color="red" />
            <StatCard label={t('satisfaction')} value={fmt(summary.satisfaction_score)} unit="/100" icon={Smile} color="green" />
            <StatCard label={t('avgTenure')} value={fmt(summary.avg_tenure_years)} unit="yrs" icon={Calendar} color="purple" />
            <StatCard label={t('openPositions')} value={fmt(summary.open_positions)} icon={Megaphone} color="cyan" />
            <StatCard label={t('trainingHours')} value={fmt(summary.training_hours_per_employee)} unit="hrs" icon={GraduationCap} color="blue" />
            <StatCard label={t('costPerHire')} value={fmt(summary.cost_per_hire)} icon={DollarSign} color="red" />
            <StatCard label={t('absenteeism')} value={fmt(summary.absenteeism_rate)} unit="%" icon={HeartPulse} color="purple" />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: 20, marginTop: 20 }}>
            <HealthScore data={health} t={t} />
            <div className="card">
              <h3 className="card-title">{t('workforceTrends')}</h3>
              {summary.trends && summary.trends.length > 0 ? (
                <table className="table">
                  <thead><tr><th>Period</th><th>Headcount</th><th>Turnover</th><th>Satisfaction</th></tr></thead>
                  <tbody>
                    {summary.trends.slice(-8).map((t, i) => (
                      <tr key={i}>
                        <td>{t.period}</td>
                        <td>{fmt(t.headcount)}</td>
                        <td>{fmt(t.turnover)}%</td>
                        <td>{fmt(t.satisfaction)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : <p style={{ color: 'var(--text-muted)' }}>No trend data available</p>}
            </div>
          </div>
        </>
      )}

      {activeTab === 'departments' && (
        <div className="card">
          <h3 className="card-title">{t('departmentBreakdown')}</h3>
          <table className="table">
            <thead><tr><th>{t('department')}</th><th>{t('headcount')}</th><th>{t('satisfaction')}</th><th>{t('turnoverRate')}</th><th>{t('avgSalary')}</th><th>{t('trainingCompl')}</th></tr></thead>
            <tbody>
              {departments.map((d, i) => (
                <tr key={i}>
                  <td style={{ fontWeight: 600 }}>{d.department}</td>
                  <td>{fmt(d.headcount)}</td>
                  <td>{fmt(d.satisfaction)}</td>
                  <td>{fmt(d.turnover)}%</td>
                  <td>{fmt(d.avg_salary)}</td>
                  <td>{fmt(d.training_completion)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {activeTab === 'recruitment' && recruitment && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
          <div className="card">
            <h3 className="card-title">{t('recruitmentPipeline')}</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {[
                [t('openPositions'), recruitment.open_positions],
                [t('applications'), recruitment.applications_received],
                [t('interviews'), recruitment.interviews_scheduled],
                [t('offersExtended'), recruitment.offers_extended],
                [t('offersAccepted'), recruitment.offers_accepted],
              ].map(([label, value]) => (
                <div key={label} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 0', borderBottom: '1px solid var(--border)' }}>
                  <span>{label}</span>
                  <span style={{ fontWeight: 700, fontSize: '1.1rem' }}>{fmt(value)}</span>
                </div>
              ))}
            </div>
          </div>
          <div className="card">
            <h3 className="card-title">{t('recruitmentEfficiency')}</h3>
            <div className="kpi-grid" style={{ gridTemplateColumns: '1fr' }}>
              <StatCard label={t('avgTimeToFill')} value={fmt(recruitment.avg_time_to_fill_days)} unit="days" icon={Calendar} color="blue" />
              <StatCard label={t('costPerHire')} value={fmt(recruitment.cost_per_hire)} icon={DollarSign} color="red" />
            </div>
          </div>
        </div>
      )}

      {activeTab === 'training' && training && (
        <div className="kpi-grid">
          <StatCard label={t('totalTrainingHours')} value={fmt(training.total_training_hours)} icon={GraduationCap} color="blue" />
          <StatCard label={t('hoursPerEmployee')} value={fmt(training.hours_per_employee)} icon={Calendar} color="purple" />
          <StatCard label={t('completionRate')} value={fmt(training.completion_rate)} unit="%" icon={UserCheck} color="green" />
          <StatCard label={t('activePrograms')} value={fmt(training.programs_active)} icon={ClipboardList} color="cyan" />
          <StatCard label={t('trainingSatisfaction')} value={fmt(training.satisfaction_with_training)} unit="/5" icon={Smile} color="blue" />
          <StatCard label={t('budgetUtilization')} value={fmt(training.budget_utilization)} unit="%" icon={DollarSign} color="red" />
        </div>
      )}
    </div>
  )
}
