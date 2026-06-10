import { useState } from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import Sidebar from './Sidebar'
import ContextualExplainer from './ContextualExplainer'
import ExportMenu from './ExportMenu'
import { useAuth } from '../context/AuthContext'
import { useTranslation } from '../i18n/I18nContext'
import { HelpCircle } from 'lucide-react'

// route segment → { title key, glossary domain (null = show everything) }
const ROUTES = {
  chat:        { title: 'Copilot',       domain: null },
  dashboard:   { title: 'navDashboard',  domain: null },
  analytics:   { title: 'navAnalytics',  domain: null },
  forecasting: { title: 'navForecasting', domain: null },
  risk:        { title: 'navRisk',       domain: 'Risk' },
  financial:   { title: 'navFinancial',  domain: 'Finance' },
  hr:          { title: 'navHR',         domain: 'People' },
  it:          { title: 'navIT',         domain: 'IT' },
  operations:  { title: 'navOperations', domain: 'Operations' },
  logistics:   { title: 'navLogistics',  domain: 'Logistics' },
  esg:         { title: 'navESG',        domain: 'ESG' },
  knowledge:   { title: 'navKnowledge',  domain: null },
  'data-hub':  { title: 'navDataHub',    domain: null },
  admin:       { title: 'navAdmin',      domain: null },
  settings:    { title: 'navSettings',   domain: null },
}

export default function Layout() {
  const { user } = useAuth()
  const { t, lang, setLang } = useTranslation()
  const loc = useLocation()
  const [explainOpen, setExplainOpen] = useState(false)

  const seg = loc.pathname.split('/')[1] || 'chat'
  const route = ROUTES[seg] || ROUTES.chat
  const title = route.title.startsWith('nav') ? t(route.title) : route.title

  return (
    <div className="layout">
      <Sidebar />
      <main className="main-content">
        <header className="topbar">
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
          <div className="role-chip">
            <b>{user?.full_name || user?.username}</b><span>· {user?.role}</span>
          </div>
        </header>
        <div className={`main-scroll${seg === 'chat' ? '' : ' page-pad'}`}><Outlet /></div>
      </main>
      {explainOpen && <ContextualExplainer domain={route.domain} onClose={() => setExplainOpen(false)} />}
    </div>
  )
}
