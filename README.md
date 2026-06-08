# 🎯 IntelAI

> **Persona-Aware AI Analytics & RAG Copilot — multi-domain KPI intelligence with GraphRAG-lite**

> ℹ️ **Scope (2026-06-09):** IntelAI is the scoped product (analytics + 9-persona RAG +
> GraphRAG-lite, one cloud deployment). It was extracted from the larger all-in-one
> platform, now the separate **private** repo `Yacine-ai-tech/OmniIntelOS`. This README is
> the pre-split version; Phase 1 trims it to <200 lines and removes platform-only features
> (monitoring/OCR/voice/n8n). See `STRATEGY.md` §1.1 for the authoritative KEEP/CUT scope.

[![IntelAI](https://img.shields.io/badge/IntelAI-2026-FF4B4B?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEyIDJDMTMuMSAyIDI0IDMuOSA4IDggNiAxMCA2IDE0IDggMTggMTAgMTggMTIgMTQgMTIgMTQgMTggMTIgMjJDMTAuOSAyMiAyIDIwLjEgMiAxOUMyIDE3LjkgMy45IDE3IDUgMTdDOSAxNyAxMSAxNSAxMSAxM0MxMSAxMSAxMyA5IDE1IDlDMTcgOSA5IDIgMTIgMloiIGZpbGw9IiNGRjRCNEEiLz4KPC9zdmc+)](https://github.com/Yacine-ai-tech/IntelAI)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![DuckDB](https://img.shields.io/badge/DuckDB-FFF000?style=for-the-badge&logo=duckdb&logoColor=black)](https://duckdb.org)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)

**Transform your business data into strategic advantage through unified multi-sector analytics, AI-powered insights, and automated governance.**

---

## 📊 Overview

**IntelAI** is a comprehensive enterprise-grade intelligence platform that transforms raw business data across multiple sectors into actionable executive intelligence. Built for 2026 enterprise buyers who demand sophisticated analytics, predictive insights, and automated governance across Finance, Growth, Operations, People/HR, and ESG domains.

### 🎯 What Makes It Special

- **Multi-Domain Intelligence**: Finance, Growth/Customer, Operations, People/HR, and ESG metrics in one unified platform
- **Unified KPI Schema**: Single format for all business metrics across departments and sectors
- **Executive Intelligence**: AI-powered health scoring and automated insights
- **Predictive Analytics**: ML-based forecasting with confidence intervals
- **Risk Management**: Anomaly detection and concentration analysis
- **ESG Compliance**: Sustainability metrics as first-class citizens
- **Local-First Architecture**: Complete data sovereignty, no cloud dependency
- **Role-Based Governance**: Secure, auditable access control
- **Board-Ready Exports**: One-click PDF and PowerPoint briefings
- **AI Model Monitoring**: Integrated MLflow, Wandb, and TensorBoard tracking

### 🚀 Key Capabilities by Sector

| Sector | Key Metrics / KPIs | Example Features |
| ------------------------ | ------------------------------------------------------------------------------------- | -------------------------------------------------- |
| **Finance** | Revenue, Gross Margin, EBITDA, Cash Flow, Accounts Receivable/Payable, Debt-to-Equity | Health Index, Forecasting, Board-ready reports |
| **Growth / Customer** | MRR, ARR, Churn Rate, NPS, CAC, LTV | Scenario planning, Trend analysis |
| **Operations** | On-time delivery, Cycle Time, Defect Rate, Capacity Utilization | Risk radar, Anomaly detection, Segment analysis |
| **People / HR** | Headcount, Turnover, Engagement, Diversity Index | Workforce analytics, Scenario planning, ESG impact |
| **ESG / Sustainability** | Carbon intensity, Energy consumption, Safety incidents, Governance metrics | Compliance reporting, Impact measurement |

### 🚀 Core Features & Capabilities

| Feature | Description | 2026 Value |
|---------|-------------|------------|
| **Multi-Domain Analytics** | Finance, Growth, Operations, People, ESG in one platform | Comprehensive business intelligence |
| **Executive Dashboard** | Health index, risk scores, AI highlights | Strategic decision support |
| **AI Forecasting** | ML predictions with scenario planning | Predictive intelligence |
| **Risk Radar** | Anomaly detection, pattern recognition | Proactive risk management |
| **ESG Intelligence** | Sustainability tracking & reporting | Compliance & impact measurement |
| **AI Copilot** | Natural language queries over data | Conversational analytics |
| **Multi-Language** | English & French interfaces | Global enterprise support |
| **AI Model Monitoring** | MLflow, Wandb, TensorBoard integration | Model performance tracking |

---

## 🏁 Quick Start (5 Minutes)

### Prerequisites
- **Python 3.10+**
 - Docker & Docker Compose (recommended)

Docker-first workflow (recommended)
----------------------------------
This repository now uses a Docker-first workflow. Containers are configured to NOT auto-start on OS boot to avoid accidental resource usage.

Basic steps:

1. Build images (no containers will be started):

```bash
./scripts/start_all.sh
```

2. Start containers when you're ready:

```bash
./scripts/start_containers.sh core   # start core services (postgres, fastapi, frontend)
./scripts/start_containers.sh all    # start everything
```

3. Stop containers:

```bash
./scripts/stop_containers.sh
```

4. Prevent Docker from auto-starting on system boot (optional):

```bash
./scripts/disable_docker_autostart.sh    # dry-run
./scripts/disable_docker_autostart.sh --apply  # apply
```

Notes:
- Services are configured with `restart: "no"` in `docker-compose.yml` so containers will not auto-restart after a reboot.
- The `start_all.sh` script will only build images (fast) and will not start containers. This keeps your machine quiet until you decide to run services.

Developer hot-reload via Docker (optional)
-----------------------------------------
If you want to use containerized hot-reload for development (without installing deps locally), use the `dev` profile in docker compose.

Examples (no services will run unless you explicitly start them):

```bash
# Build images (no containers started)
./scripts/start_all.sh

# Start only dev backend (uvicorn --reload) and dev frontend (Vite) — these are profile-based and won't run by default
docker compose --profile dev up backend-dev frontend-dev

# Stop dev services
docker compose --profile dev down
```

Notes:
- Dev services are intentionally placed in the `dev` profile so they will not run unless explicitly requested.
- The `backend-dev` service mounts your repo and runs uvicorn with `--reload`. The `frontend-dev` mounts `./frontend` and runs `npm run dev`.
- These are optional developer conveniences — production services remain the same and still won't auto-start on boot.

- **4GB RAM minimum** (8GB recommended)
- **Modern web browser**

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Yacine-ai-tech/IntelAI.git
cd IntelAI

# 2. Create virtual environment
python -m venv venv

# 3. Activate environment
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt
```

### Launch Application (Docker-first)

```bash
# Recommended: Docker-first workflow
# 1) Build images (no containers will be started):
./scripts/start_all.sh

# 2) Start containers when you're ready:
./scripts/start_containers.sh core    # start core services (postgres, fastapi, frontend)
./scripts/start_containers.sh all     # start all services

# 3) Stop containers:
./scripts/stop_containers.sh

# Advanced / Local development (not recommended for production):
# If you need to run the API locally for debugging, use an explicit uvicorn command
# from a virtual environment (see Development section):
# python -m uvicorn src.api.server_v2:app --host 0.0.0.0 --port 8000 --reload
```

### Load Sample Data

1. Open http://localhost:8000/docs (FastAPI API docs)
2. Or access the React frontend at http://localhost:5173 (when implemented)
3. Use the API endpoints to load and explore data

**🎉 You're ready! The system now contains 15+ KPIs across Finance, Growth, Operations, People, and ESG categories.**

---
# IntelAI — Complete Repository Reference

This file is a comprehensive reference for the IntelAI repository. It documents the code layout, service architecture, configuration and environment variables, runtime behavior, API reference, developer workflows, deployment runbooks, troubleshooting, security, testing, and appendices with examples, SQL schema, sample data and common utilities.

This README is intentionally exhaustive so it can serve as the single source of truth for maintainers and operators. Sections are clearly divided and cross-referenced; use your editor's search to jump to the parts you need.

Table of contents
-----------------

1. Overview
2. Architecture & components
3. Repository layout (detailed)
4. Requirements and dependencies
5. Configuration & environment variables (complete table)
6. Docker & compose (services, profiles, resource budgets)
7. Running the platform (Docker-first and local)
8. Development workflows (backend, frontend, debugging)
9. API reference (endpoints, models, examples)
10. Database schema & migrations
11. Data ingestion and sample datasets
12. AI/ML & RAG specifics (models, embeddings, persona system)
13. Integrations (Google, ClickUp, n8n)
14. Security, keys and secrets management
15. Monitoring, logging and health checks
16. Testing strategy and running tests
17. CI/CD and deployment notes
18. Troubleshooting & FAQs
19. Contributing guide
20. Changelog & release notes
21. Appendix A: example requests and curl snippets
22. Appendix B: SQL schema (full)
23. Appendix C: sample CSV and JSON datasets
24. Appendix D: command reference for scripts/
25. Appendix E: developer checklists and pair-programming tips

Each major section below contains subsections, examples, and references to the specific files in the repository.

1. Overview
-----------

IntelAI is a self-hosted intelligence operating system designed to unify multi-domain business metrics (Finance, Growth, Operations, People, ESG) and provide AI-powered insights, forecasting, and governance workflows. The platform is intentionally local-first and container-friendly for on-premise or single-server deployments.

Goals:

- Provide a unified KPI schema and data ingestion pipeline.
- Offer a secure, role-based API and UI for querying, analysis, and AI-assisted interaction.
- Support RAG (Retrieval-Augmented Generation) copilot workflows with a local/embedded vector store.
- Enable predictable, resource-constrained deployments for small servers (e.g., 8GB RAM targets).

This repository contains:

- `src/` — Python FastAPI backend with modular services for ingestion, chat, forecasting, and integrations.
- `frontend/` — React + Vite frontend UI skeleton and components.
- `docker-compose.yml` + profiles — pre-configured services for local development and optional monitoring/automation.
- `scripts/` — build and orchestration helpers.
- `requirements.txt` — pinned Python dependencies used by the backend image.
- `Dockerfile` — production-style backend image build with CPU-optimized ML dependencies.

2. Architecture & components
---------------------------

High-level architecture (ASCII diagram):

```
												 +-----------------------+
												 |   React Frontend      |
												 |   (frontend/)         |
												 +----------+------------+
																		|
																		| HTTP / WebSocket
																		|
												 +----------v------------+
												 |     FastAPI Backend   |
												 |   (src/api/server_v2) |
												 +----+---------------+--+
															|               |
						 +----------------+               +-------------------+
						 |                                                |
		+--------v--------+                              +--------v--------+
		| PostgreSQL      |                              | DuckDB          |
		| (Primary)       |                              | (Analytics)     |
		+--------+--------+                              +-----------------+
						 |                                                 
						 |                                                 
		+--------v--------+                                        
		| ChromaDB (vec)  |                                        
		+-----------------+                                        
```

Components and responsibilities:

- Backend (`src/`): API endpoints, authentication (JWT), persona and RAG orchestration, integrations, ingestion and persistence.
- Services (`src/services/`): small modules (pg_store, omnismart_chatbot, voice, ocr, forecasting, etc.) for separated responsibilities.
- Frontend (`frontend/`): UI for dashboards, assistant pages, and integration flows.
- PostgreSQL (`postgres`): primary persistent store for users, sessions, KPI rows, integration tokens (encrypted), and audit logs.
- DuckDB (optional): used for heavy analytics and in-memory query acceleration where configured.
- ChromaDB (local folder): vector store for RAG and knowledge retrieval.
- n8n (optional): workflow automation with preloaded workflows.
- Prometheus / Grafana (optional): monitoring and dashboarding.

3. Repository layout (detailed)
-----------------------------

Top-level files and directories:

- `Dockerfile` — backend build
- `docker-compose.yml` — compose configuration with resource caps and profiles
- `requirements.txt` — python dependencies
- `main.py` — app entrypoint for running backend via `python main.py`
- `src/` — backend code
	- `src/api/` — `server_v2.py` main API
	- `src/core/` — `config.py`, `jwt_auth.py`, `logger.py`, `performance.py`
	- `src/services/` — ingestion, pg_store, omnismart_chatbot, voice, ocr, forecasting, etc.
	- `src/integrations/` — connectors for external services
	- `src/models/` — pydantic/sqlalchemy models (pg_models.py, schemas.py)
- `frontend/` — react app + `package.json` & `Dockerfile`
- `scripts/` — helper scripts for build and start
- `tests/` — pytest tests
- `monitoring/` — prometheus/grafana configs

4. Requirements and dependencies
-------------------------------

The backend is tested with Python 3.10 and depends on the packages listed in `requirements.txt`. Key dependencies include:

- FastAPI, uvicorn (ASGI server)
- SQLAlchemy / asyncpg / psycopg
- pandas, numpy for data handling
- sentence-transformers, chromadb for embeddings and vector store
- groq, langchain variants for LLM integration (Groq provider in current configuration)
- plotly, fpdf2, python-pptx for exports

The `requirements.txt` includes CPU variants for heavy ML libs to avoid CUDA/GPU-only wheels by default.

5. Configuration & environment variables (complete table)
------------------------------------------------------

All configuration is stored and read via `src/core/config.py`. The following table lists important env vars, default values, and notes.

NOTE: this table mirrors `Settings` dataclass in `src/core/config.py` — verify this file when adding new env vars.

| Env Var | Default | Purpose | Required |
|---------|---------|---------|----------|
| ENVIRONMENT | development | runtime environment (development/production) | no |
| POSTGRES_URL | postgresql://omniintel:change_me_postgres_password@localhost:5432/intelai | DB connection string for PostgreSQL | yes (local default provided)
| GROQ_API_KEY | "" | API key for Groq LLM provider | yes for LLM features
| TAVILY_API_KEY | "" | Tavily web search API key | yes for web search features
| SECRET_KEY | change-me-in-production | JWT and session secret | yes in production
| FRONTEND_URL | http://localhost:5173 | Base URL for front-end (OAuth redirects) | no
| OCR_SERVICE_URL | http://omnitel-ocr:8001 | OCR microservice URL | no
| VOICE_SERVICE_URL | http://omnitel-voice:8002 | Voice microservice URL | no
| GOOGLE_CLIENT_ID | "" | Google OAuth client id | required for Google integrations
| GOOGLE_CLIENT_SECRET | "" | Google OAuth client secret | required for Google integrations
| CLICKUP_API_KEY | "" | ClickUp integration key | required for ClickUp
| CHROMA_DB_PATH | ./chroma_db | Local path for Chroma vector store | no
| FEATURE_VOICE | true | Toggle voice features | no
| FEATURE_N8N | true | Toggle n8n integration | no
| FEATURE_RAG | true | Toggle RAG features | no
| LLM_MODEL | llama-3.1-8b-instant | LLM model name used by Groq | no
| EMBEDDING_MODEL | all-MiniLM-L6-v2 | Sentence transformer for embeddings | no

For a complete list, open `src/core/config.py` and inspect the `Settings` dataclass.

6. Docker & compose (services, profiles, resource budgets)
--------------------------------------------------------

`docker-compose.yml` includes the following services (high-level):

- postgres — primary DB (image: postgres:16-alpine)
- fastapi — backend (built from root `Dockerfile`)
- frontend — frontend (built from `frontend/Dockerfile`)
- prometheus — monitoring (profile `monitoring`)
- grafana — monitoring UI (profile `monitoring`)
- n8n — automation (profile `automation`)
- omnitel-ocr — OCR microservice (profile `ai`)
- omnitel-voice — voice microservice (profile `ai`)
- cloudflare-tunnel & cloudflare-tunnel-permanent — tunnel helpers (profiles `tunnel`/`tunnel-permanent`)
- backend-dev, frontend-dev — development-only services for hot reload (profiles `dev`)

Compose profiles let you opt into optional services. The repository ships with `start_all.sh` and `start_containers.sh` scripts to build and/or bring up subsets of services.

Resource budgets

Compose sets CPU/memory limits to keep the entire stack runnable on smaller hosts. Adjust these in `docker-compose.yml` as needed.

7. Running the platform (Docker-first and local)
-----------------------------------------------

Docker-first recommended steps

1. Build images (no containers will start):

```bash
./scripts/start_all.sh
```

2. Start minimal core services (postgres, fastapi, frontend):

```bash
./scripts/start_containers.sh core
```

3. Start all services (monitoring + automation + ai):

```bash
./scripts/start_containers.sh all
```

4. Stop everything:

```bash
./scripts/stop_containers.sh
```

Local (non-Docker) development

Backend:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn src.api.server_v2:app --host 0.0.0.0 --port 8000 --reload
```

Frontend (developer):

```bash
cd frontend
npm install
npm run dev
```

Notes about running in production

- Set `ENVIRONMENT=production` and provide secure `SECRET_KEY`, `GROQ_API_KEY`, and other required secrets.
- Use process managers or orchestration platforms (Kubernetes, ECS) for production-grade deployments and scale.

8. Development workflows (backend, frontend, debugging)
----------------------------------------------------

Backend

- Use the `backend-dev` compose profile for hot reload inside containers or run `uvicorn` locally.
- Run unit tests with pytest: `python -m pytest tests/ -q`.
- Format with `black` (if installed) and lint with `flake8`/`pylint`.

Frontend

- `cd frontend && npm install` to install deps.
- `npm run dev` starts Vite dev server (port 5173 by default).

Debugging tips

- Check logs in `logs/` and container logs via `docker compose logs -f <service>`.
- Use `curl http://localhost:8000/health` to confirm backend is healthy.

9. API reference (endpoints, models, examples)
-------------------------------------------

This section documents the primary API surface exposed by `src/api/server_v2.py`. For each endpoint: path, method, auth requirements, request model, and response example.

Auth

- `POST /api/v1/auth/login`
	- Body: `{"username":"...","password":"..."}`
	- Returns: access token and user info

Example:

```bash
curl -s -X POST http://localhost:8000/api/v1/auth/login \
	-H 'Content-Type: application/json' \
	-d '{"username":"admin","password":"secret"}'
```

- `POST /api/v1/auth/register`
	- Public registration restricted to viewer/analyst roles by default.

- `GET /api/v1/auth/me`
	- Returns current user info; requires Bearer token.

Health & status

- `GET /health` — unauthenticated health check.
- `GET /api/v1/status` — authenticated; returns counts and available domains.

Chat & personas

- `POST /api/v1/chat`
	- Body model: `ChatRequest` (message, persona, session_id, context)
	- Returns `ChatResponse` with `response`, `persona_used`, `tokens_used`, `latency_ms`, `session_id`, and sources.

Files

- `GET /api/v1/files` — list user files (pagination: `limit`, `offset`).
- `GET /api/v1/files/{file_id}/preview` — preview content.
- `GET /api/v1/files/{file_id}/download` — download file.

Ingestion

- `POST /api/v1/ingest/metrics`
	- Body: `IngestMetricsRequest` with `data` array and `source_name`.
	- Stores KPI rows via `pg_store.store_kpi_metrics`.

Integrations

- `GET /api/v1/integrations/{type}/data` — fetch integration data (gmail, sheets, clickup supported).
- `POST /api/v1/integrations/{type}/connect` — store credentials (encrypted).
- OAuth flow: `GET /api/v1/integrations/{type}/oauth/start` and callback at `GET /api/v1/integrations/{type}/oauth/callback`.

Voice & OCR

- `POST /api/v1/ocr/extract` — uploads file and proxies to OCR microservice.
- `POST /api/v1/voice/transcribe` — proxies to voice microservice for STT.
- `POST /api/v1/voice/tts` — proxies to voice microservice for TTS and returns audio.

Full example: Chat with RAG

```bash
# 1) Login and get token
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login -H 'Content-Type: application/json' -d '{"username":"admin","password":"password"}' | jq -r .access_token)

# 2) Send a chat message
curl -s -X POST http://localhost:8000/api/v1/chat \
	-H "Authorization: Bearer $TOKEN" \
	-H 'Content-Type: application/json' \
	-d '{"message":"Summarize revenue trends for 2025","persona":"analyst"}'
```

10. Database schema & migrations
--------------------------------

Primary schema is managed under `src/services/pg_store.py` and migrations under `migrations/`. Key logical tables include:

- `users` — user accounts and roles
- `kpi_metrics` — long-format KPI rows (period, metric, value, category, segment, unit, direction)
- `files` — uploaded files metadata
- `chat_sessions`, `chat_messages` — conversation history (optional)
- `oauth_states`, `integration_credentials` — OAuth states and encrypted credentials
- `audit_log` — action logging for sensitive operations

11. Data ingestion and sample datasets
------------------------------------

The repo includes `enhanced_synthetic_dataset/` with JSON/CSV datasets and samples. The ingestion endpoint expects an array of dictionaries with the long-format schema:

CSV sample:

```
period,metric,value,category,segment,unit,direction
2025-01,Revenue,1250000,Finance,Global,USD,higher_is_better
2025-01,Gross Margin,540000,Finance,Global,USD,higher_is_better
```

To ingest via API:

```bash
curl -X POST http://localhost:8000/api/v1/ingest/metrics \
	-H "Authorization: Bearer $TOKEN" \
	-H 'Content-Type: application/json' \
	-d '{"data":[{"period":"2025-01","metric":"Revenue","value":1250000,"category":"Finance","segment":"Global","unit":"USD","direction":"higher_is_better"}],"source_name":"api"}'
```

12. AI/ML & RAG specifics (models, embeddings, persona system)
-----------------------------------------------------------

RAG pipeline:

- Documents are chunked using `CHUNK_SIZE` and `CHUNK_OVERLAP` from `src/core/config.py`.
- Embeddings are created with `EMBEDDING_MODEL` (default `all-MiniLM-L6-v2`).
- ChromaDB is used as the vector store; `CHROMA_DB_PATH` controls its directory.
- LLM provider configured is Groq via `GROQ_API_KEY`; prompt templates and persona wiring live in `src/services/omnismart_chatbot.py` and `src/services/omnismart_chatbot/personas` (persona factory).

Persona model

- The persona factory maps user roles to persona system instructions. Personas control verbosity, tone, and available actions (table-driven inside persona factory).

13. Integrations (Google, ClickUp, n8n)
-------------------------------------

Supported integrations:

- Gmail and Google Sheets via OAuth2 (uses `GOOGLE_CLIENT_ID/SECRET`).
- ClickUp via OAuth/API key.
- n8n for workflow automation (preloaded workflows in `n8n_workflows/`).

Integration flow summary:

1. User requests OAuth start (`/api/v1/integrations/{type}/oauth/start`). Server stores a short-lived state and returns provider URL.
2. Provider redirects back to callback (`/api/v1/integrations/{type}/oauth/callback`) where server exchanges code for tokens and stores encrypted credentials.
3. Server optionally stores refresh token metadata and schedules token refresh tasks.

14. Security, keys and secrets management
--------------------------------------

Sensitive items to manage:

- `SECRET_KEY` — set strong secret in production
- API keys (`GROQ_API_KEY`, `TAVILY_API_KEY`) — store in `.env` or a secret manager
- Database credentials — use secrets and limited DB users

Token storage:

- Integration tokens and refresh tokens are encrypted before being persisted (see `src/core/crypto.py`).

15. Monitoring, logging and health checks
---------------------------------------

- Health endpoint: `GET /health`.
- FastAPI logs are written by the logger configured in `src/core/logger.py` to `logs/`.
- Prometheus scraping configured in `monitoring/prometheus.yml` and Grafana dashboards in `monitoring/grafana` (provisioning files included).

16. Testing strategy and running tests
------------------------------------

Run unit tests:

```bash
python -m pytest tests/ -v
```

Notes:

- Tests may use a local Postgres. For isolated tests, use `pytest` fixtures to mock `pg_store` or run a test database via docker-compose.

17. CI/CD and deployment notes
-----------------------------

- CI should run linting, unit tests, and container image build.
- For production, build images with buildkit and push to a registry; deploy via Kubernetes or Docker Compose on a server with proper resource allocation.

18. Troubleshooting & FAQs
-------------------------

Q: Backend fails on startup complaining about missing keys.
A: Ensure `GROQ_API_KEY` and `TAVILY_API_KEY` are set in `.env` or environment. The backend runs a fail-fast check.

Q: Chroma DB errors on startup.
A: Verify `CHROMA_DB_PATH` is writable and that the `chroma_db/` folder exists. The `src/core/config.py` creates directories but permissions may block creation in some setups.

19. Contributing guide
---------------------

- Fork the repo and create feature branches.
- Add tests for new features and run `pytest` before PR.
- Open PRs against `main` with clear descriptions and migration notes if database changes are included.

20. Changelog & release notes
----------------------------

Maintain a concise changelog externally or expand this section with release versions, dates, and highlights.

21. Appendix A: example requests and curl snippets
-------------------------------------------------

Auth + chat example (complete):

```bash
# login
RESP=$(curl -s -X POST http://localhost:8000/api/v1/auth/login -H 'Content-Type: application/json' -d '{"username":"demo","password":"demo"}')
TOKEN=$(echo "$RESP" | jq -r .access_token)

# call chat
curl -s -X POST http://localhost:8000/api/v1/chat \
	-H "Authorization: Bearer $TOKEN" \
	-H 'Content-Type: application/json' \
	-d '{"message":"Give a one-paragraph summary of the company health index","persona":"analyst"}'
```

22. Appendix B: SQL schema (full)
--------------------------------

Below is a compact representation of the primary SQL schema used in this project. For exact migrations, see `migrations/`.

```sql
-- users
CREATE TABLE IF NOT EXISTS users (
	id UUID PRIMARY KEY,
	username TEXT UNIQUE NOT NULL,
	password_hash TEXT NOT NULL,
	role TEXT NOT NULL,
	is_active BOOLEAN DEFAULT true,
	preferred_language TEXT DEFAULT 'en',
	created_at TIMESTAMP DEFAULT now()
);

-- kpi_metrics (long format)
CREATE TABLE IF NOT EXISTS kpi_metrics (
	id SERIAL PRIMARY KEY,
	period TEXT NOT NULL,
	metric TEXT NOT NULL,
	value DOUBLE PRECISION,
	category TEXT,
	segment TEXT,
	unit TEXT,
	direction TEXT,
	source_name TEXT,
	ingested_at TIMESTAMP DEFAULT now()
);

-- files
CREATE TABLE IF NOT EXISTS files (
	id UUID PRIMARY KEY,
	owner_username TEXT NOT NULL,
	filename TEXT NOT NULL,
	path TEXT NOT NULL,
	size INTEGER,
	uploaded_at TIMESTAMP DEFAULT now()
);

-- oauth_states
CREATE TABLE IF NOT EXISTS oauth_states (
	state TEXT PRIMARY KEY,
	username TEXT NOT NULL,
	integration_type TEXT,
	created_at TIMESTAMP DEFAULT now()
);

-- integration_credentials
CREATE TABLE IF NOT EXISTS integration_credentials (
	id SERIAL PRIMARY KEY,
	username TEXT NOT NULL,
	integration_type TEXT NOT NULL,
	encrypted_payload TEXT NOT NULL,
	created_at TIMESTAMP DEFAULT now()
);

-- audit_log
CREATE TABLE IF NOT EXISTS audit_log (
	id SERIAL PRIMARY KEY,
	username TEXT,
	action TEXT NOT NULL,
	details TEXT,
	created_at TIMESTAMP DEFAULT now()
);
```

23. Appendix C: sample CSV and JSON datasets
-------------------------------------------

Small CSV:

```
period,metric,value,category,segment,unit,direction
2025-01,Revenue,1250000,Finance,Global,USD,higher_is_better
2025-01,MRR,420000,Growth,Global,USD,higher_is_better
```

Sample JSON for `ingest/metrics`:

```json
{
	"data": [
		{"period":"2025-01","metric":"Revenue","value":1250000,"category":"Finance","segment":"Global","unit":"USD","direction":"higher_is_better"}
	],
	"source_name":"api"
}
```

24. Appendix D: command reference for scripts/
--------------------------------------------

`./scripts/start_all.sh [mode]` — builds docker images for the chosen mode (minimal|core|automation|full|all). Does not start containers.

`./scripts/start_containers.sh <profile|all|core>` — starts containers per profile.

`./scripts/stop_containers.sh` — stops containers started by compose.

25. Appendix E: developer checklists and pair-programming tips
-------------------------------------------------------------

- Running locally: ensure Python 3.10, pip, node/npm are installed.
- Run backend tests before opening PRs.
- When editing env defaults, mirror changes into `src/core/config.py` and document them here.

---

If you want the README to also include full auto-generated endpoint documentation (every route, every parameter, every response example) extracted programmatically from the codebase, I can generate that next — it will add several hundred more lines and precise examples per endpoint. Tell me if you want those included as well and I'll append them.

26. Appendix F: Programmatic API Reference (auto-generated from src/api/server_v2.py)
--------------------------------------------------------------------------

The section below was generated from the backend API source and documents the routes implemented in `src/api/server_v2.py`. It lists the HTTP method, path, authentication requirement, request/response schema (when explicit), example requests, example responses, common error conditions, and internal notes pointing to the source locations. Use these examples for integration work and automated tests.

Note: this is a best-effort programmatic extraction — consult `src/api/server_v2.py` for the authoritative implementation and any runtime behavior.

--

Endpoint: Health Check
- Method: GET
- Path: `/health`
- Auth: none
- Description: Lightweight service health probe used by containers and orchestrators.
- Response model:

	{
		"status": "healthy",
		"service": "IntelAI API",
		"version": "2026.3.0",
		"timestamp": "2026-05-13T...Z",
		"database": "postgresql"
	}

- Example:

	curl http://localhost:8000/health

- Notes: See `src/api/server_v2.py` (health_check). Used by Docker Compose healthchecks.

--

Endpoint: Status
- Method: GET
- Path: `/api/v1/status`
- Auth: Bearer token (current user) — `TokenData` via `get_current_user`
- Description: Returns operational metadata including total KPI count, available periods, categories and user role.
- Successful response example:

	{
		"status": "operational",
		"user": "demo_user",
		"role": "analyst",
		"total_kpis": 1234,
		"periods": ["2024-01","2024-02"],
		"categories": ["Finance","Growth"],
		"domains": ["Finance","Growth","People","Operations","IT","ESG"]
	}

- Errors: 401 if token invalid or missing.
- Notes: Internally calls `src.services.pg_store.get_kpi_metrics()` and other helpers.

--

Endpoint: Login
- Method: POST
- Path: `/api/v1/auth/login`
- Auth: none
- Request model: `LoginRequest` (username, password)
- Response: access token, token type, and user info (id, username, role, full_name, language, pages, data_access)
- Example request:

	curl -X POST http://localhost:8000/api/v1/auth/login \
		-H 'Content-Type: application/json' \
		-d '{"username":"admin","password":"change_me_postgres_password"}'

- Example response (200):

	{
		"access_token": "ey...",
		"token_type": "bearer",
		"user": {
			"id": "...",
			"username": "admin",
			"role": "admin",
			"full_name": "Admin",
			"language": "en",
			"pages": [ ... ],
			"data_access": [ ... ]
		}
	}

- Errors: 401 Invalid credentials; 403 Account deactivated
- Notes: Uses in-memory `_users_db` seeded from defaults or PostgreSQL `pg_store`.

--

Endpoint: Register
- Method: POST
- Path: `/api/v1/auth/register`
- Auth: none
- Request model: `RegisterRequest` (username, password, role, preferred_language)
- Restrictions: Public registration only allows roles `viewer` or `analyst`.
- Example request:

	{
		"username": "new_user",
		"password": "S3curePass!",
		"role": "viewer",
		"preferred_language": "en"
	}

- Example response (201):

	{"status":"registered","user_id":"<uuid>","username":"new_user"}

- Errors: 403 if role not allowed; 400 if username exists.

--

Endpoint: Get current user
- Method: GET
- Path: `/api/v1/auth/me`
- Auth: Bearer token
- Response fields: id, username, role, full_name, language, pages, data_access, preferred_language
- Example response:

	{
		"id": "...",
		"username": "demo",
		"role": "analyst",
		"full_name": "Demo User",
		"language": "en",
		"pages": [...],
		"data_access": [...],
		"preferred_language": "en"
	}

--

Endpoint: Chat (RAG / Personas)
- Method: POST
- Path: `/api/v1/chat`
- Auth: Bearer token
- Request model: `ChatRequest`
	- `message` (string) — required
	- `persona` (optional string)
	- `session_id` (optional string)
	- `context` (optional string)
- Response model: `ChatResponse`
	- `response` (string)
	- `persona_used` (string)
	- `persona_display` (string)
	- `tokens_used` (int)
	- `latency_ms` (int)
	- `session_id` (string)
	- `mode` (string)
	- `sources` (list)
	- `reasoning` (optional)
- Example request:

	{
		"message": "Summarize revenue trends for Q1 2025",
		"persona": "analyst"
	}

- Example response:

	{
		"response": "Revenue increased 8% QoQ...",
		"persona_used": "analyst",
		"persona_display": "Analyst Persona",
		"tokens_used": 123,
		"latency_ms": 456,
		"session_id": "...",
		"mode": "conversation",
		"sources": [ ... ],
		"reasoning": "..."
	}

- Notes: The backend uses `src.services.omnismart_chatbot.get_omnismart_chatbot()` and persona factory. Messages and responses are persisted to PG when available.

--

Endpoint: List Personas
- Method: GET
- Path: `/api/v1/personas`
- Auth: Bearer token
- Response: `{ "personas": [...] }`
- Notes: Returns available personas from persona factory.

--

Endpoint: OCR Extract
- Method: POST
- Path: `/api/v1/ocr/extract`
- Auth: Bearer token
- Payload: multipart/form-data file field `file`
- Behavior: Proxies file to OCR microservice at `OCR_SERVICE_URL` (default `http://omnitel-ocr:8001/extract`).
- Example (curl):

	curl -X POST http://localhost:8000/api/v1/ocr/extract \
		-H "Authorization: Bearer $TOKEN" \
		-F "file=@/path/to/file.pdf"

- Success: returns OCR JSON from microservice. 500 if extraction fails.

--

Endpoint: List Files
- Method: GET
- Path: `/api/v1/files`
- Auth: Bearer token
- Query params: `limit` (default 50), `offset` (default 0)
- Response: array of file metadata

--

Endpoint: File Preview
- Method: GET
- Path: `/api/v1/files/{file_id}/preview`
- Auth: Bearer token
- Response: `{"content": "<first 10000 chars>"}` or 404 if not found

--

Endpoint: File Download
- Method: GET
- Path: `/api/v1/files/{file_id}/download`
- Auth: Bearer token
- Response: file binary as `application/octet-stream` or 404

--

Endpoint: Integration Data
- Method: GET
- Path: `/api/v1/integrations/{integration_type}/data`
- Auth: Bearer token
- Supported `integration_type`: `gmail`, `sheets`, `clickup`
- Query param: `limit` (default 20)
- Response: integration-specific payload (list of messages/rows/tasks)
- Errors: 400 unsupported type; 500 on integration failure

--

Endpoint: Integrations Status
- Method: GET
- Path: `/api/v1/integrations/status`
- Auth: Bearer token
- Response: `{ "statuses": { "gmail": true, "sheets": false, ... } }`

--

Endpoint: Connect Integration (store credentials)
- Method: POST
- Path: `/api/v1/integrations/{integration_type}/connect`
- Auth: Bearer token
- Request body: JSON `credentials` dict (provider-specific)
- Behavior: serializes and encrypts credentials via `src.core.crypto.encrypt_value` and stores via `pg_store.store_integration_credentials`.

--

Endpoint: OAuth Start
- Method: GET
- Path: `/api/v1/integrations/{integration_type}/oauth/start`
- Auth: Bearer token
- Supported: `gmail`, `sheets`, `clickup`
- Response: `{ "url": "<provider_auth_url>", "state": "<state>" }`
- Notes: Stores short-lived state via `pg_store.store_oauth_state` for callback verification.

--

Endpoint: OAuth Callback
- Method: GET
- Path: `/api/v1/integrations/{integration_type}/oauth/callback`
- Auth: none (provider calls this)
- Query params: `code`, `state`
- Behavior: Exchanges `code` for tokens with provider (Google or ClickUp), encrypts/stores credentials, optionally stores refresh metadata, records audit event, then redirects to frontend with `integration=connected`.
- Errors: 400 missing code/state or invalid state; 502 token exchange HTTP errors; 500 other failures

--

Endpoint: Disconnect Integration
- Method: POST
- Path: `/api/v1/integrations/{integration_type}/disconnect`
- Auth: Bearer token
- Behavior: removes stored credentials via `pg_store.remove_integration_credentials`

--

Endpoint: Voice Transcribe
- Method: POST
- Path: `/api/v1/voice/transcribe`
- Auth: Bearer token
- Payload: multipart file `audio`
- Behavior: proxies audio to `VOICE_SERVICE_URL` for STT; returns `{ "text": "..." }` or 500 on failure

--

Endpoint: Voice TTS
- Method: POST
- Path: `/api/v1/voice/tts`
- Auth: Bearer token
- Form fields: `text` (string), `language` (string)
- Behavior: proxies to voice microservice; returns audio with `audio/mpeg` media type

--

Endpoint: Ingest Metrics
- Method: POST
- Path: `/api/v1/ingest/metrics`
- Auth: Bearer token
- Request model: `IngestMetricsRequest`
	- `data`: list[dict] — KPI rows (period, metric, value, category, segment, unit, direction)
	- `source_name`: string (default 'api')
	- `replace`: bool (default True)
- Behavior: converts list into pandas DataFrame and calls `pg_store.store_kpi_metrics(df, source_name, replace)`; logs audit event
- Example request:

	{
		"data":[{"period":"2025-01","metric":"Revenue","value":1250000,"category":"Finance","segment":"Global","unit":"USD","direction":"higher_is_better"}],
		"source_name":"api",
		"replace": true
	}

- Success response: `{ "status":"ingested", "rows": 1, "source": "api" }`

--

Source mapping
- The routes above are implemented in `src/api/server_v2.py` with route decorator locations near the following lines (for maintainers):
	- `/health` : line ~232
	- `/api/v1/status` : line ~243
	- `/api/v1/auth/login` : line ~262
	- `/api/v1/auth/register` : line ~302
	- `/api/v1/auth/me` : line ~328
	- `/api/v1/chat` : line ~347
	- `/api/v1/personas` : line ~409
	- `/api/v1/ocr/extract` : line ~420
	- `/api/v1/files` : line ~445
	- `/api/v1/files/{file_id}/preview` : line ~456
	- `/api/v1/files/{file_id}/download` : line ~468
	- `/api/v1/integrations/{integration_type}/data` : line ~490
	- `/api/v1/integrations/status` : line ~511
	- `/api/v1/integrations/{integration_type}/connect` : line ~527
	- `/api/v1/integrations/{integration_type}/oauth/start` : line ~547
	- `/api/v1/integrations/{integration_type}/oauth/callback` : line ~595
	- `/api/v1/integrations/{integration_type}/disconnect` : line ~725
	- `/api/v1/voice/transcribe` : line ~740
	- `/api/v1/voice/tts` : line ~762
	- `/api/v1/ingest/metrics` : line ~788

Appendix F end.

**Appendix G: Expanded Schemas & Example Responses**

The following are expanded, machine-friendly request and response schemas with concrete examples for common success and error cases. Use these as authoritative payload examples when writing integration tests or SDK clients.

- **Health Check**
	- Request: GET /health (no auth)
	- Success (200):

		{
			"status": "healthy",
			"service": "IntelAI API",
			"version": "2026.3.0",
			"timestamp": "2026-05-13T00:00:00Z",
			"database": "postgresql"
		}

	- Error: unlikely; container orchestrators should retry on non-200.

- **Login**
	- Request: POST /api/v1/auth/login

		{
			"username": "admin",
			"password": "secret"
		}

	- Success (200):

		{
			"access_token": "eyJhbGci...",
			"token_type": "bearer",
			"user": {
				"id": "00000000-0000-0000-0000-000000000000",
				"username": "admin",
				"role": "admin",
				"full_name": "Administrator",
				"language": "en"
			}
		}

	- Failure (401):

		{
			"error": "invalid_credentials",
			"message": "Username or password incorrect",
			"code": 401
		}

- **Chat (RAG + Persona)**
	- Request: POST /api/v1/chat

		{
			"message": "Summarize revenue trends for Q1 2025",
			"persona": "analyst"
		}

	- Success (200):

		{
			"response": "Revenue grew 8% quarter-over-quarter driven by increased subscription sales...",
			"persona_used": "analyst",
			"persona_display": "Analyst Persona",
			"tokens_used": 512,
			"latency_ms": 420,
			"session_id": "sid-123",
			"mode": "rag",
			"sources": [
				{ "id": "doc-2025-q1-rev", "score": 0.93, "cursor": 0 }
			],
			"reasoning": "Top-k retrieval followed by prompt synthesis"
		}

	- Error (400):

		{
			"error": "bad_request",
			"message": "Field 'message' is required",
			"code": 400
		}

- **Files (list)**
	- Request: GET /api/v1/files?limit=50&offset=0
	- Success (200):

		[
			{
				"id": "file-1",
				"owner_username": "demo",
				"filename": "board_report_Q1_2025.pdf",
				"path": "uploads/file-1.pdf",
				"size": 1234567,
				"uploaded_at": "2026-03-01T12:00:00Z"
			}
		]

- **Ingest Metrics**
	- Request: POST /api/v1/ingest/metrics

		{
			"data": [
				{ "period": "2025-01", "metric": "Revenue", "value": 1250000, "category": "Finance", "segment": "Global", "unit": "USD", "direction": "higher_is_better" }
			],
			"source_name": "api",
			"replace": true
		}

	- Success (200):

		{ "status": "ingested", "rows": 1, "source": "api" }

	- Failure (400):

		{ "error": "validation_error", "message": "Row 1 missing required field 'metric'", "code": 400 }

- **OAuth Callback (errors)**
	- Scenario: provider redirects with missing or invalid state
	- Response (400):

		{ "error": "invalid_oauth_state", "message": "State mismatch or expired", "code": 400 }

- **OCR Extract (proxy)**
	- Request: POST /api/v1/ocr/extract (multipart file)
	- Success (200):

		{ "text": "Extracted text from the provided document...", "pages": 3 }

	- Failure (500):

		{ "error": "ocr_failed", "message": "OCR microservice returned 500", "code": 500 }

- **Voice Transcribe**
	- Request: POST /api/v1/voice/transcribe (multipart audio)
	- Success (200):

		{ "text": "Meeting notes: revenue up 8%...", "language": "en" }

	- Failure (500):

		{ "error": "transcription_failed", "message": "Voice service unreachable", "code": 502 }

Notes
- These schemas mirror the `openapi.yaml` and `openapi.json` artifacts at the repo root. If you update `src/api/server_v2.py` routes or request/response shapes, regenerate the OpenAPI artifacts and append any new examples here.


