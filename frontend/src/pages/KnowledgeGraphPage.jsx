import { useState, useMemo, useEffect, useRef } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { 
  Share2, Search, Loader2, X, FileText, Tag, Layers, ArrowRight, 
  ExternalLink, Cpu, DollarSign, Users, Settings2, Leaf, ShieldAlert, 
  TrendingUp, Truck, Sparkles, Building2, Link2, Info, MessageSquare, Database
} from 'lucide-react'
import { PageHeader, Panel, Empty } from '../components/ui'
import { useTranslation } from '../i18n/I18nContext'
import * as api from '../api'

const DOMAIN_CONFIG = {
  IT: {
    color: '#06b6d4',
    bg: 'rgba(6, 182, 212, 0.12)',
    border: '#0891b2',
    icon: Cpu,
    kpis: ['API P99 Latency', 'System Uptime', 'Deployment Frequency', 'Active Users'],
    patterns: ['it', 'informatique', 'ordinateur', 'serveur', 'materiel', 'infrastructure', 'tech', 'software', 'cloud', 'systeme', 'latency', 'uptime']
  },
  Finance: {
    color: '#10b981',
    bg: 'rgba(16, 185, 129, 0.12)',
    border: '#059669',
    icon: DollarSign,
    kpis: ['Revenue', 'ARR', 'COGS', 'Capital Expenditure', 'Cash Balance'],
    patterns: ['finance', 'financial', 'financement', 'achat', 'capex', 'opex', 'cost', 'revenue', 'budget', 'tresorerie', 'cogs', 'depense']
  },
  Operations: {
    color: '#f59e0b',
    bg: 'rgba(245, 158, 11, 0.12)',
    border: '#d97706',
    icon: Settings2,
    kpis: ['Availability', 'Capacity Utilization', 'Cycle Time Efficiency', 'Defect Rate'],
    patterns: ['operations', 'ops', 'production', 'oee', 'defect', 'qualite', 'capacity', 'utilization']
  },
  HR: {
    color: '#a855f7',
    bg: 'rgba(168, 85, 247, 0.12)',
    border: '#9333ea',
    icon: Users,
    kpis: ['Headcount', 'Annual Employee Turnover', 'Absenteeism Rate', 'Cost Per Hire'],
    patterns: ['hr', 'people', 'employee', 'headcount', 'personnel', 'recrutement', 'salaire', 'turnover', 'absenteeism']
  },
  Logistics: {
    color: '#3b82f6',
    bg: 'rgba(59, 130, 246, 0.12)',
    border: '#2563eb',
    icon: Truck,
    kpis: ['Average Lead Time', 'Carrying Cost of Inventory', 'Inventory Turnover'],
    patterns: ['logistics', 'delivery', 'warehouse', 'freight', 'expedition', 'stock', 'inventory', 'lead time']
  },
  Growth: {
    color: '#6366f1',
    bg: 'rgba(99, 102, 241, 0.12)',
    border: '#4f46e5',
    icon: TrendingUp,
    kpis: ['ARPU', 'ARR', 'CAC', 'Conversion Rate', 'Net Retention Rate'],
    patterns: ['growth', 'sales', 'customer', 'mrr', 'arr', 'churn', 'arpu', 'cac']
  },
  Risk: {
    color: '#f43f5e',
    bg: 'rgba(244, 63, 94, 0.12)',
    border: '#e11d48',
    icon: ShieldAlert,
    kpis: ['Audit Compliance Score', 'Privacy Incident Count', 'Risk Index'],
    patterns: ['risk', 'audit', 'compliance', 'conformite', 'incident', 'securite']
  },
  ESG: {
    color: '#14b8a6',
    bg: 'rgba(20, 184, 166, 0.12)',
    border: '#0d9488',
    icon: Leaf,
    kpis: ['Carbon Intensity per Revenue', 'Renewable Energy Ratio', 'Board Diversity Ratio'],
    patterns: ['esg', 'carbon', 'emission', 'renewable', 'energie', 'durabilite', 'diversity']
  }
}

// Inter-departmental operational and governance relationships
const DEPARTMENT_RELATIONSHIPS = [
  { 
    d1: 'IT', d2: 'Finance', 
    relation: 'IT Procurement & Capital Expenditure',
    description: 'Hardware, cloud compute and server infrastructure acquisitions funded via Finance Capex budget.' 
  },
  { 
    d1: 'Finance', d2: 'Operations', 
    relation: 'Operating Budget & Equipment Capex',
    description: 'Operational plant machinery funding, production maintenance contracts, and inventory financing.' 
  },
  { 
    d1: 'Operations', d2: 'Logistics', 
    relation: 'Supply Chain & Warehouse Handoff',
    description: 'Manufacturing output handoff to inventory warehousing, freight routing, and customer dispatch.' 
  },
  { 
    d1: 'HR', d2: 'Operations', 
    relation: 'Plant Staffing & Safety Compliance',
    description: 'Shift workforce scheduling, operator safety certification, and plant labor capacity planning.' 
  },
  { 
    d1: 'Growth', d2: 'Finance', 
    relation: 'CAC / LTV Budget Governance',
    description: 'Marketing acquisition expenditure governance against Annual Recurring Revenue (ARR) growth targets.' 
  },
  { 
    d1: 'Risk', d2: 'Finance', 
    relation: 'Audit Controls & Treasury Compliance',
    description: 'Statutory audit controls, fraud monitoring, capital reserve verification, and liquidity limits.' 
  },
  { 
    d1: 'Risk', d2: 'IT', 
    relation: 'Cybersecurity Posture & SLA Guarantees',
    description: 'Security incident monitoring, data privacy governance, and API P99 SLA resilience.' 
  },
  { 
    d1: 'ESG', d2: 'Operations', 
    relation: 'Emissions Standards & Energy Efficiency',
    description: 'Clean energy transition across production sites, waste reduction, and carbon intensity per revenue.' 
  },
  { 
    d1: 'HR', d2: 'ESG', 
    relation: 'Workplace Inclusion & Human Capital',
    description: 'Board diversity ratios, equitable compensation standards, and employee well-being governance.' 
  }
]

function useForceSimulation(nodes, links, width, height) {
  const [positions, setPositions] = useState({})
  
  useEffect(() => {
    if (!nodes.length) return
    let currentPositions = {}
    nodes.forEach((n, i) => {
      const angle = (i / nodes.length) * Math.PI * 2
      const radius = n.type === 'domain' ? 140 : n.type === 'document' ? 220 : 280
      currentPositions[n.id] = {
        x: width / 2 + Math.cos(angle) * (radius + (i % 3) * 20),
        y: height / 2 + Math.sin(angle) * (radius + (i % 3) * 20),
        vx: 0, vy: 0
      }
    })
    // Pin query node to center
    if (currentPositions['query']) {
      currentPositions['query'].x = width / 2
      currentPositions['query'].y = height / 2
    }

    let animationFrameId
    let alpha = 1.0

    const tick = () => {
      alpha *= 0.94
      if (alpha < 0.005) return

      const nextPositions = { ...currentPositions }

      // Spring forces
      links.forEach(link => {
        const source = nextPositions[link.source]
        const target = nextPositions[link.target]
        if (!source || !target) return
        const dx = target.x - source.x
        const dy = target.y - source.y
        const dist = Math.sqrt(dx * dx + dy * dy) || 1
        const targetDist = link.distance || 130
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
          const minDist = nodes[i].type === 'document' || nodes[j].type === 'document' ? 190 : 150
          if (dist < minDist) {
            const force = (minDist - dist) * 0.08 * alpha
            const fx = (dx / dist) * force
            const fy = (dy / dist) * force
            if (nodes[i].id !== 'query') { n1.vx -= fx; n1.vy -= fy }
            if (nodes[j].id !== 'query') { n2.vx += fx; n2.vy += fy }
          }
        }
      }

      // Update positions with bounding
      nodes.forEach(n => {
        if (n.id === 'query') return
        const pos = nextPositions[n.id]
        pos.x += pos.vx
        pos.y += pos.vy
        pos.vx *= 0.78
        pos.vy *= 0.78
        pos.x = Math.max(90, Math.min(width - 90, pos.x))
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
  const [query, setQuery] = useState(() => searchParams.get('q') || "financement du deparment it pour achat d'ordinateur et de serveur")
  const [busy, setBusy] = useState(false)
  const [graphData, setGraphData] = useState(null)
  const [hover, setHover] = useState(null)
  const [selectedNode, setSelectedNode] = useState(null)
  const [selectedLink, setSelectedLink] = useState(null)
  
  const width = 940
  const height = 660

  const run = async (searchTarget) => {
    const q = (searchTarget ?? query).trim()
    if (!q) return
    setBusy(true)
    setSelectedNode(null)
    setSelectedLink(null)
    try {
      const r = await api.searchKnowledge(q, 6)
      const res = r?.data?.results || []
      
      if (res.length === 0) {
        setGraphData({ nodes: [], links: [] })
        return
      }

      const nodes = [{ id: 'query', type: 'query', label: q }]
      const links = []
      
      const qLower = q.toLowerCase()
      const queryDomains = Object.entries(DOMAIN_CONFIG)
        .filter(([name, conf]) => conf.patterns.some(p => qLower.includes(p)))
        .map(([name]) => name)

      queryDomains.forEach(domName => {
        const domId = `dom-${domName}`
        if (!nodes.find(n => n.id === domId)) {
          nodes.push({ 
            id: domId, 
            type: 'domain', 
            label: domName,
            config: DOMAIN_CONFIG[domName],
            isQueryIntent: true,
            documents: []
          })
        }
        links.push({ 
          id: `link-query-${domId}`,
          source: 'query', 
          target: domId, 
          type: 'domain_intent', 
          label: 'Intent Match',
          distance: 140 
        })
      })

      const extractedEntityMap = new Map()

      res.forEach((d, i) => {
        const docId = `doc-${i}`
        const docLabel = d.title || `Document ${i+1}`
        const docNode = { 
          id: docId, 
          type: 'document', 
          label: docLabel, 
          score: d.score,
          content: d.content || '',
          domains: [],
          entities: []
        }
        nodes.push(docNode)
        links.push({ 
          id: `link-query-${docId}`,
          source: 'query', 
          target: docId, 
          type: 'retrieval', 
          score: d.score, 
          distance: 180 
        })

        const textContent = (docLabel + ' ' + (d.content || '')).toLowerCase()
        const matchedDomains = Object.entries(DOMAIN_CONFIG)
          .filter(([name, conf]) => conf.patterns.some(p => textContent.includes(p)))
          .map(([name]) => name)
        
        matchedDomains.forEach(domName => {
          const domId = `dom-${domName}`
          let domNode = nodes.find(n => n.id === domId)
          if (!domNode) {
            domNode = { 
              id: domId, 
              type: 'domain', 
              label: domName, 
              config: DOMAIN_CONFIG[domName],
              isQueryIntent: queryDomains.includes(domName),
              documents: []
            }
            nodes.push(domNode)
          }
          if (!domNode.documents.includes(docLabel)) {
            domNode.documents.push(docLabel)
          }
          docNode.domains.push(domName)

          links.push({ 
            id: `link-${docId}-${domId}`,
            source: docId, 
            target: domId, 
            type: 'relation', 
            label: 'Belongs to',
            distance: 120 
          })
        })

        // Clean entity extraction
        const rawTokens = (d.content || '').split(/[\s,.;:!?/\\|"'`~@#$%^&*()+=[\]{}<>«»]+/)
        const validEntities = rawTokens.filter(tok => 
          /^[A-ZÀ-ÖØ-ß][a-zà-öø-ÿ0-9_-]{3,22}$/.test(tok) &&
          !Object.keys(DOMAIN_CONFIG).some(dom => dom.toLowerCase() === tok.toLowerCase()) &&
          !['Pour', 'Avec', 'Dans', 'Cette', 'Sont', 'Comme', 'Total', 'Plus', 'Tous', 'Aussi', 'Leur', 'Entre'].includes(tok)
        )
        const uniqueEntities = [...new Set(validEntities)].slice(0, 3)
        
        uniqueEntities.forEach(ent => {
          const entId = `ent-${ent}`
          let entNode = nodes.find(n => n.id === entId)
          if (!entNode) {
            entNode = { 
              id: entId, 
              type: 'entity', 
              label: ent,
              occurrences: 0,
              documents: [],
              domains: []
            }
            nodes.push(entNode)
          }
          entNode.occurrences += 1
          if (!entNode.documents.includes(docLabel)) entNode.documents.push(docLabel)
          matchedDomains.forEach(dm => {
            if (!entNode.domains.includes(dm)) entNode.domains.push(dm)
          })
          docNode.entities.push(ent)

          links.push({ 
            id: `link-${docId}-${entId}`,
            source: docId, 
            target: entId, 
            type: 'entity_link', 
            label: 'Mentions',
            distance: 95 
          })
        })
      })

      // Cross-Department Relationships:
      // Scan all domains active in the graph and connect those with explicit organizational links
      const activeDomains = nodes.filter(n => n.type === 'domain').map(n => n.label)
      const addedDepartmentLinks = new Set()

      DEPARTMENT_RELATIONSHIPS.forEach(rel => {
        if (activeDomains.includes(rel.d1) && activeDomains.includes(rel.d2)) {
          const linkKey = [rel.d1, rel.d2].sort().join('--')
          if (!addedDepartmentLinks.has(linkKey)) {
            addedDepartmentLinks.add(linkKey)
            links.push({
              id: `rel-${rel.d1}-${rel.d2}`,
              source: `dom-${rel.d1}`,
              target: `dom-${rel.d2}`,
              type: 'department_relation',
              label: rel.relation,
              description: rel.description,
              d1: rel.d1,
              d2: rel.d2,
              distance: 190
            })
          }
        }
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

  // Quick stats
  const stats = useMemo(() => {
    if (!graphData?.nodes) return { docs: 0, domains: 0, entities: 0, deptRels: 0 }
    return {
      docs: graphData.nodes.filter(n => n.type === 'document').length,
      domains: graphData.nodes.filter(n => n.type === 'domain').length,
      entities: graphData.nodes.filter(n => n.type === 'entity').length,
      deptRels: graphData.links.filter(l => l.type === 'department_relation').length,
    }
  }, [graphData])

  return (
    <div>
      <PageHeader icon={Share2} title={t('navKnowledgeGraph') || 'Knowledge graph'}
        subtitle={t('kgTooltip') || 'Interactive map of RAG retrievals: queries, sources, cross-department relationships, and extracted entities.'}
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
            {busy ? <Loader2 size={14} className="spin" /> : <Share2 size={14} />} {t('map') || 'Map Graph'}
          </button>
        </div>

        {/* Quick query presets */}
        <div style={{ display: 'flex', gap: 8, marginTop: 12, flexWrap: 'wrap', alignItems: 'center' }}>
          <span style={{ fontSize: '.75rem', color: 'var(--text-3)', fontWeight: 600 }}>Try queries:</span>
          {[
            "financement du deparment it pour achat d'ordinateur et de serveur",
            "cross-domain audit compliance and cybersecurity posture",
            "workforce capacity planning and production equipment capex",
            "renewable energy transition and operations facility emissions"
          ].map((preset, idx) => (
            <button 
              key={idx} 
              className="badge" 
              style={{ 
                cursor: 'pointer', 
                background: query === preset ? 'var(--primary-soft)' : 'var(--surface-2)',
                color: query === preset ? 'var(--primary)' : 'var(--text-2)',
                border: '1px solid var(--border)',
                padding: '3px 8px',
                fontSize: '.72rem'
              }}
              onClick={() => {
                setQuery(preset)
                run(preset)
              }}
            >
              {preset.length > 38 ? preset.substring(0, 38) + '…' : preset}
            </button>
          ))}
        </div>
      </Panel>

      <Panel 
        title={t('retrievalGraph') || 'Retrieval graph'} 
        subtitle={graphData && `${stats.docs} Documents · ${stats.domains} Business Domains · ${stats.entities} Entities · ${stats.deptRels} Department Relations`}
        style={{ marginTop: 18 }}
      >
        {!graphData ? <Empty text={t('kgEmpty') || "Search above to build the dynamic retrieval graph."} />
          : graphData.nodes.length === 0 ? <Empty text={t('noResults') || "No documents matched that query."} />
          : (
            <div style={{ position: 'relative', background: 'var(--bg-2)', borderRadius: 14, overflow: 'hidden', border: '1px solid var(--border-2)' }}>
              <svg viewBox={`0 0 ${width} ${height}`} style={{ width: '100%', height: 'auto', display: 'block', minHeight: 520 }}>
                <defs>
                  {/* Glowing gradients */}
                  <linearGradient id="grad-query" x1="0" y1="0" x2="1" y2="1">
                    <stop offset="0%" stopColor="#6366f1" />
                    <stop offset="100%" stopColor="#4f46e5" />
                  </linearGradient>
                  <linearGradient id="grad-doc" x1="0" y1="0" x2="1" y2="1">
                    <stop offset="0%" stopColor="var(--surface-2)" />
                    <stop offset="100%" stopColor="var(--surface)" />
                  </linearGradient>
                  
                  {/* Filters for subtle glows */}
                  <filter id="glow-query" x="-30%" y="-30%" width="160%" height="160%">
                    <feDropShadow dx="0" dy="0" stdDeviation="6" floodColor="#6366f1" floodOpacity="0.5" />
                  </filter>
                  <filter id="glow-dept" x="-30%" y="-30%" width="160%" height="160%">
                    <feDropShadow dx="0" dy="0" stdDeviation="5" floodColor="#f59e0b" floodOpacity="0.4" />
                  </filter>
                  <filter id="glow-selected" x="-30%" y="-30%" width="160%" height="160%">
                    <feDropShadow dx="0" dy="0" stdDeviation="7" floodColor="var(--primary)" floodOpacity="0.6" />
                  </filter>
                </defs>

                {/* Links */}
                {graphData.links.map((l, i) => {
                  const s = positions[l.source]
                  const t_pos = positions[l.target]
                  if (!s || !t_pos) return null
                  const isRet = l.type === 'retrieval'
                  const isIntent = l.type === 'domain_intent'
                  const isDeptRel = l.type === 'department_relation'
                  const isEntity = l.type === 'entity_link'
                  const isSelected = selectedLink?.id === l.id

                  let strokeColor = 'var(--border-strong)'
                  let strokeWidth = 1.5
                  let strokeDash = ''
                  let opacity = 0.55

                  if (isRet) {
                    strokeColor = 'var(--primary-line)'
                    strokeWidth = 2.2
                    opacity = 0.75
                  } else if (isIntent) {
                    strokeColor = '#f59e0b'
                    strokeWidth = 2
                    strokeDash = '5 3'
                    opacity = 0.85
                  } else if (isDeptRel) {
                    strokeColor = '#ec4899'
                    strokeWidth = 2.6
                    strokeDash = '6 4'
                    opacity = 0.95
                  } else if (isEntity) {
                    strokeColor = 'var(--ok)'
                    strokeWidth = 1.2
                    strokeDash = '2 2'
                    opacity = 0.45
                  }

                  const midX = (s.x + t_pos.x) / 2
                  const midY = (s.y + t_pos.y) / 2

                  return (
                    <g key={l.id || i} style={{ cursor: isDeptRel ? 'pointer' : 'default' }} onClick={() => isDeptRel && setSelectedLink(l)}>
                      <line 
                        x1={s.x} y1={s.y} x2={t_pos.x} y2={t_pos.y}
                        stroke={isSelected ? '#ec4899' : strokeColor}
                        strokeWidth={isSelected ? 4 : strokeWidth} 
                        strokeDasharray={strokeDash} 
                        opacity={opacity} 
                      />

                      {/* Score pill on retrieval links */}
                      {isRet && l.score != null && (
                        <g transform={`translate(${midX}, ${midY})`}>
                          <rect x={-18} y={-9} width={36} height={18} rx={9} fill="var(--surface-3)" stroke="var(--primary-line)" strokeWidth={1} />
                          <text x={0} y={4} fontSize={9.5} fontWeight={700} fill="var(--primary)" textAnchor="middle">
                            {Number(l.score).toFixed(2)}
                          </text>
                        </g>
                      )}

                      {/* Department Relationship Badge */}
                      {isDeptRel && (
                        <g transform={`translate(${midX}, ${midY})`}>
                          <rect x={-64} y={-11} width={128} height={22} rx={11} fill="#ec4899" opacity={0.92} style={{ filter: 'drop-shadow(0 2px 6px rgba(236, 72, 153, 0.4))' }} />
                          <text x={0} y={4} fontSize={8.5} fontWeight={700} fill="#ffffff" textAnchor="middle">
                            {l.label.length > 20 ? l.label.substring(0, 20) + '…' : l.label}
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
                  
                  // 1. Query Node
                  if (n.type === 'query') {
                    return (
                      <g key={n.id} onClick={() => { setSelectedNode(n); setSelectedLink(null) }} style={{ cursor: 'pointer' }}>
                        <circle cx={pos.x} cy={pos.y} r={28} fill="url(#grad-query)" style={{ filter: 'url(#glow-query)' }} />
                        <circle cx={pos.x} cy={pos.y} r={34} fill="none" stroke="#6366f1" strokeWidth={1.5} strokeDasharray="4 4" opacity={0.6} />
                        <text x={pos.x} y={pos.y + 4} textAnchor="middle" fill="#ffffff" fontSize={11} fontWeight={800} letterSpacing={0.8}>QUERY</text>
                        <text x={pos.x} y={pos.y + 46} textAnchor="middle" fontSize={12} fontWeight={700} fill="var(--text)">
                          {n.label.length > 36 ? n.label.substring(0, 36) + '…' : n.label}
                        </text>
                      </g>
                    )
                  }
                  
                  // 2. Document Node (Rich Card)
                  if (n.type === 'document') {
                    const cardW = 118
                    const cardH = 50
                    return (
                      <g 
                        key={n.id} 
                        onClick={() => { setSelectedNode(n); setSelectedLink(null) }} 
                        onMouseEnter={() => setHover(n)} 
                        onMouseLeave={() => setHover(null)} 
                        style={{ cursor: 'pointer', transition: 'transform 0.15s ease' }}
                      >
                        <rect 
                          x={pos.x - cardW / 2} 
                          y={pos.y - cardH / 2} 
                          width={cardW} 
                          height={cardH} 
                          rx={10} 
                          fill="url(#grad-doc)" 
                          stroke={isSelected ? 'var(--primary)' : isHover ? 'var(--primary-line)' : 'var(--border-strong)'} 
                          strokeWidth={isSelected ? 2.5 : 1.4}
                          style={{ filter: isSelected ? 'url(#glow-selected)' : 'drop-shadow(0 4px 12px rgba(0,0,0,0.15))' }} 
                        />
                        {/* Document Icon Glyph */}
                        <rect x={pos.x - cardW / 2 + 8} y={pos.y - 14} width={18} height={20} rx={3} fill="var(--surface-3)" stroke="var(--border)" />
                        <text x={pos.x - cardW / 2 + 17} y={pos.y} textAnchor="middle" fontSize={9} fill="var(--primary)" fontWeight={700}>DOC</text>

                        {/* Document Title */}
                        <text 
                          x={pos.x - cardW / 2 + 32} 
                          y={pos.y - 4} 
                          fontSize={10} 
                          fontWeight={600} 
                          fill={isSelected ? 'var(--primary)' : 'var(--text)'}
                        >
                          {n.label.length > 13 ? n.label.substring(0, 13) + '…' : n.label}
                        </text>

                        {/* Score Pill */}
                        {n.score != null && (
                          <g transform={`translate(${pos.x - cardW / 2 + 32}, ${pos.y + 6})`}>
                            <rect width={48} height={13} rx={6} fill="var(--surface-3)" />
                            <text x={24} y={10} textAnchor="middle" fontSize={8.5} fontWeight={700} fill="var(--primary)">
                              {Number(n.score).toFixed(3)}
                            </text>
                          </g>
                        )}
                      </g>
                    )
                  }

                  // 3. Domain / Department Node (Glowing Badge)
                  if (n.type === 'domain') {
                    const cfg = n.config || DOMAIN_CONFIG[n.label] || { color: '#f59e0b', bg: 'rgba(245, 158, 11, 0.12)', border: '#d97706' }
                    const pillW = 96
                    const pillH = 34
                    return (
                      <g 
                        key={n.id} 
                        onClick={() => { setSelectedNode(n); setSelectedLink(null) }} 
                        onMouseEnter={() => setHover(n)} 
                        onMouseLeave={() => setHover(null)} 
                        style={{ cursor: 'pointer' }}
                      >
                        <rect 
                          x={pos.x - pillW / 2} 
                          y={pos.y - pillH / 2} 
                          width={pillW} 
                          height={pillH} 
                          rx={17} 
                          fill={isSelected ? cfg.color : cfg.bg} 
                          stroke={cfg.color} 
                          strokeWidth={isSelected ? 2.8 : 1.8}
                          style={{ filter: isSelected ? 'url(#glow-selected)' : n.isQueryIntent ? 'url(#glow-dept)' : 'none' }} 
                        />
                        <text 
                          x={pos.x} 
                          y={pos.y + 4} 
                          textAnchor="middle" 
                          fontSize={11} 
                          fontWeight={700} 
                          fill={isSelected ? '#ffffff' : cfg.color}
                          letterSpacing={0.4}
                        >
                          {n.label.toUpperCase()}
                        </text>
                      </g>
                    )
                  }

                  // 4. Extracted Entity Node (Compact Token)
                  if (n.type === 'entity') {
                    return (
                      <g 
                        key={n.id} 
                        onClick={() => { setSelectedNode(n); setSelectedLink(null) }} 
                        onMouseEnter={() => setHover(n)} 
                        onMouseLeave={() => setHover(null)} 
                        style={{ cursor: 'pointer' }}
                      >
                        <circle 
                          cx={pos.x} cy={pos.y} r={10} 
                          fill={isSelected ? 'var(--ok)' : 'var(--surface-2)'} 
                          stroke="var(--ok)" 
                          strokeWidth={isSelected ? 2.5 : 1.6} 
                          style={{ filter: isSelected ? 'url(#glow-selected)' : 'drop-shadow(0 2px 4px rgba(0,0,0,0.2))' }}
                        />
                        <circle cx={pos.x} cy={pos.y} r={4} fill={isSelected ? '#ffffff' : 'var(--ok)'} />
                        <text x={pos.x} y={pos.y + 20} textAnchor="middle" fontSize={9} fontWeight={600} fill="var(--text-2)">
                          {n.label.length > 15 ? n.label.substring(0, 15) + '…' : n.label}
                        </text>
                      </g>
                    )
                  }

                  return null
                })}
              </svg>

              {/* Node Detailed Inspection Drawer */}
              {selectedNode && (
                <div style={{ 
                  position: 'absolute', top: 16, right: 16, width: 380, maxHeight: 'calc(100% - 32px)', 
                  background: 'var(--surface)', padding: 20, borderRadius: 14, border: '1px solid var(--border)', 
                  boxShadow: '0 16px 48px rgba(0,0,0,0.4)', zIndex: 20, display: 'flex', flexDirection: 'column', gap: 14, overflowY: 'auto' 
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      {selectedNode.type === 'document' ? <FileText size={17} color="var(--primary)" /> 
                        : selectedNode.type === 'domain' ? <Building2 size={17} color={selectedNode.config?.color || '#f59e0b'} /> 
                        : selectedNode.type === 'query' ? <Sparkles size={17} color="#6366f1" />
                        : <Tag size={17} color="var(--ok)" />}
                      <span className="badge" style={{ fontSize: '.72rem', textTransform: 'uppercase', fontWeight: 700 }}>
                        {selectedNode.type}
                      </span>
                    </div>
                    <button className="btn btn-ghost btn-icon btn-sm" onClick={() => setSelectedNode(null)}>
                      <X size={15} />
                    </button>
                  </div>
                  
                  <div>
                    <h3 style={{ margin: 0, fontSize: '1.1rem', color: 'var(--text)', fontWeight: 700, lineHeight: 1.3 }}>
                      {selectedNode.label}
                    </h3>
                    {selectedNode.score != null && (
                      <div style={{ marginTop: 6, fontSize: '.84rem', color: 'var(--primary)', fontWeight: 700 }}>
                        Relevance Score: {Number(selectedNode.score).toFixed(4)}
                      </div>
                    )}
                  </div>

                  {/* DOCUMENT INSPECTION */}
                  {selectedNode.type === 'document' && (
                    <>
                      {selectedNode.domains?.length > 0 && (
                        <div>
                          <span style={{ fontSize: '.75rem', color: 'var(--text-3)', fontWeight: 600 }}>Associated Domains:</span>
                          <div style={{ display: 'flex', gap: 6, marginTop: 4, flexWrap: 'wrap' }}>
                            {selectedNode.domains.map((dm, idx) => (
                              <span key={idx} className="badge" style={{ background: 'var(--surface-3)', color: 'var(--text)' }}>
                                {dm}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}

                      {selectedNode.entities?.length > 0 && (
                        <div>
                          <span style={{ fontSize: '.75rem', color: 'var(--text-3)', fontWeight: 600 }}>Extracted Entities:</span>
                          <div style={{ display: 'flex', gap: 6, marginTop: 4, flexWrap: 'wrap' }}>
                            {selectedNode.entities.map((ent, idx) => (
                              <span key={idx} className="badge" style={{ background: 'rgba(16, 185, 129, 0.1)', color: 'var(--ok)', border: '1px solid rgba(16, 185, 129, 0.2)' }}>
                                {ent}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}

                      {selectedNode.content && (
                        <div>
                          <span style={{ fontSize: '.75rem', color: 'var(--text-3)', fontWeight: 600 }}>Document Content Snippet:</span>
                          <div style={{ marginTop: 4, fontSize: '.84rem', color: 'var(--text-2)', lineHeight: 1.6, background: 'var(--bg-2)', padding: 14, borderRadius: 10, border: '1px solid var(--border-2)', maxHeight: 220, overflowY: 'auto' }}>
                            {selectedNode.content}
                          </div>
                        </div>
                      )}
                    </>
                  )}

                  {/* DOMAIN / DEPARTMENT INSPECTION */}
                  {selectedNode.type === 'domain' && (
                    <>
                      {/* Department Relationships */}
                      <div>
                        <span style={{ fontSize: '.78rem', color: 'var(--text)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 5 }}>
                          <Link2 size={14} color="#ec4899" /> Cross-Department Relationships:
                        </span>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginTop: 8 }}>
                          {DEPARTMENT_RELATIONSHIPS
                            .filter(rel => rel.d1 === selectedNode.label || rel.d2 === selectedNode.label)
                            .map((rel, idx) => {
                              const otherDept = rel.d1 === selectedNode.label ? rel.d2 : rel.d1
                              return (
                                <div key={idx} style={{ background: 'var(--bg-2)', padding: 10, borderRadius: 8, border: '1px solid var(--border-2)' }}>
                                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                    <strong style={{ fontSize: '.82rem', color: '#ec4899' }}>{rel.relation}</strong>
                                    <span className="badge" style={{ fontSize: '.68rem' }}>{otherDept}</span>
                                  </div>
                                  <p style={{ margin: '4px 0 0', fontSize: '.76rem', color: 'var(--text-2)', lineHeight: 1.4 }}>
                                    {rel.description}
                                  </p>
                                </div>
                              )
                            })}
                        </div>
                      </div>

                      {/* Associated Retrieved Documents */}
                      {selectedNode.documents?.length > 0 && (
                        <div>
                          <span style={{ fontSize: '.75rem', color: 'var(--text-3)', fontWeight: 600 }}>Retrieved Documents in this Domain:</span>
                          <ul style={{ margin: '6px 0 0', paddingLeft: 18, fontSize: '.82rem', color: 'var(--text-2)' }}>
                            {selectedNode.documents.map((docTitle, idx) => (
                              <li key={idx} style={{ marginBottom: 4 }}>{docTitle}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Core Department KPIs in OmniIntelOS */}
                      {selectedNode.config?.kpis?.length > 0 && (
                        <div>
                          <span style={{ fontSize: '.75rem', color: 'var(--text-3)', fontWeight: 600 }}>Tracked KPIs in OmniIntelOS:</span>
                          <div style={{ display: 'flex', gap: 6, marginTop: 4, flexWrap: 'wrap' }}>
                            {selectedNode.config.kpis.map((kpi, idx) => (
                              <span key={idx} className="badge" style={{ background: 'var(--surface-2)', color: 'var(--text-2)', fontSize: '.72rem' }}>
                                {kpi}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </>
                  )}

                  {/* ENTITY INSPECTION */}
                  {selectedNode.type === 'entity' && (
                    <>
                      <div>
                        <span style={{ fontSize: '.75rem', color: 'var(--text-3)', fontWeight: 600 }}>Occurrences:</span>
                        <div style={{ fontSize: '.9rem', fontWeight: 600, color: 'var(--ok)' }}>
                          Mentioned in {selectedNode.documents?.length || 1} document(s)
                        </div>
                      </div>
                      {selectedNode.documents?.length > 0 && (
                        <div>
                          <span style={{ fontSize: '.75rem', color: 'var(--text-3)', fontWeight: 600 }}>Citing Documents:</span>
                          <ul style={{ margin: '6px 0 0', paddingLeft: 18, fontSize: '.82rem', color: 'var(--text-2)' }}>
                            {selectedNode.documents.map((docTitle, idx) => (
                              <li key={idx}>{docTitle}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {selectedNode.domains?.length > 0 && (
                        <div>
                          <span style={{ fontSize: '.75rem', color: 'var(--text-3)', fontWeight: 600 }}>Related Departments:</span>
                          <div style={{ display: 'flex', gap: 6, marginTop: 4, flexWrap: 'wrap' }}>
                            {selectedNode.domains.map((dm, idx) => (
                              <span key={idx} className="badge" style={{ background: 'var(--surface-3)', color: 'var(--text)' }}>
                                {dm}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </>
                  )}

                  {/* QUERY INSPECTION */}
                  {selectedNode.type === 'query' && (
                    <div>
                      <span style={{ fontSize: '.75rem', color: 'var(--text-3)', fontWeight: 600 }}>Active Search String:</span>
                      <div style={{ marginTop: 4, fontSize: '.86rem', color: 'var(--text)', background: 'var(--bg-2)', padding: 12, borderRadius: 8, border: '1px solid var(--border-2)' }}>
                        "{selectedNode.label}"
                      </div>
                    </div>
                  )}

                  {/* Interactive Action Buttons */}
                  <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
                    <button className="btn btn-primary btn-sm" style={{ flex: 1 }} onClick={() => {
                      const qTarget = selectedNode.type === 'document' ? selectedNode.label : `${query} ${selectedNode.label}`
                      navigate(`/chat?q=${encodeURIComponent(qTarget)}`)
                    }}>
                      <MessageSquare size={13} style={{ marginRight: 4 }} /> Ask Copilot
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

              {/* Department Relationship Edge Inspector */}
              {selectedLink && (
                <div style={{ 
                  position: 'absolute', top: 16, right: 16, width: 340, 
                  background: 'var(--surface)', padding: 18, borderRadius: 14, border: '1px solid #ec4899', 
                  boxShadow: '0 16px 48px rgba(0,0,0,0.4)', zIndex: 20, display: 'flex', flexDirection: 'column', gap: 10 
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                      <Link2 size={16} color="#ec4899" />
                      <span className="badge" style={{ fontSize: '.7rem', background: '#ec4899', color: '#fff', fontWeight: 700 }}>
                        DEPARTMENT RELATION
                      </span>
                    </div>
                    <button className="btn btn-ghost btn-icon btn-sm" onClick={() => setSelectedLink(null)}>
                      <X size={14} />
                    </button>
                  </div>
                  <h4 style={{ margin: 0, fontSize: '1rem', color: 'var(--text)', fontWeight: 700 }}>
                    {selectedLink.d1} ↔ {selectedLink.d2}
                  </h4>
                  <div style={{ fontSize: '.84rem', color: '#ec4899', fontWeight: 600 }}>
                    {selectedLink.label}
                  </div>
                  <p style={{ margin: 0, fontSize: '.8rem', color: 'var(--text-2)', lineHeight: 1.5 }}>
                    {selectedLink.description}
                  </p>
                  <button className="btn btn-primary btn-sm" style={{ marginTop: 4 }} onClick={() => {
                    navigate(`/chat?q=${encodeURIComponent(`Explain the relationship between ${selectedLink.d1} and ${selectedLink.d2} regarding ${selectedLink.label}`)}`)
                  }}>
                    <MessageSquare size={13} style={{ marginRight: 4 }} /> Ask Copilot About This Link
                  </button>
                </div>
              )}

              {/* Quick Hover Tooltip */}
              {hover && !selectedNode && !selectedLink && (
                <div style={{ position: 'absolute', bottom: 16, right: 16, width: 300, background: 'var(--surface)', padding: 14, borderRadius: 10, border: '1px solid var(--border)', boxShadow: '0 8px 24px rgba(0,0,0,0.25)', pointerEvents: 'none', zIndex: 10 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                    <strong style={{ color: 'var(--text)', fontSize: '.9rem' }}>{hover.label}</strong>
                    <span className="badge" style={{ fontSize: '.65rem', textTransform: 'uppercase' }}>{hover.type}</span>
                  </div>
                  {hover.score != null && (
                    <div style={{ fontSize: '.75rem', color: 'var(--primary)', fontWeight: 600, marginBottom: 6 }}>
                      Relevance Score: {Number(hover.score).toFixed(4)}
                    </div>
                  )}
                  {hover.content && (
                    <div style={{ fontSize: '.75rem', color: 'var(--text-2)', lineHeight: 1.4, maxHeight: 60, overflow: 'hidden' }}>
                      "{hover.content}"
                    </div>
                  )}
                </div>
              )}

              {/* Legend with interactive details */}
              <div style={{ position: 'absolute', top: 16, left: 16, background: 'var(--surface-2)', padding: '10px 14px', borderRadius: 10, border: '1px solid var(--border-2)', display: 'flex', flexDirection: 'column', gap: 7, fontSize: '.75rem', color: 'var(--text-2)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <div style={{ width: 14, height: 14, borderRadius: '50%', background: 'url(#grad-query)' }} /> 
                  <strong style={{ color: 'var(--text)' }}>Query Intent</strong>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <div style={{ width: 18, height: 12, borderRadius: 4, background: 'var(--surface)', border: '1.5px solid var(--primary)' }} /> 
                  <span>Document Evidence Card</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <div style={{ width: 16, height: 10, borderRadius: 5, background: 'rgba(245, 158, 11, 0.2)', border: '1.5px solid #f59e0b' }} /> 
                  <span>Business Domain / Dept</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <div style={{ width: 10, height: 10, borderRadius: '50%', background: 'var(--ok)' }} /> 
                  <span>Extracted Entity</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 2, paddingTop: 4, borderTop: '1px solid var(--border)' }}>
                  <div style={{ width: 20, height: 2, background: '#ec4899', borderStyle: 'dashed' }} /> 
                  <span style={{ color: '#ec4899', fontWeight: 600 }}>Cross-Dept Relation</span>
                </div>
              </div>
            </div>
          )}
      </Panel>
    </div>
  )
}
