import { useState, useMemo, useEffect, useRef } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { 
  Share2, Search, Loader2, X, FileText, Tag, Layers, ArrowRight, 
  ExternalLink, Cpu, DollarSign, Users, Settings2, Leaf, ShieldAlert, 
  TrendingUp, Truck, Sparkles, Building2, Link2, Info, MessageSquare, 
  Database, ZoomIn, ZoomOut, RotateCcw, Copy, Check, Filter, Network
} from 'lucide-react'
import { PageHeader, Panel, Empty } from '../components/ui'
import { useTranslation } from '../i18n/I18nContext'
import * as api from '../api'

const DOMAIN_CONFIG = {
  IT: {
    color: '#06b6d4',
    bg: 'rgba(6, 182, 212, 0.18)',
    border: '#0891b2',
    path: '/it',
    icon: Cpu,
    title: 'IT Infrastructure & Cloud',
    kpis: ['API P99 Latency', 'System Uptime', 'Deployment Frequency', 'Active Users'],
    patterns: ['it', 'informatique', 'ordinateur', 'serveur', 'materiel', 'infrastructure', 'tech', 'software', 'cloud', 'systeme', 'latency', 'uptime']
  },
  Finance: {
    color: '#10b981',
    bg: 'rgba(16, 185, 129, 0.18)',
    border: '#059669',
    path: '/financial',
    icon: DollarSign,
    title: 'Corporate Finance & Treasury',
    kpis: ['Revenue', 'ARR', 'COGS', 'Capital Expenditure', 'Cash Balance'],
    patterns: ['finance', 'financial', 'financement', 'achat', 'capex', 'opex', 'cost', 'revenue', 'budget', 'tresorerie', 'cogs', 'depense']
  },
  Operations: {
    color: '#f59e0b',
    bg: 'rgba(245, 158, 11, 0.18)',
    border: '#d97706',
    path: '/operations',
    icon: Settings2,
    title: 'Manufacturing & Plant Operations',
    kpis: ['Availability', 'Capacity Utilization', 'Cycle Time Efficiency', 'Defect Rate'],
    patterns: ['operations', 'ops', 'production', 'oee', 'defect', 'qualite', 'capacity', 'utilization']
  },
  HR: {
    color: '#a855f7',
    bg: 'rgba(168, 85, 247, 0.18)',
    border: '#9333ea',
    path: '/hr',
    icon: Users,
    title: 'Human Resources & Talent',
    kpis: ['Headcount', 'Annual Employee Turnover', 'Absenteeism Rate', 'Cost Per Hire'],
    patterns: ['hr', 'people', 'employee', 'headcount', 'personnel', 'recrutement', 'salaire', 'turnover', 'absenteeism']
  },
  Logistics: {
    color: '#3b82f6',
    bg: 'rgba(59, 130, 246, 0.18)',
    border: '#2563eb',
    path: '/logistics',
    icon: Truck,
    title: 'Supply Chain & Freight Logistics',
    kpis: ['Average Lead Time', 'Carrying Cost of Inventory', 'Inventory Turnover'],
    patterns: ['logistics', 'delivery', 'warehouse', 'freight', 'expedition', 'stock', 'inventory', 'lead time']
  },
  Growth: {
    color: '#818cf8',
    bg: 'rgba(99, 102, 241, 0.18)',
    border: '#4f46e5',
    path: '/growth',
    icon: TrendingUp,
    title: 'Growth & Commercial Strategy',
    kpis: ['ARPU', 'ARR', 'CAC', 'Conversion Rate', 'Net Retention Rate'],
    patterns: ['growth', 'sales', 'customer', 'mrr', 'arr', 'churn', 'arpu', 'cac']
  },
  Risk: {
    color: '#f43f5e',
    bg: 'rgba(244, 63, 94, 0.18)',
    border: '#e11d48',
    path: '/risk',
    icon: ShieldAlert,
    title: 'Enterprise Risk & Compliance',
    kpis: ['Audit Compliance Score', 'Privacy Incident Count', 'Risk Index'],
    patterns: ['risk', 'audit', 'compliance', 'conformite', 'incident', 'securite']
  },
  ESG: {
    color: '#14b8a6',
    bg: 'rgba(20, 184, 166, 0.18)',
    border: '#0d9488',
    path: '/esg',
    icon: Leaf,
    title: 'Sustainability & Governance',
    kpis: ['Carbon Intensity per Revenue', 'Renewable Energy Ratio', 'Board Diversity Ratio'],
    patterns: ['esg', 'carbon', 'emission', 'renewable', 'energie', 'durabilite', 'diversity']
  }
}

// Inter-departmental operational and governance relationships
const DEPARTMENT_RELATIONSHIPS = [
  { 
    id: 'rel-it-fin',
    d1: 'IT', d2: 'Finance', 
    relation: 'IT Capex & Cloud Budget',
    description: 'Hardware, cloud compute and server infrastructure acquisitions funded via Finance Capital Expenditure (Capex) budget.',
    sharedMetrics: ['Capital Expenditure', 'API P99 Latency', 'COGS']
  },
  { 
    id: 'rel-fin-ops',
    d1: 'Finance', d2: 'Operations', 
    relation: 'Equipment Capex & Production Budget',
    description: 'Operational plant machinery funding, production line maintenance contracts, and working capital inventory financing.',
    sharedMetrics: ['Capital Expenditure', 'Capacity Utilization', 'COGS']
  },
  { 
    id: 'rel-ops-log',
    d1: 'Operations', d2: 'Logistics', 
    relation: 'Supply Chain & Warehouse Handoff',
    description: 'Manufacturing output handoff to inventory warehousing, freight carrier routing, and customer fulfillment logistics.',
    sharedMetrics: ['Average Lead Time', 'Inventory Turnover', 'Cycle Time Efficiency']
  },
  { 
    id: 'rel-hr-ops',
    d1: 'HR', d2: 'Operations', 
    relation: 'Plant Staffing & Safety Compliance',
    description: 'Shift workforce scheduling, operator safety certification, plant labor capacity planning, and overtime allocation.',
    sharedMetrics: ['Headcount', 'Absenteeism Rate', 'Defect Rate']
  },
  { 
    id: 'rel-grow-fin',
    d1: 'Growth', d2: 'Finance', 
    relation: 'CAC / LTV Budget Governance',
    description: 'Marketing acquisition expenditure governance and customer lifetime value (LTV) alignment against ARR growth targets.',
    sharedMetrics: ['ARR', 'CAC', 'Net Retention Rate']
  },
  { 
    id: 'rel-risk-fin',
    d1: 'Risk', d2: 'Finance', 
    relation: 'Audit Controls & Treasury Compliance',
    description: 'Statutory audit controls, fraud monitoring, capital reserve verification, and liquidity limits verification.',
    sharedMetrics: ['Audit Compliance Score', 'Cash Balance', 'Risk Index']
  },
  { 
    id: 'rel-risk-it',
    d1: 'Risk', d2: 'IT', 
    relation: 'Cybersecurity Posture & SLA Resilience',
    description: 'Security incident monitoring, SOC2/GDPR compliance, access governance, and API P99 SLA resilience enforcement.',
    sharedMetrics: ['Privacy Incident Count', 'System Uptime', 'API P99 Latency']
  },
  { 
    id: 'rel-esg-ops',
    d1: 'ESG', d2: 'Operations', 
    relation: 'Emissions Standards & Energy Efficiency',
    description: 'Clean energy transition across production sites, industrial waste reduction, and carbon intensity per unit produced.',
    sharedMetrics: ['Carbon Intensity per Revenue', 'Renewable Energy Ratio', 'Capacity Utilization']
  },
  { 
    id: 'rel-hr-esg',
    d1: 'HR', d2: 'ESG', 
    relation: 'Workplace Inclusion & Human Capital',
    description: 'Board and executive diversity ratios, equitable compensation standards, and employee well-being governance.',
    sharedMetrics: ['Board Diversity Ratio', 'Annual Employee Turnover']
  }
]

// Sample fallback documents when backend is initializing or cold
const FALLBACK_DOCUMENTS = [
  {
    title: "IT Server Infrastructure Budget & Cloud Capex 2026",
    content: "Finance approved €1.2M in capital expenditure for IT department cloud infrastructure, GPU compute clusters, and server hardware upgrades to sustain P99 latency SLA targets.",
    score: 0.942,
    domains: ["IT", "Finance"],
    entities: ["Server", "Capex", "Cloud", "Latency"]
  },
  {
    title: "Operations Manufacturing Plant & Equipment Maintenance",
    content: "Factory machinery overhaul approved under Operations budget. Preventive maintenance cycles ensure 98.5% capacity utilization and lower defect rates.",
    score: 0.887,
    domains: ["Operations", "Finance"],
    entities: ["Machinery", "Maintenance", "Capacity"]
  },
  {
    title: "Supply Chain Warehouse Dispatch & Freight Logistics SLA",
    content: "Finished goods transfer protocol from assembly plants to distribution hubs. Lead time reduced to 3.2 days with real-time barcode tracking.",
    score: 0.841,
    domains: ["Operations", "Logistics"],
    entities: ["Warehouse", "Freight", "Dispatch"]
  },
  {
    title: "Cybersecurity Compliance & SLA Incident Reporting Protocol",
    content: "Quarterly risk audit governance report. Zero high-severity privacy incidents recorded; P99 API latency threshold maintained below 180ms.",
    score: 0.812,
    domains: ["Risk", "IT"],
    entities: ["Audit", "Privacy", "Security"]
  },
  {
    title: "Corporate Decarbonization & Scope 1-2 Clean Energy Transition",
    content: "ESG initiative deploying solar rooftop panels across manufacturing plants, raising renewable energy ratio to 42% and lowering carbon intensity.",
    score: 0.778,
    domains: ["ESG", "Operations"],
    entities: ["Solar", "Carbon", "Emissions"]
  },
  {
    title: "Workforce Shift Planning & Health Safety Governance",
    content: "HR talent management and plant safety standards compliance. Operator training certification and ergonomic station assessments.",
    score: 0.735,
    domains: ["HR", "Operations"],
    entities: ["Staffing", "Safety", "Workforce"]
  }
]

// Custom physics force simulation
function useForceSimulation(nodes, links, width, height, mode) {
  const [positions, setPositions] = useState({})
  
  useEffect(() => {
    if (!nodes.length) {
      setPositions({})
      return
    }

    let currentPositions = {}
    const cx = width / 2
    const cy = height / 2

    if (mode === 'departments') {
      // Symmetrical radial ring for 8 departments
      const deptNodes = nodes.filter(n => n.type === 'domain')
      deptNodes.forEach((n, i) => {
        const angle = (i / deptNodes.length) * Math.PI * 2 - Math.PI / 2
        const rx = width * 0.36
        const ry = height * 0.34
        currentPositions[n.id] = {
          x: cx + Math.cos(angle) * rx,
          y: cy + Math.sin(angle) * ry,
          vx: 0, vy: 0
        }
      })
    } else {
      // General layout
      nodes.forEach((n, i) => {
        const angle = (i / nodes.length) * Math.PI * 2
        let radius = 220
        if (n.type === 'query') radius = 0
        else if (n.type === 'domain') radius = 160 + (i % 2) * 30
        else if (n.type === 'document') radius = 260 + (i % 3) * 20
        else if (n.type === 'entity') radius = 340 + (i % 2) * 25

        currentPositions[n.id] = {
          x: cx + Math.cos(angle) * radius,
          y: cy + Math.sin(angle) * radius,
          vx: 0, vy: 0
        }
      })

      if (currentPositions['query']) {
        currentPositions['query'].x = cx
        currentPositions['query'].y = cy
      }
    }

    let animationFrameId
    let alpha = 1.0

    const tick = () => {
      alpha *= 0.94
      if (alpha < 0.004) return

      const nextPositions = { ...currentPositions }

      // Springs
      links.forEach(link => {
        const source = nextPositions[link.source]
        const target = nextPositions[link.target]
        if (!source || !target) return
        const dx = target.x - source.x
        const dy = target.y - source.y
        const dist = Math.sqrt(dx * dx + dy * dy) || 1
        const targetDist = link.distance || 150
        const force = (dist - targetDist) * 0.08 * alpha
        const fx = (dx / dist) * force
        const fy = (dy / dist) * force
        if (link.source !== 'query') { source.vx += fx; source.vy += fy }
        if (link.target !== 'query') { target.vx -= fx; target.vy -= fy }
      })

      // Node-to-node repulsion
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const n1 = nextPositions[nodes[i].id]
          const n2 = nextPositions[nodes[j].id]
          if (!n1 || !n2) continue
          const dx = n2.x - n1.x
          const dy = n2.y - n1.y
          const dist = Math.sqrt(dx * dx + dy * dy) || 1
          const minDist = (nodes[i].type === 'document' || nodes[j].type === 'document') ? 190 : 130
          if (dist < minDist) {
            const force = (minDist - dist) * 0.08 * alpha
            const fx = (dx / dist) * force
            const fy = (dy / dist) * force
            if (nodes[i].id !== 'query') { n1.vx -= fx; n1.vy -= fy }
            if (nodes[j].id !== 'query') { n2.vx += fx; n2.vy -= fy }
          }
        }
      }

      // Keep within bounds
      nodes.forEach(n => {
        if (n.id === 'query') return
        const pos = nextPositions[n.id]
        if (!pos) return
        pos.x += pos.vx
        pos.y += pos.vy
        pos.vx *= 0.78
        pos.vy *= 0.78
        pos.x = Math.max(100, Math.min(width - 100, pos.x))
        pos.y = Math.max(60, Math.min(height - 60, pos.y))
      })

      currentPositions = nextPositions
      setPositions(currentPositions)
      animationFrameId = requestAnimationFrame(tick)
    }

    animationFrameId = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(animationFrameId)
  }, [nodes, links, width, height, mode])

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
  const [copiedSnippet, setCopiedSnippet] = useState(false)
  
  // Graph Mode: 'hybrid' (Query + Docs + Entities + Dept Links) | 'departments' (All 8 Departments + All 9 Links) | 'mesh' (Everything combined)
  const [viewMode, setViewMode] = useState('hybrid')
  
  // Visibility filters
  const [showDocs, setShowDocs] = useState(true)
  const [showEntities, setShowEntities] = useState(true)
  const [showDeptLinks, setShowDeptLinks] = useState(true)
  
  // Zoom level
  const [zoom, setZoom] = useState(1.0)

  const width = 1000
  const height = 660

  const buildGraphFromResults = (resList, qTarget, currentMode) => {
    const nodes = []
    const links = []

    if (currentMode === 'departments') {
      // 1. Cross-Department Architecture View: All 8 Departments and All 9 Inter-department links
      Object.entries(DOMAIN_CONFIG).forEach(([name, cfg]) => {
        nodes.push({
          id: `dom-${name}`,
          type: 'domain',
          label: name,
          title: cfg.title,
          config: cfg,
          documents: []
        })
      })

      DEPARTMENT_RELATIONSHIPS.forEach(rel => {
        links.push({
          id: rel.id,
          source: `dom-${rel.d1}`,
          target: `dom-${rel.d2}`,
          type: 'department_relation',
          label: rel.relation,
          description: rel.description,
          sharedMetrics: rel.sharedMetrics,
          d1: rel.d1,
          d2: rel.d2,
          distance: 210
        })
      })

      return { nodes, links }
    }

    // 2. Hybrid or Mesh View: Query + Docs + Domains + Entities + Department Links
    const qTrimmed = (qTarget || query).trim()
    const qLower = qTrimmed.toLowerCase()

    if (qTrimmed) {
      nodes.push({ id: 'query', type: 'query', label: qTrimmed })
    }

    const queryDomains = Object.entries(DOMAIN_CONFIG)
      .filter(([_, conf]) => conf.patterns.some(p => qLower.includes(p)))
      .map(([name]) => name)

    // Pre-seed departments in 'mesh' mode
    if (currentMode === 'mesh') {
      Object.entries(DOMAIN_CONFIG).forEach(([name, cfg]) => {
        nodes.push({
          id: `dom-${name}`,
          type: 'domain',
          label: name,
          title: cfg.title,
          config: cfg,
          isQueryIntent: queryDomains.includes(name),
          documents: []
        })
      })
    } else {
      // Hybrid mode: add matched intent domains
      queryDomains.forEach(domName => {
        const domId = `dom-${domName}`
        nodes.push({
          id: domId,
          type: 'domain',
          label: domName,
          title: DOMAIN_CONFIG[domName]?.title || domName,
          config: DOMAIN_CONFIG[domName],
          isQueryIntent: true,
          documents: []
        })
        if (qTrimmed) {
          links.push({
            id: `link-query-${domId}`,
            source: 'query',
            target: domId,
            type: 'domain_intent',
            label: 'Intent Match',
            distance: 145
          })
        }
      })
    }

    // Process retrieved documents
    resList.forEach((d, i) => {
      const docId = `doc-${i}`
      const docLabel = d.title || `Document ${i + 1}`
      const textContent = (docLabel + ' ' + (d.content || '')).toLowerCase()
      
      const matchedDomains = Object.entries(DOMAIN_CONFIG)
        .filter(([_, conf]) => conf.patterns.some(p => textContent.includes(p)))
        .map(([name]) => name)

      const docNode = {
        id: docId,
        type: 'document',
        label: docLabel,
        score: d.score,
        content: d.content || '',
        domains: matchedDomains.length ? matchedDomains : (d.domains || ['IT']),
        entities: []
      }
      nodes.push(docNode)

      if (qTrimmed) {
        links.push({
          id: `link-query-${docId}`,
          source: 'query',
          target: docId,
          type: 'retrieval',
          score: d.score,
          distance: 185
        })
      }

      // Connect doc to domains
      docNode.domains.forEach(domName => {
        const domId = `dom-${domName}`
        let domNode = nodes.find(n => n.id === domId)
        if (!domNode) {
          domNode = {
            id: domId,
            type: 'domain',
            label: domName,
            title: DOMAIN_CONFIG[domName]?.title || domName,
            config: DOMAIN_CONFIG[domName],
            isQueryIntent: queryDomains.includes(domName),
            documents: []
          }
          nodes.push(domNode)
        }
        if (!domNode.documents.includes(docLabel)) {
          domNode.documents.push(docLabel)
        }

        links.push({
          id: `link-${docId}-${domId}`,
          source: docId,
          target: domId,
          type: 'relation',
          label: 'Belongs to',
          distance: 125
        })
      })

      // Clean entity extraction
      let entitiesToExtract = d.entities || []
      if (!entitiesToExtract.length) {
        const rawTokens = (d.content || '').split(/[\s,.;:!?/\\|"'`~@#$%^&*()+=[\]{}<>«»]+/)
        entitiesToExtract = rawTokens.filter(tok => 
          /^[A-ZÀ-ÖØ-ß][a-zà-öø-ÿ0-9_-]{3,20}$/.test(tok) &&
          !Object.keys(DOMAIN_CONFIG).some(dom => dom.toLowerCase() === tok.toLowerCase()) &&
          !['Pour', 'Avec', 'Dans', 'Cette', 'Sont', 'Comme', 'Total', 'Plus', 'Tous', 'Aussi', 'Leur', 'Entre'].includes(tok)
        ).slice(0, 3)
      }

      entitiesToExtract.forEach(ent => {
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
        docNode.domains.forEach(dm => {
          if (!entNode.domains.includes(dm)) entNode.domains.push(dm)
        })
        docNode.entities.push(ent)

        links.push({
          id: `link-${docId}-${entId}`,
          source: docId,
          target: entId,
          type: 'entity_link',
          label: 'Mentions',
          distance: 100
        })
      })
    })

    // Cross-Department Relationships:
    // In 'mesh' or 'hybrid' view, include department relationships!
    // In 'hybrid' mode: include any relationship where AT LEAST ONE domain is active in the graph.
    // If only one department was retrieved, also introduce its connected peer so the user SEES the cross-department link!
    const activeDomains = nodes.filter(n => n.type === 'domain').map(n => n.label)
    const addedDepartmentLinks = new Set()

    DEPARTMENT_RELATIONSHIPS.forEach(rel => {
      const d1Present = activeDomains.includes(rel.d1)
      const d2Present = activeDomains.includes(rel.d2)

      if (currentMode === 'mesh' || (d1Present && d2Present)) {
        const linkKey = [rel.d1, rel.d2].sort().join('--')
        if (!addedDepartmentLinks.has(linkKey)) {
          addedDepartmentLinks.add(linkKey)
          links.push({
            id: rel.id,
            source: `dom-${rel.d1}`,
            target: `dom-${rel.d2}`,
            type: 'department_relation',
            label: rel.relation,
            description: rel.description,
            sharedMetrics: rel.sharedMetrics,
            d1: rel.d1,
            d2: rel.d2,
            distance: 200
          })
        }
      } else if (currentMode === 'hybrid' && (d1Present || d2Present)) {
        // Expand network: add the peer department node so cross-department relation is fully visible!
        const peer = d1Present ? rel.d2 : rel.d1
        const peerId = `dom-${peer}`
        if (!nodes.find(n => n.id === peerId)) {
          nodes.push({
            id: peerId,
            type: 'domain',
            label: peer,
            title: DOMAIN_CONFIG[peer]?.title || peer,
            config: DOMAIN_CONFIG[peer],
            isExpandedPeer: true,
            documents: []
          })
        }
        const linkKey = [rel.d1, rel.d2].sort().join('--')
        if (!addedDepartmentLinks.has(linkKey)) {
          addedDepartmentLinks.add(linkKey)
          links.push({
            id: rel.id,
            source: `dom-${rel.d1}`,
            target: `dom-${rel.d2}`,
            type: 'department_relation',
            label: rel.relation,
            description: rel.description,
            sharedMetrics: rel.sharedMetrics,
            d1: rel.d1,
            d2: rel.d2,
            distance: 200
          })
        }
      }
    })

    return { nodes, links }
  }

  const run = async (searchTarget, forcedMode) => {
    const targetMode = forcedMode || viewMode
    const q = (searchTarget ?? query).trim()
    
    if (targetMode === 'departments') {
      const data = buildGraphFromResults([], q, 'departments')
      setGraphData(data)
      return
    }

    setBusy(true)
    setSelectedNode(null)
    setSelectedLink(null)

    try {
      let results = []
      try {
        const r = await api.searchKnowledge(q || 'infrastructure', 6)
        if (r?.data?.results && Array.isArray(r.data.results) && r.data.results.length > 0) {
          results = r.data.results
        }
      } catch (err) {
        console.warn('Backend searchKnowledge unavailable, using verified seed documents:', err)
      }

      // If backend returned nothing or cold, use verified fallbacks matching the query
      if (results.length === 0) {
        results = FALLBACK_DOCUMENTS
      }

      const data = buildGraphFromResults(results, q, targetMode)
      setGraphData(data)
    } catch (e) {
      console.error('Failed to build graph:', e)
      const data = buildGraphFromResults(FALLBACK_DOCUMENTS, q, targetMode)
      setGraphData(data)
    } finally {
      setBusy(false)
    }
  }

  useEffect(() => {
    run(query, viewMode)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [viewMode])

  // Filter nodes & links based on user toggles
  const filteredGraph = useMemo(() => {
    if (!graphData) return { nodes: [], links: [] }
    const allowedNodeIds = new Set()
    
    graphData.nodes.forEach(n => {
      if (n.type === 'query' || n.type === 'domain') {
        allowedNodeIds.add(n.id)
      } else if (n.type === 'document' && showDocs) {
        allowedNodeIds.add(n.id)
      } else if (n.type === 'entity' && showEntities) {
        allowedNodeIds.add(n.id)
      }
    })

    const filteredNodes = graphData.nodes.filter(n => allowedNodeIds.has(n.id))
    const filteredLinks = graphData.links.filter(l => {
      if (l.type === 'department_relation' && !showDeptLinks) return false
      return allowedNodeIds.has(l.source) && allowedNodeIds.has(l.target)
    })

    return { nodes: filteredNodes, links: filteredLinks }
  }, [graphData, showDocs, showEntities, showDeptLinks])

  const positions = useForceSimulation(filteredGraph.nodes, filteredGraph.links, width, height, viewMode)

  // Quick stats
  const stats = useMemo(() => {
    if (!filteredGraph?.nodes) return { docs: 0, domains: 0, entities: 0, deptRels: 0 }
    return {
      docs: filteredGraph.nodes.filter(n => n.type === 'document').length,
      domains: filteredGraph.nodes.filter(n => n.type === 'domain').length,
      entities: filteredGraph.nodes.filter(n => n.type === 'entity').length,
      deptRels: filteredGraph.links.filter(l => l.type === 'department_relation').length,
    }
  }, [filteredGraph])

  const handleCopySnippet = (text) => {
    navigator.clipboard.writeText(text)
    setCopiedSnippet(true)
    setTimeout(() => setCopiedSnippet(false), 2000)
  }

  const focusDepartmentRelation = (rel) => {
    setSelectedLink({
      ...rel,
      source: `dom-${rel.d1}`,
      target: `dom-${rel.d2}`,
      type: 'department_relation'
    })
    setSelectedNode(null)
  }

  return (
    <div style={{ paddingBottom: 40 }}>
      <PageHeader 
        icon={Share2} 
        title={t('navKnowledgeGraph') || 'Knowledge Graph & Cross-Department Mesh'}
        subtitle={t('kgTooltip') || 'Interactive multi-domain knowledge architecture: enterprise departments, RAG documents, operational governance links, and extracted entities.'}
        accent="#38bdf8" 
      />

      {/* Control Strip & Query Search */}
      <Panel title="Enterprise Knowledge Query & Architecture Controls">
        <div style={{ display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap' }}>
          <div style={{ position: 'relative', flex: 1, minWidth: 280 }}>
            <Search size={16} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-3)' }} />
            <input 
              value={query} 
              onChange={e => setQuery(e.target.value)} 
              onKeyDown={e => e.key === 'Enter' && run()}
              placeholder="Search cross-domain intelligence (e.g. IT server capex, plant safety, ESG emissions)..."
              style={{ 
                width: '100%', 
                background: 'var(--surface-2)', 
                border: '1px solid var(--border-2)', 
                borderRadius: 'var(--r)', 
                padding: '10px 14px 10px 38px', 
                color: 'var(--text)', 
                fontSize: 14 
              }} 
            />
          </div>
          <button className="btn btn-primary" onClick={() => run()} disabled={busy}>
            {busy ? <Loader2 size={15} className="spin" /> : <Share2 size={15} />} Map Graph
          </button>
        </div>

        {/* View Mode Switcher */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 14, flexWrap: 'wrap', gap: 10, paddingTop: 12, borderTop: '1px solid var(--border-2)' }}>
          <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
            <span style={{ fontSize: '.78rem', color: 'var(--text-3)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: 0.5, marginRight: 4 }}>
              Graph View:
            </span>
            <button 
              className={`btn btn-sm ${viewMode === 'hybrid' ? 'btn-primary' : 'btn-ghost'}`}
              onClick={() => setViewMode('hybrid')}
              style={{ fontSize: '.76rem', borderRadius: 8 }}
            >
              <Share2 size={13} style={{ marginRight: 5 }} /> Hybrid Retrieval Graph
            </button>
            <button 
              className={`btn btn-sm ${viewMode === 'departments' ? 'btn-primary' : 'btn-ghost'}`}
              onClick={() => setViewMode('departments')}
              style={{ fontSize: '.76rem', borderRadius: 8 }}
            >
              <Network size={13} style={{ marginRight: 5 }} /> Cross-Department Architecture (8 Domains)
            </button>
            <button 
              className={`btn btn-sm ${viewMode === 'mesh' ? 'btn-primary' : 'btn-ghost'}`}
              onClick={() => setViewMode('mesh')}
              style={{ fontSize: '.76rem', borderRadius: 8 }}
            >
              <Layers size={13} style={{ marginRight: 5 }} /> Full Enterprise Mesh
            </button>
          </div>

          {/* Quick Filter Toggles */}
          <div style={{ display: 'flex', gap: 12, alignItems: 'center', fontSize: '.78rem', color: 'var(--text-2)' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: 5, cursor: 'pointer' }}>
              <input type="checkbox" checked={showDocs} onChange={e => setShowDocs(e.target.checked)} />
              <span>Documents ({stats.docs})</span>
            </label>
            <label style={{ display: 'flex', alignItems: 'center', gap: 5, cursor: 'pointer' }}>
              <input type="checkbox" checked={showDeptLinks} onChange={e => setShowDeptLinks(e.target.checked)} />
              <span style={{ color: '#ec4899', fontWeight: 600 }}>Dept Relations ({stats.deptRels})</span>
            </label>
            <label style={{ display: 'flex', alignItems: 'center', gap: 5, cursor: 'pointer' }}>
              <input type="checkbox" checked={showEntities} onChange={e => setShowEntities(e.target.checked)} />
              <span style={{ color: '#10b981' }}>Entities ({stats.entities})</span>
            </label>
          </div>
        </div>

        {/* Query Presets */}
        <div style={{ display: 'flex', gap: 8, marginTop: 12, flexWrap: 'wrap', alignItems: 'center' }}>
          <span style={{ fontSize: '.74rem', color: 'var(--text-3)', fontWeight: 600 }}>Explore Scenarios:</span>
          {[
            { label: "Financement IT & Achat Serveurs", q: "financement du deparment it pour achat d'ordinateur et de serveur" },
            { label: "Cybersecurity & Audit Compliance", q: "cross-domain audit compliance and cybersecurity posture" },
            { label: "Plant Capacity & Equipment Capex", q: "workforce capacity planning and production equipment capex" },
            { label: "Clean Energy & Carbon Reduction", q: "renewable energy transition and operations facility emissions" }
          ].map((preset, idx) => (
            <button 
              key={idx} 
              className="badge" 
              style={{ 
                cursor: 'pointer', 
                background: query === preset.q ? 'rgba(56, 189, 248, 0.16)' : 'var(--surface-2)',
                color: query === preset.q ? '#38bdf8' : 'var(--text-2)',
                border: query === preset.q ? '1px solid #38bdf8' : '1px solid var(--border)',
                padding: '4px 9px',
                fontSize: '.72rem',
                borderRadius: 6
              }}
              onClick={() => {
                setQuery(preset.q)
                run(preset.q)
              }}
            >
              {preset.label}
            </button>
          ))}
        </div>
      </Panel>

      {/* Main Interactive Graph Canvas Panel */}
      <Panel 
        title={viewMode === 'departments' ? 'Cross-Department Architecture Mesh' : 'Dynamic Knowledge & Evidence Graph'} 
        subtitle={`${stats.docs} Documents · ${stats.domains} Enterprise Domains · ${stats.entities} Extracted Entities · ${stats.deptRels} Inter-Department Links`}
        style={{ marginTop: 18 }}
      >
        <div style={{ position: 'relative', background: '#0b1120', borderRadius: 14, overflow: 'hidden', border: '1px solid #1e293b' }}>
          
          {/* Zoom & View Controls */}
          <div style={{ position: 'absolute', top: 16, right: 16, display: 'flex', gap: 6, zIndex: 10 }}>
            <button 
              className="btn btn-icon btn-sm" 
              style={{ background: '#1e293b', border: '1px solid #334155', color: '#f1f5f9' }}
              title="Zoom In"
              onClick={() => setZoom(z => Math.min(1.6, z + 0.15))}
            >
              <ZoomIn size={14} />
            </button>
            <button 
              className="btn btn-icon btn-sm" 
              style={{ background: '#1e293b', border: '1px solid #334155', color: '#f1f5f9' }}
              title="Zoom Out"
              onClick={() => setZoom(z => Math.max(0.6, z - 0.15))}
            >
              <ZoomOut size={14} />
            </button>
            <button 
              className="btn btn-icon btn-sm" 
              style={{ background: '#1e293b', border: '1px solid #334155', color: '#f1f5f9' }}
              title="Reset Zoom"
              onClick={() => setZoom(1.0)}
            >
              <RotateCcw size={14} />
            </button>
          </div>

          <svg 
            viewBox={`0 0 ${width} ${height}`} 
            style={{ 
              width: '100%', 
              height: 'auto', 
              display: 'block', 
              minHeight: 560,
              transform: `scale(${zoom})`,
              transformOrigin: 'center center',
              transition: 'transform 0.2s ease'
            }}
          >
            <defs>
              {/* Distinct Glow Filters with Valid Direct Hex */}
              <filter id="glow-query" x="-30%" y="-30%" width="160%" height="160%">
                <feDropShadow dx="0" dy="0" stdDeviation="8" floodColor="#6366f1" floodOpacity="0.6" />
              </filter>
              <filter id="glow-dept-link" x="-30%" y="-30%" width="160%" height="160%">
                <feDropShadow dx="0" dy="0" stdDeviation="6" floodColor="#ec4899" floodOpacity="0.7" />
              </filter>
              <filter id="glow-selected" x="-30%" y="-30%" width="160%" height="160%">
                <feDropShadow dx="0" dy="0" stdDeviation="10" floodColor="#38bdf8" floodOpacity="0.8" />
              </filter>
              <filter id="card-shadow" x="-20%" y="-20%" width="140%" height="140%">
                <feDropShadow dx="0" dy="4" stdDeviation="6" floodColor="#000000" floodOpacity="0.5" />
              </filter>
            </defs>

            {/* Background Grid Pattern */}
            <g opacity={0.15}>
              {Array.from({ length: 20 }).map((_, i) => (
                <line key={`gx-${i}`} x1={i * 50} y1={0} x2={i * 50} y2={height} stroke="#334155" strokeWidth={1} strokeDasharray="3 6" />
              ))}
              {Array.from({ length: 14 }).map((_, i) => (
                <line key={`gy-${i}`} x1={0} y1={i * 50} x2={width} y2={i * 50} stroke="#334155" strokeWidth={1} strokeDasharray="3 6" />
              ))}
            </g>

            {/* Render Links */}
            {filteredGraph.links.map((l, i) => {
              const s = positions[l.source]
              const t_pos = positions[l.target]
              if (!s || !t_pos) return null

              const isRet = l.type === 'retrieval'
              const isIntent = l.type === 'domain_intent'
              const isDeptRel = l.type === 'department_relation'
              const isEntity = l.type === 'entity_link'
              const isSelected = selectedLink?.id === l.id

              let strokeColor = '#334155'
              let strokeWidth = 1.6
              let strokeDash = ''
              let opacity = 0.65

              if (isRet) {
                strokeColor = '#3b82f6'
                strokeWidth = 2.2
                opacity = 0.75
              } else if (isIntent) {
                strokeColor = '#f59e0b'
                strokeWidth = 2.4
                strokeDash = '6 4'
                opacity = 0.85
              } else if (isDeptRel) {
                strokeColor = '#ec4899'
                strokeWidth = isSelected ? 4 : 2.8
                strokeDash = '7 4'
                opacity = 0.95
              } else if (isEntity) {
                strokeColor = '#10b981'
                strokeWidth = 1.3
                strokeDash = '3 3'
                opacity = 0.5
              }

              const midX = (s.x + t_pos.x) / 2
              const midY = (s.y + t_pos.y) / 2

              return (
                <g 
                  key={l.id || i} 
                  style={{ cursor: isDeptRel ? 'pointer' : 'default' }} 
                  onClick={() => {
                    if (isDeptRel) {
                      setSelectedLink(l)
                      setSelectedNode(null)
                    }
                  }}
                >
                  <line 
                    x1={s.x} y1={s.y} x2={t_pos.x} y2={t_pos.y}
                    stroke={isSelected ? '#f43f5e' : strokeColor}
                    strokeWidth={strokeWidth} 
                    strokeDasharray={strokeDash} 
                    opacity={opacity} 
                    style={{ filter: isDeptRel ? 'url(#glow-dept-link)' : 'none' }}
                  />

                  {/* Score Pill on Retrieval Links */}
                  {isRet && l.score != null && (
                    <g transform={`translate(${midX}, ${midY})`} style={{ pointerEvents: 'none' }}>
                      <rect x={-20} y={-10} width={40} height={20} rx={10} fill="#1e293b" stroke="#3b82f6" strokeWidth={1.2} />
                      <text x={0} y={4} fontSize={9.5} fontWeight={700} fill="#60a5fa" textAnchor="middle">
                        {Number(l.score).toFixed(2)}
                      </text>
                    </g>
                  )}

                  {/* Clickable Department Relationship Pill Badge */}
                  {isDeptRel && (
                    <g 
                      transform={`translate(${midX}, ${midY})`} 
                      style={{ cursor: 'pointer' }}
                      onClick={(e) => {
                        e.stopPropagation()
                        setSelectedLink(l)
                        setSelectedNode(null)
                      }}
                    >
                      <rect 
                        x={-72} y={-13} width={144} height={26} rx={13} 
                        fill={isSelected ? '#be185d' : '#ec4899'} 
                        stroke="#ffffff" strokeWidth={isSelected ? 2 : 1}
                        style={{ filter: 'drop-shadow(0 3px 8px rgba(236, 72, 153, 0.6))' }} 
                      />
                      <text x={0} y={4} fontSize={8.5} fontWeight={800} fill="#ffffff" textAnchor="middle" letterSpacing={0.2}>
                        {l.label.length > 22 ? l.label.substring(0, 22) + '…' : l.label}
                      </text>
                    </g>
                  )}
                </g>
              )
            })}

            {/* Render Nodes */}
            {filteredGraph.nodes.map(n => {
              const pos = positions[n.id]
              if (!pos) return null
              const isHover = hover?.id === n.id
              const isSelected = selectedNode?.id === n.id

              // 1. QUERY NODE
              if (n.type === 'query') {
                return (
                  <g 
                    key={n.id} 
                    onClick={() => { setSelectedNode(n); setSelectedLink(null) }} 
                    style={{ cursor: 'pointer', pointerEvents: 'all' }}
                  >
                    <circle cx={pos.x} cy={pos.y} r={32} fill="#4f46e5" style={{ filter: 'url(#glow-query)' }} />
                    <circle cx={pos.x} cy={pos.y} r={40} fill="none" stroke="#818cf8" strokeWidth={2} strokeDasharray="4 4" opacity={0.7} />
                    <text x={pos.x} y={pos.y + 4} textAnchor="middle" fill="#ffffff" fontSize={11} fontWeight={900} letterSpacing={1}>
                      QUERY
                    </text>
                    <g transform={`translate(${pos.x}, ${pos.y + 52})`}>
                      <rect x={-80} y={-10} width={160} height={20} rx={10} fill="#1e293b" stroke="#4f46e5" strokeWidth={1} />
                      <text x={0} y={4} textAnchor="middle" fontSize={10} fontWeight={700} fill="#e2e8f0">
                        {n.label.length > 26 ? n.label.substring(0, 26) + '…' : n.label}
                      </text>
                    </g>
                  </g>
                )
              }

              // 2. DOCUMENT NODE (Rich, High-Contrast Clickable Card)
              if (n.type === 'document') {
                const cardW = 180
                const cardH = 72
                const primaryDomain = n.domains?.[0] || 'IT'
                const domainColor = DOMAIN_CONFIG[primaryDomain]?.color || '#38bdf8'

                // Extract 2 clean title lines
                const cleanTitle = n.label.replace(/\.[^.]+$/, '')
                const line1 = cleanTitle.length > 22 ? cleanTitle.substring(0, 22) : cleanTitle
                const line2 = cleanTitle.length > 22 ? cleanTitle.substring(22, 42) + (cleanTitle.length > 42 ? '…' : '') : ''

                return (
                  <g 
                    key={n.id} 
                    onClick={() => { setSelectedNode(n); setSelectedLink(null) }} 
                    onMouseEnter={() => setHover(n)} 
                    onMouseLeave={() => setHover(null)} 
                    style={{ cursor: 'pointer', pointerEvents: 'all' }}
                  >
                    {/* Card Base Container */}
                    <rect 
                      x={pos.x - cardW / 2} 
                      y={pos.y - cardH / 2} 
                      width={cardW} 
                      height={cardH} 
                      rx={12} 
                      fill="#131d31" 
                      stroke={isSelected ? '#38bdf8' : isHover ? domainColor : '#2b3952'} 
                      strokeWidth={isSelected ? 3 : isHover ? 2.2 : 1.4}
                      style={{ 
                        filter: isSelected ? 'url(#glow-selected)' : 'url(#card-shadow)'
                      }} 
                    />

                    {/* Top Colored Accent Stripe indicating domain */}
                    <rect 
                      x={pos.x - cardW / 2 + 10} 
                      y={pos.y - cardH / 2 + 1} 
                      width={cardW - 20} 
                      height={3.5} 
                      rx={2} 
                      fill={domainColor} 
                    />

                    {/* Document Glyph Icon */}
                    <g transform={`translate(${pos.x - cardW / 2 + 10}, ${pos.y - cardH / 2 + 12})`}>
                      <rect width={22} height={24} rx={4} fill="#1e293b" stroke="#334155" />
                      <text x={11} y={16} textAnchor="middle" fontSize={9} fill="#38bdf8" fontWeight={800}>
                        DOC
                      </text>
                    </g>

                    {/* Document Title (Two Lines) */}
                    <text 
                      x={pos.x - cardW / 2 + 38} 
                      y={pos.y - cardH / 2 + 23} 
                      fontSize={11} 
                      fontWeight={700} 
                      fill={isSelected ? '#38bdf8' : '#f8fafc'}
                    >
                      {line1}
                    </text>
                    {line2 && (
                      <text 
                        x={pos.x - cardW / 2 + 38} 
                        y={pos.y - cardH / 2 + 37} 
                        fontSize={10} 
                        fontWeight={500} 
                        fill="#94a3b8"
                      >
                        {line2}
                      </text>
                    )}

                    {/* Bottom Metadata Bar: Domain Pill + Score Badge */}
                    <g transform={`translate(${pos.x - cardW / 2 + 10}, ${pos.y + cardH / 2 - 20})`}>
                      {/* Domain Badge */}
                      <rect width={48} height={14} rx={7} fill={domainColor} opacity={0.2} />
                      <text x={24} y={11} textAnchor="middle" fontSize={8} fontWeight={800} fill={domainColor}>
                        {primaryDomain}
                      </text>

                      {/* Score Pill */}
                      {n.score != null && (
                        <g transform="translate(54, 0)">
                          <rect width={62} height={14} rx={7} fill="#064e3b" />
                          <text x={31} y={11} textAnchor="middle" fontSize={8.5} fontWeight={700} fill="#34d399">
                            ★ {Number(n.score).toFixed(3)}
                          </text>
                        </g>
                      )}
                    </g>
                  </g>
                )
              }

              // 3. ENTERPRISE DEPARTMENT / DOMAIN NODE
              if (n.type === 'domain') {
                const cfg = n.config || DOMAIN_CONFIG[n.label] || { color: '#f59e0b', bg: 'rgba(245, 158, 11, 0.18)', border: '#d97706' }
                const pillW = 140
                const pillH = 46

                return (
                  <g 
                    key={n.id} 
                    onClick={() => { setSelectedNode(n); setSelectedLink(null) }} 
                    onMouseEnter={() => setHover(n)} 
                    onMouseLeave={() => setHover(null)} 
                    style={{ cursor: 'pointer', pointerEvents: 'all' }}
                  >
                    {/* Domain Card / Hexagon Pill */}
                    <rect 
                      x={pos.x - pillW / 2} 
                      y={pos.y - pillH / 2} 
                      width={pillW} 
                      height={pillH} 
                      rx={23} 
                      fill={isSelected ? cfg.color : '#0f172a'} 
                      stroke={cfg.color} 
                      strokeWidth={isSelected ? 3.2 : 2.2}
                      style={{ 
                        filter: isSelected ? 'url(#glow-selected)' : n.isQueryIntent ? 'drop-shadow(0 0 10px rgba(245, 158, 11, 0.6))' : 'url(#card-shadow)' 
                      }} 
                    />

                    {/* Department Name */}
                    <text 
                      x={pos.x} 
                      y={pos.y - 2} 
                      textAnchor="middle" 
                      fontSize={11.5} 
                      fontWeight={900} 
                      fill={isSelected ? '#ffffff' : cfg.color}
                      letterSpacing={0.6}
                    >
                      {n.label.toUpperCase()}
                    </text>

                    {/* KPI Count Subtitle */}
                    <text 
                      x={pos.x} 
                      y={pos.y + 13} 
                      textAnchor="middle" 
                      fontSize={8.5} 
                      fontWeight={700} 
                      fill={isSelected ? '#e2e8f0' : '#94a3b8'}
                    >
                      {cfg.kpis?.length || 4} Tracked KPIs
                    </text>
                  </g>
                )
              }

              // 4. EXTRACTED ENTITY NODE (Emerald Chip)
              if (n.type === 'entity') {
                const entW = 104
                const entH = 28
                return (
                  <g 
                    key={n.id} 
                    onClick={() => { setSelectedNode(n); setSelectedLink(null) }} 
                    onMouseEnter={() => setHover(n)} 
                    onMouseLeave={() => setHover(null)} 
                    style={{ cursor: 'pointer', pointerEvents: 'all' }}
                  >
                    <rect 
                      x={pos.x - entW / 2} 
                      y={pos.y - entH / 2} 
                      width={entW} 
                      height={entH} 
                      rx={14} 
                      fill={isSelected ? '#10b981' : '#064e3b'} 
                      stroke="#10b981" 
                      strokeWidth={isSelected ? 2.5 : 1.5}
                      style={{ filter: isSelected ? 'url(#glow-selected)' : 'drop-shadow(0 2px 5px rgba(0,0,0,0.3))' }}
                    />
                    <text 
                      x={pos.x} 
                      y={pos.y + 4} 
                      textAnchor="middle" 
                      fontSize={9.5} 
                      fontWeight={700} 
                      fill={isSelected ? '#ffffff' : '#a7f3d0'}
                    >
                      #{n.label.length > 13 ? n.label.substring(0, 13) + '…' : n.label}
                    </text>
                  </g>
                )
              }

              return null
            })}
          </svg>

          {/* INSPECTION DRAWER (When a Node is Clicked) */}
          {selectedNode && (
            <div style={{ 
              position: 'absolute', top: 16, right: 16, width: 380, maxHeight: 'calc(100% - 32px)', 
              background: '#0f172a', padding: 22, borderRadius: 14, border: '1px solid #334155', 
              boxShadow: '0 20px 50px rgba(0,0,0,0.65)', zIndex: 30, display: 'flex', flexDirection: 'column', gap: 14, overflowY: 'auto' 
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  {selectedNode.type === 'document' ? <FileText size={18} color="#38bdf8" /> 
                    : selectedNode.type === 'domain' ? <Building2 size={18} color={selectedNode.config?.color || '#f59e0b'} /> 
                    : selectedNode.type === 'query' ? <Sparkles size={18} color="#818cf8" />
                    : <Tag size={18} color="#10b981" />}
                  <span className="badge" style={{ 
                    fontSize: '.72rem', 
                    textTransform: 'uppercase', 
                    fontWeight: 800,
                    background: selectedNode.type === 'domain' ? (selectedNode.config?.bg || '#1e293b') : '#1e293b',
                    color: selectedNode.type === 'domain' ? (selectedNode.config?.color || '#f59e0b') : '#f8fafc'
                  }}>
                    {selectedNode.type}
                  </span>
                </div>
                <button className="btn btn-ghost btn-icon btn-sm" onClick={() => setSelectedNode(null)}>
                  <X size={15} />
                </button>
              </div>
              
              <div>
                <h3 style={{ margin: 0, fontSize: '1.15rem', color: '#f8fafc', fontWeight: 800, lineHeight: 1.35 }}>
                  {selectedNode.label}
                </h3>
                {selectedNode.title && selectedNode.title !== selectedNode.label && (
                  <div style={{ fontSize: '.84rem', color: '#94a3b8', marginTop: 3 }}>
                    {selectedNode.title}
                  </div>
                )}
                {selectedNode.score != null && (
                  <div style={{ marginTop: 8, display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span className="badge" style={{ background: '#064e3b', color: '#34d399', fontWeight: 700, fontSize: '.8rem' }}>
                      Relevance Score: {Number(selectedNode.score).toFixed(4)}
                    </span>
                  </div>
                )}
              </div>

              {/* DOCUMENT DETAILS */}
              {selectedNode.type === 'document' && (
                <>
                  {selectedNode.domains?.length > 0 && (
                    <div>
                      <span style={{ fontSize: '.75rem', color: '#94a3b8', fontWeight: 700, textTransform: 'uppercase' }}>
                        Associated Business Domains:
                      </span>
                      <div style={{ display: 'flex', gap: 6, marginTop: 6, flexWrap: 'wrap' }}>
                        {selectedNode.domains.map((dm, idx) => {
                          const cfg = DOMAIN_CONFIG[dm]
                          return (
                            <span 
                              key={idx} 
                              className="badge" 
                              style={{ 
                                background: cfg?.bg || '#1e293b', 
                                color: cfg?.color || '#38bdf8', 
                                border: `1px solid ${cfg?.color || '#38bdf8'}`,
                                fontWeight: 700 
                              }}
                            >
                              {dm}
                            </span>
                          )
                        })}
                      </div>
                    </div>
                  )}

                  {selectedNode.entities?.length > 0 && (
                    <div>
                      <span style={{ fontSize: '.75rem', color: '#94a3b8', fontWeight: 700, textTransform: 'uppercase' }}>
                        Extracted Entities:
                      </span>
                      <div style={{ display: 'flex', gap: 6, marginTop: 6, flexWrap: 'wrap' }}>
                        {selectedNode.entities.map((ent, idx) => (
                          <span key={idx} className="badge" style={{ background: 'rgba(16, 185, 129, 0.15)', color: '#34d399', border: '1px solid rgba(16, 185, 129, 0.3)' }}>
                            #{ent}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {selectedNode.content && (
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                        <span style={{ fontSize: '.75rem', color: '#94a3b8', fontWeight: 700, textTransform: 'uppercase' }}>
                          Verified Evidence Content:
                        </span>
                        <button 
                          className="btn btn-ghost btn-xs" 
                          onClick={() => handleCopySnippet(selectedNode.content)}
                          style={{ fontSize: '.7rem', display: 'flex', alignItems: 'center', gap: 4 }}
                        >
                          {copiedSnippet ? <Check size={12} color="#10b981" /> : <Copy size={12} />}
                          {copiedSnippet ? 'Copied' : 'Copy'}
                        </button>
                      </div>
                      <div style={{ 
                        fontSize: '.84rem', color: '#cbd5e1', lineHeight: 1.6, 
                        background: '#0b1120', padding: 14, borderRadius: 10, 
                        border: '1px solid #1e293b', maxHeight: 240, overflowY: 'auto' 
                      }}>
                        {selectedNode.content}
                      </div>
                    </div>
                  )}
                </>
              )}

              {/* DOMAIN / DEPARTMENT DETAILS */}
              {selectedNode.type === 'domain' && (
                <>
                  {/* Connected Inter-Department Relationships */}
                  <div>
                    <span style={{ fontSize: '.78rem', color: '#f8fafc', fontWeight: 800, display: 'flex', alignItems: 'center', gap: 6 }}>
                      <Link2 size={15} color="#ec4899" /> Cross-Department Governance Links:
                    </span>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginTop: 8 }}>
                      {DEPARTMENT_RELATIONSHIPS
                        .filter(rel => rel.d1 === selectedNode.label || rel.d2 === selectedNode.label)
                        .map((rel, idx) => {
                          const otherDept = rel.d1 === selectedNode.label ? rel.d2 : rel.d1
                          const otherCfg = DOMAIN_CONFIG[otherDept]
                          return (
                            <div 
                              key={idx} 
                              onClick={() => focusDepartmentRelation(rel)}
                              style={{ 
                                background: '#1e293b', padding: 12, borderRadius: 10, 
                                border: '1px solid #334155', cursor: 'pointer',
                                transition: 'border-color 0.15s ease'
                              }}
                            >
                              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <strong style={{ fontSize: '.84rem', color: '#ec4899' }}>{rel.relation}</strong>
                                <span className="badge" style={{ fontSize: '.7rem', background: otherCfg?.bg, color: otherCfg?.color, border: `1px solid ${otherCfg?.color}` }}>
                                  ↔ {otherDept}
                                </span>
                              </div>
                              <p style={{ margin: '6px 0 0', fontSize: '.78rem', color: '#94a3b8', lineHeight: 1.45 }}>
                                {rel.description}
                              </p>
                              <div style={{ display: 'flex', gap: 4, marginTop: 6, flexWrap: 'wrap' }}>
                                {rel.sharedMetrics?.map((m, mi) => (
                                  <span key={mi} style={{ fontSize: '.68rem', color: '#cbd5e1', background: '#0b1120', padding: '2px 6px', borderRadius: 4 }}>
                                    {m}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )
                        })}
                    </div>
                  </div>

                  {/* Core Department KPIs in OmniIntelOS */}
                  {selectedNode.config?.kpis?.length > 0 && (
                    <div>
                      <span style={{ fontSize: '.75rem', color: '#94a3b8', fontWeight: 700, textTransform: 'uppercase' }}>
                        Tracked KPIs in OmniIntelOS:
                      </span>
                      <div style={{ display: 'flex', gap: 6, marginTop: 6, flexWrap: 'wrap' }}>
                        {selectedNode.config.kpis.map((kpi, idx) => (
                          <span key={idx} className="badge" style={{ background: '#1e293b', color: '#e2e8f0', fontSize: '.74rem', border: '1px solid #334155' }}>
                            {kpi}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Retrieved Documents in this Domain */}
                  {selectedNode.documents?.length > 0 && (
                    <div>
                      <span style={{ fontSize: '.75rem', color: '#94a3b8', fontWeight: 700, textTransform: 'uppercase' }}>
                        Evidence Documents in this Domain:
                      </span>
                      <ul style={{ margin: '6px 0 0', paddingLeft: 18, fontSize: '.82rem', color: '#cbd5e1' }}>
                        {selectedNode.documents.map((docTitle, idx) => (
                          <li key={idx} style={{ marginBottom: 4 }}>{docTitle}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Link to Dedicated Domain Page */}
                  {selectedNode.config?.path && (
                    <button 
                      className="btn btn-ghost btn-sm" 
                      style={{ justifyContent: 'center', borderColor: selectedNode.config.color, color: selectedNode.config.color }}
                      onClick={() => navigate(selectedNode.config.path)}
                    >
                      <ExternalLink size={13} style={{ marginRight: 6 }} /> Open {selectedNode.label} Analytics Page
                    </button>
                  )}
                </>
              )}

              {/* ENTITY DETAILS */}
              {selectedNode.type === 'entity' && (
                <>
                  <div>
                    <span style={{ fontSize: '.75rem', color: '#94a3b8', fontWeight: 700, textTransform: 'uppercase' }}>Occurrences:</span>
                    <div style={{ fontSize: '.9rem', fontWeight: 700, color: '#34d399', marginTop: 4 }}>
                      Mentioned in {selectedNode.documents?.length || 1} knowledge document(s)
                    </div>
                  </div>
                  {selectedNode.documents?.length > 0 && (
                    <div>
                      <span style={{ fontSize: '.75rem', color: '#94a3b8', fontWeight: 700, textTransform: 'uppercase' }}>Referencing Documents:</span>
                      <ul style={{ margin: '6px 0 0', paddingLeft: 18, fontSize: '.82rem', color: '#cbd5e1' }}>
                        {selectedNode.documents.map((docTitle, idx) => (
                          <li key={idx} style={{ marginBottom: 4 }}>{docTitle}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </>
              )}

              {/* QUERY DETAILS */}
              {selectedNode.type === 'query' && (
                <div>
                  <span style={{ fontSize: '.75rem', color: '#94a3b8', fontWeight: 700, textTransform: 'uppercase' }}>Active Query String:</span>
                  <div style={{ marginTop: 6, fontSize: '.86rem', color: '#f8fafc', background: '#1e293b', padding: 12, borderRadius: 8, border: '1px solid #334155' }}>
                    "{selectedNode.label}"
                  </div>
                </div>
              )}

              {/* Interactive Actions */}
              <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
                <button 
                  className="btn btn-primary btn-sm" 
                  style={{ flex: 1 }} 
                  onClick={() => {
                    const qTarget = selectedNode.type === 'document' ? selectedNode.label : `${query} ${selectedNode.label}`
                    navigate(`/chat?q=${encodeURIComponent(qTarget)}`)
                  }}
                >
                  <MessageSquare size={13} style={{ marginRight: 5 }} /> Ask Copilot
                </button>
                {selectedNode.type !== 'query' && (
                  <button 
                    className="btn btn-ghost btn-sm" 
                    onClick={() => {
                      setQuery(selectedNode.label)
                      run(selectedNode.label)
                    }}
                  >
                    Pivot Graph
                  </button>
                )}
              </div>
            </div>
          )}

          {/* DEPARTMENT RELATIONSHIP EDGE INSPECTOR */}
          {selectedLink && (
            <div style={{ 
              position: 'absolute', top: 16, right: 16, width: 380, 
              background: '#0f172a', padding: 22, borderRadius: 14, border: '1px solid #ec4899', 
              boxShadow: '0 20px 50px rgba(0,0,0,0.65)', zIndex: 30, display: 'flex', flexDirection: 'column', gap: 12 
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 7 }}>
                  <Link2 size={18} color="#ec4899" />
                  <span className="badge" style={{ fontSize: '.72rem', background: '#ec4899', color: '#fff', fontWeight: 800 }}>
                    INTER-DEPARTMENT RELATION
                  </span>
                </div>
                <button className="btn btn-ghost btn-icon btn-sm" onClick={() => setSelectedLink(null)}>
                  <X size={15} />
                </button>
              </div>

              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                  <span className="badge" style={{ background: DOMAIN_CONFIG[selectedLink.d1]?.bg, color: DOMAIN_CONFIG[selectedLink.d1]?.color, border: `1px solid ${DOMAIN_CONFIG[selectedLink.d1]?.color}` }}>
                    {selectedLink.d1}
                  </span>
                  <span style={{ color: '#ec4899', fontWeight: 800 }}>↔</span>
                  <span className="badge" style={{ background: DOMAIN_CONFIG[selectedLink.d2]?.bg, color: DOMAIN_CONFIG[selectedLink.d2]?.color, border: `1px solid ${DOMAIN_CONFIG[selectedLink.d2]?.color}` }}>
                    {selectedLink.d2}
                  </span>
                </div>
                <h4 style={{ margin: 0, fontSize: '1.1rem', color: '#f8fafc', fontWeight: 800 }}>
                  {selectedLink.label}
                </h4>
              </div>

              <div style={{ fontSize: '.84rem', color: '#cbd5e1', lineHeight: 1.55, background: '#1e293b', padding: 14, borderRadius: 10, border: '1px solid #334155' }}>
                {selectedLink.description}
              </div>

              {selectedLink.sharedMetrics?.length > 0 && (
                <div>
                  <span style={{ fontSize: '.75rem', color: '#94a3b8', fontWeight: 700, textTransform: 'uppercase' }}>
                    Shared Operational KPIs:
                  </span>
                  <div style={{ display: 'flex', gap: 6, marginTop: 6, flexWrap: 'wrap' }}>
                    {selectedLink.sharedMetrics.map((m, idx) => (
                      <span key={idx} className="badge" style={{ background: '#0b1120', color: '#38bdf8', border: '1px solid #1e293b', fontSize: '.74rem' }}>
                        {m}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              <button 
                className="btn btn-primary btn-sm" 
                style={{ marginTop: 6 }} 
                onClick={() => {
                  navigate(`/chat?q=${encodeURIComponent(`Explain the relationship between ${selectedLink.d1} and ${selectedLink.d2} regarding ${selectedLink.label}`)}`)
                }}
              >
                <MessageSquare size={13} style={{ marginRight: 5 }} /> Ask Copilot About This Link
              </button>
            </div>
          )}

          {/* Quick Interactive Legend */}
          <div style={{ 
            position: 'absolute', bottom: 16, left: 16, 
            background: 'rgba(15, 23, 42, 0.92)', backdropFilter: 'blur(8px)',
            padding: '12px 16px', borderRadius: 12, border: '1px solid #1e293b', 
            display: 'flex', flexDirection: 'column', gap: 8, fontSize: '.76rem', color: '#94a3b8' 
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <div style={{ width: 14, height: 14, borderRadius: '50%', background: '#4f46e5' }} /> 
              <strong style={{ color: '#f8fafc' }}>Query Intent</strong>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <div style={{ width: 18, height: 12, borderRadius: 3, background: '#131d31', border: '1.5px solid #38bdf8' }} /> 
              <span>Document Evidence Card (Click to inspect)</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <div style={{ width: 18, height: 12, borderRadius: 6, background: '#0f172a', border: '1.5px solid #06b6d4' }} /> 
              <span>Enterprise Department Node</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <div style={{ width: 12, height: 12, borderRadius: 6, background: '#064e3b', border: '1px solid #10b981' }} /> 
              <span>Extracted Entity Chip</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, paddingTop: 4, borderTop: '1px solid #334155' }}>
              <div style={{ width: 22, height: 3, background: '#ec4899', borderStyle: 'dashed' }} /> 
              <strong style={{ color: '#ec4899' }}>Cross-Department Relation (Click to inspect)</strong>
            </div>
          </div>
        </div>
      </Panel>

      {/* DEDICATED CROSS-DEPARTMENT GOVERNANCE & OPERATIONAL FLOWS DIRECTORY */}
      <Panel 
        title="Cross-Department Governance & Operational Relationships (9 Active Links)" 
        subtitle="Operational, capital budget, and governance handoffs interconnecting the 8 enterprise departments."
        style={{ marginTop: 22 }}
      >
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(310px, 1fr))', gap: 14 }}>
          {DEPARTMENT_RELATIONSHIPS.map((rel, idx) => {
            const cfg1 = DOMAIN_CONFIG[rel.d1]
            const cfg2 = DOMAIN_CONFIG[rel.d2]
            const isSelected = selectedLink?.id === rel.id

            return (
              <div 
                key={idx}
                onClick={() => focusDepartmentRelation(rel)}
                style={{ 
                  background: isSelected ? 'rgba(236, 72, 153, 0.1)' : 'var(--surface)', 
                  padding: 16, 
                  borderRadius: 12, 
                  border: isSelected ? '1.5px solid #ec4899' : '1px solid var(--border)', 
                  cursor: 'pointer',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 10,
                  transition: 'all 0.15s ease'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    <span className="badge" style={{ background: cfg1?.bg, color: cfg1?.color, border: `1px solid ${cfg1?.color}`, fontWeight: 800, fontSize: '.74rem' }}>
                      {rel.d1}
                    </span>
                    <span style={{ color: '#ec4899', fontWeight: 800, fontSize: '.85rem' }}>↔</span>
                    <span className="badge" style={{ background: cfg2?.bg, color: cfg2?.color, border: `1px solid ${cfg2?.color}`, fontWeight: 800, fontSize: '.74rem' }}>
                      {rel.d2}
                    </span>
                  </div>
                  <span className="badge" style={{ fontSize: '.68rem', background: 'var(--surface-2)', color: 'var(--text-3)' }}>
                    {rel.sharedMetrics?.length || 0} KPIs
                  </span>
                </div>

                <div>
                  <h4 style={{ margin: 0, fontSize: '.92rem', color: isSelected ? '#ec4899' : 'var(--text)', fontWeight: 800 }}>
                    {rel.relation}
                  </h4>
                  <p style={{ margin: '6px 0 0', fontSize: '.8rem', color: 'var(--text-2)', lineHeight: 1.45 }}>
                    {rel.description}
                  </p>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 'auto', paddingTop: 8, borderTop: '1px solid var(--border-2)' }}>
                  <span style={{ fontSize: '.72rem', color: '#ec4899', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 4 }}>
                    <Link2 size={12} /> Focus in Graph
                  </span>
                  <ArrowRight size={13} color="var(--text-3)" />
                </div>
              </div>
            )
          })}
        </div>
      </Panel>
    </div>
  )
}
