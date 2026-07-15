import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';

export default function CameraMobilePage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');
  const [status, setStatus] = useState('idle');
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!token) {
      setError('Invalid pairing token. Please scan the QR code from DocIntel again.');
    }
  }, [token]);

  const handleCapture = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setStatus('uploading');
    setError('');
    try {
      const form = new FormData();
      form.append('token', token);
      form.append('file', file);
      form.append('doc_type', 'default');

      const res = await fetch('https://docintel-f4g1.onrender.com/camera/upload', {
        method: 'POST',
        body: form
      });
      
      const data = await res.json();
      
      if (!res.ok) {
        throw new Error(data.detail || 'Upload failed');
      }
      
      setStatus('success');
      setResult(data);
    } catch (err) {
      setError(err.message);
      setStatus('idle');
    }
  };

  if (error && !token) {
    return (
      <div style={{ padding: '20px', textAlign: 'center', fontFamily: 'sans-serif' }}>
        <h2 style={{ color: '#ff4444' }}>Error</h2>
        <p>{error}</p>
      </div>
    );
  }

  return (
    <div style={{ 
      padding: '20px', 
      minHeight: '100vh', 
      backgroundColor: '#121212', 
      color: '#fff',
      fontFamily: 'sans-serif',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center'
    }}>
      <div style={{ textAlign: 'center', maxWidth: '400px', width: '100%' }}>
        <h1 style={{ marginBottom: '10px' }}>DocIntel Scanner</h1>
        <p style={{ opacity: 0.7, marginBottom: '40px' }}>Session active. Ready to scan.</p>

        {status === 'idle' && (
          <div style={{ position: 'relative' }}>
            <label 
              htmlFor="camera-input"
              style={{
                display: 'block',
                background: '#4CAF50',
                color: '#fff',
                padding: '20px',
                borderRadius: '12px',
                fontSize: '18px',
                fontWeight: 'bold',
                cursor: 'pointer',
                boxShadow: '0 4px 12px rgba(76, 175, 80, 0.3)'
              }}
            >
              Take Photo
            </label>
            <input 
              id="camera-input"
              type="file" 
              accept="image/*" 
              capture="environment" 
              onChange={handleCapture}
              style={{ display: 'none' }} 
            />
          </div>
        )}

        {status === 'uploading' && (
          <div>
            <div style={{ 
              width: '50px', 
              height: '50px', 
              border: '4px solid rgba(255,255,255,0.1)', 
              borderTop: '4px solid #4CAF50', 
              borderRadius: '50%', 
              animation: 'spin 1s linear infinite',
              margin: '0 auto 20px auto'
            }}>
              <style>{`@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`}</style>
            </div>
            <p>Processing via Vision Agent...</p>
          </div>
        )}

        {status === 'success' && (
          <div>
            <div style={{ fontSize: '48px', marginBottom: '10px' }}>✅</div>
            <h2 style={{ color: '#4CAF50', marginBottom: '20px' }}>Upload Successful!</h2>
            <p style={{ opacity: 0.8 }}>Check your desktop dashboard for the results.</p>
            <button 
              onClick={() => setStatus('idle')}
              style={{
                background: 'transparent',
                color: '#fff',
                border: '1px solid rgba(255,255,255,0.3)',
                padding: '10px 20px',
                borderRadius: '8px',
                marginTop: '30px'
              }}
            >
              Scan Another Document
            </button>
          </div>
        )}

        {error && (
          <div style={{ marginTop: '20px', color: '#ff4444', background: 'rgba(255,68,68,0.1)', padding: '15px', borderRadius: '8px' }}>
            {error}
          </div>
        )}
      </div>
    </div>
  );
}
