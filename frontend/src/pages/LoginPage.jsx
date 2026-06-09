import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useTranslation } from '../i18n/I18nContext'
import { ShieldCheck, Briefcase, DollarSign, Cpu, BarChart3, Eye, AlertCircle, Sparkles } from 'lucide-react'

export default function LoginPage() {
  const { login } = useAuth()
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(username, password)
      navigate('/dashboard')
    } catch (err) {
      setError(err.response?.data?.detail || t('loginFailed'))
    } finally {
      setLoading(false)
    }
  }

  const quickLogins = [
    { user: 'admin',   role: 'Admin',   Icon: ShieldCheck },
    { user: 'ceo',     role: 'CEO',     Icon: Briefcase },
    { user: 'cfo',     role: 'CFO',     Icon: DollarSign },
    { user: 'cto',     role: 'CTO',     Icon: Cpu },
    { user: 'analyst', role: 'Analyst', Icon: BarChart3 },
    { user: 'viewer',  role: 'Viewer',  Icon: Eye },
  ]

  return (
    <div className="login-page">
      <div className="login-container">
        <div className="login-header">
          <div className="login-brand-icon">
            <Sparkles size={30} strokeWidth={2.2} />
          </div>
          <h1>{t('appName')}</h1>
          <p style={{ color: 'var(--text-muted)', margin: 0, fontSize: '0.85rem' }}>
            {t('appTagline')}
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          {error && (
            <div className="alert alert-danger">
              <AlertCircle size={16} />
              <span>{error}</span>
            </div>
          )}

          <div className="form-group">
            <label className="form-label">{t('username')}</label>
            <input
              type="text"
              className="form-input"
              value={username}
              onChange={e => setUsername(e.target.value)}
              placeholder={t('enterUsername')}
              autoFocus
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">{t('password')}</label>
            <input
              type="password"
              className="form-input"
              value={password}
              onChange={e => setPassword(e.target.value)}
              placeholder={t('enterPassword')}
              required
            />
          </div>

          <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: 8 }} disabled={loading}>
            {loading ? (
              <><span className="spinner" style={{ width: 16, height: 16 }} /> {t('signingIn')}</>
            ) : t('signIn')}
          </button>
        </form>

        <div style={{ marginTop: 24 }}>
          <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textAlign: 'center', marginBottom: 12, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
            {t('quickAccess')}
          </div>
          <div className="login-quick-grid">
            {quickLogins.map(q => (
              <button
                key={q.user}
                className="login-quick-btn"
                onClick={() => { setUsername(q.user); setPassword(q.user + '123') }}
              >
                <q.Icon size={18} />
                <span>{q.role}</span>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
