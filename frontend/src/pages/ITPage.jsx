import { useQuery } from '@tanstack/react-query'
import * as api from '../api'
import { useTranslation } from '../i18n/I18nContext'
import {
  Monitor, Activity, Ticket, Timer, ShieldCheck, Server, DollarSign, Rocket,
  AlertTriangle, Bug, Lock, GitBranch,
} from 'lucide-react'
import {
  PageHeader, Stat, StatGrid, Panel, Grid, Loading, BarList, AskCopilot,
  fmtNum, fmtMoney, fmtPct,
} from '../components/ui'

const ACCENT = 'var(--p-cto)'

export default function ITPage() {
  const { t } = useTranslation()
  const ov = useQuery({ queryKey: ['it-ov'], queryFn: () => api.getITOverview().then(r => r.data), retry: 1 })
  const sec = useQuery({ queryKey: ['it-sec'], queryFn: () => api.getITSecurity().then(r => r.data), retry: 1 })
  const dev = useQuery({ queryKey: ['it-dev'], queryFn: () => api.getITDevOps().then(r => r.data), retry: 1 })

  if (ov.isLoading) return <Loading />
  const o = ov.data || {}, s = sec.data || {}, d = dev.data || {}

  return (
    <div>
      <PageHeader icon={Monitor} accent={ACCENT} title={t('navIT') || 'IT Operations'}
        subtitle={t('itSubtitle') || 'Reliability, security & DevOps performance (DORA)'}
        actions={<AskCopilot q="How healthy is our IT — uptime, security posture and DORA metrics — vs 2026 benchmarks?" />} />

      <StatGrid>
        <Stat label="System Uptime" value={fmtPct(o.system_uptime)} icon={Activity} accent={ACCENT} good="up" hint="2026 elite: 99.99%" />
        <Stat label="Open Tickets" value={fmtNum(o.open_tickets)} icon={Ticket} accent={ACCENT} good="down" />
        <Stat label="MTTR" value={fmtNum(o.mttr_hours)} unit="h" icon={Timer} accent={ACCENT} good="down" hint="DORA elite: <1h" />
        <Stat label="SLA Compliance" value={fmtPct(o.sla_compliance)} icon={ShieldCheck} accent={ACCENT} good="up" />
        <Stat label="Security Score" value={fmtNum(o.security_score)} unit="/100" icon={Lock} accent={ACCENT} good="up" />
        <Stat label="Servers" value={fmtNum(o.server_count)} icon={Server} accent={ACCENT} />
        <Stat label="Cloud Spend" value={fmtMoney(o.cloud_spend)} icon={DollarSign} accent={ACCENT} good="down" />
        <Stat label="Deploy Frequency" value={fmtNum(o.deployment_frequency)} unit="/mo" icon={Rocket} accent={ACCENT} good="up" />
      </StatGrid>

      <Grid style={{ marginTop: 18 }}>
        <Panel title="DevOps — DORA metrics" icon={GitBranch}
          actions={<AskCopilot q="Interpret our DORA metrics vs the 2026 elite benchmarks and what to improve first." label="Interpret" />}>
          <BarList items={[
            { label: 'Deployment frequency (/mo)', value: d.deployment_frequency, display: fmtNum(d.deployment_frequency) },
            { label: 'Lead time (h)', value: d.lead_time_hours, display: fmtNum(d.lead_time_hours) + 'h', color: 'var(--warn)' },
            { label: 'Change failure rate (%)', value: d.change_failure_rate, display: fmtPct(d.change_failure_rate), color: 'var(--bad)' },
            { label: 'MTTR (h)', value: d.mttr_hours, display: fmtNum(d.mttr_hours) + 'h', color: 'var(--warn)' },
            { label: 'Code coverage (%)', value: d.code_coverage, display: fmtPct(d.code_coverage), color: 'var(--ok)' },
            { label: 'Build success (%)', value: d.build_success_rate, display: fmtPct(d.build_success_rate), color: 'var(--ok)' },
          ]} />
        </Panel>
        <Panel title="Security posture" icon={ShieldCheck}>
          <StatGrid>
            <Stat label="Security Score" value={fmtNum(s.security_score)} unit="/100" icon={Lock} accent={ACCENT} good="up" />
            <Stat label="Open Vulns" value={fmtNum(s.vulnerabilities_open)} icon={Bug} accent="var(--bad)" good="down" />
            <Stat label="Critical Vulns" value={fmtNum(s.vulnerabilities_critical)} icon={AlertTriangle} accent="var(--bad)" good="down" />
            <Stat label="Compliance" value={fmtPct(s.compliance_score)} icon={ShieldCheck} accent={ACCENT} good="up" />
            <Stat label="Phishing Blocked" value={fmtNum(s.phishing_attempts_blocked)} icon={Lock} accent={ACCENT} />
            <Stat label="Backup Success" value={fmtPct(s.backup_success_rate)} icon={ShieldCheck} accent={ACCENT} good="up" />
          </StatGrid>
        </Panel>
      </Grid>
    </div>
  )
}
