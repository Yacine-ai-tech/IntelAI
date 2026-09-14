import { useState, useMemo, useEffect, useRef } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { Share2, Search, Loader2, X, FileText, Tag, Layers, ArrowRight, ExternalLink } from 'lucide-react'
import { PageHeader, Panel, Empty } from '../components/ui'
import { useTranslation } from '../i18n/I18nContext'
import * as api from '../api'

function useForceSimulation(nodes, links, width, height) {
  const [positions, setPositions] = useState({})
  
  useEffect(() => {
    if (!nodes.length) return
    let currentPositions = {}
    nodes.forEach((n, i) => {
      const angle = (i / nodes.length) * Math.PI * 2
      const radius = n.type === 'domain' ? 120 : n.type === 'document' ? 180 : 240
      currentPositions[n.id] = {
        x: width / 2 + Math.cos(angle) * (radius + Math.random() * 30),
        y: height / 2 + Math.sin(angle) * (radius + Math.random() * 30),
        vx: 0, vy: 0
      }
    })
    // Pin the query node to center
    if (currentPositions['query']) {
      currentPositions['query'].x = width / 2
      currentPositions['query'].y = height / 2
    }

    let animationFrameId
    let alpha = 1.0

    const tick = () => {
      alpha *= 0.95
      if (alpha < 0.008) return

      const nextPositions = { ...currentPositions }

      // Spring forces
      links.forEach(link => {
        const source = nextPositions[link.source]
        const target = nextPositions[link.target]
        if (!source || !target) return
        const dx = target.x - source.x
        const dy = target.y - source.y
        const dist = Math.sqrt(dx * dx + dy * dy) || 1
        const targetDist = link.distance || 110
        const force = (dist - targetDist) * 0.12 * alpha
        const fx = (dx / dist) * force
        const fy = (dy / dist) * force
        if (link.source !== 'query') { source.vx += fx; source.vy += fy }
        if (link.target !== 'query') { target.vx -= fx; target.vy -= fy }
      })

      // Repulsion
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const n1 = nextPositions[nodes[i].id]
          const n2 = nextPositions[nodes[j].id]
          const dx = n2.x - n1.x
          const dy = n2.y - n1.y
          const dist = Math.sqrt(dx * dx + dy * dy) || 1
          if (dist < 260) {
            const force = (260 - dist) * 0.06 * alpha
            const fx = (dx / dist) * force
            const fy = (dy / dist) * force
            if (nodes[i].id !== 'query') { n1.vx -= fx; n1.vy -= fy }
            if (nodes[j].id !== 'query') { n2.vx += fx; n2.vy += fy }
          }
        }
      }

      // Update positions
      nodes.forEach(n => {
        if (n.id === 'query') return
        const pos = nextPositions[n.id]
        pos.x += pos.vx
        pos.y += pos.vy
        pos.vx *= 0.8
        pos.vy *= 0.8
        pos.x = Math.max(60, Math.min(width - 60, pos.x))
        pos.y = Math.max(60, Math.min(height - 60, pos.y))
      })

      currentPositions = nextPositions
      setPositions(currentPositions)
      animationFrameId = requestAnimationFrame(tick)
    }

    animationFrameId = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(animationFrameId)
  }, [nodes, links, width, height])

  return positions
}

export default function KnowledgeGraphPage() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()
  const [query, setQuery] = useState(() => searchParams.get('q') || 'financement du deparment it pour achat d\'ordinateur et de serveur')
  const [busy, setBusy] = useState(false)
  const [graphData, setGraphData] = useState(null)
  const [hover, setHover] = useState(null)
  const [selectedNode, setSelectedNode] = useState(null)
  
  const width = 840
  const height = 620

  const run = async (searchTarget) => {
    const q = (searchTarget ?? query).trim()
    if (!q) return
    setBusy(true)
    setSelectedNode(null)
    try {
      const r = await api.searchKnowledge(q, 6)
      const res = r?.data?.results || []
      
      if (res.length === 0) {
        setGraphData({ nodes: [], links: [] })
        return
      }

      const nodes = [{ id: 'query', type: 'query', label: q }]
      const links = []
      
      const domainDefs = [
        { name: 'IT', patterns: ['it', 'informatique', 'ordinateur', 'serveur', 'materiel', 'infrastructure', 'tech', 'software', 'cloud', 'systeme'] },
        { name: 'Finance', patterns: ['finance', 'financial', 'financement', 'achat', 'capex', 'opex', 'cost', 'revenue', 'budget', 'tresorerie'] },
        { name: 'Operations', patterns: ['operations', 'ops', 'production', 'oee', 'defect', 'qualite'] },
        { name: 'HR', patterns: ['hr', 'people', 'employee', 'headcount', 'personnel', 'recrutement', 'salaire'] },
        { name: 'Logistics', patterns: ['logistics', 'delivery', 'warehouse', 'freight', 'expedition', 'stock'] },
        { name: 'Growth', patterns: ['growth', 'sales', 'customer', 'mrr', 'arr', 'churn'] },
        { name: 'Risk', patterns: ['risk', 'audit', 'compliance', 'conformite'] },
        { name: 'ESG', patterns: ['esg', 'carbon', 'emission', 'renewable', 'energie', 'durabilite'] }
      ]

      // Identify domains explicitly touched by the query
      const qLower = q.toLowerCase()
      const queryDomains = domainDefs.filter(d => d.patterns.some(p => qLower.includes(p)))
      queryDomains.forEach(dom => {
        const domId = `dom-${dom.name}`
        if (!nodes.find(n => n.id === domId)) {
          nodes.push({ id: domId, type: 'domain', label: dom.name })
        }
        links.push({ source: 'query', target: domId, type: 'domain_intent', distance: 120 })
      })

      res.forEach((d, i) => {
        const docId = `doc-${i}`
        const docLabel = d.title || `Document ${i+1}`
        nodes.push({ 
          id: docId, 
          type: 'document', 
          label: docLabel, 
          score: d.score,
          content: d.content 
        })
        links.push({ source: 'query', target: docId, type: 'retrieval', score: d.score, distance: 160 })

        // Extract and connect domains
        const textContent = (docLabel + ' ' + (d.content || '')).toLowerCase()
        const matchedDomains = domainDefs.filter(dom => dom.patterns.some(p => textContent.includes(p)))
        
        matchedDomains.forEach(dom => {
          const domId = `dom-${dom.name}`
          if (!nodes.find(n => n.id === domId)) {
            nodes.push({ id: domId, type: 'domain', label: dom.name })
          }
          links.push({ source: docId, target: domId, type: 'relation', distance: 100 })
        })

        // Clean entity extraction: alphanumeric tokens 4-24 chars, no parentheses, formulas, or syntax tokens
        const rawTokens = (d.content || '').split(/[\s,.;:!?/\\|"'`~@#$%^&*()+=[\]{}<>«»]+/)
        const validEntities = rawTokens.filter(tok => 
          /^[A-ZÀ-ÖØ-ß][a-zà-öø-ÿ0-9_-]{3,22}$/.test(tok) &&
          !domainDefs.some(dom => dom.name.toLowerCase() === tok.toLowerCase()) &&
          !['Pour', 'Avec', 'Dans', 'Cette', 'Sont', 'Comme', 'Total', 'Plus', 'Tous'].includes(tok)
        )
        const uniqueEntities = [...new Set(validEntities)].slice(0, 2)
        
        uniqueEntities.forEach(ent => {
          const entId = `ent-${ent}`
          if (!nodes.find(n => n.id === entId)) {
            nodes.push({ id: entId, type: 'entity', label: ent })
          }
          links.push({ source: docId, target: entId, type: 'entity_link', distance: 85 })
        })
      })

      setGraphData({ nodes, links })
    } catch (e) {
      console.error(e)
    } finally {
      setBusy(false)
    }
  }

  useEffect(() => {
    run()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const positions = useForceSimulation(graphData?.nodes || [], graphData?.links || [], width, height)

  return (
    <div>
      <PageHeader icon={Share2} title={t('navKnowledgeGraph') || 'Knowledge graph'}
        subtitle={t('kgTooltip') || 'Interactive map of RAG retrievals: queries, sources, business domains, and extracted entities.'}
        accent="var(--primary-2)" />

      <Panel title={t('explore') || 'Explore'}>
        <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
          <div style={{ position: 'relative', flex: 1 }}>
            <Search size={15} style={{ position: 'absolute', left: 11, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-3)' }} />
            <input value={query} onChange={e => setQuery(e.target.value)} onKeyDown={e => e.key === 'Enter' && run()}
              placeholder={t('searchKnowledgeBase') || 'Search the knowledge base…'}
              style={{ width: '100%', background: 'var(--surface-2)', border: '1px solid var(--border-2)', borderRadius: 'var(--r)', padding: '9px 12px 9px 34px', color: 'var(--text)', fontSize: 14 }} />
          </div>
          <button className="btn btn-primary" onClick={() => run()} disabled={busy}>
            {busy ? <Loader2 size={14} className="spin" /> : <Share2 size={14} />} {t('map') || 'Map'}
          </button>
        </div>
      </Panel>

      <Panel title={t('retrievalGraph') || 'Retrieval graph'} style={{ marginTop: 18 }}>
        {!graphData ? <Empty text={t('kgEmpty') || "Search above to build the dynamic retrieval graph."} />
          : graphData.nodes.length === 0 ? <Empty text={t('noResults') || "No documents matched that query."} />
          : (
            <div style={{ position: 'relative', background: 'var(--bg-2)', borderRadius: 12, overflow: 'hidden', border: '1px solid var(--border-2)' }}>
              <svg viewBox={`0 0 ${width} ${height}`} style={{ width: '100%', height: 'auto', display: 'block', minHeight: 460 }}>
                {/* Links */}
                {graphData.links.map((l, i) => {
                  const s = positions[l.source]
                  const t_pos = positions[l.target]
                  if (!s || !t_pos) return null
                  const isRet = l.type === 'retrieval'
                  const isIntent = l.type === 'domain_intent'
                  return (
                    <g key={i}>
                      <line x1={s.x} y1={s.y} x2={t_pos.x} y2={t_pos.y}
                        stroke={isRet ? 'var(--primary-line)' : isIntent ? 'var(--warn)' : 'var(--border-strong)'}
                        strokeWidth={isRet ? 2 : isIntent ? 2 : 1.5} 
                        strokeDasharray={l.type === 'relation' ? '4 4' : l.type === 'entity_link' ? '2 2' : ''} 
                        opacity={isIntent ? 0.8 : 0.6} />
                      {isRet && l.score && (
                        <g>
                          <rect x={(s.x + t_pos.x)/2 - 14} y={(s.y + t_pos.y)/2 - 14} width={28} height={12} rx={6} fill="var(--surface-3)" opacity={0.9} />
                          <text x={(s.x + t_pos.x)/2} y={(s.y + t_pos.y)/2 - 5} fontSize={9} fontWeight={600} fill="var(--primary)" textAnchor="middle">
                            {Number(l.score).toFixed(2)}
                          </text>
                        </g>
                      )}
                    </g>
                  )
                })}

                {/* Nodes */}
                {graphData.nodes.map(n => {
                  const pos = positions[n.id]
                  if (!pos) return null
                  const isHover = hover?.id === n.id
                  const isSelected = selectedNode?.id === n.id
                  
                  if (n.type === 'query') {
                    return (
                      <g key={n.id} onClick={() => setSelectedNode(n)} style={{ cursor: 'pointer' }}>
                        <circle cx={pos.x} cy={pos.y} r={22} fill="var(--primary)" style={{ filter: 'drop-shadow(0 0 12px var(--primary-line))' }} />
                        <text x={pos.x} y={pos.y + 4} textAnchor="middle" fill="#ffffff" fontSize={11} fontWeight="bold">QUERY</text>
                        <text x={pos.x} y={pos.y + 36} textAnchor="middle" fontSize={12} fontWeight="bold" fill="var(--text)">
                          {n.label.length > 34 ? n.label.substring(0, 34) + '...' : n.label}
                        </text>
                      </g>
                    )
                  }
                  
                  if (n.type === 'document') {
                    return (
                      <g key={n.id} onClick={() => setSelectedNode(n)} onMouseEnter={() => setHover(n)} onMouseLeave={() => setHover(null)} style={{ cursor: 'pointer', transition: 'all 0.2s' }}>
                        <rect x={pos.x - 46} y={pos.y - 20} width={92} height={40} rx={8} 
                              fill={isSelected ? 'var(--primary-soft)' : isHover ? 'var(--surface-2)' : 'var(--surface)'} 
                              stroke={isSelected ? 'var(--primary)' : isHover ? 'var(--primary-line)' : 'var(--border-strong)'} 
                              strokeWidth={isSelected ? 2.5 : 1.5}
                              style={{ filter: isSelected ? 'drop-shadow(0 0 10px var(--primary-soft))' : 'none' }} />
                        <text x={pos.x} y={pos.y - 4} textAnchor="middle" fontSize={10} fontWeight={600} fill={isSelected ? 'var(--primary)' : 'var(--text)'}>
                          {n.label.substring(0, 14)}{n.label.length > 14 ? '...' : ''}
                        </text>
                        {n.score != null && (
                          <g>
                            <rect x={pos.x - 22} y={pos.y + 3} width={44} height={13} rx={6} fill="var(--surface-3)" />
                            <text x={pos.x} y={pos.y + 13} textAnchor="middle" fontSize={9} fontWeight={600} fill="var(--primary)">
                              {Number(n.score).toFixed(2)}
                            </text>
                          </g>
                        )}
                      </g>
                    )
                  }

                  if (n.type === 'domain') {
                    return (
                      <g key={n.id} onClick={() => setSelectedNode(n)} onMouseEnter={() => setHover(n)} onMouseLeave={() => setHover(null)} style={{ cursor: 'pointer' }}>
                        <rect x={pos.x - 38} y={pos.y - 14} width={76} height={28} rx={14} 
                              fill={isSelected ? 'var(--warn)' : 'color-mix(in srgb, var(--warn) 18%, transparent)'} 
                              stroke="var(--warn)" strokeWidth={isSelected ? 2.5 : 1.5} />
                        <text x={pos.x} y={pos.y + 4} textAnchor="middle" fontSize={10} fontWeight="bold" fill={isSelected ? '#1a1a1a' : 'var(--warn)'}>
                          {n.label}
                        </text>
                      </g>
                    )
                  }

                  if (n.type === 'entity') {
                    return (
                      <g key={n.id} onClick={() => setSelectedNode(n)} onMouseEnter={() => setHover(n)} onMouseLeave={() => setHover(null)} style={{ cursor: 'pointer' }}>
                        <circle cx={pos.x} cy={pos.y} r={8} fill={isSelected ? 'var(--ok)' : 'var(--surface-3)'} stroke="var(--ok)" strokeWidth={isSelected ? 2.5 : 1.5} />
                        <text x={pos.x} y={pos.y + 18} textAnchor="middle" fontSize={9} fontWeight={500} fill="var(--text-2)">{n.label}</text>
                      </g>
                    )
                  }

                  return null
                })}
              </svg>

              {/* Node Inspection Drawer */}
              {selectedNode && (
                <div style={{ 
                  position: 'absolute', top: 16, right: 16, width: 340, maxHeight: 'calc(100% - 32px)', 
                  background: 'var(--surface)', padding: 18, borderRadius: 12, border: '1px solid var(--border)', 
                  boxShadow: '0 12px 40px rgba(0,0,0,0.35)', zIndex: 20, display: 'flex', flexDirection: 'column', gap: 12, overflowY: 'auto' 
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      {selectedNode.type === 'document' ? <FileText size={16} color="var(--primary)" /> : selectedNode.type === 'domain' ? <Layers size={16} color="var(--warn)" /> : <Tag size={16} color="var(--ok)" />}
                      <span className="badge" style={{ fontSize: '.7rem', textTransform: 'uppercase' }}>{selectedNode.type}</span>
                    </div>
                    <button className="btn btn-ghost btn-icon btn-sm" onClick={() => setSelectedNode(null)}><X size={14} /></button>
                  </div>
                  
                  <div>
                    <h4 style={{ margin: 0, fontSize: '1rem', color: 'var(--text)', fontWeight: 600 }}>{selectedNode.label}</h4>
                    {selectedNode.score != null && (
                      <div style={{ marginTop: 6, fontSize: '.8rem', color: 'var(--primary)', fontWeight: 600 }}>
                        Relevance Score: {Number(selectedNode.score).toFixed(4)}
                      </div>
                    )}
                  </div>

                  {selectedNode.content && (
                    <div style={{ fontSize: '.82rem', color: 'var(--text-2)', lineHeight: 1.6, background: 'var(--bg-2)', padding: 12, borderRadius: 8, border: '1px solid var(--border-2)', maxHeight: 200, overflowY: 'auto' }}>
                      {selectedNode.content}
                    </div>
                  )}

                  <div style={{ display: 'flex', gap: 8, marginTop: 4 }}>
                    <button className="btn btn-primary btn-sm" style={{ flex: 1 }} onClick={() => {
                      const qTarget = selectedNode.type === 'document' ? selectedNode.label : `${query} ${selectedNode.label}`
                      navigate(`/chat?q=${encodeURIComponent(qTarget)}`)
                    }}>
                      <ArrowRight size={13} style={{ marginRight: 4 }} /> Ask Copilot
                    </button>
                    {selectedNode.type !== 'query' && (
                      <button className="btn btn-ghost btn-sm" onClick={() => {
                        setQuery(selectedNode.label)
                        run(selectedNode.label)
                      }}>
                        Pivot Graph
                      </button>
                    )}
                  </div>
                </div>
              )}

              {/* Hover tooltip for quick preview */}
              {hover && !selectedNode && (
                <div style={{ position: 'absolute', bottom: 16, right: 16, width: 300, background: 'var(--surface)', padding: 14, borderRadius: 10, border: '1px solid var(--border)', boxShadow: '0 8px 24px rgba(0,0,0,0.25)', pointerEvents: 'none', zIndex: 10 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                    <strong style={{ color: 'var(--text)', fontSize: '.9rem' }}>{hover.label}</strong>
                    <span className="badge" style={{ fontSize: '.65rem', textTransform: 'uppercase' }}>{hover.type}</span>
                  </div>
                  {hover.score != null && (
                    <div style={{ fontSize: '.75rem', color: 'var(--primary)', fontWeight: 600, marginBottom: 6 }}>
                      Score: {Number(hover.score).toFixed(4)}
                    </div>
                  )}
                  {hover.content && (
                    <div style={{ fontSize: '.75rem', color: 'var(--text-2)', lineHeight: 1.4, maxHeight: 60, overflow: 'hidden' }}>
                      "{hover.content}"
                    </div>
                  )}
                </div>
              )}

              {/* Legend */}
              <div style={{ position: 'absolute', top: 16, left: 16, background: 'var(--surface-2)', padding: '8px 12px', borderRadius: 8, border: '1px solid var(--border-2)', display: 'flex', flexDirection: 'column', gap: 6, fontSize: '.75rem', color: 'var(--text-2)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}><div style={{ width: 12, height: 12, borderRadius: '50%', background: 'var(--primary)' }} /> Query</div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}><div style={{ width: 16, height: 10, borderRadius: 3, background: 'var(--surface)', border: '1px solid var(--border-strong)' }} /> Document Card</div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}><div style={{ width: 14, height: 8, borderRadius: 4, background: 'var(--warn)' }} /> Business Domain</div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}><div style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--ok)' }} /> Extracted Entity</div>
              </div>
            </div>
          )}
      </Panel>
    </div>
  )
}
