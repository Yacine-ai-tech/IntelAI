import { useQuery } from '@tanstack/react-query'
import * as api from '../api'
import { useTranslation } from '../i18n/I18nContext'
import {
  Users, UserMinus, Smile, Briefcase, Clock, GraduationCap, DollarSign, CalendarX, UserPlus,
} from 'lucide-react'
import { fmtPct, PageHeader, Stat, StatGrid, BarList, fmtNum, Loading, ErrorState, Grid, AskCopilot, AreaTrend, DomainHero, Panel, fmtMoney } from '../components/ui'

const ACCENT = 'var(--p-chro)'

export default function HRPage() {
  const { t } = useTranslation()
  const summary = useQuery({ queryKey: ['hr-summary'], queryFn: () => api.getHRSummary().then(r => r.data), retry: 1 })
  const depts = useQuery({ queryKey: ['hr-depts'], queryFn: () => api.getHRDepartments().then(r => r.data?.departments || []), retry: 1 })
  const recruit = useQuery({ queryKey: ['hr-recruit'], queryFn: () => api.getHRRecruitment().then(r => r.data), retry: 1 })
  const hlt = useQuery({ queryKey: ['hr-health'], queryFn: () => api.getHRHealth().then(r => r.data), retry: 1 })

  if (summary.isLoading) return <Loading />
  if (summary.isError) return <ErrorState />
  const s = summary.data || {}
  const r = recruit.data || {}

  return (
    <div>
      <PageHeader icon={Users} accent={ACCENT} title={t('navHR') || 'Human Resources'}
        subtitle={t('hrSubtitle') || 'Workforce, engagement & talent analytics'}
        actions={<AskCopilot q={t('askCopilot_HRPage_SummarizeOurPeople')} />} />

      <DomainHero health={hlt.data} accent={ACCENT} />

      <StatGrid>
        <Stat label={t('lblHeadcount')} value={fmtNum(s.headcount)} icon={Users} accent={ACCENT} />
        <Stat label={t('lblTurnoverRate')} value={fmtPct(s.turnover_rate)} icon={UserMinus} accent={ACCENT} good="down" />
        <Stat label={t('lblSatisfaction')} value={fmtNum(s.satisfaction_score)} unit="/100" icon={Smile} accent={ACCENT} good="up" />
        <Stat label={t('lblOpenPositions')} value={fmtNum(s.open_positions)} icon={Briefcase} accent={ACCENT} good="down" />
        <Stat label={t('lblAvgTenure')} value={fmtNum(s.avg_tenure_years)} unit="yrs" icon={Clock} accent={ACCENT} />
        <Stat label={t('lblTrainingEmployee')} value={fmtNum(s.training_hours_per_employee)} unit="h" icon={GraduationCap} accent={ACCENT} good="up" />
        <Stat label={t('lblCostPerHire')} value={fmtMoney(s.cost_per_hire)} icon={DollarSign} accent={ACCENT} good="down" />
        <Stat label={t('lblAbsenteeism')} value={fmtPct(s.absenteeism_rate)} icon={CalendarX} accent={ACCENT} good="down" />
      </StatGrid>

      <Grid style={{ marginTop: 18 }}>
        <Panel title={t('lblHeadcountTrend')} icon={Users} style={{ gridColumn: 'span 2' }}>
          <AreaTrend data={Array.isArray(s.trends) ? s.trends : []} y="headcount" color={ACCENT} />
        </Panel>
        <Panel title={t('lblRecruitmentFunnel')} icon={UserPlus}>
          <BarList items={[
            { label: 'Applications', value: r.applications_received, display: fmtNum(r.applications_received) },
            { label: 'Interviews', value: r.interviews_scheduled, display: fmtNum(r.interviews_scheduled) },
            { label: 'Offers extended', value: r.offers_extended, display: fmtNum(r.offers_extended) },
            { label: 'Offers accepted', value: r.offers_accepted, display: fmtNum(r.offers_accepted), color: 'var(--ok)' },
          ]} />
          <div style={{ marginTop: 14, fontSize: '.82rem', color: 'var(--text-2)' }}>
            Avg time to fill: <b style={{ color: 'var(--text)' }}>{fmtNum(r.avg_time_to_fill_days)} days</b>
          </div>
        </Panel>
      </Grid>

      <Panel title={t('lblByDepartment')} icon={Users} style={{ marginTop: 18 }}
        actions={<AskCopilot q={t('askCopilot_HRPage_WhichDepartmentHas')} label={t('lblAnalyze')} />}>
        <table className="table">
          <thead><tr><th>{t('thDept') || 'Department'}</th><th>{t('thHeadcount') || 'Headcount'}</th><th>{t('thSat') || 'Satisfaction'}</th><th>{t('thTurnover') || 'Turnover'}</th><th>{t('thAvgSalary') || 'Avg Salary'}</th><th>{t('thTraining') || 'Training'}</th></tr></thead>
          <tbody>
            {(Array.isArray(depts.data) ? depts.data : []).map((d, i) => (
              <tr key={i}>
                <td style={{ fontWeight: 600 }}>{d.department}</td>
                <td>{fmtNum(d.headcount)}</td>
                <td>{fmtNum(d.satisfaction)}</td>
                <td><span className={`badge ${d.turnover > 15 ? 'bad' : d.turnover > 10 ? 'warn' : 'ok'}`}>{fmtPct(d.turnover)}</span></td>
                <td>{fmtMoney(d.avg_salary)}</td>
                <td>{fmtPct(d.training_completion)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Panel>
    </div>
  )
}
