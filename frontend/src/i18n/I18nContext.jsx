import React, { createContext, useContext, useState, useCallback, useEffect } from 'react'
import translations from './translations'

const I18nContext = createContext()

// Convert camelCase key to readable label as last-resort fallback
function keyToLabel(key) {
  if (!key) return ''
  // Remove 'nav' prefix if present, then split camelCase
  const k = key.startsWith('nav') ? key.slice(3) : key
  return k.replace(/([A-Z])/g, ' $1').trim()
}

export function I18nProvider({ children }) {
  const [lang, setLangState] = useState(() => {
    try { return localStorage.getItem('omni_lang') || 'en' }
    catch { return 'en' }
  })

  const setLang = useCallback((l) => {
    setLangState(l)
    try { localStorage.setItem('omni_lang', l) } catch {}
  }, [])

  const t = useCallback((key) => {
    const val = translations[lang]?.[key] ?? translations.en?.[key]
    // Return human readable fallback instead of null to prevent blank nav items
    return val !== undefined ? val : keyToLabel(key)
  }, [lang])

  // Listen for storage changes from other tabs
  useEffect(() => {
    const handler = (e) => { if (e.key === 'omni_lang' && e.newValue) setLangState(e.newValue) }
    window.addEventListener('storage', handler)
    return () => window.removeEventListener('storage', handler)
  }, [])

  return (
    <I18nContext.Provider value={{ t, lang, setLang }}>
      {children}
    </I18nContext.Provider>
  )
}

export function useTranslation() {
  const ctx = useContext(I18nContext)
  if (!ctx) throw new Error('useTranslation must be used inside <I18nProvider>')
  return ctx
}
