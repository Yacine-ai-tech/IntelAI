import { useState, useMemo } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import * as api from '../api'
import { useTranslation } from '../i18n/I18nContext'
import { BarChart3, Hash, Calendar, Layers, FolderKanban, TrendingUp } from 'lucide-react'
import {
  PageHeader, Stat, StatGrid, Panel, Grid, Loading, AreaTrend, AskCopilot, fmtNum,
} from '../components/ui'

export default function AnalyticsPage() {
  const { user, hasAction } = useAuth()
  const { t } = useTranslation()
  const [metric, setMetric] = useState('')
  const [fcMetric, setFcMetric] = useState('')

  const { data: kpis = [], isLoading } = useQuery({ queryKey: ['kpis'], queryFn: () => api.getKPIs().then(r => r.data?.metrics || []), staleTime: 300_000 })
  const { data: periods = [] } = useQuery({ queryKey: ['periods'], queryFn: () => api.getPeriods().then(r => r.data?.periods || []), staleTime: 600_000 })
  const { data: metricNames = [] } = useQuery({ queryKey: ['metrics'], queryFn: () => api.getMetrics().then(r => r.data?.metrics || []), staleTime: 600_000 })

  const forecast = useMutation({ mutationFn: (m) => api.runForecast(m, 6).then(r => r.data) })

  const categories = useMemo(() => [...new Set(kpis.map(k => k.category).filter(Boolean))], [kpis])
  const selected = metric || metricNames[0] || ''
  const series = useMemo(() => kpis
    .filter(k => (k.metric_name || k.name) === selected)
    .map(k => ({ period: k.period, value: Math.round((k.value || 0) * 100) / 100 }))
    .sort((a, b) => (a.period || '').localeCompare(b.period || '')), [kpis, selected])

  if (isLoading) return <Loading />
  const fc = forecast.data

  return (
    <div>
      <PageHeader icon={BarChart3} title={t('navAnalytics') || 'Analytics'}
        subtitle={t('analyticsSubtitle') || 'Cross-domain KPI explorer & forecasting'}
        actions={<AskCopilot q="What are the most important trends across all our KPIs this period?" />} />

      <StatGrid>
        <Stat label={t('totalMetrics') || 'Metrics'} value={fmtNum(metricNames.length)} icon={Hash} />
        <Stat label={t('timePeriods') || 'Periods'} value={fmtNum(periods.length)} icon={Calendar} />
        <Stat label={t('dataPoints') || 'Data points'} value={fmtNum(kpis.length)} icon={Layers} />
        <Stat label={t('categories') || 'Domains'} value={fmtNum(categories.length)} icon={FolderKanban} />
      </StatGrid>

      <Panel title={t('metricExplorer') || 'Metric explorer'} icon={TrendingUp} style={{ marginTop: 18 }}
        actions={
          <select className="form-input" style={{ width: 220 }} value={selected} onChange={e => setMetric(e.target.value)}>
            {metricNames.map((m, i) => <option key={i} value={m}>{m}</option>)}
          </select>
        }>
        <AreaTrend data={series} y="value" />
      </Panel>

      <Grid style={{ marginTop: 18 }} min={320}>
        {hasAction('forecast') && (
          <Panel title={t('forecasting') || 'Forecast'} icon={TrendingUp}>
            <div style={{ display: 'flex', gap: 10, marginBottom: 14 }}>
              <select className="form-input" style={{ flex: 1 }} value={fcMetric} onChange={e => setFcMetric(e.target.value)}>
                <option value="">{t('selectMetric') || 'Select a metric…'}</option>
                {metricNames.map((m, i) => <option key={i} value={m}>{m}</option>)}
              </select>
              <button className="btn btn-primary" disabled={!fcMetric || forecast.isPending} onClick={() => forecast.mutate(fcMetric)}>
                {forecast.isPending ? (t('running') || 'Running…') : (t('runForecast') || 'Run')}
              </button>
            </div>
            {fc && !fc.error && (
              <>
                <div style={{ display: 'flex', gap: 16, marginBottom: 12, fontSize: '.82rem', color: 'var(--text-2)' }}>
                  <span>{t('method') || 'Method'}: <b style={{ color: 'var(--text)' }}>{fc.method}</b></span>
                  {fc.confidence != null && <span>{t('confidence') || 'Confidence'}: <b style={{ color: 'var(--text)' }}>{(fc.confidence * 100).toFixed(0)}%</b></span>}
                </div>
                <AreaTrend data={(fc.predictions || []).map((p, i) => ({ period: p.period || `+${i + 1}`, value: typeof p.value === 'number' ? Math.round(p.value * 100) / 100 : 0 }))} y="value" color="var(--accent)" height={180} />
              </>
            )}
            {fc?.error && <div className="alert alert-danger">{fc.error}</div>}
          </Panel>
        )}

        <Panel title={t('allMetrics') || 'All metrics'} icon={Layers} style={{ gridColumn: 'span 2' }}>
          <div style={{ maxHeight: 360, overflowY: 'auto' }}>
            <table className="table">
              <thead><tr><th>Metric</th><th>Value</th><th>Domain</th><th>Period</th></tr></thead>
              <tbody>
                {kpis.slice(0, 60).map((k, i) => (
                  <tr key={i}>
                    <td>{k.metric_name || k.name}</td>
                    <td style={{ fontFamily: 'var(--font-mono)' }}>{typeof k.value === 'number' ? fmtNum(k.value) : k.value}</td>
                    <td><span className="badge">{k.category || '—'}</span></td>
                    <td>{k.period || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Panel>
      </Grid>
    </div>
  )
}
