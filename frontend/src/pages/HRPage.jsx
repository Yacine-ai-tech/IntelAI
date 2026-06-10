import { useQuery } from '@tanstack/react-query'
import * as api from '../api'
import { useTranslation } from '../i18n/I18nContext'
import {
  Users, UserMinus, Smile, Briefcase, Clock, GraduationCap, DollarSign, CalendarX, UserPlus,
} from 'lucide-react'
import {
  PageHeader, Stat, StatGrid, Panel, Grid, Loading, AreaTrend, BarList, AskCopilot,
  fmtNum, fmtMoney, fmtPct,
} from '../components/ui'

const ACCENT = 'var(--p-chro)'

export default function HRPage() {
  const { t } = useTranslation()
  const summary = useQuery({ queryKey: ['hr-summary'], queryFn: () => api.getHRSummary().then(r => r.data), retry: 1 })
  const depts = useQuery({ queryKey: ['hr-depts'], queryFn: () => api.getHRDepartments().then(r => r.data?.departments || []), retry: 1 })
  const recruit = useQuery({ queryKey: ['hr-recruit'], queryFn: () => api.getHRRecruitment().then(r => r.data), retry: 1 })

  if (summary.isLoading) return <Loading />
  const s = summary.data || {}
  const r = recruit.data || {}

  return (
    <div>
      <PageHeader icon={Users} accent={ACCENT} title={t('navHR') || 'Human Resources'}
        subtitle={t('hrSubtitle') || 'Workforce, engagement & talent analytics'}
        actions={<AskCopilot q="Summarize our people metrics — headcount, turnover, engagement — and what needs attention." />} />

      <StatGrid>
        <Stat label="Headcount" value={fmtNum(s.headcount)} icon={Users} accent={ACCENT} />
        <Stat label="Turnover Rate" value={fmtPct(s.turnover_rate)} icon={UserMinus} accent={ACCENT} good="down" />
        <Stat label="Satisfaction" value={fmtNum(s.satisfaction_score)} unit="/100" icon={Smile} accent={ACCENT} good="up" />
        <Stat label="Open Positions" value={fmtNum(s.open_positions)} icon={Briefcase} accent={ACCENT} good="down" />
        <Stat label="Avg Tenure" value={fmtNum(s.avg_tenure_years)} unit="yrs" icon={Clock} accent={ACCENT} />
        <Stat label="Training / Employee" value={fmtNum(s.training_hours_per_employee)} unit="h" icon={GraduationCap} accent={ACCENT} good="up" />
        <Stat label="Cost per Hire" value={fmtMoney(s.cost_per_hire)} icon={DollarSign} accent={ACCENT} good="down" />
        <Stat label="Absenteeism" value={fmtPct(s.absenteeism_rate)} icon={CalendarX} accent={ACCENT} good="down" />
      </StatGrid>

      <Grid style={{ marginTop: 18 }}>
        <Panel title="Headcount trend" icon={Users} style={{ gridColumn: 'span 2' }}>
          <AreaTrend data={s.trends || []} y="headcount" color={ACCENT} />
        </Panel>
        <Panel title="Recruitment funnel" icon={UserPlus}>
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

      <Panel title="By department" icon={Users} style={{ marginTop: 18 }}
        actions={<AskCopilot q="Which department has the highest turnover and lowest satisfaction, and why?" label="Analyze" />}>
        <table className="table">
          <thead><tr><th>Department</th><th>Headcount</th><th>Satisfaction</th><th>Turnover</th><th>Avg Salary</th><th>Training</th></tr></thead>
          <tbody>
            {(depts.data || []).map((d, i) => (
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
