import axios from 'axios'

const API_BASE = '/api/v1'

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
})

// Attach JWT token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle 401 globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// ── Auth ────────────────────────────────────────────────
export const login = (username, password) =>
  api.post('/auth/login', { username, password })
export const demoLogin = (role) =>
  api.post(`/auth/demo-login?role=${encodeURIComponent(role)}`)

export const register = (username, password, role = 'viewer') =>
  api.post('/auth/register', { username, password, role })

export const getMe = () => api.get('/auth/me')

// ── Chat ────────────────────────────────────────────────
export const sendChat = (message, persona = null, sessionId = null, context = '') =>
  api.post('/chat', { message, persona, session_id: sessionId, context })

export const listPersonas = () => api.get('/personas')

// ── Glossary (contextual explainer / grounding) ─────────
export const getGlossary = (domain = null, lang = null) => api.get('/glossary', { params: { ...(domain ? { domain } : {}), ...(lang ? { lang } : {}) } })

// ── Data export ─────────────────────────────────────────
export const exportData = (format = 'json', source_type = 'kpis', source_name = null) =>
  api.post('/data/export', { format, source_type, source_name })

// ── Chat Sessions & History ─────────────────────────────
export const getChatSessions = () => api.get('/chat/sessions')
export const createChatSession = () => api.post('/chat/sessions')
export const getChatMessages = (sessionId) => api.get(`/chat/sessions/${sessionId}/messages`)
export const renameSession = (sessionId, title) => api.put(`/chat/sessions/${sessionId}/title`, { title })
export const deleteChatSession = (sessionId) => api.delete(`/chat/sessions/${sessionId}`)

// ── Knowledge / Vector Search ───────────────────────────
export const searchKnowledge = (query, n = 5) => api.get('/knowledge/search', { params: { q: query, n } })
export const getKnowledgeStats = () => api.get('/knowledge/stats')

// ── KPIs (cross-domain) ────────────────────────────────
export const getKPIs = (params = {}) => api.get('/kpis', { params })
export const getPeriods = () => api.get('/kpis/periods')
export const getMetrics = () => api.get('/kpis/metrics')
export const getCategories = () => api.get('/kpis/categories')

// ── Insights ────────────────────────────────────────────
export const getHealth = () => api.get('/insights/health')
export const getRisk = () => api.get('/insights/risk')
export const getSummary = () => api.get('/insights/summary')
export const getAnomalies = (metric) => api.get('/insights/anomalies', { params: { metric } })

// ── Forecast ────────────────────────────────────────────
export const runForecast = (metric, periods = 3) => {
  const formData = new FormData()
  formData.append('metric', metric)
  formData.append('periods', periods)
  return api.post('/forecast', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

// ── Financial ───────────────────────────────────────────
export const generateStatement = (statementType, period = null) =>
  api.post('/financial/statement', { statement_type: statementType, period })

// ── HR / People ─────────────────────────────────────────
export const getHRSummary = () => api.get('/hr/summary')
export const getHRDepartments = () => api.get('/hr/departments')
export const getHRRecruitment = () => api.get('/hr/recruitment')
export const getHRTraining = () => api.get('/hr/training')
export const getHRHealth = () => api.get('/hr/health')

// ── Logistics ───────────────────────────────────────────
export const getLogisticsSummary = () => api.get('/logistics/summary')
export const getLogisticsInventory = () => api.get('/logistics/inventory')
export const getLogisticsShipping = () => api.get('/logistics/shipping')
export const getLogisticsSuppliers = () => api.get('/logistics/suppliers')
export const getLogisticsHealth = () => api.get('/logistics/health')

// ── IT Operations ───────────────────────────────────────
export const getITOverview = () => api.get('/it/overview')
export const getITTickets = () => api.get('/it/tickets')
export const getITSecurity = () => api.get('/it/security')
export const getITInfrastructure = () => api.get('/it/infrastructure')
export const getITDevOps = () => api.get('/it/devops')
export const getITHealth = () => api.get('/it/health')

// ── Operations ──────────────────────────────────────────
export const getOpsSummary = () => api.get('/operations/summary')
export const getOpsQuality = () => api.get('/operations/quality')
export const getOpsProduction = () => api.get('/operations/production')
export const getOpsSafety = () => api.get('/operations/safety')
export const getOpsHealth = () => api.get('/operations/health')

// ── ESG ─────────────────────────────────────────────────
export const getESGSummary = () => api.get('/esg/summary')

// ── Admin ───────────────────────────────────────────────
export const listUsers = () => api.get('/admin/users')
export const updateUser = (userId, data) => api.put(`/admin/users/${userId}`, data)
export const listRoles = () => api.get('/admin/roles')
export const getAuditLog = (limit = 100) => api.get('/admin/audit', { params: { limit } })
export const seedData = () => api.post('/admin/seed')

// ── Ingestion ───────────────────────────────────────────
export const ingestMetrics = (data, sourceName = 'api') =>
  api.post('/ingest/metrics', { data, source_name: sourceName })

export const uploadCSV = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/ingest/csv', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export const uploadDocument = (file, category = 'Misc') => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('category', category)
  return api.post('/ingest/document', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

// ── File Management ───────────────────────────────────
export const getUserFiles = () => api.get('/files')
export const getFilePreview = (fileId) => api.get(`/files/${fileId}/preview`)
export const downloadFile = (fileId) => api.get(`/files/${fileId}/download`, { responseType: 'blob' })

// ── Status ──────────────────────────────────────────────
export const getStatus = () => api.get('/status')

export default api
