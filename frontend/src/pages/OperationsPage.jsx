import { useQuery } from '@tanstack/react-query'
import * as api from '../api'
import { useTranslation } from '../i18n/I18nContext'
import {
  Settings2, Gauge, CheckCircle2, AlertOctagon, Boxes, Timer, Power, DollarSign,
  Factory, HardHat, ShieldCheck,
} from 'lucide-react'
import {
  PageHeader, DomainHero, Stat, StatGrid, Panel, Grid, Loading, AreaTrend, BarList, AskCopilot,
  fmtNum, fmtMoney, fmtPct,
} from '../components/ui'

const ACCENT = 'var(--p-coo)'

export default function OperationsPage() {
  const { t } = useTranslation()
  const sum = useQuery({ queryKey: ['ops-sum'], queryFn: () => api.getOpsSummary().then(r => r.data), retry: 1 })
  const qual = useQuery({ queryKey: ['ops-qual'], queryFn: () => api.getOpsQuality().then(r => r.data), retry: 1 })
  const prod = useQuery({ queryKey: ['ops-prod'], queryFn: () => api.getOpsProduction().then(r => r.data), retry: 1 })
  const safe = useQuery({ queryKey: ['ops-safe'], queryFn: () => api.getOpsSafety().then(r => r.data), retry: 1 })
  const hlt = useQuery({ queryKey: ['ops-health'], queryFn: () => api.getOpsHealth().then(r => r.data), retry: 1 })

  if (sum.isLoading) return <Loading />
  const s = sum.data || {}, q = qual.data || {}, p = prod.data || {}, sf = safe.data || {}

  return (
    <div>
      <PageHeader icon={Settings2} accent={ACCENT} title={t('navOperations') || 'Operations'}
        subtitle={t('opsSubtitle') || 'Efficiency, quality, production & safety'}
        actions={<AskCopilot q="Summarize operations health — OEE, quality, on-time completion and safety — and the top bottleneck." />} />

      <DomainHero health={hlt.data} accent={ACCENT} />

      <StatGrid>
        <Stat label={t('lblOverallEfficiency')} value={fmtPct(s.overall_efficiency)} icon={Gauge} accent={ACCENT} good="up" hint="World-class OEE ≈ 85%" />
        <Stat label={t('lblCapacityUtilization')} value={fmtPct(s.capacity_utilization)} icon={Boxes} accent={ACCENT} good="up" />
        <Stat label={t('lblQualityRate')} value={fmtPct(s.quality_rate)} icon={CheckCircle2} accent={ACCENT} good="up" />
        <Stat label={t('lblDefectRate')} value={fmtPct(s.defect_rate)} icon={AlertOctagon} accent="var(--bad)" good="down" />
        <Stat label={t('lblCycleTime')} value={fmtNum(s.cycle_time)} unit="d" icon={Timer} accent={ACCENT} good="down" />
        <Stat label={t('lblOnTimeCompletion')} value={fmtPct(s.on_time_completion)} icon={CheckCircle2} accent={ACCENT} good="up" />
        <Stat label={t('lblDowntime')} value={fmtNum(s.downtime_hours)} unit="h" icon={Power} accent={ACCENT} good="down" />
        <Stat label={t('lblCostPerUnit')} value={fmtMoney(s.cost_per_unit)} icon={DollarSign} accent={ACCENT} good="down" />
      </StatGrid>

      <Grid style={{ marginTop: 18 }}>
        <Panel title={t('lblEfficiencyTrend')} icon={Gauge} style={{ gridColumn: 'span 2' }}>
          <AreaTrend data={s.trends || []} y="efficiency" color={ACCENT} />
        </Panel>
        <Panel title={t('lblProcessAreas')} icon={Factory}>
          <BarList items={(s.process_areas || []).map(a => ({
            label: a.area, value: a.efficiency, display: fmtPct(a.efficiency),
            color: a.efficiency > 85 ? 'var(--ok)' : a.efficiency > 70 ? 'var(--warn)' : 'var(--bad)',
          }))} />
        </Panel>
      </Grid>

      <Grid style={{ marginTop: 18 }}>
        <Panel title={t('lblQuality')} icon={CheckCircle2}>
          <BarList items={[
            { label: 'First pass yield', value: q.first_pass_yield, display: fmtPct(q.first_pass_yield), color: 'var(--ok)' },
            { label: 'Inspection pass rate', value: q.inspection_pass_rate, display: fmtPct(q.inspection_pass_rate), color: 'var(--ok)' },
            { label: 'Rework rate', value: q.rework_rate, display: fmtPct(q.rework_rate), color: 'var(--warn)' },
            { label: 'Customer complaints', value: q.customer_complaints, display: fmtNum(q.customer_complaints), color: 'var(--bad)' },
          ]} />
        </Panel>
        <Panel title={t('lblProduction')} icon={Factory}>
          <StatGrid>
            <Stat label={t('lblOEE')} value={fmtPct(p.oee)} accent={ACCENT} good="up" />
            <Stat label={t('lblDailyOutput')} value={fmtNum(p.daily_output)} accent={ACCENT} />
            <Stat label={t('lblLaborProductivity')} value={fmtPct(p.labor_productivity)} accent={ACCENT} good="up" />
            <Stat label={t('lblScrapRate')} value={fmtPct(p.scrap_rate)} accent="var(--bad)" good="down" />
          </StatGrid>
        </Panel>
        <Panel title={t('lblSafety')} icon={HardHat}>
          <StatGrid>
            <Stat label={t('lblTRIR')} value={fmtNum(sf.trir)} icon={ShieldCheck} accent={ACCENT} good="down" />
            <Stat label={t('lblDaysWOIncident')} value={fmtNum(sf.days_without_incident)} accent="var(--ok)" good="up" />
            <Stat label={t('lblLostTimeIncidents')} value={fmtNum(sf.lost_time_incidents)} accent="var(--bad)" good="down" />
            <Stat label={t('lblNearMisses')} value={fmtNum(sf.near_misses)} accent="var(--warn)" />
          </StatGrid>
        </Panel>
      </Grid>
    </div>
  )
}
