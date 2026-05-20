import { useState } from 'react'
import { useTranslation } from '../i18n/I18nContext'
import * as api from '../api'

export default function FinancialPage() {
  const { t } = useTranslation()
  const [type, setType] = useState('income_statement')
  const [period, setPeriod] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const runGenerate = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const res = await api.generateStatement(type, period || null)
      setResult(res.data)
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed')
    }
    setLoading(false)
  }

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">{t('financialStatements')}</h1>
        <p className="page-subtitle">{t('financialStatementsDesc')}</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: 20 }}>
        <div className="card">
          <h3 className="card-title">{t('generateStatement')}</h3>
          <form onSubmit={runGenerate}>
            <div className="form-group">
              <label className="form-label">{t('statementType')}</label>
              <select className="form-input" value={type} onChange={e => setType(e.target.value)}>
                <option value="income_statement">Income Statement (P&L)</option>
                <option value="balance_sheet">Balance Sheet</option>
                <option value="cash_flow">Cash Flow</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">{t('period')}</label>
              <input className="form-input" value={period} onChange={e => setPeriod(e.target.value)} placeholder="e.g. 2025-Q4 or 2025-12" />
            </div>
            <button className="btn btn-primary" type="submit" disabled={loading}>
              {loading ? t('generating') : t('generate')}
            </button>
          </form>
        </div>

        <div className="card">
          <h3 className="card-title">{t('result')}</h3>
          {error && <div className="alert alert-danger">{error}</div>}
          {result ? (
            <div style={{ overflow: 'auto' }}>
              <pre style={{ whiteSpace: 'pre-wrap', fontSize: '0.9rem' }}>{JSON.stringify(result, null, 2)}</pre>
            </div>
          ) : (
            <p className="text-muted">{t('noResult')}</p>
          )}
        </div>
      </div>
    </div>
  )
}
