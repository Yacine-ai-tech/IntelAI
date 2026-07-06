// Knowledge graph — the retrieval relationships behind an answer. A real query hits
// /knowledge/search; the returned documents become nodes, linked to the KPI domains
// they mention (from /kpis/categories). This visualizes what GraphRAG connects:
// query → retrieved context → business domains.
import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Share2, Search, Loader2 } from 'lucide-react'
import * as api from '../api'
import { PageHeader, Panel, Empty } from '../components/ui'

export default function KnowledgeGraphPage() {
  const { data: categories = [] } = useQuery({
    queryKey: ['categories'], queryFn: () => api.getCategories().then(r => r.data?.categories || r.data || []),
  })

  const [query, setQuery] = useState('revenue growth and margin risk')
  const [busy, setBusy] = useState(false)
  const [docs, setDocs] = useState(null)
  const [hover, setHover] = useState(null)

  const run = async () => {
    setBusy(true)
    try {
      const res = await api.searchKnowledge(query, 8).then(r => r.data)
      setDocs(res?.results || res?.hits || [])
    } catch { setDocs([]) } finally { setBusy(false) }
  }

  // Build a real graph: center (query) → document nodes → domain nodes they mention.
  const graph = useMemo(() => {
    if (!docs) return null
    const domains = categories.length ? categories : ['Finance', 'Growth', 'Operations', 'People', 'ESG', 'IT', 'Logistics']
    const W = 900, H = 520, cx = W / 2, cy = H / 2
    const docNodes = docs.map((d, i) => {
      const ang = (i / Math.max(docs.length, 1)) * Math.PI * 2 - Math.PI / 2
      const text = `${d.title || ''} ${d.content || ''}`.toLowerCase()
      const mentioned = domains.filter(dom => text.includes(dom.toLowerCase()))
      return { id: `doc${i}`, x: cx + Math.cos(ang) * 180, y: cy + Math.sin(ang) * 150,
               label: (d.title || `doc ${i + 1}`).slice(0, 28), score: d.score, mentioned }
    })
    const usedDomains = [...new Set(docNodes.flatMap(n => n.mentioned))]
    const domNodes = usedDomains.map((dom, i) => {
      const ang = (i / Math.max(usedDomains.length, 1)) * Math.PI * 2 - Math.PI / 2
      return { id: `dom${dom}`, dom, x: cx + Math.cos(ang) * 340, y: cy + Math.sin(ang) * 220, label: dom }
    })
    const links = []
    docNodes.forEach(n => {
      links.push({ from: { x: cx, y: cy }, to: n, kind: 'retrieval' })
      n.mentioned.forEach(dom => {
        const dn = domNodes.find(d => d.dom === dom)
        if (dn) links.push({ from: n, to: dn, kind: 'domain' })
      })
    })
    return { W, H, cx, cy, docNodes, domNodes, links }
  }, [docs, categories])

  return (
    <div>
      <PageHeader icon={Share2} title="Knowledge graph"
        subtitle="See the retrieval relationships behind an answer: your query, the documents it pulled, and the business domains they connect."
        accent="var(--primary-2)" />

      <Panel title="Explore">
        <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
          <div style={{ position: 'relative', flex: 1 }}>
            <Search size={15} style={{ position: 'absolute', left: 11, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-3)' }} />
            <input value={query} onChange={e => setQuery(e.target.value)} onKeyDown={e => e.key === 'Enter' && run()}
              placeholder="Search the knowledge base…"
              style={{ width: '100%', background: 'var(--surface-2)', border: '1px solid var(--border-2)', borderRadius: 'var(--r)', padding: '9px 12px 9px 34px', color: 'var(--text)', fontSize: 14 }} />
          </div>
          <button className="btn btn-primary" onClick={run} disabled={busy}>
            {busy ? <Loader2 size={14} className="spin" /> : <Share2 size={14} />} Map
          </button>
        </div>
      </Panel>

      <Panel title="Retrieval graph">
        {!graph ? <Empty text="Search above to build the graph." />
          : graph.docNodes.length === 0 ? <Empty text="No documents matched that query." />
          : (
            <div style={{ overflowX: 'auto' }}>
              <svg viewBox={`0 0 ${graph.W} ${graph.H}`} style={{ width: '100%', minWidth: 620, height: 'auto' }}>
                {graph.links.map((l, i) => (
                  <line key={i} x1={l.from.x} y1={l.from.y} x2={l.to.x} y2={l.to.y}
                    stroke={l.kind === 'retrieval' ? 'var(--primary-line)' : 'var(--border-2)'}
                    strokeWidth={l.kind === 'retrieval' ? 1.5 : 1} strokeDasharray={l.kind === 'domain' ? '3 3' : ''} />
                ))}
                {/* domain nodes */}
                {graph.domNodes.map(n => (
                  <g key={n.id}>
                    <rect x={n.x - 44} y={n.y - 13} width={88} height={26} rx={7} fill="var(--surface-3)" stroke="var(--border-2)" />
                    <text x={n.x} y={n.y + 4} textAnchor="middle" fontSize={11} fill="var(--text-2)">{n.label}</text>
                  </g>
                ))}
                {/* document nodes */}
                {graph.docNodes.map(n => (
                  <g key={n.id} onMouseEnter={() => setHover(n)} onMouseLeave={() => setHover(null)} style={{ cursor: 'pointer' }}>
                    <circle cx={n.x} cy={n.y} r={hover?.id === n.id ? 9 : 7} fill="var(--primary)" />
                    <text x={n.x} y={n.y - 13} textAnchor="middle" fontSize={10.5} fill="var(--text-2)">{n.label}</text>
                  </g>
                ))}
                {/* center query node */}
                <circle cx={graph.cx} cy={graph.cy} r={13} fill="url(#qg)" />
                <defs><radialGradient id="qg"><stop offset="0%" stopColor="var(--primary-2)" /><stop offset="100%" stopColor="var(--primary-strong)" /></radialGradient></defs>
                <text x={graph.cx} y={graph.cy + 30} textAnchor="middle" fontSize={12} fontWeight="700" fill="var(--text)">your query</text>
              </svg>
              {hover && (
                <div style={{ marginTop: 8, fontSize: 12.5, color: 'var(--text-2)' }}>
                  <strong style={{ color: 'var(--text)' }}>{hover.label}</strong>
                  {hover.score != null && <span style={{ color: 'var(--text-3)' }}> · relevance {Number(hover.score).toFixed(3)}</span>}
                  {hover.mentioned.length > 0 && <span style={{ color: 'var(--text-3)' }}> · domains: {hover.mentioned.join(', ')}</span>}
                </div>
              )}
              <p style={{ marginTop: 10, fontSize: 12, color: 'var(--text-3)' }}>
                Solid lines are retrieval (query → document, by relevance); dashed lines connect each document to the
                business domains it mentions. Hover a document for its relevance score and linked domains.
              </p>
            </div>
          )}
      </Panel>
    </div>
  )
}
