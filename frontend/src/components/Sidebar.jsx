import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useTranslation } from '../i18n/I18nContext'
import CubeMark from './Brand'
import {
  LayoutDashboard, BarChart3, TrendingUp, Users, Package, Monitor,
  Settings2, Leaf, ShieldAlert, Database, ShieldCheck, Settings,
  LogOut, BookOpen, Sparkles, DollarSign,
} from 'lucide-react'

export default function Sidebar() {
  const { user, logout, hasPage } = useAuth()
  const { t } = useTranslation()
  const navigate = useNavigate()

  // Copilot is the product centerpiece — pinned at the top, everything else is supporting context.
  const SECTIONS = [
    {
      label: t('sidebarCore') || 'Overview',
      items: [
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
        { to: '/data-hub',  label: t('navDataHub'),                  icon: Database,    page: 'data_hub' },
        { to: '/admin',     label: t('navAdmin'),                    icon: ShieldCheck, page: 'admin' },
        { to: '/settings',  label: t('navSettings'),                 icon: Settings,    page: 'settings' },
      ],
    },
  ]

  const handleLogout = () => { logout(); navigate('/login') }
  const initials = (user?.full_name || user?.username || 'U')
    .split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase()

  return (
    <aside className="sidebar">
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
          <NavLink to="/chat" className={({ isActive }) => `sidebar-cta${isActive ? ' active' : ''}`}>
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
                  <NavLink key={item.to} to={item.to}
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
        <button onClick={handleLogout} className="btn btn-outline btn-sm" style={{ width: '100%' }}>
          <LogOut size={14} />
          <span>{t('signOut')}</span>
        </button>
      </div>
    </aside>
  )
}
