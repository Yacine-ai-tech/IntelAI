import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { useTranslation } from '../i18n/I18nContext'
import { Settings, User, SlidersHorizontal, Info, Check } from 'lucide-react'

export default function SettingsPage() {
  const { user } = useAuth()
  const { t, lang, setLang } = useTranslation()
  const [theme, setTheme] = useState(localStorage.getItem('omni_theme') || 'dark')
  const [ttsVoice, setTtsVoice] = useState(localStorage.getItem('omni_tts_voice') || 'en-US-AriaNeural')
  const [saved, setSaved] = useState(false)

  const saveSettings = () => {
    localStorage.setItem('omni_theme', theme)
    localStorage.setItem('omni_tts_voice', ttsVoice)

    if (theme === 'light') {
      document.documentElement.style.setProperty('--bg-primary', '#f8fafc')
      document.documentElement.style.setProperty('--bg-secondary', '#ffffff')
      document.documentElement.style.setProperty('--bg-tertiary', '#f1f5f9')
      document.documentElement.style.setProperty('--text-primary', '#0f172a')
      document.documentElement.style.setProperty('--text-secondary', '#334155')
      document.documentElement.style.setProperty('--text-muted', '#64748b')
      document.documentElement.style.setProperty('--border', '#e2e8f0')
    } else {
      document.documentElement.style.setProperty('--bg-primary', '#0f1117')
      document.documentElement.style.setProperty('--bg-secondary', '#1a1d27')
      document.documentElement.style.setProperty('--bg-tertiary', '#242837')
      document.documentElement.style.setProperty('--text-primary', '#e2e8f0')
      document.documentElement.style.setProperty('--text-secondary', '#94a3b8')
      document.documentElement.style.setProperty('--text-muted', '#64748b')
      document.documentElement.style.setProperty('--border', '#2d3348')
    }

    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  return (
    <div>
      <h1 className="page-title" style={{ marginBottom: 24 }}><Settings size={24} /> {t('settings')}</h1>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
        {/* Profile */}
        <div className="card">
          <h3 className="card-title"><User size={16} /> {t('profile')}</h3>
          <div className="form-group">
            <label className="form-label">{t('username')}</label>
            <input className="form-input" value={user?.username || ''} disabled />
          </div>
          <div className="form-group">
            <label className="form-label">{t('fullName')}</label>
            <input className="form-input" value={user?.full_name || ''} disabled />
          </div>
          <div className="form-group">
            <label className="form-label">{t('role')}</label>
            <input className="form-input" value={user?.role?.toUpperCase() || ''} disabled />
          </div>
        </div>

        {/* Preferences */}
        <div className="card">
          <h3 className="card-title"><SlidersHorizontal size={16} /> {t('preferences')}</h3>

          <div className="form-group">
            <label className="form-label">{t('language')}</label>
            <select className="form-input" value={lang} onChange={e => setLang(e.target.value)}>
              <option value="en">English</option>
              <option value="fr">Français</option>
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">{t('theme')}</label>
            <select className="form-input" value={theme} onChange={e => setTheme(e.target.value)}>
              <option value="dark">{t('dark')}</option>
              <option value="light">{t('light')}</option>
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">{t('ttsVoice')}</label>
            <select className="form-input" value={ttsVoice} onChange={e => setTtsVoice(e.target.value)}>
              <optgroup label="English">
                <option value="en-US-AriaNeural">Aria (Female)</option>
                <option value="en-US-GuyNeural">Guy (Male)</option>
              </optgroup>
              <optgroup label="Français">
                <option value="fr-FR-DeniseNeural">Denise (Femme)</option>
                <option value="fr-FR-HenriNeural">Henri (Homme)</option>
              </optgroup>
            </select>
          </div>

          <button className="btn btn-primary" onClick={saveSettings} style={{ marginTop: 8 }}>
            {saved ? <><Check size={14} /> {t('saved')}</> : t('savePreferences')}
          </button>
        </div>
      </div>

      {/* System Info */}
      <div className="card" style={{ marginTop: 20 }}>
        <h3 className="card-title"><Info size={16} /> {t('systemInfo')}</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16 }}>
          <div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{t('platform')}</div>
            <div style={{ fontWeight: 600 }}>OmniIntelOS v2.0</div>
          </div>
          <div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{t('backend')}</div>
            <div style={{ fontWeight: 600 }}>FastAPI + PostgreSQL</div>
          </div>
          <div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{t('llmProvider')}</div>
            <div style={{ fontWeight: 600 }}>Groq (LLaMA 3.1)</div>
          </div>
          <div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{t('ttsEngine')}</div>
            <div style={{ fontWeight: 600 }}>Edge-TTS (Microsoft Neural)</div>
          </div>
          <div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{t('vectorStore')}</div>
            <div style={{ fontWeight: 600 }}>ChromaDB</div>
          </div>
          <div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{t('agentSystem')}</div>
            <div style={{ fontWeight: 600 }}>Dynamic Persona Factory</div>
          </div>
        </div>
      </div>
    </div>
  )
}
