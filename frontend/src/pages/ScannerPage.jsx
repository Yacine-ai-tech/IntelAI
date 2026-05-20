import { useState, useRef, useCallback } from 'react'
import { useTranslation } from '../i18n/I18nContext'
import * as api from '../api'
import {
  Camera, Upload, X, CheckCircle2, XCircle, RotateCcw,
  FileText, Scan, ImagePlus, Loader2, Smartphone
} from 'lucide-react'
import PairingModal from '../components/PairingModal'

export default function ScannerPage() {
  const { t } = useTranslation()
  const videoRef = useRef(null)
  const canvasRef = useRef(null)
  const fileRef = useRef(null)

  const [cameraOpen, setCameraOpen] = useState(false)
  const [capturedImage, setCapturedImage] = useState(null)
  const [previewFile, setPreviewFile] = useState(null)
  const [processing, setProcessing] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const streamRef = useRef(null)
  const [pairingModalOpen, setPairingModalOpen] = useState(false)

  const openCamera = useCallback(async () => {
    setError(null)
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment', width: { ideal: 1920 }, height: { ideal: 1080 } },
      })
      streamRef.current = stream
      if (videoRef.current) {
        videoRef.current.srcObject = stream
        videoRef.current.play()
      }
      setCameraOpen(true)
    } catch (err) {
      setError(t('cameraNotAvailable'))
    }
  }, [t])

  const closeCamera = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(t => t.stop())
      streamRef.current = null
    }
    setCameraOpen(false)
  }, [])

  const capturePhoto = useCallback(() => {
    if (!videoRef.current || !canvasRef.current) return
    const video = videoRef.current
    const canvas = canvasRef.current
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    const ctx = canvas.getContext('2d')
    ctx.drawImage(video, 0, 0)
    const dataUrl = canvas.toDataURL('image/jpeg', 0.9)
    setCapturedImage(dataUrl)
    closeCamera()
  }, [closeCamera])

  const retake = () => {
    setCapturedImage(null)
    setResult(null)
    setError(null)
    openCamera()
  }

  const handleFileSelect = (e) => {
    const file = e.target.files[0]
    if (!file) return
    setPreviewFile(file)
    setResult(null)
    setError(null)
    const reader = new FileReader()
    reader.onload = () => setCapturedImage(reader.result)
    reader.readAsDataURL(file)
  }

  const dataURLtoBlob = (dataUrl) => {
    const arr = dataUrl.split(',')
    const mime = arr[0].match(/:(.*?);/)[1]
    const bstr = atob(arr[1])
    let n = bstr.length
    const u8arr = new Uint8Array(n)
    while (n--) u8arr[n] = bstr.charCodeAt(n)
    return new Blob([u8arr], { type: mime })
  }

  const ingestScanned = async () => {
    if (!capturedImage) return
    setProcessing(true)
    setResult(null)
    setError(null)

    try {
      let file
      if (previewFile) {
        file = previewFile
      } else {
        const blob = dataURLtoBlob(capturedImage)
        file = new File([blob], `scan_${Date.now()}.jpg`, { type: 'image/jpeg' })
      }

      const res = await api.uploadDocument(file, 'scanned')
      setResult(res.data)
    } catch (err) {
      setError(err.response?.data?.detail || t('scanError'))
    } finally {
      setProcessing(false)
    }
  }

  const reset = () => {
    setCapturedImage(null)
    setPreviewFile(null)
    setResult(null)
    setError(null)
    if (fileRef.current) fileRef.current.value = ''
  }

  return (
    <div>
      <PairingModal
        isOpen={pairingModalOpen}
        onClose={() => setPairingModalOpen(false)}
        onPaired={() => {
          setPairingModalOpen(false)
        }}
      />

      <div className="page-header">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <h1 className="page-title"><Scan size={24} /> {t('scanDocument')}</h1>
          <button
            className="btn btn-outline"
            onClick={() => setPairingModalOpen(true)}
            style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: '0.9rem' }}
          >
            <Smartphone size={16} /> {t('pairDevice')}
          </button>
        </div>
      </div>

      <p style={{ color: 'var(--text-secondary)', marginBottom: 24, fontSize: '0.9rem' }}>
        {t('scanDesc')}
      </p>

      {/* Camera / Upload Controls */}
      {!capturedImage && !cameraOpen && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, marginBottom: 24 }}>
          {/* Camera capture card */}
          <div className="card" style={{ textAlign: 'center', padding: 40 }}>
            <Camera size={48} style={{ color: 'var(--primary)', marginBottom: 16 }} />
            <h3 style={{ margin: '0 0 8px 0' }}>{t('takePhoto')}</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: 20 }}>
              {t('captureDoc')}
            </p>
            <button className="btn btn-primary" onClick={openCamera}>
              <Camera size={16} /> {t('openCamera')}
            </button>
          </div>

          {/* File upload card */}
          <div className="card" style={{ textAlign: 'center', padding: 40 }}>
            <ImagePlus size={48} style={{ color: 'var(--primary)', marginBottom: 16 }} />
            <h3 style={{ margin: '0 0 8px 0' }}>{t('uploadDoc')}</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: 20 }}>
              PDF, TXT, PNG, JPG
            </p>
            <input ref={fileRef} type="file" accept=".pdf,.txt,.png,.jpg,.jpeg"
              onChange={handleFileSelect} style={{ display: 'none' }} />
            <button className="btn btn-primary" onClick={() => fileRef.current?.click()}>
              <Upload size={16} /> {t('upload')}
            </button>
          </div>
        </div>
      )}

      {/* Camera Feed */}
      {cameraOpen && (
        <div className="card" style={{ marginBottom: 24 }}>
          <div style={{ position: 'relative', background: '#000', borderRadius: 12, overflow: 'hidden' }}>
            <video ref={videoRef} autoPlay playsInline muted
              style={{ width: '100%', maxHeight: 500, display: 'block', objectFit: 'contain' }} />
            <div style={{
              position: 'absolute', bottom: 20, left: '50%', transform: 'translateX(-50%)',
              display: 'flex', gap: 12,
            }}>
              <button className="btn btn-primary" onClick={capturePhoto}
                style={{ borderRadius: '50%', width: 64, height: 64, fontSize: '1.5rem' }}>
                <Camera size={24} />
              </button>
              <button className="btn btn-outline" onClick={closeCamera}
                style={{ borderRadius: '50%', width: 48, height: 48 }}>
                <X size={20} />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Hidden canvas for capture */}
      <canvas ref={canvasRef} style={{ display: 'none' }} />

      {/* Captured Image Preview */}
      {capturedImage && (
        <div className="card" style={{ marginBottom: 24 }}>
          <h3 className="card-title"><FileText size={16} /> {t('scanDocument')}</h3>
          <div style={{ background: '#000', borderRadius: 12, overflow: 'hidden', marginBottom: 16 }}>
            <img src={capturedImage} alt="Scanned" style={{
              width: '100%', maxHeight: 500, objectFit: 'contain', display: 'block',
            }} />
          </div>

          <div style={{ display: 'flex', gap: 12 }}>
            <button className="btn btn-primary" onClick={ingestScanned} disabled={processing}>
              {processing ? (
                <><Loader2 size={16} className="spin" /> {t('scanProcessing')}</>
              ) : (
                <><Upload size={16} /> {t('ingestScanned')}</>
              )}
            </button>
            <button className="btn btn-outline" onClick={retake} disabled={processing}>
              <RotateCcw size={16} /> {t('retake')}
            </button>
            <button className="btn btn-ghost" onClick={reset} disabled={processing}>
              <X size={16} /> {t('cancel')}
            </button>
          </div>
        </div>
      )}

      {/* Result */}
      {result && (
        <div className="alert alert-success">
          <CheckCircle2 size={16} />
          <span>
            {t('scanSuccess')}
            {result.chunks ? ` ${result.chunks} ${t('chunksVectorized')}` : ''}
          </span>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="alert alert-danger">
          <XCircle size={16} />
          <span>{error}</span>
        </div>
      )}
    </div>
  )
}

