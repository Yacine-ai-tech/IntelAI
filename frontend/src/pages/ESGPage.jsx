import { useQuery } from '@tanstack/react-query'
import * as api from '../api'
import { useTranslation } from '../i18n/I18nContext'
import { Leaf, Cloud, Zap, Droplet, Recycle, Users, Scale, Landmark, ShieldCheck } from 'lucide-react'
import {
  PageHeader, Stat, StatGrid, Panel, Grid, Loading, AreaTrend, AskCopilot,
  fmtNum, fmtMoney, fmtPct,
} from '../components/ui'

const ACCENT = 'var(--p-esg)'

export default function ESGPage() {
  const { t } = useTranslation()
  const { data, isLoading } = useQuery({ queryKey: ['esg'], queryFn: () => api.getESGSummary().then(r => r.data), retry: 1 })
  if (isLoading) return <Loading />
  const d = data || {}
  const env = d.environment || {}, soc = d.social || {}, gov = d.governance || {}
  const score = Math.round(d.score ?? 0)
  const scoreColor = score >= 70 ? 'var(--ok)' : score >= 50 ? 'var(--warn)' : 'var(--bad)'

  return (
    <div>
      <PageHeader icon={Leaf} accent={ACCENT} title={t('navESG') || 'ESG & Sustainability'}
        subtitle={t('esgSubtitle') || 'Environmental, social & governance — GHG Protocol / CSRD aligned'}
        actions={<AskCopilot q="Summarize our ESG position across environment, social and governance, and CSRD readiness." />} />

      <Grid min={260}>
        <Panel style={{ textAlign: 'center' }}>
          <div className="kpi-label">ESG Score</div>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: '3rem', fontWeight: 700, color: scoreColor }}>{score}<span style={{ fontSize: '1.1rem', color: 'var(--text-3)' }}>/100</span></div>
          <div style={{ marginTop: 8 }}><AskCopilot q="What is driving our ESG score and how do we improve it under CSRD?" label="Improve score" /></div>
        </Panel>
        <Panel title="Carbon trend" icon={Cloud} style={{ gridColumn: 'span 2' }}>
          <AreaTrend data={d.trends || []} y="carbon" color={ACCENT} height={180} />
        </Panel>
      </Grid>

      <Panel title="Environment" icon={Leaf} style={{ marginTop: 18 }}>
        <StatGrid>
          <Stat label="Carbon Emissions" value={fmtNum(env.carbon_emissions)} unit="tCO₂e" icon={Cloud} accent={ACCENT} good="down" hint="Scope 1–3 (GHG Protocol)" />
          <Stat label="Renewable Energy" value={fmtPct(env.renewable_energy_pct)} icon={Zap} accent={ACCENT} good="up" />
          <Stat label="Water Usage" value={fmtNum(env.water_usage)} unit="m³" icon={Droplet} accent={ACCENT} good="down" />
          <Stat label="Waste Diverted" value={fmtPct(env.waste_diverted)} icon={Recycle} accent={ACCENT} good="up" />
        </StatGrid>
      </Panel>

      <Grid style={{ marginTop: 18 }}>
        <Panel title="Social" icon={Users}>
          <StatGrid>
            <Stat label="Community Investment" value={fmtMoney(soc.community_investment)} icon={Landmark} accent={ACCENT} good="up" />
            <Stat label="Diversity Index" value={fmtNum(soc.diversity_index)} unit="/100" icon={Users} accent={ACCENT} good="up" />
            <Stat label="Gender Pay Gap" value={fmtPct(soc.gender_pay_gap)} icon={Scale} accent={ACCENT} good="down" />
          </StatGrid>
        </Panel>
        <Panel title="Governance" icon={Landmark}>
          <StatGrid>
            <Stat label="Board Diversity" value={fmtPct(gov.board_diversity)} icon={Users} accent={ACCENT} good="up" />
            <Stat label="Ethics Training" value={fmtPct(gov.ethics_training)} icon={ShieldCheck} accent={ACCENT} good="up" />
            <Stat label="Supplier Compliance" value={fmtPct(gov.supplier_compliance)} icon={ShieldCheck} accent={ACCENT} good="up" />
            <Stat label="Data Privacy Incidents" value={fmtNum(gov.data_privacy_incidents)} icon={ShieldCheck} accent="var(--bad)" good="down" />
          </StatGrid>
        </Panel>
      </Grid>
    </div>
  )
}
