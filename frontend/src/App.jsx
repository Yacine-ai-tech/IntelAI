import { lazy, Suspense, useCallback, useEffect, useRef, useState } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import { checkHealth } from './api'
import { WakingBackend, Loading } from './components/ui'
import Layout from './components/Layout'
import LoginPage from './pages/LoginPage'

const DashboardPage = lazy(() => import('./pages/DashboardPage'))
const WorkspacePage = lazy(() => import('./pages/WorkspacePage'))
const ReportsPage = lazy(() => import('./pages/ReportsPage'))
const GovernancePage = lazy(() => import('./pages/GovernancePage'))
const OrganizationPage = lazy(() => import('./pages/OrganizationPage'))
const ComparePage = lazy(() => import('./pages/ComparePage'))
const KnowledgeGraphPage = lazy(() => import('./pages/KnowledgeGraphPage'))
const ChatPage = lazy(() => import('./pages/ChatPage'))
const AnalyticsPage = lazy(() => import('./pages/AnalyticsPage'))
const DataHubPage = lazy(() => import('./pages/DataHubPage'))
const AdminPage = lazy(() => import('./pages/AdminPage'))
const SettingsPage = lazy(() => import('./pages/SettingsPage'))
const HRPage = lazy(() => import('./pages/HRPage'))
const LogisticsPage = lazy(() => import('./pages/LogisticsPage'))
const ITPage = lazy(() => import('./pages/ITPage'))
const OperationsPage = lazy(() => import('./pages/OperationsPage'))
const ForecastingPage = lazy(() => import('./pages/ForecastingPage'))
const ESGPage = lazy(() => import('./pages/ESGPage'))
const RiskPage = lazy(() => import('./pages/RiskPage'))
const FinancialPage = lazy(() => import('./pages/FinancialPage'))
const KnowledgePage = lazy(() => import('./pages/KnowledgePage'))
const GrowthPage = lazy(() => import('./pages/GrowthPage'))
const GlossaryPage = lazy(() => import('./pages/GlossaryPage'))
const ApiDocs = lazy(() => import('./pages/ApiDocs'))
const UserGuidePage = lazy(() => import('./pages/UserGuidePage'))
const ResearchPage = lazy(() => import('./pages/ResearchPage'))
const ArchitecturePage = lazy(() => import('./pages/ArchitecturePage'))
const BenchmarkPage = lazy(() => import('./pages/BenchmarkPage'))
const SandboxPage = lazy(() => import('./pages/SandboxPage'))
const LicensePage = lazy(() => import('./pages/LicensePage'))

// Unguessable operator sign-in path — set VITE_ADMIN_PATH at build time.
// Credential login (admin + registered users) lives ONLY here; /login is demo-only.
const ADMIN_PATH = import.meta.env.VITE_ADMIN_PATH || '/operator'

function ProtectedRoute({ children, page }) {
  const { isAuthenticated, loading, hasPage } = useAuth()
  
  if (loading) return <div className="text-center" style={{ padding: '100px' }}>Loading...</div>
  if (!isAuthenticated) return <Navigate to="/login" replace />
  if (page && !hasPage(page)) return <Navigate to="/chat" replace />
  
  return children
}

export default function App() {
  const { isAuthenticated, loading, token } = useAuth()
  const [backendUp, setBackendUp] = useState(null) // null = checking, true/false once known
  const [attempts, setAttempts] = useState(0)
  const everConnected = useRef(false)

  // Only needed for the no-token path: with a stored token, AuthContext's own getMe()
  // call already proves the backend is reachable (or isn't, via its catch) before
  // `loading` clears, so a second independent check here would be redundant.
  const check = useCallback(() => {
    if (token) return
    checkHealth()
      .then(() => { everConnected.current = true; setBackendUp(true) })
      .catch(() => setBackendUp(false))
  }, [token])

  useEffect(() => { check() }, [check, attempts])

  useEffect(() => {
    if (backendUp === false && attempts < 6) {
      const t = setTimeout(() => setAttempts((a) => a + 1), 8000)
      return () => clearTimeout(t)
    }
  }, [backendUp, attempts])

  if (loading) return <div className="text-center" style={{ padding: '100px' }}>Loading IntelAI...</div>

  if (!token && backendUp === false && attempts >= 6 && !everConnected.current) {
    return <WakingBackend waking={attempts < 6} onRetry={() => setAttempts(0)} />
  }

  return (
    <Suspense fallback={<Loading />}>
    <Routes>
      <Route path="/login" element={
        isAuthenticated ? <Navigate to="/workspace" replace /> : <LoginPage showCredentials={false} />
      } />
      <Route path={ADMIN_PATH} element={
        isAuthenticated ? <Navigate to="/workspace" replace /> : <LoginPage showCredentials />
      } />
      <Route path="/sandbox" element={<SandboxPage />} />

      <Route path="/" element={
        <ProtectedRoute><Layout /></ProtectedRoute>
      }>
        <Route index element={<Navigate to="/workspace" replace />} />
        <Route path="workspace" element={<ProtectedRoute page="assistant"><WorkspacePage /></ProtectedRoute>} />
        <Route path="reports" element={<ProtectedRoute page="analytics"><ReportsPage /></ProtectedRoute>} />
        <Route path="compare" element={<ProtectedRoute page="assistant"><ComparePage /></ProtectedRoute>} />
        <Route path="knowledge-graph" element={<ProtectedRoute page="analytics"><KnowledgeGraphPage /></ProtectedRoute>} />
        <Route path="organization" element={<ProtectedRoute page="analytics"><OrganizationPage /></ProtectedRoute>} />
        <Route path="governance" element={<ProtectedRoute page="admin"><GovernancePage /></ProtectedRoute>} />
        <Route path="dashboard" element={<ProtectedRoute page="dashboard"><DashboardPage /></ProtectedRoute>} />
        <Route path="chat" element={<ProtectedRoute page="assistant"><ChatPage /></ProtectedRoute>} />
        <Route path="analytics" element={<ProtectedRoute page="analytics"><AnalyticsPage /></ProtectedRoute>} />
        <Route path="growth" element={<ProtectedRoute page="analytics"><GrowthPage /></ProtectedRoute>} />
        <Route path="financial" element={<ProtectedRoute page="financial"><FinancialPage /></ProtectedRoute>} />
        <Route path="data-hub" element={<ProtectedRoute page="data_hub"><DataHubPage /></ProtectedRoute>} />
        <Route path="admin" element={<ProtectedRoute page="admin"><AdminPage /></ProtectedRoute>} />
        <Route path="settings" element={<ProtectedRoute page="settings"><SettingsPage /></ProtectedRoute>} />
        <Route path="hr" element={<ProtectedRoute page="hr"><HRPage /></ProtectedRoute>} />
        <Route path="logistics" element={<ProtectedRoute page="logistics"><LogisticsPage /></ProtectedRoute>} />
        <Route path="it" element={<ProtectedRoute page="it"><ITPage /></ProtectedRoute>} />
        <Route path="operations" element={<ProtectedRoute page="operations"><OperationsPage /></ProtectedRoute>} />
        <Route path="forecasting" element={<ProtectedRoute page="forecasting"><ForecastingPage /></ProtectedRoute>} />
        <Route path="esg" element={<ProtectedRoute page="esg"><ESGPage /></ProtectedRoute>} />
        <Route path="risk" element={<ProtectedRoute page="risk"><RiskPage /></ProtectedRoute>} />
        <Route path="knowledge" element={<ProtectedRoute page="analytics"><KnowledgePage /></ProtectedRoute>} />
        <Route path="glossary" element={<ProtectedRoute page="analytics"><GlossaryPage /></ProtectedRoute>} />
        <Route path="license" element={<LicensePage />} />
        <Route path="user-guide" element={<ProtectedRoute page="assistant"><UserGuidePage /></ProtectedRoute>} />
        <Route path="guide" element={<Navigate to="/user-guide" replace />} />
        <Route path="architecture" element={<ProtectedRoute page="assistant"><ArchitecturePage /></ProtectedRoute>} />
        <Route path="research" element={<ProtectedRoute page="assistant"><ResearchPage /></ProtectedRoute>} />
        <Route path="benchmark" element={<ProtectedRoute page="assistant"><BenchmarkPage /></ProtectedRoute>} />
        <Route path="benchmarks" element={<Navigate to="/benchmark" replace />} />
        <Route path="api-docs" element={<ProtectedRoute page="assistant"><ApiDocs /></ProtectedRoute>} />
      </Route>
      
      <Route path="*" element={<Navigate to="/workspace" replace />} />
    </Routes>
    </Suspense>
  )
}
