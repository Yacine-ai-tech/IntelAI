import { useState, useEffect, useCallback } from 'react'
import { useAuth } from '../context/AuthContext'
import { useTranslation } from '../i18n/I18nContext'
import * as api from '../api'
import { ShieldCheck, Users, FileText, Key, Plus, UserCheck, UserX } from 'lucide-react'
import { PageHeader, Stat, StatGrid, Panel, Loading } from '../components/ui'

export default function AdminPage() {
  const { user, hasPage } = useAuth()
  const { t } = useTranslation()
  const [users, setUsers] = useState([])
  const [auditLogs, setAuditLogs] = useState([])
  const [loading, setLoading] = useState(true)
  const [tab, setTab] = useState('users')
  const [showForm, setShowForm] = useState(false)
  const [newUser, setNewUser] = useState({ username: '', password: '', full_name: '', role: 'viewer' })
  const [formError, setFormError] = useState('')
  const [formLoading, setFormLoading] = useState(false)

  const roles = ['admin', 'ceo', 'cfo', 'cto', 'coo', 'chro', 'hr', 'esg', 'risk', 'analyst', 'board', 'viewer']

  const fetchData = useCallback(async () => {
    setLoading(true)
    const [u, a] = await Promise.allSettled([api.listUsers(), api.getAuditLog()])
    if (u.status === 'fulfilled') setUsers(u.value.data?.users || u.value.data || [])
    if (a.status === 'fulfilled') setAuditLogs(a.value.data?.logs || a.value.data || [])
    setLoading(false)
  }, [])
  useEffect(() => { fetchData() }, [fetchData])

  const createUser = async (e) => {
    e.preventDefault(); setFormError(''); setFormLoading(true)
    try {
      await api.register(newUser.username, newUser.password, newUser.role)
      setShowForm(false); setNewUser({ username: '', password: '', full_name: '', role: 'viewer' }); fetchData()
    } catch (err) { setFormError(err.response?.data?.detail || 'Failed to create user') }
    setFormLoading(false)
  }
  const toggleStatus = async (id, active) => { try { await api.updateUser(id, { is_active: !active }); fetchData() } catch { /* */ } }

  if (!hasPage('admin')) return <div className="text-center" style={{ padding: 60 }}>{t('accessDenied') || 'Access denied'}</div>
  if (loading) return <Loading />

  const active = users.filter(u => u.is_active !== false).length

  return (
    <div>
      <PageHeader icon={ShieldCheck} accent="var(--p-risk)" title={t('navAdmin') || 'Administration'}
        subtitle={t('adminSubtitle') || 'Users, roles & audit trail'} />

      <StatGrid>
        <Stat label={t('users') || 'Users'} value={users.length} icon={Users} accent="var(--p-risk)" />
        <Stat label={t('active') || 'Active'} value={active} icon={UserCheck} accent="var(--ok)" />
        <Stat label={t('disabled') || 'Disabled'} value={users.length - active} icon={UserX} accent="var(--bad)" />
        <Stat label={t('roles') || 'Roles'} value={new Set(users.map(u => u.role)).size} icon={Key} accent="var(--accent)" />
      </StatGrid>

      <div className="tab-bar" style={{ marginTop: 18 }}>
        <button className={tab === 'users' ? 'active' : ''} onClick={() => setTab('users')}><Users size={14} /> {t('users') || 'Users'}</button>
        <button className={tab === 'audit' ? 'active' : ''} onClick={() => setTab('audit')}><FileText size={14} /> {t('auditLog') || 'Audit log'}</button>
        <button className={tab === 'roles' ? 'active' : ''} onClick={() => setTab('roles')}><Key size={14} /> {t('roles') || 'Roles'}</button>
      </div>

      {tab === 'users' && (
        <Panel title={t('userManagement') || 'User management'} icon={Users}
          actions={<button className="btn btn-primary btn-sm" onClick={() => setShowForm(!showForm)}>{showForm ? (t('cancel') || 'Cancel') : <><Plus size={14} /> {t('newUser') || 'New user'}</>}</button>}>
          {showForm && (
            <form onSubmit={createUser} style={{ background: 'var(--bg-2)', padding: 18, borderRadius: 'var(--r)', marginBottom: 18 }}>
              {formError && <div className="alert alert-danger" style={{ marginBottom: 12 }}>{formError}</div>}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(160px,1fr))', gap: 12 }}>
                <div className="form-group"><label className="form-label">{t('username') || 'Username'}</label><input className="form-input" value={newUser.username} onChange={e => setNewUser({ ...newUser, username: e.target.value })} required /></div>
                <div className="form-group"><label className="form-label">{t('fullName') || 'Full name'}</label><input className="form-input" value={newUser.full_name} onChange={e => setNewUser({ ...newUser, full_name: e.target.value })} /></div>
                <div className="form-group"><label className="form-label">{t('password') || 'Password'}</label><input className="form-input" type="password" value={newUser.password} onChange={e => setNewUser({ ...newUser, password: e.target.value })} required /></div>
                <div className="form-group"><label className="form-label">{t('role') || 'Role'}</label><select className="form-input" value={newUser.role} onChange={e => setNewUser({ ...newUser, role: e.target.value })}>{roles.map(r => <option key={r} value={r}>{r.toUpperCase()}</option>)}</select></div>
              </div>
              <button type="submit" className="btn btn-primary" style={{ marginTop: 10 }} disabled={formLoading}>{formLoading ? (t('creating') || 'Creating…') : (t('createUser') || 'Create user')}</button>
            </form>
          )}
          <table className="table">
            <thead><tr><th>{t('username') || 'Username'}</th><th>{t('fullName') || 'Full name'}</th><th>{t('role') || 'Role'}</th><th>{t('status') || 'Status'}</th><th>{t('actions') || 'Actions'}</th></tr></thead>
            <tbody>
              {users.map(u => (
                <tr key={u.id || u.username}>
                  <td style={{ fontWeight: 600 }}>{u.username}</td>
                  <td>{u.full_name || '—'}</td>
                  <td><span className="badge">{u.role?.toUpperCase()}</span></td>
                  <td><span className={`badge ${u.is_active !== false ? 'ok' : 'bad'}`}>{u.is_active !== false ? (t('active') || 'Active') : (t('disabled') || 'Disabled')}</span></td>
                  <td>{u.username !== user?.username && <button className="btn btn-outline btn-sm" onClick={() => toggleStatus(u.id, u.is_active !== false)}>{u.is_active !== false ? (t('disable') || 'Disable') : (t('enable') || 'Enable')}</button>}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Panel>
      )}

      {tab === 'audit' && (
        <Panel title={t('auditLog') || 'Audit log'} icon={FileText}>
          {auditLogs.length === 0 ? <p className="text-muted">{t('noAudit') || 'No audit events.'}</p> : (
            <div style={{ maxHeight: 520, overflowY: 'auto' }}>
              <table className="table">
                <thead><tr><th>{t('timestamp') || 'Time'}</th><th>{t('user') || 'User'}</th><th>{t('action') || 'Action'}</th><th>{t('details') || 'Details'}</th></tr></thead>
                <tbody>
                  {auditLogs.slice(0, 100).map((l, i) => (
                    <tr key={i}>
                      <td style={{ fontSize: '.8rem', whiteSpace: 'nowrap' }}>{new Date(l.timestamp || l.created_at).toLocaleString()}</td>
                      <td>{l.username || l.user || '—'}</td>
                      <td><span className="badge">{l.action || l.event_type}</span></td>
                      <td style={{ fontSize: '.8rem', maxWidth: 320, overflow: 'hidden', textOverflow: 'ellipsis' }}>{l.details || l.description || '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Panel>
      )}

      {tab === 'roles' && (
        <Panel title={t('roleDefinitions') || 'Role definitions'} icon={Key}>
          <table className="table">
            <thead><tr><th>{t('role') || 'Role'}</th><th>{t('description') || 'Description'}</th><th>{t('users') || 'Users'}</th></tr></thead>
            <tbody>
              {roles.map(r => (
                <tr key={r}>
                  <td><span className="badge">{r.toUpperCase()}</span></td>
                  <td style={{ fontSize: '.85rem', color: 'var(--text-2)' }}>{t(`role${r.charAt(0).toUpperCase() + r.slice(1)}`)}</td>
                  <td>{users.filter(u => u.role === r).length}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Panel>
      )}
    </div>
  )
}
