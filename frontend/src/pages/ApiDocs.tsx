import { useState } from "react";
import {
  Terminal, Copy, Check, Code2, Shield, Zap, BookOpen, Globe,
  ChevronDown, ChevronRight, Lock,
} from "lucide-react";

// Same resolution order as src/api.js's request client: an explicit VITE_API_BASE_URL
// (for split frontend/backend deployments) wins, otherwise fall back to the current
// origin (same-origin deployments, e.g. the Docker single-container setup) — so the
// copy-paste examples always match wherever this page is actually being served from,
// author's deployment or any self-hoster's, instead of a hardcoded URL.
const BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  (typeof window !== "undefined" ? window.location.origin : "");

const AUTH_META: Record<string, { label: string; color: string; icon: any }> = {
  public: { label: "Public", color: "var(--ok)", icon: Globe },
  user: { label: "Bearer JWT", color: "var(--primary)", icon: Lock },
  admin: { label: "JWT · role: admin", color: "var(--warn)", icon: Shield },
  "admin|risk": { label: "JWT · role: admin or risk", color: "var(--warn)", icon: Shield },
};

const METHOD_COLOR: Record<string, string> = {
  GET: "var(--primary)", POST: "var(--ok)", PUT: "var(--warn)", DELETE: "var(--bad)", WS: "var(--accent)",
};

// ─────────────────────────────────────────────────────────────────────────
// ENDPOINTS — every route registered on the FastAPI app (src/api/server.py),
// grouped into the information architecture used in the sidebar. Request/
// response shapes are taken from the actual handler bodies and the Pydantic
// models / service return dicts they call, not invented.
// ─────────────────────────────────────────────────────────────────────────

const ENDPOINTS = [
  // ── System ────────────────────────────────────────────────────────────
  {
    method: "GET", path: "/health", group: "System", auth: "public",
    desc: "Liveness probe. No auth, no internal token — used by the platform's uptime checks.",
    body: null,
    response: `{
  "status": "healthy",
  "service": "IntelAI API",
  "version": "2026.3.0",
  "timestamp": "2026-08-09T12:00:00Z",
  "database": "postgresql"
}`,
  },
  {
    method: "GET", path: "/api/v1/status", group: "System", auth: "user",
    desc: "Operational snapshot for the caller: KPI row count, available periods/categories and the domains the backend tracks.",
    body: null,
    response: `{
  "status": "operational",
  "user": "cfo",
  "role": "cfo",
  "total_kpis": 842,
  "periods": ["2025-01", "2025-02", "2025-03"],
  "categories": ["Finance", "Growth", "People", "Operations", "IT", "ESG"],
  "domains": ["Finance", "Growth", "People", "Operations", "IT", "ESG"]
}`,
  },

  // ── Auth ──────────────────────────────────────────────────────────────
  {
    method: "POST", path: "/api/v1/auth/login", group: "Auth", auth: "public",
    desc: "Password login. Returns a Bearer JWT (8h expiry) plus the user's page/data-access grants for the frontend to gate on.",
    bodyType: "json",
    body: `{
  "username": "cfo",
  "password": "••••••••"
}`,
    response: `{
  "access_token": "eyJhbGciOi...",
  "token_type": "bearer",
  "user": {
    "id": "8f1c...",
    "username": "cfo",
    "role": "cfo",
    "full_name": "Cfo",
    "language": "en",
    "pages": ["dashboard", "analytics", "assistant", "forecasting", "data_hub", "settings"],
    "data_access": ["Finance", "Growth"],
    "actions": ["read", "analyze", "forecast", "report", "financial_write", "ingest"]
  }
}`,
  },
  {
    method: "POST", path: "/api/v1/auth/demo-login", group: "Auth", auth: "public",
    desc: "One-click \"try as {role}\" — issues a token for a role with no password. Gated by DEMO_MODE (on by default). `role` is a query param, one of the ROLE_DEFINITIONS keys (admin, ceo, cfo, cto, coo, chro, hr, esg, risk, analyst, board, viewer). Send an `X-Demo-Session-Id` header to keep each browser's demo identity isolated (own chat history/uploads) instead of sharing one identity per role.",
    query: "?role=cfo",
    body: null,
    response: `{
  "access_token": "eyJhbGciOi...",
  "token_type": "bearer",
  "user": {
    "id": "cfo-8f1c2a90",
    "username": "cfo-8f1c2a90",
    "role": "cfo",
    "full_name": "CFO",
    "language": "en",
    "pages": ["dashboard", "analytics", "assistant", "forecasting", "data_hub", "settings"],
    "data_access": ["Finance", "Growth"],
    "actions": ["read", "analyze", "forecast", "report", "financial_write", "ingest"]
  }
}`,
  },
  {
    method: "POST", path: "/api/v1/auth/register", group: "Auth", auth: "public",
    desc: "Public self-service registration. Restricted to non-privileged roles — anything other than \"viewer\" or \"analyst\" is rejected with 403.",
    bodyType: "json",
    body: `{
  "username": "jdoe",
  "password": "••••••••",
  "role": "analyst",
  "preferred_language": "en"
}`,
    response: `{
  "status": "registered",
  "user_id": "2b6e...",
  "username": "jdoe"
}`,
  },
  {
    method: "GET", path: "/api/v1/auth/me", group: "Auth", auth: "user",
    desc: "Resolve the caller's identity, RBAC grants, and preferred language from the JWT.",
    body: null,
    response: `{
  "id": "8f1c...",
  "username": "cfo",
  "role": "cfo",
  "full_name": "Cfo",
  "language": "en",
  "pages": ["dashboard", "analytics", "assistant", "forecasting", "data_hub", "settings"],
  "data_access": ["Finance", "Growth"],
  "preferred_language": "en",
  "actions": ["read", "analyze", "forecast", "report", "financial_write", "ingest"]
}`,
  },

  // ── Copilot: chat, personas, glossary, realtime, domain preference ─────
  {
    method: "POST", path: "/api/v1/chat", group: "Copilot", auth: "user",
    desc: "Persona-routed RAG copilot. Auto-retrieves a role-scoped KPI snapshot + knowledge docs (hybrid retrieval: vector store fused with BM25/GraphRAG-lite entity traversal) and returns a grounded answer with citations. Persists both turns to the session. `blocks` is the same Markdown→typed-block structuring used by the WebSocket path (headings, lists, KPI pills, quotes, code, text).",
    bodyType: "json",
    body: `{
  "message": "What's our Q3 revenue trend?",
  "persona": "cfo",
  "session_id": null,
  "context": "",
  "language": "en"
}`,
    response: `{
  "response": "**Q3 Revenue:** $1.32M (+4.2% QoQ)...",
  "persona_used": "cfo",
  "persona_display": "CFO Analyst",
  "tokens_used": 412,
  "latency_ms": 1380,
  "session_id": "9c21...",
  "sources": [
    { "title": "Q3 Board Deck", "type": "kpi", "relevance": 0.92 }
  ],
  "blocks": [
    { "type": "kpi", "label": "Q3 Revenue", "value": "$1.32M" },
    { "type": "text", "content": "Revenue grew 4.2% quarter over quarter..." }
  ]
}`,
  },
  {
    method: "GET", path: "/api/v1/personas", group: "Copilot", auth: "user",
    desc: "List the personas the caller's role is allowed to use (RBAC-filtered subset of PERSONA_TEMPLATES: ceo, cfo, cto, coo, chro, esg, risk, analyst, general).",
    body: null,
    response: `{
  "personas": [
    { "name": "cfo", "display_name": "CFO Analyst", "data_access": ["Finance", "Growth"] },
    { "name": "general", "display_name": "IntelAI Assistant", "data_access": ["Finance", "Growth", "Operations", "People"] }
  ]
}`,
  },
  {
    method: "GET", path: "/api/v1/glossary", group: "Copilot", auth: "user",
    desc: "Authoritative, sourced domain glossary — powers the contextual explainer and grounds term definitions. `domain` filters by business domain, `term` returns a single entry (404 if unknown), `lang=fr` returns French definitions (static overlay, LLM-translated fallback for anything uncovered; numbers/formulas untouched).",
    query: "?domain=Finance&term=Gross%20Margin&lang=en",
    body: null,
    response: `{
  "terms": [
    {
      "term": "Gross Margin",
      "definition": "Revenue minus cost of goods sold, as a % of revenue.",
      "domain": "Finance",
      "formula": "(Revenue - COGS) / Revenue"
    }
  ]
}`,
  },
  {
    method: "WS", path: "/api/v1/ws/chat", group: "Copilot", auth: "user",
    desc: "Realtime copilot channel — same persona-routed RAG path as POST /chat, streamed over a persistent connection. First frame must be an auth handshake; every subsequent frame is a chat turn. Falls back gracefully to the REST endpoint if the socket can't connect.",
    body: `// 1) Connect, then send the auth handshake as the first frame:
{ "token": "<jwt access_token>" }

// 2) Send chat turns:
{ "message": "Any anomalies this month?", "persona": "cfo", "session_id": "9c21...", "language": "en" }`,
    response: `// Sent once, right after the handshake:
{ "type": "connected", "user": "cfo", "session_id": "9c21..." }

// Sent for every chat turn:
{
  "type": "response",
  "response": "...",
  "persona_used": "cfo",
  "persona_display": "CFO Analyst",
  "tokens_used": 388,
  "latency_ms": 1120,
  "sources": [...],
  "blocks": [...]
}`,
  },
  {
    method: "POST", path: "/api/v1/chatbot/domain", group: "Copilot", auth: "user",
    desc: "Set the caller's default chatbot domain focus, persisted per user.",
    query: "?domain=finance",
    body: "// domain ∈ {finance, hr, ops, esg, growth, general}",
    response: `{
  "status": "success",
  "domain": "finance",
  "message": "Chatbot domain switched to finance"
}`,
  },
  {
    method: "GET", path: "/api/v1/chatbot/domain", group: "Copilot", auth: "user",
    desc: "Get the caller's current chatbot domain preference.",
    body: null,
    response: `{
  "domain": "finance",
  "valid_domains": ["finance", "hr", "ops", "esg", "growth", "general"]
}`,
  },

  // ── Chat Sessions (persisted history, PostgreSQL) ───────────────────────
  {
    method: "GET", path: "/api/v1/chat/sessions", group: "Chat Sessions", auth: "user",
    desc: "List the caller's chat sessions (most recent 50), for the history sidebar.",
    body: null,
    response: `{ "sessions": [ { "session_id": "9c21...", "title": "Q3 revenue trend", "updated_at": "2026-08-09T10:02:00Z" } ] }`,
  },
  {
    method: "GET", path: "/api/v1/chat/sessions/{session_id}/messages", group: "Chat Sessions", auth: "user",
    desc: "Fetch all persisted messages for one session, scoped to the caller.",
    body: null,
    response: `{ "messages": [ { "role": "user", "content": "..." }, { "role": "assistant", "content": "...", "sources": [] } ], "session_id": "9c21..." }`,
  },
  {
    method: "POST", path: "/api/v1/chat/sessions", group: "Chat Sessions", auth: "user",
    desc: "Create a new empty session (used by the \"New Chat\" button before the first message is sent).",
    body: null,
    response: `{ "session_id": "b74a...", "title": "New Chat" }`,
  },
  {
    method: "PUT", path: "/api/v1/chat/sessions/{session_id}/title", group: "Chat Sessions", auth: "user",
    desc: "Rename a session.",
    bodyType: "json",
    body: `{ "title": "Q3 Deep Dive" }`,
    response: `{ "status": "updated" }`,
  },
  {
    method: "DELETE", path: "/api/v1/chat/sessions/{session_id}", group: "Chat Sessions", auth: "user",
    desc: "Delete a session and its messages.",
    body: null,
    response: `{ "status": "deleted" }`,
  },

  // ── Files ────────────────────────────────────────────────────────────
  {
    method: "GET", path: "/api/v1/files", group: "Files", auth: "user",
    desc: "List the caller's uploaded files (paginated).",
    query: "?limit=50&offset=0",
    body: null,
    response: `[ { "id": "f1a2...", "filename": "q3_report.pdf", "uploaded_at": "2026-08-01T09:11:00Z", "size_bytes": 48213 } ]`,
  },
  {
    method: "GET", path: "/api/v1/files/{file_id}/preview", group: "Files", auth: "user",
    desc: "Return the first 10,000 characters of extracted file content. 404 if the file doesn't belong to the caller.",
    body: null,
    response: `{ "content": "Q3 board deck — revenue $1.32M, gross margin 41%..." }`,
  },
  {
    method: "DELETE", path: "/api/v1/files/{file_id}", group: "Files", auth: "user",
    desc: "Delete an uploaded file (DB row + file on disk).",
    body: null,
    response: `{ "status": "ok" }`,
  },
  {
    method: "GET", path: "/api/v1/files/{file_id}/download", group: "Files", auth: "user",
    desc: "Download the raw file. Returns a binary stream (`application/octet-stream`), not JSON.",
    body: null,
    response: `// binary response — Content-Disposition: attachment; filename="<original filename>"`,
  },

  // ── Ingestion ────────────────────────────────────────────────────────
  {
    method: "POST", path: "/api/v1/ingest/metrics", group: "Ingestion", auth: "user",
    desc: "Bulk-load KPI rows directly as JSON.",
    bodyType: "json",
    body: `{
  "data": [
    { "metric": "Revenue", "value": 125000, "period": "2025-06", "category": "Finance", "segment": "NA" }
  ],
  "source_name": "api",
  "replace": true
}`,
    response: `{ "status": "ingested", "rows": 1, "source": "api" }`,
  },
  {
    method: "POST", path: "/api/v1/ingest/webhook", group: "Ingestion", auth: "user",
    desc: "Generic webhook intake for external systems (e.g. StreamPulse, n8n). Strict schema enforcement per `schema_type`: `kpi_metrics` requires a list with `metric_name` + `value`; `knowledge_doc` requires `data.content` and is auto-categorized (LLM domain classification) and vector-indexed in the background.",
    bodyType: "json",
    body: `{
  "source": "streampulse",
  "schema_type": "kpi_metrics",
  "data": [ { "metric_name": "Revenue", "value": 125000, "period": "2025-06" } ]
}`,
    response: `// schema_type = "kpi_metrics"
{ "status": "success", "processed": 1, "type": "kpi_metrics" }

// schema_type = "knowledge_doc"
{ "status": "success", "message": "Document accepted for background processing and categorization", "type": "knowledge_doc" }`,
  },
  {
    method: "POST", path: "/api/v1/ingest/csv", group: "Ingestion", auth: "user",
    desc: "Upload a CSV of metrics (columns: metric_name, value, period, category, segment).",
    bodyType: "multipart",
    body: `// multipart/form-data
file: metrics.csv
source_name: "csv_upload"   // optional, defaults to "csv_upload"`,
    response: `{ "status": "ingested", "rows_inserted": 120, "filename": "metrics.csv" }`,
  },
  {
    method: "POST", path: "/api/v1/ingest/document", group: "Ingestion", auth: "user",
    desc: "Upload a document into the knowledge base. PDF text is extracted with pypdf; PNG/JPG images are read with Groq Vision (OCR + visual-element description); everything else is decoded as text. PII/secrets are redacted (SecurityScanner) before storage.",
    bodyType: "multipart",
    body: `// multipart/form-data
file: board_policy.pdf
category: "Finance"   // optional, defaults to "Misc"`,
    response: `{ "status": "ingested", "doc_id": "d41a...", "filename": "board_policy.pdf", "chars": 15234 }`,
  },
  {
    method: "POST", path: "/api/v1/ingest/audio", group: "Ingestion", auth: "user",
    desc: "Transcribe + analyze audio via a pluggable external processor (AUDIO_PROCESSOR_URL — a VoiceFlow instance or any compliant service implementing POST {url}/pipeline). 501 if unconfigured — never a fake transcript.",
    bodyType: "multipart",
    body: `// multipart/form-data
file: meeting.mp3
category: "Misc"          // optional
analysis_type: "meeting"  // optional`,
    response: `{ "status": "ingested", "doc_id": "d41a...", "filename": "meeting.mp3", "transcript": {...}, "analysis": {...} }`,
  },
  {
    method: "POST", path: "/api/v1/webhook/{source_name}", group: "Ingestion", auth: "public",
    desc: "HMAC-signed public ingestion endpoint for external systems that can't do an interactive JWT login (StreamPulse, a Kafka HTTP sink connector, n8n). No user session — authenticity comes entirely from the signature. 501 if INGEST_WEBHOOK_SECRET isn't configured; 401 on a missing/invalid signature.",
    bodyType: "json",
    body: `// Header: X-Signature-256: sha256=<hmac-sha256 hex of the raw body>
{ "source": "my_system", "schema_type": "kpi_metrics", "data": [...] }`,
    response: `{ "status": "success", "processed": 42, "type": "kpi_metrics" }`,
  },

  // ── KPIs ─────────────────────────────────────────────────────────────
  {
    method: "GET", path: "/api/v1/kpis", group: "KPIs", auth: "user",
    desc: "Query raw KPI rows, filtered by period/category/segment and further restricted server-side to the caller's role `data_access` categories.",
    query: "?period=2025-06&category=Finance&segment=NA",
    body: null,
    response: `{ "metrics": [ { "metric": "Revenue", "value": 125000, "period": "2025-06", "category": "Finance", "segment": "NA" } ], "count": 842 }`,
  },
  {
    method: "GET", path: "/api/v1/kpis/periods", group: "KPIs", auth: "user",
    desc: "List all distinct periods present in the KPI store.",
    body: null,
    response: `{ "periods": ["2025-01", "2025-02", "2025-03", "..."] }`,
  },
  {
    method: "GET", path: "/api/v1/kpis/metrics", group: "KPIs", auth: "user",
    desc: "List all distinct metric names.",
    body: null,
    response: `{ "metrics": ["Revenue", "Gross Margin", "Cash", "MRR", "Churn Rate"] }`,
  },
  {
    method: "GET", path: "/api/v1/kpis/categories", group: "KPIs", auth: "user",
    desc: "List all distinct KPI categories (business domains).",
    body: null,
    response: `{ "categories": ["Finance", "Growth", "People", "Operations", "IT", "ESG"] }`,
  },

  // ── Financial statements & Forecasting ──────────────────────────────
  {
    method: "POST", path: "/api/v1/financial/statement", group: "Financial & Forecasting", auth: "user",
    desc: "Generate an income statement, balance sheet, or cash flow statement for a period (FinancialStatementEngine). `statement_type` accepts income_statement/pl/P&L/profit_loss, balance_sheet/bs, or cash_flow/cf. Defaults to the latest available period.",
    bodyType: "json",
    body: `{ "company_id": null, "period": "2025-06", "statement_type": "income_statement" }`,
    response: `// income_statement — margins included
{
  "line_items": [
    { "item_name": "Revenue", "name": "Revenue", "amount": 1250000 },
    { "item_name": "Net Income", "name": "Net Income", "amount": 187500 }
  ],
  "margins": { "gross_margin": 0.41, "operating_margin": 0.22, "net_margin": 0.15 },
  "period": "2025-06",
  "statement_type": "income_statement"
}
// balance_sheet returns "ratios" instead of "margins"; cash_flow returns neither.`,
  },
  {
    method: "POST", path: "/api/v1/forecast", group: "Financial & Forecasting", auth: "user",
    desc: "Time-series forecast for one metric (ForecastEngine — regression trend + Monte Carlo–style confidence framing via explain_forecast). Sent as form fields, not JSON.",
    bodyType: "form",
    body: `// application/x-www-form-urlencoded
metric=Revenue&periods=3`,
    response: `{
  "metric": "Revenue",
  "historical": [ { "month_tag": "2025-04", "actual": 1180000 } ],
  "forecast": [ { "month_tag": "2025-07", "predicted": 1320000 } ],
  "explanation": { "r_squared": 0.91, "slope": 42000.0, "intercept": 980000.0 }
}`,
  },

  // ── Insights & Risk ──────────────────────────────────────────────────
  {
    method: "GET", path: "/api/v1/insights/health", group: "Insights & Risk", auth: "user",
    desc: "Composite business health index (0–100) from revenue growth, gross margin, cash position and opex efficiency.",
    body: null,
    response: `{ "score": 78.4, "label": "Stable", "growth": 4.2, "margin": 38.1, "cash_score": 62.0, "efficiency": 71.0 }`,
  },
  {
    method: "GET", path: "/api/v1/insights/risk", group: "Insights & Risk", auth: "user",
    desc: "Composite risk score (0–100, lower is better) from KPI volatility, anomaly count, revenue concentration and liquidity/execution proxies.",
    body: null,
    response: `{
  "score": 68.2, "label": "Moderate", "volatility": 12.4, "anomaly_count": 3,
  "volatility_score": 24.8, "anomaly_score": 30.0, "concentration_score": 41.2,
  "liquidity_score": 85.1, "execution_score": 76.0
}`,
  },
  {
    method: "GET", path: "/api/v1/insights/summary", group: "Insights & Risk", auth: "user",
    desc: "Board-ready executive summary: health + risk + key metrics, plus a generated narrative paragraph.",
    body: null,
    response: `{
  "health": { "score": 78.4, "label": "Stable" },
  "risk": { "score": 68.2, "label": "Moderate" },
  "key_metrics": { "revenue": 1250000, "gross_margin": 38.1, "cash": 420000 },
  "summary": "Revenue grew 4.2% QoQ with stable margins; risk exposure remains moderate driven by 3 flagged anomalies."
}`,
  },
  {
    method: "GET", path: "/api/v1/insights/anomalies", group: "Insights & Risk", auth: "user",
    desc: "Statistical anomaly detection over KPI history (z-score by default; the underlying `detect_anomalies` also supports IQR, isolation-forest and EWMA methods). Optionally scoped to one metric.",
    query: "?metric=Revenue",
    body: null,
    response: `{ "anomalies": [ { "period": "2025-05", "metric": "Revenue", "value": 89000, "z_score": -2.9, "is_anomaly": true } ], "count": 1 }`,
  },

  // ── HR / People ──────────────────────────────────────────────────────
  {
    method: "GET", path: "/api/v1/hr/summary", group: "HR", auth: "user",
    desc: "Workforce overview: headcount, turnover, satisfaction, tenure, open positions, training hours, cost per hire, absenteeism, plus department breakdown and trends.",
    body: null,
    response: `{
  "headcount": 342, "turnover_rate": 11.2, "satisfaction_score": 7.8, "avg_tenure_years": 3.1,
  "open_positions": 14, "training_hours_per_employee": 18.5, "cost_per_hire": 4200, "absenteeism_rate": 2.1,
  "departments": [ { "department": "Engineering", "headcount": 96, "satisfaction": 8.1, "turnover": 9.4, "avg_salary": 118000, "training_completion": 88.0 } ],
  "trends": [ { "period": "2025-06", "headcount": 340 } ]
}`,
  },
  {
    method: "GET", path: "/api/v1/hr/departments", group: "HR", auth: "user",
    desc: "Per-department HR analytics.",
    body: null,
    response: `{ "departments": [ { "department": "Sales", "headcount": 58, "satisfaction": 7.4, "turnover": 13.2, "avg_salary": 92000, "training_completion": 76.0 } ] }`,
  },
  {
    method: "GET", path: "/api/v1/hr/recruitment", group: "HR", auth: "user",
    desc: "Recruitment funnel metrics.",
    body: null,
    response: `{
  "open_positions": 14, "applications_received": 410, "interviews_scheduled": 62,
  "offers_extended": 9, "offers_accepted": 7, "avg_time_to_fill_days": 34.0, "cost_per_hire": 4200
}`,
  },
  {
    method: "GET", path: "/api/v1/hr/training", group: "HR", auth: "user",
    desc: "Training and development metrics.",
    body: null,
    response: `{
  "total_training_hours": 6320, "hours_per_employee": 18.5, "completion_rate": 84.0,
  "programs_active": 11, "satisfaction_with_training": 8.0, "budget_utilization": 71.5
}`,
  },
  {
    method: "GET", path: "/api/v1/hr/health", group: "HR", auth: "user",
    desc: "HR health score (0–100) computed from the workforce summary.",
    body: null,
    response: `{ "score": 74, "rating": "Stable", "color": "var(--ok)", "factors": { "retention": 26, "engagement": 22, "hiring_velocity": 14, "training": 12 } }`,
  },

  // ── Logistics ────────────────────────────────────────────────────────
  {
    method: "GET", path: "/api/v1/logistics/summary", group: "Logistics", auth: "user",
    desc: "Supply-chain overview: orders, on-time delivery, fill rate, lead time, inventory turnover, carrying cost, stockout/return rates, plus warehouse breakdown and trends.",
    body: null,
    response: `{
  "total_orders": 4820, "on_time_delivery_rate": 93.2, "fill_rate": 97.1, "avg_lead_time_days": 5.4,
  "inventory_turnover": 8.2, "carrying_cost": 210000, "stockout_rate": 1.8, "return_rate": 2.4,
  "shipping_cost_per_unit": 3.15, "warehouse_utilization": 78.0,
  "warehouses": [ { "warehouse": "DC-East", "utilization": 81.0 } ],
  "trends": [ { "period": "2025-06", "on_time_delivery_rate": 92.8 } ]
}`,
  },
  {
    method: "GET", path: "/api/v1/logistics/inventory", group: "Logistics", auth: "user",
    desc: "Inventory health metrics.",
    body: null,
    response: `{
  "total_sku_count": 1240, "inventory_value": 3400000, "days_of_supply": 28.0, "inventory_turnover": 8.2,
  "slow_moving_pct": 6.1, "overstock_pct": 4.3, "stockout_rate": 1.8, "accuracy_rate": 98.4,
  "categories": [ { "category": "Electronics", "value": 1200000 } ]
}`,
  },
  {
    method: "GET", path: "/api/v1/logistics/shipping", group: "Logistics", auth: "user",
    desc: "Shipping and delivery performance.",
    body: null,
    response: `{
  "shipments_today": 142, "shipments_month": 3980, "on_time_rate": 93.2, "damaged_rate": 0.6,
  "avg_transit_days": 3.1, "cost_per_shipment": 11.40,
  "carrier_performance": [ { "carrier": "FedEx", "on_time_rate": 95.1 } ]
}`,
  },
  {
    method: "GET", path: "/api/v1/logistics/suppliers", group: "Logistics", auth: "user",
    desc: "Supplier/vendor performance scorecards.",
    body: null,
    response: `{ "suppliers": [ { "supplier": "Acme Components", "quality_score": 96.0, "on_time_rate": 91.0, "lead_time_days": 12.0, "cost_variance": -2.1 } ] }`,
  },
  {
    method: "GET", path: "/api/v1/logistics/health", group: "Logistics", auth: "user",
    desc: "Logistics health score (0–100), weighted on on-time delivery among other factors.",
    body: null,
    response: `{ "score": 81, "rating": "Strong", "color": "var(--ok)", "factors": { "on_time_delivery": 28, "inventory": 20, "cost": 18, "quality": 15 } }`,
  },

  // ── IT ───────────────────────────────────────────────────────────────
  {
    method: "GET", path: "/api/v1/it/overview", group: "IT", auth: "user",
    desc: "IT operations overview: uptime, ticket backlog, MTTR, incidents, SLA compliance, security score, infra spend, DORA-lite deployment/change-failure rates.",
    body: null,
    response: `{
  "system_uptime": 99.92, "open_tickets": 38, "resolved_today": 21, "mttr_hours": 3.4,
  "incidents_month": 12, "critical_incidents": 1, "sla_compliance": 97.5, "security_score": 88.0,
  "server_count": 64, "cloud_spend": 42000, "deployment_frequency": 18.0, "change_failure_rate": 4.2,
  "infrastructure": [ { "component": "API Gateway", "utilization": 62.0 } ],
  "trends": [ { "period": "2025-06", "uptime": 99.9 } ]
}`,
  },
  {
    method: "GET", path: "/api/v1/it/tickets", group: "IT", auth: "user",
    desc: "Support ticket analytics with priority/category breakdowns.",
    body: null,
    response: `{
  "total_open": 38, "total_in_progress": 12, "total_resolved": 210, "avg_resolution_hours": 6.1,
  "first_response_hours": 0.8, "escalation_rate": 3.2, "satisfaction_score": 4.4,
  "by_priority": { "critical": 1, "high": 6, "medium": 18, "low": 13 },
  "by_category": [ { "category": "Access", "count": 14 } ]
}`,
  },
  {
    method: "GET", path: "/api/v1/it/security", group: "IT", auth: "user",
    desc: "Security posture dashboard.",
    body: null,
    response: `{
  "security_score": 88.0, "vulnerabilities_open": 22, "vulnerabilities_critical": 1, "patches_pending": 6,
  "phishing_attempts_blocked": 340, "failed_logins": 58, "compliance_score": 94.0,
  "last_pen_test_score": 91.0, "backup_success_rate": 99.8
}`,
  },
  {
    method: "GET", path: "/api/v1/it/infrastructure", group: "IT", auth: "user",
    desc: "Infrastructure utilization metrics.",
    body: null,
    response: `{
  "cpu_utilization": 61.0, "memory_utilization": 72.0, "disk_utilization": 54.0,
  "network_throughput_gbps": 3.2, "active_users": 812, "api_latency_ms": 118.0,
  "error_rate": 0.4, "uptime_pct": 99.92
}`,
  },
  {
    method: "GET", path: "/api/v1/it/devops", group: "IT", auth: "user",
    desc: "DORA-style DevOps metrics.",
    body: null,
    response: `{
  "deployment_frequency": 18.0, "lead_time_hours": 4.2, "change_failure_rate": 4.2, "mttr_hours": 3.4,
  "code_coverage": 82.0, "build_success_rate": 96.5, "releases_month": 9
}`,
  },
  {
    method: "GET", path: "/api/v1/it/health", group: "IT", auth: "user",
    desc: "IT operations health score (0–100).",
    body: null,
    response: `{ "score": 85, "rating": "Strong", "color": "var(--ok)", "factors": { "uptime": 30, "security": 24, "incidents": 18, "devops": 13 } }`,
  },

  // ── Operations ───────────────────────────────────────────────────────
  {
    method: "GET", path: "/api/v1/operations/summary", group: "Operations", auth: "user",
    desc: "Operations overview: OEE/efficiency, capacity, quality/defect rate, throughput, cycle time, downtime, unit cost, safety incidents, energy use, plus process-area breakdown and trends.",
    body: null,
    response: `{
  "overall_efficiency": 87.0, "capacity_utilization": 79.0, "quality_rate": 98.2, "defect_rate": 1.8,
  "throughput": 4200.0, "cycle_time": 11.4, "downtime_hours": 6.0, "cost_per_unit": 4.12,
  "on_time_completion": 94.0, "safety_incidents": 1, "energy_consumption": 18400.0, "waste_reduction": 12.0,
  "process_areas": [ { "area": "Assembly", "efficiency": 89.0 } ],
  "trends": [ { "period": "2025-06", "overall_efficiency": 86.5 } ]
}`,
  },
  {
    method: "GET", path: "/api/v1/operations/quality", group: "Operations", auth: "user",
    desc: "Quality control and assurance metrics.",
    body: null,
    response: `{
  "overall_quality_rate": 98.2, "defect_rate_ppm": 210.0, "first_pass_yield": 96.5, "rework_rate": 2.1,
  "customer_complaints": 4, "cost_of_quality": 18400.0, "inspection_pass_rate": 97.8, "nonconformance_count": 3
}`,
  },
  {
    method: "GET", path: "/api/v1/operations/production", group: "Operations", auth: "user",
    desc: "Production and manufacturing metrics.",
    body: null,
    response: `{
  "daily_output": 1420.0, "capacity_utilization": 79.0, "oee": 87.0, "planned_vs_actual": 96.0,
  "changeover_time": 22.0, "scrap_rate": 1.4, "maintenance_compliance": 93.0, "labor_productivity": 112.0
}`,
  },
  {
    method: "GET", path: "/api/v1/operations/safety", group: "Operations", auth: "user",
    desc: "Workplace safety metrics.",
    body: null,
    response: `{
  "total_incidents": 1, "lost_time_incidents": 0, "near_misses": 3, "days_without_incident": 46,
  "safety_training_completion": 97.0, "trir": 0.8, "severity_rate": 0.2
}`,
  },
  {
    method: "GET", path: "/api/v1/operations/health", group: "Operations", auth: "user",
    desc: "Operations health score (0–100).",
    body: null,
    response: `{ "score": 82, "rating": "Strong", "color": "var(--ok)", "factors": { "efficiency": 27, "quality": 22, "safety": 17, "cost": 16 } }`,
  },

  // ── Growth ───────────────────────────────────────────────────────────
  {
    method: "GET", path: "/api/v1/growth/summary", group: "Growth", auth: "user",
    desc: "SaaS growth metrics from the \"Growth\" KPI category: MRR/ARR, CAC, LTV, churn, plus a 12-point MRR trend and period-over-period trend %s.",
    body: null,
    response: `{
  "mrr": 108000.0, "arr": 1296000.0, "cac": 620.0, "ltv": 4200.0, "churn_rate": 2.1,
  "trends": [ { "period": "2025-06", "value": 104000.0 } ],
  "mrr_trend": 3.8, "cac_trend": -1.4, "churn_trend": 0.3
}`,
  },

  // ── ESG ──────────────────────────────────────────────────────────────
  {
    method: "GET", path: "/api/v1/esg/summary", group: "ESG", auth: "user",
    desc: "ESG scorecard from the \"ESG\" KPI category: overall score plus environment/social/governance sub-metrics and a per-period score/carbon trend.",
    body: null,
    response: `{
  "score": 72.0,
  "environment": { "carbon_emissions": 4200.0, "renewable_energy_pct": 38.0, "water_usage": 12000.0, "waste_diverted": 61.0 },
  "social": { "community_investment": 180000.0, "diversity_index": 0.71, "gender_pay_gap": 3.2 },
  "governance": { "board_diversity": 44.0, "ethics_training": 96.0, "supplier_compliance": 88.0, "data_privacy_incidents": 0 },
  "trends": [ { "period": "2025-06", "score": 71.0, "carbon": 4300.0 } ]
}`,
  },

  // ── Agent tools ──────────────────────────────────────────────────────
  {
    method: "GET", path: "/api/v1/agent/tools", group: "Agent Tools", auth: "user",
    desc: "List the tools a persona may invoke — its RBAC- and whitelist-enforced tool set. Defaults to the persona mapped to the caller's role; 403 if the requested persona isn't allowed for that role.",
    query: "?persona=cfo",
    body: null,
    response: `{
  "persona": "cfo",
  "allowed_tools": ["kpi_query", "forecast", "financial_statements", "budget_analysis"],
  "implemented": ["anomaly_detection", "budget_analysis", "data_analysis", "esg_metrics", "financial_statements", "forecast", "kpi_query", "market_analysis", "operations_metrics", "people_metrics", "report_generate", "risk_analysis", "supply_chain", "technology_metrics"]
}`,
  },
  {
    method: "POST", path: "/api/v1/agent/run", group: "Agent Tools", auth: "user",
    desc: "Invoke one whitelisted tool for a persona. Enforces both RBAC (role → persona) and the persona's own tool whitelist (tool must be in `allowed_tools`).",
    bodyType: "json",
    body: `{ "tool": "kpi_query", "persona": "cfo", "args": { "metric": "Revenue" } }`,
    response: `// shape depends on the tool invoked — always JSON-safe (NaN/Inf stripped)
{ "metric": "Revenue", "value": 1320000, "period": "2025-06" }`,
  },

  // ── Admin ────────────────────────────────────────────────────────────
  {
    method: "GET", path: "/api/v1/admin/users", group: "Admin", auth: "admin",
    desc: "List all users.",
    body: null,
    response: `{ "users": [ { "id": "8f1c...", "username": "cfo", "role": "cfo", "is_active": true, "language": "en", "created_at": "2026-01-04T00:00:00Z" } ] }`,
  },
  {
    method: "PUT", path: "/api/v1/admin/users/{user_id}", group: "Admin", auth: "admin",
    desc: "Update a user's role, active status, or preferred language.",
    bodyType: "json",
    body: `{ "role": "analyst", "is_active": true, "preferred_language": "fr" }`,
    response: `{ "status": "updated" }`,
  },
  {
    method: "GET", path: "/api/v1/admin/roles", group: "Admin", auth: "user",
    desc: "Return the full RBAC role table (ROLE_DEFINITIONS) — pages, actions, and data_access per role. Open to any authenticated user (used by the frontend to render role pickers).",
    body: null,
    response: `{
  "roles": {
    "admin": { "pages": ["*"], "actions": ["*"], "data_access": ["*"], "description": "Full system access" },
    "cfo": { "pages": ["dashboard", "analytics", "assistant", "forecasting", "data_hub", "settings"], "actions": ["read", "analyze", "forecast", "report", "financial_write", "ingest"], "data_access": ["Finance", "Growth"], "description": "Financial analysis and reporting" }
  }
}`,
  },
  {
    method: "GET", path: "/api/v1/admin/audit", group: "Admin", auth: "admin|risk",
    desc: "Read the audit trail (logins, ingests, admin actions).",
    query: "?limit=100",
    body: null,
    response: `{ "logs": [ { "username": "cfo", "action": "LOGIN", "detail": "User cfo logged in", "timestamp": "2026-08-09T09:58:00Z" } ] }`,
  },
  {
    method: "POST", path: "/api/v1/admin/seed", group: "Admin", auth: "admin",
    desc: "Re-seed the multi-domain KPI dataset (all 7 domains) if it's currently empty.",
    body: null,
    response: `{ "status": "seeded", "rows": 842 }`,
  },
  {
    method: "POST", path: "/api/v1/admin/scenario", group: "Admin", auth: "admin",
    desc: "Switch the database to a named benchmarking scenario (replaces all KPI data). Valid values: healthy, declining_financial, high_churn_crisis, operational_meltdown, talent_crisis, cybersecurity_breach, esg_compliance_failure. Synchronous — blocks until the switch finishes; on the larger scenarios this can exceed a proxy's request timeout (e.g. Cloudflare), so the frontend itself uses the async form below instead.",
    bodyType: "json",
    body: `{ "scenario": "declining_financial" }`,
    response: `{ "status": "success", "scenario": "declining_financial", "counts": { "kpi_rows": 842 } }`,
  },
  {
    method: "POST", path: "/api/v1/admin/scenario/async", group: "Admin", auth: "admin",
    desc: "Same switch as POST /api/v1/admin/scenario, but returns a job_id immediately and runs the switch in the background — poll GET /api/v1/admin/scenario/{job_id} for the result. This is what the Admin → Scenarios UI tab calls.",
    bodyType: "json",
    body: `{ "scenario": "declining_financial" }`,
    response: `{ "job_id": "3f9a1c2e-..." }`,
  },
  {
    method: "GET", path: "/api/v1/admin/scenario/{job_id}", group: "Admin", auth: "admin",
    desc: "Poll target for POST /api/v1/admin/scenario/async. status is pending | done | error.",
    body: null,
    response: `{ "job_id": "3f9a1c2e-...", "status": "done", "scenario": "declining_financial", "counts": { "kpi_rows": 842 } }`,
  },
  {
    method: "GET", path: "/api/v1/admin/scenario", group: "Admin", auth: "admin",
    desc: "Get the current scenario and the list of valid scenario names.",
    body: null,
    response: `{ "current_scenario": "healthy", "available_scenarios": ["healthy", "declining_financial", "high_churn_crisis", "operational_meltdown", "talent_crisis", "cybersecurity_breach", "esg_compliance_failure"] }`,
  },
  {
    method: "POST", path: "/api/v1/admin/cleanup", group: "Admin", auth: "admin",
    desc: "Wipe safe-to-delete data — chat history + audit trail. Keeps KPI/knowledge/seed data intact.",
    body: null,
    response: `{ "status": "cleaned", "deleted": { "sessions": 12, "messages": 214, "audit_logs": 340 } }`,
  },
  {
    method: "GET", path: "/api/v1/admin/vsdebug", group: "Admin", auth: "admin",
    desc: "Diagnostic endpoint: probes the vector store directly to localize why knowledge search may be returning nothing (dense-only hits vs. fused hybrid retrieval).",
    query: "?q=revenue",
    body: null,
    response: `{ "vs": "chroma", "count": 842, "dense_hits": 5, "dense_top": ["Q3 Board Deck", 0.834], "fused_hits": 5 }`,
  },
  {
    method: "POST", path: "/api/v1/admin/reindex", group: "Admin", auth: "admin",
    desc: "(Re)build the persistent vector store from the knowledge base — fixes an empty/stale index. `force=true` (default) drops and recreates the store at the current embedding dimension.",
    query: "?force=true",
    body: null,
    response: `{ "status": "reindexed", "docs": 842, "force": true }
// or, if VECTOR_STORE=memory (no persistent store configured):
{ "status": "skipped", "reason": "VECTOR_STORE=memory (no persistent store)" }`,
  },

  // ── Knowledge / RAG ──────────────────────────────────────────────────
  {
    method: "GET", path: "/api/v1/knowledge/search", group: "Knowledge & RAG", auth: "user",
    desc: "Direct access to the retrieval stack the copilot uses internally: persistent vector store (Chroma/pgvector/Qdrant) fused with BM25 + reranker when VECTOR_STORE is set, otherwise the in-process hybrid retriever.",
    query: "?q=revenue%20trend&n=5",
    body: null,
    response: `{ "results": [ { "title": "Q3 Board Deck", "content": "Revenue grew 4.2% quarter over quarter...", "score": 0.8421 } ], "query": "revenue trend", "count": 1 }`,
  },
  {
    method: "GET", path: "/api/v1/knowledge/stats", group: "Knowledge & RAG", auth: "user",
    desc: "Knowledge base indexing stats — total vs. embedded documents and distinct sources.",
    body: null,
    response: `{ "total_documents": 214, "embedded_documents": 214, "sources": ["upload", "webhook", "seed"] }`,
  },

  // ── Export ───────────────────────────────────────────────────────────
  {
    method: "POST", path: "/api/v1/data/export", group: "Export", auth: "user",
    desc: "Export data as CSV, JSON, XLSX, or a board-ready PDF report. `source_type` ∈ {kpis, spreadsheet, knowledge_base, conversation} (kpis and spreadsheet are the implemented paths). CSV/JSON come back as text; XLSX/PDF come back base64-encoded for direct client-side download.",
    bodyType: "json",
    body: `{ "source_type": "kpis", "format": "pdf", "source_name": null, "query": null }`,
    response: `{
  "status": "success",
  "export_id": "e91a...",
  "format": "pdf",
  "filename": "board_report.pdf",
  "encoding": "base64",
  "data": "JVBERi0xLjQKJ...",
  "download_url": "/api/v1/exports/e91a.../download"
}`,
  },
];

const GROUP_ORDER = [
  "System", "Auth", "Copilot", "Chat Sessions", "Files", "Ingestion", "KPIs",
  "Financial & Forecasting", "Insights & Risk", "HR", "Logistics", "IT", "Operations",
  "Growth", "ESG", "Agent Tools", "Admin", "Knowledge & RAG", "Export",
];

const GROUPS = GROUP_ORDER.map((name) => ({
  name,
  items: ENDPOINTS.filter((e) => e.group === name),
}));

// ─────────────────────────────────────────────────────────────────────────

function curlFor(ep: any) {
  const authLine = ep.auth === "public" ? "" : `  -H "Authorization: Bearer $TOKEN" \\\n`;
  const url = `${BASE_URL}${ep.path}${ep.query || ""}`;
  if (ep.bodyType === "multipart") {
    const fields = (ep.body || "")
      .split("\n")
      .filter((l: string) => l.includes(":") && !l.trim().startsWith("//"))
      .map((l: string) => {
        const [k] = l.split(":");
        return `  -F "${k.trim()}=@/path/to/file"`;
      })
      .join(" \\\n");
    return `curl -X ${ep.method} "${url}" \\\n${authLine}${fields || '  -F "file=@/path/to/file"'}`;
  }
  if (ep.bodyType === "form") {
    return `curl -X ${ep.method} "${url}" \\\n${authLine}  -H "Content-Type: application/x-www-form-urlencoded" \\\n  -d "metric=Revenue&periods=3"`;
  }
  if (ep.bodyType === "json") {
    return `curl -X ${ep.method} "${url}" \\\n${authLine}  -H "Content-Type: application/json" \\\n  -d '${(ep.body || "{}").replace(/\n/g, "").replace(/\s+/g, " ").trim()}'`;
  }
  if (ep.method === "WS") {
    return `# wscat (or any WebSocket client)\nwscat -c "${BASE_URL.replace("https://", "wss://")}${ep.path}"\n# then send: {"token":"$TOKEN"}  followed by chat-turn frames`;
  }
  return `curl "${url}"${ep.auth === "public" ? "" : ` \\\n${authLine.trimEnd()}`}`;
}

function CopyBtn({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <button
      onClick={() => { navigator.clipboard.writeText(text); setCopied(true); setTimeout(() => setCopied(false), 1400); }}
      className="btn btn-ghost btn-icon btn-sm"
      title="Copy"
      style={{ position: "absolute", top: 8, right: 8 }}
    >
      {copied ? <Check size={13} color="var(--ok)" /> : <Copy size={13} />}
    </button>
  );
}

function CodeBlock({ code }: { code: string }) {
  return (
    <div style={{
      position: "relative", background: "var(--bg-2)", border: "1px solid var(--border)",
      borderRadius: "var(--r)", padding: "12px 40px 12px 14px", fontFamily: "var(--font-mono)",
      fontSize: ".78rem", color: "var(--text-2)", whiteSpace: "pre-wrap", wordBreak: "break-word", lineHeight: 1.6,
    }}>
      <CopyBtn text={code} />
      {code}
    </div>
  );
}

function MethodBadge({ method }: { method: string }) {
  const color = METHOD_COLOR[method] || "var(--text-3)";
  return (
    <span style={{
      fontSize: ".68rem", fontWeight: 700, fontFamily: "var(--font-mono)",
      background: `color-mix(in srgb, ${color} 16%, transparent)`, color,
      borderRadius: 5, padding: "2px 7px", flexShrink: 0,
    }}>{method}</span>
  );
}

function AuthBadge({ auth }: { auth: string }) {
  const meta = AUTH_META[auth] || AUTH_META.user;
  const Icon = meta.icon;
  return (
    <span style={{
      display: "inline-flex", alignItems: "center", gap: 5, fontSize: ".74rem", fontWeight: 600,
      color: meta.color, background: `color-mix(in srgb, ${meta.color} 14%, transparent)`,
      borderRadius: "var(--r-pill)", padding: "3px 10px",
    }}>
      <Icon size={12} /> {meta.label}
    </span>
  );
}

export default function ApiDocs() {
  const [openGroups, setOpenGroups] = useState<Record<string, boolean>>({ System: true, Auth: true, Copilot: true });
  const [activeKey, setActiveKey] = useState(`${ENDPOINTS[0].method} ${ENDPOINTS[0].path}`);
  const [lang, setLang] = useState<"curl" | "response">("curl");

  const active = ENDPOINTS.find((e) => `${e.method} ${e.path}` === activeKey) || ENDPOINTS[0];

  const toggleGroup = (name: string) => setOpenGroups((s) => ({ ...s, [name]: !s[name] }));
  const select = (ep: any) => {
    setActiveKey(`${ep.method} ${ep.path}`);
    setOpenGroups((s) => ({ ...s, [ep.group]: true }));
  };

  return (
    <div>
      <div className="page-header">
        <div style={{ display: "flex", gap: 14, alignItems: "center" }}>
          <div className="kpi-icon-wrap" style={{ width: 44, height: 44, margin: 0, borderRadius: 13, background: "color-mix(in srgb, var(--primary) 16%, transparent)", color: "var(--primary)" }}>
            <Terminal size={22} />
          </div>
          <div>
            <h1 className="page-title" style={{ margin: 0 }}>API Reference</h1>
            <p className="page-subtitle">Persona-Aware AI Analytics &amp; RAG Copilot — REST + WebSocket API, {ENDPOINTS.length} endpoints across {GROUPS.length} groups</p>
          </div>
        </div>
      </div>

      <div className="kpi-grid" style={{ marginBottom: 18 }}>
        {[
          { icon: Globe, label: "Base URL", value: BASE_URL, color: "var(--primary)" },
          { icon: Shield, label: "Auth", value: "Bearer JWT (login / demo-login)", color: "var(--ok)" },
          { icon: Zap, label: "Format", value: "REST / JSON + 1 WebSocket", color: "var(--warn)" },
          { icon: BookOpen, label: "Interactive docs", value: "/api/docs (Swagger) · /api/redoc", color: "var(--accent)" },
        ].map(({ icon: Icon, label, value, color }) => (
          <div key={label} className="card" style={{ display: "flex", gap: 12, alignItems: "center", padding: "14px 16px" }}>
            <div className="kpi-icon-wrap" style={{ margin: 0, background: `color-mix(in srgb, ${color} 15%, transparent)`, color }}>
              <Icon size={16} />
            </div>
            <div style={{ minWidth: 0 }}>
              <div className="kpi-label truncate">{label}</div>
              <div style={{ fontSize: ".84rem", fontWeight: 600, wordBreak: "break-all" }}>{value}</div>
            </div>
          </div>
        ))}
      </div>

      <div className="card" style={{ marginBottom: 18, display: "flex", gap: 10, alignItems: "flex-start" }}>
        <Lock size={16} color="var(--warn)" style={{ flexShrink: 0, marginTop: 2 }} />
        <div style={{ fontSize: ".83rem", color: "var(--text-2)", lineHeight: 1.6 }}>
          <b style={{ color: "var(--text)" }}>Two auth layers.</b> Every route below except <code>/health</code>, the OpenAPI/docs
          routes, and everything under <code>/api/v1/auth/*</code> sits behind the same-origin internal-token middleware
          (<code>X-IntelAI-Internal-Token</code>) that the gateway attaches automatically for browser/API traffic — you don't
          set this yourself when calling through <code>{BASE_URL}</code>. On top of that, every endpoint marked{" "}
          <AuthBadge auth="user" /> also requires a <b>Bearer JWT</b> from <code>POST /auth/login</code> or{" "}
          <code>POST /auth/demo-login</code>, and endpoints marked <AuthBadge auth="admin" /> additionally require that JWT's
          role to be <code>admin</code> (or <code>risk</code> where noted).
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "280px 1fr", gap: 20, alignItems: "start" }}>
        {/* Sidebar — grouped endpoint list */}
        <div className="card" style={{ padding: 10, maxHeight: "calc(100vh - 340px)", overflowY: "auto", position: "sticky", top: 0 }}>
          {GROUPS.map((g) => (
            <div key={g.name} style={{ marginBottom: 2 }}>
              <button
                onClick={() => toggleGroup(g.name)}
                className="btn btn-ghost btn-sm"
                style={{ width: "100%", justifyContent: "space-between", display: "flex", fontWeight: 600, padding: "8px 10px" }}
              >
                <span style={{ display: "flex", alignItems: "center", gap: 6 }}>
                  {openGroups[g.name] ? <ChevronDown size={13} /> : <ChevronRight size={13} />}
                  {g.name}
                </span>
                <span style={{ color: "var(--text-3)", fontSize: ".72rem" }}>{g.items.length}</span>
              </button>
              {openGroups[g.name] && (
                <div style={{ display: "flex", flexDirection: "column", gap: 2, paddingLeft: 8, marginBottom: 6 }}>
                  {g.items.map((e) => {
                    const key = `${e.method} ${e.path}`;
                    const isActive = key === activeKey;
                    return (
                      <button
                        key={key}
                        onClick={() => select(e)}
                        style={{
                          display: "flex", alignItems: "center", gap: 8, textAlign: "left",
                          background: isActive ? "var(--primary-soft)" : "transparent",
                          border: isActive ? "1px solid var(--primary-line)" : "1px solid transparent",
                          borderRadius: 8, padding: "6px 8px", cursor: "pointer", width: "100%",
                        }}
                      >
                        <MethodBadge method={e.method} />
                        <span style={{ fontSize: ".76rem", fontFamily: "var(--font-mono)", color: isActive ? "var(--text)" : "var(--text-2)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                          {e.path}
                        </span>
                      </button>
                    );
                  })}
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Detail panel */}
        <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
          <div className="card">
            <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 10, flexWrap: "wrap" }}>
              <MethodBadge method={active.method} />
              <code style={{ fontSize: ".92rem" }}>{active.path}{(active as any).query || ""}</code>
              <span style={{ flex: 1 }} />
              <AuthBadge auth={active.auth} />
            </div>
            <p style={{ margin: 0, fontSize: ".86rem", color: "var(--text-2)", lineHeight: 1.6 }}>{active.desc}</p>
          </div>

          {active.body && (
            <div>
              <div style={{ fontSize: ".75rem", color: "var(--text-3)", marginBottom: 6, display: "flex", alignItems: "center", gap: 6 }}>
                <Code2 size={13} /> {(active as any).bodyType === "multipart" ? "Request (multipart form)" : (active as any).bodyType === "form" ? "Request (form-encoded)" : active.method === "WS" ? "Message frames" : "Request body"}
              </div>
              <CodeBlock code={active.body} />
            </div>
          )}

          <div>
            <div style={{ display: "flex", gap: 6, marginBottom: 8, alignItems: "center" }}>
              {(["curl", "response"] as const).map((l) => (
                <button
                  key={l}
                  onClick={() => setLang(l)}
                  className={`btn btn-sm ${lang === l ? "btn-primary" : "btn-secondary"}`}
                >
                  {l === "curl" ? "cURL" : "Sample response"}
                </button>
              ))}
            </div>
            <CodeBlock code={lang === "curl" ? curlFor(active) : active.response} />
          </div>
        </div>
      </div>
    </div>
  );
}
