import { useState, useEffect } from 'react'
import { Outlet, useLocation, useNavigate } from 'react-router-dom'
import Sidebar from './Sidebar'
import ContextualExplainer from './ContextualExplainer'
import ExportMenu from './ExportMenu'
import { useAuth } from '../context/AuthContext'
import * as api from '../api'
import { useTranslation } from '../i18n/I18nContext'
import { HelpCircle, Menu, X, Maximize2 } from 'lucide-react'
import ChatPage from '../pages/ChatPage'

// route segment → { title key, glossary domain (null = show everything) }
const ROUTES = {
  chat:        { title: 'Copilot',       domain: null },
  dashboard:   { title: 'navDashboard',  domain: null },
  analytics:   { title: 'navAnalytics',  domain: null },
  growth:      { title: 'navGrowth',     domain: 'Growth' },
  forecasting: { title: 'navForecasting', domain: null },
  risk:        { title: 'navRisk',       domain: 'Risk' },
  financial:   { title: 'navFinancial',  domain: 'Finance' },
  hr:          { title: 'navHR',         domain: 'People' },
  it:          { title: 'navIT',         domain: 'IT' },
  operations:  { title: 'navOperations', domain: 'Operations' },
  logistics:   { title: 'navLogistics',  domain: 'Logistics' },
  esg:         { title: 'navESG',        domain: 'ESG' },
  knowledge:   { title: 'navKnowledge',  domain: null },
  glossary:    { title: 'navGlossary',   domain: null },
  'data-hub':  { title: 'navDataHub',    domain: null },
  admin:       { title: 'navAdmin',      domain: null },
  settings:    { title: 'navSettings',   domain: null },
  'user-guide': { title: 'navUserGuide', domain: null },
  'api-docs':  { title: 'navApiDocs',    domain: null },
}

export default function Layout() {
  const { user, demoLogin } = useAuth()
  const { t, lang, setLang } = useTranslation()
  const loc = useLocation()
  const navigate = useNavigate()
  const [explainOpen, setExplainOpen] = useState(false)
  const [mobileMenu, setMobileMenu] = useState(false)
  const [collapsed, setCollapsed] = useState(() => localStorage.getItem('sidebar_collapsed') === '1')
  const toggleCollapse = () => setCollapsed(c => { localStorage.setItem('sidebar_collapsed', c ? '0' : '1'); return !c })

  // Global Mini Copilot State
  const [copilotOpen, setCopilotOpen] = useState(false)
  const [copilotQuery, setCopilotQuery] = useState('')

  useEffect(() => {
    const handleOpen = (e) => {
      setCopilotQuery(e.detail.q)
      setCopilotOpen(true)
    }
    window.addEventListener('open-copilot', handleOpen)
    return () => window.removeEventListener('open-copilot', handleOpen)
  }, [])

  const seg = loc.pathname.split('/')[1] || 'chat'
  const route = ROUTES[seg] || ROUTES.chat
  const title = route.title.startsWith('nav') ? t(route.title) : route.title

  useEffect(() => { setMobileMenu(false) }, [loc.pathname])

  return (
    <div className="layout">
      <Sidebar mobileOpen={mobileMenu} onClose={() => setMobileMenu(false)} collapsed={collapsed} onToggleCollapse={toggleCollapse} />
      <main className="main-content">
        <header className="topbar">
          <button className="mobile-nav-btn" onClick={() => setMobileMenu(true)} aria-label={t('openNavigation') || 'Open navigation'}><Menu size={18} /></button>
          <span className="topbar-title">{title}</span>
          <div className="topbar-spacer" />
          {seg !== 'admin' && seg !== 'settings' && (
            <button className="btn btn-sm" onClick={() => setExplainOpen(true)} title={t('explainThisPage') || 'Explain this page'}>
              <HelpCircle size={15} /> {t('explain') || 'Explain'}
            </button>
          )}
          <ExportMenu />
          <div className="lang-toggle" title="Language">
            <button className={lang === 'en' ? 'active' : ''} onClick={() => setLang('en')}>EN</button>
            <button className={lang === 'fr' ? 'active' : ''} onClick={() => setLang('fr')}>FR</button>
          </div>
          {user?.role === 'admin' || localStorage.getItem('was_admin') === 'true' ? (
            <select 
              className="form-input" 
              style={{ width: 'auto', padding: '4px 28px 4px 10px', fontSize: '.85rem' }}
              value={user?.role || 'viewer'}
              onChange={async (e) => {
                try {
                  await demoLogin(e.target.value);
                } catch (err) {
                  console.error("Failed to switch persona", err);
                }
              }}
            >
              <option value="admin">{t('roleAdmin') || 'Admin'}</option>
              <option value="ceo">{t('roleCEO') || 'CEO'}</option>
              <option value="cfo">{t('roleCFO') || 'CFO'}</option>
              <option value="cto">{t('roleCTO') || 'CTO'}</option>
              <option value="coo">{t('roleCOO') || 'COO'}</option>
              <option value="chro">{t('roleCHRO') || 'CHRO'}</option>
              <option value="esg">{t('roleESG') || 'ESG'}</option>
              <option value="risk">{t('roleRisk') || 'Risk'}</option>
              <option value="analyst">{t('roleAnalyst') || 'Analyst'}</option>
              <option value="viewer">{t('roleViewer') || 'Viewer'}</option>
            </select>
          ) : (
            <div className="role-chip">
              <b>{user?.full_name || user?.username}</b><span>· {user?.role}</span>
            </div>
          )}
        </header>
        <div className={`main-scroll${seg === 'chat' ? '' : ' page-pad'}`}><Outlet /></div>
      </main>
      {explainOpen && <ContextualExplainer domain={route.domain} onClose={() => setExplainOpen(false)} />}
      
      {/* Floating Mini Copilot */}
      {copilotOpen && seg !== 'chat' && (
        <div style={{
          position: 'fixed', bottom: 20, right: 20, width: 450, height: 600,
          background: 'var(--surface)', borderRadius: 12, boxShadow: '0 10px 40px rgba(0,0,0,0.2)',
          display: 'flex', flexDirection: 'column', zIndex: 9999, border: '1px solid var(--border)', overflow: 'hidden'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 14px', background: 'var(--surface-2)', borderBottom: '1px solid var(--border)' }}>
            <span style={{ fontWeight: 600, fontSize: '.95rem' }}>{t('navAssistant') || 'Copilot'}</span>
            <div style={{ display: 'flex', gap: 6 }}>
              <button className="btn btn-ghost btn-sm btn-icon" title={t('expandToFull') || 'Expand to full page'} aria-label={t('expandToFull') || 'Expand to full page'} onClick={() => { setCopilotOpen(false); navigate(`/chat?q=${encodeURIComponent(copilotQuery)}`) }}>
                <Maximize2 size={14} />
              </button>
              <button className="btn btn-ghost btn-sm btn-icon" aria-label={t('close') || 'Close'} onClick={() => setCopilotOpen(false)}>
                <X size={14} />
              </button>
            </div>
          </div>
          <div style={{ flex: 1, position: 'relative' }}>
             <ChatPage isWidget={true} initialQuery={copilotQuery} />
          </div>
        </div>
      )}
    </div>
  )
}
