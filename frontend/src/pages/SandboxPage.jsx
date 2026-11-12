import { useEffect, useRef, useState } from 'react'
import { useTranslation } from '../i18n/I18nContext'
import { FormattedContent } from './ChatPage'
import { Panel, Loading, Empty } from '../components/ui'
import { Paperclip, Trash2, Upload, Sparkles, User, ChevronDown, ChevronRight } from 'lucide-react'
import {
  getSandboxSession, setSandboxSession, sandboxCreate, sandboxGet, sandboxDocs,
  sandboxIngest, sandboxJob, sandboxWipe, sandboxChat, sandboxChatStatus,
} from '../api'

const ACCEPT = '.csv,.txt,.md,.json,.pdf,.docx,.doc,.pptx,.xlsx,.mp3,.wav,.m4a,.ogg,.webm,.jpg,.jpeg,.png,.webp'
const JOB_LABEL = { queued: 'Queued', processing: 'Processing…', done: 'Done', failed: 'Failed' }

function fmtBytes(n) {
  if (!n) return '0 B'
  if (n < 1024) return `${n} B`
  if (n < 1048576) return `${(n / 1024).toFixed(1)} KB`
  return `${(n / 1048576).toFixed(1)} MB`
}

export default function SandboxPage() {
  const { t } = useTranslation()
  const [phase, setPhase] = useState('loading')
  const [session, setSession] = useState(null)
  const [docs, setDocs] = useState([])
  const [quota, setQuota] = useState(null)
  const [jobs, setJobs] = useState({})
  const [entities, setEntities] = useState({})
  const [openEntities, setOpenEntities] = useState({})
  const [chatId, setChatId] = useState(null)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [confirmWipe, setConfirmWipe] = useState(false)
  const [dragOver, setDragOver] = useState(false)
  const fileRef = useRef(null)
  const chatEndRef = useRef(null)
  const pollRef = useRef({})

  const refresh = async () => {
    try {
      const [s, d] = await Promise.all([sandboxGet(), sandboxDocs()])
      setSession(s.data.session)
      setQuota(s.data.quota)
      setDocs(d.data.docs || [])
      setPhase('workspace')
    } catch (e) {
      const detail = e?.response?.data?.detail
      if (detail === 'sandbox_not_found_or_expired') { setSandboxSession(null); setPhase('entry') }
      else { setError(typeof detail === 'string' ? detail : 'sandbox_load_failed'); setPhase('entry') }
    }
  }

  useEffect(() => {
    const existing = getSandboxSession()
    if (!existing?.session_id) { setPhase('entry'); return }
    refresh()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages, busy])

  const start = async () => {
    setBusy(true); setError('')
    try {
      const { data } = await sandboxCreate()
      setSandboxSession({ session_id: data.session_id, token: data.token, expires_at: data.expires_at })
      setQuota({ docs_used: 0, docs_max: data.quota.docs, bytes_used: 0, bytes_max: data.quota.text_bytes, media_bytes_used: 0, media_bytes_max: data.quota.media_bytes })
      setPhase('workspace'); refresh()
    } catch (e) { setError(e?.response?.data?.detail || 'sandbox_create_failed') }
    finally { setBusy(false) }
  }

  const upload = async (file) => {
    if (!file) return
    setError('')
    try {
      const { data } = await sandboxIngest(file)
      setJobs((j) => ({ ...j, [data.job_id]: { name: file.name, status: 'queued' } }))
      pollJob(data.job_id)
    } catch (e) {
      const d = e?.response?.data?.detail
      setError(typeof d === 'string' ? d : 'upload_failed')
    }
  }

  const pollJob = async (jobId) => {
    try {
      const { data } = await sandboxJob(jobId)
      setJobs((j) => ({ ...j, [jobId]: { ...j[jobId], status: data.status, error: data.error } }))
      if (data.status === 'queued' || data.status === 'processing') {
        pollRef.current[jobId] = setTimeout(() => pollJob(jobId), 2000)
      } else if (data.status === 'done') { refresh() }
    } catch { /* job may be gone after wipe */ }
  }

  const toggleEntities = async (doc) => {
    const id = doc.doc_id
    if (openEntities[id]) { setOpenEntities((o) => ({ ...o, [id]: false })); return }
    setOpenEntities((o) => ({ ...o, [id]: true }))
    if (!entities[id]) {
      try {
        const { data } = await import('../api').then(m => m.sandboxDocEntities(doc.doc_id))
        setEntities((e) => ({ ...e, [id]: data.entities || [] }))
      } catch { setEntities((e) => ({ ...e, [id]: [] })) }
    }
  }

  const send = async (file) => {
    const msg = input.trim()
    if ((!msg && !file) || busy) return
    setInput(''); setBusy(true)
    let content = msg
    if (file) {
      try {
        const { data } = await sandboxIngest(file)
        setJobs((j) => ({ ...j, [data.job_id]: { name: file.name, status: 'queued' } }))
        pollJob(data.job_id)
        content = msg ? `${msg}\n\n[attached: ${file.name}]` : `[attached: ${file.name}] — summarize this file`
      } catch (e) { setError(e?.response?.data?.detail || 'upload_failed'); setBusy(false); return }
    }
    setMessages((m) => [...m, { role: 'user', content }])
    try {
      const { data } = await sandboxChat(content, chatId || null, true)
      const jid = data.job_id || data.id
      if (!chatId) setChatId(data.session_id || jid)
      pollChat(jid)
    } catch (e) {
      setMessages((m) => [...m, { role: 'assistant', content: `⚠️ ${e?.response?.data?.detail || 'chat_failed'}` }])
      setBusy(false)
    }
  }

  const pollChat = async (jobId) => {
    for (let i = 0; i < 60; i++) {
      await new Promise((r) => setTimeout(r, 1500))
      try {
        const { data } = await sandboxChatStatus(jobId)
        const st = data.status
        if (st === 'done' || st === 'completed' || data.answer || data.response) {
          const text = data.answer || data.response || data.result?.answer || JSON.stringify(data).slice(0, 500)
          setMessages((m) => [...m, { role: 'assistant', content: typeof text === 'string' ? text : JSON.stringify(text) }])
          setBusy(false); return
        }
        if (st === 'error' || st === 'failed') {
          setMessages((m) => [...m, { role: 'assistant', content: '⚠️ chat_error' }])
          setBusy(false); return
        }
      } catch { /* keep polling */ }
    }
    setMessages((m) => [...m, { role: 'assistant', content: '⚠️ chat_timeout' }])
    setBusy(false)
  }

  const wipe = async () => {
    setBusy(true)
    try {
      await sandboxWipe()
      Object.values(pollRef.current).forEach(clearTimeout)
      setSandboxSession(null); setDocs([]); setMessages([]); setChatId(null); setJobs({}); setEntities({}); setOpenEntities({})
      setPhase('wiped')
    } catch (e) { setError(e?.response?.data?.detail || 'wipe_failed') }
    finally { setBusy(false); setConfirmWipe(false) }
  }

  if (phase === 'loading') return <Loading />

  if (phase === 'entry' || phase === 'wiped') {
    return (
      <div className="page" style={{ display: 'grid', placeItems: 'center', minHeight: '70vh' }}>
        <Panel title={phase === 'wiped' ? 'Sandbox wiped' : 'Personal Data Sandbox'} style={{ maxWidth: 560, width: '100%' }}>
          <p style={{ color: 'var(--text-2)', lineHeight: 1.6 }}>
            {phase === 'wiped'
              ? 'All your documents, transcripts and vectors have been permanently deleted.'
              : 'Upload your own files and chat with them — answers come only from your uploads, scoped to this browser session and auto-deleted after 90 days. To mix your data with the shared OmniIntelOS knowledge, use Data Hub instead.'}
          </p>
          <ul style={{ color: 'var(--text-2)', paddingLeft: '1.2rem', lineHeight: 1.8 }}>
            <li>{t('sandboxQuotaDocs') || '10 documents'} · {t('sandboxQuotaText') || '25 MB text'} · {t('sandboxQuotaMedia') || '50 MB media'}</li>
            <li>CSV, PDF, DOCX, TXT, audio (mp3/wav/m4a/ogg), images</li>
            <li>{t('sandboxQuotaWipe') || 'One-click wipe — nothing persists'}</li>
          </ul>
          {error && <p style={{ color: 'var(--danger, #f87171)', fontSize: '.85rem' }}>{error}</p>}
          <button className="btn btn-primary" onClick={start} disabled={busy}>
            {busy ? 'Creating…' : phase === 'wiped' ? 'Start a new sandbox' : 'Start sandbox'}
          </button>
        </Panel>
      </div>
    )
  }

  const docsUsed = quota?.docs_used ?? 0
  const docsMax = quota?.docs_max ?? 10
  const pct = (used, max) => Math.min(100, Math.round((used / (max || 1)) * 100))

  return (
    <div className="page" style={{ display: 'grid', gridTemplateColumns: 'minmax(300px, 360px) 1fr', gap: '1rem', alignItems: 'start' }}>
      {/* ── Data panel ─────────────────────────────────────────── */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <Panel title="Your data" icon={Upload} actions={
          <button className="btn btn-ghost btn-sm" onClick={() => setConfirmWipe(true)} disabled={busy} title="Wipe everything">
            <Trash2 size={14} />
          </button>
        }>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginBottom: 12 }}>
            {[['Documents', docsUsed, docsMax], ['Text', quota?.bytes_used || 0, quota?.bytes_max || 1], ['Media', quota?.media_bytes_used || 0, quota?.media_bytes_max || 1]].map(([label, used, max]) => (
              <div key={label}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '.75rem', color: 'var(--text-2)', marginBottom: 3 }}>
                  <span>{label}</span><span>{label === 'Documents' ? `${used}/${max}` : `${fmtBytes(used)} / ${fmtBytes(max)}`}</span>
                </div>
                <div style={{ height: 5, background: 'var(--bg-2, #1b2632)', borderRadius: 3, overflow: 'hidden' }}>
                  <div style={{ width: `${pct(used, max)}%`, height: '100%', background: 'var(--primary, #22d3ee)', transition: 'width .4s' }} />
                </div>
              </div>
            ))}
          </div>

          <div
            onClick={() => fileRef.current?.click()}
            onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
            onDragLeave={() => setDragOver(false)}
            onDrop={(e) => { e.preventDefault(); setDragOver(false); upload(e.dataTransfer.files?.[0]) }}
            style={{
              border: `2px dashed ${dragOver ? 'var(--primary, #22d3ee)' : 'var(--border, #34465a)'}`,
              borderRadius: 10, padding: '1.25rem', textAlign: 'center', cursor: 'pointer',
              background: dragOver ? 'rgba(34,211,238,.06)' : 'transparent', transition: 'all .15s',
            }}
          >
            <Upload size={20} style={{ opacity: .6, marginBottom: 6 }} />
            <div style={{ fontSize: '.85rem', fontWeight: 600 }}>Drop files or click to upload</div>
            <div style={{ fontSize: '.72rem', color: 'var(--text-2)', marginTop: 3 }}>CSV · PDF · DOCX · TXT · audio · images</div>
          </div>
          <input ref={fileRef} type="file" accept={ACCEPT} style={{ display: 'none' }}
            onChange={(e) => { upload(e.target.files?.[0]); e.target.value = '' }} />
          {docsUsed >= docsMax && <p style={{ fontSize: '.75rem', color: 'var(--warning, #f59e0b)', marginTop: 8 }}>Document limit reached — wipe to start over.</p>}
        </Panel>

        {/* jobs */}
        {Object.keys(jobs).length > 0 && (
          <Panel title="Processing">
            {Object.entries(jobs).map(([id, j]) => (
              <div key={id} style={{ display: 'flex', justifyContent: 'space-between', gap: 8, padding: '6px 0', fontSize: '.82rem', borderBottom: '1px solid var(--border, #1b2632)' }}>
                <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{j.name}</span>
                <span style={{ color: j.status === 'failed' ? 'var(--danger,#f87171)' : j.status === 'done' ? 'var(--success,#34d399)' : 'var(--text-2)', flexShrink: 0 }}>
                  {JOB_LABEL[j.status] || j.status}{j.error ? ` — ${j.error}` : ''}
                </span>
              </div>
            ))}
          </Panel>
        )}

        {/* docs */}
        <Panel title={`Documents (${docs.length})`}>
          {docs.length === 0 && <Empty text="No documents yet — upload one to ground the chat." />}
          {docs.map((d) => (
            <div key={d.doc_id} style={{ padding: '8px 0', borderBottom: '1px solid var(--border, #1b2632)' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 8 }}>
                <div style={{ minWidth: 0 }}>
                  <div style={{ fontWeight: 600, fontSize: '.88rem', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{d.title}</div>
                  <div style={{ fontSize: '.72rem', color: 'var(--text-2)' }}>{d.source} · {d.chars} chars</div>
                </div>
                <button className="btn btn-ghost btn-sm" onClick={() => toggleEntities(d)} title="Entities">
                  {openEntities[d.doc_id] ? <ChevronDown size={13} /> : <ChevronRight size={13} />}
                </button>
              </div>
              {openEntities[d.doc_id] && (
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, marginTop: 6 }}>
                  {(entities[d.doc_id] || []).length === 0 && <span style={{ fontSize: '.75rem', color: 'var(--text-2)' }}>No entities extracted yet.</span>}
                  {(entities[d.doc_id] || []).map((en, i) => (
                    <span key={i} style={{ fontSize: '.7rem', background: 'var(--bg-2,#1b2632)', borderRadius: 10, padding: '2px 8px' }}>{en}</span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </Panel>
      </div>

      {/* ── Chat panel (copilot UI) ────────────────────────────── */}
      <Panel title="Chat" icon={Sparkles} style={{ display: 'flex', flexDirection: 'column', minHeight: '70vh' }}>
        <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '0.9rem', padding: '0.5rem 0.25rem' }}>
          {messages.length === 0 && (
            <div style={{ textAlign: 'center', color: 'var(--text-2)', padding: '3rem 1rem' }}>
              <Sparkles size={28} style={{ opacity: .4, marginBottom: 10 }} />
              <p>Ask anything about your uploaded files — answers use only your sandbox data.</p>
            </div>
          )}
          {messages.map((m, i) => (
            <div key={i} className={`chat-message ${m.role === 'user' ? 'user' : 'assistant'}`}>
              <div className="chat-avatar">{m.role === 'user' ? <User size={15} /> : <Sparkles size={15} />}</div>
              <div style={{ minWidth: 0 }}>
                <div className="chat-bubble">
                  {m.role === 'user' ? <div style={{ whiteSpace: 'pre-wrap' }}>{m.content}</div> : <FormattedContent content={m.content} />}
                </div>
              </div>
            </div>
          ))}
          {busy && (
            <div className="chat-message assistant">
              <div className="chat-avatar"><Sparkles size={15} /></div>
              <div className="chat-bubble"><span style={{ opacity: .6 }}>Thinking…</span></div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        <div style={{ display: 'flex', gap: '0.5rem', paddingTop: '0.75rem', borderTop: '1px solid var(--border, #1b2632)' }}>
          <input
            className="input"
            style={{ flex: 1 }}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && send()}
            placeholder="Ask about your documents…"
            disabled={busy}
          />
          <button className="btn btn-ghost btn-sm" onClick={() => fileRef.current?.click()} disabled={busy} title="Attach file">
            <Paperclip size={16} />
          </button>
          <button className="btn btn-primary btn-sm" onClick={() => send()} disabled={busy || (!input.trim())}>Send</button>
        </div>
      </Panel>

      {confirmWipe && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,.6)', display: 'grid', placeItems: 'center', zIndex: 50 }}>
          <Panel title="Wipe sandbox?" style={{ maxWidth: 420 }}>
            <p style={{ color: 'var(--text-2)' }}>
              This permanently deletes {docs.length} document(s), all extracted text, vectors and chat history. Cannot be undone.
            </p>
            <div style={{ display: 'flex', gap: '0.75rem', marginTop: '1rem' }}>
              <button className="btn btn-danger" onClick={wipe} disabled={busy}>Yes, wipe everything</button>
              <button className="btn btn-ghost" onClick={() => setConfirmWipe(false)}>Cancel</button>
            </div>
          </Panel>
        </div>
      )}
    </div>
  )
}
