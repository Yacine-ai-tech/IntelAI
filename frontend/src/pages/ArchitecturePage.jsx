import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  Workflow, BookOpen, TrendingUp, Play, Pause, Brain, Search, Globe, ShieldCheck, Database,
  Sparkles, Layers, Network, Gauge, FileText, Zap, Check,
} from 'lucide-react'
import { PageHeader, Panel } from '../components/ui'

const ICONS = { Brain, Search, Globe, ShieldCheck, Database, Sparkles, Layers, Network, Gauge, FileText, Zap, Workflow }

const LAYERS = ['Clients', 'Understanding', 'Evidence', 'Answer']

const NODES = [
  { id: 'api', layer: 'Clients', label: 'Chat transports', icon: 'Network',
    summary: 'Server-sent events, polled jobs, blocking call or WebSocket.',
    detail: ['The interface streams stage events, sources and answer text as they are produced.', 'A polled job carries the same stage data when streaming is not available.'],
    env: ['VITE_USE_WS', 'CHAT_TURN_TIMEOUT'] },
  { id: 'persona', layer: 'Understanding', label: 'Persona and language', icon: 'ShieldCheck',
    summary: 'Nine role-scoped personas; the answer language follows the question.',
    detail: ['The server maps each role to the personas it may use.', 'French and English are detected from accents, function words and elisions.'],
    env: ['DEFAULT_LANGUAGE'] },
  { id: 'plan', layer: 'Understanding', label: 'Web-search decision', icon: 'Zap',
    summary: 'Rules decide in microseconds whether the web is needed.',
    detail: ['Explicit requests ("search the web", "verify online") always search.', 'Questions about external companies, people or current events search automatically.', 'Questions about the organisation\'s own metrics never leave the internal data.'],
    env: ['TAVILY_API_KEY', 'WEB_SEARCH_BUDGET_SECONDS'] },
  { id: 'retrieval', layer: 'Evidence', label: 'Internal retrieval', icon: 'Database',
    summary: 'KPI snapshot, documents and glossary through hybrid retrieval.',
    detail: ['Dense embeddings and BM25 fused by reciprocal rank fusion.', 'Same-language documents are preferred; other languages stay eligible.', 'An optional cross-encoder refines the progressive knowledge search.'],
    env: ['RETRIEVAL_DENSE_K', 'RETRIEVAL_SPARSE_K', 'RERANK_IN_CHAT', 'RETRIEVAL_LANGUAGE_BOOST'] },
  { id: 'web', layer: 'Evidence', label: 'Live web search', icon: 'Globe',
    summary: 'Runs in parallel with retrieval, so it adds no waiting time of its own.',
    detail: ['Automatic searches are cut off after a short budget rather than delaying the answer.', 'Identical searches are cached for a few minutes.', 'Only the question text is sent to the search provider.'],
    env: ['WEB_SEARCH_MAX_RESULTS', 'WEB_SEARCH_TIMEOUT_SECONDS', 'WEB_SEARCH_CACHE_TTL_SECONDS'] },
  { id: 'model', layer: 'Answer', label: 'Model and streaming', icon: 'Brain',
    summary: 'Tiered models, key rotation and a streamed answer.',
    detail: ['A rate-limited key is parked and the next one is used immediately.', 'A model that fails before producing text is replaced by the tier fallback.'],
    env: ['LLM_DEFAULT', 'LLM_REASONING', 'LLM_DEFAULT_FALLBACK', 'GROQ_KEY_ATTEMPTS'] },
  { id: 'sources', layer: 'Answer', label: 'Sources and history', icon: 'FileText',
    summary: 'Knowledge-base and web sources listed separately and stored with the answer.',
    detail: ['Sources appear as soon as they are known, before the answer is written.'] },
]

const STAGES = [
  { id: 'understand', label: 'Understand', text: 'Detect the language, resolve the persona and decide by rules whether the web is needed.', nodes: ['persona', 'plan'] },
  { id: 'gather', label: 'Gather', text: 'Internal retrieval and the web search start together; sources are shown as each finishes.', nodes: ['retrieval', 'web'] },
  { id: 'prompt', label: 'Prompt', text: 'A stable persona prefix, then the evidence and the question. The prompt states what the search found.', nodes: ['model'] },
  { id: 'write', label: 'Write', text: 'Tokens stream to the page as the model produces them; rate limits rotate keys at once.', nodes: ['model', 'api'] },
  { id: 'finish', label: 'Finish', text: 'Sources and structure are returned and the turn is stored with its sources.', nodes: ['sources'] },
]

const ENDPOINTS = [
  ['POST /api/v1/chat/stream', 'Copilot turn as server-sent events'],
  ['POST /api/v1/chat/async · GET /api/v1/chat/{job}', 'Polled turn with stage data'],
  ['GET /api/v1/knowledge/search · POST …/search/async', 'Knowledge search; the async job refines progressively'],
  ['GET /api/v1/kpis · /insights/* · POST /forecast', 'KPIs, health, anomalies, forecasts'],
  ['POST /api/v1/ingest/csv · /document · /audio · /metrics', 'Data hub'],
  ['GET /api/v1/personas · /glossary · /chat/sessions', 'Personas, glossary and history'],
  ['GET /health · GET /ready', 'Liveness and readiness'],
]

const DECISIONS = [
  ['Rules decide the search', 'No model call is needed to choose, so the decision is instant and testable.'],
  ['Parallel with a budget', 'The web never makes an answer that only needs internal data slower.'],
  ['Soft language preference', 'Models are multilingual; filtering by language would hide relevant documents.'],
]

export default function ArchitecturePage() {
  const [selected, setSelected] = useState('plan')
  const [step, setStep] = useState(0)
  const [playing, setPlaying] = useState(true)
  const [filter, setFilter] = useState('')

  useEffect(() => {
    if (!playing) return undefined
    const id = setInterval(() => setStep(s => (s + 1) % (STAGES.length + 1)), 1800)
    return () => clearInterval(id)
  }, [playing])

  const current = STAGES[Math.min(step, STAGES.length - 1)]
  const lit = useMemo(() => new Set(step < STAGES.length ? current.nodes : []), [step, current])
  const node = NODES.find(n => n.id === selected) || NODES[0]
  const endpoints = ENDPOINTS.filter(([r, p]) => `${r} ${p}`.toLowerCase().includes(filter.toLowerCase()))

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', paddingBottom: 60 }}>
      <PageHeader
        icon={Workflow}
        title="Architecture"
        subtitle="How a question becomes a grounded, cited answer — and what the interface shows while it happens."
        actions={
          <div style={{ display: 'flex', gap: 10 }}>
            <Link to="/research" className="btn btn-secondary" style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}><BookOpen size={16} /> Research</Link>
            <Link to="/benchmark" className="btn btn-secondary" style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}><TrendingUp size={16} /> Benchmarks</Link>
          </div>
        }
      />

      <Panel title="Life of a chat turn" style={{ marginBottom: 24 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
          <span style={{ fontSize: '.8rem', color: 'var(--text-3)' }}>Pick a stage or let it play; the components involved are highlighted below.</span>
          <button type="button" className="btn btn-secondary btn-sm" onClick={() => setPlaying(p => !p)}>
            {playing ? <Pause size={14} /> : <Play size={14} />} {playing ? 'Pause' : 'Play'}
          </button>
        </div>
        <ol style={{ listStyle: 'none', margin: 0, padding: 0, display: 'flex', flexWrap: 'wrap', gap: 10 }}>
          {STAGES.map((s, i) => {
            const done = step >= STAGES.length || i < step
            const running = step < STAGES.length && i === step
            return (
              <li key={s.id}>
                <button type="button" onClick={() => { setPlaying(false); setStep(i) }}
                  style={{
                    display: 'inline-flex', alignItems: 'center', gap: 8, padding: '8px 12px', borderRadius: 10, cursor: 'pointer',
                    border: `1px solid ${running ? 'var(--primary)' : 'var(--border-subtle, rgba(255,255,255,.1))'}`,
                    background: running ? 'color-mix(in srgb, var(--primary) 14%, transparent)' : 'transparent',
                    color: done || running ? 'var(--text)' : 'var(--text-3)',
                  }}>
                  <span style={{ width: 18, height: 18, display: 'inline-flex', alignItems: 'center', justifyContent: 'center', color: 'var(--primary)' }}>
                    {done ? <Check size={15} /> : running ? <span style={{ width: 12, height: 12, border: '2px solid rgba(34,211,238,.25)', borderTopColor: 'var(--primary)', borderRadius: '50%', animation: 'spin .8s linear infinite' }} /> : i + 1}
                  </span>
                  {s.label}
                </button>
              </li>
            )
          })}
        </ol>
        <p style={{ margin: '14px 0 0', color: 'var(--text-2)', fontSize: '.92rem' }}>
          {step < STAGES.length ? current.text : 'Complete: the answer, its sources and the turn history are in place.'}
        </p>
      </Panel>

      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 2fr) minmax(0, 1fr)', gap: 20 }} className="arch-grid">
        <div style={{ display: 'grid', gap: 16 }}>
          {LAYERS.map(layer => (
            <Panel key={layer} title={layer}>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 12 }}>
                {NODES.filter(n => n.layer === layer).map(n => {
                  const Icon = ICONS[n.icon] || Layers
                  const active = selected === n.id
                  return (
                    <button key={n.id} type="button" onClick={() => setSelected(n.id)}
                      style={{
                        textAlign: 'left', padding: 12, borderRadius: 12, cursor: 'pointer', color: 'var(--text)',
                        border: `1px solid ${active ? 'var(--primary)' : 'var(--border-subtle, rgba(255,255,255,.1))'}`,
                        background: active ? 'color-mix(in srgb, var(--primary) 10%, transparent)' : 'transparent',
                        boxShadow: lit.has(n.id) ? '0 0 0 1px var(--primary)' : 'none',
                      }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontWeight: 600, fontSize: '.9rem' }}><Icon size={15} /> {n.label}</div>
                      <div style={{ marginTop: 4, fontSize: '.8rem', color: 'var(--text-3)' }}>{n.summary}</div>
                    </button>
                  )
                })}
              </div>
            </Panel>
          ))}
        </div>

        <Panel title={node.label} style={{ alignSelf: 'start' }}>
          <p style={{ margin: 0, color: 'var(--text-2)', fontSize: '.9rem' }}>{node.summary}</p>
          <ul style={{ margin: '12px 0 0', paddingLeft: 18, color: 'var(--text-3)', fontSize: '.8rem', display: 'grid', gap: 6 }}>
            {node.detail.map(d => <li key={d}>{d}</li>)}
          </ul>
          {node.env && (
            <div style={{ marginTop: 14 }}>
              <div style={{ fontSize: '.7rem', textTransform: 'uppercase', letterSpacing: '.06em', color: 'var(--text-3)', marginBottom: 6 }}>Configuration</div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>{node.env.map(e => <code key={e} className="badge">{e}</code>)}</div>
            </div>
          )}
        </Panel>
      </div>

      <Panel title="Interfaces" style={{ marginTop: 24 }}>
        <input value={filter} onChange={e => setFilter(e.target.value)} placeholder="Filter routes…" aria-label="Filter routes"
          style={{ width: '100%', marginBottom: 12, padding: '8px 12px', borderRadius: 8, border: '1px solid var(--border-subtle, rgba(255,255,255,.1))', background: 'transparent', color: 'var(--text)' }} />
        <div style={{ display: 'grid', gap: 0 }}>
          {endpoints.map(([r, p]) => (
            <div key={r} style={{ display: 'flex', flexWrap: 'wrap', gap: '4px 16px', padding: '8px 0', borderTop: '1px solid var(--border-subtle, rgba(255,255,255,.06))', fontSize: '.82rem' }}>
              <code style={{ minWidth: 300 }}>{r}</code><span style={{ color: 'var(--text-3)' }}>{p}</span>
            </div>
          ))}
          {endpoints.length === 0 && <div style={{ color: 'var(--text-3)', padding: '8px 0' }}>No route matches.</div>}
        </div>
      </Panel>

      <Panel title="Design decisions" style={{ marginTop: 24 }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 14 }}>
          {DECISIONS.map(([t, d]) => (
            <div key={t} style={{ padding: 14, borderRadius: 12, border: '1px solid var(--border-subtle, rgba(255,255,255,.08))' }}>
              <div style={{ fontWeight: 600, fontSize: '.9rem', marginBottom: 4 }}>{t}</div>
              <div style={{ fontSize: '.8rem', color: 'var(--text-3)' }}>{d}</div>
            </div>
          ))}
        </div>
      </Panel>
    </div>
  )
}
