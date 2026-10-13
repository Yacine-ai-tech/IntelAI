import { useState, useRef, useEffect } from 'react'
import { useTranslation } from '../i18n/I18nContext'
import { useQuery } from '@tanstack/react-query'
import * as api from '../api'
import { Search, Database, FileText, BookOpen, Layers, Sparkles, X, StopCircle } from 'lucide-react'
import { PageHeader, Stat, StatGrid, fmtNum, Loading, AskCopilot, Panel } from '../components/ui'

export default function KnowledgePage() {
  const { t } = useTranslation()
  const [q, setQ] = useState('')
  const [n, setN] = useState(10)
  const [preview, setPreview] = useState(null)

  const { data: stats } = useQuery({ queryKey: ['knowledge-stats'], queryFn: () => api.getKnowledgeStats().then(r => r.data || {}), staleTime: 300_000 })
  // Search runs as a polled job so the page can show real stage progress and the fused
  // (preliminary) ranking while the cross-encoder finishes.
  const [run, setRun] = useState({ phase: 'idle', progress: null, preliminary: null, data: null, error: null, query: '' })
  const [elapsed, setElapsed] = useState(0)
  const abortRef = useRef(null)

  useEffect(() => {
    if (run.phase !== 'running') { setElapsed(0); return undefined }
    const started = Date.now()
    const id = setInterval(() => setElapsed(Math.floor((Date.now() - started) / 1000)), 1000)
    return () => clearInterval(id)
  }, [run.phase])

  const startSearch = async (query) => {
    abortRef.current?.abort()
    const controller = new AbortController()
    abortRef.current = controller
    setRun({ phase: 'running', progress: null, preliminary: null, data: null, error: null, query })
    try {
      const data = await api.searchKnowledgeJob(query, n, {
        signal: controller.signal,
        onProgress: (st) => setRun(r => r.phase !== 'running' ? r : ({
          ...r, progress: st.progress || r.progress, preliminary: st.preliminary || r.preliminary,
        })),
      })
      setRun(r => ({ ...r, phase: 'done', data, progress: { stage: 'done' } }))
    } catch (e) {
      if (e.name === 'CanceledError' || e.message === 'canceled') setRun(r => ({ ...r, phase: 'canceled' }))
      else setRun(r => ({ ...r, phase: 'error', error: e.message || 'Search failed' }))
    }
  }
  const cancelSearch = () => abortRef.current?.abort()
  useEffect(() => () => abortRef.current?.abort(), [])

  const onSearch = (e) => { e.preventDefault(); if (q.trim()) startSearch(q.trim()) }
  const running = run.phase === 'running'
  const stageLabel = (p) => {
    const stage = p?.stage
    if (stage === 'fused') return t('searchStageFused') || `Candidates found (${p.candidates ?? p.total ?? 0}). Ranking the best passages…`
    if (stage === 'reranking') return `${t('searchStageRerank') || 'Ranking the best passages'} (${p.done ?? 0}/${p.total ?? '?'})`
    if (stage === 'searching') return t('searchStageSearching') || 'Searching the knowledge base…'
    return t('searchStageStarting') || 'Starting…'
  }
  const livePreliminary = running && run.preliminary && !run.data
  const results = run.data?.results || (livePreliminary ? run.preliminary : [])
  const progressPct = run.progress?.total ? Math.min(100, Math.round(((run.progress.done || 0) / run.progress.total) * 100)) : null
  const docCount = stats?.document_count ?? stats?.total_documents ?? stats?.count ?? 0

  return (
    <div>
      <PageHeader icon={BookOpen} title={t('navKnowledge') || 'Knowledge Base'}
        subtitle={t('knSubtitle') || 'Hybrid retrieval (vector + BM25 + reranking) over your indexed docs'}
        actions={<AskCopilot q={t('askCopilot_KnowledgePage_WhatKnowledgeDo')} />} />

      <StatGrid>
        <Stat label={t('totalDocuments') || 'Indexed Documents'} value={fmtNum(docCount)} icon={Database} />
        <Stat label={t('lblGlossaryTerms')} value="101" icon={BookOpen} accent="var(--accent)" />
        <Stat label={t('lblDomainsCovered')} value="7" icon={Layers} accent="var(--ok)" />
      </StatGrid>

      <Panel title={t('searchKnowledge') || 'Search the knowledge base'} icon={Search} style={{ marginTop: 18 }}>
        <form onSubmit={onSearch} style={{ display: 'flex', gap: 10, marginBottom: 6 }}>
          <div className="chat-input-wrap" style={{ flex: 1, padding: '6px 14px', margin: 0 }}>
            <Search size={16} style={{ color: 'var(--text-3)' }} />
            <input className="chat-input" style={{ padding: '6px 0' }} placeholder={t('knowledgeSearchPlaceholder') || 'e.g. Q1 churn drivers, ESG carbon, MTTR…'}
              value={q} onChange={e => setQ(e.target.value)} />
          </div>
          <select className="form-input" style={{ width: 90 }} value={n} onChange={e => setN(Number(e.target.value))}>
            {[5, 10, 20, 50].map(v => <option key={v} value={v}>{v}</option>)}
          </select>
          {running ? (
            <button className="btn" type="button" onClick={cancelSearch}>
              <StopCircle size={15} /> {t('cancel') || 'Cancel'}
            </button>
          ) : (
            <button className="btn btn-primary" type="submit" disabled={!q.trim()}>
              <Search size={15} /> {t('search') || 'Search'}
            </button>
          )}
        </form>
      </Panel>

      {running && (
        <div className="card" style={{ marginTop: 18 }} role="status" aria-live="polite">
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <span style={{ display: 'inline-block', width: 14, height: 14, border: '2px solid rgba(34, 211, 238, 0.25)', borderTopColor: 'var(--primary, #22d3ee)', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} />
            <span style={{ fontSize: '.88rem' }}>{stageLabel(run.progress)}</span>
            <span style={{ marginLeft: 'auto', fontSize: '.75rem', color: 'var(--text-3)' }}>{elapsed}s</span>
          </div>
          {progressPct != null && (
            <div style={{ height: 4, background: 'var(--bg-3, rgba(255,255,255,.08))', borderRadius: 2, marginTop: 10, overflow: 'hidden' }}>
              <div style={{ width: `${progressPct}%`, height: '100%', background: 'var(--primary, #22d3ee)', transition: 'width .4s ease' }} />
            </div>
          )}
          {elapsed >= 20 && (
            <div style={{ marginTop: 10, fontSize: '.78rem', color: 'var(--text-3)' }}>
              {t('searchSlowNote') || 'Still working. Ranking runs on CPU and can take up to a minute on a cold start; the list below is the preliminary order.'}
            </div>
          )}
        </div>
      )}
      {run.phase === 'canceled' && <div className="alert" style={{ marginTop: 16 }}>{t('searchCanceled') || 'Search canceled.'}</div>}
      {run.phase === 'error' && <div className="alert alert-danger" style={{ marginTop: 16 }}>Search failed: {run.error}</div>}

      {(run.data || livePreliminary) && (
        <div style={{ marginTop: 18 }}>
          <div style={{ color: 'var(--text-3)', fontSize: '.82rem', marginBottom: 12 }}>
            {results.length} {t('results') || 'results'} for “{run.query}”
            {livePreliminary && <span className="badge" style={{ marginLeft: 8 }}>{t('searchPreliminary') || 'Preliminary, refining…'}</span>}
            {run.data?.partial && <span className="badge" style={{ marginLeft: 8 }}>{t('searchPartial') || 'Fused order (ranking was cut short)'}</span>}
            {run.data && !run.data.partial && <span className="badge" style={{ marginLeft: 8 }}>{t('searchFinal') || 'Final'}</span>}
          </div>
          {results.map((r, i) => (
            <div key={`${r.title}-${i}`} className="card clickable" style={{ marginBottom: 10, opacity: livePreliminary ? 0.85 : 1, transition: 'opacity .3s ease' }} onClick={() => setPreview(r)}>
              <div style={{ display: 'flex', gap: 12 }}>
                <div className="kpi-icon-wrap" style={{ margin: 0, flexShrink: 0 }}><FileText size={17} /></div>
                <div style={{ minWidth: 0 }}>
                  <div style={{ fontWeight: 600 }}>{r.title || r.source || `Result ${i + 1}`}</div>
                  <div style={{ color: 'var(--text-2)', fontSize: '.85rem', margin: '4px 0', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                    {r.content || r.preview || r.text || '—'}
                  </div>
                  <div style={{ display: 'flex', gap: 14, fontSize: '.72rem', color: 'var(--text-3)' }}>
                    {(r.score != null || r.relevance != null) && <span><Sparkles size={11} style={{ verticalAlign: 'middle' }} /> {((r.score ?? r.relevance) * 100).toFixed(0)}% relevance</span>}
                    {r.source && <span>{r.source}</span>}
                    {r.category && <span className="badge">{r.category}</span>}
                  </div>
                </div>
              </div>
            </div>
          ))}
          {results.length === 0 && !running && (
            <Panel style={{ textAlign: 'center', padding: 40, color: 'var(--text-3)' }}>
              <Search size={38} style={{ margin: '0 auto 12px', opacity: .5 }} /><p>{t('noResultsTryDiff') || 'No results. Try different terms.'}</p>
            </Panel>
          )}
        </div>
      )}

      {preview && (
        <div className="drawer-overlay" onClick={() => setPreview(null)} style={{ justifyContent: 'center', alignItems: 'center' }}>
          <div className="card" onClick={e => e.stopPropagation()} style={{ maxWidth: 760, width: '90%', maxHeight: '80vh', overflowY: 'auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 }}>
              <h3 className="card-title" style={{ margin: 0 }}><FileText size={16} /> {preview.title || 'Document'}</h3>
              <button className="btn btn-ghost btn-icon" onClick={() => setPreview(null)}><X size={18} /></button>
            </div>
            <div style={{ whiteSpace: 'pre-wrap', lineHeight: 1.6, color: 'var(--text-2)', fontSize: '.9rem' }}>
              {preview.content || preview.preview || preview.text || 'No content.'}
            </div>
            {preview.source && <div style={{ marginTop: 14, fontSize: '.78rem', color: 'var(--text-3)' }}>Source: {preview.source}</div>}
          </div>
        </div>
      )}
    </div>
  )
}
