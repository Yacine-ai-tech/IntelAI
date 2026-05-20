import { useState, useRef, useEffect } from 'react'
import * as api from '../api'
import { useTranslation } from '../i18n/I18nContext'
import FilePreview, { IntegrationPreview } from '../components/FilePreview'
import DataIngestionPanel from '../components/DataIngestionPanel'
import {
  Database, Upload, FileSpreadsheet, FileText, Search,
  CheckCircle2, XCircle, BookOpen, Layers, Eye, Mail,
  FileBarChart, CheckSquare, ExternalLink, FolderOpen
} from 'lucide-react'

export default function DataHubPage() {
  const { t } = useTranslation()
  const [csvFile, setCsvFile] = useState(null)
  const [docFile, setDocFile] = useState(null)
  const [csvResult, setCsvResult] = useState(null)
  const [docResult, setDocResult] = useState(null)
  const [csvLoading, setCsvLoading] = useState(false)
  const [docLoading, setDocLoading] = useState(false)
  const [vectorQuery, setVectorQuery] = useState('')
  const [vectorResults, setVectorResults] = useState(null)
  const [vectorLoading, setVectorLoading] = useState(false)
  const [kbStats, setKbStats] = useState(null)
  const [userFiles, setUserFiles] = useState([])
  const [filesLoading, setFilesLoading] = useState(false)
  const [previewFile, setPreviewFile] = useState(null)
  const [previewIntegration, setPreviewIntegration] = useState(null)
  const csvRef = useRef(null)
  const docRef = useRef(null)

  // Integration configurations
  const integrations = [
    { type: 'gmail', name: 'Gmail', url: 'https://mail.google.com', connected: true },
    { type: 'sheets', name: 'Google Sheets', url: 'https://sheets.google.com', connected: true },
    { type: 'clickup', name: 'ClickUp', url: 'https://app.clickup.com', connected: true }
  ]

  useEffect(() => {
    api.getKnowledgeStats?.()
      .then(res => setKbStats(res.data))
      .catch(() => {})

    loadUserFiles()
  }, [])

  const loadUserFiles = async () => {
    setFilesLoading(true)
    try {
      const res = await api.getUserFiles()
      setUserFiles(res.data || [])
    } catch (err) {
      console.error('Failed to load files:', err)
    }
    setFilesLoading(false)
  }

  const uploadCSV = async () => {
    if (!csvFile) return
    setCsvLoading(true)
    setCsvResult(null)
    try {
      const res = await api.uploadCSV(csvFile)
      setCsvResult({ success: true, data: res.data })
      setCsvFile(null)
      if (csvRef.current) csvRef.current.value = ''
    } catch (err) {
      setCsvResult({ success: false, error: err.response?.data?.detail || 'Upload failed' })
    }
    setCsvLoading(false)
  }

  const uploadDocument = async () => {
    if (!docFile) return
    setDocLoading(true)
    setDocResult(null)
    try {
      const res = await api.uploadDocument(docFile)
      setDocResult({ success: true, data: res.data })
      setDocFile(null)
      if (docRef.current) docRef.current.value = ''
    } catch (err) {
      setDocResult({ success: false, error: err.response?.data?.detail || 'Upload failed' })
    }
    setDocLoading(false)
  }

  const runVectorSearch = async () => {
    if (!vectorQuery.trim()) return
    setVectorLoading(true)
    try {
      const res = await api.searchKnowledge(vectorQuery, 5)
      setVectorResults(res.data)
    } catch {
      setVectorResults({ error: 'Search failed' })
    }
    setVectorLoading(false)
  }

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title"><Database size={24} /> {t('dataHub')}</h1>
      </div>

      {/* Knowledge Base Stats */}
      {kbStats && (
        <div className="kpi-grid" style={{ marginBottom: 20 }}>
          <div className="kpi-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div>
                <div className="kpi-label">{t('documents')}</div>
                <div className="kpi-value">{kbStats.document_count ?? kbStats.total_documents ?? '—'}</div>
              </div>
              <div className="kpi-icon-wrap blue"><FileText size={20} /></div>
            </div>
          </div>
          <div className="kpi-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div>
                <div className="kpi-label">{t('vectorChunks')}</div>
                <div className="kpi-value">{kbStats.chunk_count ?? kbStats.total_chunks ?? '—'}</div>
              </div>
              <div className="kpi-icon-wrap purple"><Layers size={20} /></div>
            </div>
          </div>
          <div className="kpi-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div>
                <div className="kpi-label">{t('categories')}</div>
                <div className="kpi-value">{kbStats.categories?.length ?? kbStats.category_count ?? '—'}</div>
              </div>
              <div className="kpi-icon-wrap cyan"><BookOpen size={20} /></div>
            </div>
          </div>
        </div>
      )}

      {/* Data Ingestion Control Panel */}
      <div style={{ marginBottom: 30 }}>
        <DataIngestionPanel />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
        {/* CSV Upload */}
        <div className="card">
          <h3 className="card-title"><FileSpreadsheet size={16} /> {t('uploadCSV')}</h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: 16 }}>
            {t('uploadCSVDesc')}
          </p>
          <div style={{ marginBottom: 16 }}>
            <input ref={csvRef} type="file" accept=".csv" onChange={e => setCsvFile(e.target.files[0])} className="form-input" />
          </div>
          {csvFile && (
            <div className="text-sm text-muted" style={{ marginBottom: 12 }}>
              {t('selected')}: <strong>{csvFile.name}</strong> ({(csvFile.size / 1024).toFixed(1)} KB)
            </div>
          )}
          <button className="btn btn-primary" onClick={uploadCSV} disabled={!csvFile || csvLoading}>
            <Upload size={14} />
            {csvLoading ? t('uploading') : t('uploadCSV')}
          </button>
          {csvResult && (
            <div className={`alert ${csvResult.success ? 'alert-success' : 'alert-danger'}`} style={{ marginTop: 16 }}>
              {csvResult.success ? <CheckCircle2 size={16} /> : <XCircle size={16} />}
              <span>
                {csvResult.success
                  ? `${t('uploadSuccess')}${csvResult.data?.rows_inserted ? ` ${csvResult.data.rows_inserted} ${t('rowsIngested')}` : ''}`
                  : csvResult.error}
              </span>
            </div>
          )}
        </div>

        {/* Document Upload */}
        <div className="card">
          <h3 className="card-title"><FileText size={16} /> {t('uploadDoc')}</h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: 16 }}>
            {t('uploadDocDesc')}
          </p>
          <div style={{ marginBottom: 16 }}>
            <input ref={docRef} type="file" accept=".pdf,.txt,.png,.jpg,.jpeg" onChange={e => setDocFile(e.target.files[0])} className="form-input" />
          </div>
          {docFile && (
            <div className="text-sm text-muted" style={{ marginBottom: 12 }}>
              {t('selected')}: <strong>{docFile.name}</strong> ({(docFile.size / 1024).toFixed(1)} KB)
            </div>
          )}
          <button className="btn btn-primary" onClick={uploadDocument} disabled={!docFile || docLoading}>
            <Upload size={14} />
            {docLoading ? t('processing') : t('uploadDoc')}
          </button>
          {docResult && (
            <div className={`alert ${docResult.success ? 'alert-success' : 'alert-danger'}`} style={{ marginTop: 16 }}>
              {docResult.success ? <CheckCircle2 size={16} /> : <XCircle size={16} />}
              <span>
                {docResult.success
                  ? `${t('docProcessed')}${docResult.data?.chunks ? ` ${docResult.data.chunks} ${t('chunksVectorized')}` : ''}`
                  : docResult.error}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Vector Search */}
      <div className="card" style={{ marginTop: 20 }}>
        <h3 className="card-title"><Search size={16} /> {t('knowledgeSearch')}</h3>
        <div style={{ display: 'flex', gap: 12, marginBottom: 16 }}>
          <input
            className="form-input"
            style={{ flex: 1 }}
            placeholder={t('searchPlaceholder')}
            value={vectorQuery}
            onChange={e => setVectorQuery(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && runVectorSearch()}
          />
          <button className="btn btn-primary" onClick={runVectorSearch} disabled={vectorLoading || !vectorQuery.trim()}>
            <Search size={14} />
            {vectorLoading ? t('searching') : t('search')}
          </button>
        </div>
        {vectorResults && !vectorResults.error && (
          <div>
            {(vectorResults.results || vectorResults.documents || []).map((r, i) => (
              <div key={i} style={{ padding: '12px 0', borderBottom: '1px solid var(--border)' }}>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-primary)', lineHeight: 1.6 }}>
                  {r.content || r.text || r.document || JSON.stringify(r)}
                </div>
                {r.score && (
                  <div className="text-xs text-muted" style={{ marginTop: 4 }}>
                    Relevance: {(r.score * 100).toFixed(1)}%
                  </div>
                )}
              </div>
            ))}
            {(vectorResults.results || vectorResults.documents || []).length === 0 && (
              <p className="text-muted text-sm">{t('noResults')}</p>
            )}
          </div>
        )}
        {vectorResults?.error && (
          <div className="alert alert-danger"><XCircle size={16} /> {vectorResults.error}</div>
        )}
      </div>

      {/* Format Guide */}
      <div className="card" style={{ marginTop: 20 }}>
        <h3 className="card-title"><BookOpen size={16} /> {t('dataFormatGuide')}</h3>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
          <div>
            <h4 style={{ fontSize: '0.9rem', marginBottom: 8, color: 'var(--text-primary)' }}>{t('csvFormat')}</h4>
            <pre style={{
              background: 'var(--bg-primary)', padding: 16, borderRadius: 'var(--radius)',
              fontSize: '0.75rem', overflow: 'auto', color: 'var(--text-secondary)',
              border: '1px solid var(--border)',
            }}>
{`metric_name,value,period,category,segment
Revenue,1250000,2024-Q1,revenue,enterprise
COGS,450000,2024-Q1,cost,enterprise
Net Margin,0.64,2024-Q1,profitability,all`}
            </pre>
          </div>
          <div>
            <h4 style={{ fontSize: '0.9rem', marginBottom: 8, color: 'var(--text-primary)' }}>{t('supportedDocs')}</h4>
            <ul style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 2, paddingLeft: 20 }}>
              <li><strong>PDF</strong> — Annual reports, financial statements</li>
              <li><strong>TXT</strong> — Meeting notes, memos</li>
              <li><strong>Images</strong> — Receipts, invoices (OCR)</li>
            </ul>
          </div>
        </div>
      </div>

      {/* File Browser */}
      <div className="card" style={{ marginTop: 20 }}>
        <h3 className="card-title"><FolderOpen size={16} /> {t('myFiles')}</h3>
        {filesLoading ? (
          <div className="loading">Loading files...</div>
        ) : userFiles.length === 0 ? (
          <p className="text-muted text-sm">No files uploaded yet</p>
        ) : (
          <div className="file-grid">
            {userFiles.map((file, i) => (
              <div key={i} className="file-item">
                <div className="file-icon">
                  {file.type === 'document' ? <FileText size={24} /> :
                   file.type === 'spreadsheet' ? <FileSpreadsheet size={24} /> :
                   <Image size={24} />}
                </div>
                <div className="file-info">
                  <div className="file-name">{file.name}</div>
                  <div className="file-meta">
                    {(file.size / 1024).toFixed(1)} KB • {file.uploaded_at}
                  </div>
                </div>
                <button
                  className="btn btn-sm btn-outline"
                  onClick={() => setPreviewFile(file)}
                >
                  <Eye size={14} /> Preview
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Integrations */}
      <div className="card" style={{ marginTop: 20 }}>
        <h3 className="card-title"><ExternalLink size={16} /> {t('integrations')}</h3>
        <div className="integration-grid">
          {integrations.map((integration, i) => (
            <div key={i} className={`integration-item ${integration.connected ? 'connected' : 'disconnected'}`}>
              <div className="integration-header">
                <div className="integration-icon">
                  {integration.type === 'gmail' && <Mail size={20} />}
                  {integration.type === 'sheets' && <FileSpreadsheet size={20} />}
                  {integration.type === 'clickup' && <CheckSquare size={20} />}
                </div>
                <div className="integration-info">
                  <div className="integration-name">{integration.name}</div>
                  <div className="integration-status">
                    {integration.connected ? 'Connected' : 'Not Connected'}
                  </div>
                </div>
              </div>
              {integration.connected && (
                <button
                  className="btn btn-sm btn-primary"
                  onClick={() => setPreviewIntegration(integration)}
                >
                  <Eye size={14} /> Preview Data
                </button>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Preview Modals */}
      {previewFile && (
        <FilePreview
          file={previewFile}
          onClose={() => setPreviewFile(null)}
        />
      )}

      {previewIntegration && (
        <IntegrationPreview
          integration={previewIntegration}
          onClose={() => setPreviewIntegration(null)}
        />
      )}
    </div>
  )
}
