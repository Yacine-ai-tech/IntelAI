# 🎯 IntelAI

> **Persona-Aware AI Analytics & RAG Copilot** — multi-domain KPI intelligence with a
> 9-persona, role-scoped RAG copilot, GraphRAG-lite retrieval, ML forecasting, and
> board-ready exports. One FastAPI service. Bilingual (EN/FR).

[![CI](https://github.com/Yacine-ai-tech/IntelAI/actions/workflows/ci.yml/badge.svg)](https://github.com/Yacine-ai-tech/IntelAI/actions)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

IntelAI turns multi-domain business KPIs (Finance, HR, IT, Operations, Logistics, ESG,
Risk) into executive intelligence and lets each role *talk to its own data* through a
RAG copilot that respects role boundaries.

> IntelAI is the scoped product extracted from a larger all-in-one platform. The full
> self-hostable platform (monitoring, OCR, voice, n8n, on-prem stack) is a separate
> project, **OmniIntelOS**.

---

## ✨ Features

- **9-persona RAG copilot** — CEO, CFO, CTO, COO, CHRO, ESG, Risk, Business Analyst, and a
  general Assistant. Each persona has its own system prompt **and data scope** (e.g. the
  CHRO can't see Finance-only data). WebSocket token streaming + source citations.
- **GraphRAG-lite** — for multi-hop questions ("how does Engineering headcount track
  Finance margin?"), an entity graph ranks KPI records by overlap and feeds them to the
  copilot. Opt-in via `USE_GRAPH_RAG`.
- **Hybrid retrieval** — dense (BGE-large) + BM25 + RRF + BGE reranker (`USE_HYBRID_RETRIEVAL`).
- **Multi-domain KPI analytics** — dashboards, anomaly detection, health scoring, and a
  unified KPI schema across domains.
- **ML forecasting** — Monte Carlo forecasts with confidence-interval bands (Recharts).
- **Board-ready exports** — one-click PDF / PPTX executive briefings.
- **Auth + RBAC** — JWT, role-based pages and data scoping, audit log.
- **Multi-provider LLM** — Groq (default) / Anthropic / OpenAI via a LiteLLM router.
- **Bilingual** — full EN / FR UI and responses.

## 🏗️ Architecture

```
            React + Vite (Recharts, i18n)          ← deploy to Vercel/Netlify
                       │  HTTP / WebSocket  /api/v1/*
            ┌──────────▼─────────────────────────────────────┐
            │  FastAPI (src/api/server_v2.py)                 │
            │  auth · chat (9 personas) · KPIs · insights ·   │
            │  forecasting · ingestion · admin · /metrics     │
            └───┬───────────────┬───────────────┬────────────┘
            PostgreSQL       ChromaDB         LLM (Groq /
            (KPIs, auth)     (vectors)        Anthropic / OpenAI)
                                  ▲
                          GraphRAG-lite + hybrid retrieval + reranker
```

One deployable service (FastAPI + embedded ChromaDB). The React frontend deploys
separately. Production target: a single cloud service (Railway/Fly) + managed Postgres.

## 🚀 Quickstart

**Prerequisites:** Python 3.11, Node 18+, a Postgres URL (Neon free tier works), and a
`GROQ_API_KEY` (Anthropic/OpenAI optional).

```bash
git clone https://github.com/Yacine-ai-tech/IntelAI.git
cd IntelAI
cp .env.example .env        # fill POSTGRES_URL, GROQ_API_KEY, SECRET_KEY (see below)

# Backend (API on :8000)
pip install -r requirements.txt
alembic upgrade head        # create tables
python main.py              # → http://localhost:8000  (docs at /api/docs)

# Frontend (UI on :5173, proxies to :8000)
cd frontend && npm install && npm run dev
```

**Docker (single app):**
```bash
docker compose -f docker-compose.dev.yml up --build   # app only (uses your .env DB)
docker compose up --build                              # app + bundled Postgres
```

Default login: **`admin` / `admin123`** (change after first login).

## 🔑 Configuration (`.env`)

| Variable | Required | Notes |
|---|---|---|
| `POSTGRES_URL` | ✅ | KPIs + auth (Neon / Railway / local) |
| `GROQ_API_KEY` | ✅ | default LLM provider |
| `SECRET_KEY` | ✅ | JWT signing (`python -c "import secrets;print(secrets.token_hex(32))"`) |
| `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` | ⬜ | reasoning / judge tiers |
| `TAVILY_API_KEY` | ⬜ | web search enrichment |
| `USE_HYBRID_RETRIEVAL` | ⬜ | `true` = dense+BM25+RRF+reranker |
| `USE_GRAPH_RAG` | ⬜ | `true` = GraphRAG-lite for multi-hop KPI queries |
| `VECTOR_STORE` | ⬜ | `chroma` (dev) / `qdrant` (prod) |

## 🔌 Key API endpoints

`/health` · `/api/docs` · `/metrics` ·
`POST /api/v1/auth/login` · `GET /api/v1/auth/me` ·
`POST /api/v1/chat` · `WS /api/v1/ws/chat` (streaming) ·
`GET /api/v1/kpis[/periods|/metrics|/categories]` ·
`GET /api/v1/insights/{health,risk,summary,anomalies}` ·
`POST /api/v1/forecast` · `POST /api/v1/ingest/{metrics,csv}` ·
`GET /api/v1/knowledge/{search,stats}` · `GET /api/v1/admin/{users,roles,audit}`

Full interactive reference at **`/api/docs`**.

## 🧪 Tests

```bash
pytest tests/ -q
```
`tests/test_smoke.py` + `tests/test_api.py` run **in-process** via FastAPI `TestClient`
(no live server). DB-dependent checks run when a seeded DB is reachable and skip cleanly
otherwise, so CI is green without a database. The Playwright e2e
(`tests/test_e2e_playwright.py`) runs only when the live stack + Playwright are present.

## ☁️ Deploy

IntelAI deploys as **one cloud service** built from the `Dockerfile` (`railway.toml`
included). On Railway/Fly: connect the repo, set the env vars above, attach Postgres.
Deploy the frontend separately (Vercel/Netlify) with its API base pointed at the backend.

## 🗺️ Roadmap

- `omnismart-personas` published to PyPI (persona templates + router — see `packages/`).
- RAG eval harness wired to the RAGeval project; weekly groundedness gate.
- Qdrant production vector store; saved dashboards.

## 📄 License

MIT — see [LICENSE](LICENSE).
