import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useTranslation } from '../i18n/I18nContext'
import * as api from '../api'
import { DollarSign, TrendingUp, Percent, Banknote, Wallet, FileText, Coins } from 'lucide-react'
import { fmtPct, PageHeader, Stat, StatGrid, Line, fmtNum, Loading, Grid, AskCopilot, AreaTrend, Panel, fmtMoney, fmtCurrency, MiniBars } from '../components/ui'
import PeriodFilter from '../components/PeriodFilter'

const ACCENT = 'var(--p-cfo)'
const ICONS = { Revenue: DollarSign, 'Gross Margin': Percent, EBITDA: TrendingUp, 'Net Profit': Banknote, 'Operating Cash Flow': Wallet, 'Operating Costs': Coins }

const fmtVal = (k) => {
  const u = (k.unit || '').toLowerCase()
  if (u === '%') return fmtPct(k.value)
  if (u === 'usd') return fmtMoney(k.value)
  if (u === 'xof' || u === 'fcfa') return fmtCurrency(k.value, 'XOF')
  if (u === 'days') return fmtNum(k.value) + ' d'
  if (u === 'months') return fmtNum(k.value) + ' mo'
  if (u === 'ratio') return fmtNum(k.value) + '×'
  return fmtNum(k.value)
}

export default function FinancialPage() {
  const { t } = useTranslation()
  const [type, setType] = useState('income_statement')
  const [period, setPeriod] = useState('')
  const [selectedSnapshot, setSelectedSnapshot] = useState('')
  const [startPeriod, setStartPeriod] = useState('')
  const [endPeriod, setEndPeriod] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const { data: kpis = [], isLoading } = useQuery({
    queryKey: ['fin-kpis'],
    queryFn: () => api.getKPIs({ category: 'Finance', limit: 10000 }).then(r => r.data?.metrics || []),
    retry: 1,
    staleTime: 300_000,
  })

  const { data: periods = [] } = useQuery({
    queryKey: ['periods'],
    queryFn: () => api.getPeriods().then(r => r.data?.periods || []),
    staleTime: 600_000,
  })

  const sortedPeriods = useMemo(() => [...periods].sort(), [periods])
  const latestPeriod = sortedPeriods[sortedPeriods.length - 1] || '2026-06'
  const activePeriod = selectedSnapshot || latestPeriod

  // Group metrics and get reading for the chosen snapshot period (or latest <= activePeriod)
  const { snapshotMetrics, revSeries } = useMemo(() => {
    const byMetric = {}
    kpis.forEach(k => {
      const n = k.metric || k.metric_name || k.name
      ;(byMetric[n] = byMetric[n] || []).push(k)
    })
    Object.values(byMetric).forEach(a => a.sort((x, y) => (x.period || '').localeCompare(y.period || '')))

    const snapshot = Object.entries(byMetric).map(([n, rows]) => {
      // Find row for activePeriod, or highest period <= activePeriod
      const matching = rows.filter(r => (r.period || '') <= activePeriod)
      const row = matching.length > 0 ? matching[matching.length - 1] : rows[rows.length - 1]
      return { ...row, name: n }
    })

    // Revenue trend filtered by startPeriod and endPeriod
    const revRows = (byMetric['Revenue'] || []).filter(k => {
      if (startPeriod && (k.period || '') < startPeriod) return false
      if (endPeriod && (k.period || '') > endPeriod) return false
      return true
    })
    const trend = (revRows.length > 0 ? revRows : (byMetric['Revenue'] || []).slice(-12)).map(k => ({
      period: k.period,
      value: Math.round(k.value),
    }))

    return { snapshotMetrics: snapshot, revSeries: trend }
  }, [kpis, activePeriod, startPeriod, endPeriod])

  const runGenerate = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      setResult((await api.generateStatement(type, period || activePeriod || null)).data)
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed')
    }
    setLoading(false)
  }

  const lineItems = (result?.line_items || []).map(it => ({
    name: it.item_name || it.name || '—',
    value: it.amount || it.value || 0,
  }))

  if (isLoading && kpis.length === 0) return <Loading />

  return (
    <div>
      <PageHeader
        icon={DollarSign}
        accent={ACCENT}
        title={t('navFinancial') || 'Financial'}
        subtitle={t('finSubtitle') || 'Financial position, profitability & statements'}
        actions={<AskCopilot q={t('askCopilot_FinancialPage_GiveMeA')} />}
      />

      {/* Reusable Period Filter */}
      <PeriodFilter
        periods={periods}
        selectedPeriod={activePeriod}
        onSelectPeriod={(p) => {
          setSelectedSnapshot(p)
          setPeriod(p)
        }}
        startPeriod={startPeriod}
        endPeriod={endPeriod}
        onRangeChange={({ start, end }) => {
          setStartPeriod(start)
          setEndPeriod(end)
        }}
        accent={ACCENT}
      />

      <StatGrid>
        {snapshotMetrics.map((k, i) => {
          const Icon = ICONS[k.name] || DollarSign
          return (
            <Stat
              key={i}
              label={k.name}
              icon={Icon}
              accent={ACCENT}
              value={fmtVal(k)}
              good={k.direction || (/cost|cogs|tax|churn/i.test(k.name) ? 'down' : 'up')}
            />
          )
        })}
      </StatGrid>

      <Panel title={t('revenueTrend') || 'Revenue trend'} icon={TrendingUp} style={{ marginTop: 18 }}>
        <AreaTrend data={revSeries} y="value" color={ACCENT} height={240} />
      </Panel>

      <Grid style={{ marginTop: 18 }} min={320}>
        <Panel title={t('generateStatement') || 'Generate statement'} icon={FileText}>
          <form onSubmit={runGenerate}>
            <div className="form-group">
              <label className="form-label">{t('statementType') || 'Statement type'}</label>
              <select className="form-input" value={type} onChange={e => setType(e.target.value)}>
                <option value="income_statement">{t('incomeStatement') || 'Income Statement (P&L)'}</option>
                <option value="balance_sheet">{t('balanceSheet') || 'Balance Sheet'}</option>
                <option value="cash_flow">{t('cashFlow') || 'Cash Flow'}</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">{t('period') || 'Period'}</label>
              <input
                className="form-input"
                value={period || activePeriod}
                onChange={e => setPeriod(e.target.value)}
                placeholder={t('finPlaceholder') || 'e.g. 2026-05 (year-month)'}
              />
            </div>
            <button className="btn btn-primary" type="submit" disabled={loading}>
              {loading ? (t('generating') || 'Generating…') : (t('generate') || 'Generate')}
            </button>
          </form>
        </Panel>

        <Panel
          title={result?.statement_type ? result.statement_type.replace(/_/g, ' ') : (t('result') || 'Result')}
          icon={DollarSign}
          style={{ gridColumn: 'span 2' }}
        >
          {error && <div className="alert alert-danger">{error}</div>}
          {!result && !error && <p className="text-muted">{t('noResult') || 'Generate a statement to see the breakdown.'}</p>}
          {result && (
            <>
              {lineItems.length > 0 && (
                <MiniBars data={lineItems} x="name" y="value" color={ACCENT} height={Math.max(180, lineItems.length * 30)} />
              )}
              <table className="table" style={{ marginTop: 14 }}>
                <thead>
                  <tr>
                    <th>{t('lineItem') || 'Line item'}</th>
                    <th style={{ textAlign: 'right' }}>{t('amount') || 'Amount'}</th>
                  </tr>
                </thead>
                <tbody>
                  {lineItems.map((it, i) => (
                    <tr key={i}>
                      <td>{it.name}</td>
                      <td style={{ textAlign: 'right', fontFamily: 'var(--font-mono)' }}>{fmtMoney(it.value)}</td>
                    </tr>
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
