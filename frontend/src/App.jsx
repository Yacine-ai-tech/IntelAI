import UserGuidePage from './pages/UserGuidePage'
import BenchmarkPage from './pages/BenchmarkPage';
import ApiDocsPage from './pages/ApiDocsPage';
import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import Layout from './components/Layout'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import WorkspacePage from './pages/WorkspacePage'
import ReportsPage from './pages/ReportsPage'
import GovernancePage from './pages/GovernancePage'
import OrganizationPage from './pages/OrganizationPage'
import ComparePage from './pages/ComparePage'
import KnowledgeGraphPage from './pages/KnowledgeGraphPage' 
import ChatPage from './pages/ChatPage'
import AnalyticsPage from './pages/AnalyticsPage'
import DataHubPage from './pages/DataHubPage'
import AdminPage from './pages/AdminPage'
import SettingsPage from './pages/SettingsPage'
import HRPage from './pages/HRPage'
import LogisticsPage from './pages/LogisticsPage'
import ITPage from './pages/ITPage'
import OperationsPage from './pages/OperationsPage'
import ForecastingPage from './pages/ForecastingPage'
import ESGPage from './pages/ESGPage'
import RiskPage from './pages/RiskPage'
import FinancialPage from './pages/FinancialPage'
import KnowledgePage from './pages/KnowledgePage'

import GrowthPage from './pages/GrowthPage'
import GlossaryPage from './pages/GlossaryPage'

import { Component } from 'react'

class ErrorBoundary extends Component {
  state = { hasError: false, error: null }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  componentDidCatch(error, errorInfo) {
    console.error("IntelAI UI Error caught by boundary:", error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="p-8 text-center text-red-400 bg-red-950/30 rounded-xl border border-red-800/50 m-4" style={{ margin: '40px auto', maxWidth: '600px', padding: '30px' }}>
          <h2 className="text-xl font-bold mb-2">Component Error</h2>
          <p className="text-sm opacity-80 mb-4">{this.state.error?.message || "An unexpected error occurred."}</p>
          <button
            onClick={() => {
              this.setState({ hasError: false, error: null })
              window.location.reload()
            }}
            className="px-4 py-2 bg-red-600 hover:bg-red-500 text-white font-medium rounded-lg text-sm transition"
            style={{ padding: '8px 16px', background: '#e11d48', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer' }}
          >
            Reload Page
          </button>
        </div>
      )
    }
    return this.props.children
  }
}

function ProtectedRoute({ children, page }) {
  const { isAuthenticated, loading, hasPage } = useAuth()
  
  if (loading) return <div className="text-center" style={{ padding: '100px' }}>Loading...</div>
  if (!isAuthenticated) return <Navigate to="/login" replace />
  if (page && !hasPage(page)) return <Navigate to="/chat" replace />
  
  return children
}

export default function App() {
  const { isAuthenticated, loading } = useAuth()

  if (loading) return <div className="text-center" style={{ padding: '100px' }}>Loading IntelAI...</div>

  return (
    <ErrorBoundary>
      <Routes>
        <Route path="/login" element={
          isAuthenticated ? <Navigate to="/workspace" replace /> : <LoginPage />
        } />

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
        </Route>
        
        <Route path="/benchmark" element={<BenchmarkPage />} />
        <Route path="/api-docs" element={<ApiDocsPage />} />
        <Route path="/user-guide" element={<UserGuidePage />} />
        <Route path="*" element={<Navigate to="/workspace" replace />} />
      </Routes>
    </ErrorBoundary>
  )
}
