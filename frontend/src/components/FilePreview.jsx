import { useState, useEffect } from 'react'
import * as api from '../api'
import { useTranslation } from '../i18n/I18nContext'
import {
  FileText, FileSpreadsheet, Image, Eye, Download,
  Mail, FileBarChart, CheckSquare, ExternalLink
} from 'lucide-react'

export default function FilePreview({ file, onClose }) {
  const { t } = useTranslation()
  const [content, setContent] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (file.type === 'document' || file.type === 'image') {
      // For documents and images, try to get preview content
      api.getFilePreview(file.id)
        .then(res => setContent(res.data.content || 'Preview not available'))
        .catch(() => setContent('Preview not available'))
        .finally(() => setLoading(false))
    } else {
      setContent('Preview not available for this file type')
      setLoading(false)
    }
  }, [file])

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h3>{file.name}</h3>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        <div className="modal-body">
          {loading ? (
            <div className="loading">Loading preview...</div>
          ) : (
            <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace', fontSize: '0.9rem' }}>
              {content}
            </pre>
          )}
        </div>
        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>Close</button>
          <button className="btn btn-primary" onClick={() => api.downloadFile(file.id)}>
            <Download size={14} /> Download
          </button>
        </div>
      </div>
    </div>
  )
}

export function IntegrationPreview({ integration, onClose }) {
  const { t } = useTranslation()
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getIntegrationData(integration.type)
      .then(res => setData(res.data))
      .catch(() => setData([]))
      .finally(() => setLoading(false))
  }, [integration])

  const getIcon = (type) => {
    switch (type) {
      case 'gmail': return <Mail size={20} />
      case 'sheets': return <FileSpreadsheet size={20} />
      case 'clickup': return <CheckSquare size={20} />
      default: return <ExternalLink size={20} />
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content large-modal" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h3>{getIcon(integration.type)} {integration.name} Integration</h3>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        <div className="modal-body">
          {loading ? (
            <div className="loading">Loading {integration.name} data...</div>
          ) : (
            <div className="integration-preview">
              {integration.type === 'gmail' && (
                <div className="email-list">
                  {data.map((email, i) => (
                    <div key={i} className="email-item">
                      <div className="email-header">
                        <strong>{email.subject}</strong>
                        <span className="email-date">{email.date}</span>
                      </div>
                      <div className="email-from">From: {email.from}</div>
                      <div className="email-preview">{email.snippet}</div>
                    </div>
                  ))}
                </div>
              )}
              {integration.type === 'sheets' && (
                <div className="sheets-preview">
                  {data.map((sheet, i) => (
                    <div key={i} className="sheet-item">
                      <h4>{sheet.name}</h4>
                      <div className="sheet-data">
                        {sheet.data?.slice(0, 5).map((row, j) => (
                          <div key={j} className="sheet-row">
                            {row.map((cell, k) => (
                              <span key={k} className="sheet-cell">{cell}</span>
                            ))}
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}
              {integration.type === 'clickup' && (
                <div className="clickup-list">
                  {data.map((task, i) => (
                    <div key={i} className="task-item">
                      <div className="task-header">
                        <strong>{task.name}</strong>
                        <span className={`task-status ${task.status.toLowerCase()}`}>{task.status}</span>
                      </div>
                      <div className="task-meta">
                        List: {task.list} | Due: {task.due_date || 'No due date'}
                      </div>
                      <div className="task-description">{task.description}</div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>Close</button>
          <button className="btn btn-primary" onClick={() => window.open(integration.url, '_blank')}>
            <ExternalLink size={14} /> Open in {integration.name}
          </button>
        </div>
      </div>
    </div>
  )
}