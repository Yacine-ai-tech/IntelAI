import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import * as api from '../api'
import { useTranslation } from '../i18n/I18nContext'
import { BarChart3, Hash, Calendar, Layers, FolderKanban, TrendingUp } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

function MetricChart({ data, title }) {
  if (!data || data.length === 0) return null

  const chartData = data.slice(-20).map(d => ({
    period: d.period || d.date || '',
    value: d.value || 0
  }))

  return (
    <div className="card">
      <h3 className="card-title">{title}</h3>
      <div style={{ height: 250 }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="period" 
              style={{ fontSize: '0.7rem', fill: 'var(--text-muted)' }}
            />
            <YAxis 
              style={{ fontSize: '0.7rem', fill: 'var(--text-muted)' }}
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: 'var(--card-bg)', 
                border: '1px solid var(--border)',
                borderRadius: '4px'
              }}
              itemStyle={{ color: 'var(--text)' }}
            />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="value" 
              stroke="var(--primary)" 
              strokeWidth={2}
              dot={{ r: 4 }}
              activeDot={{ r: 6 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

export default function AnalyticsPage() {
  const { t } = useTranslation()
  const queryClient = useQueryClient()
  const [selectedMetric, setSelectedMetric] = useState('')

  // Use React Query for cached data fetching
  const { data: kpis = [], isLoading: kpisLoading } = useQuery({
    queryKey: ['kpis'],
    queryFn: () => api.getKPIs().then(res => res.data?.metrics || []),
    staleTime: 5 * 60 * 1000, // 5 minutes
  })

  const { data: periods = [], isLoading: periodsLoading } = useQuery({
    queryKey: ['periods'],
    queryFn: () => api.getPeriods().then(res => res.data?.periods || []),
    staleTime: 10 * 60 * 1000, // 10 minutes
  })

  const { data: metrics = [], isLoading: metricsLoading } = useQuery({
    queryKey: ['metrics'],
    queryFn: () => api.getMetrics().then(res => res.data?.metrics || []),
    staleTime: 10 * 60 * 1000, // 10 minutes
  })

  // Forecast mutation
  const forecastMutation = useMutation({
    mutationFn: (metric) => api.runForecast(metric, 6).then(res => res.data),
    onSuccess: (data) => {
      // Invalidate relevant queries if needed
      queryClient.invalidateQueries(['forecast', selectedMetric])
    },
  })

  const runForecast = () => {
    if (!selectedMetric) return
    forecastMutation.mutate(selectedMetric)
  }

  const loading = kpisLoading || periodsLoading || metricsLoading
  const forecastLoading = forecastMutation.isPending
  const forecast = forecastMutation.data || null

  // Group KPIs by category
  const categories = {}
  kpis.forEach(k => {
    const cat = k.category || 'Other'
    if (!categories[cat]) categories[cat] = []
    categories[cat].push(k)
  })

  // Create chart data from KPIs
  const revenueData = kpis
    .filter(k => k.metric_name?.toLowerCase().includes('revenue') || k.category === 'revenue')
    .map(k => ({ period: k.period || '', value: k.value || 0 }))
    .sort((a, b) => a.period.localeCompare(b.period))

  return (
    <div>
      <h1 className="page-title" style={{ marginBottom: 24 }}><BarChart3 size={24} /> {t('analytics')}</h1>

      {loading ? (
        <div className="text-center" style={{ padding: 60 }}>{t('loading')}</div>
      ) : (
        <>
          {/* Summary Stats */}
          <div className="kpi-grid" style={{ marginBottom: 24 }}>
            <div className="kpi-card">
              <div className="kpi-label">{t('totalMetrics')}</div>
              <div className="kpi-value">{metrics.length}</div>
            </div>
            <div className="kpi-card">
              <div className="kpi-label">{t('timePeriods')}</div>
              <div className="kpi-value">{periods.length}</div>
            </div>
            <div className="kpi-card">
              <div className="kpi-label">{t('dataPoints')}</div>
              <div className="kpi-value">{kpis.length}</div>
            </div>
            <div className="kpi-card">
              <div className="kpi-label">{t('categories')}</div>
              <div className="kpi-value">{Object.keys(categories).length}</div>
            </div>
          </div>

          {/* Chart */}
          {revenueData.length > 0 && (
            <MetricChart data={revenueData} title="Revenue Trend" />
          )}

          {/* Forecast */}
          <div className="card" style={{ marginTop: 20 }}>
            <h3 className="card-title">{t('forecasting')}</h3>
            <div style={{ display: 'flex', gap: 12, alignItems: 'center', marginBottom: 16 }}>
              <select
                className="form-input"
                style={{ flex: 1 }}
                value={selectedMetric}
                onChange={e => setSelectedMetric(e.target.value)}
              >
                <option value="">{t('selectMetric')}</option>
                {metrics.map((m, i) => (
                  <option key={i} value={m}>{m}</option>
                ))}
              </select>
              <button
                className="btn btn-primary"
                onClick={runForecast}
                disabled={!selectedMetric || forecastLoading}
              >
                {forecastLoading ? t('running') : t('runForecast')}
              </button>
            </div>

            {forecast && (
              forecast.error ? (
                <p style={{ color: '#ef4444' }}>{forecast.error}</p>
              ) : (
                <div>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12, marginBottom: 16 }}>
                    <div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Method</div>
                      <div style={{ fontWeight: 600 }}>{forecast.method}</div>
                    </div>
                    <div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Confidence</div>
                      <div style={{ fontWeight: 600 }}>{forecast.confidence ? `${(forecast.confidence * 100).toFixed(0)}%` : '—'}</div>
                    </div>
                    <div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Periods</div>
                      <div style={{ fontWeight: 600 }}>{forecast.predictions?.length || 0}</div>
                    </div>
                  </div>
                  {forecast.predictions && (
                    <table className="table">
                      <thead>
                        <tr><th>Period</th><th>Predicted Value</th></tr>
                      </thead>
                      <tbody>
                        {forecast.predictions.map((p, i) => (
                          <tr key={i}>
                            <td>{p.period || `+${i + 1}`}</td>
                            <td>{typeof p.value === 'number' ? p.value.toFixed(2) : p.value ?? '—'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  )}
                </div>
              )
            )}
          </div>

          {/* KPI Table */}
          {kpis.length > 0 && (
            <div className="card" style={{ marginTop: 20 }}>
              <h3 className="card-title">{t('allMetrics')}</h3>
              <div style={{ maxHeight: 400, overflowY: 'auto' }}>
                <table className="table">
                  <thead>
                    <tr>
                      <th>Metric</th>
                      <th>Value</th>
                      <th>Category</th>
                      <th>Period</th>
                    </tr>
                  </thead>
                  <tbody>
                    {kpis.slice(0, 50).map((k, i) => (
                      <tr key={i}>
                        <td>{k.metric_name || k.name}</td>
                        <td style={{ fontWeight: 600 }}>{typeof k.value === 'number' ? k.value.toFixed(2) : k.value}</td>
                        <td><span className="badge">{k.category || '—'}</span></td>
                        <td>{k.period || '—'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}
