import { useState, useRef, useEffect } from 'react'
import { useTranslation } from '../i18n/I18nContext'
import * as api from '../api'
import { Download, FileJson, FileSpreadsheet, FileText, Sheet, Loader2 } from 'lucide-react'

function download(filename, content, mime) {
  const blob = content instanceof Blob ? content : new Blob([content], { type: mime })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url; a.download = filename; a.click()
  setTimeout(() => URL.revokeObjectURL(url), 1000)
}
function b64ToBlob(b64, mime) {
  const bin = atob(b64); const arr = new Uint8Array(bin.length)
  for (let i = 0; i < bin.length; i++) arr[i] = bin.charCodeAt(i)
  return new Blob([arr], { type: mime })
}
function toCSV(rows) {
  if (!rows.length) return ''
  const cols = Object.keys(rows[0])
  const esc = (v) => `"${String(v ?? '').replace(/"/g, '""')}"`
  return [cols.join(','), ...rows.map(r => cols.map(c => esc(r[c])).join(','))].join('\n')
}

export default function ExportMenu() {
  const { t } = useTranslation()
  const [open, setOpen] = useState(false)
  const [busy, setBusy] = useState(null)
  const ref = useRef(null)

  useEffect(() => {
    const h = (e) => { if (ref.current && !ref.current.contains(e.target)) setOpen(false) }
    document.addEventListener('mousedown', h)
    return () => document.removeEventListener('mousedown', h)
  }, [])

  const run = async (fmt) => {
    setBusy(fmt)
    try {
      if (fmt === 'json' || fmt === 'csv') {
        const rows = (await api.getKPIs()).data?.metrics || []
        if (fmt === 'json') download('intelai_kpis.json', JSON.stringify(rows, null, 2), 'application/json')
        else download('intelai_kpis.csv', toCSV(rows), 'text/csv')
      } else if (fmt === 'xlsx') {
        const r = (await api.exportData('xlsx')).data
        download(r.filename || 'intelai_kpis.xlsx',
          b64ToBlob(r.data, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'))
      } else if (fmt === 'pdf') {
        await printReport(t)
      }
    } catch (e) {
      alert((t('exportFailed') || 'Export failed') + ': ' + (e.response?.data?.detail || e.message))
    } finally {
      setBusy(null); setOpen(false)
    }
  }

  const items = [
    { fmt: 'pdf',  icon: FileText,        label: t('exportPdf') || 'Board PDF' },
    { fmt: 'xlsx', icon: FileSpreadsheet, label: t('exportExcel') || 'Excel' },
    { fmt: 'csv',  icon: Sheet,           label: 'CSV' },
    { fmt: 'json', icon: FileJson,        label: 'JSON' },
  ]

  return (
    <div ref={ref} style={{ position: 'relative' }}>
      <button className="btn btn-sm" onClick={() => setOpen(o => !o)} title={t('export') || 'Export'}>
        <Download size={15} /> {t('export') || 'Export'}
      </button>
      {open && (
        <div className="menu-pop">
          {items.map(({ fmt, icon: Icon, label }) => (
            <button key={fmt} className="menu-item" onClick={() => run(fmt)} disabled={busy}>
              {busy === fmt ? <Loader2 size={15} className="spin-inline" /> : <Icon size={15} />} {label}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

// Board-ready PDF via the browser's print engine (print-styled, reliable, no server deps).
async function printReport(t) {
  const [kpisR, healthR, riskR, sumR] = await Promise.allSettled([
    api.getKPIs(), api.getHealth(), api.getRisk(), api.getSummary(),
  ])
  const kpis = kpisR.value?.data?.metrics || []
  const health = healthR.value?.data || {}
  const risk = riskR.value?.data || {}
  const summary = sumR.value?.data?.summary || ''
  // latest reading per metric
  const seen = {}; kpis.forEach(k => { const n = k.metric_name || k.name; if (!seen[n] || (k.period > seen[n].period)) seen[n] = k })
  const latest = Object.values(seen)
  const fmt = (v) => typeof v === 'number' ? (Math.abs(v) >= 1e6 ? (v / 1e6).toFixed(2) + 'M' : Math.abs(v) >= 1e3 ? (v / 1e3).toFixed(1) + 'K' : v.toFixed(1)) : (v ?? '—')
  const rows = latest.map(k => `<tr><td>${k.metric_name || k.name}</td><td>${k.category || ''}</td><td style="text-align:right">${fmt(k.value)} ${k.unit || ''}</td><td>${k.period || ''}</td></tr>`).join('')
  const w = window.open('', '_blank')
  w.document.write(`<!doctype html><html><head><title>IntelAI — Executive Report</title>
  <style>
    body{font-family:Inter,Arial,sans-serif;color:#111;margin:40px;}
    h1{margin:0;font-size:26px;color:#0d9488} .sub{color:#666;margin:2px 0 24px}
    .cards{display:flex;gap:16px;margin-bottom:24px}
    .c{flex:1;border:1px solid #e5e7eb;border-radius:10px;padding:14px}
    .c .l{font-size:11px;text-transform:uppercase;color:#888} .c .v{font-size:28px;font-weight:700}
    table{width:100%;border-collapse:collapse;font-size:13px} th{text-align:left;color:#888;font-size:11px;text-transform:uppercase;border-bottom:2px solid #e5e7eb;padding:8px}
    td{padding:8px;border-bottom:1px solid #f0f0f0} p.s{line-height:1.6;color:#333}
    @media print{body{margin:18mm}}
  </style></head><body>
  <h1>IntelAI — Executive Report</h1>
  <div class="sub">${new Date().toLocaleString()}</div>
  <div class="cards">
    <div class="c"><div class="l">Health Index</div><div class="v">${Math.round(health.score ?? health.health_index ?? 0)}/100</div></div>
    <div class="c"><div class="l">Risk Score</div><div class="v">${Math.round(risk.score ?? 0)} <span style="font-size:14px;color:#888">${risk.label || ''}</span></div></div>
    <div class="c"><div class="l">Metrics Tracked</div><div class="v">${latest.length}</div></div>
  </div>
  ${summary ? `<h3>Executive Summary</h3><p class="s">${summary}</p>` : ''}
  <h3>Latest KPIs</h3>
  <table><thead><tr><th>Metric</th><th>Domain</th><th style="text-align:right">Value</th><th>Period</th></tr></thead><tbody>${rows}</tbody></table>
  </body></html>`)
  w.document.close()
  setTimeout(() => { w.focus(); w.print() }, 400)
}
