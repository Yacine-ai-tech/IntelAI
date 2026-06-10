import { useState, useEffect, useRef } from 'react'
import * as api from '../api'
import { Database, Upload, FileText, Search, Loader2, CheckCircle2, AlertCircle } from 'lucide-react'

/**
 * Data — simple, scoped ingestion + knowledge for IntelAI.
 * Upload KPI CSVs, add documents to the knowledge base, and search the RAG index.
 * (Bulk dataset ingestion / 3rd-party integrations live in the OmniIntelOS platform.)
 */
export default function DataHubPage() {
  const [stats, setStats] = useState(null)
  const [files, setFiles] = useState([])
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [busy, setBusy] = useState('')
  const [msg, setMsg] = useState(null)
  const csvRef = useRef(null)
  const docRef = useRef(null)

  const refresh = async () => {
    const [s, f] = await Promise.allSettled([api.getKnowledgeStats?.(), api.getUserFiles()])
    if (s.status === 'fulfilled') setStats(s.value?.data ?? s.value)
    if (f.status === 'fulfilled') setFiles((f.value?.data ?? f.value ?? []).slice(0, 8))
  }
  useEffect(() => { refresh() }, [])

  const flash = (type, text) => { setMsg({ type, text }); setTimeout(() => setMsg(null), 4000) }

  const onUpload = async (kind, file) => {
    if (!file) return
    setBusy(kind)
    try {
      if (kind === 'csv') await api.uploadCSV(file)
      else await api.uploadDocument(file, 'Knowledge')
      flash('ok', `${file.name} ingested.`)
      refresh()
    } catch (e) {
      flash('err', e?.response?.data?.detail || `Upload failed: ${e.message}`)
    } finally {
      setBusy('')
    }
  }

  const onSearch = async (e) => {
    e.preventDefault()
    if (!query.trim()) return
    setBusy('search')
    try {
      const r = await api.searchKnowledge(query, 5)
      setResults(r?.data?.results ?? r?.data ?? [])
    } catch (e) {
      flash('err', `Search failed: ${e.message}`)
    } finally {
      setBusy('')
    }
  }

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 6 }}>
        <Database size={26} style={{ color: 'var(--primary)' }} />
        <h1 className="display" style={{ fontSize: '1.6rem' }}>Data</h1>
      </div>
      <p style={{ color: 'var(--text-secondary)', marginBottom: 24 }}>
        Upload KPI data, add documents to the knowledge base, and search the RAG index.
      </p>

      {msg && (
        <div className="card" style={{ marginBottom: 18, display: 'flex', gap: 10, alignItems: 'center',
          borderColor: msg.type === 'ok' ? 'var(--success)' : 'var(--danger)' }}>
          {msg.type === 'ok' ? <CheckCircle2 size={18} style={{ color: 'var(--success)' }} />
            : <AlertCircle size={18} style={{ color: 'var(--danger)' }} />}
          <span>{msg.text}</span>
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 18 }}>
        <div className="card">
          <div className="card-title"><Upload size={16} /> Upload KPI CSV</div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: 14 }}>
            Columns: <code>period, metric, value, category, segment, unit</code>.
          </p>
          <input ref={csvRef} type="file" accept=".csv" style={{ display: 'none' }}
            onChange={(e) => onUpload('csv', e.target.files[0])} />
          <button className="btn btn-primary" disabled={busy === 'csv'} onClick={() => csvRef.current?.click()}>
            {busy === 'csv' ? <Loader2 size={16} /> : <Upload size={16} />} Choose CSV
          </button>
        </div>

        <div className="card">
          <div className="card-title"><FileText size={16} /> Add document to knowledge base</div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: 14 }}>
            PDF / TXT / CSV / MD — text is indexed for the persona RAG copilot.
          </p>
          <input ref={docRef} type="file" accept=".pdf,.txt,.csv,.md" style={{ display: 'none' }}
            onChange={(e) => onUpload('doc', e.target.files[0])} />
          <button className="btn btn-primary" disabled={busy === 'doc'} onClick={() => docRef.current?.click()}>
            {busy === 'doc' ? <Loader2 size={16} /> : <FileText size={16} />} Choose document
          </button>
        </div>

        <div className="card">
          <div className="card-title"><Database size={16} /> Knowledge base</div>
          <div style={{ fontSize: '2rem', fontWeight: 700 }} className="brand-gradient">
            {stats?.document_count ?? stats?.count ?? files.length ?? 0}
          </div>
          <div style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>indexed documents</div>
        </div>
      </div>

      <div className="card" style={{ marginTop: 22 }}>
        <div className="card-title"><Search size={16} /> Search the knowledge base</div>
        <form onSubmit={onSearch} style={{ display: 'flex', gap: 10, marginBottom: 14 }}>
          <input className="input" style={{ flex: 1 }} value={query} placeholder="e.g. Q1 churn drivers"
            onChange={(e) => setQuery(e.target.value)} />
          <button className="btn btn-primary" disabled={busy === 'search'}>
            {busy === 'search' ? <Loader2 size={16} /> : <Search size={16} />} Search
          </button>
        </form>
        {results.map((r, i) => (
          <div key={i} style={{ padding: '12px 0', borderTop: '1px solid var(--border)' }}>
            <div style={{ fontWeight: 600 }}>{r.title || r.source || `Result ${i + 1}`}</div>
            <div style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
              {(r.content || r.preview || '').slice(0, 220)}…
            </div>
          </div>
        ))}
        {results.length === 0 && <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>No results yet.</div>}
      </div>
    </div>
  )
}
