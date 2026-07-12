import { useQuery } from '@tanstack/react-query'
import * as api from '../api'
import { useTranslation } from '../i18n/I18nContext'
import {
  Package, Truck, Clock, RefreshCw, Boxes, DollarSign, Warehouse, RotateCcw, PackageCheck, Ban,
} from 'lucide-react'
import { fmtPct, PageHeader, Stat, StatGrid, BarList, fmtNum, Loading, Grid, AskCopilot, AreaTrend, DomainHero, Panel, fmtMoney } from '../components/ui'

const ACCENT = 'var(--p-coo)'

export default function LogisticsPage() {
  const { t } = useTranslation()
  const sum = useQuery({ queryKey: ['log-sum'], queryFn: () => api.getLogisticsSummary().then(r => r.data), retry: 1 })
  const inv = useQuery({ queryKey: ['log-inv'], queryFn: () => api.getLogisticsInventory().then(r => r.data), retry: 1 })
  const ship = useQuery({ queryKey: ['log-ship'], queryFn: () => api.getLogisticsShipping().then(r => r.data), retry: 1 })
  const hlt = useQuery({ queryKey: ['log-health'], queryFn: () => api.getLogisticsHealth().then(r => r.data), retry: 1 })

  if (sum.isLoading) return <Loading />
  const s = sum.data || {}, iv = inv.data || {}, sh = ship.data || {}

  return (
    <div>
      <PageHeader icon={Package} accent={ACCENT} title={t('navLogistics') || 'Logistics'}
        subtitle={t('logSubtitle') || 'Fulfilment, inventory & transportation'}
        actions={<AskCopilot q={t('askCopilot_LogisticsPage_HowIsOur')} />} />

      <DomainHero health={hlt.data} accent={ACCENT} />

      <StatGrid>
        <Stat label={t('lblTotalOrders')} value={fmtNum(s.total_orders)} icon={Package} accent={ACCENT} />
        <Stat label={t('lblOnTimeDelivery')} value={fmtPct(s.on_time_delivery_rate)} icon={Truck} accent={ACCENT} good="up" hint="World-class 95–98%" />
        <Stat label={t('lblFillRate')} value={fmtPct(s.fill_rate)} icon={PackageCheck} accent={ACCENT} good="up" />
        <Stat label={t('lblAvgLeadTime')} value={fmtNum(s.avg_lead_time_days)} unit="d" icon={Clock} accent={ACCENT} good="down" />
        <Stat label={t('lblInventoryTurnover')} value={fmtNum(s.inventory_turnover)} unit="×" icon={RefreshCw} accent={ACCENT} good="up" />
        <Stat label={t('lblStockoutRate')} value={fmtPct(s.stockout_rate)} icon={Ban} accent="var(--bad)" good="down" />
        <Stat label={t('lblReturnRate')} value={fmtPct(s.return_rate)} icon={RotateCcw} accent={ACCENT} good="down" />
        <Stat label={t('lblShipCostUnit')} value={fmtMoney(s.shipping_cost_per_unit)} icon={DollarSign} accent={ACCENT} good="down" />
      </StatGrid>

      <Grid style={{ marginTop: 18 }}>
        <Panel title={t('lblOrderVolumeTrend')} icon={Package} style={{ gridColumn: 'span 2' }}>
          <AreaTrend data={s.trends || []} y="orders" color={ACCENT} />
        </Panel>
        <Panel title={t('lblInventoryHealth')} icon={Boxes}>
          <BarList items={[
            { label: 'Accuracy rate', value: iv.accuracy_rate, display: fmtPct(iv.accuracy_rate), color: 'var(--ok)' },
            { label: 'Days of supply', value: iv.days_of_supply, display: fmtNum(iv.days_of_supply) + 'd' },
            { label: 'Slow-moving %', value: iv.slow_moving_pct, display: fmtPct(iv.slow_moving_pct), color: 'var(--warn)' },
            { label: 'Overstock %', value: iv.overstock_pct, display: fmtPct(iv.overstock_pct), color: 'var(--warn)' },
          ]} />
          <div style={{ marginTop: 14, fontSize: '.82rem', color: 'var(--text-2)' }}>
            SKUs: <b style={{ color: 'var(--text)' }}>{fmtNum(iv.total_sku_count)}</b> · Value: <b style={{ color: 'var(--text)' }}>{fmtMoney(iv.inventory_value)}</b>
          </div>
        </Panel>
      </Grid>

      <Panel title={t('lblShipping')} icon={Truck} style={{ marginTop: 18 }}>
        <StatGrid>
          <Stat label={t('lblShipmentsMo')} value={fmtNum(sh.shipments_month)} icon={Truck} accent={ACCENT} />
          <Stat label={t('lblOnTimeRate')} value={fmtPct(sh.on_time_rate)} icon={PackageCheck} accent={ACCENT} good="up" />
          <Stat label={t('lblDamagedRate')} value={fmtPct(sh.damaged_rate)} icon={Ban} accent="var(--bad)" good="down" />
          <Stat label={t('lblAvgTransit')} value={fmtNum(sh.avg_transit_days)} unit="d" icon={Clock} accent={ACCENT} good="down" />
          <Stat label={t('lblCostShipment')} value={fmtMoney(sh.cost_per_shipment)} icon={DollarSign} accent={ACCENT} good="down" />
          <Stat label={t('lblWarehouseUtil')} value={fmtPct(s.warehouse_utilization)} icon={Warehouse} accent={ACCENT} good="up" />
        </StatGrid>
      </Panel>
    </div>
  )
}
