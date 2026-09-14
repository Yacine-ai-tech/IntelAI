import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import * as api from '../api'
import { useTranslation } from '../i18n/I18nContext'
import {
  Monitor, Activity, Ticket, Timer, ShieldCheck, Server, DollarSign, Rocket,
  AlertTriangle, Bug, Lock, GitBranch,
} from 'lucide-react'
import { fmtPct, PageHeader, Stat, StatGrid, BarList, fmtNum, Loading, ErrorState, Grid, AskCopilot, DomainHero, Panel, fmtMoney } from '../components/ui'
import PeriodFilter from '../components/PeriodFilter'

const ACCENT = 'var(--p-cto)'

export default function ITPage() {
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

  const ov = useQuery({
    queryKey: ['it-ov', queryParams],
    queryFn: () => api.getITOverview(queryParams).then(r => r.data),
    retry: 1,
  })
  const sec = useQuery({
    queryKey: ['it-sec', queryParams],
    queryFn: () => api.getITSecurity(queryParams).then(r => r.data),
    retry: 1,
  })
  const dev = useQuery({
    queryKey: ['it-dev', queryParams],
    queryFn: () => api.getITDevOps(queryParams).then(r => r.data),
    retry: 1,
  })
  const hlt = useQuery({
    queryKey: ['it-health', queryParams],
    queryFn: () => api.getITHealth(queryParams).then(r => r.data),
    retry: 1,
  })

  if (ov.isLoading) return <Loading />
  if (ov.isError) return <ErrorState />
  const o = ov.data || {}, s = sec.data || {}, d = dev.data || {}

  return (
    <div>
      <PageHeader
        icon={Monitor}
        accent={ACCENT}
        title={t('navIT') || 'IT Operations'}
        subtitle={t('itSubtitle') || 'Reliability, security & DevOps performance (DORA)'}
        actions={<AskCopilot q={t('askCopilot_ITPage_HowHealthyIs')} />}
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

      <DomainHero health={hlt.data} accent={ACCENT} />

      <StatGrid>
        <Stat label={t('lblSystemUptime')} value={fmtPct(o.system_uptime)} icon={Activity} accent={ACCENT} good="up" hint="2026 elite: 99.99%" />
        <Stat label={t('lblOpenTickets')} value={fmtNum(o.open_tickets)} icon={Ticket} accent={ACCENT} good="down" />
        <Stat label={t('lblMTTR')} value={fmtNum(o.mttr_hours)} unit="h" icon={Timer} accent={ACCENT} good="down" hint="DORA elite: <1h" />
        <Stat label={t('lblSLACompliance')} value={fmtPct(o.sla_compliance)} icon={ShieldCheck} accent={ACCENT} good="up" />
        <Stat label={t('lblSecurityScore')} value={fmtNum(o.security_score)} unit="/100" icon={Lock} accent={ACCENT} good="up" />
        <Stat label={t('lblServers')} value={fmtNum(o.server_count)} icon={Server} accent={ACCENT} />
        <Stat label={t('lblCloudSpend')} value={fmtMoney(o.cloud_spend)} icon={DollarSign} accent={ACCENT} good="down" />
        <Stat label={t('lblDeployFrequency')} value={fmtNum(o.deployment_frequency)} unit="/mo" icon={Rocket} accent={ACCENT} good="up" />
      </StatGrid>

      <Grid style={{ marginTop: 18 }}>
        <Panel
          title={t('lblDevOpsDORAMetrics')}
          icon={GitBranch}
          actions={<AskCopilot q={t('askCopilot_ITPage_InterpretOurDora')} label={t('lblInterpret')} />}
        >
          <BarList items={[
            { label: 'Deployment frequency (/mo)', value: d.deployment_frequency, display: fmtNum(d.deployment_frequency) },
            { label: 'Lead time (h)', value: d.lead_time_hours, display: fmtNum(d.lead_time_hours) + 'h', color: 'var(--warn)' },
            { label: 'Change failure rate (%)', value: d.change_failure_rate, display: fmtPct(d.change_failure_rate), color: 'var(--bad)' },
            { label: 'MTTR (h)', value: d.mttr_hours, display: fmtNum(d.mttr_hours) + 'h', color: 'var(--warn)' },
            { label: 'Code coverage (%)', value: d.code_coverage, display: fmtPct(d.code_coverage), color: 'var(--ok)' },
            { label: 'Build success (%)', value: d.build_success_rate, display: fmtPct(d.build_success_rate), color: 'var(--ok)' },
          ]} />
        </Panel>
        <Panel title={t('lblSecurityPosture')} icon={ShieldCheck}>
          <StatGrid>
            <Stat label={t('lblSecurityScore')} value={fmtNum(s.security_score)} unit="/100" icon={Lock} accent={ACCENT} good="up" />
            <Stat label={t('lblOpenVulns')} value={fmtNum(s.vulnerabilities_open)} icon={Bug} accent="var(--bad)" good="down" />
            <Stat label={t('lblCriticalVulns')} value={fmtNum(s.vulnerabilities_critical)} icon={AlertTriangle} accent="var(--bad)" good="down" />
            <Stat label={t('lblCompliance')} value={fmtPct(s.compliance_score)} icon={ShieldCheck} accent={ACCENT} good="up" />
            <Stat label={t('lblPhishingBlocked')} value={fmtNum(s.phishing_attempts_blocked)} icon={Lock} accent={ACCENT} />
            <Stat label={t('lblBackupSuccess')} value={fmtPct(s.backup_success_rate)} icon={ShieldCheck} accent={ACCENT} good="up" />
          </StatGrid>
        </Panel>
      </Grid>
    </div>
  )
}
