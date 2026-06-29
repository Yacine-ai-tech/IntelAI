import { useState } from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import Sidebar from './Sidebar'
import ContextualExplainer from './ContextualExplainer'
import ExportMenu from './ExportMenu'
import { useAuth } from '../context/AuthContext'
import * as api from '../api'
import { useTranslation } from '../i18n/I18nContext'
import { HelpCircle, Menu, X } from 'lucide-react'
import { useEffect } from 'react'

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
}

export default function Layout() {
  const { user } = useAuth()
  const { t, lang, setLang } = useTranslation()
  const loc = useLocation()
  const [explainOpen, setExplainOpen] = useState(false)
  const [mobileMenu, setMobileMenu] = useState(false)

  const seg = loc.pathname.split('/')[1] || 'chat'
  const route = ROUTES[seg] || ROUTES.chat
  const title = route.title.startsWith('nav') ? t(route.title) : route.title

  useEffect(() => { setMobileMenu(false) }, [loc.pathname])

  return (
    <div className="layout">
      <Sidebar mobileOpen={mobileMenu} onClose={() => setMobileMenu(false)} />
      <main className="main-content">
        <header className="topbar">
          <button className="mobile-nav-btn" onClick={() => setMobileMenu(true)}><Menu size={18} /></button>
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
          {user?.role === 'admin' ? (
            <select 
              className="form-input" 
              style={{ width: 'auto', padding: '4px 28px 4px 10px', fontSize: '.85rem' }}
              value={user?.role || 'viewer'}
              onChange={async (e) => {
                try {
                  const res = await api.demoLogin(e.target.value);
                  localStorage.setItem('access_token', res.data.access_token);
                  window.location.reload();
                } catch (err) {
                  console.error("Failed to switch persona", err);
                }
              }}
            >
              <option value="admin">Admin</option>
              <option value="ceo">CEO</option>
              <option value="cfo">CFO</option>
              <option value="cto">CTO</option>
              <option value="coo">COO</option>
              <option value="chro">CHRO</option>
              <option value="esg">ESG</option>
              <option value="risk">Risk</option>
              <option value="analyst">Analyst</option>
              <option value="viewer">Viewer</option>
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
    </div>
  )
}
