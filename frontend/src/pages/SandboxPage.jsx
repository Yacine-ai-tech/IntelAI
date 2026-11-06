import { useEffect, useRef, useState } from 'react'
import { useTranslation } from '../i18n/I18nContext'
import {
  getSandboxSession, setSandboxSession, sandboxCreate, sandboxGet, sandboxDocs,
  sandboxIngest, sandboxJob, sandboxWipe, sandboxChat, sandboxChatStatus,
} from '../api'

const ACCEPT = '.csv,.txt,.md,.json,.pdf,.docx,.doc,.pptx,.xlsx,.mp3,.wav,.m4a,.ogg,.webm,.jpg,.jpeg,.png,.webp'

function fmtBytes(n) {
  if (!n) return '0 B'
  if (n < 1024) return `${n} B`
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`
  return `${(n / 1024 / 1024).toFixed(1)} MB`
}

export default function SandboxPage() {
  const { t } = useTranslation()
  const [phase, setPhase] = useState('loading') // loading | entry | workspace | wiped
  const [session, setSession] = useState(null)
  const [docs, setDocs] = useState([])
  const [quota, setQuota] = useState(null)
  const [jobs, setJobs] = useState({})
  const [chatId, setChatId] = useState(null)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [confirmWipe, setConfirmWipe] = useState(false)
  const [sandboxOnly, setSandboxOnly] = useState(true) // "my data only" — exclude OmniIntelOS global corpus
  const fileRef = useRef(null)
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
      if (detail === 'sandbox_not_found_or_expired') {
        setSandboxSession(null)
        setPhase('entry')
      } else {
        setError(typeof detail === 'string' ? detail : 'sandbox_load_failed')
        setPhase('entry')
      }
    }
  }

  useEffect(() => {
    const existing = getSandboxSession()
    if (!existing?.session_id) { setPhase('entry'); return }
    refresh()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const start = async () => {
    setBusy(true); setError('')
    try {
      const { data } = await sandboxCreate()
      setSandboxSession({ session_id: data.session_id, token: data.token, expires_at: data.expires_at })
      setQuota({ docs_used: 0, docs_max: data.quota.docs, bytes_used: 0, bytes_max: data.quota.text_bytes, media_bytes_used: 0, media_bytes_max: data.quota.media_bytes })
      setPhase('workspace')
      refresh()
    } catch (e) {
      setError(e?.response?.data?.detail || 'sandbox_create_failed')
    } finally { setBusy(false) }
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
      } else if (data.status === 'done') {
        refresh()
      }
    } catch { /* job may be gone after wipe */ }
  }

  const send = async () => {
    const msg = input.trim()
    if (!msg || busy) return
    setInput(''); setBusy(true)
    setMessages((m) => [...m, { role: 'user', content: msg }])
    try {
      if (!chatId) {
        const { data } = await sandboxChat(msg, null, sandboxOnly)
        setChatId(data.session_id || data.job_id)
        pollChat(data.job_id || data.id, msg)
      } else {
        const { data } = await sandboxChat(msg, chatId, sandboxOnly)
        pollChat(data.job_id || data.id, msg)
      }
    } catch (e) {
      setMessages((m) => [...m, { role: 'assistant', content: `⚠️ ${e?.response?.data?.detail || 'chat_failed'}` }])
      setBusy(false)
    }
  }

  const pollChat = async (jobId, _msg) => {
    // /chat/{job_id} returns the completed turn; poll until done.
    for (let i = 0; i < 60; i++) {
      await new Promise((r) => setTimeout(r, 1500))
      try {
        const { data } = await sandboxChatStatus(jobId)
        const st = data.status
        if (st === 'done' || st === 'completed' || data.answer || data.response) {
          const text = data.answer || data.response || data.result?.answer || JSON.stringify(data).slice(0, 500)
          setMessages((m) => [...m, { role: 'assistant', content: typeof text === 'string' ? text : JSON.stringify(text) }])
          setBusy(false)
          return
        }
        if (st === 'error' || st === 'failed') {
          setMessages((m) => [...m, { role: 'assistant', content: '⚠️ chat_error' }])
          setBusy(false)
          return
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
      setSandboxSession(null)
      setDocs([]); setMessages([]); setChatId(null); setJobs({})
      setPhase('wiped')
    } catch (e) {
      setError(e?.response?.data?.detail || 'wipe_failed')
    } finally { setBusy(false); setConfirmWipe(false) }
  }

  if (phase === 'loading') return <div style={S.center}>{t('sandboxLoading') || 'Loading…'}</div>

  if (phase === 'entry' || phase === 'wiped') {
    return (
      <div style={S.page}>
        <div style={S.card}>
          <h1 style={S.h1}>{phase === 'wiped' ? (t('sandboxWipedTitle') || 'Sandbox wiped') : (t('sandboxTitle') || 'Personal Data Sandbox')}</h1>
          <p style={S.p}>
            {phase === 'wiped'
              ? (t('sandboxWipedMsg') || 'All your documents, transcripts and vectors have been permanently deleted.')
              : (t('sandboxIntro') || 'Upload your own CSVs, documents, audio or images — the copilot answers from OmniIntelOS knowledge plus your private files. Everything is scoped to this browser session and auto-deleted after 90 days.')}
          </p>
          <ul style={S.list}>
            <li>{t('sandboxQuotaDocs') || '10 documents'} · {t('sandboxQuotaText') || '25 MB text'} · {t('sandboxQuotaMedia') || '50 MB media'}</li>
            <li>CSV, PDF, DOCX, TXT, audio (mp3/wav/m4a/ogg), images</li>
            <li>{t('sandboxQuotaWipe') || 'One-click wipe — nothing persists'}</li>
          </ul>
          {error && <p style={S.err}>{error}</p>}
          <button style={S.btn} onClick={start} disabled={busy}>
            {busy ? (t('sandboxCreating') || 'Creating…') : phase === 'wiped' ? (t('sandboxNew') || 'Start a new sandbox') : (t('sandboxStart') || 'Start sandbox')}
          </button>
        </div>
      </div>
    )
  }

  const docsUsed = quota?.docs_used ?? 0
  const docsMax = quota?.docs_max ?? 10

  return (
    <div style={S.page}>
      <div style={S.banner}>{t('sandboxBanner') || 'Sandbox — your data stays private to this session'}</div>
      {error && <div style={S.errBar}>{error}</div>}

      <div style={S.grid}>
        <div style={S.col}>
          <h2 style={S.h2}>{t('sandboxYourDocs') || 'Your documents'}</h2>
          <div style={S.quota}>Docs {docsUsed}/{docsMax} · {fmtBytes(quota?.bytes_used)} {t('sandboxTextLabel') || 'text'} · {fmtBytes(quota?.media_bytes_used)} {t('sandboxMediaLabel') || 'media'}</div>
          <button style={S.btnSmall} onClick={() => fileRef.current?.click()} disabled={docsUsed >= docsMax}>
            {t('sandboxUpload') || 'Upload file'}
          </button>
          <input ref={fileRef} type="file" accept={ACCEPT} style={{ display: 'none' }}
            onChange={(e) => { upload(e.target.files?.[0]); e.target.value = '' }} />

          {Object.entries(jobs).map(([id, j]) => (
            <div key={id} style={S.job}>
              <span>{j.name}</span>
              <span style={j.status === 'failed' ? S.jobErr : S.jobOk}>{j.status}{j.error ? ` — ${j.error}` : ''}</span>
            </div>
          ))}

          <div style={S.docList}>
            {docs.length === 0 && <p style={S.muted}>{t('sandboxNoDocs') || 'No documents yet — upload one to ground the chat in your data.'}</p>}
            {docs.map((d) => (
              <div key={d.doc_id} style={S.doc}>
                <div>
                  <div style={S.docTitle}>{d.title}</div>
                  <div style={S.muted}>{d.source} · {d.chars} chars</div>
                </div>
              </div>
            ))}
          </div>

          <button style={S.wipeBtn} onClick={() => setConfirmWipe(true)} disabled={busy}>
            {t('sandboxWipeBtn') || 'Wipe my data'}
          </button>
        </div>

        <div style={S.col}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h2 style={S.h2}>{t('sandboxChatTitle') || 'Chat'}</h2>
            <label style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '.78rem', color: 'var(--text-2)', cursor: 'pointer' }}>
              <input type="checkbox" checked={sandboxOnly} onChange={(e) => setSandboxOnly(e.target.checked)} />
              {t('sandboxOnlyMode') || 'My data only'}
            </label>
          </div>
          <div style={S.chat}>
            {messages.length === 0 && <p style={S.muted}>{t('sandboxChatEmpty') || 'Ask anything — answers use OmniIntelOS knowledge plus your uploaded files.'}</p>}
            {messages.map((m, i) => (
              <div key={i} style={m.role === 'user' ? S.msgUser : S.msgBot}>{m.content}</div>
            ))}
          </div>
          <div style={S.inputRow}>
            <input style={S.input} value={input} onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && send()} placeholder={t('sandboxChatPlaceholder') || 'Ask about your documents…'} />
            <button style={S.btnSmall} onClick={send} disabled={busy || !input.trim()}>{t('sandboxSend') || 'Send'}</button>
          </div>
        </div>
      </div>

      {confirmWipe && (
        <div style={S.modal}>
          <div style={S.modalCard}>
            <h3 style={S.h3}>{t('sandboxWipeTitle') || 'Wipe sandbox?'}</h3>
            <p style={S.p}>{(t('sandboxWipeMsg') || 'This permanently deletes {count} document(s), all extracted text, vectors and chat history for this session. This cannot be undone.').replace('{count}', docs.length)}</p>
            <div style={S.modalRow}>
              <button style={S.wipeBtn} onClick={wipe} disabled={busy}>{t('sandboxWipeConfirm') || 'Yes, wipe everything'}</button>
              <button style={S.btnSmall} onClick={() => setConfirmWipe(false)}>{t('sandboxCancel') || 'Cancel'}</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

const S = {
  page: { minHeight: '100vh', background: '#0B0F14', color: '#E8EEF5', padding: '2rem 1rem', fontFamily: 'system-ui, sans-serif' },
  center: { minHeight: '100vh', display: 'grid', placeItems: 'center', background: '#0B0F14', color: '#E8EEF5' },
  card: { maxWidth: 560, margin: '4rem auto', background: '#12181F', border: '1px solid #26313D', borderRadius: 12, padding: '2rem' },
  h1: { fontSize: '1.6rem', marginBottom: '0.75rem' },
  h2: { fontSize: '1.05rem', marginBottom: '0.5rem' },
  h3: { fontSize: '1rem', marginBottom: '0.5rem' },
  p: { color: '#9AA8B6', lineHeight: 1.55, marginBottom: '1rem' },
  muted: { color: '#7A8896', fontSize: '0.85rem' },
  list: { color: '#9AA8B6', paddingLeft: '1.2rem', marginBottom: '1.25rem', lineHeight: 1.7 },
  err: { color: '#FF8A8A', fontSize: '0.85rem', marginBottom: '0.75rem' },
  errBar: { maxWidth: 1100, margin: '0 auto 1rem', background: '#3A1D1D', border: '1px solid #7A2E2E', color: '#FFB3B3', borderRadius: 8, padding: '0.5rem 1rem', fontSize: '0.85rem' },
  banner: { maxWidth: 1100, margin: '0 auto 1rem', background: '#0E2A33', border: '1px solid #1E5A6B', color: '#7FE3F0', borderRadius: 8, padding: '0.5rem 1rem', fontSize: '0.85rem', textAlign: 'center' },
  grid: { maxWidth: 1100, margin: '0 auto', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem' },
  col: { background: '#12181F', border: '1px solid #26313D', borderRadius: 12, padding: '1.25rem' },
  quota: { color: '#9AA8B6', fontSize: '0.8rem', marginBottom: '0.75rem', fontFamily: 'monospace' },
  btn: { background: '#00F0FF', color: '#06121A', border: 'none', borderRadius: 8, padding: '0.65rem 1.4rem', fontWeight: 700, cursor: 'pointer' },
  btnSmall: { background: '#1B2632', color: '#E8EEF5', border: '1px solid #34465A', borderRadius: 8, padding: '0.45rem 0.9rem', cursor: 'pointer', fontSize: '0.85rem' },
  wipeBtn: { background: 'transparent', color: '#FF9A9A', border: '1px solid #7A2E2E', borderRadius: 8, padding: '0.5rem 1rem', cursor: 'pointer', marginTop: '1rem', fontSize: '0.85rem' },
  job: { display: 'flex', justifyContent: 'space-between', gap: '0.5rem', padding: '0.4rem 0', fontSize: '0.8rem', borderBottom: '1px solid #1B2632' },
  jobOk: { color: '#7FE3A0' }, jobErr: { color: '#FF9A9A' },
  docList: { marginTop: '1rem', display: 'flex', flexDirection: 'column', gap: '0.4rem' },
  doc: { background: '#0E141B', border: '1px solid #1B2632', borderRadius: 8, padding: '0.6rem 0.8rem' },
  docTitle: { fontWeight: 600, fontSize: '0.9rem' },
  chat: { height: 380, overflowY: 'auto', background: '#0E141B', border: '1px solid #1B2632', borderRadius: 8, padding: '0.75rem', display: 'flex', flexDirection: 'column', gap: '0.5rem', marginBottom: '0.75rem' },
  msgUser: { alignSelf: 'flex-end', background: '#123A4A', borderRadius: '10px 10px 2px 10px', padding: '0.5rem 0.8rem', maxWidth: '85%', fontSize: '0.9rem', whiteSpace: 'pre-wrap' },
  msgBot: { alignSelf: 'flex-start', background: '#1B2632', borderRadius: '10px 10px 10px 2px', padding: '0.5rem 0.8rem', maxWidth: '85%', fontSize: '0.9rem', whiteSpace: 'pre-wrap' },
  inputRow: { display: 'flex', gap: '0.5rem' },
  input: { flex: 1, background: '#0E141B', border: '1px solid #34465A', borderRadius: 8, padding: '0.55rem 0.8rem', color: '#E8EEF5', fontSize: '0.9rem' },
  modal: { position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.6)', display: 'grid', placeItems: 'center', zIndex: 50 },
  modalCard: { background: '#12181F', border: '1px solid #34465A', borderRadius: 12, padding: '1.5rem', maxWidth: 420 },
  modalRow: { display: 'flex', gap: '0.75rem', marginTop: '1rem' },
}
