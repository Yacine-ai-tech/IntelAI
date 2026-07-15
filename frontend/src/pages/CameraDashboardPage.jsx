import React, { useState } from 'react';

export default function CameraDashboardPage() {
  const [qrCode, setQrCode] = useState(null);
  const [token, setToken] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handlePair = async () => {
    setLoading(true);
    setError('');
    try {
      const form = new FormData();
      form.append('user', 'admin');
      form.append('device', 'Mobile Scanner');

      const res = await fetch('https://docintel-f4g1.onrender.com/camera/pair', {
        method: 'POST',
        body: form
      });
      if (!res.ok) throw new Error('Failed to generate pairing token');
      const data = await res.json();
      setQrCode(data.qr_code);
      setToken(data.token);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '40px', color: '#fff', maxWidth: '800px', margin: '0 auto' }}>
      <h2>Mobile Camera Scanner</h2>
      <p style={{ opacity: 0.8, marginBottom: '30px' }}>
        Pair your smartphone to instantly scan physical documents directly into DocIntel.
      </p>

      <div style={{ 
        background: 'rgba(255,255,255,0.05)', 
        padding: '30px', 
        borderRadius: '12px',
        border: '1px solid rgba(255,255,255,0.1)',
        textAlign: 'center'
      }}>
        {!qrCode ? (
          <div>
            <button 
              onClick={handlePair} 
              disabled={loading}
              style={{
                background: '#4CAF50',
                color: '#fff',
                border: 'none',
                padding: '12px 24px',
                borderRadius: '8px',
                fontSize: '16px',
                cursor: loading ? 'wait' : 'pointer'
              }}
            >
              {loading ? 'Generating...' : 'Pair Mobile Device'}
            </button>
          </div>
        ) : (
          <div>
            <h3>Scan this QR code with your phone</h3>
            <div style={{ margin: '20px 0', background: '#fff', display: 'inline-block', padding: '10px', borderRadius: '8px' }}>
              <img src={qrCode} alt="QR Code" style={{ width: '250px', height: '250px' }} />
            </div>
            <p style={{ opacity: 0.7, fontSize: '14px' }}>Token: {token}</p>
            <p style={{ marginTop: '20px', color: '#4CAF50' }}>Waiting for mobile upload...</p>
            <button 
              onClick={() => { setQrCode(null); setToken(''); }}
              style={{
                background: 'transparent',
                color: '#fff',
                border: '1px solid rgba(255,255,255,0.3)',
                padding: '8px 16px',
                borderRadius: '6px',
                marginTop: '10px',
                cursor: 'pointer'
              }}
            >
              Reset Session
            </button>
          </div>
        )}

        {error && (
          <div style={{ marginTop: '20px', color: '#ff4444' }}>
            {error}
          </div>
        )}
      </div>
    </div>
  );
}
