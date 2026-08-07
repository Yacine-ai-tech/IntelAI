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
| **90+ curated KPIs** | Finance, HR, IT, Ops, Logistics, ESG, Growth — 36-month history, 7 benchmarking scenarios |
| **ML forecasting** | Monte Carlo with confidence bands |
| **Data export/ingest** | PDF / Excel / CSV / JSON export; CSV & document ingestion |
| **Auth + RBAC** | JWT, role-based pages, per-persona data scoping, audit log |
| **Admin governance** | User management (create/edit/disable), role viewer, scenario switcher, vector store reindex |
| **Multi-provider LLM** | Groq (default) / Anthropic via LiteLLM |
| **Bilingual** | Full EN / FR UI and copilot responses |

## Architecture

```
React + Vite (Recharts · TanStack Query · i18n)   → Vercel / Netlify
        │  HTTP / WebSocket  /api/v1/*
FastAPI  (src/api/server.py)
  auth · chat (9 personas) · KPIs · insights · forecasting · admin
        │
   PostgreSQL (Neon)          LLM  (Groq / Anthropic via LiteLLM)
   KPIs · auth · sessions ·   GraphRAG-lite · hybrid retrieval
   vectors (pgvector opt-in)  BGE reranker · BM25
```

## Quickstart

**Prerequisites:** Python 3.11, Node 18+, Postgres URL, `GROQ_API_KEY`.

```bash
git clone https://github.com/Yacine-ai-tech/IntelAI.git
cd IntelAI
cp .env.example .env   # fill POSTGRES_URL, GROQ_API_KEY, SECRET_KEY

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

| Variable | Required | Description |
|---|---|---|
| `POSTGRES_URL` | ✅ | Neon / Render / local Postgres |
| `GROQ_API_KEY` | ✅ | Default LLM provider |
| `SECRET_KEY` | ✅ | JWT signing key |
| `ANTHROPIC_API_KEY` | ⬜ | Claude reasoning tier |
| `USE_GRAPH_RAG` | ⬜ | `true` = GraphRAG-lite multi-hop |
| `USE_HYBRID_RETRIEVAL` | ⬜ | `true` = dense+BM25+RRF+reranker |
| `VECTOR_STORE` | ⬜ | `memory` · `chroma` (dev) · `pgvector` · `qdrant` (prod) |
| `LLM_MODEL` | ⬜ | Groq model id (default `llama-3.1-8b-instant`) |

## Key API Endpoints

```
/health  ·  /api/docs
POST /api/v1/auth/login   GET /api/v1/auth/me
POST /api/v1/chat         WS  /api/v1/ws/chat      GET /api/v1/personas
GET  /api/v1/kpis[/periods|/metrics|/categories]
GET  /api/v1/insights/{health,risk,summary,anomalies}
POST /api/v1/forecast      GET /api/v1/glossary
POST /api/v1/data/export   POST /api/v1/ingest/{metrics,csv,document}
GET  /api/v1/admin/{users,roles,audit,scenario}
```

Full interactive reference at `/api/docs`.

## Tests

```bash
pytest tests/ -q                  # all in-process (no live server needed)
pytest tests/test_smoke.py -q     # 5 smoke checks (zero deps)
pytest tests/test_api.py -q       # 30+ auth/RBAC/endpoint checks
pytest tests/test_chat.py -q      # chat endpoint + answer-block assertions
```

DB-dependent tests run automatically when `POSTGRES_URL` is reachable and skip cleanly otherwise — CI is green without a database.

## Benchmarking Scenarios (Research & Evaluation)

IntelAI provides seven seeded deterministic environments for evaluating RAG retrieval accuracy and forecasting models under structural stress. Rather than generating synthetic data, the official seeding process uses the API to ingest **real data**, accurately simulating the production context pipeline. These scenarios are selectable via the `Admin → Scenarios` tab or API (`POST /api/v1/admin/scenario`):

| Scenario | Research Application | Description |
|---|---|---|
| `healthy` | Baseline RAG Eval | S&P 500 baseline with stationary distributions. |
| `declining_financial` | Trend Reversal | Revenue contraction & margin compression; tests forecast adaptability. |
| `high_churn_crisis` | Lagging Indicators | Customer retention failure; tests cross-domain correlation (Growth vs Finance). |
| `operational_meltdown` | Volatility Stress | OEE collapse & quality failures; introduces severe noise to operational metrics. |
| `talent_crisis` | Sentiment Impact | High attrition, open-req spike; evaluates HR to operational efficiency lag. |
| `cybersecurity_breach` | Shock Event | Security incident; step-function disruption in SLA/SLO metrics. |
| `esg_compliance_failure` | Policy Violation | Governance failures & emissions spike; tests multi-hop entity reasoning. |

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

## 📡 Anonymous Telemetry
This project collects anonymous, GDPR-compliant startup pings to help the author understand usage volume and prioritize development. 
* **What is collected:** Only the project name and a "startup" event timestamp. No PII, no API keys, no user data.
* **How to disable:** We respect your privacy. To opt-out, simply set `TELEMETRY_OPT_OUT=true` in your `.env` file.


<!-- Scarf Analytics Pixel -->
<img referrerpolicy="no-referrer-when-downgrade" src="https://static.scarf.sh/a.png?x-pxid=ada53b5b-d56f-447f-b5ab-a65a061b7d5a" />


