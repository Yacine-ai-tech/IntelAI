import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import * as api from '../api'
import { useTranslation } from '../i18n/I18nContext'
import { Rocket, TrendingUp, DollarSign, Activity, Percent } from 'lucide-react'
import { fmtPct, PageHeader, Stat, StatGrid, Loading, ErrorState, Grid, AskCopilot, AreaTrend, Panel, fmtMoney } from '../components/ui'
import PeriodFilter from '../components/PeriodFilter'

const ACCENT = 'var(--p-cro)'

export default function GrowthPage() {
  const { t } = useTranslation()
  const [selectedPeriod, setSelectedPeriod] = useState('')
  const [startPeriod, setStartPeriod] = useState('')
  const [endPeriod, setEndPeriod] = useState('')

  const { data: periods = [] } = useQuery({
    queryKey: ['periods'],
    queryFn: () => api.getPeriods().then(r => r.data?.periods || []),
    staleTime: 600_000,
  })

  const queryParams = {
    period: selectedPeriod || undefined,
    start_period: startPeriod || undefined,
    end_period: endPeriod || undefined,
  }

  const { data: s, isLoading, isError } = useQuery({
    queryKey: ['growth-summary', queryParams],
    queryFn: () => api.getGrowthSummary(queryParams).then(r => r.data),
    retry: 1,
  })

  if (isLoading) return <Loading />
  if (isError) return <ErrorState />
  const d = s || {}

  return (
    <div>
      <PageHeader
        icon={Rocket}
        accent={ACCENT}
        title={t('navGrowth') || 'Sales & Growth'}
        subtitle={t('growthSubtitle') || 'Revenue pipelines, retention & unit economics'}
        actions={<AskCopilot q={t('askCopilot_GrowthPage_AnalyzeOurRecent')} />}
      />

      <PeriodFilter
        periods={periods}
        selectedPeriod={selectedPeriod}
        onSelectPeriod={(p) => setSelectedPeriod(p)}
        startPeriod={startPeriod}
        endPeriod={endPeriod}
        onRangeChange={({ start, end }) => {
          setStartPeriod(start)
          setEndPeriod(end)
        }}
        accent={ACCENT}
      />

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
