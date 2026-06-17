import { useState, useEffect, useRef, useCallback } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useTranslation } from '../i18n/I18nContext'
import { useQuery } from '@tanstack/react-query'
import * as api from '../api'
import { Citations } from '../components/ui'
import {
  Send, Sparkles, User, Plus, History, MessageSquare,
  Crown, DollarSign, Cpu, Settings2, Users, Leaf, ShieldAlert, BarChart3, Bot,
} from 'lucide-react'

// Persona identity (color + icon + suggested prompts) — the persona-routed RAG copilot.
const PERSONA_META = {
  general: { color: 'var(--p-general)', icon: Bot, label: 'Assistant' },
  ceo:     { color: 'var(--p-ceo)', icon: Crown, label: 'CEO' },
  cfo:     { color: 'var(--p-cfo)', icon: DollarSign, label: 'CFO' },
  cto:     { color: 'var(--p-cto)', icon: Cpu, label: 'CTO' },
  coo:     { color: 'var(--p-coo)', icon: Settings2, label: 'COO' },
  chro:    { color: 'var(--p-chro)', icon: Users, label: 'CHRO' },
  esg:     { color: 'var(--p-esg)', icon: Leaf, label: 'ESG' },
  risk:    { color: 'var(--p-risk)', icon: ShieldAlert, label: 'Risk' },
  analyst: { color: 'var(--p-analyst)', icon: BarChart3, label: 'Analyst' },
}
const PROMPTS = {
  general: ['What is our overall business health?', 'Summarize this period’s key metrics', 'What risks should I watch right now?'],
  cfo: ['How is our financial health?', 'Why might gross margin move this quarter?', 'What is our revenue and EBITDA trend?'],
  ceo: ['Give me a board-level snapshot', 'How is MRR and customer growth?', 'Where are our biggest risks?'],
  chro: ['What is our headcount and turnover?', 'How is employee engagement trending?', 'What is our time to hire?'],
  cto: ['What is system uptime and security posture?', 'How is our deployment frequency?', 'Any IT cost concerns?'],
  coo: ['How is on-time delivery and defect rate?', 'What is our capacity utilization?', 'Any operations bottlenecks?'],
  esg: ['What are our carbon emissions?', 'How is our renewable energy share?', 'Summarize our ESG position'],
  risk: ['What recent anomalies should I review?', 'What is our risk score?', 'Where is concentration risk?'],
  analyst: ['Summarize the latest KPIs', 'What changed most this period?', 'Forecast revenue for next quarter'],
}
const PROMPTS_FR = {
  general: ['Quelle est la santé globale de notre activité ?', 'Résume les indicateurs clés de la période', 'Quels risques dois-je surveiller maintenant ?'],
  cfo: ['Comment se porte notre santé financière ?', 'Pourquoi la marge brute pourrait-elle bouger ce trimestre ?', 'Quelle est la tendance du revenu et de l’EBITDA ?'],
  ceo: ['Donne-moi un aperçu pour le conseil', 'Comment évoluent le MRR et la croissance client ?', 'Où sont nos plus grands risques ?'],
  chro: ['Quel est notre effectif et le taux de rotation ?', 'Comment évolue l’engagement des employés ?', 'Quel est notre délai d’embauche ?'],
  cto: ['Quelle est la disponibilité système et la posture de sécurité ?', 'Quelle est notre fréquence de déploiement ?', 'Des préoccupations sur les coûts IT ?'],
  coo: ['Comment se portent la livraison à temps et le taux de défauts ?', 'Quel est notre taux d’utilisation des capacités ?', 'Des goulots d’étranglement opérationnels ?'],
  esg: ['Quelles sont nos émissions de carbone ?', 'Quelle est notre part d’énergie renouvelable ?', 'Résume notre position ESG'],
  risk: ['Quelles anomalies récentes dois-je examiner ?', 'Quel est notre score de risque ?', 'Où est le risque de concentration ?'],
  analyst: ['Résume les derniers indicateurs', 'Qu’est-ce qui a le plus changé cette période ?', 'Prévois le revenu du prochain trimestre'],
}

function MessageBubble({ msg }) {
  const isUser = msg.role === 'user'
  const Icon = isUser ? User : Sparkles
  return (
    <div className={`chat-message ${isUser ? 'user' : 'assistant'}`}>
      <div className="chat-avatar"><Icon size={15} /></div>
      <div style={{ minWidth: 0 }}>
        <div className="chat-bubble" style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</div>
        {!isUser && <Citations sources={msg.sources} />}
      </div>
    </div>
  )
}

export default function ChatPage() {
  const { user } = useAuth()
  const { t, lang } = useTranslation()
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [slowHint, setSlowHint] = useState(false)
  const [persona, setPersona] = useState('')          // '' = auto (role-based)
  const [activeSession, setActiveSession] = useState(null)
  const [status, setStatus] = useState('disconnected')
  const [searchParams, setSearchParams] = useSearchParams()
  const endRef = useRef(null)
  const wsRef = useRef(null)
  const reconnectRef = useRef(null)

  const { data: personas = [] } = useQuery({
    queryKey: ['personas'],
    queryFn: () => api.listPersonas().then(r => r.data?.personas || r.data || []),
    staleTime: 3600_000,
  })
  const { data: sessions = [] } = useQuery({
    queryKey: ['chat-sessions'],
    queryFn: () => api.getChatSessions?.().then(r => r.data?.sessions || []) || [],
    staleTime: 300_000,
  })

  const scroll = useCallback(() => endRef.current?.scrollIntoView({ behavior: 'smooth' }), [])
  useEffect(() => { scroll() }, [messages, loading, scroll])
  // Show a gentle "warming up" hint if a reply takes a while (cold model load / on-demand wake).
  useEffect(() => {
    if (!loading) { setSlowHint(false); return }
    const id = setTimeout(() => setSlowHint(true), 6000)
    return () => clearTimeout(id)
  }, [loading])

  // Prefill from a Dashboard "ask copilot" deep-link (?q=…), then clear it from the URL.
  useEffect(() => {
    const q = searchParams.get('q')
    if (q) { setInput(q); setSearchParams({}, { replace: true }) }
  }, [searchParams, setSearchParams])

  // WebSocket
  useEffect(() => {
    if (!user) return
    const connect = () => {
      const token = localStorage.getItem('access_token')
      if (!token) { setStatus('error'); return }
      // WebSocket can't be proxied by Vercel rewrites, so connect straight to the backend
      // origin when VITE_API_BASE_URL is set (prod); fall back to same-host in dev (Vite proxy).
      const apiBase = import.meta.env.VITE_API_BASE_URL
      const wsBase = apiBase
        ? apiBase.replace(/^http/, 'ws').replace(/\/$/, '')
        : `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}`
      const ws = new WebSocket(`${wsBase}/api/v1/ws/chat`)
      wsRef.current = ws
      ws.onopen = () => { setStatus('connecting'); ws.send(JSON.stringify({ token })) }
      ws.onmessage = (ev) => {
        const d = JSON.parse(ev.data)
        if (d.type === 'connected') setStatus('connected')
        else if (d.type === 'response') {
          setMessages(p => [...p, { role: 'assistant', content: d.response, sources: d.sources || [], persona_used: d.persona_used }])
          setLoading(false)
        } else if (d.type === 'error' || d.error) {
          setMessages(p => [...p, { role: 'assistant', content: `Error: ${d.error || 'request failed'}` }])
          setLoading(false)
        }
      }
      ws.onerror = () => setStatus('error')
      ws.onclose = () => { setStatus('disconnected'); if (user) reconnectRef.current = setTimeout(connect, 3000) }
    }
    connect()
    return () => { wsRef.current?.close(); clearTimeout(reconnectRef.current) }
  }, [user])

  const send = (text) => {
    const q = (text ?? input).trim()
    if (!q || loading) return
    setMessages(p => [...p, { role: 'user', content: q }])
    setInput(''); setLoading(true)
    const ws = wsRef.current
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ message: q, persona: persona || undefined, session_id: activeSession || undefined }))
    } else {
      api.sendChat(q, persona || null, activeSession, '')
        .then(r => setMessages(p => [...p, { role: 'assistant', content: r.data.response || 'No response.', sources: r.data.sources || [] }]))
        .catch(e => setMessages(p => [...p, { role: 'assistant', content: `Error: ${e.response?.data?.detail || 'request failed'}` }]))
        .finally(() => setLoading(false))
    }
  }

  const onSubmit = (e) => { e.preventDefault(); send() }
  const onKey = (e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send() } }
  const newChat = () => { setActiveSession(null); setMessages([]) }
  const loadSession = async (id) => {
    try {
      const r = await api.getChatMessages?.(id)
      setMessages((r?.data?.messages || []).map(m => ({
        role: m.role || (m.is_user ? 'user' : 'assistant'),
        content: m.content || m.message || m.response, sources: m.sources || [],
      })))
      setActiveSession(id)
    } catch { /* ignore */ }
  }

  const activeKey = persona || 'general'
  const promptSet = lang === 'fr' ? PROMPTS_FR : PROMPTS
  const prompts = promptSet[activeKey] || promptSet.general
  const dotColor = status === 'connected' ? 'var(--ok)' : status === 'connecting' ? 'var(--warn)' : 'var(--bad)'

  return (
    <div className="chat-layout">
      <aside className="chat-history-panel">
        <div className="chat-history-header" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: 7, fontWeight: 600, fontSize: '.9rem' }}>
            <History size={15} /> {t('history') || 'History'}
          </span>
          <button className="btn btn-primary btn-sm" onClick={newChat}><Plus size={14} /> {t('newChat') || 'New'}</button>
        </div>
        <div className="chat-history-list">
          {sessions.length ? sessions.map(s => {
            const id = s.id || s.session_id
            return (
              <div key={id} className={`chat-history-item${activeSession === id ? ' active' : ''}`} onClick={() => loadSession(id)}>
                <MessageSquare size={13} style={{ marginRight: 6, verticalAlign: 'middle', opacity: .6 }} />
                {s.title || `Chat ${String(id).slice(0, 6)}`}
              </div>
            )
          }) : <div style={{ padding: '18px 12px', textAlign: 'center', color: 'var(--text-3)', fontSize: '.8rem' }}>{t('noHistory') || 'No conversations yet'}</div>}
        </div>
      </aside>

      <section className="chat-main">
        <div className="chat-header">
          <span className="page-title" style={{ fontSize: '1.05rem' }}><Sparkles size={18} /> Copilot</span>
          <span className="badge" style={{ gap: 6 }}><span className="status-dot" style={{ background: dotColor, boxShadow: `0 0 0 3px color-mix(in srgb, ${dotColor} 20%, transparent)` }} />{status}</span>
          <div className="topbar-spacer" />
          <div className="persona-row">
            <span className="persona-chip" onClick={() => setPersona('')} style={{ '--pc': 'var(--p-general)' }}
              {...(persona === '' ? { className: 'persona-chip active' } : {})}>
              <span className="dot" /> Auto
            </span>
            {personas.map(p => {
              const key = p.id || p.persona_id || p.name
              const pm = PERSONA_META[key] || PERSONA_META.general
              const PIcon = pm.icon
              return (
                <span key={key} className={`persona-chip${persona === key ? ' active' : ''}`} style={{ '--pc': pm.color }} onClick={() => setPersona(key)}>
                  <PIcon size={13} /> {p.display_name || pm.label || key}
                </span>
              )
            })}
          </div>
        </div>

        <div className="chat-messages">
          {messages.length === 0 && !loading && (
            <div className="copilot-empty">
              <div className="copilot-emblem"><Sparkles size={32} /></div>
              <h2 className="display" style={{ fontSize: '1.5rem' }}>{(t('appName') || 'IntelAI')} Copilot</h2>
              <p style={{ color: 'var(--text-2)', marginTop: 8 }}>
                Persona-aware analytics over your live KPIs — grounded answers with sources.
              </p>
              <div className="prompt-grid">
                {prompts.map((p, i) => (
                  <div key={i} className="prompt-card" onClick={() => send(p)}>{p}</div>
                ))}
              </div>
            </div>
          )}
          {messages.map((m, i) => <MessageBubble key={i} msg={m} />)}
          {loading && (
            <div className="chat-message assistant">
              <div className="chat-avatar"><Sparkles size={15} /></div>
              <div className="chat-bubble">
                <span className="typing-dot" /> <span className="typing-dot" style={{ animationDelay: '.2s' }} /> <span className="typing-dot" style={{ animationDelay: '.4s' }} />
                {slowHint && <div style={{ marginTop: 8, fontSize: '.78rem', color: 'var(--text-3)' }}>{t('warmingHint') || 'Warming up the copilot — the first reply can take ~30s, then it’s fast.'}</div>}
              </div>
            </div>
          )}
          <div ref={endRef} />
        </div>

        <form className="chat-input-bar" onSubmit={onSubmit}>
          <div className="chat-input-wrap">
            <textarea
              className="chat-input" rows={1} value={input}
              placeholder={status === 'connected' ? (t('chatPlaceholder') || 'Ask about your KPIs, risks, forecasts…') : 'Connecting…'}
              onChange={e => setInput(e.target.value)} onKeyDown={onKey}
            />
            <button type="submit" className="chat-send-btn" disabled={loading || !input.trim()}><Send size={18} /></button>
          </div>
        </form>
      </section>
    </div>
  )
}
