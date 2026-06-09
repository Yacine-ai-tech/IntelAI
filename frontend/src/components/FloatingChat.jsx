import { useState, useRef, useEffect, useCallback } from 'react'
import { MessageSquare, X, Send, Mic, Volume2, Sparkles, User } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { useTranslation } from '../i18n/I18nContext'
import * as api from '../api'

export default function FloatingChat() {
  const { user } = useAuth()
  const { t } = useTranslation()
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEnd = useRef(null)
  const inputRef = useRef(null)

  const scrollToBottom = useCallback(() => {
    messagesEnd.current?.scrollIntoView({ behavior: 'smooth' })
  }, [])

  useEffect(() => { scrollToBottom() }, [messages, scrollToBottom])

  useEffect(() => {
    if (open && messages.length === 0) {
      setMessages([{
        role: 'assistant',
        content: t('chatWelcome'),
      }])
      setTimeout(() => inputRef.current?.focus(), 200)
    }
  }, [open, user, messages.length, t])

  const send = async (e) => {
    e?.preventDefault()
    if (!input.trim() || loading) return

    const userMsg = { role: 'user', content: input.trim() }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setLoading(true)

    try {
      const res = await api.sendChat(userMsg.content)
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: res.data?.response || res.data?.message || 'No response.',
        audio_url: res.data?.audio_url || null,
      }])
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `Error: ${err.response?.data?.detail || 'Failed to reach assistant.'}`,
      }])
    } finally {
      setLoading(false)
      inputRef.current?.focus()
    }
  }

  const handleKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      send()
    }
  }

  if (!user) return null

  return (
    <>
      {/* Toggle Button */}
      <button
        className="floating-chat-toggle"
        onClick={() => setOpen(!open)}
        title="IntelAI Assistant"
        aria-label="Toggle assistant"
      >
        {open ? <X /> : <MessageSquare />}
      </button>

      {/* Panel */}
      {open && (
        <div className="floating-chat-panel">
          {/* Header */}
          <div className="floating-chat-header">
            <div className="floating-chat-header-left">
              <div className="floating-chat-header-icon">
                <Sparkles size={18} strokeWidth={2.2} />
              </div>
              <div>
                <h4>IntelAI Assistant <span className="status-dot" /></h4>
                <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                  {t('poweredByAI')}
                </span>
              </div>
            </div>
            <button className="btn btn-ghost btn-sm" onClick={() => setOpen(false)} aria-label="Close">
              <X size={16} />
            </button>
          </div>

          {/* Messages */}
          <div className="floating-chat-messages">
            {messages.map((msg, i) => (
              <div key={i} className={`chat-message ${msg.role}`}>
                <div className="chat-avatar">
                  {msg.role === 'user' ? <User size={14} /> : <Sparkles size={14} />}
                </div>
                <div className="chat-bubble">
                  {msg.content}
                  {msg.audio_url && (
                    <audio controls src={msg.audio_url} style={{ marginTop: 8, width: '100%' }} />
                  )}
                </div>
              </div>
            ))}
            {loading && (
              <div className="chat-message assistant">
                <div className="chat-avatar"><Sparkles size={14} /></div>
                <div className="chat-bubble" style={{ opacity: 0.6 }}>
                  <span className="spinner" style={{ display: 'inline-block', width: 14, height: 14, verticalAlign: 'middle', marginRight: 8 }} />
                  {t('chatThinking')}
                </div>
              </div>
            )}
            <div ref={messagesEnd} />
          </div>

          {/* Input */}
          <div className="floating-chat-input-area">
            <input
              ref={inputRef}
              type="text"
              placeholder={t('chatPlaceholder')}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKey}
              disabled={loading}
            />
            <button
              className="chat-send-btn"
              onClick={send}
              disabled={loading || !input.trim()}
              style={{ width: 36, height: 36 }}
            >
              <Send size={16} />
            </button>
          </div>
        </div>
      )}
    </>
  )
}
