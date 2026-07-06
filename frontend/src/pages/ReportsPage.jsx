// Reports — board-ready export. Real /data/export: PDF board report (generate_board_pdf),
// plus CSV / JSON / XLSX of live KPIs. The executive brief comes from /insights/summary.
import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { FileText, Download, FileSpreadsheet, FileJson, FileType, Loader2, AlertTriangle } from 'lucide-react'
import * as api from '../api'
import { PageHeader, Panel, Loading } from '../components/ui'

const FORMATS = [
  { format: 'pdf', label: 'Board report (PDF)', icon: FileType, desc: 'Executive summary, charts and recommendations as a formatted PDF.' },
  { format: 'xlsx', label: 'KPIs (Excel)', icon: FileSpreadsheet, desc: 'All live KPI metrics as a spreadsheet.' },
  { format: 'csv', label: 'KPIs (CSV)', icon: FileSpreadsheet, desc: 'Live KPI metrics for any downstream tool.' },
  { format: 'json', label: 'KPIs (JSON)', icon: FileJson, desc: 'Structured KPI export for programmatic use.' },
]

function downloadExport(res) {
  const { data, filename, encoding, format } = res
  let blob
  if (encoding === 'base64') {
    const bytes = Uint8Array.from(atob(data), c => c.charCodeAt(0))
    blob = new Blob([bytes], { type: format === 'pdf' ? 'application/pdf' : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
  } else {
    blob = new Blob([data], { type: format === 'json' ? 'application/json' : 'text/csv' })
  }
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url; a.download = filename || `export.${format}`; a.click()
  URL.revokeObjectURL(url)
}

export default function ReportsPage() {
  const [busy, setBusy] = useState('')
  const [err, setErr] = useState('')

  const { data: summary, isLoading } = useQuery({
    queryKey: ['summary'], queryFn: () => api.getSummary().then(r => r.data),
  })

  const run = async (format) => {
    setBusy(format); setErr('')
    try {
      const res = await api.exportData(format, 'kpis').then(r => r.data)
      if (res?.data) downloadExport(res)
      else setErr('Export returned no data.')
    } catch (e) {
      setErr(e?.response?.data?.detail || e.message || 'Export failed')
    } finally { setBusy('') }
  }

  const brief = summary?.summary || summary?.executive_summary
  const health = summary?.health

  return (
    <div>
      <PageHeader icon={FileText} title="Reports"
        subtitle="Board-ready exports generated from your live data — no copy-paste."
        accent="var(--p-ceo)" />

      <Panel title="Latest executive brief" icon={FileText}
        actions={<button className="btn btn-primary btn-sm" onClick={() => run('pdf')} disabled={busy === 'pdf'}>
          {busy === 'pdf' ? <Loader2 size={13} className="spin" /> : <Download size={13} />} Board PDF
        </button>}>
        {isLoading ? <Loading /> : (
          <>
            {health && (
              <div style={{ display: 'flex', gap: 18, marginBottom: 12, flexWrap: 'wrap' }}>
                <Metric label="Health" value={Math.round(health.score ?? 0)} unit="/100" />
                {health.label && <Metric label="Status" value={health.label} />}
                {summary?.risk?.label && <Metric label="Risk" value={summary.risk.label} />}
              </div>
            )}
            <p style={{ fontSize: 13.5, lineHeight: 1.75, color: 'var(--text-2)', whiteSpace: 'pre-wrap' }}>
              {typeof brief === 'string' ? brief : brief ? JSON.stringify(brief) : 'No executive brief available yet.'}
            </p>
          </>
        )}
      </Panel>

      <Panel title="Export formats" icon={Download}>
        {err && (
          <div style={{ display: 'flex', gap: 8, alignItems: 'center', color: 'var(--bad)', fontSize: 13, marginBottom: 10 }}>
            <AlertTriangle size={15} /> {err}
          </div>
        )}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(250px,1fr))', gap: 12 }}>
          {FORMATS.map(f => (
            <button key={f.format} onClick={() => run(f.format)} disabled={!!busy}
              style={{ textAlign: 'left', background: 'var(--surface-2)', border: '1px solid var(--border)', borderRadius: 'var(--r-lg)', padding: 15, cursor: 'pointer', color: 'var(--text)' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <f.icon size={18} style={{ color: 'var(--primary)' }} />
                {busy === f.format ? <Loader2 size={15} className="spin" style={{ color: 'var(--primary)' }} /> : <Download size={14} style={{ color: 'var(--text-3)' }} />}
              </div>
              <div style={{ marginTop: 10, fontSize: 13.5, fontWeight: 600 }}>{f.label}</div>
              <div style={{ marginTop: 4, fontSize: 12, color: 'var(--text-3)', lineHeight: 1.5 }}>{f.desc}</div>
            </button>
          ))}
        </div>
      </Panel>
    </div>
  )
}

function Metric({ label, value, unit }) {
  return (
    <div>
      <div style={{ fontSize: 10.5, textTransform: 'uppercase', letterSpacing: '.05em', color: 'var(--text-3)' }}>{label}</div>
      <div style={{ fontSize: 20, fontWeight: 700, color: 'var(--text)' }}>{value}<span style={{ fontSize: 12, color: 'var(--text-3)' }}>{unit}</span></div>
    </div>
  )
}
