// Organization — departments, the KPI domains each owns, and the executive persona that
// governs each lens. Built from real /personas + /kpis/categories.
import { useQuery } from '@tanstack/react-query'
import { Network, Crown, DollarSign, Cpu, Settings2, Users, Leaf, ShieldAlert, BarChart3, Bot } from 'lucide-react'
import * as api from '../api'
import { PageHeader, Loading, Panel } from '../components/ui'

const PERSONA_ICON = {
  general: Bot, ceo: Crown, cfo: DollarSign, cto: Cpu, coo: Settings2,
  chro: Users, esg: Leaf, risk: ShieldAlert, analyst: BarChart3,
}
const PERSONA_COLOR = {
  general: 'var(--p-general)', ceo: 'var(--p-ceo)', cfo: 'var(--p-cfo)', cto: 'var(--p-cto)',
  coo: 'var(--p-coo)', chro: 'var(--p-chro)', esg: 'var(--p-esg)', risk: 'var(--p-risk)', analyst: 'var(--p-analyst)',
}

export default function OrganizationPage() {
  const { data: personas = [], isLoading } = useQuery({
    queryKey: ['personas'], queryFn: () => api.listPersonas().then(r => r.data?.personas || r.data || []),
  })
  const { data: categories = [] } = useQuery({
    queryKey: ['categories'], queryFn: () => api.getCategories().then(r => r.data?.categories || r.data || []),
  })

  return (
    <div>
      <PageHeader icon={Network} title="Organization"
        subtitle="Departments, the data domains each owns, and the executive persona that governs each lens."
        accent="var(--accent)" />

      {isLoading ? <Loading label="Loading organization…" /> : (
        <Panel title="Executive lenses & data domains" icon={Network}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(280px,1fr))', gap: 12 }}>
            {personas.map(p => {
              const key = p.id || p.persona_id || p.name
              const Icon = PERSONA_ICON[key] || Bot
              const color = PERSONA_COLOR[key] || 'var(--primary)'
              const domains = p.data_access || p.domains || []
              return (
                <div key={key} style={{ background: 'var(--surface-2)', border: '1px solid var(--border)', borderLeft: `2px solid ${color}`, borderRadius: 'var(--r-lg)', padding: 15 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <span style={{ display: 'grid', placeItems: 'center', width: 32, height: 32, borderRadius: 9, background: 'var(--surface-3)', color }}>
                      <Icon size={16} />
                    </span>
                    <div>
                      <div style={{ fontSize: 14, fontWeight: 700, color: 'var(--text)' }}>{p.display_name || key}</div>
                      <div style={{ fontSize: 11, color: 'var(--text-3)', textTransform: 'uppercase', letterSpacing: '.05em' }}>{key}</div>
                    </div>
                  </div>
                  {p.description && <p style={{ marginTop: 10, fontSize: 12.5, lineHeight: 1.6, color: 'var(--text-2)' }}>{p.description}</p>}
                  {domains.length > 0 && (
                    <div style={{ marginTop: 10 }}>
                      <div style={{ fontSize: 10.5, textTransform: 'uppercase', letterSpacing: '.04em', color: 'var(--text-3)', marginBottom: 5 }}>Data domains</div>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 5 }}>
                        {domains.map(d => (
                          <span key={d} style={{ fontSize: 11, padding: '2px 8px', borderRadius: 999, background: 'var(--surface-3)', color: 'var(--text-2)' }}>{d}</span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </Panel>
      )}

      {categories.length > 0 && (
        <Panel title="KPI domains" icon={BarChart3}>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
            {categories.map(c => (
              <span key={c} style={{ fontSize: 12.5, padding: '5px 12px', borderRadius: 999, border: '1px solid var(--border)', background: 'var(--surface-2)', color: 'var(--text-2)' }}>{c}</span>
            ))}
          </div>
          <p style={{ marginTop: 10, fontSize: 12.5, color: 'var(--text-3)' }}>
            Every persona above is scoped to a subset of these domains — the boundary is enforced by the backend, not just the prompt.
          </p>
        </Panel>
      )}
    </div>
  )
}
