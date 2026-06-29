import { useQuery } from '@tanstack/react-query'
import * as api from '../api'
import { useTranslation } from '../i18n/I18nContext'
import { Rocket, TrendingUp, Users, DollarSign, Activity, Percent, ArrowUpRight } from 'lucide-react'
import {
  PageHeader, Stat, StatGrid, Panel, Grid, Loading, AreaTrend, AskCopilot,
  fmtNum, fmtMoney, fmtPct,
} from '../components/ui'

const ACCENT = 'var(--p-cro)'

export default function GrowthPage() {
  const { t } = useTranslation()
  const { data: s, isLoading } = useQuery({ queryKey: ['growth-summary'], queryFn: () => api.getGrowthSummary().then(r => r.data), retry: 1 })

  if (isLoading) return <Loading />
  const d = s || {}

  return (
    <div>
      <PageHeader icon={Rocket} accent={ACCENT} title={t('navGrowth') || 'Sales & Growth'}
        subtitle={t('growthSubtitle') || 'Revenue pipelines, retention & unit economics'}
        actions={<AskCopilot q="Analyze our recent MRR and Churn trends. Are our unit economics (LTV/CAC) healthy?" />} />

      <StatGrid>
        <Stat label={t('mrr') || 'MRR'} value={fmtMoney(d.mrr)} trend={d.mrr_trend} icon={DollarSign} accent={ACCENT} good="up" />
        <Stat label={t('arr') || 'ARR'} value={fmtMoney(d.arr)} icon={DollarSign} accent={ACCENT} good="up" />
        <Stat label={t('cac') || 'CAC'} value={fmtMoney(d.cac)} trend={d.cac_trend} icon={Activity} accent={ACCENT} good="down" />
        <Stat label={t('ltv') || 'LTV'} value={fmtMoney(d.ltv)} icon={TrendingUp} accent={ACCENT} good="up" />
        <Stat label={t('churnRate') || 'Churn Rate'} value={fmtPct(d.churn_rate)} trend={d.churn_trend} icon={Percent} accent={ACCENT} good="down" />
      </StatGrid>

      <Grid style={{ marginTop: 18 }}>
        <Panel title={t('mrrTrend') || 'MRR Trend'} icon={TrendingUp} style={{ gridColumn: 'span 2' }}>
          <AreaTrend data={d.trends || []} y="value" color={ACCENT} height={250} />
        </Panel>
      </Grid>
    </div>
  )
}
