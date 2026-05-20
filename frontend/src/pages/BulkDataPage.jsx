import { useState } from 'react'
import * as api from '../api'
import { useTranslation } from '../i18n/I18nContext'

export default function BulkDataPage() {
  const { t } = useTranslation()
  const [jsonText, setJsonText] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [file, setFile] = useState(null)

  const submitJSON = async () => {
    try {
      const data = JSON.parse(jsonText)
      setLoading(true)
      const res = await api.ingestMetrics(data, 'bulk_json')
      setResult(res.data)
    } catch (err) {
      setResult({ error: err.message || 'Invalid JSON' })
    }
    setLoading(false)
  }

  const uploadCSV = async () => {
    if (!file) return
    setLoading(true)
    try {
      const res = await api.uploadCSV(file)
      setResult(res.data)
    } catch (err) {
      setResult({ error: err.response?.data?.detail || err.message })
    }
    setLoading(false)
  }

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">{t('bulkOps')}</h1>
        <p className="page-subtitle">{t('bulkOpsDesc')}</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
        <div className="card">
          <h3 className="card-title">{t('pasteJson')}</h3>
          <textarea className="form-input" rows={12} value={jsonText} onChange={e => setJsonText(e.target.value)} />
          <div style={{ marginTop: 8 }}>
            <button className="btn btn-primary" onClick={submitJSON} disabled={loading}>{loading ? t('processing') : t('submit')}</button>
          </div>
        </div>

        <div className="card">
          <h3 className="card-title">{t('uploadCsvFile')}</h3>
          <input type="file" accept=".csv" onChange={e => setFile(e.target.files[0])} />
          <div style={{ marginTop: 8 }}>
            <button className="btn btn-primary" onClick={uploadCSV} disabled={!file || loading}>{t('upload')}</button>
          </div>
          {result && (
            <div style={{ marginTop: 12 }}>
              <pre style={{ whiteSpace: 'pre-wrap' }}>{JSON.stringify(result, null, 2)}</pre>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
