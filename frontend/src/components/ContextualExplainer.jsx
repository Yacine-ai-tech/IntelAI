import { useState, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { useTranslation } from '../i18n/I18nContext'
import * as api from '../api'
import { X, Search, Sparkles, ArrowUp, ArrowDown, BookOpen } from 'lucide-react'

// A per-page contextual explainer: lists the glossary terms relevant to the current
// domain, defines each (definition + formula + how to read it + 2026 benchmark +
// source), and can hand off to the copilot for an in-context explanation.
export default function ContextualExplainer({ domain, onClose }) {
  const { t, lang } = useTranslation()
  const navigate = useNavigate()
  const [q, setQ] = useState('')
  const [active, setActive] = useState(null)

  const { data: terms = [], isLoading } = useQuery({
    queryKey: ['glossary', domain || 'all', lang],
    queryFn: () => api.getGlossary(domain || null, lang).then(r => r.data?.terms || []),
    staleTime: 3600_000,
  })

  const filtered = useMemo(() => {
    const s = q.trim().toLowerCase()
    if (!s) return terms
    return terms.filter(e =>
      e.term.toLowerCase().includes(s) ||
      (e.abbr && e.abbr.toLowerCase().includes(s)) ||
      (e.definition && e.definition.toLowerCase().includes(s)))
  }, [terms, q])

  const askCopilot = (term) => {
    onClose?.()
    navigate(`/chat?q=${encodeURIComponent(`Explain "${term}" in the context of our current numbers, and what it means for us.`)}`)
  }

  return (
    <div className="drawer-overlay" onClick={onClose}>
      <aside className="drawer" onClick={e => e.stopPropagation()}>
        <div className="drawer-header">
          <span className="page-title" style={{ fontSize: '1.05rem' }}>
            <BookOpen size={18} /> {t('explainThisPage') || 'Explain this page'}
          </span>
          <button className="btn btn-ghost btn-icon" onClick={onClose}><X size={18} /></button>
        </div>
        <p style={{ color: 'var(--text-2)', fontSize: '.82rem', padding: '0 18px 12px' }}>
          {domain ? `${domain} ${t('glossaryHint') || 'terms — definitions, formulas & 2026 benchmarks.'}`
                  : (t('glossaryHintAll') || 'Every metric & concept — defined, with formulas and benchmarks.')}
        </p>

        <div style={{ padding: '0 18px 12px' }}>
          <div className="chat-input-wrap" style={{ padding: '6px 12px' }}>
            <Search size={15} style={{ color: 'var(--text-3)' }} />
            <input className="chat-input" style={{ padding: '4px 0' }} placeholder={t('searchTerms') || 'Search terms…'}
              value={q} onChange={e => setQ(e.target.value)} />
          </div>
        </div>

        <div className="drawer-body">
          {isLoading && <div className="spinner" style={{ margin: '30px auto' }} />}
          {!isLoading && filtered.map(e => {
            const open = active === e.term
            return (
              <div key={e.term} className={`gloss-item${open ? ' open' : ''}`}>
                <button className="gloss-head" onClick={() => setActive(open ? null : e.term)}>
                  <span className="gloss-term">
                    {e.term}{e.abbr && e.abbr !== e.term ? <span className="gloss-abbr">{e.abbr}</span> : null}
                  </span>
                  {e.direction === 'up' && <ArrowUp size={13} style={{ color: 'var(--ok)' }} title="Higher is better" />}
                  {e.direction === 'down' && <ArrowDown size={13} style={{ color: 'var(--ok)' }} title="Lower is better" />}
                </button>
                {open && (
                  <div className="gloss-body">
                    <p>{e.definition}</p>
                    {e.formula && <div className="gloss-row"><b>Formula</b><code>{e.formula}</code></div>}
                    {e.benchmark && <div className="gloss-row"><b>2026 benchmark</b><span>{e.benchmark}</span></div>}
                    {e.source && <div className="gloss-row"><b>Source</b><span style={{ color: 'var(--text-3)' }}>{e.source}</span></div>}
                    <button className="btn btn-outline btn-sm" style={{ marginTop: 10 }} onClick={() => askCopilot(e.term)}>
                      <Sparkles size={13} /> {t('askCopilotInContext') || 'Ask the copilot in context'}
                    </button>
                  </div>
                )}
              </div>
            )
          })}
          {!isLoading && filtered.length === 0 && (
            <div style={{ textAlign: 'center', color: 'var(--text-3)', padding: 30 }}>{t('noTerms') || 'No matching terms.'}</div>
          )}
        </div>
      </aside>
    </div>
  )
}
