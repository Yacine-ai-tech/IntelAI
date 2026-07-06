// Governance — RBAC visualization, user directory, and audit trail. All real:
// /admin/roles, /admin/users, /admin/audit. Admin-scoped (guarded by the route).
import { useQuery } from '@tanstack/react-query'
import { ShieldCheck, Users, ScrollText, KeyRound, Lock } from 'lucide-react'
import * as api from '../api'
import { PageHeader, Panel, Loading, Empty } from '../components/ui'

export default function GovernancePage() {
  const { data: rolesData, isLoading: rLoading } = useQuery({
    queryKey: ['roles'], queryFn: () => api.listRoles().then(r => r.data?.roles || {}),
  })
  const { data: users = [], isLoading: uLoading } = useQuery({
    queryKey: ['users'], queryFn: () => api.listUsers().then(r => r.data?.users || []),
  })
  const { data: audit = [], isLoading: aLoading } = useQuery({
    queryKey: ['audit'], queryFn: () => api.getAuditLog(100).then(r => r.data?.logs || []),
  })

  const roles = rolesData || {}

  return (
    <div>
      <PageHeader icon={ShieldCheck} title="Governance"
        subtitle="Role-based access, the user directory and the audit trail — enforced by the backend, visualized here."
        accent="var(--p-risk)" />

      {/* RBAC */}
      <Panel title="Roles & permissions" icon={KeyRound}>
        {rLoading ? <Loading /> : Object.keys(roles).length === 0 ? <Empty text="No roles defined." /> : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(240px,1fr))', gap: 12 }}>
            {Object.entries(roles).map(([role, def]) => {
              const actions = def?.actions || def?.permissions || []
              const pages = def?.pages || []
              return (
                <div key={role} style={{ background: 'var(--surface-2)', border: '1px solid var(--border)', borderRadius: 'var(--r-lg)', padding: 14 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <Lock size={14} style={{ color: 'var(--primary)' }} />
                    <strong style={{ fontSize: 13.5, textTransform: 'capitalize' }}>{role}</strong>
                  </div>
                  {Array.isArray(actions) && actions.length > 0 && (
                    <div style={{ marginTop: 8 }}>
                      <div style={{ fontSize: 10.5, textTransform: 'uppercase', letterSpacing: '.04em', color: 'var(--text-3)' }}>Actions</div>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 5, marginTop: 4 }}>
                        {actions.slice(0, 8).map(a => (
                          <span key={a} style={{ fontSize: 11, padding: '2px 7px', borderRadius: 999, border: '1px solid var(--border)', color: 'var(--text-2)' }}>{a}</span>
                        ))}
                      </div>
                    </div>
                  )}
                  {Array.isArray(pages) && pages.length > 0 && (
                    <div style={{ marginTop: 8, fontSize: 11, color: 'var(--text-3)' }}>{pages.length} accessible pages</div>
                  )}
                </div>
              )
            })}
          </div>
        )}
      </Panel>

      {/* Users */}
      <Panel title="User directory" icon={Users}>
        {uLoading ? <Loading /> : users.length === 0 ? <Empty text="No users." /> : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
              <thead>
                <tr style={{ textAlign: 'left', color: 'var(--text-3)', fontSize: 11, textTransform: 'uppercase', letterSpacing: '.04em' }}>
                  <th style={{ padding: '8px 10px' }}>User</th><th style={{ padding: '8px 10px' }}>Role</th><th style={{ padding: '8px 10px' }}>Status</th>
                </tr>
              </thead>
              <tbody>
                {users.map(u => (
                  <tr key={u.id || u.username} style={{ borderTop: '1px solid var(--border)' }}>
                    <td style={{ padding: '9px 10px', color: 'var(--text)' }}>{u.username}</td>
                    <td style={{ padding: '9px 10px' }}>
                      <span style={{ fontSize: 11.5, padding: '2px 8px', borderRadius: 999, background: 'var(--surface-3)', color: 'var(--primary)', textTransform: 'capitalize' }}>{u.role}</span>
                    </td>
                    <td style={{ padding: '9px 10px', color: u.active === false ? 'var(--text-3)' : 'var(--ok)' }}>{u.active === false ? 'disabled' : 'active'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Panel>

      {/* Audit */}
      <Panel title="Audit trail" icon={ScrollText}>
        {aLoading ? <Loading /> : audit.length === 0 ? <Empty text="No audit events recorded." /> : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
            {audit.slice(0, 40).map((e, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '9px 4px', borderTop: i ? '1px solid var(--border)' : 'none' }}>
                <span style={{ width: 8, height: 8, borderRadius: 999, background: 'var(--primary)', flexShrink: 0 }} />
                <span style={{ fontSize: 12.5, fontWeight: 600, color: 'var(--text)', minWidth: 140 }}>{e.event_type || e.event || 'event'}</span>
                <span style={{ fontSize: 12.5, color: 'var(--text-2)', flex: 1, minWidth: 0, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {e.detail || e.description || ''}
                </span>
                <span style={{ fontSize: 11.5, color: 'var(--text-3)' }}>{e.actor || e.user || ''}</span>
                <span style={{ fontSize: 11, color: 'var(--text-3)' }}>{e.timestamp ? new Date(e.timestamp).toLocaleString() : ''}</span>
              </div>
            ))}
          </div>
        )}
      </Panel>
    </div>
  )
}
