import { useState, useEffect, useRef, useCallback } from 'react'
import { useAuth } from '../context/AuthContext'
import { useTranslation } from '../i18n/I18nContext'
import * as api from '../api'
import {
  MessageSquare, Send, Sparkles, User, Trash2, Plus,
  Volume2, History, ChevronRight, Bot
} from 'lucide-react'

function MessageBubble({ msg }) {
  const isUser = msg.role === 'user'
  return (
    <div className={`chat-message ${isUser ? 'user' : 'assistant'}`}>
      <div className="chat-avatar">
        {isUser ? <User size={14} /> : <Sparkles size={14} />}
      </div>
      <div className="chat-bubble">
        {msg.content}
        {msg.audio_url && (
          <audio controls src={msg.audio_url} style={{ marginTop: 8, width: '100%' }} />
        )}
        {msg.sources && msg.sources.length > 0 && (
          <div style={{ marginTop: 10, paddingTop: 8, borderTop: '1px solid var(--border)', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            {msg.sources.join(', ')}
          </div>
        )}
      </div>
    </div>
  )
}

export default function ChatPage() {
  const { user } = useAuth()
  const { t } = useTranslation()
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [personas, setPersonas] = useState([])
  const [selectedPersona, setSelectedPersona] = useState('')
  const [ttsEnabled, setTtsEnabled] = useState(false)
  const [sessions, setSessions] = useState([])
  const [activeSession, setActiveSession] = useState(null)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [])

  useEffect(() => { scrollToBottom() }, [messages, scrollToBottom])

  useEffect(() => {
    api.listPersonas()
      .then(res => {
        const list = res.data?.personas || res.data || []
        setPersonas(list)
      })
      .catch(() => setPersonas([]))

    // Load sessions
    api.getChatSessions?.()
      .then(res => setSessions(res.data?.sessions || []))
      .catch(() => {})
  }, [])

  useEffect(() => {
    setMessages([{
      role: 'assistant',
      content: t('chatWelcome'),
    }])
  }, [user, t])

  const loadSession = async (sessionId) => {
    try {
      const res = await api.getChatMessages?.(sessionId)
      const msgs = res?.data?.messages || []
      setMessages(msgs.map(m => ({
        role: m.role || (m.is_user ? 'user' : 'assistant'),
        content: m.content || m.message || m.response,
      })))
      setActiveSession(sessionId)
    } catch {
      // silent
    }
  }

  const newSession = () => {
    setActiveSession(null)
    setMessages([{
      role: 'assistant',
      content: t('chatNew'),
    }])
  }

  const sendMessage = async (e) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userMsg = { role: 'user', content: input.trim() }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setLoading(true)

    try {
      const res = await api.sendChat(
        userMsg.content,
        selectedPersona || null,
        activeSession,
        '',
      )

      const data = res.data
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.response || data.message || 'No response received.',
        audio_url: data.audio_url || null,
        sources: data.sources || null,
      }])
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `Error: ${err.response?.data?.detail || 'Failed to get response. Please try again.'}`,
      }])
    } finally {
      setLoading(false)
      inputRef.current?.focus()
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage(e)
    }
  }

  const clearChat = () => {
    setMessages([{
      role: 'assistant',
      content: t('chatCleared'),
    }])
  }

  return (
    <div className="chat-layout">
      {/* History Panel */}
      <div className="chat-history-panel">
        <div className="chat-history-header">
          <h3><History size={14} style={{ marginRight: 6, verticalAlign: 'middle' }} /> {t('history')}</h3>
          <button className="btn btn-ghost btn-sm" onClick={newSession} title={t('newChat')}>
            <Plus size={15} />
          </button>
        </div>
        <div className="chat-history-list">
          {sessions.length > 0 ? sessions.map(s => (
            <button
              key={s.id || s.session_id}
              className={`chat-session-item${activeSession === (s.id || s.session_id) ? ' active' : ''}`}
              onClick={() => loadSession(s.id || s.session_id)}
            >
              <MessageSquare size={14} />
              <span className="truncate">{s.title || s.preview || `Session ${(s.id || s.session_id).slice(0, 8)}`}</span>
            </button>
          )) : (
            <div style={{ padding: '20px 12px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
              {t('noHistory')}
            </div>
          )}
        </div>
      </div>

      {/* Main Chat */}
      <div className="chat-main">
        <div className="chat-header">
          <div className="page-title" style={{ fontSize: '1.1rem' }}>
            <Bot size={20} /> {t('aiAssistant')}
          </div>
          <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
            {personas.length > 0 && (
              <select
                className="form-input"
                style={{ width: 170, padding: '6px 10px', fontSize: '0.78rem' }}
                value={selectedPersona}
                onChange={e => setSelectedPersona(e.target.value)}
              >
                <option value="">{t('autoRoleBased')}</option>
                {personas.map(p => (
                  <option key={p.id || p.persona_id} value={p.id || p.persona_id}>
                    {p.display_name || p.name}
                  </option>
                ))}
              </select>
            )}
            <label style={{ display: 'flex', alignItems: 'center', gap: 5, fontSize: '0.78rem', cursor: 'pointer', color: 'var(--text-secondary)' }}>
              <input type="checkbox" checked={ttsEnabled} onChange={e => setTtsEnabled(e.target.checked)} />
              <Volume2 size={14} /> TTS
            </label>
            <button className="btn btn-ghost btn-sm" onClick={clearChat} title={t('clearChat')}>
              <Trash2 size={14} />
            </button>
          </div>
        </div>

        <div className="chat-messages">
          {messages.map((msg, i) => (
            <MessageBubble key={i} msg={msg} />
          ))}
          {loading && (
            <div className="chat-message assistant">
              <div className="chat-avatar"><Sparkles size={14} /></div>
              <div className="chat-bubble" style={{ opacity: 0.6 }}>
                <span className="spinner" style={{ display: 'inline-block', width: 14, height: 14, verticalAlign: 'middle', marginRight: 8 }} />
                Thinking...
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={sendMessage} className="chat-input-bar">
          <input
            ref={inputRef}
            type="text"
            className="chat-input"
            placeholder={t('chatPlaceholder')}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={loading}
          />
          <button type="submit" className="chat-send-btn" disabled={loading || !input.trim()}>
            <Send size={18} />
          </button>
        </form>
      </div>
    </div>
  )
}
