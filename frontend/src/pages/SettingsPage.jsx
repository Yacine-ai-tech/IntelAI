import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { useTranslation } from '../i18n/I18nContext'
import { Settings, User, SlidersHorizontal, Info, Check, Globe } from 'lucide-react'
import { PageHeader, Panel, Grid, Stat, StatGrid } from '../components/ui'

export default function SettingsPage() {
  const { user } = useAuth()
  const { t, lang, setLang } = useTranslation()
  const [saved, setSaved] = useState(false)

  const save = () => { setSaved(true); setTimeout(() => setSaved(false), 1800) }

  const sys = [
    [t('platform') || 'Platform', 'IntelAI v0.1.0'],
    [t('backend') || 'Backend', 'FastAPI + PostgreSQL'],
    [t('llmProvider') || 'LLM', 'Groq / Anthropic (LiteLLM router)'],
    [t('vectorStore') || 'Retrieval', 'Hybrid (vector + BM25 + RRF + reranker)'],
    [t('agentSystem') || 'Agents', 'Persona-Routed RAG (9 personas)'],
    ['Grounding', '64-term glossary · cited answers'],
  ]

  return (
    <div>
      <PageHeader icon={Settings} title={t('navSettings') || 'Settings'} subtitle={t('settingsSubtitle') || 'Profile, preferences & system'} />

      <Grid min={320}>
        <Panel title={t('profile') || 'Profile'} icon={User}>
          <div className="form-group">
            <label className="form-label">{t('username') || 'Username'}</label>
            <input className="form-input" value={user?.username || ''} disabled />
          </div>
          <div className="form-group">
            <label className="form-label">{t('fullName') || 'Full name'}</label>
            <input className="form-input" value={user?.full_name || ''} disabled />
          </div>
          <div className="form-group">
            <label className="form-label">{t('role') || 'Role'}</label>
            <input className="form-input" value={user?.role?.toUpperCase() || ''} disabled />
          </div>
        </Panel>

        <Panel title={t('preferences') || 'Preferences'} icon={SlidersHorizontal}>
          <div className="form-group">
            <label className="form-label"><Globe size={13} style={{ verticalAlign: 'middle', marginRight: 6 }} />{t('language') || 'Language'}</label>
            <select className="form-input" value={lang} onChange={e => setLang(e.target.value)}>
              <option value="en">English</option>
              <option value="fr">Français</option>
            </select>
          </div>
          <p style={{ fontSize: '.8rem', color: 'var(--text-3)', marginBottom: 14 }}>
            {t('themeNote') || 'IntelAI uses a focused dark theme tuned for analytics dashboards.'}
          </p>
          <button className="btn btn-primary" onClick={save}>
            {saved ? <><Check size={14} /> {t('saved') || 'Saved'}</> : (t('savePreferences') || 'Save preferences')}
          </button>
        </Panel>
      </Grid>

      <Panel title={t('systemInfo') || 'System'} icon={Info} style={{ marginTop: 18 }}>
        <StatGrid>
          {sys.map(([label, value]) => (
            <div key={label} className="kpi-card">
              <div className="kpi-label">{label}</div>
              <div style={{ fontWeight: 600, marginTop: 4, fontSize: '.92rem' }}>{value}</div>
            </div>
          ))}
        </StatGrid>
      </Panel>
    </div>
  )
}
