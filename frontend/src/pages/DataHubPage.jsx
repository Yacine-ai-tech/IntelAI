import { useState, useEffect, useRef, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useTranslation } from '../i18n/I18nContext'
import * as api from '../api'
import {
  Database, Upload, FileText, Search, Loader2, CheckCircle2, AlertCircle,
  BarChart3, File, ArrowRight, Table as TableIcon,
} from 'lucide-react'
import { PageHeader, Panel, Grid, Stat, StatGrid, MiniBars, Empty, fmtNum } from '../components/ui'

// Minimal CSV parser (handles quoted fields) — lets us preview/visualize a file
// in the browser before it's ingested, so the user sees exactly what they uploaded.
function parseCSV(text) {
  const lines = text.replace(/\r/g, '').split('\n').filter(l => l.trim())
  if (!lines.length) return { headers: [], rows: [] }
  const split = (line) => {
    const out = []; let cur = ''; let q = false
    for (const ch of line) {
      if (ch === '"') q = !q
      else if (ch === ',' && !q) { out.push(cur); cur = '' }
      else cur += ch
    }
    out.push(cur)
    return out.map(s => s.trim().replace(/^"|"$/g, ''))
  }
  const headers = split(lines[0])
  const rows = lines.slice(1).map(l => {
    const c = split(l); const o = {}; headers.forEach((h, i) => (o[h] = c[i])); return o
  })
  return { headers, rows }
}

// Build a quick bar chart from parsed rows when there's a metric + numeric value column.
function chartFromRows(headers, rows) {
  const find = (re) => headers.find(h => re.test(h.toLowerCase()))
  const mCol = find(/metric|name|kpi/), vCol = find(/value|amount|count/), pCol = find(/period|date|month/)
  if (!mCol || !vCol) return null
  let subset = rows
  if (pCol) {
    const latest = rows.map(r => r[pCol]).filter(Boolean).sort().slice(-1)[0]
    if (latest) subset = rows.filter(r => r[pCol] === latest)
  }
  const data = subset
    .map(r => ({ metric: r[mCol], value: parseFloat(String(r[vCol]).replace(/[^0-9.\-]/g, '')) }))
    .filter(d => d.metric && !isNaN(d.value))
    .slice(0, 12)
  return data.length ? data : null
}

export default function DataHubPage() {
  const { user } = useAuth()
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [stats, setStats] = useState(null)
  const [files, setFiles] = useState([])
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [busy, setBusy] = useState('')
  const [msg, setMsg] = useState(null)
  const [preview, setPreview] = useState(null)   // { file, headers, rows, chart }
  const [drag, setDrag] = useState('')
  const csvRef = useRef(null)
  const docRef = useRef(null)

  const refresh = useCallback(async () => {
    const [s, f] = await Promise.allSettled([api.getKnowledgeStats?.(), api.getUserFiles()])
    if (s.status === 'fulfilled') setStats(s.value?.data ?? s.value)
    if (f.status === 'fulfilled') setFiles((f.value?.data?.files ?? f.value?.data ?? f.value ?? []).slice(0, 10))
  }, [])
  useEffect(() => { refresh() }, [refresh])

  const flash = (type, text) => { setMsg({ type, text }); setTimeout(() => setMsg(null), 5000) }

  // Pick/drop a CSV → parse + preview locally (no upload yet)
  const onPickCSV = (file) => {
    if (!file) return
    const reader = new FileReader()
    reader.onload = () => {
      const text = String(reader.result || '')
      const { headers, rows } = parseCSV(text)
      setPreview({ file, headers, rows, chart: chartFromRows(headers, rows) })
    }
    reader.readAsText(file)
  }

  const ingestCSV = async () => {
    if (!preview?.file) return
    setBusy('csv')
    try {
      const r = await api.uploadCSV(preview.file)
      const n = r?.data?.rows_inserted ?? preview.rows.length
      flash('ok', `${preview.file.name} ingested — ${n} rows now live in your KPIs.`)
      setPreview(null)
      refresh()
    } catch (e) {
      flash('err', e?.response?.data?.detail || `Upload failed: ${e.message}`)
    } finally { setBusy('') }
  }

  const onUploadDoc = async (file) => {
    if (!file) return
    setBusy('doc')
    try {
      await api.uploadDocument(file, 'Knowledge')
      flash('ok', `${file.name} indexed into the knowledge base.`)
      refresh()
    } catch (e) {
      flash('err', e?.response?.data?.detail || `Upload failed: ${e.message}`)
    } finally { setBusy('') }
  }

  const onSearch = async (e) => {
    e.preventDefault()
    if (!query.trim()) return
    setBusy('search')
    try {
      const r = await api.searchKnowledge(query, 5)
      setResults(r?.data?.results ?? r?.data ?? [])
    } catch (e) { flash('err', `Search failed: ${e.message}`) } finally { setBusy('') }
  }

  const dz = (kind, onFile) => ({
    onDragOver: (e) => { e.preventDefault(); setDrag(kind) },
    onDragLeave: () => setDrag(''),
    onDrop: (e) => { e.preventDefault(); setDrag(''); onFile(e.dataTransfer.files?.[0]) },
  })

  return (
    <div>
      <PageHeader icon={Database} title={t('navDataHub') || 'Data'}
        subtitle={t('dataSubtitle') || 'Upload KPI data & documents, preview them, then explore in the copilot'}
        actions={<span className="role-chip"><b>{user?.role?.toUpperCase()}</b><span>· {t('uploadsScoped') || 'uploads feed your dashboards & copilot'}</span></span>} />

      {msg && (
        <div className={`alert ${msg.type === 'ok' ? 'alert-success' : 'alert-danger'}`} style={{ marginBottom: 18 }}>
          {msg.type === 'ok' ? <CheckCircle2 size={18} /> : <AlertCircle size={18} />}<span>{msg.text}</span>
        </div>
      )}

      <Grid min={300}>
        <Panel title={t('uploadKpiCsv') || 'Upload KPI data (CSV)'} icon={Upload}>
          <div className={`dropzone${drag === 'csv' ? ' over' : ''}`} {...dz('csv', onPickCSV)} onClick={() => csvRef.current?.click()}>
            <Upload size={26} />
            <div style={{ fontWeight: 600, marginTop: 8 }}>{t('dropCsv') || 'Drop a CSV here or click to choose'}</div>
            <div style={{ fontSize: '.78rem', color: 'var(--text-3)', marginTop: 4 }}>
              <code>period, metric, value, category, unit</code>
            </div>
          </div>
          <input ref={csvRef} type="file" accept=".csv" style={{ display: 'none' }}
            onChange={(e) => onPickCSV(e.target.files[0])} />
        </Panel>

        <Panel title={t('addDocument') || 'Add document to knowledge base'} icon={FileText}>
          <div className={`dropzone${drag === 'doc' ? ' over' : ''}`} {...dz('doc', onUploadDoc)} onClick={() => docRef.current?.click()}>
            {busy === 'doc' ? <Loader2 size={26} className="spin-inline" /> : <FileText size={26} />}
            <div style={{ fontWeight: 600, marginTop: 8 }}>{t('dropDoc') || 'Drop a PDF/TXT/MD or click to choose'}</div>
            <div style={{ fontSize: '.78rem', color: 'var(--text-3)', marginTop: 4 }}>{t('docIndexed') || 'Indexed for the persona RAG copilot'}</div>
          </div>
          <input ref={docRef} type="file" accept=".pdf,.txt,.csv,.md" style={{ display: 'none' }}
            onChange={(e) => onUploadDoc(e.target.files[0])} />
        </Panel>

        <Panel title={t('knowledgeBase') || 'Knowledge base'} icon={Database} style={{ textAlign: 'center' }}>
          <div className="brand-gradient" style={{ fontSize: '2.4rem', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>
            {fmtNum(stats?.document_count ?? stats?.total_documents ?? stats?.count ?? 0)}
          </div>
          <div style={{ color: 'var(--text-3)', fontSize: '.85rem' }}>{t('indexedDocuments') || 'indexed documents'}</div>
        </Panel>
      </Grid>

      {/* Visualize the uploaded data BEFORE ingest */}
      {preview && (
        <Panel title={`${t('preview') || 'Preview'}: ${preview.file.name}`} icon={TableIcon} style={{ marginTop: 18 }}
          actions={
            <div style={{ display: 'flex', gap: 8 }}>
              <button className="btn btn-sm" onClick={() => setPreview(null)}>{t('cancel') || 'Cancel'}</button>
              <button className="btn btn-primary btn-sm" disabled={busy === 'csv'} onClick={ingestCSV}>
                {busy === 'csv' ? <Loader2 size={14} className="spin-inline" /> : <Upload size={14} />} {t('ingest') || 'Ingest'} {preview.rows.length} {t('rows') || 'rows'}
              </button>
            </div>
          }>
          {preview.chart && (
            <div style={{ marginBottom: 16 }}>
              <div className="kpi-label" style={{ marginBottom: 6 }}><BarChart3 size={13} style={{ verticalAlign: 'middle' }} /> {t('uploadedDataChart') || 'Uploaded values (latest period)'}</div>
              <MiniBars data={preview.chart} x="metric" y="value" height={200} />
            </div>
          )}
          <div style={{ maxHeight: 260, overflow: 'auto' }}>
            {preview.rows.length ? (
              <table className="table">
                <thead><tr>{preview.headers.map(h => <th key={h}>{h}</th>)}</tr></thead>
                <tbody>
                  {preview.rows.slice(0, 50).map((r, i) => (
                    <tr key={i}>{preview.headers.map(h => <td key={h}>{r[h]}</td>)}</tr>
                  ))}
                </tbody>
              </table>
            ) : <Empty text={t('emptyCsv') || 'No rows found in this CSV.'} />}
          </div>
          <div style={{ margintop: 12, marginTop: 12, fontSize: '.8rem', color: 'var(--text-3)' }}>
            {t('showing') || 'Showing'} {Math.min(preview.rows.length, 50)} / {preview.rows.length} {t('rows') || 'rows'}
          </div>
        </Panel>
      )}

      <Grid min={320} style={{ marginTop: 18 }}>
        {/* Uploaded files */}
        <Panel title={t('yourUploads') || 'Your uploads'} icon={File}
          actions={<button className="btn btn-outline btn-sm" onClick={() => navigate('/analytics')}>{t('viewInAnalytics') || 'View in Analytics'} <ArrowRight size={13} /></button>}>
          {files.length ? (
            <table className="table">
              <thead><tr><th>{t('file') || 'File'}</th><th>{t('type') || 'Type'}</th><th>{t('when') || 'When'}</th></tr></thead>
              <tbody>
                {files.map((f, i) => (
                  <tr key={i}>
                    <td style={{ fontWeight: 600 }}>{f.file_name || f.filename || f.name || '—'}</td>
                    <td><span className="badge">{f.file_type || f.type || 'file'}</span></td>
                    <td style={{ fontSize: '.8rem', color: 'var(--text-3)' }}>{f.created_at ? new Date(f.created_at).toLocaleString() : '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : <Empty text={t('noUploads') || 'No uploads yet — drop a CSV above to get started.'} />}
        </Panel>

        {/* Knowledge search */}
        <Panel title={t('searchKnowledge') || 'Search the knowledge base'} icon={Search}>
          <form onSubmit={onSearch} style={{ display: 'flex', gap: 10, marginBottom: 12 }}>
            <input className="form-input" style={{ flex: 1 }} value={query} placeholder="e.g. Q1 churn drivers"
              onChange={(e) => setQuery(e.target.value)} />
            <button className="btn btn-primary" disabled={busy === 'search'}>
              {busy === 'search' ? <Loader2 size={16} className="spin-inline" /> : <Search size={16} />}
            </button>
          </form>
          {results.map((r, i) => (
            <div key={i} style={{ padding: '10px 0', borderTop: '1px solid var(--border)' }}>
              <div style={{ fontWeight: 600, fontSize: '.9rem' }}>{r.title || r.source || `Result ${i + 1}`}</div>
              <div style={{ color: 'var(--text-2)', fontSize: '.82rem' }}>{(r.content || r.preview || '').slice(0, 200)}…</div>
            </div>
          ))}
          {results.length === 0 && <div style={{ color: 'var(--text-3)', fontSize: '.85rem' }}>{t('noResults') || 'No results yet.'}</div>}
        </Panel>
      </Grid>
    </div>
  )
}
