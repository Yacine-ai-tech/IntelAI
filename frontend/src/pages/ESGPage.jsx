import { useQuery } from '@tanstack/react-query'
import * as api from '../api'
import { useTranslation } from '../i18n/I18nContext'
import { Leaf, Cloud, Zap, Droplet, Recycle, Users, Scale, Landmark, ShieldCheck } from 'lucide-react'
import { fmtPct, PageHeader, Stat, StatGrid, fmtNum, Loading, Grid, AskCopilot, AreaTrend, DomainHero, Panel, fmtMoney } from '../components/ui'

const ACCENT = 'var(--p-esg)'

export default function ESGPage() {
  const { t } = useTranslation()
  const { data, isLoading } = useQuery({ queryKey: ['esg'], queryFn: () => api.getESGSummary().then(r => r.data), retry: 1 })
  if (isLoading) return <Loading />
  const d = data || {}
  const env = d.environment || {}, soc = d.social || {}, gov = d.governance || {}
  const score = Math.round(d.score ?? 0)
  const scoreColor = score >= 70 ? 'var(--ok)' : score >= 50 ? 'var(--warn)' : 'var(--bad)'
  const esgHealth = {
    score, color: scoreColor, captionLabel: t('lblEsgScore') || 'ESG score',
    rating: score >= 70 ? (t('strong') || 'Strong') : score >= 50 ? (t('moderate') || 'Developing') : (t('atRisk') || 'At risk'),
    factors: [
      { label: t('lblRenewableEnergy') || 'Renewable %', value: env.renewable_energy_pct },
      { label: t('lblWasteDiverted') || 'Waste diverted %', value: env.waste_diverted },
      { label: t('lblDiversityIndex') || 'Diversity /100', value: soc.diversity_index },
      { label: t('lblEthicsTraining') || 'Ethics training %', value: gov.ethics_training },
    ],
  }

  return (
    <div>
      <PageHeader icon={Leaf} accent={ACCENT} title={t('navESG') || 'ESG & Sustainability'}
        subtitle={t('esgSubtitle') || 'Environmental, social & governance — GHG Protocol / CSRD aligned'}
        actions={<AskCopilot q="Summarize our ESG position across environment, social and governance, and CSRD readiness." />} />

      <DomainHero health={esgHealth} accent={ACCENT} />

      <Panel title={t('lblCarbonTrend')} icon={Cloud}
        actions={<AskCopilot q="What is driving our ESG score and how do we improve it under CSRD?" label={t('lblImproveScore')} />}>
        <AreaTrend data={d.trends || []} y="carbon" color={ACCENT} height={200} />
      </Panel>

      <Panel title={t('lblEnvironment')} icon={Leaf} style={{ marginTop: 18 }}>
        <StatGrid>
          <Stat label={t('lblCarbonEmissions')} value={fmtNum(env.carbon_emissions)} unit="tCO₂e" icon={Cloud} accent={ACCENT} good="down" hint="Scope 1–3 (GHG Protocol)" />
          <Stat label={t('lblRenewableEnergy')} value={fmtPct(env.renewable_energy_pct)} icon={Zap} accent={ACCENT} good="up" />
          <Stat label={t('lblWaterUsage')} value={fmtNum(env.water_usage)} unit="m³" icon={Droplet} accent={ACCENT} good="down" />
          <Stat label={t('lblWasteDiverted')} value={fmtPct(env.waste_diverted)} icon={Recycle} accent={ACCENT} good="up" />
        </StatGrid>
      </Panel>

      <Grid style={{ marginTop: 18 }}>
        <Panel title={t('lblSocial')} icon={Users}>
          <StatGrid>
            <Stat label={t('lblCommunityInvestment')} value={fmtMoney(soc.community_investment)} icon={Landmark} accent={ACCENT} good="up" />
            <Stat label={t('lblDiversityIndex')} value={fmtNum(soc.diversity_index)} unit="/100" icon={Users} accent={ACCENT} good="up" />
            <Stat label={t('lblGenderPayGap')} value={fmtPct(soc.gender_pay_gap)} icon={Scale} accent={ACCENT} good="down" />
          </StatGrid>
        </Panel>
        <Panel title={t('lblGovernance')} icon={Landmark}>
          <StatGrid>
            <Stat label={t('lblBoardDiversity')} value={fmtPct(gov.board_diversity)} icon={Users} accent={ACCENT} good="up" />
            <Stat label={t('lblEthicsTraining')} value={fmtPct(gov.ethics_training)} icon={ShieldCheck} accent={ACCENT} good="up" />
            <Stat label={t('lblSupplierCompliance')} value={fmtPct(gov.supplier_compliance)} icon={ShieldCheck} accent={ACCENT} good="up" />
            <Stat label={t('lblDataPrivacyIncidents')} value={fmtNum(gov.data_privacy_incidents)} icon={ShieldCheck} accent="var(--bad)" good="down" />
          </StatGrid>
        </Panel>
      </Grid>
    </div>
  )
}
