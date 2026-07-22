import { useState, useEffect, useCallback } from 'react'
import { useAuth } from '../context/AuthContext'
import { useTranslation } from '../i18n/I18nContext'
import * as api from '../api'
import {
  ShieldCheck, Users, FileText, Key, Plus, UserCheck, UserX,
  FlaskConical, Zap, Trash2, RefreshCw, Activity, Server,
} from 'lucide-react'
import { PageHeader, Stat, StatGrid, Loading, Panel } from '../components/ui'
import { reindexVectors, cleanupData } from '../api'

const SCENARIOS = [
  { id: 'healthy',               label: 'Healthy',                desc: 'S&P 500 baseline — all green metrics.' },
  { id: 'declining_financial',   label: 'Declining Financial',    desc: 'Revenue contraction & margin compression.' },
  { id: 'high_churn_crisis',     label: 'High Churn Crisis',      desc: 'Severe customer retention failure.' },
  { id: 'operational_meltdown',  label: 'Operational Meltdown',   desc: 'OEE collapse & quality failures.' },
  { id: 'talent_crisis',         label: 'Talent Crisis',          desc: 'High attrition, open reqs spike.' },
  { id: 'cybersecurity_breach',  label: 'Cybersecurity Breach',   desc: 'Security incident — SLA & SLO degrade.' },
  { id: 'esg_compliance_failure',label: 'ESG Compliance Failure', desc: 'Governance failures & emissions spike.' },
]

const ROLES = ['admin', 'ceo', 'cfo', 'cto', 'coo', 'chro', 'hr', 'esg', 'risk', 'analyst', 'board', 'viewer']

export default function AdminPage() {
  const { user, hasPage } = useAuth()
  const { t } = useTranslation()

  const [users, setUsers]       = useState([])
  const [auditLogs, setAuditLogs] = useState([])
  const [rolesData, setRolesData] = useState({})
  const [loading, setLoading]   = useState(true)
  const [tab, setTab]           = useState('users')

  // User creation form
  const [showForm, setShowForm]   = useState(false)
  const [newUser, setNewUser]     = useState({ username: '', password = 'REDACTED', full_name: '', role: 'viewer' })
  const [formError, setFormError] = useState('')
  const [formLoading, setFormLoading] = useState(false)

  // Scenario switcher
  const [activeScenario, setActiveScenario] = useState(null)
  const [scenarioLoading, setScenarioLoading] = useState(false)
  const [scenarioMsg, setScenarioMsg]   = useState('')

  // Infra controls
  const [reindexing, setReindexing] = useState(false)
  const [cleaning,   setCleaning]   = useState(false)
  const [infraMsg,   setInfraMsg]   = useState('')

  const fetchData = useCallback(async () => {
    setLoading(true)
    const [u, a, r] = await Promise.allSettled([
      api.listUsers(),
      api.getAuditLog(150),
      api.listRoles(),
    ])
    if (u.status === 'fulfilled') setUsers(u.value.data?.users || u.value.data || [])
    if (a.status === 'fulfilled') setAuditLogs(a.value.data?.logs || a.value.data || [])
    if (r.status === 'fulfilled') setRolesData(r.value.data?.roles || {})
    setLoading(false)
  }, [])

  const fetchScenario = useCallback(async () => {
    try {
      const r = await api.getCurrentScenario()
      setActiveScenario(r.data?.current_scenario || 'healthy')
    } catch { /* ok */ }
  }, [])

  useEffect(() => { fetchData(); fetchScenario() }, [fetchData, fetchScenario])

  const createUser = async (e) => {
    e.preventDefault(); setFormError(''); setFormLoading(true)
    try {
      await api.register(newUser.username, newUser.password, newUser.role)
      setShowForm(false)
      setNewUser({ username: '', password = 'REDACTED', full_name: '', role: 'viewer' })
      fetchData()
    } catch (err) { setFormError(err.response?.data?.detail || 'Failed to create user') }
    setFormLoading(false)
  }

  const toggleStatus = async (id, active) => {
    try { await api.updateUser(id, { is_active: !active }); fetchData() } catch { /* */ }
  }

  const changeRole = async (id, role) => {
    try { await api.updateUser(id, { role }); fetchData() } catch { /* */ }
  }

  const switchScenario = async (id) => {
    if (scenarioLoading) return
    setScenarioLoading(true); setScenarioMsg('')
    try {
      await api.switchScenario(id)
      setActiveScenario(id)
      setScenarioMsg(`✓ Switched to "${SCENARIOS.find(s => s.id === id)?.label}" — data refreshed.`)
    } catch (err) {
      setScenarioMsg(`✗ ${err.response?.data?.detail || 'Scenario switch failed'}`)
    }
    setScenarioLoading(false)
  }

  const reindex = async () => {
    setReindexing(true); setInfraMsg('')
    try {
      await reindexVectors(true)
      setInfraMsg('✓ Vector store reindexed.')
    } catch { setInfraMsg('✗ Reindex failed (check server logs).') }
    setReindexing(false)
  }

  const cleanup = async () => {
    if (!window.confirm('Clear chat history & audit trail? This cannot be undone.')) return
    setCleaning(true); setInfraMsg('')
    try {
      await cleanupData()
      setInfraMsg('✓ Chat history and audit trail cleared.')
      fetchData()
    } catch { setInfraMsg('✗ Cleanup failed.') }
    setCleaning(false)
  }

  if (!hasPage('admin')) return <div className="text-center" style={{ padding: 60 }}>{t('accessDenied') || 'Access denied'}</div>
  if (loading) return <Loading />

  const active = users.filter(u => u.is_active !== false).length

  return (
    <div>
      <PageHeader icon={ShieldCheck} accent="var(--p-risk)" title={t('navAdmin') || 'Administration'}
        subtitle={t('adminSubtitle') || 'Users, roles, audit trail, scenarios & infrastructure'} />

      <StatGrid>
        <Stat label={t('users') || 'Users'}    value={users.length}        icon={Users}     accent="var(--p-risk)" />
        <Stat label={t('active') || 'Active'}  value={active}              icon={UserCheck} accent="var(--ok)" />
        <Stat label={t('disabled') || 'Disabled'} value={users.length - active} icon={UserX} accent="var(--bad)" />
        <Stat label={t('roles') || 'Roles'}    value={new Set(users.map(u => u.role)).size} icon={Key} accent="var(--accent)" />
      </StatGrid>

      <div className="tab-bar" style={{ marginTop: 18 }}>
        <button className={tab === 'users'     ? 'active' : ''} onClick={() => setTab('users')}    ><Users     size={14} /> {t('users')   || 'Users'}</button>
        <button className={tab === 'audit'     ? 'active' : ''} onClick={() => setTab('audit')}    ><FileText  size={14} /> {t('auditLog') || 'Audit log'}</button>
        <button className={tab === 'roles'     ? 'active' : ''} onClick={() => setTab('roles')}    ><Key       size={14} /> {t('roles')   || 'Roles'}</button>
        <button className={tab === 'scenarios' ? 'active' : ''} onClick={() => setTab('scenarios')}><FlaskConical size={14} /> Scenarios</button>
        <button className={tab === 'infra'     ? 'active' : ''} onClick={() => setTab('infra')}    ><Server   size={14} /> Infrastructure</button>
      </div>

      {/* ── Users ── */}
      {tab === 'users' && (
        <Panel title={t('userManagement') || 'User management'} icon={Users}
          actions={<button className="btn btn-primary btn-sm" onClick={() => setShowForm(!showForm)}>
            {showForm ? (t('cancel') || 'Cancel') : <><Plus size={14} /> {t('newUser') || 'New user'}</>}
          </button>}>

          {showForm && (
            <form onSubmit={createUser} style={{ background: 'var(--bg-2)', padding: 18, borderRadius: 'var(--r)', marginBottom: 18 }}>
              {formError && <div className="alert alert-danger" style={{ marginBottom: 12 }}>{formError}</div>}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(160px,1fr))', gap: 12 }}>
                <div className="form-group"><label className="form-label">{t('username') || 'Username'}</label>
                  <input className="form-input" value={newUser.username} onChange={e => setNewUser({ ...newUser, username: e.target.value })} required /></div>
                <div className="form-group"><label className="form-label">{t('fullName') || 'Full name'}</label>
                  <input className="form-input" value={newUser.full_name} onChange={e => setNewUser({ ...newUser, full_name: e.target.value })} /></div>
                <div className="form-group"><label className="form-label">{t('password') || 'Password'}</label>
                  <input className="form-input" type="password" value={newUser.password} onChange={e => setNewUser({ ...newUser, password: e.target.value })} required /></div>
                <div className="form-group"><label className="form-label">{t('role') || 'Role'}</label>
                  <select className="form-input" value={newUser.role} onChange={e => setNewUser({ ...newUser, role: e.target.value })}>
                    {ROLES.map(r => <option key={r} value={r}>{r.toUpperCase()}</option>)}
                  </select></div>
              </div>
              <button type="submit" className="btn btn-primary" style={{ marginTop: 10 }} disabled={formLoading}>
                {formLoading ? (t('creating') || 'Creating…') : (t('createUser') || 'Create user')}
              </button>
            </form>
          )}

          <table className="table">
            <thead><tr>
              <th>{t('username') || 'Username'}</th>
              <th>{t('role') || 'Role'}</th>
              <th>{t('status') || 'Status'}</th>
              <th>{t('actions') || 'Actions'}</th>
            </tr></thead>
            <tbody>
              {users.map(u => (
                <tr key={u.id || u.username}>
                  <td style={{ fontWeight: 600 }}>{u.username}</td>
                  <td>
                    {u.username === user?.username
                      ? <span className="badge">{u.role?.toUpperCase()}</span>
                      : <select className="form-input" style={{ width: 120, padding: '4px 8px', fontSize: '.78rem' }}
                          value={u.role} onChange={e => changeRole(u.id, e.target.value)}>
                          {ROLES.map(r => <option key={r} value={r}>{r.toUpperCase()}</option>)}
                        </select>
                    }
                  </td>
                  <td><span className={`badge ${u.is_active !== false ? 'ok' : 'bad'}`}>
                    {u.is_active !== false ? (t('active') || 'Active') : (t('disabled') || 'Disabled')}
                  </span></td>
                  <td>{u.username !== user?.username &&
                    <button className="btn btn-outline btn-sm" onClick={() => toggleStatus(u.id, u.is_active !== false)}>
                      {u.is_active !== false ? (t('disable') || 'Disable') : (t('enable') || 'Enable')}
                    </button>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Panel>
      )}

      {/* ── Audit ── */}
      {tab === 'audit' && (
        <Panel title={t('auditLog') || 'Audit log'} icon={FileText}>
          {auditLogs.length === 0 ? <p className="text-muted">{t('noAudit') || 'No audit events.'}</p> : (
            <div style={{ maxHeight: 560, overflowY: 'auto' }}>
              <table className="table">
                <thead><tr>
                  <th>{t('timestamp') || 'Time'}</th>
                  <th>{t('user') || 'User'}</th>
                  <th>{t('action') || 'Action'}</th>
                  <th>{t('details') || 'Details'}</th>
                </tr></thead>
                <tbody>
                  {auditLogs.slice(0, 150).map((l, i) => (
                    <tr key={i}>
                      <td style={{ fontSize: '.8rem', whiteSpace: 'nowrap' }}>
                        {new Date(l.timestamp || l.created_at).toLocaleString()}</td>
                      <td>{l.username || l.user || '—'}</td>
                      <td><span className="badge">{l.action || l.event_type}</span></td>
                      <td style={{ fontSize: '.8rem', maxWidth: 340, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {l.details || l.description || '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Panel>
      )}

      {/* ── Roles ── */}
      {tab === 'roles' && (
        <Panel title={t('roleDefinitions') || 'Role definitions'} icon={Key}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(260px,1fr))', gap: 14 }}>
            {ROLES.map(r => {
              const def = rolesData[r] || {}
              const actions = def.actions || []
              const pages   = def.pages   || []
              const count   = users.filter(u => u.role === r).length
              return (
                <div key={r} style={{ background: 'var(--surface-2)', border: '1px solid var(--border)', borderRadius: 'var(--r-lg)', padding: 16 }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 10 }}>
                    <strong style={{ fontSize: '.9rem', textTransform: 'uppercase', letterSpacing: '.04em' }}>{r}</strong>
                    <span className="badge">{count} user{count !== 1 ? 's' : ''}</span>
                  </div>
                  {actions.length > 0 && (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 5 }}>
                      {actions.slice(0, 10).map(a => (
                        <span key={a} style={{ fontSize: '.7rem', padding: '2px 8px', borderRadius: 999, border: '1px solid var(--border)', color: 'var(--text-2)' }}>{a}</span>
                      ))}
                    </div>
                  )}
                  <div style={{ marginTop: 8, fontSize: '.75rem', color: 'var(--text-3)' }}>
                    {pages.length > 0 ? `${pages.length} accessible pages` : 'No page restrictions'}
                  </div>
                </div>
              )
            })}
          </div>
        </Panel>
      )}

      {/* ── Scenarios ── */}
      {tab === 'scenarios' && (
        <Panel title={t('benchmarkingScenarios') || 'Benchmarking Scenarios'} icon={FlaskConical}
          actions={<span style={{ fontSize: '.78rem', color: 'var(--text-3)' }}>
            {t('activeColon') || 'Active:'} <b style={{ color: 'var(--primary)' }}>{SCENARIOS.find(s => s.id === activeScenario)?.label || activeScenario}</b>
          </span>}>
          <p style={{ fontSize: '.86rem', color: 'var(--text-2)', marginBottom: 18 }}>
            {t('scenarioDesc') || 'Switch the live database to any of the 7 industry-benchmarked scenarios. Each seeds 36 months of KPI data. Affects all live endpoints — copilot answers, dashboards, forecasts.'}
          </p>
          {scenarioMsg && (
            <div className={`alert ${scenarioMsg.startsWith('✓') ? 'alert-success' : 'alert-danger'}`} style={{ marginBottom: 16 }}>
              {scenarioMsg}
            </div>
          )}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(280px,1fr))', gap: 12 }}>
            {SCENARIOS.map(s => {
              const isActive = activeScenario === s.id
              return (
                <div key={s.id} style={{
                  padding: 18, borderRadius: 'var(--r-lg)',
                  background: isActive ? 'var(--primary-soft)' : 'var(--surface-2)',
                  border: `1px solid ${isActive ? 'var(--primary-line)' : 'var(--border)'}`,
                  transition: 'all var(--t)',
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
                    <strong style={{ fontSize: '.9rem', color: isActive ? 'var(--primary)' : 'var(--text)' }}>
                      {isActive && '● '}{s.label}
                    </strong>
                    {isActive && <span className="badge ok">{t('active') || 'Active'}</span>}
                  </div>
                  <p style={{ fontSize: '.8rem', color: 'var(--text-2)', marginBottom: 14 }}>{s.desc}</p>
                  <button
                    className={`btn btn-sm ${isActive ? 'btn-outline' : 'btn-primary'}`}
                    disabled={scenarioLoading || isActive}
                    onClick={() => switchScenario(s.id)}>
                    {scenarioLoading && !isActive ? <><RefreshCw size={13} className="spin-inline" /> {t('loading') || 'Loading…'}</> : isActive ? (<span>✓ {t('current') || 'Current'}</span>) : (t('activate') || 'Activate')}
                  </button>
                </div>
              )
            })}
          </div>
        </Panel>
      )}

      {/* ── Infrastructure ── */}
      {tab === 'infra' && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(320px,1fr))', gap: 18 }}>
          {infraMsg && (
            <div className={`alert ${infraMsg.startsWith('✓') ? 'alert-success' : 'alert-danger'}`}
              style={{ gridColumn: '1 / -1' }}>{infraMsg}</div>
          )}
          <Panel title={t('vectorStore') || 'Vector Store'} icon={Activity}>
            <p style={{ fontSize: '.86rem', color: 'var(--text-2)', marginBottom: 14 }}>
              Rebuild the persistent vector/BM25 knowledge index from the current knowledge base.
              Run after a large document ingest or if knowledge search returns empty results.
            </p>
            <button className="btn btn-primary" disabled={reindexing} onClick={reindex}>
              {reindexing
                ? <><RefreshCw size={15} className="spin-inline" /> {t('reindexing') || 'Reindexing…'}</>
                : <><Zap size={15} /> {t('reindexDocs') || 'Reindex Knowledge Store'}</>}
            </button>
          </Panel>

          <Panel title={t('dataCleanup') || 'Data Cleanup'} icon={Trash2}>
            <p style={{ fontSize: '.86rem', color: 'var(--text-2)', marginBottom: 14 }}>
              {t('clearChatDesc') || 'Clear chat history and audit trail.'} <strong style={{ color: 'var(--warn)' }}>{t('irreversible') || 'Irreversible.'}</strong>&nbsp;
              {t('noAffectData') || 'KPI data, users, and knowledge docs are not affected.'}
            </p>
            <button className="btn btn-danger" disabled={cleaning} onClick={cleanup}>
              {cleaning
                ? <><RefreshCw size={15} className="spin-inline" /> {t('clearing') || 'Clearing…'}</>
                : <><Trash2 size={15} /> {t('clearHistoryTrail') || 'Clear History & Audit Trail'}</>}
            </button>
          </Panel>

          <Panel title={t('seedDemoData') || 'Seed Demo Data'} icon={FlaskConical}>
            <p style={{ fontSize: '.86rem', color: 'var(--text-2)', marginBottom: 14 }}>
              {t('reseedDesc') || 'Re-seed the KPI catalog with the healthy (S&P 500 baseline) scenario without clearing existing data. Use the Scenarios tab to switch to a different health state.'}
            </p>
            <button className="btn btn-outline" onClick={async () => {
              setInfraMsg('')
              try { await api.seedData(); setInfraMsg('✓ Demo data seeded.') }
              catch { setInfraMsg('✗ Seed failed.') }
            }}>
              <FlaskConical size={15} /> {t('seedDemoKpis') || 'Seed Demo KPIs'}
            </button>
          </Panel>
        </div>
      )}
    </div>
  )
}
