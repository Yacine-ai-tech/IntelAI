import { useState, useEffect } from 'react'
import { useTranslation } from '../i18n/I18nContext'
import { CheckCircle } from 'lucide-react'
import * as api from '../api'

const INTEGRATIONS = [
  { type: 'gmail', name: 'Gmail' },
  { type: 'sheets', name: 'Google Sheets' },
  { type: 'clickup', name: 'ClickUp' },
]

export default function IntegrationsPage() {
  const { t } = useTranslation()
  const [connected, setConnected] = useState({})
  const [loading, setLoading] = useState(false)
  const [previewData, setPreviewData] = useState(null)
  const [error, setError] = useState(null)
  const [notification, setNotification] = useState(null)

  useEffect(() => {
    // Check URL query params for OAuth callback (e.g. ?integration=connected&name=gmail)
    const params = new URLSearchParams(window.location.search)
    const integrationConnected = params.get('integration') === 'connected'
    const integrationName = params.get('name')
    if (integrationConnected && integrationName) {
      setConnected(prev => ({ ...prev, [integrationName]: true }))
      const disp = INTEGRATIONS.find(x => x.type === integrationName)?.name || integrationName
      setNotification(`${disp} connected successfully`)
      // remove query params from URL to clean up UX
      try {
        const url = new URL(window.location.href)
        url.search = ''
        window.history.replaceState({}, document.title, url.toString())
      } catch (e) {
        // ignore
      }
    }

    // Query backend for actual connection/status for each integration (efficient endpoint)
    const fetchStatuses = async () => {
      try {
        const res = await api.getIntegrationsStatus()
        const statuses = res.data?.statuses || {}
        setConnected(statuses)
      } catch (e) {
        // fallback: probe each integration (older behavior)
        const map = {}
        await Promise.all(INTEGRATIONS.map(async (i) => {
          try {
            await api.getIntegrationData(i.type)
            map[i.type] = true
          } catch (err) {
            map[i.type] = false
          }
        }))
        setConnected(map)
      }
    }
    fetchStatuses()
  }, [])

  const preview = async (type) => {
    setError(null)
    setPreviewData(null)
    try {
      const res = await api.getIntegrationData(type)
      setPreviewData({ type, data: res.data })
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to preview')
    }
  }

  const connect = async (type) => {
    setLoading(true)
    try {
      // For OAuth-enabled integrations, start OAuth flow and redirect user
      if (['gmail', 'sheets', 'clickup'].includes(type)) {
        const res = await api.oauthStart(type)
        const url = res.data?.url
        if (url) {
          // redirect to provider auth page
          window.location.href = url
          return
        }
      }
      // Fallback (legacy/manual) connect
      await api.connectIntegration(type, { demo: true })
      setConnected(prev => ({ ...prev, [type]: true }))
  setNotification(`${INTEGRATIONS.find(x => x.type === type)?.name || type} connected`)
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to connect')
    }
    setLoading(false)
  }

  const disconnect = async (type) => {
    setLoading(true)
    try {
      // Start OAuth flow and redirect user to provider consent page
      const res = await api.oauthStart(type)
      const url = res.data?.url
      if (url) {
        // Redirect browser to provider
        window.location.href = url
      } else {
        setError('Failed to start OAuth flow')
      }
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to disconnect')
    } finally {
      setLoading(false)
    }
  }

  // show a short-lived success notification for OAuth redirects
  useEffect(() => {
    if (!notification) return
    const id = setTimeout(() => setNotification(null), 5000)
    return () => clearTimeout(id)
  }, [notification])

  return (
    <div>
      {/* Top-right toast notification */}
      {notification && (
        <div style={{
          position: 'fixed',
          top: 16,
          right: 16,
          zIndex: 9999,
          backgroundColor: '#10b981',
          color: 'white',
          padding: '12px 16px',
          borderRadius: '6px',
          boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
          display: 'flex',
          alignItems: 'center',
          gap: 8,
          fontSize: '0.9rem',
          fontWeight: 500,
          animation: 'slideIn 0.3s ease-out'
        }}>
          <CheckCircle size={16} />
          {notification}
        </div>
      )}
      
      <div className="page-header">
        <h1 className="page-title">{t('integrations')}</h1>
        <p className="page-subtitle">{t('integrationsDesc')}</p>
      </div>

      {error && <div className="alert alert-danger">{error}</div>}

      <div className="card">
        <h3 className="card-title">{t('manageIntegrations')}</h3>
        <div style={{ display: 'grid', gap: 12 }}>
          {INTEGRATIONS.map(i => (
            <div key={i.type} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, flex: 1 }}>
                <div>
                  <div style={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: 6 }}>
                    {i.name}
                    {connected[i.type] && (
                      <CheckCircle size={16} style={{ color: '#10b981' }} title="Connected" />
                    )}
                  </div>
                  <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{i.type}</div>
                </div>
              </div>
              <div style={{ display: 'flex', gap: 8 }}>
                <button className="btn btn-sm" onClick={() => preview(i.type)}>Preview</button>
                {connected[i.type] ? (
                  <button className="btn btn-outline btn-sm" onClick={() => disconnect(i.type)} disabled={loading}>Disconnect</button>
                ) : (
                  <button className="btn btn-primary btn-sm" onClick={() => connect(i.type)} disabled={loading}>Connect</button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div style={{ marginTop: 16 }}>
        {previewData ? (
          <div className="card">
            <h3 className="card-title">Preview: {previewData.type}</h3>
            <pre style={{ whiteSpace: 'pre-wrap', fontSize: '0.9rem' }}>{JSON.stringify(previewData.data, null, 2)}</pre>
          </div>
        ) : (
          <div className="text-muted">{t('selectIntegrationPreview')}</div>
        )}
      </div>

      {/* CSS for toast animation */}
      <style>{`
        @keyframes slideIn {
          from {
            transform: translateX(400px);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }
      `}</style>
    </div>
  )
}
