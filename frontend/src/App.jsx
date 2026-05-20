import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import Layout from './components/Layout'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
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
import MonitoringPage from './pages/MonitoringPage'
import ScannerPage from './pages/ScannerPage'
import FinancialPage from './pages/FinancialPage'
import IntegrationsPage from './pages/IntegrationsPage'
import BulkDataPage from './pages/BulkDataPage'

function ProtectedRoute({ children, page }) {
  const { isAuthenticated, loading, hasPage } = useAuth()
  
  if (loading) return <div className="text-center" style={{ padding: '100px' }}>Loading...</div>
  if (!isAuthenticated) return <Navigate to="/login" replace />
  if (page && !hasPage(page)) return <Navigate to="/dashboard" replace />
  
  return children
}

export default function App() {
  const { isAuthenticated, loading } = useAuth()

  if (loading) return <div className="text-center" style={{ padding: '100px' }}>Loading OmniIntelOS...</div>

  return (
    <Routes>
      <Route path="/login" element={
        isAuthenticated ? <Navigate to="/dashboard" replace /> : <LoginPage />
      } />
      
      <Route path="/" element={
        <ProtectedRoute><Layout /></ProtectedRoute>
      }>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={
          <ProtectedRoute page="dashboard"><DashboardPage /></ProtectedRoute>
        } />
        <Route path="chat" element={
          <ProtectedRoute page="assistant"><ChatPage /></ProtectedRoute>
        } />
        <Route path="analytics" element={
          <ProtectedRoute page="analytics"><AnalyticsPage /></ProtectedRoute>
        } />
        <Route path="financial" element={
          <ProtectedRoute page="financial"><FinancialPage /></ProtectedRoute>
        } />
        <Route path="integrations" element={
          <ProtectedRoute page="data_hub"><IntegrationsPage /></ProtectedRoute>
        } />
        <Route path="bulk" element={
          <ProtectedRoute page="data_hub"><BulkDataPage /></ProtectedRoute>
        } />
        <Route path="data-hub" element={
          <ProtectedRoute page="data_hub"><DataHubPage /></ProtectedRoute>
        } />
        <Route path="admin" element={
          <ProtectedRoute page="admin"><AdminPage /></ProtectedRoute>
        } />
        <Route path="settings" element={
          <ProtectedRoute page="settings"><SettingsPage /></ProtectedRoute>
        } />
        <Route path="hr" element={
          <ProtectedRoute page="hr"><HRPage /></ProtectedRoute>
        } />
        <Route path="logistics" element={
          <ProtectedRoute page="logistics"><LogisticsPage /></ProtectedRoute>
        } />
        <Route path="it" element={
          <ProtectedRoute page="it"><ITPage /></ProtectedRoute>
        } />
        <Route path="operations" element={
          <ProtectedRoute page="operations"><OperationsPage /></ProtectedRoute>
        } />
        <Route path="forecasting" element={
          <ProtectedRoute page="forecasting"><ForecastingPage /></ProtectedRoute>
        } />
        <Route path="esg" element={
          <ProtectedRoute page="esg"><ESGPage /></ProtectedRoute>
        } />
        <Route path="risk" element={
          <ProtectedRoute page="risk"><RiskPage /></ProtectedRoute>
        } />
        <Route path="monitoring" element={
          <ProtectedRoute page="admin"><MonitoringPage /></ProtectedRoute>
        } />
        <Route path="scanner" element={
          <ProtectedRoute page="data_hub"><ScannerPage /></ProtectedRoute>
        } />
      </Route>
      
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}
