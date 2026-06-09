import { useState, useEffect, useCallback } from 'react'
import * as api from '../api'
import { useTranslation } from '../i18n/I18nContext'
import {
  Leaf, Globe, TreePine, Handshake, Landmark,
  Factory, Zap, Users, Droplets, Recycle, Home, BookOpen, ShieldCheck, Lock
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

export default function ESGPage() {
  const { t } = useTranslation()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('overview')

  const fetchData = useCallback(async () => {
    setLoading(true)
    try {
      const res = await api.getESGSummary()
      setData(res.data)
    } catch (err) {
      console.error('ESG fetch error:', err)
    }
    setLoading(false)
  }, [])

  useEffect(() => { fetchData() }, [fetchData])

  const fmt = (v) => {
    if (v === null || v === undefined) return '—'
    if (typeof v === 'number') {
      if (Math.abs(v) >= 1e6) return `${(v / 1e6).toFixed(1)}M`
      if (Math.abs(v) >= 1e3) return `${(v / 1e3).toFixed(1)}K`
      return v % 1 === 0 ? v.toString() : v.toFixed(1)
    }
    return v
  }

  const tabs = [
    { id: 'overview', label: t('overview'), Icon: Globe },
    { id: 'environment', label: t('environment'), Icon: TreePine },
    { id: 'social', label: t('social'), Icon: Handshake },
    { id: 'governance', label: t('governance'), Icon: Landmark },
  ]

  if (loading) return <div className="text-center" style={{ padding: 60 }}>{t('loading')}</div>

  const env = data?.environment || {}
  const soc = data?.social || {}
  const gov = data?.governance || {}

  return (
    <div>
      <h1 className="page-title" style={{ marginBottom: 20 }}><Leaf size={24} /> {t('esgDashboard')}</h1>

      <div className="tab-bar">
        {tabs.map(tab => (
          <button key={tab.id} className={`tab-btn${activeTab === tab.id ? ' active' : ''}`}
            onClick={() => setActiveTab(tab.id)}>
            <tab.Icon size={15} /> {tab.label}
          </button>
        ))}
      </div>

      {activeTab === 'overview' && data && (
        <>
          <div className="kpi-grid">
            <StatCard label={t('esgScore')} value={fmt(data.esg_score)} unit="/100" icon={Globe} color="green" />
            <StatCard label={t('carbonEmissions')} value={fmt(env.carbon_emissions)} unit="tons" icon={Factory} color="red" />
            <StatCard label={t('renewableEnergy')} value={fmt(env.renewable_energy_pct)} unit="%" icon={Zap} color="cyan" />
            <StatCard label={t('boardDiversity')} value={fmt(gov.board_diversity)} unit="%" icon={Users} color="purple" />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, marginTop: 20 }}>
            {/* ESG Score gauge */}
            <div className="card" style={{ textAlign: 'center' }}>
              <h3 className="card-title">{t('compositeESG')}</h3>
              <div style={{
                width: 140, height: 140, borderRadius: '50%',
                border: `8px solid ${(data.esg_score || 0) >= 75 ? '#22c55e' : (data.esg_score || 0) >= 50 ? '#eab308' : '#ef4444'}`,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                flexDirection: 'column', margin: '20px auto'
              }}>
                <div style={{ fontSize: '2.2rem', fontWeight: 700, color: (data.esg_score || 0) >= 75 ? '#22c55e' : (data.esg_score || 0) >= 50 ? '#eab308' : '#ef4444' }}>
                  {fmt(data.esg_score)}
                </div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>/100</div>
              </div>
              <div style={{ display: 'flex', justifyContent: 'center', gap: 20, marginTop: 16 }}>
                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{t('environment')}</div>
                  <div style={{ fontSize: '1.1rem', fontWeight: 600, color: '#22c55e' }}><TreePine size={18} /></div>
                </div>
                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{t('social')}</div>
                  <div style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--primary)' }}><Handshake size={18} /></div>
                </div>
                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{t('governance')}</div>
                  <div style={{ fontSize: '1.1rem', fontWeight: 600, color: '#8b5cf6' }}><Landmark size={18} /></div>
                </div>
              </div>
            </div>

            {/* Trends */}
            <div className="card">
              <h3 className="card-title">{t('esgTrends')}</h3>
              {data.trends && data.trends.length > 0 ? (
                <table className="table">
                  <thead><tr><th>Period</th><th>ESG Score</th><th>Carbon</th><th>Renewables</th></tr></thead>
                  <tbody>
                    {data.trends.slice(-8).map((t, i) => (
                      <tr key={i}>
                        <td>{t.period}</td>
                        <td>{fmt(t.esg_score)}</td>
                        <td>{fmt(t.carbon)}</td>
                        <td>{fmt(t.renewables)}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : <p style={{ color: 'var(--text-muted)' }}>No trend data available</p>}
            </div>
          </div>
        </>
      )}

      {activeTab === 'environment' && (
        <div className="kpi-grid">
          <StatCard label={t('carbonEmissions')} value={fmt(env.carbon_emissions)} unit="tons" icon={Factory} color="red" />
          <StatCard label={t('renewableEnergy')} value={fmt(env.renewable_energy_pct)} unit="%" icon={Zap} color="green" />
          <StatCard label={t('waterUsage')} value={fmt(env.water_usage)} unit="m³" icon={Droplets} color="blue" />
          <StatCard label={t('wasteDiversion')} value={fmt(env.waste_diversion_rate)} unit="%" icon={Recycle} color="cyan" />
        </div>
      )}

      {activeTab === 'social' && (
        <div className="kpi-grid">
          <StatCard label={t('communityInvestment')} value={`$${fmt(soc.community_investment)}`} icon={Home} color="blue" />
          <StatCard label={t('ethicsTraining')} value={fmt(soc.ethics_training_completion)} unit="%" icon={BookOpen} color="purple" />
          <StatCard label={t('supplierCompliance')} value={fmt(soc.supplier_compliance)} unit="%" icon={Handshake} color="green" />
          <StatCard label={t('dataPrivacy')} value={fmt(soc.data_privacy_score)} unit="/100" icon={Lock} color="cyan" />
        </div>
      )}

      {activeTab === 'governance' && (
        <div className="kpi-grid">
          <StatCard label={t('boardDiversity')} value={fmt(gov.board_diversity)} unit="%" icon={Users} color="purple" />
          <StatCard label={t('ethicsTraining')} value={fmt(gov.ethics_training)} unit="%" icon={ShieldCheck} color="green" />
          <StatCard label={t('esgScore')} value={fmt(data?.esg_score)} unit="/100" icon={Globe} color="blue" />
        </div>
      )}
    </div>
  )
}
