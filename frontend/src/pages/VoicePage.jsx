import { useState, useRef } from 'react'
import { useTranslation } from '../i18n/I18nContext'
import { useMutation, useQuery } from '@tanstack/react-query'
import * as api from '../api'
import {
  Mic, MicOff, Volume2, Play, Square, Upload, FileAudio,
  Languages, Sparkles, AlertCircle, CheckCircle
} from 'lucide-react'

function AudioPlayer({ audioUrl, onPlay, onPause, isPlaying }) {
  const audioRef = useRef(null)

  const handlePlay = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause()
        onPause?.()
      } else {
        audioRef.current.play()
        onPlay?.()
      }
    }
  }

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
      <audio 
        ref={audioRef}
        src={audioUrl}
        onEnded={() => onPause?.()}
        style={{ display: 'none' }}
      />
      <button 
        className="btn btn-primary"
        onClick={handlePlay}
      >
        {isPlaying ? <Square size={16} /> : <Play size={16} />}
      </button>
      <div style={{ flex: 1, height: 4, background: 'var(--border)', borderRadius: 2 }}>
        <div 
          style={{ 
            width: isPlaying ? '100%' : '0%', 
            height: '100%', 
            background: 'var(--primary)', 
            borderRadius: 2,
            transition: 'width 0.3s'
          }} 
        />
      </div>
    </div>
  )
}

function TranscriptionResult({ result }) {
  return (
    <div className="card" style={{ marginTop: 16 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
        <CheckCircle size={16} style={{ color: 'var(--success)' }} />
        <span style={{ fontWeight: 600 }}>Transcription Complete</span>
      </div>
      <div style={{ 
        padding: 16, 
        background: 'var(--card-bg)', 
        borderRadius: 8,
        maxHeight: 200,
        overflowY: 'auto'
      }}>
        {result.text}
      </div>
      {result.confidence && (
        <div style={{ marginTop: 12, fontSize: '0.875rem', color: 'var(--text-muted)' }}>
          Confidence: {(result.confidence * 100).toFixed(1)}%
        </div>
      )}
      {result.language && (
        <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
          Language: {result.language}
        </div>
      )}
      {result.duration && (
        <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
          Duration: {result.duration.toFixed(2)}s
        </div>
      )}
    </div>
  )
}

export default function VoicePage() {
  const { t } = useTranslation()
  const [isRecording, setIsRecording] = useState(false)
  const [recordedBlob, setRecordedBlob] = useState(null)
  const [selectedFile, setSelectedFile] = useState(null)
  const [textInput, setTextInput] = useState('')
  const [selectedLanguage, setSelectedLanguage] = useState('en')
  const mediaRecorderRef = useRef(null)
  const chunksRef = useRef([])

  // Transcribe mutation
  const transcribeMutation = useMutation({
    mutationFn: async (audioBlob) => {
      const formData = new FormData()
      formData.append('audio_file', audioBlob, 'audio.webm')
      formData.append('language', selectedLanguage)
      const res = await api.transcribeAudio(formData)
      return res.data
    },
  })

  // TTS mutation
  const ttsMutation = useMutation({
    mutationFn: async (text) => {
      const res = await api.textToSpeech({
        text,
        language: selectedLanguage,
        voice: 'default'
      })
      return res.data
    },
  })

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      mediaRecorderRef.current = new MediaRecorder(stream)
      chunksRef.current = []

      mediaRecorderRef.current.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data)
        }
      }

      mediaRecorderRef.current.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' })
        setRecordedBlob(blob)
      }

      mediaRecorderRef.current.start()
      setIsRecording(true)
    } catch (error) {
      console.error('Error accessing microphone:', error)
      alert('Unable to access microphone. Please check permissions.')
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
      // Stop all tracks to release microphone
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop())
    }
  }

  const handleFileUpload = (e) => {
    const file = e.target.files[0]
    if (file) {
      setSelectedFile(file)
    }
  }

  const handleTranscribe = async () => {
    const audioToTranscribe = recordedBlob || selectedFile
    if (!audioToTranscribe) return

    transcribeMutation.mutate(audioToTranscribe)
  }

  const handleTextToSpeech = () => {
    if (!textInput.trim()) return
    ttsMutation.mutate(textInput)
  }

  const handleDownload = (url, filename) => {
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
  }

  return (
    <div>
      <h1 className="page-title">
        <Volume2 size={24} />
        {t('voiceIntelligence')}
      </h1>
      <p className="page-subtitle">
        Speech-to-Text and Text-to-Speech capabilities with multi-language support
      </p>

      {/* Speech-to-Text Section */}
      <div className="card" style={{ marginBottom: 20 }}>
        <h3 className="card-title">
          <Mic size={16} />
          Speech to Text
        </h3>

        {/* Recording Controls */}
        <div style={{ display: 'flex', gap: 12, alignItems: 'center', marginBottom: 16 }}>
          <button
            className={`btn ${isRecording ? 'btn-danger' : 'btn-primary'}`}
            onClick={isRecording ? stopRecording : startRecording}
            disabled={transcribeMutation.isPending}
          >
            {isRecording ? <MicOff size={16} /> : <Mic size={16} />}
            {isRecording ? 'Stop Recording' : 'Start Recording'}
          </button>

          <div style={{ flex: 1 }} />

          <label className="btn btn-secondary" style={{ cursor: 'pointer' }}>
            <Upload size={16} />
            Upload Audio File
            <input
              type="file"
              accept="audio/*"
              onChange={handleFileUpload}
              style={{ display: 'none' }}
              disabled={transcribeMutation.isPending}
            />
          </label>

          <select
            className="form-input"
            value={selectedLanguage}
            onChange={(e) => setSelectedLanguage(e.target.value)}
            style={{ width: 150 }}
          >
            <option value="en">English</option>
            <option value="fr">French</option>
            <option value="es">Spanish</option>
            <option value="de">German</option>
            <option value="zh">Chinese</option>
          </select>
        </div>

        {/* Recording Status */}
        {isRecording && (
          <div style={{ 
            padding: 12, 
            background: 'var(--danger-bg)', 
            borderRadius: 8,
            marginBottom: 16,
            display: 'flex',
            alignItems: 'center',
            gap: 8
          }}>
            <div style={{ 
              width: 10, 
              height: 10, 
              background: 'var(--danger)', 
              borderRadius: '50%',
              animation: 'pulse 1s infinite'
            }} />
            <span style={{ color: 'var(--danger)' }}>Recording in progress...</span>
          </div>
        )}

        {/* File/Recording Info */}
        {(recordedBlob || selectedFile) && (
          <div style={{ 
            padding: 12, 
            background: 'var(--card-bg)', 
            borderRadius: 8,
            marginBottom: 16,
            display: 'flex',
            alignItems: 'center',
            gap: 12
          }}>
            <FileAudio size={20} style={{ color: 'var(--primary)' }} />
            <span style={{ flex: 1 }}>
              {recordedBlob ? 'Recorded Audio' : selectedFile?.name}
            </span>
            <span style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
              {recordedBlob ? `${(recordedBlob.size / 1024).toFixed(1)} KB` : `${(selectedFile?.size / 1024).toFixed(1)} KB`}
            </span>
          </div>
        )}

        {/* Transcribe Button */}
        <button
          className="btn btn-primary"
          onClick={handleTranscribe}
          disabled={!recordedBlob && !selectedFile}
          style={{ width: '100%' }}
        >
          <Sparkles size={16} />
          {transcribeMutation.isPending ? 'Transcribing...' : 'Transcribe Audio'}
        </button>

        {/* Transcription Result */}
        {transcribeMutation.data && (
          <TranscriptionResult result={transcribeMutation.data} />
        )}

        {transcribeMutation.error && (
          <div style={{ 
            marginTop: 16, 
            padding: 12, 
            background: 'var(--danger-bg)', 
            borderRadius: 8,
            color: 'var(--danger)',
            display: 'flex',
            alignItems: 'center',
            gap: 8
          }}>
            <AlertCircle size={16} />
            <span>
              Transcription failed: {transcribeMutation.error.message || 'Unknown error'}
            </span>
          </div>
        )}
      </div>

      {/* Text-to-Speech Section */}
      <div className="card">
        <h3 className="card-title">
          <Languages size={16} />
          Text to Speech
        </h3>

        <textarea
          className="form-input"
          placeholder="Enter text to convert to speech..."
          value={textInput}
          onChange={(e) => setTextInput(e.target.value)}
          style={{ 
            minHeight: 120, 
            marginBottom: 16,
            fontFamily: 'inherit'
          }}
          disabled={ttsMutation.isPending}
        />

        <div style={{ display: 'flex', gap: 12, alignItems: 'center', marginBottom: 16 }}>
          <button
            className="btn btn-primary"
            onClick={handleTextToSpeech}
            disabled={!textInput.trim() || ttsMutation.isPending}
          >
            <Sparkles size={16} />
            {ttsMutation.isPending ? 'Generating...' : 'Generate Speech'}
          </button>

          <select
            className="form-input"
            value={selectedLanguage}
            onChange={(e) => setSelectedLanguage(e.target.value)}
            style={{ width: 150 }}
          >
            <option value="en">English</option>
            <option value="fr">French</option>
            <option value="es">Spanish</option>
            <option value="de">German</option>
            <option value="zh">Chinese</option>
          </select>
        </div>

        {/* TTS Result */}
        {ttsMutation.data && ttsMutation.data.audio_url && (
          <div style={{ 
            padding: 16, 
            background: 'var(--card-bg)', 
            borderRadius: 8
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
              <CheckCircle size={16} style={{ color: 'var(--success)' }} />
              <span style={{ fontWeight: 600 }}>Speech Generated</span>
            </div>
            <AudioPlayer 
              audioUrl={ttsMutation.data.audio_url}
              isPlaying={false}
            />
            <button
              className="btn btn-secondary"
              onClick={() => handleDownload(ttsMutation.data.audio_url, 'speech.mp3')}
              style={{ marginTop: 12 }}
            >
              Download Audio
            </button>
          </div>
        )}

        {ttsMutation.error && (
          <div style={{ 
            marginTop: 16, 
            padding: 12, 
            background: 'var(--danger-bg)', 
            borderRadius: 8,
            color: 'var(--danger)',
            display: 'flex',
            alignItems: 'center',
            gap: 8
          }}>
            <AlertCircle size={16} />
            <span>
              Speech generation failed: {ttsMutation.error.message || 'Unknown error'}
            </span>
          </div>
        )}
      </div>
    </div>
  )
}