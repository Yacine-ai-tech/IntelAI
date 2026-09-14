import React from 'react'
import { Calendar, Filter, RotateCcw } from 'lucide-react'
import { useTranslation } from '../i18n/I18nContext'

export default function PeriodFilter({
  periods = [],
  selectedPeriod = '',
  onSelectPeriod,
  startPeriod = '',
  endPeriod = '',
  onRangeChange,
  showPresets = true,
  showInterval = true,
  showSnapshot = true,
  accent = 'var(--primary)',
}) {
  const { t } = useTranslation()

  // Sorted list of periods
  const sortedPeriods = [...periods].sort()
  const latestPeriod = sortedPeriods[sortedPeriods.length - 1] || '2026-06'
  const reversedPeriods = [...sortedPeriods].reverse()

  const presets = [
    { label: t('presetAll') || 'All (2020–2026)', start: '2020-01', end: latestPeriod },
    { label: t('presetLast12M') || 'Last 12M', start: '2025-07', end: latestPeriod },
    { label: t('presetLast24M') || 'Last 24M', start: '2024-07', end: latestPeriod },
    { label: '2025–2026', start: '2025-01', end: latestPeriod },
    { label: '2023–2024', start: '2023-01', end: '2024-12' },
    { label: '2020–2022', start: '2020-01', end: '2022-12' },
  ]

  const handlePreset = (p) => {
    if (onRangeChange) {
      onRangeChange({ start: p.start, end: p.end })
    }
    if (onSelectPeriod) {
      onSelectPeriod(p.end)
    }
  }

  const handleReset = () => {
    if (onRangeChange) {
      onRangeChange({ start: '', end: '' })
    }
    if (onSelectPeriod) {
      onSelectPeriod(latestPeriod)
    }
  }

  const isPresetActive = (p) => {
    return (startPeriod === p.start && endPeriod === p.end) || (!startPeriod && !endPeriod && p.start === '2020-01')
  }

  return (
    <div
      style={{
        background: 'var(--surface)',
        border: '1px solid var(--border)',
        borderRadius: 10,
        padding: '12px 16px',
        marginBottom: 18,
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: 12,
      }}
    >
      {/* Left section: Filter icon + Snapshot period or label */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: accent, fontWeight: 600, fontSize: '.88rem' }}>
          <Calendar size={18} />
          <span>{t('timePeriodFilter') || 'Time Filter'}:</span>
        </div>

        {showSnapshot && onSelectPeriod && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <span style={{ fontSize: '.82rem', color: 'var(--text-2)' }}>{t('asOfPeriod') || 'As of'}:</span>
            <select
              className="form-input"
              style={{ padding: '4px 10px', height: 32, fontSize: '.84rem', minWidth: 140 }}
              value={selectedPeriod || latestPeriod}
              onChange={(e) => onSelectPeriod(e.target.value)}
            >
              {reversedPeriods.map((p) => (
                <option key={p} value={p}>
                  {p} {p === latestPeriod ? `(${t('latest') || 'Latest'})` : ''}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {/* Center: Quick Presets */}
      {showPresets && onRangeChange && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap' }}>
          {presets.map((p) => {
            const active = isPresetActive(p)
            return (
              <button
                key={p.label}
                type="button"
                className="btn btn-sm"
                onClick={() => handlePreset(p)}
                style={{
                  padding: '4px 10px',
                  fontSize: '.78rem',
                  borderRadius: 6,
                  border: active ? `1px solid ${accent}` : '1px solid var(--border)',
                  background: active ? accent : 'var(--surface-2)',
                  color: active ? '#fff' : 'var(--text-2)',
                  cursor: 'pointer',
                  fontWeight: active ? 600 : 400,
                  transition: 'all .15s ease',
                }}
              >
                {p.label}
              </button>
            )
          })}
        </div>
      )}

      {/* Right: Custom Date Interval dropdowns + Reset button */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
        {showInterval && onRangeChange && (
          <>
            <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
              <span style={{ fontSize: '.80rem', color: 'var(--text-3)' }}>{t('from') || 'From'}:</span>
              <select
                className="form-input"
                style={{ padding: '3px 8px', height: 30, fontSize: '.82rem', width: 110 }}
                value={startPeriod || (sortedPeriods[0] || '2020-01')}
                onChange={(e) => onRangeChange({ start: e.target.value, end: endPeriod || latestPeriod })}
              >
                {sortedPeriods.map((p) => (
                  <option key={p} value={p}>
                    {p}
                  </option>
                ))}
              </select>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
              <span style={{ fontSize: '.80rem', color: 'var(--text-3)' }}>{t('to') || 'To'}:</span>
              <select
                className="form-input"
                style={{ padding: '3px 8px', height: 30, fontSize: '.82rem', width: 110 }}
                value={endPeriod || latestPeriod}
                onChange={(e) => onRangeChange({ start: startPeriod || sortedPeriods[0] || '2020-01', end: e.target.value })}
              >
                {sortedPeriods.map((p) => (
                  <option key={p} value={p}>
                    {p}
                  </option>
                ))}
              </select>
            </div>
          </>
        )}

        <button
          type="button"
          className="btn btn-sm btn-ghost"
          onClick={handleReset}
          title={t('resetToLatest') || 'Reset to latest'}
          style={{ padding: '4px 8px', height: 30, display: 'flex', alignItems: 'center', gap: 4, fontSize: '.80rem' }}
        >
          <RotateCcw size={13} />
          <span>{t('reset') || 'Reset'}</span>
        </button>
      </div>
    </div>
  )
}
