# IntelAI

[![CI](https://github.com/Yacine-ai-tech/IntelAI/actions/workflows/ci.yml/badge.svg)](https://github.com/Yacine-ai-tech/IntelAI/actions/workflows/ci.yml)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/intelai.svg)](https://pypi.org/project/intelai/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://python.org)

**Persona-aware AI analytics and RAG copilot.** A nine-persona, role-scoped analytics
assistant with hybrid retrieval, a lightweight knowledge graph for multi-hop queries, classical
forecasting, and board-ready exports, over 146 curated KPIs.

**Live demo:** https://intelai.ysiddo-ai-projects.app — password-less role login (demo mode).
The backend runs on demand; the first request after idle may take up to a minute. Self-hosting
instructions: [SELF_HOSTING.md](SELF_HOSTING.md).

## Features

| Area | Detail |
|---|---|
| Nine-persona RAG copilot | CEO, CFO, CTO, COO, CHRO, ESG, Risk, Analyst, Assistant — role-scoped data, WebSocket streaming, source citations |
| GraphRAG-lite | A multi-hop entity graph for cross-domain queries (`USE_GRAPH_RAG=true`) |
| Hybrid retrieval | Dense embeddings + BM25 + Reciprocal Rank Fusion + a cross-encoder reranker, degrading gracefully when a component is unavailable |
| Answer-block structuring | The backend parses LLM markdown into typed blocks (heading, KPI, list, quote, code) |
| 146 curated KPIs | Finance, HR, IT, Operations, Logistics, ESG, Growth — 78-month history, 7 benchmarking scenarios |
| ML forecasting | Monte Carlo forecasting with confidence bands |
| Data export/ingest | PDF, Excel, CSV, and JSON export; CSV and document ingestion |
| Auth and RBAC | JWT authentication, role-based pages, per-persona data scoping, an audit log |
| Admin governance | User management, role viewer, scenario switcher, vector-store reindexing |
| Multi-provider LLM | OpenAI-compatible providers via LiteLLM, configured through `LLM_ENDPOINT` |
| Bilingual | Full English and French UI and copilot responses |

## Architecture

```
React + Vite (Recharts, TanStack Query, i18n)     → Vercel / Netlify
        │  HTTP / WebSocket  /api/v1/*
FastAPI  (src/api/server.py)
  auth · chat (9 personas) · KPIs · insights · forecasting · admin
        │
   PostgreSQL (Neon)             LLM (OpenAI-compatible via LiteLLM)
   KPIs · auth · sessions ·      GraphRAG-lite · hybrid retrieval ·
   vectors (pgvector, opt-in)    BGE reranker · BM25
```

## Quick Start

**Prerequisites:** Python 3.11, Node 18+, a Postgres URL, and a `GROQ_API_KEY`.

```bash
git clone https://github.com/Yacine-ai-tech/IntelAI.git
cd IntelAI
cp .env.example .env   # fill in POSTGRES_URL, GROQ_API_KEY, SECRET_KEY — see SELF_HOSTING.md

# Backend (port 8000 — tables and seed data are created automatically)
pip install -r requirements.txt
python main.py

# Frontend (port 5173, proxies /api to :8000)
cd frontend && npm install && npm run dev
```

Default login: `admin` / `admin123` — change after first login.

**Docker:**

```bash
docker compose -f docker-compose.dev.yml up --build   # app only, uses .env's database
docker compose up --build                              # app plus a bundled Postgres
```

## Configuration

Every variable and its default is documented in `.env.example`. The ones most commonly
adjusted:

| Variable | Required | Description |
|---|---|---|
| `POSTGRES_URL` | Yes | Neon, Render, or local Postgres |
| `GROQ_API_KEY` | Yes | Default-tier LLM provider key |
| `SECRET_KEY` | Yes | JWT signing key |
| `REQUIRE_INTERNAL_TOKEN` | No | Set `false` for standalone self-hosting — see [SELF_HOSTING.md](SELF_HOSTING.md) |
| `ANTHROPIC_API_KEY` | No | Reasoning-tier LLM (CEO/CFO/CTO/Risk personas); falls back to Groq if unset |
| `LLM_DEFAULT` / `LLM_REASONING` / `LLM_JUDGE` | No | LiteLLM model IDs per tier, for any provider LiteLLM supports |
| `USE_GRAPH_RAG` | No | `true` enables GraphRAG-lite multi-hop retrieval |
| `USE_HYBRID_RETRIEVAL` | No | `true` enables dense + BM25 + RRF + reranker |
| `VECTOR_STORE` | No | `chroma` (dev, default), `pgvector`, or `qdrant` (production) |
| `AUDIO_PROCESSOR_URL` / `DOC_PROCESSOR_URL` | No | Pluggable audio/document processors — for example, a VoiceFlow or DocIntel instance |
| `INGEST_WEBHOOK_SECRET` | No | Enables the HMAC-signed `/api/v1/webhook/{source}` ingestion path |

## Key API Endpoints

```
/health  ·  /api/docs
POST /api/v1/auth/login          GET /api/v1/auth/me
POST /api/v1/chat                WS  /api/v1/ws/chat        GET /api/v1/personas
POST /api/v1/chat/async          GET /api/v1/chat/{job_id}  (async job+poll form for slow turns behind a timeout-limited proxy)
GET  /api/v1/kpis[/periods|/metrics|/categories]
GET  /api/v1/insights/{health,risk,summary,anomalies}
POST /api/v1/forecast            GET /api/v1/glossary
POST /api/v1/data/export         POST /api/v1/ingest/{metrics,csv,document}
GET  /api/v1/admin/{users,roles,audit,scenario}
```

Full interactive reference at `/api/docs`.

## Tests

```bash
pytest tests/ -q                        # fast unit suite — no database or LLM keys needed
pytest tests/test_smoke.py -q           # 5 zero-dependency smoke checks
pytest tests/test_api.py -q             # unit-marked subset of auth/RBAC/endpoint checks
pytest tests/test_chat.py -q            # unit-marked subset of chat/answer-block checks
pytest tests/ -o addopts="" -q          # full suite, including database-dependent integration tests
```

`pytest.ini` restricts the default run to unit-marked tests (`addopts = -m "unit"`), matching
CI's Unit Tests job, which needs no database. The full suite (42 checks in `test_api.py` alone)
also includes integration-marked tests requiring a reachable `POSTGRES_URL`/`TEST_POSTGRES_URL`;
run with `-o addopts=""` to lift the default filter.

## Benchmarking Scenarios

IntelAI provides seven seeded, deterministic, benchmark-calibrated environments (78 months ×
7 domains × 146 metrics, formula-derived where a real formula applies — see
[DATA_SEEDING.md](DATA_SEEDING.md)) for evaluating RAG retrieval accuracy and forecasting
models under structural stress. Selectable via the Admin → Scenarios tab, or the API directly
(`POST /api/v1/admin/scenario/async`, then poll `GET /api/v1/admin/scenario/{job_id}`):

| Scenario | Research application | Description |
|---|---|---|
| `healthy` | Baseline RAG evaluation | Reverts to the real baseline, removing any active scenario overlay |
| `declining_financial` | Trend reversal | Revenue contraction and margin compression; tests forecast adaptability |
| `high_churn_crisis` | Lagging indicators | Customer retention failure; tests cross-domain correlation (Growth vs. Finance) |
| `operational_meltdown` | Volatility stress | OEE collapse and quality failures; introduces severe noise to operational metrics |
| `talent_crisis` | Sentiment impact | High attrition and open-requisition spike; evaluates People-to-Operations efficiency lag |
| `cybersecurity_breach` | Shock event | Security incident; step-function disruption in SLA/SLO metrics |
| `esg_compliance_failure` | Policy violation | Governance failures and emissions spike; tests multi-hop entity reasoning |

Every scenario also carries a short cross-domain cascade (IT → Logistics/Operations → Growth →
Finance, mirroring how a real incident's financial impact lags its root cause) — see
`DATA_SEEDING.md` §4 for the full methodology.

For the reasoning behind the retrieval, evaluation, graph, and forecasting design choices, see
[RESEARCH.md](RESEARCH.md). For measured results — a live production RAG evaluation, an
out-of-sample forecast backtest, and a knowledge-graph coverage measurement — see
[BENCHMARK.md](BENCHMARK.md).

## Deploy

IntelAI deploys as one containerized service — build the included `Dockerfile` and run it on
any host that honors `$PORT` (a VPS with Docker Compose, Fly.io, Railway, Render, and similar),
set the environment variables above, and attach a managed Postgres instance. Deploy the
frontend separately (Vercel, Netlify, or as static files) with `VITE_API_BASE_URL` pointing to
the backend, and keep `VITE_USE_WS=false` in production to use the resilient `/chat/async`
job-and-poll path by default. See [SELF_HOSTING.md](SELF_HOSTING.md) for a full walkthrough.

## License

Open-source under the AGPL-3.0 License, free for researchers, students, and open-source use.
AGPLv3 requires that any proprietary network service built on modified code also open-source
its backend. A commercial license — for closed-source use or enterprise features such as SSO,
Active Directory integration, and custom VPC deployment — is available on request.

## Anonymous Telemetry

IntelAI can send an anonymous, GDPR-compliant startup ping so a deployment's operator can
count distinct installs. This is opt-in only: it sends nothing unless `TELEMETRY_URL` is set
to a collector the operator controls, so a fresh clone never phones home by default. Only the
project name and a startup-event timestamp are collected — no PII, API keys, or user data.
`TELEMETRY_OPT_OUT=true` disables it explicitly regardless of `TELEMETRY_URL`.

<!-- Scarf Analytics Pixel -->
<img referrerpolicy="no-referrer-when-downgrade" src="https://static.scarf.sh/a.png?x-pxid=ada53b5b-d56f-447f-b5ab-a65a061b7d5a" />
