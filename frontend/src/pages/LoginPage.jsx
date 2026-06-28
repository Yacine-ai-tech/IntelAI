import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useTranslation } from '../i18n/I18nContext'
import CubeMark from '../components/Brand'
import {
  ShieldCheck, Briefcase, DollarSign, Cpu, BarChart3, Eye, EyeOff, AlertCircle,
  Sparkles, FileText, Languages, Lock, ArrowRight, Loader2,
  Settings2, Users, Leaf, ShieldAlert, Landmark,
} from 'lucide-react'

// All personas — one-click demo via the password-less /auth/demo-login endpoint.
const DEMO = [
  { user: 'admin',   role: 'Admin',   Icon: ShieldCheck },
  { user: 'ceo',     role: 'CEO',     Icon: Briefcase },
  { user: 'cfo',     role: 'CFO',     Icon: DollarSign },
  { user: 'cto',     role: 'CTO',     Icon: Cpu },
  { user: 'coo',     role: 'COO',     Icon: Settings2 },
  { user: 'chro',    role: 'CHRO',    Icon: Users },
  { user: 'esg',     role: 'ESG',     Icon: Leaf },
  { user: 'risk',    role: 'Risk',    Icon: ShieldAlert },
  { user: 'analyst', role: 'Analyst', Icon: BarChart3 },
  { user: 'board',   role: 'Board',   Icon: Landmark },
  { user: 'viewer',  role: 'Viewer',  Icon: Eye },
]

export default function LoginPage() {
  const { login, demoLogin: demoAuth } = useAuth()
  const { t, lang, setLang } = useTranslation()
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [showPw, setShowPw] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const doLogin = async (u, p) => {
    setError(''); setLoading(true)
    try {
      await login(u, p)
      navigate('/chat')
    } catch (err) {
      setError(err.response?.data?.detail || t('loginFailed') || 'Login failed')
      setLoading(false)
    }
  }
  const onSubmit = (e) => { e.preventDefault(); doLogin(username, password) }
  const demoLogin = async (u) => {
    setError(''); setLoading(true)
    try { await demoAuth(u); navigate('/chat') }
    catch (err) { setError(err.response?.data?.detail || t('loginFailed') || 'Login failed'); setLoading(false) }
  }

  const features = [
    { icon: Sparkles, text: t('authFeat1') || 'Persona-routed RAG copilot — answers scoped to your role' },
    { icon: FileText, text: t('authFeat2') || 'Grounded, cited answers over your live KPIs' },
    { icon: Languages, text: t('authFeat3') || 'Bilingual (EN / FR) · 7 business domains' },
  ]

  return (
    <div className="auth-page">
      {/* Brand / marketing panel */}
      <div className="auth-brand">
        <div className="auth-brand-inner">
          <div className="sidebar-brand" style={{ marginBottom: 28 }}>
            <CubeMark size={48} />
            <div>
              <div className="sidebar-brand-text" style={{ fontSize: '1.5rem' }}>{t('appName') || 'IntelAI'}</div>
              <div className="sidebar-brand-sub">{t('appTagline') || 'AI Analytics & RAG Copilot'}</div>
            </div>
          </div>
          <h1 className="display" style={{ fontSize: '2rem', lineHeight: 1.2, marginBottom: 14 }}>
            {t('authHeadline') || 'Decisions, grounded in your data.'}
          </h1>
          <p style={{ color: 'var(--text-2)', fontSize: '.95rem', maxWidth: 420 }}>
            {t('authSub') || 'Ask in plain language. Get role-scoped, cited answers from your live KPIs — never a hallucination.'}
          </p>
          <div style={{ marginTop: 30, display: 'flex', flexDirection: 'column', gap: 16 }}>
            {features.map((f, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <div className="auth-feat-icon"><f.icon size={16} /></div>
                <span style={{ color: 'var(--text-2)', fontSize: '.9rem' }}>{f.text}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Form panel */}
      <div className="auth-form-wrap">
        <div className="lang-toggle" style={{ position: 'absolute', top: 24, right: 24 }}>
          <button className={lang === 'en' ? 'active' : ''} onClick={() => setLang('en')}>EN</button>
          <button className={lang === 'fr' ? 'active' : ''} onClick={() => setLang('fr')}>FR</button>
        </div>

        <div className="auth-card">
          <h2 className="display" style={{ fontSize: '1.5rem' }}>{t('welcomeBack') || 'Welcome back'}</h2>
          <p style={{ color: 'var(--text-3)', fontSize: '.86rem', marginBottom: 22 }}>{t('signInToContinue') || 'Sign in to continue'}</p>

          {error && <div className="alert alert-danger" style={{ marginBottom: 16 }}><AlertCircle size={16} /><span>{error}</span></div>}

          <form onSubmit={onSubmit}>
            <div className="form-group">
              <label className="form-label">{t('username') || 'Username'}</label>
              <input className="form-input" value={username} autoFocus required
                onChange={e => setUsername(e.target.value)} placeholder={t('enterUsername') || 'e.g. analyst'} />
            </div>
            <div className="form-group">
              <label className="form-label">{t('password') || 'Password'}</label>
              <div style={{ position: 'relative' }}>
                <input className="form-input" type={showPw ? 'text' : 'password'} value={password} required
                  onChange={e => setPassword(e.target.value)} placeholder={t('enterPassword') || '••••••••'} style={{ paddingRight: 42 }} />
                <button type="button" onClick={() => setShowPw(s => !s)} title={showPw ? 'Hide' : 'Show'}
                  style={{ position: 'absolute', right: 8, top: '50%', transform: 'translateY(-50%)', background: 'none', border: 0, color: 'var(--text-3)', cursor: 'pointer', padding: 4 }}>
                  {showPw ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>
            <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: 6 }} disabled={loading}>
              {loading ? <><Loader2 size={16} className="spin-inline" /> {t('signingIn') || 'Signing in…'}</>
                       : <><Lock size={15} /> {t('signIn') || 'Sign in'} <ArrowRight size={15} /></>}
            </button>
          </form>

          <div className="auth-divider"><span>{t('demoAccounts') || 'or try a demo role'}</span></div>
          <div className="login-quick-grid">
            {DEMO.map(d => (
              <button key={d.user} className="login-quick-btn" disabled={loading} onClick={() => demoLogin(d.user)}>
                <d.Icon size={18} /><span>{d.role}</span>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
