import { useState } from 'react'
import { useTranslation } from '../i18n/I18nContext'
import { PageHeader, Panel, Grid } from '../components/ui'
import {
  LifeBuoy, Sparkles, MessageSquare, Users, Shield,
  UploadCloud, Download, Globe2, ChevronDown, ChevronRight,
  BarChart3, BookOpen, Terminal,
} from 'lucide-react'

// ─────────────────────────────────────────────────────────────────────────
// Content is grounded in the actual routed pages (frontend/src/App.jsx),
// the sidebar (frontend/src/components/Sidebar.jsx) and the RBAC role table
// (src/core/jwt_auth.py ROLE_DEFINITIONS) — not invented feature copy.
// ─────────────────────────────────────────────────────────────────────────

const ROLES = [
  { role: 'admin', desc: 'Full access — every page, every action, every data domain, plus user management, scenario switching and vector reindex.' },
  { role: 'ceo', desc: 'Cross-domain view: dashboard, analytics, forecasting, ESG, risk, HR, logistics, IT, operations.' },
  { role: 'cfo', desc: 'Financial statements, forecasting, budget analysis — data scoped to Finance & Growth.' },
  { role: 'cto', desc: 'IT operations, DevOps metrics, security posture, risk — data scoped to IT.' },
  { role: 'coo', desc: 'Operations, logistics, forecasting — data scoped to Operations & Logistics.' },
  { role: 'chro / hr', desc: 'Workforce analytics: headcount, turnover, recruitment, training — data scoped to People.' },
  { role: 'esg', desc: 'Environment, social and governance scorecards.' },
  { role: 'risk', desc: 'Risk radar, anomaly detection, plus admin audit-log read access.' },
  { role: 'analyst / board / viewer', desc: 'Read-focused access for reporting and oversight, with narrower page sets.' },
]

const NAV_SECTIONS = [
  {
    icon: Sparkles, title: 'Overview', accent: 'var(--primary)',
    items: [
      { label: 'Workspace', detail: 'Landing page after login — a persona-aware summary of what matters to your role today.' },
      { label: 'Dashboard', detail: 'Cross-domain KPI overview: the 90+ curated metrics across Finance, HR, IT, Ops, Logistics, ESG and Growth.' },
      { label: 'Analytics', detail: 'Deeper KPI exploration with period/category/segment filters, backed by GET /api/v1/kpis.' },
      { label: 'Forecasting', detail: 'Pick a metric, get a regression-based forecast with confidence framing (ForecastEngine, explain_forecast).' },
      { label: 'Risk Radar', detail: 'Composite risk score from KPI volatility, anomaly count, revenue concentration and liquidity/execution proxies.' },
      { label: 'Financial', detail: 'Income statement, balance sheet and cash-flow statements per period, with computed margins/ratios.' },
    ],
  },
  {
    icon: BarChart3, title: 'Domains', accent: 'var(--ok)',
    items: [
      { label: 'Growth', detail: 'SaaS metrics — MRR, ARR, CAC, LTV, churn — with a 12-point trend.' },
      { label: 'HR', detail: 'Headcount, turnover, satisfaction, recruitment funnel, training completion, department breakdowns.' },
      { label: 'IT', detail: 'Uptime, ticket backlog, MTTR, security score, DORA-style DevOps metrics.' },
      { label: 'Operations', detail: 'OEE/efficiency, quality/defect rate, throughput, safety incidents, process-area breakdown.' },
      { label: 'Logistics', detail: 'On-time delivery, fill rate, inventory turnover, warehouse and supplier performance.' },
      { label: 'ESG', detail: 'Environment (carbon, renewables), social (diversity, community investment) and governance sub-scores.' },
    ],
  },
  {
    icon: BookOpen, title: 'Knowledge & System', accent: 'var(--warn)',
    items: [
      { label: 'Knowledge', detail: 'Search the ingested knowledge base directly — the same hybrid retrieval (vector + BM25 + reranker) the copilot uses.' },
      { label: 'Knowledge Graph', detail: 'Multi-hop entity relationships across domains (GraphRAG-lite) for cross-domain questions.' },
      { label: 'Glossary', detail: 'Authoritative, sourced definitions for every tracked metric — available in EN and FR.' },
      { label: 'Reports', detail: 'Board-ready report generation, drawing on KPIs, insights and the knowledge base.' },
      { label: 'Compare Personas', detail: 'Ask the same question through two different persona lenses side by side.' },
      { label: 'Organization', detail: 'Org-wide structural view (headcount, departments) built on the HR and analytics data.' },
      { label: 'Data Hub', detail: 'Central place to upload CSV metrics or documents (PDF, images, text) into the platform.' },
      { label: 'Governance', detail: 'RBAC role table, audit-trail visibility, and platform governance controls (admin role).' },
      { label: 'Admin', detail: 'User management, benchmarking scenarios, vector-store reindex, safe data cleanup (admin role).' },
      { label: 'Settings', detail: 'Personal preferences — language, and per-user configuration.' },
    ],
  },
]

const INGEST_EXPORT = [
  { icon: UploadCloud, title: 'Bringing data in', points: [
    'CSV upload (Data Hub) — bulk metric rows, mapped to metric/value/period/category/segment.',
    'Document upload — PDF (text extraction), PPTX/DOCX/XLSX (native text extraction — read directly from the file, not OCR), PNG/JPG (vision-model OCR), or plain text — indexed into the knowledge base for the copilot to cite. PII/secrets are redacted before storage.',
    'Audio upload — meeting recordings and voice notes are transcribed (speech-to-text) and summarized (participants, decisions, action items) automatically, then indexed alongside the rest of the knowledge base.',
    'Webhook intake — for external systems to push KPI rows or knowledge documents directly.',
  ]},
  { icon: Download, title: 'Getting data out', points: [
    'Export any KPI view or the knowledge base as CSV, JSON, XLSX, or a formatted board-ready PDF.',
    'Exports are available from the export control in the top bar on most pages.',
  ]},
]

function Section({ icon: Icon, title, accent, children, defaultOpen = true }) {
  const [open, setOpen] = useState(defaultOpen)
  return (
    <div className="card" style={{ marginBottom: 14 }}>
      <button
        onClick={() => setOpen(o => !o)}
        className="btn btn-ghost"
        style={{ width: '100%', justifyContent: 'space-between', display: 'flex', alignItems: 'center', padding: '4px 0' }}
      >
        <span style={{ display: 'flex', alignItems: 'center', gap: 10, fontWeight: 700, fontSize: '1rem' }}>
          <span className="kpi-icon-wrap" style={{ width: 32, height: 32, margin: 0, borderRadius: 9, background: `color-mix(in srgb, ${accent} 16%, transparent)`, color: accent }}>
            <Icon size={16} />
          </span>
          {title}
        </span>
        {open ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
      </button>
      {open && <div style={{ marginTop: 14 }}>{children}</div>}
    </div>
  )
}

export default function UserGuidePage() {
  const { t } = useTranslation()

  return (
    <div>
      <PageHeader
        icon={LifeBuoy}
        title={t('navUserGuide') || 'User Guide'}
        subtitle="How to navigate IntelAI — the persona-aware AI analytics & RAG copilot platform"
      />

      {/* What is IntelAI */}
      <Section icon={Sparkles} title="What is IntelAI?" accent="var(--primary)">
        <p style={{ margin: 0, fontSize: '.9rem', color: 'var(--text-2)', lineHeight: 1.7 }}>
          IntelAI is a 9-persona, role-scoped analytics copilot on top of your KPI data and documents. Every role
          (CEO, CFO, CTO, COO, CHRO, ESG, Risk, Analyst, plus a general Assistant) sees the metrics and knowledge
          it's scoped to, asks questions in plain language, and gets grounded answers with citations — powered by
          hybrid retrieval (vector search fused with BM25 and a GraphRAG-lite entity graph), ML forecasting, and
          board-ready exports. The UI is fully bilingual (English/French).
        </p>
      </Section>

      {/* Getting started / roles */}
      <Section icon={Users} title="Getting started: roles & demo login" accent="var(--ok)">
        <p style={{ margin: '0 0 12px', fontSize: '.86rem', color: 'var(--text-2)', lineHeight: 1.6 }}>
          On the login screen, use <b>"Try as…"</b> to get an instant, password-less session for any role
          (this calls <code>POST /api/v1/auth/demo-login</code>). Each role only sees the pages and data
          categories granted to it — the sidebar and every page below automatically adapt.
        </p>
        <Grid min={260}>
          {ROLES.map(r => (
            <div key={r.role} className="card" style={{ padding: '12px 14px' }}>
              <div style={{ fontWeight: 700, fontSize: '.85rem', marginBottom: 4, textTransform: 'capitalize' }}>{r.role}</div>
              <div style={{ fontSize: '.78rem', color: 'var(--text-3)', lineHeight: 1.5 }}>{r.desc}</div>
            </div>
          ))}
        </Grid>
      </Section>

      {/* Copilot */}
      <Section icon={MessageSquare} title="Using the Copilot" accent="var(--accent, var(--primary))">
        <div style={{ fontSize: '.86rem', color: 'var(--text-2)', lineHeight: 1.7 }}>
          <p style={{ marginTop: 0 }}>
            The Copilot (pinned at the top of the sidebar) is the fastest way to get an answer. Ask anything in
            natural language — it auto-retrieves a role-scoped KPI snapshot plus relevant knowledge documents,
            then answers with inline citations. Responses stream in real time over WebSocket, with a graceful
            fallback to a regular request if the socket can't connect.
          </p>
          <ul style={{ margin: '0 0 0 18px', padding: 0 }}>
            <li>Every non-chat page has a floating mini-copilot and an <b>Explain</b> button in the top bar that opens a glossary-grounded explainer for that page's domain.</li>
            <li>Chat history is persisted per session — use the history sidebar on the Copilot page to rename, revisit or delete past conversations.</li>
            <li>Use <b>Compare Personas</b> to see how two roles (e.g. CFO vs. COO) answer the same question differently, based on their scoped data.</li>
          </ul>
        </div>
      </Section>

      {/* Navigation walkthrough */}
      {NAV_SECTIONS.map(section => (
        <Section key={section.title} icon={section.icon} title={section.title} accent={section.accent}>
          <div style={{ display: 'grid', gap: 10 }}>
            {section.items.map(item => (
              <div key={item.label} style={{ display: 'flex', gap: 10, alignItems: 'flex-start' }}>
                <span style={{ color: 'var(--text-3)', fontSize: '.8rem', marginTop: 2 }}>&bull;</span>
                <div style={{ fontSize: '.85rem', lineHeight: 1.55 }}>
                  <b>{item.label}</b>
                  <span style={{ color: 'var(--text-3)' }}> — {item.detail}</span>
                </div>
              </div>
            ))}
          </div>
        </Section>
      ))}

      {/* Ingest / export */}
      <Section icon={UploadCloud} title="Bringing data in & getting it out" accent="var(--warn)">
        <Grid min={280}>
          {INGEST_EXPORT.map(block => (
            <div key={block.title} className="card" style={{ padding: 16 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontWeight: 700, fontSize: '.88rem', marginBottom: 10 }}>
                <block.icon size={16} color="var(--primary)" /> {block.title}
              </div>
              <ul style={{ margin: 0, paddingLeft: 18, fontSize: '.8rem', color: 'var(--text-3)', lineHeight: 1.6 }}>
                {block.points.map((p, i) => <li key={i}>{p}</li>)}
              </ul>
            </div>
          ))}
        </Grid>
      </Section>

      {/* Security */}
      <Section icon={Shield} title="Security & access control" accent="var(--bad)">
        <ul style={{ margin: 0, paddingLeft: 18, fontSize: '.85rem', color: 'var(--text-2)', lineHeight: 1.7 }}>
          <li>Authentication is a Bearer JWT (8-hour expiry) issued by <code>/api/v1/auth/login</code> or <code>/api/v1/auth/demo-login</code>.</li>
          <li>Every page and every action is gated by your role's RBAC grants — pages, actions and data-category access are all enforced server-side, not just hidden in the UI. View the full role table on the <b>Governance</b> page.</li>
          <li>Admin actions (user management, scenario switching, reindexing) are further restricted to the <code>admin</code> role and recorded in the audit log.</li>
          <li>Uploaded documents pass through PII/secret redaction before being stored or indexed.</li>
        </ul>
      </Section>

      {/* Language */}
      <Section icon={Globe2} title="Language" accent="var(--primary)" defaultOpen={false}>
        <p style={{ margin: 0, fontSize: '.85rem', color: 'var(--text-2)', lineHeight: 1.6 }}>
          Toggle <b>EN / FR</b> from the top bar on any page. The UI, the glossary, and Copilot responses all
          respect the selected language — French definitions are static where curated, with an LLM-translated
          fallback for anything not yet covered (numbers and formulas are never altered).
        </p>
      </Section>

      {/* Cross-link to API docs */}
      <div className="card" style={{ display: 'flex', gap: 12, alignItems: 'center', padding: '16px 18px' }}>
        <span className="kpi-icon-wrap" style={{ width: 36, height: 36, margin: 0, borderRadius: 10, background: 'color-mix(in srgb, var(--primary) 16%, transparent)', color: 'var(--primary)' }}>
          <Terminal size={18} />
        </span>
        <div style={{ fontSize: '.85rem', color: 'var(--text-2)' }}>
          Building an integration instead? See the full <b>API Reference</b> in the sidebar for every REST and
          WebSocket endpoint, with request/response shapes and ready-to-run cURL examples.
        </div>
      </div>
    </div>
  )
}
