import { useState, useMemo, useEffect, useRef } from 'react'
import { useSearchParams } from 'react-router-dom'
import { Share2, Search, Loader2 } from 'lucide-react'
import { PageHeader, Panel, Empty } from '../components/ui'
import { useTranslation } from '../i18n/I18nContext'
import * as api from '../api'

function useForceSimulation(nodes, links, width, height) {
  const [positions, setPositions] = useState({})
  
  useEffect(() => {
    if (!nodes.length) return
    let currentPositions = {}
    nodes.forEach((n, i) => {
      // Initialize in a circle around center
      const angle = (i / nodes.length) * Math.PI * 2
      const radius = 100 + Math.random() * 50
      currentPositions[n.id] = {
        x: width / 2 + Math.cos(angle) * radius,
        y: height / 2 + Math.sin(angle) * radius,
        vx: 0, vy: 0
      }
    })
    // Pin the query node to the center
    if (currentPositions['query']) {
      currentPositions['query'].x = width / 2
      currentPositions['query'].y = height / 2
    }

    let animationFrameId
    let alpha = 1.0

    const tick = () => {
      alpha *= 0.95
      if (alpha < 0.01) return

      const nextPositions = { ...currentPositions }
      const k = 0.5 * alpha

      // Spring force
      links.forEach(link => {
        const source = nextPositions[link.source]
        const target = nextPositions[link.target]
        if (!source || !target) return
        const dx = target.x - source.x
        const dy = target.y - source.y
        const dist = Math.sqrt(dx * dx + dy * dy) || 1
        const targetDist = link.distance || 100
        const force = (dist - targetDist) * 0.1 * alpha
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
          if (dist < 300) {
            const force = (300 - dist) * 0.05 * alpha
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
        // Bounds
        pos.x = Math.max(50, Math.min(width - 50, pos.x))
        pos.y = Math.max(50, Math.min(height - 50, pos.y))
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
  const [searchParams, setSearchParams] = useSearchParams()
  // A "View Graph" deep-link from the Copilot (?q=<query>) should open the graph for that
  // specific query/entity, not the default overview — previously this param was read by
  // nobody, so every deep-link silently fell back to the hardcoded 'Overview' seed query.
  const [query, setQuery] = useState(() => searchParams.get('q') || 'Overview')
  const [busy, setBusy] = useState(false)
  const [graphData, setGraphData] = useState(null)
  const [hover, setHover] = useState(null)
  
  const width = 800
  const height = 600

  const run = async () => {
    if (!query.trim()) return
    setBusy(true)
    try {
      const r = await api.searchKnowledge(query, 6)
      const res = r?.data?.results || []
      
      if (res.length === 0) {
        setGraphData({ nodes: [], links: [] })
        return
      }

      const nodes = [{ id: 'query', type: 'query', label: query }]
      const links = []
      
      const terms = ['Finance', 'HR', 'Growth', 'Operations', 'Risk', 'ESG', 'IT', 'Logistics']

      res.forEach((d, i) => {
        const docId = `doc-${i}`
        nodes.push({ 
          id: docId, 
          type: 'document', 
          label: d.title || `Document ${i+1}`, 
          score: d.score,
          content: d.content 
        })
        links.push({ source: 'query', target: docId, type: 'retrieval', score: d.score, distance: 150 })

        // Extract Domains
        const t_content = (d.title + ' ' + (d.content || '')).toLowerCase()
        const mentionedDomains = terms.filter(x => t_content.includes(x.toLowerCase()))
        
        mentionedDomains.forEach(dom => {
          const domId = `dom-${dom}`
          if (!nodes.find(n => n.id === domId)) {
            nodes.push({ id: domId, type: 'domain', label: dom })
          }
          links.push({ source: docId, target: domId, type: 'relation', distance: 100 })
        })

        // Naive Entity Extraction for richer graph (Capitalized words > 5 chars)
        const words = (d.content || '').split(/[\s,.-]+/).filter(w => w.length > 5 && w[0] === w[0].toUpperCase() && !terms.includes(w))
        const entities = [...new Set(words)].slice(0, 2)
        
        entities.forEach(ent => {
          const entId = `ent-${ent}`
          if (!nodes.find(n => n.id === entId)) {
            nodes.push({ id: entId, type: 'entity', label: ent })
          }
          links.push({ source: docId, target: entId, type: 'entity_link', distance: 80 })
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
          <button className="btn btn-primary" onClick={run} disabled={busy}>
            {busy ? <Loader2 size={14} className="spin" /> : <Share2 size={14} />} {t('map') || 'Map'}
          </button>
        </div>
      </Panel>

      <Panel title={t('retrievalGraph') || 'Retrieval graph'} style={{ marginTop: 18 }}>
        {!graphData ? <Empty text={t('kgEmpty') || "Search above to build the dynamic retrieval graph."} />
          : graphData.nodes.length === 0 ? <Empty text={t('noResults') || "No documents matched that query."} />
          : (
            <div style={{ position: 'relative', background: 'var(--bg-2)', borderRadius: 12, overflow: 'hidden', border: '1px solid var(--border-2)' }}>
              <svg viewBox={`0 0 ${width} ${height}`} style={{ width: '100%', height: 'auto', display: 'block', minHeight: 400 }}>
                {/* Links */}
                {graphData.links.map((l, i) => {
                  const s = positions[l.source]
                  const t_pos = positions[l.target]
                  if (!s || !t_pos) return null
                  const isRet = l.type === 'retrieval'
                  return (
                    <g key={i}>
                      <line x1={s.x} y1={s.y} x2={t_pos.x} y2={t_pos.y}
                        stroke={isRet ? 'var(--primary-line)' : 'var(--border-strong)'}
                        strokeWidth={isRet ? 2 : 1.5} 
                        strokeDasharray={l.type === 'relation' ? '4 4' : l.type === 'entity_link' ? '2 2' : ''} 
                        opacity={0.6} />
                      {isRet && l.score && (
                        <text x={(s.x + t_pos.x)/2} y={(s.y + t_pos.y)/2 - 5} fontSize={10} fill="var(--primary)" textAnchor="middle">
                          {Number(l.score).toFixed(2)}
                        </text>
                      )}
                    </g>
                  )
                })}

                {/* Nodes */}
                {graphData.nodes.map(n => {
                  const pos = positions[n.id]
                  if (!pos) return null
                  const isHover = hover?.id === n.id
                  
                  if (n.type === 'query') {
                    return (
                      <g key={n.id}>
                        <circle cx={pos.x} cy={pos.y} r={16} fill="var(--primary)" style={{ filter: 'drop-shadow(0 0 8px var(--primary-line))' }} />
                        <text x={pos.x} y={pos.y + 26} textAnchor="middle" fontSize={13} fontWeight="bold" fill="var(--text)">{n.label}</text>
                      </g>
                    )
                  }
                  
                  if (n.type === 'document') {
                    return (
                      <g key={n.id} onMouseEnter={() => setHover(n)} onMouseLeave={() => setHover(null)} style={{ cursor: 'pointer', transition: 'all 0.2s' }}>
                        <rect x={pos.x - 12} y={pos.y - 12} width={24} height={24} rx={4} fill="var(--surface-3)" stroke={isHover ? 'var(--primary)' : 'var(--border-strong)'} strokeWidth={2} />
                        <text x={pos.x} y={pos.y - 16} textAnchor="middle" fontSize={11} fontWeight={600} fill={isHover ? 'var(--primary)' : 'var(--text)'}>{n.label.substring(0,20)}{n.label.length > 20 ? '...' : ''}</text>
                      </g>
                    )
                  }

                  if (n.type === 'domain') {
                    return (
                      <g key={n.id} onMouseEnter={() => setHover(n)} onMouseLeave={() => setHover(null)} style={{ cursor: 'pointer' }}>
                        <polygon points={`${pos.x},${pos.y-12} ${pos.x+12},${pos.y} ${pos.x},${pos.y+12} ${pos.x-12},${pos.y}`} fill="var(--warn)" opacity={0.8} />
                        <text x={pos.x} y={pos.y + 20} textAnchor="middle" fontSize={10} fill="var(--warn)">{n.label}</text>
                      </g>
                    )
                  }

                  if (n.type === 'entity') {
                    return (
                      <g key={n.id} onMouseEnter={() => setHover(n)} onMouseLeave={() => setHover(null)} style={{ cursor: 'pointer' }}>
                        <circle cx={pos.x} cy={pos.y} r={6} fill="var(--ok)" />
                        <text x={pos.x} y={pos.y + 14} textAnchor="middle" fontSize={9} fill="var(--text-3)">{n.label}</text>
                      </g>
                    )
                  }

                  return null
                })}
              </svg>

              {/* Enhanced Info Panel Overlay */}
              {hover && (
                <div style={{ position: 'absolute', bottom: 16, right: 16, width: 320, background: 'var(--surface)', padding: 16, borderRadius: 12, border: '1px solid var(--border)', boxShadow: '0 8px 30px rgba(0,0,0,0.3)', pointerEvents: 'none', zIndex: 10 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                    <strong style={{ color: 'var(--text)', fontSize: '.95rem' }}>{hover.label}</strong>
                    <span className="badge" style={{ fontSize: '.7rem', textTransform: 'uppercase' }}>{hover.type}</span>
                  </div>
                  {hover.score != null && (
                    <div style={{ fontSize: '.8rem', color: 'var(--primary)', marginBottom: 8, fontWeight: 600 }}>
                      Relevance Score: {Number(hover.score).toFixed(4)}
                    </div>
                  )}
                  {hover.content && (
                    <div style={{ fontSize: '.8rem', color: 'var(--text-2)', lineHeight: 1.5, maxHeight: 100, overflow: 'hidden', textOverflow: 'ellipsis', display: '-webkit-box', WebkitLineClamp: 4, WebkitBoxOrient: 'vertical' }}>
                      "{hover.content}"
                    </div>
                  )}
                </div>
              )}

              {/* Legend */}
              <div style={{ position: 'absolute', top: 16, left: 16, background: 'var(--surface-2)', padding: '8px 12px', borderRadius: 8, border: '1px solid var(--border-2)', display: 'flex', flexDirection: 'column', gap: 6, fontSize: '.75rem', color: 'var(--text-2)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}><div style={{ width: 12, height: 12, borderRadius: '50%', background: 'var(--primary)' }} /> Query</div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}><div style={{ width: 12, height: 12, borderRadius: 2, background: 'var(--surface-3)', border: '1px solid var(--border-strong)' }} /> Document Source</div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}><div style={{ width: 12, height: 12, background: 'var(--warn)', clipPath: 'polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%)' }} /> Business Domain</div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}><div style={{ width: 12, height: 12, borderRadius: '50%', background: 'var(--ok)' }} /> Extracted Entity</div>
              </div>
            </div>
          )}
      </Panel>
    </div>
  )
}
