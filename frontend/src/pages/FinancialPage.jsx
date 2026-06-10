import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useTranslation } from '../i18n/I18nContext'
import * as api from '../api'
import { DollarSign, TrendingUp, Percent, Banknote, Wallet, FileText, Coins } from 'lucide-react'
import {
  PageHeader, Stat, StatGrid, Panel, Grid, Loading, AreaTrend, MiniBars, AskCopilot,
  fmtNum, fmtMoney, fmtPct,
} from '../components/ui'

const ACCENT = 'var(--p-cfo)'
const ICONS = { Revenue: DollarSign, 'Gross Margin': Percent, EBITDA: TrendingUp, 'Net Profit': Banknote, 'Operating Cash Flow': Wallet, 'Operating Costs': Coins }

// Format a KPI row by its declared unit (Finance now spans %, days, months, ratio, score, USD).
const fmtVal = (k) => {
  const u = (k.unit || '').toLowerCase()
  if (u === '%') return fmtPct(k.value)
  if (u === 'usd') return fmtMoney(k.value)
  if (u === 'days') return fmtNum(k.value) + ' d'
  if (u === 'months') return fmtNum(k.value) + ' mo'
  if (u === 'ratio') return fmtNum(k.value) + '×'
  return fmtNum(k.value)
}

export default function FinancialPage() {
  const { t } = useTranslation()
  const [type, setType] = useState('income_statement')
  const [period, setPeriod] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const { data: kpis = [], isLoading } = useQuery({
    queryKey: ['fin-kpis'], queryFn: () => api.getKPIs({ category: 'Finance' }).then(r => r.data?.metrics || []), retry: 1,
  })

  // latest reading per metric + a revenue series for the trend
  const byMetric = {}
  kpis.forEach(k => { const n = k.metric || k.metric_name || k.name; (byMetric[n] = byMetric[n] || []).push(k) })
  Object.values(byMetric).forEach(a => a.sort((x, y) => (x.period || '').localeCompare(y.period || '')))
  const latest = Object.entries(byMetric).map(([n, a]) => ({ ...a[a.length - 1], name: n }))
  const revSeries = (byMetric['Revenue'] || []).slice(-12).map(k => ({ period: k.period, value: Math.round(k.value) }))

  const runGenerate = async (e) => {
    e.preventDefault(); setLoading(true); setError(null); setResult(null)
    try { setResult((await api.generateStatement(type, period || null)).data) }
    catch (err) { setError(err.response?.data?.detail || err.message || 'Failed') }
    setLoading(false)
  }
  const lineItems = (result?.line_items || []).map(it => ({ name: it.item_name || it.name || '—', value: it.amount || it.value || 0 }))

  if (isLoading) return <Loading />

  return (
    <div>
      <PageHeader icon={DollarSign} accent={ACCENT} title={t('navFinancial') || 'Financial'}
        subtitle={t('finSubtitle') || 'Financial position, profitability & statements'}
        actions={<AskCopilot q="Give me a CFO-level read on our financial health: revenue, margin, EBITDA, cash flow and the Rule of 40." />} />

      <StatGrid>
        {latest.map((k, i) => {
          const Icon = ICONS[k.name] || DollarSign
          return <Stat key={i} label={k.name} icon={Icon} accent={ACCENT}
            value={fmtVal(k)}
            good={k.direction || (/cost|cogs|tax|churn/i.test(k.name) ? 'down' : 'up')} />
        })}
      </StatGrid>

      <Panel title="Revenue trend" icon={TrendingUp} style={{ marginTop: 18 }}>
        <AreaTrend data={revSeries} y="value" color={ACCENT} />
      </Panel>

      <Grid style={{ marginTop: 18 }} min={320}>
        <Panel title="Generate statement" icon={FileText}>
          <form onSubmit={runGenerate}>
            <div className="form-group">
              <label className="form-label">{t('statementType') || 'Statement type'}</label>
              <select className="form-input" value={type} onChange={e => setType(e.target.value)}>
                <option value="income_statement">Income Statement (P&L)</option>
                <option value="balance_sheet">Balance Sheet</option>
                <option value="cash_flow">Cash Flow</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">{t('period') || 'Period'}</label>
              <input className="form-input" value={period} onChange={e => setPeriod(e.target.value)} placeholder="e.g. 2026-Q1 or 2026-05" />
            </div>
            <button className="btn btn-primary" type="submit" disabled={loading}>
              {loading ? (t('generating') || 'Generating…') : (t('generate') || 'Generate')}
            </button>
          </form>
        </Panel>

        <Panel title={result?.statement_type ? result.statement_type.replace(/_/g, ' ') : (t('result') || 'Result')} icon={DollarSign} style={{ gridColumn: 'span 2' }}>
          {error && <div className="alert alert-danger">{error}</div>}
          {!result && !error && <p className="text-muted">{t('noResult') || 'Generate a statement to see the breakdown.'}</p>}
          {result && (
            <>
              {lineItems.length > 0 && <MiniBars data={lineItems} x="name" y="value" color={ACCENT} height={Math.max(180, lineItems.length * 30)} />}
              <table className="table" style={{ marginTop: 14 }}>
                <thead><tr><th>Line item</th><th style={{ textAlign: 'right' }}>Amount</th></tr></thead>
                <tbody>
                  {lineItems.map((it, i) => (
                    <tr key={i}><td>{it.name}</td><td style={{ textAlign: 'right', fontFamily: 'var(--font-mono)' }}>{fmtMoney(it.value)}</td></tr>
                  ))}
                </tbody>
              </table>
            </>
          )}
        </Panel>
      </Grid>
    </div>
  )
}
