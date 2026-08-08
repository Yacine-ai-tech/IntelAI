import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useTranslation } from '../i18n/I18nContext'
import CubeMark from './Brand'
import {
  LayoutDashboard, BarChart3, TrendingUp, Users, Package, Monitor,
  Settings2, Leaf, ShieldAlert, Database, ShieldCheck, Settings,
  LogOut, BookOpen, Sparkles, DollarSign, X, ChevronsLeft, ChevronsRight,
  Share2, FileText, GitCompareArrows, Network, Terminal, LifeBuoy,
} from 'lucide-react'

export default function Sidebar({ mobileOpen, onClose, collapsed = false, onToggleCollapse = () => {} }) {
  const { user, logout, hasPage } = useAuth()
  const { t } = useTranslation()
  const navigate = useNavigate()

  // Copilot is the product centerpiece — pinned at the top, everything else is supporting context.
  const SECTIONS = [
    {
      label: t('sidebarCore') || 'Overview',
      items: [
        { to: '/workspace',   label: t('navWorkspace') || 'Workspace', icon: Sparkles, page: 'assistant' },
        { to: '/dashboard',   label: t('navDashboard'),   icon: LayoutDashboard, page: 'dashboard' },
        { to: '/analytics',   label: t('navAnalytics'),   icon: BarChart3,       page: 'analytics' },
        { to: '/forecasting', label: t('navForecasting'), icon: TrendingUp,      page: 'forecasting' },
        { to: '/risk',        label: t('navRisk'),        icon: ShieldAlert,     page: 'risk' },
        { to: '/financial',   label: t('navFinancial'),   icon: DollarSign,      page: 'cfo' },
      ],
    },
    {
      label: t('sidebarDomains') || 'Domains',
      items: [
        { to: '/growth',     label: t('navGrowth') || 'Growth', icon: TrendingUp, page: 'analytics' },
        { to: '/hr',         label: t('navHR'),         icon: Users,     page: 'hr' },
        { to: '/it',         label: t('navIT'),         icon: Monitor,   page: 'it' },
        { to: '/operations', label: t('navOperations'), icon: Settings2, page: 'operations' },
        { to: '/logistics',  label: t('navLogistics'),  icon: Package,   page: 'logistics' },
        { to: '/esg',        label: t('navESG'),        icon: Leaf,      page: 'esg' },
      ],
    },
    {
      label: t('sidebarSystem') || 'Knowledge & System',
      items: [
        { to: '/knowledge', label: t('navKnowledge') || 'Knowledge', icon: BookOpen,    page: 'analytics' },
        { to: '/knowledge-graph', label: t('navKnowledgeGraph') || 'Knowledge Graph', icon: Share2, page: 'analytics' },
        { to: '/glossary',  label: t('navGlossary') || 'Glossary',   icon: BookOpen,    page: 'analytics' },
        { to: '/reports',   label: t('navReports') || 'Reports',      icon: FileText,    page: 'analytics' },
        { to: '/compare',   label: t('navCompare') || 'Compare Personas', icon: GitCompareArrows, page: 'assistant' },
        { to: '/organization', label: t('navOrganization') || 'Organization', icon: Network, page: 'analytics' },
        { to: '/data-hub',  label: t('navDataHub'),                  icon: Database,    page: 'data_hub' },
        { to: '/governance', label: t('navGovernance') || 'Governance', icon: ShieldCheck, page: 'admin' },
        { to: '/admin',     label: t('navAdmin'),                    icon: ShieldCheck, page: 'admin' },
        { to: '/settings',  label: t('navSettings'),                 icon: Settings,    page: 'settings' },
        { to: '/user-guide', label: t('navUserGuide') || 'User Guide', icon: LifeBuoy,  page: 'assistant' },
        { to: '/api-docs',  label: t('navApiDocs') || 'API Reference', icon: Terminal,  page: 'assistant' },
      ],
    },
  ]

  const handleLogout = () => { logout(); navigate('/login') }
  const initials = (user?.full_name || user?.username || 'U')
    .split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase()

  return (
    <>
      {mobileOpen && <div className="sidebar-overlay" onClick={onClose} />}
      <aside className={`sidebar ${mobileOpen ? 'mobile-open' : ''}${collapsed ? ' collapsed' : ''}`}>
        {mobileOpen && <button className="btn btn-ghost btn-icon mobile-close-btn" onClick={onClose} style={{ position: 'absolute', top: 12, right: 12, zIndex: 10 }}><X size={18} /></button>}
        <div className="sidebar-header">
          <div className="sidebar-brand">
            <CubeMark size={38} />
            <div>
              <div className="sidebar-brand-text">{t('appName')}</div>
              <div className="sidebar-brand-sub">{t('appTagline')}</div>
            </div>
          </div>
        </div>

      <nav className="sidebar-nav">
        {hasPage('assistant') && (
          <NavLink to="/chat" title={t('navAssistant') || 'Copilot'} className={({ isActive }) => `sidebar-cta${isActive ? ' active' : ''}`}>
            <Sparkles size={18} />
            <span>{t('navAssistant') || 'Copilot'}</span>
          </NavLink>
        )}

        {SECTIONS.map(section => {
          const visible = section.items.filter(item => hasPage(item.page))
          if (visible.length === 0) return null
          return (
            <div key={section.label} className="sidebar-section">
              <div className="sidebar-section-label">{section.label}</div>
              {visible.map(item => {
                const Icon = item.icon
                return (
                  <NavLink key={item.to} to={item.to} title={item.label}
                    className={({ isActive }) => `sidebar-link${isActive ? ' active' : ''}`}>
                    <Icon size={18} />
                    <span>{item.label}</span>
                  </NavLink>
                )
              })}
            </div>
          )
        })}
      </nav>

      <div className="sidebar-footer">
        <div className="sidebar-user">
          <div className="sidebar-user-avatar">{initials}</div>
          <div className="sidebar-user-info">
            <div className="sidebar-user-name">{user?.full_name || user?.username}</div>
            <div className="sidebar-user-role">{user?.role}</div>
          </div>
        </div>
        <button onClick={handleLogout} className="btn btn-outline btn-sm" style={{ width: '100%' }} title={t('signOut')}>
          <LogOut size={14} />
          <span className="sidebar-label">{t('signOut')}</span>
        </button>
        <button onClick={onToggleCollapse} className="btn btn-ghost btn-sm sidebar-collapse-btn" style={{ width: '100%', marginTop: 6 }}
          title={collapsed ? (t('expand') || 'Expand') : (t('collapse') || 'Collapse')}>
          {collapsed ? <ChevronsRight size={16} /> : <ChevronsLeft size={16} />}
          <span className="sidebar-label">{t('collapse') || 'Collapse'}</span>
        </button>
      </div>
    </aside>
    </>
  )
}
