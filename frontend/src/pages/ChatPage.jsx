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
  Info, MoreHorizontal, ArrowUpRight, ArrowDownRight, PanelLeftClose, PanelRightClose, PanelLeft, PanelRight, X, Network
} from 'lucide-react'
import * as Recharts from "recharts";
const { AreaChart, Area, YAxis, ResponsiveContainer } = Recharts;

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

// Inline markdown → React nodes: **bold**, __bold__, *italic*, _italic_, `code`, [text](url).
function renderInline(text, keyBase = 'i') {
  if (text == null) return null
  const s = String(text)
  const re = /(\*\*([^*]+)\*\*|__([^_]+)__|`([^`]+)`|\*([^*\s][^*]*?)\*|(?<![A-Za-z0-9])_([^_\s][^_]*?)_(?![A-Za-z0-9])|\[([^\]]+)\]\((https?:[^)]+)\))/g
  const nodes = []
  let last = 0, m, k = 0
  while ((m = re.exec(s)) !== null) {
    if (m.index > last) nodes.push(s.slice(last, m.index))
    if (m[2] != null) nodes.push(<strong key={`${keyBase}-${k++}`}>{m[2]}</strong>)
    else if (m[3] != null) nodes.push(<strong key={`${keyBase}-${k++}`}>{m[3]}</strong>)
    else if (m[4] != null) nodes.push(<code key={`${keyBase}-${k++}`} className="msg-code">{m[4]}</code>)
    else if (m[5] != null) nodes.push(<em key={`${keyBase}-${k++}`}>{m[5]}</em>)
    else if (m[6] != null) nodes.push(<em key={`${keyBase}-${k++}`}>{m[6]}</em>)
    else if (m[7] != null) nodes.push(<a key={`${keyBase}-${k++}`} href={m[8]} target="_blank" rel="noreferrer">{m[7]}</a>)
    last = re.lastIndex
  }
  if (last < s.length) nodes.push(s.slice(last))
  return nodes.length ? nodes : s
}

// Block-level markdown parser: headings, lists (ordered/unordered, with inline formatting),
// fenced code, blockquotes, tables and paragraphs. Robust to unmatched symbols.
function parseBlocks(content) {
  const lines = String(content || '').replace(/\r\n/g, '\n').split('\n')
  const blocks = []
  let list = null, code = null
  const flush = () => { if (list) { blocks.push(list); list = null } }
  for (let i = 0; i < lines.length; i++) {
    const t = lines[i].trim()
    if (t.startsWith('```')) {
      if (code) { blocks.push({ type: 'code', text: code.join('\n') }); code = null }
      else { flush(); code = [] }
      continue
    }
    if (code) { code.push(lines[i]); continue }
    if (!t) { flush(); continue }
    if (/^(-{3,}|\*{3,}|_{3,})$/.test(t)) { flush(); continue }           // hr
    const h = t.match(/^(#{1,6})\s+(.*)$/)
    if (h) { flush(); blocks.push({ type: `h${Math.min(h[1].length, 3)}`, text: h[2] }); continue }
    if (/^\|.*\|$/.test(t)) {                                             // table
      flush(); const rows = []; let j = i
      while (j < lines.length && /^\|.*\|$/.test(lines[j].trim())) { rows.push(lines[j].trim()); j++ }
      const parsed = rows.filter(r => !/^\|[\s:|-]+\|$/.test(r))
        .map(r => r.replace(/^\||\|$/g, '').split('|').map(c => c.trim()))
      if (parsed.length) blocks.push({ type: 'table', rows: parsed })
      i = j - 1; continue
    }
    if (t.startsWith('>')) { flush(); blocks.push({ type: 'quote', text: t.replace(/^>\s?/, '') }); continue }
    let m = t.match(/^[-*•]\s+(.*)$/)
    if (m) { if (!list || list.ordered) { flush(); list = { type: 'list', ordered: false, items: [] } } list.items.push(m[1]); continue }
    m = t.match(/^\d+[.)]\s+(.*)$/)
    if (m) { if (!list || !list.ordered) { flush(); list = { type: 'list', ordered: true, items: [] } } list.items.push(m[1]); continue }
    flush(); blocks.push({ type: 'p', text: t })
  }
  flush(); if (code) blocks.push({ type: 'code', text: code.join('\n') })
  return blocks
}

// KPI block rendered as an accent pill (from server answer-block structuring)
function KpiBlock({ label, value }) {
  return (
    <div className="msg-kpi-block">
      <span className="msg-kpi-label">{label}</span>
      <span className="msg-kpi-value">{value}</span>
    </div>
  )
}

// Prefer server-sent blocks[] (structured by _structure_answer); fall back to client-side parsing.
export function FormattedContent({ content, blocks: serverBlocks }) {
  // If the server sent typed blocks use them directly; otherwise parse client-side
  const blocks = (serverBlocks && serverBlocks.length > 0) ? serverBlocks : parseBlocks(content)

  const renderBlock = (b, idx) => {
    // Server block types
    if (b.type === 'heading') {
      const Tag = b.level === 1 ? 'h3' : b.level === 2 ? 'h4' : 'h5'
      const cls = b.level === 1 ? 'msg-h1' : b.level === 2 ? 'msg-h2' : 'msg-h3'
      return <Tag key={idx} className={cls}>{renderInline(b.content, `hd${idx}`)}</Tag>
    }
    if (b.type === 'kpi') return <KpiBlock key={idx} label={b.label} value={b.value} />
    if (b.type === 'quote') return <blockquote key={idx} className="msg-quote">{renderInline(b.content, `q${idx}`)}</blockquote>
    if (b.type === 'code') return <pre key={idx} className="msg-pre"><code>{b.content}</code></pre>
    if (b.type === 'text' && b.content) return <p key={idx} className="msg-text">{renderInline(b.content, `p${idx}`)}</p>
    if (b.type === 'list') {
      const Tag = b.ordered ? 'ol' : 'ul'
      return (
        <Tag key={idx} className={b.ordered ? 'msg-numbered-list' : 'msg-list'}>
          {b.items.map((it, i) => <li key={i}>{renderInline(it, `l${idx}-${i}`)}</li>)}
        </Tag>
      )
    }
    // Client-side parse block types (parseBlocks output)
    if (b.type === 'h1') return <h3 key={idx} className="msg-h1">{renderInline(b.text, `h1${idx}`)}</h3>
    if (b.type === 'h2') return <h4 key={idx} className="msg-h2">{renderInline(b.text, `h2${idx}`)}</h4>
    if (b.type === 'h3') return <h5 key={idx} className="msg-h3">{renderInline(b.text, `h3${idx}`)}</h5>
    if (b.type === 'code') return <pre key={idx} className="msg-pre"><code>{b.text}</code></pre>
    if (b.type === 'quote') return <blockquote key={idx} className="msg-quote">{renderInline(b.text, `q${idx}`)}</blockquote>
    if (b.type === 'table') return (
      <div key={idx} className="msg-table-wrap">
        <table className="table msg-table"><tbody>
          {b.rows.map((r, ri) => (
            <tr key={ri}>{r.map((c, ci) => ri === 0
              ? <th key={ci}>{renderInline(c, `t${idx}-${ri}-${ci}`)}</th>
              : <td key={ci}>{renderInline(c, `t${idx}-${ri}-${ci}`)}</td>)}</tr>
          ))}
        </tbody></table>
      </div>
    )
    if (b.type === 'list') {
      const Tag = b.ordered ? 'ol' : 'ul'
      return (
        <Tag key={idx} className={b.ordered ? 'msg-numbered-list' : 'msg-list'}>
          {b.items.map((it, i) => <li key={i}>{renderInline(it, `l${idx}-${i}`)}</li>)}
        </Tag>
      )
    }
    return <p key={idx} className="msg-text">{renderInline(b.text || b.content || '', `p${idx}`)}</p>
  }

  return (
    <div className="formatted-message">
      {blocks.map((b, idx) => renderBlock(b, idx))}
    </div>
  )
}

function MessageBubble({ msg }) {
  const { t } = useTranslation()
  const isUser = msg.role === 'user'
  const Icon = isUser ? User : Sparkles
  return (
    <div className={`chat-message ${isUser ? 'user' : 'assistant'}`}>
      <div className="chat-avatar"><Icon size={15} /></div>
      <div style={{ minWidth: 0 }}>
        <div className="chat-bubble">
          {isUser ? (
            <div style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</div>
          ) : (
            <FormattedContent content={msg.content} blocks={msg.blocks} />
          )}
        </div>
        {!isUser && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap', marginTop: 8 }}>
            <Citations sources={msg.sources} />
            {msg.sources?.length > 0 && (
              <a href={`/knowledge-graph?q=${encodeURIComponent(msg.query || 'knowledge')}`} target="_blank" rel="noreferrer" 
                 className="btn btn-ghost btn-sm" style={{ padding: '2px 8px', fontSize: '.75rem', height: '24px' }} title={t('visualizeGraphRAG') || 'Visualize GraphRAG Entities'}>
                <Network size={12} style={{ marginRight: 4 }} /> View Graph
              </a>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default function ChatPage({ isWidget = false, initialQuery = '' }) {
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
  const [showHistory, setShowHistory] = useState(false)
  const [showKPI, setShowKPI] = useState(false)
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
    if (isWidget) {
      if (initialQuery) {
        setInput(initialQuery)
      }
      return
    }
    const pp = searchParams.get('persona')
    if (pp && PERSONA_META[pp]) { setPersona(pp); searchParams.delete('persona'); setSearchParams(searchParams, { replace: true }) }
    const q = searchParams.get('q')
    if (q) { setInput(q); setSearchParams({}, { replace: true }) }
  }, [searchParams, setSearchParams, isWidget, initialQuery])

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
          setMessages(p => [...p, {
            role: 'assistant',
            content: d.response,
            sources: d.sources || [],
            blocks: d.blocks || [],
            persona_used: d.persona_used,
          }])
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
    setMessages(p => [...p, { role: 'user', content: q, query: q }])
    setInput(''); setLoading(true)
    const ws = wsRef.current
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ message: q, persona: persona || undefined, session_id: activeSession || undefined, language: lang }))
    } else {
      api.sendChat(q, persona || null, activeSession, '', lang)
        .then(r => setMessages(p => [...p, {
          role: 'assistant',
          content: r.data.response || 'No response.',
          sources: r.data.sources || [],
          blocks: r.data.blocks || [],
          query: q,
        }]))
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
    <div className="chat-layout" style={{ position: 'relative', overflow: 'hidden' }}>
      {!isWidget && (
        <aside className={`chat-history-panel${showHistory ? ' mobile-open' : ' collapsed'}`}>
          <div className="chat-history-header" style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: 7, fontWeight: 600, fontSize: '.9rem', overflow: 'hidden' }}>
                <History size={15} style={{ flexShrink: 0 }} /> 
                <span className="truncate" title={t('history') || 'History'}>{t('history') || 'History'}</span>
              </span>
              <button className="btn btn-ghost btn-icon mobile-only" onClick={() => setShowHistory(false)}><X size={14} /></button>
            </div>
            <button className="btn btn-primary btn-sm" onClick={newChat} style={{ width: '100%', justifyContent: 'center' }}>
              <Plus size={14} style={{ flexShrink: 0 }} /> 
              <span className="truncate" title={t('newChat') || 'New'}>{t('newChat') || 'New'}</span>
            </button>
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
      )}

      <section className="chat-main" style={{ zIndex: 1 }}>
        <div className="chat-header">
          {!isWidget && (
            <button className="btn btn-ghost btn-icon" onClick={() => setShowHistory(!showHistory)} style={{ marginRight: 6 }}>
              {showHistory ? <PanelLeftClose size={18} /> : <PanelLeft size={18} />}
            </button>
          )}
          <span className="page-title" style={{ fontSize: '1.05rem' }}><Sparkles size={18} /> Copilot</span>
          <span className="badge" style={{ gap: 6 }}><span className="status-dot" style={{ background: dotColor, boxShadow: `0 0 0 3px color-mix(in srgb, ${dotColor} 20%, transparent)` }} />{status}</span>
          <div className="topbar-spacer" />
          {!isWidget && (
            <>
              <div className="persona-row">
                {user?.role === 'admin' ? (
                  <>
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
                  </>
                ) : (
                  (() => {
                    const rolePersonaMap = {
                      "admin": "ceo", "ceo": "ceo", "cfo": "cfo", "cto": "cto",
                      "coo": "coo", "chro": "chro", "hr": "chro", "esg": "esg", "risk": "risk",
                      "analyst": "analyst", "viewer": "general", "operations": "coo", "it": "cto",
                      "custom": "general",
                    }
                    const allowedForRole = rolePersonaMap[user?.role] || 'general'
                    const pm = PERSONA_META[allowedForRole] || PERSONA_META.general
                    const PIcon = pm.icon
                    return (
                      <span className="persona-chip active" style={{ '--pc': pm.color, cursor: 'default' }}>
                        <PIcon size={13} /> {pm.label || allowedForRole}
                      </span>
                    )
                  })()
                )}
              </div>
              <button className="btn btn-ghost btn-icon" onClick={() => setShowKPI(!showKPI)} style={{ marginLeft: 6 }}>
                {showKPI ? <PanelRightClose size={18} /> : <PanelRight size={18} />}
              </button>
            </>
          )}
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

      <ChatKPIRail showKPI={showKPI} setShowKPI={setShowKPI} />
    </div>
  )
}

/* ── Right-side KPI rail (matches og-image thumbnail) ────────── */
function ChatKPIRail({ showKPI, setShowKPI }) {
  const { t } = useTranslation()
  const { data: kpis = [] } = useQuery({
    queryKey: ['kpis'], queryFn: () => api.getKPIs().then(r => r.data?.metrics || []),
    staleTime: 300_000, retry: 1,
  })

  // Build per-metric history and pick 3 representative KPIs
  const hist = {}
  kpis.forEach(k => {
    const name = k.metric || 'Unknown'
    ;(hist[name] = hist[name] || []).push({ period: k.period, value: k.value })
  })
  Object.keys(hist).forEach(n => {
    hist[n].sort((a, b) => (a.period || '').localeCompare(b.period || ''))
    hist[n] = hist[n].slice(-6)
  })

  const seen = new Set()
  const unique = kpis.filter(k => {
    const n = k.metric
    if (seen.has(n)) return false; seen.add(n); return true
  })

  // Pick representative KPIs for the rail
  const picks = [
    unique.find(k => /revenue/i.test(k.metric)),
    unique.find(k => /ebitda|margin/i.test(k.metric)),
    unique.find(k => /cost|opex/i.test(k.metric)),
  ].filter(Boolean).slice(0, 3)
  if (picks.length === 0) picks.push(...unique.slice(0, 3))

  const fmt = (v) => {
    if (v == null || isNaN(v)) return '—'
    const a = Math.abs(v)
    if (a >= 1e9) return '$' + (v / 1e9).toFixed(2) + 'B'
    if (a >= 1e6) return '$' + (v / 1e6).toFixed(1) + 'M'
    if (a >= 1e3) return '$' + (v / 1e3).toFixed(1) + 'K'
    if (a < 1) return (v * 100).toFixed(1) + '%'
    return v.toFixed(1)
  }

  return (
    <aside className={`chat-kpi-rail${showKPI ? ' mobile-open' : ' collapsed'}`}>
      <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 4 }} className="mobile-only">
        <button className="btn btn-ghost btn-icon" onClick={() => setShowKPI(false)}><X size={14} /></button>
      </div>
      {picks.map((k, i) => {
        const name = k.metric
        const data = hist[name] || []
        // No change_pct field from the API — derive it from this metric's own history.
        const change = data.length >= 2 && data[data.length - 2].value
          ? ((data[data.length - 1].value - data[data.length - 2].value) / Math.abs(data[data.length - 2].value)) * 100
          : undefined
        const up = (change ?? 0) >= 0
        return (
          <div key={i} className="rail-card">
            <div className="rail-card-header">
              <span className="rail-card-title"><Info size={14} /> {name}</span>
              <span className="rail-card-period">{t('latest') || 'Latest'}</span>
            </div>
            <div className="rail-card-value">{fmt(k.value)}</div>
            {change != null && (
              <div className={`rail-card-change ${up ? 'up' : 'down'}`}>
                {up ? <ArrowUpRight size={12} /> : <ArrowDownRight size={12} />}
                {' '}{Math.abs(change).toFixed(1)}%
              </div>
            )}
            {data.length >= 2 && (
              <div style={{ height: 64, marginTop: 10 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={data}>
                    <defs>
                      <linearGradient id={`railG${i}`} x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#22d3ee" stopOpacity={0.4} />
                        <stop offset="100%" stopColor="#22d3ee" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <YAxis hide domain={['dataMin', 'dataMax']} />
                    <Area type="monotone" dataKey="value" stroke="#22d3ee" strokeWidth={2} fill={`url(#railG${i})`} dot={false} />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>
        )
      })}
    </aside>
  )
}
