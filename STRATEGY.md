# IntelAI → Freelance Income → Research Pipeline
## Complete Strategy 2026 (v2 — Refactored)

**Document Version:** 2.0
**Date:** May 2026
**Audience:** Yacine — Personal execution only
**Supersedes:** `omniinteloscompletestrategy` (v1, kept as backup)

---

> **⚑ 2026-06-09 — PROJECT SPLIT (read first).** "IntelAI" is the scoped product
> formerly called *OmniIntelOS*. The original codebase had grown into an all-in-one,
> Palantir-style platform (monitoring, OCR + voice microservices, n8n, on-prem
> multi-service Docker). That **full platform was moved out** of this 6-project program
> into its own **private** repo `github.com/Yacine-ai-tech/OmniIntelOS` (with its own
> dedicated Studio — see that repo's `PLATFORM_GUIDE.md`). **IntelAI = project #1 of 6**:
> a single cloud deployment scoped to *analytics + 9-persona RAG + GraphRAG-lite*,
> branded and packageable, with **null dependency** on the full platform or the other 5
> projects. Where sections below describe broader "platform" features, they refer to the
> now-separate OmniIntelOS; IntelAI's authoritative scope is §1.1 (KEEP/CUT). The actual
> code-level scope-down runs in **Phase 1** — the codebase still carries the full feature
> set until then.

---

> **Thesis in one paragraph**
>
> One codebase you already built (IntelAI, ~14k lines Python + ~5.5k lines React,
> verified by repo audit) becomes the seed for three parallel outcomes in 2026:
> (1) consistent Upwork freelance income at $65–95/hr,
> (2) an open-source + technical-writing footprint that powers your 2027 LinkedIn launch,
> (3) research-grade credentials (deployed systems + 1–2 arXiv preprints + reference relationships)
> that make you a competitive applicant for top AI research programs and fellowships in 2027–2028.
>
> The mechanism: split the monorepo into 6 focused portfolio projects, ship them in
> a **phased sequence** (not parallel), distribute across **multiple channels**
> (Upwork is the income engine, GitHub + blog are the credibility engine, LinkedIn
> is the 2027 amplifier), and write **one technical post per project** that
> doubles as a workshop-paper draft.
>
> This document is grounded in the actual code in this repo. Nothing here is
> aspirational fiction — every file reference and line count was verified by
> reading the repository on the date above.

---

## Table of Contents

```
PART I  — THE THESIS AND THE CODEBASE
  Section 1     What This Document Is (And Isn't)
  Section 2     The Compound-Career Argument
  Section 3     Real Codebase Inventory (Audited)
  Section 4     What's Weak, What's Missing, What to Sharpen
  Section 4.5   2026 Stack Refresh — What's Leading And Why
                (LLMs, RAG, embeddings, agents, vision, speech, LLMOps,
                 orchestration, research-strong choices, pricing,
                 multi-provider abstraction via LiteLLM)

PART II — THE SIX PROJECTS (Refined + 2026 Stack Upgrades)
  Project 1   IntelAI Refactored — AI Analytics + Persona RAG
              + 1.10 Multi-LLM, Hybrid Retrieval, GraphRAG-lite, Qdrant
  Project 2   AgentKit — MCP Server + Multi-Agent Workflow
              + 2.10 Claude Sonnet + LangGraph + Claude Agent SDK + CrewAI + DSPy
  Project 3   DocIntel — Document Intelligence Pipeline
              + 3.10 Vision-First (Claude Vision + Ollama Llama 3.2 Vision)
                     + Marker + Surya + /classify-image endpoint
  Project 4   VoiceFlow — Speech-to-Intelligence
              + 4.10 WhisperX + Deepgram + AssemblyAI + Realtime API + ElevenLabs
  Project 5   RAGeval — LLMOps Observability (Self-Hosted)
              + 5.10 Multi-Judge Consensus + OpenTelemetry + DSPy + pgvector
  Project 6   StreamPulse — Real-Time Data Pipeline
              + 6.10 First-class n8n + Prefect 3 + dlt + Vision-Composition
  Cross-Project Synergy Summary

PART III — MULTI-CHANNEL DISTRIBUTION
  Section 5   The 2026 Channel Mix (GitHub + Upwork + Loom ONLY)
              2026 vs 2027 channel split; what to draft now, deploy later
  Section 6   Upwork Strategy For 0-Review Freelancers
  Section 7   Open-Source Strategy (PyPI, GitHub, DockerHub)
  Section 8   Technical Writing Strategy (Draft In 2026, Publish In 2027)
  Section 9   Cold Email + Communities
  Section 10  LinkedIn 2027 — Light-Touch Prep Now

PART IV — THE RESEARCH DEGREE TRACK
  Section 11  What Top Programs And Fellowships Want In 2026
  Section 12  How This Plan Builds Research Capital
  Section 13  One Preprint Per Year (Realistic Cadence)
  Section 14  Research-Aligned Freelance Opportunities
  Section 15  Reference Letter Strategy

PART V — EXECUTION (18 WEEKS + WEEK 0, SEQUENTIAL, ALL SIX)
  Section 16  Phased Build Plan (Day-by-Day, All Six Projects)
    16.0      Principles And The Decision To Build All Six
    16.1      Phase 0 — Repository Splitting (Week 0)
    16.2      Phase 1 — IntelAI Foundation (Weeks 1–3)
    16.3      Phase 2 — DocIntel (Weeks 4–6)
    16.4      Phase 3 — AgentKit (Weeks 7–9)
    16.5      Phase 4 — VoiceFlow (Weeks 10–12)
    16.6      Phase 5 — RAGeval (Weeks 13–15)
    16.7      Phase 6 — StreamPulse + Polish + Preprint (Weeks 16–18)
    16.8      Weekly Metrics, Decision Gates, And Cumulative Tracker
  Section 17  Daily / Weekly Operating Rhythm
  Section 18  Capacity Rules (When To Stop Applying)
  Section 19  When To Pivot Or Quit

PART VI — INFRASTRUCTURE, TOOLING, AND COST REALITY
  Section 20  Hosting Tiers (Railway, Fly.io, Local-Only)
  Section 21  Pipeline Monitoring (Proposals, Demos, Outcomes)
  Section 22  Tools You Need (Free Or Near-Free)

PART VII — POSITIONING, PRICING, AND PROPOSALS
  Section 23   Vertical Niching Within Each Project
  Section 24   Upwork Profile (Refined)
  Section 25   Pricing By Channel
  Section 26   Six Proposal Templates (Niche-Specific)
  Section 26.5 Applying Your Projects To Real Job Posts — Worked Case Study
               (Equipment Sourcing System job: $5,000, vision-first
                multi-source aggregator — full proposal walkthrough)

PART VIII — RISK AND REALITY CHECK
  Section 27  Things That Will Go Wrong (Plan For Them)
  Section 28  Milestone Expectations (What Realistic Looks Like)
  Section 29  Common Failure Modes (And Their Fixes)

PART IX — THE AI-AGENT BUILD PROMPT
  Section 30  Complete Codebase Splitting Prompt (For Claude/Cursor)
              [Full embedded prompt, ~600 lines, with 2026 stack defaults]

PART X — THE 2027 MULTI-CHANNEL DEPLOYMENT PLAYBOOK
  Section 31  The 2027 Launch Week (January Week 2)
  Section 32  arXiv Submission Window (February–March 2027)
  Section 33  The 2027 LinkedIn Posting Engine
  Section 34  Personal Portfolio Site (yacine.dev or similar)
  Section 35  Cold Email Evolution In 2027
  Section 36  Research-Program Outreach Calendar (Q2 2027)
  Section 37  2027 Quarterly Outcome Targets
  Section 38  The Long Game (2028 And Beyond)

APPENDIX
  Quick Reference Cards
  Project Source Map
  Channel × Project × Template Matrix
  Glossary
```

---

# PART I — THE THESIS AND THE CODEBASE

---

## Section 1: What This Document Is (And Isn't)

### What it is

A concrete, phased, 18-week execution plan to convert the IntelAI codebase
into three compounding assets:

1. **A freelance income pipeline** on Upwork, generating $4k–$15k/month by month 6
2. **An open-source + writing footprint** that pre-loads your 2027 LinkedIn launch
   and makes your future direct-client outreach 5× more credible
3. **Research credentials** (deployed systems + preprints + relationships) for
   top research-degree and fellowship applications in late 2027

Every section is grounded in your actual repository state, your stated goals
(2026 income on Upwork, 2027 expansion, eventual research degrees), and the
realities of being a 0-review freelancer in the AI niche in 2026.

### What it isn't

- **Not a get-rich-quick plan.** First 30 proposals will likely get zero replies.
  This is normal. The plan accounts for it.
- **Not a parallel six-project blitz.** You will build two or three projects
  in sequence, validate market signal, then expand. Building six things before
  the first paying client is a recipe for burning four months on the wrong niches.
- **Not a copy of every AI freelancer's playbook.** Most freelancers don't have
  14k lines of working Python they can point to. Your codebase justifies premium
  pricing and a research-track positioning from day one.

### What changed from v1

The previous draft (`omniinteloscompletestrategy`) was technically excellent
but had four structural weaknesses:

| Issue | v1 Position | v2 Position |
|-------|-------------|-------------|
| Timeline | 12 weeks for 6 projects in parallel | **19 weeks (Week 0 splitting + 18 build weeks)**, all six projects built sequentially, one repo published before the next starts |
| Repo extraction | Incremental, mid-plan | **All 6 repos extracted upfront in Week 0** via single splitting prompt, validated against DocIntel first |
| Channel mix | Upwork-only | Upwork-primary, with parallel open-source + content + cold-email channels |
| Hosting cost | "Railway free tier sufficient" | $20–50/mo realistic; mixed Railway + Fly.io + local-only tiers |
| Research angle | None | Explicit research-credential track running in parallel |
| Competitive landscape | RAGeval framed as "rare" | Acknowledge Phoenix, LangSmith, TruLens, Helicone exist; differentiate as self-hosted/drop-in |
| Demo testing | "Record, upload, link" | Pre-launch to 5–10 trusted reviewers before going live |
| LLM extraction prep | "1–2 days" for DocIntel | 1–2 weeks of prompt iteration with eval dataset |

The technical content (project architectures, code patterns, MCP server design,
LangGraph workflows) is largely preserved from v1 — it was the document's
strongest part, and the audit confirms it's grounded in real code.

---

## Section 2: The Compound-Career Argument

### Why split rather than market the platform whole?

Upwork search works by **keyword and niche specificity**, not by ambition.
A client posting "Build me a RAG pipeline for legal documents" searches for
`RAG`, `LangChain`, `ChromaDB`, `document Q&A` — not `enterprise intelligence
platform`. One mega-platform marketed as "everything" competes with nothing.

But that argument from v1 stops at Upwork. The deeper compounding effect:

```
ONE CODEBASE
    │
    ├─→ 6 FOCUSED REPOS (each a different keyword cluster)
    │     ├─→ UPWORK: 6 different niches to compete in
    │     ├─→ COLD EMAIL: 6 different CTO archetypes to target
    │     └─→ LINKEDIN 2027: 6 different post topics to deploy
    │
    ├─→ OPEN-SOURCE TRACTION (PyPI / GitHub stars)
    │     ├─→ FREELANCE: Social proof that beats reviews
    │     ├─→ RESEARCH APPS: Demonstrated real-world impact
    │     └─→ EMPLOYMENT: Top AI labs hire from OSS contributors
    │
    └─→ TECHNICAL WRITING (1 post per project)
          ├─→ SEO: Long-tail traffic forever
          ├─→ LINKEDIN 2027: Ready-made content library
          ├─→ ARXIV: Workshop-paper drafts → preprints → publications
          └─→ RESEARCH APPS: Show writing, thinking, and depth
```

The same project (`AgentKit`, an MCP server) functions simultaneously as:

- **An Upwork portfolio entry** — proves you can deliver AI agent work
- **An open-source GitHub repo** — proves you understand bleeding-edge protocols
- **A blog post / arXiv-style preprint** — "MCP Tool Design for Business Intelligence Agents"
- **A LinkedIn 2027 cornerstone** — recorded demo + tutorial thread
- **A research-app credential** — applied work in agentic AI / tool use

Building it once gives you five compounding returns. This is why a phased,
quality-over-speed build wins over a parallel six-project sprint.

### Why income first, research second

You stated explicitly: 2026 is for earning and gaining experience on Upwork.
Research-degree applications happen in late 2027 / early 2028.

This sequencing is correct because:

1. **Income reduces cognitive load.** Once basic income is solved, research
   work compounds without survival pressure.
2. **Industrial experience now has narrative weight in research applications.**
   Top programs and labs in 2026 explicitly value "deployed AI systems"
   and "industrial AI engineering experience." This was less true pre-2022.
3. **Reference letters from real clients are stronger than from short-term mentors.**
   A CTO who paid you for 6 months and watched you ship is a more credible
   referee than a professor you took one class with.
4. **You can't research what you haven't shipped.** Your best research ideas
   in 2027 will come from problems you discover shipping in 2026. RAGeval
   exists in this plan precisely because you have observability data sitting
   unlogged in `omnismart_chatbot.py`.

So: build income in 2026, let the research track quietly compound in the
background (one preprint by end of year, open-source published by month 6),
and convert in 2027.

---

## Section 3: Real Codebase Inventory (Audited)

Verified by reading the repo on the date of this document.
Line counts are exact from `wc -l`.

### Backend (Python) — ~14,000 lines

| File | Lines | What It Does |
|------|-------|--------------|
| `src/api/server_v2.py` | 2,579 | 60+ endpoints, full RBAC, JWT, WebSocket chat |
| `src/services/pg_store.py` | 1,669 | 50+ DB functions (KPIs, auth, sessions, audit) |
| `src/services/omnismart_chatbot.py` | 1,658 | 9 personas, LangChain RAG, ChromaDB integration |
| `src/services/advanced_chatbot.py` | 1,137 | 5 Groq patterns, agentic flows, Tavily search |
| `src/integrations/dispatcher.py` | 605 | Gmail/Sheets/n8n/TTS/Voice central dispatcher |
| `src/services/data_ingestion_manager.py` | 558 | CSV/JSON/PDF/Email/Sheets ingestion orchestration |
| `src/services/realtime_pipeline.py` | 500 | Domain classifier, async ingestion, 6-domain routing |
| `src/integrations/n8n.py` | 445 | n8n workflow integration |
| `src/services/ocr_enhancement.py` | 428 | PDF tables, forms, OCR via pdfplumber + tesseract |
| `src/core/i18n.py` | 380 | Full EN/FR translation system |
| `src/core/jwt_auth.py` | 312 | JWT + 9 role definitions, RBAC enforcement |
| `src/core/config.py` | 311 | Settings, RBAC enums, env management |
| `src/models/pg_models.py` | 309 | SQLAlchemy models for all entities |
| `src/services/forecasting.py` | 276 | LinearRegression + Monte Carlo forecasting |
| `src/services/insights.py` | 275 | Health index, 4 anomaly detection methods |
| `src/services/hr.py` | 225 | Headcount, turnover, department metrics |
| `src/services/operations.py` | 204 | Efficiency, utilization, cycle time |
| `src/services/it_ops.py` | 213 | Uptime, incidents, ticket metrics |
| `src/services/logistics.py` | 210 | On-time delivery, OTD, cycle time |
| `src/services/financial.py` | 137 | P&L, balance sheet, EBITDA |
| `src/services/auth.py` | 180 | Auth helpers, bcrypt, session management |
| `src/integrations/camera.py` | 189 | QR pairing + mobile upload flow |
| `src/services/lazy_loader.py` | 160 | Lazy model loading |
| `src/core/performance.py` | 149 | Latency tracking infrastructure |
| `src/integrations/tts.py` | 135 | TTS service wrapper |
| `src/core/monitoring.py` | 122 | Prometheus metrics emitter |
| `src/core/pg_engine.py` | 114 | DB engine and connection pool |
| `src/services/voice/main.py` | 130 | faster-whisper + edge-tts microservice |
| `src/services/ocr/main.py` | ~80 | Tesseract image OCR microservice |
| `src/integrations/__init__.py` | 75 | Public integration API |
| `src/models/schemas.py` | 77 | Pydantic request/response schemas |
| `src/core/logger.py` | 54 | Structured logging |
| `src/core/crypto.py` | 32 | Credential encryption |
| `src/services/ingestion.py` | 107 | Ingestion helpers |
| `src/core/db_engine.py` | 18 | Engine getters |
| `main.py` | 44 | App entry point |

### Frontend (React + Vite) — ~5,500 lines

19 pages, all routed in `App.jsx`. Highlights:

| File | Lines | What It Does |
|------|-------|--------------|
| `frontend/src/pages/DataHubPage.jsx` | 356 | Full ingestion control UI |
| `frontend/src/pages/AdminPage.jsx` | 261 | User management, roles, audit |
| `frontend/src/pages/ScannerPage.jsx` | 256 | Camera + file OCR upload |
| `frontend/src/pages/ChatPage.jsx` | 238 | Sessions, personas, TTS, **but uses HTTP not WebSocket** |
| `frontend/src/pages/ITPage.jsx` | 230 | Incidents, uptime, tickets |
| `frontend/src/pages/AnalyticsPage.jsx` | 230 | KPI browser, **hand-coded SVG bar charts** |
| `frontend/src/pages/HRPage.jsx` | 210 | Headcount, turnover, departments |
| `frontend/src/pages/IntegrationsPage.jsx` | 210 | Gmail, Sheets, ClickUp UI |
| `frontend/src/pages/DashboardPage.jsx` | 199 | KPIs, Health, Summary, Risk cards |
| `frontend/src/pages/RiskPage.jsx` | 192 | Risk score, anomalies |
| `frontend/src/pages/OperationsPage.jsx` | 187 | Efficiency, cycle time |
| `frontend/src/pages/ESGPage.jsx` | 168 | Carbon, safety, governance |
| `frontend/src/pages/LogisticsPage.jsx` | 165 | OTD, delivery metrics |
| `frontend/src/pages/ForecastingPage.jsx` | 153 | Metric select, **lacks proper chart** |
| `frontend/src/pages/MonitoringPage.jsx` | 153 | System health, Prometheus |
| `frontend/src/pages/SettingsPage.jsx` | 133 | Language, preferences |
| `frontend/src/pages/LoginPage.jsx` | 112 | Auth form |
| `frontend/src/pages/FinancialPage.jsx` | 70 | **Stub — minimal content** |
| `frontend/src/pages/BulkDataPage.jsx` | 67 | **Stub — minimal content** |

Plus components (`DataIngestionPanel`, `FloatingChat`, `PairingModal`,
`Sidebar`, `FilePreview`), full EN+FR translations, and a working
design system.

### Infrastructure

```
docker-compose.yml         13 services: postgres, fastapi, frontend,
                           prometheus, grafana, n8n, ocr, voice, tunnels
Dockerfile                 Backend image (Python 3.10)
frontend/Dockerfile        nginx-served frontend
src/services/ocr/          Standalone OCR microservice (Tesseract, :8001)
src/services/voice/        Standalone voice microservice (Whisper, :8002)
monitoring/                Prometheus rules + Grafana provisioning
scripts/                   10 ops shell scripts
n8n_workflows/             4 pre-built n8n workflows
tunnels/                   Cloudflare tunnel configs
db/schema.sql              Full PostgreSQL schema
```

### API Surface (60+ endpoints)

Organized in groups:

```
AUTH       (5)   login, register, me, logout, status
CHAT       (10)  /chat HTTP, /ws/chat WebSocket, /personas, sessions, domain
KPI        (7)   kpis, periods, metrics, categories + insights health/risk/summary
INGESTION  (12)  metrics, csv, document + data/ingest, spreadsheets, bulk
DOMAIN     (14)  hr, operations, esg, logistics, financial, IT
INTEGRATIONS (9) Gmail, Sheets, ClickUp OAuth + connect/disconnect
VOICE/OCR  (4)   transcribe, tts, ocr/extract
CAMERA     (5)   pair, upload, sessions
ADMIN      (8)   users, roles, audit, seed, monitoring, /metrics, /health
```

### Nine AI Personas (Implemented in omnismart_chatbot.py lines 1048–1230)

```
PERSONA   TEMP   DATA_ACCESS               ALLOWED_TOOLS
ceo       0.4    All 6 domains             kpi, forecast, report, market
cfo       0.2    Finance, Growth           kpi, forecast, financial_stmt
cto       0.3    Operations, Finance, IT   kpi, risk, tech_metrics
coo       0.3    Operations, Growth, People kpi, ops_metrics, supply_chain
chro      0.4    People, ESG               kpi, people_metrics, engagement
esg       0.3    ESG, Operations, People   kpi, esg_metrics, sustain_rpt
risk      0.2    Finance, Operations       kpi, risk_analysis, alerts
analyst   0.3    All except admin          kpi, forecast, analysis, report
general   0.5    Finance, Growth           kpi, basic_query
```

Each persona has: custom system prompt, role-to-persona auto-mapping,
temperature tuned (executives conservative, analysts flexible), tool
whitelist, and data scoping.

### Synthetic Dataset (`enhanced_synthetic_dataset/`)

- 25,920 KPI records across 10 companies, 144 monthly periods, 5 domains
- 30 P&L / balance sheet JSON files (10 companies × 3 years)
- 3 sample invoice PDFs (for OCR testing)
- 5 sample images / charts (for vision)
- 10 email samples (for Gmail automation testing)
- 5 sheets exports (for Sheets automation testing)
- 30 n8n webhook payloads
- 5 domain configuration files

**Why this matters:** every demo can show real data flowing through real
pipelines. That's a credibility advantage 90% of freelancer portfolios lack.

---

## Section 4: What's Weak, What's Missing, What to Sharpen

### Weak — Needs Fixing Before Going Public

#### Issue 1: Charts look like a 2018 prototype

`AnalyticsPage.jsx` and `ForecastingPage.jsx` use hand-coded SVG bars:

```jsx
<div style={{
  flex: 1,
  height: `${(d.value / maxVal) * 100}%`,
  background: 'var(--primary)',
  borderRadius: '4px 4px 0 0',
}} />
```

This is the **single highest-ROI fix in the entire repo**. Recharts is in
neither `package.json` nor the codebase. `npm install recharts` plus 2 days
of integration transforms every demo screenshot. Do this first regardless
of which projects you build.

#### Issue 2: WebSocket streaming chat is built but not wired

`server_v2.py` line 1553: `@app.websocket("/api/v1/ws/chat")` exists and works.
`frontend/src/pages/ChatPage.jsx`: uses `api.post('/chat')` — the HTTP endpoint.

Users wait 2–5 seconds for a full response when they could see it streaming
token by token. Streaming feels 5× more impressive in demos. 1 day of work
to wire it.

#### Issue 3: Tests are skeletal

```
tests/test_api.py: 25 lines, 2 test functions (health + login)
tests/test_ui_playwright.py: 453 lines but mostly fixture skeletons
```

A CTO who clones the repo and runs `pytest` sees:

```
collected 2 items
PASSED tests/test_api.py::test_health
PASSED tests/test_api.py::test_login
```

That's a credibility problem on inspection. Expand to 25–30 API tests
covering auth, RBAC, chat, KPI, insights, ingestion, monitoring,
knowledge search.

#### Issue 4: README misrepresents the build

43,934-byte README with 26 appendices. Mentions "React frontend at
localhost:5173 (when implemented)" but the frontend is fully implemented.
Claims features that need the full Docker stack but doesn't provide a
one-command demo path.

Replace with a clean <200-line README that matches what actually works,
links to the live demo, and ships in 1 day.

#### Issue 5: Financial and Bulk pages are stubs

`FinancialPage.jsx`: 70 lines — title and loading state only
`BulkDataPage.jsx`: 67 lines — title and empty state only

They appear in the router. Anyone navigating to them sees nothing. Either
complete them (1–2 days each) or remove from the router entirely.

#### Issue 6 (NEW, missing from v1): No prompt eval discipline

The chatbot's RAG quality is unknown. There's no eval set, no recorded
groundedness scores, no regression test for retrieval relevance. If a
client clones it and the chatbot hallucinates on their data, they'll
walk away.

Add a small eval set (20–30 manually-graded query/answer/source-doc
triples in `tests/rag_eval.jsonl`) and a script to score current
performance against it. This work directly feeds RAGeval (Project 5).

### Missing — Net-New Builds Required

#### Missing 1: Persona-Routed RAG Evaluation Documentation

You have 9 personas. You don't have a single document showing **why
this design wins over a single-prompt chatbot**. A client (and a
research-app reader) wants to see the comparison: same query, 9 different
persona responses, measurable differences in retrieval and groundedness.

This is a 1-day write-up that becomes the basis for your first technical
blog post and an eventual workshop paper.

#### Missing 2: Open-source publication of any module

Nothing in this repo is `pip install`-able as a standalone library. The
most natural candidates:

- `omnismart-personas` — persona templates and resolution logic as a
  small library (consumable by any LangChain user)
- `rageval` — the LLMOps observability package (Project 5)
- `agentkit-mcp` — the MCP server module (Project 2)

Each of these published to PyPI with even 100 downloads a month is
a stronger credential than 95% of freelancer portfolios. Plan to ship
two by end of 2026.

#### Missing 3: Technical writing

No blog posts. No arXiv preprints. No conference workshop submissions.
Every other entry on a research-degree application has at least one.
This is the gap.

The plan calls for 6 technical posts in 2026 (one per project, one
every 3 weeks), at least one of which gets reworked into an arXiv
preprint by end of year.

#### Missing 4: Vertical positioning

Your current README markets "IntelAI" to "enterprises in general."
A Series A SaaS CTO and a healthcare CIO have completely different
buying criteria. You'll close more deals positioning as "AI analytics
for Series A SaaS" or "AI analytics for healthcare compliance" than
as "enterprise OS for everyone."

Pick one primary vertical and one secondary for each project, and
write proposal templates targeted at each.

#### Missing 5: A working LLMOps loop

Your chatbot returns `tokens_used` and `latency_ms` but logs neither.
The data needed for RAGeval already exists at the API boundary —
it's just unpersisted. Build the storage layer in Phase 5.

#### Missing 6: A research-app narrative

Your eventual research application needs a coherent through-line:
"I built X production systems in 2026, observed Y patterns, formalized
them into Z preprint, want to extend at PhD level into W."

Plan that narrative now so each blog post and each project description
reinforces it. Suggested through-line: **persona-routed and role-scoped
RAG as a production-deployable alignment pattern**. (Why this is good:
it's interpretable, evaluable, falsifiable, and connects to current
alignment-research interest in role/persona conditioning.)

---

## Section 4.5: 2026 Stack Refresh — What's Leading And Why

The v1 strategy was written against an early-2025 stack. The world has moved.
This section maps the 2026 leading stack across the layers each of your six
projects touches, and names the specific upgrades you should bake into the
repos when Phase 0 splits the codebase.

The principle: **lead with the strongest model in each tier, fall back to the
fastest/cheapest, never lock to a single vendor.** Multi-provider abstraction
via LiteLLM (or equivalent) is now table stakes — clients ask about it in
interviews.

### 4.5.1 The Frontier LLM Landscape (May 2026)

Tier 1 — Frontier reasoning (use for hard agent loops, executive personas,
nuanced analysis):

```
MODEL                     STRENGTH                        TYPICAL USE
─────────────────────────────────────────────────────────────────────────
Claude Opus 4.7           Best agentic + coding +         Planner agent,
(Anthropic)               long-horizon reasoning           preprint co-author,
                                                           executive RAG
Claude Sonnet 4.6         80% of Opus quality at          Default workhorse
                          3× speed and ~5× cheaper         for production
Claude Haiku 4.5          Cheapest frontier; great        LLM-as-judge,
                          for high-volume judge tasks      classifiers
GPT-5 / o3-pro            Strong for math, code,          Optional alternative
(OpenAI)                  research benchmarks              for diversity
Gemini 2.5 Pro            Massive context (2M tokens),    Long-document RAG,
(Google)                  multimodal native                video understanding
```

Tier 2 — Fast inference for volume (when you don't need frontier quality):

```
MODEL / PROVIDER          STRENGTH                        TYPICAL USE
─────────────────────────────────────────────────────────────────────────
Groq Llama 3.3 70B        ~500 tok/sec, $0.59/M out       High-volume RAG,
                          industry-leading speed           per-query analysis
Cerebras Inference        ~1800 tok/sec on Llama 3.3      Real-time UX,
                          (fastest available 2026)         streaming chat
Together AI / Fireworks   Hosted open weights at scale    Custom fine-tunes,
                                                           batch jobs
DeepSeek V3.5 / Qwen 3    Strong open-weights frontier    Local + Ollama tier,
                                                           sovereign deployments
```

Tier 3 — Local / on-prem (Ollama + commodity GPU or even CPU):

```
MODEL                     RUNS ON                          USE CASE
─────────────────────────────────────────────────────────────────────────
Llama 3.3 70B             1× A100 / 2× consumer GPU       Self-hosted dashboards
Qwen 3 32B                Single 4090 / mac M3            Embedded + tool use
Llama 3.2 Vision (11B)    1× 3090 / 4090                  Vision-first OCR
Qwen 2.5-VL (7B)          Mac M2/M3, lighter GPU          Document AI on-prem
Gemma 3 (8B vision)       Mid-tier GPU                    Vision classification
DeepSeek V3-lite          Apple M-series Macs             Latency-sensitive local
```

**Practical implication for your projects:** every project should default to
Claude Sonnet 4.6 for quality-critical paths, Groq Llama 3.3 70B for
high-volume paths, and ship with an Ollama path documented for clients who
need local. The proposal to the Equipment Sourcing job (Section 26.5) is
*precisely* this stack — local Ollama + n8n + vision LLM — and you should be
able to claim that experience because your DocIntel + StreamPulse repos
demonstrate it.

### 4.5.2 RAG In 2026 — Beyond Naive Vector Search

The "embed-and-cosine-similarity" RAG that defined 2023–24 is now considered
the baseline. The leading patterns in 2026:

**1. Hybrid retrieval (mandatory now).** Combine dense (embedding) with sparse
(BM25) retrieval, then merge with Reciprocal Rank Fusion. Pure vector search
fails on rare entities and exact-match queries (product codes, names).

```
QUERY → [dense search via bge-large] → top-50 docs
      ↘ [sparse search via BM25]    → top-50 docs
                                      ↓
                              RRF merge → top-30 docs
                                      ↓
                          [cross-encoder rerank: bge-reranker-v2-m3]
                                      ↓
                                  top-5 docs → LLM
```

**2. Reranking with a cross-encoder.** A bi-encoder embedding model is fast
but loose. A cross-encoder reranker (BGE Reranker v2 m3, Cohere Rerank v3,
Voyage Rerank-2) takes the top-50 retrieved docs and rescores them by
attending to query+doc jointly. Adds 100-300ms, but precision@5 jumps
20-40%.

**3. GraphRAG (Microsoft Research, 2024) — now production-deployable.**
Extracts entities and relationships during ingestion, builds a knowledge
graph, performs graph-traversal queries for multi-hop reasoning. Critical
for queries like "show me how X relates to Y across Z time periods" — which
is exactly the executive analytics pattern in IntelAI.

**4. Agentic RAG.** Instead of retrieve-once-and-answer, an agent decides
*what* to retrieve, *when* to re-query, and *when to give up*. Uses tool
calling against the retrieval API as a sub-tool. LangGraph and CrewAI are
the dominant frameworks. The latency cost is real (3-10x slower than naive
RAG) but the quality on complex queries is dramatically better.

**5. Long-context-as-RAG (controversial).** Gemini 2.5 Pro's 2M-token context
and Claude Sonnet 4.6's 1M-token context let you skip retrieval entirely for
many use cases — just paste the whole document. Cheaper than expected
because of caching. Doesn't replace RAG for huge corpora, but reduces it for
medium-sized knowledge bases.

**6. ColBERT and late-interaction.** Token-level scoring, not document-level.
Better for fine-grained matching. Open-source via PyLate / RAGatouille. Niche
but research-strong.

**Practical implication:** IntelAI and AgentKit should both upgrade from
pure ChromaDB cosine similarity to hybrid retrieval + reranker. RAGeval
should measure all of these as separate metrics, because "retrieval quality"
is no longer a single number — it's a stack.

### 4.5.3 Embeddings In 2026

```
MODEL                          OPEN?  TIER         USE CASE
─────────────────────────────────────────────────────────────────────
OpenAI text-embed-3-large      No     Premium      Production default
                                                    (3072d, $0.13/M tokens)
Voyage AI voyage-3-large       No     Premium      Best benchmark, $0.18/M
Cohere embed-english-v3        No     Premium      Strong for English
BGE-large-en-v1.5 (BAAI)       Yes    Self-host    Best open weights baseline
                                                    (1024d, free)
BGE-M3                         Yes    Self-host    Multilingual + multi-vector
                                                    (1024d, free)
Jina embeddings v3             Yes    Self-host    Fast, code-friendly
Nomic embed v1.5               Yes    Self-host    Long-context (8k tokens)
sentence-transformers          Yes    Legacy       Still works, but older
all-MiniLM-L6-v2                                    (384d, smaller, faster)
```

**Practical implication:** for IntelAI keep MiniLM as the fast lane,
add BGE-large for the persona-grounded paths. For RAGeval, both should be
recorded so you can compare embedding quality per metric.

### 4.5.4 Vector & Hybrid Stores

```
STORE              FIT                                   COMMENT
──────────────────────────────────────────────────────────────────────
Qdrant             Self-hosted, production-grade        2026 leader
                                                         for self-host
Weaviate           Hybrid (vector + scalar) + graph     Strong for GraphRAG
LanceDB            Embedded, fast, file-based            Replacing Chroma
                                                         for serverless
pgvector + Postgres Unified with relational              Rising fast (one DB
                                                          to operate)
Chroma             Simple, popular                       Fine for prototype,
                                                         not production
Pinecone           Managed                                Premium, easy
Turbopuffer        Serverless cloud vector              New, fast-growing
```

**Practical implication:** IntelAI should add an "advanced" config that
swaps ChromaDB for **Qdrant or pgvector**. The README should explicitly say
"ChromaDB for dev, Qdrant for prod" — this resonates with senior buyers.

### 4.5.5 Agent Frameworks In 2026

```
FRAMEWORK           STRENGTH                        WHEN TO USE
─────────────────────────────────────────────────────────────────────
LangGraph           Graph-based, stateful,           Production multi-step
                    Anthropic-friendly                workflows
Claude Agent SDK    Anthropic-native, MCP-first      Anything Claude-centric
                                                      (your strongest path)
CrewAI              Role-based multi-agent           Marketing differentiation,
                                                      easier mental model
AutoGen             Microsoft, conversation-first    Enterprise/Microsoft buyers
DSPy                Programming, not prompting       Research credential,
                                                      self-optimizing pipelines
OpenAI Swarm        Lightweight handoffs             Lean orchestration
Pydantic AI         Type-safe, model-agnostic       Production reliability
                                                      (rising fast)
```

**Practical implication:** AgentKit (Project 2) goes from "MCP server +
LangGraph" to "MCP server + LangGraph + Claude Agent SDK demo + CrewAI
example." Three demos in one repo signals breadth. DSPy as a sub-experiment
is your research credential — it's where current AI eng research is moving.

### 4.5.6 Vision-LLM For Document/Image Understanding

This is the single biggest 2026 stack shift relevant to your projects. The
old pipeline `OCR → text → LLM` is being replaced by `image → vision LLM →
JSON` for almost every document and image task.

```
MODEL                     OPEN?   STRENGTH                  RUNS ON
──────────────────────────────────────────────────────────────────────
Claude Sonnet 4.6 Vision   No     Best for complex layouts   API only
GPT-4o Vision / GPT-5      No     Strong, broad use cases   API only
Gemini 2.5 Flash Vision    No     Cheapest premium tier     API only
Llama 3.2 Vision 11B/90B   Yes    Best open-weights         Ollama / vLLM
Qwen 2.5-VL 7B/72B         Yes    Best small open-weights   Ollama
Pixtral 12B (Mistral)      Yes    Document-focused          1× GPU
PaliGemma 2 (Google)       Yes    Lightweight, embedded     Mid-tier GPU
Gemma 3 Vision (8B)        Yes    Local-first design        Consumer GPU
```

**Practical implication:** DocIntel (Project 3) gets a major upgrade. Instead
of `pdfplumber → pytesseract → Groq text extraction`, the modern pipeline is:

```
PDF → render page to image
    → choose route:
        Route A (premium): Claude Sonnet 4.6 Vision → structured JSON
        Route B (local):   Llama 3.2 Vision via Ollama → structured JSON
        Route C (legacy):  Tesseract OCR → text → LLM (fallback only)
    → validate JSON schema
    → store
```

The "vision-first" framing is what the Equipment Sourcing job post explicitly
asks for. Your DocIntel repo, with vision-first as the headline mode and
Ollama support as a documented config, becomes the perfect case study for
that job.

### 4.5.7 Speech Stack In 2026

```
LAYER                     2025 LEADER       2026 LEADER
─────────────────────────────────────────────────────────────────────
Self-host transcription   faster-whisper    WhisperX (faster-whisper +
                                            forced alignment + diarization
                                            in one) or NVIDIA NeMo Canary
                                            (research SOTA 2026)
Premium transcription API Whisper API       Deepgram Nova-3 or
                                            AssemblyAI Universal-2
                                            (both beat Whisper on streaming +
                                            diarization for production)
Diarization               pyannote.audio    pyannote 3.x (now production-stable)
                                            or NeMo's built-in
Open TTS                  edge-tts          Kokoro TTS (open, expressive)
                                            or Coqui XTTS v2
Premium TTS               ElevenLabs        ElevenLabs Multilingual v3
                                            or OpenAI tts-1-hd
Real-time voice agents    n/a               OpenAI Realtime API (gpt-4o-realtime)
                                            or Hume EVI 2 (emotionally aware)
```

**Practical implication:** VoiceFlow (Project 4) becomes more compelling with
multi-provider transcription (faster-whisper local, Groq Whisper for speed,
Deepgram for premium) and adds a "real-time voice agent" demo using OpenAI
Realtime API. That demo is the visual hook that makes the project memorable.

### 4.5.8 LLMOps + Observability In 2026

```
TOOL                      STRENGTH                    WATCH FOR
─────────────────────────────────────────────────────────────────────
Phoenix (Arize)           OSS leader, hosted optional Strong defaults
Langfuse                  Self-host or SaaS           Rich integrations
TruLens                   OSS eval-first              Research community
Helicone                  Proxy-style observability   Simplest install
OpenLLMetry               OpenTelemetry-native        Standards path
                          (Traceloop)                  for enterprise
Weights & Biases Weave    GenAI-focused W&B           Strong for fine-tuning
LangSmith                 LangChain-native            Tied to LangChain
Arize Copilot             Auto-debugging agent        Frontier feature
                          (2026 launch)
```

**Practical implication:** RAGeval (Project 5) should explicitly support
OpenLLMetry / OpenTelemetry export. That makes it interoperable with any
enterprise observability stack. The differentiator stays: self-hosted,
SQLite-default, persona-aware, drop-in decorator — but with OTEL export,
enterprise buyers can route data to their existing observability platform.

### 4.5.9 Orchestration + Data Pipelines

```
TOOL              FIT
─────────────────────────────────────────────────────────────────────
Prefect 3         Modern Python, async-native, hybrid hosted+self-host
Dagster           Asset-based, strong for analytics
Airflow           Still industry default, especially in big-data shops
n8n               No-code/low-code, growing in SMB + AI-aggregator builds
                  (the Equipment Sourcing job explicitly uses n8n)
dlt               Declarative ingestion, "the Stripe of pipelines"
Estuary Flow      Real-time CDC, growing
Apache Kafka      Still the default for high-throughput streaming
Modal             Serverless Python for AI workloads (rising)
RunPod / Vast.ai  Cheap GPU for batch inference
```

**Practical implication:** StreamPulse (Project 6) should ship with **first-class
n8n integration** (a documented n8n node or webhook endpoint pattern) and an
optional Prefect orchestration example. n8n is now in the job posts you'll
respond to — being able to claim "deployed and integrated with n8n in
production" is worth real money.

### 4.5.10 Research-Strong Stack Choices (Signals For 2027–28 Applications)

If your goal is research-program admission, a few stack choices send
disproportionate signal because they're the same tools researchers use:

```
SIGNAL TOOL              WHY IT MATTERS FOR RESEARCH APPLICATIONS
─────────────────────────────────────────────────────────────────────
DSPy                     The "programming over prompting" paradigm; cited
                         in 2025–26 papers; using it suggests methodological
                         depth
LangGraph                The default agent framework in Anthropic-adjacent
                         research; pairs with arXiv-citable agent papers
OpenLLMetry              Standards-track observability — researchers respect
                         instrumentation discipline
pyannote.audio           Standard in speech research; using it signals
                         you've read the literature
ColBERT / RAGatouille    Late-interaction retrieval is a research topic;
                         engaging with it signals you read IR papers
W&B Weave                Researchers use W&B; "I tracked this with Weave"
                         is a research-fluent phrase
LiteLLM                  Engineering hygiene — multi-provider is now a
                         hallmark of mature systems
```

You don't need every tool. But **two or three of them sprinkled across the
six repos** signal: this person reads papers, ships systems, and respects
the discipline.

### 4.5.11 Pricing And Provider Strategy (Realistic, 2026)

```
MODEL                            COST (per 1M tokens, in/out)   USE WHEN
─────────────────────────────────────────────────────────────────────────
Claude Opus 4.7                  $15 / $75                       Critical reasoning
Claude Sonnet 4.6                $3 / $15                        Default production
Claude Haiku 4.5                 $0.80 / $4                      Judge/classify
GPT-5                            $10 / $40 (est.)                Alternative frontier
Gemini 2.5 Pro                   $1.25 / $10                     Long context
Groq Llama 3.3 70B               $0.59 / $0.79                   High-volume speed
Together Llama 3.3 70B           $0.88 / $0.88                   Batched API
DeepSeek V3.5                    $0.27 / $1.10                   Cheapest frontier
                                                                  (research-trained)
Local Llama 3.3 70B (Ollama)     $0 + electricity                Privacy / cost cap
```

A typical production IntelAI chat call might mix:
- Claude Sonnet 4.6 for the persona-grounded synthesis ($0.02 per call)
- Groq Llama 3.3 70B for high-volume KPI summarization ($0.001 per call)
- Local Llama 3.2 Vision via Ollama for any document parsing ($0)

**This three-tier mix is exactly what enterprise buyers want**: top quality
where it matters, fast/cheap for volume, local for privacy. Your README
should describe it explicitly in the architecture section.

### 4.5.12 The Multi-Provider Abstraction Layer

In 2026, locking to a single provider is now a yellow flag in client
interviews. Use **LiteLLM** (or `instructor`, or your own thin wrapper) to
make every LLM call routable across providers via config:

```python
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
```

Every one of the six projects should adopt this pattern. The cost is one
afternoon of refactor; the upside is that you can demo each project against
Claude, Groq, GPT, and a local Ollama instance — and clients see this in
the README and immediately trust you.

---

# PART II — THE SIX PROJECTS (Refined)

The technical content of the 6 projects from v1 was the strongest part
of that document. It is preserved here with refinements based on the
reality checks above. Specifically:

- Project 1 adds a vertical-positioning section and a prompt-eval task
- Project 2 reframes the primary channel (GitHub + blog, not Upwork)
- Project 3 expands the LLM-extraction prompt-tuning timeline
- Project 4 adds a fallback path if pyannote diarization fails to install
- Project 5 acknowledges Phoenix/LangSmith/TruLens and sharpens the differentiator
- Project 6 reframes the primary channel (cold email, not Upwork)

---

## PROJECT 1: IntelAI Refactored
### AI Analytics Platform with Persona-Aware RAG Copilot

### 1.1 What it becomes

IntelAI is the **scoped** extraction from the original codebase — *not* the all-in-one
platform (that is now the separate private `OmniIntelOS` repo). Reframe as:

> **A production-ready AI analytics backend with a 9-persona RAG copilot,
> multi-domain KPI intelligence, GraphRAG-lite retrieval, ML forecasting, and
> board-ready exports. JWT + RBAC. Bilingual (EN/FR). One cloud deployment.**

This maps to five Upwork search queries (RAG developer, FastAPI developer, BI
developer, AI chatbot developer, AI integration engineer) and is concrete enough for a
CTO to evaluate.

**IntelAI scope (authoritative).** One cloud deployment (Railway/Fly + managed
Postgres); no on-prem multi-service stack.

KEEP (in scope):
- Multi-domain KPI analytics (Finance, HR, IT, Ops, Logistics, ESG, Risk): Dashboard,
  Analytics, Forecasting (Monte Carlo CI), Insights/anomalies, board-ready PDF export.
- 9-persona RAG copilot — role-scoped data, WebSocket streaming, source citations.
- **GraphRAG-lite + hybrid retrieval + BGE reranker** — the branded differentiator.
- LiteLLM multi-provider router; Auth + JWT + RBAC; bilingual EN/FR.
- ChromaDB (dev) / pgvector or Qdrant (prod, via env).
- Packageable: `omnismart-personas` on PyPI — the only artifact shared across projects.

CUT — these belong to the separate full OmniIntelOS platform or to sibling niches;
**Phase 1 removes them from this repo**:
- Monitoring (Prometheus/Grafana/alert rules), nginx, Cloudflare tunnels, the
  multi-service on-prem `docker-compose.yml`, MonitoringPage → **OmniIntelOS platform**.
- n8n workflows + N8NWorkflowPage + IntegrationsPage → OmniIntelOS / StreamPulse + AgentKit.
- OCR microservice (`src/services/ocr`, ScannerPage, `omnitel-ocr`) → **DocIntel**.
- Voice microservice (`src/services/voice`, VoicePage, `omnitel-voice`) → **VoiceFlow**.
- Heavy BulkData/DataHub ingestion → trim to a simple CSV/JSON upload; streaming → StreamPulse.

**Dependency rule:** IntelAI must build, test, and deploy with **zero** runtime or import
dependency on the OmniIntelOS platform or any of the other 5 projects. The personas package
is consumed via PyPI, not via a repo link.

### 1.2 Architecture (what exists today)

```
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
```

### 1.3 What to fix (concrete code changes)

Five fixes. Roughly 2 weeks of work total.

#### Fix A — Install and wire Recharts (2 days)

```bash
cd frontend
npm install recharts
```

In `frontend/src/pages/AnalyticsPage.jsx`, replace the hand-coded SVG bars
with `LineChart`. In `ForecastingPage.jsx`, use `AreaChart` with two `Area`
components to show forecast values with confidence-interval shaded bands.
In `RiskPage.jsx`, add a `RadarChart` for risk-component visualization.
In `DashboardPage.jsx`, add 60px-tall sparkline `LineChart`s inside each
KPI card. In `FinancialPage.jsx`, replace the stub with a `BarChart` of
line-items from `/api/v1/financial/statement`.

(Detailed code snippets retained from v1 — they're correct.)

#### Fix B — Wire WebSocket streaming in ChatPage (1 day)

Replace the `api.post('/chat')` call with a WebSocket connection to
`/api/v1/ws/chat`. Authenticate on `onopen`, accumulate chunks on
`onmessage`, set streaming state to false on `done`.

The pattern in v1 is correct. Test against all 9 personas. Watch for
CORS issues — handle them in your `server_v2.py` CORS middleware
configuration.

#### Fix C — Complete FinancialPage.jsx (1 day)

70-line stub becomes a working page with statement-type select
(income statement, balance sheet, cash flow), a `BarChart` of line
items, and proper currency formatting.

#### Fix D — Expand tests from 2 to 30+ (2 days)

Cover: auth (success, wrong password, register, get-me, viewer-blocked),
chat (basic, with persona, sessions list), KPIs (get, periods, metrics),
insights (health, risk, summary, anomalies), ingestion (valid, empty),
forecast, RBAC (admin works, viewer blocked), knowledge search,
monitoring stats, Prometheus metrics endpoint.

#### Fix E — Railway deployment (1 day)

Create `railway.toml` at repo root. Configure environment variables
in the Railway dashboard. Connect Railway-provisioned PostgreSQL
via `DATABASE_URL`. Confirm `/health` returns healthy and the
synthetic dataset loads on first run.

**Hosting note (NEW from v2):** Railway free credit may not sustain
this always-on. If costs trip $20/mo, move to Fly.io with a small
shared-cpu-1x machine and an external Supabase free-tier Postgres.
See Section 20.

### 1.4 What's new from v1

#### NEW: Vertical positioning options

Pick a primary vertical to lead with on Upwork. Three good candidates:

| Vertical | Why it works | Sample headline |
|----------|--------------|-----------------|
| **Series A SaaS** | KPIs already align (ARR, churn, headcount, runway). High Upwork volume. | "AI analytics + RAG copilot for Series A SaaS — built around SaaSOps KPIs and finance reporting cadence." |
| **Healthcare KPI / Compliance** | Long-tail demand, willing to pay premium for ESG-style domain coverage. | "Healthcare analytics with role-scoped AI copilot — clinical, ops, and compliance KPIs with audit logging." |
| **ESG / Sustainability** | Mandatory reporting wave in EU + parts of US drives demand. Your ESG domain is real. | "ESG reporting copilot — automated compliance reporting from raw KPI data with AI-generated executive summaries." |

You don't have to commit to one. You can run three parallel proposal templates,
each emphasizing the vertical-specific value. But **the demo Loom video must
show data that looks like the targeted vertical** — generic "Company X"
demo data is less compelling than "Acme SaaS, ARR $4.2M, churn 3.1%."

Generate three vertical-flavored datasets from your existing 25,920-record
base. 1 day of work.

#### NEW: Prompt eval discipline

Before going public, build a small RAG eval set:

```
tests/rag_eval.jsonl
  20-30 entries, each:
    {
      "query": "What was our Q1 2025 churn rate?",
      "expected_keywords": ["churn", "Q1", "2025"],
      "expected_sources": ["finance_kpis_2025q1.csv"],
      "min_groundedness": 0.7
    }
```

Run weekly. If groundedness drops below threshold across more than
20% of the eval set, fix before shipping new chatbot changes.

This work directly seeds Project 5 (RAGeval).

### 1.5 Demo recording script (3 minutes)

```
0:00 - 0:15  Login as CFO persona, land on Dashboard.
             Health Index 72/100. 6 KPI cards visible with sparkline trends.

0:15 - 0:45  Click Chat. Ask "Why is our gross margin declining this quarter?"
             Watch streamed response appear word by word.
             Source citations visible at bottom of response.

0:45 - 1:20  Switch persona to CHRO mid-session.
             Ask "What's our headcount trend and turnover risk?"
             Different response style, different data scope (no Finance data).

1:20 - 1:50  Navigate to Forecasting.
             Select "Revenue", click Run Forecast.
             AreaChart appears with confidence-interval shaded bands.
             Show Monte Carlo p10/p50/p90 scenario numbers.

1:50 - 2:20  Navigate to Risk page.
             RadarChart shows risk profile across domains.
             Click an anomaly in the table — drill-down to source data.

2:20 - 2:45  Dashboard → Export PDF button.
             PDF downloads. Open first page — health gauge, KPIs, narrative.

2:45 - 3:00  Log out. Log in as `viewer` role.
             Sidebar menu is restricted — admin tools hidden.
             Demonstrates role-based access control.
```

Upload to Loom. Link in profile and in every proposal.

**NEW from v2:** Before going public with this video, share it with 3–5
trusted reviewers (peer freelancers, friends with tech backgrounds,
your future self after sleep). Get feedback. Iterate. Most demos fail
because they're optimized for the builder, not the buyer.

### 1.6 Upwork niches for IntelAI

```
NICHE 1: RAG / AI Chatbot Developer
  Search: RAG developer, LangChain developer, AI chatbot, ChromaDB
  Angle:  "9 specialized AI personas with role-based data scoping.
           ChromaDB RAG with source citations. Streaming responses.
           Production-deployed."

NICHE 2: FastAPI / Python Backend Developer
  Search: FastAPI developer, Python API developer, async backend
  Angle:  "60-endpoint async FastAPI with JWT auth, RBAC,
           PostgreSQL, WebSocket streaming. 30+ tests."

NICHE 3: Business Intelligence / Analytics Developer
  Search: BI developer, analytics dashboard, KPI dashboard
  Angle:  "Multi-domain KPI platform: Finance, HR, Ops, ESG.
           ML forecasting with confidence intervals. Board-ready exports."

NICHE 4: AI Integration Engineer
  Search: AI integration, LLM integration, Groq developer
  Angle:  "Gmail/Sheets/ClickUp OAuth integration.
           n8n workflow automation. Production-deployed."

NICHE 5 (NEW): Vertical-Specific (rotate based on demand)
  Search: SaaS analytics developer, healthcare reporting AI, ESG reporting
  Angle:  "[Vertical-specific value statement]"
```

### 1.7 Research-track artifact

Project 1's research output is a technical blog post / arXiv-style preprint:

> **"Persona-Routed RAG: Role-Based Data Scoping for Production AI Assistants"**
>
> A pattern for routing the same retrieval system through different
> persona-conditioned prompts and data filters. Demonstrated on a
> 9-persona business-intelligence assistant. Evaluated on retrieval
> relevance, groundedness, and adherence to role data boundaries.
> Open-source persona templates released as `omnismart-personas`.

This becomes:

- A 2,000-word blog post (drafted in 2026, published in 2027 — see Section 5.1
  for the 2026-vs-2027 channel split)
- A 6-page arXiv-style preprint (drafted in 2026, submitted in 2027)
- A LinkedIn post in 2027 ("Here's what I learned building production RAG")
- A research-app credential ("I demonstrated this pattern in deployment")

### 1.10 2026 Stack Upgrade For IntelAI (apply during Phase 0 + Phase 1)

The original IntelAI shipped on Groq + LangChain + ChromaDB + sentence-transformers
(MiniLM). For 2026 leadership, upgrade in three targeted moves. None of these
are blocking — the existing stack works — but each upgrade adds a line your
clients ask about in interviews.

**Move 1 — Multi-provider LLM via LiteLLM (mandatory, low effort).**

```python
# requirements.txt (new entries)
litellm>=1.55.0
anthropic>=0.40.0   # if not already
openai>=1.55.0      # for GPT-5 / Realtime API path

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
```

Every persona handler in `omnismart_chatbot.py` calls `llm_call(...)`. The
default tier covers Business Analyst, General User, COO, CHRO, ESG Officer.
The reasoning tier (Claude Sonnet 4.6) covers CEO, CFO, CTO, Risk Manager
where nuance and reasoning depth matter. The judge tier (Claude Haiku 4.5)
is used by RAGeval integration.

**Move 2 — Hybrid retrieval + reranker (medium effort, big quality jump).**

```python
# requirements.txt (new entries)
rank-bm25>=0.2.2
FlagEmbedding>=1.3.0       # for BGE reranker
# (sentence-transformers already installed)

# src/services/hybrid_retrieval.py (NEW FILE)
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
from FlagEmbedding import FlagReranker

class HybridRetriever:
    def __init__(self):
        self.embedder = SentenceTransformer("BAAI/bge-large-en-v1.5")
        self.reranker = FlagReranker("BAAI/bge-reranker-v2-m3",
                                     use_fp16=True)
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
```

Add a config flag `USE_HYBRID_RETRIEVAL=true` so the upgrade is opt-in
during Phase 1 polish, then enabled by default in production.

**Move 3 — GraphRAG-lite for cross-domain queries (research-credential
move, optional but high signal).**

Most enterprise queries that fail in naive RAG are multi-hop: "show me how
headcount in Engineering correlates with Finance margin over the last 6
quarters." Pure vector search returns disjoint snippets. GraphRAG extracts
entities (departments, time periods, KPI categories) during ingestion and
performs graph traversal at query time.

You don't need full Microsoft GraphRAG. Implement a lite version:

```
1. During ingestion of each KPI record, extract entities:
   {department, category, period, metric_name}
   Store in a sidecar table: kpi_entities(record_id, entity_type, entity_value)

2. At query time:
   a. Extract entities from the query (LLM call to Claude Haiku 4.5)
   b. Find KPI records whose entities overlap with query entities
   c. Use those records (not raw embedding search) for retrieval

3. Combine with hybrid retrieval — use graph results when query mentions
   ≥ 2 entities; fall back to hybrid retrieval otherwise.
```

This is exactly the kind of work that becomes a workshop paper. RAGeval
(Project 5) records the graph-vs-vector quality delta. You publish the
finding as part of the 2027 preprint.

**Move 4 — Add Qdrant as a production vector store (optional, signal move).**

Keep ChromaDB as the dev default. Document a Qdrant config in the README:

```yaml
# .env
VECTOR_STORE=qdrant     # or "chroma" for dev
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=...
```

Even if you never deploy Qdrant in 2026, the documentation alone — "swap
to Qdrant for production via env var" — signals to senior buyers.

**Summary — IntelAI 2026 stack:**

```
LAYER                 OLD                          NEW
─────────────────────────────────────────────────────────────────────
LLM (default)         Groq Llama 3.1 70B           Groq Llama 3.3 70B
LLM (reasoning)       —                            Claude Sonnet 4.6
LLM (judge)           Groq                         Claude Haiku 4.5
LLM (local option)    —                            Ollama Llama 3.3 70B
Multi-provider        Hardcoded clients            LiteLLM router
Embeddings            all-MiniLM-L6-v2 only        + BGE-large-en-v1.5
Retrieval             Cosine similarity only       Hybrid (dense + BM25 + RRF)
Reranking             None                         BGE Reranker v2 m3
Knowledge graph       None                         GraphRAG-lite (entities)
Vector store          ChromaDB                     ChromaDB (dev) + Qdrant (prod)
Frontend visualization Custom SVG                  Recharts (Phase 1 already)
Streaming chat        REST polling                 WebSocket (Phase 1 already)
```

---

## PROJECT 2: AgentKit
### MCP Server + Multi-Agent Workflow Orchestration

### 2.1 Market positioning (REFINED from v1)

V1 framed AgentKit primarily as an Upwork play. **v2 reframes:**

- **Primary channel: GitHub + technical blog + cold email** (not Upwork)
- **Secondary channel: Upwork** (when MCP-tagged jobs appear, which is still
  thin as of May 2026)
- **Tertiary channel: LinkedIn 2027** (the demo notebook + blog post are
  prime LinkedIn 2027 content)

Why? MCP demand on Upwork is real but concentrated in a handful of jobs per
week. The bigger market is:

1. **AI agencies and consultancies** who'd hire you on retainer to build
   MCP servers for their clients. These come from cold email + LinkedIn,
   not Upwork postings.
2. **Open-source visibility** — a polished MCP server with stars and PyPI
   downloads is a hiring magnet for top labs. Anthropic, Cursor, Codeium,
   Replit all hire from OSS.
3. **Research credibility** — agentic AI is a hot research area. An open-source
   contribution here looks substantial on a research application.

So: build for the open-source-first audience. Polish accordingly. Treat
Upwork as bonus, not primary.

### 2.2 Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│          AI AGENT CLIENTS (any MCP-compatible client)               │
│                                                                     │
│  Claude Desktop  ·  Cursor IDE  ·  LangGraph Agent  ·  Custom      │
└─────────────────────────────┬───────────────────────────────────────┘
                              │ MCP Protocol (stdio/HTTP)
┌─────────────────────────────▼───────────────────────────────────────┐
│                    AgentKit MCP Server                               │
│                                                                     │
│  query_kpis(domain, period_from, period_to)                         │
│  get_company_health(domain?)                                        │
│  detect_kpi_anomalies(domain, method, threshold)                    │
│  forecast_metric(metric_name, periods, confidence_level)            │
│  list_available_metrics(domain?)                                    │
│  get_executive_summary()                                            │
└─────────────────────────────┬───────────────────────────────────────┘
                              │ Direct Python imports
┌─────────────────────────────▼───────────────────────────────────────┐
│                    IntelAI Backend (data layer)                  │
│  pg_store · insights · forecasting · PostgreSQL + ChromaDB          │
└──────────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────▼────────────────────────────────────────┐
│           3-AGENT LANGGRAPH WORKFLOW                                 │
│                                                                      │
│   PLANNER  ───▶  ANALYST  ───▶  REPORTER                           │
│                                                                      │
│   Input:  "Why is our company health declining?"                    │
│   Output: Structured executive report with numbers,                 │
│           root cause analysis, and prioritized recommendations.     │
└──────────────────────────────────────────────────────────────────────┘
```

### 2.3 Build plan

Repo: `agentkit/`

Extracted (copied from IntelAI):
- `src/services/pg_store.py` → `agentkit/services/pg_store.py`
- `src/services/insights.py` → `agentkit/services/insights.py`
- `src/services/forecasting.py` → `agentkit/services/forecasting.py`
- `src/core/config.py` → `agentkit/core/config.py`
- `src/core/logger.py` → `agentkit/core/logger.py`
- `src/core/pg_engine.py` → `agentkit/core/pg_engine.py`
- `db/schema.sql` → `agentkit/db/schema.sql`

New code:
- `mcp_server.py` — FastMCP server with 6 tools (full code preserved in v1)
- `workflow.py` — LangGraph 3-agent pipeline (full code preserved in v1)
- `agents/planner.py`, `agents/analyst.py`, `agents/reporter.py`
- `demo/demo_notebook.ipynb` — Jupyter demo
- `demo/claude_desktop_config.json` — drop-in config
- `tests/test_mcp_tools.py`

(Full code snippets retained from v1. They are correct, well-structured,
and ready to copy.)

### 2.4 Open-source publication checklist

This is **the primary distribution** for AgentKit. Treat it accordingly.

**Before push to public:**
- README is clear, concise, has architecture diagram
- LICENSE: MIT or Apache 2.0 (pick one, stick with it)
- `.env.example` with placeholders, no secrets
- Tests pass — visible CI badge in README
- A 90-second Loom demo embedded at top of README
- One-paragraph "what this is" elevator pitch
- Quick-start that works on a fresh machine in 5 minutes

**After push:**
- Submit to relevant Awesome lists (`awesome-mcp`, `awesome-llm-agents`)
- Post in MCP-related Discord servers, ML Twitter, r/LocalLLaMA
- Cross-post the demo video to YouTube (organic search traffic)

**Stretch goal (do this by end of 2026):**
- Publish a `pip install agentkit-mcp` package to PyPI
- Even 50 downloads/week is a credible signal

### 2.5 Demo recording (90 seconds)

```
0:00 - 0:10  Open Claude Desktop. Type: "What tools do you have available?"
0:10 - 0:20  Claude lists: query_kpis, get_company_health, etc.
0:20 - 0:35  Type: "What's our company health score and top 3 risks?"
             Watch Claude call get_company_health() — show real score.
             Claude calls detect_kpi_anomalies() — show real anomalies.
0:35 - 0:60  Type: "Generate a full executive report on why our
             company health might be declining."
             Watch Claude call multiple tools sequentially.
             Claude synthesizes into structured report.
0:60 - 1:30  Switch to terminal. Run: `python workflow.py`
             Show 3-agent LangGraph execution logs.
             Final structured report output.
```

### 2.6 Upwork angle (secondary)

When MCP jobs appear, your proposal:

> I've built a production MCP server exposing business intelligence tools
> that works with Claude Desktop, Cursor, and any LangChain agent.
> The demo video shows real data flowing through Claude Desktop calling
> a live PostgreSQL: [Loom link].
>
> A few things to scope your project:
> 1. Which AI client(s) need to consume the MCP tools? (Claude, Cursor, custom?)
> 2. What data sources should the tools access? (DB, API, files?)
> 3. Do you need the full LangGraph 3-agent workflow, or just the MCP server?
>
> Server with your tools: 3–4 days. Workflow on top: additional 3–4 days.

### 2.7 Research-track artifact

> **"MCP Tool Design Patterns for Business Intelligence Agents"**
>
> A taxonomy of MCP tools by access pattern (read-only vs mutating),
> by domain (analytical vs operational), and by latency profile.
> Demonstrated on an MCP server exposing 6 business intelligence
> tools backed by PostgreSQL and a vector store. Recommendations for
> tool granularity, error handling, and audit logging.

Suitable for a workshop submission. Decent shot at acceptance at an
agents-themed workshop (NeurIPS, ICLR, etc.) given how new the field
is. The bar is "novel pattern + working code + a small eval," all of
which you'll have.

### 2.10 2026 Stack Upgrade For AgentKit

AgentKit's v1 stack was `fastmcp + LangGraph + langchain-groq`. For 2026 it
becomes a **multi-framework, multi-provider agent showcase**. The position:
"you can plug AgentKit into Claude Desktop, Cursor, any LangGraph project,
any CrewAI project, or build your own client — same six tools."

**Move 1 — Multi-LLM via LiteLLM (same pattern as IntelAI).**

The planner agent uses Claude Sonnet 4.6 (best for breaking down hard
business questions). The analyst agent uses Groq Llama 3.3 70B (high
volume of tool calls — speed matters). The reporter agent uses Claude
Sonnet 4.6 (synthesis needs nuance).

```python
# workflow.py — agent definitions
from litellm import acompletion

PLANNER_MODEL  = "anthropic/claude-sonnet-4-6"
ANALYST_MODEL  = "groq/llama-3.3-70b-versatile"
REPORTER_MODEL = "anthropic/claude-sonnet-4-6"
LOCAL_FALLBACK = "ollama/llama3.3"

async def planner_agent(state):
    response = await acompletion(
        model=PLANNER_MODEL,
        messages=[{"role":"system","content":PLANNER_SYS_PROMPT},
                  {"role":"user","content":state["question"]}],
        response_format={"type":"json_object"},
    )
    state["plan"] = json.loads(response.choices[0].message.content)
    return state
```

**Move 2 — Add a Claude Agent SDK demo alongside LangGraph.**

The Claude Agent SDK is the native way to build Claude-powered agents. Ship
a parallel example in `demos/claude_agent_sdk_demo.py` that uses the same
six MCP tools but orchestrates them via Claude Agent SDK. This positions
AgentKit as "framework-agnostic" — a major credibility lift.

```python
# demos/claude_agent_sdk_demo.py (NEW)
from claude_agent_sdk import Agent, MCPServer

agent = Agent(
    model="claude-sonnet-4-6",
    mcp_servers=[MCPServer(command="python", args=["mcp_server.py"])],
    system="You are a business analyst. Use the tools to answer questions.",
)
result = agent.run("What drove gross margin last quarter?")
print(result.messages[-1].content)
```

**Move 3 — Add a CrewAI demo for the multi-agent-collaboration audience.**

Some clients think in CrewAI's "role" abstractions (Researcher / Analyst /
Writer crew). Ship `demos/crewai_demo.py` that wraps the same MCP tools as
CrewAI `@tool` decorators and defines a 3-agent crew. ~80 lines of code,
high marketing surface.

**Move 4 — Add a DSPy experiment (research credential).**

DSPy is the "programming over prompting" paradigm gaining serious research
traction. Ship a `research/dspy_experiment.py` that frames the planner→
analyst→reporter pipeline as a DSPy module, optimized via DSPy's compiler
on a held-out training set of business questions. The result becomes a
mid-2026 blog draft + a section in the AgentKit preprint.

```python
# research/dspy_experiment.py (NEW)
import dspy

class BusinessAnalysis(dspy.Module):
    def __init__(self):
        self.plan     = dspy.Predict("question -> plan: list[str]")
        self.analyze  = dspy.ReAct("plan, tools -> raw_data")
        self.report   = dspy.ChainOfThought("question, raw_data -> report")

    def forward(self, question):
        plan = self.plan(question=question).plan
        data = self.analyze(plan=plan, tools=MCP_TOOLS).raw_data
        return self.report(question=question, raw_data=data).report

# Compile with DSPy's BootstrapFewShot using your eval set
```

**Move 5 — First-class MCP resources + prompts (not just tools).**

The MCP 2026 best practice extends beyond tools to also expose **resources**
(read-only data anchors) and **prompts** (reusable prompt templates). Add:

- `@mcp.resource("kpi://Finance/latest")` — exposes the latest Finance
  snapshot as a stable URI Claude can pin in its context.
- `@mcp.prompt("monthly_executive_briefing")` — exposes a reusable prompt
  template that clients can invoke without writing prompt text themselves.

This 2026 best practice is rare in third-party MCP servers — you'd be early.

**Summary — AgentKit 2026 stack:**

```
LAYER                 OLD                          NEW
─────────────────────────────────────────────────────────────────────
LLM (planner)         Groq                         Claude Sonnet 4.6
LLM (analyst)         Groq                         Groq Llama 3.3 70B
LLM (reporter)        Groq                         Claude Sonnet 4.6
LLM (local fallback)  —                            Ollama Llama 3.3 70B
Multi-provider        Single client                LiteLLM
Agent frameworks      LangGraph only               LangGraph + Claude Agent SDK
                                                    + CrewAI + DSPy (research)
MCP feature surface   Tools only                   Tools + Resources + Prompts
Research artifact     None                         DSPy-compiled pipeline
                                                    benchmarked
```

---

## PROJECT 3: DocIntel
### Intelligent Document Processing Pipeline

### 3.1 Why this wins consistently

Document processing is the most **volume-consistent** AI niche on Upwork.
Every industry has the same problem: piles of PDFs that need to become
structured data. The 2026 upgrade: clients no longer want just OCR — they
want structured JSON with confidence scores, ready to push into their DB
or ERP.

Your `src/services/ocr_enhancement.py` (428 lines) plus `src/services/ocr/main.py`
(~80 lines) plus `src/integrations/camera.py` (189 lines) already contain the
core of a standalone product.

### 3.2 Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                  DocIntel — Document AI API                  │
│                                                              │
│  POST /process           Full pipeline (upload → JSON)      │
│  POST /extract-tables    PDF table extraction only           │
│  POST /classify          Document type detection             │
│  POST /extract-fields    Form field extraction               │
│  POST /extract-llm       LLM-enhanced structured extraction  │
│  POST /batch/upload      Upload 1-100 files → job_id         │
│  GET  /batch/{job_id}    Poll async batch status             │
└──────────────────────────────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                Document Processing Engine                        │
│                                                                  │
│  1. File intake — Detect PDF native / scanned / image           │
│  2. Pre-processing — Deskew, denoise, threshold (OpenCV)        │
│  3. Extraction — pdfplumber for native, Tesseract for scans     │
│  4. Tables — PDFTableExtractor                                  │
│  5. Forms — FormFieldDetector                                   │
│  6. Classification — invoice/contract/report/form/medical       │
│  7. LLM-enhanced fields — Groq with type-specific prompts       │
│  8. Output — JSON with confidence + CSV + webhook              │
└──────────────────────────────────────────────────────────────────┘
```

### 3.3 Build plan

Repo: `docintel/`

Extracted from IntelAI:
- `src/services/ocr_enhancement.py` → `docintel/services/ocr_enhancement.py`
- `src/services/ocr/main.py` → `docintel/services/tesseract_service.py`
- `src/services/ocr/Dockerfile.ocr` → `docintel/Dockerfile`
- `src/integrations/camera.py` → `docintel/services/camera.py`
- `src/core/logger.py` → `docintel/core/logger.py`

New code:
- `api.py` — FastAPI wrapper with the endpoints above
- `services/llm_extractor.py` — LLM-enhanced field extraction
- `services/batch_processor.py` — async batch processing
- `demo/index.html` — drag-and-drop demo UI
- `tests/test_docIntel.py`
- `sample_docs/` — invoice, contract, form samples

(Code snippets preserved from v1.)

### 3.4 The LLM extraction layer (EXPANDED from v1)

V1 budgeted 1–2 days for `llm_extractor.py`. **v2 budgets 1–2 weeks.**

Why: pure OCR gives you raw text. Reliable structured extraction across
diverse document layouts takes prompt iteration on real data. You will
discover:

- Some vendors put totals in a sidebar, not in line items
- Some invoices use commas as decimals (EU)
- Some scanned receipts have OCR garbage that confuses LLM parsing
- Some contracts have multi-page clauses that don't fit your prompt budget
- LLM responses sometimes include markdown fences, hallucinated fields, or
  silently wrong values

Mitigation plan:

1. **Build an eval dataset**: 50 real invoices from different vendors.
   For each, manually create the expected JSON. Save to
   `docintel/tests/invoice_eval.jsonl`. Run weekly.
2. **Iterate prompts** until accuracy on key fields (total, vendor, date,
   invoice number) reaches 90%+ on the eval set.
3. **Log every extraction** with confidence and inputs. Review failures.
4. **Add fallbacks**: if LLM returns malformed JSON, retry once with a
   stricter prompt. If still fails, return raw text with a flag.

**Realistic timeline:** 2 weeks of focused work to get to 90% accuracy
on invoices. Contracts and medical records take longer per document
type. Don't claim what you haven't measured.

### 3.5 Demo UI

A single HTML page with a drag-and-drop zone. Dark theme. Vanilla JS,
~150 lines. No framework. Shows:

- Drop zone with file picker
- Loading spinner during processing
- Result card: classification badge, confidence %, processing time,
  tables count
- Structured JSON output, syntax-highlighted

(Full HTML preserved from v1.)

### 3.6 Demo recording (60 seconds)

```
0:00 - 0:05  Open demo UI.
0:05 - 0:15  Drag a real invoice PDF onto drop zone.
0:15 - 0:30  "Processing..." → Results appear:
             doc_type: "invoice", confidence: 0.94
0:30 - 0:50  Show structured_data: vendor, total, line_items, due_date
             all extracted with sensible values.
0:50 - 0:60  Drag in a contract — different doc_type detected, different
             field set extracted.
```

### 3.7 Upwork niches for DocIntel

```
NICHE 1: OCR Developer
  Search: OCR developer, PDF extraction, document data extraction
  Angle:  "Pipeline from scan to structured JSON. 90%+ field accuracy
           on invoices. Supports native + scanned PDFs."

NICHE 2: Document AI Engineer
  Search: document AI, invoice extraction, contract extraction
  Angle:  "LLM-enhanced extraction beyond OCR. Type-specific prompts
           for invoice, contract, receipt, medical."

NICHE 3: Computer Vision Engineer (lower-priority)
  Search: computer vision, document preprocessing
  Angle:  "Document preprocessing pipeline: deskew, denoise, threshold."

NICHE 4: Data Entry Automation
  Search: data entry automation, AI data extraction
  Angle:  "Replace manual data entry. Batch process 100 documents async."
```

### 3.8 Vertical positioning options

| Vertical | Why it works |
|----------|--------------|
| **Invoice AP automation** | High volume, $5K–$20K projects |
| **Legal contract review** | Premium pricing, large enterprise budgets |
| **Medical records extraction** | Compliance-driven, recurring revenue |
| **Receipts for expense reporting** | High volume, low complexity per unit |

Lead with invoice AP automation — highest volume, fastest demo iteration,
most concrete output for a proposal.

### 3.9 Research-track artifact

> **"LLM-Enhanced OCR: Bridging Raw Text Extraction and Structured Output"**
>
> An evaluation framework for document AI systems combining OCR with
> LLM-based structured extraction. Compares pure-OCR, layout-aware OCR
> (LayoutLM), and LLM-enhanced pipelines on a 200-document benchmark
> across invoices, contracts, and forms. Releases the benchmark.

Strong workshop-paper candidate. Releasing the benchmark is the
biggest contribution — datasets are highly cited.

### 3.10 2026 Stack Upgrade For DocIntel — The Vision-First Pivot

This is the **most important stack upgrade across all six projects**. The
v1 pipeline (`pdfplumber → pytesseract → Groq text extraction`) is now a
fallback path, not the primary path. In 2026, the leading approach is
**vision-LLM-first** extraction: skip OCR entirely and pass page images
directly to a vision LLM that returns structured JSON.

Why this matters specifically for your career: the Equipment Sourcing job
post (analyzed in Section 26.5) explicitly asks for "a locally-hosted
vision model to look at every photo of every auction listing." If your
DocIntel repo demonstrates exactly this pattern with Ollama + Llama 3.2
Vision, your proposal moves from "I can probably do this" to "here's
the open-source repo where I already did it."

**Move 1 — Three-route extraction pipeline.**

```
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
    │        Cost: $0 + electricity. Latency: 3-10s on GPU, 30s+ on CPU.
    │
    └──→ ROUTE C: OCR_FALLBACK (Tesseract + LLM cleanup)
             Use when vision LLM cost is prohibitive or image quality
             is too low for vision LLM (very low-res scans, faxes).
             Cost: ~$0.001 per page. Latency: 1-3s.
```

The README leads with Route A and Route B side by side. The endpoint
accepts a `route` parameter so clients choose:

```python
# api.py
@app.post("/extract")
async def extract(file: UploadFile, route: str = "vision_premium"):
    if route == "vision_premium":
        return await extract_via_vision_llm(file, model="anthropic/claude-sonnet-4-6")
    elif route == "vision_local":
        return await extract_via_vision_llm(file, model="ollama/llama3.2-vision")
    elif route == "ocr_fallback":
        return await extract_via_ocr_then_llm(file)
```

**Move 2 — Implement the vision LLM extractor.**

```python
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
        model=model,
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
```

LiteLLM handles the provider-specific image-message format differences —
this same function works for Claude Vision, GPT-4o Vision, Gemini 2.5
Vision, and Ollama vision models.

**Move 3 — Add Marker for high-quality PDF-to-Markdown.**

For documents where you want structured text intermediate (e.g., to ingest
into RAG), Marker (open-source by VikParuchuri) is the 2026 SOTA. Ship as
an alternative route:

```python
# services/marker_extractor.py
from marker.converters.pdf import PdfConverter
converter = PdfConverter(artifact_dict=create_model_dict())
rendered = converter("doc.pdf")
markdown_text = text_from_rendered(rendered)
```

**Move 4 — Add Surya OCR + DocTR for layout-aware OCR (fallback path).**

Tesseract is fine but old. Surya OCR (also VikParuchuri) and DocTR (Mindee)
are stronger fallbacks. Surya is particularly good for non-Latin scripts.

```python
# services/ocr_extractor.py
from surya.ocr import run_ocr
from surya.model.detection.model import load_model, load_processor

DET_MODEL = load_model()
DET_PROC  = load_processor()

def surya_extract(image):
    predictions = run_ocr([image], ["en"], DET_MODEL, DET_PROC)
    return predictions
```

**Move 5 — Vision-first object detection for the Equipment Sourcing pattern.**

For the auction-listing use case (Section 26.5), you need to classify
*what's in the photo*, not just OCR text. Add a `/classify-image` endpoint:

```python
# api.py
@app.post("/classify-image")
async def classify_image(file: UploadFile,
                          categories: list[str] = Query(...),
                          route: str = "vision_local"):
    """Given an image and a list of possible categories, return which
    category the image most likely belongs to plus confidence.
    Critical for: auction listings, marketplace scrapers, inventory."""
    image = await file.read()
    prompt = f"""Look at this image. Which category does the main
    object belong to? Categories: {", ".join(categories)}.
    Return JSON: {{"category": str, "confidence": float, "reasoning": str}}"""
    return await classify_via_vision_llm(image, prompt, route=route)
```

This endpoint is what makes DocIntel directly applicable to the Equipment
Sourcing job. Your proposal can say: "DocIntel's `/classify-image`
endpoint is the exact pattern you described in the job post — local
Ollama + vision LLM + structured classification output."

**Move 6 — Add an eval harness for vision-vs-OCR comparison (Phase 5
research artifact).**

```python
# eval/vision_vs_ocr_benchmark.py (NEW)
# Runs 200-document benchmark across:
#   Route A: Claude Sonnet 4.6 Vision
#   Route B: Llama 3.2 Vision (local via Ollama)
#   Route C: Tesseract → Claude Haiku 4.5 cleanup
# Measures: field-level accuracy, latency, cost
# Outputs: comparison table for blog post + preprint
```

The result becomes Blog Post 2 (drafted in 2026, published in 2027) and
the seed of an arXiv preprint on cost/quality tradeoffs in document AI.

**Summary — DocIntel 2026 stack:**

```
LAYER                 OLD                          NEW
─────────────────────────────────────────────────────────────────────
Primary route         Tesseract → Groq text        Vision LLM → JSON
                                                    (Claude Sonnet 4.6 OR
                                                     Ollama Llama 3.2 Vision)
Secondary route       —                            Marker (PDF → Markdown)
Fallback route        pdfplumber + Tesseract       Surya OCR + DocTR + LLM
LLM (premium)         Groq                         Claude Sonnet 4.6 Vision
LLM (local)           —                            Ollama Llama 3.2 Vision 11B
                                                    OR Qwen 2.5-VL 7B
Multi-provider        Hardcoded                    LiteLLM (vision included)
New endpoint          —                            /classify-image (vision-first
                                                    object/category classification)
Eval harness          Per-field accuracy            + vision-vs-OCR benchmark
                                                    (200-doc dataset, released)
n8n integration       —                            Webhook endpoint + n8n node
                                                    template documented
Demo (Loom)           PDF drag-drop                + image classification demo
                                                    (auction-listing pattern)
```

---

## PROJECT 4: VoiceFlow
### Speech-to-Intelligence Pipeline

### 4.1 Differentiation (preserved from v1)

Transcription is a commodity (Whisper is free). What clients pay for is
the **intelligence layer on top** — meeting notes with action items,
sales calls with CRM-ready output, voice-to-task automation.

Your `src/services/voice/main.py` (130 lines) already implements
faster-whisper transcription, Groq cloud fallback, edge-tts TTS, and
language detection. The gap is what happens after the words exist.

### 4.2 Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                    VoiceFlow API                               │
│                                                                │
│  POST /transcribe          Audio → text                        │
│  POST /analyze             Text → structured insights          │
│  POST /pipeline            Audio → insights (full pipeline)    │
│  POST /meeting/process     Meeting audio → meeting notes       │
│  POST /call/analyze        Sales call → CRM-ready data         │
│  POST /tts                 Text → speech                       │
│  WS   /stream              Real-time streaming transcription   │
└────────────────────────────────────────────────────────────────┘
                            │
   ┌────────────────────────┼────────────────────────┐
   ▼                                                  ▼
┌────────────────┐                          ┌──────────────────┐
│ Whisper Layer  │                          │ Intelligence Layer│
│                │                          │                  │
│ faster-whisper │                          │ Meeting Analyzer │
│ Groq fallback  │                          │ Sales Analyzer   │
│ 99 languages   │                          │ General Analysis │
└────────────────┘                          └──────────────────┘
```

### 4.3 Speaker diarization (REVISED from v1)

V1 promised pyannote diarization in 1–2 days. **v2 acknowledges this
is risky.** pyannote.audio requires:

- HuggingFace authentication
- A model download (~1 GB)
- pytorch + torchaudio with compatible CUDA or CPU build
- Often fights with macOS/Linux audio driver quirks

If you can't install it cleanly in 2 hours, **fall back to no diarization**.
Whisper alone provides "this is what was said." Diarization adds "who said
what" — useful but not critical. Most meeting-notes use cases don't need it.

If you do want diarization:

1. Try `pyannote.audio` first (best quality if it installs)
2. Fall back to `simple-diarizer` (lighter, less accurate)
3. Final fallback: skip diarization entirely. Note this in your README
   as "not yet implemented — single-speaker assumed."

Honesty wins clients. Don't promise diarization if you can't reliably ship it.

### 4.4 Build plan

Repo: `voiceflow/`

Extracted from IntelAI:
- `src/services/voice/main.py` → `voiceflow/services/voice_service.py`
- `src/integrations/tts.py` → `voiceflow/services/tts_service.py`
- `src/core/logger.py` → `voiceflow/core/logger.py`

New code:
- `services/meeting_analyzer.py` — MeetingAnalyzer class with three methods:
  `analyze_meeting`, `analyze_sales_call`, `general_analysis`. Each calls
  Groq with type-specific prompts and returns structured JSON.
- `api.py` — FastAPI app with the endpoints listed in 4.2
- `demo/record.html` — browser MediaRecorder demo
- `tests/test_voiceflow.py`

(Full code preserved from v1.)

### 4.5 Demo recording (90 seconds)

```
0:00 - 0:05  Open browser demo.
0:05 - 0:20  Click record. Say: "Team meeting March 15th. Sarah committed
             to finishing the API integration by end of week. John to
             review the $50,000 proposal from Acme Corp by Friday."
0:20 - 0:35  Click stop — transcription appears live.
0:35 - 0:50  Click Analyze (meeting mode).
0:50 - 1:10  JSON appears: action_items shows Sarah with deadline,
             key_numbers shows $50,000, decisions shows the assignment.
1:10 - 1:30  Switch to sales-call mode. Same recording, different output:
             prospect, deal stage, recommended next step.
```

### 4.6 Upwork niches

```
NICHE 1: Speech-to-Text Developer
  Search: Whisper developer, STT developer, transcription tool
  Angle:  "faster-whisper pipeline with multilingual support and
           downstream intelligence layer."

NICHE 2: Meeting Notes Automation
  Search: meeting notes AI, meeting transcription tool
  Angle:  "Audio → structured meeting notes with action items in <60s.
           Each action item has owner, deadline, priority."

NICHE 3: Sales Intelligence Tool
  Search: sales call analyzer, CRM data automation
  Angle:  "Sales call → CRM-ready structured data automatically.
           Identifies pain points, objections, buying signals."

NICHE 4: Voice AI Developer (lower-priority)
  Search: voice AI, conversational AI, voice assistant
  Angle:  "Real-time transcription with WebSocket streaming."
```

### 4.7 Research-track artifact

> **"Speech-to-Intelligence: Evaluating LLM Post-Processing of Whisper
> Transcripts for Action Item Extraction"**
>
> An eval framework comparing pure Whisper, Whisper + GPT-4o-mini post-
> processing, and Whisper + LLaMA 3.1 post-processing on a 50-meeting
> benchmark. Released benchmark. Recommendations for cost/accuracy
> tradeoffs.

Workshop-quality. Releasing the benchmark is the contribution.

### 4.10 2026 Stack Upgrade For VoiceFlow

The v1 stack (`faster-whisper + Groq + edge-tts`) becomes a **multi-provider
speech intelligence platform** with both self-hosted and premium API paths.

**Move 1 — Upgrade transcription to WhisperX or NeMo Canary.**

WhisperX wraps faster-whisper with forced alignment (word-level timestamps)
and pyannote diarization (who-spoke-when) in a single library. This is the
2026 self-hosted SOTA for production-grade transcription.

```python
# services/whisperx_service.py (NEW)
import whisperx

# Load once at startup (large model, ~3GB)
model = whisperx.load_model("large-v3", device="cuda", compute_type="float16")
align_model, metadata = whisperx.load_align_model(language_code="en", device="cuda")
diarize_model = whisperx.DiarizationPipeline(use_auth_token=HF_TOKEN, device="cuda")

async def transcribe_with_diarization(audio_bytes):
    audio = whisperx.load_audio(audio_bytes)
    result = model.transcribe(audio, batch_size=16)
    result = whisperx.align(result["segments"], align_model, metadata,
                             audio, device="cuda", return_char_alignments=False)
    diarize_segments = diarize_model(audio)
    result = whisperx.assign_word_speakers(diarize_segments, result)
    return {
        "transcript": result["segments"],
        "speakers": list(set(s.get("speaker") for s in result["segments"])),
    }
```

For research credibility, also document NVIDIA NeMo Canary — the 2026 SOTA
benchmark transcription model — as an "advanced" option.

**Move 2 — Add premium API providers for clients who need them.**

Some clients won't tolerate self-hosted Whisper because of latency,
diarization quality, or compliance. Add provider abstractions:

```python
# services/transcription_router.py (NEW)
from enum import Enum

class TranscriptionProvider(Enum):
    LOCAL_WHISPERX = "local_whisperx"
    GROQ_WHISPER   = "groq_whisper"     # ~10x faster than self-host
    DEEPGRAM       = "deepgram"          # Nova-3, best diarization
    ASSEMBLYAI     = "assemblyai"        # Universal-2, strong streaming

async def transcribe(audio_bytes, provider: TranscriptionProvider,
                     language="auto", diarize=True):
    if provider == TranscriptionProvider.LOCAL_WHISPERX:
        return await whisperx_service.transcribe(audio_bytes, diarize=diarize)
    elif provider == TranscriptionProvider.GROQ_WHISPER:
        return await groq_transcribe(audio_bytes, language)
    elif provider == TranscriptionProvider.DEEPGRAM:
        return await deepgram_transcribe(audio_bytes, language, diarize)
    elif provider == TranscriptionProvider.ASSEMBLYAI:
        return await assemblyai_transcribe(audio_bytes, language, diarize)
```

**Move 3 — Multi-LLM for analysis layer.**

Sales-call analysis benefits most from Claude Sonnet 4.6 — reading between
the lines (objections, buying signals, sentiment nuance) is exactly where
Claude excels. Meeting-notes extraction can use Groq Llama 3.3 70B for
speed. Configure per-analysis-type:

```python
# services/meeting_analyzer.py
ANALYSIS_MODELS = {
    "meeting":     "groq/llama-3.3-70b-versatile",     # speed, structured
    "sales_call":  "anthropic/claude-sonnet-4-6",       # nuance critical
    "support_call": "anthropic/claude-haiku-4-5",       # cheap, high-volume
    "interview":   "anthropic/claude-sonnet-4-6",       # quality matters
    "general":     "groq/llama-3.3-70b-versatile",
}
```

**Move 4 — Real-time voice agent demo (OpenAI Realtime API or Hume EVI 2).**

The breakout speech feature of 2026 is bidirectional real-time voice agents
— the model listens and speaks in the same stream, sub-second latency. Add
a demo:

```python
# demos/realtime_voice_agent.py (NEW)
# Browser opens a WebRTC connection to /realtime/ws
# Server bridges to OpenAI Realtime API (gpt-4o-realtime-preview)
# Voice in → model processes → voice out, all <500ms
# Demo: "Talk to your business analyst" — the agent answers KPI questions
# in real time using AgentKit's MCP tools
```

This demo is the most memorable element of VoiceFlow — and connects to
AgentKit (cross-project synergy in your portfolio narrative).

**Move 5 — TTS upgrades.**

Add three TTS providers:

```
edge-tts        Free, fast, decent voices       Default
Kokoro TTS      Open-source, expressive          Self-host premium
ElevenLabs      Best voice quality + cloning     Paid premium
OpenAI tts-1-hd Reliable HD voice                Paid alternative
```

A single `/tts` endpoint with `provider=...` parameter.

**Move 6 — Speaker diarization fallback chain.**

`pyannote.audio` 3.x is now production-stable but still finicky to install.
Document the fallback:

```
Primary:  pyannote.audio 3.x (best quality, GPU needed)
Fallback: NeMo's built-in diarization (CPU-OK)
Last resort: speaker_diarization=false (just transcript, document this)
```

Each repo's README should be honest about which fallback was used in the
demo recording.

**Summary — VoiceFlow 2026 stack:**

```
LAYER                 OLD                          NEW
─────────────────────────────────────────────────────────────────────
Transcription (local) faster-whisper              WhisperX (faster-whisper +
                                                    alignment + diarization)
                                                    + NeMo Canary (advanced)
Transcription (API)   —                            Groq Whisper + Deepgram +
                                                    AssemblyAI (provider router)
Diarization           —                            pyannote 3.x + NeMo fallback
LLM (analysis)        Groq                         Claude Sonnet 4.6 (sales,
                                                    interview) + Groq Llama 3.3
                                                    + Claude Haiku 4.5 (support)
TTS                   edge-tts                     edge-tts + Kokoro TTS +
                                                    ElevenLabs + OpenAI tts-1-hd
Real-time voice agent —                            OpenAI Realtime API demo
                                                    bridged to AgentKit MCP tools
Multi-provider        Hardcoded                    LiteLLM + provider router
Research artifact     None                         50-meeting eval set,
                                                    pure-Whisper vs LLM-augmented
                                                    benchmark (released)
```

---

## PROJECT 5: RAGeval
### LLMOps Observability — Self-Hosted Drop-In

### 5.1 Competitive landscape (NEW in v2)

V1 framed RAGeval as "almost no one offers this." That's misleading.
The space is:

| Tool | Type | Pricing | Self-hosted? |
|------|------|---------|--------------|
| **Arize Phoenix** | OSS + commercial | Free OSS, $$ commercial | Yes (OSS) |
| **LangSmith** | Commercial (Langchain) | Free tier, $$ at scale | No |
| **TruLens** | OSS | Free | Yes |
| **Helicone** | Commercial | Free tier, $$ | Self-host possible |
| **Langfuse** | OSS + commercial | Free OSS, $$ commercial | Yes (OSS) |

So **rare-skill positioning doesn't work**. Phoenix and Langfuse are both
strong, self-hostable, and free.

**RAGeval's differentiator must be:**

- **Drop-in for FastAPI + LangChain** — most existing tools require either
  callback wiring or a full new framework. A `@track` decorator with zero
  config is genuinely rare.
- **Self-hosted, <$5/month to run** — Phoenix and Langfuse need a Postgres
  + UI service. RAGeval can ship as one Docker container with SQLite as
  default, optional Postgres for production.
- **Domain-aware metrics** — most generic eval tools measure abstract
  groundedness. RAGeval ships with persona-aware metrics: "Did the CFO
  response actually stay within Finance + Growth data?" That's a metric
  that matters in production.

The honest competitive frame for a proposal:

> "Phoenix and Langfuse are great if you can deploy a full UI stack.
> RAGeval is for teams who want drop-in observability in one Docker
> container with SQLite default — same metrics, no infrastructure overhead."

### 5.2 Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                   RAGeval Dashboard (React)                       │
│                                                                   │
│   SYSTEM Health  ·  QUALITY Metrics  ·  COST Tracker             │
│                                                                   │
│   Query Log (last 50, color-coded by score)                      │
└──────────────────────────┬───────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                    RAGeval API                                    │
│                                                                   │
│  POST /eval/log         Log a RAG interaction                    │
│  POST /eval/score       Score a specific query                   │
│  GET  /eval/metrics     Aggregated metrics                       │
│  GET  /eval/queries     Query history with scores                │
│  GET  /eval/cost-report Token usage + cost                       │
│  GET  /eval/alerts      Threshold violations                     │
│  WS   /eval/live        Real-time metric stream                  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                  Evaluation Engine                                │
│                                                                   │
│  1. Retrieval Relevance  cosine_similarity(query, chunks).mean() │
│  2. Groundedness         LLM-as-judge (Groq)                     │
│  3. Faithfulness         Embedding-similarity proxy / NLI        │
│  4. Latency Tracking     P50, P95, P99 per query type            │
│  5. Cost Per Query       tokens_used × price_per_token           │
│  6. Persona Adherence    NEW — did response stay in role scope?  │
└──────────────────────────────────────────────────────────────────┘
```

### 5.3 Build plan

Repo: `rageval/`

Extracted from IntelAI:
- `src/core/monitoring.py` → `rageval/core/monitoring.py`
- `src/core/performance.py` → `rageval/core/performance.py`
- `src/core/logger.py` → `rageval/core/logger.py`
- `src/core/config.py` → `rageval/core/config.py` (simplified)

New code:
- `evaluator.py` — RAGEvaluator class with all 6 scorers
- `store.py` — SQLite default, Postgres optional
- `api.py` — FastAPI app
- `dashboard/` — React app (Recharts)
- `sdk/__init__.py` — drop-in `@track` decorator
- `tests/test_rageval.py`

(Full code preserved from v1, with persona-adherence metric added.)

### 5.4 The drop-in SDK (killer feature)

```python
from rageval import track

@track(project="my_rag_app")
async def my_rag_query(question: str) -> str:
    chunks = retriever.get(question)
    answer = llm.generate(question, chunks)
    return answer
```

That's it. The decorator:

1. Times the function
2. Captures input/output
3. Calls evaluator on the result
4. Stores in SQLite (default) or your configured backend
5. Exposes metrics via `/eval/metrics`

**Publish as `pip install rageval` to PyPI.** This is the project's
biggest credibility play. Even 100 downloads a month is meaningful.
Target: 500 downloads/month by end of 2026.

### 5.5 Integration into IntelAI (self-eating dogfood)

Modify `omnismart_chatbot.py` to call `rageval.track`. Now every chat
interaction in IntelAI is automatically logged and scored. This
is your demo: open the RAGeval dashboard, see real production data
from your own deployed system flowing in.

### 5.6 Demo recording (90 seconds)

```
0:00 - 0:10  Open RAGeval dashboard. Show: avg relevance 0.78, avg
             groundedness 0.84.
0:10 - 0:25  Show line chart — quality over last 7 days. One dip
             visible.
0:25 - 0:40  Show query log. Highlight a red row (low relevance score).
0:40 - 0:55  Click the flagged query. Show the flag:
             LOW_RETRIEVAL_RELEVANCE. The retrieved chunks weren't
             aligned with the query.
0:55 - 1:10  Show cost tracker: $0.023 today, $0.42 this week.
             Projected monthly: $1.80.
1:10 - 1:30  Switch tab. Open IDE. Show a 5-line code snippet:
             `from rageval import track; @track(project="my_rag")`.
             Show this is the entire integration code.
```

### 5.7 Upwork niches

```
NICHE 1: LLMOps Engineer (premium-rate niche)
  Search: LLMOps, LLM observability, RAG evaluation
  Angle:  "Drop-in observability for RAG. SDK published to PyPI.
           Self-hosted, SQLite-default. <$5/mo to run."

NICHE 2: AI Quality Engineer
  Search: AI evaluation, RAG quality, hallucination detection
  Angle:  "Retrieval relevance, groundedness, faithfulness scoring.
           Persona-aware metrics. Auto-flagging."

NICHE 3: MLOps Engineer
  Search: MLOps for LLMs, ML monitoring
  Angle:  "End-to-end monitoring for LLM applications.
           Drop-in SDK, no framework lock-in."
```

### 5.8 Research-track artifact

> **"Persona-Conditioned Groundedness: An Evaluation Framework for
> Role-Scoped RAG Systems"**
>
> Extends standard groundedness metrics (Phoenix, Langfuse) to incorporate
> persona/role constraints. Demonstrates that an answer can be groundedness-
> valid against the retrieved chunks but violate role-scope constraints
> (e.g., a CFO response citing People-domain data). Releases the metric
> implementation as `rageval-persona`.

This is a real research contribution. Connects to alignment-research
interest in scoped/conditioned LLM behavior. Strong candidate for a
workshop submission.

### 5.10 2026 Stack Upgrade For RAGeval

RAGeval's v1 (`sentence-transformers MiniLM + Groq judge + SQLite`) becomes
a 2026 **standards-track observability platform** with multi-judge
consensus, OpenTelemetry export, and built-in benchmarks for retrieval
strategy comparison.

**Move 1 — Multi-judge LLM evaluation with consensus.**

Single-judge LLM evaluation is noisy. The 2026 best practice is multi-judge
consensus across diverse models, with disagreement flagged for human review.

```python
# evaluator.py — multi-judge scoring
JUDGE_MODELS = [
    "anthropic/claude-haiku-4-5",       # fast, cheap, frontier
    "groq/llama-3.3-70b-versatile",      # diverse perspective
    "openai/gpt-5-mini",                 # diverse perspective
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
```

This single change is a defensible novel contribution for the preprint.

**Move 2 — OpenTelemetry / OpenLLMetry export.**

Enterprise buyers (and research grant reviewers) want standards. Add OTEL
export so RAGeval data flows to any OpenTelemetry-compatible backend
(Datadog, Honeycomb, Jaeger, Grafana, etc.):

```python
# rageval/otel_exporter.py (NEW)
from opentelemetry import trace, metrics
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

tracer = trace.get_tracer("rageval")

def export_interaction(interaction):
    with tracer.start_as_current_span("rag.interaction") as span:
        span.set_attribute("rag.query", interaction["query"])
        span.set_attribute("rag.relevance", interaction["scores"]["relevance"])
        span.set_attribute("rag.groundedness", interaction["scores"]["groundedness"])
        span.set_attribute("rag.cost_usd", interaction["cost_usd"])
        span.set_attribute("rag.persona", interaction.get("persona"))
```

Configurable via env var: `RAGEVAL_OTEL_ENDPOINT=http://localhost:4317`.

**Move 3 — Embedding model upgrade + multi-embedding eval.**

The v1 used `all-MiniLM-L6-v2` for relevance scoring. 2026 best practice
records relevance with multiple embedding models (lets you measure which
embedding model your client's RAG should use). Add:

```python
EMBEDDING_MODELS_AVAILABLE = [
    "sentence-transformers/all-MiniLM-L6-v2",     # legacy baseline
    "BAAI/bge-large-en-v1.5",                      # current open SOTA
    "BAAI/bge-m3",                                  # multilingual
    "Snowflake/snowflake-arctic-embed-l",          # 2025-2026 strong open
    "jinaai/jina-embeddings-v3",                   # code-friendly
]
# API endpoint: POST /eval/embedding-comparison
#   Returns per-embedding relevance scores → tells client which to use
```

**Move 4 — Retrieval strategy benchmark endpoint.**

RAGeval becomes an **A/B testing tool for retrieval strategies**: pure
dense, hybrid (dense+BM25+RRF), with reranker, GraphRAG-lite, etc. Add an
endpoint that scores a fixed eval set against any configured retrieval
strategy and returns a comparison table.

```python
# api.py
@app.post("/eval/retrieval-bench")
async def benchmark_retrieval_strategy(strategy: str, eval_set: str = "default"):
    """Run a 200-query benchmark against a configured retrieval strategy.
    Returns: precision@5, recall@10, MRR, latency, cost."""
    return await run_retrieval_benchmark(strategy, eval_set)
```

**Move 5 — DSPy compilation telemetry.**

Researchers using DSPy want to track compilation runs (which prompt
template won, which examples were chosen by BootstrapFewShot, etc.).
RAGeval becomes the natural home for that data:

```python
# rageval/dspy_integration.py (NEW)
@dspy_compile_callback
def log_compilation_run(run):
    rageval.log_dspy_compilation(
        program=run.program_name,
        candidates=run.candidates,
        winner=run.winner,
        eval_metric=run.eval_metric,
        eval_score=run.eval_score,
    )
```

This single integration positions RAGeval in the DSPy community — a small
but research-active audience.

**Move 6 — pgvector option for production scale.**

SQLite is the default. Add Postgres + pgvector as the production tier so
RAGeval can store millions of interactions efficiently:

```python
# rageval/store.py
import os
STORE_BACKEND = os.getenv("RAGEVAL_STORE", "sqlite")
# "sqlite" → ~/.rageval/rageval.db (default, zero-config)
# "postgres" → POSTGRES_URL env var (production, pgvector for embedding
#              storage to make retrieval-relevance queries fast)
```

**Summary — RAGeval 2026 stack:**

```
LAYER                 OLD                          NEW
─────────────────────────────────────────────────────────────────────
LLM judge             Single Groq call             Multi-judge consensus
                                                    (Claude Haiku 4.5 + Groq +
                                                     GPT-5-mini) with flag-for-
                                                     review on disagreement
Embeddings            MiniLM only                  + BGE-large + BGE-M3 +
                                                    Arctic + Jina v3 (compare)
Storage               SQLite only                  SQLite (default) + Postgres
                                                    + pgvector (production)
Observability         Internal only                + OpenTelemetry / OpenLLMetry
                                                    export (any OTEL backend)
Retrieval benchmarks  None                         /eval/retrieval-bench endpoint
                                                    (compares strategies)
DSPy integration      None                         DSPy compilation telemetry
                                                    (logs prompt-program runs)
Research artifact     None                         Persona-Conditioned Ground.
                                                    + Multi-Judge Consensus
                                                    methodology (preprint)
```

---

## PROJECT 6: StreamPulse
### Real-Time Business Data Intelligence Pipeline

### 6.1 Positioning (REVISED from v1)

V1 framed StreamPulse as an Upwork ETL/data-pipeline play. **v2 reframes:**

- **Primary channel: Cold email to operations directors / data engineers**
  at growing SaaS companies (50–200 employees). They have webhook + email
  data scattered across tools and no time to wire it.
- **Secondary channel: Upwork** (n8n/Zapier developer searches, data
  pipeline engineer searches). Real but lower volume than RAG/OCR.
- **Tertiary channel: Open-source positioning** — the DomainClassifier
  with 160+ keywords could ship as a small library.

### 6.2 Architecture

```
External Sources:
  Gmail  ·  G.Sheets  ·  Webhooks (n8n/Zapier)  ·  CSV  ·  API
            └────────────┬───────────┘
                         ▼
                ┌─────────────────┐
                │  StreamPulse API │
                └────────┬────────┘
                         ▼
                ┌─────────────────┐
                │ Domain Classifier│
                │ 160+ keywords    │
                │ Finance/Growth/  │
                │ Ops/People/ESG/  │
                │ IT/Logistics     │
                └────────┬────────┘
                         ▼
       ┌─────────────────┼─────────────────┐
       ▼                 ▼                 ▼
   PostgreSQL        DuckDB         WebSocket Push
   (persist)        (analytics)    (live dashboard)
```

### 6.3 Build plan

Repo: `streampulse/`

Extracted from IntelAI (the full primary modules):
- `src/services/realtime_pipeline.py` (500 lines) → `streampulse/pipeline/classifier.py`
- `src/services/data_ingestion_manager.py` (558 lines) → `streampulse/pipeline/ingestion.py`
- `src/integrations/dispatcher.py` (Gmail + Sheets parts) → `streampulse/connectors/`
- `src/integrations/n8n.py` (445 lines) → `streampulse/connectors/n8n.py`
- `src/core/config.py` → `streampulse/core/config.py` (simplified)
- `src/services/pg_store.py` → `streampulse/store.py` (KPI functions only)

New code:
- `api.py` — FastAPI with ingestion + WebSocket endpoints
- `connectors/webhook_receiver.py` — HMAC signature verification
- `dashboard/` — React LiveDashboard.jsx
- `tests/test_streampulse.py`

### 6.4 Demo recording (60 seconds)

```
0:00 - 0:05  Open live dashboard. "0 records" state.
0:05 - 0:15  Open Postman. Fire a webhook:
             POST localhost:8080/webhook/test
             { "metric": "Revenue", "value": 1250000 }
0:15 - 0:25  Watch: record appears in live feed.
             Domain "Finance" classified. Confidence 0.91.
0:25 - 0:40  Fire 5 more webhooks rapidly with mixed payloads.
             Volume chart spikes. Domain pie chart updates.
0:40 - 0:60  Show records flowing in with confidence scores.
             Click on one — drill-down to source detail.
```

### 6.5 Upwork niches (secondary channel)

```
NICHE 1: Data Pipeline Engineer
  Search: data pipeline, ETL developer, real-time pipeline
  Angle:  "Event-driven ingestion from email/webhooks/APIs.
           Auto-classification. WebSocket live dashboard."

NICHE 2: n8n / Zapier Developer
  Search: n8n developer, Zapier alternative, workflow automation
  Angle:  "Custom webhook processor with classification logic.
           Replaces brittle Zapier chains."

NICHE 3: Real-Time Dashboard
  Search: real-time dashboard, WebSocket dashboard
  Angle:  "Live data visualization with WebSocket. <100ms latency."
```

### 6.6 Research-track artifact

Lowest priority for research output. If you have bandwidth in 2027:

> **"Online Domain Classification for Heterogeneous Business Data Streams"**
>
> An evaluation of keyword-based, embedding-based, and LLM-based
> domain classification for real-time business data. Tradeoff analysis:
> latency vs accuracy. Suggestion for hybrid pipelines.

Lower-priority than RAGeval or AgentKit research outputs.

### 6.10 2026 Stack Upgrade For StreamPulse

StreamPulse v1 was a custom domain classifier + FastAPI + Postgres. For
2026 it becomes a **standards-track real-time data platform** with
first-class n8n + Prefect integration and an upgraded classifier.

**Move 1 — First-class n8n integration (mandatory).**

The Equipment Sourcing job post explicitly says "Comfortable with n8n or
similar workflow tools." Your repo demonstrates exactly that. Add:

```
streampulse/integrations/n8n/
  README.md            # how to plug StreamPulse into n8n
  n8n_node.json        # custom n8n node definition (community node format)
  workflows/
    auction_aggregator.json   # importable n8n workflow demo
    invoice_intake.json
    crm_sync.json
```

The custom n8n node template lets clients install StreamPulse as a
drag-and-drop n8n component. Even if your client builds their own
workflows, having the node ready is a major credibility lift.

**Move 2 — Prefect 3 orchestration layer (optional but research-strong).**

For clients who outgrow n8n, add a Prefect 3 flow that demonstrates the
same pipeline orchestrated with retries, observability, and scheduling:

```python
# streampulse/orchestration/prefect_flow.py (NEW)
from prefect import flow, task

@task(retries=3, retry_delay_seconds=30)
async def ingest_source(source: str): ...

@task
async def classify_record(record: dict) -> dict: ...

@task
async def store_kpi(record: dict) -> None: ...

@flow(name="streampulse-realtime-pipeline")
async def pipeline_flow(sources: list[str]):
    for source in sources:
        records = await ingest_source(source)
        classified = [await classify_record(r) for r in records]
        await asyncio.gather(*[store_kpi(c) for c in classified])
```

**Move 3 — Domain classifier upgrade.**

V1 used 160 keywords across 6 domains. The 2026 upgrade is a hybrid:

```
1. Fast path: keyword matching (existing, <1ms latency)
2. Confidence threshold: if keyword match confidence < 0.7
3. Fallback path: embedding similarity vs domain prototypes (BGE-large)
   OR Claude Haiku 4.5 zero-shot classification
4. Cache classification results by content hash (avoid re-classify)
```

The fallback is invoked only when keyword classification is uncertain.
This keeps the median latency low while improving tail-case accuracy.

```python
# streampulse/classifier.py
async def classify(content: str, fast_only: bool = False) -> dict:
    keyword_result = keyword_classify(content)
    if keyword_result.confidence >= 0.7 or fast_only:
        return keyword_result
    # Slow path
    embedding_result = await embedding_classify(content)
    if embedding_result.confidence >= 0.75:
        return embedding_result
    return await llm_classify(content, model="anthropic/claude-haiku-4-5")
```

**Move 4 — dlt (data load tool) for declarative source ingestion.**

dlt is the modern declarative way to define data sources (the "Stripe of
pipelines"). Add it as an alternative ingestion mechanism:

```python
# streampulse/ingestion/dlt_sources.py (NEW)
import dlt

@dlt.source
def gmail_source(): ...

@dlt.source
def gsheet_source(): ...

@dlt.source
def webhook_source(): ...

# Pipelines are declarative: pipeline = dlt.pipeline("streampulse")
#                            pipeline.run(gmail_source())
```

dlt handles incremental loading, schema evolution, and idempotency — all
things you'd otherwise build manually.

**Move 5 — Vision-classification webhook (synergy with DocIntel).**

For the Equipment Sourcing use case: many incoming "records" are auction
listings with photos. Add a webhook endpoint that classifies photo+text
together:

```python
@app.post("/webhook/{source}/with-vision")
async def webhook_with_vision(source: str, payload: dict):
    # payload contains text + image_url
    # 1. Classify domain from text (StreamPulse classifier)
    # 2. Classify image category (DocIntel /classify-image)
    # 3. Combine → enriched record
    # 4. Broadcast to live dashboard
```

This single endpoint demonstrates **DocIntel + StreamPulse working together**
— exactly the cross-project composition the Equipment Sourcing job needs.

**Move 6 — Server-Sent Events as a simpler real-time option.**

WebSocket is great for bidirectional, but most "live dashboard" use cases
are one-way (server → browser). Add SSE as an alternative:

```python
@app.get("/live/sse")
async def live_sse_endpoint():
    async def event_stream():
        async for record in pipeline.subscribe():
            yield f"data: {json.dumps(record)}\n\n"
    return StreamingResponse(event_stream(), media_type="text/event-stream")
```

SSE works through more firewalls and is simpler for frontend developers.

**Summary — StreamPulse 2026 stack:**

```
LAYER                 OLD                          NEW
─────────────────────────────────────────────────────────────────────
Classifier            Keyword-only (160 kw)         Hybrid: keyword fast path
                                                    + BGE-large embedding +
                                                    Claude Haiku 4.5 fallback
Ingestion             Custom Python                + dlt declarative sources
Orchestration         None                         + Prefect 3 flow (research)
n8n integration       Webhook only                 + custom n8n node template
                                                    + 3 ready-to-import flows
Vision pipeline       —                            /webhook/.../with-vision
                                                    (composes with DocIntel)
Real-time channel     WebSocket only               + Server-Sent Events
Storage               Postgres custom              + pgvector for embedding
                                                    cache; DuckDB for analytics
                                                    queries; same Postgres
                                                    schema
Multi-provider LLM    Hardcoded                    LiteLLM
Research artifact     None                         Online classification eval
                                                    (keyword vs embedding vs
                                                    LLM) latency/accuracy paper
```

---

### Cross-Project Synergy Summary (Why The Stack Choices Compound)

The six projects are not independent — they share a deliberate stack so a
single Upwork client can buy two or three of them as a bundle:

```
SYNERGY PAIR / TRIPLE        CLIENT VALUE PROPOSITION
─────────────────────────────────────────────────────────────────────
IntelAI + RAGeval        "Production RAG + measured quality"
                              (RAGeval drops in via @track decorator)
AgentKit + IntelAI       "MCP-powered analytics agents"
                              (Claude Desktop talks to your data)
DocIntel + StreamPulse       "Vision-first multi-source aggregator"
                              (auction listings, invoice intake, etc.)
                              ↑ This is the Equipment Sourcing pattern
VoiceFlow + AgentKit         "Real-time voice agent for KPIs"
                              (talk to your business via Realtime API)
RAGeval + DSPy + AgentKit    "Self-optimizing observable agents"
                              (research-credential story for 2027)
All six                      "Full AI-engineering stack reference"
                              (consultancy-level positioning by 2027)
```

The shared stack across all six:

```
LiteLLM                multi-provider abstraction
Claude Sonnet 4.6      premium reasoning tier (paid via Anthropic)
Claude Haiku 4.5       cheap frontier (judge, classify)
Groq Llama 3.3 70B     fast inference tier
Ollama Llama 3.3 70B   local fallback tier (and Llama 3.2 Vision)
BGE-large-en-v1.5      embeddings default
BGE Reranker v2 m3     reranking default
Postgres + pgvector    production storage default
ChromaDB / SQLite      dev storage default
OpenTelemetry / OTLP   observability standard
FastAPI + Uvicorn      API framework
LangGraph + Claude Agent SDK   agent frameworks
DSPy                   research-grade prompt programs
LiteLLM Embeddings     embedding provider abstraction
```

If a client asks "what's your stack" you have one answer. That coherence
is what separates a $35/hr "AI dev" from a $95/hr "AI systems engineer."

---

# PART III — MULTI-CHANNEL DISTRIBUTION

---

## Section 5: The 2026 Channel Mix (Strictly GitHub + Upwork + Loom)

**Important refinement (your explicit preference):** In 2026 you publish to
**three channels only — GitHub, Upwork, and Loom (demo videos).** Everything
else — personal portfolio site, Medium, dev.to, arXiv, LinkedIn — is deferred
to **2027**, where it becomes a deliberate multi-channel launch with all
2026's accumulated material as ammunition.

This is intentional minimalism. Doing fewer channels well in 2026 beats doing
many channels half-heartedly.

### 5.1 The 2026 vs 2027 channel split

```
                                  2026 (NOW)       2027 (LATER)
─────────────────────────────────────────────────────────────────────────
Upwork (proposals, delivery)        ✅ PRIMARY      Maintain rate
GitHub (public repos, README)       ✅ PRIMARY      Maintain + new repos
Loom (demo videos)                  ✅ PRIMARY      Maintain + voice-over
PyPI / DockerHub (artifacts)        ✅ Yes          Maintain
Personal portfolio site             ❌ NOT YET      ✅ Launch Q1 2027
Medium                              ❌ NOT YET      ✅ Cross-post Q1 2027
dev.to                              ❌ NOT YET      ✅ Cross-post Q1 2027
arXiv (preprint submission)         ❌ NOT YET      ✅ Submit Q1-Q2 2027
LinkedIn (posts)                    ❌ NOT YET      ✅ Cornerstone Q1 2027
Hacker News (Show HN)               ❌ NOT YET      ✅ One per project 2027
Reddit (r/MachineLearning etc.)     ❌ NOT YET      ✅ Selectively 2027
Twitter / X                         ❌ NOT YET      ✅ Optional 2027
Newsletter (Buttondown)             ❌ NOT YET      ✅ Optional Q2 2027
```

### 5.2 What "publish" means in 2026

For each completed project in 2026, "published" means:

1. **GitHub repo is public** with full README, demo link, LICENSE, CI green
2. **Loom demo recorded** (60-180 seconds, linked from README + Upwork)
3. **Upwork portfolio entry** with screenshots + demo link + bullets
4. **PyPI/DockerHub artifact** (where applicable: omnismart-personas, rageval, docintel image)

That's it. No blog post goes live in 2026. No Medium account is created in
2026. No arXiv submission in 2026. No LinkedIn post in 2026.

### 5.3 What you still DO in 2026 (without publishing)

You write **drafts**. You record **raw clips**. You collect **screenshots**.
You journal **stories**. All of this is **2027 ammunition**, not 2026 output.

```
ARTIFACT (drafted in 2026)                          DEPLOYED IN 2027
─────────────────────────────────────────────────────────────────────
6 blog posts (one per project, ~2000 words each)    Personal site + Medium
                                                     + dev.to (Q1 2027)
1 arXiv preprint draft                              Submitted to arXiv +
                                                     workshop (Q1-Q2 2027)
LinkedIn cornerstone post ("What I built in 2026")  Published Day 1 of
                                                     LinkedIn launch (Q1 2027)
20-30 short LinkedIn drafts (stories, snippets,     Drip-fed 2x/week
mini-tutorials, lessons from client work)            through 2027
Hacker News "Show HN" drafts (one per project)      Submitted across Q1-Q2
                                                     2027 (spaced out)
Conference talk outline (1 keynote-able topic)      Submitted to AI confs
                                                     for 2027 speaking slots
```

### 5.4 Why this minimalism is right for 2026

Three reasons:

**1. Channel proliferation is the freelancer killer.** Writers and devs who
try to be on 8 platforms simultaneously deliver nothing well. By restricting
to GitHub + Upwork + Loom, you concentrate all signal in the place clients
actually look.

**2. Late publishing compounds.** A blog post published in Q1 2027 with 6
months of post-build perspective + screenshots from real client work is
dramatically better than the same post published live during a hectic build
phase. Quality > timing, by a lot.

**3. You avoid the "stale content problem."** Posts published mid-build often
contain claims that turn out wrong by week 12. Drafting now and publishing
later lets you fact-check against shipped reality.

### 5.5 Effort allocation in 2026

```
Channel                                    Effort  ROI in 2026   ROI in 2027+
────────────────────────────────────────────────────────────────────────────
Upwork (proposals, profile, delivery)       65%   High           Medium
GitHub (public repos, README, CI, demos)    20%   High           Very high
Loom (demo videos + drafted-blog clips)      8%   High           Medium
PyPI / DockerHub artifacts                   5%   Medium         Medium
Writing drafts (blog, preprint, LinkedIn)    2%   Zero (drafted) Very high (deploy)
LinkedIn / Medium / arXiv / portfolio        0%   Zero           Foundation laid
```

### 5.6 By end of 2026, the position is:

```
PUBLISHED (LIVE) IN 2026:
  ✓ 6 GitHub public repos with READMEs, demos, CI
  ✓ 6 Loom demo videos
  ✓ 6 Upwork portfolio entries
  ✓ 2 PyPI packages (omnismart-personas, rageval)
  ✓ 1 DockerHub image (docintel)
  ✓ 5-10 paying Upwork client engagements completed

DRAFTED (BUT NOT PUBLISHED) IN 2026, READY FOR 2027:
  ✓ 6 blog posts (one per project, fact-checked against shipped reality)
  ✓ 1 arXiv preprint draft, peer-reviewed by 3-5 contacts
  ✓ 1 LinkedIn cornerstone post ("What I built in 2026")
  ✓ 20-30 short LinkedIn posts (stories, micro-tutorials, lessons)
  ✓ 6 Hacker News "Show HN" submission drafts
  ✓ 1 personal portfolio site design + content (ready to deploy)
  ✓ A spreadsheet of 100-200 LinkedIn target connections (from Upwork + cold email)
```

That's what makes 2027 explode rather than start cold. See Section 10 and the
2027 Distribution Plan (PART X) for the deployment playbook.

---

## Section 6: Upwork Strategy For 0-Review Freelancers

### 6.1 The fundamental constraint

Upwork's algorithm de-prioritizes new freelancers in search. Even with a
strong profile, your proposals will:

- Be invisible to most clients in the first 30 days
- Get throttled — you can only send ~30 proposals/week with Connects
- Be filtered out by clients with "Top Rated" preference set
- Need 5–10 reviews before unlock noticeable visibility increase

This means the first 4–8 weeks will feel discouragingly slow. Plan for it.

### 6.2 The 5-element proposal that works at 0 reviews

```
1. ONE sentence showing you read their specific job post
   (NOT generic "I have experience with X")

2. ONE sentence on the specific technical approach
   (Shows you've thought about THEIR problem)

3. Demo link (THE NEUTRALIZER — this replaces reviews)
   (Live URL OR Loom video — never just screenshots)

4. THREE specific technical questions
   (Proves you've thought about edge cases)

5. Clear timeline + scope
   (Shows you can manage a project, not just code)

Never write:
  - "I am an experienced AI developer with 5 years of experience"
  - "I am confident I can deliver this project"
  - Long lists of technologies

Always write:
  - Something specific about their job in the first line
  - A technical insight they may not have considered
  - The demo link in line 3 or 4, not at the end
```

### 6.3 Which projects to lead with on Upwork

```
PROJECT          UPWORK PRIORITY    WHY
─────────────────────────────────────────────────────────────
IntelAI     PRIMARY            Highest niche overlap
DocIntel        PRIMARY            Most consistent demand
RAGeval         SECONDARY          Premium-rate, lower volume
VoiceFlow       SECONDARY          Growing niche, lower volume
AgentKit        TERTIARY           Volume too thin; do open-source
StreamPulse     TERTIARY           Niche better suited to cold email
```

### 6.4 Application volume

Target: **5 proposals per day, every day**, for the first 60 days.
That's 300 proposals in 2 months. Realistic outcomes:

- 250–280 silence
- 15–25 interview requests
- 8–12 actual conversations
- 3–5 paid contracts
- 1–2 great long-term clients

This is the funnel. Plan for it. Don't be discouraged by silence — that's
the unavoidable cost of building visibility.

### 6.5 Connects (Upwork currency) management

Upwork charges Connects per proposal. Budget:

- 40 Connects/week starting (free Plus plan)
- Each proposal: 4–16 Connects depending on job complexity
- ROI metric: cost-per-interview-reply (CPR). Target <15 Connects/CPR.

If a niche burns 100+ Connects with 0 replies, **stop applying there**
and re-examine your demo and angle.

### 6.6 When to walk away from a job thread

- Client asks for free work as a "test" → walk away
- Client asks for a Skype/WhatsApp call before Upwork interview → walk away
- Client's job has 50+ applicants and 0 reviews on their side → low priority
- Client's last hire was paid $5/hr → walk away

Time spent dodging bad clients is worth more than time spent serving them.

---

## Section 7: Open-Source Strategy (PyPI, GitHub, DockerHub)

### 7.1 The compounding return

For each project, publish:

```
PROJECT          OSS DELIVERABLE                                LAUNCH BY
─────────────────────────────────────────────────────────────────────────
IntelAI     `pip install omnismart-personas`               Week 4
                (persona templates as standalone package)
AgentKit        GitHub repo (primary) + Awesome-MCP listing    Week 10
DocIntel        DockerHub: `docintel/api:latest`               Week 7
                (one command to run anywhere)
VoiceFlow       GitHub repo + Loom-anchored README             Week 13
RAGeval         `pip install rageval`                           Week 16
                (the SDK as primary distribution)
StreamPulse     GitHub repo                                     Week 18
```

### 7.2 Publishing checklist (every repo)

Before flipping public visibility:

- [ ] README under 200 lines, no marketing fluff
- [ ] Architecture ASCII diagram in README
- [ ] Quick-start (3 commands max) verified on fresh machine
- [ ] LICENSE (MIT or Apache 2.0)
- [ ] `.env.example` with placeholders, no secrets
- [ ] CI badge (GitHub Actions running tests on push)
- [ ] Loom demo embedded in README (top of file)
- [ ] Issue template (helps you when external users file issues)
- [ ] One-paragraph "why this exists" at top

### 7.3 Distribution after launch

- Submit to Awesome lists (`awesome-mcp`, `awesome-llm-tools`,
  `awesome-langchain`, `awesome-ocr`, `awesome-rag`, etc.)
- Post in relevant Discord/Slack: MCP Discord, Anthropic Discord,
  LangChain Discord, MLOps Community
- Cross-post Loom demo to YouTube Shorts (60–90s) — organic search traffic
- Submit to Hacker News on a Tuesday at 9am EST (highest visibility window)
- Reddit: r/LocalLLaMA, r/MachineLearning (read rules carefully), r/Python

**Do NOT** spam these communities. Post once per project, well-framed,
with the demo as the hook. Respond to every comment.

### 7.4 PyPI publishing (rageval, omnismart-personas)

```bash
# Setup
pip install build twine
python -m build  # Creates dist/*.tar.gz and dist/*.whl
twine upload dist/*  # First time: prompts for credentials
```

Use semantic versioning. Start at 0.1.0. Bump 0.2.0 on first
real feature add. Reach 1.0.0 when API is stable.

### 7.5 The PyPI download lift

Even modest download numbers carry weight:

| Downloads/month | Signal |
|-----------------|--------|
| 50–100 | "Built and shipped a real package" |
| 200–500 | "Has actual users, useful enough to install repeatedly" |
| 1000+ | "Notable community traction" |
| 5000+ | "Recognized in the niche" |

Target by end of 2026: rageval at 300/month, omnismart-personas at 100/month.

---

## Section 8: Technical Writing Strategy (Draft In 2026, Publish In 2027)

**Important per the channel split in Section 5.1:** in 2026 you **draft and
fact-check** all six blog posts, but **none are published publicly** in 2026.
They go into a `drafts/` directory in each repo (or a single private
`writing/` Notion workspace). Q1 2027 they all go live as part of the
LinkedIn launch sequence.

### 8.1 Cadence (drafting in 2026)

One post drafted per build phase. Six posts drafted by end of Phase 6. The
"finishing pass" (post-build, with screenshots from real client work) happens
in December 2026 or January 2027 — that's when each post becomes
publication-ready.

### 8.2 The 6 posts (drafted alongside build phases)

```
End of Phase 1  Draft 1: Persona-Routed RAG — How To Scope LLM Responses By Role
                (Project 1 artifact)
End of Phase 2  Draft 2: Vision-First Document AI — Beyond Tesseract
                (Project 3 artifact, leads with vision-LLM upgrade)
End of Phase 3  Draft 3: Building MCP Servers For Business Data — Tool Design Patterns
                (Project 2 artifact, biggest reach potential)
End of Phase 4  Draft 4: Speech-To-Intelligence — Whisper Plus LLM Post-Processing
                (Project 4 artifact, includes real-time voice agent demo)
End of Phase 5  Draft 5: Multi-Judge LLM Evaluation For Production RAG
                (Project 5 artifact, the research-credential post)
End of Phase 6  Draft 6: Vision-First Multi-Source Aggregation — A Pattern
                (Project 6 + Project 3 combo, includes Equipment Sourcing
                 case study from real client work)
```

### 8.3 Where (eventually) to publish — 2027 only

The full publish-stack (deployed in Q1 2027):

1. **Personal site** (`yacine.dev` or similar) — own the canonical URL,
   launched Q1 2027
2. **Medium** — cross-posted with canonical link back to personal site
3. **dev.to** — community traffic, cross-posted
4. **LinkedIn article format** — for the cornerstone-post and 1-2 best posts
5. **Hacker News** — Show HN for repo-tied posts, one shot per post
6. **Reddit (r/MachineLearning, r/LocalLLaMA, r/LanguageTechnology)** —
   thoughtful, methodology-led posts only
7. **arXiv** — for the 1–2 posts that get polished into preprints (Q1-Q2 2027)
8. **Substack newsletter** — optional, only if you decide to commit to it

In **2026 you publish to NONE of these.** The drafts live in:

```
~/projects/<each-repo>/drafts/
  blog_post_1_persona_routed_rag.md
  blog_post_2_vision_first_doc_ai.md
  ... etc

~/projects/writing_workspace/
  blog_drafts/
  linkedin_drafts/
  preprint_v1.tex (Overleaf-synced)
  client_stories.md
```

### 8.3.1 The 2026 "finishing pass" workflow

After each build phase ends, before starting the next phase:

```
1. Open the draft you wrote during the phase
2. Read it against the actual shipped repo
   — Are all claims still accurate? (claims rot fast)
   — Are code snippets the actual code? (paste them, don't transcribe)
   — Did the numbers change? (eval numbers especially)
3. If a paying client used this project, add a 1-2 sentence
   anonymized story ("One client used this to do X, saving Y hours/week")
4. Mark TODO comments where you want to add a screenshot from production
5. Save as `vN-postship.md` — this is the version that gets published Q1 2027
6. Do NOT publish yet. Move on to next phase.
```

### 8.4 Post structure (use this template every time)

```
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
```

### 8.5 From blog post to arXiv preprint

If 2 of the 6 posts have:
- A novel pattern
- A small empirical evaluation
- An open-source artifact

They're arXiv-suitable. Format using a NeurIPS/ICML LaTeX template
(easier than you think — Overleaf has them). Aim for 6 pages.

**Submission strategy:** workshop submission, not main conference.
Workshops accept 50%+ of submissions. Workshop accept on your CV
is meaningful for research-degree applications.

Target workshops for 2026 preprints:
- NeurIPS 2026 (Dec) — workshop deadlines in Oct
- ICLR 2027 (May) — workshop deadlines in Jan
- AAAI 2027 (Feb) — workshop deadlines in Nov

### 8.6 Realistic outcomes

```
End of 2026:
  6 blog posts published
  Total readership: 5,000–15,000 unique reads (long tail accumulates)
  1 arXiv preprint up
  Maybe 1 accepted at a workshop (50/50 odds)
  Established as "person who writes well in this niche"
```

That's enough to make research-program admissions committees take you
seriously.

---

## Section 9: Cold Email + Communities

### 9.1 Cold email cadence

10 emails per week. Targeting:

- **Tier 1: YC startup CTOs** in your verticals (use F6S, LinkedIn search,
  YC alumni directory). 30% of effort.
- **Tier 2: Fractional CTO / consulting agencies** that need overflow
  AI engineering help. 30% of effort.
- **Tier 3: Slack/Discord community admins** who might want to feature
  your open-source work. 20% of effort.
- **Tier 4: AI labs and research-aligned orgs** for research-engineer
  contract work. 20% of effort.

### 9.2 Cold email template

```
Subject: [Specific value tied to their company/role]

Hi [Name],

I noticed [specific thing about their company/recent post/job posting].

I built [specific thing relevant to their work]. Demo: [link].

The interesting part for you might be [specific feature].

Worth a 15-minute chat?

Yacine
[Brief signature: 1 line + link to portfolio]
```

Do NOT send 100-word "I'm an experienced developer" boilerplate. The
3-sentence specific email outperforms it 10:1.

### 9.3 Communities to be active in

```
COMMUNITY                      VALUE
─────────────────────────────────────────────────────────────
Indie Hackers                  Find peers, see what's selling
MLOps Community Slack          Build credibility in observability niche
LangChain Discord              Cross-promote AgentKit + RAGeval
MCP-related servers            First-mover advantage on AgentKit
r/LocalLLaMA                   Cross-promote OSS releases
r/MachineLearning              Research-adjacent traffic
HN (Hacker News)               Launch posts, 1 per project
arXiv-sanity                   Stay current on research
```

Be useful, not promotional. Answer questions. Drop your demos when
genuinely relevant. People will look you up.

### 9.4 Conversion from communities to clients

- Direct: someone posts a problem you can solve, you DM/email them
- Indirect: someone notices your demos, recommends you to a colleague
- Compound: 6 months of being known in a community = warm referrals forever

Track community-driven leads separately from Upwork in your Notion log.

---

## Section 10: LinkedIn 2027 — Light-Touch Prep Now

You said: not active on LinkedIn in 2026, planning to start in 2027.
Don't ignore it entirely — do this minimum:

### 10.1 The 2026 LinkedIn prep checklist

- [ ] Profile fully filled (use the title and overview from Section 24)
- [ ] Headshot updated (clean, professional, not corporate-formal)
- [ ] Connect with every Upwork client you complete a project with
- [ ] Connect with anyone whose cold email warmly replies
- [ ] Follow (don't engage with) 50 AI freelancers + researchers you admire
- [ ] Save (don't post) content you find good — build your asset library
- [ ] Observe which post formats perform: technical depth? story?
  carousel? short hot take?

### 10.2 The 2026 quiet network growth

Every Upwork client connect + every cold email reply = a new LinkedIn
connection. By end of year, target 200+ connections.

These will be your 2027 launch audience. They'll see your posts naturally
in their feeds. Cold launch (zero network) is dead; warm launch
(200+ in-niche) is a different ballgame.

### 10.3 The 2027 launch (one paragraph for now)

In January 2027, you'll:

1. Publish a "what I built in 2026" post linking your 6 demos + 6 blog
   posts + 2 PyPI packages
2. Begin a 2-posts-per-week cadence using your 2026 content library
3. Pin a featured section with your strongest 3 projects
4. Run weekly engagement (comment thoughtfully on 10 posts/day)

But that's 2027's problem. In 2026, just build the asset library and
the connection base.

---

# PART IV — THE RESEARCH DEGREE TRACK

---

## Section 11: What Top Programs And Fellowships Want In 2026

Top AI programs (Stanford, CMU, MIT, Berkeley, UCL, ETH, Mila, Vector,
Oxford) and prestigious fellowships (Anthropic Fellows, OpenAI Residents,
Meta AI Residents) have shifted what they value in 2024–2026.

### 11.1 What used to matter (less now)

- GRE scores → most programs dropped or made optional
- Undergrad GPA → still matters but weighted less for industry applicants
- Generic Python/ML skills → assumed, not differentiating
- Course projects → too easy to fake, less weight

### 11.2 What matters now

In descending order of weight for an industry-to-research candidate:

1. **Published research output**: arXiv preprints, workshop papers, or full
   conference papers. Even 1 strong preprint moves you from "competitive"
   to "stand out."

2. **Open-source contributions with traction**: maintained repos with
   stars/downloads/forks. Anthropic, OpenAI, and DeepMind explicitly hire
   from OSS in 2026.

3. **Deployed AI systems with documented impact**: not toy projects.
   Production systems with users, real data, measurable outcomes.

4. **Reference letters from research-active mentors**: 2–3 strong letters.
   Industry leaders count if they've done research.

5. **Statement of purpose with a clear research question**: not "I want to
   study AI" but "I want to study X specific phenomenon I observed in
   production."

6. **Technical writing**: blog posts, contributed papers, well-documented
   code. Shows clarity of thought.

7. **Coursework / prior research**: still matters but less than the above
   for industry applicants.

### 11.3 The Anthropic Fellows path specifically

The Anthropic Fellows program (and similar at other top labs) values:

- Demonstrated work on alignment, interpretability, or AI safety problems
- Strong technical engineering skills (production deployment)
- Independent thinking (a portfolio of well-argued blog posts goes far)
- Ability to write clearly (most candidates can't)

**Persona-routed RAG with role-scoped data access** (your IntelAI
core differentiator) connects to alignment-relevant questions:

- How do you constrain LLM behavior to a defined role?
- How do you evaluate adherence to that role at scale?
- How do you make role-conditioned responses measurable and auditable?

These are not arbitrary connections — they're the alignment community's
language for what you've been building.

---

## Section 12: How This Plan Builds Research Capital

### 12.1 The asset stack at end of 2026

```
ASSET                                     WHAT IT BUYS YOU
─────────────────────────────────────────────────────────────
6 deployed projects (live demos)          Production AI experience narrative
2 PyPI packages with users                Open-source contribution credibility
6 technical blog posts                    Technical writing demonstration
1 arXiv preprint (probably 2)             Research output credibility
Workshop submission (maybe accepted)      External validation
200+ in-niche LinkedIn connections        Network depth
2-3 strong client references              Letters of recommendation
Sustained Upwork income                   Industrial experience proof
A coherent through-line in your writing   Statement-of-purpose foundation
```

This is a strong industry-to-research transition portfolio. Stronger
than 80% of CS-grad applicants who haven't shipped to production.

### 12.2 The through-line you should be writing toward

Your research narrative in late 2027 should look something like:

> "I spent 2026 building production AI systems for business intelligence.
> Across 6 deployed projects, I observed a recurring pattern: production
> AI assistants need role-scoped behavior — a CFO query and a CHRO query
> should retrieve different data and produce different responses, even
> against the same underlying corpus.
>
> Existing RAG evaluation frameworks (Phoenix, Langfuse, TruLens) measure
> retrieval relevance and groundedness, but don't capture role-scope
> adherence. I formalized this with 'persona-conditioned groundedness'
> in a preprint and an open-source library (rageval).
>
> At PhD level, I want to extend this in two directions:
> (1) interpretability — what mechanisms in instruction-tuned LLMs
> mediate role conditioning?, and (2) alignment — can role-scoped
> behavior be a primitive for more general AI safety properties?"

That narrative is concrete, falsifiable, connects to current research
agendas, and is grounded in deployed work. It's not generic.

### 12.3 The work-to-narrative pipeline

```
EVERY PROJECT YOU SHIP:
   ↓ produces
LIVE DEMO + GITHUB REPO + BLOG POST
   ↓ together feed
THE NARRATIVE THROUGH-LINE (Section 12.2)
   ↓ which structures
YOUR ARXIV PREPRINT(S) IN 2026
   ↓ which become
YOUR STATEMENT OF PURPOSE IN 2027
   ↓ supported by
REFERENCE LETTERS FROM CLIENTS YOU SERVED IN 2026
```

Each link reinforces the next. Don't write your statement of purpose
in 2027 from scratch — write it incrementally as you ship in 2026.
The blog posts are the drafts.

---

## Section 13: One Preprint Per Year (Realistic Cadence)

### 13.1 The 2026 preprint

Target: **"Persona-Conditioned Groundedness: An Evaluation Framework
for Role-Scoped RAG Systems"**

Why this one first:
- Builds directly on work you're already doing
- Has a concrete artifact (rageval library)
- Has a clear measurement story (you'll have the eval data)
- Connects to active research areas (RAG eval + alignment)
- Workshop-publishable bar (not full-conference difficulty)

Timeline:
- Weeks 14–16: build RAGeval (the artifact)
- Weeks 17–20: collect evaluation data on real persona usage
- Weeks 21–24: write draft, submit to a workshop, publish to arXiv

End-of-year goal: preprint on arXiv with link in your portfolio.

### 13.2 The 2027 preprint (preview)

Likely topic: **"MCP Tool Design Patterns for Production AI Agents"**

Why:
- AgentKit is the artifact
- Pattern catalog is workshop-quality novelty
- Field is hot, accept rates favorable

Don't commit yet — let 2026 deployment data shape the exact angle.

### 13.3 Workshop submission strategy

Submit your 2026 preprint to **2–3 workshops simultaneously**:

- NeurIPS workshop track (most workshops accept dual submissions; check
  individual workshop rules)
- A pure-eval workshop (e.g., "Workshop on LLM Evaluation")
- An alignment-adjacent workshop (e.g., "Workshop on Trustworthy LLMs")

Workshops accept 40–60% of submissions. With a polished preprint,
strong odds of at least one acceptance. Workshop acceptance = a citable
publication on your CV.

### 13.4 The "good enough" preprint standard

You're not aiming for ICLR oral. You're aiming for:

- 6 pages of clean, well-formatted writing
- A concrete problem statement
- A novel pattern or framework
- A small empirical evaluation (10–30 data points minimum)
- A released artifact (code + data)
- A statement of limitations

That's the bar. Stop polishing past it.

---

## Section 14: Research-Aligned Freelance Opportunities

Some freelance work moves you toward research credentials:

### 14.1 Research-adjacent contract work

| Organization | Type | Pay | Research Value |
|--------------|------|-----|----------------|
| **Anthropic** | Research engineer contracts | $$$$ | Very High |
| **OpenAI** | Research engineer contracts | $$$$ | Very High |
| **Cohere / Mistral / AI21** | Engineering contracts | $$$ | High |
| **Apollo Research** | AI safety contracts | $$$ | Very High |
| **METR / ARC Evals** | Evaluation contracts | $$$ | Very High |
| **MIRI / FHI / GovAI** | Safety / policy research | $$ | Very High |
| **Workshop / conference orgs** | Reviewer, organizing | $0–$ | Medium |
| **Open-source maintenance grants** (Sloan, NumFOCUS) | Maintenance | $$$ | Medium-High |

Apply for these strategically. Even one short contract with a research-aligned
org is a strong reference and a CV bullet that beats most Upwork work.

### 14.2 Upwork research-engineer postings (yes, they exist)

Search Upwork for:
- "Research engineer"
- "AI research engineer"
- "LLM researcher"

Filter for U.S. tech-company clients. Pay is usually $80–150/hr.
Apply with your strongest demo + a brief note that you've published
to arXiv (when you have).

### 14.3 The reference letter strategy

For each major client engagement, after 3+ months of solid work:

1. Ask if they'd be willing to write a reference letter (or be a referee
   you can list) for future opportunities.
2. Prefer clients who themselves do research or are former researchers.
3. Maintain the relationship light-touch — quarterly check-ins, sharing
   relevant blog posts.

Goal: 3 strong references by end of 2027 from professional engagements.
Combined with 1–2 references from open-source community work (maintainers
of projects you contributed to), that's 5 letters.

---

## Section 15: Reference Letter Strategy

(Folded into Section 14 above — three short-form reference building paths:
client work, open-source community contribution, and research-aligned
contract work.)

The biggest mistake industry-to-research applicants make: assuming professors
they took classes with will write strong letters. Often professors barely
remember them and write generic letters. **Specific, recent, work-based
referees write specific, recent, work-based letters.** That's what wins.

---

# PART V — EXECUTION (18 WEEKS + WEEK 0, SEQUENTIAL, ALL SIX)

---

## Section 16: Phased Build Plan (Day-by-Day, All Six Projects)

This section is the operational core of the document. It assumes you build all six
projects sequentially — one finished and published before the next begins — and
that the **monorepo split is executed once, upfront, in Week 0**, before any
phased product work begins.

The total span is **19 calendar weeks**: 1 splitting week + 18 build weeks.
Day numbering restarts at Day 1 of Week 0 and runs continuously through Day 133.

---

### 16.0 Principles And The Decision To Build All Six

You made an explicit decision: **build all six, sequentially, publish each as it
ships**. This section codifies the implications of that decision.

#### Why sequential beats parallel (for you, in 2026)

1. **Cognitive coherence.** Switching contexts between MCP servers, OCR pipelines,
   and voice intelligence kills depth. One project at a time lets your brain stay
   in one architectural model.
2. **Publish-as-you-go compounds.** Each shipped project becomes a portfolio entry
   *while the next is being built*. By Week 6 you already have two live demos,
   not zero "until Phase 6 finally lands."
3. **Feedback is cheaper.** If DocIntel's positioning bombs in Phase 2, you adjust
   in Phase 3 — not after you've committed three more months to parallel builds.
4. **One environment to operate at a time.** Build environment, test environment,
   deploy environment all stay focused on the current project. No cross-repo
   dependency tangles.

#### Why the split happens in Week 0, not later

The original v1 plan said "extract repos incrementally as you start each phase."
Your stated preference: **extract them all upfront**. This is the better call for
five reasons:

1. **Clean scope from day one.** The moment you start Phase 1, every other repo
   is already its own directory with its own `requirements.txt`. No "wait, is this
   still in the monorepo?" ambiguity.
2. **Forces architectural decisions early.** Splitting reveals which utilities are
   shared, which dependencies are core vs. peripheral, which imports were sloppy.
   You make those calls once at the start.
3. **Git history starts clean per repo.** Each project has commits that read like
   the project's own evolution, not "extracted from IntelAI in week N."
4. **Easier mental model.** Six directories side-by-side. You always know which
   one you're working in.
5. **One splitting pass, not six.** The AI agent prompt is run once with all six
   target schemas. If you split incrementally you'd re-prime context six times.

The de-risking step: **test the prompt on DocIntel first** (the most self-contained
project, primary file is `ocr_enhancement.py`). If DocIntel's extraction works
cleanly — imports resolve, tests pass, server starts — you trust the prompt for the
other five. If DocIntel breaks, you fix the prompt before running it on the others.

#### Build order rationale (why Phase 1 = IntelAI, Phase 6 = StreamPulse)

The order is chosen by **freelance signal value × research signal value × build
risk**, not by alphabetical or technical convenience.

```
PHASE  PROJECT          WHY THIS POSITION
─────────────────────────────────────────────────────────────────────────────
1      IntelAI      Already mostly built. Fastest path to first live demo.
                        Sets the Upwork profile baseline. Bilingual hero asset.
2      DocIntel         Highest-volume Upwork niche (OCR/document AI). Validates
                        income signal before committing to longer builds.
3      AgentKit         Open-source-first asset. MCP is rare/elite. Compounds
                        GitHub stars and cold-email credibility during weeks 7-9.
4      VoiceFlow        Visual demo (browser recording) → strong portfolio piece.
                        Medium freelance niche. Builds before research push.
5      RAGeval          Highest research-value project. PyPI package + preprint
                        foundation. Built after you have signal on what to evaluate.
6      StreamPulse      Cold-email primary (data/ops directors). Lower Upwork
                        priority. Last because it's the most peripheral to your
                        2027 narrative — finishing the set, not anchoring it.
```

#### What "publish" means at the end of each phase

A project is **published** (not just "built") when ALL of the following are true:

- Live demo URL works in incognito browser (no auth, no broken images)
- GitHub repo is public with README < 250 lines, accurate, with demo link
- One Loom video (60–180 seconds) walking through the demo, linked in README
- For PyPI projects: `pip install <package>` works for a stranger
- For Docker-shipped projects: `docker pull` works from DockerHub
- One blog post live on your personal site + cross-posted to Medium/dev.to
- Project added to Upwork portfolio with screenshots + demo link
- One proposal already sent on Upwork referencing the new portfolio entry
- (For Phases 3 & 5) Posted to relevant community (MCP Discord, HN, r/LocalLLaMA)

If any of those fail, **do not advance to the next phase**. Take the buffer day
to finish — quality of the published asset matters more than calendar pace.

#### Calendar reality check

The schedule below assumes ~6 productive hours per day, 5–6 days per week, with
Sundays usually off. If your reality is less, scale every phase by 1.3× and accept
the longer total. Do not compress by skipping eval datasets, demo recordings, or
README rewrites — those are the assets that earn money, not the code itself.

---

### 16.1 Phase 0 — Repository Splitting (Week 0)

**Goal:** Six standalone repositories created, validated, pushed to GitHub
(private until each phase ships), local dev environments ready for Phase 1
to start Monday of Week 1 without setup overhead.

**Duration:** 7 days (1 calendar week). If you finish earlier, do not start
Phase 1 early — use the slack for clean-up audits and reading.

**Output:** Six directories at `~/projects/` (or your preferred location):
```
~/projects/
  intelai/        ← refactored monorepo (Phase 1 target)
  agentkit/           ← MCP server + LangGraph workflow
  docintel/           ← document intelligence pipeline
  voiceflow/          ← speech-to-intelligence
  rageval/            ← LLMOps observability
  streampulse/        ← real-time data pipeline
```

#### Day 1 — Pre-Split Audit + Cleanup

**Morning (3h):** Inventory and decision-making.

```
Tasks:
  1. Snapshot the monorepo as-is (tag git: git tag pre-split-2026-05-18)
  2. Read /etc and /docs directories. List stale files for deletion:
       COMPLETION_REPORT.md
       INTEGRATION_PLAN.md
       WORK_INDEX.md
       Production_Readiness_Checklist.md
       docs/200_TASKS_COVERAGE.md
       omniinteloscompletestrategy  (replaced by STRATEGY.md v2)
       Any *_NOTES.md or *_PLAN.md older than 30 days
  3. For each candidate deletion, grep the codebase for references.
     If nothing references it, mark for deletion.
  4. Verify pyproject.toml / requirements.txt match what's actually
     imported (use `pip-check` or `pipreqs .`).
  5. List shared utilities (logger.py, config.py) and note which projects
     will need slim copies vs. full copies.
```

**Afternoon (3h):** Reference the split.

```
Tasks:
  6. Re-read STRATEGY.md Appendix "Project Source Map" — confirm the
     file-to-project mapping still matches the current repo state.
  7. Re-read Section 30 (the splitting prompt). Walk through mentally:
     where would the prompt fail given the current code? Note pre-edits
     needed (e.g., is src.core.pg_engine importable standalone?).
  8. If imports are tangled, do a minimal pre-clean: convert any
     "from src.something.deep import" to "from src.X import" where it
     reduces depth without behavior change.
```

**End of day checkpoint:**
- [ ] Pre-split git tag exists
- [ ] List of files to delete is written down
- [ ] List of pre-edits to imports is written down (≤ 10 edits)
- [ ] You can articulate in 60 seconds what the splitting prompt does

If any checkpoint fails, spend an extra day. Do not move on with foggy intent.

#### Day 2 — Splitting Prompt Dry-Run on DocIntel

**Morning (4h):** Test the prompt on a single project to catch bugs cheaply.

```
Tasks:
  1. Open a NEW Claude Code session (clean context window).
  2. Provide it ONLY the DocIntel section of the splitting prompt
     (from Section 30, the PROJECT 3 block).
  3. Let it create the docintel/ directory and all files.
  4. As soon as it finishes:
       cd docintel
       python -m venv .venv && source .venv/bin/activate
       pip install -r requirements.txt
       python -c "from services.ocr_enhancement import *"
       python -c "from services.llm_extractor import LLMExtractor"
       uvicorn api:app --port 8001 &
       curl http://localhost:8001/health
  5. Test the /classify endpoint with a sample PDF:
       curl -X POST http://localhost:8001/classify -F file=@sample.pdf
  6. If anything breaks, the splitting prompt has a bug. Fix it BEFORE
     running on the other 5.
```

**Afternoon (3h):** Identify and patch prompt gaps.

```
Common breakages to look for:
  - "from src.X import" left in files (the prompt missed an import rewrite)
  - Missing __init__.py files in services/ or core/
  - Hardcoded paths that assume monorepo root
  - Requirements.txt missing a dep that's actually imported
  - .env.example missing a var that the code reads on startup
  - Dockerfile copies non-existent paths

For each gap found:
  1. Note the exact symptom
  2. Update Section 30's prompt text to fix it explicitly
  3. Re-run prompt on DocIntel to confirm fix works
  4. Repeat until DocIntel starts cleanly from a fresh clone
```

**End of day checkpoint:**
- [ ] `docintel/` runs `uvicorn api:app` and responds to /health
- [ ] All imports resolve from project root (no `from src.*` left)
- [ ] requirements.txt has no missing or extra deps
- [ ] Splitting prompt has been updated with any fixes discovered

#### Day 3 — Run Full Splitting Prompt for Remaining 5 Projects

**Morning (5h):** Execute the validated prompt on the other five projects.

```
Tasks:
  1. Open a NEW Claude Code session per project (5 sessions, sequential).
     Doing them sequentially in fresh sessions keeps context focused.
  2. For each project (AgentKit, VoiceFlow, RAGeval, StreamPulse, plus
     the IntelAI refactor):
       a. Provide the corresponding PROJECT N block from Section 30
       b. Let it create the directory and files
       c. Immediately verify:
            cd <project>
            python -m venv .venv && source .venv/bin/activate
            pip install -r requirements.txt
            python -c "import <main_module>"  # smoke test
            uvicorn api:app --port 8001 &     # for FastAPI projects
            curl http://localhost:8001/health
       d. Note any failure; do NOT move to next project until current is clean
  3. The IntelAI refactor is "edits in place," not a new directory:
       a. Apply the PROJECT 1 changes to the existing repo
       b. cd frontend && npm install recharts (do this!)
       c. Run pytest tests/test_api.py to confirm tests still pass
       d. Skip deployment to Railway for now (Phase 1, Day 5)
```

**Afternoon (3h):** Cross-project sanity checks.

```
Tasks:
  4. Confirm no project imports from another project (no cross-repo deps)
  5. Confirm every project has:
       - README.md (even if minimal)
       - requirements.txt (minimal, no transitive bloat)
       - Dockerfile (builds without error: docker build -t <name>:test .)
       - .env.example (every secret has a placeholder)
       - .gitignore (.venv, __pycache__, .env, *.db, etc.)
  6. Run pip-compile or similar on each requirements.txt to flag
     unpinned versions that could drift.
  7. For each project, write a 3-line note in your Notion log:
       "What does this project actually do, in plain English?"
     If you can't write 3 clear lines, the README needs work — flag it
     for the project's own phase.
```

**End of day checkpoint:**
- [ ] All 6 directories exist
- [ ] All 6 pass smoke tests (import works, /health works for FastAPI ones)
- [ ] All 6 have Dockerfile that builds
- [ ] You have written what each project does in your own words

#### Day 4 — Per-Project Verification Pass + Test Skeletons

**Morning (4h):** Deeper verification beyond smoke tests.

For each of the six projects, run the following matrix:

```
PROJECT       SMOKE TEST                    DEEPER VERIFY
──────────────────────────────────────────────────────────────────────────
intelai   pytest tests/                 All 9 personas resolve;
                                            chat endpoint returns text
agentkit      python mcp_server.py          MCP tools list correctly;
                                            workflow.analyze() returns dict
docintel      curl /classify with PDF       Returns doc_type within 5s
voiceflow     curl /health                  Whisper loads (may take 30s
                                            first time — note this)
rageval       python -c "import evaluator"  RAGEvaluator.score_interaction()
                                            runs on fake data
streampulse   curl /pipeline/status         WebSocket /live accepts connection
```

For each project that has tests/, ensure pytest runs and at least one test
passes. For projects without tests, create `tests/__init__.py` and a single
`tests/test_smoke.py` with one trivial assert — this primes the test culture
for that phase's expansion.

**Afternoon (3h):** Per-project notes file.

In each project root, create `STATUS.md` (this file is NOT committed; it's your
working notes). Format:

```
# <project> STATUS

## What works today
- [list smoke-test-verified capabilities]

## Known gaps (will fix in Phase N)
- [list things you noticed during the split that need polish]

## Risk items
- [things that might break when deployed or scaled]

## Next phase tasks (pre-load Phase N's todo list)
- [3-5 concrete tasks the phase will tackle]
```

This file becomes your phase kickoff brief 1, 4, 7, 10, 13, or 16 weeks from now —
when you've forgotten the context. Future-you will be grateful.

**End of day checkpoint:**
- [ ] All 6 projects have deeper verify passing
- [ ] Each project has a STATUS.md with known gaps noted
- [ ] You have a list of pre-Phase 1 fixes needed for IntelAI

#### Day 5 — Git Init + GitHub Push (Private) + Branch Strategy

**Morning (3h):** Initialize git per project and push as private repos.

```
Tasks (do this for each of the 6 projects):
  1. cd <project>
  2. git init
  3. git add . (after .gitignore is in place — verify with git status)
  4. git commit -m "initial: extracted from IntelAI monorepo (week 0)"
  5. Create the repo on GitHub as PRIVATE:
       gh repo create <yourname>/<project> --private --source=. --remote=origin
  6. git push -u origin main
  7. Verify: gh repo view <yourname>/<project>

Repos to create (suggested naming):
  - intelai        (or omnismart if name conflicts)
  - agentkit
  - docintel
  - voiceflow
  - rageval
  - streampulse
```

**Afternoon (3h):** Branch strategy + CI scaffolding.

```
Tasks:
  8. On each repo, create a "develop" branch for daily work:
       git checkout -b develop && git push -u origin develop
     "main" is for shipped/tagged versions. "develop" is for build work.
  9. Add minimal GitHub Actions to each repo (.github/workflows/ci.yml):
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
     This catches "the app doesn't even start" failures automatically
     for the next 18 weeks.
 10. Run a manual "Actions" trigger on each repo to confirm CI is green.
     If a project's CI fails, add it to the project's STATUS.md as
     a "must fix in Phase N Day 1" item.
```

**End of day checkpoint:**
- [ ] 6 private GitHub repos exist
- [ ] Each has a develop branch
- [ ] Each has CI configured and passing (or a known-issue noted)
- [ ] You can `gh repo view <name>` on each one

#### Day 6 — Local Environment Hygiene + IDE Workspace

**Morning (3h):** Make the local dev experience friction-free.

```
Tasks:
  1. Decide on a single Python version (recommend 3.11 — stable, broad
     dependency support, matches Railway/Fly.io defaults). Install via
     pyenv if you don't already use it.
  2. For each project, ensure .venv exists and is fresh:
       cd <project>
       rm -rf .venv
       python3.11 -m venv .venv
       source .venv/bin/activate
       pip install -U pip wheel setuptools
       pip install -r requirements.txt
  3. Document this in each project's CONTRIBUTING.md or README's "Quick
     Start" so you (and future contributors) can replicate.
  4. Create a top-level workspace dotfile if your editor supports it
     (VS Code: <name>.code-workspace pointing at all 6 directories).
     This lets you open all 6 in one window with cross-project search.
```

**Afternoon (3h):** Environment variables and secrets hygiene.

```
Tasks:
  5. For each project, copy .env.example → .env and fill in real values
     (your actual GROQ_API_KEY, POSTGRES_URL, etc.). Verify NONE of
     these .env files are committed (git status should not list them).
  6. Create a top-level secrets.md outside any repo with all the keys
     and URLs you're using locally. This is your single source of truth
     when something breaks at 11pm.
  7. Run each project once locally end-to-end with real keys to confirm
     the .env propagates correctly (FastMCP, Groq, Whisper, all need
     valid keys to do anything useful).
```

**End of day checkpoint:**
- [ ] All 6 projects have working .venv (3.11)
- [ ] All 6 have working .env (not committed)
- [ ] You can `cd <project> && source .venv/bin/activate && uvicorn api:app`
      for each FastAPI project in under 30 seconds
- [ ] secrets.md exists somewhere safe (NOT in any repo)

#### Day 7 — Buffer + Pre-Phase-1 Planning

**Morning (3h):** Cleanup.

```
Tasks:
  1. Apply the file deletions from Day 1 to the IntelAI refactor:
       rm COMPLETION_REPORT.md INTEGRATION_PLAN.md WORK_INDEX.md
       rm Production_Readiness_Checklist.md
       rm docs/200_TASKS_COVERAGE.md
       rm omniinteloscompletestrategy   # v1 strategy now superseded
     Commit: "chore: remove stale planning docs (v2 strategy supersedes)"
  2. Refactor the intelai repo README to point at STRATEGY.md
     instead of the deleted docs.
  3. Ensure STRATEGY.md (this file) is itself committed.
```

**Afternoon (3h):** Phase 1 prep.

```
Tasks:
  4. Open the intelai repo and lay out a TODO.md with Phase 1's
     Day 1-5 tasks in checkbox form (from Section 16.2). You will
     check these off in real time during Phase 1.
  5. Confirm Recharts is installed in frontend/ (was done Day 3 if
     part of IntelAI refactor — verify):
       cd intelai/frontend && npm list recharts
  6. Identify which Upwork niches you'll start with on Day 12 of Phase 1
     (after profile + demo are live). Recommended: RAG, FastAPI, AI chatbot.
  7. Set a personal calendar reminder for Phase 1, Day 1: "Build IntelAI
     visuals — Recharts replacement starts today."
```

**End of day checkpoint (end of Week 0):**
- [ ] All Day 1-6 checkpoints are green
- [ ] Stale docs deleted from intelai repo
- [ ] TODO.md exists in intelai for Phase 1
- [ ] You are not exhausted; you are ready for Phase 1
- [ ] You have not started Phase 1 work yet (respect the buffer)

#### Week 0 success criteria (overall)

```
DELIVERABLE                                                 STATUS
─────────────────────────────────────────────────────────────────
6 standalone project directories                            [ ]
All 6 have passing smoke tests                              [ ]
All 6 have private GitHub repos with develop branch         [ ]
All 6 have working .venv + .env + Dockerfile that builds    [ ]
All 6 have CI configured and green                          [ ]
Each project has a STATUS.md with known gaps                [ ]
IntelAI stale docs deleted, README updated              [ ]
TODO.md in intelai exists for Phase 1 Day 1             [ ]
```

If any row is unchecked, **do not start Phase 1**. Spend the weekend (or an
extra day) closing the gap. Phase 1 success depends on Week 0 being clean.

---

### 16.2 Phase 1 — IntelAI Foundation (Weeks 1–3)

**Goal:** Publish the first portfolio entry. Demo live, Upwork profile launched,
omnismart-personas package on PyPI, first 50 proposals out, Blog Post 1 published.

**Phase 1 cadence:** Build → Polish → Publish. Three weeks, one deliverable
shipped at the end.

#### Week 1 — Visual + Technical Fixes

```
Day 8 — Recharts Conversion (Part 1)
─────────────────────────────────────────────
Morning:
  cd intelai/frontend
  npm install recharts (confirm package.json)
  Replace SVG bars in AnalyticsPage.jsx with Recharts LineChart
  Verify in browser: charts render, data loads from API
Afternoon:
  Replace ForecastingPage.jsx chart with AreaChart + CI bands
  (use two Area components stacked for upper_ci / lower_ci shading)
  Test with multiple metric selections


Day 9 — Recharts Conversion (Part 2) + Risk + Dashboard
─────────────────────────────────────────────
Morning:
  Add RadarChart to RiskPage.jsx (risk.components data)
  Add sparkline LineCharts to DashboardPage.jsx (last 6 KPI values)
Afternoon:
  Complete FinancialPage.jsx (replace stub):
    - Dropdown for income_statement / balance_sheet / cash_flow
    - Call api.post('/financial/statement', {statement_type: selectedType})
    - BarChart of line_items from response
  Manual smoke test all 4 pages in browser


Day 10 — WebSocket Streaming for Chat
─────────────────────────────────────────────
Morning:
  Read existing src/api/server_v2.py WebSocket chat endpoint
  Fix any handler bugs (CORS, auth, persona routing)
Afternoon:
  Wire ChatPage.jsx to /ws/chat endpoint instead of POST /chat
  Test all 9 personas through streaming
  Verify token-by-token rendering works
  Handle disconnect gracefully (reconnect logic)


Day 11 — Tests Expansion
─────────────────────────────────────────────
Full day:
  Expand tests/test_api.py from 2 tests → 30+ tests
  Cover:
    auth (login, wrong password, register, get me)         [5 tests]
    chat (basic, persona, streaming)                       [4 tests]
    kpis (get, periods, metrics, by category)              [4 tests]
    insights (health, risk, summary)                       [3 tests]
    forecast (basic, with CI)                              [2 tests]
    ingest (valid, empty, malformed)                       [3 tests]
    rbac (admin works, viewer blocked, scope enforcement)  [4 tests]
    monitoring (stats, knowledge search)                   [3 tests]
    misc (health, root, 404 handler)                       [3 tests]
  Run pytest, fix all failures
  Confirm CI is green on develop branch


Day 12 — Railway Deploy + Smoke Test
─────────────────────────────────────────────
Morning:
  Deploy to Railway (or Fly.io if Railway pricing exceeds budget)
  Configure env vars in Railway dashboard
  Set up Railway PostgreSQL add-on (or Supabase free tier)
  Run db migrations against production DB
Afternoon:
  Smoke test every endpoint in production:
    /health, /api/docs, /auth/login, /chat (with persona),
    /kpis, /insights/health, /forecast, WebSocket /ws/chat
  Document any prod-only failures, fix them
  Note the public URL — this becomes your Upwork demo link
```

**Week 1 checkpoint:**
- [ ] All 4 chart pages use Recharts (no SVG bars left)
- [ ] WebSocket streaming chat works with all 9 personas
- [ ] pytest passes 30+ tests
- [ ] Live production URL exists and responds

#### Week 2 — Demo + Profile + First Proposals

```
Day 13 — README Rewrite + Stale Doc Cleanup
─────────────────────────────────────────────
Morning:
  Rewrite README.md from scratch:
    - One-line description (under 100 chars)
    - "What it does" (3-5 bullets, accurate to actual code)
    - "Quick Start" (3 commands max)
    - "Default Credentials" section (admin/admin → change immediately)
    - Link to /api/docs
    - Architecture diagram (ASCII, 10 lines max)
    - Demo link at the top
    - Total length: < 200 lines
Afternoon:
  Final pass on stale-doc cleanup if anything missed from Week 0
  Update top-level pyproject.toml metadata (author, description, urls)
  Commit and push develop → merge to main
  Tag v0.1.0: git tag v0.1.0 && git push --tags


Day 14 — Loom Demo Recording (3-minute walkthrough)
─────────────────────────────────────────────
Morning:
  Script the demo (write it out, don't ad-lib):
    0:00–0:15  "Hi, I'm Yacine. IntelAI is a multi-persona AI
                analytics platform. Let me show you."
    0:15–0:45  Login → dashboard → switch persona to CFO →
                show financial KPIs scoped to CFO view
    0:45–1:15  Chat with CFO persona → ask "What drove gross margin
                in Q1?" → show streaming token-by-token answer
    1:15–1:45  Switch to RiskPage → show RadarChart of risk components
    1:45–2:15  Switch to ForecastingPage → show AreaChart + CI bands
    2:15–2:45  Highlight: bilingual (toggle FR), 9 personas, role-based
                data scoping
    2:45–3:00  "Demo at <URL>. Repo at <GitHub>. Contact on Upwork."
  Practice once with screen recording but no audio (timing)
  Record final take with audio
Afternoon:
  Upload to Loom (free 5min plan is fine)
  Watch it back — is the audio clear? Pacing? Did everything work?
  Re-record if anything is broken or unclear (don't ship a bad demo)


Day 15 — Pre-Review With 3-5 Trusted Reviewers
─────────────────────────────────────────────
Morning:
  DM the Loom link to 3-5 trusted reviewers:
    - 2 friends who know the field
    - 1-2 peers from Twitter/Discord (DM cold but politely)
    - 1 person outside tech (catches jargon)
  Ask: "60-second feedback. What's confusing? What works? What's missing?"
Afternoon:
  Wait for replies. While waiting:
    - Re-read the demo URL on a phone browser (mobile responsiveness check)
    - Test the demo from incognito (auth flow, no cached state)
    - Run a Lighthouse audit on the frontend (speed, SEO, a11y)
  Collect feedback by evening. Iterate based on common themes.


Day 16 — Iterate Demo + Set Up Upwork Profile
─────────────────────────────────────────────
Morning:
  Apply demo feedback: re-record if structural issues, edit caption
  if minor. Final Loom URL goes in README and Upwork profile.
Afternoon:
  Set up Upwork profile from Section 24:
    - Title: "AI Systems Engineer | RAG · MCP Agents · Document AI · LLMOps · FastAPI"
    - Overview (paste from 24.2, customize for your tone)
    - Skills (paste from 24.3)
    - Hourly rate: $65 (will raise after first 3-5 reviews)
    - Profile photo: professional but not stiff
  Add IntelAI as portfolio entry #1:
    - Title: "IntelAI — AI Analytics with 9 C-Suite Personas"
    - Description: 3 bullets, lead with live demo link
    - 3 screenshots: dashboard, chat, forecasting page


Day 17 — Write 3 Vertical Proposal Templates
─────────────────────────────────────────────
Full day:
  From Section 26, customize Templates 1, 2, 3 for your voice:
    Template 1: For RAG / AI chatbot jobs → leads with IntelAI demo
    Template 2: For FastAPI / backend jobs → leads with API design
    Template 3: For BI / analytics jobs → leads with multi-persona angle
  Each template:
    - Opens with a specific reference to the client's job post
    - Has demo link in the THIRD line, not buried at the bottom
    - Asks 1-2 specific technical questions
    - Closes with clear timeline and rate
  Save them in Notion / a notes app so you can copy/paste fast


Day 18 — First 10 Proposals Sent
─────────────────────────────────────────────
Morning:
  Find 10 strong-fit Upwork jobs (filter: 5+ client reviews, posted
  within 7 days, hourly $30-80, < 30 applicants).
  Distribute across templates:
    4 RAG / chatbot jobs (Template 1)
    3 FastAPI / Python backend jobs (Template 2)
    3 BI / dashboard / KPI jobs (Template 3)
Afternoon:
  Send all 10 with customization per job (don't blast generic).
  Log each in Notion:
    Date, job title, niche, demo link, template used,
    client country, client reviews, expected outcome
  Block calendar for tomorrow: more proposals + start Blog Post 1
```

**Week 2 checkpoint:**
- [ ] Loom demo is recorded, < 3:30, watched by 3+ reviewers
- [ ] Upwork profile is live with IntelAI portfolio entry
- [ ] 10 proposals sent, all logged in Notion

#### Week 3 — Volume Application + Blog Post 1 + PyPI Package

```
Day 19-21 — Daily Proposal Volume (Mon-Wed)
─────────────────────────────────────────────
Each day:
  Morning: send 8-10 proposals (target 30 by end of week)
  Afternoon: monitor replies, respond to invites
            review any rejections — pattern recognition matters here
  Log every proposal. Note response rate by template/niche.

  Side task each afternoon:
    Day 19: Draft Blog Post 1 outline + opening paragraph
            Title candidate: "Persona-Routed RAG: One Retrieval, Nine Personas"
            Sketch 5 sections, 100-word summary of each
    Day 20: Write the first half of the post (~1000 words)
            Focus on: the problem (one-size-fits-all RAG), your solution
            (persona-conditioned prompts + data scoping), the architecture
            diagram, the code skeleton
    Day 21: Write the second half (~1000 words)
            Focus on: real examples from IntelAI (CFO vs CTO query
            differences), evaluation metrics (groundedness shifts per
            persona), what worked, what didn't, future work


Day 22 — Blog Post 1 Reviewer Pass
─────────────────────────────────────────────
Morning:
  Finish blog post draft (~2000 words total)
  Read it aloud once — flag anything that sounds wrong
  Send draft to 2 reviewers (technical peer + writing-strong friend)
Afternoon:
  Apply review feedback
  Add 3-5 code snippets (real code from intelai, not pseudocode)
  Add 1 architecture diagram (ASCII or Excalidraw export)
  Add 1 evaluation table (if you have RAGeval data even minimal)


Day 23 — Finalize Blog Post 1 Draft (NOT PUBLISHED — defer to 2027)
─────────────────────────────────────────────
Morning:
  Save the cleaned draft to: intelai/drafts/blog_post_1_persona_rag.md
  Save a parallel LinkedIn-length draft (300 words) to:
    writing_workspace/linkedin_drafts/post_1_persona_rag_linkedin.md
  Save a Hacker News "Show HN" draft (title + 200-word comment) to:
    writing_workspace/hn_drafts/show_hn_omniintelos.md
  Tag the draft as "v1-pre-ship" — you'll do a finishing pass in
  December 2026 with real-client screenshots before Q1 2027 launch.
  Do NOT publish anywhere public. (See Section 5.1 channel split.)
Afternoon:
  More Upwork proposals (5-10 today)
  Update the intelai GitHub README to reference the live demo
    + link to the Loom video. The README is your public surface in 2026.


Day 24 — Extract omnismart-personas Package
─────────────────────────────────────────────
Morning:
  Create new sub-directory inside intelai: packages/omnismart-personas/
  Or new repo: gh repo create <yourname>/omnismart-personas --public
  Structure:
    omnismart_personas/
      __init__.py
      templates.py  ← PERSONA_TEMPLATES dict (9 personas)
      router.py     ← resolve_persona() function
      context.py    ← PersonaContext dataclass
    pyproject.toml
    README.md       ← clear: "Drop-in 9-persona prompts for any LangChain RAG"
    tests/
      test_templates.py
      test_router.py
  Run pip install -e . locally — verify import works


Day 25 — Publish omnismart-personas to PyPI
─────────────────────────────────────────────
Morning:
  Create PyPI account if you don't have one (verify email)
  Install build tools: pip install build twine
  Build the package: python -m build
  Test upload to test.pypi.org first:
    python -m twine upload --repository testpypi dist/*
  Install from test PyPI in a clean venv — verify it works
Afternoon:
  Upload to real PyPI:
    python -m twine upload dist/*
  Verify: pip install omnismart-personas (in a clean venv anywhere)
  Add the PyPI badge to the package README:
    [![PyPI](https://img.shields.io/pypi/v/omnismart-personas.svg)]
  Tweet/post about it (1 short sentence + link, no hype)


Day 26 — Continue Proposal Volume + Phase 1 Metrics Review
─────────────────────────────────────────────
Morning:
  Send 5-10 more proposals (cumulative target: 50 by Day 27)
Afternoon:
  Phase 1 metrics review:
    - Proposals sent: ___ (target: 50)
    - Replies: ___ (target: 5-10)
    - Interviews: ___ (target: 1-3)
    - Contracts: ___ (target: 0-1)
    - Blog post views: ___ (target: 100-500)
    - PyPI downloads (omnismart-personas): ___
    - GitHub stars (intelai public if it is): ___
  Review the Notion proposal log: which template/niche converts best?


Day 27 — Buffer + Phase 2 Prep
─────────────────────────────────────────────
Morning:
  Fix anything broken from the week (Railway downtime, demo bugs)
  Polish any rough edges in the Loom demo or README
Afternoon:
  Open the docintel/ repo (created Week 0)
  Read its STATUS.md (you wrote this Day 4 of Week 0)
  Write a Phase 2 TODO.md inside docintel/
  Confirm sample invoices are ready: enhanced_synthetic_dataset/pdf/
    has 3 PDFs (insufficient — you'll need 50 for eval, plan for it)
  Pre-stage 50 invoice sources for Day 30:
    - Open government datasets (data.gov, eu-data-portal)
    - Public invoice samples (Stripe, Square, online templates)
    - 10-15 from your own synthetic dataset
  Save links in docintel/eval_sources.md
```

**Phase 1 final checkpoint (end of Week 3):**
```
DELIVERABLE                                                 STATUS
─────────────────────────────────────────────────────────────────
IntelAI deployed at public URL                           [ ]
4 chart pages use Recharts                                   [ ]
WebSocket streaming chat working                             [ ]
30+ pytest tests passing                                     [ ]
README rewritten, < 200 lines                                [ ]
Loom demo recorded, pre-reviewed                             [ ]
Upwork profile live with IntelAI portfolio              [ ]
50 proposals sent, all logged                                [ ]
Blog Post 1 DRAFTED + saved to drafts/ (defer publishing to Q1 2027)  [ ]
omnismart-personas published to PyPI                         [ ]
0-3 client interviews secured                                [ ]
```

If 50 proposals → 0 replies, **stop. Do not start Phase 2.** Spend Day 27-28
diagnosing: is the demo broken? Is the proposal generic? Is the niche wrong?
Get external review before proceeding.

---

### 16.3 Phase 2 — DocIntel (Weeks 4–6)

**Goal:** Second portfolio entry live. Validates the OCR/document AI freelance
niche. PyPI / DockerHub artifact published. Blog Post 2 live. 30 OCR-niche
proposals sent.

#### Week 4 — Core Build (API + LLM Extractor + Batch)

```
Day 28 — Verify Extracted Repo + Build api.py
─────────────────────────────────────────────
Morning:
  cd docintel
  source .venv/bin/activate
  Re-read STATUS.md (written Week 0 Day 4) — refresh memory
  Run pytest tests/ — confirm baseline passes
Afternoon:
  Build api.py (FastAPI app) with endpoints:
    GET  /health
    POST /process (file upload → full pipeline)
    POST /classify (file → doc_type only)
    POST /extract-tables (PDF file → tables list)
    POST /extract-llm (text + doc_type → structured dict via LLM)
    POST /batch/upload (list of files → job_id)
    GET  /batch/{job_id} (status)
    GET  /batch/{job_id}/results
  Define ProcessResponse Pydantic model
  Serve demo/ as static files at /demo
  Local smoke test: uvicorn api:app and curl each endpoint with a sample PDF


Day 29 — Build services/llm_extractor.py
─────────────────────────────────────────────
Morning:
  Create services/llm_extractor.py
  Implement LLMExtractor class with async extract(text, doc_type) method
  Prompts for doc types:
    - invoice: fields = [vendor, invoice_number, date, due_date,
                          line_items, subtotal, tax, total, currency]
    - contract: fields = [parties, effective_date, expiration_date,
                          payment_terms, jurisdiction, key_clauses]
    - receipt: fields = [merchant, date, total, currency, items, payment_method]
    - financial_report: fields = [period, revenue, cogs, opex, ebitda,
                                   net_income, key_metrics_summary]
    - default: extract any structured info as flexible JSON
  Each prompt requests JSON output, temperature=0.1
  Strip markdown fences from response before json.loads
Afternoon:
  Wire LLMExtractor into api.py's /extract-llm and /process endpoints
  Test with 3-5 real PDFs from your enhanced_synthetic_dataset
  Note any obvious failures — these become eval items in Week 5


Day 30 — Build services/batch_processor.py + Demo UI
─────────────────────────────────────────────
Morning:
  Create services/batch_processor.py
  BatchProcessor class:
    process(job_id, file_data_list) → background task
    get_status(job_id) → {status, total, processed, failed, percent}
    get_results(job_id) → list of processed results
  In-memory dict for job tracking (sufficient for demo)
  Wire into api.py's /batch/* endpoints
  Test with 5-document batch
Afternoon:
  Build demo/index.html — single-page drag-and-drop demo:
    Dark theme (#0f172a background)
    Drop zone + file input
    On drop: POST /process, show spinner
    On response: show doc_type badge, confidence, processing time,
                  structured JSON output (pretty-printed)
    Pure vanilla JS (no framework), ~150 lines
  Manual test: drag 3 different PDFs, verify each renders correctly


Day 31 — Polish + Local End-to-End
─────────────────────────────────────────────
Morning:
  Run a full local end-to-end:
    Upload via demo UI → process pipeline → LLM extract → render JSON
    Time: aim for <5 seconds per document (your premium positioning)
  Profile the slow spots (likely Tesseract OCR or LLM call)
Afternoon:
  Add response caching for repeat documents (hash file → check cache)
  Add request logging (every /process call logged to a file or DB)
  Confirm Dockerfile builds cleanly: docker build -t docintel:dev .


Day 32 — Tests + CI
─────────────────────────────────────────────
Full day:
  Expand tests/:
    test_api.py: 8 tests for /health, /classify, /process, /batch/*
    test_extractor.py: 5 tests for each doc_type
    test_batch.py: 3 tests for batch lifecycle (upload, status, results)
    test_demo.py: 1 smoke test that /demo serves the HTML
  Use fixtures: include 5 small test PDFs in tests/fixtures/
  Run pytest, fix failures
  CI green on develop branch
```

**Week 4 checkpoint:**
- [ ] api.py exposes all 7 endpoints, all returning 2xx for valid inputs
- [ ] LLMExtractor handles 4 doc types with reasonable JSON output
- [ ] BatchProcessor handles a 5-document batch end-to-end
- [ ] Drag-and-drop demo works locally with 3+ test PDFs
- [ ] pytest passes 15+ tests
- [ ] Docker build succeeds

#### Week 5 — Eval Dataset + Prompt Iteration

This is the most important week of Phase 2. Skipping or shortcutting it
produces a demo that looks good but fails when a real client uploads their
actual invoices. Budget 5 full days for prompt iteration. Do not compress.

```
Day 33 — Collect 50 Real Invoices (Eval Set)
─────────────────────────────────────────────
Full day, focused task:
  Source 50 diverse invoices:
    - 15 from open government datasets (data.gov procurement records,
      eu-data-portal vendor invoices)
    - 15 from public invoice samples (online templates, Stripe sample,
      Square sample, QuickBooks examples)
    - 10 from your enhanced_synthetic_dataset (already have these)
    - 10 anonymized real-world ones (ask 5 friends for blanked invoices
      from their companies — explicitly anonymized)
  Store all 50 in docintel/eval/invoices/ as PDFs (numbered 01-50)
  Create docintel/eval/invoice_eval.jsonl with expected JSON for each
  Each line: {"file": "01.pdf", "expected": {...fields...}}
  Time investment: 4-6 hours for collection, 2-3 hours for hand-labeling
  This is the dataset that earns your $65/hr rate.


Day 34 — Initial Eval Run
─────────────────────────────────────────────
Morning:
  Write docintel/eval/run_eval.py:
    For each row in invoice_eval.jsonl:
      result = await llm_extractor.extract(text, "invoice")
      compare result vs expected (per-field accuracy)
      log: filename, accuracy_per_field, hallucinations, missing_fields
    Output: docintel/eval/results_v1.json
Afternoon:
  Run the eval. Look at the numbers:
    - Vendor name accuracy: ___%
    - Total amount accuracy: ___%
    - Date accuracy: ___%
    - Line items accuracy: ___%
  Baseline target: 60-75% on first run is typical. Below 60% means
  the prompt has a structural problem.
  Top failure modes (rank by frequency):
    1. ___
    2. ___
    3. ___


Day 35 — Prompt Iteration Round 1
─────────────────────────────────────────────
Morning:
  Pick the worst-performing field. Rewrite the relevant prompt section
  to be more specific. Examples:
    - If line items fail: add "extract every row, even single-line items"
    - If totals fail: add "the total is the largest currency amount;
                      if multiple totals, prefer the one labeled 'Total'"
    - If dates fail: specify expected format (ISO YYYY-MM-DD)
  Re-run eval.
  Track delta: did this field improve? Did others regress?
Afternoon:
  Pick next worst field. Iterate.
  Document each prompt change with a 1-line rationale (what you saw,
    what you changed, the result).
  Target by end of day: top-3 fields at 80%+


Day 36 — Prompt Iteration Round 2 + Few-Shot
─────────────────────────────────────────────
Morning:
  Add 1-2 few-shot examples to the invoice prompt
    (1 simple US invoice, 1 European-format invoice)
  Re-run eval. Few-shot usually moves the needle 5-15% on tough fields.
Afternoon:
  Consider switching extraction strategy for specific fields:
    - For dates: post-process with dateparser library (more reliable
      than LLM for date normalization)
    - For totals: regex over OCR'd text as fallback if LLM returns null
    - For line items: try JSON-mode (if Groq model supports it) or
      function-calling format
  Re-run eval. Document which fields are now LLM-only vs hybrid.


Day 37 — Prompt Iteration Round 3 + Failure Mode Documentation
─────────────────────────────────────────────
Morning:
  Final prompt iteration: target 85%+ overall accuracy on key fields
    (vendor, total, date, currency).
  Other fields (line items, tax breakdown) can be lower; document this
  in the README as known limitations.
Afternoon:
  Write docintel/README.md "Known Limitations" section:
    - "Handwritten invoices: not supported (use external OCR)"
    - "Receipts with tip lines: tip amount sometimes misclassified
      into subtotal — manual review recommended for high-value receipts"
    - "Foreign currencies: works for USD, EUR, GBP, JPY; others may
      require config update"
    - "Multi-page invoices: only first page processed (Phase 2.1 work)"
  Honesty in the README earns trust faster than overclaiming.
  Final eval pass — record the actual numbers. Use them in the blog post.
```

**Week 5 checkpoint:**
- [ ] 50-invoice eval set exists and is hand-labeled
- [ ] Key field accuracy (vendor, total, date) is 85%+
- [ ] Prompt iteration log documents each change and its delta
- [ ] README has honest "Known Limitations" section
- [ ] You have numbers to put in Blog Post 2 (this is your credibility moat)

#### Week 6 — Ship + Blog Post 2 + OCR-Niche Proposals

```
Day 38 — Deploy DocIntel + Demo Recording
─────────────────────────────────────────────
Morning:
  Deploy DocIntel to Railway or Fly.io
    (Tesseract install in Dockerfile may surprise you — test on Day 33!)
  Configure GROQ_API_KEY env var
  Smoke test all endpoints in production
Afternoon:
  Record 90-second Loom demo:
    0:00–0:10  "DocIntel — drag a PDF, get structured JSON in <1 second."
    0:10–0:30  Drag a sample invoice → show doc_type badge, confidence
    0:30–0:50  Drag a contract → show different schema extracted
    0:50–1:10  Show the eval metrics: 85% accuracy on 50-invoice test
    1:10–1:30  "Self-hosted, $20/mo to run. Open source on GitHub."
  Pre-review with 3 reviewers before finalizing


Day 39 — Publish to DockerHub + GitHub Public
─────────────────────────────────────────────
Morning:
  Build and push Docker image:
    docker build -t <yourname>/docintel:latest -t <yourname>/docintel:0.1.0 .
    docker push <yourname>/docintel:latest
    docker push <yourname>/docintel:0.1.0
  Verify pullable from anywhere: docker pull <yourname>/docintel:latest
Afternoon:
  Make GitHub repo public:
    gh repo edit <yourname>/docintel --visibility public
  Polish README:
    - Title + one-line description
    - Live demo link (Railway URL)
    - "What it does" (3 bullets, accurate)
    - Quick Start (3 commands)
    - Architecture diagram (ASCII)
    - Eval numbers (from Week 5)
    - Known Limitations (from Day 37)
  Tag v0.1.0: git tag v0.1.0 && git push --tags


Day 40 — Add DocIntel to Upwork Portfolio + OCR Proposals
─────────────────────────────────────────────
Morning:
  Add DocIntel as Upwork portfolio entry #2:
    - Title: "DocIntel — PDF & Invoice AI Pipeline"
    - 3 screenshots: drag-drop demo, JSON output, eval results
    - Description: "PDF → classified + structured JSON in <1 sec.
                    85% accuracy on real invoices. Self-hosted."
  Customize Section 26 Template 3 for OCR/document AI jobs
Afternoon:
  Send 10 OCR-niche proposals:
    Filter Upwork for: "OCR" "invoice extraction" "document AI"
                       "PDF processing" "intelligent document"
  Lead with the DocIntel demo + the 85% accuracy stat
  Log each in Notion


Day 41 — Blog Post 2 Draft
─────────────────────────────────────────────
Full day:
  Title: "LLM-Enhanced OCR: Beyond Tesseract"
  Outline (5 sections, ~400 words each = ~2000 total):
    1. The problem: traditional OCR gives you text, not data.
       Real-world need: structured fields with provenance.
    2. The architecture: file → classifier → OCR/text → LLM extract → JSON
       (with diagram)
    3. Prompt engineering for invoice extraction:
       - JSON-mode requests, temperature 0.1, few-shot examples
       - When LLM is unreliable (dates, multi-currency)
       - Hybrid approaches (regex + LLM)
    4. Building an eval set: 50 invoices, hand-labeled
       Show actual numbers per field
    5. Production reality: latency, cost, error modes
       Honest limitations + when to fall back to human review
  Include 3-5 code snippets (real LLMExtractor code)
  Include the eval results table


Day 42 — Blog Post 2 Polish + Save Draft (NOT PUBLISHED in 2026)
─────────────────────────────────────────────
Morning:
  Send draft to 2 reviewers (peers, not publication)
  Apply feedback
Afternoon:
  Save final draft to: docintel/drafts/blog_post_2_vision_first_doc_ai.md
  Save parallel LinkedIn draft to: writing_workspace/linkedin_drafts/
  Save Reddit r/MachineLearning draft (methodology-led) to: writing_workspace/reddit_drafts/
  Save Show HN draft to: writing_workspace/hn_drafts/
  Save the eval methodology + numbers section verbatim — this is the
    research-credential ammunition for the 2027 arXiv preprint.
  Do NOT publish anywhere public in 2026. (Section 5.1)


Day 43 — Phase 2 Metrics Review + Phase 3 Prep
─────────────────────────────────────────────
Morning:
  Phase 2 metrics:
    - DocIntel deployed and accessible: ___
    - Eval accuracy: ___%
    - 10 OCR proposals sent: ___
    - Blog Post 2 views: ___
    - DockerHub pulls: ___
    - GitHub stars: ___
    - Phase 1+2 cumulative interviews: ___
    - Phase 1+2 cumulative contracts: ___
Afternoon:
  Open agentkit/ — re-read STATUS.md from Week 0 Day 4
  Write Phase 3 TODO.md in agentkit/
  Confirm fastmcp is in requirements.txt (was installed Week 0?)
  Pre-stage MCP testing: install Claude Desktop locally if not already


Day 44 — Buffer + Continue Volume
─────────────────────────────────────────────
Morning:
  Fix anything broken from the week
  Continue OCR proposal volume (10 more today, cumulative 20+)
Afternoon:
  Send 5 proposals on IntelAI-niche jobs (don't abandon Phase 1
    niches just because Phase 2 shipped)
  Plan Phase 3: when does Phase 3 Day 1 start?
```

**Phase 2 final checkpoint:**
```
DELIVERABLE                                                 STATUS
─────────────────────────────────────────────────────────────────
DocIntel deployed at public URL                              [ ]
50-invoice eval set, 85%+ key-field accuracy                 [ ]
Demo recorded, README accurate                               [ ]
GitHub repo public                                           [ ]
DockerHub image published                                    [ ]
Blog Post 2 DRAFTED + fact-checked (defer publishing to Q1 2027) [ ]
Upwork portfolio entry #2 added                              [ ]
30+ OCR-niche proposals sent                                 [ ]
Cumulative interviews (Phases 1-2): 2-5                      [ ]
Cumulative contracts (Phases 1-2): 1-3                       [ ]
```

If OCR-niche conversion is poor (0 interviews after 30 proposals), revisit
the demo. Test it from a hiring manager's perspective: do they see the eval
numbers in the first 30 seconds? Is the file-upload flow obvious?

---

### 16.4 Phase 3 — AgentKit (Weeks 7–9)

**Goal:** Open-source MCP server published with traction. Third blog post.
GitHub stars (10+). MCP-niche proposals on Upwork.

This phase is your **open-source primary** project. Freelance is secondary;
the win is GitHub stars, community recognition, and cold-email leverage.

#### Week 7 — MCP Server Build (6 Tools)

```
Day 45 — Verify Extracted Repo + Install fastmcp
─────────────────────────────────────────────
Morning:
  cd agentkit
  source .venv/bin/activate
  Read STATUS.md (Week 0)
  pip install fastmcp (>= 0.4.0)
  Verify install: python -c "from fastmcp import FastMCP"
Afternoon:
  Read FastMCP docs (15 minutes): https://github.com/jlowin/fastmcp
  Build mcp_server.py skeleton:
    mcp = FastMCP("AgentKit Business Intelligence")
    @mcp.tool() async def query_kpis(...): ...
    @mcp.tool() async def get_company_health(...): ...
    ... (6 tools total, per Section 30 / PROJECT 2)
    if __name__ == "__main__": mcp.run()


Day 46 — Implement Tools 1-3
─────────────────────────────────────────────
Morning:
  Tool 1: query_kpis(domain, period_from, period_to, metric_filter, limit)
    Calls services.pg_store.get_kpi_metrics(category=domain)
    Filters by period and metric_filter
    Returns dict: {kpis: [...], total: N}
  Tool 2: get_company_health(domain=None)
    Calls get_kpi_metrics(), compute_health_index() (from insights.py)
    Returns: {score: 0.78, interpretation: "Healthy", components: {...}}
Afternoon:
  Tool 3: detect_kpi_anomalies(domain, method="zscore", threshold=2.5)
    Calls get_kpi_metrics(category=domain) and detect_anomalies(df, method=method)
    Returns: {anomalies: [...], total: N, threshold: 2.5}
  Test each tool in isolation via REPL:
    python -c "import asyncio; from mcp_server import query_kpis;
               print(asyncio.run(query_kpis('Finance')))"


Day 47 — Implement Tools 4-6
─────────────────────────────────────────────
Morning:
  Tool 4: forecast_metric(metric_name, periods=6, confidence_level=0.95)
    Finds metric in get_kpi_metrics(), calls ForecastEngine().time_series_forecast()
    Returns: {forecast: [...], upper_ci: [...], lower_ci: [...], method: "..."}
  Tool 5: list_available_metrics(domain=None)
    Calls get_available_metrics(), get_available_categories(), get_available_periods()
    Returns: {metrics: [...], categories: [...], periods: [...]}
Afternoon:
  Tool 6: get_executive_summary()
    Calls get_kpi_metrics(), compute_health_index()
    Synthesizes into a dict: {summary, health_score, key_metrics, anomalies, top_growth}
  Run mcp_server.py — confirm server starts and lists 6 tools


Day 48 — Connect to Claude Desktop Locally
─────────────────────────────────────────────
Morning:
  Open Claude Desktop config file (~/.config/Claude/claude_desktop_config.json
    on Linux, or equivalent on Mac/Windows)
  Add AgentKit MCP server:
    {
      "mcpServers": {
        "agentkit": {
          "command": "python",
          "args": ["/path/to/agentkit/mcp_server.py"],
          "env": { "POSTGRES_URL": "postgresql://...",
                   "GROQ_API_KEY": "gsk_..." }
        }
      }
    }
  Restart Claude Desktop
  Verify: Claude sees the 6 tools (look for the MCP indicator in UI)
Afternoon:
  Test through Claude:
    "What's our company health right now?" → should trigger get_company_health
    "Forecast revenue for next 6 months" → should trigger forecast_metric
    "Are there any anomalies in the Finance KPIs?" → detect_kpi_anomalies
  Note any tool that doesn't trigger correctly. Could be tool description
  unclear → improve docstring → re-test.


Day 49 — Tests + Fix Bugs
─────────────────────────────────────────────
Full day:
  Write tests/test_mcp_tools.py:
    1 test per tool (6 tests minimum)
    Mock pg_store / insights / forecasting if DB not available
    Include edge cases: empty data, invalid domain, large datasets
  Run pytest, fix failures
  CI green on develop branch
```

**Week 7 checkpoint:**
- [ ] mcp_server.py exposes all 6 tools
- [ ] Claude Desktop sees and triggers each tool
- [ ] pytest passes 10+ tests
- [ ] Tool descriptions are clear enough that Claude routes correctly

#### Week 8 — LangGraph Workflow (3 Agents)

```
Day 50 — Install LangGraph + Build Planner Agent
─────────────────────────────────────────────
Morning:
  pip install langgraph langchain-groq langchain
  Verify: python -c "from langgraph.graph import StateGraph"
  Create workflow.py:
    Define BusinessAnalysisState (TypedDict):
      question: str
      plan: str
      tool_calls: list[dict]
      raw_data: dict
      report: str
      report_sections: dict
      error: Optional[str]
Afternoon:
  Implement planner_agent(state):
    Uses ChatGroq (model="llama-3.1-70b-versatile", temp=0.3)
    System prompt: "You are a planner. Given a business question, produce
                    a 3-4 step analysis plan using available tools..."
    Calls list_available_metrics() to know what's available
    Returns state with state["plan"] populated
  Test in isolation: run planner_agent on 3 sample questions


Day 51 — Build Analyst Agent
─────────────────────────────────────────────
Full day:
  Implement analyst_agent(state):
    Reads state["question"] and state["plan"]
    Routes to relevant MCP tools based on keywords:
      "Finance" / "revenue" / "margin" → query_kpis("Finance")
                                          + detect_kpi_anomalies("Finance")
      "People" / "HR" / "headcount" → query_kpis("People")
      "Growth" / "customer" / "MRR" → query_kpis("Growth")
      Always also call: get_company_health() + get_executive_summary()
    Aggregates results into state["raw_data"]
    Returns state
  Test: run planner → analyst on the 3 sample questions
        Inspect state["raw_data"] — does it contain the right slices?


Day 52 — Build Reporter Agent
─────────────────────────────────────────────
Full day:
  Implement reporter_agent(state):
    Uses ChatGroq with temp=0.2
    System prompt: "You synthesize raw data into executive reports
                    with these sections: KEY FINDING, EVIDENCE,
                    ROOT CAUSE, RECOMMENDED ACTION, RISK IF UNADDRESSED"
    Input: state["question"], state["plan"], state["raw_data"]
    Parses response into state["report_sections"]
    Returns state with state["report"] and state["report_sections"]
  Test: run full chain on 3 questions, inspect final reports.
        Quality check: are sections logical? Do recommendations
        actually follow from the evidence? If weak, iterate prompts.


Day 53 — Wire StateGraph + Public API
─────────────────────────────────────────────
Morning:
  Build the LangGraph StateGraph in workflow.py:
    graph = StateGraph(BusinessAnalysisState)
    graph.add_node("planner", planner_agent)
    graph.add_node("analyst", analyst_agent)
    graph.add_node("reporter", reporter_agent)
    graph.set_entry_point("planner")
    graph.add_edge("planner", "analyst")
    graph.add_edge("analyst", "reporter")
    graph.add_edge("reporter", END)
    app = graph.compile()
  Public API: def analyze(question: str) -> dict:
                final = app.invoke({"question": question, ...})
                return final
Afternoon:
  Test analyze() on 5 different business questions:
    "What drove gross margin in Q1?"
    "Are there hiring anomalies in the People domain?"
    "Forecast revenue and growth for next quarter."
    "What's our biggest risk right now?"
    "Summarize the company's overall financial health."
  Time each call (should be 5-15 seconds total)


Day 54 — Demo Notebooks + Fixes
─────────────────────────────────────────────
Morning:
  Create demos/claude_desktop_demo.ipynb:
    Markdown cells explaining MCP setup
    Screenshots of Claude Desktop UI showing tool calls
    Example queries + responses
  Create demos/langgraph_workflow_demo.ipynb:
    Code cells running analyze() on different questions
    Display state["plan"], state["raw_data"] (truncated), state["report"]
    Markdown commentary on each
Afternoon:
  Polish workflow.py based on what you noticed running 5 test questions
  Add error handling: if any agent throws, populate state["error"]
                      gracefully and return partial results
  Run final test pass — 5 questions, 5 clean reports
```

**Week 8 checkpoint:**
- [ ] workflow.py runs 3-agent chain end-to-end
- [ ] analyze() returns coherent reports for 5+ different questions
- [ ] Two demo notebooks exist
- [ ] Latency is acceptable (<20s per analyze call)

#### Week 9 — Distribution + Community + Blog Post 3

```
Day 55 — README + Demo Video
─────────────────────────────────────────────
Morning:
  Write agentkit/README.md:
    Title: "AgentKit — MCP Server for Business Intelligence Agents"
    Hero: Claude Desktop screenshot showing tool list
    Sections:
      - What It Does (2-3 sentences)
      - Tools Exposed (table: tool name, params, returns)
      - Quick Start (pip install -r requirements.txt && python mcp_server.py)
      - Claude Desktop Setup (JSON config snippet)
      - LangGraph Workflow (when to use vs MCP)
      - Architecture (ASCII diagram)
      - Roadmap (future tools)
Afternoon:
  Record 90-second demo:
    0:00–0:15  Show Claude Desktop with AgentKit tools listed
    0:15–0:45  Ask Claude a business question → watch it call 3 tools
    0:45–1:15  Show the LangGraph workflow output (richer report)
    1:15–1:30  "Open source, MIT license. Link in description."
  Pre-review with 2-3 MCP-aware reviewers (DM Anthropic Discord folks)


Day 56 — Make Public + Submit to Lists
─────────────────────────────────────────────
Morning:
  gh repo edit <yourname>/agentkit --visibility public
  Tag v0.1.0: git tag v0.1.0 && git push --tags
  Add LICENSE (MIT) file
  Add CODE_OF_CONDUCT.md (use GitHub's standard template)
  Add CONTRIBUTING.md (simple: how to add a tool)
Afternoon:
  Submit to awesome-mcp listings:
    - github.com/punkpeye/awesome-mcp-servers
    - github.com/wong2/awesome-mcp-servers
    - Any other lists you find (search GitHub for "awesome-mcp")
  Submit a PR to each — they usually merge fast


Day 57 — Community Posts
─────────────────────────────────────────────
Morning:
  Anthropic Discord (#mcp channel): share repo with 2-3 lines:
    "AgentKit — MCP server exposing business analytics (KPIs, health
    score, forecasting, anomalies). 6 tools, works with Claude Desktop,
    Cursor, and LangChain agents. Open source: [link]"
  MCP-related Discords: similar message
Afternoon:
  r/LocalLLaMA post (be useful, not promo):
    Title: "Built an MCP server that lets Claude do business KPI analysis
            — 6 tools, open source"
    Body: 2 paragraphs explaining the use case and architecture,
          link to repo, link to demo video
  Respond to comments throughout the day


Day 58 — Blog Post 3 Draft
─────────────────────────────────────────────
Full day:
  Title: "MCP Tool Design Patterns: From Database to AI Agent in 6 Tools"
  Outline:
    1. What MCP is, briefly (1 paragraph for newcomers)
    2. The 6 tools I built and why each one exists
    3. Tool description as the entire UX:
       - Why "query_kpis" works but "get_data" doesn't
       - Parameter naming for LLM clarity
       - Returning structured data with metadata
    4. Composability: why agentic workflows beat single tool calls
       (show LangGraph workflow example)
    5. What I'd build next (roadmap = invitation for contributors)
  Include 5-7 code snippets (real fastmcp decorators)
  Include the LangGraph state diagram


Day 59 — Blog Post 3 Polish + Save Draft (NOT PUBLISHED in 2026)
─────────────────────────────────────────────
Morning:
  Send draft to 2 reviewers (1 MCP person, 1 tech-writing person)
  Apply feedback
Afternoon:
  Save final draft to: agentkit/drafts/blog_post_3_mcp_patterns.md
  Save Hacker News "Show HN" draft to: writing_workspace/hn_drafts/
    Title pre-written: "MCP Tool Design Patterns: From Database to AI Agent (6 tools)"
  Save Reddit /r/LocalLLaMA + /r/MachineLearning drafts to: writing_workspace/reddit_drafts/
  Save LinkedIn cornerstone-supporting draft to: writing_workspace/linkedin_drafts/
  Do NOT publish anywhere public. (Section 5.1)
  In Q1 2027 these all go live in one coordinated launch sequence.


Day 60 — MCP Proposals + Continue Volume
─────────────────────────────────────────────
Morning:
  Search Upwork for: "MCP" "Model Context Protocol" "AI agent"
                     "agentic AI" "LangGraph" "tool use"
  Send 5-10 MCP-specific proposals (Section 26 Template 2)
  Lead with AgentKit GitHub link + Claude Desktop demo
Afternoon:
  Continue IntelAI + DocIntel niche proposals (5-10 today)
  Phase 3 metrics review:
    - AgentKit GitHub stars: ___ (target: 10+)
    - Demo video views: ___
    - Blog Post 3 traction: ___ HN points, ___ Medium claps
    - MCP-niche proposals sent: ___
    - Cold-email-worthy inbound DMs from blog/HN: ___
    - Phase 1-3 cumulative interviews: ___
    - Phase 1-3 cumulative contracts: ___


Day 61 — Buffer + Phase 4 Prep
─────────────────────────────────────────────
Morning:
  Fix anything broken from the week
  Respond to GitHub issues if AgentKit got some (this builds community)
Afternoon:
  Open voiceflow/ repo — re-read STATUS.md
  Verify Whisper / faster-whisper installs cleanly (this is the
    notorious dependency-hell project — pre-test now, not Day 1)
  Write Phase 4 TODO.md in voiceflow/
  Pre-stage audio test data:
    - 2-3 short meeting recordings (yours or public domain podcasts)
    - 1-2 sales call audio (use public sales-call YouTube samples)
```

**Phase 3 final checkpoint:**
```
DELIVERABLE                                                 STATUS
─────────────────────────────────────────────────────────────────
AgentKit public on GitHub                                    [ ]
6 MCP tools working with Claude Desktop                      [ ]
LangGraph 3-agent workflow operational                       [ ]
Demo video recorded                                          [ ]
Submitted to awesome-mcp lists                               [ ]
Posted in Anthropic Discord + MCP communities                [ ]
Blog Post 3 DRAFTED + HN/Reddit drafts saved (defer publishing to Q1 2027) [ ]
10+ GitHub stars                                             [ ]
10+ MCP-niche proposals sent                                 [ ]
Phase 1-3 cumulative: 2-5 contracts, $5-15k earned           [ ]
```

If AgentKit got 0 GitHub stars and 0 community traction after 5 days
public, the issue is usually one of:
  1. README isn't clear about what it does
  2. Demo video buried (should be in the very first README line)
  3. Posted at the wrong time (HN US-morning, Discord during EU hours)

Spend Day 61 diagnosing if traction is zero.

---

### 16.5 Phase 4 — VoiceFlow (Weeks 10–12)

**Goal:** Voice-to-intelligence portfolio entry. Recording demo is unique
and memorable. Meeting analyzer / sales-call analyzer differentiates from
generic transcription wrappers.

This is your "browser-recording-demo" project. Visual impact is high.
A client clicks the demo, records 10 seconds of themselves talking, and
sees structured notes appear. That moment is the sale.

#### Week 10 — Voice Service + Meeting Analyzer

```
Day 62 — Verify Whisper Install + Voice Service
─────────────────────────────────────────────
Morning:
  cd voiceflow
  source .venv/bin/activate
  Re-read STATUS.md
  pip install -r requirements.txt  (includes faster-whisper)
  python -c "from faster_whisper import WhisperModel; print('OK')"
  Download the base model: WhisperModel("base", device="cpu", compute_type="int8")
    (This downloads ~150MB on first use. Note the cache location.)
Afternoon:
  Test transcribe on a 30-second audio sample:
    from faster_whisper import WhisperModel
    model = WhisperModel("base")
    segments, info = model.transcribe("sample.mp3")
    for seg in segments: print(seg.text)
  Measure latency. Aim for <2x realtime (30s audio → <60s transcribe).
  If latency is bad: try "tiny" model first; consider GPU for production.


Day 63 — Build services/voice_service.py
─────────────────────────────────────────────
Full day:
  Implement services/voice_service.py:
    transcribe_audio(audio_bytes, language="auto") → dict
      Returns: {text, language, latency_seconds, method, segments}
      Method = "faster-whisper" (Groq Whisper as fallback if API key set)
    detect_language(audio_bytes) → str
    Optional: speaker_diarization (pyannote if available, fallback to None)
      Document the fallback clearly — pyannote install is notoriously fragile
  Test on 3 audio samples (English, French, mixed)


Day 64 — Build services/meeting_analyzer.py
─────────────────────────────────────────────
Full day:
  Implement services/meeting_analyzer.py with MeetingAnalyzer class:
    analyze_meeting(transcript) → structured dict with:
      meeting_summary (3-5 sentences)
      duration_minutes (estimated from word count if not provided)
      participants_mentioned (list)
      decisions (list of strings)
      action_items: [{owner, action, due, priority}]
      key_numbers (any quoted figures: $50k, 30%, Q2 2026, etc.)
      open_questions (list)
      next_steps (list)
      sentiment ("positive" | "neutral" | "tense" | "mixed")
      topics_covered (list)
    analyze_sales_call(transcript) → structured dict with:
      call_summary
      prospect_company, prospect_contact, prospect_role
      pain_points (list)
      objections: [{type, content}]
      buying_signals (list)
      budget_mentioned (string or null)
      deal_stage ("discovery" | "evaluation" | "negotiation" | "closing")
      crm_notes (formatted for Salesforce/HubSpot paste)
      overall_sentiment, likelihood_to_close (0-1)
    general_analysis(transcript) → structured dict
  All methods call Groq API, temperature=0.2, return parsed JSON
  Test on 3 sample transcripts (use your meeting recordings → voice_service)


Day 65 — Build api.py
─────────────────────────────────────────────
Morning:
  Implement api.py endpoints:
    GET  /health
    POST /transcribe (audio file → {text, language, latency, method})
    POST /tts (text + language → audio/mpeg streaming)
    POST /analyze (JSON: {text, analysis_type} → dict)
    POST /pipeline (audio file + analysis_type → transcribe + analyze)
    POST /meeting/process (audio file → meeting notes JSON)
    POST /call/analyze (audio file → sales call JSON)
    WS   /stream (optional: WebSocket streaming transcription)
  Serve demo/ at /demo
Afternoon:
  Wire TTS service from services/tts_service.py (edge-tts)
  Test /tts: curl with text → should return audio bytes
  Test /pipeline: upload meeting.mp3 with analysis_type=meeting → full output


Day 66 — Test + Polish
─────────────────────────────────────────────
Full day:
  Tests:
    test_voice.py: 4 tests (transcribe, language detect, edge cases)
    test_analyzer.py: 6 tests (meeting, sales, general, edge)
    test_api.py: 5 tests (all endpoints)
    test_pipeline.py: 2 end-to-end tests
  Run pytest, fix failures
  Polish: error handling for unsupported audio formats
  Confirm Dockerfile builds (Whisper model bundled or downloaded at start?)
```

**Week 10 checkpoint:**
- [ ] Whisper transcription works on 3 test files
- [ ] MeetingAnalyzer + SalesCallAnalyzer return well-structured JSON
- [ ] All 7 endpoints respond correctly
- [ ] Tests pass

#### Week 11 — Browser Recording Demo + Deploy

```
Day 67 — Build demo/record.html
─────────────────────────────────────────────
Full day:
  Single-page browser recording demo (~200 lines vanilla JS):
    Dark theme (#0f172a background)
    "Click to record" button (idle: purple, recording: red pulsing)
    Uses MediaRecorder API to capture microphone audio
    On stop: sends audio blob to /transcribe via fetch
    Displays transcript with fade-in animation
    Then auto-calls /analyze with selected analysis_type (radio buttons:
      Meeting / Sales Call / General)
    Displays structured JSON with syntax highlighting
    Final UI: transcript on left, JSON on right
  Mobile responsive (works on phone browsers)
  Test in Chrome, Firefox, Safari


Day 68 — Visual Polish + UX
─────────────────────────────────────────────
Morning:
  Add a 3-second countdown when user clicks record (reduces awkward pause)
  Add a waveform visualization while recording (Web Audio API)
  Add a "stop and analyze" button that's prominent
Afternoon:
  Add 3 sample audio buttons ("Try with sample meeting", "Try with sample
    sales call", "Try with sample interview") for users who can't or
    don't want to record their own audio
  Test on real users (DM 3 friends, ask them to try it for 60 seconds)
  Iterate based on what was confusing


Day 69 — Deploy
─────────────────────────────────────────────
Full day:
  Deploy VoiceFlow to Railway or Fly.io
  IMPORTANT: Whisper model downloads on first container start. Pre-bake
    it into the Docker image, OR have it download to a persistent volume.
    Cold-start without pre-baked model = 60+ seconds, will tank demos.
  Test thoroughly in production:
    - Record from production URL with Chrome
    - Verify transcription works (Whisper alive in container)
    - Verify analysis works (Groq API key configured)
  Document any production-only failures, fix them


Day 70 — Demo Video + Pre-Review
─────────────────────────────────────────────
Morning:
  Record 90-second Loom demo:
    0:00–0:10  "VoiceFlow — speech to structured intelligence."
    0:10–0:30  Click record, talk: "Let's discuss the Q2 launch.
                 Alice will own the marketing campaign, due May 15..."
    0:30–0:50  Stop → show transcript appearing → show JSON output:
                 action items, owner=Alice, due=2026-05-15, etc.
    0:50–1:10  Switch to Sales Call analysis → repeat with sales script
    1:10–1:30  "Self-hosted, open source. Link in description."
  Pre-review with 3 testers
Afternoon:
  Apply demo feedback, re-record if needed


Day 71 — README + GitHub Public
─────────────────────────────────────────────
Morning:
  Write README.md:
    Hero: GIF of someone speaking → JSON appearing (Loom GIF export)
    What It Does (3 bullets: transcription, meeting notes, sales CRM)
    Quick Start (3 commands)
    Use Cases (table: meeting notes, sales call CRM, support QA)
    Architecture (ASCII)
    Tech: faster-whisper + Groq LLM + edge-tts
Afternoon:
  Make GitHub repo public
  Tag v0.1.0
  Add LICENSE (MIT)


Day 72 — Phase 4 Halfway Review + Continue Volume
─────────────────────────────────────────────
Morning:
  Add VoiceFlow as Upwork portfolio entry #4 (after AgentKit which was #3)
  Customize Section 26 Template 4 for voice/transcription jobs
  Send 5-10 voice-niche proposals:
    Filter Upwork for: "Whisper" "speech to text" "meeting notes AI"
                       "sales call analysis" "transcription pipeline"
Afternoon:
  Continue MCP / OCR / RAG niche volume
  Phase 4 halfway check: any inbound interest from Phase 1-3 ramping?
```

**Week 11 checkpoint:**
- [ ] Browser recording demo works end-to-end
- [ ] Deployed at public URL with Whisper preloaded
- [ ] Demo video recorded
- [ ] GitHub repo public

#### Week 12 — Blog Post 4 + Distribution + Voice Proposals

```
Day 73 — Blog Post 4 Draft
─────────────────────────────────────────────
Full day:
  Title: "From Audio to Action Items: Speech-to-Intelligence Pipelines"
  Outline:
    1. The gap: transcription gives you words, not insight.
       Real value is the structured layer after the transcript.
    2. Architecture: audio → Whisper → LLM analyzer → JSON
    3. Prompt design for meeting analysis:
       - The 8 fields and why each one
       - Handling ambiguity (action items with no clear owner)
       - Sentiment that isn't fake-empathetic
    4. Sales call analysis: the CRM-paste-ready format
       Why this is different from meeting notes
       Pain point detection, objection types, deal stage inference
    5. Cost and latency reality:
       - faster-whisper base model: ~2x realtime, free
       - Groq LLM analysis: ~$0.0005 per call, <2s
       - End-to-end: $0.001 per minute of audio
    6. What I'd build next: real-time streaming, diarization
       (pyannote if you can get it installed)


Day 74 — Polish + Save Blog Post 4 Draft (NOT PUBLISHED in 2026)
─────────────────────────────────────────────
Morning:
  Send draft to 2 reviewers (peers, not publication)
  Apply feedback
Afternoon:
  Save final draft to: voiceflow/drafts/blog_post_4_speech_intelligence.md
  Save subreddit posts (r/LanguageTechnology, r/speech_recognition) to:
    writing_workspace/reddit_drafts/
  Save Discord/Slack drop-in messages (Whisper Discord, AI-in-business) to:
    writing_workspace/community_drafts/
  Save LinkedIn draft to: writing_workspace/linkedin_drafts/
  Do NOT publish anywhere public. (Section 5.1)


Day 75 — Voice Proposals Volume
─────────────────────────────────────────────
Full day:
  Send 15+ voice-niche proposals:
    Lead with the browser-recording demo (memorable hook)
    Mention the 85%+ accuracy stat from DocIntel + the structured-output
      capability from VoiceFlow
  Continue IntelAI / DocIntel / AgentKit niches (5+ each)
  Total proposals today: 25-30


Day 76 — Phase 4 Metrics + Phase 5 Prep
─────────────────────────────────────────────
Morning:
  Phase 4 metrics:
    - VoiceFlow deployed and accessible: ___
    - Demo video views: ___
    - Blog Post 4 traction: ___
    - Voice-niche proposals sent: ___
    - Inbound DMs / cold-email replies: ___
    - Phase 1-4 cumulative: ___ interviews, ___ contracts
Afternoon:
  Open rageval/ repo — re-read STATUS.md
  Write Phase 5 TODO.md
  Decide: SQLite default vs PostgreSQL? (Recommend SQLite default for
    drop-in deploy; Postgres as optional config)
  Pre-stage: collect 5-10 query/answer pairs for testing scorers
    (you can synthesize these from IntelAI chat logs)


Day 77 — Buffer + Continue Volume
─────────────────────────────────────────────
Morning:
  Fix anything broken from the week
  Continue proposal volume
Afternoon:
  Respond to any DMs from Blog Post 4 / community posts
  Plan Phase 5 kickoff timing


Day 78 — Phase 5 Kickoff Prep
─────────────────────────────────────────────
Full day off (Sunday) — protect this. Burnout in month 3 kills the plan.
  If you must work: read 1-2 LLMOps blog posts from competitors
    (Phoenix, Langfuse, TruLens, Helicone) — know what you're differentiating
    against.
```

**Phase 4 final checkpoint:**
```
DELIVERABLE                                                 STATUS
─────────────────────────────────────────────────────────────────
VoiceFlow deployed at public URL                             [ ]
Browser recording demo works                                 [ ]
GitHub repo public                                           [ ]
Demo video recorded                                          [ ]
Blog Post 4 DRAFTED + community drafts saved (defer publishing to Q1 2027) [ ]
Upwork portfolio entry #4 added                              [ ]
15+ voice-niche proposals sent                               [ ]
Phase 1-4 cumulative: 3-7 contracts, $10-25k earned          [ ]
```

---

### 16.6 Phase 5 — RAGeval (Weeks 13–15)

**Goal:** LLMOps observability tool published to PyPI. This is your
**highest research-value project** — it sets up the arXiv preprint in
Phase 6 and signals to research programs that you ship production observability.

Differentiation against Phoenix / Langfuse / TruLens / Helicone:
self-hosted, SQLite-default (no infra), persona-aware metrics, drop-in
decorator API. Acknowledge competitors openly in the README — it builds
credibility.

#### Week 13 — Evaluator + Store

```
Day 79 — Verify Repo + Build Evaluator (Part 1)
─────────────────────────────────────────────
Morning:
  cd rageval
  source .venv/bin/activate
  Re-read STATUS.md
  pip install sentence-transformers scikit-learn numpy
  Verify install: python -c "from sentence_transformers import SentenceTransformer"
Afternoon:
  Build evaluator.py with RAGEvaluator class:
    __init__: loads SentenceTransformer("all-MiniLM-L6-v2") once
    score_retrieval_relevance(query, retrieved_chunks) → float 0-1
      cosine_similarity(query_embedding, chunk_embeddings).mean()
    score_groundedness(answer, context_chunks, model) → float 0-1
      LLM-as-judge: prompt Groq to rate 0-1
      Prompt template: "Is this answer supported by the context? Score 0-1.
                        Answer: {answer}\nContext: {context}"
      Strip and parse float from response
  Test each scorer on 5 sample query/answer/chunks tuples


Day 80 — Build Evaluator (Part 2)
─────────────────────────────────────────────
Morning:
  Add score_faithfulness(answer, context_chunks) → float 0-1
    Uses embedding similarity as NLI proxy:
      For each sentence in answer, find max similarity to any chunk
      Average across sentences (penalizes unsupported claims)
Afternoon:
  Add calculate_cost(tokens_used, model, input_ratio=0.7) → float (USD)
    GROQ_PRICES dict: {model_name: (input_per_1m, output_per_1m)}
    Includes: llama-3.1-70b, llama-3.1-8b, mixtral-8x7b
    cost = (input_tokens × in_price + output_tokens × out_price) / 1_000_000
  Add score_interaction(query, answer, retrieved_chunks, tokens_used,
                       latency_ms, model) → dict
    Runs all 4 scorers (relevance, groundedness, faithfulness, cost)
    Computes overall_quality = 0.4*relevance + 0.4*groundedness + 0.2*faithfulness
    Identifies flags:
      LOW_RETRIEVAL_RELEVANCE (relevance < 0.5)
      POTENTIAL_HALLUCINATION (groundedness < 0.6)
      HIGH_LATENCY (latency_ms > 5000)
    Returns complete dict


Day 81 — Build store.py
─────────────────────────────────────────────
Full day:
  Build store.py with SQLite-default + Postgres-optional storage:
    init_rageval_table() — creates rageval_log table
      Fields: id, timestamp, query, answer, persona, model,
              relevance, groundedness, faithfulness, cost_usd,
              latency_ms, tokens_used, flags, session_id, needs_review
    async log_interaction(query, answer, persona, scores, session_id) → None
    get_metrics(days=7) → dict for dashboard:
      avg_relevance, avg_groundedness, avg_faithfulness,
      avg_latency_ms, total_queries, total_cost_usd,
      flagged_count, query_volume_by_hour
    get_query_log(limit=50, needs_review=None) → list
    get_cost_report(days=30) → daily_costs, total_cost, by_model
  Use sqlite3 (stdlib) by default; switch to psycopg if RAGEVAL_DB env
    var points to a Postgres URL.
  Test: log 20 fake interactions, query metrics, verify aggregates


Day 82 — Build api.py
─────────────────────────────────────────────
Morning:
  Implement api.py:
    GET  /health
    POST /eval/log (body: query, answer, chunks, tokens_used, latency_ms, model)
      Computes scores, stores in DB
    POST /eval/score (body: query, answer, chunks)
      Returns scores without storage (for ad-hoc evaluation)
    GET  /eval/metrics?days=7
    GET  /eval/queries?limit=50&needs_review=true
    GET  /eval/cost-report?days=30
    GET  /eval/alerts (recent flagged queries)
Afternoon:
  Test all endpoints with curl + fake data
  Confirm SQLite file is created at first /eval/log call


Day 83 — Decorator API + Tests
─────────────────────────────────────────────
Morning:
  Build rageval/decorator.py:
    @track(model="llama-3.1-70b") decorator that wraps any function
      Captures: input query (from first arg), output answer, latency
      Auto-logs to RAGeval store via /eval/log
    Drop-in usage:
      from rageval import track
      @track(model="llama-3.1-70b")
      def answer_question(query, context_chunks): ...
  Test the decorator wraps a function and logs correctly
Afternoon:
  Tests:
    test_evaluator.py: 6 tests (each scorer + score_interaction)
    test_store.py: 4 tests (init, log, get_metrics, get_query_log)
    test_api.py: 5 tests (each endpoint)
    test_decorator.py: 2 tests (sync + async function wrapping)
  Run pytest, fix failures
```

**Week 13 checkpoint:**
- [ ] All 5 scorers (incl. cost) return values
- [ ] SQLite store logs and aggregates correctly
- [ ] 6 API endpoints respond
- [ ] @track decorator works on a sample RAG function
- [ ] 17+ tests pass

#### Week 14 — Dashboard + PyPI Publish

```
Day 84 — Dashboard Build (React) (Part 1)
─────────────────────────────────────────────
Morning:
  cd rageval && npx create-vite dashboard --template react
  cd dashboard && npm install recharts
  Configure proxy to API in vite.config.js:
    server: { proxy: { '/eval': 'http://localhost:8000' } }
Afternoon:
  Build App.jsx with 3 tabs: Overview | Query Log | Cost Report
  Implement Overview tab:
    3 metric cards (avg relevance, avg groundedness, avg latency)
    LineChart: quality score over time (7 days)
    BarChart: query volume by hour
    Fetches from /eval/metrics?days=7


Day 85 — Dashboard Build (Part 2)
─────────────────────────────────────────────
Morning:
  Implement Query Log tab:
    Fetch from /eval/queries?limit=50
    Table columns: time, query(truncated), relevance, groundedness,
                   latency, cost, flags
    Color-code rows: green (quality > 0.7), yellow (0.4-0.7), red (< 0.4)
    Toggle: "Show flagged only" → re-fetch with needs_review=true
Afternoon:
  Implement Cost Report tab:
    Fetch from /eval/cost-report?days=30
    LineChart: daily cost over 30 days
    Summary: total cost, avg per query, projected monthly
    Model breakdown table
  Polish: dark theme (#0f172a), consistent with IntelAI
  Manual test: generate 50 fake interactions, verify dashboard renders


Day 86 — PyPI Package Prep
─────────────────────────────────────────────
Full day:
  Restructure into installable package:
    rageval/
      __init__.py  (exposes: track, RAGEvaluator, init_db)
      evaluator.py
      store.py
      decorator.py
      cli.py  (rageval init / rageval serve commands)
    pyproject.toml with:
      [project]
      name = "rageval"
      version = "0.1.0"
      dependencies = [sentence-transformers, scikit-learn, ...]
      [project.scripts]
      rageval = "rageval.cli:main"
    README.md (the marketing surface — see Day 87)
  Test: pip install -e . in a fresh venv
        rageval init → creates SQLite DB
        from rageval import track → works


Day 87 — Polish README (Marketing-Critical)
─────────────────────────────────────────────
Full day:
  RAGeval's README is its growth engine. Treat it as the most important
  file. Structure:
    Title + badges (PyPI version, build status, license)
    Hero (one sentence): "Drop-in LLMOps observability for RAG systems.
                          Self-hosted. SQLite-default. Persona-aware."
    The 60-second pitch:
      ```python
      from rageval import track
      @track(model="llama-3.1-70b")
      def answer_question(query, context_chunks): ...
      # That's it. Open dashboard at localhost:8001.
      ```
    What It Measures (5 metrics with definitions)
    Comparison table:
      Feature              RAGeval   Phoenix   Langfuse  TruLens
      Self-hosted          ✅        ✅        ✅         ✅
      SQLite default       ✅        ❌        ❌         ❌
      Drop-in decorator    ✅        partial   ❌         partial
      Persona-aware        ✅        ❌        ❌         ❌
      Cost tracking        ✅        ✅        ✅         partial
      Open source          ✅        ✅        partial    ✅
      Setup time           60 sec    10 min    15 min    10 min
    Quick Start (3 commands)
    Integration Guide (how to add to FastAPI + LangChain)
    Dashboard Preview (3 screenshots)
    Roadmap


Day 88 — Publish to PyPI
─────────────────────────────────────────────
Morning:
  python -m build
  python -m twine upload --repository testpypi dist/*
  Install from test PyPI in a fresh venv — verify it works end-to-end
Afternoon:
  python -m twine upload dist/*
  Verify: pip install rageval in a clean venv anywhere
  Add PyPI badge to README
  Tag v0.1.0


Day 89 — Make GitHub Public + Submit to Lists
─────────────────────────────────────────────
Morning:
  gh repo edit <yourname>/rageval --visibility public
  Add LICENSE (MIT), CODE_OF_CONDUCT.md, CONTRIBUTING.md
  Tag and release on GitHub with release notes
Afternoon:
  Submit to:
    - awesome-llmops listings
    - awesome-rag listings
    - "Show HN: RAGeval — drop-in LLMOps observability (60-second setup)"
  Post in AI engineering Discords (lurk first; reply to existing
    observability threads; don't blast spam)


Day 90 — Blog Post 5 Draft
─────────────────────────────────────────────
Full day:
  Title: "Observability for RAG: Why I Built RAGeval (and Why Phoenix and
          Langfuse Are Great Too)"
  Outline:
    1. The state of LLMOps observability in 2026:
       Phoenix (Arize), Langfuse, TruLens, Helicone — all great products
    2. The gap I felt: too much setup for hobby/freelance/small-team use
       SQLite, decorator, 60-second-to-running
    3. The 5 metrics and why each one:
       retrieval relevance, groundedness, faithfulness, latency, cost
    4. Persona-aware groundedness:
       Same query, different persona → different "right answer"
       Standard groundedness misses this
       Our prompt: judge groundedness conditional on persona
    5. Honest comparison:
       When to use Phoenix instead (high-volume, enterprise)
       When to use Langfuse instead (rich integrations, hosted option)
       When RAGeval is the right call (self-hosted, simple, fast setup)
    6. Future: this becomes the basis of an arXiv preprint on
       Persona-Conditioned Groundedness (Phase 6 work)
```

**Week 14 checkpoint:**
- [ ] RAGeval is on PyPI, `pip install rageval` works
- [ ] Dashboard runs locally
- [ ] GitHub repo public
- [ ] README is marketing-grade with honest competitor table

#### Week 15 — Publish Blog Post 5 + LLMOps Proposals + Preprint Pre-Work

```
Day 91 — Polish + Save Blog Post 5 Draft (NOT PUBLISHED in 2026)
─────────────────────────────────────────────
Morning:
  Send draft to 2 reviewers (1 LLMOps person, 1 outside-tech for clarity)
  Apply feedback
Afternoon:
  Save final draft to: rageval/drafts/blog_post_5_rageval_observability.md
  Save Show HN draft with pre-written title:
    "RAGeval — self-hosted LLMOps observability (60-second setup)"
  Save Reddit drafts for r/MachineLearning + r/LocalLLaMA
  Save Discord drop-ins for LangChain #observability, Anthropic, DataTalksClub
  Save LinkedIn cornerstone-supporting draft
  Do NOT publish anywhere public. (Section 5.1)
  NOTE: RAGeval still gets pip-installed in 2026 — PyPI publish is fine
        (that's an artifact, not a content channel). What you defer is the
        marketing-content distribution (HN, Reddit, Medium, LinkedIn).


Day 92 — LLMOps Proposals + Dashboard Deploy
─────────────────────────────────────────────
Morning:
  Deploy dashboard to Vercel (free) or Railway:
    Build the React app: npm run build
    Deploy dist/ to Vercel
    Configure dashboard to point at a sample RAGeval API instance
  Or: keep dashboard local-only with great screenshots in README
Afternoon:
  Add RAGeval as Upwork portfolio entry #5
  Customize Section 26 Template 5 for LLMOps jobs
  Send 10 LLMOps proposals:
    Filter Upwork for: "LLMOps" "RAG evaluation" "AI observability"
                       "RAG monitoring" "hallucination detection"
  Lead with the comparison table + 60-second setup demo


Day 93 — Continue Volume + Inbound Response
─────────────────────────────────────────────
Morning:
  Continue IntelAI / DocIntel / AgentKit / VoiceFlow niches
    (5 proposals each across the day = 20 total)
Afternoon:
  Respond to PyPI download spike notifications, GitHub issues,
    blog post comments
  Engage genuinely — RAGeval is your community-credibility project
  If anyone asks about persona-aware groundedness specifically,
    flag that DM — these are potential preprint co-discussions


Day 94 — arXiv Preprint Pre-Work
─────────────────────────────────────────────
Full day:
  Start the LaTeX skeleton for the preprint:
    Title: "Persona-Conditioned Groundedness for RAG Systems"
    (or similar, refine later)
    Abstract (200 words, draft):
      "Standard groundedness metrics in RAG evaluation assume a single
      'correct' answer per query. In multi-persona systems (e.g.,
      enterprise assistants with role-based responses), the same query
      retrieves different relevant context per persona. We propose
      persona-conditioned groundedness, an LLM-judge prompt that scores
      answer support conditional on the persona's expected information
      scope. We implement this in RAGeval (open-source) and report
      results on a 9-persona enterprise analytics platform with
      [N] queries and [accuracy delta] vs. unconditioned groundedness."
    Sections (skeleton):
      1. Introduction (the gap)
      2. Related work (Phoenix, Langfuse, TruLens, recent RAG eval papers)
      3. Method (the prompt, the integration)
      4. Experiments (your IntelAI data with 9 personas)
      5. Discussion (limitations, future work)
      6. Conclusion
    Identify 10-15 papers to cite (recent RAG eval literature)
    Use Overleaf (free) for collaborative editing


Day 95 — Phase 5 Metrics + Phase 6 Prep
─────────────────────────────────────────────
Morning:
  Phase 5 metrics:
    - RAGeval on PyPI: ___ downloads
    - GitHub stars: ___
    - Blog Post 5 traction: ___ HN points, ___ Medium claps
    - LLMOps proposals sent: ___
    - Cumulative blog post views (Posts 1-5): ___
    - Phase 1-5 cumulative: ___ interviews, ___ contracts
Afternoon:
  Open streampulse/ — re-read STATUS.md
  Write Phase 6 TODO.md
  This is the last build phase before preprint focus.
  Prepare cold email list: 20-30 data/ops directors at growing SaaS
    companies (use LinkedIn search + Apollo trial)


Day 96 — Buffer
─────────────────────────────────────────────
Half day:
  Fix anything broken from the week
  Respond to community DMs / GitHub issues
Half day off — burnout management is critical at month 4
```

**Phase 5 final checkpoint:**
```
DELIVERABLE                                                 STATUS
─────────────────────────────────────────────────────────────────
RAGeval on PyPI (pip install rageval works)                  [ ]
GitHub repo public, 20+ stars                                [ ]
Dashboard demoed (locally or live)                           [ ]
Blog Post 5 DRAFTED + Show HN draft saved (defer publishing to Q1 2027) [ ]
10+ LLMOps-niche proposals sent                              [ ]
arXiv preprint skeleton started (LaTeX, abstract draft)      [ ]
Phase 1-5 cumulative: 3-7 contracts, $15-35k earned          [ ]
```

---

### 16.7 Phase 6 — StreamPulse + Polish + Preprint (Weeks 16–18)

**Goal:** Final project shipped. All 6 portfolio entries reviewed and
polished. arXiv preprint drafted to submittable state. Cold email push
across all 6 projects.

This phase is shorter on build work (1.5 weeks for StreamPulse) and
heavier on consolidation (portfolio polish, preprint, cold email).

#### Week 16 — StreamPulse Build

```
Day 97 — Verify Repo + Build api.py
─────────────────────────────────────────────
Morning:
  cd streampulse
  source .venv/bin/activate
  Re-read STATUS.md
  pip install -r requirements.txt
  Verify imports work
Afternoon:
  Build api.py:
    GET  /health
    POST /ingest/json (list of records)
    POST /ingest/csv (CSV file upload)
    POST /ingest/email (Gmail integration payload)
    POST /webhook/{source_name} (generic, with HMAC verify)
    GET  /pipeline/status
    GET  /pipeline/history (last 100 processed records)
    WS   /live (WebSocket — broadcasts classified records real-time)
  Test each with curl


Day 98 — Build connectors/webhook_receiver.py
─────────────────────────────────────────────
Full day:
  WebhookReceiver class:
    verify_signature(payload, signature, secret) → bool
      HMAC-SHA256 verification of X-Signature-256 header
    parse_payload(raw_json, source_name) → list of DataRecord
    route_to_pipeline(records) → None
      Calls DomainClassifier (already exists in classifier.py)
      Validates with DataValidator
      Stores via store_kpi_metrics
      Broadcasts to WebSocket connections
  Test with simulated webhook calls from N8N and custom sources


Day 99 — Build dashboard/LiveDashboard.jsx
─────────────────────────────────────────────
Full day:
  React app for live dashboard:
    WebSocket connection to /live endpoint
    State: records (last 50), volumeData (last 20 time buckets), domainDist
    Recharts LineChart: records per minute (live updating)
    Recharts PieChart: domain distribution (live updating)
    Table: live record feed (time, domain, metric, value, source, confidence)
    Domain colors:
      Finance: #6366f1 (indigo)
      Growth: #22c55e (green)
      Operations: #f59e0b (amber)
      People: #ec4899 (pink)
      ESG: #14b8a6 (teal)
      IT_Ops: #8b5cf6 (violet)
    Header: connection status (green/red dot), error count
    Dark theme (#0f172a)
  Test by streaming fake events via /ingest/json — verify dashboard updates


Day 100 — Tests + Deploy
─────────────────────────────────────────────
Morning:
  Tests:
    test_classifier.py: 5 tests (6 domains, edge cases)
    test_webhook.py: 4 tests (signature verify, payload parse, routing)
    test_api.py: 6 tests (each ingest endpoint, pipeline status)
    test_websocket.py: 2 tests (connect, broadcast)
  Run pytest, fix failures
Afternoon:
  Deploy StreamPulse to Railway or Fly.io
    (Cold-start tier — this is a secondary demo, can spin down)
  OR: ship as "docker compose up" in README, document as local-demo project
      (saves $5/mo on hosting if you'd rather not deploy a 6th project)
  Either way: record a 60-second demo video


Day 101 — README + GitHub Public + Portfolio
─────────────────────────────────────────────
Morning:
  Write README.md:
    Title: "StreamPulse — Real-Time Business Data Pipeline"
    Hero: GIF of dashboard updating live
    What It Does (3 bullets: ingestion, classification, dashboard)
    Supported Sources table (JSON, CSV, webhook, Gmail, Sheets)
    Quick Start (3 commands)
    Architecture ASCII
Afternoon:
  Make GitHub repo public
  Tag v0.1.0
  Add StreamPulse as Upwork portfolio entry #6
  Customize Section 26 Template 6 for data pipeline jobs
```

**Week 16 checkpoint:**
- [ ] StreamPulse api.py + dashboard work end-to-end
- [ ] WebSocket live updates verified
- [ ] Repo public, README ready
- [ ] Portfolio entry #6 added on Upwork

#### Week 17 — Cold Email Push + Blog Post 6 + Portfolio Polish

```
Day 102 — Cold Email List Prep
─────────────────────────────────────────────
Full day:
  Build a list of 30 cold email targets:
    Roles: Head of Data, VP Engineering, Director of Operations, CTO
    Companies: Series A/B SaaS (50-300 employees), with public data
      infrastructure pain (Reddit posts, hiring data engineers, etc.)
  Tools: LinkedIn Sales Navigator trial (or Apollo free tier, 50 leads)
  For each target, find:
    Name, role, company, LinkedIn URL, work email (or guess pattern),
    1 specific reason their company might need a real-time pipeline
      (recent funding, new data team hire, public scaling pain, etc.)
  Store in Notion or a spreadsheet


Day 103 — Cold Email Templates + First 15 Sends
─────────────────────────────────────────────
Morning:
  Write 2 cold email templates:
    Template A (data infra angle): for VP Eng / Director of Data
      Subject: "Real-time domain classification for your data pipeline?"
      Body (under 120 words):
        Personalized opener (1 sentence about their company)
        The pain you solve (1 sentence)
        StreamPulse demo link + 1-line description
        Soft CTA: "Worth a 15-min look?"
    Template B (BI angle): for COO / VP Operations
      Lead with IntelAI demo instead, soft offer to discuss
      analytics/BI overall
Afternoon:
  Send 15 cold emails (mix of A and B templates)
  Track open rates, replies, ghosts in spreadsheet


Day 104 — Blog Post 6 Draft
─────────────────────────────────────────────
Full day:
  Title: "Real-Time Domain Classification: From Webhook to KPI in 200ms"
  Outline:
    1. The problem: real-time data lands raw; classification is manual
    2. Architecture: webhook → classifier → store → dashboard
    3. Domain classifier design:
       6 domains, 160+ keywords, confidence scoring
       Why keyword-based instead of full ML (latency, explainability)
       When to upgrade to embeddings (future work)
    4. Webhook security: HMAC, replay protection, idempotency
    5. Building a live dashboard: WebSocket patterns, throttling
    6. Production reality: backpressure, retries, dead-letter queue


Day 105 — Polish + Save Blog Post 6 Draft + 15 More Emails
─────────────────────────────────────────────
Morning:
  Polish blog post, send to 2 reviewers, apply feedback
Afternoon:
  Save final draft to: streampulse/drafts/blog_post_6_realtime_classification.md
  Save Reddit drafts (r/dataengineering, r/Python) to writing_workspace/reddit_drafts/
  Save LinkedIn cornerstone-supporting draft to writing_workspace/linkedin_drafts/
  Do NOT publish anywhere public. (Section 5.1)
  Send 15 more cold emails (cumulative 30) — cold email IS allowed in 2026
    (it's direct outreach, not public publishing). Section 9 covers it.
  Continue Upwork volume on all niches


Day 106 — Portfolio-Wide Polish (All 6 Projects)
─────────────────────────────────────────────
Full day (do this carefully — these assets compound for years):
  For each of 6 projects:
    [ ] Demo URL works in incognito browser (no broken images, no 500s)
    [ ] README is < 250 lines, accurate, demo link in first 3 lines
    [ ] LICENSE file present (MIT)
    [ ] CI is green on main branch
    [ ] Loom demo video URL is live (Loom doesn't expire on free tier
        for active videos)
    [ ] GitHub repo description matches what the README says
    [ ] PyPI page (for omnismart-personas + rageval) has clear description
    [ ] DockerHub page (for docintel) has README synced
    [ ] Upwork portfolio entry has 3+ screenshots and clear bullets


Day 107 — All-Niche Volume + Inbound
─────────────────────────────────────────────
Morning:
  Send proposals across all 6 niches (60 minutes per niche, 8-10 total)
Afternoon:
  Respond to:
    - Cold email replies
    - GitHub issues / PRs (build community = future references)
    - DMs from blog posts
    - Upwork inbound DMs
  Schedule 2-3 discovery calls if you have inbound interest


Day 108 — Buffer
─────────────────────────────────────────────
Half day:
  Fix anything broken from the week
  Update Notion with cumulative metrics
Half day off (Sunday) — week 17 was heavy
```

**Week 17 checkpoint:**
- [ ] All 6 projects polished and verified
- [ ] 30 cold emails sent
- [ ] Blog Post 6 published
- [ ] All 6 blog posts cross-posted

#### Week 18 — arXiv Preprint Draft + Plan Q4

```
Day 109 — Preprint Section 1-2 (Intro + Related Work)
─────────────────────────────────────────────
Full day:
  Open the Overleaf project from Day 94
  Write Section 1 (Introduction, ~800 words):
    The standard groundedness problem
    Why multi-persona RAG is increasingly common (enterprise, healthcare,
    legal — cite 2-3 papers)
    Your contribution (persona-conditioned groundedness scoring)
    Roadmap of the paper
  Write Section 2 (Related Work, ~1000 words):
    Cluster A: RAG evaluation metrics (RAGAS, ARES, TruLens-Eval)
    Cluster B: LLM-as-judge methodology (LMSYS chatbot arena, MT-Bench)
    Cluster C: Multi-persona / multi-agent systems
    Position your work explicitly relative to each cluster


Day 110 — Preprint Section 3 (Method)
─────────────────────────────────────────────
Full day:
  Section 3 (Method, ~1200 words):
    Formal definition: groundedness(q, a, c) vs. groundedness(q, a, c, p)
    The persona-conditioned prompt:
      Show the exact prompt text
      Explain why the persona context is added at this layer
    Implementation in RAGeval:
      Decorator wraps any LLM call
      Stores per-persona groundedness scores
      Aggregates dashboards by persona
    Calibration: how you set scoring scale (0-1), few-shot examples


Day 111 — Preprint Section 4 (Experiments)
─────────────────────────────────────────────
Full day:
  Section 4 (Experiments, ~1500 words):
    Dataset: IntelAI with 9 personas
    Generate 200-500 query-answer-context tuples (one big eval run):
      Use the synthetic dataset (25,920 KPI records, 144 months, 5 domains)
      For each persona, generate 20-50 representative queries
      Run RAG pipeline, capture (query, answer, retrieved chunks)
    Score every tuple with both:
      Standard groundedness (no persona context)
      Persona-conditioned groundedness
    Report:
      Average score per persona (table)
      Score distribution (histogram or violin plot per persona)
      Cases where the two metrics diverge (qualitative analysis)
    Limitations: sample size, single LLM judge, no human eval (yet)


Day 112 — Preprint Section 5-6 (Discussion + Conclusion)
─────────────────────────────────────────────
Morning:
  Section 5 (Discussion, ~800 words):
    What the divergent cases reveal about RAG eval blind spots
    Implications for production RAG systems (especially enterprise)
    Honest limitations (LLM judge calibration, generalization to other personas)
    Future work: human eval, fine-tuned judge, real-time monitoring
  Section 6 (Conclusion, ~300 words):
    Restate contribution, results in 2 sentences, invitation to engage
Afternoon:
  Polish abstract (rewrite based on actual results)
  Build figure list:
    Figure 1: System diagram (RAG → RAGeval → persona-conditioned score)
    Figure 2: Score distribution per persona
    Figure 3: Divergence cases (scatter: standard vs persona-cond)
  Use TikZ or matplotlib exports (Overleaf supports both)


Day 113 — Send Preprint Draft for Review + Cold Email Round 3
─────────────────────────────────────────────
Morning:
  Compile the preprint PDF (Overleaf → Download → PDF)
  Send to 3-5 reviewers:
    - 1-2 academic contacts if you have any (LinkedIn outreach is fine)
    - 2-3 RAG-eval practitioners from your blog post comments
    - Subject: "Draft preprint on persona-conditioned groundedness —
                feedback before arXiv submission?"
    - Be explicit: "I'm not asking for endorsement, just a sanity check.
                    I'll cite acknowledgment if useful to you."
Afternoon:
  Send 15 more cold emails (cumulative 45)
  Send 20 more Upwork proposals across all 6 niches


Day 114 — Phase 6 Metrics + 18-Week Retrospective
─────────────────────────────────────────────
Full day, structured reflection:
  Phase 6 metrics:
    - StreamPulse deployed: ___
    - All 6 portfolio entries polished: ___
    - 45 cold emails sent: ___
    - Cold email reply rate: ___%
    - Blog Post 6 published: ___
    - Preprint sent for review: ___
  Cumulative 18-week metrics:
    - 6 deployed projects: ___
    - 6 blog posts published: ___
    - 2 PyPI packages with users: ___
    - DockerHub image: ___
    - Total Upwork proposals sent: ___ (target: 300-450)
    - Total interviews: ___ (target: 20-40)
    - Total contracts: ___ (target: 3-7)
    - Total earned: $___ (target: $15-40k by end of week 18)
    - GitHub stars across all repos: ___
    - Cumulative LinkedIn connections: ___
    - Preprint drafted: ___
  18-week retrospective:
    - Which project drove the most freelance interest?
    - Which project drove the most community/research interest?
    - Which niches converted on Upwork?
    - Which channel (Upwork / cold email / community) was strongest?
    - Where did you waste time? Where did you underinvest?
    - What would you change if you started over?
  Write this up in 500-1000 words. This becomes part of your eventual
  "What I built in 2026" LinkedIn launch post (Q1 2027).


Day 115 — Q4 2026 Planning + 2027 Launch Prep
─────────────────────────────────────────────
Morning:
  Plan weeks 19-30 (Q4 2026, post-build) — still 2026, so all publishing
  is still deferred. Q4 is "finishing pass + launch prep" only.
    [ ] Continue weekly Upwork proposal volume (now with reviews accumulating)
    [ ] Maintain GitHub repos (issues, PRs, small features, dependabot)
    [ ] Apply finishing pass to each blog draft once per month
        (add client-story sentence, real screenshots, updated numbers)
    [ ] Polish arXiv preprint to fully-submittable form (still NOT submitted in 2026)
    [ ] Build the personal portfolio site (Astro/Hugo) — locally, NOT deployed
    [ ] Build LinkedIn content library (20-30 short drafts written)
    [ ] Draft LinkedIn cornerstone post: "What I Built In 2026 (And What I Learned)"
    [ ] Start drafting research-program statements of purpose (outline only)
    [ ] Identify 3 workshop deadlines in Q1 2027 (NeurIPS retrospective workshops,
        ICLR workshops, AAAI 2027 — note dates, line up co-author/reviewer asks)
Afternoon:
  Plan 2027 (high-level — see PART X for the full deployment playbook):
    January 2027:  Multi-channel launch week (PART X Section 31)
                   • Personal site goes live
                   • LinkedIn cornerstone post published
                   • All 6 blog posts published over 6 weeks (one per week)
                   • Show HN submissions spread across Q1
                   • Reddit posts spread across Q1
    Feb-Mar 2027:  arXiv preprint submitted (cs.IR), workshop submission
    Q2 2027:       Faculty outreach (informational chats with research-program profs)
    Q3 2027:       Application drafting (SOPs, recommendation requests, CV polish)
    Q4 2027:       Submit applications (PhD/MS/fellowships), start preprint #2


Day 116 — Final Preprint Polish (NOT submitted in 2026)
─────────────────────────────────────────────
Morning:
  Apply review feedback from Day 113
  Polish formatting, figures, bibliography
  Final read-through: clarity, claims, citations
Afternoon:
  Save the polished preprint as: writing_workspace/preprint_v_final_2026.pdf
  Note in your Q1 2027 launch calendar: "Submit preprint to arXiv —
  pick a Tuesday morning UTC so European researchers see the announcement."
  Do NOT submit in 2026. (Section 5.1 — all public publishing is deferred.)
  This is intentional. A Q1 2027 arXiv announcement timed alongside your
  LinkedIn launch and personal site reveal compounds. A solo December
  2026 submission gets lost in the holiday news cycle.
  This is a quiet milestone. Sit with it.


Day 117 — Buffer + Final Sweep
─────────────────────────────────────────────
Full day:
  Final hygiene pass on everything:
    All 6 demos still respond
    All 6 GitHub READMEs current
    Upwork profile current with all 6 portfolio entries
    Notion / Airtable proposal log archived and analyzed
    secrets.md and .env files NOT committed anywhere
    All 6 blog drafts and preprint draft saved to writing_workspace/
    Personal site code committed (private repo) — ready to deploy 2027
    LinkedIn cornerstone draft + 20+ short drafts in writing_workspace/
  Plan a real break: 3-5 days actually offline before Q4 ramp


Day 118 — Done (end of Week 18)
─────────────────────────────────────────────
Take the day completely off. You earned it.
Tomorrow Q4 begins, at a sustainable pace.
Q1 2027 the multi-channel launch begins — see PART X.
```

**Phase 6 final checkpoint = End of 18-week plan:**
```
DELIVERED ACROSS 18 WEEKS (2026, intentionally minimalist channel mix):
  ✓ 6 deployed projects with live demos (where always-on tier applies)
  ✓ 6 technical blog posts DRAFTED + fact-checked (publish Q1 2027)
  ✓ 2 PyPI packages (omnismart-personas, rageval) with users
  ✓ 5 GitHub public repos (AgentKit, DocIntel, VoiceFlow, RAGeval, StreamPulse)
  ✓ 1 DockerHub image (DocIntel)
  ✓ 1 arXiv preprint POLISHED and review-ready (submitted Q1 2027)
  ✓ Upwork portfolio at 6 entries
  ✓ Cumulative: $15-40k earned (depending on conversion)
  ✓ 3-7 ongoing or completed client relationships
  ✓ 30-60 client reviews + recommendations starting to accumulate
  ✓ 150-300 LinkedIn connections (passively accumulated)
  ✓ Personal portfolio site coded (private), ready to deploy Q1 2027
  ✓ 20-30 short LinkedIn drafts written, ready to drip-feed in 2027
  ✓ 6 Show HN drafts, 6 Reddit drafts, LinkedIn cornerstone draft
  ✓ Material for 2027 multi-channel launch fully prepared
  ✓ Research-credential foundation set (deployed systems + preprint
    + community presence + client references)
```

### 16.8 Weekly Metrics, Decision Gates, And Cumulative Tracker

Track these weekly in Notion or Airtable. The numbers don't lie — they tell
you whether to continue, pivot, or pause.

#### Weekly tracker template

```
WEEK N (DATE):
  Build:
    Project worked on: _______
    Hours of build time: ___
    Lines of code added: ___
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
    Blog post views: ___
  Wellness:
    Hours slept: ___
    Days off: ___
    Mood (1-10): ___
  Reflection (1-3 sentences):
    What went well? ___
    What was a slog? ___
    Adjustment for next week? ___
```

#### Decision gates by phase

```
END OF PHASE 1 (Week 3):
  GO criteria:    50 proposals sent + 1 interview + demo live
  PAUSE if:       50 proposals + 0 interviews → demo/messaging audit before Phase 2

END OF PHASE 2 (Week 6):
  GO criteria:    DocIntel live + 30 OCR proposals + cumulative 1+ contract
  PAUSE if:       2 phases in and still 0 contracts → external audit

END OF PHASE 3 (Week 9):
  GO criteria:    AgentKit public + 10+ stars + Blog Post 3 drafted
  PAUSE if:       AgentKit has 0 stars after 5 days → README/demo audit

END OF PHASE 4 (Week 12):
  GO criteria:    VoiceFlow demo works + cumulative 3+ contracts OR
                  inbound interest from communities (DMs from blog 1-4)
  PAUSE if:       Cumulative <2 contracts → reduce build velocity, increase
                  proposal velocity, consider rate adjustment

END OF PHASE 5 (Week 15):
  GO criteria:    RAGeval on PyPI + Blog Post 5 drafted + preprint started
  PAUSE if:       Preprint draft has no shape → use Phase 6 buffer to extend

END OF PHASE 6 (Week 18):
  Final review (Day 114) — see retrospective questions above.
```

#### Cumulative tracker (Month 1 through Month 12)

```
                M1     M2     M3     M4     M5     M6     M9     M12
─────────────────────────────────────────────────────────────────────
Projects live   1      2      3      4      5      6      6      6
Blog posts      1      2      3      4      5      6      9      12
PyPI pkgs       1      1      1      1      2      2      2-3    3
GitHub stars    5-15   15-30  30-60  50-100 80-150 100-200 200-400 300-600
Total props     50     90     150    200    240    280    400    500
Interviews      0-2    2-5    4-8    6-12   8-15   10-18  20-30  30-45
Contracts (TC)  0-1    1-2    2-3    2-4    3-5    3-6    5-9    8-15
Earned          0-2k   2-6k   6-12k  12-22k 18-30k 22-40k 35-65k 50-90k
Preprints       0      0      0      0      0      1draft 1live  1-2live
```

(M = month. TC = total cumulative contracts.)

Bottom-of-range = slow conversion. Top-of-range = strong conversion. Both
are normal. The plan accommodates both.

---

## Section 17: Daily / Weekly Operating Rhythm

### 17.1 Daily structure (focused 4-hour build window + 2-3h pipeline work)

```
MORNINGS (4 hours, focused):
  Build the current phase's project
  No proposals, no email, no Slack
  Pure deep work

EARLY AFTERNOON (1 hour):
  Lunch + read 1 paper or blog post in your niche
  (Anthropic blog, OpenAI research, NeurIPS proceedings, etc.)

AFTERNOON (2 hours):
  Send proposals (5/day target)
  Respond to client messages
  Review and respond to community posts (DMs, GitHub issues, etc.)

EVENING (1 hour, optional):
  Light writing on current blog post
  Or: review code from a research paper you found interesting
  Or: lurk and learn on LinkedIn
```

### 17.2 Weekly structure

```
MONDAY-FRIDAY:    Build (mornings), Pipeline (afternoons), Learn (evening)

SATURDAY:         Buffer + content
                  Catch up on the week's leftover work
                  Make progress on current blog post

SUNDAY:           Off OR review and plan
                  Notion log review: what's converting?
                  Next week's task list
```

**Sundays off matter.** Burnout in month 3 kills the plan. Protect them.

---

## Section 18: Capacity Rules (When To Stop Applying)

```
CAPACITY            CLIENT WORK   PIPELINE WORK   STATUS
─────────────────────────────────────────────────────────────
0 active clients    0%            100%             Apply hard
1 active client     50%           50%              Steady pipeline
2 active clients    70%           30%              Reduce pipeline volume
3 active clients    90%           10%              Almost no new proposals
4+ active clients   100%          0%               Stop applying entirely
```

**Trigger to re-open pipeline:** When 1 contract ends OR when delivery
quality starts slipping → cut load before adding.

### 18.1 The "no new" stoppage rule

When 3+ clients are active:

- Do not respond to new Upwork DM invitations
- Do not send new proposals
- Auto-respond to cold emails with "Thanks, currently at capacity until [date]"
- Finish current commitments well — quality at this stage produces reviews
  that compound forever

---

## Section 19: When To Pivot Or Quit

### 19.1 Pivot triggers

```
TRIGGER                               ACTION
─────────────────────────────────────────────────────────────
30 proposals, 0 interview replies     Niche or messaging is wrong
                                      Pause, revise demo + proposal,
                                      get external feedback

5 interviews, 0 offers                Demo or pricing is wrong
                                      Watch the interview replay
                                      (Upwork records audio)
                                      Get peer review on demo

3+ months, 0 clients                  Channel is wrong
                                      Switch primary channel temporarily
                                      (try cold email or community
                                      for next 30 days)
```

### 19.2 Quit/postpone triggers (rare but real)

```
TRIGGER                               ACTION
─────────────────────────────────────────────────────────────
A FT job offer at a top AI lab        Strongly consider taking it
                                      (sometimes the freelance path
                                      is the slower path)

A research-fellowship offer            Almost always take it
(Anthropic Fellows, etc.)              The credentials compound faster

6 months, 0 paid contracts            Step back. Restructure.
                                      Get a structured mentorship or
                                      bootcamp on freelancing specifically
                                      (it's a separate skill from coding)
```

### 19.3 The 4-month checkpoint

By Week 16, you should have:
- 2+ paying contracts completed
- 4 blog posts published
- 4 portfolio entries
- Cumulative earnings of $5–20k

If you're materially below this, **stop building and diagnose**:
- Have you actually been pre-reviewing demos before going live?
- Are your proposals genuinely specific or actually generic?
- Are you applying to the right niches?

Get a real review from someone successful in AI freelancing (DM 3
established freelancers on Upwork or Twitter, offer to pay for a 1-hour
audit). $200 for a strong audit is the best money you can spend.

---

# PART VI — INFRASTRUCTURE, TOOLING, AND COST REALITY

---

## Section 20: Hosting Tiers (Railway, Fly.io, Local-Only)

### 20.1 The cost reality

V1 said "Railway free tier sufficient." This is wrong for 6 always-on
projects with PostgreSQL. Reality:

```
6 projects × Railway Hobby ($5/month base) = $30/month
6 PostgreSQL add-ons × $5 = $30/month
                              ─────────
Total minimum:              $60/month
```

Plus traffic, plus storage if you have any. Real number: $60–120/month.

This is sustainable if you have 1 paying client. Not sustainable from day 1.

### 20.2 The tiered hosting strategy

```
TIER 1 — ALWAYS-ON (your strongest demos)
  Hosted on: Railway or Fly.io
  Cost: $15-25/month
  Projects: IntelAI (primary demo), DocIntel (second-strongest)

TIER 2 — COLD-START (acceptable for demos, secondary)
  Hosted on: Fly.io free machines (cold-start in 2-3 seconds)
  Cost: ~$0
  Projects: AgentKit (open-source-driven, mostly read locally),
            RAGeval (you can run dashboard demo locally for video)

TIER 3 — LOCAL-ONLY (documented in README)
  Hosted on: nowhere
  Cost: $0
  Projects: VoiceFlow (Whisper models are heavy, demo via video),
            StreamPulse (live dashboard reproducible locally)
  README says: "Demo: see Loom video / clone + docker compose up"
```

This caps your monthly hosting at $25–40 even with 6 projects.

### 20.3 Fly.io is underrated for cold-start demos

For each cold-start project:

```toml
# fly.toml
app = "agentkit-yourname"

[build]
  dockerfile = "Dockerfile"

[[services]]
  internal_port = 8000
  protocol = "tcp"

  [services.concurrency]
    type = "connections"
    hard_limit = 25
    soft_limit = 20

  [[services.ports]]
    handlers = ["http"]
    port = 80

  [[services.ports]]
    handlers = ["tls", "http"]
    port = 443

[[services.http_checks]]
  interval = 10000
  grace_period = "5s"
  method = "get"
  path = "/health"

[[services.tcp_checks]]
  interval = 15000
  timeout = 2000

[deploy]
  strategy = "immediate"

[experimental]
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0  # Allows full cold-start
```

`min_machines_running = 0` makes it free between requests. First request
spins up the machine in ~3 seconds. Subsequent requests are fast. Perfect
for portfolio demos.

### 20.4 Database tier strategy

```
TIER 1 PostgreSQL — Railway add-on or Supabase free tier
TIER 2 SQLite — for projects where Postgres is overkill
                (rageval default, simple ingestion)
TIER 3 DuckDB — embedded, no separate process
                (StreamPulse analytics)
```

Each tier shifts cost down by 5-10x. RAGeval shipping with SQLite as
default makes it $0 to demo. Phoenix and Langfuse require Postgres
from day one — that's part of your competitive differentiation.

---

## Section 21: Pipeline Monitoring (Proposals, Demos, Outcomes)

### 21.1 The Notion / Airtable proposal log

One row per proposal. Columns:

```
- Date sent
- Job title (and link)
- Niche (RAG / OCR / FastAPI / etc.)
- Demo used (IntelAI / DocIntel / etc.)
- Template used (T1-T6)
- Client's prior reviews (0 / 1-10 / 10+)
- Client country
- Response (None / Interview / Hired)
- Outcome (Hired with rate / Withdrew / Ghosted)
- Lesson / note
```

### 21.2 Weekly review questions

Every Sunday, review the log and answer:

1. Which niche had the highest reply rate this week?
2. Which demo was used in the proposals that got replies?
3. What patterns do "no reply" proposals share?
4. Are you sending too many to high-competition jobs (50+ applicants)?
5. Are clients consistently asking the same questions in interviews?
   (If yes, update your proposal template to preempt them.)

### 21.3 The minimum viable analytics

After 60 days, you should know:

```
                            BEST     WORST
Niche by reply rate:        [niche]  [niche]
Demo by interview rate:     [demo]   [demo]
Template by hire rate:      [T#]     [T#]
Best client country:        [region] [region]
Worst client country:       [region] [region]
```

Double down on the best. Drop the worst. This data takes 60 days to be
meaningful — don't optimize too early.

---

## Section 22: Tools You Need (Free Or Near-Free)

```
TOOL                        PURPOSE                     COST
─────────────────────────────────────────────────────────────
Loom                        Demo video recording        Free (5min clips)
Notion or Airtable          Proposal + content tracker  Free
GitHub                      Code hosting                Free (public)
PyPI                        Package publishing          Free
DockerHub                   Image publishing            Free
Railway / Fly.io            Deployment                  $20-40/month
Supabase                    Postgres (alt to Railway)   Free tier
Personal site (Vercel)      Blog hosting                Free
Medium / Substack           Secondary blog distribution Free
arXiv                       Preprint hosting            Free
Cal.com or Calendly Free   Booking links               Free
Buttondown / EmailOctopus   Newsletter (optional 2027)  Free under 1k subs
Overleaf                    LaTeX for preprints         Free
─────────────────────────────────────────────────────────────
                                  TOTAL: ~$25-40/month
```

Add to this your existing Upwork costs (Connects) and you're at
$50-60/month operating expense. That's reasonable for a freelance
business.

---

# PART VII — POSITIONING, PRICING, AND PROPOSALS

---

## Section 23: Vertical Niching Within Each Project

Each project has 2–3 vertical-specific positioning angles. Pick ONE
primary per project and lead with it. Have a backup for variety.

```
PROJECT 1 — IntelAI
  PRIMARY:   Series A SaaS analytics ("ARR, churn, headcount built-in")
  SECONDARY: Healthcare KPI + compliance reporting
  TERTIARY:  ESG / sustainability reporting (EU CSRD-driven)

PROJECT 2 — AgentKit
  PRIMARY:   "MCP server for any business intelligence stack"
  SECONDARY: AI agency / consultancy white-label
  TERTIARY:  Internal R&D for AI-first product teams

PROJECT 3 — DocIntel
  PRIMARY:   Invoice AP automation (high volume)
  SECONDARY: Legal contract review
  TERTIARY:  Medical records extraction (highest premium)

PROJECT 4 — VoiceFlow
  PRIMARY:   Meeting transcription + action items (broad market)
  SECONDARY: Sales call analyzer + CRM integration
  TERTIARY:  Customer support call quality monitoring

PROJECT 5 — RAGeval
  PRIMARY:   "Drop-in observability for FastAPI + LangChain teams"
  SECONDARY: AI teams scaling RAG (50+ queries/day)
  TERTIARY:  Compliance teams needing audit logs

PROJECT 6 — StreamPulse
  PRIMARY:   Real-time pipeline for ops teams (replace manual data entry)
  SECONDARY: Custom n8n / Zapier alternative
  TERTIARY:  Webhook-driven analytics for SaaS dashboards
```

Each vertical is a different proposal template, a different blog post
opening, a different cold email subject line.

---

## Section 24: Upwork Profile (Refined)

### 24.1 Title

```
AI Systems Engineer | RAG · MCP Agents · Document AI · LLMOps · FastAPI
```

Why this works:
- "AI Systems Engineer" = premium positioning, not "developer"
- RAG = highest search volume AI skill on Upwork
- MCP Agents = trending, rare, high rates
- Document AI = consistent volume niche
- LLMOps = elite, growing demand
- FastAPI = largest Python API framework by job volume

### 24.2 Overview (first 300 chars are critical for search snippet)

```
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
STACK: Groq LLaMA 3.1 · sentence-transformers · faster-whisper · edge-tts
PUBLISHED: rageval (PyPI) · omnismart-personas (PyPI) · 6 blog posts
```

### 24.3 Skills tags

```
Primary (high search volume):
  RAG (Retrieval-Augmented Generation)
  LangChain
  FastAPI
  Python
  AI Chatbot Development
  PostgreSQL

Secondary (premium niches):
  LangGraph
  ChromaDB
  Docker
  React

Tertiary (rare, high rates):
  MCP (Model Context Protocol)
  LLMOps
  Agentic AI
  AI Observability
  Sentence Transformers

Supporting:
  OCR
  Speech-to-Text
  Groq
  Prometheus
  Whisper
```

### 24.4 Portfolio entries (one per project, ordered by Phase build)

(Templates from v1 preserved — they're correct. Each entry has:
title, 3 screenshots, 3-bullet description, demo link, stack.)

---

## Section 25: Pricing By Channel

```
CHANNEL                  STARTING RATE   AT 5 REVIEWS    AT 20 REVIEWS
─────────────────────────────────────────────────────────────────────
Upwork (cold inbound)    $65/hr          $85/hr          $110/hr

Upwork (warm referral)   $75/hr          $95/hr          $130/hr

Cold email (direct)      $85/hr          $110/hr         $150/hr

LinkedIn 2027 inbound    $95/hr          $130/hr         $170/hr

Research-aligned         Variable        Variable        Variable
  (Anthropic, etc.)      Often $100-150/hr; rate is secondary to credentials
```

### 25.1 Why don't compete on price

A $25-40/hr "AI engineer" attracts clients who want the cheapest option.
These clients almost universally:
- Pay late
- Demand scope creep
- Leave bad reviews
- Don't understand technical work

$65/hr filters them out. Your codebase justifies it from day one.

### 25.2 Fixed-price structure

```
PROJECTS UNDER $2,000:
  Milestone 1 (40%):  Core feature working + deployed
  Milestone 2 (60%):  Full feature + tests + docs

PROJECTS $2,000 - $5,000:
  Milestone 1 (30%):  Architecture + first endpoint
  Milestone 2 (40%):  Full backend feature
  Milestone 3 (30%):  Frontend + tests + deploy

PROJECTS OVER $5,000:
  Milestone 1 (20%):  Spec + first milestone delivered
  Milestone 2 (30%):  Core features working
  Milestone 3 (30%):  Full system complete
  Milestone 4 (20%):  Testing, deploy, docs
```

### 25.3 The 30% deposit rule

Always require milestone 1 paid before significant code is delivered.
This is for both your safety and the client's psychological commitment.

---

## Section 26: Six Proposal Templates (Niche-Specific)

(Preserved from v1. Each template has: opening sentence, demo link
placement, 3 specific technical questions, clear timeline. Templates
1-6 map to niches: RAG/AI Chatbot, MCP/Agentic AI, OCR/Document, Voice,
LLMOps, Data Pipeline.)

For brevity, refer to v1 Section 8 for the full templates. They're
correct and don't need refinement.

---

## Section 26.5: Applying Your Projects To Real Job Posts — A Worked Case Study

This section is a live case study. As you build the six projects, you'll
encounter actual Upwork job posts whose requirements map across multiple
projects. This section walks you through one specific real-world post (the
"Equipment Sourcing System" job, $5,000 fixed, 4-6 weeks, posted while this
document was being written) and shows you exactly how to apply.

The pattern is reusable: parse the post → map requirements to your projects
→ answer the gating questions with project-grounded evidence → quote
appropriately → close.

### 26.5.1 The Job Post (verbatim summary)

```
TITLE: Build an AI-Powered Equipment Sourcing System (Multi-Source Aggregator)
BUDGET: $3,500–$5,500 USD fixed price
TIMELINE: 4-6 weeks
LEVEL: Expert
PROPOSALS: 20-50 (so competition is moderate, not catastrophic)

CLIENT'S PROBLEM:
  Purchases specialized used equipment from government surplus, marketplaces,
  dealer liquidations. Current keyword-based scraper produces too much noise.

CLIENT'S PROPOSED SOLUTION:
  Vision-first classification (LLM looks at every photo, identifies relevant
  equipment regardless of title/description) — replaces noisy keyword approach.

WHAT THE SYSTEM DOES:
  - Ingests listings from 8+ sources (gov APIs, marketplace APIs, RSS feeds,
    email-based saved searches)
  - Runs every photo through a local vision model
  - Ranks results with a local LLM
  - Presents results in a mobile-friendly web dashboard
  - Sends daily digest email + push notifications for time-sensitive items
  - Runs unattended with self-monitoring

CLIENT'S EXISTING INFRA (KEY!):
  - Workstation server with Ollama, n8n, Gemma 4 (vision-capable), and
    Llama 3.3 70B already installed
  - Active subscription to a search API used by the current scraper
  - Existing scraper codebase available as reference

WHO THE CLIENT IS LOOKING FOR:
  - Strong Python or Node.js
  - Hands-on experience with locally-hosted LLMs (Ollama)
  - Comfortable with n8n
  - Has built multi-source data aggregation before
  - Communicates clearly, responds promptly
  - Available for 30-min video call

4 GATING QUESTIONS (must address each):
  1. Briefly describe a previous project where you integrated multiple data
     sources into a single pipeline. Link to code or detailed case study.
  2. Have you worked with locally-hosted vision models before? Which ones
     and for what?
  3. Initial intuition for handling duplicate listings across sources?
  4. One question you'd want answered before finalizing a bid?

PENALTY: Bids that don't address these four points will not be considered.
```

### 26.5.2 Why This Job Is Tailor-Made For Your Stack

This post is unusually well-aligned with your portfolio. The mapping:

```
CLIENT REQUIREMENT              YOUR PROJECT THAT PROVES IT
─────────────────────────────────────────────────────────────────────
Multi-source ingestion          StreamPulse (6 sources, classifier, n8n
                                integration, webhook receiver)
Local vision model              DocIntel (Route B: Ollama Llama 3.2 Vision)
Local LLM ranking               DocIntel + StreamPulse (Ollama tier)
n8n workflow integration        StreamPulse (custom n8n node + 3 workflows)
Unattended + self-monitoring    StreamPulse (Prefect 3 orchestration option)
Mobile-friendly dashboard       StreamPulse (React + responsive design)
Daily digest email              Reuse IntelAI's email infrastructure
Existing-code reference         You can read their scraper, integrate cleanly
```

You are answering this post from a position of "I already built each piece
of this in open source, here are the links" — which is the opposite of the
position 90% of competing applicants will be in.

**Critical:** you cannot apply to this post **until DocIntel + StreamPulse +
IntelAI are all live with public READMEs and Loom demos.** That's the
end of Phase 6 of the 18-week plan. This case study is a forward-looking
example, not an immediate action.

If this exact post (or one like it) shows up in May 2026 — before you've
finished Phase 6 — your move is to **bookmark it** and revisit in October.
By then your repos exist. If it's already filled, others like it will
appear — this client archetype is now common.

### 26.5.3 The Proposal Template For This Post

Here is the exact proposal text you'd submit. Read it carefully, then we'll
break down why each element is there.

```
Hi,

I read your post twice. The vision-first classification idea is the right
move — keyword scrapers fail on the exact case you described (mislabeled
or vague listings), and a local vision LLM solves it cleanly.

I've built each piece of what you're describing in open source, deployed
and demo-able. Three of my projects compose into roughly the system you
specified:

→ DocIntel — vision-first document/image classification. Route B is local
  Ollama + Llama 3.2 Vision (the exact pattern you need). The endpoint
  /classify-image takes an image + a list of candidate categories and
  returns category + confidence + reasoning, with the local-vision route
  selected via config:
    Demo: <DOCINTEL_DEMO_URL>
    Repo: github.com/<yourname>/docintel

→ StreamPulse — real-time multi-source ingestion pipeline with a domain
  classifier and a custom n8n node. Sources are pluggable (webhooks,
  REST APIs, Gmail polling, RSS, Sheets). Has a live React dashboard,
  self-monitoring via /pipeline/status, and a Prefect 3 orchestration
  flow for the unattended case.
    Demo: <STREAMPULSE_DEMO_URL>
    Repo: github.com/<yourname>/streampulse

→ IntelAI — provides the email-digest pipeline I'd reuse for your
  daily digest + push notifications.
    Repo: github.com/<yourname>/intelai

Now to your four questions:

(1) Previous multi-source pipeline:
StreamPulse (link above) ingests from 6+ sources (Gmail, Google Sheets,
N8N webhooks, REST APIs, CSV upload, manual JSON) into a unified
classified store with a live dashboard. Deployed, open source, with a
documented n8n node template. The Equipment Sourcing system is the same
pattern with different sources — I'd plug in your government auction
APIs, marketplace APIs, RSS feeds, and the email-based saved searches as
StreamPulse sources, then add the vision-classification step (DocIntel's
/classify-image) between ingest and store.

(2) Local vision model experience:
DocIntel ships with two local-vision options: Llama 3.2 Vision 11B and
Qwen 2.5-VL 7B, both via Ollama. I've used both for invoice extraction
and image classification. For the equipment-photo use case I'd start with
Llama 3.2 Vision 11B (your server already has Llama 3.3 70B, so adding
the 3.2 vision variant is a 6GB download) and benchmark against Gemma 4
Vision (which you already have installed). I'd expect Llama 3.2 to win
on visual categorization given current benchmarks, but it's worth a
4-hour comparison on a sample of your real listings before committing.

(3) Duplicate listings across sources:
Three-layer dedup, hardest-first:
  Layer 1: Content-hash dedup (SHA-256 of normalized title + price +
           seller). Catches exact reposts.
  Layer 2: Perceptual image hash (pHash via imagehash library). Catches
           the same listing posted with renamed title across sources.
  Layer 3: Embedding-similarity dedup. Compute a joint embedding of
           (title text + image embedding) per listing and use cosine
           similarity > 0.93 as a "likely duplicate" threshold for
           human review.
The first two layers cover ~90% of cases at zero LLM cost. Layer 3 is
the safety net for cross-source listings that have different titles and
slightly different photos. I'd ship Layer 1 + 2 by week 2, Layer 3 by
week 4 with a configurable threshold so you can tune false-positive vs
false-negative rate based on early feedback.

(4) My pre-bid question:
What's the daily volume of new listings across all 8 sources, and is
there a latency SLA per listing? This shapes the architecture
fundamentally:
  - <500 listings/day, no real-time SLA → I batch-process nightly with
    cron + Ollama (cheapest, simplest, easiest to operate). Estimated
    4-5 weeks.
  - 500-5000/day, near-real-time → I stream through n8n + StreamPulse,
    vision-classify on-the-fly, queue with Redis. Estimated 5-6 weeks.
  - >5000/day → I'd recommend a slimmer vision model (Qwen 2.5-VL 7B
    or Gemma 4 Vision) and a 2-stage pipeline (cheap visual filter
    first, expensive classification only on passes). Estimated 6+
    weeks; we'd need to scope carefully.

The 30-minute video call you mentioned: I'd come prepared to walk
through DocIntel's /classify-image endpoint live on one of your real
listings (if you can share an anonymized URL), and to whiteboard the
data flow including how StreamPulse's existing n8n integration plugs
into your existing Ollama + n8n + Llama 3.3 70B server.

Timeline: 4-6 weeks fits with my realistic estimate. I'd structure it
as:
  Week 1 — discovery, source enumeration, integration scoping
  Week 2 — ingestion pipeline + Layer 1+2 dedup
  Week 3 — vision classification + ranking
  Week 4 — dashboard + digest emails + push notifications
  Week 5 — self-monitoring + dedup Layer 3 + tuning
  Week 6 — buffer + handoff documentation

Bid: $5,000 fixed, milestoned at 30/30/40 (after weeks 2, 4, and 6).

Available for the video call within 48 hours of your reply. My time
zone is <YOUR_TIMEZONE>; I'm flexible.

— Yacine
```

### 26.5.4 Why This Proposal Wins (Diagnosis)

**Length:** It's longer than the typical Upwork proposal (around 1000
words). That's intentional: the post says "Bids that don't address these
four points will not be considered" and "I'm looking for someone who reads
carefully and thinks before quoting." This client *wants* thoughtful
length. A 200-word proposal would be filtered out for not engaging
substantively.

**Demo placement:** First demo link appears in the 7th line. Second in the
13th. Third in the 18th. Before any of the gating questions. This is
deliberate: by the time the client reads question 1, they've already
clicked at least one of your demos.

**Each gating question answered with project-grounded evidence:**
- Q1 answered with StreamPulse + concrete mapping to their use case
- Q2 answered with two specific local vision models + a benchmarking plan
- Q3 answered with a three-layer technical strategy + week-numbered
  delivery commitments
- Q4 (the meta-question) answered with three scenarios scaled to
  volume, each with a different architectural recommendation and a
  different timeline — proves you've genuinely thought about it

**Bid positioning:** $5,000 (the top of the stated range). Cheap bids get
deprioritized per the post. Coming in at the top with a clear scope
breakdown signals confidence.

**Milestone structure:** 30/30/40 reduces client risk while protecting
your cashflow. The 30% upfront-after-week-2 is the trust-builder.

**Tone:** No "I am confident I can deliver this." No "I have 5 years of
experience." Just specific technical content, with confidence implicit
in the depth of the answers.

### 26.5.5 The Generalized Pattern (For Future Job Posts)

When you see a multi-component job post like this one, walk through:

```
STEP 1 — INVENTORY THE COMPONENTS
  List every distinct capability the post asks for.
  For each, note which of your 6 projects (or none) demonstrates it.

STEP 2 — DECIDE IF YOU CAN COVER 70%+ OF COMPONENTS
  If yes → apply with composition proposal (this section's template).
  If no → either decline, or apply with honest scope ("I can do A, B, C;
          would need to build D fresh; here's how I'd approach it").

STEP 3 — MAP THE GATING QUESTIONS TO PROJECT EVIDENCE
  Every question becomes: "Here's the project / line of code / demo that
  proves I've done this exact thing before."

STEP 4 — ADD ONE THOUGHTFUL META-QUESTION
  The "pre-bid question" prompt (Q4 above) is your chance to show
  architectural thinking. ALWAYS frame it as "shape the architecture"
  not "is this even possible." It must be a question whose answer
  meaningfully changes the technical approach, not a clarification ask.

STEP 5 — QUOTE AT THE TOP OF THE STATED RANGE
  If they say "$3,500-$5,500," quote $5,000 or $5,500. Cheap bids
  signal you don't believe in your work. The client said as much in
  the post.

STEP 6 — STRUCTURE MILESTONES TO PROTECT BOTH SIDES
  Never 100% on completion. Always at least 3 milestones. The first
  one paid early enough that you've recouped most of your risk.

STEP 7 — VIDEO CALL READINESS
  If the post mentions a call, signal you're ready and have something
  to show on the call (a live demo on their data, a whiteboard sketch).
```

### 26.5.6 Three More Job Archetypes You'll Match

The same pattern applies to other 2026 archetypes. Below are the briefs
plus the project composition that wins each one.

#### Archetype A — "Build me a chatbot over my docs" ($1,500–$5,000)

```
TYPICAL POST:    "I have ~500 PDF/markdown docs. Want an internal
                  chatbot that answers questions with sources cited.
                  React frontend OK. Self-hosted preferred."

PROJECTS USED:   IntelAI (RAG + chat UI + sources) + DocIntel
                  (PDF ingestion via vision-first or Marker) + RAGeval
                  (groundedness scoring shipped with their deploy)

WINNING ANGLE:   "Three-tier model strategy: Claude Sonnet 4.6 for
                  quality, Groq for volume, Ollama for privacy. You
                  pick via env var. Plus drop-in observability —
                  you'll see exactly which answers are well-grounded
                  and which aren't."

QUOTE:           $3,500-$5,000 depending on scope and source count.
```

#### Archetype B — "MCP server / Claude Desktop integration" ($800–$3,000)

```
TYPICAL POST:    "I want Claude Desktop to interact with our internal
                  database / Notion / Salesforce. Build me an MCP server."

PROJECTS USED:   AgentKit (exact pattern, multiple framework demos)

WINNING ANGLE:   "Here's my open-source MCP server with 6 tools. I'd
                  adapt the same patterns to your data sources. Bonus:
                  I can also build a CrewAI or LangGraph workflow on
                  top if you want non-Claude clients later."

QUOTE:           $1,500-$3,000. MCP work has rare-skill premium.
```

#### Archetype C — "Sales-call analyzer / meeting summarizer" ($1,500–$6,000)

```
TYPICAL POST:    "Transcribe sales calls and extract: pain points,
                  objections, deal stage, CRM-paste-ready notes."

PROJECTS USED:   VoiceFlow (exactly this; Claude Sonnet 4.6 for the
                  analysis step) + RAGeval (for ongoing quality
                  monitoring)

WINNING ANGLE:   "Browser-recording demo I can show you in 30 seconds
                  on a call. Multi-provider transcription so you can
                  switch from Deepgram to local Whisper without
                  rewriting code. Claude Sonnet 4.6 for the analysis
                  layer — that nuance matters for buying signals."

QUOTE:           $2,500-$6,000 depending on CRM integration scope.
```

### 26.5.7 A Discipline Note On Application Velocity

Once your portfolio is at 4+ live projects, **stop spraying generic
proposals**. The composition-based proposals in this section take 30-45
minutes each to write properly. You can produce 3-5 of them per day
maximum. That's right for the Phase 6+ stage.

The volume game (10 proposals/day) is what gets you the first 1-3
contracts when you have nothing else. Once you do, **proposal quality
scales the rate** — better proposals lead to higher-budget contracts
with happier clients.

By month 4-6 of your 2026 plan, your typical proposal should look more
like Section 26.5.3 above and less like a Section 26 template.

---

# PART VIII — RISK AND REALITY CHECK

---

## Section 27: Things That Will Go Wrong (Plan For Them)

### 27.1 Technical surprises

| Risk | Probability | Mitigation |
|------|-------------|------------|
| Whisper / faster-whisper dependency hell on Railway | High | Test deploy in Phase 4 Day 1, not Day 10 |
| LLM extraction prompts produce inconsistent JSON | Very High | Plan 1-2 weeks of prompt iteration |
| WebSocket auth/CORS issues in production | High | Add to test suite explicitly |
| pyannote diarization fails to install | High | Documented fallback to no-diarization |
| ChromaDB memory blowup with full dataset | Medium | Use streaming retrieval, batch ingestion |
| Railway / Fly.io free tier exhausted faster than expected | High | Tier the demos per Section 20 |
| Frontend Recharts performance on big datasets | Low | Limit chart data points to last 20-50 |

### 27.2 Market surprises

| Risk | Probability | Mitigation |
|------|-------------|------------|
| First 30 Upwork proposals get 0 replies | Very High | Plan for this, don't panic |
| The niche you targeted has too much competition | Medium | Track in Notion, pivot at 30-proposal mark |
| Clients ghost mid-interview | High | Don't take it personally; this is normal |
| A "great" client turns out to be slow-paying | Medium | Always milestone-based; verify payment before sprint |
| MCP demand on Upwork stays thin in 2026 | High | Treat AgentKit as OSS-first, not Upwork-first |
| Phoenix or Langfuse announce a self-hosted lightweight version | Medium | Make RAGeval's persona-aware metric the durable differentiator |

### 27.3 Personal surprises

| Risk | Probability | Mitigation |
|------|-------------|------------|
| Burnout in month 2-3 | Very High | Protect Sundays. Cap proposal volume. |
| Discouragement after 60 days, $0 earned | High | Re-read Section 19. The funnel takes 60-90 days. |
| Imposter syndrome reading other freelancers' portfolios | High | They had 12 months to build that. You're in month 2. |
| Tempted to take a $30/hr "easy" gig | High | Don't. Costs are bigger than gains. |
| Family / friends questioning the path | High | Show them the live demo + the income trajectory chart |

### 27.4 The "first paid client" trap

When your first paid contract arrives, the temptation is to celebrate and
deliver fast. Common mistakes:

- Over-promising scope to win it
- Under-pricing to "get the review"
- Working 12-hour days, burning out by week 2

Better: deliver well, on time, at your stated rate, with no scope creep.
The first review is more valuable than the first $1,000.

---

## Section 28: Milestone Expectations (What Realistic Looks Like)

```
MONTH       PORTFOLIO   PROPOSALS  CONTRACTS    EARNED        OSS
─────────────────────────────────────────────────────────────────────
Month 1     1 entry     50          0-1          $0-1k         0 packages
Month 2     2 entries   120         1-2          $2-4k         1 package
Month 3     3 entries   200         2-3          $4-8k         1 package
Month 4     4 entries   270         3-4          $8-15k        2 packages
Month 5     5 entries   320         3-5          $12-22k       2 packages
Month 6     6 entries   360         3-5          $18-30k       2 packages
Month 9     6 + maint   400+        4-6          $35-55k       2-3 packages
Month 12    6 + papers  450+        4-6          $50-80k       3 packages
            +1 preprint                                        +preprint
```

### 28.1 Reading the table

- **Bottom of range** = slow conversion, primarily 1-2 small clients
- **Top of range** = strong conversion, 2-3 ongoing + multiple small projects
- **Both are normal.** Don't be disappointed by the lower number.

### 28.2 The "Month 6 reset" milestone

By month 6:
- If you're at the bottom of the range, reassess: niche, demo, pricing
- If you're at the top of the range, increase rates by 20%
- Either way, start LinkedIn 2027 prep work in earnest (build content
  library, connect with everyone in your network)

### 28.3 Sustainability check

A realistic 2026 outcome:
- $25–60k freelance income
- 2 PyPI packages with users
- 6 blog posts published
- 1 arXiv preprint up
- 5+ ongoing or recurring clients
- 200-400 in-niche LinkedIn connections
- Material for research applications ready to submit late 2027

That's a strong industry-to-research transition foundation. Not Twitter-famous,
not "$200k by year-end" mythology. But solid, real, and compounds.

---

## Section 29: Common Failure Modes (And Their Fixes)

### 29.1 "I sent 50 proposals and got 0 replies"

Most common causes (in order):
1. Demo is broken when client clicks the link (test it weekly!)
2. Demo link is buried at the end of the proposal, not the third line
3. Proposals are too generic — "I have experience with X"
4. Targeting jobs with 50+ applicants and 0 client reviews (low quality)
5. Title/profile keywords don't match what clients search for

Fix: pick 1 trusted freelancer in your niche. Pay them $100-200 for a
30-minute review of your profile + 3 sample proposals. They'll tell you
which of the 5 issues above is killing you. Cheapest, fastest, most
useful investment.

### 29.2 "Clients are flaky / scope-creep / underpay"

This is a filtering problem upstream. Better filters:
- Only apply to jobs with 3+ client reviews
- Require milestone 1 paid upfront (Upwork escrow)
- State scope clearly in the proposal; revise if they push
- Track "client pain index" in your Notion log → don't repeat clients with high scores

### 29.3 "I'm building project 3 but no one cares about project 1"

This is exactly why the plan is phased, not parallel. Before starting
Phase 4 (week 11), review:
- Has project 1's portfolio entry generated interview interest? (>3 in 8 weeks expected)
- Has project 2 generated interest? (>2 in 4 weeks expected)
- Has project 3 generated interest? (>1 in 2 weeks expected)

If yes to 2/3 → continue per plan.
If yes to only 1/3 → before Phase 4, do another week of intensive
proposal-tweaking on the underperforming projects. Maybe the demo is
the issue, not the project.
If yes to 0/3 → STOP, pause Phase 4, get external review. Something
fundamental is misaligned.

### 29.4 "My demos work locally but break on Railway/Fly.io"

This is universal. Plan for it.

- Test deployment **on day 1 of building**, not day 10
- Use `.env.example` to ensure environment-variable parity
- Use the same Python version locally as on Railway
- Watch for: file paths, CORS origins, database connection strings,
  Whisper / Tesseract binary dependencies

### 29.5 "I'm exhausted and want to quit"

Take a real week off. Not "I'll only work 3 hours a day" — actually off.
Walk, sleep, see friends. Most freelancers who quit do so in month 3.
The ones who succeed are usually the ones who took week 12 off and came
back instead.

---

# PART X — THE 2027 MULTI-CHANNEL DEPLOYMENT PLAYBOOK

In 2026 you built six projects, drafted six blog posts, polished one
preprint, designed a personal site, and wrote a LinkedIn cornerstone post
plus 20-30 supporting drafts. None of it went public in 2026.

This part is the **2027 deployment plan**: how the ammunition you stockpiled
becomes a multi-channel launch over Q1-Q2 2027 that compounds for the rest
of your career.

The key insight: **a coordinated launch beats spreading the same content
over 12 months by a wide margin.** When LinkedIn, your personal site,
Medium, dev.to, arXiv, and HN all light up within a 6-week window pointing
at the same six projects, the cross-referencing creates an "I keep seeing
this person" effect that no individual channel produces.

---

## Section 31: The 2027 Launch Week (January Week 2)

The first concentrated launch event of 2027. Pick a Tuesday-Wednesday-
Thursday window in mid-January (avoid New Year week — engagement is low).

### 31.1 Day-by-day launch schedule

```
MONDAY (preparation, no public posts)
  - Final review of personal site (built in 2026, deployed today)
  - Push personal site to production: yacine.dev (or your domain)
  - Verify all 6 GitHub repos still public, all demos still respond
  - Verify Loom video links still work (test from incognito)
  - Cross-check: every README links to live demo + Loom

TUESDAY (LinkedIn cornerstone + personal site)
  10:00 AM (your TZ): Publish LinkedIn cornerstone post
                       "What I built in 2026: 6 AI projects, $X earned,
                       what I learned about [theme]"
                       Cross-link to personal site (yacine.dev/2026)
  Throughout day:    Respond to comments. NO new content. Just engage.

WEDNESDAY (Hacker News submission #1 — AgentKit)
  US morning (9 AM ET): Submit "Show HN: AgentKit — MCP server for
                         business intelligence agents"
                         Post in /r/LocalLLaMA + Anthropic Discord
                         simultaneously (different angle, same project)
                         Cross-link to GitHub.
  Throughout day:    Respond to HN comments. AgentKit is the most likely
                     to hit HN's front page because of MCP novelty.

THURSDAY (Medium + dev.to publishing — Blog Post 1)
  9 AM (your TZ):    Publish Blog Post 1 (Persona-Routed RAG) on personal
                     site as canonical URL.
                     Cross-post to Medium with canonical link back.
                     Cross-post to dev.to with canonical link back.
                     Post a LinkedIn share-link with 2-sentence framing.
  Afternoon:         Respond to Medium claps, dev.to comments,
                     LinkedIn engagement.

FRIDAY (decompression + planning week 2)
  No new content.
  Review week-1 metrics:
    - LinkedIn cornerstone post reach
    - Personal site traffic
    - HN front-page yes/no for AgentKit
    - Blog Post 1 view counts across channels
    - New connection requests, DMs, GitHub stars
  Decide adjustments for weeks 2-6.
```

### 31.2 Weeks 2-6 — Rolling blog post + Show HN cadence

```
WEEK 2  — Blog Post 2 (Vision-First Document AI) + Show HN #2 (DocIntel)
          Post Reddit r/MachineLearning methodology-led excerpt
WEEK 3  — Blog Post 3 (MCP Tool Design Patterns) + Show HN #3 (already
          submitted AgentKit in week 1; this week's Show HN can be
          DocIntel or IntelAI depending on which got Reddit traction)
WEEK 4  — Blog Post 4 (Speech-to-Intelligence) + Show HN #4 (VoiceFlow)
          Reddit r/speech_recognition crosspost
WEEK 5  — Blog Post 5 (Multi-Judge LLM Eval) + Show HN #5 (RAGeval)
          This is the most likely HN hit because LLMOps is hot
WEEK 6  — Blog Post 6 (Vision-First Multi-Source Aggregation, with the
          anonymized Equipment Sourcing case study if that contract
          happened) + Show HN #6 (StreamPulse)
```

Across the 6-week launch:
- 6 Show HN submissions (3-4 will probably die on /new; 1-2 should hit
  front page given quality + topic relevance)
- 6 blog posts on personal site + Medium + dev.to
- 6 supporting LinkedIn posts
- 6 supporting Reddit posts (carefully targeted)
- 1 LinkedIn cornerstone post (week 1)
- Continuous LinkedIn 2x/week cadence using the 20-30 short drafts

By end of Week 6 (mid-February 2027), your public footprint is:

```
PERSONAL SITE:      6 blog posts, project gallery, about page
MEDIUM:             6 cross-posted articles, ~5-30k cumulative reads
DEV.TO:             6 cross-posted, more engagement than Medium typically
LINKEDIN:           1 cornerstone, 6 supporting, 10+ short posts = network
                    explosion (~500-2000 new connections likely)
HACKER NEWS:        6 submissions, ~1-2 front-page hits, ~5-20k cumulative
                    visits
REDDIT:             6 thoughtful posts, ~1-3 went viral in niche subs
GITHUB:             Stars across all repos likely +500-3000 cumulative
                    over the 6 weeks
UPWORK:             Inbound DMs noticeably increased due to "I keep seeing
                    this person's name" effect
EMAIL INBOX:        Cold inbound from CTOs, agencies, recruiters,
                    research-program profs
```

This is what the 2026 minimalism buys you. A coordinated launch beats a
trickle.

---

## Section 32: arXiv Submission Window (February-March 2027)

The preprint sat polished from end of 2026. Submit it in the right window:

```
WHY NOT JANUARY:    LinkedIn launch consumes your bandwidth and a
                     pre-print announcement gets lost
WHY FEBRUARY-MARCH:  Quiet enough that the preprint announcement gets
                     attention; well-timed before workshop deadlines
                     for spring conferences

SUBMISSION DAY:
  Tuesday morning UTC. European researchers wake up to it, US researchers
  see it during their workday.

SUBMISSION CONTENT:
  - Preprint v2 (with Q4 2026 finishing-pass refinements)
  - Categories: cs.IR (primary), cross-list cs.CL, cs.LG
  - arXiv comment: "Code at github.com/<yourname>/rageval; data at <link>"

ANNOUNCEMENT:
  - LinkedIn post (timed with submission day)
  - Personal site blog post: "My first preprint: <title>"
  - Twitter / X (if you use it)
  - DM the 3-5 reviewers from Day 113 thanking them and sharing the
    submission link
```

### 32.1 Workshop submissions following the preprint

```
WORKSHOP                                  TYPICAL DEADLINE     YOUR TARGET
─────────────────────────────────────────────────────────────────────────
NeurIPS 2027 RAG workshops                Aug-Sep 2027         Submit
ICLR 2027 workshops                        Dec 2026 (missed)    —
                                                                (this is why
                                                                 you'd shifted
                                                                 the preprint
                                                                 timing)
AAAI 2027 workshops                       Nov 2026 (missed)    —
ICML 2027 workshops                        Mar 2027             Submit
ACL 2027 workshops                         Apr 2027             Submit
EMNLP 2027 workshops                       Jun 2027             Submit
COLM 2027 (Conf on Language Modeling)     Mar 2027             Submit if RAG
                                                                topic fits
```

You don't have to submit to all. Pick 2-3 that align thematically with the
preprint. Workshop acceptance rates are 30-50%, so submitting to 3 gives
you a real shot at 1-2 accepts.

---

## Section 33: The 2027 LinkedIn Posting Engine

Once the launch week is past, settle into a sustainable cadence:

```
CADENCE:            2 posts per week (Tuesday + Thursday, mid-day local)
TOPICS:             Drawn from the 20-30 drafts you wrote in 2026, with
                    fresh updates from 2027 client work
LENGTH:             200-400 words ideal; longer posts can do well but
                    rarely the right move for technical content
HOOKS:              Story-led, not list-led. "I just fixed a bug that
                    cost a client X..." beats "10 tips for RAG."
ENGAGEMENT:         Respond to every comment in the first 6 hours.
                    LinkedIn rewards early engagement velocity.
DM CULTURE:         Treat DMs as a primary inbound channel. Most of
                    your 2027 best clients will come from LinkedIn DMs
                    after seeing 3-5 posts.
```

### 33.1 Content categories (drawn from 2026 ammunition)

```
CATEGORY                          POSTS    SOURCE
────────────────────────────────────────────────────────────────
Project showcase                   8        One per project + 2 deeper dives
Technical mini-lessons             10       Pulled from blog posts
Lessons from client work           6-10     Anonymized stories from 2026
Tool reviews / comparisons         4-6      LiteLLM, n8n, Marker, etc.
Career / freelance narrative       3-5      Your story, with specifics
Research-track signals             2-4      Preprint announcement,
                                            workshop submission, paper
                                            recommendations
Engagement plays                   ongoing  Reply to others; original
                                            posts driven by responses
```

Hold ~30 weeks of content (60 posts) in the queue. Drip-feed.

---

## Section 34: Personal Portfolio Site (yacine.dev or similar)

Built locally in Q4 2026 (Phase 6 + Q4 buffer), deployed January 2027
launch day.

### 34.1 Site structure

```
yacine.dev/
  /              Homepage: hero + 6 project cards + "About" link
  /projects/     Project gallery (one card per repo with screenshot, hook)
  /projects/intelai/   Per-project deep page
  /projects/agentkit/
  /projects/docintel/
  /projects/voiceflow/
  /projects/rageval/
  /projects/streampulse/
  /blog/         Blog index
  /blog/persona-routed-rag/   Each blog post (canonical URL)
  /blog/vision-first-doc-ai/
  ...
  /about/        Short bio, what you do, what you've built, contact
  /research/     Preprint + future preprints + reading list
  /now/          "What I'm working on now" — updated quarterly
  /contact/      Email + Cal.com booking link
```

### 34.2 Tech stack for the site

```
Generator:    Astro (static-site, fast, MDX support)
              or Hugo (simpler, faster builds)
              Both are free, both deploy to Vercel/Netlify in 1 command.
Hosting:      Vercel (free for personal projects, instant deploys)
Domain:       Namecheap or Cloudflare Registrar (~$10/year)
Analytics:    Plausible (privacy-first, $9/mo) or Cloudflare Analytics (free)
Email:        Buttondown if you want a newsletter ($9/mo); skip otherwise
Search:       Pagefind (free, client-side, no service to operate)
```

### 34.3 SEO and discoverability

Pick 3-4 long-tail keywords each blog post targets:

```
BLOG POST                              KEYWORDS
─────────────────────────────────────────────────────────────────────
Persona-Routed RAG                     "multi-persona RAG", "role-based RAG",
                                        "RAG persona prompts"
Vision-First Document AI               "vision LLM OCR", "Llama vision invoice",
                                        "Ollama document extraction"
MCP Tool Design Patterns              "MCP server tutorial", "fastmcp tutorial",
                                        "Claude Desktop MCP business intelligence"
Speech-to-Intelligence                "Whisper sales call analysis",
                                        "meeting notes AI extraction"
Multi-Judge LLM Evaluation            "RAG evaluation framework",
                                        "LLM-as-judge consensus", "RAGeval"
Vision-First Multi-Source Aggregation "auction listing aggregator AI",
                                        "vision-first scraper alternative"
```

By month 6 of 2027 these should be ranking for at least their long-tail
queries. Long-tail SEO is the gift that keeps giving.

---

## Section 35: Cold Email Evolution In 2027

Cold email in 2026 was tier-1 outreach (warm leads from your network +
30-50 emails). In 2027 it scales because:
- You have public proof (blog posts, GitHub, preprint)
- Your name is more recognizable in the niche
- Your reply rate jumps from ~5% to ~15-20%

```
2027 CADENCE:        15-20 cold emails per week (up from 5-10 in 2026)
TARGETS:             Same archetypes (Series A/B SaaS, AI consultancies,
                     mid-market verticals) but you can be more selective
HIT RATE:            ~15-20% reply rate, ~5-8% to discovery call,
                     ~2-3% to contract — 3-5x improvement over 2026
TEMPLATES:           Now reference your published material, not just demos
                     "I wrote about this here [link to blog]" hits harder
                     than "Here's a demo URL"
```

### 35.1 The "warmed by content" pattern

Track LinkedIn engagement and convert it to email:

```
1. Someone likes 3+ of your LinkedIn posts over 4 weeks
2. Check their profile: are they a buying-relevant role at a fit company?
3. Send a personalized LinkedIn DM: "Loved your engagement with my posts.
   Are you working on something in [adjacent area]? Happy to share notes."
4. If they engage → move to email for substantive conversation
5. Convert ~20% of warmed leads to discovery calls
```

This is the cycle that makes a strong LinkedIn presence durably valuable —
not the posts themselves, but the inbound that posts unlock.

---

## Section 36: Research-Program Outreach Calendar (Q2 2027)

The freelance + content engine running on autopilot, you turn to research-
degree applications. Outreach starts April-May 2027.

```
APRIL 2027:
  - Identify 10-15 target research programs (PhD, MS, fellowships)
  - For each: identify 2-3 faculty whose work aligns with your preprint
  - Draft personalized outreach email per faculty (informational chat ask)

MAY-JUNE 2027:
  - Send 20-30 faculty outreach emails (5/week to manage replies)
  - Expect 30-40% reply rate (your preprint + projects are credibility)
  - Have 5-10 informational chats (Zoom, 30 min each)
  - These are NOT application asks. They are "I'm exploring research
    programs, your work resonates, would love your perspective on..."

JULY-AUGUST 2027:
  - Based on chats, narrow to 5-8 application targets
  - Begin SOP drafts (3-4 versions, tailored per program)
  - Request reference letters from:
      • 2 academic-aligned people (preprint reviewers, faculty contacts)
      • 1-2 clients ("research-aligned freelance" engagements from 2026
        per Section 14)
      • Possibly 1 open-source community contact

SEPTEMBER-NOVEMBER 2027:
  - Submit applications
  - Continue freelance income (now at premium rates)
  - Start preprint #2 (drafted alongside applications)

DECEMBER 2027:
  - Wait. Process feedback if any.
  - Begin preprint #2 polish phase
  - Plan 2028 contingencies (continue freelance, take research program,
    take fellowship, etc.)
```

---

## Section 37: 2027 Quarterly Outcome Targets

```
Q1 2027 (Jan-Mar):   Launch week. 6 blog posts live. Preprint submitted.
                      LinkedIn cadence established.
                      Target outcomes:
                        + 1500-3000 LinkedIn connections (network triples)
                        + 1 HN front-page (likely RAGeval or AgentKit)
                        + Preprint announcement gets 50-200 cites/shares
                        + Freelance: $20-40k earned (rate has risen)

Q2 2027 (Apr-Jun):   Research outreach. 1-2 workshop submissions.
                      Continued LinkedIn cadence.
                      Target outcomes:
                        + 5-10 informational research chats
                        + 1 workshop acceptance (50/50 odds)
                        + Freelance: $20-40k earned

Q3 2027 (Jul-Sep):   Application prep. Quality-over-quantity client work.
                      Target outcomes:
                        + SOPs drafted and reviewed
                        + Reference letters secured
                        + Freelance: $15-30k earned (reduced load)

Q4 2027 (Oct-Dec):   Submit applications. Preprint #2 in progress.
                      Target outcomes:
                        + 5-8 research program applications submitted
                        + Preprint #2 draft 70-80% complete
                        + Freelance: $15-25k earned

TOTAL 2027:           $70-135k freelance income + research-app
                      position secured for 2028
```

---

## Section 38: The Long Game (2028 And Beyond)

What 2026's minimalism + 2027's launch buy you in 2028:

```
2028 OPTIONS (mutually optional):

OPTION A — Continue freelance, build a small product
  Rate at $130-180/hr inbound (LinkedIn + referrals).
  Convert 1-2 of your 6 projects into a paid product
  (RAGeval Pro? DocIntel managed service?).
  Capacity: 20-25 hrs/week + product work.
  Annual income: $150-300k.

OPTION B — Accept research program (PhD / MS / fellowship)
  Reduce freelance to maintenance level (1-2 retainer clients).
  Full-time research, draws on your 6 projects as platform.
  Annual income: $30-50k stipend, but credentials compound.

OPTION C — Lead AI engineering at a startup
  Inbound recruiting from CTOs you've talked to in 2026-27.
  Full-time AI engineering or "Head of AI" at Series A/B.
  Annual comp: $180-280k base + equity.

OPTION D — Independent research / fellowship combo
  Anthropic Fellowship, OpenAI Residency, MATS, etc.
  Continue light freelance to maintain optionality.
  Annual income: $60-100k stipend, plus freelance.

OPTION E — Open-source maintainer / advocate role
  Maintain RAGeval + AgentKit, get sponsorship (GitHub Sponsors,
  corporate backers).
  Annual income: $50-120k from sponsorships + light consulting.
```

You don't have to choose now. The plan builds the optionality. **By
end of 2027, all five options are open simultaneously.** That's the
compounding-career outcome the document targets.

---

# PART IX — THE AI-AGENT BUILD PROMPT

---

## Section 30: Complete Codebase Splitting Prompt (For Claude/Cursor)

This is the **entire** splitting prompt, embedded verbatim with the 2026
stack upgrades from Section 4.5 folded in. Copy from the START OF PROMPT
marker to the END OF PROMPT marker. Paste it into Claude Code or Cursor
when you're ready to execute Phase 0, Day 3 of Section 16.1.

**Important:** before running on all 6 projects, run the DocIntel section
alone first (Day 2 of Phase 0) to validate the prompt. If anything breaks,
fix the prompt before running on the remaining 5 projects.

### Pre-prompt context (read this first)

The prompt below produces 6 standalone repositories from the IntelAI
monorepo. It assumes:

- You're running in a directory ABOVE the IntelAI source (so the AI
  agent can read from `./IntelAI/...` and write to sibling directories)
- You have write access to the working directory
- Python 3.11 is available
- You'll add real API keys to `.env` files after the prompt runs
- You'll do the per-project verification (Phase 0 Day 4) yourself, not the
  agent

The prompt is ~600 lines (longer than v1's ~500 because it now includes
2026 stack defaults: LiteLLM, multi-provider config, vision routes for
DocIntel, multi-judge for RAGeval, n8n integration for StreamPulse).

### START OF PROMPT

```
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
5. Creating a requirements.txt with the 2026 stack (see below per project)
6. Creating a Dockerfile for each project
7. Creating a .env.example with the env vars each project needs
8. Creating tests/ with at least 5 smoke tests per project

GLOBAL DEFAULTS (apply to every project unless overridden):
- Python 3.11
- FastAPI for HTTP APIs, uvicorn[standard] as server
- LiteLLM for multi-provider LLM routing (every project depends on litellm)
- python-dotenv for config
- httpx + aiohttp for async HTTP
- pytest for testing
- All code must work with these env vars present:
    LLM_DEFAULT     (e.g. groq/llama-3.3-70b-versatile)
    LLM_REASONING   (e.g. anthropic/claude-sonnet-4-6)
    LLM_JUDGE       (e.g. anthropic/claude-haiku-4-5)
    LLM_LOCAL       (e.g. ollama/llama3.3)
    GROQ_API_KEY, ANTHROPIC_API_KEY, OPENAI_API_KEY (optional, code degrades)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PROJECT 1: IntelAI (refactor the existing repo in place)
Goal: Clean, deployable version of the main platform

KEEP all files in the repo. Make these specific changes:

  a) In frontend/: run `npm install recharts` and update package.json
  b) In frontend/src/pages/AnalyticsPage.jsx: replace SVG bars with
     Recharts LineChart.
  c) In frontend/src/pages/ForecastingPage.jsx: replace table-based forecast
     with Recharts AreaChart (actual=green line, forecast=blue dashed,
     upper_ci/lower_ci as shaded band).
  d) In frontend/src/pages/RiskPage.jsx: add Recharts RadarChart of
     risk.components.
  e) In frontend/src/pages/DashboardPage.jsx: add sparkline LineChart
     (height 60) of last 6 KPI values.
  f) In frontend/src/pages/FinancialPage.jsx: replace stub with working
     page (dropdown of statement type, BarChart of line_items).

  g) In tests/test_api.py: expand from 2 tests to 30+ covering auth, chat,
     kpis, insights, ingest, rbac, monitoring, knowledge search.

  h) Replace README.md with a clean version (<200 lines):
     one-line description, what's built, Quick Start (3 commands),
     default credentials, API docs link, live demo URL, architecture
     diagram (ASCII).

  i) Create railway.toml:
       [build] builder = "DOCKERFILE"
       [deploy] startCommand = "python -m uvicorn src.api.server_v2:app
                                  --host 0.0.0.0 --port $PORT --workers 1"
       healthcheckPath = "/health"

  j) ADD 2026 stack upgrades:
     - pip install litellm>=1.55.0 anthropic openai
     - Create src/services/llm_router.py with llm_call(messages, tier=...)
       routing across groq/anthropic/ollama via LiteLLM
     - Update omnismart_chatbot.py to call llm_router.llm_call() instead
       of direct Groq client
     - Create src/services/hybrid_retrieval.py with HybridRetriever class
       (dense via bge-large + sparse via rank_bm25 + RRF + BGE reranker)
     - Add USE_HYBRID_RETRIEVAL env flag (default false in dev, true in prod)
     - Add VECTOR_STORE env flag (chroma | qdrant) with Qdrant as
       documented production option
     - Update requirements.txt with: rank-bm25, FlagEmbedding, qdrant-client,
       litellm, anthropic, openai

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PROJECT 2: AgentKit
Goal: MCP server + multi-framework agent workflow (LangGraph + Claude Agent SDK + CrewAI)

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
      @mcp.resource("kpi://Finance/latest") and similar for 5 other domains
      @mcp.prompt("monthly_executive_briefing") with reusable template
    Entry: if __name__ == "__main__": mcp.run()

  agentkit/workflow.py:
    LangGraph StateGraph (BusinessAnalysisState) with 3 nodes:
      planner_agent: uses litellm with LLM_REASONING (anthropic/claude-sonnet-4-6)
      analyst_agent: uses LLM_DEFAULT (groq/llama-3.3-70b-versatile)
      reporter_agent: uses LLM_REASONING (claude-sonnet-4-6)
    All calls via litellm.acompletion(model=...)
    Public API: def analyze(question: str) -> dict

  agentkit/demos/claude_agent_sdk_demo.py:
    Uses claude_agent_sdk.Agent + MCPServer to call the same 6 tools
    via Claude Agent SDK orchestration.

  agentkit/demos/crewai_demo.py:
    Uses CrewAI to wrap the same MCP tools as @tool decorators and
    defines a 3-agent crew (Researcher / Analyst / Reporter).

  agentkit/research/dspy_experiment.py:
    DSPy module framing planner→analyst→reporter as compilable program.
    BootstrapFewShot training over held-out business questions.

  agentkit/requirements.txt:
    fastmcp>=0.4.0
    langgraph>=0.2.0
    langchain>=0.3.0
    litellm>=1.55.0
    anthropic>=0.40.0
    groq>=0.11.0
    openai>=1.55.0
    crewai>=0.86.0
    dspy-ai>=2.5.0
    psycopg[binary]>=3.1.18
    pandas>=2.2.3
    numpy>=2.1.3
    scikit-learn>=1.5.2
    chromadb>=0.5.18
    sentence-transformers>=3.1.1
    python-dotenv>=1.0.1
    claude-agent-sdk>=0.1.0   # if available; otherwise comment out

  agentkit/README.md:
    Title: "AgentKit — MCP Server for Business Intelligence Agents"
    Sections: What It Does, Tools (table), Resources, Prompts, Quick Start,
              Claude Desktop Setup, LangGraph Workflow, Claude Agent SDK,
              CrewAI Example, DSPy Experiment (research)
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
    10+ tests for all 6 MCP tools, resources, prompts (mock DB if needed)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PROJECT 3: DocIntel
Goal: Vision-first document AI pipeline (the 2026 leading approach)

CREATE new directory: docintel/

EXTRACT from IntelAI:
  src/services/ocr_enhancement.py  → docintel/services/ocr_extractor.py
  src/services/ocr/main.py         → docintel/services/tesseract_service.py
  src/integrations/camera.py       → docintel/services/camera.py
  src/core/logger.py               → docintel/core/logger.py
  src/core/config.py               → docintel/core/config.py (slim)

UPDATE imports as above.

CREATE new files:

  docintel/api.py:
    GET  /health
    POST /extract (file + route: vision_premium|vision_local|ocr_fallback)
    POST /classify (file → doc_type only, fast)
    POST /classify-image (image + categories list → category + confidence)
                       ← this is the vision-first object classification
                          endpoint for auction-listing / inventory use cases
    POST /extract-tables (PDF → tables list, via pdfplumber + Marker)
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
    auction_listing, default.
    Supports both Claude Sonnet 4.6 Vision and Ollama Llama 3.2 Vision.

  docintel/services/marker_extractor.py:
    Uses marker library to convert PDF → Markdown for the secondary route.

  docintel/services/llm_extractor.py:
    LLMExtractor class with async extract(text, doc_type) for OCR-fallback
    route. Uses LLM_REASONING tier by default.

  docintel/services/batch_processor.py:
    BatchProcessor with process / get_status / get_results methods.

  docintel/demo/index.html:
    Single-page drag-and-drop demo (dark theme, vanilla JS, ~200 lines).
    Toggle between routes (vision_premium | vision_local | ocr_fallback).
    Shows: doc_type badge, confidence, processing time, structured JSON.

  docintel/demo/classify_image.html:
    Separate page demonstrating /classify-image for auction-listing
    classification. Drag an image + select category list → see result.
    This is the Equipment Sourcing pattern demo.

  docintel/eval/run_eval.py:
    Eval harness comparing routes A/B/C on a benchmark dataset.

  docintel/requirements.txt:
    fastapi>=0.115.0
    uvicorn[standard]>=0.32.0
    python-multipart>=0.0.12
    litellm>=1.55.0
    anthropic>=0.40.0
    groq>=0.11.0
    openai>=1.55.0
    pdfplumber>=0.11.0
    pytesseract>=0.3.10
    pillow>=10.1.0
    pypdf>=4.3.1
    marker-pdf>=0.2.0          # for high-quality PDF→Markdown
    surya-ocr>=0.5.0           # for layout-aware OCR fallback
    python-dotenv>=1.0.1
    pandas>=2.2.3
    aiofiles>=24.1.0

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
  src/integrations/tts.py          → voiceflow/services/tts_service.py
  src/core/logger.py               → voiceflow/core/logger.py

UPDATE imports.

CREATE new files:

  voiceflow/services/whisperx_service.py:
    Uses whisperx for faster-whisper + alignment + pyannote diarization.
    Falls back gracefully if pyannote not installed.

  voiceflow/services/transcription_router.py:
    Routes transcribe() calls to: LOCAL_WHISPERX | GROQ_WHISPER |
    DEEPGRAM | ASSEMBLYAI based on provider parameter or env default.

  voiceflow/services/meeting_analyzer.py:
    MeetingAnalyzer class with analyze_meeting, analyze_sales_call,
    analyze_support_call, analyze_interview, general_analysis methods.
    Each picks LLM model per ANALYSIS_MODELS dict:
      meeting:     LLM_DEFAULT (groq/llama-3.3-70b-versatile)
      sales_call:  LLM_REASONING (anthropic/claude-sonnet-4-6)
      support_call: LLM_JUDGE (anthropic/claude-haiku-4-5)
      interview:   LLM_REASONING
      general:     LLM_DEFAULT
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
    Browser-recording demo (MediaRecorder API), 3-second countdown,
    waveform visualization, sample-audio buttons, analysis-type radio.
    ~250 lines vanilla JS.

  voiceflow/demo/realtime.html:
    OpenAI Realtime API voice agent demo (WebRTC).
    Talks to AgentKit MCP tools via bridge.

  voiceflow/requirements.txt:
    fastapi>=0.115.0
    uvicorn[standard]>=0.32.0
    python-multipart>=0.0.12
    litellm>=1.55.0
    anthropic>=0.40.0
    groq>=0.11.0
    openai>=1.55.0
    edge-tts>=6.1.9
    faster-whisper>=1.0.3
    whisperx>=3.1.0
    pyannote.audio>=3.1.0       # may need HF token
    python-dotenv>=1.0.1
    requests>=2.32.3
    aiohttp>=3.10.0
    deepgram-sdk>=3.7.0        # optional, used if DEEPGRAM_API_KEY set
    assemblyai>=0.30.0          # optional

  voiceflow/README.md:
    Hero: "Speech → structured intelligence. Browser-recording demo.
           4 providers, 5 analysis types, real-time voice agent."
    Architecture ASCII: Audio → Whisper → LLM Intelligence → JSON
    Use Cases table.

  voiceflow/.env.example:
    LLM_DEFAULT=groq/llama-3.3-70b-versatile
    LLM_REASONING=anthropic/claude-sonnet-4-6
    LLM_JUDGE=anthropic/claude-haiku-4-5
    GROQ_API_KEY=...
    ANTHROPIC_API_KEY=...
    OPENAI_API_KEY=...
    HF_TOKEN=...                # for pyannote
    DEEPGRAM_API_KEY=...        # optional
    ASSEMBLYAI_API_KEY=...      # optional

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
      score_groundedness_consensus(answer, context) → dict
        Multi-judge across [claude-haiku-4-5, groq llama 3.3 70b, gpt-5-mini]
        Returns: {consensus, stdev, judges:[...], flag_for_review:bool}
      score_faithfulness(answer, chunks) → float
      calculate_cost(tokens, model, input_ratio=0.7) → float (USD)
        GROQ_PRICES + ANTHROPIC_PRICES + OPENAI_PRICES dicts
      score_interaction(query, answer, chunks, tokens_used, latency_ms,
                        model, persona=None) → dict
    Embeddings: BAAI/bge-large-en-v1.5 default; optional MiniLM, BGE-M3.

  rageval/store.py:
    SQLite default (~/.rageval/rageval.db); Postgres+pgvector optional.
    init_rageval_table, log_interaction, get_metrics, get_query_log,
    get_cost_report functions.

  rageval/api.py:
    GET  /health
    POST /eval/log
    POST /eval/score (no storage)
    GET  /eval/metrics?days=7
    GET  /eval/queries?limit=50&needs_review=true
    GET  /eval/cost-report?days=30
    GET  /eval/alerts
    POST /eval/retrieval-bench (benchmark a configured retrieval strategy)
    POST /eval/embedding-comparison (compare embedding models on relevance)

  rageval/decorator.py:
    @track(model="...") decorator wrapping any function.
    Auto-logs to RAGeval store.

  rageval/otel_exporter.py:
    OpenTelemetry / OpenLLMetry export when RAGEVAL_OTEL_ENDPOINT is set.

  rageval/dspy_integration.py:
    Hook to log DSPy compilation runs (program, candidates, winner, score).

  rageval/cli.py:
    rageval init (creates DB), rageval serve (starts API).
    Entry point in pyproject.toml.

  rageval/dashboard/ (React app):
    3 tabs: Overview | Query Log | Cost Report
    Recharts charts. Dark theme. Fetches from RAGeval API.

  rageval/requirements.txt:
    fastapi>=0.115.0
    uvicorn[standard]>=0.32.0
    litellm>=1.55.0
    anthropic>=0.40.0
    groq>=0.11.0
    openai>=1.55.0
    sentence-transformers>=3.1.1
    FlagEmbedding>=1.3.0
    scikit-learn>=1.5.2
    numpy>=2.1.3
    psycopg[binary]>=3.1.18    # optional for pgvector tier
    pgvector>=0.3.0             # optional
    python-dotenv>=1.0.1
    opentelemetry-api>=1.27.0
    opentelemetry-sdk>=1.27.0
    opentelemetry-exporter-otlp>=1.27.0
    dspy-ai>=2.5.0              # optional integration

  rageval/README.md:
    Hero: "Drop-in LLMOps observability. Self-hosted. SQLite-default.
           Persona-aware. Multi-judge consensus."
    60-second pitch (decorator example).
    Comparison table vs Phoenix, Langfuse, TruLens, Helicone (be honest).
    Quick Start (3 commands).
    Integration guide (FastAPI + LangChain).
    Dashboard preview (3 screenshots).

  rageval/.env.example:
    RAGEVAL_STORE=sqlite                 # or "postgres"
    POSTGRES_URL=postgresql://...        # if postgres
    RAGEVAL_OTEL_ENDPOINT=http://localhost:4317  # optional
    LLM_JUDGE=anthropic/claude-haiku-4-5
    LLM_DEFAULT=groq/llama-3.3-70b-versatile
    GROQ_API_KEY=...
    ANTHROPIC_API_KEY=...
    OPENAI_API_KEY=...

  rageval/pyproject.toml (PyPI-publishable):
    [project]
    name = "rageval"
    version = "0.1.0"
    [project.scripts]
    rageval = "rageval.cli:main"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PROJECT 6: StreamPulse
Goal: Real-time multi-source data pipeline (with n8n + vision composition)

CREATE new directory: streampulse/

EXTRACT from IntelAI:
  src/services/realtime_pipeline.py    → streampulse/pipeline/classifier.py
  src/services/data_ingestion_manager.py → streampulse/pipeline/ingestion.py
  src/integrations/n8n.py               → streampulse/connectors/n8n.py
  src/core/config.py                    → streampulse/core/config.py (slim)
  src/core/logger.py                    → streampulse/core/logger.py
  src/services/pg_store.py              → streampulse/store.py (slim)

UPDATE imports. SIMPLIFY store.py: keep only KPI store functions.

CREATE new files:

  streampulse/api.py:
    GET  /health
    POST /ingest/json
    POST /ingest/csv
    POST /ingest/email
    POST /webhook/{source_name}         # with HMAC verify
    POST /webhook/{source}/with-vision  # composes with DocIntel classify-image
    GET  /pipeline/status
    GET  /pipeline/history
    WS   /live
    GET  /live/sse                       # Server-Sent Events alternative

  streampulse/connectors/webhook_receiver.py:
    HMAC verification (X-Signature-256), payload parsing, pipeline routing.

  streampulse/connectors/n8n/
    README.md (how to integrate)
    n8n_node.json (custom n8n community node definition)
    workflows/
      auction_aggregator.json
      invoice_intake.json
      crm_sync.json

  streampulse/ingestion/dlt_sources.py:
    dlt-based declarative sources: gmail_source, gsheet_source,
    webhook_source.

  streampulse/orchestration/prefect_flow.py:
    Prefect 3 flow with @task(retries=3) and @flow definitions
    for the full pipeline.

  streampulse/classifier.py (UPGRADED):
    classify(content, fast_only=False) → dict
    Fast path: keyword matching (existing logic).
    Fallback: embedding similarity vs domain prototypes (bge-large).
    Last fallback: Claude Haiku 4.5 zero-shot classification via litellm.

  streampulse/dashboard/ (React):
    LiveDashboard.jsx — Recharts LineChart + PieChart, live record feed,
    domain colors, dark theme, WebSocket + SSE fallback.

  streampulse/requirements.txt:
    fastapi>=0.115.0
    uvicorn[standard]>=0.32.0
    python-multipart>=0.0.12
    litellm>=1.55.0
    anthropic>=0.40.0
    groq>=0.11.0
    psycopg[binary]>=3.1.18
    pgvector>=0.3.0
    pandas>=2.2.3
    numpy>=2.1.3
    sentence-transformers>=3.1.1
    aiohttp>=3.10.0
    httpx>=0.27.0
    python-dotenv>=1.0.1
    requests>=2.32.3
    dlt>=0.5.0
    prefect>=3.0.0
    duckdb>=1.1.0                # optional for analytics queries

  streampulse/README.md:
    Hero: "Real-time business data pipeline. 6+ source types,
           live dashboard, first-class n8n integration."
    Supported Sources table.
    Architecture ASCII.
    n8n integration walkthrough.

  streampulse/.env.example:
    POSTGRES_URL=postgresql://...
    LLM_DEFAULT=groq/llama-3.3-70b-versatile
    LLM_JUDGE=anthropic/claude-haiku-4-5
    GROQ_API_KEY=...
    ANTHROPIC_API_KEY=...
    WEBHOOK_SECRET=change_me

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EXECUTION ORDER:
1. ALWAYS start with Project 3 (DocIntel) as the prompt-validation test.
   If DocIntel extraction works cleanly (imports resolve, uvicorn starts,
   /classify endpoint responds), proceed to the others.
2. Then Project 1 (IntelAI refactor) — edits in place, smaller scope.
3. Then Projects 2, 4, 5, 6 in any order (they're independent).

QUALITY REQUIREMENTS FOR EACH PROJECT:
- All import paths work from project root (NO `from src.*` left)
- Every new file has a module docstring
- Every class has a docstring
- Every public async function has docstring with Args / Returns
- requirements.txt is minimal (only what that project needs)
- README is accurate (only claim what code actually does)
- .env.example has every required env var with a placeholder
- Dockerfile builds without error
- pytest tests/ has at least 5 smoke tests per project

DO NOT:
- Overclaim features not implemented
- Leave broken imports
- Create circular dependencies between projects
- Include unused dependencies
- Hardcode any credentials
- Skip the 2026 stack upgrades (LiteLLM, multi-provider env vars, etc.)

OUTPUT: Create all 6 project directories. Print a summary at the end:
  - Files created per project
  - Tests passing per project
  - Any TODOs that need human follow-up
```

### END OF PROMPT

### Post-prompt verification (do not skip)

After the agent runs:

1. For each of the 6 projects, run:
   ```
   cd <project>
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   pytest tests/ -v
   uvicorn api:app --port 8001 &   # for FastAPI projects
   curl http://localhost:8001/health
   ```
2. Diff your `.env.example` files against what each project's code actually
   reads — `grep -r "os.getenv\|os.environ" src/ | grep -oE '"[A-Z_]+"'`
   should match `.env.example` 1:1.
3. Run the splitting prompt's "Output Summary" against each project's
   actual state — does what the prompt claimed it created actually exist?
4. If any project fails verification, fix the prompt and re-run for that
   project specifically (do not blanket re-run).

This validation is Phase 0 Day 4 of Section 16.1. Block on it.

---

# APPENDIX

---

## Quick Reference: Project Source Map

```
FROM IntelAI-master/          → TO PROJECT
───────────────────────────────────────────────────────────────────
src/api/server_v2.py              → P1: Keep (refactor in place)
src/services/omnismart_chatbot.py → P1: Keep
src/services/pg_store.py          → P1: Keep | P2: Copy | P6: Slim copy
src/services/advanced_chatbot.py  → P1: Keep
src/services/insights.py          → P1: Keep | P2: Copy
src/services/forecasting.py       → P1: Keep | P2: Copy
src/services/ocr_enhancement.py   → P3: Copy (primary)
src/services/realtime_pipeline.py → P6: Copy (primary)
src/services/data_ingestion_*     → P6: Copy
src/services/voice/main.py        → P4: Copy (primary)
src/services/ocr/main.py          → P3: Copy
src/integrations/dispatcher.py    → P4: Voice + TTS partial copy
src/integrations/tts.py           → P4: Copy
src/integrations/n8n.py           → P6: Copy
src/integrations/camera.py        → P3: Copy
src/core/config.py                → P2,P3,P4,P5,P6: Slim copy each
src/core/monitoring.py            → P5: Copy
src/core/performance.py           → P5: Copy
src/core/logger.py                → All projects: Copy
src/core/jwt_auth.py              → P1: Keep only
src/core/crypto.py                → P1: Keep only
frontend/                         → P1: Keep
db/schema.sql                     → P1: Keep | P2: Copy
enhanced_synthetic_dataset/       → P1: Keep
```

---

## Quick Reference: Channel × Project × Template Matrix

```
                    P1 OMS   P2 AK   P3 DI   P4 VF   P5 RE   P6 SP
─────────────────────────────────────────────────────────────────
UPWORK              PRIMARY  TER     PRIMARY SEC     SEC     TER
  Template          T1, T3   T2      T3      T4      T5      T6

OPEN-SOURCE         SEC      PRIMARY SEC     SEC     PRIMARY TER
  PyPI?             YES      maybe   no      no      YES     no
  GitHub launch     no       YES     YES     YES     YES     YES

BLOG POST           POST-1   POST-3  POST-2  POST-4  POST-5  POST-6

COLD EMAIL          SEC      PRIMARY SEC     TER     SEC     PRIMARY
  Target            CTOs     AI agencies CTOs (vert) SaaS    Eng leaders Data dirs

LINKEDIN 2027       SEC      PRIMARY SEC     SEC     PRIMARY SEC
  (use the
  recorded
  content in 2027)

RESEARCH OUTPUT     2026-1   maybe   2027    maybe   2026-1  no
  Preprint/paper

PRIMARY CHANNEL     Upwork   GitHub  Upwork  Upwork  GitHub  Cold email
```

---

## Quick Reference: Rates By Channel

```
CHANNEL                 STARTING  AT 5 REVIEWS  AT 20 REVIEWS
─────────────────────────────────────────────────────────────
Upwork cold             $65/hr    $85/hr        $110/hr
Upwork warm             $75/hr    $95/hr        $130/hr
Cold email              $85/hr    $110/hr       $150/hr
LinkedIn (2027)         $95/hr    $130/hr       $170/hr
Research-aligned        Variable  Variable      Variable
  contract              ($100-150/hr typical, rate secondary to credential)
```

---

## Quick Reference: Niche → Project → Template

```
CLIENT SEARCHES FOR           USE PROJECT     USE TEMPLATE
─────────────────────────────────────────────────────────────
RAG, LangChain, chatbot       IntelAI     Template 1
MCP server, agent orchestr.   AgentKit        Template 2
OCR, PDF, document AI, invoice DocIntel        Template 3
Whisper, STT, voice AI        VoiceFlow       Template 4
LLMOps, observability, eval   RAGeval         Template 5
ETL, webhook, real-time       StreamPulse     Template 6
```

---

## Quick Reference: Capacity Matrix

```
ACTIVE CLIENTS    CLIENT TIME   PIPELINE TIME    NEW PROPOSALS
─────────────────────────────────────────────────────────────
0                 0%            100%             10/day target
1                 50%           50%              5/day target
2                 70%           30%              3/day target
3                 90%           10%              1/day target
4+                100%          0%               STOP — focus delivery
```

---

## Glossary

- **MCP** — Model Context Protocol. Anthropic's open standard for letting
  AI agents call external tools. The fastest-moving protocol in AI tooling
  as of 2026.
- **RAG** — Retrieval-Augmented Generation. Retrieving relevant documents
  before LLM generation to improve factuality.
- **Groundedness** — How well an LLM answer is supported by retrieved
  context. A core RAG evaluation metric.
- **Persona-routed RAG** — Same retrieval, different system prompts and
  data scoping per role/persona. Your differentiator in IntelAI.
- **LLMOps** — Operations and monitoring for LLM-based systems. The DevOps
  of the LLM era.
- **Phoenix / Langfuse / TruLens / Helicone** — LLMOps observability tools.
  RAGeval competes with these as a self-hosted, drop-in alternative.
- **fastmcp** — Python library for building MCP servers (anthropic-affiliated).
- **LangGraph** — Library for building stateful multi-agent workflows.
- **Persona** — In IntelAI, one of 9 C-suite roles (CEO, CFO, CTO, COO,
  CHRO, ESG Officer, Risk Manager, Business Analyst, General User) each
  with custom system prompts and data scoping.
- **arXiv preprint** — A research paper publicly released before formal
  peer review. Citation-worthy. Free to publish.
- **Workshop paper** — A peer-reviewed paper accepted to a topical workshop
  at a major conference. Lower bar than main-conference acceptance, higher
  credibility than blog post.
- **Connects** — Upwork's internal currency. Each proposal costs Connects.
- **Top Rated** — Upwork status given after consistent strong reviews.

---

## Final Note

This is your execution plan. It's grounded in your actual codebase, your
actual goals, and the actual market reality as of May 2026.

It accommodates three things at once:
- **Earning money in 2026 on Upwork** (your stated primary goal)
- **Preparing for 2027 LinkedIn launch + multi-channel expansion**
- **Building research credentials for late-2027 program applications**

The plan is sequential not parallel, 18 weeks not 12, multi-channel not
Upwork-only, and honest about cost and risk.

You don't need to be Twitter-famous. You don't need to ship six things in
three months. You need to ship one thing well, validate the market, ship
the next thing well, validate again, and compound.

That's it. That's the whole strategy.

---

*End of Document v2.0*

*Built from a real codebase audit. Every line count was verified.*
*Every claim about the code is checkable in the repo.*
*Every step in the timeline is achievable for one focused person working alone.*
