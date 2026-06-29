import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import * as api from '../api'
import { useTranslation } from '../i18n/I18nContext'
import { BookOpen, Search } from 'lucide-react'
import { PageHeader, Panel, Loading, Empty } from '../components/ui'

export default function GlossaryPage() {
  const { t } = useTranslation()
  const { data: terms = [], isLoading } = useQuery({ queryKey: ['glossary'], queryFn: () => api.getGlossary().then(r => r.data?.terms || []), retry: 1 })
  const [q, setQ] = useState('')

  if (isLoading) return <Loading />

  const filtered = terms.filter(tt => 
    (tt.term || '').toLowerCase().includes(q.toLowerCase()) || 
    (tt.definition || '').toLowerCase().includes(q.toLowerCase()) ||
    (tt.domain || '').toLowerCase().includes(q.toLowerCase())
  )

  // Group by domain
  const byDomain = {}
  filtered.forEach(tt => {
    const d = tt.domain || 'General'
    if (!byDomain[d]) byDomain[d] = []
    byDomain[d].push(tt)
  })

  return (
    <div>
      <PageHeader icon={BookOpen} title={t('navGlossary') || 'Glossary'}
        subtitle={t('glossarySubtitle') || 'Standardized definitions for all tracked metrics'} />

      <Panel style={{ marginBottom: 18 }}>
        <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
          <Search size={16} color="var(--text-3)" />
          <input className="form-input" style={{ flex: 1, border: 'none', background: 'transparent' }} 
            placeholder="Search metrics or definitions..." 
            value={q} onChange={e => setQ(e.target.value)} />
        </div>
      </Panel>

      {Object.keys(byDomain).length === 0 ? <Empty text="No terms found." /> : (
        Object.entries(byDomain).map(([domain, items]) => (
          <Panel key={domain} title={domain} style={{ marginBottom: 18 }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              {items.map((tt, i) => (
                <div key={i} style={{ paddingBottom: 14, borderBottom: i < items.length - 1 ? '1px solid var(--border)' : 'none' }}>
                  <div style={{ fontWeight: 600, fontSize: '.95rem', color: 'var(--primary)', marginBottom: 4 }}>{tt.term}</div>
                  <div style={{ color: 'var(--text-2)', fontSize: '.88rem', lineHeight: 1.5 }}>{tt.definition}</div>
                  {tt.formula && <div style={{ marginTop: 6, fontFamily: 'var(--font-mono)', fontSize: '.8rem', background: 'var(--surface-2)', padding: '4px 8px', borderRadius: 4, display: 'inline-block' }}>{tt.formula}</div>}
                </div>
              ))}
            </div>
          </Panel>
        ))
      )}
    </div>
  )
}
