// Executive Workspace — the landing experience. The same organizational data, entered
// through strategic questions rather than a chat box: persona lenses, live health,
// anomalies, and one-click paths into Copilot, Forecasting and Knowledge.
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  Sparkles, TrendingUp, ShieldAlert, BookOpen, DollarSign, Activity, Flag,
  Bot, Crown, Cpu, Settings2, Users, Leaf, BarChart3, ArrowRight,
} from 'lucide-react'
import * as api from '../api'
import { useAuth } from '../context/AuthContext'
import { useTranslation } from '../i18n/I18nContext'
import { Stat, StatGrid, Panel, Loading } from '../components/ui'

// Same identity map the Copilot uses (ChatPage) — one visual language for personas.
const PERSONA_META = {
  general: { color: 'var(--p-general)', icon: Bot, label: 'Assistant', focus: 'Cross-domain questions' },
  ceo:     { color: 'var(--p-ceo)', icon: Crown, label: 'CEO', focus: 'Board-level snapshot · growth · risk' },
  cfo:     { color: 'var(--p-cfo)', icon: DollarSign, label: 'CFO', focus: 'Margins · cash flow · revenue' },
  cto:     { color: 'var(--p-cto)', icon: Cpu, label: 'CTO', focus: 'Uptime · security · engineering' },
  coo:     { color: 'var(--p-coo)', icon: Settings2, label: 'COO', focus: 'Operations · supply chain · quality' },
  chro:    { color: 'var(--p-chro)', icon: Users, label: 'CHRO', focus: 'Talent · retention · headcount' },
  esg:     { color: 'var(--p-esg)', icon: Leaf, label: 'ESG', focus: 'Emissions · sustainability · governance' },
  risk:    { color: 'var(--p-risk)', icon: ShieldAlert, label: 'Risk', focus: 'Anomalies · exposure · compliance' },
  analyst: { color: 'var(--p-analyst)', icon: BarChart3, label: 'Analyst', focus: 'KPIs · trends · deep dives' },
}

export default function WorkspacePage() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const { t } = useTranslation()

  const { data: personas = [] } = useQuery({
    queryKey: ['personas'],
    queryFn: () => api.listPersonas().then(r => r.data?.personas || r.data || []),
  })
  const { data: health } = useQuery({
    queryKey: ['health'], queryFn: () => api.getHealth().then(r => r.data),
  })
  const { data: summary } = useQuery({
    queryKey: ['summary'], queryFn: () => api.getSummary().then(r => r.data),
  })
  const { data: anomalies = [] } = useQuery({
    queryKey: ['anomalies'], queryFn: () => api.getAnomalies().then(r => r.data?.anomalies || []),
  })
  const { data: kstats } = useQuery({
    queryKey: ['knowledge-stats'], queryFn: () => api.getKnowledgeStats().then(r => r.data),
  })

  const h = new Date().getHours()
  const greeting = h < 12 ? (t('goodMorning') || 'Good morning') : h < 18 ? (t('goodAfternoon') || 'Good afternoon') : (t('goodEvening') || 'Good evening')
  const firstName = (user?.full_name || user?.username || '').split(' ')[0]
  const hScore = Math.round(health?.score ?? health?.health_index ?? 0)
  const docCount = kstats?.documents ?? kstats?.total_documents ?? kstats?.count

  const QUICK = [
    { icon: Sparkles, label: t('navAssistant') || 'Ask Executive Copilot', hint: 'Strategic Q&A with sources', to: '/chat' },
    { icon: TrendingUp, label: t('navForecasting') || 'Run a forecast', hint: 'Monte-Carlo confidence bands', to: '/forecasting' },
    { icon: Flag, label: 'Review anomalies', hint: `${anomalies.length} flagged across domains`, to: '/analytics' },
    { icon: BookOpen, label: t('navKnowledge') || 'Search knowledge', hint: 'RAG over indexed documents', to: '/knowledge' },
    { icon: DollarSign, label: t('navFinancial') || 'Financial statement', hint: 'Generated from live KPIs', to: '/financial' },
    { icon: ShieldAlert, label: t('navRisk') || 'Risk posture', hint: 'Exposure & concentration', to: '/risk' },
  ]

  return (
    <div>
      {/* Hero */}
      <div style={{ margin: '6px 0 22px' }}>
        <h1 style={{ font: '700 26px/1.25 var(--font-display)', letterSpacing: '-0.5px' }}>
          {greeting}{firstName ? `, ${firstName}` : ''}.
        </h1>
        <p style={{ color: 'var(--text-2)', marginTop: 6, fontSize: 14.5 }}>
          What strategic question are we solving today?
        </p>
      </div>

      {/* Live pulse — same sources the Dashboard reads */}
      <StatGrid>
        <Stat label={t('healthIndex') || 'Business health'} value={hScore} unit="/100" icon={Activity}
          accent={hScore >= 70 ? 'var(--ok)' : hScore >= 45 ? 'var(--warn)' : 'var(--bad)'}
          hint={health?.label} onClick={() => navigate('/analytics')} />
        <Stat label="Active anomalies" value={anomalies.length} icon={Flag}
          accent={anomalies.length ? 'var(--anomaly)' : 'var(--ok)'}
          hint={anomalies.length ? 'click to investigate' : 'all clear'} onClick={() => navigate('/analytics')} />
        <Stat label="Executive personas" value={personas.length || Object.keys(PERSONA_META).length - 1} icon={Users}
          accent="var(--accent)" hint="role-scoped intelligence" onClick={() => navigate('/chat')} />
        {docCount != null && (
          <Stat label="Indexed documents" value={docCount} icon={BookOpen}
            accent="var(--primary-2)" hint="knowledge base" onClick={() => navigate('/knowledge')} />
        )}
      </StatGrid>

      {/* Persona lenses — the defining feature, not hidden in a dropdown */}
      <Panel title="Choose your lens" icon={Users}
        actions={<span style={{ color: 'var(--text-3)', fontSize: 12 }}>same company · different intelligence</span>}>
        {personas.length === 0 ? (
          <Loading label="Loading personas…" />
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(190px, 1fr))', gap: 10 }}>
            {personas.map(p => {
              const key = p.id || p.persona_id || p.name
              const pm = PERSONA_META[key] || PERSONA_META.general
              const PIcon = pm.icon
              return (
                <button key={key} onClick={() => navigate(`/chat?persona=${encodeURIComponent(key)}`)}
                  className="workspace-persona-card"
                  style={{
                    display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 8,
                    padding: '14px 15px', textAlign: 'left', cursor: 'pointer',
                    background: 'var(--surface-2)', border: '1px solid var(--border)',
                    borderRadius: 'var(--r-lg)', transition: 'var(--t)', color: 'var(--text)',
                    borderLeft: `2px solid ${pm.color}`,
                  }}
                  onMouseEnter={e => { e.currentTarget.style.borderColor = pm.color; e.currentTarget.style.transform = 'translateY(-1px)' }}
                  onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--border)'; e.currentTarget.style.borderLeft = `2px solid ${pm.color}`; e.currentTarget.style.transform = 'none' }}>
                  <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span style={{ display: 'grid', placeItems: 'center', width: 30, height: 30, borderRadius: 9, background: 'var(--surface-3)', color: pm.color }}>
                      <PIcon size={15} />
                    </span>
                    <strong style={{ fontSize: 13.5 }}>{p.display_name || pm.label || key}</strong>
                  </span>
                  <span style={{ color: 'var(--text-3)', fontSize: 11.5, lineHeight: 1.5 }}>
                    {p.description || pm.focus}
                  </span>
                </button>
              )
            })}
          </div>
        )}
      </Panel>

      {/* Quick actions — every card routes to a real capability */}
      <Panel title="Quick actions" icon={Sparkles}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(230px, 1fr))', gap: 10 }}>
          {QUICK.map(q => (
            <button key={q.label} onClick={() => navigate(q.to)}
              style={{
                display: 'flex', alignItems: 'center', gap: 12, padding: '13px 14px',
                background: 'var(--surface-2)', border: '1px solid var(--border)',
                borderRadius: 'var(--r-lg)', cursor: 'pointer', color: 'var(--text)',
                transition: 'var(--t)', textAlign: 'left',
              }}
              onMouseEnter={e => { e.currentTarget.style.borderColor = 'var(--primary-line)'; e.currentTarget.style.background = 'var(--hover)' }}
              onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--border)'; e.currentTarget.style.background = 'var(--surface-2)' }}>
              <q.icon size={17} style={{ color: 'var(--primary)', flexShrink: 0 }} />
              <span style={{ minWidth: 0, flex: 1 }}>
                <span style={{ display: 'block', fontSize: 13.5, fontWeight: 600 }}>{q.label}</span>
                <span style={{ display: 'block', color: 'var(--text-3)', fontSize: 11.5, marginTop: 2 }}>{q.hint}</span>
              </span>
              <ArrowRight size={14} style={{ color: 'var(--text-3)', flexShrink: 0 }} />
            </button>
          ))}
        </div>
      </Panel>

      {/* Executive brief — real insights summary when available */}
      {summary?.summary && (
        <Panel title="Latest executive brief" icon={Activity}
          actions={<button className="btn btn-outline btn-sm" onClick={() => navigate('/analytics')}>Open analytics</button>}>
          <p style={{ color: 'var(--text-2)', fontSize: 13.5, lineHeight: 1.75, whiteSpace: 'pre-wrap' }}>
            {typeof summary.summary === 'string' ? summary.summary : JSON.stringify(summary.summary)}
          </p>
        </Panel>
      )}
    </div>
  )
}
