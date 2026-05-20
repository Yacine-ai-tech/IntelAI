import { useState, useEffect } from 'react'
import { useTranslation } from '../i18n/I18nContext'
import * as api from '../api'
import { X, Copy, CheckCircle2, Loader2, AlertCircle, Phone, Smartphone } from 'lucide-react'

export default function PairingModal({ isOpen, onClose, onPaired }) {
  const { t } = useTranslation()
  const [step, setStep] = useState('request') // request | qr | sessions
  const [loading, setLoading] = useState(false)
  const [deviceName, setDeviceName] = useState('Mobile Device')
  const [pairingData, setPairingData] = useState(null)
  const [sessions, setSessions] = useState([])
  const [error, setError] = useState(null)
  const [copied, setCopied] = useState(false)

  const requestPairing = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await api.requestDevicePairing(deviceName)
      setPairingData(res.data)
      setStep('qr')
    } catch (err) {
      setError(err.response?.data?.detail || t('pairingFailed'))
    } finally {
      setLoading(false)
    }
  }

  const loadSessions = async () => {
    setLoading(true)
    try {
      const res = await api.listPairingSessions()
      setSessions(res.data.sessions || [])
      setStep('sessions')
    } catch (err) {
      setError(err.response?.data?.detail || t('loadSessionsFailed'))
    } finally {
      setLoading(false)
    }
  }

  const revokePairing = async (token) => {
    if (!window.confirm(t('confirmRevokeSession'))) return
    try {
      await api.revokePairingSession(token)
      setSessions(sessions.filter(s => s.token !== token))
    } catch (err) {
      setError(err.response?.data?.detail || t('revokeFailed'))
    }
  }

  const copyToken = () => {
    if (pairingData?.token) {
      navigator.clipboard.writeText(pairingData.token)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  if (!isOpen) return null

  return (
    <div style={{
      position: 'fixed',
      top: 0, left: 0, right: 0, bottom: 0,
      background: 'rgba(0,0,0,0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
    }}>
      <div className="card" style={{
        width: '90%',
        maxWidth: 500,
        maxHeight: '90vh',
        overflow: 'auto',
        position: 'relative',
      }}>
        <button
          onClick={onClose}
          style={{
            position: 'absolute',
            top: 16,
            right: 16,
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            color: 'var(--text-secondary)',
          }}
        >
          <X size={20} />
        </button>

        <h2 style={{ display: 'flex', alignItems: 'center', gap: 10, margin: '0 0 20px 0' }}>
          <Smartphone size={24} style={{ color: 'var(--primary)' }} />
          {t('devicePairing')}
        </h2>

        {/* Step 1: Request Pairing */}
        {step === 'request' && (
          <div>
            <p style={{ color: 'var(--text-secondary)', marginBottom: 20 }}>
              {t('pairingDesc')}
            </p>
            <div style={{ marginBottom: 20 }}>
              <label style={{ display: 'block', marginBottom: 8, fontWeight: 500 }}>
                {t('deviceName')}
              </label>
              <input
                type="text"
                value={deviceName}
                onChange={(e) => setDeviceName(e.target.value)}
                placeholder={t('mobileDevicePlaceholder')}
                style={{
                  width: '100%',
                  padding: '10px 12px',
                  border: '1px solid var(--border)',
                  borderRadius: 8,
                  fontSize: '0.9rem',
                  fontFamily: 'inherit',
                }}
              />
            </div>
            {error && (
              <div style={{
                padding: 12,
                background: 'rgba(239, 68, 68, 0.1)',
                border: '1px solid rgba(239, 68, 68, 0.3)',
                borderRadius: 8,
                marginBottom: 16,
                display: 'flex',
                gap: 8,
                alignItems: 'flex-start',
              }}>
                <AlertCircle size={16} style={{ color: '#ef4444', flexShrink: 0, marginTop: 2 }} />
                <span style={{ fontSize: '0.85rem', color: '#dc2626' }}>{error}</span>
              </div>
            )}
            <div style={{ display: 'flex', gap: 12 }}>
              <button
                className="btn btn-primary"
                onClick={requestPairing}
                disabled={loading}
                style={{ flex: 1 }}
              >
                {loading ? (
                  <><Loader2 size={16} className="spin" /> {t('generating')}</>
                ) : (
                  <>{t('generateQR')}</>
                )}
              </button>
              <button
                className="btn btn-outline"
                onClick={loadSessions}
                style={{ flex: 1 }}
              >
                {t('viewSessions')}
              </button>
            </div>
          </div>
        )}

        {/* Step 2: QR Code Display */}
        {step === 'qr' && pairingData && (
          <div style={{ textAlign: 'center' }}>
            <p style={{ color: 'var(--text-secondary)', marginBottom: 20 }}>
              {t('scanQROnMobile')}
            </p>
            {pairingData.qr_code ? (
              <div style={{
                background: 'white',
                padding: 20,
                borderRadius: 12,
                marginBottom: 20,
                display: 'inline-block',
              }}>
                <img
                  src={pairingData.qr_code}
                  alt="Pairing QR"
                  style={{ width: 250, height: 250, imageRendering: 'pixelated' }}
                />
              </div>
            ) : (
              <div style={{
                padding: 40,
                background: 'var(--bg-secondary)',
                borderRadius: 12,
                marginBottom: 20,
                color: 'var(--text-muted)',
              }}>
                {t('qrNotAvailable')}
              </div>
            )}

            <div style={{
              padding: 12,
              background: 'var(--bg-secondary)',
              borderRadius: 8,
              marginBottom: 20,
              wordBreak: 'break-all',
              fontSize: '0.8rem',
              fontFamily: 'monospace',
            }}>
              {pairingData.token}
            </div>

            <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
              <button
                className="btn btn-outline"
                onClick={copyToken}
                style={{ flex: 1 }}
              >
                {copied ? (
                  <><CheckCircle2 size={16} /> {t('copied')}</>
                ) : (
                  <><Copy size={16} /> {t('copyToken')}</>
                )}
              </button>
            </div>

            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 16 }}>
              {t('expiresIn')} {pairingData.expires_in_hours} {t('hours')}
            </p>

            <div style={{ display: 'flex', gap: 12 }}>
              <button className="btn btn-primary" onClick={() => setStep('request')} style={{ flex: 1 }}>
                {t('newPairing')}
              </button>
              <button className="btn btn-outline" onClick={onClose} style={{ flex: 1 }}>
                {t('close')}
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Active Sessions */}
        {step === 'sessions' && (
          <div>
            <h3 style={{ marginBottom: 16, fontSize: '1rem' }}>
              {t('activeSessions')} ({sessions.length})
            </h3>

            {sessions.length === 0 ? (
              <div style={{
                padding: 40,
                textAlign: 'center',
                color: 'var(--text-muted)',
              }}>
                <Phone size={32} style={{ marginBottom: 12, opacity: 0.5 }} />
                <p>{t('noPairedDevices')}</p>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12, marginBottom: 20 }}>
                {sessions.map((session, idx) => (
                  <div
                    key={idx}
                    style={{
                      padding: 12,
                      border: '1px solid var(--border)',
                      borderRadius: 8,
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                    }}
                  >
                    <div style={{ flex: 1 }}>
                      <div style={{ fontWeight: 500, marginBottom: 4 }}>
                        {session.device_name}
                      </div>
                      <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                        {session.uploads} {t('uploads')} • {session.active ? t('active') : t('inactive')}
                      </div>
                      {session.last_upload && (
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 4 }}>
                          {t('lastUpload')}: {new Date(session.last_upload).toLocaleDateString()}
                        </div>
                      )}
                    </div>
                    {session.active && (
                      <button
                        className="btn btn-outline"
                        onClick={() => revokePairing(session.token)}
                        style={{ fontSize: '0.85rem', padding: '6px 12px' }}
                      >
                        {t('revoke')}
                      </button>
                    )}
                  </div>
                ))}
              </div>
            )}

            <div style={{ display: 'flex', gap: 12 }}>
              <button className="btn btn-primary" onClick={() => setStep('request')} style={{ flex: 1 }}>
                {t('newPairing')}
              </button>
              <button className="btn btn-outline" onClick={onClose} style={{ flex: 1 }}>
                {t('close')}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
