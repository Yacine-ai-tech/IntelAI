# IntelAI

[![CI](https://github.com/Yacine-ai-tech/IntelAI/actions/workflows/ci.yml/badge.svg)](https://github.com/Yacine-ai-tech/IntelAI/actions/workflows/ci.yml)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/intelai.svg)](https://pypi.org/project/intelai/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://python.org)

> **Persona-Aware AI Analytics & RAG Copilot** — 9-persona, role-scoped copilot with
> GraphRAG-lite retrieval, ML forecasting, bilingual (EN/FR) UI, and board-ready exports.


**Live demo:** https://intelai.ysiddo-ai-projects.app · password-less role login (DEMO_MODE).
First request may take ~60 s to wake the on-demand backend.
> Self-hosting: see [SELF_HOSTING.md](SELF_HOSTING.md).  
> Data Model & Benchmarks: see [DATA_SEEDING.md](DATA_SEEDING.md).

---

## Features

| Area | Detail |
|---|---|
| **9-persona RAG copilot** | CEO, CFO, CTO, COO, CHRO, ESG, Risk, Analyst, Assistant — role-scoped data, WS streaming, citations |
| **GraphRAG-lite** | Multi-hop entity graph for cross-domain queries (`USE_GRAPH_RAG=true`) |
| **Hybrid retrieval** | Dense + BM25 + RRF + BGE reranker; degrades gracefully |
| **Answer-block structuring** | Backend parses LLM markdown into typed blocks (heading, kpi, list, quote, code) |
| **169 curated KPIs** | Finance, HR, IT, Ops, Logistics, ESG, Growth — 36-month history, 7 benchmarking scenarios |
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
git clone https://gateway.ysiddo-ai-projects.app/git/IntelAI.git
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
| `POSTGRES_URL` | ✅ | Neon / Railway / local Postgres |
| `GROQ_API_KEY` | ✅ | Default LLM provider |
| `SECRET_KEY` | ✅ | JWT signing key |
| `ANTHROPIC_API_KEY` | ⬜ | Claude reasoning tier |
| `USE_GRAPH_RAG` | ⬜ | `true` = GraphRAG-lite multi-hop |
| `USE_HYBRID_RETRIEVAL` | ⬜ | `true` = dense+BM25+RRF+reranker |
| `VECTOR_STORE` | ⬜ | `memory` · `chroma` · `pgvector` · `qdrant` |
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
pytest tests/ -q                       # all in-process (no live server needed)
pytest tests/test_smoke.py -q          # 5 smoke checks (zero deps)
pytest tests/test_api.py -q            # 42 auth/RBAC/endpoint checks
pytest tests/test_exhaustive_api.py -q # 71 exhaustive API coverage tests
pytest tests/test_chat.py -q           # 9 chat endpoint + answer-block assertions
```

DB-dependent tests run automatically when `POSTGRES_URL` is reachable and skip cleanly otherwise — CI is green without a database.

## Benchmarking Scenarios

Seven seeded scenarios (selectable from the Admin → Scenarios tab or via `POST /api/v1/admin/scenario`):

| Scenario | Description |
|---|---|
| `healthy` | S&P 500 baseline |
| `declining_financial` | Revenue contraction & margin compression |
| `high_churn_crisis` | Customer retention failure |
| `operational_meltdown` | OEE collapse & quality failures |
| `talent_crisis` | High attrition, open-req spike |
| `cybersecurity_breach` | Security incident — SLA/SLO degrade |
| `esg_compliance_failure` | Governance failures & emissions spike |

## Deploy

IntelAI deploys as **one cloud service**. Connect the repo on Render or your preferred host,
set the env vars above, attach a Postgres add-on (Neon recommended). Deploy the frontend separately on Vercel with
`VITE_API_BASE_URL` pointing to the backend service URL.

## PyPI Packages

Two reusable packages are extracted from this codebase and published to PyPI:

```bash
pip install intelai              # v0.1.2 — the full deployable app
pip install omnismart-personas  # v0.1.3 — persona templates for LangChain RAG projects
```

## Research Novelty & Scientific Contributions

IntelAI is built with research-proof reproducibility standards:
- **Autonomous Dual-Loop RAG**: Query decomposition outer loop combined with micro-claim verification inner loop.
- **Graph-Dense Reranking**: Dynamic score combination fusing dense vector cosine distance with knowledge graph PageRank adjacency metrics.
- **Active Citation Grounding**: Automatic verification of generated claims against exact document source tuples.

For full mathematical formulation and evaluation analysis, see [RESEARCH.md](RESEARCH.md).

## Benchmark Reproduction Suite

Run the empirical benchmark evaluation:
```bash
python3 eval/run_benchmarks.py --seed 42
```

## License & Enterprise Use (Dual-License)

This project is open-source under the **AGPL-3.0 License**. Free for researchers, students, and open-source projects.
Commercial license: see [COMMERCIAL.md](COMMERCIAL.md).

