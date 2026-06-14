import { useState } from 'react'
import { useTranslation } from '../i18n/I18nContext'
import { useQuery, useMutation } from '@tanstack/react-query'
import * as api from '../api'
import { Search, Database, FileText, BookOpen, Layers, Sparkles, X } from 'lucide-react'
import { PageHeader, Stat, StatGrid, Panel, Loading, AskCopilot, fmtNum } from '../components/ui'

export default function KnowledgePage() {
  const { t } = useTranslation()
  const [q, setQ] = useState('')
  const [n, setN] = useState(10)
  const [preview, setPreview] = useState(null)

  const { data: stats } = useQuery({ queryKey: ['knowledge-stats'], queryFn: () => api.getKnowledgeStats().then(r => r.data || {}), staleTime: 300_000 })
  const search = useMutation({ mutationFn: (query) => api.searchKnowledge(query, n).then(r => r.data) })

  const onSearch = (e) => { e.preventDefault(); if (q.trim()) search.mutate(q) }
  const results = search.data?.results || search.data || []
  const docCount = stats?.document_count ?? stats?.total_documents ?? stats?.count ?? 0

  return (
    <div>
      <PageHeader icon={BookOpen} title={t('navKnowledge') || 'Knowledge Base'}
        subtitle={t('knSubtitle') || 'Hybrid retrieval (vector + BM25 + reranking) over your indexed docs'}
        actions={<AskCopilot q="What knowledge do we have indexed, and summarize the most relevant documents." />} />

      <StatGrid>
        <Stat label={t('totalDocuments') || 'Indexed Documents'} value={fmtNum(docCount)} icon={Database} />
        <Stat label="Glossary Terms" value="101" icon={BookOpen} accent="var(--accent)" />
        <Stat label="Domains Covered" value="7" icon={Layers} accent="var(--ok)" />
      </StatGrid>

      <Panel title={t('searchKnowledge') || 'Search the knowledge base'} icon={Search} style={{ marginTop: 18 }}>
        <form onSubmit={onSearch} style={{ display: 'flex', gap: 10, marginBottom: 6 }}>
          <div className="chat-input-wrap" style={{ flex: 1, padding: '6px 14px', margin: 0 }}>
            <Search size={16} style={{ color: 'var(--text-3)' }} />
            <input className="chat-input" style={{ padding: '6px 0' }} placeholder="e.g. Q1 churn drivers, ESG carbon, MTTR…"
              value={q} onChange={e => setQ(e.target.value)} />
          </div>
          <select className="form-input" style={{ width: 90 }} value={n} onChange={e => setN(Number(e.target.value))}>
            {[5, 10, 20, 50].map(v => <option key={v} value={v}>{v}</option>)}
          </select>
          <button className="btn btn-primary" type="submit" disabled={!q.trim() || search.isPending}>
            <Search size={15} /> {search.isPending ? (t('searching') || 'Searching…') : (t('search') || 'Search')}
          </button>
        </form>
      </Panel>

      {search.isPending && <Loading label="Searching…" />}
      {search.error && <div className="alert alert-danger" style={{ marginTop: 16 }}>Search failed: {search.error.message}</div>}

      {search.data && (
        <div style={{ marginTop: 18 }}>
          <div style={{ color: 'var(--text-3)', fontSize: '.82rem', marginBottom: 12 }}>
            {results.length} {t('results') || 'results'} for “{q}”
          </div>
          {results.map((r, i) => (
            <div key={i} className="card clickable" style={{ marginBottom: 10 }} onClick={() => setPreview(r)}>
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
          {results.length === 0 && !search.isPending && (
            <Panel style={{ textAlign: 'center', padding: 40, color: 'var(--text-3)' }}>
              <Search size={38} style={{ margin: '0 auto 12px', opacity: .5 }} /><p>No results. Try different terms.</p>
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
