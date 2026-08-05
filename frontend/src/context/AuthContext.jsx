import { createContext, useContext, useState, useEffect } from 'react'
import { login as apiLogin, demoLogin as apiDemoLogin, getMe } from '../api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(localStorage.getItem('access_token'))
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (token) {
      // Retry getMe up to 3 times to handle Render cold-start delay
      const tryGetMe = async (attemptsLeft) => {
        try {
          const res = await getMe();
          setUser(res.data);
          setLoading(false);
        } catch (err) {
          if (attemptsLeft > 0 && !err.response) {
            // Network error (likely cold start) - retry after delay
            await new Promise(r => setTimeout(r, 4000));
            await tryGetMe(attemptsLeft - 1);
          } else {
            localStorage.removeItem('access_token');
            localStorage.removeItem('user');
            setToken(null);
            setUser(null);
            setLoading(false);
          }
        }
      };
      tryGetMe(3);
    } else {
      setLoading(false);
    }
  }, [token])

  const login = async (username, password) => {
    const res = await apiLogin(username, password)
    const { access_token, user: userData } = res.data
    localStorage.setItem('access_token', access_token)
    localStorage.setItem('user', JSON.stringify(userData))
    if (userData.role === 'admin') localStorage.setItem('was_admin', 'true')
    else localStorage.removeItem('was_admin')
    setToken(access_token)
    setUser(userData)
    return userData
  }

  const demoLogin = async (role) => {
    const res = await apiDemoLogin(role)
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
    localStorage.removeItem('was_admin')
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
    if (!user) return false
    const actions = user.actions || []
    return actions.includes('*') || actions.includes(action)
  }

  return (
    <AuthContext.Provider value={{ user, token, loading, login, demoLogin, logout, isAuthenticated, hasPage, hasAction }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used within AuthProvider')
  return context
}
