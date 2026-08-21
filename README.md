# IntelAI

[![CI](https://github.com/Yacine-ai-tech/IntelAI/actions/workflows/ci.yml/badge.svg)](https://github.com/Yacine-ai-tech/IntelAI/actions/workflows/ci.yml)


[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)


[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/intelai.svg)](https://pypi.org/project/intelai/)

> **Persona-Aware AI Analytics & RAG Copilot** — 9-persona, role-scoped copilot with
> GraphRAG-lite retrieval, ML forecasting, bilingual (EN/FR) UI, and board-ready exports.

[![CI](https://github.com/Yacine-ai-tech/IntelAI/actions/workflows/ci.yml/badge.svg)](https://github.com/Yacine-ai-tech/IntelAI/actions)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://python.org)

**Live demo:** https://intelai.ysiddo-ai-projects.app · password-less role login (DEMO_MODE).
First request may take ~60 s to wake the on-demand backend.
> Self-hosting: see [SELF_HOSTING.md](SELF_HOSTING.md).

---

## Features

| Area | Detail |
|---|---|
| **9-persona RAG copilot** | CEO, CFO, CTO, COO, CHRO, ESG, Risk, Analyst, Assistant — role-scoped data, WS streaming, citations |
| **GraphRAG-lite** | Multi-hop entity graph for cross-domain queries (`USE_GRAPH_RAG=true`) |
| **Hybrid retrieval** | Dense + BM25 + RRF + BGE reranker; degrades gracefully |
| **Answer-block structuring** | Backend parses LLM markdown into typed blocks (heading, kpi, list, quote, code) |
| **146 curated KPIs** | Finance, HR, IT, Ops, Logistics, ESG, Growth — 78-month history, 7 benchmarking scenarios |
| **ML forecasting** | Monte Carlo with confidence bands |
| **Data export/ingest** | PDF / Excel / CSV / JSON export; CSV & document ingestion |
| **Auth + RBAC** | JWT, role-based pages, per-persona data scoping, audit log |
| **Admin governance** | User management (create/edit/disable), role viewer, scenario switcher, vector store reindex |
| **Multi-provider LLM** | OpenAI-compatible proxies via LiteLLM (using `LLM_ENDPOINT`) |
| **Bilingual** | Full EN / FR UI and copilot responses |

## Architecture

```
React + Vite (Recharts · TanStack Query · i18n)   → Vercel / Netlify
        │  HTTP / WebSocket  /api/v1/*
FastAPI  (src/api/server.py)
  auth · chat (9 personas) · KPIs · insights · forecasting · admin
        │
   PostgreSQL (Neon)          LLM  (OpenAI-compatible via LiteLLM)
   KPIs · auth · sessions ·   GraphRAG-lite · hybrid retrieval
   vectors (pgvector opt-in)  BGE reranker · BM25
```

## Quickstart

**Prerequisites:** Python 3.11, Node 18+, Postgres URL, `GROQ_API_KEY`.

```bash
git clone https://github.com/Yacine-ai-tech/IntelAI.git
cd IntelAI
cp .env.example .env   # fill POSTGRES_URL, GROQ_API_KEY, SECRET_KEY — see SELF_HOSTING.md

# Backend (port 8000 — tables & seed created automatically)
pip install -r requirements.txt
python main.py

# Frontend (port 5173, proxies /api → :8000)
cd frontend && npm install && npm run dev
```

Default login: **`admin` / `admin123`** — change after first login.

**Docker:**
```bash
docker compose -f docker-compose.dev.yml up --build   # app only (uses .env DB)
docker compose up --build                              # app + bundled Postgres
```

## Configuration (`.env`)

Full reference with every variable and its default lives in `.env.example`. The ones
you're most likely to touch:

| Variable | Required | Description |
|---|---|---|
| `POSTGRES_URL` | ✅ | Neon / Render / local Postgres |
| `GROQ_API_KEY` | ✅ | Default-tier LLM provider key |
| `SECRET_KEY` | ✅ | JWT signing key |
| `REQUIRE_INTERNAL_TOKEN` | ⬜ | Set `false` for standalone self-hosting — see [SELF_HOSTING.md](SELF_HOSTING.md) |
| `ANTHROPIC_API_KEY` | ⬜ | Reasoning-tier LLM (CEO/CFO/CTO/Risk personas); falls back to Groq if unset |
| `LLM_DEFAULT` / `LLM_REASONING` / `LLM_JUDGE` | ⬜ | LiteLLM model IDs per tier (any provider LiteLLM supports) |
| `USE_GRAPH_RAG` | ⬜ | `true` = GraphRAG-lite multi-hop |
| `USE_HYBRID_RETRIEVAL` | ⬜ | `true` = dense+BM25+RRF+reranker |
| `VECTOR_STORE` | ⬜ | `chroma` (dev, default) · `pgvector` · `qdrant` (prod) |
| `AUDIO_PROCESSOR_URL` / `DOC_PROCESSOR_URL` | ⬜ | Pluggable audio/document processors (e.g. a VoiceFlow/DocIntel instance) |
| `INGEST_WEBHOOK_SECRET` | ⬜ | Enables the public HMAC-signed `/api/v1/webhook/{source}` ingestion path |

## Key API Endpoints

```
/health  ·  /api/docs
POST /api/v1/auth/login   GET /api/v1/auth/me
POST /api/v1/chat         WS  /api/v1/ws/chat      GET /api/v1/personas
POST /api/v1/chat/async   GET /api/v1/chat/{job_id}   (async job+poll form — avoids proxy timeouts on slow turns)
GET  /api/v1/kpis[/periods|/metrics|/categories]
GET  /api/v1/insights/{health,risk,summary,anomalies}
POST /api/v1/forecast      GET /api/v1/glossary
POST /api/v1/data/export   POST /api/v1/ingest/{metrics,csv,document}
GET  /api/v1/admin/{users,roles,audit,scenario}
```

Full interactive reference at `/api/docs`.

## Tests

```bash
pytest tests/ -q                        # fast unit suite (in-process, no DB/LLM keys needed)
pytest tests/test_smoke.py -q           # 5 smoke checks (zero deps)
pytest tests/test_api.py -q             # unit-marked subset of the auth/RBAC/endpoint checks
pytest tests/test_chat.py -q            # unit-marked subset of chat/answer-block assertions
pytest tests/ -o addopts="" -q          # full suite incl. DB-dependent integration tests
```

`pytest.ini` restricts the default run to `unit`-marked tests (`addopts = -m "unit"`), which is
what CI's "Unit Tests" job runs — no database needed. The full suite (42 checks in
`test_api.py` alone) also includes `integration`-marked tests that need a reachable
`POSTGRES_URL`/`TEST_POSTGRES_URL`; run it with `-o addopts=""` to lift the default filter.

## Benchmarking Scenarios (Research & Evaluation)

IntelAI provides seven seeded, deterministic, benchmark-calibrated environments (78 months
× 7 domains × 146 metrics, formula-derived where a real formula applies — see
[DATA_SEEDING.md](DATA_SEEDING.md)) for evaluating RAG retrieval accuracy and forecasting
models under structural stress. Selectable via the `Admin → Scenarios` tab or the API directly
(`POST /api/v1/admin/scenario/async`, then poll `GET /api/v1/admin/scenario/{job_id}` — the
synchronous `POST /api/v1/admin/scenario` still works but the UI uses the async form so the
switch survives Cloudflare's proxy timeout on the larger scenarios):

| Scenario | Research Application | Description |
|---|---|---|
| `healthy` | Baseline RAG Eval | Exact revert to the real OmniIntelOS baseline — removes whatever scenario overlay is active rather than generating a fresh approximation of it (every scenario write is additive-alongside, so the baseline underneath is never modified while a scenario is active). |
| `declining_financial` | Trend Reversal | Revenue contraction & margin compression; tests forecast adaptability. |
| `high_churn_crisis` | Lagging Indicators | Customer retention failure; tests cross-domain correlation (Growth vs Finance). |
| `operational_meltdown` | Volatility Stress | OEE collapse & quality failures; introduces severe noise to operational metrics. |
| `talent_crisis` | Sentiment Impact | High attrition, open-req spike; evaluates People-to-Operations efficiency lag. |
| `cybersecurity_breach` | Shock Event | Security incident; step-function disruption in SLA/SLO metrics. |
| `esg_compliance_failure` | Policy Violation | Governance failures & emissions spike; tests multi-hop entity reasoning. |

Every scenario also carries a short cross-domain cascade (IT → Logistics/Ops → Growth →
Finance, mirroring how a real incident's financial impact actually lags its root cause) —
see DATA_SEEDING.md §4 for the full methodology.

For the reasoning behind the retrieval, evaluation, graph and forecasting design choices,
see [RESEARCH.md](RESEARCH.md). For real, measured results — a live production RAG
evaluation, an out-of-sample forecast backtest, a knowledge-graph coverage/retrieval
measurement, and the scenario-switcher correctness fixes above — see
[BENCHMARK.md](BENCHMARK.md).

## Deploy

IntelAI deploys as **one cloud service** (`render.yaml` included). Connect the repo on Render,
set the env vars above, and attach a Postgres add-on. Deploy the frontend separately on Vercel with
`VITE_API_BASE_URL` pointing to the Render service URL.

## License

AGPL-3.0 — see [LICENSE](LICENSE).

## ⚖️ License & Enterprise Use (Dual-License)

This project is open-source under the **AGPL-3.0 License**. It is completely free for researchers, students, and open-source hobbyists.

> **Commercial Use:** The AGPLv3 license requires that any proprietary network service (SaaS, internal corporate tools) that uses or modifies this code must also open-source its entire backend. 
> 
> If you wish to use this framework in a closed-source commercial environment, or require **Enterprise features** (SSO, Active Directory, Custom VPC Deployment, Strict RBAC), you must obtain a **Commercial License**. 
> Please reach out to discuss commercial licensing and integration consulting.

## Anonymous Telemetry
This project can send an anonymous, GDPR-compliant startup ping so whoever is running a
deployment can count distinct installs — **opt-in only**: it does nothing unless you set
`TELEMETRY_URL` to a collector you control, so a fresh clone never phones home anywhere
by default.
* **What is collected:** Only the project name and a "startup" event timestamp. No PII, no API keys, no user data.
* **How to enable/disable:** Set `TELEMETRY_URL` in your `.env` file to opt in; set `TELEMETRY_OPT_OUT=true` to force it off regardless of `TELEMETRY_URL`.


<!-- Scarf Analytics Pixel -->
<img referrerpolicy="no-referrer-when-downgrade" src="https://static.scarf.sh/a.png?x-pxid=ada53b5b-d56f-447f-b5ab-a65a061b7d5a" />
