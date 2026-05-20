import { createContext, useContext, useState, useEffect } from 'react'
import { login as apiLogin, getMe } from '../api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(localStorage.getItem('access_token'))
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (token) {
      getMe()
        .then((res) => {
          setUser(res.data)
          setLoading(false)
        })
        .catch(() => {
          localStorage.removeItem('access_token')
          localStorage.removeItem('user')
          setToken(null)
          setUser(null)
          setLoading(false)
        })
    } else {
      setLoading(false)
    }
  }, [token])

  const login = async (username, password) => {
    const res = await apiLogin(username, password)
    const { access_token, user: userData } = res.data
    localStorage.setItem('access_token', access_token)
    localStorage.setItem('user', JSON.stringify(userData))
    setToken(access_token)
    setUser(userData)
    return userData
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
    setToken(null)
    setUser(null)
  }

  const isAuthenticated = !!user && !!token
  const hasPage = (page) => {
    if (!user) return false
    const pages = user.pages || []
    return pages.includes('*') || pages.includes(page)
  }

  const hasAction = (action) => {
    // Check from ROLE_DEFINITIONS in user data
    return true // Simplified — actual check happens server-side
  }

  return (
    <AuthContext.Provider value={{ user, token, loading, login, logout, isAuthenticated, hasPage, hasAction }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used within AuthProvider')
  return context
}
