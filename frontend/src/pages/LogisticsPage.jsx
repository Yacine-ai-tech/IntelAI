import { useState, useEffect, useCallback } from 'react'
import * as api from '../api'
import { useTranslation } from '../i18n/I18nContext'
import {
  Package, BarChart3, Warehouse, Truck, ClipboardList,
  CheckCircle2, Timer, RefreshCcw, DollarSign, AlertTriangle,
  CornerDownLeft, Target, PackageCheck, Snail, TrendingUp, Crosshair
} from 'lucide-react'

function StatCard({ label, value, unit, icon: Icon, color = 'blue' }) {
  return (
    <div className="kpi-card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <div className="kpi-label">{label}</div>
          <div className="kpi-value">{value}{unit ? <span style={{ fontSize: '0.7em', color: 'var(--text-muted)' }}> {unit}</span> : ''}</div>
        </div>
        <div className={`kpi-icon-wrap ${color}`}><Icon size={20} /></div>
      </div>
    </div>
  )
}

export default function LogisticsPage() {
  const [summary, setSummary] = useState(null)
  const [inventory, setInventory] = useState(null)
  const [shipping, setShipping] = useState(null)
  const [health, setHealth] = useState(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('overview')
  const { t } = useTranslation()

  const fetchData = useCallback(async () => {
    setLoading(true)
    const [s, inv, sh, h] = await Promise.allSettled([
      api.getLogisticsSummary(), api.getLogisticsInventory(),
      api.getLogisticsShipping(), api.getLogisticsHealth(),
    ])
    if (s.status === 'fulfilled') setSummary(s.value.data)
    if (inv.status === 'fulfilled') setInventory(inv.value.data)
    if (sh.status === 'fulfilled') setShipping(sh.value.data)
    if (h.status === 'fulfilled') setHealth(h.value.data)
    setLoading(false)
  }, [])

  useEffect(() => { fetchData() }, [fetchData])

  const fmt = (v) => {
    if (v === null || v === undefined) return '—'
    if (typeof v === 'number') {
      if (Math.abs(v) >= 1e6) return `$${(v / 1e6).toFixed(1)}M`
      if (Math.abs(v) >= 1e3) return `$${(v / 1e3).toFixed(1)}K`
      return v % 1 === 0 ? v.toString() : v.toFixed(1)
    }
    return v
  }

  const tabs = [
    { id: 'overview', label: t('overview'), Icon: BarChart3 },
    { id: 'inventory', label: t('inventory'), Icon: Warehouse },
    { id: 'shipping', label: t('shipping'), Icon: Truck },
  ]

  if (loading) return <div className="text-center" style={{ padding: 60 }}>{t('loading')}</div>

  return (
    <div>
      <h1 className="page-title" style={{ marginBottom: 20 }}><Package size={24} /> {t('logistics')}</h1>

      <div className="tab-bar">
        {tabs.map(tab => (
          <button key={tab.id} className={`tab-btn${activeTab === tab.id ? ' active' : ''}`}
            onClick={() => setActiveTab(tab.id)}>
            <tab.Icon size={15} /> {tab.label}
          </button>
        ))}
      </div>

      {activeTab === 'overview' && summary && (
        <>
          <div className="kpi-grid">
            <StatCard label={t('totalOrders')} value={fmt(summary.total_orders)} icon={ClipboardList} color="blue" />
            <StatCard label={t('onTimeDelivery')} value={fmt(summary.on_time_delivery_rate)} unit="%" icon={CheckCircle2} color="green" />
            <StatCard label={t('fillRate')} value={fmt(summary.fill_rate)} unit="%" icon={BarChart3} color="purple" />
            <StatCard label={t('avgLeadTime')} value={fmt(summary.avg_lead_time_days)} unit="days" icon={Timer} color="cyan" />
            <StatCard label={t('inventoryTurnover')} value={fmt(summary.inventory_turnover)} unit="turns" icon={RefreshCcw} color="blue" />
            <StatCard label={t('carryingCost')} value={fmt(summary.carrying_cost)} icon={DollarSign} color="red" />
            <StatCard label={t('stockoutRate')} value={fmt(summary.stockout_rate)} unit="%" icon={AlertTriangle} color="red" />
            <StatCard label={t('returnRate')} value={fmt(summary.return_rate)} unit="%" icon={CornerDownLeft} color="purple" />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: 20, marginTop: 20 }}>
            {health && (
              <div className="card" style={{ textAlign: 'center' }}>
                <h3 className="card-title">{t('supplyChainHealth')}</h3>
                <div style={{
                  width: 120, height: 120, borderRadius: '50%',
                  border: `6px solid ${health.color}`,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  flexDirection: 'column', margin: '16px auto'
                }}>
                  <div style={{ fontSize: '1.8rem', fontWeight: 700, color: health.color }}>{health.score}</div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>/100</div>
                </div>
                <div style={{ fontWeight: 600, color: health.color }}>{health.rating}</div>
                {health.factors && (
                  <div style={{ marginTop: 16, textAlign: 'left' }}>
                    {Object.entries(health.factors).map(([k, v]) => (
                      <div key={k} style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0', fontSize: '0.85rem' }}>
                        <span style={{ textTransform: 'capitalize' }}>{k.replace(/_/g, ' ')}</span>
                        <span style={{ fontWeight: 600 }}>{v}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
            <div className="card">
              <h3 className="card-title">{t('logisticsTrends')}</h3>
              {summary.trends && summary.trends.length > 0 ? (
                <table className="table">
                  <thead><tr><th>Period</th><th>Orders</th><th>OTD %</th><th>Cost</th></tr></thead>
                  <tbody>
                    {summary.trends.slice(-8).map((t, i) => (
                      <tr key={i}>
                        <td>{t.period}</td>
                        <td>{fmt(t.orders)}</td>
                        <td>{fmt(t.on_time_rate)}%</td>
                        <td>{fmt(t.cost)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : <p style={{ color: 'var(--text-muted)' }}>No trend data available</p>}
            </div>
          </div>
        </>
      )}

      {activeTab === 'inventory' && inventory && (
        <div className="kpi-grid">
          <StatCard label="Total SKUs" value={fmt(inventory.total_sku_count)} icon={Package} color="blue" />
          <StatCard label="Inventory Value" value={fmt(inventory.inventory_value)} icon={DollarSign} color="red" />
          <StatCard label="Days of Supply" value={fmt(inventory.days_of_supply)} unit="days" icon={Timer} color="purple" />
          <StatCard label={t('inventoryTurnover')} value={fmt(inventory.inventory_turnover)} unit="turns" icon={RefreshCcw} color="cyan" />
          <StatCard label="Slow Moving %" value={fmt(inventory.slow_moving_pct)} unit="%" icon={Snail} color="red" />
          <StatCard label="Overstock %" value={fmt(inventory.overstock_pct)} unit="%" icon={TrendingUp} color="purple" />
          <StatCard label={t('stockoutRate')} value={fmt(inventory.stockout_rate)} unit="%" icon={AlertTriangle} color="red" />
          <StatCard label="Accuracy" value={fmt(inventory.accuracy_rate)} unit="%" icon={Crosshair} color="green" />
        </div>
      )}

      {activeTab === 'shipping' && shipping && (
        <div className="kpi-grid">
          <StatCard label="Shipments Today" value={fmt(shipping.shipments_today)} icon={Truck} color="blue" />
          <StatCard label="Monthly Shipments" value={fmt(shipping.shipments_month)} icon={PackageCheck} color="purple" />
          <StatCard label="On-Time Rate" value={fmt(shipping.on_time_rate)} unit="%" icon={CheckCircle2} color="green" />
          <StatCard label="Damage Rate" value={fmt(shipping.damaged_rate)} unit="%" icon={AlertTriangle} color="red" />
          <StatCard label="Avg Transit" value={fmt(shipping.avg_transit_days)} unit="days" icon={Timer} color="cyan" />
          <StatCard label="Cost/Shipment" value={fmt(shipping.cost_per_shipment)} icon={DollarSign} color="red" />
        </div>
      )}
    </div>
  )
}
