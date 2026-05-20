import { useState, useEffect, useCallback } from 'react'
import { useAuth } from '../context/AuthContext'
import { useTranslation } from '../i18n/I18nContext'
import * as api from '../api'
import { ShieldCheck, Users, FileText, Key, Plus } from 'lucide-react'

export default function AdminPage() {
  const { user, hasPage } = useAuth()
  const { t } = useTranslation()
  const [users, setUsers] = useState([])
  const [auditLogs, setAuditLogs] = useState([])
  const [loading, setLoading] = useState(true)
  const [tab, setTab] = useState('users')

  // New user form
  const [showForm, setShowForm] = useState(false)
  const [newUser, setNewUser] = useState({ username: '', password: '', full_name: '', role: 'viewer' })
  const [formError, setFormError] = useState('')
  const [formLoading, setFormLoading] = useState(false)

  const roles = ['admin', 'ceo', 'cfo', 'cto', 'coo', 'chro', 'hr', 'esg', 'risk', 'analyst', 'board', 'viewer']

  const fetchData = useCallback(async () => {
    setLoading(true)
    try {
      const [usersRes, auditRes] = await Promise.allSettled([
        api.listUsers(),
        api.getAuditLog(),
      ])
      if (usersRes.status === 'fulfilled') setUsers(usersRes.value.data?.users || usersRes.value.data || [])
      if (auditRes.status === 'fulfilled') setAuditLogs(auditRes.value.data?.logs || auditRes.value.data || [])
    } catch {
      // handled
    }
    setLoading(false)
  }, [])

  useEffect(() => { fetchData() }, [fetchData])

  const createUser = async (e) => {
    e.preventDefault()
    setFormError('')
    setFormLoading(true)
    try {
      await api.register(newUser.username, newUser.password, newUser.role)
      setShowForm(false)
      setNewUser({ username: '', password: '', full_name: '', role: 'viewer' })
      fetchData()
    } catch (err) {
      setFormError(err.response?.data?.detail || 'Failed to create user')
    }
    setFormLoading(false)
  }

  const toggleUserStatus = async (userId, currentActive) => {
    try {
      await api.updateUser(userId, { is_active: !currentActive })
      fetchData()
    } catch {
      // silent
    }
  }

  if (!hasPage('admin')) {
    return <div className="text-center" style={{ padding: 60 }}>{t('accessDenied')}</div>
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <h1 style={{ margin: 0 }} className="page-title"><ShieldCheck size={24} /> {t('administration')}</h1>
        <div className="tab-bar" style={{ marginBottom: 0 }}>
          <button className={`tab-btn${tab === 'users' ? ' active' : ''}`} onClick={() => setTab('users')}>
            <Users size={14} /> {t('users')}
          </button>
          <button className={`tab-btn${tab === 'audit' ? ' active' : ''}`} onClick={() => setTab('audit')}>
            <FileText size={14} /> {t('auditLog')}
          </button>
          <button className={`tab-btn${tab === 'roles' ? ' active' : ''}`} onClick={() => setTab('roles')}>
            <Key size={14} /> {t('roles')}
          </button>
        </div>
      </div>

      {loading ? (
        <div className="text-center" style={{ padding: 60 }}>{t('loading')}</div>
      ) : (
        <>
          {/* Users Tab */}
          {tab === 'users' && (
            <div className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                <h3 className="card-title" style={{ margin: 0 }}>{t('userManagement')}</h3>
                <button className="btn btn-primary btn-sm" onClick={() => setShowForm(!showForm)}>
                  {showForm ? t('cancel') : <><Plus size={14} /> {t('newUser')}</>}
                </button>
              </div>

              {showForm && (
                <form onSubmit={createUser} style={{
                  background: 'var(--bg-primary)',
                  padding: 20,
                  borderRadius: 12,
                  marginBottom: 20,
                }}>
                  {formError && (
                    <div style={{ color: '#ef4444', marginBottom: 12, fontSize: '0.85rem' }}>{formError}</div>
                  )}
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12 }}>
                    <div className="form-group">
                      <label className="form-label">{t('username')}</label>
                      <input
                        className="form-input"
                        value={newUser.username}
                        onChange={e => setNewUser({ ...newUser, username: e.target.value })}
                        required
                      />
                    </div>
                    <div className="form-group">
                      <label className="form-label">{t('fullName')}</label>
                      <input
                        className="form-input"
                        value={newUser.full_name}
                        onChange={e => setNewUser({ ...newUser, full_name: e.target.value })}
                        required
                      />
                    </div>
                    <div className="form-group">
                      <label className="form-label">{t('password')}</label>
                      <input
                        className="form-input"
                        type="password"
                        value={newUser.password}
                        onChange={e => setNewUser({ ...newUser, password: e.target.value })}
                        required
                      />
                    </div>
                    <div className="form-group">
                      <label className="form-label">{t('role')}</label>
                      <select
                        className="form-input"
                        value={newUser.role}
                        onChange={e => setNewUser({ ...newUser, role: e.target.value })}
                      >
                        {roles.map(r => <option key={r} value={r}>{r.toUpperCase()}</option>)}
                      </select>
                    </div>
                  </div>
                  <button type="submit" className="btn btn-primary" style={{ marginTop: 12 }} disabled={formLoading}>
                    {formLoading ? t('creating') : t('createUser')}
                  </button>
                </form>
              )}

              <table className="table">
                <thead>
                  <tr>
                    <th>{t('username')}</th>
                    <th>{t('fullName')}</th>
                    <th>{t('role')}</th>
                    <th>{t('status')}</th>
                    <th>{t('actions')}</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map(u => (
                    <tr key={u.id || u.username}>
                      <td style={{ fontWeight: 600 }}>{u.username}</td>
                      <td>{u.full_name || '—'}</td>
                      <td><span className="badge">{u.role?.toUpperCase()}</span></td>
                      <td>
                        <span className={`badge badge-${u.is_active !== false ? 'success' : 'danger'}`}>
                          {u.is_active !== false ? t('active') : t('disabled')}
                        </span>
                      </td>
                      <td>
                        {u.username !== user?.username && (
                          <button
                            className="btn btn-outline"
                            style={{ fontSize: '0.75rem', padding: '4px 10px' }}
                            onClick={() => toggleUserStatus(u.id, u.is_active !== false)}
                          >
                            {u.is_active !== false ? t('disable') : t('enable')}
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Audit Log Tab */}
          {tab === 'audit' && (
            <div className="card">
              <h3 className="card-title">{t('auditLog')}</h3>
              {auditLogs.length === 0 ? (
                <p style={{ color: 'var(--text-muted)' }}>{t('noAudit')}</p>
              ) : (
                <div style={{ maxHeight: 500, overflowY: 'auto' }}>
                  <table className="table">
                    <thead>
                      <tr>
                        <th>{t('timestamp')}</th>
                        <th>{t('user')}</th>
                        <th>{t('action')}</th>
                        <th>{t('details')}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {auditLogs.slice(0, 100).map((log, i) => (
                        <tr key={i}>
                          <td style={{ fontSize: '0.8rem', whiteSpace: 'nowrap' }}>
                            {new Date(log.timestamp || log.created_at).toLocaleString()}
                          </td>
                          <td>{log.username || log.user || '—'}</td>
                          <td><span className="badge">{log.action || log.event_type}</span></td>
                          <td style={{ fontSize: '0.8rem', maxWidth: 300, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                            {log.details || log.description || '—'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {/* Roles Tab */}
          {tab === 'roles' && (
            <div className="card">
              <h3 className="card-title">{t('roleDefinitions')}</h3>
              <table className="table">
                <thead>
                  <tr>
                    <th>{t('role')}</th>
                    <th>{t('description')}</th>
                    <th>{t('users')}</th>
                  </tr>
                </thead>
                <tbody>
                  {roles.map(r => (
                    <tr key={r}>
                      <td><span className="badge">{r.toUpperCase()}</span></td>
                      <td style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                        {t(`role${r.charAt(0).toUpperCase() + r.slice(1)}`)}
                      </td>
                      <td>{users.filter(u => u.role === r).length}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </div>
  )
}
