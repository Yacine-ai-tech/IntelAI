import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { useTranslation } from '../i18n/I18nContext'
import { Settings, User, SlidersHorizontal, Info, Check, Globe, Database, RefreshCw } from 'lucide-react'
import { PageHeader, Panel, Grid, Stat, StatGrid } from '../components/ui'
import * as api from '../api'

const SCENARIOS = [
  { id: 'healthy', label: 'Healthy', description: 'Baseline healthy company with strong performance' },
  { id: 'declining_financial', label: 'Declining Financial', description: 'Financial distress scenario' },
  { id: 'high_churn_crisis', label: 'High Churn Crisis', description: 'Customer retention crisis' },
  { id: 'operational_meltdown', label: 'Operational Meltdown', description: 'Operations failure' },
  { id: 'talent_crisis', label: 'Talent Crisis', description: 'HR/talent issues' },
  { id: 'cybersecurity_breach', label: 'Cybersecurity Breach', description: 'Security incident' },
  { id: 'esg_compliance_failure', label: 'ESG Compliance Failure', description: 'ESG governance issues' },
]

export default function SettingsPage() {
  const { user } = useAuth()
  const { t, lang, setLang } = useTranslation()
  const [saved, setSaved] = useState(false)
  const [currentScenario, setCurrentScenario] = useState('healthy')
  const [seeding, setSeeding] = useState(false)
  const [seedError, setSeedError] = useState(null)

  const save = () => { setSaved(true); setTimeout(() => setSaved(false), 1800) }

  const handleScenarioChange = async (scenarioId) => {
    if (seeding) return
    setSeeding(true)
    setSeedError(null)
    try {
      await api.switchScenario(scenarioId)
      setCurrentScenario(scenarioId)
      save()
    } catch (err) {
      setSeedError(err.response?.data?.detail || err.message || 'Failed to switch scenario')
    } finally {
      setSeeding(false)
    }
  }

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

        {user?.role === 'admin' && (
          <Panel title={t('scenarioManagement') || 'Benchmarking Scenarios'} icon={Database} style={{ marginTop: 18 }}>
            <div className="form-group">
              <label className="form-label"><Database size={13} style={{ verticalAlign: 'middle', marginRight: 6 }} />{t('currentScenario') || 'Current Scenario'}</label>
              <select className="form-input" value={currentScenario} onChange={e => handleScenarioChange(e.target.value)} disabled={seeding}>
                {SCENARIOS.map(s => (
                  <option key={s.id} value={s.id}>{s.label}</option>
                ))}
              </select>
            </div>
            <div style={{ marginTop: 12, padding: 12, background: 'var(--surface-2)', borderRadius: 8, border: '1px solid var(--border)' }}>
              <h4 style={{ margin: '0 0 8px 0', fontSize: '.9rem', color: 'var(--text)' }}>{SCENARIOS.find(s => s.id === currentScenario)?.description}</h4>
              <p style={{ margin: 0, fontSize: '.8rem', color: 'var(--text-2)' }}>
                {t('scenarioNote') || 'Switching scenarios will reseed the database with different business health patterns for testing and benchmarking.'}
              </p>
            </div>
            {seedError && (
              <div className="alert alert-danger" style={{ marginTop: 12 }}>{seedError}</div>
            )}
            {seeding && (
              <div style={{ marginTop: 12, display: 'flex', alignItems: 'center', gap: 8, color: 'var(--text-2)', fontSize: '.8rem' }}>
                <RefreshCw size={14} className="spin" /> {t('seedingDatabase') || 'Seeding database with new scenario...'}
              </div>
            )}
          </Panel>
        )}
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
