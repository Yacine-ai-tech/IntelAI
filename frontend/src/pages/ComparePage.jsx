// Persona compare — the same question through two executive lenses, side by side.
// Two real /chat calls with different persona scoping. Shows how the same data yields
// different answers, sources and scope per role — the product's core differentiator.
import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { GitCompareArrows, Send, Loader2, AlertTriangle, Crown, DollarSign, Cpu, Settings2, Users, Leaf, ShieldAlert, BarChart3, Bot } from 'lucide-react'
import * as api from '../api'
import { PageHeader, Citations, Panel } from '../components/ui'

const ICON = { general: Bot, ceo: Crown, cfo: DollarSign, cto: Cpu, coo: Settings2, chro: Users, esg: Leaf, risk: ShieldAlert, analyst: BarChart3 }
const COLOR = { general: 'var(--p-general)', ceo: 'var(--p-ceo)', cfo: 'var(--p-cfo)', cto: 'var(--p-cto)', coo: 'var(--p-coo)', chro: 'var(--p-chro)', esg: 'var(--p-esg)', risk: 'var(--p-risk)', analyst: 'var(--p-analyst)' }

export default function ComparePage() {
  const { data: personas = [] } = useQuery({
    queryKey: ['personas'], queryFn: () => api.listPersonas().then(r => r.data?.personas || r.data || []),
  })
  const keys = personas.map(p => p.id || p.persona_id || p.name)

  const [question, setQuestion] = useState('What are our biggest risks and opportunities this quarter?')
  const [pa, setPa] = useState('')
  const [pb, setPb] = useState('')
  const [busy, setBusy] = useState(false)
  const [out, setOut] = useState(null)
  const [err, setErr] = useState('')

  // default to first two distinct personas once loaded
  if (!pa && keys.length) setPa(keys.includes('cfo') ? 'cfo' : keys[0])
  if (!pb && keys.length > 1) setPb(keys.includes('chro') ? 'chro' : keys[1])

  const run = async () => {
    if (!question.trim() || pa === pb) return
    setBusy(true); setErr(''); setOut(null)
    try {
      const [ra, rb] = await Promise.all([
        api.sendChat(question, pa).then(r => r.data),
        api.sendChat(question, pb).then(r => r.data),
      ])
      setOut([ra, rb])
    } catch (e) {
      setErr(e?.response?.data?.detail || e.message || 'Compare failed')
    } finally { setBusy(false) }
  }

  return (
    <div>
      <PageHeader icon={GitCompareArrows} title="Compare personas"
        subtitle="Ask one question, see two executive lenses answer it side by side — same company, different intelligence."
        accent="var(--accent)" />

      <Panel title="Question">
        <textarea value={question} onChange={e => setQuestion(e.target.value)} rows={2}
          style={{ width: '100%', background: 'var(--surface-2)', border: '1px solid var(--border-2)', borderRadius: 'var(--r)', padding: '10px 12px', color: 'var(--text)', fontSize: 14, resize: 'vertical', fontFamily: 'inherit' }} />
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12, alignItems: 'center', marginTop: 12 }}>
          <PersonaSelect label="Lens A" value={pa} onChange={setPa} personas={personas} keys={keys} />
          <PersonaSelect label="Lens B" value={pb} onChange={setPb} personas={personas} keys={keys} />
          <button className="btn btn-primary" onClick={run} disabled={busy || pa === pb || !question.trim()}>
            {busy ? <Loader2 size={14} className="spin" /> : <Send size={14} />} Compare
          </button>
          {pa === pb && <span style={{ fontSize: 12, color: 'var(--warn)' }}>Pick two different lenses.</span>}
        </div>
        {err && <div style={{ display: 'flex', gap: 8, alignItems: 'center', color: 'var(--bad)', fontSize: 13, marginTop: 10 }}><AlertTriangle size={15} /> {err}</div>}
      </Panel>

      {out && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }} className="compare-grid">
          {out.map((r, i) => <Answer key={i} persona={i === 0 ? pa : pb} r={r} />)}
        </div>
      )}
    </div>
  )
}

function PersonaSelect({ label, value, onChange, personas, keys }) {
  return (
    <label style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
      <span style={{ fontSize: 10.5, textTransform: 'uppercase', letterSpacing: '.05em', color: 'var(--text-3)' }}>{label}</span>
      <select value={value} onChange={e => onChange(e.target.value)}
        style={{ background: 'var(--surface-2)', border: '1px solid var(--border-2)', borderRadius: 'var(--r)', padding: '7px 10px', color: 'var(--text)', fontSize: 13 }}>
        {personas.map((p, idx) => {
          const k = keys[idx]
          return <option key={k} value={k}>{p.display_name || k}</option>
        })}
      </select>
    </label>
  )
}

function Answer({ persona, r }) {
  const Icon = ICON[persona] || Bot
  const color = COLOR[persona] || 'var(--primary)'
  return (
    <div style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderTop: `2px solid ${color}`, borderRadius: 'var(--r-lg)', padding: 16 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
        <span style={{ display: 'grid', placeItems: 'center', width: 28, height: 28, borderRadius: 8, background: 'var(--surface-3)', color }}><Icon size={15} /></span>
        <strong style={{ fontSize: 13.5, textTransform: 'uppercase', letterSpacing: '.03em' }}>{r.persona_used || persona}</strong>
      </div>
      <p style={{ fontSize: 13.5, lineHeight: 1.7, color: 'var(--text-2)', whiteSpace: 'pre-wrap' }}>{r.response}</p>
      {Array.isArray(r.sources) && r.sources.length > 0 && <div style={{ marginTop: 12 }}><Citations sources={r.sources} /></div>}
    </div>
  )
}
