import { useState, useMemo, Component } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import * as api from '../api'
import { useAuth } from '../context/AuthContext'
import { useTranslation } from '../i18n/I18nContext'
import { BarChart3, Hash, Calendar, Layers, FolderKanban, TrendingUp, AlertTriangle, ChevronDown, ChevronUp, Search } from 'lucide-react'
import { PageHeader, Stat, StatGrid, fmtNum, Loading, ErrorState, Grid, AskCopilot, AreaTrend, Panel } from '../components/ui'
import PeriodFilter from '../components/PeriodFilter'

class AnalyticsErrorBoundary extends Component {
  constructor(props) { super(props); this.state = { hasError: false, error: null } }
  static getDerivedStateFromError(error) { return { hasError: true, error } }
  componentDidCatch(error, info) { console.error('AnalyticsPage error:', error, info) }
  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text, #fff)' }}>
          <AlertTriangle size={40} style={{ color: '#f59e0b', marginBottom: 16 }} />
          <h2 style={{ marginBottom: 8 }}>Analytics Unavailable</h2>
          <p style={{ color: 'var(--text-2, #94a3b8)', marginBottom: 20 }}>
            {this.state.error?.message || 'The analytics panel encountered an error.'}
          </p>
          <button className="btn btn-primary" onClick={() => this.setState({ hasError: false, error: null })}>
            Retry
          </button>
        </div>
      )
    }
    return this.props.children
  }
}

export default function AnalyticsPage() {
  return (
    <AnalyticsErrorBoundary>
      <AnalyticsInner />
    </AnalyticsErrorBoundary>
  )
}

function AnalyticsInner() {
  const { user, hasAction } = useAuth()
  const { t } = useTranslation()
  const [metric, setMetric] = useState('')
  const [fcMetric, setFcMetric] = useState('')
  const [startPeriod, setStartPeriod] = useState('')
  const [endPeriod, setEndPeriod] = useState('')
  const [tablePeriod, setTablePeriod] = useState('')
  const [tableSearch, setTableSearch] = useState('')
  const [tableCategory, setTableCategory] = useState('')
  const [showForecastPanel, setShowForecastPanel] = useState(true)

  // Fetch full KPI dataset (limit=10000 ensures 2020-01 to 2026-06 across all metrics)
  const { data: kpis = [], isLoading, isError } = useQuery({
    queryKey: ['kpis-all'],
    queryFn: () => api.getKPIs({ limit: 10000 }).then(r => r.data?.metrics || []),
    staleTime: 300_000,
  })
  const { data: periods = [] } = useQuery({
    queryKey: ['periods'],
    queryFn: () => api.getPeriods().then(r => r.data?.periods || []),
    staleTime: 600_000,
  })
  const { data: metricNames = [] } = useQuery({
    queryKey: ['metrics'],
    queryFn: () => api.getMetrics().then(r => r.data?.metrics || []),
    staleTime: 600_000,
  })

  const forecast = useMutation({
    mutationFn: (m) => api.runForecast(m, 6).then(r => r.data),
  })

  const sortedPeriods = useMemo(() => [...periods].sort(), [periods])
  const latestPeriod = sortedPeriods[sortedPeriods.length - 1] || '2026-06'
  const activeTablePeriod = tablePeriod || latestPeriod

  const categories = useMemo(() => [...new Set(kpis.map(k => k.category).filter(Boolean))].sort(), [kpis])

  const selected = metric || metricNames[0] || ''

  // Metric Explorer series filtered by selected date interval
  const series = useMemo(() => {
    return kpis
      .filter(k => k.metric === selected)
      .filter(k => {
        if (startPeriod && (k.period || '') < startPeriod) return false
        if (endPeriod && (k.period || '') > endPeriod) return false
        return true
      })
      .map(k => ({ period: k.period, value: Math.round((k.value || 0) * 100) / 100 }))
      .sort((a, b) => (a.period || '').localeCompare(b.period || ''))
  }, [kpis, selected, startPeriod, endPeriod])

  // Table rows filtered by selected snapshot month and optional search/category
  const tableRows = useMemo(() => {
    return kpis
      .filter(k => {
        if (activeTablePeriod !== 'ALL' && k.period !== activeTablePeriod) return false
        if (tableCategory && k.category !== tableCategory) return false
        if (tableSearch) {
          const q = tableSearch.toLowerCase()
          return (k.metric || '').toLowerCase().includes(q) || (k.category || '').toLowerCase().includes(q)
        }
        return true
      })
      .sort((a, b) => (a.metric || '').localeCompare(b.metric || ''))
  }, [kpis, activeTablePeriod, tableCategory, tableSearch])

  if (isLoading && kpis.length === 0) return <Loading />
  if (isError) return <ErrorState />
  if (!isLoading && kpis.length === 0 && metricNames.length === 0) {
    return (
      <div className="empty-state-fallback" style={{ padding: '50px', textAlign: 'center', color: '#fff' }}>
        <h2>No Analytics Data Available</h2>
        <p>The backend may be offline or returned no data.</p>
      </div>
    )
  }

  const fc = forecast.data
  const forecastSeries = (fc?.forecast || []).map((p, i) => ({
    period: p.month_tag || `+${i + 1}`,
    value: typeof p.forecast === 'number' ? Math.round(p.forecast * 100) / 100 : 0,
    lower: typeof p.lower_bound === 'number' ? Math.round(p.lower_bound * 100) / 100 : null,
    upper: typeof p.upper_bound === 'number' ? Math.round(p.upper_bound * 100) / 100 : null,
  }))

  return (
    <div>
      <PageHeader
        icon={BarChart3}
        title={t('navAnalytics') || 'Analytics'}
        subtitle={t('analyticsSubtitle') || 'Cross-domain KPI explorer & forecasting'}
        actions={<AskCopilot q={t('askCopilot_AnalyticsPage_WhatAreThe')} />}
      />

      <StatGrid>
        <Stat label={t('totalMetrics') || 'Metrics'} value={fmtNum(metricNames.length)} icon={Hash} />
        <Stat label={t('timePeriods') || 'Periods'} value={fmtNum(periods.length)} icon={Calendar} />
        <Stat label={t('dataPoints') || 'Data points'} value={fmtNum(kpis.length)} icon={Layers} />
        <Stat label={t('categories') || 'Domains'} value={fmtNum(categories.length)} icon={FolderKanban} />
      </StatGrid>

      {/* Global Date Interval Filter Toolbar */}
      <PeriodFilter
        periods={periods}
        startPeriod={startPeriod}
        endPeriod={endPeriod}
        onRangeChange={({ start, end }) => {
          setStartPeriod(start)
          setEndPeriod(end)
        }}
        selectedPeriod={activeTablePeriod}
        onSelectPeriod={(p) => setTablePeriod(p)}
        showPresets={true}
        showInterval={true}
        showSnapshot={false}
      />

      {/* Metric Explorer Panel */}
      <Panel
        title={t('metricExplorer') || 'Metric explorer'}
        icon={TrendingUp}
        style={{ marginTop: 12 }}
        actions={
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <span style={{ fontSize: '.82rem', color: 'var(--text-2)' }}>{series.length} {t('points') || 'points'}:</span>
            <select
              className="form-input"
              style={{ width: 240, height: 34 }}
              value={selected}
              onChange={(e) => setMetric(e.target.value)}
            >
              {metricNames.map((m, i) => (
                <option key={i} value={m}>{m}</option>
              ))}
            </select>
          </div>
        }
      >
        <AreaTrend data={series} y="value" height={260} />
      </Panel>

      <Grid style={{ marginTop: 18 }} min={320}>
        {/* Collapsible & Working Forecasting Panel */}
        {hasAction('forecast') && (
          <Panel
            title={t('forecasting') || 'Forecast'}
            icon={TrendingUp}
            actions={
              <button
                type="button"
                className="btn btn-sm btn-ghost"
                onClick={() => setShowForecastPanel(!showForecastPanel)}
                style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: '.78rem' }}
              >
                {showForecastPanel ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                <span>{showForecastPanel ? (t('hide') || 'Hide') : (t('show') || 'Show')}</span>
              </button>
            }
          >
            {showForecastPanel && (
              <div>
                <div style={{ display: 'flex', gap: 10, marginBottom: 14 }}>
                  <select
                    className="form-input"
                    style={{ flex: 1, height: 34 }}
                    value={fcMetric}
                    onChange={(e) => setFcMetric(e.target.value)}
                  >
                    <option value="">{t('selectMetric') || 'Select a metric…'}</option>
                    {metricNames.map((m, i) => (
                      <option key={i} value={m}>{m}</option>
                    ))}
                  </select>
                  <button
                    className="btn btn-primary"
                    style={{ height: 34 }}
                    disabled={!fcMetric || forecast.isPending}
                    onClick={() => forecast.mutate(fcMetric)}
                  >
                    {forecast.isPending ? (t('running') || 'Running…') : (t('runForecast') || 'Run')}
                  </button>
                </div>

                {fc && !fc.error && (
                  <>
                    <div
                      style={{
                        display: 'flex',
                        flexWrap: 'wrap',
                        gap: 14,
                        marginBottom: 12,
                        padding: '8px 12px',
                        background: 'var(--surface-2)',
                        borderRadius: 6,
                        fontSize: '.82rem',
                        color: 'var(--text-2)',
                      }}
                    >
                      <span>
                        {t('method') || 'Method'}: <b style={{ color: 'var(--text)' }}>Linear Trend (95% CI)</b>
                      </span>
                      {fc.explanation?.r_squared != null && (
                        <span>
                          R² Fit: <b style={{ color: 'var(--text)' }}>{(fc.explanation.r_squared * 100).toFixed(1)}%</b>
                        </span>
                      )}
                      {fc.explanation?.slope != null && (
                        <span>
                          Trend: <b style={{ color: fc.explanation.slope >= 0 ? 'var(--ok)' : 'var(--warn)' }}>
                            {fc.explanation.slope >= 0 ? '↑ Positive' : '↓ Negative'} ({fc.explanation.slope.toFixed(2)}/mo)
                          </b>
                        </span>
                      )}
                    </div>

                    {forecastSeries.length > 0 ? (
                      <AreaTrend
                        data={forecastSeries}
                        y="value"
                        color="var(--accent)"
                        height={180}
                      />
                    ) : (
                      <div style={{ padding: '14px', fontSize: '.84rem', color: 'var(--text-3)', textAlign: 'center' }}>
                        {fc.message || t('noForecastData') || 'Insufficient historical data to produce a multi-step forecast.'}
                      </div>
                    )}
                  </>
                )}

                {fc?.error && <div className="alert alert-danger" style={{ marginTop: 10 }}>{fc.error}</div>}
              </div>
            )}
          </Panel>
        )}

        {/* All Metrics Table with Period Selector & Search Filter */}
        <Panel
          title={t('allMetrics') || 'All metrics'}
          icon={Layers}
          style={{ gridColumn: hasAction('forecast') ? 'span 2' : 'span 3' }}
          actions={
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
              {/* Period Selector */}
              <select
                className="form-input"
                style={{ height: 30, padding: '2px 8px', fontSize: '.80rem', minWidth: 120 }}
                value={activeTablePeriod}
                onChange={(e) => setTablePeriod(e.target.value)}
              >
                <option value="ALL">{t('allPeriods') || 'All periods'}</option>
                {[...sortedPeriods].reverse().map((p) => (
                  <option key={p} value={p}>
                    {p} {p === latestPeriod ? `(${t('latest') || 'Latest'})` : ''}
                  </option>
                ))}
              </select>

              {/* Category Filter */}
              <select
                className="form-input"
                style={{ height: 30, padding: '2px 8px', fontSize: '.80rem', minWidth: 100 }}
                value={tableCategory}
                onChange={(e) => setTableCategory(e.target.value)}
              >
                <option value="">{t('allDomains') || 'All Domains'}</option>
                {categories.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>

              {/* Search box */}
              <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
                <Search size={13} style={{ position: 'absolute', left: 8, color: 'var(--text-3)' }} />
                <input
                  className="form-input"
                  type="text"
                  placeholder={t('searchPlaceholder') || 'Search…'}
                  value={tableSearch}
                  onChange={(e) => setTableSearch(e.target.value)}
                  style={{ height: 30, paddingLeft: 26, paddingRight: 8, fontSize: '.80rem', width: 120 }}
                />
              </div>
            </div>
          }
        >
          <div style={{ maxHeight: 380, overflowY: 'auto' }}>
            <table className="table">
              <thead>
                <tr>
                  <th>{t('thMetric') || 'Metric'}</th>
                  <th>{t('thValue') || 'Value'}</th>
                  <th>{t('thDomain') || 'Domain'}</th>
                  <th>{t('thPeriod') || 'Period'}</th>
                </tr>
              </thead>
              <tbody>
                {tableRows.slice(0, 100).map((k, i) => (
                  <tr key={i}>
                    <td>{k.metric}</td>
                    <td style={{ fontFamily: 'var(--font-mono)' }}>
                      {typeof k.value === 'number' ? fmtNum(k.value) : k.value}
                    </td>
                    <td><span className="badge">{k.category || '—'}</span></td>
                    <td>{k.period || '—'}</td>
                  </tr>
                ))}
                {tableRows.length === 0 && (
                  <tr>
                    <td colSpan={4} style={{ textAlign: 'center', color: 'var(--text-3)', padding: 20 }}>
                      {t('noResults') || 'No metrics found matching criteria.'}
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
          {tableRows.length > 100 && (
            <div style={{ padding: '8px 12px', fontSize: '.78rem', color: 'var(--text-3)', textAlign: 'right' }}>
              Showing 100 of {tableRows.length} metrics
            </div>
          )}
        </Panel>
      </Grid>
    </div>
  )
}
