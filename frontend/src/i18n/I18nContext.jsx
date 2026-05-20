import React, { createContext, useContext, useState, useCallback, useEffect } from 'react'
import translations from './translations'

const I18nContext = createContext()

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
    return translations[lang]?.[key] ?? translations.en?.[key] ?? key
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
