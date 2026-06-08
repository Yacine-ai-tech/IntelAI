 
 
 
 
 
 
 
 
 
 
 
 
 
 
IntelAI
Freelance Income  →  Research Pipeline
Complete Strategy 2026  —  Version 2.0

⚑ 2026-06-09 — PROJECT SPLIT: "IntelAI" is the scoped product formerly named OmniIntelOS
(project #1 of 6: analytics + 9-persona RAG + GraphRAG-lite, one cloud deployment, null
dependency on the other projects). The original all-in-one, Palantir-style platform was
moved out to its own PRIVATE repo github.com/Yacine-ai-tech/OmniIntelOS with a dedicated
Studio (see that repo's PLATFORM_GUIDE.md). IntelAI's authoritative scope (KEEP/CUT) is in
STRATEGY.md §1.1; the code-level scope-down runs in Phase 1.
 
 
 
 
 
 
 
 
Author: Yacine
Date: May 2026
Supersedes: omniinteloscompletestrategy (v1, kept as backup)
For personal execution only
 
 
 
 
 
Table of Contents

PART I — THE THESIS AND THE CODEBASE
Section 1: What This Document Is (And Isn't)
Section 2: The Compound-Career Argument
Section 3: Real Codebase Inventory (Audited)
Section 4: What's Weak, What's Missing, What to Sharpen
Section 4.5: 2026 Stack Refresh — What's Leading And Why
  4.5.1 Frontier LLM Landscape
  4.5.2 RAG in 2026 — Beyond Naive Vector Search
  4.5.3 Embeddings in 2026
  4.5.4 Vector & Hybrid Stores
  4.5.5 Agent Frameworks in 2026
  4.5.6 Vision-LLM For Document/Image Understanding
  4.5.7 Speech Stack in 2026
  4.5.8 LLMOps + Observability in 2026
  4.5.9 Orchestration + Data Pipelines
  4.5.10 Research-Strong Stack Choices
  4.5.11 Pricing And Provider Strategy
  4.5.12 The Multi-Provider Abstraction Layer

PART II — THE SIX PROJECTS
Project 1: IntelAI Refactored
  1.3 What to Fix (Concrete Code Changes)
  1.4 NEW: Vertical Positioning Options
  1.5 Demo Recording Script
  1.6 Upwork Niches
  1.7 Research-Track Artifact
  1.10 2026 Stack Upgrade
Project 2: AgentKit — MCP Server + Multi-Agent Workflow
  2.1 Market Positioning
  2.3 Build Plan
  2.4 Open-Source Publication Checklist
  2.5 Demo Recording Script
  2.10 2026 Stack Upgrade
Project 3: DocIntel — Document Intelligence Pipeline
  3.4 LLM Extraction Layer (Expanded)
  3.10 2026 Stack Upgrade — Vision-First Pivot
Project 4: VoiceFlow — Speech-to-Intelligence
  4.3 Speaker Diarization (Revised)
  4.10 2026 Stack Upgrade
Project 5: RAGeval — LLMOps Observability
  5.1 Competitive Landscape
  5.4 The Drop-In SDK
  5.10 2026 Stack Upgrade
Project 6: StreamPulse — Real-Time Pipeline
  6.1 Positioning
  6.10 2026 Stack Upgrade
Cross-Project Synergy Summary

PART III — MULTI-CHANNEL DISTRIBUTION
Section 5: The 2026 Channel Mix (GitHub + Upwork + Loom ONLY)
Section 6: Upwork Strategy For 0-Review Freelancers
Section 7: Open-Source Strategy (PyPI, GitHub, DockerHub)
Section 8: Technical Writing Strategy (Draft In 2026, Publish In 2027)
Section 9: Cold Email + Communities
Section 10: LinkedIn 2027 — Light-Touch Prep Now

PART IV — THE RESEARCH DEGREE TRACK
Section 11: What Top Programs And Fellowships Want In 2026
Section 12: How This Plan Builds Research Capital
Section 13: One Preprint Per Year (Realistic Cadence)
Section 14: Research-Aligned Freelance Opportunities
Section 15: Reference Letter Strategy

PART V — EXECUTION (19 Weeks: Week 0 + 18 Build Weeks)
Section 16.0: Principles And The Decision To Build All Six
Section 16.1: Phase 0 — Repository Splitting (Week 0, Days 1-7)
Section 16.2: Phase 1 — IntelAI Foundation (Weeks 1-3, Days 8-27)
Section 16.3: Phase 2 — DocIntel (Weeks 4-6, Days 28-44)
Section 16.4: Phase 3 — AgentKit (Weeks 7-9, Days 45-61)
Section 16.5: Phase 4 — VoiceFlow (Weeks 10-12, Days 62-78)
Section 16.6: Phase 5 — RAGeval (Weeks 13-15, Days 79-96)
Section 16.7: Phase 6 — StreamPulse + Polish + Preprint (Weeks 16-18, Days 97-118)
Section 16.8: Weekly Metrics, Decision Gates, Cumulative Tracker
Section 17: Daily / Weekly Operating Rhythm
Section 18: Capacity Rules
Section 19: When To Pivot Or Quit

PART VI — INFRASTRUCTURE, TOOLING, AND COST REALITY
Section 20: Hosting Tiers (Railway, Fly.io, Local-Only)
Section 21: Pipeline Monitoring
Section 22: Tools You Need

PART VII — POSITIONING, PRICING, AND PROPOSALS
Section 23: Vertical Niching Within Each Project
Section 24: Upwork Profile (Refined)
Section 25: Pricing By Channel
Section 26: Six Proposal Templates
Section 26.5: Worked Case Study — Equipment Sourcing System ($5,000)

PART VIII — RISK AND REALITY CHECK
Section 27: Things That Will Go Wrong
Section 28: Milestone Expectations
Section 29: Common Failure Modes

PART IX — THE AI-AGENT BUILD PROMPT
Section 30: Complete Codebase Splitting Prompt (For Claude/Cursor)

PART X — THE 2027 MULTI-CHANNEL DEPLOYMENT PLAYBOOK
Section 31: The 2027 Launch Week (January Week 2)
Section 32: arXiv Submission Window
Section 33: The 2027 LinkedIn Posting Engine
Section 34: Personal Portfolio Site
Section 35: Cold Email Evolution In 2027
Section 36: Research-Program Outreach Calendar
Section 37: 2027 Quarterly Outcome Targets
Section 38: The Long Game (2028 And Beyond)

APPENDIX
Quick Reference Cards
Project Source Map
Channel × Project × Template Matrix
Glossary
 
PART I — THE THESIS AND THE CODEBASE
Section 1: What This Document Is (And Isn't)
Thesis in one paragraph: One codebase you already built (IntelAI, ~14k lines Python + ~5.5k lines React, verified by repo audit) becomes the seed for three parallel outcomes in 2026: (1) consistent Upwork freelance income at $65–95/hr, (2) an open-source + technical-writing footprint that powers your 2027 LinkedIn launch, (3) research-grade credentials (deployed systems + 1–2 arXiv preprints + reference relationships) that make you a competitive applicant for top AI research programs and fellowships in 2027–2028.

The mechanism: split the monorepo into 6 focused portfolio projects, ship them in a phased sequence (not parallel), distribute across multiple channels (Upwork is the income engine, GitHub + blog are the credibility engine, LinkedIn is the 2027 amplifier), and write one technical post per project that doubles as a workshop-paper draft.

This document is grounded in the actual code in this repo. Nothing here is aspirational fiction — every file reference and line count was verified by reading the repository on the date above.

What it is
A concrete, phased, 18-week execution plan to convert the IntelAI codebase into three compounding assets:
•	A freelance income pipeline on Upwork, generating $4k–$15k/month by month 6
•	An open-source + writing footprint that pre-loads your 2027 LinkedIn launch and makes your future direct-client outreach 5× more credible
•	Research credentials (deployed systems + preprints + relationships) for top research-degree and fellowship applications in late 2027

Every section is grounded in your actual repository state, your stated goals (2026 income on Upwork, 2027 expansion, eventual research degrees), and the realities of being a 0-review freelancer in the AI niche in 2026.
What it isn't
•	Not a get-rich-quick plan. First 30 proposals will likely get zero replies. This is normal. The plan accounts for it.
•	Not a parallel six-project blitz. You will build two or three projects in sequence, validate market signal, then expand. Building six things before the first paying client is a recipe for burning four months on the wrong niches.
•	Not a copy of every AI freelancer's playbook. Most freelancers don't have 14k lines of working Python they can point to. Your codebase justifies premium pricing and a research-track positioning from day one.
What Changed from v1
Issue	v1 Position	v2 Position
Timeline	12 weeks for 6 projects in parallel	19 weeks (Week 0 splitting + 18 build weeks), all six projects built sequentially, one repo published before the next starts
Repo extraction	Incremental, mid-plan	All 6 repos extracted upfront in Week 0 via single splitting prompt, validated against DocIntel first
Channel mix	Upwork-only	Upwork-primary, with parallel open-source + content + cold-email channels
Hosting cost	"Railway free tier sufficient"	$20–50/mo realistic; mixed Railway + Fly.io + local-only tiers
Research angle	None	Explicit research-credential track running in parallel
Competitive landscape	RAGeval framed as "rare"	Acknowledge Phoenix, LangSmith, TruLens, Helicone exist; differentiate as self-hosted/drop-in
Demo testing	"Record, upload, link"	Pre-launch to 5–10 trusted reviewers before going live
LLM extraction prep	"1–2 days" for DocIntel	1–2 weeks of prompt iteration with eval dataset
Section 2: The Compound-Career Argument
Why Split Rather Than Market the Platform Whole?
Upwork search works by keyword and niche specificity, not by ambition. A client posting "Build me a RAG pipeline for legal documents" searches for RAG, LangChain, ChromaDB, document Q&A — not "enterprise intelligence platform". One mega-platform marketed as "everything" competes with nothing.

But that argument from v1 stops at Upwork. The deeper compounding effect:

The same project (AgentKit, an MCP server) functions simultaneously as: (1) An Upwork portfolio entry — proves you can deliver AI agent work. (2) An open-source GitHub repo — proves you understand bleeding-edge protocols. (3) A blog post / arXiv-style preprint — "MCP Tool Design for Business Intelligence Agents". (4) A LinkedIn 2027 cornerstone — recorded demo + tutorial thread. (5) A research-app credential — applied work in agentic AI / tool use. Building it once gives you five compounding returns.

Why Income First, Research Second
You stated explicitly: 2026 is for earning and gaining experience on Upwork. Research-degree applications happen in late 2027 / early 2028. This sequencing is correct because:
•	Income reduces cognitive load. Once basic income is solved, research work compounds without survival pressure.
•	Industrial experience now has narrative weight in research applications. Top programs and labs in 2026 explicitly value "deployed AI systems" and "industrial AI engineering experience." This was less true pre-2022.
•	Reference letters from real clients are stronger than from short-term mentors. A CTO who paid you for 6 months and watched you ship is a more credible referee than a professor you took one class with.
•	You can't research what you haven't shipped. Your best research ideas in 2027 will come from problems you discover shipping in 2026. RAGeval exists in this plan precisely because you have observability data sitting unlogged in omnismart_chatbot.py.

So: build income in 2026, let the research track quietly compound in the background (one preprint by end of year, open-source published by month 6), and convert in 2027.
Section 3: Real Codebase Inventory (Audited)
Verified by reading the repo on the date of this document. Line counts are exact from wc -l.

Backend (Python) — ~14,000 lines
File	Lines	What It Does
src/api/server_v2.py	2,579	60+ endpoints, full RBAC, JWT, WebSocket chat
src/services/pg_store.py	1,669	50+ DB functions (KPIs, auth, sessions, audit)
src/services/omnismart_chatbot.py	1,658	9 personas, LangChain RAG, ChromaDB integration
src/services/advanced_chatbot.py	1,137	5 Groq patterns, agentic flows, Tavily search
src/integrations/dispatcher.py	605	Gmail/Sheets/n8n/TTS/Voice central dispatcher
src/services/data_ingestion_manager.py	558	CSV/JSON/PDF/Email/Sheets ingestion orchestration
src/services/realtime_pipeline.py	500	Domain classifier, async ingestion, 6-domain routing
src/integrations/n8n.py	445	n8n workflow integration
src/services/ocr_enhancement.py	428	PDF tables, forms, OCR via pdfplumber + tesseract
src/core/i18n.py	380	Full EN/FR translation system
src/core/jwt_auth.py	312	JWT + 9 role definitions, RBAC enforcement
src/core/config.py	311	Settings, RBAC enums, env management
src/models/pg_models.py	309	SQLAlchemy models for all entities
src/services/forecasting.py	276	LinearRegression + Monte Carlo forecasting
src/services/insights.py	275	Health index, 4 anomaly detection methods
src/services/hr.py	225	Headcount, turnover, department metrics
src/services/operations.py	204	Efficiency, utilization, cycle time
src/services/it_ops.py	213	Uptime, incidents, ticket metrics
src/services/logistics.py	210	On-time delivery, OTD, cycle time
src/services/financial.py	137	P&L, balance sheet, EBITDA
src/services/auth.py	180	Auth helpers, bcrypt, session management
src/integrations/camera.py	189	QR pairing + mobile upload flow
src/services/lazy_loader.py	160	Lazy model loading
src/core/performance.py	149	Latency tracking infrastructure
src/integrations/tts.py	135	TTS service wrapper
src/core/monitoring.py	122	Prometheus metrics emitter
src/core/pg_engine.py	114	DB engine and connection pool
src/services/voice/main.py	130	faster-whisper + edge-tts microservice
src/services/ocr/main.py	~80	Tesseract image OCR microservice
src/models/schemas.py	77	Pydantic request/response schemas
src/core/logger.py	54	Structured logging
src/core/crypto.py	32	Credential encryption

Frontend (React + Vite) — ~5,500 lines
19 pages, all routed in App.jsx. Highlights:
File	Lines	What It Does
frontend/src/pages/DataHubPage.jsx	356	Full ingestion control UI
frontend/src/pages/AdminPage.jsx	261	User management, roles, audit
frontend/src/pages/ScannerPage.jsx	256	Camera + file OCR upload
frontend/src/pages/ChatPage.jsx	238	Sessions, personas, TTS — but uses HTTP not WebSocket (bug)
frontend/src/pages/ITPage.jsx	230	Incidents, uptime, tickets
frontend/src/pages/AnalyticsPage.jsx	230	KPI browser — hand-coded SVG bar charts (needs Recharts)
frontend/src/pages/HRPage.jsx	210	Headcount, turnover, departments
frontend/src/pages/IntegrationsPage.jsx	210	Gmail, Sheets, ClickUp UI
frontend/src/pages/DashboardPage.jsx	199	KPIs, Health, Summary, Risk cards
frontend/src/pages/RiskPage.jsx	192	Risk score, anomalies
frontend/src/pages/OperationsPage.jsx	187	Efficiency, cycle time
frontend/src/pages/ESGPage.jsx	168	Carbon, safety, governance
frontend/src/pages/LogisticsPage.jsx	165	OTD, delivery metrics
frontend/src/pages/ForecastingPage.jsx	153	Metric select — lacks proper chart
frontend/src/pages/MonitoringPage.jsx	153	System health, Prometheus
frontend/src/pages/SettingsPage.jsx	133	Language, preferences
frontend/src/pages/LoginPage.jsx	112	Auth form
frontend/src/pages/FinancialPage.jsx	70	STUB — minimal content
frontend/src/pages/BulkDataPage.jsx	67	STUB — minimal content

Plus components (DataIngestionPanel, FloatingChat, PairingModal, Sidebar, FilePreview), full EN+FR translations (translations.js, ~800 lines), and a working design system (index.css, ~400 lines).
Infrastructure
Component	Detail
docker-compose.yml	13 services: postgres, fastapi, frontend, prometheus, grafana, n8n, ocr, voice, tunnels, devs
Dockerfile	Backend image (Python 3.10)
frontend/Dockerfile	nginx-served frontend image
src/services/ocr/Dockerfile.ocr	Standalone OCR microservice (Tesseract, :8001)
src/services/voice/Dockerfile.voice	Standalone voice microservice (Whisper, :8002)
monitoring/	Prometheus rules + Grafana provisioning/datasources
scripts/	10 ops shell scripts (start, stop, status, cleanup, etc.)
n8n_workflows/	4 pre-built n8n workflows (Gmail alert, Sheets push, Drive upload, ClickUp task)
tunnels/	Cloudflare tunnel configs (api.yml, frontend.yml, n8n.yml)
db/schema.sql	Full PostgreSQL schema
API Surface (60+ Endpoints)
Organized in functional groups:
AUTH       (5)   login, register, me, logout, status
CHAT       (10)  /chat HTTP, /ws/chat WebSocket, /personas, sessions CRUD, domain
KPI        (7)   /kpis, /kpis/periods, /kpis/metrics, /kpis/categories
                 /insights/health, /insights/risk, /insights/summary, /insights/anomalies
FORECAST   (1)   /forecast (LinearReg + Monte Carlo + CI bands)
INGESTION  (12)  /ingest/metrics, /ingest/csv, /ingest/document
                 /data/ingest, /data/export, /spreadsheets
                 /data-ingestion/ingest-all, /ingest-by-domains, /ingest-by-companies
                 /ingest-pdfs, /ingest-emails, /ingest-sheets
DOMAIN     (14)  /hr/summary, /hr/departments, /operations/health, /esg/summary,
                 /financial/statement + logistics, IT, risk endpoints
INTEGRATIONS (9) /integrations/{type}/data, /status, /connect,
                 /oauth/start, /oauth/callback, /disconnect
VOICE/OCR  (4)   /voice/transcribe, /voice/tts, /ocr/extract
CAMERA     (5)   /camera/pair, /camera/upload, /camera/sessions
ADMIN/MON  (8)   /admin/users, /admin/roles, /admin/audit, /admin/seed,
                 /monitoring/stats, /knowledge/search, /metrics, /health
Nine AI Personas (omnismart_chatbot.py lines 1048–1230)
Persona	Temp	Data Access	Allowed Tools
ceo	0.4	All 6 domains	kpi, forecast, report, market
cfo	0.2	Finance, Growth	kpi, forecast, financial_stmt, budget_analysis
cto	0.3	Operations, Finance, IT	kpi, risk, tech_metrics
coo	0.3	Operations, Growth, People	kpi, ops_metrics, supply_chain
chro	0.4	People, ESG	kpi, people_metrics, engagement_analysis
esg	0.3	ESG, Operations, People	kpi, esg_metrics, sustainability_rpt
risk	0.2	Finance, Operations	kpi, risk_analysis, alerts
analyst	0.3	All except admin	kpi, forecast, analysis, report
general	0.5	Finance, Growth	kpi, basic_query

Each persona has: custom system prompt (50-100 words of domain expertise), role-to-persona automatic mapping (CEO role → ceo persona), temperature tuned for executive (conservative) vs analyst (flexible), tool whitelist, and data scoping.
Synthetic Dataset (enhanced_synthetic_dataset/)
•	25,920 KPI records across 10 companies, 144 monthly periods, 5 domains
•	30 P&L / balance sheet JSON files (10 companies × 3 years)
•	3 sample invoice PDFs (for OCR testing)
•	5 sample images / charts (for vision)
•	10 email samples (for Gmail automation testing)
•	5 sheets exports (for Sheets automation testing)
•	30 n8n webhook payloads

Why this matters: every demo can show real data flowing through real pipelines. That's a credibility advantage 90% of freelancer portfolios lack.
Section 4: What's Weak, What's Missing, What to Sharpen
Weak — Needs Fixing Before Going Public
Issue 1: Charts Look Like a 2018 Prototype
This is the single highest-ROI fix in the entire repo. Recharts is in neither package.json nor the codebase. npm install recharts plus 2 days of integration transforms every demo screenshot. Do this first regardless of which projects you build.
AnalyticsPage.jsx and ForecastingPage.jsx use hand-coded SVG bars:
// Current code in AnalyticsPage.jsx — this is what clients see:
<div style={{
  flex: 1,
  height: `${(d.value / maxVal) * 100}%`,
  background: 'var(--primary)',
  borderRadius: '4px 4px 0 0',
}} />
Issue 2: WebSocket Streaming Chat Is Built but Not Wired
server_v2.py line 1553: @app.websocket("/api/v1/ws/chat") exists and works. frontend/src/pages/ChatPage.jsx: uses api.post('/chat') — the HTTP endpoint. Users wait 2–5 seconds for a full response when they could see it streaming token by token. Streaming feels 5× more impressive in demos. 1 day of work to wire it.
Issue 3: Tests Are Skeletal
tests/test_api.py: 25 lines, 2 test functions (health + login). tests/test_ui_playwright.py: 453 lines but mostly fixture skeletons. A CTO who clones the repo and runs pytest sees:
collected 2 items
PASSED tests/test_api.py::test_health
PASSED tests/test_api.py::test_login
That is a credibility problem on inspection. Expand to 25–30 API tests covering auth, RBAC, chat, KPI, insights, ingestion, monitoring, knowledge search.
Issue 4: README Misrepresents the Build
43,934-byte README with 26 appendices. Mentions "React frontend at localhost:5173 (when implemented)" but the frontend IS fully implemented. Claims features that need the full Docker stack but doesn't provide a one-command demo path. Replace with a clean <200-line README that matches what actually works, links to the live demo, and ships in 1 day.
Issue 5: Financial and Bulk Pages Are Stubs
FinancialPage.jsx: 70 lines — title and loading state only. BulkDataPage.jsx: 67 lines — title and empty state only. They appear in the router. Anyone navigating to them sees nothing. Either complete them (1–2 days each) or remove from the router entirely.
Issue 6 (NEW): No Prompt Eval Discipline
The chatbot's RAG quality is unknown. There's no eval set, no recorded groundedness scores, no regression test for retrieval relevance. If a client clones it and the chatbot hallucinates on their data, they'll walk away. Add a small eval set (20–30 manually-graded query/answer/source-doc triples in tests/rag_eval.jsonl) and a script to score current performance against it. This work directly feeds RAGeval (Project 5).
Missing — Net-New Builds Required
Missing 1: Persona-Routed RAG Evaluation Documentation
You have 9 personas. You don't have a single document showing why this design wins over a single-prompt chatbot. A client (and a research-app reader) wants to see the comparison: same query, 9 different persona responses, measurable differences in retrieval and groundedness. This is a 1-day write-up that becomes the basis for your first technical blog post and an eventual workshop paper.
Missing 2: Open-Source Publication of Any Module
Nothing in this repo is pip installable as a standalone library. The most natural candidates:
•	omnismart-personas — persona templates and resolution logic as a small library (consumable by any LangChain user)
•	rageval — the LLMOps observability package (Project 5)
•	agentkit-mcp — the MCP server module (Project 2)
Each of these published to PyPI with even 100 downloads a month is a stronger credential than 95% of freelancer portfolios. Plan to ship two by end of 2026.
Missing 3: Technical Writing
No blog posts. No arXiv preprints. No conference workshop submissions. Every other entry on a research-degree application has at least one. This is the gap. The plan calls for 6 technical posts in 2026 (one per project, one every 3 weeks), at least one of which gets reworked into an arXiv preprint by end of year.
Missing 4: Vertical Positioning
Your current README markets "IntelAI" to "enterprises in general." A Series A SaaS CTO and a healthcare CIO have completely different buying criteria. You'll close more deals positioning as "AI analytics for Series A SaaS" or "AI analytics for healthcare compliance" than as "enterprise OS for everyone." Pick one primary vertical and one secondary for each project, and write proposal templates targeted at each.
Missing 5: A Working LLMOps Loop
Your chatbot returns tokens_used and latency_ms but logs neither. The data needed for RAGeval already exists at the API boundary — it's just unpersisted. Build the storage layer in Phase 5.
Missing 6: A Research-App Narrative
Your eventual research application needs a coherent through-line. Plan that narrative now so each blog post and each project description reinforces it.
Suggested through-line: "persona-routed and role-scoped RAG as a production-deployable alignment pattern." Why this is good: it's interpretable, evaluable, falsifiable, and connects to current alignment-research interest in role/persona conditioning.
Section 4.5: 2026 Stack Refresh — What's Leading And Why
The v1 strategy was written against an early-2025 stack. The world has moved. This section maps the 2026 leading stack across the layers each of your six projects touches, and names the specific upgrades you should bake into the repos when Phase 0 splits the codebase.
The principle: lead with the strongest model in each tier, fall back to the fastest/cheapest, never lock to a single vendor. Multi-provider abstraction via LiteLLM (or equivalent) is now table stakes — clients ask about it in interviews.
4.5.1 The Frontier LLM Landscape (May 2026)
Tier 1 — Frontier reasoning (use for hard agent loops, executive personas, nuanced analysis):
Model	Strength	Typical Use
Claude Opus 4.7 (Anthropic)	Best agentic + coding + long-horizon reasoning	Planner agent, preprint co-author, executive RAG
Claude Sonnet 4.6	80% of Opus quality at 3× speed and ~5× cheaper	Default workhorse for production
Claude Haiku 4.5	Cheapest frontier; great for high-volume judge tasks	LLM-as-judge, classifiers
GPT-5 / o3-pro (OpenAI)	Strong for math, code, research benchmarks	Optional alternative for diversity
Gemini 2.5 Pro (Google)	Massive context (2M tokens), multimodal native	Long-document RAG, video understanding

Tier 2 — Fast inference for volume (when you don't need frontier quality):
Model / Provider	Strength	Typical Use
Groq Llama 3.3 70B	~500 tok/sec, $0.59/M out, industry-leading speed	High-volume RAG, per-query analysis
Cerebras Inference	~1800 tok/sec on Llama 3.3 (fastest available 2026)	Real-time UX, streaming chat
Together AI / Fireworks	Hosted open weights at scale	Custom fine-tunes, batch jobs
DeepSeek V3.5 / Qwen 3	Strong open-weights frontier	Local + Ollama tier, sovereign deployments

Tier 3 — Local / on-prem (Ollama + commodity GPU or even CPU):
Model	Runs On	Use Case
Llama 3.3 70B	1× A100 / 2× consumer GPU	Self-hosted dashboards
Qwen 3 32B	Single 4090 / mac M3	Embedded + tool use
Llama 3.2 Vision (11B)	1× 3090 / 4090	Vision-first OCR
Qwen 2.5-VL (7B)	Mac M2/M3, lighter GPU	Document AI on-prem
Gemma 3 (8B vision)	Mid-tier GPU	Vision classification
DeepSeek V3-lite	Apple M-series Macs	Latency-sensitive local

Practical implication: every project should default to Claude Sonnet 4.6 for quality-critical paths, Groq Llama 3.3 70B for high-volume paths, and ship with an Ollama path documented for clients who need local.
4.5.2 RAG in 2026 — Beyond Naive Vector Search
The "embed-and-cosine-similarity" RAG that defined 2023–24 is now considered the baseline. The leading patterns in 2026:

1. Hybrid retrieval (mandatory now)
Combine dense (embedding) with sparse (BM25) retrieval, then merge with Reciprocal Rank Fusion. Pure vector search fails on rare entities and exact-match queries (product codes, names).
QUERY → [dense search via bge-large] → top-50 docs
      ↘ [sparse search via BM25]    → top-50 docs
                                      ↓
                              RRF merge → top-30 docs
                                      ↓
                          [cross-encoder rerank: bge-reranker-v2-m3]
                                      ↓
                                  top-5 docs → LLM
2. Reranking with a cross-encoder
A bi-encoder embedding model is fast but loose. A cross-encoder reranker (BGE Reranker v2 m3, Cohere Rerank v3, Voyage Rerank-2) takes the top-50 retrieved docs and rescores them by attending to query+doc jointly. Adds 100-300ms, but precision@5 jumps 20-40%.
3. GraphRAG (Microsoft Research, 2024) — now production-deployable
Extracts entities and relationships during ingestion, builds a knowledge graph, performs graph-traversal queries for multi-hop reasoning. Critical for queries like "show me how X relates to Y across Z time periods" — which is exactly the executive analytics pattern in IntelAI.
4. Agentic RAG
Instead of retrieve-once-and-answer, an agent decides what to retrieve, when to re-query, and when to give up. Uses tool calling against the retrieval API as a sub-tool. LangGraph and CrewAI are the dominant frameworks. The latency cost is real (3-10x slower than naive RAG) but the quality on complex queries is dramatically better.
5. Long-context-as-RAG (controversial)
Gemini 2.5 Pro's 2M-token context and Claude Sonnet 4.6's 1M-token context let you skip retrieval entirely for many use cases — just paste the whole document. Cheaper than expected because of caching. Doesn't replace RAG for huge corpora, but reduces it for medium-sized knowledge bases.
6. ColBERT and late-interaction
Token-level scoring, not document-level. Better for fine-grained matching. Open-source via PyLate / RAGatouille. Niche but research-strong.

Practical implication: IntelAI and AgentKit should both upgrade from pure ChromaDB cosine similarity to hybrid retrieval + reranker. RAGeval should measure all of these as separate metrics.
4.5.3 Embeddings in 2026
Model	Open?	Tier	Use Case
OpenAI text-embed-3-large	No	Premium	Production default (3072d, $0.13/M tokens)
Voyage AI voyage-3-large	No	Premium	Best benchmark, $0.18/M
Cohere embed-english-v3	No	Premium	Strong for English
BGE-large-en-v1.5 (BAAI)	Yes	Self-host	Best open weights baseline (1024d, free)
BGE-M3	Yes	Self-host	Multilingual + multi-vector (1024d, free)
Jina embeddings v3	Yes	Self-host	Fast, code-friendly
Nomic embed v1.5	Yes	Self-host	Long-context (8k tokens)
all-MiniLM-L6-v2	Yes	Legacy	Still works, but older (384d, smaller, faster)
Practical implication: for IntelAI keep MiniLM as the fast lane, add BGE-large for the persona-grounded paths. For RAGeval, both should be recorded so you can compare embedding quality per metric.
4.5.4 Vector & Hybrid Stores
Store	Fit	Comment
Qdrant	Self-hosted, production-grade	2026 leader for self-host
Weaviate	Hybrid (vector + scalar) + graph	Strong for GraphRAG
LanceDB	Embedded, fast, file-based	Replacing Chroma for serverless
pgvector + Postgres	Unified with relational	Rising fast (one DB to operate)
Chroma	Simple, popular	Fine for prototype, not production
Pinecone	Managed	Premium, easy
Turbopuffer	Serverless cloud vector	New, fast-growing
Practical implication: IntelAI should add an "advanced" config that swaps ChromaDB for Qdrant or pgvector. The README should explicitly say "ChromaDB for dev, Qdrant for prod" — this resonates with senior buyers.
4.5.5 Agent Frameworks in 2026
Framework	Strength	When to Use
LangGraph	Graph-based, stateful, Anthropic-friendly	Production multi-step workflows
Claude Agent SDK	Anthropic-native, MCP-first	Anything Claude-centric (your strongest path)
CrewAI	Role-based multi-agent	Marketing differentiation, easier mental model
AutoGen	Microsoft, conversation-first	Enterprise/Microsoft buyers
DSPy	Programming, not prompting	Research credential, self-optimizing pipelines
OpenAI Swarm	Lightweight handoffs	Lean orchestration
Pydantic AI	Type-safe, model-agnostic	Production reliability (rising fast)
Practical implication: AgentKit goes from "MCP server + LangGraph" to "MCP server + LangGraph + Claude Agent SDK demo + CrewAI example." Three demos in one repo signals breadth. DSPy as a sub-experiment is your research credential.
4.5.6 Vision-LLM For Document/Image Understanding
This is the single biggest 2026 stack shift relevant to your projects. The old pipeline "OCR → text → LLM" is being replaced by "image → vision LLM → JSON" for almost every document and image task.
Model	Open?	Strength	Runs On
Claude Sonnet 4.6 Vision	No	Best for complex layouts	API only
GPT-4o Vision / GPT-5	No	Strong, broad use cases	API only
Gemini 2.5 Flash Vision	No	Cheapest premium tier	API only
Llama 3.2 Vision 11B/90B	Yes	Best open-weights	Ollama / vLLM
Qwen 2.5-VL 7B/72B	Yes	Best small open-weights	Ollama
Pixtral 12B (Mistral)	Yes	Document-focused	1× GPU
PaliGemma 2 (Google)	Yes	Lightweight, embedded	Mid-tier GPU
Gemma 3 Vision (8B)	Yes	Local-first design	Consumer GPU

Practical implication: DocIntel (Project 3) gets a major upgrade. Instead of pdfplumber → pytesseract → Groq text extraction, the modern pipeline is:
PDF → render page to image
    → choose route:
        Route A (premium): Claude Sonnet 4.6 Vision → structured JSON
        Route B (local):   Llama 3.2 Vision via Ollama → structured JSON
        Route C (legacy):  Tesseract OCR → text → LLM (fallback only)
    → validate JSON schema
    → store
4.5.7 Speech Stack in 2026
Layer	2025 Leader	2026 Leader
Self-host transcription	faster-whisper	WhisperX (faster-whisper + forced alignment + diarization) or NVIDIA NeMo Canary (research SOTA 2026)
Premium transcription API	Whisper API	Deepgram Nova-3 or AssemblyAI Universal-2 (both beat Whisper on streaming + diarization)
Diarization	pyannote.audio	pyannote 3.x (now production-stable) or NeMo built-in
Open TTS	edge-tts	Kokoro TTS (open, expressive) or Coqui XTTS v2
Premium TTS	ElevenLabs	ElevenLabs Multilingual v3 or OpenAI tts-1-hd
Real-time voice agents	n/a	OpenAI Realtime API (gpt-4o-realtime) or Hume EVI 2 (emotionally aware)
4.5.8 LLMOps + Observability in 2026
Tool	Strength	Watch For
Phoenix (Arize)	OSS leader, hosted optional	Strong defaults
Langfuse	Self-host or SaaS	Rich integrations
TruLens	OSS eval-first	Research community
Helicone	Proxy-style observability	Simplest install
OpenLLMetry	OpenTelemetry-native (Traceloop)	Standards path for enterprise
Weights & Biases Weave	GenAI-focused W&B	Strong for fine-tuning
LangSmith	LangChain-native	Tied to LangChain
Arize Copilot	Auto-debugging agent (2026 launch)	Frontier feature
Practical implication: RAGeval should explicitly support OpenLLMetry / OpenTelemetry export. That makes it interoperable with any enterprise observability stack. The differentiator stays: self-hosted, SQLite-default, persona-aware, drop-in decorator — but with OTEL export, enterprise buyers can route data to their existing platform.
4.5.9 Orchestration + Data Pipelines
Tool	Fit
Prefect 3	Modern Python, async-native, hybrid hosted+self-host
Dagster	Asset-based, strong for analytics
Airflow	Still industry default, especially in big-data shops
n8n	No-code/low-code, growing in SMB + AI-aggregator builds (Equipment Sourcing job explicitly uses n8n)
dlt	Declarative ingestion, "the Stripe of pipelines"
Estuary Flow	Real-time CDC, growing
Apache Kafka	Still the default for high-throughput streaming
Modal	Serverless Python for AI workloads (rising)
RunPod / Vast.ai	Cheap GPU for batch inference
Practical implication: StreamPulse should ship with first-class n8n integration (documented n8n node or webhook endpoint pattern) and an optional Prefect orchestration example. n8n is now in the job posts you'll respond to.
4.5.10 Research-Strong Stack Choices
If your goal is research-program admission, a few stack choices send disproportionate signal because they're the same tools researchers use:
Signal Tool	Why It Matters for Research Applications
DSPy	The "programming over prompting" paradigm; cited in 2025–26 papers; using it suggests methodological depth
LangGraph	The default agent framework in Anthropic-adjacent research; pairs with arXiv-citable agent papers
OpenLLMetry	Standards-track observability — researchers respect instrumentation discipline
pyannote.audio	Standard in speech research; using it signals you've read the literature
ColBERT / RAGatouille	Late-interaction retrieval is a research topic; engaging with it signals you read IR papers
W&B Weave	Researchers use W&B; "I tracked this with Weave" is a research-fluent phrase
LiteLLM	Engineering hygiene — multi-provider is now a hallmark of mature systems
You don't need every tool. But two or three of them sprinkled across the six repos signal: this person reads papers, ships systems, and respects the discipline.
4.5.11 Pricing And Provider Strategy (Realistic, 2026)
Model	Cost (per 1M tokens, in/out)	Use When
Claude Opus 4.7	$15 / $75	Critical reasoning
Claude Sonnet 4.6	$3 / $15	Default production
Claude Haiku 4.5	$0.80 / $4	Judge/classify
GPT-5	$10 / $40 (est.)	Alternative frontier
Gemini 2.5 Pro	$1.25 / $10	Long context
Groq Llama 3.3 70B	$0.59 / $0.79	High-volume speed
Together Llama 3.3 70B	$0.88 / $0.88	Batched API
DeepSeek V3.5	$0.27 / $1.10	Cheapest frontier (research-trained)
Local Llama 3.3 70B (Ollama)	$0 + electricity	Privacy / cost cap

A typical production IntelAI chat call might mix:
•	Claude Sonnet 4.6 for the persona-grounded synthesis (~$0.02 per call)
•	Groq Llama 3.3 70B for high-volume KPI summarization (~$0.001 per call)
•	Local Llama 3.2 Vision via Ollama for any document parsing ($0)
This three-tier mix is exactly what enterprise buyers want: top quality where it matters, fast/cheap for volume, local for privacy. Your README should describe it explicitly in the architecture section.
4.5.12 The Multi-Provider Abstraction Layer
In 2026, locking to a single provider is now a yellow flag in client interviews. Use LiteLLM (or instructor, or your own thin wrapper) to make every LLM call routable across providers via config:
# Everywhere you'd hardcode:
#   client = Groq(api_key=...)
#   response = client.chat.completions.create(model="llama-3.1-70b", ...)
#
# Use instead:
from litellm import acompletion
 
response = await acompletion(
    model=os.getenv("LLM_DEFAULT", "groq/llama-3.3-70b-versatile"),
    messages=[...],
    response_format={"type": "json_object"},
)
 
# Switch provider by env var:
#   LLM_DEFAULT=anthropic/claude-sonnet-4-6
#   LLM_DEFAULT=openai/gpt-5
#   LLM_DEFAULT=ollama/llama3.3

Every one of the six projects should adopt this pattern. The cost is one afternoon of refactor; the upside is that you can demo each project against Claude, Groq, GPT, and a local Ollama instance — and clients see this in the README and immediately trust you.


PART II — THE SIX PROJECTS (Refined + 2026 Stack Upgrades)
The technical content of the 6 projects from v1 was the strongest part of that document. It is preserved here with refinements based on the reality checks above.
PROJECT 1: IntelAI Refactored
AI Analytics Platform with Persona-Aware RAG Copilot
1.1 What it becomes
Stop marketing this as "enterprise operating system." Reframe as:
"A production-ready AI analytics backend with a 9-persona RAG copilot, multi-domain KPI intelligence, ML forecasting, and board-ready exports. 60 API endpoints. Role-based access. Bilingual (EN/FR)."
This description maps to five different Upwork search queries (RAG developer, FastAPI developer, BI developer, AI chatbot developer, AI integration engineer) and is concrete enough for a CTO to evaluate.
1.2 Architecture (What Actually Exists Today)
┌──────────────────────────────────────────────────────────────────┐
│                    BROWSER (React + Vite)                        │
│                                                                  │
│  Login  Dashboard  Chat  Analytics  Forecast  ESG  HR  Risk     │
│  IT     Logistics  Operations  Admin  DataHub  Scanner          │
│                    19 pages, ~5,500 lines                        │
└──────────────────────────┬───────────────────────────────────────┘
                           │ HTTP / WebSocket
                           │ /api/v1/*
┌──────────────────────────▼───────────────────────────────────────┐
│               FastAPI Backend — server_v2.py (2,579 lines)       │
│                                                                  │
│  Auth · Chat · Insights · Forecasting · Ingestion · Admin       │
│  9 personas · ChromaDB RAG · Groq LLaMA 3.1 · JWT + RBAC        │
└──────┬──────────────┬──────────────┬─────────────────────────────┘
       │              │              │
  ┌────▼────┐   ┌─────▼──────┐  ┌───▼──────┐
  │PostgreSQL│   │  ChromaDB  │  │  Groq    │
  │ KPIs/Auth│   │  Vectors   │  │  LLaMA   │
  └──────────┘   └────────────┘  └──────────┘
         │
  ┌──────▼──────────────────────────┐
  │   Microservices (Docker)        │
  │  omnitel-ocr:8001 (Tesseract)  │
  │  omnitel-voice:8002 (Whisper)  │
  └─────────────────────────────────┘
1.3 What to Fix (Concrete Code Changes)
Five fixes. Roughly 2 weeks of work total.
Fix A — Install and Wire Recharts (2 days)
cd frontend
npm install recharts
In frontend/src/pages/AnalyticsPage.jsx, replace the hand-coded SVG bars with LineChart. In ForecastingPage.jsx, use AreaChart with two Area components to show forecast values with confidence-interval shaded bands. In RiskPage.jsx, add a RadarChart for risk-component visualization. In DashboardPage.jsx, add 60px-tall sparkline LineCharts inside each KPI card. In FinancialPage.jsx, replace the stub with a BarChart of line-items from /api/v1/financial/statement.

ForecastingPage replacement (AreaChart with CI bands):
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
 
<ResponsiveContainer width="100%" height={300}>
  <AreaChart data={[
    ...(forecast.historical || []).map(h => ({ period: h.month_tag, actual: h.actual })),
    ...(forecast.data || []).map(f => ({
      period: f.month_tag,
      forecast: f.forecast,
      upper: f.upper_ci,
      lower: f.lower_ci,
    }))
  ]}>
    <defs>
      <linearGradient id="colorForecast" x1="0" y1="0" x2="0" y2="1">
        <stop offset="5%" stopColor="var(--primary)" stopOpacity={0.3}/>
        <stop offset="95%" stopColor="var(--primary)" stopOpacity={0.05}/>
      </linearGradient>
    </defs>
    <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
    <XAxis dataKey="period" tick={{ fill: 'var(--text-muted)', fontSize: 10 }} />
    <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 10 }} />
    <Tooltip contentStyle={{ background: 'var(--card)' }} />
    <Area type="monotone" dataKey="upper" stroke="none" fill="var(--primary)" fillOpacity={0.1} />
    <Area type="monotone" dataKey="lower" stroke="none" fill="var(--card)" fillOpacity={1} />
    <Area type="monotone" dataKey="actual" stroke="var(--success)" strokeWidth={2} fill="none" dot={{ r: 2 }} />
    <Area type="monotone" dataKey="forecast" stroke="var(--primary)" strokeWidth={2}
          strokeDasharray="4 2" fill="url(#colorForecast)" dot={{ r: 3 }} />
  </AreaChart>
</ResponsiveContainer>
 
<div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
  Shaded area = 95% confidence interval
</div>
Fix B — Wire WebSocket Streaming in ChatPage (1 day)
Replace the api.post('/chat') call with a WebSocket connection to /api/v1/ws/chat. Authenticate on onopen, accumulate chunks on onmessage, set streaming state to false on done.
// In ChatPage.jsx — replace the sendMessage function:
const wsRef = useRef(null)
const [isStreaming, setIsStreaming] = useState(false)
 
const connectWebSocket = useCallback(() => {
  const token = localStorage.getItem('access_token')
  const wsUrl = `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}/api/v1/ws/chat`
  
  const ws = new WebSocket(wsUrl)
  
  ws.onopen = () => {
    ws.send(JSON.stringify({ type: 'auth', token }))
  }
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)
    if (data.type === 'chunk') {
      setMessages(prev => {
        const updated = [...prev]
        const last = updated[updated.length - 1]
        if (last?.role === 'assistant' && last.streaming) {
          updated[updated.length - 1] = { ...last, content: last.content + data.content }
        }
        return updated
      })
    } else if (data.type === 'done') {
      setIsStreaming(false)
    }
  }
  
  wsRef.current = ws
  return ws
}, [])
Fix C — Complete FinancialPage.jsx (1 day)
70-line stub becomes a working page with statement-type select (income statement, balance sheet, cash flow), a BarChart of line items, and proper currency formatting.
import { useState, useEffect } from 'react'
import * as api from '../api'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
 
export default function FinancialPage() {
  const [statement, setStatement] = useState(null)
  const [stmtType, setStmtType] = useState('income_statement')
  const [loading, setLoading] = useState(false)
 
  const load = async () => {
    setLoading(true)
    try {
      const res = await api.post('/financial/statement', { statement_type: stmtType })
      setStatement(res.data)
    } catch(e) { console.error(e) }
    setLoading(false)
  }
 
  useEffect(() => { load() }, [stmtType])
 
  return (
    <div>
      <select value={stmtType} onChange={e => setStmtType(e.target.value)}>
        <option value="income_statement">Income Statement</option>
        <option value="balance_sheet">Balance Sheet</option>
        <option value="cash_flow">Cash Flow</option>
      </select>
      {statement?.line_items && (
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={statement.line_items}>
            <XAxis dataKey="name" tick={{ fontSize: 10 }} />
            <YAxis tickFormatter={v => `$${(v/1e6).toFixed(1)}M`} />
            <Tooltip formatter={v => `$${(v/1e6).toFixed(2)}M`} />
            <Bar dataKey="value" fill="var(--primary)" radius={[4,4,0,0]} />
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  )
}
Fix D — Expand Tests from 2 to 30+ (2 days)
# tests/test_api.py — expand to cover:
 
# AUTH (5 tests)
def test_health()            # exists
def test_login()             # exists
def test_login_wrong_password()
def test_register_viewer()
def test_get_me(auth_headers)
 
# CHAT (4 tests)
def test_chat_basic(auth_headers)
def test_chat_with_persona(auth_headers)
def test_chat_sessions(auth_headers)
def test_create_and_rename_session(auth_headers)
 
# KPIs (4 tests)
def test_get_kpis(auth_headers)
def test_get_kpi_periods(auth_headers)
def test_get_kpi_metrics(auth_headers)
def test_get_kpi_categories(auth_headers)
 
# INSIGHTS (4 tests)
def test_health_index(auth_headers)
def test_risk_score(auth_headers)
def test_executive_summary(auth_headers)
def test_anomalies(auth_headers)
 
# INGESTION (3 tests)
def test_ingest_valid_metrics(auth_headers)
def test_ingest_empty_data(auth_headers)
def test_forecast_endpoint(auth_headers)
 
# RBAC (4 tests)
def test_admin_endpoint_requires_admin(auth_headers)
def test_admin_endpoint_blocks_viewer()
def test_cfo_cannot_see_hr_data(auth_headers)
def test_analyst_no_admin_access(auth_headers)
 
# MONITORING (3 tests)
def test_monitoring_stats(auth_headers)
def test_knowledge_search(auth_headers)
def test_prometheus_metrics()
Fix E — Railway Deployment (1 day)
# railway.toml — place in project root
[build]
builder = "DOCKERFILE"
 
[deploy]
startCommand = "python -m uvicorn src.api.server_v2:app --host 0.0.0.0 --port $PORT --workers 1"
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "ON_FAILURE"
 
# Environment variables to set in Railway dashboard:
GROQ_API_KEY=gsk_...
SECRET_KEY=your-secure-random-secret-64-chars
ENVIRONMENT=production
ALLOW_INSECURE_DEFAULT_USERS=true    # For demo only
BOOTSTRAP_ADMIN_USERNAME=admin
BOOTSTRAP_ADMIN_PASSWORD=demo2026
CHROMA_DB_PATH=/app/chroma_db
Hosting note (NEW from v2): Railway free credit may not sustain this always-on. If costs trip $20/mo, move to Fly.io with a small shared-cpu-1x machine and an external Supabase free-tier Postgres. See Section 20.
1.4 NEW: Vertical Positioning Options
Pick a primary vertical to lead with on Upwork. Three good candidates:
Vertical	Why it works	Sample headline
Series A SaaS	KPIs already align (ARR, churn, headcount, runway). High Upwork volume.	"AI analytics + RAG copilot for Series A SaaS — built around SaaSOps KPIs and finance reporting cadence."
Healthcare KPI / Compliance	Long-tail demand, willing to pay premium for ESG-style domain coverage.	"Healthcare analytics with role-scoped AI copilot — clinical, ops, and compliance KPIs with audit logging."
ESG / Sustainability	Mandatory reporting wave in EU + parts of US drives demand. Your ESG domain is real.	"ESG reporting copilot — automated compliance reporting from raw KPI data with AI-generated executive summaries."

You don't have to commit to one. You can run three parallel proposal templates, each emphasizing the vertical-specific value. But the demo Loom video must show data that looks like the targeted vertical — generic "Company X" demo data is less compelling than "Acme SaaS, ARR $4.2M, churn 3.1%."

Generate three vertical-flavored datasets from your existing 25,920-record base. 1 day of work.
1.4.1 NEW: Prompt Eval Discipline
Before going public, build a small RAG eval set:
# tests/rag_eval.jsonl — 20-30 entries, each:
{
  "query": "What was our Q1 2025 churn rate?",
  "expected_keywords": ["churn", "Q1", "2025"],
  "expected_sources": ["finance_kpis_2025q1.csv"],
  "min_groundedness": 0.7
}
 
# Run weekly. If groundedness drops below threshold across
# more than 20% of the eval set, fix before shipping new chatbot changes.
# This work directly seeds Project 5 (RAGeval).
1.5 Demo Recording Script (3 minutes)
Time	Action
0:00–0:15	Login as CFO persona, land on Dashboard. Health Index 72/100. 6 KPI cards visible with sparkline trends.
0:15–0:45	Click Chat. Ask "Why is our gross margin declining this quarter?" Watch streamed response appear word by word. Source citations visible at bottom of response.
0:45–1:20	Switch persona to CHRO mid-session. Ask "What's our headcount trend and turnover risk?" Different response style, different data scope (no Finance data).
1:20–1:50	Navigate to Forecasting. Select "Revenue", click Run Forecast. AreaChart appears with confidence-interval shaded bands. Show Monte Carlo p10/p50/p90 scenario numbers.
1:50–2:20	Navigate to Risk page. RadarChart shows risk profile across domains. Click an anomaly in the table — drill-down to source data.
2:20–2:45	Dashboard → Export PDF button. PDF downloads. Open first page — health gauge, KPIs, narrative.
2:45–3:00	Log out. Log in as viewer role. Sidebar menu is restricted — admin tools hidden. Demonstrates role-based access control.
NEW from v2: Before going public with this video, share it with 3–5 trusted reviewers (peer freelancers, friends with tech backgrounds, your future self after sleep). Get feedback. Iterate. Most demos fail because they're optimized for the builder, not the buyer.
1.6 Upwork Niches for IntelAI
Niche	Search Terms	Your Angle
RAG / AI Chatbot Developer	RAG developer, LangChain developer, AI chatbot, ChromaDB	"9 specialized AI personas with role-based data scoping. ChromaDB RAG with source citations. Streaming responses. Production-deployed."
FastAPI / Python Backend Developer	FastAPI developer, Python API developer, async backend	"60-endpoint async FastAPI with JWT auth, RBAC, PostgreSQL, WebSocket streaming. 30+ tests."
Business Intelligence / Analytics Developer	BI developer, analytics dashboard, KPI dashboard	"Multi-domain KPI platform: Finance, HR, Ops, ESG. ML forecasting with confidence intervals. Board-ready exports."
AI Integration Engineer	AI integration, LLM integration, Groq developer	"Gmail/Sheets/ClickUp OAuth integration. n8n workflow automation. Production-deployed."
Vertical-Specific (rotate by demand)	SaaS analytics developer, healthcare reporting AI, ESG reporting	"[Vertical-specific value statement]"
1.7 Research-Track Artifact
"Persona-Routed RAG: Role-Based Data Scoping for Production AI Assistants" — A pattern for routing the same retrieval system through different persona-conditioned prompts and data filters. Demonstrated on a 9-persona business-intelligence assistant. Evaluated on retrieval relevance, groundedness, and adherence to role data boundaries. Open-source persona templates released as omnismart-personas.

This becomes: (1) A 2,000-word blog post (drafted 2026, published 2027). (2) A 6-page arXiv-style preprint (drafted 2026, submitted 2027). (3) A LinkedIn post in 2027. (4) A research-app credential ("I demonstrated this pattern in deployment").
1.10 2026 Stack Upgrade For IntelAI
Layer	Old	New
LLM (default)	Groq Llama 3.1 70B	Groq Llama 3.3 70B
LLM (reasoning)	—	Claude Sonnet 4.6
LLM (judge)	Groq	Claude Haiku 4.5
LLM (local option)	—	Ollama Llama 3.3 70B
Multi-provider	Hardcoded clients	LiteLLM router
Embeddings	all-MiniLM-L6-v2 only	+ BGE-large-en-v1.5
Retrieval	Cosine similarity only	Hybrid (dense + BM25 + RRF)
Reranking	None	BGE Reranker v2 m3
Knowledge graph	None	GraphRAG-lite (entities)
Vector store	ChromaDB	ChromaDB (dev) + Qdrant (prod)
Frontend visualization	Custom SVG	Recharts (Phase 1)
Streaming chat	REST polling	WebSocket (Phase 1)
Move 1 — Multi-provider LLM via LiteLLM (mandatory, low effort):
# src/services/llm_router.py (NEW FILE, ~40 lines)
from litellm import acompletion
import os
 
DEFAULT_MODEL    = os.getenv("LLM_DEFAULT",    "groq/llama-3.3-70b-versatile")
REASONING_MODEL  = os.getenv("LLM_REASONING",  "anthropic/claude-sonnet-4-6")
JUDGE_MODEL      = os.getenv("LLM_JUDGE",      "anthropic/claude-haiku-4-5")
LOCAL_FALLBACK   = os.getenv("LLM_LOCAL",      "ollama/llama3.3")
 
async def llm_call(messages, *, tier="default", **kwargs):
    model = {
        "default":   DEFAULT_MODEL,
        "reasoning": REASONING_MODEL,
        "judge":     JUDGE_MODEL,
        "local":     LOCAL_FALLBACK,
    }[tier]
    return await acompletion(model=model, messages=messages, **kwargs)
 
# Use:
# reasoning tier (CEO, CFO, CTO, Risk Manager): better nuance + depth
# default tier (Analyst, COO, CHRO, ESG, General): speed + cost
# judge tier: Claude Haiku for RAGeval integration (cheap + frontier)
Move 2 — Hybrid retrieval + reranker (medium effort, big quality jump):
# requirements.txt (new entries)
rank-bm25>=0.2.2
FlagEmbedding>=1.3.0       # for BGE reranker
 
# src/services/hybrid_retrieval.py (NEW FILE)
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
from FlagEmbedding import FlagReranker
 
class HybridRetriever:
    def __init__(self):
        self.embedder = SentenceTransformer("BAAI/bge-large-en-v1.5")
        self.reranker = FlagReranker("BAAI/bge-reranker-v2-m3", use_fp16=True)
        self.bm25 = None  # built per-collection
 
    def retrieve(self, query, docs, k=5, prefetch=50):
        # 1. Dense
        q_emb  = self.embedder.encode([query])
        d_emb  = self.embedder.encode(docs)
        dense  = cosine_top_k(q_emb, d_emb, prefetch)
        # 2. Sparse
        if not self.bm25:
            self.bm25 = BM25Okapi([d.split() for d in docs])
        sparse = self.bm25.get_top_n(query.split(), docs, n=prefetch)
        # 3. RRF merge
        merged = reciprocal_rank_fusion([dense, sparse], k=prefetch)
        # 4. Rerank
        pairs  = [[query, docs[i]] for i in merged]
        scores = self.reranker.compute_score(pairs, normalize=True)
        ranked = sorted(zip(merged, scores), key=lambda x: -x[1])[:k]
        return [docs[i] for i, _ in ranked]
 
# Add config flag: USE_HYBRID_RETRIEVAL=true
# Opt-in during Phase 1 polish, then enabled by default in production.
Move 3 — GraphRAG-lite for cross-domain queries (research-credential move):
# 1. During ingestion of each KPI record, extract entities:
#    {department, category, period, metric_name}
#    Store in: kpi_entities(record_id, entity_type, entity_value)
 
# 2. At query time:
#    a. Extract entities from the query (LLM call to Claude Haiku 4.5)
#    b. Find KPI records whose entities overlap with query entities
#    c. Use those records for retrieval
 
# 3. Combine with hybrid retrieval:
#    - graph results when query mentions >= 2 entities
#    - fall back to hybrid retrieval otherwise
 
# This is exactly the kind of work that becomes a workshop paper.
# RAGeval (Project 5) records the graph-vs-vector quality delta.
# You publish the finding as part of the 2027 preprint.
PROJECT 2: AgentKit
MCP Server + Multi-Agent Workflow Orchestration
2.1 Market Positioning (REFINED from v1)
v2 reframes: Primary channel = GitHub + technical blog + cold email (NOT Upwork). Secondary = Upwork (when MCP-tagged jobs appear, still thin as of May 2026). Tertiary = LinkedIn 2027.
Why? MCP demand on Upwork is real but concentrated in a handful of jobs per week. The bigger market is:
•	AI agencies and consultancies who'd hire you on retainer to build MCP servers for their clients. These come from cold email + LinkedIn, not Upwork postings.
•	Open-source visibility — a polished MCP server with stars and PyPI downloads is a hiring magnet for top labs. Anthropic, Cursor, Codeium, Replit all hire from OSS.
•	Research credibility — agentic AI is a hot research area. An open-source contribution here looks substantial on a research application.

So: build for the open-source-first audience. Polish accordingly. Treat Upwork as bonus, not primary.
2.2 Architecture
┌─────────────────────────────────────────────────────────────────────┐
│          AI AGENT CLIENTS (any MCP-compatible client)               │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │ Claude       │  │ Cursor IDE   │  │ Custom LangGraph Agent   │  │
│  │ Desktop      │  │              │  │ (Your 3-agent workflow)  │  │
│  └──────┬───────┘  └──────┬───────┘  └─────────────┬────────────┘  │
│         └─────────────────┴──────────────────────────┘              │
│                            │ MCP Protocol (stdio/HTTP)               │
└────────────────────────────┼────────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────────┐
│                    AgentKit MCP Server                               │
│                   (agentkit/mcp_server.py)                          │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    TOOL REGISTRY                             │   │
│  │                                                              │   │
│  │  query_kpis(domain, period_from, period_to)                 │   │
│  │  get_company_health(domain?)                                │   │
│  │  detect_kpi_anomalies(domain, method)                       │   │
│  │  forecast_metric(metric_name, periods)                      │   │
│  │  list_available_metrics()                                   │   │
│  │  get_executive_summary()                                    │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                 │                                    │
│  RESOURCES: kpi://Finance/latest, kpi://People/latest, etc.         │
│  PROMPTS:   monthly_executive_briefing, quarterly_review_prep       │
└─────────────────────────────────┼────────────────────────────────────┘
                                  │ Direct Python imports
┌─────────────────────────────────▼────────────────────────────────────┐
│                    IntelAI Backend                               │
│  pg_store · insights · forecasting · PostgreSQL + ChromaDB          │
└──────────────────────────────────────────────────────────────────────┘
                                  │
┌─────────────────────────────────▼────────────────────────────────────┐
│           3-AGENT LANGGRAPH WORKFLOW                                 │
│  PLANNER (Sonnet 4.6) ──▶ ANALYST (Groq) ──▶ REPORTER (Sonnet 4.6) │
│                                                                      │
│  Input:  "Why is our company health declining?"                      │
│  Output: Structured report with numbers, root cause, recommendations │
└──────────────────────────────────────────────────────────────────────┘
2.3 Build Plan
Repository: agentkit/

Extract these files from IntelAI (copy, don't move):
Source (IntelAI)	Destination (AgentKit)
src/services/pg_store.py	agentkit/services/pg_store.py
src/services/insights.py	agentkit/services/insights.py
src/services/forecasting.py	agentkit/services/forecasting.py
src/core/config.py	agentkit/core/config.py
src/core/logger.py	agentkit/core/logger.py
src/core/pg_engine.py	agentkit/core/pg_engine.py
db/schema.sql	agentkit/db/schema.sql

New files to create:
•	mcp_server.py — FastMCP server with 6 tools + resources + prompts
•	workflow.py — LangGraph 3-agent pipeline (Planner → Analyst → Reporter)
•	agents/planner.py, agents/analyst.py, agents/reporter.py
•	demos/claude_agent_sdk_demo.py — Claude Agent SDK orchestration
•	demos/crewai_demo.py — CrewAI crew (Researcher / Analyst / Reporter)
•	research/dspy_experiment.py — DSPy compilable pipeline
•	demo/demo_notebook.ipynb — Jupyter demo
•	demo/claude_desktop_config.json — drop-in config
•	tests/test_mcp_tools.py
Complete mcp_server.py Implementation
"""
AgentKit — MCP Server for Business Intelligence
 
Exposes IntelAI analytics as MCP tools compatible with:
- Claude Desktop
- Cursor IDE  
- Any LangChain/LangGraph agent
"""
from __future__ import annotations
import sys, os
from pathlib import Path
from typing import Optional
 
OMNI_PATH = Path(__file__).parent.parent / "IntelAI"
if OMNI_PATH.exists():
    sys.path.insert(0, str(OMNI_PATH))
 
from dotenv import load_dotenv
load_dotenv()
 
from fastmcp import FastMCP
from services.pg_store import (
    get_kpi_metrics, get_available_metrics,
    get_available_categories, get_available_periods,
)
from services.insights import (
    compute_health_index, detect_anomalies,
    compute_risk_score, generate_executive_summary,
)
from services.forecasting import ForecastEngine
 
mcp = FastMCP(
    name="AgentKit Business Intelligence",
    instructions="""
    You have access to real business intelligence data from IntelAI.
    The data covers 7 domains: Finance, Growth, Operations, People (HR),
    ESG, IT, and Logistics. 144 monthly periods (2015–2026). 10 companies.
    Use these tools to answer business questions with real data.
    """
)
 
@mcp.tool()
def query_kpis(
    domain: str = "Finance",
    period_from: Optional[str] = None,
    period_to: Optional[str] = None,
    metric_filter: Optional[str] = None,
    limit: int = 50
) -> dict:
    """Query business KPIs from the IntelAI database.
    
    Args:
        domain: Finance | Growth | Operations | People | ESG | IT | Logistics
        period_from: Start period YYYY-MM (e.g., "2025-01"). Optional.
        period_to: End period YYYY-MM (e.g., "2025-12"). Optional.
        metric_filter: Filter to a specific metric name. Optional.
        limit: Max rows to return (default 50, max 500).
    """
    import pandas as pd
    df = get_kpi_metrics(category=domain)
    if df.empty:
        return {"kpis": [], "count": 0, "domain": domain}
    if period_from:
        df = df[df["period"] >= period_from]
    if period_to:
        df = df[df["period"] <= period_to]
    if metric_filter:
        df = df[df["metric"].str.lower().str.contains(metric_filter.lower())]
    df = df.head(limit)
    return {
        "kpis": df.to_dict(orient="records"),
        "count": len(df),
        "domain": domain,
        "periods_covered": sorted(df["period"].unique().tolist()),
        "metrics_available": sorted(df["metric"].unique().tolist()),
    }
 
 
@mcp.tool()
def get_company_health(domain: Optional[str] = None) -> dict:
    """Calculate the company health index (0-100) with breakdown by factor.
    
    Returns: score, label (Excellent/Moderate/At Risk), factors, interpretation.
    """
    df = get_kpi_metrics(category=domain)
    if df.empty:
        return {"score": 0, "label": "No Data", "factors": {}}
    health = compute_health_index(df)
    score = health.get("score", 0)
    health["interpretation"] = (
        "Company is performing well." if score >= 80 else
        "Moderate health. Monitor flagged areas." if score >= 60 else
        "Stress indicators. Immediate review recommended." if score >= 40 else
        "Critical issues detected. Urgent intervention needed."
    )
    return health
 
 
@mcp.tool()
def detect_kpi_anomalies(
    domain: str = "Finance",
    method: str = "zscore",
    threshold: float = 2.5
) -> dict:
    """Detect statistical anomalies in KPI data.
    
    Args:
        domain: Business domain to analyze
        method: zscore | iqr | isolation_forest | ewma
        threshold: Sensitivity (default 2.5 sigma for zscore)
    """
    df = get_kpi_metrics(category=domain)
    if df.empty:
        return {"anomalies": [], "count": 0, "method": method}
    anomalies = detect_anomalies(df, method=method)
    if isinstance(anomalies, list):
        top = sorted(anomalies, key=lambda x: abs(x.get("zscore", 0)), reverse=True)[:10]
    else:
        top = []
    return {
        "anomalies": anomalies if isinstance(anomalies, list) else [],
        "count": len(anomalies) if isinstance(anomalies, list) else 0,
        "method": method, "top_anomalies": top, "domain": domain,
    }
 
 
@mcp.tool()
def forecast_metric(
    metric_name: str,
    periods: int = 6,
    confidence_level: float = 0.95
) -> dict:
    """Generate ML-powered time-series forecast with confidence intervals."""
    import pandas as pd
    df = get_kpi_metrics()
    metric_df = df[df["metric"].str.lower() == metric_name.lower()].copy()
    if metric_df.empty:
        metric_df = df[df["metric"].str.lower().str.contains(metric_name.lower())].copy()
    if metric_df.empty:
        return {"error": f"Metric '{metric_name}' not found",
                "available_metrics": sorted(df["metric"].unique().tolist())[:20]}
    chart_df = metric_df.rename(columns={"period": "month_tag", "value": "actual"})
    engine = ForecastEngine()
    result = engine.time_series_forecast(chart_df, periods=periods,
                                          confidence_level=confidence_level)
    if result.empty:
        return {"error": "Insufficient data for forecast"}
    return {
        "metric": metric_name, "periods_requested": periods,
        "confidence_level": confidence_level,
        "forecast": result.to_dict(orient="records"),
        "trend_direction": "increasing" if result["forecast"].iloc[-1] > result["forecast"].iloc[0] else "decreasing",
    }
 
 
@mcp.tool()
def list_available_metrics(domain: Optional[str] = None) -> dict:
    """List all available KPI metrics with their domains and period range."""
    metrics = get_available_metrics()
    categories = get_available_categories()
    periods = get_available_periods()
    return {
        "metrics": metrics, "domains": categories,
        "period_range": {
            "earliest": min(periods) if periods else None,
            "latest": max(periods) if periods else None,
            "total_periods": len(periods)
        },
        "total_metrics": len(metrics),
    }
 
 
@mcp.tool()
def get_executive_summary() -> dict:
    """Generate an AI executive summary of the current business state."""
    df = get_kpi_metrics()
    if df.empty:
        return {"summary": "No data available."}
    health = compute_health_index(df)
    summary = generate_executive_summary(df)
    return {
        "summary": summary, "health": health,
        "data_coverage": {
            "domains": sorted(df["category"].unique().tolist()) if "category" in df.columns else [],
            "total_kpis": len(df),
            "latest_period": df["period"].max() if "period" in df.columns else None,
        }
    }
 
 
# MCP Resources (2026 best practice)
@mcp.resource("kpi://Finance/latest")
def finance_latest():
    """Latest Finance KPI snapshot as a stable URI."""
    return query_kpis("Finance", limit=20)
 
 
# MCP Prompts (reusable templates)
@mcp.prompt("monthly_executive_briefing")
def monthly_briefing_prompt():
    """Standard monthly executive briefing prompt."""
    return [
        {"role": "user", "content": "Generate the monthly executive briefing.
         Include: health score trend, top 3 risks, top 3 opportunities, and
         recommended board-level actions for next month."}
    ]
 
 
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--transport", default="stdio", choices=["stdio", "http"])
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    if args.transport == "http":
        mcp.run(transport="http", port=args.port)
    else:
        mcp.run()  # stdio mode for Claude Desktop
2.4 Open-Source Publication Checklist
This is the primary distribution for AgentKit. Treat it accordingly.

Before push to public:
☐  README is clear, concise, has architecture diagram
☐  LICENSE: MIT or Apache 2.0 (pick one, stick with it)
☐  .env.example with placeholders, no secrets
☐  Tests pass — visible CI badge in README
☐  A 90-second Loom demo embedded at top of README
☐  One-paragraph "what this is" elevator pitch
☐  Quick-start that works on a fresh machine in 5 minutes

After push:
☐  Submit to relevant Awesome lists (awesome-mcp, awesome-llm-agents)
☐  Post in MCP-related Discord servers, ML Twitter, r/LocalLLaMA
☐  Cross-post the demo video to YouTube (organic search traffic)

Stretch goal (do this by end of 2026):
☐  Publish pip install agentkit-mcp package to PyPI
2.5 Demo Recording Script (90 seconds)
Time	Action
0:00–0:10	Open Claude Desktop. Type: "What tools do you have available?"
0:10–0:20	Claude lists: query_kpis, get_company_health, detect_kpi_anomalies, etc.
0:20–0:35	Type: "What's our company health score and top 3 risks?" Watch Claude call get_company_health() — show real score. Claude calls detect_kpi_anomalies() — show real anomalies.
0:35–0:60	Type: "Generate a full executive report on why our company health might be declining." Watch Claude call multiple tools sequentially. See actual data flowing through tools.
0:60–1:15	Switch to terminal. Run: python workflow.py Show 3-agent execution logs.
1:15–1:30	Show the structured executive report output.
2.7 Research-Track Artifact
"MCP Tool Design Patterns for Business Intelligence Agents" — A taxonomy of MCP tools by access pattern (read-only vs mutating), by domain (analytical vs operational), and by latency profile. Demonstrated on a 6-tool MCP server backed by PostgreSQL. Recommendations for tool granularity, error handling, and audit logging. Suitable for workshop submission.
2.10 2026 Stack Upgrade For AgentKit
Layer	Old	New
LLM (planner)	Groq	Claude Sonnet 4.6
LLM (analyst)	Groq	Groq Llama 3.3 70B
LLM (reporter)	Groq	Claude Sonnet 4.6
LLM (local fallback)	—	Ollama Llama 3.3 70B
Multi-provider	Single client	LiteLLM
Agent frameworks	LangGraph only	LangGraph + Claude Agent SDK + CrewAI + DSPy (research)
MCP feature surface	Tools only	Tools + Resources + Prompts
Research artifact	None	DSPy-compiled pipeline benchmarked
Claude Desktop integration config:
# ~/.config/Claude/claude_desktop_config.json (Linux)
# ~/Library/Application Support/Claude/claude_desktop_config.json (macOS)
{
  "mcpServers": {
    "business-intelligence": {
      "command": "python",
      "args": ["/absolute/path/to/agentkit/mcp_server.py"],
      "env": {
        "POSTGRES_URL": "postgresql://omniintel:change_me@localhost:5432/intelai",
        "LLM_DEFAULT": "groq/llama-3.3-70b-versatile",
        "LLM_REASONING": "anthropic/claude-sonnet-4-6",
        "GROQ_API_KEY": "gsk_your_key",
        "ANTHROPIC_API_KEY": "sk-ant-your_key"
      }
    }
  }
}
PROJECT 3: DocIntel
Intelligent Document Processing Pipeline
3.1 Why This Wins Consistently
Document processing is the most volume-consistent AI niche on Upwork. Every industry has the same problem: piles of PDFs that need to become structured data. The 2026 upgrade: clients no longer want "extract text from PDF." They want structured JSON with confidence scores, ready to push to their database or ERP.

Your src/services/ocr_enhancement.py (428 lines) plus src/services/ocr/main.py (~80 lines) plus src/integrations/camera.py (189 lines) already contain the core of a standalone product.
3.2 Architecture
┌──────────────────────────────────────────────────────────────┐
│                  DocIntel — Document AI API                  │
│                                                              │
│  POST /extract           Full pipeline (upload → JSON)      │
│  POST /extract-tables    PDF table extraction only           │
│  POST /classify          Document type detection             │
│  POST /classify-image    Vision-first object classification  │
│  POST /extract-llm       LLM-enhanced structured extraction  │
│  POST /batch/upload      Upload 1-100 files → job_id         │
│  GET  /batch/{job_id}    Poll async batch status             │
│  GET  /batch/{job_id}/results  Download results JSON/CSV     │
│  GET  /health            Health check                        │
└──────────────────────────────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                Document Processing Engine                        │
│                                                                  │
│  STAGE 1: File Intake                                           │
│    Detect: PDF native | PDF scanned | Image | DOCX              │
│                                                                  │
│  STAGE 2: Pre-Processing (OpenCV if available)                  │
│    Deskew → Denoise → Threshold → Enhance contrast              │
│                                                                  │
│  STAGE 3: Extraction — choose route:                            │
│    Route A (VISION_PREMIUM): Claude Sonnet 4.6 Vision → JSON   │
│    Route B (VISION_LOCAL):   Ollama Llama 3.2 Vision → JSON    │
│    Route C (OCR_FALLBACK):   Tesseract → text → LLM            │
│                                                                  │
│  STAGE 4: Classification                                        │
│    invoice | contract | receipt | form | medical | financial     │
│                                                                  │
│  STAGE 5: LLM-Enhanced Field Extraction                        │
│    Invoice → {vendor, total, items, due_date, invoice_no}       │
│    Contract → {parties, effective_date, key_clauses, term}      │
│    Medical → {patient_id, diagnosis, medications, dates}        │
│                                                                  │
│  STAGE 6: Output                                                │
│    JSON with confidence scores | CSV export | Webhook callback   │
└──────────────────────────────────────────────────────────────────┘
3.10 2026 Stack Upgrade — The Vision-First Pivot
This is the most important stack upgrade across all six projects. The v1 pipeline (pdfplumber → pytesseract → Groq text extraction) is now a fallback path, not the primary path.

Why this matters specifically for your career: the Equipment Sourcing job post explicitly asks for "a locally-hosted vision model to look at every photo of every auction listing." If your DocIntel repo demonstrates exactly this pattern with Ollama + Llama 3.2 Vision, your proposal moves from "I can probably do this" to "here's the open-source repo where I already did it."
Move 1 — Three-route extraction pipeline:
PDF or image
    │
    ▼
[choose route by env var or per-request param]
    │
    ├──→ ROUTE A: VISION_PREMIUM (Claude Sonnet 4.6 Vision)
    │        Best for complex layouts, handwriting, mixed languages.
    │        Cost: ~$0.01-0.05 per page. Latency: 2-5s.
    │
    ├──→ ROUTE B: VISION_LOCAL (Ollama + Llama 3.2 Vision 11B or
    │              Qwen 2.5-VL 7B)
    │        Best for privacy, cost-bound, high-volume.
    │        Cost: $0 + electricity. Latency: 3-10s GPU, 30s+ CPU.
    │
    └──→ ROUTE C: OCR_FALLBACK (Tesseract + LLM cleanup)
             Use when vision cost prohibitive or image quality too low.
             Cost: ~$0.001 per page. Latency: 1-3s.

Move 2 — Implement the vision LLM extractor:
# services/vision_extractor.py (NEW)
import base64
from litellm import acompletion
 
INVOICE_PROMPT = """You are a precise invoice data extractor.
Look at the document image and return JSON with these fields:
{
  "vendor": str, "invoice_number": str, "invoice_date": str (ISO 8601),
  "due_date": str (ISO 8601), "currency": str (ISO 4217),
  "subtotal": float, "tax": float, "total": float,
  "line_items": [{"description": str, "quantity": float,
                  "unit_price": float, "amount": float}]
}
Only return valid JSON. If a field is not visible, use null."""
 
async def extract_via_vision_llm(image_bytes, model, doc_type="invoice"):
    b64 = base64.b64encode(image_bytes).decode()
    response = await acompletion(
        model=model,  # anthropic/claude-sonnet-4-6 OR ollama/llama3.2-vision
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": PROMPTS[doc_type]},
                {"type": "image_url",
                 "image_url": {"url": f"data:image/png;base64,{b64}"}},
            ],
        }],
        response_format={"type": "json_object"},
        temperature=0.1,
    )
    return json.loads(response.choices[0].message.content)
# LiteLLM handles provider-specific image-message format differences
# Same function works for Claude, GPT-4o, Gemini, Ollama vision models
Move 3 — NEW: /classify-image endpoint for the Equipment Sourcing pattern:
# api.py
@app.post("/classify-image")
async def classify_image(
    file: UploadFile,
    categories: list[str] = Query(...),
    route: str = "vision_local"
):
    """Given an image and a list of possible categories, return
    which category the image most likely belongs to + confidence.
    
    Critical for: auction listings, marketplace scrapers, inventory.
    The Equipment Sourcing job uses this exact pattern.
    """
    image = await file.read()
    prompt = f"""Look at this image. Which category does the main
    object belong to? Categories: {", ".join(categories)}.
    Return JSON: {{"category": str, "confidence": float, "reasoning": str}}"""
    return await classify_via_vision_llm(image, prompt, route=route)
3.4 The LLM Extraction Layer — Expanded Timeline
V1 budgeted 1–2 days for llm_extractor.py. V2 budgets 1–2 weeks. Reliable structured extraction across diverse document layouts takes prompt iteration on real data.

You will discover:
•	Some vendors put totals in a sidebar, not in line items
•	Some invoices use commas as decimals (EU format)
•	Some scanned receipts have OCR garbage that confuses LLM parsing
•	Some contracts have multi-page clauses that don't fit your prompt budget
•	LLM responses sometimes include markdown fences, hallucinated fields, or silently wrong values

Mitigation plan:
1.	Build an eval dataset: 50 real invoices from different vendors. For each, manually create the expected JSON. Save to docintel/tests/invoice_eval.jsonl. Run weekly.
2.	Iterate prompts until accuracy on key fields (total, vendor, date, invoice number) reaches 90%+ on the eval set.
3.	Log every extraction with confidence and inputs. Review failures.
4.	Add fallbacks: if LLM returns malformed JSON, retry once with a stricter prompt. If still fails, return raw text with a flag.

Realistic timeline: 2 weeks of focused work to get to 90% accuracy on invoices. Contracts and medical records take longer per document type. Don't claim what you haven't measured.
Layer	Old	New
Primary route	Tesseract → Groq text	Vision LLM → JSON (Claude Sonnet 4.6 OR Ollama Llama 3.2 Vision)
Secondary route	—	Marker (PDF → high-quality Markdown)
Fallback route	pdfplumber + Tesseract	Surya OCR + DocTR + LLM cleanup
LLM (premium)	Groq	Claude Sonnet 4.6 Vision
LLM (local)	—	Ollama Llama 3.2 Vision 11B OR Qwen 2.5-VL 7B
Multi-provider	Hardcoded	LiteLLM (vision included)
New endpoint	—	/classify-image (vision-first object/category classification)
Eval harness	Per-field accuracy only	+ vision-vs-OCR benchmark (200-doc dataset, released)
n8n integration	—	Webhook endpoint + n8n node template documented
PROJECT 4: VoiceFlow
Speech-to-Intelligence Pipeline
4.1 Differentiation
Transcription is a commodity (Whisper is free). What clients pay for is the intelligence layer on top — meeting notes with action items, sales calls with CRM-ready output, voice-to-task automation.
4.2 Architecture
┌────────────────────────────────────────────────────────────────┐
│                    VoiceFlow API                               │
│                                                                │
│  POST /transcribe          Audio → text                        │
│  POST /analyze             Text → structured insights          │
│  POST /pipeline            Audio → insights (full pipeline)    │
│  POST /meeting/process     Meeting audio → meeting notes       │
│  POST /call/analyze        Sales call → CRM-ready data         │
│  POST /tts                 Text → speech (multi-provider)      │
│  WS   /stream              Real-time streaming transcription   │
│  WS   /realtime            OpenAI Realtime API voice agent     │
└────────────────────────────────────────────────────────────────┘
                            │
   ┌────────────────────────┼────────────────────────┐
   ▼                                                  ▼
┌────────────────┐                          ┌──────────────────┐
│ Whisper Layer  │                          │ Intelligence Layer│
│                │                          │                  │
│ WhisperX       │                          │ Meeting Analyzer │
│  (alignment    │                          │ Sales Analyzer   │
│   + diarize)   │                          │ Support Analyzer │
│ Groq fallback  │                          │ Interview Anal.  │
│ Deepgram       │                          │ General Analysis │
│ AssemblyAI     │                          └──────────────────┘
└────────────────┘                          
4.3 Speaker Diarization (REVISED from v1)
V1 promised pyannote diarization in 1–2 days. V2 acknowledges this is risky. pyannote.audio requires HuggingFace authentication, ~1GB download, pytorch with compatible CUDA or CPU build, and often fights with macOS/Linux audio driver quirks.

If you can't install it cleanly in 2 hours, fall back to no diarization. Whisper alone provides "this is what was said." Diarization adds "who said what" — useful but not critical. Most meeting-notes use cases don't need it.

If you do want diarization — fallback chain:
5.	Try pyannote.audio first (best quality if it installs)
6.	Fall back to simple-diarizer (lighter, less accurate)
7.	Final fallback: skip diarization entirely. Note in README as "not yet implemented — single-speaker assumed."
Honesty wins clients. Don't promise diarization if you can't reliably ship it.
Meeting Analyzer Implementation
# voiceflow/services/meeting_analyzer.py
 
ANALYSIS_MODELS = {
    "meeting":      "groq/llama-3.3-70b-versatile",
    "sales_call":   "anthropic/claude-sonnet-4-6",
    "support_call": "anthropic/claude-haiku-4-5",
    "interview":    "anthropic/claude-sonnet-4-6",
    "general":      "groq/llama-3.3-70b-versatile",
}
 
MEETING_PROMPT = """Analyze this meeting transcript and extract structured information.
Return ONLY valid JSON, no markdown fences.
 
{
  "meeting_summary": "3-sentence executive summary",
  "participants_mentioned": ["list of names mentioned"],
  "decisions": [{"decision": str, "made_by": str, "context": str}],
  "action_items": [
    {"action": str, "owner": str, "due": "deadline or null", "priority": "high|medium|low"}
  ],
  "key_numbers": [{"value": str, "context": str, "unit": str}],
  "open_questions": ["list of unresolved questions"],
  "next_steps": ["ordered list of next steps"],
  "sentiment": "positive|neutral|tense|mixed",
  "topics_covered": ["list of main topics"]
}
 
Transcript: {transcript}"""
 
SALES_CALL_PROMPT = """Analyze this sales call transcript.
Return ONLY valid JSON.
 
{
  "call_summary": "2-sentence summary",
  "prospect_company": "company name or null",
  "prospect_contact": "contact name or null",
  "prospect_role": "their role or null",
  "pain_points": ["list of pains they mentioned"],
  "objections": [{"objection": str, "type": "price|timing|need|trust|authority"}],
  "buying_signals": ["positive signals detected"],
  "budget_mentioned": "amount or null",
  "timeline_mentioned": "string or null",
  "deal_stage": "awareness|interest|consideration|intent|evaluation|purchase",
  "recommended_next_step": "specific recommended action",
  "crm_notes": "2-3 sentence note suitable for CRM entry",
  "overall_sentiment": "positive|neutral|negative",
  "likelihood_to_close": "high|medium|low"
}
 
Call transcript: {transcript}"""
4.5 Demo Recording Script (90 seconds)
Time	Action
0:00–0:05	Open browser demo (record.html)
0:05–0:20	Click record. Say: "Team meeting March 15th. Sarah committed to finishing the API integration by end of week. John to review the $50,000 proposal from Acme Corp by Friday."
0:20–0:35	Click stop — transcription appears live
0:35–0:50	Click Analyze (meeting mode)
0:50–1:10	JSON appears: action_items shows Sarah with deadline, key_numbers shows $50,000, decisions shows the assignment.
1:10–1:30	Switch to sales-call mode. Same recording, different output: prospect, deal stage, CRM notes, recommended next step.
4.10 2026 Stack Upgrade For VoiceFlow
Layer	Old	New
Transcription (local)	faster-whisper	WhisperX (faster-whisper + alignment + diarization) + NeMo Canary (advanced)
Transcription (API)	—	Groq Whisper + Deepgram Nova-3 + AssemblyAI Universal-2 (provider router)
Diarization	—	pyannote 3.x + NeMo fallback + no-diarization fallback
LLM (sales, interview)	Groq	Claude Sonnet 4.6 (nuance critical)
LLM (support calls)	Groq	Claude Haiku 4.5 (cheap, high-volume)
LLM (meeting, general)	Groq	Groq Llama 3.3 70B (speed matters)
TTS	edge-tts	edge-tts + Kokoro TTS + ElevenLabs + OpenAI tts-1-hd
Real-time voice agent	—	OpenAI Realtime API demo bridged to AgentKit MCP tools
Multi-provider	Hardcoded	LiteLLM + provider router
PROJECT 5: RAGeval
LLMOps Observability — Self-Hosted Drop-In
5.1 Competitive Landscape (NEW in v2)
V1 framed RAGeval as "almost no one offers this." That's misleading. The space has real, capable competitors. Rare-skill positioning doesn't work. The differentiator must be architectural, not scarcity.
Tool	Type	Pricing	Self-hosted?
Arize Phoenix	OSS + commercial	Free OSS, $$ commercial	Yes (OSS)
LangSmith	Commercial (LangChain)	Free tier, $$ at scale	No
TruLens	OSS	Free	Yes
Helicone	Commercial	Free tier, $$ at scale	Self-host possible
Langfuse	OSS + commercial	Free OSS, $$ commercial	Yes (OSS)

RAGeval's differentiator must be:
•	Drop-in for FastAPI + LangChain — a @track decorator with zero config is genuinely rare
•	Self-hosted, <$5/month to run — ships as one Docker container with SQLite as default
•	Domain-aware metrics — persona-aware groundedness: "Did the CFO response actually stay within Finance + Growth data?"

The honest competitive frame: "Phoenix and Langfuse are great if you can deploy a full UI stack. RAGeval is for teams who want drop-in observability in one Docker container with SQLite default — same metrics, no infrastructure overhead."
5.2 Architecture
┌──────────────────────────────────────────────────────────────────┐
│                   RAGeval Dashboard (React)                       │
│                                                                   │
│   SYSTEM Health  ·  QUALITY Metrics  ·  COST Tracker             │
│                                                                   │
│   Query Log (last 50, color-coded: green/yellow/red by score)    │
│   Retrieval Bench · Embedding Comparison                         │
└──────────────────────────┬───────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                    RAGeval API                                    │
│  POST /eval/log · POST /eval/score · GET /eval/metrics           │
│  GET /eval/queries · GET /eval/cost-report · GET /eval/alerts    │
│  POST /eval/retrieval-bench · POST /eval/embedding-comparison    │
│  WS   /eval/live                                                  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                  Evaluation Engine                                │
│                                                                   │
│  1. Retrieval Relevance  cosine_similarity(query, chunks).mean() │
│  2. Groundedness         Multi-judge consensus (3 models)        │
│  3. Faithfulness         Embedding-similarity NLI proxy          │
│  4. Latency Tracking     P50, P95, P99 per query type            │
│  5. Cost Per Query       tokens × price_per_token                │
│  6. Persona Adherence    NEW — did response stay in role scope?  │
└──────────────────────────────────────────────────────────────────┘
5.4 The Drop-In SDK (killer feature)
from rageval import track
 
@track(project="my_rag_app")
async def my_rag_query(question: str) -> str:
    chunks = retriever.get(question)
    answer = llm.generate(question, chunks)
    return answer
# That's it. The decorator:
# 1. Times the function
# 2. Captures input/output
# 3. Calls evaluator on the result
# 4. Stores in SQLite (default) or configured backend
# 5. Exposes metrics via /eval/metrics
Publish as pip install rageval to PyPI. Target: 500 downloads/month by end of 2026. Even 100 downloads a month is meaningful.
5.5 Integration into IntelAI (Self-Eating Dogfood)
Modify omnismart_chatbot.py to call rageval.track. Now every chat interaction in IntelAI is automatically logged and scored. This is your demo: open the RAGeval dashboard, see real production data from your own deployed system flowing in.
5.8 Research-Track Artifact
"Persona-Conditioned Groundedness: An Evaluation Framework for Role-Scoped RAG Systems" — Extends standard groundedness metrics to incorporate persona/role constraints. An answer can be groundedness-valid against retrieved chunks but violate role-scope constraints (a CFO response citing People-domain data). Releases the metric as rageval-persona. Strong alignment-research connection.
5.10 2026 Stack Upgrade For RAGeval
Layer	Old	New
LLM judge	Single Groq call	Multi-judge consensus (Claude Haiku 4.5 + Groq + GPT-5-mini) with flag-for-review on disagreement
Embeddings	MiniLM only	+ BGE-large + BGE-M3 + Arctic + Jina v3 (compare all)
Storage	SQLite only	SQLite (default) + Postgres + pgvector (production)
Observability	Internal only	+ OpenTelemetry / OpenLLMetry export (any OTEL backend)
Retrieval benchmarks	None	/eval/retrieval-bench endpoint (compares strategies)
DSPy integration	None	DSPy compilation telemetry (logs prompt-program runs)
Research artifact	None	Persona-Conditioned Groundedness + Multi-Judge Consensus methodology
Multi-judge consensus implementation:
# evaluator.py — multi-judge scoring
JUDGE_MODELS = [
    "anthropic/claude-haiku-4-5",        # fast, cheap, frontier
    "groq/llama-3.3-70b-versatile",       # diverse perspective
    "openai/gpt-5-mini",                  # diverse perspective
]
 
async def score_groundedness_consensus(answer, context):
    scores = []
    for model in JUDGE_MODELS:
        s = await llm_judge_groundedness(answer, context, model=model)
        scores.append({"model": model, "score": s})
    return {
        "consensus": np.mean([s["score"] for s in scores]),
        "stdev":     np.std([s["score"] for s in scores]),
        "judges":    scores,
        "flag_for_review": np.std([s["score"] for s in scores]) > 0.2,
    }
# This single change is a defensible novel contribution for the preprint.
PROJECT 6: StreamPulse
Real-Time Business Data Intelligence Pipeline
6.1 Positioning (REVISED from v1)
Primary channel: Cold email to operations directors / data engineers at growing SaaS companies (50–200 employees). They have webhook + email data scattered across tools and no time to wire it. Secondary: Upwork (n8n/Zapier developer searches). Tertiary: Open-source positioning — the DomainClassifier with 160+ keywords could ship as a small library.
6.2 Architecture
External Sources:
┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐
│  Gmail  │  │ G.Sheets│  │Webhooks │  │  CSV    │  │   API   │
│  (email)│  │ (data)  │  │ (n8n/   │  │ Upload  │  │ (REST)  │
│         │  │         │  │  Zapier)│  │         │  │         │
└────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘
     └────────────┴────────────┴────────────┴────────────┘
                               │
              ┌────────────────▼───────────────┐
              │        StreamPulse API          │
              │  POST /ingest/json              │
              │  POST /ingest/csv               │
              │  POST /ingest/email             │
              │  POST /webhook/{source}         │
              │  POST /webhook/{source}/with-vision │
              │  GET  /pipeline/status          │
              │  WS   /live                     │
              │  GET  /live/sse                  │
              └────────────────┬───────────────┘
                               │
              ┌────────────────▼───────────────┐
              │     Domain Classifier           │
              │   (from realtime_pipeline.py)   │
              │                                 │
              │  Fast path: keyword matching    │
              │  Fallback: BGE-large embedding  │
              │  Last resort: Claude Haiku 4.5  │
              │                                 │
              │  Finance | Growth | Operations  │
              │  People  | ESG   | IT | Logistics│
              └────────────────┬───────────────┘
                               │
         ┌─────────────────────┼──────────────────────┐
         ▼                     ▼                      ▼
  ┌──────────┐        ┌─────────────┐        ┌──────────────┐
  │PostgreSQL│        │  DuckDB     │        │  WebSocket   │
  │ Persist  │        │  Analytics  │        │  Live Push   │
  │ All data │        │  Fast query │        │  Dashboard   │
  └──────────┘        └─────────────┘        └──────────────┘
6.4 NEW: Vision-Classification Webhook (DocIntel Synergy)
For the Equipment Sourcing use case: many incoming "records" are auction listings with photos. Add a webhook endpoint that classifies photo+text together:
@app.post("/webhook/{source}/with-vision")
async def webhook_with_vision(source: str, payload: dict):
    """
    payload contains text + image_url
    1. Classify domain from text (StreamPulse classifier)
    2. Classify image category (DocIntel /classify-image)
    3. Combine → enriched record
    4. Broadcast to live dashboard
    """
    text_classification = await classify_domain(payload.get("description", ""))
    
    image_classification = None
    if payload.get("image_url"):
        image_classification = await docintel_classify_image(
            payload["image_url"],
            categories=payload.get("categories", ["equipment", "vehicle", "electronics"]),
        )
    
    enriched = {
        **payload,
        "domain": text_classification["domain"],
        "domain_confidence": text_classification["confidence"],
        "image_category": image_classification.get("category") if image_classification else None,
        "image_confidence": image_classification.get("confidence") if image_classification else None,
    }
    await pipeline.store_and_broadcast(enriched)
    return {"status": "processed", "record": enriched}
 
# This single endpoint demonstrates DocIntel + StreamPulse working together
# — exactly the cross-project composition the Equipment Sourcing job needs.
6.10 2026 Stack Upgrade For StreamPulse
Layer	Old	New
Classifier	Keyword-only (160 kw)	Hybrid: keyword fast path + BGE-large embedding + Claude Haiku 4.5 fallback
Ingestion	Custom Python	+ dlt declarative sources (gmail, gsheets, webhook)
Orchestration	None	+ Prefect 3 flow (retries=3, observability, scheduling)
n8n integration	Webhook only	+ custom n8n node template + 3 ready-to-import flows
Vision pipeline	—	/webhook/.../with-vision (composes with DocIntel)
Real-time channel	WebSocket only	+ Server-Sent Events (simpler for one-way push)
Storage	Postgres custom	+ pgvector for embedding cache + DuckDB for analytics
Prefect 3 Orchestration Example
# streampulse/orchestration/prefect_flow.py (NEW)
from prefect import flow, task
 
@task(retries=3, retry_delay_seconds=30)
async def ingest_source(source: str): ...
 
@task
async def classify_record(record: dict) -> dict:
    # Hybrid classifier (keyword → embedding → LLM fallback)
    return await classifier.classify(record)
 
@task
async def store_kpi(record: dict) -> None:
    await store_kpi_metrics([record])
 
@flow(name="streampulse-realtime-pipeline")
async def pipeline_flow(sources: list[str]):
    for source in sources:
        records = await ingest_source(source)
        classified = [await classify_record(r) for r in records]
        await asyncio.gather(*[store_kpi(c) for c in classified])
Cross-Project Synergy Summary
The six projects are not independent — they share a deliberate stack so a single Upwork client can buy two or three of them as a bundle:
Synergy Pair / Triple	Client Value Proposition
IntelAI + RAGeval	"Production RAG + measured quality" (RAGeval drops in via @track decorator)
AgentKit + IntelAI	"MCP-powered analytics agents" (Claude Desktop talks to your data)
DocIntel + StreamPulse	"Vision-first multi-source aggregator" (auction listings, invoice intake, etc.) — the Equipment Sourcing pattern
VoiceFlow + AgentKit	"Real-time voice agent for KPIs" (talk to your business via Realtime API)
RAGeval + DSPy + AgentKit	"Self-optimizing observable agents" (research-credential story for 2027)
All six	"Full AI-engineering stack reference" (consultancy-level positioning by 2027)

The shared stack across all six:
Component	All Six Projects Use
LiteLLM	Multi-provider abstraction (mandatory)
Claude Sonnet 4.6	Premium reasoning tier (paid via Anthropic)
Claude Haiku 4.5	Cheap frontier (judge, classify)
Groq Llama 3.3 70B	Fast inference tier
Ollama Llama 3.3 70B	Local fallback tier (+ Llama 3.2 Vision)
BGE-large-en-v1.5	Embeddings default
BGE Reranker v2 m3	Reranking default
Postgres + pgvector	Production storage default
ChromaDB / SQLite	Dev storage default
OpenTelemetry / OTLP	Observability standard
FastAPI + Uvicorn	API framework
LangGraph + Claude Agent SDK	Agent frameworks
DSPy	Research-grade prompt programs


PART III — MULTI-CHANNEL DISTRIBUTION
Section 5: The 2026 Channel Mix (GitHub + Upwork + Loom ONLY)
Important refinement (your explicit preference): In 2026 you publish to THREE channels only — GitHub, Upwork, and Loom (demo videos). Everything else is deferred to 2027, where it becomes a deliberate multi-channel launch with all 2026's accumulated material as ammunition.
5.1 The 2026 vs 2027 Channel Split
Channel	2026 (NOW)	2027 (LATER)
Upwork (proposals, delivery)	✅ PRIMARY	Maintain rate
GitHub (public repos, README)	✅ PRIMARY	Maintain + new repos
Loom (demo videos)	✅ PRIMARY	Maintain + voice-over
PyPI / DockerHub (artifacts)	✅ Yes	Maintain
Personal portfolio site	❌ NOT YET	✅ Launch Q1 2027
Medium	❌ NOT YET	✅ Cross-post Q1 2027
dev.to	❌ NOT YET	✅ Cross-post Q1 2027
arXiv (preprint submission)	❌ NOT YET	✅ Submit Q1-Q2 2027
LinkedIn (posts)	❌ NOT YET	✅ Cornerstone Q1 2027
Hacker News (Show HN)	❌ NOT YET	✅ One per project 2027
Reddit (r/MachineLearning etc.)	❌ NOT YET	✅ Selectively 2027
Twitter / X	❌ NOT YET	✅ Optional 2027
Newsletter (Buttondown)	❌ NOT YET	✅ Optional Q2 2027
5.2 What "Publish" Means in 2026
For each completed project in 2026, "published" means:
8.	GitHub repo is public with full README, demo link, LICENSE, CI green
9.	Loom demo recorded (60-180 seconds), linked from README + Upwork
10.	Upwork portfolio entry with screenshots + demo link + bullets
11.	PyPI/DockerHub artifact (where applicable: omnismart-personas, rageval, docintel image)

That's it. No blog post goes live in 2026. No Medium account is created in 2026. No arXiv submission in 2026. No LinkedIn post in 2026.
5.3 What You Still DO in 2026 (Without Publishing)
You write drafts. You record raw clips. You collect screenshots. You journal stories. All of this is 2027 ammunition, not 2026 output.
Artifact (Drafted in 2026)	Deployed in 2027
6 blog posts (one per project, ~2000 words each)	Personal site + Medium + dev.to (Q1 2027)
1 arXiv preprint draft	Submitted to arXiv + workshop (Q1-Q2 2027)
LinkedIn cornerstone post ("What I built in 2026")	Published Day 1 of LinkedIn launch (Q1 2027)
20-30 short LinkedIn drafts (stories, snippets, mini-tutorials)	Drip-fed 2x/week through 2027
Hacker News "Show HN" drafts (one per project)	Submitted across Q1-Q2 2027 (spaced out)
Conference talk outline (1 keynote-able topic)	Submitted to AI confs for 2027 speaking slots
5.4 Why This Minimalism Is Right for 2026
12.	Channel proliferation is the freelancer killer. Writers and devs who try to be on 8 platforms simultaneously deliver nothing well. By restricting to GitHub + Upwork + Loom, you concentrate all signal in the place clients actually look.
13.	Late publishing compounds. A blog post published in Q1 2027 with 6 months of post-build perspective + screenshots from real client work is dramatically better than the same post published live during a hectic build phase.
14.	You avoid the "stale content problem." Posts published mid-build often contain claims that turn out wrong by week 12. Drafting now and publishing later lets you fact-check against shipped reality.
5.5 Effort Allocation in 2026
Channel	Effort	ROI in 2026	ROI in 2027+
Upwork (proposals, profile, delivery)	65%	High	Medium
GitHub (public repos, README, CI, demos)	20%	High	Very high
Loom (demo videos + drafted-blog clips)	8%	High	Medium
PyPI / DockerHub artifacts	5%	Medium	Medium
Writing drafts (blog, preprint, LinkedIn)	2%	Zero (drafted)	Very high (deploy)
LinkedIn / Medium / arXiv / portfolio	0%	Zero	Foundation laid
5.6 End of 2026 Position
Published (live) in 2026:
☐  6 GitHub public repos with READMEs, demos, CI
☐  6 Loom demo videos
☐  6 Upwork portfolio entries
☐  2 PyPI packages (omnismart-personas, rageval)
☐  1 DockerHub image (docintel)
☐  5-10 paying Upwork client engagements completed

Drafted (not published) in 2026, ready for 2027:
☐  6 blog posts (one per project, fact-checked against shipped reality)
☐  1 arXiv preprint draft, peer-reviewed by 3-5 contacts
☐  1 LinkedIn cornerstone post ("What I built in 2026")
☐  20-30 short LinkedIn posts (stories, micro-tutorials, lessons)
☐  6 Hacker News "Show HN" submission drafts
☐  1 personal portfolio site design + content (ready to deploy)
☐  A spreadsheet of 100-200 LinkedIn target connections
Section 6: Upwork Strategy For 0-Review Freelancers
6.1 The Fundamental Constraint
Upwork's algorithm de-prioritizes new freelancers in search. Even with a strong profile, your proposals will:
•	Be invisible to most clients in the first 30 days
•	Get throttled — you can only send ~30 proposals/week with Connects
•	Be filtered out by clients with "Top Rated" preference set
•	Need 5–10 reviews before unlocking noticeable visibility increase

This means the first 4–8 weeks will feel discouragingly slow. Plan for it.
6.2 The 5-Element Proposal That Works at 0 Reviews
1. ONE sentence showing you read their SPECIFIC job post
   (NOT generic "I have experience with X")
 
2. ONE sentence on the specific technical approach
   (Shows you've thought about THEIR problem)
 
3. Demo link (THE NEUTRALIZER — this replaces reviews)
   (Live URL OR Loom video — never just screenshots)
 
4. THREE specific technical questions
   (Proves you've thought about edge cases)
 
5. Clear timeline + scope
   (Shows you can manage a project, not just code)
 
NEVER WRITE:
  - "I am an experienced AI developer with 5 years of experience"
  - "I am confident I can deliver this project"
  - Long lists of every technology you know
  - Anything that starts with "I" for the first 3 lines
 
ALWAYS WRITE:
  - Something specific about THEIR job in the first line
  - A technical insight they may not have considered
  - The demo link in line 3 or 4, not at the end
6.3 Which Projects to Lead With on Upwork
Project	Upwork Priority	Why
IntelAI	PRIMARY	Highest niche overlap
DocIntel	PRIMARY	Most consistent demand
RAGeval	SECONDARY	Premium-rate, lower volume
VoiceFlow	SECONDARY	Growing niche, lower volume
AgentKit	TERTIARY	Volume too thin; do open-source first
StreamPulse	TERTIARY	Niche better suited to cold email
6.4 Application Volume
Target: 5 proposals per day, every day, for the first 60 days. That's 300 proposals in 2 months. Realistic outcomes:
•	250–280 silence
•	15–25 interview requests
•	8–12 actual conversations
•	3–5 paid contracts
•	1–2 great long-term clients

This is the funnel. Plan for it. Don't be discouraged by silence — that's the unavoidable cost of building visibility.
6.5 Connects (Upwork Currency) Management
Budget: 40 Connects/week starting (free Plus plan). Each proposal: 4–16 Connects depending on job complexity. ROI metric: cost-per-interview-reply (CPR). Target <15 Connects/CPR.

If a niche burns 100+ Connects with 0 replies, STOP applying there and re-examine your demo and angle.
6.6 When to Walk Away from a Job Thread
•	Client asks for free work as a "test" → walk away
•	Client asks for a Skype/WhatsApp call before Upwork interview → walk away
•	Client's job has 50+ applicants and 0 reviews on their side → low priority
•	Client's last hire was paid $5/hr → walk away

Time spent dodging bad clients is worth more than time spent serving them.
Section 7: Open-Source Strategy (PyPI, GitHub, DockerHub)
7.1 The Compounding Return
Project	OSS Deliverable	Launch By
IntelAI	pip install omnismart-personas (persona templates as standalone package)	Week 4
AgentKit	GitHub repo (primary) + Awesome-MCP listing	Week 10
DocIntel	DockerHub: docintel/api:latest (one command to run anywhere)	Week 7
VoiceFlow	GitHub repo + Loom-anchored README	Week 13
RAGeval	pip install rageval (the SDK as primary distribution)	Week 16
StreamPulse	GitHub repo	Week 18
7.2 Publishing Checklist (Every Repo)
Before flipping public visibility:
☐  README under 200 lines, no marketing fluff
☐  Architecture ASCII diagram in README
☐  Quick-start (3 commands max) verified on fresh machine
☐  LICENSE (MIT or Apache 2.0)
☐  .env.example with placeholders, no secrets
☐  CI badge (GitHub Actions running tests on push)
☐  Loom demo embedded in README (top of file)
☐  Issue template (helps you when external users file issues)
☐  One-paragraph "why this exists" at top
7.3 Distribution After Launch
•	Submit to Awesome lists (awesome-mcp, awesome-llm-tools, awesome-langchain, awesome-ocr, awesome-rag, etc.)
•	Post in relevant Discord/Slack: MCP Discord, Anthropic Discord, LangChain Discord, MLOps Community
•	Cross-post Loom demo to YouTube Shorts (60–90s) — organic search traffic
•	Submit to Hacker News on a Tuesday at 9am EST (highest visibility window)
•	Reddit: r/LocalLLaMA, r/MachineLearning (read rules carefully), r/Python
Do NOT spam these communities. Post once per project, well-framed, with the demo as the hook. Respond to every comment.
7.4 PyPI Publishing (rageval, omnismart-personas)
# Setup
pip install build twine
python -m build  # Creates dist/*.tar.gz and dist/*.whl
python -m twine upload --repository testpypi dist/*  # Test first
twine upload dist/*  # First time: prompts for credentials
 
# Use semantic versioning.
# Start at 0.1.0. Bump 0.2.0 on first real feature add.
# Reach 1.0.0 when API is stable.
7.5 The PyPI Download Lift
Downloads/Month	Signal
50–100	"Built and shipped a real package"
200–500	"Has actual users, useful enough to install repeatedly"
1000+	"Notable community traction"
5000+	"Recognized in the niche"
Target by end of 2026: rageval at 300/month, omnismart-personas at 100/month.
Section 8: Technical Writing Strategy (Draft In 2026, Publish In 2027)
Important per the channel split in Section 5.1: in 2026 you DRAFT and fact-check all six blog posts, but NONE are published publicly in 2026.
8.2 The 6 Posts (Drafted Alongside Build Phases)
End of Phase	Draft Title
Phase 1	Persona-Routed RAG — How To Scope LLM Responses By Role (Project 1 artifact)
Phase 2	Vision-First Document AI — Beyond Tesseract (Project 3 artifact, leads with vision-LLM upgrade)
Phase 3	Building MCP Servers For Business Data — Tool Design Patterns (Project 2 artifact, biggest reach potential)
Phase 4	Speech-To-Intelligence — Whisper Plus LLM Post-Processing (Project 4 artifact, includes real-time voice agent demo)
Phase 5	Multi-Judge LLM Evaluation For Production RAG (Project 5 artifact, the research-credential post)
Phase 6	Vision-First Multi-Source Aggregation — A Pattern (Project 6 + Project 3 combo, includes Equipment Sourcing case study)
8.3.1 The 2026 "Finishing Pass" Workflow
After each build phase ends, before starting the next phase:
15.	Open the draft you wrote during the phase
16.	Read it against the actual shipped repo — are all claims still accurate?
17.	If a paying client used this project, add a 1-2 sentence anonymized story
18.	Mark TODO comments where you want to add a screenshot from production
19.	Save as vN-postship.md — this is the version that gets published Q1 2027
20.	Do NOT publish yet. Move on to next phase.
8.4 Post Structure (Template Every Time)
TITLE: <Specific, problem-led, not clickbait>
 
OPENING (2-3 sentences):
  What problem this solves. Who has it. Why current solutions fall short.
 
CONTEXT (1-2 paragraphs):
  Where this came from. Brief background on your work.
 
THE PATTERN / TECHNIQUE (the main body, ~1500 words):
  Concrete code. Diagrams. Tradeoffs explicitly named.
 
EVALUATION (200-400 words):
  How well does it work? What did you measure? Show numbers.
 
WHEN NOT TO USE IT (100-200 words):
  Honesty wins. Listing failure modes makes readers trust you.
 
CALL TO ACTION:
  Link to GitHub repo. Link to live demo. Email if interested.
8.5 From Blog Post to arXiv Preprint
If 2 of the 6 posts have: a novel pattern, a small empirical evaluation, an open-source artifact — they're arXiv-suitable. Format using a NeurIPS/ICML LaTeX template (Overleaf has them). Aim for 6 pages.

Submission strategy: workshop submission, not main conference. Workshops accept 50%+ of submissions. Target workshops:
•	NeurIPS 2026 (Dec) — workshop deadlines in Oct
•	ICLR 2027 (May) — workshop deadlines in Jan
•	AAAI 2027 (Feb) — workshop deadlines in Nov
•	ICML 2027 (Mar), ACL 2027 (Apr), EMNLP 2027 (Jun)
Section 9: Cold Email + Communities
9.1 Cold Email Cadence
10 emails per week. Targeting:
Tier	Target	Effort
Tier 1	YC startup CTOs in your verticals (F6S, LinkedIn search, YC alumni directory)	30%
Tier 2	Fractional CTO / consulting agencies that need overflow AI engineering help	30%
Tier 3	Slack/Discord community admins who might feature your open-source work	20%
Tier 4	AI labs and research-aligned orgs for research-engineer contract work	20%
9.2 Cold Email Template
Subject: [Specific value tied to their company/role]
 
Hi [Name],
 
I noticed [specific thing about their company/recent post/job posting].
 
I built [specific thing relevant to their work]. Demo: [link].
 
The interesting part for you might be [specific feature].
 
Worth a 15-minute chat?
 
Yacine
[Brief signature: 1 line + link to portfolio]
 
# Do NOT send 100-word "I'm an experienced developer" boilerplate.
# The 3-sentence specific email outperforms it 10:1.
9.3 Communities to Be Active In
Community	Value
Indie Hackers	Find peers, see what's selling
MLOps Community Slack	Build credibility in observability niche
LangChain Discord	Cross-promote AgentKit + RAGeval
MCP-related servers	First-mover advantage on AgentKit
r/LocalLLaMA	Cross-promote OSS releases
r/MachineLearning	Research-adjacent traffic
HN (Hacker News)	Launch posts, 1 per project
arXiv-sanity	Stay current on research
Be useful, not promotional. Answer questions. Drop your demos when genuinely relevant. People will look you up.
Section 10: LinkedIn 2027 — Light-Touch Prep Now
10.1 The 2026 LinkedIn Prep Checklist
☐  Profile fully filled (use the title and overview from Section 24)
☐  Headshot updated (clean, professional, not corporate-formal)
☐  Connect with every Upwork client you complete a project with
☐  Connect with anyone whose cold email warmly replies
☐  Follow (don't engage with) 50 AI freelancers + researchers you admire
☐  Save (don't post) content you find good — build your asset library
☐  Observe which post formats perform: technical depth? story? carousel? short hot take?
10.2 The 2026 Quiet Network Growth
Every Upwork client connect + every cold email reply = a new LinkedIn connection. By end of year, target 200+ connections. These will be your 2027 launch audience. They'll see your posts naturally in their feeds. Cold launch (zero network) is dead; warm launch (200+ in-niche) is a different ballgame.
10.3 The 2027 Launch (Preview)
In January 2027, you'll:
21.	Publish a "what I built in 2026" post linking your 6 demos + 6 blog posts + 2 PyPI packages
22.	Begin a 2-posts-per-week cadence using your 2026 content library
23.	Pin a featured section with your strongest 3 projects
24.	Run weekly engagement (comment thoughtfully on 10 posts/day)

But that's 2027's problem. In 2026, just build the asset library and the connection base.
PART IV — THE RESEARCH DEGREE TRACK
Section 11: What Top Programs And Fellowships Want In 2026
Top AI programs (Stanford, CMU, MIT, Berkeley, UCL, ETH, Mila, Vector, Oxford) and prestigious fellowships (Anthropic Fellows, OpenAI Residents, Meta AI Residents) have shifted what they value in 2024–2026.
11.1 What Used to Matter (Less Now)
•	GRE scores → most programs dropped or made optional
•	Undergrad GPA → still matters but weighted less for industry applicants
•	Generic Python/ML skills → assumed, not differentiating
•	Course projects → too easy to fake, less weight
11.2 What Matters Now (Descending Order of Weight)
Rank	Signal	Weight
1	Published research output: arXiv preprints, workshop papers, or full conference papers	Very High
2	Open-source contributions with traction: maintained repos with stars/downloads/forks	Very High
3	Deployed AI systems with documented impact — not toy projects	High
4	Reference letters from research-active mentors — 2–3 strong letters	High
5	Statement of purpose with a clear research question (not "I want to study AI")	High
6	Technical writing: blog posts, contributed papers, well-documented code	Medium
7	Coursework / prior research — still matters but less than above for industry applicants	Medium
11.3 The Anthropic Fellows Path Specifically
The Anthropic Fellows program values: demonstrated work on alignment, interpretability, or AI safety problems; strong technical engineering skills (production deployment); independent thinking; ability to write clearly.

"Persona-routed RAG with role-scoped data access" (your IntelAI core differentiator) connects to alignment-relevant questions: How do you constrain LLM behavior to a defined role? How do you evaluate adherence to that role at scale? How do you make role-conditioned responses measurable and auditable?
Section 12: How This Plan Builds Research Capital
12.1 The Asset Stack at End of 2026
Asset	What It Buys You
6 deployed projects (live demos)	Production AI experience narrative
2 PyPI packages with users	Open-source contribution credibility
6 technical blog posts (drafted, published Q1 2027)	Technical writing demonstration
1 arXiv preprint (probably 2)	Research output credibility
Workshop submission (maybe accepted)	External validation
200+ in-niche LinkedIn connections	Network depth
2-3 strong client references	Letters of recommendation
Sustained Upwork income	Industrial experience proof
A coherent through-line in your writing	Statement-of-purpose foundation
12.2 The Through-Line You Should Be Writing Toward
Your research narrative in late 2027: "I spent 2026 building production AI systems for business intelligence. Across 6 deployed projects, I observed a recurring pattern: production AI assistants need role-scoped behavior — a CFO query and a CHRO query should retrieve different data and produce different responses. Existing RAG evaluation frameworks don't capture role-scope adherence. I formalized this with 'persona-conditioned groundedness' in a preprint and an open-source library (rageval). At PhD level, I want to extend this in two directions: (1) interpretability — what mechanisms in instruction-tuned LLMs mediate role conditioning?, and (2) alignment — can role-scoped behavior be a primitive for more general AI safety properties?"
12.3 The Work-to-Narrative Pipeline
EVERY PROJECT YOU SHIP:
   ↓ produces
LIVE DEMO + GITHUB REPO + BLOG POST DRAFT
   ↓ together feed
THE NARRATIVE THROUGH-LINE (Section 12.2)
   ↓ which structures
YOUR ARXIV PREPRINT(S) IN 2026 / 2027
   ↓ which become
YOUR STATEMENT OF PURPOSE IN 2027
   ↓ supported by
REFERENCE LETTERS FROM CLIENTS YOU SERVED IN 2026
Section 13: One Preprint Per Year (Realistic Cadence)
13.1 The 2026 Preprint
Target: "Persona-Conditioned Groundedness: An Evaluation Framework for Role-Scoped RAG Systems"
Why this one first: builds directly on work you're already doing; has a concrete artifact (rageval library); has a clear measurement story (you'll have the eval data); connects to active research areas (RAG eval + alignment); workshop-publishable bar (not full-conference difficulty).

Timeline:
•	Weeks 14–16: build RAGeval (the artifact)
•	Weeks 17–20: collect evaluation data on real persona usage
•	Weeks 21–24: write draft, submit to a workshop, publish to arXiv
•	End-of-year goal: preprint on arXiv with link in your portfolio
13.2 The 2027 Preprint (Preview)
Likely topic: "MCP Tool Design Patterns for Production AI Agents." Why: AgentKit is the artifact; pattern catalog is workshop-quality novelty; field is hot, accept rates favorable. Don't commit yet — let 2026 deployment data shape the exact angle.
13.3 Workshop Submission Strategy
Submit your 2026 preprint to 2–3 workshops simultaneously:
•	NeurIPS workshop track (most workshops accept dual submissions; check individual workshop rules)
•	A pure-eval workshop (e.g., "Workshop on LLM Evaluation")
•	An alignment-adjacent workshop (e.g., "Workshop on Trustworthy LLMs")

Workshops accept 40–60% of submissions. With a polished preprint, strong odds of at least one acceptance.
13.4 The "Good Enough" Preprint Standard
You're not aiming for ICLR oral. Stop polishing past this bar.
☐  6 pages of clean, well-formatted writing
☐  A concrete problem statement
☐  A novel pattern or framework
☐  A small empirical evaluation (10–30 data points minimum)
☐  A released artifact (code + data)
☐  A statement of limitations
Section 14: Research-Aligned Freelance Opportunities
Organization	Type	Pay	Research Value
Anthropic	Research engineer contracts	$$$$	Very High
OpenAI	Research engineer contracts	$$$$	Very High
Cohere / Mistral / AI21	Engineering contracts	$$$	High
Apollo Research	AI safety contracts	$$$	Very High
METR / ARC Evals	Evaluation contracts	$$$	Very High
MIRI / FHI / GovAI	Safety / policy research	$$-$$$	Very High
Workshop / conference orgs	Reviewer, organizing	$0–$	Medium
Open-source maintenance grants (Sloan, NumFOCUS)	Maintenance	$$$	Medium-High

On Upwork: search for "Research engineer", "AI research engineer", "LLM researcher". Filter for U.S. tech-company clients. Pay is usually $80–150/hr. Apply with your strongest demo + a brief note that you've published to arXiv (when you have).
Section 15: Reference Letter Strategy
Three short-form reference building paths:
•	Client work: After 3+ months of solid work, ask if they'd be willing to write a reference letter or be a referee. Prefer clients who themselves do research or are former researchers.
•	Open-source community: maintainers of projects you contributed to
•	Research-aligned contract work: even one short contract with an Anthropic-adjacent org is a strong reference

The biggest mistake industry-to-research applicants make: assuming professors they took classes with will write strong letters. Often professors barely remember them and write generic letters. Specific, recent, work-based referees write specific, recent, work-based letters. That's what wins.

Goal: 3 strong references by end of 2027 from professional engagements. Combined with 1–2 references from open-source community work (maintainers of projects you contributed to), that's 5 letters.


PART V — EXECUTION (18 WEEKS + WEEK 0, SEQUENTIAL, ALL SIX)
Section 16: Phased Build Plan (Day-by-Day, All Six Projects)
This section is the operational core of the document. It assumes you build all six projects sequentially — one finished and published before the next begins — and that the monorepo split is executed once, upfront, in Week 0 via the AI agent prompt.

The total span is 19 calendar weeks: 1 splitting week + 18 build weeks. Day numbering restarts at Day 1 of Week 0 and runs continuously through Day 133.
16.0 Principles And The Decision To Build All Six
Why Sequential Beats Parallel (For You, In 2026)
25.	Cognitive coherence. Switching contexts between MCP servers, OCR pipelines, and voice intelligence kills depth. One project at a time lets your brain stay in one architectural model.
26.	Publish-as-you-go compounds. Each shipped project becomes a portfolio entry while the next is being built. By Week 6 you already have two live demos, not zero "until Phase 6 finally lands."
27.	Feedback is cheaper. If DocIntel's positioning bombs in Phase 2, you adjust in Phase 3 — not after you've committed three more months to parallel builds.
28.	One environment to operate at a time. Build environment, test environment, deploy environment all stay focused on the current project. No cross-repo dependency tangles.
Why the Split Happens in Week 0, Not Later
29.	Clean scope from day one. The moment you start Phase 1, every other repo is already its own directory with its own requirements.txt.
30.	Forces architectural decisions early. Splitting reveals which utilities are shared, which dependencies are core vs. peripheral, which imports were sloppy.
31.	Git history starts clean per repo. Each project has commits that read like the project's own evolution.
32.	Easier mental model. Six directories side-by-side. You always know which one you're working in.
33.	One splitting pass, not six. The AI agent prompt is run once with all six target schemas.

De-risking step: test the prompt on DocIntel first (the most self-contained project). If DocIntel's extraction works cleanly — imports resolve, tests pass, server starts — you trust the prompt for the other five.
Build Order Rationale
Phase	Project	Why This Position
1	IntelAI	Already mostly built. Fastest path to first live demo. Sets the Upwork profile baseline. Bilingual hero asset.
2	DocIntel	Highest-volume Upwork niche (OCR/document AI). Validates income signal before committing to longer builds.
3	AgentKit	Open-source-first asset. MCP is rare/elite. Compounds GitHub stars and cold-email credibility during weeks 7-9.
4	VoiceFlow	Visual demo (browser recording) → strong portfolio piece. Medium freelance niche. Builds before research push.
5	RAGeval	Highest research-value project. PyPI package + preprint foundation. Built after you have signal on what to evaluate.
6	StreamPulse	Cold-email primary (data/ops directors). Lower Upwork priority. Last because it's most peripheral to 2027 narrative.
What "Publish" Means at End of Each Phase
A project is published (not just "built") when ALL of the following are true:
☐  Live demo URL works in incognito browser (no auth, no broken images)
☐  GitHub repo is public with README < 250 lines, accurate, with demo link
☐  One Loom video (60–180 seconds) walking through the demo, linked in README
☐  For PyPI projects: pip install <package> works for a stranger
☐  For Docker-shipped projects: docker pull works from DockerHub
☐  Blog post DRAFTED and fact-checked (NOT published — defer to Q1 2027 per channel split)
☐  Project added to Upwork portfolio with screenshots + demo link
☐  One proposal already sent on Upwork referencing the new portfolio entry
☐  (For Phases 3 & 5) Posted to relevant community (MCP Discord, HN, r/LocalLLaMA)

If any of those fail, do not advance to the next phase. Take the buffer day to finish — quality of the published asset matters more than calendar pace.
16.1 Phase 0 — Repository Splitting (Week 0)
Goal: Six standalone repositories created, validated, pushed to GitHub (private until each phase ships), local dev environments ready for Phase 1 to start Monday of Week 1 without setup overhead.
Day 1 — Pre-Split Audit + Cleanup
Morning (3h): Inventory and decision-making.
34.	Snapshot the monorepo as-is: git tag pre-split-2026-05-18
35.	Read /etc and /docs directories. List stale files for deletion: COMPLETION_REPORT.md, INTEGRATION_PLAN.md, WORK_INDEX.md, Production_Readiness_Checklist.md, docs/200_TASKS_COVERAGE.md, omniinteloscompletestrategy (replaced by STRATEGY.md v2)
36.	For each candidate deletion, grep the codebase for references. If nothing references it, mark for deletion.
37.	Verify pyproject.toml / requirements.txt match what's actually imported (use pip-check or pipreqs .).
38.	List shared utilities (logger.py, config.py) and note which projects will need slim copies vs. full copies.

Afternoon (3h): Reference the split.
39.	Re-read STRATEGY.md Appendix "Project Source Map" — confirm the file-to-project mapping still matches the current repo state.
40.	Re-read Section 30 (the splitting prompt). Walk through mentally: where would the prompt fail? Note pre-edits needed.
41.	If imports are tangled, do a minimal pre-clean: convert any "from src.something.deep import" to "from src.X import" where it reduces depth without behavior change.
End of Day 1 Checkpoint
☐  Pre-split git tag exists
☐  List of files to delete is written down
☐  List of pre-edits to imports is written down (≤ 10 edits)
☐  You can articulate in 60 seconds what the splitting prompt does
Day 2 — Splitting Prompt Dry-Run on DocIntel
Morning (4h): Test the prompt on a single project to catch bugs cheaply.
42.	Open a NEW Claude Code session (clean context window).
43.	Provide it ONLY the DocIntel section of the splitting prompt (from Section 30, the PROJECT 3 block).
44.	Let it create the docintel/ directory and all files.
45.	As soon as it finishes, run the verification matrix:
cd docintel
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -c "from services.ocr_enhancement import *"
python -c "from services.llm_extractor import LLMExtractor"
uvicorn api:app --port 8001 &
curl http://localhost:8001/health
curl -X POST http://localhost:8001/classify -F file=@sample.pdf

Afternoon (3h): Identify and patch prompt gaps.
Common breakages to look for:
•	"from src.X import" left in files (the prompt missed an import rewrite)
•	Missing __init__.py files in services/ or core/
•	Hardcoded paths that assume monorepo root
•	requirements.txt missing a dep that's actually imported
•	.env.example missing a var that the code reads on startup
•	Dockerfile copies non-existent paths

For each gap found: (1) Note the exact symptom. (2) Update Section 30's prompt text to fix it explicitly. (3) Re-run prompt on DocIntel to confirm fix works. (4) Repeat until DocIntel starts cleanly from a fresh clone.
End of Day 2 Checkpoint
☐  docintel/ runs uvicorn api:app and responds to /health
☐  All imports resolve from project root (no from src.* left)
☐  requirements.txt has no missing or extra deps
☐  Splitting prompt has been updated with any fixes discovered
Day 3 — Run Full Splitting Prompt for Remaining 5 Projects
Morning (5h): Execute the validated prompt on the other five projects.
46.	Open a NEW Claude Code session per project (5 sessions, sequential). Doing them sequentially in fresh sessions keeps context focused.
47.	For each project (AgentKit, VoiceFlow, RAGeval, StreamPulse, plus the IntelAI refactor): provide the PROJECT N block from Section 30, let it create the directory and files, immediately verify smoke test.
48.	The IntelAI refactor is "edits in place," not a new directory: apply the PROJECT 1 changes, cd frontend && npm install recharts, run pytest tests/test_api.py to confirm tests still pass.

Afternoon (3h): Cross-project sanity checks.
49.	Confirm no project imports from another project (no cross-repo deps)
50.	Confirm every project has: README.md, requirements.txt, Dockerfile (builds without error: docker build -t <name>:test .), .env.example, .gitignore
51.	Run pip-compile or similar on each requirements.txt to flag unpinned versions
52.	For each project, write a 3-line note in your Notion log: "What does this project actually do, in plain English?"
Day 4 — Per-Project Verification Pass + Test Skeletons
Morning (4h): Deeper verification beyond smoke tests.
Project	Smoke Test	Deeper Verify
intelai	pytest tests/	All 9 personas resolve; chat endpoint returns text
agentkit	python mcp_server.py	MCP tools list correctly; workflow.analyze() returns dict
docintel	curl /classify with PDF	Returns doc_type within 5s
voiceflow	curl /health	Whisper loads (may take 30s first time — note this)
rageval	python -c "import evaluator"	RAGEvaluator.score_interaction() runs on fake data
streampulse	curl /pipeline/status	WebSocket /live accepts connection

Afternoon (3h): Per-project STATUS.md (your working notes, NOT committed).
# <project> STATUS
 
## What works today
- [list smoke-test-verified capabilities]
 
## Known gaps (will fix in Phase N)
- [list things noticed during the split that need polish]
 
## Risk items
- [things that might break when deployed or scaled]
 
## Next phase tasks (pre-load Phase N's todo list)
- [3-5 concrete tasks the phase will tackle]
Day 5 — Git Init + GitHub Push (Private) + Branch Strategy
# For each of the 6 projects:
cd <project>
git init
git add .  # after .gitignore is in place — verify with git status
git commit -m "initial: extracted from IntelAI monorepo (week 0)"
gh repo create <yourname>/<project> --private --source=. --remote=origin
git push -u origin main
 
# Branch strategy
git checkout -b develop && git push -u origin develop
# main = shipped/tagged versions
# develop = daily build work
 
# CI scaffold (.github/workflows/ci.yml):
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install -r requirements.txt
      - run: pytest tests/ -v --tb=short
Day 6 — Local Environment Hygiene + IDE Workspace
For each project:
53.	Use Python 3.11 (install via pyenv). Create .venv: python3.11 -m venv .venv && source .venv/bin/activate && pip install -U pip wheel setuptools && pip install -r requirements.txt
54.	Create a top-level workspace dotfile if your editor supports it (VS Code: <name>.code-workspace pointing at all 6 directories).
55.	Copy .env.example → .env and fill in real values (GROQ_API_KEY, POSTGRES_URL, etc.). Verify NONE of these .env files are committed.
56.	Create a top-level secrets.md outside any repo with all the keys and URLs you're using locally.
57.	Run each project once locally end-to-end with real keys to confirm the .env propagates correctly.
Day 7 — Buffer + Pre-Phase-1 Planning
Morning (3h): Apply the file deletions from Day 1 to the IntelAI refactor:
rm COMPLETION_REPORT.md INTEGRATION_PLAN.md WORK_INDEX.md
rm Production_Readiness_Checklist.md
rm docs/200_TASKS_COVERAGE.md
rm omniinteloscompletestrategy   # v1 strategy now superseded
git commit -m "chore: remove stale planning docs (v2 strategy supersedes)"

Afternoon (3h): Phase 1 prep.
58.	Open the intelai repo and lay out a TODO.md with Phase 1's Day 1-5 tasks in checkbox form.
59.	Confirm Recharts is installed in frontend/: cd intelai/frontend && npm list recharts
60.	Identify which Upwork niches you'll start with on Day 12 of Phase 1. Recommended: RAG, FastAPI, AI chatbot.
61.	Set a personal calendar reminder for Phase 1, Day 1.
Week 0 Success Criteria
Deliverable	Status
6 standalone project directories	[ ]
All 6 have passing smoke tests	[ ]
All 6 have private GitHub repos with develop branch	[ ]
All 6 have working .venv + .env + Dockerfile that builds	[ ]
All 6 have CI configured and green	[ ]
Each project has STATUS.md with known gaps	[ ]
IntelAI stale docs deleted, README updated	[ ]
TODO.md in intelai exists for Phase 1 Day 1	[ ]
If any row is unchecked, do NOT start Phase 1. Spend the weekend closing the gap. Phase 1 success depends on Week 0 being clean.
16.2 Phase 1 — IntelAI Foundation (Weeks 1–3)
Goal: Publish the first portfolio entry. Demo live, Upwork profile launched, omnismart-personas on PyPI, first 50 proposals out, Blog Post 1 drafted.
Week 1 — Visual + Technical Fixes
Day	Tasks
Day 8	Recharts Conversion Part 1: npm install recharts. Replace SVG bars in AnalyticsPage.jsx with Recharts LineChart. Verify in browser: charts render, data loads from API. Afternoon: Replace ForecastingPage.jsx chart with AreaChart + CI bands. Test with multiple metric selections.
Day 9	Recharts Conversion Part 2: Add RadarChart to RiskPage.jsx. Add sparkline LineCharts (h=60px) to DashboardPage.jsx. Afternoon: Complete FinancialPage.jsx (dropdown + BarChart + currency formatting). Manual smoke test all 4 pages in browser.
Day 10	WebSocket Streaming: Read existing server_v2.py WebSocket chat endpoint. Fix any handler bugs (CORS, auth, persona routing). Afternoon: Wire ChatPage.jsx to /ws/chat instead of POST /chat. Test all 9 personas. Handle disconnect gracefully (reconnect logic).
Day 11	Tests Expansion (full day): Expand tests/test_api.py from 2 tests → 30+ tests. Cover: auth (5), chat (4), kpis (4), insights (3), forecast (2), ingest (3), rbac (4), monitoring (3), misc (3). Run pytest, fix all failures. Confirm CI green.
Day 12	Deploy to Railway: Set up Railway account, connect GitHub. Configure env vars. Set up Railway PostgreSQL add-on. Run db migrations against production DB. Afternoon: Smoke test every endpoint in production. Note the public URL.
Week 1 Checkpoint
☐  All 4 chart pages use Recharts (no SVG bars left)
☐  WebSocket streaming chat works with all 9 personas
☐  pytest passes 30+ tests
☐  Live production URL exists and responds
Week 2 — Demo + Profile + First Proposals
Day	Tasks
Day 13	README Rewrite: Rewrite README.md from scratch. One-line description (<100 chars). "What it does" (3-5 bullets, accurate to actual code). "Quick Start" (3 commands max). "Default Credentials" section. Link to /api/docs. Architecture diagram (ASCII, 10 lines). Demo link at the top. Total length: < 200 lines. Commit and push. Tag v0.1.0.
Day 14	Loom Demo Recording (3-minute walkthrough): Script the demo (write it out, don't ad-lib). Follow the script from Section 1.5. Practice once with screen recording but no audio (timing). Record final take with audio. Upload to Loom. Watch it back — is the audio clear? Did everything work?
Day 15	Pre-Review With 3-5 Trusted Reviewers: DM the Loom link to 3-5 reviewers (2 friends who know the field, 1-2 peers from Discord, 1 person outside tech who catches jargon). Ask for 60-second feedback. While waiting: test demo URL on a phone browser, test from incognito, run Lighthouse audit. Collect feedback by evening. Iterate based on common themes.
Day 16	Iterate Demo + Set Up Upwork Profile: Apply demo feedback — re-record if structural issues. Final Loom URL goes in README. Set up Upwork profile from Section 24: title, overview, skills, hourly rate $65. Add IntelAI as portfolio entry #1.
Day 17	Write 3 Vertical Proposal Templates: Customize Templates 1, 2, 3 from Section 26 for your voice. Each opens with a specific reference to the client's job post. Demo link in the THIRD line. 1-2 specific technical questions. Clear timeline and rate. Save in Notion for copy/paste.
Day 18	First 10 Proposals Sent: Find 10 strong-fit Upwork jobs (filter: 5+ client reviews, posted within 7 days, hourly $30-80, < 30 applicants). 4 RAG/chatbot (T1), 3 FastAPI/Python (T2), 3 BI/dashboard (T3). Log each in Notion: Date, job title, niche, demo link, template used, client country, client reviews.
Week 2 Checkpoint
☐  Loom demo is recorded, < 3:30, watched by 3+ reviewers
☐  Upwork profile is live with IntelAI portfolio entry
☐  10 proposals sent, all logged in Notion
Week 3 — Volume Application + Blog Post 1 + PyPI Package
Day	Tasks
Days 19-21	Daily Proposal Volume (Mon-Wed): Each morning send 8-10 proposals (target 30 by end of week). Each afternoon monitor replies. Side tasks: Day 19: Draft Blog Post 1 outline + opening paragraph. Day 20: Write first half (~1000 words). Day 21: Write second half (~1000 words).
Day 22	Blog Post 1 Reviewer Pass: Finish blog post draft (~2000 words total). Read aloud once. Send draft to 2 reviewers (technical peer + writing-strong friend). Afternoon: Apply review feedback. Add 3-5 code snippets. Add 1 architecture diagram. Add 1 evaluation table.
Day 23	Finalize Blog Post 1 Draft (NOT PUBLISHED — defer to Q1 2027): Save cleaned draft to: intelai/drafts/blog_post_1_persona_rag.md. Save parallel LinkedIn-length draft to writing_workspace/linkedin_drafts/. Save Show HN draft to writing_workspace/hn_drafts/. Tag as "v1-pre-ship".
Day 24	Extract omnismart-personas Package: Create packages/omnismart-personas/. Structure: omnismart_personas/__init__.py, templates.py (PERSONA_TEMPLATES dict), router.py (resolve_persona() function), context.py (PersonaContext dataclass). pyproject.toml, README.md, tests/. Run pip install -e . locally.
Day 25	Publish omnismart-personas to PyPI: Create PyPI account. Install build tools. Build: python -m build. Test upload to test.pypi.org first. Install from test PyPI in a clean venv — verify it works. Upload to real PyPI. Verify: pip install omnismart-personas. Add PyPI badge to README.
Day 26	Continue Proposal Volume + Phase 1 Metrics Review: Send 5-10 more proposals (cumulative target: 50 by Day 27). Phase 1 metrics review: proposals sent, replies, interviews, contracts, PyPI downloads, GitHub stars.
Day 27	Buffer + Phase 2 Prep: Fix anything broken from the week. Polish any rough edges in the Loom demo or README. Open the docintel/ repo. Read its STATUS.md. Write Phase 2 TODO.md. Pre-stage 50 invoice sources for Day 30.
Phase 1 Final Checkpoint
Deliverable	Status
IntelAI deployed at public URL	[ ]
4 chart pages use Recharts	[ ]
WebSocket streaming chat working	[ ]
30+ pytest tests passing	[ ]
README rewritten, < 200 lines	[ ]
Loom demo recorded, pre-reviewed	[ ]
Upwork profile live with IntelAI portfolio	[ ]
50 proposals sent, all logged	[ ]
Blog Post 1 DRAFTED + saved to drafts/ (publish Q1 2027)	[ ]
omnismart-personas published to PyPI	[ ]
0-3 client interviews secured	[ ]
If 50 proposals → 0 replies, STOP. Do not start Phase 2. Spend Day 27-28 diagnosing: is the demo broken? Is the proposal generic? Is the niche wrong? Get external review before proceeding.
16.3 Phase 2 — DocIntel (Weeks 4–6)
Goal: Second portfolio entry live. Validates OCR/document AI niche. DockerHub artifact published. Blog Post 2 drafted. 30 OCR-niche proposals sent.
Week 4 — Core Build
Day	Tasks
Day 28	Verify Extracted Repo + Build api.py: cd docintel, re-read STATUS.md, run pytest tests/ (confirm baseline). Build api.py with all endpoints. Define ProcessResponse Pydantic model. Serve demo/ as static at /demo. Local smoke test: uvicorn api:app and curl each endpoint with a sample PDF.
Day 29	Build services/llm_extractor.py: Implement LLMExtractor class with async extract(text, doc_type) method. Prompts for: invoice, contract, receipt, financial_report, default. temperature=0.1. Strip markdown fences before json.loads. Test with 3-5 real PDFs from enhanced_synthetic_dataset.
Day 30	Build services/batch_processor.py + Demo UI: BatchProcessor class with process/get_status/get_results. In-memory dict for job tracking. Test with 5-document batch. Build demo/index.html — drag-and-drop demo, dark theme (#0f172a), vanilla JS ~150 lines. Shows doc_type badge, confidence, processing time, JSON output.
Day 31	Polish + Local End-to-End: Run full local end-to-end. Time: aim for <5 seconds per document. Profile slow spots. Add response caching for repeat documents (hash file → check cache). Add request logging. Confirm Dockerfile builds cleanly.
Day 32	Tests + CI: test_api.py (8 tests), test_extractor.py (5 tests), test_batch.py (3 tests), test_demo.py (1 test). Use fixtures: include 5 small test PDFs in tests/fixtures/. Run pytest, fix failures. CI green.
Week 5 — Eval Dataset + Prompt Iteration (THE MOST IMPORTANT WEEK)
V1 budgeted 1–2 days for llm_extractor.py. V2 budgets 1–2 weeks. Do NOT skip this week. 85%+ field accuracy on real invoices is what earns your $65/hr rate.
Day	Tasks
Day 33	Collect 50 Real Invoices (Eval Set) — full day: 15 from open government datasets. 15 from public invoice samples (Stripe, Square, QuickBooks). 10 from enhanced_synthetic_dataset. 10 anonymized real-world ones (ask friends for blanked invoices). Store in docintel/eval/invoices/ (01-50.pdf). Create invoice_eval.jsonl with expected JSON for each. Hand-label every field.
Day 34	Initial Eval Run: Write eval/run_eval.py — for each row in invoice_eval.jsonl, extract and compare to expected. Log per-field accuracy. Run the eval. Record baseline: vendor accuracy ___%, total accuracy ___%, date accuracy ___%. Top failure modes (rank by frequency).
Day 35	Prompt Iteration Round 1: Pick worst-performing field. Rewrite the relevant prompt section. Re-run eval. Track delta. Pick next worst field. Iterate. Document each prompt change with 1-line rationale. Target by end of day: top-3 fields at 80%+.
Day 36	Prompt Iteration Round 2 + Few-Shot: Add 1-2 few-shot examples to the invoice prompt (1 simple US invoice, 1 European-format). Re-run eval. Consider switching strategy for specific fields: dateparser for dates, regex for totals as fallback.
Day 37	Prompt Iteration Round 3 + Failure Mode Documentation: Final iteration — target 85%+ overall on key fields. Write docintel/README.md "Known Limitations" section. Final eval pass — record actual numbers. Use them in the blog post. Honesty earns trust faster than overclaiming.
Week 6 — Ship + Blog Post 2 + OCR-Niche Proposals
Day	Tasks
Day 38	Deploy DocIntel + Demo Recording: Deploy to Railway or Fly.io (test Tesseract install in Dockerfile early!). Configure GROQ_API_KEY. Smoke test all endpoints in production. Record 90-second Loom demo: drag invoice → doc_type badge, confidence, eval stats ("85% accuracy on 50-invoice test set"). Pre-review with 3 reviewers before finalizing.
Day 39	Publish to DockerHub + GitHub Public: Build and push Docker image (docintel:latest + docintel:0.1.0). Verify pullable from anywhere. Make GitHub repo public. Polish README: title, live demo link, "What it does" (3 bullets), Quick Start (3 commands), architecture diagram, eval numbers, Known Limitations. Tag v0.1.0.
Day 40	Add DocIntel to Upwork Portfolio + OCR Proposals: Add portfolio entry #2 with 3 screenshots (drag-drop demo, JSON output, eval results). Customize Template 3 for OCR/document AI jobs. Send 10 OCR-niche proposals.
Day 41	Blog Post 2 Draft: "LLM-Enhanced OCR: Beyond Tesseract." Sections: (1) The problem — traditional OCR gives text, not data. (2) The architecture + diagram. (3) Prompt engineering for invoice extraction. (4) Building an eval set — show actual numbers. (5) Production reality — latency, cost, error modes.
Day 42	Blog Post 2 Polish + Save Draft (NOT PUBLISHED in 2026): Send to 2 reviewers. Apply feedback. Save to docintel/drafts/blog_post_2_vision_first_doc_ai.md. Save LinkedIn, Reddit, HN drafts to writing_workspace/. Save eval methodology section verbatim — this is the research-credential ammunition for the 2027 arXiv preprint.
Day 43	Phase 2 Metrics Review + Phase 3 Prep: DocIntel deployed, eval accuracy, proposals sent, DockerHub pulls, GitHub stars. Open agentkit/ — re-read STATUS.md. Write Phase 3 TODO.md. Install Claude Desktop locally. Prepare MCP testing.
Day 44	Buffer + Continue Volume: Fix anything broken from the week. Continue OCR proposal volume (10 more today). Send 5 proposals on IntelAI-niche jobs (don't abandon Phase 1 niches).
Phase 2 Final Checkpoint
Deliverable	Status
DocIntel deployed at public URL	[ ]
50-invoice eval set, 85%+ key-field accuracy	[ ]
Demo recorded, README accurate	[ ]
GitHub repo public	[ ]
DockerHub image published	[ ]
Blog Post 2 DRAFTED + fact-checked (defer publishing to Q1 2027)	[ ]
Upwork portfolio entry #2 added	[ ]
30+ OCR-niche proposals sent	[ ]
Cumulative interviews (Phases 1-2): 2-5	[ ]
Cumulative contracts (Phases 1-2): 1-3	[ ]
16.4 Phase 3 — AgentKit (Weeks 7–9)
Goal: Open-source MCP server published with traction. Blog Post 3 drafted. GitHub stars (10+). MCP-niche proposals on Upwork. PRIMARY CHANNEL IS OPEN-SOURCE, NOT UPWORK.
Week 7 — MCP Server Build (6 Tools)
Day	Tasks
Day 45	Verify Extracted Repo + Install fastmcp: cd agentkit, read STATUS.md, pip install fastmcp (>= 0.4.0). Read FastMCP docs (15 min). Build mcp_server.py skeleton with 6 @mcp.tool() decorators. Add MCP resources and prompts.
Day 46	Implement Tools 1-3: query_kpis, get_company_health, detect_kpi_anomalies. Test each in isolation via Python REPL: python -c "import asyncio; from mcp_server import query_kpis; print(asyncio.run(query_kpis('Finance')))"
Day 47	Implement Tools 4-6: forecast_metric, list_available_metrics, get_executive_summary. Run mcp_server.py — confirm server starts and lists all 6 tools.
Day 48	Connect to Claude Desktop Locally: Edit claude_desktop_config.json. Add AgentKit MCP server. Restart Claude Desktop. Verify Claude sees the 6 tools. Test natural language queries through Claude. Note any tool with unclear description → improve docstring → re-test.
Day 49	Tests + Fix Bugs: Write tests/test_mcp_tools.py — 1 test per tool (6 tests minimum). Include edge cases: empty data, invalid domain, large datasets. Mock pg_store / insights / forecasting if DB not available. Run pytest, fix failures. CI green.
Week 8 — LangGraph Workflow (3 Agents)
Day	Tasks
Day 50	Install LangGraph + Build Planner Agent: pip install langgraph langchain-groq langchain. Create workflow.py with BusinessAnalysisState TypedDict. Implement planner_agent using Claude Sonnet 4.6. Test on 3 sample questions.
Day 51	Build Analyst Agent: analyst_agent routes to relevant MCP tools based on keywords in question["Finance" → query_kpis("Finance") + detect_kpi_anomalies]. Always calls get_company_health() + get_executive_summary(). Aggregates results into state["raw_data"].
Day 52	Build Reporter Agent: reporter_agent uses Claude Sonnet 4.6 with structured report format. Sections: KEY FINDING, EVIDENCE, ROOT CAUSE, RECOMMENDED ACTION, RISK IF UNADDRESSED. Parses sections into state["report_sections"].
Day 53	Wire StateGraph + Public API: Build the LangGraph StateGraph. Define analyze(question) public function. Test analyze() on 5 different business questions. Time each call (should be 5-15 seconds total).
Day 54	Demo Notebooks + Fixes: Create demos/claude_desktop_demo.ipynb (MCP setup + Claude Desktop screenshots + example queries). Create demos/langgraph_workflow_demo.ipynb (code cells + markdown commentary). Add error handling: if any agent throws, populate state["error"] gracefully.
Week 9 — Distribution + Community + Blog Post 3
Day	Tasks
Day 55	README + Demo Video: Write agentkit/README.md with architecture diagram, tools table, Claude Desktop config, Quick Start. Record 90-second demo (Claude Desktop tool calls → LangGraph workflow output). Pre-review with 2-3 MCP-aware reviewers from Anthropic Discord.
Day 56	Make Public + Submit to Lists: gh repo edit --visibility public. Tag v0.1.0. Add LICENSE (MIT), CODE_OF_CONDUCT.md, CONTRIBUTING.md. Submit PR to awesome-mcp-servers (punkpeye/awesome-mcp-servers, wong2/awesome-mcp-servers).
Day 57	Community Posts: Anthropic Discord (#mcp channel): share repo with 2-3 lines. MCP-related Discords: similar message. r/LocalLLaMA: "Built an MCP server that lets Claude do business KPI analysis — 6 tools, open source" (2 paragraphs explaining use case + architecture + link). Respond to comments throughout the day.
Day 58	Blog Post 3 Draft: "MCP Tool Design Patterns: From Database to AI Agent in 6 Tools." Sections: (1) What MCP is briefly. (2) The 6 tools I built and why. (3) Tool description as the entire UX. (4) Composability: why agentic workflows beat single tool calls. (5) Roadmap = invitation for contributors.
Day 59	Blog Post 3 Polish + Save Draft (NOT PUBLISHED in 2026): Send to 2 reviewers. Apply feedback. Save to agentkit/drafts/. Save Show HN draft (pre-written title: "MCP Tool Design Patterns: From Database to AI Agent (6 tools)"). Save Reddit + LinkedIn drafts. Do NOT publish anywhere public.
Day 60	MCP Proposals + Continue Volume: Search Upwork for "MCP" "Model Context Protocol" "agentic AI" "LangGraph". Send 5-10 MCP-specific proposals (Template 2). Continue IntelAI + DocIntel niche proposals.
Day 61	Buffer + Phase 4 Prep: Fix anything broken. Respond to GitHub issues. Open voiceflow/ repo — re-read STATUS.md. Verify Whisper / faster-whisper installs cleanly NOW (notorious dependency-hell project). Write Phase 4 TODO.md. Pre-stage audio test data.
Phase 3 Final Checkpoint
Deliverable	Status
AgentKit public on GitHub	[ ]
6 MCP tools working with Claude Desktop	[ ]
LangGraph 3-agent workflow operational	[ ]
Demo video recorded	[ ]
Submitted to awesome-mcp lists	[ ]
Posted in Anthropic Discord + MCP communities	[ ]
Blog Post 3 DRAFTED + HN/Reddit drafts saved (defer publishing Q1 2027)	[ ]
10+ GitHub stars	[ ]
10+ MCP-niche proposals sent	[ ]
Phase 1-3 cumulative: 2-5 contracts, $5-15k earned	[ ]
16.5 Phase 4 — VoiceFlow (Weeks 10–12)
Goal: Voice-to-intelligence portfolio entry. Browser recording demo is unique and memorable. Meeting analyzer / sales-call analyzer differentiates from generic transcription wrappers.
Week 10 — Voice Service + Meeting Analyzer
Day	Tasks
Day 62	Verify Whisper Install + Voice Service: cd voiceflow, re-read STATUS.md. pip install -r requirements.txt. python -c "from faster_whisper import WhisperModel; print('OK')". Download the base model (WhisperModel("base")). Test transcribe on 30-second audio sample. Measure latency. Aim for <2x realtime. If latency is bad: try "tiny" model first.
Day 63	Build services/voice_service.py: transcribe_audio(audio_bytes, language="auto") → {text, language, latency_seconds, method, segments}. Groq Whisper as cloud fallback. Test on 3 audio samples (English, French, mixed). Optional: speaker diarization (pyannote if available, fallback to None — document honestly).
Day 64	Build services/meeting_analyzer.py: MeetingAnalyzer class with analyze_meeting, analyze_sales_call, general_analysis methods. Per-analysis-type model routing (ANALYSIS_MODELS dict). All methods call Groq/Claude API, temperature=0.2, return parsed JSON. Test on 3 sample transcripts.
Day 65	Build api.py: All 8 endpoints. Wire TTS service from services/tts_service.py (edge-tts). Test /tts and /pipeline with real audio.
Day 66	Test + Polish: tests/test_voice.py (4), test_analyzer.py (6), test_api.py (5), test_pipeline.py (2). Run pytest, fix failures. Error handling for unsupported audio formats. Confirm Dockerfile builds.
Week 11 — Browser Recording Demo + Deploy
Day	Tasks
Day 67	Build demo/record.html: Single-page browser recording demo (~200 lines vanilla JS). Dark theme. MediaRecorder API. 3-second countdown before recording. Waveform visualization (Web Audio API). 3 sample-audio buttons for users who can't record. Test in Chrome, Firefox, Safari.
Day 68	Visual Polish + UX: "Stop and analyze" button is prominent. Test on real users (DM 3 friends, ask them to try it for 60 seconds). Iterate based on what was confusing.
Day 69	Deploy: Deploy VoiceFlow to Railway or Fly.io. IMPORTANT: Whisper model downloads on first container start — PRE-BAKE it into the Docker image OR have it download to a persistent volume. Cold-start without pre-baked model = 60+ seconds = kills demos. Test thoroughly in production.
Day 70	Demo Video + Pre-Review: Record 90-second Loom demo. Pre-review with 3 testers. Apply feedback, re-record if needed.
Day 71	README + GitHub Public: Write README with GIF of recording → JSON appearing. What It Does (3 bullets). Quick Start. Use Cases table. Architecture (ASCII). Make GitHub repo public. Tag v0.1.0.
Day 72	Add to Upwork Portfolio + Voice Proposals: Portfolio entry #4. Send 5-10 voice-niche proposals (Whisper, speech to text, meeting notes AI, sales call analysis, transcription pipeline).
Week 12 — Blog Post 4 + Distribution + Voice Proposals
Day	Tasks
Day 73	Blog Post 4 Draft: "From Audio to Action Items: Speech-to-Intelligence Pipelines." Sections: (1) The gap — transcription gives words, not insight. (2) Architecture + diagram. (3) Prompt design for meeting analysis. (4) Sales call analysis — CRM-paste-ready format. (5) Cost and latency reality.
Day 74	Polish + Save Blog Post 4 Draft (NOT PUBLISHED in 2026): Send to 2 reviewers. Apply feedback. Save to voiceflow/drafts/. Save subreddit posts (r/LanguageTechnology, r/speech_recognition) to writing_workspace/reddit_drafts/. Save Discord drop-ins.
Day 75	Voice Proposals Volume: Send 15+ voice-niche proposals. Lead with the browser-recording demo. Continue IntelAI / DocIntel / AgentKit niches (5+ each). Total today: 25-30.
Day 76	Phase 4 Metrics + Phase 5 Prep: VoiceFlow deployed, demo video views, voice-niche proposals sent. Open rageval/ repo — re-read STATUS.md. Write Phase 5 TODO.md. Decide: SQLite default vs PostgreSQL? Pre-stage 5-10 query/answer pairs for testing scorers.
Day 77	Buffer + Continue Volume: Fix anything broken. Continue proposal volume. Respond to DMs from community posts.
Day 78	Full Day Off (Sunday): Protect this. Burnout in month 3 kills the plan. If you must work: read 1-2 LLMOps blog posts from competitors (Phoenix, Langfuse, TruLens, Helicone) — know what you're differentiating against.
Phase 4 Final Checkpoint
Deliverable	Status
VoiceFlow deployed at public URL	[ ]
Browser recording demo works	[ ]
GitHub repo public	[ ]
Demo video recorded	[ ]
Blog Post 4 DRAFTED + community drafts saved (defer Q1 2027)	[ ]
Upwork portfolio entry #4 added	[ ]
15+ voice-niche proposals sent	[ ]
Phase 1-4 cumulative: 3-7 contracts, $10-25k earned	[ ]
16.6 Phase 5 — RAGeval (Weeks 13–15)
Goal: LLMOps observability tool published to PyPI. HIGHEST RESEARCH-VALUE PROJECT. Sets up the arXiv preprint in Phase 6. Signals to research programs that you ship production observability.
Week 13 — Evaluator + Store
Day	Tasks
Day 79	Verify Repo + Build Evaluator Part 1: cd rageval, re-read STATUS.md. pip install sentence-transformers scikit-learn numpy. Build evaluator.py with RAGEvaluator class. score_retrieval_relevance(query, retrieved_chunks) → float. score_groundedness(answer, context_chunks, model) → float (LLM-as-judge). Test each scorer on 5 sample query/answer/chunks tuples.
Day 80	Build Evaluator Part 2: Add score_faithfulness(answer, context_chunks) → float. Add calculate_cost(tokens_used, model, input_ratio=0.7) → float. Add score_interaction(...) → dict. Add multi-judge consensus: 3 models, consensus = mean, flag_for_review when stdev > 0.2.
Day 81	Build store.py: SQLite-default + Postgres-optional. init_rageval_table(). async log_interaction(...). get_metrics(days=7) → dict for dashboard. get_query_log(limit=50). get_cost_report(days=30). Add pgvector option for production scale. Test: log 20 fake interactions, query metrics, verify aggregates.
Day 82	Build api.py: All endpoints including /eval/retrieval-bench and /eval/embedding-comparison. Add OpenTelemetry export (otel_exporter.py). Test all endpoints with curl + fake data. Confirm SQLite file is created at first /eval/log call.
Day 83	Decorator API + Tests: Build rageval/decorator.py — @track(model="...") decorator. Test wrapping sync + async functions. Build 17 tests total. Run pytest, fix failures. Add DSPy integration hook (dspy_integration.py).
Week 14 — Dashboard + PyPI Publish
Day	Tasks
Day 84	Dashboard Build Part 1: cd rageval && npx create-vite dashboard --template react && cd dashboard && npm install recharts. Configure proxy to API in vite.config.js. Build App.jsx with 3 tabs: Overview | Query Log | Cost Report. Implement Overview tab (3 metric cards + LineChart + BarChart).
Day 85	Dashboard Build Part 2: Implement Query Log tab (table, color-coded rows, "Show flagged only" toggle). Implement Cost Report tab (daily cost LineChart, summary, model breakdown). Dark theme (#0f172a). Manual test: generate 50 fake interactions, verify dashboard renders.
Day 86	PyPI Package Prep: Restructure into installable package with pyproject.toml. Add CLI (rageval init / rageval serve). Test: pip install -e . in a fresh venv. rageval init → creates SQLite DB. from rageval import track → works.
Day 87	Polish README (Marketing-Critical): Title + badges. Hero (one sentence). 60-second pitch (decorator example). What It Measures (5 metrics). Comparison table (RAGeval vs Phoenix vs Langfuse vs TruLens). Quick Start. Integration Guide. Dashboard Preview (3 screenshots). Roadmap.
Day 88	Publish to PyPI: python -m build. Upload to test PyPI. Install from test PyPI in fresh venv. Upload to real PyPI. Verify: pip install rageval works. Add PyPI badge. Tag v0.1.0.
Day 89	Make GitHub Public + Submit to Lists: gh repo edit --visibility public. Add LICENSE, CODE_OF_CONDUCT.md, CONTRIBUTING.md. Release on GitHub with release notes. Submit to awesome-llmops, awesome-rag listings.
Day 90	Blog Post 5 Draft: "Observability for RAG: Why I Built RAGeval (and Why Phoenix and Langfuse Are Great Too)." Sections: state of LLMOps observability, the gap I felt, the 5 metrics and why, persona-aware groundedness, honest comparison, future as arXiv preprint.
Week 15 — Blog Post 5 + LLMOps Proposals + Preprint Pre-Work
Day	Tasks
Day 91	Polish + Save Blog Post 5 Draft (NOT PUBLISHED in 2026): Send to 2 reviewers. Apply feedback. Save to rageval/drafts/. Save Show HN draft: "RAGeval — self-hosted LLMOps observability (60-second setup)". Save Reddit, Discord drafts. Note: rageval PyPI publish is fine in 2026. Only the MARKETING CONTENT is deferred.
Day 92	LLMOps Proposals + Dashboard Deploy: Deploy dashboard to Vercel (free). Add RAGeval as Upwork portfolio entry #5. Send 10 LLMOps proposals (LLMOps, RAG evaluation, AI observability, RAG monitoring, hallucination detection). Lead with comparison table + 60-second setup demo.
Day 93	Continue Volume + Inbound Response: 20 total proposals across all niches (5 each). Respond to PyPI download spike notifications, GitHub issues, blog comments.
Day 94	arXiv Preprint Pre-Work: Start LaTeX skeleton in Overleaf. Title: "Persona-Conditioned Groundedness for RAG Systems". Abstract draft (200 words). Sections skeleton: Introduction, Related Work, Method, Experiments, Discussion, Conclusion. Identify 10-15 papers to cite. This is the preprint you submit Q1 2027.
Day 95	Phase 5 Metrics + Phase 6 Prep: RAGeval on PyPI downloads, GitHub stars, LLMOps proposals sent. Open streampulse/ — re-read STATUS.md. Write Phase 6 TODO.md. Prepare cold email list: 20-30 data/ops directors at growing SaaS companies.
Day 96	Buffer (half day): Fix anything broken. Respond to community DMs / GitHub issues. Half day off — burnout management is critical at month 4.
Phase 5 Final Checkpoint
Deliverable	Status
RAGeval on PyPI (pip install rageval works)	[ ]
GitHub repo public, 20+ stars	[ ]
Dashboard demoed (locally or live)	[ ]
Blog Post 5 DRAFTED + Show HN draft saved (defer Q1 2027)	[ ]
10+ LLMOps-niche proposals sent	[ ]
arXiv preprint skeleton started (LaTeX, abstract draft)	[ ]
Phase 1-5 cumulative: 3-7 contracts, $15-35k earned	[ ]
16.7 Phase 6 — StreamPulse + Polish + Preprint (Weeks 16–18)
Goal: Final project shipped. All 6 portfolio entries reviewed and polished. arXiv preprint drafted to submittable state. Cold email push across all 6 projects.
Week 16 — StreamPulse Build
Day	Tasks
Day 97	Verify Repo + Build api.py: cd streampulse, re-read STATUS.md. pip install -r requirements.txt. Build api.py with all endpoints including /webhook/{source}/with-vision and /live/sse. Test each with curl.
Day 98	Build connectors/webhook_receiver.py: HMAC signature verification. parse_payload. route_to_pipeline (calls DomainClassifier → DataValidator → store_kpi_metrics → broadcast to WebSocket). Test with simulated webhook calls. Build n8n node template and 3 importable workflows.
Day 99	Build dashboard/LiveDashboard.jsx: WebSocket connection to /live. State: records (last 50), volumeData, domainDist. Recharts LineChart (records/min) + PieChart (domain distribution). Live record feed table. Domain colors. SSE fallback. Dark theme. Test by streaming fake events.
Day 100	Tests + Deploy: 17 tests total. Run pytest, fix failures. Deploy to Railway or Fly.io (or ship as "docker compose up" in README, document as local-demo). Record 60-second demo video.
Day 101	README + GitHub Public + Portfolio: Write README with GIF of live dashboard updating. Supported Sources table. Architecture ASCII. Quick Start. Make GitHub repo public. Tag v0.1.0. Add StreamPulse as Upwork portfolio entry #6.
Week 17 — Cold Email Push + Blog Post 6 + Portfolio Polish
Day	Tasks
Day 102	Cold Email List Prep: Build list of 30 cold email targets. Roles: Head of Data, VP Engineering, Director of Operations, CTO. Companies: Series A/B SaaS (50-300 employees) with public data infrastructure pain. For each target: name, role, company, LinkedIn URL, email, 1 specific reason their company needs a real-time pipeline.
Day 103	Cold Email Templates + First 15 Sends: Write Template A (data infra angle for VP Eng / Director of Data). Write Template B (BI angle for COO / VP Operations). Send 15 cold emails. Track open rates, replies in spreadsheet.
Day 104	Blog Post 6 Draft: "Real-Time Domain Classification: From Webhook to KPI in 200ms." Sections: (1) The problem — real-time data lands raw. (2) Architecture. (3) Domain classifier design. (4) Webhook security (HMAC, replay protection). (5) Building a live dashboard. (6) Production reality.
Day 105	Polish + Save Blog Post 6 Draft + 15 More Emails: Polish, send to 2 reviewers, apply feedback. Save to streampulse/drafts/. Send 15 more cold emails (cumulative 30). Continue Upwork volume on all niches.
Day 106	Portfolio-Wide Polish (All 6 Projects): For each of 6 projects: demo URL works in incognito browser, README < 250 lines and accurate, LICENSE present, CI green, Loom demo URL live, GitHub repo description matches README, PyPI/DockerHub pages current, Upwork portfolio entry has 3+ screenshots.
Day 107	All-Niche Volume + Inbound: Send proposals across all 6 niches. Respond to cold email replies, GitHub issues, DMs, Upwork inbound. Schedule 2-3 discovery calls if you have inbound interest.
Day 108	Buffer (half day + half off): Fix anything broken. Update Notion with cumulative metrics. Half day off (Sunday).
Week 18 — arXiv Preprint Draft + Plan Q4
Day	Tasks
Day 109	Preprint Section 1-2 (Intro + Related Work): Open Overleaf project from Day 94. Write Section 1 Introduction (~800 words): the standard groundedness problem, why multi-persona RAG is increasingly common, your contribution, roadmap. Write Section 2 Related Work (~1000 words): RAGAS/ARES/TruLens-Eval, LLM-as-judge methodology, multi-persona/multi-agent systems.
Day 110	Preprint Section 3 (Method): Formal definition of groundedness(q,a,c) vs groundedness(q,a,c,p). The persona-conditioned prompt (show exact text). Implementation in RAGeval (decorator → per-persona scores). Calibration: how you set scoring scale, few-shot examples.
Day 111	Preprint Section 4 (Experiments): Generate 200-500 query-answer-context tuples from IntelAI 9-persona system. Score with both standard and persona-conditioned groundedness. Report: average score per persona (table), score distribution (histogram), divergent cases (qualitative analysis). Limitations: sample size, single LLM judge, no human eval (yet).
Day 112	Preprint Section 5-6 (Discussion + Conclusion): What divergent cases reveal about RAG eval blind spots. Implications for production RAG. Future work: human eval, fine-tuned judge, real-time monitoring. Conclusion (300 words). Polish abstract. Build figures: system diagram, score distribution, divergence scatter.
Day 113	Send Preprint Draft for Review + Cold Email Round 3: Compile PDF. Send to 3-5 reviewers (academic contacts, RAG-eval practitioners from blog comments). Send 15 more cold emails. Send 20 more Upwork proposals. Subject: "Draft preprint on persona-conditioned groundedness — feedback before arXiv submission?"
Day 114	Phase 6 Metrics + 18-Week Retrospective: Full retrospective. 6 deployed projects, 6 blog drafts, 2 PyPI packages, OSS artifacts, total proposals, total interviews, total contracts, total earned. Which project drove most interest? Which channel converted? Where did you waste time? What would you change? Write in 500-1000 words — this becomes part of the 2027 LinkedIn launch post.
Day 115	Q4 Planning + 2027 Launch Prep: Plan weeks 19-30 (Q4 2026): continue weekly Upwork proposals, maintain GitHub repos, apply finishing pass to each blog draft monthly, polish arXiv preprint to submittable form (still NOT submitted in 2026 — timed for Q1 2027 launch), build personal portfolio site (locally, NOT deployed). Draft research-program statements of purpose (outline only). Identify 3 workshop deadlines in Q1 2027.
Day 116	Final Preprint Polish (NOT submitted in 2026): Apply review feedback. Polish formatting, figures, bibliography. Final read-through. Save as: writing_workspace/preprint_v_final_2026.pdf. Calendar reminder: "Submit preprint to arXiv Q1 2027 — Tuesday morning UTC."
Day 117	Buffer + Final Sweep: All 6 demos still respond. All 6 GitHub READMEs current. Upwork profile has all 6 entries. Notion proposal log archived. All 6 blog drafts and preprint saved. Personal site code committed (private repo). LinkedIn cornerstone draft + 20+ short drafts in writing_workspace/. Plan real break: 3-5 days actually offline before Q4 ramp.
Day 118	Done (End of Week 18): Take the day completely off. You earned it. Tomorrow Q4 begins, at a sustainable pace. Q1 2027 the multi-channel launch begins.
Phase 6 Final Checkpoint = End of 18-Week Plan
Delivered Across 18 Weeks	Status
6 deployed projects with live demos (where always-on tier applies)	[ ]
6 technical blog posts DRAFTED + fact-checked (publish Q1 2027)	[ ]
2 PyPI packages (omnismart-personas, rageval) with users	[ ]
5 GitHub public repos (AgentKit, DocIntel, VoiceFlow, RAGeval, StreamPulse)	[ ]
1 DockerHub image (DocIntel)	[ ]
1 arXiv preprint POLISHED and review-ready (submitted Q1 2027)	[ ]
Upwork portfolio at 6 entries	[ ]
Cumulative: $15-40k earned (depending on conversion)	[ ]
3-7 ongoing or completed client relationships	[ ]
150-300 LinkedIn connections (passively accumulated)	[ ]
Personal portfolio site coded (private), ready to deploy Q1 2027	[ ]
20-30 short LinkedIn drafts written, ready to drip-feed in 2027	[ ]
6 Show HN drafts, 6 Reddit drafts, LinkedIn cornerstone draft	[ ]
Material for 2027 multi-channel launch fully prepared	[ ]
Research-credential foundation set (deployed systems + preprint + community + client references)	[ ]
16.8 Weekly Metrics, Decision Gates, And Cumulative Tracker
Weekly Tracker Template
WEEK N (DATE):
  Build:
    Project worked on: _______
    Hours of build time: ___
    Tests added: ___
  Distribution:
    Proposals sent: ___
    Cold emails sent: ___
    Blog post drafted: ___ % complete
    Community posts: ___
  Outcomes:
    Replies: ___
    Interviews: ___
    Contracts started/ended: ___
    Earned this week: $___
    GitHub stars added: ___
    PyPI downloads: ___
  Wellness:
    Hours slept: ___
    Days off: ___
    Mood (1-10): ___
  Reflection (1-3 sentences):
    What went well? ___
    What was a slog? ___
    Adjustment for next week? ___
Decision Gates By Phase
End of Phase	GO Criteria	PAUSE If
Phase 1 (Week 3)	50 proposals sent + 1 interview + demo live	50 proposals + 0 interviews → demo/messaging audit before Phase 2
Phase 2 (Week 6)	DocIntel live + 30 OCR proposals + cumulative 1+ contract	2 phases in and still 0 contracts → external audit
Phase 3 (Week 9)	AgentKit public + 10+ stars + Blog Post 3 drafted	AgentKit has 0 stars after 5 days → README/demo audit
Phase 4 (Week 12)	VoiceFlow demo works + cumulative 3+ contracts OR inbound from communities	Cumulative <2 contracts → reduce build velocity, increase proposal velocity
Phase 5 (Week 15)	RAGeval on PyPI + Blog Post 5 drafted + preprint started	Preprint draft has no shape → use Phase 6 buffer to extend
Phase 6 (Week 18)	Day 114 retrospective — all 15 deliverables in final checkpoint	Any deliverable missing → spend buffer days closing the gap
Cumulative Tracker (Month 1 Through Month 12)
Month	Projects Live	Total Props	Contracts (TC)	Earned	PyPI Pkgs
M1	1	50	0-1	$0-2k	0
M2	2	120	1-2	$2-4k	1
M3	3	200	2-3	$4-8k	1
M4	4	270	3-4	$8-15k	2
M5	5	320	3-5	$12-22k	2
M6	6	360	3-5	$18-30k	2
M9	6 + maint	400+	4-6	$35-55k	2-3
M12	6 + papers	450+	4-6	$50-80k	3 + preprint
Section 17: Daily / Weekly Operating Rhythm
Time Block	Activity
Mornings (4h, focused)	Build the current phase's project. No proposals, no email, no Slack. Pure deep work.
Early Afternoon (1h)	Lunch + read 1 paper or blog post in your niche (Anthropic blog, OpenAI research, NeurIPS proceedings).
Afternoon (2h)	Send proposals (5/day target). Respond to client messages. Review and respond to community posts (DMs, GitHub issues).
Evening (1h, optional)	Light writing on current blog post. Or: review code from a research paper. Or: lurk and learn on LinkedIn.
Monday-Friday	Build (mornings), Pipeline (afternoons), Learn (evening)
Saturday	Buffer + content. Catch up on week's leftover work. Progress on current blog post.
Sunday	OFF OR review and plan. Notion log review: what's converting? Next week's task list.
Sundays off matter. Burnout in month 3 kills the plan. Protect them.
Section 18: Capacity Rules (When To Stop Applying)
Active Clients	Client Work	Pipeline Work	Status
0 active clients	0%	100%	Apply hard — 10/day target
1 active client	50%	50%	Steady pipeline — 5/day
2 active clients	70%	30%	Reduce pipeline volume — 3/day
3 active clients	90%	10%	Almost no new proposals — 1/day
4+ active clients	100%	0%	STOP applying entirely — focus on delivery quality

When 3+ clients are active: Do not respond to new Upwork DM invitations. Do not send new proposals. Auto-respond to cold emails with "Thanks, currently at capacity until [date]." Finish current commitments well — quality at this stage produces reviews that compound forever.
Section 19: When To Pivot Or Quit
Pivot Triggers
Trigger	Action
30 proposals, 0 interview replies	Niche or messaging is wrong. Pause, revise demo + proposal, get external feedback.
5 interviews, 0 offers	Demo or pricing is wrong. Watch the interview replay (Upwork records audio). Get peer review on demo.
3+ months, 0 clients	Channel is wrong. Switch primary channel temporarily (try cold email or community for next 30 days).
Quit/Postpone Triggers (Rare but Real)
Trigger	Action
A full-time job offer at a top AI lab	Strongly consider taking it (sometimes the freelance path is the slower path)
A research-fellowship offer (Anthropic Fellows, etc.)	Almost always take it. The credentials compound faster.
6 months, 0 paid contracts	Step back. Restructure. Get a structured mentorship or bootcamp on freelancing specifically — it's a separate skill from coding.
The 4-Month Checkpoint
By Week 16, you should have: 2+ paying contracts completed, 4 blog posts drafted, 4 portfolio entries, cumulative earnings of $5–20k. If you're materially below this, STOP building and diagnose. Get a real review from someone successful in AI freelancing — pay $200 for a 1-hour audit. That's the best money you can spend.


PART VI — INFRASTRUCTURE, TOOLING, AND COST REALITY
Section 20: Hosting Tiers (Railway, Fly.io, Local-Only)
V1 said "Railway free tier sufficient." This is wrong for 6 always-on projects with PostgreSQL. 6 projects × Railway Hobby ($5/month) + 6 PostgreSQL × $5 = $60/month minimum. Tier your hosting instead.
Tier	Projects	Hosting	Cost/Mo
Always-On (strongest demos)	IntelAI, DocIntel	Railway or Fly.io	$15-25
Cold-Start (secondary demos)	AgentKit, RAGeval	Fly.io free machines (cold-start ~3s)	~$0
Local-Only (video demos)	VoiceFlow, StreamPulse	None — clone + docker compose up in README	$0

Total demo cost: ~$25-40/month. This caps your monthly hosting even with 6 projects.
20.3 Fly.io for Cold-Start Demos
# fly.toml
[experimental]
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0  # Allows full cold-start (free between requests)
 
# First request spins up the machine in ~3 seconds.
# Subsequent requests are fast.
# Perfect for portfolio demos.
20.4 Database Tier Strategy
•	Tier 1 PostgreSQL: Railway add-on or Supabase free tier (for always-on projects)
•	Tier 2 SQLite: for projects where Postgres is overkill (rageval default, simple ingestion) — saves $5/mo
•	Tier 3 DuckDB: embedded, no separate process (StreamPulse analytics queries)
Section 21: Pipeline Monitoring (Proposals, Demos, Outcomes)
21.1 The Notion / Airtable Proposal Log
One row per proposal. Columns:
Date sent | Job title (and link) | Niche | Demo used | Template used |
Client's prior reviews | Client country | Response (None/Interview/Hired) |
Outcome (Hired/Withdrew/Ghosted) | Lesson / note
21.2 Weekly Review Questions
62.	Which niche had the highest reply rate this week?
63.	Which demo was used in the proposals that got replies?
64.	What patterns do "no reply" proposals share?
65.	Are you sending too many to high-competition jobs (50+ applicants)?
66.	Are clients consistently asking the same questions in interviews? (If yes, update your proposal template to preempt them.)
21.3 The Minimum Viable Analytics
After 60 days, you should know:
Metric	Best	Worst
Niche by reply rate	[niche]	[niche]
Demo by interview rate	[demo]	[demo]
Template by hire rate	[T#]	[T#]
Best client country	[region]	[region]
Double down on the best. Drop the worst. This data takes 60 days to be meaningful — don't optimize too early.
Section 22: Tools You Need (Free Or Near-Free)
Tool	Purpose	Cost
Loom	Demo video recording	Free (5min clips)
Notion or Airtable	Proposal + content tracker	Free
GitHub	Code hosting	Free (public)
PyPI	Package publishing	Free
DockerHub	Image publishing	Free
Railway / Fly.io	Deployment	$20-40/month
Supabase	Postgres (alternative)	Free tier
Personal site (Vercel)	Blog hosting (2027)	Free
Medium / Substack	Secondary blog distribution (2027)	Free
arXiv	Preprint hosting (2027)	Free
Cal.com or Calendly Free	Booking links	Free
Buttondown / EmailOctopus	Newsletter (optional 2027)	Free under 1k subs
Overleaf	LaTeX for preprints	Free
Add Upwork Connects costs. Total operating expense: ~$50-60/month. Reasonable for a freelance business.
PART VII — POSITIONING, PRICING, AND PROPOSALS
Section 23: Vertical Niching Within Each Project
Project	PRIMARY Vertical	SECONDARY Vertical	TERTIARY Vertical
IntelAI	Series A SaaS analytics ("ARR, churn, headcount built-in")	Healthcare KPI + compliance reporting	ESG / sustainability reporting (EU CSRD-driven)
AgentKit	"MCP server for any business intelligence stack"	AI agency / consultancy white-label	Internal R&D for AI-first product teams
DocIntel	Invoice AP automation (high volume)	Legal contract review	Medical records extraction (highest premium)
VoiceFlow	Meeting transcription + action items (broad market)	Sales call analyzer + CRM integration	Customer support call quality monitoring
RAGeval	"Drop-in observability for FastAPI + LangChain teams"	AI teams scaling RAG (50+ queries/day)	Compliance teams needing audit logs
StreamPulse	Real-time pipeline for ops teams (replace manual data entry)	Custom n8n / Zapier alternative	Webhook-driven analytics for SaaS dashboards
Section 24: Upwork Profile (Refined)
24.1 Profile Title
AI Systems Engineer | RAG · MCP Agents · Document AI · LLMOps · FastAPI
Why this title works: "AI Systems Engineer" = premium positioning. RAG = highest search volume AI skill. MCP Agents = trending, rare, high rates. Document AI = consistent volume. LLMOps = elite, growing demand. FastAPI = largest Python API framework by job volume.
24.2 Profile Overview (First 300 Chars Are Critical)
I build production AI systems that work after deployment — not just in demos.
 
Portfolio includes 6 deployed AI projects with live demos and open-source
artifacts on PyPI/GitHub:
 
→ IntelAI: 60-endpoint AI analytics backend with 9 C-suite AI personas.
  Each persona has role-based data scoping. Bilingual (EN/FR). Deployed.
 
→ AgentKit: MCP server exposing business intelligence to Claude Desktop,
  Cursor, and any LangChain agent. Open-source on GitHub.
 
→ DocIntel: PDF/image → structured JSON in <1 second with 85%+ accuracy
  on invoice fields. LLM-enhanced extraction beyond pure OCR.
 
→ VoiceFlow: Audio → meeting notes or sales CRM data automatically.
  faster-whisper + Groq intelligence layer.
 
→ RAGeval: LLMOps observability for RAG systems. PyPI package with
  drop-in @track decorator. Self-hosted, SQLite default.
 
→ StreamPulse: Real-time data pipeline with domain auto-classification
  and live WebSocket dashboard.
 
TECH: FastAPI · LangChain · LangGraph · ChromaDB · PostgreSQL · React
STACK: Claude Sonnet 4.6 · Groq LLaMA 3.3 · sentence-transformers · faster-whisper
PUBLISHED: rageval (PyPI) · omnismart-personas (PyPI) · 6 open-source repos
24.3 Skills Tags
Category	Tags
Primary (high search)	RAG (Retrieval-Augmented Generation), LangChain, FastAPI, Python, AI Chatbot Development, PostgreSQL
Secondary (premium niches)	LangGraph, ChromaDB, Docker, React, Groq
Tertiary (rare, high rates)	MCP (Model Context Protocol), LLMOps, Agentic AI, AI Observability, Sentence Transformers
Supporting	OCR, Speech-to-Text, Whisper, Prometheus, n8n, LiteLLM
Section 25: Pricing By Channel
Channel	Starting Rate	At 5 Reviews	At 20 Reviews
Upwork (cold inbound)	$65/hr	$85/hr	$110/hr
Upwork (warm referral)	$75/hr	$95/hr	$130/hr
Cold email (direct)	$85/hr	$110/hr	$150/hr
LinkedIn 2027 inbound	$95/hr	$130/hr	$170/hr
Research-aligned	Variable	Variable	Rate secondary to credentials ($100-150/hr typical)

Why not compete on price: A $25-40/hr "AI engineer" attracts clients who want the cheapest option. These clients almost universally pay late, demand scope creep, leave bad reviews, and don't understand technical work. $65/hr filters them out. Your codebase justifies it from day one.
25.2 Fixed-Price Structure
Project Size	Milestone Structure
Under $2,000	Milestone 1 (40%): Core feature working + deployed. Milestone 2 (60%): Full feature + tests + docs.
$2,000 - $5,000	Milestone 1 (30%): Architecture + first endpoint. Milestone 2 (40%): Full backend. Milestone 3 (30%): Frontend + tests + deploy.
Over $5,000	Milestone 1 (20%): Spec + first milestone delivered. Milestone 2 (30%): Core features working. Milestone 3 (30%): Full system. Milestone 4 (20%): Testing + deploy + docs.
Section 26: Six Proposal Templates (Niche-Specific)
Template 1 — RAG / AI Chatbot Jobs
[Opening — reference their SPECIFIC job post]
You mentioned needing a RAG system that handles [their specific docs/domain].
The architecture I'd use: hybrid retrieval (BM25 + vector) with ChromaDB,
using sentence-transformers for embeddings — CPU-friendly, no GPU needed.
 
[Demo link — second paragraph always]
I've deployed this pattern in production: [IntelAI demo URL]
The Chat page shows what persona-aware RAG looks like — source citations,
streaming responses, role-based data scoping.
 
[3 specific technical questions]
To scope this accurately:
1. What document formats and roughly what volume? (Affects chunking strategy)
2. Do users need to see source citations, or just answers?
3. Any authentication requirement — single user or multi-user with roles?
 
[Clear timeline]
Based on your description: ingest + RAG working in week 1,
persona/UI customization in week 2.
 
Yacine
Template 2 — MCP / Agentic AI Jobs
[Opening]
I see you need [MCP server / agent workflow / tool integration].
I've built a production MCP server exposing business intelligence tools
that works with Claude Desktop, Cursor, and any LangChain agent.
 
[Demo]
Demo video showing real data flowing through Claude Desktop: [AgentKit Loom URL]
The agent calls query_kpis(), detect_anomalies(), and forecast_metric()
against a live PostgreSQL database.
 
[Technical questions]
A few things to understand your use case:
1. Which AI client(s) need to consume the MCP tools? (Claude, Cursor, custom?)
2. What data sources should the tools access? (DB, API, files?)
3. Do you need the full LangGraph 3-agent workflow, or just the MCP server?
 
[Timeline]
MCP server with your tools: 3-4 days.
LangGraph workflow on top: additional 3-4 days.
Template 3 — OCR / Document Processing Jobs
[Opening — paste example JSON output directly in the proposal]
Your job asks for [invoice extraction / PDF data / document classification].
Here's the output my pipeline produces for invoices:
 
{
  "invoice_number": "INV-2025-4821",
  "vendor_name": "Acme Corporation",
  "invoice_date": "2025-02-01",
  "due_date": "2025-02-15",
  "subtotal": 11500.00,
  "tax": 950.00,
  "total": 12450.00,
  "currency": "USD",
  "confidence": 0.94
}
 
[Demo]
Live demo where you can upload your own document: [DocIntel URL]
85% field accuracy on a 50-invoice eval set.
 
[Questions]
1. What document types? (Invoice/contract/receipt/form/other?)
2. Are these native PDFs or scanned images? (Affects OCR approach)
3. Do you need batch processing, or single-document API?
Template 4 — Voice / Speech AI Jobs
[Opening]
You need [meeting transcription / voice assistant / speech processing].
I run faster-whisper locally (CPU-only, no GPU required) with WhisperX
for alignment — both work offline, no cloud dependency.
 
[What differentiates me]
The interesting part isn't transcription (that's free with Whisper).
It's the intelligence layer: my meeting analyzer extracts structured
action items with owner + deadline + priority, and my sales call analyzer
outputs CRM-ready JSON directly.
 
[Demo]
Browser demo — record your voice, see structured output in real-time: [VoiceFlow URL]
 
[Questions]
1. Is this real-time streaming or batch (upload file, get result)?
2. What's the downstream integration? (Notion, CRM, DB, custom?)
3. Do you need speaker diarization (who said what)?
Template 5 — LLMOps / AI Observability Jobs
[Opening]
You're asking exactly the right question. Most RAG systems are black boxes —
you find out they're hallucinating after users complain.
 
[Your differentiator]
I built RAGeval: drop-in observability for RAG. It scores every query on:
- Retrieval relevance (are retrieved chunks related to the query?)
- Groundedness (does the answer stay within the retrieved context?)
- Cost per query (so you can budget at scale)
Flags potential hallucinations automatically. Self-hosted, SQLite default,
60-second setup. Published to PyPI.
 
Honest comparison: Phoenix and Langfuse are great if you need a full UI stack.
RAGeval is for teams who want drop-in in one container with no infra overhead.
 
[Demo]
Dashboard demo: [RAGeval URL]
 
[Technical depth]
I instrument at the LangChain callback level — no changes to your existing chain logic.
Just add the @track(project="my_rag") decorator.
 
[Questions]
1. What's your current RAG stack? (LangChain/LlamaIndex/custom?)
2. What's your daily query volume approximately?
3. Do you need real-time alerts or daily digest?
Template 6 — Data Pipeline / ETL Jobs
[Opening]
You need [webhook processing / real-time ETL / data pipeline].
The pattern I've implemented: webhook → domain classification →
validation → PostgreSQL + live dashboard.
 
[Specific to their job]
For your use case ([their specific source]), the pipeline would:
1. Receive the [webhook/API/file]
2. Classify and validate each record (Finance/HR/Ops/ESG/IT)
3. Route to the correct table/schema
4. Update your dashboard in real-time via WebSocket
 
[Demo]
Live pipeline demo: [StreamPulse URL]
Watch records flow in real-time after a webhook fires.
Bonus: first-class n8n integration — custom n8n node + 3 importable workflows.
 
[Questions]
1. What's the data source? (Webhook, API polling, file upload, streaming?)
2. What's the expected volume? (Records/hour or records/day?)
3. Does the output need to feed another system, or just PostgreSQL?
Section 26.5: Applying Your Projects To Real Job Posts — A Worked Case Study
This section is a live case study. As you build the six projects, you'll encounter actual Upwork job posts whose requirements map across multiple projects. This section walks you through one specific real-world post (the "Equipment Sourcing System" job, $5,000 fixed, 4-6 weeks) and shows you exactly how to apply.
The Job Post (Summary)
Field	Detail
Title	Build an AI-Powered Equipment Sourcing System (Multi-Source Aggregator)
Budget	$3,500–$5,500 USD fixed price
Timeline	4-6 weeks
Level	Expert
Proposals	20-50 (moderate competition)
Client's problem	Purchases specialized used equipment from government surplus, marketplaces, dealer liquidations. Current keyword-based scraper produces too much noise.
Client's solution	Vision-first classification (LLM looks at every photo, identifies relevant equipment regardless of title/description)
What the system does	Ingests listings from 8+ sources (gov APIs, marketplace APIs, RSS feeds, email). Runs every photo through a local vision model. Ranks results. Mobile-friendly dashboard. Daily digest email + push notifications. Runs unattended with self-monitoring.
Client's existing infra	Workstation server with Ollama, n8n, Gemma 4 (vision-capable), and Llama 3.3 70B already installed.
4 GATING QUESTIONS	(1) Multi-source pipeline — link to code/case study. (2) Local vision models experience. (3) Handling duplicate listings. (4) One pre-bid question. NOTE: Bids that don't address all four points will not be considered.
Why This Job Is Tailor-Made For Your Stack
Client Requirement	Your Project That Proves It
Vision-first photo classification	DocIntel Route B: Ollama + Llama 3.2 Vision + /classify-image endpoint
Multi-source ingestion (8+ sources)	StreamPulse (6+ sources, classifier, n8n integration, webhook receiver)
Local LLM (Ollama already installed)	Both DocIntel + StreamPulse support Ollama via LLM_LOCAL env var
n8n workflow integration	StreamPulse custom n8n node template + 3 ready-to-import workflows
Unattended + self-monitoring	StreamPulse Prefect 3 orchestration flow + /pipeline/status endpoint
Duplicate dedup across sources	Three-layer: content-hash + perceptual image hash (pHash) + embedding similarity
Mobile-friendly dashboard	StreamPulse React dashboard (responsive design)
Daily digest email	Reuse IntelAI's email infrastructure (Gmail integration from dispatcher.py)
CRITICAL: You cannot apply to this post until DocIntel + StreamPulse + IntelAI are all live with public READMEs and Loom demos. That's the end of Phase 6 of the 18-week plan. If this exact post shows up before Phase 6, bookmark it and revisit in October.
The Winning Proposal (Annotated)
Hi,
 
I read your post twice. The vision-first classification idea is the right
move — keyword scrapers fail on the exact case you described (mislabeled
or vague listings), and a local vision LLM solves it cleanly.
 
I've built each piece of what you're describing in open source.
Three of my projects compose into roughly the system you specified:
 
→ DocIntel — vision-first document/image classification. Route B is local
  Ollama + Llama 3.2 Vision (the exact pattern you need). Endpoint
  /classify-image takes image + candidate categories, returns category +
  confidence + reasoning with the local-vision route selected via config:
    Demo: <DOCINTEL_DEMO_URL>
    Repo: github.com/<yourname>/docintel
 
→ StreamPulse — real-time multi-source ingestion pipeline with a domain
  classifier and a custom n8n node. Sources are pluggable (webhooks,
  REST APIs, Gmail polling, RSS, Sheets). Live React dashboard,
  self-monitoring via /pipeline/status, Prefect 3 orchestration for
  the unattended case.
    Demo: <STREAMPULSE_DEMO_URL>
    Repo: github.com/<yourname>/streampulse
 
→ IntelAI — provides the email-digest + push notification infrastructure.
    Repo: github.com/<yourname>/intelai
 
Now to your four questions:
 
(1) Previous multi-source pipeline:
StreamPulse (link above) ingests from 6+ sources (Gmail, Google Sheets,
n8n webhooks, REST APIs, CSV upload, JSON) into a unified classified store
with a live dashboard. The Equipment Sourcing system is the same pattern
with different sources — I'd plug in your government auction APIs, marketplace
APIs, RSS feeds, and email-based saved searches as StreamPulse sources,
then add the vision-classification step between ingest and store.
 
(2) Local vision model experience:
DocIntel ships with two local-vision options: Llama 3.2 Vision 11B and
Qwen 2.5-VL 7B, both via Ollama. For the equipment-photo use case I'd
start with Llama 3.2 Vision 11B (your server already has Llama 3.3 70B,
so adding 3.2 vision variant is a 6GB download) and benchmark against
Gemma 4 Vision (which you already have installed).
 
(3) Duplicate listings across sources:
Three-layer dedup, hardest-first:
  Layer 1: Content-hash dedup (SHA-256 of normalized title + price + seller).
            Catches exact reposts.
  Layer 2: Perceptual image hash (pHash via imagehash library).
            Catches same listing posted with renamed title.
  Layer 3: Embedding-similarity dedup. Joint embedding of (title text +
            image embedding), cosine similarity > 0.93 = likely duplicate.
Layers 1+2 cover ~90% of cases at zero LLM cost. Layer 3 is the safety net.
I'd ship Layer 1+2 by week 2, Layer 3 by week 4.
 
(4) My pre-bid question:
What's the daily volume of new listings across all 8 sources, and is there
a latency SLA per listing? This shapes the architecture fundamentally:
  - <500 listings/day, no real-time SLA → batch-process nightly. 4-5 weeks.
  - 500-5000/day, near-real-time → stream through n8n + StreamPulse. 5-6 weeks.
  - >5000/day → slimmer vision model + 2-stage pipeline. 6+ weeks.
 
Timeline: 4-6 weeks fits my realistic estimate. Structured as:
  Week 1 — discovery, source enumeration, integration scoping
  Week 2 — ingestion pipeline + Layer 1+2 dedup
  Week 3 — vision classification + ranking
  Week 4 — dashboard + digest emails + push notifications
  Week 5 — self-monitoring + dedup Layer 3 + tuning
  Week 6 — buffer + handoff documentation
 
Bid: $5,000 fixed, milestoned at 30/30/40 (after weeks 2, 4, and 6).
 
Available for the video call within 48 hours of your reply.
 
— Yacine
Why This Proposal Wins (Diagnosis)
Element	Why It's There
Length (~1000 words)	Post explicitly says "Bids that don't address four points will not be considered" — this client wants thoughtful length. A 200-word proposal would be filtered out.
Demo placement	First demo link appears in line 7. Second in line 13. Third in line 18. Before any gating answers — by the time the client reads Q1, they've already clicked at least one demo.
Q1 answered	StreamPulse + concrete mapping to their use case ("plug in your government auction APIs"). Not generic.
Q2 answered	Two specific local vision models + a benchmarking plan comparing against their existing Gemma 4. Shows you've thought about their actual hardware.
Q3 answered	Three-layer technical strategy + week-numbered delivery. Proves you've thought about the real edge case.
Q4 answered	Three scenarios scaled to volume, each with different architecture and timeline. Shows architectural depth.
Bid at top of range	$5,000. Cheap bids get deprioritized per the post. Coming in at the top with clear scope signals confidence.
30/30/40 milestones	Reduces client risk while protecting your cashflow. The 30% upfront-after-week-2 is the trust-builder.
The Generalized Pattern For Future Job Posts
67.	INVENTORY THE COMPONENTS: List every distinct capability the post asks for. For each, note which of your 6 projects demonstrates it.
68.	DECIDE IF YOU CAN COVER 70%+: If yes → apply with composition proposal. If no → either decline or apply with honest scope.
69.	MAP GATING QUESTIONS TO PROJECT EVIDENCE: Every question becomes "here's the project/demo/code that proves I've done this exact thing before."
70.	ADD ONE THOUGHTFUL META-QUESTION: The pre-bid question frames an architectural decision based on their answer. Must be a question whose answer meaningfully changes the technical approach.
71.	QUOTE AT TOP OF STATED RANGE: If they say "$3,500-$5,500," quote $5,000 or $5,500. Cheap bids signal you don't believe in your work.
72.	STRUCTURE MILESTONES: Never 100% on completion. Always at least 3 milestones. First one paid early enough that you've recouped most of your risk.
73.	VIDEO CALL READINESS: If the post mentions a call, signal you're ready with a live demo on their data or a whiteboard sketch.
Three More Job Archetypes You'll Match
Archetype	Projects Used	Quote
Archetype A: "Build me a chatbot over my docs" ($1,500-$5,000)	IntelAI + DocIntel + RAGeval. Lead with persona-aware RAG + vision-first ingestion + groundedness observability.	$3,500-$5,000
Archetype B: "MCP server / Claude Desktop integration" ($800-$3,000)	AgentKit. Show demo video of Claude Desktop calling real tools. Bonus: offer CrewAI or LangGraph workflow on top.	$1,500-$3,000
Archetype C: "Sales-call analyzer / meeting summarizer" ($1,500-$6,000)	VoiceFlow + RAGeval. Browser-recording demo is memorable. Claude Sonnet 4.6 for sales analysis. Ongoing quality monitoring.	$2,500-$6,000
A Discipline Note On Application Velocity
Once your portfolio is at 4+ live projects, stop spraying generic proposals. The composition-based proposals in this section take 30-45 minutes each to write properly. You can produce 3-5 of them per day maximum. That's right for the Phase 6+ stage.

The volume game (10 proposals/day) is what gets you the first 1-3 contracts when you have nothing else. Once you do, proposal quality scales the rate — better proposals lead to higher-budget contracts with happier clients.
PART VIII — RISK AND REALITY CHECK
Section 27: Things That Will Go Wrong (Plan For Them)
27.1 Technical Surprises
Risk	Probability	Mitigation
Whisper / faster-whisper dependency hell on Railway	High	Test deploy in Phase 4 Day 1, not Day 10. Pre-bake model into Docker image.
LLM extraction prompts produce inconsistent JSON	Very High	Plan 1-2 weeks of prompt iteration with eval dataset. Use json.loads with try/catch + retry.
WebSocket auth/CORS issues in production	High	Add to test suite explicitly. Test from Railway before recording demo.
pyannote diarization fails to install	High	Documented fallback to no-diarization in README. Honesty wins clients.
ChromaDB memory blowup with full dataset	Medium	Use streaming retrieval, batch ingestion. Monitor container memory.
Railway / Fly.io free tier exhausted faster than expected	High	Tier the demos per Section 20. Cap two always-on, rest cold-start or local.
Frontend Recharts performance on big datasets	Low	Limit chart data points to last 20-50 records per chart.
27.2 Market Surprises
Risk	Probability	Mitigation
First 30 Upwork proposals get 0 replies	Very High	Plan for this, don't panic. Diagnose at 30-proposal mark. Get external review.
The niche you targeted has too much competition	Medium	Track in Notion, pivot at 30-proposal mark.
Clients ghost mid-interview	High	Don't take it personally; this is normal.
A "great" client turns out to be slow-paying	Medium	Always milestone-based; verify payment before sprint.
MCP demand on Upwork stays thin in 2026	High	Treat AgentKit as OSS-first, not Upwork-first.
Phoenix or Langfuse announce a self-hosted lightweight version	Medium	Make RAGeval's persona-aware metric the durable differentiator. OSS stays differentiated.
27.3 Personal Surprises
Risk	Probability	Mitigation
Burnout in month 2-3	Very High	Protect Sundays. Cap proposal volume. Three active clients = stop applying.
Discouragement after 60 days, $0 earned	High	Re-read Section 19. The funnel takes 60-90 days. This is normal.
Imposter syndrome reading other freelancers' portfolios	High	They had 12 months to build that. You're in month 2.
Tempted to take a $30/hr "easy" gig	High	Don't. Costs are bigger than gains. Wrong clients = bad reviews.
Family / friends questioning the path	High	Show them the live demo + the income trajectory chart.
27.4 The "First Paid Client" Trap
When your first paid contract arrives, the temptation is to celebrate and deliver fast. Common mistakes:
•	Over-promising scope to win it
•	Under-pricing to "get the review"
•	Working 12-hour days, burning out by week 2

Better: deliver well, on time, at your stated rate, with no scope creep. The first review is more valuable than the first $1,000.
Section 28: Milestone Expectations (What Realistic Looks Like)
Month	Portfolio	Proposals	Contracts	Earned	OSS
Month 1	1 entry	50	0-1	$0-1k	0 packages
Month 2	2 entries	120	1-2	$2-4k	1 package
Month 3	3 entries	200	2-3	$4-8k	1 package
Month 4	4 entries	270	3-4	$8-15k	2 packages
Month 5	5 entries	320	3-5	$12-22k	2 packages
Month 6	6 entries	360	3-5	$18-30k	2 packages
Month 9	6 + maint	400+	4-6	$35-55k	2-3 packages
Month 12	6 + papers +1 preprint	450+	4-6	$50-80k	3 packages
28.1 Reading the Table
•	Bottom of range = slow conversion, primarily 1-2 small clients
•	Top of range = strong conversion, 2-3 ongoing + multiple small projects
•	Both are normal. Don't be disappointed by the lower number.
28.2 The "Month 6 Reset" Milestone
By month 6:
•	If you're at the bottom of the range: reassess niche, demo, pricing. Request an external review.
•	If you're at the top of the range: increase rates by 20%.
•	Either way: start LinkedIn 2027 prep work in earnest (build content library, connect with everyone in your network).
28.3 Sustainability Check
A realistic 2026 outcome: $25–60k freelance income, 2 PyPI packages with users, 6 blog posts drafted, 1 arXiv preprint polished, 5+ ongoing or recurring clients, 200-400 in-niche LinkedIn connections, material for research applications ready to submit late 2027. That's a strong industry-to-research transition foundation. Stronger than 80% of CS-grad applicants who haven't shipped to production.
Section 29: Common Failure Modes (And Their Fixes)
29.1 "I sent 50 proposals and got 0 replies"
Most common causes (in order):
74.	Demo is broken when client clicks the link (test it weekly!)
75.	Demo link is buried at the end of the proposal, not the third line
76.	Proposals are too generic — "I have experience with X"
77.	Targeting jobs with 50+ applicants and 0 client reviews (low quality)
78.	Title/profile keywords don't match what clients search for

Fix: pick 1 trusted freelancer in your niche. Pay $100-200 for a 30-minute review of your profile + 3 sample proposals. They'll tell you which of the 5 issues above is killing you. Cheapest, fastest, most useful investment.
29.2 "Clients are flaky / scope-creep / underpay"
This is a filtering problem upstream. Better filters:
•	Only apply to jobs with 3+ client reviews
•	Require milestone 1 paid upfront (Upwork escrow)
•	State scope clearly in the proposal; revise if they push
•	Track "client pain index" in your Notion log → don't repeat clients with high scores
29.3 "I'm building project 3 but no one cares about project 1"
Before starting Phase 4 (week 11), review:
•	Has project 1's portfolio entry generated interview interest? (>3 in 8 weeks expected)
•	Has project 2 generated interest? (>2 in 4 weeks expected)
•	Has project 3 generated interest? (>1 in 2 weeks expected)

If yes to 2/3 → continue per plan. If yes to only 1/3 → before Phase 4, do another week of intensive proposal-tweaking on the underperforming projects. If yes to 0/3 → STOP, pause Phase 4, get external review.
29.4 "My demos work locally but break on Railway/Fly.io"
This is universal. Plan for it:
•	Test deployment ON DAY 1 OF BUILDING, not day 10
•	Use .env.example to ensure environment-variable parity
•	Use the same Python version locally as on Railway
•	Watch for: file paths, CORS origins, database connection strings, Whisper / Tesseract binary dependencies
29.5 "I'm exhausted and want to quit"
Take a real week off. Not "I'll only work 3 hours a day" — actually off. Walk, sleep, see friends. Most freelancers who quit do so in month 3. The ones who succeed are usually the ones who took week 12 off and came back instead.


PART IX — THE AI-AGENT BUILD PROMPT
Section 30: Complete Codebase Splitting Prompt (For Claude/Cursor)
The following is the complete prompt to give to an AI coding agent (Claude, Cursor, GitHub Copilot Workspace) to split IntelAI into 6 separate starter codebases.

IMPORTANT: Run on DocIntel ALONE first (Phase 0 Day 2) to validate the prompt. Fix any issues before running on the remaining 5 projects.
Pre-Prompt Context (Read This First)
•	Run in a directory ABOVE the IntelAI source (agent reads from ./IntelAI/ and writes to sibling directories)
•	Python 3.11 must be available
•	Add real API keys to .env files AFTER the prompt runs
•	Do Phase 0 Day 4 verification yourself — not the agent
•	EXECUTION ORDER: DocIntel first (validation) → IntelAI refactor → Projects 2, 4, 5, 6 in any order
━━ START OF PROMPT ━━
You are a senior Python engineer tasked with refactoring a large monorepo
into 6 focused, standalone repositories. Each repo will become an
independent portfolio project shipping with the 2026 industry-leading
AI engineering stack.
 
THE SOURCE REPO: IntelAI/
(The full directory structure is accessible to you in the working dir.)
 
YOUR TASK: Create 6 new project repositories by:
1. Extracting the relevant files from IntelAI
2. Updating all import paths to match the new structure
3. Adding any glue code needed for each project to be standalone
4. Creating a proper README.md for each project
5. Creating a requirements.txt with the 2026 stack
6. Creating a Dockerfile for each project
7. Creating a .env.example with the env vars each project needs
8. Creating tests/ with at least 5 smoke tests per project
 
GLOBAL DEFAULTS (apply to every project unless overridden):
- Python 3.11
- FastAPI for HTTP APIs, uvicorn[standard] as server
- LiteLLM for multi-provider LLM routing (EVERY project depends on litellm)
- python-dotenv for config
- pytest for testing
- All code must work with these env vars present:
    LLM_DEFAULT     (e.g. groq/llama-3.3-70b-versatile)
    LLM_REASONING   (e.g. anthropic/claude-sonnet-4-6)
    LLM_JUDGE       (e.g. anthropic/claude-haiku-4-5)
    LLM_LOCAL       (e.g. ollama/llama3.3)
    GROQ_API_KEY, ANTHROPIC_API_KEY, OPENAI_API_KEY (optional, code degrades gracefully)
 
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 
PROJECT 1: IntelAI (refactor the existing repo in place)
Goal: Clean, deployable version of the main platform
 
KEEP all files in the repo. Make these specific changes:
 
  a) In frontend/: run `npm install recharts` and update package.json
 
  b) In frontend/src/pages/AnalyticsPage.jsx:
     Replace the custom SVG bar chart component with a Recharts LineChart.
     Import: { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer }
 
  c) In frontend/src/pages/ForecastingPage.jsx:
     Replace the table-based forecast display with a Recharts AreaChart.
     Show: actual (green line), forecast (blue dashed), CI bands (shaded area).
     Use two Area components stacked to create the CI band.
 
  d) In frontend/src/pages/RiskPage.jsx:
     Add a Recharts RadarChart visualizing risk.components.
 
  e) In frontend/src/pages/DashboardPage.jsx:
     Add 60px-tall sparkline LineCharts inside each KPI card.
     Use last 6 KPI values from existing kpis state.
 
  f) In frontend/src/pages/FinancialPage.jsx:
     Replace stub with working page:
     - Dropdown for: income_statement | balance_sheet | cash_flow
     - Call api.post('/financial/statement', {statement_type: selectedType})
     - Recharts BarChart of line_items from response
 
  g) In tests/test_api.py:
     Expand from 2 tests to at least 30 tests covering:
     auth (login, wrong password, register, get me, viewer-blocked),
     chat (basic, with persona, streaming),
     kpis (get, periods, metrics, categories),
     insights (health, risk, summary, anomalies),
     ingest (valid data, empty data, malformed),
     forecast (basic, with CI),
     rbac (admin works, viewer blocked, scope enforcement),
     monitoring (stats, knowledge search), prometheus endpoint.
 
  h) Replace README.md with a clean version (<200 lines):
     one-line description, what's built (table), Quick Start (3 commands),
     default credentials, API docs link (/api/docs), live demo URL,
     architecture ASCII diagram.
 
  i) Create railway.toml in the root:
     [build] builder = "DOCKERFILE"
     [deploy] startCommand = "python -m uvicorn src.api.server_v2:app
                               --host 0.0.0.0 --port $PORT --workers 1"
     healthcheckPath = "/health"
 
  j) ADD 2026 stack upgrades:
     - pip install litellm>=1.55.0 anthropic openai
     - Create src/services/llm_router.py with llm_call(messages, tier=...)
       routing across groq/anthropic/ollama via LiteLLM
     - Update omnismart_chatbot.py to call llm_router.llm_call() instead
       of direct Groq client. Tier: CEO/CFO/CTO/Risk → reasoning,
       COO/CHRO/ESG/Analyst/General → default.
     - Create src/services/hybrid_retrieval.py with HybridRetriever:
       dense (bge-large) + sparse (BM25) + RRF + BGE Reranker v2 m3
     - Add USE_HYBRID_RETRIEVAL env flag (default false in dev)
     - Add VECTOR_STORE env flag (chroma | qdrant) with Qdrant documented
     - Update requirements.txt with: rank-bm25, FlagEmbedding, qdrant-client,
       litellm, anthropic, openai
 
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 
PROJECT 2: AgentKit
Goal: MCP server + multi-framework agent workflow
 
CREATE new directory: agentkit/
 
EXTRACT these files from IntelAI (copy, don't move):
  src/services/pg_store.py        → agentkit/services/pg_store.py
  src/services/insights.py        → agentkit/services/insights.py
  src/services/forecasting.py     → agentkit/services/forecasting.py
  src/core/config.py              → agentkit/core/config.py
  src/core/logger.py              → agentkit/core/logger.py
  src/core/pg_engine.py           → agentkit/core/pg_engine.py
  db/schema.sql                   → agentkit/db/schema.sql
  .env.example                    → agentkit/.env.example
 
UPDATE imports: from src.* → from services.* or from core.*
 
CREATE these new files:
 
  agentkit/mcp_server.py:
    FastMCP server with 6 tools:
      query_kpis(domain, period_from, period_to, metric_filter, limit)
      get_company_health(domain=None)
      detect_kpi_anomalies(domain, method="zscore", threshold=2.5)
      forecast_metric(metric_name, periods=6, confidence_level=0.95)
      list_available_metrics(domain=None)
      get_executive_summary()
    Also expose:
      @mcp.resource("kpi://Finance/latest") and similar for other domains
      @mcp.prompt("monthly_executive_briefing") reusable template
    Entry: if __name__ == "__main__": mcp.run()
 
  agentkit/workflow.py:
    LangGraph StateGraph (BusinessAnalysisState TypedDict) with 3 nodes:
      planner_agent: uses litellm with LLM_REASONING (claude-sonnet-4-6)
        Breaks question into 3-4 analysis steps
      analyst_agent: uses LLM_DEFAULT (groq/llama-3.3-70b-versatile)
        Calls relevant MCP tools based on keywords in question
        Always calls: get_company_health() + get_executive_summary()
      reporter_agent: uses LLM_REASONING (claude-sonnet-4-6)
        Sections: KEY FINDING, EVIDENCE, ROOT CAUSE,
                  RECOMMENDED ACTION, RISK IF UNADDRESSED
    All LLM calls via litellm.acompletion(model=...)
    Public API: def analyze(question: str) -> dict
 
  agentkit/demos/claude_agent_sdk_demo.py:
    Uses claude_agent_sdk.Agent + MCPServer to call same 6 tools
    via Claude Agent SDK orchestration. (~50 lines)
 
  agentkit/demos/crewai_demo.py:
    Uses CrewAI to wrap same MCP tools as @tool decorators.
    Defines a 3-agent crew (Researcher / Analyst / Reporter). (~80 lines)
 
  agentkit/research/dspy_experiment.py:
    DSPy module framing planner→analyst→reporter as compilable program.
    BootstrapFewShot training over held-out business questions.
 
  agentkit/requirements.txt:
    fastmcp>=0.4.0, langgraph>=0.2.0, langchain>=0.3.0,
    litellm>=1.55.0, anthropic>=0.40.0, groq>=0.11.0,
    openai>=1.55.0, crewai>=0.86.0, dspy-ai>=2.5.0,
    psycopg[binary]>=3.1.18, pandas>=2.2.3, numpy>=2.1.3,
    scikit-learn>=1.5.2, chromadb>=0.5.18,
    sentence-transformers>=3.1.1, python-dotenv>=1.0.1
 
  agentkit/README.md:
    Title: "AgentKit — MCP Server for Business Intelligence Agents"
    Sections: What It Does, Tools (table), Resources, Prompts,
    Quick Start, Claude Desktop Setup, LangGraph Workflow,
    Claude Agent SDK, CrewAI Example, DSPy Experiment (research)
    Quick Start: pip install -r requirements.txt && python mcp_server.py
    Claude Desktop config (JSON block)
    Architecture ASCII diagram
 
  agentkit/.env.example:
    POSTGRES_URL=postgresql://omniintel:change_me@localhost:5432/intelai
    LLM_DEFAULT=groq/llama-3.3-70b-versatile
    LLM_REASONING=anthropic/claude-sonnet-4-6
    LLM_JUDGE=anthropic/claude-haiku-4-5
    LLM_LOCAL=ollama/llama3.3
    GROQ_API_KEY=gsk_your_key_here
    ANTHROPIC_API_KEY=sk-ant-your_key_here
    OPENAI_API_KEY=sk-your_key_here
 
  agentkit/tests/test_mcp_tools.py:
    10+ tests for all 6 MCP tools, resources, prompts
    Mock pg_store / insights / forecasting if DB not available
 
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 
PROJECT 3: DocIntel
Goal: Vision-first document AI pipeline as standalone service
 
CREATE new directory: docintel/
 
EXTRACT from IntelAI:
  src/services/ocr_enhancement.py  → docintel/services/ocr_extractor.py
  src/services/ocr/main.py         → docintel/services/tesseract_service.py
  src/services/ocr/Dockerfile.ocr  → docintel/Dockerfile
  src/integrations/camera.py       → docintel/services/camera.py
  src/core/logger.py               → docintel/core/logger.py
  src/core/config.py               → docintel/core/config.py (slim)
 
UPDATE imports in all extracted files.
 
CREATE new files:
 
  docintel/api.py:
    GET  /health
    POST /extract (file + route: vision_premium|vision_local|ocr_fallback)
    POST /classify (file → doc_type only, fast)
    POST /classify-image (image + categories list → category + confidence)
                         ← CRITICAL: this is the Equipment Sourcing pattern
    POST /extract-tables (PDF → tables list)
    POST /extract-llm (text + doc_type → structured dict)
    POST /batch/upload (list of files → job_id + background task)
    GET  /batch/{job_id}
    GET  /batch/{job_id}/results
    ProcessResponse Pydantic model.
    Serve demo/ as static at /demo
 
  docintel/services/vision_extractor.py:
    extract_via_vision_llm(image_bytes, model, doc_type) → dict
    Uses litellm.acompletion with image_url message format.
    Prompts per doc_type: invoice, contract, receipt, financial_report,
    auction_listing, default. Supports Claude Vision and Ollama vision.
 
  docintel/services/marker_extractor.py:
    Uses marker library to convert PDF → Markdown.
 
  docintel/services/llm_extractor.py:
    LLMExtractor class with async extract(text, doc_type) for OCR-fallback.
 
  docintel/services/batch_processor.py:
    BatchProcessor with process / get_status / get_results.
    In-memory dict for job tracking (sufficient for demo).
 
  docintel/demo/index.html:
    Single-page drag-and-drop demo (dark #0f172a, vanilla JS, ~200 lines).
    Toggle between routes (vision_premium | vision_local | ocr_fallback).
    Shows: doc_type badge, confidence, processing time, structured JSON.
 
  docintel/demo/classify_image.html:
    Separate page demonstrating /classify-image for auction-listing
    classification. Drag image + enter category list → show result.
 
  docintel/eval/run_eval.py:
    Eval harness comparing routes A/B/C on a benchmark dataset.
    Measures per-field accuracy, latency, cost.
 
  docintel/requirements.txt:
    fastapi>=0.115.0, uvicorn[standard]>=0.32.0,
    python-multipart>=0.0.12, litellm>=1.55.0, anthropic>=0.40.0,
    groq>=0.11.0, openai>=1.55.0, pdfplumber>=0.11.0,
    pytesseract>=0.3.10, pillow>=10.1.0, pypdf>=4.3.1,
    marker-pdf>=0.2.0, surya-ocr>=0.5.0,
    python-dotenv>=1.0.1, pandas>=2.2.3, aiofiles>=24.1.0
 
  docintel/README.md:
    Hero: "Vision-first document AI. Drop a PDF or image, get structured
           JSON in under 2 seconds. Local or cloud."
    Three routes documented prominently.
    Live demo URL + classify-image demo URL.
    Quick Start (3 commands).
    Eval results table (vision_premium vs vision_local vs ocr_fallback).
 
  docintel/.env.example:
    LLM_DEFAULT=groq/llama-3.3-70b-versatile
    LLM_REASONING=anthropic/claude-sonnet-4-6
    LLM_VISION_PREMIUM=anthropic/claude-sonnet-4-6
    LLM_VISION_LOCAL=ollama/llama3.2-vision
    GROQ_API_KEY=...
    ANTHROPIC_API_KEY=...
    OLLAMA_BASE_URL=http://localhost:11434
 
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 
PROJECT 4: VoiceFlow
Goal: Multi-provider speech-to-intelligence pipeline
 
CREATE new directory: voiceflow/
 
EXTRACT from IntelAI:
  src/services/voice/main.py       → voiceflow/services/voice_service.py
  src/services/voice/Dockerfile.voice → voiceflow/Dockerfile
  src/integrations/tts.py          → voiceflow/services/tts_service.py
  src/core/logger.py               → voiceflow/core/logger.py
 
UPDATE imports.
 
CREATE new files:
 
  voiceflow/services/whisperx_service.py:
    Uses whisperx for faster-whisper + forced alignment + pyannote diarization.
    Falls back gracefully if pyannote not installed.
    Document fallback in README: pyannote 3.x → NeMo → no-diarization.
 
  voiceflow/services/transcription_router.py:
    Routes transcribe() calls to:
    LOCAL_WHISPERX | GROQ_WHISPER | DEEPGRAM | ASSEMBLYAI
    based on provider parameter or env default.
 
  voiceflow/services/meeting_analyzer.py:
    MeetingAnalyzer class with 5 methods:
    analyze_meeting, analyze_sales_call, analyze_support_call,
    analyze_interview, general_analysis
    ANALYSIS_MODELS dict routing per analysis type:
      meeting/general:  LLM_DEFAULT (groq/llama-3.3-70b-versatile)
      sales_call:       LLM_REASONING (anthropic/claude-sonnet-4-6)
      support_call:     LLM_JUDGE (anthropic/claude-haiku-4-5)
      interview:        LLM_REASONING
    All calls via litellm.acompletion, temperature=0.2, return parsed JSON.
 
  voiceflow/api.py:
    GET  /health
    POST /transcribe (audio + provider)
    POST /tts (text + provider + voice)
    POST /analyze (text + analysis_type)
    POST /pipeline (audio + analysis_type → transcribe + analyze)
    POST /meeting/process
    POST /call/analyze
    WS   /stream (optional)
    WS   /realtime (bridges to OpenAI Realtime API for voice agent demo)
    Serve demo/ at /demo
 
  voiceflow/demo/record.html:
    Browser-recording demo (MediaRecorder API).
    3-second countdown before recording. Waveform visualization.
    3 sample-audio buttons. Analysis-type radio (Meeting/Sales/General).
    ~250 lines vanilla JS.
 
  voiceflow/demo/realtime.html:
    OpenAI Realtime API voice agent demo (WebRTC).
    Talks to AgentKit MCP tools via bridge.
    Shows real-time voice agent responding to KPI questions.
 
  voiceflow/requirements.txt:
    fastapi>=0.115.0, uvicorn[standard]>=0.32.0,
    python-multipart>=0.0.12, litellm>=1.55.0, anthropic>=0.40.0,
    groq>=0.11.0, openai>=1.55.0, edge-tts>=6.1.9,
    faster-whisper>=1.0.3, whisperx>=3.1.0,
    pyannote.audio>=3.1.0 (optional, HF_TOKEN needed),
    python-dotenv>=1.0.1, requests>=2.32.3, aiohttp>=3.10.0,
    deepgram-sdk>=3.7.0 (optional), assemblyai>=0.30.0 (optional)
 
  voiceflow/README.md:
    Hero: "Speech → structured intelligence. Browser-recording demo.
           4 providers, 5 analysis types, real-time voice agent."
    Architecture ASCII: Audio → Whisper → LLM Intelligence → JSON
    Use Cases table. Diarization fallback chain documented.
 
  voiceflow/.env.example:
    LLM_DEFAULT=groq/llama-3.3-70b-versatile
    LLM_REASONING=anthropic/claude-sonnet-4-6
    LLM_JUDGE=anthropic/claude-haiku-4-5
    GROQ_API_KEY=...  ANTHROPIC_API_KEY=...  OPENAI_API_KEY=...
    HF_TOKEN=...  (for pyannote)
    DEEPGRAM_API_KEY=...  (optional)
    ASSEMBLYAI_API_KEY=...  (optional)
 
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 
PROJECT 5: RAGeval
Goal: Standards-track LLMOps observability with multi-judge consensus
 
CREATE new directory: rageval/
 
EXTRACT from IntelAI:
  src/core/monitoring.py    → rageval/core/monitoring.py
  src/core/performance.py   → rageval/core/performance.py
  src/core/logger.py        → rageval/core/logger.py
  src/core/config.py        → rageval/core/config.py (slim)
 
CREATE new files:
 
  rageval/evaluator.py:
    RAGEvaluator class:
      score_retrieval_relevance(query, chunks) → float
        Uses SentenceTransformer("BAAI/bge-large-en-v1.5")
        cosine_similarity(query_embedding, chunk_embeddings).mean()
      score_groundedness_consensus(answer, context) → dict
        Multi-judge: claude-haiku-4-5 + groq/llama-3.3-70b + openai/gpt-5-mini
        Returns: {consensus, stdev, judges:[...], flag_for_review: stdev>0.2}
      score_faithfulness(answer, chunks) → float
        Embedding-similarity NLI proxy
      calculate_cost(tokens, model, input_ratio=0.7) → float (USD)
        GROQ_PRICES + ANTHROPIC_PRICES + OPENAI_PRICES dicts
      score_interaction(query, answer, chunks, tokens_used, latency_ms,
                        model, persona=None) → dict
        Runs all scorers. overall_quality = 0.4*relevance + 0.4*groundedness
                          + 0.2*faithfulness. Flags: LOW_RETRIEVAL_RELEVANCE,
                          POTENTIAL_HALLUCINATION, HIGH_LATENCY.
    Embeddings: BAAI/bge-large-en-v1.5 default; also support MiniLM, BGE-M3.
 
  rageval/store.py:
    SQLite-default (~/.rageval/rageval.db); Postgres+pgvector optional.
    init_rageval_table(), async log_interaction(...),
    get_metrics(days=7), get_query_log(limit=50), get_cost_report(days=30)
    RAGEVAL_STORE env var: "sqlite" (default) or "postgres"
 
  rageval/api.py:
    GET  /health
    POST /eval/log (computes scores, stores)
    POST /eval/score (no storage)
    GET  /eval/metrics?days=7
    GET  /eval/queries?limit=50&needs_review=true
    GET  /eval/cost-report?days=30
    GET  /eval/alerts (recent flagged queries)
    POST /eval/retrieval-bench (A/B test retrieval strategies)
    POST /eval/embedding-comparison (compare embedding models)
 
  rageval/decorator.py:
    @track(model="...") decorator wrapping any function.
    Captures: input query, output answer, latency.
    Auto-logs to RAGeval store via /eval/log.
    Works with both sync and async functions.
 
  rageval/otel_exporter.py:
    OpenTelemetry / OpenLLMetry export.
    Configurable via RAGEVAL_OTEL_ENDPOINT env var.
 
  rageval/dspy_integration.py:
    Hook to log DSPy compilation runs:
    program name, candidates, winner, eval_metric, eval_score.
 
  rageval/cli.py:
    rageval init (creates DB), rageval serve (starts API).
    Entry point in pyproject.toml.
 
  rageval/dashboard/ (React app):
    3 tabs: Overview | Query Log | Cost Report
    Recharts charts. Dark theme. Fetches from RAGeval API.
    Overview: 3 metric cards + LineChart (quality over time) + BarChart (volume).
    Query Log: table with color-coded rows + "Show flagged only" toggle.
    Cost Report: daily cost LineChart + total + model breakdown.
 
  rageval/requirements.txt:
    fastapi>=0.115.0, uvicorn[standard]>=0.32.0, litellm>=1.55.0,
    anthropic>=0.40.0, groq>=0.11.0, openai>=1.55.0,
    sentence-transformers>=3.1.1, FlagEmbedding>=1.3.0,
    scikit-learn>=1.5.2, numpy>=2.1.3,
    psycopg[binary]>=3.1.18 (optional for pgvector tier),
    pgvector>=0.3.0 (optional),
    opentelemetry-api>=1.27.0, opentelemetry-sdk>=1.27.0,
    opentelemetry-exporter-otlp>=1.27.0,
    dspy-ai>=2.5.0 (optional integration),
    python-dotenv>=1.0.1
 
  rageval/pyproject.toml (PyPI-publishable):
    [project]
    name = "rageval"
    version = "0.1.0"
    [project.scripts]
    rageval = "rageval.cli:main"
 
  rageval/README.md:
    Title + badges (PyPI version, build status, license).
    Hero: "Drop-in LLMOps observability. Self-hosted. SQLite-default.
           Persona-aware. Multi-judge consensus."
    60-second pitch (decorator code example).
    What It Measures (5 metrics with definitions).
    Comparison table vs Phoenix, Langfuse, TruLens, Helicone.
    Quick Start (3 commands). Integration Guide. Dashboard Preview.
    Roadmap.
 
  rageval/.env.example:
    RAGEVAL_STORE=sqlite
    POSTGRES_URL=postgresql://...  (if postgres)
    RAGEVAL_OTEL_ENDPOINT=http://localhost:4317  (optional)
    LLM_JUDGE=anthropic/claude-haiku-4-5
    LLM_DEFAULT=groq/llama-3.3-70b-versatile
    GROQ_API_KEY=...  ANTHROPIC_API_KEY=...  OPENAI_API_KEY=...
 
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 
PROJECT 6: StreamPulse
Goal: Real-time multi-source data pipeline with first-class n8n
 
CREATE new directory: streampulse/
 
EXTRACT from IntelAI:
  src/services/realtime_pipeline.py    → streampulse/pipeline/classifier.py
  src/services/data_ingestion_manager.py → streampulse/pipeline/ingestion.py
  src/integrations/n8n.py               → streampulse/connectors/n8n.py
  src/core/config.py                    → streampulse/core/config.py (slim)
  src/core/logger.py                    → streampulse/core/logger.py
  src/services/pg_store.py              → streampulse/store.py (slim)
 
UPDATE imports. SIMPLIFY streampulse/store.py:
  Keep ONLY: store_kpi_metrics, get_kpi_metrics, log_data_ingestion,
  update_ingestion_log. Remove ALL chat, OCR, voice, camera, OAuth,
  user functions.
 
UPGRADE streampulse/pipeline/classifier.py:
  Add hybrid classification:
    Fast path: keyword matching (existing logic, <1ms)
    Fallback: BGE-large embedding similarity (if keyword confidence < 0.7)
    Last resort: litellm.acompletion with LLM_JUDGE (Claude Haiku 4.5)
    Cache classification results by content hash.
 
CREATE new files:
 
  streampulse/api.py:
    GET  /health
    POST /ingest/json
    POST /ingest/csv
    POST /ingest/email
    POST /webhook/{source_name}  (with HMAC X-Signature-256 verify)
    POST /webhook/{source}/with-vision
         Calls DocIntel /classify-image for images in payload.
         Enriches record with image category + confidence.
         Broadcasts enriched record to WebSocket connections.
    GET  /pipeline/status
    GET  /pipeline/history
    WS   /live
    GET  /live/sse  (Server-Sent Events alternative — simpler for one-way push)
 
  streampulse/connectors/webhook_receiver.py:
    WebhookReceiver class:
    verify_signature(payload, signature, secret) → bool (HMAC-SHA256)
    parse_payload(raw_json, source_name) → list of DataRecord
    route_to_pipeline(records) → None
 
  streampulse/connectors/n8n/:
    README.md (how to integrate StreamPulse into n8n)
    n8n_node.json (custom n8n community node definition)
    workflows/
      auction_aggregator.json (importable n8n workflow)
      invoice_intake.json
      crm_sync.json
 
  streampulse/ingestion/dlt_sources.py:
    dlt-based declarative sources:
    @dlt.source gmail_source()
    @dlt.source gsheet_source()
    @dlt.source webhook_source()
 
  streampulse/orchestration/prefect_flow.py:
    Prefect 3 flow with @task(retries=3, retry_delay_seconds=30)
    and @flow(name="streampulse-realtime-pipeline") definitions.
 
  streampulse/dashboard/ (React app):
    LiveDashboard.jsx with:
    WebSocket connection to /live (SSE fallback to /live/sse).
    State: records (last 50), volumeData (last 20 time buckets), domainDist.
    Recharts LineChart: records per minute (live updating).
    Recharts PieChart: domain distribution (live updating).
    Table: live record feed (time, domain, metric, value, source, confidence,
           image_category if available).
    Domain colors: Finance=#6366f1, Growth=#22c55e, Operations=#f59e0b,
                   People=#ec4899, ESG=#14b8a6, IT_Ops=#8b5cf6.
    Header: connection status (green/red), error count.
    Dark theme (#0f172a).
 
  streampulse/requirements.txt:
    fastapi>=0.115.0, uvicorn[standard]>=0.32.0,
    python-multipart>=0.0.12, litellm>=1.55.0, anthropic>=0.40.0,
    groq>=0.11.0, psycopg[binary]>=3.1.18, pgvector>=0.3.0,
    pandas>=2.2.3, numpy>=2.1.3,
    sentence-transformers>=3.1.1, aiohttp>=3.10.0,
    python-dotenv>=1.0.1, requests>=2.32.3,
    dlt>=0.5.0, prefect>=3.0.0,
    duckdb>=1.1.0 (optional for analytics queries)
 
  streampulse/README.md:
    Hero: "Real-time business data pipeline. 6+ source types,
           live dashboard, first-class n8n integration."
    Supported Sources table.
    n8n integration walkthrough.
    Architecture ASCII.
 
  streampulse/.env.example:
    POSTGRES_URL=postgresql://...
    LLM_DEFAULT=groq/llama-3.3-70b-versatile
    LLM_JUDGE=anthropic/claude-haiku-4-5
    GROQ_API_KEY=...  ANTHROPIC_API_KEY=...
    WEBHOOK_SECRET=change_me
    DOCINTEL_URL=http://localhost:8001  (for vision composition)
 
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 
EXECUTION ORDER:
1. ALWAYS start with Project 3 (DocIntel) as the prompt-validation test.
   If DocIntel starts cleanly, proceed to the others.
2. Then Project 1 (IntelAI refactor) — edits in place, smaller scope.
3. Then Projects 2, 4, 5, 6 in any order (they're independent).
 
QUALITY REQUIREMENTS FOR EACH PROJECT:
- All import paths work from project root (NO `from src.*` left)
- Every new file has a module docstring
- Every class has a class docstring
- Every public async function has docstring with Args and Returns
- requirements.txt is minimal (only what that project needs)
- README is accurate (only claim what code actually does)
- .env.example has every required env var with a placeholder
- Dockerfile builds without error: docker build -t <name>:test .
- pytest tests/ has at least 5 smoke tests per project
 
DO NOT:
- Overclaim features not implemented
- Leave broken import statements
- Create circular dependencies between projects
- Include unused dependencies in requirements.txt
- Hardcode any credentials anywhere
- Skip the 2026 stack upgrades (LiteLLM, multi-provider env vars, etc.)
 
OUTPUT:
Create all 6 project directories as described above.
Print a summary at the end:
  - Files created per project
  - Tests passing per project
  - Any TODOs that need human follow-up
 
━━ END OF PROMPT ━━
Post-Prompt Verification (Do Not Skip)
After the agent runs, for each of the 6 projects:
cd <project>
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest tests/ -v
uvicorn api:app --port 8001 &   # for FastAPI projects
curl http://localhost:8001/health

79.	Diff your .env.example files against what each project's code actually reads: grep -r "os.getenv" src/ | grep -oE '"[A-Z_]+"' should match .env.example 1:1.
80.	Run the splitting prompt's "Output Summary" against each project's actual state — does what the prompt claimed it created actually exist?
81.	If any project fails verification, fix the prompt and re-run for that project specifically (do not blanket re-run).


PART X — THE 2027 MULTI-CHANNEL DEPLOYMENT PLAYBOOK
In 2026 you built six projects, drafted six blog posts, polished one preprint, designed a personal site, and wrote a LinkedIn cornerstone post plus 20-30 supporting drafts. None of it went public in 2026. This part is the 2027 deployment plan — how the ammunition you stockpiled becomes a multi-channel launch over Q1-Q2 2027 that compounds for the rest of your career.
Section 31: The 2027 Launch Week (January Week 2)
Pick a Tuesday-Wednesday-Thursday window in mid-January (avoid New Year week — engagement is low).
Day	Action
Monday (preparation, no public posts)	Final review of personal site. Deploy yacine.dev (or your domain) to production. Verify all 6 GitHub repos still public, all demos respond. Verify Loom video links still work (test from incognito). Cross-check: every README links to live demo + Loom.
Tuesday 10:00 AM (your TZ)	Publish LinkedIn cornerstone post: "What I built in 2026: 6 AI projects, $X earned, what I learned about [theme]." Cross-link to personal site. Respond to comments throughout day — NO new content.
Wednesday (US morning 9 AM ET)	Submit "Show HN: AgentKit — MCP server for business intelligence agents" to Hacker News. Post in r/LocalLLaMA + Anthropic Discord simultaneously. Cross-link to GitHub. Respond to HN comments — AgentKit is most likely to hit front page because of MCP novelty.
Thursday (9 AM your TZ)	Publish Blog Post 1 (Persona-Routed RAG) on personal site as canonical URL. Cross-post to Medium with canonical link back. Cross-post to dev.to. Post LinkedIn share-link with 2-sentence framing. Respond to comments.
Friday (decompression + planning)	Review week-1 metrics: LinkedIn cornerstone reach, site traffic, HN front-page yes/no, Blog Post 1 views, new connections/DMs/GitHub stars. Decide adjustments for weeks 2-6.
Weeks 2–6 Rolling Blog Post + Show HN Cadence
Week	Blog Post + Show HN + Community
Week 2	Blog Post 2 (Vision-First Document AI) + Show HN #2 (DocIntel) + Reddit r/MachineLearning methodology excerpt
Week 3	Blog Post 3 (MCP Tool Design Patterns) + Show HN #3 (DocIntel or IntelAI depending on which got Reddit traction)
Week 4	Blog Post 4 (Speech-to-Intelligence) + Show HN #4 (VoiceFlow) + Reddit r/speech_recognition crosspost
Week 5	Blog Post 5 (Multi-Judge LLM Eval) + Show HN #5 (RAGeval) — most likely HN hit because LLMOps is hot
Week 6	Blog Post 6 (Vision-First Multi-Source, Equipment Sourcing case study) + Show HN #6 (StreamPulse)

Across the 6-week launch: 6 Show HN submissions (3-4 will probably die on /new; 1-2 should hit front page given quality + topic relevance), 6 blog posts live, 6 LinkedIn supporting posts, 6 Reddit posts. By end of Week 6, your public footprint includes 500-3000+ new LinkedIn connections and measurable HN + blog traffic.
Section 32: arXiv Submission Window (February-March 2027)
Don't submit in January — LinkedIn launch consumes bandwidth and a pre-print announcement gets lost. February–March is the right window:
•	Submit Tuesday morning UTC — European researchers wake up to it, US researchers see it during their workday
•	Categories: cs.IR (primary), cross-list cs.CL, cs.LG
•	arXiv comment: "Code at github.com/<yourname>/rageval; data at <link>"
•	Announce on LinkedIn + personal site on submission day
•	DM the 3-5 reviewers from Day 113 thanking them and sharing the submission link

Workshop Submissions Following the Preprint
Workshop / Conference	Typical Deadline	Target?
NeurIPS 2027 RAG workshops	Aug-Sep 2027	Yes — submit
ICML 2027 workshops	Mar 2027	Yes — submit
ACL 2027 workshops	Apr 2027	Yes — submit
EMNLP 2027 workshops	Jun 2027	Yes — submit
COLM 2027 (Conf on Language Modeling)	Mar 2027	Yes if RAG topic fits
ICLR 2027 workshops	Dec 2026 — missed	No (submit to 2028 ICLR)
Submit to 2-3 workshops simultaneously. Workshop acceptance rates are 30-50%. Submitting to 3 gives a real shot at 1-2 accepts.
Section 33: The 2027 LinkedIn Posting Engine
Category	Posts	Source
Project showcases	8	One per project + 2 deeper dives
Technical mini-lessons	10	Pulled from blog posts
Lessons from client work	6-10	Anonymized stories from 2026
Tool reviews / comparisons	4-6	LiteLLM, n8n, Marker, WhisperX, etc.
Career / freelance narrative	3-5	Your story, with specifics
Research-track signals	2-4	Preprint announcement, workshop submission
Engagement plays	ongoing	Reply to others; original posts driven by responses

Cadence: 2 posts per week (Tuesday + Thursday, mid-day local). Respond to every comment in the first 6 hours. LinkedIn rewards early engagement velocity. Hold ~30 weeks of content (60 posts) in the queue — drip-feed using your 2026 drafts.
The "Warmed by Content" Pattern
82.	Someone likes 3+ of your LinkedIn posts over 4 weeks
83.	Check their profile: are they a buying-relevant role at a fit company?
84.	Send a personalized LinkedIn DM: "Loved your engagement with my posts. Are you working on something in [adjacent area]? Happy to share notes."
85.	If they engage → move to email for substantive conversation
86.	Convert ~20% of warmed leads to discovery calls

This is the cycle that makes a strong LinkedIn presence durably valuable — not the posts themselves, but the inbound that posts unlock.
Section 34: Personal Portfolio Site (yacine.dev or similar)
Site Structure
yacine.dev/
  /              Homepage: hero + 6 project cards + "About" link
  /projects/     Project gallery (one card per repo with screenshot, hook)
  /projects/intelai/
  /projects/agentkit/
  /projects/docintel/
  /projects/voiceflow/
  /projects/rageval/
  /projects/streampulse/
  /blog/         Blog index
  /blog/persona-routed-rag/
  /blog/vision-first-doc-ai/
  /blog/mcp-tool-patterns/
  /blog/speech-to-intelligence/
  /blog/multi-judge-llm-eval/
  /blog/vision-first-multi-source/
  /about/        Short bio, what you do, what you've built, contact
  /research/     Preprint + future preprints + reading list
  /now/          "What I'm working on now" — updated quarterly
  /contact/      Email + Cal.com booking link
Tech Stack for the Site
Component	Choice	Why
Generator	Astro or Hugo	Static-site, fast, MDX support, deploys to Vercel in 1 command
Hosting	Vercel	Free for personal projects, instant deploys
Domain	Namecheap or Cloudflare Registrar	~$10/year
Analytics	Plausible ($9/mo) or Cloudflare Analytics (free)	Privacy-first
Search	Pagefind	Free, client-side, no service to operate
SEO and Discoverability
Pick 3-4 long-tail keywords each blog post targets:
Blog Post	Target Keywords
Persona-Routed RAG	"multi-persona RAG", "role-based RAG", "RAG persona prompts"
Vision-First Document AI	"vision LLM OCR", "Llama vision invoice", "Ollama document extraction"
MCP Tool Design Patterns	"MCP server tutorial", "fastmcp tutorial", "Claude Desktop MCP business intelligence"
Speech-to-Intelligence	"Whisper sales call analysis", "meeting notes AI extraction"
Multi-Judge LLM Evaluation	"RAG evaluation framework", "LLM-as-judge consensus", "RAGeval"
Vision-First Multi-Source	"auction listing aggregator AI", "vision-first scraper alternative"
Section 35: Cold Email Evolution In 2027
Cold email in 2026 was 10 emails/week (warm leads from network + direct outreach). In 2027 it scales because you have public proof (blog posts, GitHub, preprint) and your reply rate jumps from ~5% to ~15-20%.
Metric	2026	2027
Weekly emails sent	10	15-20
Reply rate	~5%	~15-20%
Reply to discovery call	~1-2%	~5-8%
Discovery call to contract	~50%	~50%
Unique value add	Demo links	"I wrote about this here [link to blog]"
Section 36: Research-Program Outreach Calendar (Q2 2027)
Month	Activity
April 2027	Identify 10-15 target research programs (PhD, MS, fellowships). For each: identify 2-3 faculty whose work aligns with your preprint. Draft personalized outreach email per faculty (informational chat ask, NOT application ask).
May-June 2027	Send 20-30 faculty outreach emails (5/week). Expect 30-40% reply rate (your preprint + projects are credibility). Have 5-10 informational Zoom chats (30 min each). These are NOT application asks.
July-August 2027	Based on chats, narrow to 5-8 application targets. Begin SOP drafts (3-4 versions, tailored per program). Request reference letters from: 2 academic-aligned, 1-2 clients, possibly 1 OSS community contact.
September-November 2027	Submit applications. Continue freelance income. Start preprint #2 (drafted alongside applications).
December 2027	Wait. Process feedback. Begin preprint #2 polish. Plan 2028 contingencies.
Section 37: 2027 Quarterly Outcome Targets
Quarter	Targets	Income
Q1 2027	Launch week. 6 blog posts live. Preprint submitted to arXiv. LinkedIn cadence established. 1500-3000 new LinkedIn connections. 1 HN front-page likely. Preprint announcement 50-200 cites/shares.	$20-40k earned
Q2 2027	Research outreach. 1-2 workshop submissions. 5-10 informational research chats. 1 workshop acceptance (50/50 odds).	$20-40k earned
Q3 2027	Application prep. SOPs drafted and reviewed. Reference letters secured.	$15-30k (reduced load)
Q4 2027	5-8 research program applications submitted. Preprint #2 draft 70-80% complete.	$15-25k earned
Total 2027: $70–135k freelance income + research-application position secured for 2028.
Section 38: The Long Game (2028 And Beyond)
By end of 2027, all five options are open simultaneously. The plan builds optionality, not a predetermined path.
Option	Description	Annual Income
A — Continue freelance + build a product	Rate at $130-180/hr inbound (LinkedIn + referrals). Convert 1-2 of your 6 projects into a paid product (RAGeval Pro? DocIntel managed service?). Capacity: 20-25 hrs/week + product work.	$150-300k
B — Accept research program (PhD / MS / fellowship)	Reduce freelance to maintenance level (1-2 retainer clients). Full-time research, draws on your 6 projects as platform.	$30-50k stipend
C — Lead AI engineering at a startup	Inbound recruiting from CTOs you've talked to in 2026-27. "Head of AI" at Series A/B.	$180-280k base + equity
D — Independent research / fellowship combo	Anthropic Fellowship, OpenAI Residency, MATS, etc. Continue light freelance to maintain optionality.	$60-100k stipend + freelance
E — Open-source maintainer / advocate role	Maintain RAGeval + AgentKit, get sponsorship (GitHub Sponsors, corporate backers).	$50-120k from sponsorships + light consulting


APPENDIX — QUICK REFERENCE CARDS
Quick Reference: Project Source Map
From IntelAI-master/	To Project
src/api/server_v2.py	P1: Keep (refactor in place)
src/services/omnismart_chatbot.py	P1: Keep
src/services/pg_store.py	P1: Keep | P2: Copy | P6: Slim copy
src/services/advanced_chatbot.py	P1: Keep
src/services/insights.py	P1: Keep | P2: Copy
src/services/forecasting.py	P1: Keep | P2: Copy
src/services/ocr_enhancement.py	P3: Copy (primary)
src/services/realtime_pipeline.py	P6: Copy (primary)
src/services/data_ingestion_manager.py	P6: Copy
src/services/voice/main.py	P4: Copy (primary)
src/services/ocr/main.py	P3: Copy
src/integrations/dispatcher.py	P4: Voice + TTS partial copy
src/integrations/tts.py	P4: Copy
src/integrations/n8n.py	P6: Copy
src/integrations/camera.py	P3: Copy
src/core/config.py	P2, P3, P4, P5, P6: Slim copy each
src/core/monitoring.py	P5: Copy
src/core/performance.py	P5: Copy
src/core/logger.py	All projects: Copy
src/core/jwt_auth.py	P1: Keep only
src/core/crypto.py	P1: Keep only
src/core/i18n.py	P1: Keep only
src/models/pg_models.py	P1: Keep only
src/models/schemas.py	P1: Keep only
frontend/	P1: Keep
db/schema.sql	P1: Keep | P2: Copy
enhanced_synthetic_dataset/	P1: Keep
n8n_workflows/	P6: Copy
monitoring/	P1: Keep
scripts/	P1: Keep
Quick Reference: Channel × Project × Template Matrix
Client Searches For	Use Project	Use Template	Primary Channel
RAG, LangChain, chatbot, ChromaDB	IntelAI	Template 1	Upwork PRIMARY
MCP server, agentic AI, LangGraph, multi-agent	AgentKit	Template 2	GitHub + Cold Email
OCR, PDF extraction, document AI, invoice, contract	DocIntel	Template 3	Upwork PRIMARY
Whisper, STT, voice AI, meeting notes, speech-to-text	VoiceFlow	Template 4	Upwork SECONDARY
LLMOps, RAG evaluation, observability, hallucination	RAGeval	Template 5	GitHub + Upwork SECONDARY
ETL, webhook, real-time dashboard, n8n, data pipeline	StreamPulse	Template 6	Cold Email PRIMARY
Quick Reference: Rates By Channel
Channel	Starting	At 5 Reviews	At 20 Reviews
Upwork cold inbound	$65/hr	$85/hr	$110/hr
Upwork warm referral	$75/hr	$95/hr	$130/hr
Cold email direct	$85/hr	$110/hr	$150/hr
LinkedIn 2027 inbound	$95/hr	$130/hr	$170/hr
Research-aligned contract	~$100-150/hr	Variable	Rate secondary to credential value
Quick Reference: Capacity Matrix
Active Clients	Client Time	Pipeline Time	Daily Proposals
0	0%	100%	10/day target
1	50%	50%	5/day target
2	70%	30%	3/day target
3	90%	10%	1/day target
4+	100%	0%	STOP — focus delivery quality
Glossary
Term	Definition
MCP	Model Context Protocol — Anthropic's open standard for letting AI agents call external tools. The connectivity layer for AI agents.
RAG	Retrieval-Augmented Generation — retrieving relevant documents before LLM generation to improve factuality and groundedness.
Groundedness	How well an LLM answer is supported by retrieved context. Core RAG evaluation metric. Score 0.0-1.0.
Persona-Routed RAG	Same retrieval system, different system prompts + data scoping per role/persona. Your core IntelAI differentiator.
Persona-Conditioned Groundedness	Groundedness metric that accounts for role constraints. A CFO response can be groundedness-valid but still violate Finance-only scope. Your research contribution.
LLMOps	Operations and monitoring for LLM-based systems — the DevOps of the LLM era.
fastmcp	Python library for building MCP servers (Anthropic-affiliated). The tool you use for AgentKit.
LangGraph	Library for building stateful multi-agent workflows via a directed graph. The production standard for agentic AI.
Claude Agent SDK	Anthropic's native Python SDK for building Claude-powered agents. MCP-first design.
CrewAI	Role-based multi-agent framework with a "crew" mental model (Researcher / Analyst / Reporter).
DSPy	"Programming over prompting" paradigm. Self-optimizing LLM pipelines via compilation. Research-strong signal tool.
LiteLLM	Multi-provider LLM abstraction layer — route any call across Anthropic, Groq, OpenAI, Ollama via config. Mandatory in 2026.
WhisperX	faster-whisper + forced alignment + pyannote diarization in one library. The 2026 self-hosted transcription SOTA.
BGE Reranker v2 m3	Cross-encoder reranker from BAAI. Takes top-50 retrieved docs and rescores them jointly with query. Adds 100-300ms, precision@5 jumps 20-40%.
GraphRAG	Entity extraction → knowledge graph → graph-traversal queries for multi-hop reasoning. Microsoft Research, now production-deployable.
Hybrid Retrieval	Combining dense (embedding) + sparse (BM25) retrieval, merged via Reciprocal Rank Fusion (RRF). Now mandatory for production RAG.
pgvector	PostgreSQL extension for vector similarity search. Enables one-database-to-operate production setup.
OpenTelemetry / OTLP	Open standards for observability (traces, metrics, logs). OpenLLMetry extends OTel for LLM applications.
arXiv preprint	Research paper publicly released before formal peer review. Citation-worthy. Free to publish. Submittable to cs.IR, cs.CL, cs.LG.
Workshop paper	Peer-reviewed, accepted at a topical workshop at a major conference (NeurIPS, ICML, ACL, etc.). Lower bar than main conference; meaningful on PhD application CV.
Connects	Upwork's internal currency. Each proposal costs 4–16 Connects depending on job complexity.
Top Rated	Upwork status given after consistent strong reviews. Increases visibility in search results.
dlt	"data load tool" — declarative ingestion library. The "Stripe of pipelines." Used in StreamPulse.
Prefect 3	Modern Python workflow orchestration with async-native design. Used in StreamPulse for reliable scheduled runs.
Marker	Open-source PDF-to-Markdown converter by VikParuchuri. 2026 SOTA for high-quality PDF text extraction. Used in DocIntel secondary route.
Surya OCR	Open-source layout-aware OCR by VikParuchuri. Better than Tesseract for non-Latin scripts. Used in DocIntel fallback route.




End of Document — Version 2.0
Built from a real codebase audit. Every line count was verified.
Every step is achievable for one focused person working alone.
