import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE_URL ? import.meta.env.VITE_API_BASE_URL + '/api/v1' : '/api/v1'

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
})

// Bare, unauthenticated liveness check at the API root (not /api/v1) — used to tell a
// cold/unreachable backend apart from "you're just not logged in yet", so a first-time
// visitor sees a "waking up" state instead of a login form that will silently fail.
const HEALTH_BASE = import.meta.env.VITE_API_BASE_URL || ''
export const checkHealth = () => axios.get(HEALTH_BASE + '/health', { timeout: 8000 })

const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// One anonymous, per-browser id — lets the demo give each visitor their own chat
// history/uploads instead of everyone sharing one persona's data. Not an auth
// credential; just keeps visitors from seeing each other's demo content.
function getDemoSessionId() {
  let id = localStorage.getItem('demo_session_id')
  if (!id) {
    id = (crypto.randomUUID ? crypto.randomUUID() : `${Date.now()}-${Math.random().toString(36).slice(2)}`)
    localStorage.setItem('demo_session_id', id)
  }
  return id
}

// Attach JWT token + demo session id to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  config.headers['X-Demo-Session-Id'] = getDemoSessionId()
  return config
})

// Handle 401 globally
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const config = error.config;
    if (config) {
      config.__retryCount = config.__retryCount || 0;
      const status = error.response ? error.response.status : null;
      // Retry on network errors or 502, 503, 504 (Cloudflare auto-wake)
      if (!status || status >= 500) {
        if (config.__retryCount < 5) {
          config.__retryCount += 1;
          await delay(2000 * config.__retryCount);
          return api(config);
        }
      }
    }
    
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
// POST /chat is synchronous end-to-end, and a real chat turn under cold retrieval can
// take 60-100s+ — long enough that the reverse proxy in front of this service cuts the
// connection before an otherwise-successful response comes back (confirmed live: this
// showed up as the request hanging with no response at all). The backend's own
// /chat/async + GET /chat/{job_id} pair exists specifically to avoid that: return
// immediately with a job_id, then poll in short, fast requests that can never individually
// run long enough to hit that ceiling — same pattern as DocIntel's batch upload/status.
export const sendChat = async (message, persona = null, sessionId = null, context = '', lang = 'en', signal = null) => {
  const { data: job } = await api.post('/chat/async', { message, persona, session_id: sessionId, context, language: lang }, { signal })
  const jobId = job.job_id
  const pollIntervalMs = 2000
  const maxWaitMs = 6 * 60 * 1000
  const startedAt = Date.now()
  while (true) {
    if (signal?.aborted) { const e = new Error('canceled'); e.name = 'CanceledError'; throw e }
    if (Date.now() - startedAt > maxWaitMs) throw new Error('Chat request timed out waiting for a response.')
    await new Promise(r => setTimeout(r, pollIntervalMs))
    const { data: status } = await api.get(`/chat/${jobId}`, { signal })
    if (status.status === 'done') return { data: status }
    if (status.status === 'error') throw new Error(status.error || 'request failed')
  }
}

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
export const getHRSummary = (params = {}) => api.get('/hr/summary', { params })
export const getHRDepartments = (params = {}) => api.get('/hr/departments', { params })
export const getHRRecruitment = (params = {}) => api.get('/hr/recruitment', { params })
export const getHRTraining = (params = {}) => api.get('/hr/training', { params })
export const getHRHealth = (params = {}) => api.get('/hr/health', { params })

// ── Growth ──────────────────────────────────────────────
export const getGrowthSummary = (params = {}) => api.get('/growth/summary', { params })

// ── Logistics ───────────────────────────────────────────
export const getLogisticsSummary = (params = {}) => api.get('/logistics/summary', { params })
export const getLogisticsInventory = (params = {}) => api.get('/logistics/inventory', { params })
export const getLogisticsShipping = (params = {}) => api.get('/logistics/shipping', { params })
export const getLogisticsSuppliers = (params = {}) => api.get('/logistics/suppliers', { params })
export const getLogisticsHealth = (params = {}) => api.get('/logistics/health', { params })

// ── IT Operations ───────────────────────────────────────
export const getITOverview = (params = {}) => api.get('/it/overview', { params })
export const getITTickets = (params = {}) => api.get('/it/tickets', { params })
export const getITSecurity = (params = {}) => api.get('/it/security', { params })
export const getITInfrastructure = (params = {}) => api.get('/it/infrastructure', { params })
export const getITDevOps = (params = {}) => api.get('/it/devops', { params })
export const getITHealth = (params = {}) => api.get('/it/health', { params })

// ── Operations ──────────────────────────────────────────
export const getOpsSummary = (params = {}) => api.get('/operations/summary', { params })
export const getOpsQuality = (params = {}) => api.get('/operations/quality', { params })
export const getOpsProduction = (params = {}) => api.get('/operations/production', { params })
export const getOpsSafety = (params = {}) => api.get('/operations/safety', { params })
export const getOpsHealth = (params = {}) => api.get('/operations/health', { params })

// ── ESG ─────────────────────────────────────────────────
export const getESGSummary = (params = {}) => api.get('/esg/summary', { params })

// ── Admin ───────────────────────────────────────────────
export const listUsers = () => api.get('/admin/users')
export const updateUser = (userId, data) => api.put(`/admin/users/${userId}`, data)
export const listRoles = () => api.get('/admin/roles')
export const getAuditLog = (limit = 100) => api.get('/admin/audit', { params: { limit } })
export const seedData = () => api.post('/admin/seed')
export const reindexVectors = (force = true) => api.post(`/admin/reindex?force=${force}`)
export const cleanupData = () => api.post('/admin/cleanup')

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

// ── Scenario Management ─────────────────────────────────
// A scenario switch writes thousands of KPI rows, extracts entities, and generates +
// embeds knowledge docs — confirmed live to take 80s+, long enough that the proxy in
// front of production can cut the connection with a 502/524 before the (otherwise
// successful) synchronous response comes back. Submit + poll instead, so no single
// request needs to stay open long enough to hit that ceiling.
// Mimics axios's error shape (err.response.data.detail) on failure — existing callers
// already read errors that way (from the old synchronous endpoint's real axios
// errors), so this keeps their error handling working unchanged.
const scenarioError = (detail) => {
  const err = new Error(detail)
  err.response = { data: { detail } }
  return err
}

export const switchScenario = async (scenarioId, { pollIntervalMs = 3000, timeoutMs = 180000 } = {}) => {
  const submit = await api.post('/admin/scenario/async', { scenario: scenarioId })
  const jobId = submit.data.job_id
  const start = Date.now()
  while (Date.now() - start < timeoutMs) {
    const poll = await api.get(`/admin/scenario/${jobId}`)
    const { status } = poll.data
    if (status === 'done') return poll
    if (status === 'error') throw scenarioError(poll.data.error || 'Scenario switch failed')
    await delay(pollIntervalMs)
  }
  throw scenarioError('Scenario switch timed out waiting for completion')
}
export const getCurrentScenario = () => api.get('/admin/scenario')

export default api

export const deleteFile = (fileId) => api.delete(`/files/${fileId}`)
