# EXECUTION PLAN: Week 0–Week 18 (Code Execution Tasks Only)

**Document Purpose:** Pure execution tasks, commands, and verification steps for building and shipping 6 projects in 18 weeks.
**No strategy narrative. No code implementation. Just tasks and their details.**

---

> **⚑ 2026-06-09 — PROJECT SPLIT.** Project #1 was renamed **OmniIntelOS → IntelAI**
> (scoped: analytics + persona RAG + GraphRAG-lite, one cloud deploy). The original
> all-in-one platform was moved to the private repo `Yacine-ai-tech/OmniIntelOS` with its
> own dedicated Studio (see its `PLATFORM_GUIDE.md`). On the shared `upwork` Studio,
> `~/OmniIntelOS` is now `~/IntelAI`. **Phase 1 below begins with a scope-down step** —
> this repo still physically carries the full feature set until then.

---

## 📊 Week 1 Implementation Status (as of 2026-06-07)

### ✅ Completed (Days 8-9):
- [x] Recharts conversion for AnalyticsPage (LineChart)
- [x] Recharts conversion for ForecastingPage (AreaChart + CI bands)
- [x] Recharts conversion for RiskPage (RadarChart)
- [x] Sparkline LineCharts for DashboardPage KPI cards
- [x] BarChart for FinancialPage line items with dropdown
- [x] Committed to branch: `feat/week-1-visual-technical-fixes`

### 🔄 Remaining (Days 10-12):
- [ ] Day 10: WebSocket streaming for chat (backend + frontend wiring)
- [ ] Day 10: Test all 9 personas through streaming
- [ ] Day 10: Verify token-by-token rendering and reconnect logic
- [ ] Day 11: Expand tests from 2 to 30+ (auth, chat, kpis, insights, forecast, ingest, rbac, monitoring)
- [ ] Day 11: GraphRAG-lite implementation (entity extraction, graph traversal, multi-hop queries)
- [ ] Day 11: Run pytest and fix failures
- [ ] Day 11: Confirm CI green on develop
- [ ] Day 12: Deploy to Railway/Fly.io
- [ ] Day 12: Run database migrations against production
- [ ] Day 12: Smoke test all endpoints in production

### 📝 Technical Notes:
- Recharts is already installed (v2.13.0 in package.json)
- WebSocket endpoint exists at `/api/v1/ws/chat` in server_v2.py
- Current implementation needs enhancement for true token-by-token streaming
- GraphRAG-lite requires: kpi_entities table, entity extraction service, graph traversal, hybrid retrieval integration

---

## ✅ UPDATED 2026-06-07 — Full Alignment with STRATEGY.md

This EXECUTION_PLAN.md has been comprehensively updated to include **all 2026 Stack Upgrades** claimed in STRATEGY.md and STRATEGY_DOC.md. 

### Key Additions by Project:

**IntelAI (Phase 1):**
- ✅ GraphRAG-lite implementation (entity extraction, sidecar tables, graph traversal)
- ✅ Entity overlap detection for multi-hop queries
- ✅ Graph-vs-vector quality delta recording (for RAGeval integration)

**AgentKit (Phase 3):**
- ✅ Claude Agent SDK demo (framework-agnostic positioning)
- ✅ CrewAI demo (multi-agent collaboration audience)
- ✅ DSPy experiment (research credential)
- ✅ MCP resources + prompts (2026 best practice)
- ✅ Multi-LLM configuration per agent type

**DocIntel (Phase 2):**
- ✅ Three-route extraction pipeline (vision_premium, vision_local, ocr_fallback)
- ✅ Vision LLM extractor with Claude Sonnet 4.6 Vision + Ollama Llama 3.2 Vision
- ✅ Marker integration for PDF-to-Markdown
- ✅ Surya OCR + DocTR for layout-aware OCR
- ✅ /classify-image endpoint for Equipment Sourcing pattern
- ✅ Vision-vs-OCR benchmark harness (research artifact)
- ✅ n8n integration templates

**VoiceFlow (Phase 4):**
- ✅ WhisperX upgrade with forced alignment + diarization
- ✅ Premium API providers (Deepgram Nova-3, AssemblyAI Universal-2)
- ✅ Multi-LLM analysis layer (Claude Sonnet 4.6 for sales, Groq for speed)
- ✅ Real-time voice agent demo (OpenAI Realtime API)
- ✅ TTS provider upgrades (Kokoro TTS, ElevenLabs, OpenAI tts-1-hd)
- ✅ Speaker diarization fallback chain (pyannote → NeMo → skip)

**RAGeval (Phase 5):**
- ✅ Multi-judge LLM evaluation with consensus (Claude Haiku + Groq + GPT-5-mini)
- ✅ OpenTelemetry / OpenLLMetry export (enterprise observability standards)
- ✅ Multi-embedding comparison endpoint (5 embedding models)
- ✅ Retrieval strategy benchmark endpoint (A/B testing for retrieval strategies)
- ✅ DSPy compilation telemetry (research community integration)
- ✅ pgvector production backend option (millions of interactions scale)

**StreamPulse (Phase 6):**
- ✅ First-class n8n integration (custom node + 3 workflows)
- ✅ Prefect 3 orchestration layer (research-strong)
- ✅ Hybrid domain classifier (keyword → embedding → LLM fallback)
- ✅ dlt declarative source ingestion (modern pipeline patterns)
- ✅ Vision-classification webhook (DocIntel synergy)
- ✅ Server-Sent Events as WebSocket alternative
- ✅ pgvector + DuckDB advanced storage options

### Implementation Status:
- **Requirements.txt files**: Already include most 2026 stack dependencies (LiteLLM, anthropic, openai, crewai, dspy-ai, prefect, etc.)
- **Docker setup**: All repos have docker-compose.dev.yml for Lightning Studio workflow
- **Missing implementation gaps**: Now scheduled in appropriate phases with specific day-by-day tasks

### Verification:
All upgrades align with STRATEGY.md sections:
- Project 1 IntelAI: Section 1.10 (Multi-LLM, Hybrid Retrieval, GraphRAG-lite, Qdrant)
- Project 2 AgentKit: Section 2.10 (Claude Sonnet + LangGraph + Claude Agent SDK + CrewAI + DSPy)
- Project 3 DocIntel: Section 3.10 (Vision-First: Claude Vision + Ollama Llama 3.2 Vision + Marker + Surya)
- Project 4 VoiceFlow: Section 4.10 (WhisperX + Deepgram + AssemblyAI + Realtime API + ElevenLabs)
- Project 5 RAGeval: Section 5.10 (Multi-Judge Consensus + OpenTelemetry + DSPy + pgvector)
- Project 6 StreamPulse: Section 6.10 (n8n + Prefect 3 + dlt + Vision-Composition + Hybrid classifier)

---
## ✅ PHASE 0 — COMPLETE (2026-06-05)

All Phase 0 success criteria met:
- 6 repos cloned in `upwork` Studio on `develop` branch
- All 6 Docker containers built and health-checked (`/health` 200 OK on ports 8000-8005)
- IntelAI connected to Neon Postgres (299 KPI rows seeded)
- All `.env` files set: GROQ, ANTHROPIC, TAVILY keys + SECRET_KEY + WEBHOOK_SECRET
- AgentKit MCP running over SSE on port 8005 (not stdio)
- Admin user bootstrapped: `admin / admin123`
- SSH tunnel active, all 6 ports reachable from laptop
- Frontend Vite running on laptop at `http://localhost:5173`, proxying to Studio `:8000`
- 7/7 tests passing (5 smoke + 2 live API including login)

**→ Phase 1 starts next.**
---

---

# ENVIRONMENT MODEL — Lightning AI Remote Dev (READ FIRST)

**Why this exists:** the local laptop is **2-core / 8 GB RAM**. It cannot build or run this stack (torch, sentence-transformers, FlagEmbedding/`bge-large` ~1.3 GB, chromadb, crewai, dspy, marker/surya OCR, whisperx, prefect, dlt). **All heavy work runs on Lightning AI.** The laptop only edits, browses, runs git, and at most runs the (light) React dev server.

## Hard rules
- **ONE Lightning Studio (free plan = 1 Studio total, not 1 at a time).** The Studio is named `upwork`. All 6 repos are cloned inside it. Never create a second Studio — the second one is billed.
- **Docker containers = the dependency isolation layer.** Each repo has a `docker-compose.dev.yml` that builds its `Dockerfile` and volume-mounts the source for hot-reload. This replaces venvs: each container is a fully isolated Python environment. The Studio has no venv; isolation comes from containers.
- **Docker: laptop NO, Studio YES.** Never `docker build`/`docker run` on the 2-core/8GB laptop. The Studio supports Docker fully (build, run, push to DockerHub). The Railway / GitHub-Actions builders are the fallback for image publishing.
- **Laptop stays light.** Laptop runs: VS Code (Remote-SSH), git, browser, and at most ONE React dev server (`npm run dev`). It **NEVER** runs Python ML deps, torch, uvicorn, Whisper, or Docker.
- **Only one container runs at a time.** `switch-project.sh` (in `~/` of the Studio) stops the current container and starts the target one. Docker layer cache persists on the Studio disk — first build is 3-8 min, every subsequent start is near-instant.

## The split
```
LAPTOP (2 core / 8 GB)            upwork Studio (Lightning — your only Studio)
─────────────────────────        ───────────────────────────────────────────────
VS Code + Remote-SSH             ~/IntelAI/  (git clone)
git (local clone for frontend)   ~/DocIntel/     (git clone)
browser (localhost:5173)         ~/VoiceFlow/    (git clone)
npm run dev (React, Vite)        ~/RAGeval/      (git clone)
                                 ~/StreamPulse/  (git clone)
                                 ~/AgentKit/     (git clone)
        │                        ~/switch-project.sh
        └─── SSH lightning-dev ──────────────────────┘
             (auto-forwards 8000-8005 in one connection)
```

## Per-repo Docker run (use switch-project.sh, not these directly)
| Repo | `docker-compose.dev.yml` start command | Port |
|---|---|---|
| IntelAI | `bash ~/switch-project.sh IntelAI` | 8000 |
| DocIntel    | `bash ~/switch-project.sh DocIntel` | 8001 |
| VoiceFlow   | `bash ~/switch-project.sh VoiceFlow` | 8002 |
| RAGeval     | `bash ~/switch-project.sh RAGeval` | 8003 |
| StreamPulse | `bash ~/switch-project.sh StreamPulse` | 8004 |
| AgentKit    | `bash ~/switch-project.sh AgentKit` (MCP/SSE) | 8005 |

## SSH (laptop → Studio)
Single SSH host entry: `lightning-dev` → `s_01kt2x8h2w3mg9hcgy83whmqjc@ssh.lightning.ai`.
Key: `~/.ssh/lightning_rsa`. All 6 ports forwarded in one connection.

- VS Code → Remote-SSH: Connect to Host → `lightning-dev` (auto-forwards ports)
- CLI: `ssh lightning-dev`

## Frontend wiring (zero code changes needed)
Vite dev proxy targets `localhost:8000`, `api.js` uses `/api/v1` — with the SSH connection open and the IntelAI container running, it all resolves with no changes:
- Laptop: `cd IntelAI/frontend && npm run dev` → `http://localhost:5173`.
- RAGeval and StreamPulse dashboards (built in their phases) run the same way on their ports.

## Databases
- **IntelAI** → **requires** Postgres → `POSTGRES_URL` set to Neon (already in `.env`).
- **AgentKit** → uses same Neon URL or runs stubbed (already in `.env`).
- **StreamPulse** → SQLite default (`store.py` → `streampulse.db` inside the container volume).
- **RAGeval** → SQLite default (`RAGEVAL_STORE=sqlite`).
- **DocIntel, VoiceFlow** → no database.

## Ollama — skip it
Leave all `LLM_LOCAL=ollama/...` and `OLLAMA_BASE_URL` vars blank. Use Groq/Anthropic/OpenAI (the defaults). No deliverable requires Ollama.

## AgentKit MCP — served over SSE inside the Studio
The container runs `python mcp_server.py` with `MCP_TRANSPORT=sse MCP_PORT=8005` (set in `docker-compose.dev.yml`). Port 8005 is forwarded by the SSH connection. Bridge Claude Desktop (laptop) to it:

`~/.config/Claude/claude_desktop_config.json`:
```json
{ "mcpServers": { "agentkit": { "command": "npx", "args": ["-y","mcp-remote","http://localhost:8005/sse"] } } }
```

## Daily workflow
1. Studio is already awake (it's your only Studio — keep it running or wake it when needed).
2. Connect: VS Code → Remote-SSH → `lightning-dev`. Edit files there; commit/push from there.
3. `bash ~/switch-project.sh <Repo>` — stops previous container, starts the target.
4. All 6 ports are forwarded by the SSH connection; whichever container is running responds.
5. Frontend: laptop `npm run dev`, port 5173.
6. Switching repos: just `bash ~/switch-project.sh <NextRepo>` — no reconnecting needed.

## How this rewrites the steps below
Throughout this plan:
- `source .venv/bin/activate` or `python -m venv .venv` → means `bash ~/switch-project.sh <Repo>` (start that repo's container). No venv exists; isolation is Docker.
- `docker build …` → runs inside the Studio (never on the laptop). `switch-project.sh` does this automatically via `docker compose -f docker-compose.dev.yml up --build`.
- "install in a clean/fresh venv" (PyPI publish verification) → `docker run --rm python:3.11-slim pip install <pkg>` inside the Studio, or `pip install --target /tmp/verify <pkg>` in the Studio shell.

---

# WEEK 0: Repository Splitting (Days 1–7)

## Day 1: Pre-Split Audit + Cleanup (6 hours total)

**Morning Session (3h):**
- Task 1a: Create git tag of monorepo as-is: `git tag pre-split-2026-05-18`
- Task 1b: Read /etc and /docs directories. List all files to evaluate for deletion:
  - COMPLETION_REPORT.md
  - INTEGRATION_PLAN.md
  - WORK_INDEX.md
  - Production_Readiness_Checklist.md
  - docs/200_TASKS_COVERAGE.md
  - omniinteloscompletestrategy (v1, replaced by v2)
  - Any *_NOTES.md or *_PLAN.md older than 30 days
- Task 1c: For each candidate deletion, run grep to find references in codebase
- Task 1d: Verify pyproject.toml and requirements.txt match actual imports. Run pip-check or pipreqs
- Task 1e: List shared utilities (logger.py, config.py, crypto.py, jwt_auth.py) and note which projects need full copies vs slim copies

**Afternoon Session (3h):**
- Task 1f: Re-read STRATEGY.md Appendix "Project Source Map" and verify file-to-project mapping matches current code
- Task 1g: Re-read STRATEGY.md Section 30 (splitting prompt) and mentally trace where it could fail:
  - Are imports in src.core.pg_engine standalone-importable?
  - Are there any tangled dependencies?
  - Does the monorepo have any hardcoded absolute paths?
- Task 1h: If imports are tangled, do minimal pre-clean (≤10 import refactors). Convert deep imports to shallow imports where safe.

**End of Day Checkpoint:**
- Pre-split git tag exists: `git tag -l | grep pre-split`
- Written list of files marked for deletion (in a notes file)
- Written list of import pre-edits needed (≤10 total)
- Can articulate in 60 seconds: "The splitting prompt extracts 6 standalone repos from the monorepo by [your summary]"

---

## Day 2: Splitting Prompt Dry-Run on DocIntel (7 hours total)

**Morning Session (4h):**
- Task 2a: Open NEW Claude Code session (clean context). Do NOT reuse main session.
- Task 2b: Copy ONLY the DocIntel section from Section 30 (PROJECT 3 block, ~400 lines)
- Task 2c: Provide the PROJECT 3 prompt to the new session. Let it create docintel/ and all files.
- Task 2d: Once done, in the **DocIntel Studio** (no venv — install into base env) run:
  - pip install -r requirements.txt
  - python -c "from services.ocr_enhancement import *"
  - python -c "from services.llm_extractor import LLMExtractor"
  - uvicorn api:app --port 8001 & (background)
  - curl http://localhost:8001/health (should return 200 OK)
- Task 2e: Test /classify endpoint: curl -X POST http://localhost:8001/classify -F file=@sample.pdf
  - If this works, DocIntel extraction is good. If it fails, note the exact error.

**Afternoon Session (3h):**
- Task 2f: If anything breaks, identify the root cause:
  - "from src.X import" left in files? (prompt missed import rewrite)
  - Missing __init__.py? (need to add to services/, core/, etc.)
  - Hardcoded paths? (grep for absolute paths in code)
  - Requirements.txt missing a dep? (check actual imports)
  - .env.example missing a var? (grep for os.getenv calls)
  - Dockerfile copies non-existent paths?
- Task 2g: For each gap found, note the exact symptom and update Section 30 of STRATEGY.md to fix it
- Task 2h: Re-run the prompt on DocIntel to confirm fix works
- Task 2i: Repeat until DocIntel starts cleanly from fresh clone

**End of Day Checkpoint:**
- `docintel/` directory exists with all files
- `uvicorn api:app` starts without errors
- /health endpoint responds with 200
- All imports resolve from project root (no "from src.*" anywhere)
- requirements.txt has no missing/extra deps
- Splitting prompt has been updated with any fixes discovered
- docstring on major classes/functions exists

---

## Day 3: Run Full Splitting Prompt for 5 Remaining Projects (8 hours total)

**Morning Session (5h):**
- Task 3a: Open NEW Claude Code session for Project 1 (IntelAI refactor). Sequential, not parallel.
  - Copy PROJECT 1 block from Section 30 (~200 lines, in-place refactor)
  - Let it apply all changes to existing repo
  - Immediately verify:
    - cd intelai/frontend && npm install recharts
    - cd .. && pytest tests/test_api.py (should still pass)
    - uvicorn src.api.server_v2:app --port 8001 & and curl /health
  - If fails, fix before moving to next project

- Task 3b: Open NEW session for Project 2 (AgentKit). 
  - Copy PROJECT 2 block (~300 lines)
  - Let it create agentkit/ directory and all files
  - Verify (in the AgentKit Studio, base env — no venv): pip install -r requirements.txt && python -c "import mcp_server"
  - Verify: python mcp_server.py (should start and list 6 tools)

- Task 3c: Open NEW session for Project 3 (DocIntel) — already mostly done Day 2, but now full version
  - Copy PROJECT 3 block
  - Verify all endpoints as on Day 2

- Task 3d: Open NEW session for Project 4 (VoiceFlow)
  - Copy PROJECT 4 block (~350 lines)
  - Create voiceflow/ directory
  - Verify (in the VoiceFlow Studio, base env): pip install -r requirements.txt && python -c "from faster_whisper import WhisperModel"

- Task 3e: Open NEW session for Project 5 (RAGeval)
  - Copy PROJECT 5 block (~350 lines)
  - Create rageval/ directory
  - Verify (in the RAGeval Studio, base env): pip install -r requirements.txt && python -c "from sentence_transformers import SentenceTransformer"

**Afternoon Session (3h):**
- Task 3f: Cross-project sanity checks (all 6 repos):
  - Confirm no project imports from another project (grep -r "from agentkit\|from docintel" etc in each project dir — should find nothing)
  - Confirm every project has: README.md, requirements.txt, Dockerfile, .env.example, .gitignore
  - Don't `docker build` on the laptop. If you want to build now, do it **inside the project's Studio** (`docker build -t <name>:test .`); otherwise just confirm the Dockerfile COPY paths reference files that exist and let the build happen at deploy time (Railway/Actions). Image builds happen in the Studio or on a remote builder — never on the laptop.
  - Use pip-compile or similar to check for unpinned versions
  - Write a 3-line summary in plain English of what each project does
    - If you can't write 3 clear lines, the README needs work — flag for that phase

**End of Day Checkpoint:**
- All 6 directories exist (each in its own Lightning Studio; laptop holds code-only clones)
- All 6 pass basic import/startup tests (run inside their Studio)
- All 6 have a Dockerfile whose COPY paths resolve (build it in the Studio or on the deploy builder — never on the laptop)
- You have written what each project does in your own words
- No cross-project imports exist

---

## Day 4: Per-Project Verification Pass + Test Skeletons (7 hours total)

**Morning Session (4h):**

For each of the six projects, run the following verification matrix:

| Project | Smoke Test | Deeper Verify |
|---------|-----------|---------------|
| intelai | pytest tests/ | All 9 personas resolve; chat endpoint returns text |
| agentkit | python mcp_server.py | MCP tools list correctly; workflow.analyze() returns dict |
| docintel | curl /classify with PDF | Returns doc_type within 5s |
| voiceflow | curl /health | Whisper loads (may take 30s first time) |
| rageval | python -c "import evaluator" | RAGEvaluator.score_interaction() runs on fake data |
| streampulse | curl /pipeline/status | WebSocket /live accepts connection |

For each project:
- Run the smoke test
- If smoke test passes, run the deeper verify
- Document the result in a notes file
- For projects without tests/, create tests/__init__.py and tests/test_smoke.py with one trivial assert

**Afternoon Session (3h):**

For each project, create STATUS.md (working notes, NOT committed):

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

**End of Day Checkpoint:**
- All 6 projects have deeper verify passing
- Each project has a STATUS.md with known gaps noted
- You have a list of pre-Phase 1 fixes needed for IntelAI
- All test skeletons in place (tests/__init__.py + test_smoke.py minimum)

---

## Day 5: Git Init + GitHub Push (Private) + Branch Strategy (6 hours total)

**Morning Session (3h):**

For each of the 6 projects:
- cd <project>
- git init
- Verify .gitignore is in place, then: git add . && git status (verify .venv, __pycache__, .env are NOT listed)
- git commit -m "initial: extracted from IntelAI monorepo (week 0)"
- Create GitHub repo as PRIVATE: gh repo create <yourname>/<project> --private --source=. --remote=origin
- git push -u origin main
- Verify: gh repo view <yourname>/<project>

Repos to create:
- intelai
- agentkit
- docintel
- voiceflow
- rageval
- streampulse

**Afternoon Session (3h):**

For each repo:
- Task 5a: Create develop branch for daily work: git checkout -b develop && git push -u origin develop
- Task 5b: Add .github/workflows/ci.yml with minimal GitHub Actions:
  - on: [push, pull_request]
  - runs-on: ubuntu-latest
  - Checkout code
  - Setup Python 3.11
  - pip install -r requirements.txt
  - pytest tests/ -v --tb=short
- Task 5c: Push the CI file to develop: git add .github/workflows/ci.yml && git commit -m "ci: add pytest workflow" && git push
- Task 5d: Run manual Actions trigger on each repo to confirm CI is green
  - If CI fails on any project, add it to that project's STATUS.md as "must fix in Phase N Day 1"

**End of Day Checkpoint:**
- 6 private GitHub repos exist
- Each has a develop branch
- Each has CI configured (may be failing for known reasons)
- You can run: gh repo view <name> for each one

---

## Day 6: Remote Environment Setup (Lightning Studios) + IDE Workspace (6 hours total)

> See **ENVIRONMENT MODEL** at the top of this doc. Heavy deps live in each repo's Lightning Studio (base env, no venv); the laptop stays light.

**Morning Session (3h) — provision the 6 Studios:**

- Task 6a: Create **6 Lightning Studios**, one per repo (IntelAI, DocIntel, VoiceFlow, RAGeval, StreamPulse, AgentKit). Keep only ONE awake at a time (free plan). Confirm each Studio's Python is 3.11.
- Task 6b: In **each** Studio, clone ONLY that one repo and install its deps into the **base env (no venv)**:
  - `git clone https://github.com/<you>/<repo>.git && cd <repo>`
  - `pip install -U pip wheel setuptools`
  - `pip install -r requirements.txt`
  - If `requirements-ml.txt` exists (DocIntel, VoiceFlow), install it here too — these big downloads land on the Studio disk and persist across sleeps.
  - Helper: `bash setup-new-laptop.sh studio <repo>` does steps b automatically.
- Task 6c: Provision **one free serverless Postgres** (Neon free tier — includes `pgvector`). Put its URL in `POSTGRES_URL` for the IntelAI, StreamPulse, and AgentKit Studios. RAGeval stays SQLite; DocIntel/VoiceFlow need no DB.
- Task 6d: On the **laptop**, install VS Code + the **Remote-SSH** + Python extensions. Connect to the awake Studio; confirm ports auto-forward (or use `ssh -L 8000:localhost:8000 <studio-host>`). Optionally make a `<name>.code-workspace` per Studio.

**Afternoon Session (3h) — secrets + smoke each Studio:**

- Task 6e: In each Studio, copy `.env.example` → `.env` and fill real values (GROQ_API_KEY, POSTGRES_URL, etc.).
  - Verify NONE of these `.env` files are committed: `git status` should NOT list them.
- Task 6f: Create a top-level `secrets.md` (outside any repo, kept on the laptop) with all keys and URLs — your single source of truth when something breaks at 11pm. NOT in any git repo.
- Task 6g: Run each FastAPI project once **in its Studio** end-to-end with real keys (deps already in base env):
  - `cd <repo> && uvicorn api:app --host 0.0.0.0 --port <repo-port> --reload` (IntelAI: `python -m uvicorn src.api.server_v2:app --host 0.0.0.0 --port 8000 --reload`; AgentKit: `python mcp_server.py`)
  - Forward the port and confirm `/health` responds from the laptop browser.

**End of Day Checkpoint:**
- 6 Lightning Studios exist, one repo each, deps installed in base env (no venv)
- One hosted Postgres provisioned; `POSTGRES_URL` set where needed
- VS Code Remote-SSH connects to a Studio and forwards its port
- All 6 have working `.env` (not committed)
- Each FastAPI project starts with uvicorn in its Studio and answers `/health`
- secrets.md exists on the laptop (NOT in any repo)

---

## Day 7: Buffer + Pre-Phase-1 Planning (6 hours total)

**Morning Session (3h):**

- Task 7a: Apply file deletions from Day 1 to IntelAI repo:
  - rm COMPLETION_REPORT.md INTEGRATION_PLAN.md WORK_INDEX.md Production_Readiness_Checklist.md
  - rm docs/200_TASKS_COVERAGE.md
  - rm omniinteloscompletestrategy
  - Commit: git add -A && git commit -m "chore: remove stale planning docs (v2 strategy supersedes)"
- Task 7b: Refactor IntelAI README to point at STRATEGY.md instead of deleted docs
- Task 7c: Ensure STRATEGY.md is committed to the repo

**Afternoon Session (3h):**

- Task 7d: In intelai repo, create TODO.md with Phase 1's Day 1-5 tasks in checkbox form
  - Copy from Section 16.2 of STRATEGY.md
  - You will check these off in real time during Phase 1
- Task 7e: Verify Recharts was installed in frontend during Day 3:
  - cd intelai/frontend && npm list recharts (should show installed)
- Task 7f: Identify which Upwork niches you'll start with on Day 12 of Phase 1
  - Recommended: RAG, FastAPI, AI chatbot
- Task 7g: Set personal calendar reminder for Phase 1 Day 1: "Build IntelAI visuals — Recharts replacement starts today"

**End of Week 0 Checkpoint:**
- All Day 1-6 checkpoints are green
- Stale docs deleted from intelai repo
- TODO.md exists in intelai for Phase 1
- You are not exhausted; you are ready for Phase 1
- You have not started Phase 1 work yet (respect the buffer)

**WEEK 0 SUCCESS CRITERIA (Overall):**
- 6 standalone project directories exist
- All 6 have passing smoke tests
- All 6 have private GitHub repos with develop branch
- All 6 have a Lightning Studio with deps installed (base env, no venv) + working .env + a Dockerfile reserved for deploy
- All 6 have CI configured (may be failing for known reasons)
- Each project has STATUS.md with known gaps
- IntelAI stale docs deleted, README updated
- TODO.md in intelai exists for Phase 1

**DO NOT START PHASE 1 until all above boxes are checked.**

---

# WEEK 0 SPLITTING PROMPT (COMPLETE — Run on Day 3)

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

  a) In frontend/: run npm install recharts and update package.json
  b) In frontend/src/pages/AnalyticsPage.jsx: replace SVG bars with Recharts LineChart
  c) In frontend/src/pages/ForecastingPage.jsx: replace table-based forecast with Recharts AreaChart (actual=green line, forecast=blue dashed, upper_ci/lower_ci as shaded band)
  d) In frontend/src/pages/RiskPage.jsx: add Recharts RadarChart of risk.components
  e) In frontend/src/pages/DashboardPage.jsx: add sparkline LineChart (height 60) of last 6 KPI values
  f) In frontend/src/pages/FinancialPage.jsx: replace stub with working page (dropdown of statement type, BarChart of line_items)
  g) In tests/test_api.py: expand from 2 tests to 30+ covering auth, chat, kpis, insights, ingest, rbac, monitoring, knowledge search
  h) Replace README.md with clean version (<200 lines): one-line description, what's built, Quick Start (3 commands), default credentials, API docs link, live demo URL, architecture diagram (ASCII)
  i) Create railway.toml with proper build/deploy config
  j) ADD 2026 stack upgrades:
     - pip install litellm>=1.55.0 anthropic openai
     - Create src/services/llm_router.py with llm_call(messages, tier=...) routing
     - Update omnismart_chatbot.py to use llm_router instead of direct Groq
     - Create src/services/hybrid_retrieval.py with HybridRetriever (dense + sparse + RRF + reranker)
     - Add USE_HYBRID_RETRIEVAL env flag
     - Add VECTOR_STORE env flag (chroma | qdrant)
     - Update requirements.txt with: rank-bm25, FlagEmbedding, qdrant-client, litellm, anthropic, openai

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
      planner_agent: uses litellm with LLM_REASONING (claude-sonnet-4-6)
      analyst_agent: uses LLM_DEFAULT (groq/llama-3.3-70b-versatile)
      reporter_agent: uses LLM_REASONING (claude-sonnet-4-6)
    All calls via litellm.acompletion(model=...)
    Public API: def analyze(question: str) -> dict

  agentkit/demos/claude_agent_sdk_demo.py:
    Uses claude_agent_sdk.Agent + MCPServer to call the same 6 tools

  agentkit/demos/crewai_demo.py:
    Uses CrewAI to wrap the same MCP tools as @tool decorators

  agentkit/research/dspy_experiment.py:
    DSPy module framing planner→analyst→reporter as compilable program

  agentkit/requirements.txt:
    fastmcp>=0.4.0, langgraph>=0.2.0, langchain>=0.3.0, litellm>=1.55.0,
    anthropic>=0.40.0, groq>=0.11.0, openai>=1.55.0, crewai>=0.86.0,
    dspy-ai>=2.5.0, psycopg[binary]>=3.1.18, pandas>=2.2.3, numpy>=2.1.3,
    scikit-learn>=1.5.2, chromadb>=0.5.18, sentence-transformers>=3.1.1,
    python-dotenv>=1.0.1, claude-agent-sdk>=0.1.0 (optional)

  agentkit/README.md:
    Title: "AgentKit — MCP Server for Business Intelligence Agents"
    Sections: What It Does, Tools (table), Resources, Prompts, Quick Start, Claude Desktop Setup, LangGraph Workflow, Claude Agent SDK, CrewAI Example, DSPy Experiment

  agentkit/.env.example:
    POSTGRES_URL, LLM_DEFAULT, LLM_REASONING, LLM_JUDGE, LLM_LOCAL,
    GROQ_API_KEY, ANTHROPIC_API_KEY, OPENAI_API_KEY

  agentkit/tests/test_mcp_tools.py:
    10+ tests for all 6 MCP tools, resources, prompts (mock DB if needed)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PROJECT 3: DocIntel
Goal: Vision-first document AI pipeline

CREATE new directory: docintel/

EXTRACT from IntelAI:
  src/services/ocr_enhancement.py  → docintel/services/ocr_extractor.py
  src/services/ocr/main.py         → docintel/services/tesseract_service.py
  src/integrations/camera.py       → docintel/services/camera.py
  src/core/logger.py               → docintel/core/logger.py
  src/core/config.py               → docintel/core/config.py (slim)

CREATE new files:

  docintel/api.py:
    GET  /health
    POST /extract (file + route: vision_premium|vision_local|ocr_fallback)
    POST /classify (file → doc_type only, fast)
    POST /classify-image (image + categories list → category + confidence)
    POST /extract-tables (PDF → tables list, via pdfplumber + Marker)
    POST /extract-llm (text + doc_type → structured dict)
    POST /batch/upload (list of files → job_id + background task)
    GET  /batch/{job_id}
    GET  /batch/{job_id}/results
    Serve demo/ as static at /demo

  docintel/services/vision_extractor.py:
    extract_via_vision_llm(image_bytes, model, doc_type) → dict
    Uses litellm.acompletion with image_url message format
    Prompts per doc_type: invoice, contract, receipt, financial_report, auction_listing, default
    Supports Claude Sonnet 4.6 Vision and Ollama Llama 3.2 Vision

  docintel/services/marker_extractor.py:
    Uses marker library to convert PDF → Markdown

  docintel/services/llm_extractor.py:
    LLMExtractor class with async extract(text, doc_type) for OCR-fallback route

  docintel/services/batch_processor.py:
    BatchProcessor with process / get_status / get_results methods

  docintel/demo/index.html:
    Single-page drag-and-drop demo (dark theme, vanilla JS, ~200 lines)
    Toggle between routes, show results

  docintel/demo/classify_image.html:
    For auction-listing classification

  docintel/eval/run_eval.py:
    Eval harness comparing routes A/B/C on benchmark dataset

  docintel/requirements.txt:
    fastapi>=0.115.0, uvicorn[standard]>=0.32.0, python-multipart>=0.0.12,
    litellm>=1.55.0, anthropic>=0.40.0, groq>=0.11.0, openai>=1.55.0,
    pdfplumber>=0.11.0, pytesseract>=0.3.10, pillow>=10.1.0, pypdf>=4.3.1,
    marker-pdf>=0.2.0, surya-ocr>=0.5.0, python-dotenv>=1.0.1,
    pandas>=2.2.3, aiofiles>=24.1.0

  docintel/README.md:
    Hero: "Vision-first document AI. Drop a PDF or image, get structured JSON in under 2 seconds."
    Three routes documented prominently. Live demo URL. Quick Start (3 commands).
    Eval results table.

  docintel/.env.example:
    LLM_DEFAULT, LLM_REASONING, LLM_VISION_PREMIUM, LLM_VISION_LOCAL,
    GROQ_API_KEY, ANTHROPIC_API_KEY, OLLAMA_BASE_URL

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PROJECT 4: VoiceFlow
Goal: Multi-provider speech-to-intelligence pipeline

CREATE new directory: voiceflow/

EXTRACT from IntelAI:
  src/services/voice/main.py       → voiceflow/services/voice_service.py
  src/integrations/tts.py          → voiceflow/services/tts_service.py
  src/core/logger.py               → voiceflow/core/logger.py

CREATE new files:

  voiceflow/services/whisperx_service.py:
    Uses whisperx for faster-whisper + alignment + pyannote diarization
    Falls back gracefully if pyannote not installed

  voiceflow/services/transcription_router.py:
    Routes transcribe() calls to: LOCAL_WHISPERX | GROQ_WHISPER | DEEPGRAM | ASSEMBLYAI

  voiceflow/services/meeting_analyzer.py:
    MeetingAnalyzer class with analyze_meeting, analyze_sales_call, analyze_support_call, etc.
    Each picks LLM model per ANALYSIS_MODELS dict

  voiceflow/api.py:
    GET  /health
    POST /transcribe (audio + provider)
    POST /tts (text + provider + voice)
    POST /analyze (text + analysis_type)
    POST /pipeline (audio + analysis_type → transcribe + analyze)
    POST /meeting/process
    POST /call/analyze
    WS   /stream (optional)
    WS   /realtime (OpenAI Realtime API bridge)
    Serve demo/ at /demo

  voiceflow/demo/record.html:
    Browser-recording demo (MediaRecorder API), 3-second countdown, ~250 lines vanilla JS

  voiceflow/demo/realtime.html:
    OpenAI Realtime API voice agent demo (WebRTC)

  voiceflow/requirements.txt:
    fastapi>=0.115.0, uvicorn[standard]>=0.32.0, python-multipart>=0.0.12,
    litellm>=1.55.0, anthropic>=0.40.0, groq>=0.11.0, openai>=1.55.0,
    edge-tts>=6.1.9, faster-whisper>=1.0.3, whisperx>=3.1.0, pyannote.audio>=3.1.0,
    python-dotenv>=1.0.1, requests>=2.32.3, aiohttp>=3.10.0,
    deepgram-sdk>=3.7.0 (optional), assemblyai>=0.30.0 (optional)

  voiceflow/README.md:
    Hero: "Speech → structured intelligence. Browser-recording demo. 4 providers, 5 analysis types."

  voiceflow/.env.example:
    LLM_DEFAULT, LLM_REASONING, LLM_JUDGE, GROQ_API_KEY, ANTHROPIC_API_KEY,
    OPENAI_API_KEY, HF_TOKEN, DEEPGRAM_API_KEY, ASSEMBLYAI_API_KEY

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
    RAGEvaluator class with methods:
      score_retrieval_relevance(query, chunks) → float
      score_groundedness_consensus(answer, context) → dict
        Multi-judge across [claude-haiku-4-5, groq llama 3.3 70b, gpt-5-mini]
      score_faithfulness(answer, chunks) → float
      calculate_cost(tokens, model, input_ratio=0.7) → float (USD)
      score_interaction(...) → dict
    Embeddings: BAAI/bge-large-en-v1.5 default

  rageval/store.py:
    SQLite default (~/.rageval/rageval.db); Postgres+pgvector optional
    Functions: init_rageval_table, log_interaction, get_metrics, get_query_log, get_cost_report

  rageval/api.py:
    GET  /health
    POST /eval/log
    POST /eval/score (no storage)
    GET  /eval/metrics?days=7
    GET  /eval/queries?limit=50&needs_review=true
    GET  /eval/cost-report?days=30
    GET  /eval/alerts
    POST /eval/retrieval-bench
    POST /eval/embedding-comparison

  rageval/decorator.py:
    @track(model="...") decorator wrapping any function

  rageval/otel_exporter.py:
    OpenTelemetry / OpenLLMetry export

  rageval/dspy_integration.py:
    Hook to log DSPy compilation runs

  rageval/cli.py:
    rageval init / rageval serve commands

  rageval/dashboard/ (React app):
    3 tabs: Overview | Query Log | Cost Report
    Recharts charts, dark theme

  rageval/requirements.txt:
    fastapi>=0.115.0, uvicorn[standard]>=0.32.0, litellm>=1.55.0,
    anthropic>=0.40.0, groq>=0.11.0, openai>=1.55.0,
    sentence-transformers>=3.1.1, FlagEmbedding>=1.3.0, scikit-learn>=1.5.2,
    numpy>=2.1.3, psycopg[binary]>=3.1.18, pgvector>=0.3.0,
    python-dotenv>=1.0.1, opentelemetry-api>=1.27.0, opentelemetry-sdk>=1.27.0,
    opentelemetry-exporter-otlp>=1.27.0, dspy-ai>=2.5.0

  rageval/README.md:
    Hero: "Drop-in LLMOps observability. Self-hosted. SQLite-default. Persona-aware. Multi-judge consensus."
    60-second pitch with code example. Comparison table vs competitors. Quick Start.

  rageval/.env.example:
    RAGEVAL_STORE, POSTGRES_URL, RAGEVAL_OTEL_ENDPOINT,
    LLM_JUDGE, LLM_DEFAULT, GROQ_API_KEY, ANTHROPIC_API_KEY, OPENAI_API_KEY

  rageval/pyproject.toml:
    [project] name = "rageval", version = "0.1.0"
    [project.scripts] rageval = "rageval.cli:main"

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

CREATE new files:

  streampulse/api.py:
    GET  /health
    POST /ingest/json
    POST /ingest/csv
    POST /ingest/email
    POST /webhook/{source_name} (with HMAC verify)
    POST /webhook/{source}/with-vision (composes with DocIntel classify-image)
    GET  /pipeline/status
    GET  /pipeline/history
    WS   /live
    GET  /live/sse (Server-Sent Events alternative)

  streampulse/connectors/webhook_receiver.py:
    HMAC verification, payload parsing, pipeline routing

  streampulse/connectors/n8n/:
    README.md, n8n_node.json, workflows/ (auction_aggregator.json, invoice_intake.json, crm_sync.json)

  streampulse/ingestion/dlt_sources.py:
    dlt-based declarative sources: gmail_source, gsheet_source, webhook_source

  streampulse/orchestration/prefect_flow.py:
    Prefect 3 flow with @task(retries=3) and @flow definitions

  streampulse/classifier.py (UPGRADED):
    classify(content, fast_only=False) → dict
    Fast path: keyword matching. Fallback: embedding similarity. Last fallback: Claude Haiku

  streampulse/dashboard/ (React):
    LiveDashboard.jsx with Recharts LineChart + PieChart, live record feed, WebSocket + SSE fallback

  streampulse/requirements.txt:
    fastapi>=0.115.0, uvicorn[standard]>=0.32.0, python-multipart>=0.0.12,
    litellm>=1.55.0, anthropic>=0.40.0, groq>=0.11.0, psycopg[binary]>=3.1.18,
    pgvector>=0.3.0, pandas>=2.2.3, numpy>=2.1.3, sentence-transformers>=3.1.1,
    aiohttp>=3.10.0, httpx>=0.27.0, python-dotenv>=1.0.1, requests>=2.32.3,
    dlt>=0.5.0, prefect>=3.0.0, duckdb>=1.1.0 (optional)

  streampulse/README.md:
    Hero: "Real-time business data pipeline. 6+ source types, live dashboard, first-class n8n integration."

  streampulse/.env.example:
    POSTGRES_URL, LLM_DEFAULT, LLM_JUDGE, GROQ_API_KEY, ANTHROPIC_API_KEY, WEBHOOK_SECRET

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EXECUTION ORDER:
1. ALWAYS start with Project 3 (DocIntel) as prompt-validation test
2. Then Project 1 (IntelAI refactor)
3. Then Projects 2, 4, 5, 6 in any order (independent)

QUALITY REQUIREMENTS FOR EACH PROJECT:
- All import paths work from project root (NO `from src.*` left)
- Every new file has a module docstring
- Every class has a docstring
- Every public async function has docstring with Args / Returns
- requirements.txt is minimal (only what that project needs)
- README is accurate (only claim what code actually does)
- .env.example has every required env var with a placeholder
- Dockerfile is valid (COPY paths resolve) — build it in the Studio (Docker is supported there) or on Railway/GitHub Actions, never on the laptop
- pytest tests/ has at least 5 smoke tests per project

DO NOT:
- Overclaim features not implemented
- Leave broken imports
- Create circular dependencies between projects
- Include unused dependencies
- Hardcode any credentials
- Skip the 2026 stack upgrades (LiteLLM, multi-provider env vars, etc.)

OUTPUT: Create all 6 project directories. Print summary: files created, tests passing, TODOs for human follow-up
```

---

# PHASE 1: IntelAI Foundation (Weeks 1–3, Days 8–27)

> **⚑ Phase 1 reframed (2026-06-09): "recreate IntelAI as the scoped product."**
> The full all-in-one platform was split out to the private `OmniIntelOS` repo + its own
> Studio (a done, structural step). This repo (`IntelAI`) still *physically* carries the
> full feature set, so **Phase 1 starts by scoping the codebase down** before the
> visual/technical fixes below.

## Day 8 (prerequisite): Scope-down to IntelAI
Remove the platform-only surface from this repo (see STRATEGY.md §1.1 CUT list):
- `git rm -r monitoring/ nginx/ n8n_workflows/ tunnels/ src/services/ocr/ src/services/voice/`
- Delete pages `ScannerPage.jsx, VoicePage.jsx, N8NWorkflowPage.jsx, IntegrationsPage.jsx, MonitoringPage.jsx` and their Sidebar/route entries.
- Replace the multi-service `docker-compose.yml` with a single-app dev compose (keep `docker-compose.dev.yml`) + `railway.toml` for cloud deploy; drop the `omnitel-ocr`/`omnitel-voice`/`prometheus`/`grafana`/`n8n`/`cloudflare-tunnel` services.
- Trim BulkData/DataHub to a simple CSV/JSON upload; remove heavy ingestion paths.
- Remove now-orphaned deps from `requirements.txt`; rename app identity strings OmniIntelOS→IntelAI in code (title, package, paths — docs are already renamed).
- **Verify:** app boots, `/health` 200, kept pages render, `pytest` green, no import errors from removed modules.

## Week 1: Visual + Technical Fixes (Days 8–12)

**Day 8: Recharts Conversion (Part 1)**
- cd intelai/frontend && npm install recharts && verify package.json updated
- Replace SVG bars in AnalyticsPage.jsx with Recharts LineChart
- Verify in browser: charts render, data loads from API
- Replace ForecastingPage.jsx chart with AreaChart + CI bands (afternoon)

**Day 9: Recharts Conversion (Part 2) + Risk + Dashboard**
- Add RadarChart to RiskPage.jsx (risk.components data)
- Add sparkline LineCharts to DashboardPage.jsx (last 6 KPI values, height 60)
- Complete FinancialPage.jsx: dropdown for income_statement/balance_sheet/cash_flow, BarChart of line_items
- Manual smoke test all 4 pages in browser

**Day 10: WebSocket Streaming for Chat**
- Read existing WebSocket chat endpoint in src/api/server_v2.py
- Fix any handler bugs (CORS, auth, persona routing)
- Wire ChatPage.jsx to /ws/chat instead of POST /chat
- Test all 9 personas through streaming
- Verify token-by-token rendering works, reconnect logic handles disconnect

**Day 11: Tests Expansion + GraphRAG-lite Implementation**
- Expand tests/test_api.py from 2 tests to 30+:
  - auth tests (5): login, wrong password, register, get me, token validation
  - chat tests (4): basic, persona, streaming, edge cases
  - kpis tests (4): get, periods, metrics, by category
  - insights tests (3): health, risk, summary
  - forecast tests (2): basic, with CI
  - ingest tests (3): valid, empty, malformed
  - rbac tests (4): admin works, viewer blocked, scope enforcement, edge cases
  - monitoring tests (3): stats, knowledge search, performance
  - misc tests (3): health, root, 404 handler
- **GraphRAG-lite Implementation (Research Credential Feature)**:
  - Create database migration for sidecar table: `kpi_entities(record_id, entity_type, entity_value)`
  - Implement entity extraction during KPI ingestion: extract {department, category, period, metric_name}
  - Create `src/services/graph_retrieval.py` with graph traversal logic
  - Implement query-time entity extraction using Claude Haiku 4.5
  - Add entity overlap detection for multi-hop queries
  - Integrate with hybrid retrieval: use graph results when query mentions ≥2 entities
  - Add `USE_GRAPH_RAG=true` config flag (opt-in during Phase 1, evaluate with RAGeval)
- Run pytest, fix all failures
- Confirm CI is green on develop branch

**Day 12: Railway Deploy + Smoke Test**
- Deploy to Railway (or Fly.io if Railway pricing exceeds budget). **Railway builds the image from the Dockerfile on its own builders — no local Docker needed** (push the repo / connect GitHub; `railway.toml` already sets the build + start command).
- Configure env vars in Railway dashboard (same keys as the Studio `.env`)
- Database: point `POSTGRES_URL` at the **Neon** project you already use in dev (or add a Railway/Supabase Postgres add-on for prod). One DB across dev + prod is fine to start.
- Run db migrations against production DB (from the IntelAI Studio: `alembic upgrade head` with the prod `POSTGRES_URL`)
- The React frontend deploys separately (Vercel/Netlify free, or Railway static) — build runs on their builder, not the laptop. Set its API base to the deployed backend URL.
- Smoke test every endpoint in production:
  - /health, /api/docs, /auth/login, /chat (with persona), /kpis, /insights/health, /forecast, WebSocket /ws/chat
- Document any prod-only failures, fix them
- Note the public URL — this becomes your Upwork demo link

**Week 1 Checkpoint:** All 4 chart pages use Recharts. WebSocket streaming chat works. 30+ tests passing. Live production URL exists.

## Week 2: Demo + Profile + First Proposals (Days 13–18)

**Day 13: README Rewrite + Stale Doc Cleanup**
- Rewrite README.md from scratch:
  - One-line description (<100 chars)
  - "What it does" (3-5 bullets, accurate)
  - "Quick Start" (3 commands max)
  - "Default Credentials" section (admin/admin → change immediately)
  - Link to /api/docs
  - Architecture diagram (ASCII, 10 lines max)
  - Demo link at the top
  - Total: <200 lines
- Final pass on stale-doc cleanup if anything missed
- Update top-level pyproject.toml metadata
- Commit and push develop → merge to main
- Tag v0.1.0

**Day 14: Loom Demo Recording (3-minute walkthrough)**
- Script the demo (write it out):
  - 0:00–0:15: Intro ("Hi, I'm Yacine. IntelAI is...")
  - 0:15–0:45: Login → dashboard → switch persona to CFO → show financial KPIs
  - 0:45–1:15: Chat with CFO persona → show streaming answer
  - 1:15–1:45: RiskPage → show RadarChart
  - 1:45–2:15: ForecastingPage → show AreaChart + CI bands
  - 2:15–2:45: Highlight bilingual, 9 personas, role-based data scoping
  - 2:45–3:00: "Demo at <URL>. Repo at <GitHub>. Contact on Upwork."
- Practice once with screen recording but no audio (timing)
- Record final take with audio
- Upload to Loom (free 5min plan is fine)
- Watch it back — is audio clear? Pacing? Did everything work?

**Day 15: Pre-Review With 3-5 Trusted Reviewers**
- DM the Loom link to 3-5 trusted reviewers:
  - 2 friends who know the field
  - 1-2 peers from Twitter/Discord (DM cold but politely)
  - 1 person outside tech (catches jargon)
- Ask: "60-second feedback. What's confusing? What works? What's missing?"
- While waiting:
  - Re-read the demo URL on a phone browser (mobile responsiveness check)
  - Test from incognito (auth flow, no cached state)
  - Run Lighthouse audit on frontend (speed, SEO, a11y)
- Collect feedback by evening. Iterate based on common themes.

**Day 16: Iterate Demo + Set Up Upwork Profile**
- Apply demo feedback: re-record if structural issues, edit caption if minor
- Set up Upwork profile:
  - Title: "AI Systems Engineer | RAG · MCP Agents · Document AI · LLMOps · FastAPI"
  - Overview (from STRATEGY.md Section 24, customize for your tone)
  - Skills (from Section 24)
  - Hourly rate: $65 (will raise after 3-5 reviews)
  - Professional photo
- Add IntelAI as portfolio entry #1:
  - Title: "IntelAI — AI Analytics with 9 C-Suite Personas"
  - Description: 3 bullets, lead with live demo link
  - 3 screenshots: dashboard, chat, forecasting page

**Day 17: Write 3 Vertical Proposal Templates**
- From STRATEGY.md Section 26, customize Templates 1, 2, 3 for your voice:
  - Template 1: RAG / AI chatbot jobs → leads with IntelAI demo
  - Template 2: FastAPI / backend jobs → leads with API design
  - Template 3: BI / analytics jobs → leads with multi-persona angle
- Each template:
  - Opens with specific reference to client's job post
  - Demo link in third line (not buried at bottom)
  - Asks 1-2 specific technical questions
  - Clear timeline and rate
- Save in Notion so you can copy/paste fast

**Day 18: First 10 Proposals Sent**
- Find 10 strong-fit jobs: 5+ client reviews, posted within 7 days, $30-80 hourly, <30 applicants
- Distribute across templates:
  - 4 RAG / chatbot jobs (Template 1)
  - 3 FastAPI / Python backend (Template 2)
  - 3 BI / dashboard / KPI (Template 3)
- Customize each proposal (don't blast generic)
- Log in Notion: date, job title, niche, demo link, template used, client country, client reviews, expected outcome
- Block calendar: more proposals + start Blog Post 1 tomorrow

**Week 2 Checkpoint:** Loom demo recorded, watched by 3+ reviewers. Upwork profile live with IntelAI portfolio entry. 10 proposals sent, all logged.

## Week 3: Volume Application + Blog Post 1 + PyPI Package (Days 19–27)

**Days 19-21: Daily Proposal Volume (Mon-Wed)**
- Each day:
  - Morning: send 8-10 proposals (target 30 by end of week)
  - Afternoon: monitor replies, respond to invites, review rejections for patterns
  - Log every proposal
- Side task each afternoon:
  - Day 19: Draft Blog Post 1 outline + opening paragraph
    - Title: "Persona-Routed RAG: One Retrieval, Nine Personas"
    - Sketch 5 sections, 100-word summary of each
  - Day 20: Write first half (~1000 words)
    - Focus: problem, solution, architecture diagram, code skeleton
  - Day 21: Write second half (~1000 words)
    - Focus: real examples (CFO vs CTO), evaluation metrics, what worked/didn't, future work

**Day 22: Blog Post 1 Reviewer Pass**
- Finish blog post draft (~2000 words total)
- Read aloud once — flag anything that sounds wrong
- Send to 2 reviewers (technical peer + writing-strong friend)
- Apply review feedback, add 3-5 code snippets, add 1 architecture diagram, add 1 evaluation table (if available)

**Day 23: Finalize Blog Post 1 Draft (NOT PUBLISHED — defer to 2027)**
- Save cleaned draft to: intelai/drafts/blog_post_1_persona_rag.md
- Save parallel LinkedIn-length draft (300 words) to: writing_workspace/linkedin_drafts/post_1_persona_rag_linkedin.md
- Save Hacker News "Show HN" draft (title + 200-word comment) to: writing_workspace/hn_drafts/show_hn_omniintelos.md
- Tag draft as "v1-pre-ship"
- DO NOT publish anywhere public (Section 5.1)
- More Upwork proposals (5-10)
- Update intelai GitHub README: reference live demo + Loom video link

**Day 24: Extract omnismart-personas Package**
- Create new sub-directory inside intelai: packages/omnismart-personas/ (or new repo)
- Structure:
  - omnismart_personas/__init__.py
  - omnismart_personas/templates.py (PERSONA_TEMPLATES dict with 9 personas)
  - omnismart_personas/router.py (resolve_persona() function)
  - omnismart_personas/context.py (PersonaContext dataclass)
  - pyproject.toml
  - README.md ("Drop-in 9-persona prompts for any LangChain RAG")
  - tests/test_templates.py, tests/test_router.py
- In the IntelAI Studio: `pip install -e .` — verify import works (no venv; base env is fine)

**Day 25: Publish omnismart-personas to PyPI**
- Create PyPI account if you don't have one (verify email)
- Install build tools (in the Studio): pip install build twine
- Build: python -m build
- Test upload: python -m twine upload --repository testpypi dist/*
- Verify the install in **isolation without a venv** (venv is blocked on the free plan): `pip install --target /tmp/verify -i https://test.pypi.org/simple/ omnismart-personas` then `PYTHONPATH=/tmp/verify python -c "import omnismart_personas"` — or test in a fresh throwaway Studio.
- Upload to real PyPI: python -m twine upload dist/*
- Verify: `pip install --target /tmp/verify2 omnismart-personas` (or a fresh Studio)
- Add PyPI badge to README
- Tweet/post about it (1 short sentence + link, no hype)

**Day 26: Continue Proposal Volume + Phase 1 Metrics Review**
- Send 5-10 more proposals (cumulative target: 50 by Day 27)
- Phase 1 metrics review:
  - Proposals sent: ___ (target: 50)
  - Replies: ___ (target: 5-10)
  - Interviews: ___ (target: 1-3)
  - Contracts: ___ (target: 0-1)
  - Blog post views: ___ (target: 100-500)
  - PyPI downloads (omnismart-personas): ___
  - GitHub stars (intelai if public): ___
- Review Notion proposal log: which template/niche converts best?

**Day 27: Buffer + Phase 2 Prep**
- Fix anything broken from the week
- Polish any rough edges in Loom demo or README
- Open docintel/ repo — read its STATUS.md (you wrote this Week 0 Day 4)
- Write Phase 2 TODO.md inside docintel/
- Confirm sample invoices are ready
- Pre-stage 50 invoice sources for Day 30:
  - Open government datasets (data.gov, eu-data-portal)
  - Public invoice samples (Stripe, Square, online templates)
  - 10-15 from synthetic dataset
- Save links in docintel/eval_sources.md

**Phase 1 Final Checkpoint:** IntelAI deployed. 4 chart pages use Recharts. WebSocket streaming working. 30+ tests passing. README < 200 lines. Loom demo pre-reviewed. Upwork profile live. 50 proposals sent, all logged. Blog Post 1 drafted. omnismart-personas published to PyPI. 0-3 interviews secured.

---

# PHASE 2: DocIntel (Weeks 4–6, Days 28–44)

**Goal:** Second portfolio entry live. Validates OCR/document AI freelance niche. DockerHub artifact published. Blog Post 2 drafted. 30+ OCR-niche proposals sent.

## Week 4: Core Build (api.py + LLM Extractor + Batch) — Days 28-32

**Day 28: Verify Extracted Repo + Build api.py**
- Open the **DocIntel Studio** and `cd docintel` (deps already in base env — no venv)
- Re-read STATUS.md (written Week 0 Day 4)
- Run pytest tests/ — confirm baseline passes
- Build api.py (FastAPI app) with endpoints:
  - GET /health
  - POST /extract (file + route: vision_premium | vision_local | ocr_fallback)
  - POST /classify (file → doc_type only, fast)
  - POST /classify-image (image + categories → category + confidence)
  - POST /extract-tables (PDF → tables list, via pdfplumber + Marker)
  - POST /extract-llm (text + doc_type → structured dict)
  - POST /batch/upload (list of files → job_id + background task)
  - GET /batch/{job_id} (status)
  - GET /batch/{job_id}/results
- Define ProcessResponse Pydantic model
- Serve demo/ as static files at /demo
- Local smoke test: uvicorn api:app and curl each endpoint with sample PDF

**Day 29: Build services/llm_extractor.py**
- Implement LLMExtractor class with async extract(text, doc_type) method
- Prompts for doc types:
  - invoice: [vendor, invoice_number, date, due_date, line_items, subtotal, tax, total, currency]
  - contract: [parties, effective_date, expiration_date, payment_terms, jurisdiction, key_clauses]
  - receipt: [merchant, date, total, currency, items, payment_method]
  - financial_report: [period, revenue, cogs, opex, ebitda, net_income, key_metrics_summary]
  - default: extract any structured info as flexible JSON
- Each prompt requests JSON output, temperature=0.1
- Strip markdown fences from response before json.loads
- Wire LLMExtractor into api.py's /extract-llm and /process endpoints
- Test with 3-5 real PDFs from enhanced_synthetic_dataset
- Note obvious failures — these become eval items in Week 5

**Day 30: Build services/batch_processor.py + Demo UI**
- Implement BatchProcessor class:
  - process(job_id, file_data_list) → background task
  - get_status(job_id) → {status, total, processed, failed, percent}
  - get_results(job_id) → list of processed results
- Use in-memory dict for job tracking (sufficient for demo)
- Wire into api.py's /batch/* endpoints
- Test with 5-document batch
- Build demo/index.html — single-page drag-and-drop demo:
  - Dark theme (#0f172a background)
  - Drop zone + file input
  - On drop: POST /process, show spinner
  - On response: show doc_type badge, confidence, processing time, structured JSON (pretty-printed)
  - Pure vanilla JS (no framework), ~150 lines
- Manual test: drag 3 different PDFs, verify each renders correctly

**Day 31: Polish + Local End-to-End**
- Run full local end-to-end: Upload via demo UI → process pipeline → LLM extract → render JSON
- Target: <5 seconds per document (premium positioning)
- Profile slow spots (likely Tesseract OCR or LLM call)
- Add response caching for repeat documents (hash file → check cache)
- Add request logging (every /process call logged to file or DB)
- Build the Dockerfile **in the DocIntel Studio** (`docker build -t docintel:dev .`) to confirm the Tesseract/poppler apt layers and COPY paths work — never on the laptop. (No Docker in your Studio? Lint with `hadolint` and let Railway/Actions build it on Day 38.)

**Day 32: Tests + CI**
- Expand tests/:
  - test_api.py: 8 tests for /health, /classify, /process, /batch/*
  - test_extractor.py: 5 tests for each doc_type
  - test_batch.py: 3 tests for batch lifecycle (upload, status, results)
  - test_demo.py: 1 smoke test that /demo serves the HTML
- Use fixtures: include 5 small test PDFs in tests/fixtures/
- Run pytest, fix failures
- CI green on develop branch

**Week 4 Checkpoint:** api.py exposes all 7 endpoints (2xx for valid inputs). LLMExtractor handles 4 doc types. BatchProcessor handles 5-doc batch. Demo works (frontend on laptop → backend in Studio). 15+ tests pass. Docker image builds in the Studio (or on Railway/Actions) — never on the laptop.

## Week 4.5: Vision-First Pipeline Implementation — Days 32.5-34.5

**Day 32.5: Implement Vision LLM Extractor (Three-Route Pipeline)**
- Create services/vision_extractor.py with multi-route extraction:
  - Route A: VISION_PREMIUM (Claude Sonnet 4.6 Vision) — best for complex layouts, handwriting
  - Route B: VISION_LOCAL (Ollama Llama 3.2 Vision 11B or Qwen 2.5-VL 7B) — privacy, cost-bound
  - Route C: OCR_FALLBACK (Tesseract + LLM cleanup) — legacy path
- Implement extract_via_vision_llm(image_bytes, model, doc_type):
  - Convert image to base64
  - Use LiteLLM with vision model (Claude Sonnet 4.6 Vision or Ollama vision)
  - Type-specific prompts (invoice, contract, receipt, etc.)
  - Request JSON output with confidence scores
- Add route parameter to /extract endpoint: POST /extract?route=vision_premium|vision_local|ocr_fallback
- Test all three routes with sample PDFs:
  - vision_premium: should handle complex layouts best
  - vision_local: should work but slower on CPU
  - ocr_fallback: baseline comparison
- Document three-route strategy in README with cost/latency tradeoffs

**Day 33: Marker Integration + Advanced OCR**
- pip install marker-pdf (for PDF-to-Markdown conversion)
- Create services/marker_extractor.py:
  - Use Marker's PdfConverter for high-quality PDF-to-Markdown
  - Target: documents where structured text intermediate is needed (RAG ingestion)
- pip install surya-ocr (for layout-aware OCR fallback)
- Create services/surya_extractor.py:
  - Implement Surya OCR with detection model and processor
  - Better than Tesseract for non-Latin scripts and complex layouts
- Update services/ocr_extractor.py to include fallback chain:
  - Primary: Surya OCR (if installed)
  - Fallback: Tesseract (legacy)
  - Last resort: pure LLM on images (no OCR intermediate)
- Test Marker on 5 PDFs, compare output vs pdfplumber
- Test Surya on 5 scanned documents, compare vs Tesseract
- Document OCR fallback chain in README

**Day 33.5: Enhanced /classify-image Endpoint (Equipment Sourcing Pattern)**
- Implement POST /classify-image endpoint:
  - Accepts image file + list of categories
  - Returns: {category, confidence, reasoning}
  - Supports route parameter (vision_local for Ollama, vision_premium for Claude)
- Create classification prompts for common categories:
  - Equipment types: excavator, crane, bulldozer, truck, etc.
  - Marketplace items: electronics, furniture, industrial, etc.
  - Business documents: invoice, contract, receipt, report
- Test /classify-image with sample images from different categories
- Measure accuracy and confidence scores
- Document /classify-image for Equipment Sourcing job applications
- Create demo showing image classification workflow

**Day 34: Vision-vs-OCR Benchmark Harness (Research Artifact)**
- Create eval/vision_vs_ocr_benchmark.py:
  - Load 200-document eval set (can reuse invoice eval + add other doc types)
  - Run benchmark across three routes:
    - Route A: Claude Sonnet 4.6 Vision
    - Route B: Llama 3.2 Vision (local via Ollama)
    - Route C: Tesseract → Claude Haiku 4.5 cleanup
  - Measure per-field accuracy, latency, cost per document
  - Output comparison table for blog post + preprint
- Run benchmark (may take several hours depending on Ollama performance)
- Analyze results: which route offers best cost/accuracy tradeoff?
- Save benchmark results to eval/benchmark_results_2026.json
- Document methodology for Blog Post 2 (drafted Week 6)
- This becomes research artifact: cost/quality tradeoffs in document AI

**Day 34.5: n8n Integration Templates (Workflow Automation)**
- Create integrations/n8n/ directory:
  - README.md: how to plug DocIntel into n8n workflows
  - DocIntel node template (n8n community node format)
  - workflows/: 3 ready-to-import n8n workflow demos
- Implement workflow examples:
  - invoice_intake.json: webhook → DocIntel → ERP system
  - contract_review.json: document upload → extraction → approval workflow
  - crm_sync.json: invoice processing → CRM data update
- Test n8n workflows with sample documents
- Document webhook endpoint signature verification (HMAC)
- Add n8n integration section to README
- This addresses Equipment Sourcing job's "n8n or similar workflow tools" requirement

## Week 5: Eval Dataset + Prompt Iteration — Days 33-37

**CRITICAL:** This is the most important week of Phase 2. Skipping produces a demo that looks good but fails on real client invoices. Budget 5 full days. Do NOT compress.

**Day 33: Collect 50 Real Invoices (Eval Set)**
- Source 50 diverse invoices (full day, focused task):
  - 15 from open government datasets (data.gov procurement, eu-data-portal vendor invoices)
  - 15 from public invoice samples (online templates, Stripe sample, Square sample, QuickBooks examples)
  - 10 from enhanced_synthetic_dataset (already have these)
  - 10 anonymized real-world ones (ask 5 friends for blanked invoices — explicitly anonymized)
- Store all 50 in docintel/eval/invoices/ as PDFs (numbered 01-50)
- Create docintel/eval/invoice_eval.jsonl with expected JSON for each:
  - Each line: {"file": "01.pdf", "expected": {...fields...}}
- Time: 4-6 hours collection, 2-3 hours hand-labeling
- This dataset earns your $65/hr rate

**Day 34: Initial Eval Run**
- Write docintel/eval/run_eval.py:
  - For each row in invoice_eval.jsonl:
    - result = await llm_extractor.extract(text, "invoice")
    - Compare result vs expected (per-field accuracy)
    - Log: filename, accuracy_per_field, hallucinations, missing_fields
  - Output: docintel/eval/results_v1.json
- Run the eval. Inspect the numbers:
  - Vendor name accuracy: ___%
  - Total amount accuracy: ___%
  - Date accuracy: ___%
  - Line items accuracy: ___%
- Baseline target: 60-75% on first run is typical. Below 60% = structural problem
- List top 3 failure modes by frequency

**Day 35: Prompt Iteration Round 1**
- Pick worst-performing field. Rewrite relevant prompt section to be more specific:
  - Line items fail: add "extract every row, even single-line items"
  - Totals fail: add "the total is the largest currency amount; if multiple totals, prefer the one labeled 'Total'"
  - Dates fail: specify expected format (ISO YYYY-MM-DD)
- Re-run eval. Track delta: did this field improve? Did others regress?
- Pick next worst field. Iterate.
- Document each prompt change with 1-line rationale
- End-of-day target: top-3 fields at 80%+

**Day 36: Prompt Iteration Round 2 + Few-Shot**
- Add 1-2 few-shot examples to invoice prompt (1 simple US invoice, 1 European-format invoice)
- Re-run eval. Few-shot usually moves needle 5-15% on tough fields.
- Consider hybrid extraction for specific fields:
  - Dates: post-process with dateparser library (more reliable than LLM for normalization)
  - Totals: regex over OCR'd text as fallback if LLM returns null
  - Line items: try JSON-mode (if Groq model supports) or function-calling format
- Re-run eval. Document which fields are now LLM-only vs hybrid.

**Day 37: Prompt Iteration Round 3 + Failure Mode Documentation**
- Final iteration: target 85%+ overall accuracy on key fields (vendor, total, date, currency)
- Other fields (line items, tax breakdown) can be lower; document in README as known limitations
- Write docintel/README.md "Known Limitations" section:
  - "Handwritten invoices: not supported (use external OCR)"
  - "Receipts with tip lines: tip amount sometimes misclassified into subtotal"
  - "Foreign currencies: USD, EUR, GBP, JPY supported; others may require config update"
  - "Multi-page invoices: only first page processed (Phase 2.1 work)"
- Final eval pass — record actual numbers. Use them in Blog Post 2.

**Week 5 Checkpoint:** 50-invoice eval set hand-labeled. Key field accuracy 85%+. Prompt iteration log documents every change and delta. README has honest Known Limitations. Numbers ready for Blog Post 2.

## Week 6: Ship + Blog Post 2 + OCR-Niche Proposals — Days 38-44

**Day 38: Deploy DocIntel + Demo Recording**
- Deploy DocIntel to Railway or Fly.io. **The platform builds the image from the Dockerfile on its builders — no local Docker** (the Tesseract/poppler apt installs run there; this is the first time the image is actually built, so watch the build log).
- Configure GROQ_API_KEY / ANTHROPIC_API_KEY env vars (use the Anthropic API vision path, not Ollama — see Environment Model)
- Smoke test all endpoints in production
- Record 90-second Loom demo:
  - 0:00–0:10: "DocIntel — drag a PDF, get structured JSON in <1 second"
  - 0:10–0:30: Drag sample invoice → show doc_type badge, confidence
  - 0:30–0:50: Drag contract → show different schema extracted
  - 0:50–1:10: Show eval metrics: 85% accuracy on 50-invoice test
  - 1:10–1:30: "Self-hosted, $20/mo to run. Open source on GitHub."
- Pre-review with 3 reviewers before finalizing

**Day 39: Publish to DockerHub + GitHub Public**
- Build and push the Docker image **from the DocIntel Studio** (Docker is supported there; never on the laptop):
  - `docker login`
  - `docker build -t <yourname>/docintel:latest -t <yourname>/docintel:0.1.0 .`
  - `docker push <yourname>/docintel:latest && docker push <yourname>/docintel:0.1.0`
  - (No Docker in your Studio? Add `.github/workflows/docker.yml` with `docker/build-push-action@v6` on tag `v*` + `DOCKERHUB_USERNAME`/`DOCKERHUB_TOKEN` secrets and push a tag to build on GitHub's runners.)
- Verify pullable: `docker pull <yourname>/docintel:latest` (from the Studio or any Docker host).
- Make GitHub repo public: gh repo edit <yourname>/docintel --visibility public
- Polish README:
  - Title + one-line description
  - Live demo link (Railway URL)
  - "What it does" (3 bullets, accurate)
  - Quick Start (3 commands)
  - Architecture diagram (ASCII)
  - Eval numbers (from Week 5)
  - Known Limitations (from Day 37)
- Tag v0.1.0: git tag v0.1.0 && git push --tags

**Day 40: Add DocIntel to Upwork Portfolio + OCR Proposals**
- Add DocIntel as Upwork portfolio entry #2:
  - Title: "DocIntel — PDF & Invoice AI Pipeline"
  - 3 screenshots: drag-drop demo, JSON output, eval results
  - Description: "PDF → classified + structured JSON in <1 sec. 85% accuracy on real invoices. Self-hosted."
- Customize Section 26 Template 3 for OCR/document AI jobs
- Send 10 OCR-niche proposals:
  - Filter Upwork: "OCR" "invoice extraction" "document AI" "PDF processing" "intelligent document"
  - Lead with DocIntel demo + 85% accuracy stat
- Log each in Notion

**Day 41: Blog Post 2 Draft**
- Title: "LLM-Enhanced OCR: Beyond Tesseract"
- Outline (5 sections, ~400 words each = ~2000 total):
  1. The problem: traditional OCR gives text, not data. Real-world need: structured fields with provenance.
  2. The architecture: file → classifier → OCR/text → LLM extract → JSON (with diagram)
  3. Prompt engineering for invoice extraction: JSON-mode requests, temperature 0.1, few-shot examples. When LLM is unreliable (dates, multi-currency). Hybrid approaches.
  4. Building an eval set: 50 invoices, hand-labeled. Show actual numbers per field.
  5. Production reality: latency, cost, error modes. Honest limitations + when to fall back to human review.
- Include 3-5 code snippets (real LLMExtractor code)
- Include eval results table

**Day 42: Blog Post 2 Polish + Save Draft (NOT PUBLISHED in 2026)**
- Send draft to 2 reviewers (peers, not publication)
- Apply feedback
- Save final draft to: docintel/drafts/blog_post_2_vision_first_doc_ai.md
- Save parallel LinkedIn draft to: writing_workspace/linkedin_drafts/
- Save Reddit r/MachineLearning draft (methodology-led) to: writing_workspace/reddit_drafts/
- Save Show HN draft to: writing_workspace/hn_drafts/
- Save eval methodology + numbers section verbatim — ammunition for 2027 arXiv preprint
- DO NOT publish anywhere public in 2026 (Section 5.1)

**Day 43: Phase 2 Metrics Review + Phase 3 Prep**
- Phase 2 metrics:
  - DocIntel deployed and accessible: ___
  - Eval accuracy: ___%
  - 10 OCR proposals sent: ___
  - Blog Post 2 views: ___
  - DockerHub pulls: ___
  - GitHub stars: ___
  - Phase 1+2 cumulative interviews: ___
  - Phase 1+2 cumulative contracts: ___
- Open agentkit/ — re-read STATUS.md from Week 0 Day 4
- Write Phase 3 TODO.md in agentkit/
- Confirm fastmcp is in requirements.txt (was installed Week 0?)
- Pre-stage MCP testing: install **Claude Desktop on the laptop** (it's a light desktop app). The MCP server itself runs in the AgentKit Studio — you'll bridge Claude Desktop to it over SSE (see Day 48 + the "AgentKit MCP" note in the Environment Model). Also `npm i -g mcp-remote` (or use `npx`) for the stdio→SSE bridge.

**Day 44: Buffer + Continue Volume**
- Fix anything broken from the week
- Continue OCR proposal volume (10 more today, cumulative 20+)
- Send 5 proposals on IntelAI-niche jobs (don't abandon Phase 1 niches)
- Plan Phase 3: when does Phase 3 Day 1 start?

**Phase 2 Final Checkpoint:** DocIntel deployed at public URL. 50-invoice eval set, 85%+ key-field accuracy. Demo recorded, README accurate. GitHub repo public. DockerHub image published. Blog Post 2 drafted (defer publishing to Q1 2027). Upwork portfolio entry #2 added. 30+ OCR-niche proposals sent. Cumulative 2-5 interviews, 1-3 contracts.

---

# PHASE 3: AgentKit (Weeks 7–9, Days 45–61)

**Goal:** Open-source MCP server published with traction. Third blog post drafted. GitHub stars (10+). MCP-niche proposals on Upwork. This is your **open-source primary** project — freelance is secondary; the win is GitHub stars, community recognition, cold-email leverage.

## Week 7: MCP Server Build (6 Tools) — Days 45-49

**Day 45: Verify Extracted Repo + Install fastmcp**
- Open the **AgentKit Studio** and `cd agentkit` (deps already in base env — no venv)
- Read STATUS.md (Week 0)
- pip install fastmcp (>= 0.4.0)
- Verify install: python -c "from fastmcp import FastMCP"
- Read FastMCP docs (15 min): https://github.com/jlowin/fastmcp
- Build mcp_server.py skeleton with 6 @mcp.tool() decorators. Make the transport configurable so it runs **over SSE in the Studio**: `if __name__ == "__main__": mcp.run(transport=os.getenv("MCP_TRANSPORT","sse"), host="0.0.0.0", port=int(os.getenv("MCP_PORT","8005")))` (stdio stays available for quick local REPL checks).

**Day 46: Implement Tools 1-3**
- Tool 1: query_kpis(domain, period_from, period_to, metric_filter, limit)
  - Calls services.pg_store.get_kpi_metrics(category=domain)
  - Filters by period and metric_filter
  - Returns: {kpis: [...], total: N}
- Tool 2: get_company_health(domain=None)
  - Calls get_kpi_metrics(), compute_health_index() (from insights.py)
  - Returns: {score: 0.78, interpretation: "Healthy", components: {...}}
- Tool 3: detect_kpi_anomalies(domain, method="zscore", threshold=2.5)
  - Calls get_kpi_metrics(category=domain) and detect_anomalies(df, method=method)
  - Returns: {anomalies: [...], total: N, threshold: 2.5}
- Test each tool in isolation via REPL

**Day 47: Implement Tools 4-6**
- Tool 4: forecast_metric(metric_name, periods=6, confidence_level=0.95)
  - Finds metric in get_kpi_metrics(), calls ForecastEngine().time_series_forecast()
  - Returns: {forecast: [...], upper_ci: [...], lower_ci: [...], method: "..."}
- Tool 5: list_available_metrics(domain=None)
  - Calls get_available_metrics(), get_available_categories(), get_available_periods()
  - Returns: {metrics: [...], categories: [...], periods: [...]}
- Tool 6: get_executive_summary()
  - Calls get_kpi_metrics(), compute_health_index()
  - Synthesizes into: {summary, health_score, key_metrics, anomalies, top_growth}
- Run mcp_server.py — confirm server starts and lists 6 tools

**Day 48: Connect Claude Desktop (laptop) to the remote MCP server (Studio)**
- In the AgentKit Studio: start the server over SSE — `MCP_TRANSPORT=sse MCP_PORT=8005 python mcp_server.py` (set POSTGRES_URL + GROQ_API_KEY in the Studio `.env`).
- Forward the port to the laptop: VS Code Remote-SSH auto-forwards 8005, or run `ssh -L 8005:localhost:8005 <studio-host>`.
- Open Claude Desktop config on the laptop (~/.config/Claude/claude_desktop_config.json on Linux). Add the AgentKit server via the stdio→SSE bridge (heavy server stays remote):
  - command: npx
  - args: ["-y", "mcp-remote", "http://localhost:8005/sse"]
- Restart Claude Desktop
- Verify: Claude sees the 6 tools (MCP indicator in UI)
- Test through Claude:
  - "What's our company health right now?" → triggers get_company_health
  - "Forecast revenue for next 6 months" → triggers forecast_metric
  - "Are there any anomalies in the Finance KPIs?" → detect_kpi_anomalies
- Note any tool that doesn't trigger — improve docstring, re-test

**Day 49: Tests + Fix Bugs**
- Write tests/test_mcp_tools.py:
  - 1 test per tool (6 tests minimum)
  - Mock pg_store / insights / forecasting if DB not available
  - Include edge cases: empty data, invalid domain, large datasets
- Run pytest, fix failures
- CI green on develop branch

**Week 7 Checkpoint:** mcp_server.py exposes all 6 tools. Claude Desktop sees and triggers each. 10+ tests pass. Tool descriptions clear enough that Claude routes correctly.

## Week 8: LangGraph Workflow (3 Agents) — Days 50-54

**Day 50: Install LangGraph + Build Planner Agent**
- pip install langgraph langchain-groq langchain
- Verify: python -c "from langgraph.graph import StateGraph"
- Create workflow.py with BusinessAnalysisState (TypedDict):
  - question: str, plan: str, tool_calls: list[dict], raw_data: dict, report: str, report_sections: dict, error: Optional[str]
- Implement planner_agent(state):
  - Uses litellm with LLM_REASONING (anthropic/claude-sonnet-4-6), temp=0.3
  - System prompt: "You are a planner. Given a business question, produce a 3-4 step analysis plan using available tools..."
  - Calls list_available_metrics() to know what's available
  - Returns state with state["plan"] populated
- Test in isolation: run planner_agent on 3 sample questions

**Day 51: Build Analyst Agent**
- Implement analyst_agent(state):
  - Reads state["question"] and state["plan"]
  - Routes to relevant MCP tools based on keywords:
    - "Finance"/"revenue"/"margin" → query_kpis("Finance") + detect_kpi_anomalies("Finance")
    - "People"/"HR"/"headcount" → query_kpis("People")
    - "Growth"/"customer"/"MRR" → query_kpis("Growth")
    - Always also call: get_company_health() + get_executive_summary()
  - Aggregates results into state["raw_data"]
- Test: run planner → analyst on 3 sample questions. Inspect state["raw_data"] — does it contain the right slices?

**Day 52: Build Reporter Agent**
- Implement reporter_agent(state):
  - Uses litellm with LLM_REASONING (claude-sonnet-4-6), temp=0.2
  - System prompt: "You synthesize raw data into executive reports with these sections: KEY FINDING, EVIDENCE, ROOT CAUSE, RECOMMENDED ACTION, RISK IF UNADDRESSED"
  - Input: state["question"], state["plan"], state["raw_data"]
  - Parses response into state["report_sections"]
  - Returns state with state["report"] and state["report_sections"]
- Test: run full chain on 3 questions, inspect final reports. Quality check: logical sections? Recommendations follow from evidence? Iterate prompts if weak.

**Day 53: Wire StateGraph + Public API**
- Build LangGraph StateGraph in workflow.py:
  - graph = StateGraph(BusinessAnalysisState)
  - graph.add_node("planner", planner_agent), ("analyst", analyst_agent), ("reporter", reporter_agent)
  - graph.set_entry_point("planner")
  - graph.add_edge("planner", "analyst"), ("analyst", "reporter"), ("reporter", END)
  - app = graph.compile()
- Public API: def analyze(question: str) -> dict
- Test analyze() on 5 business questions:
  - "What drove gross margin in Q1?"
  - "Are there hiring anomalies in the People domain?"
  - "Forecast revenue and growth for next quarter."
  - "What's our biggest risk right now?"
  - "Summarize the company's overall financial health."
- Time each call (should be 5-15 seconds total)

**Day 54: Demo Notebooks + Fixes**
- Create demos/claude_desktop_demo.ipynb:
  - Markdown cells explaining MCP setup
  - Screenshots of Claude Desktop UI showing tool calls
  - Example queries + responses
- Create demos/langgraph_workflow_demo.ipynb:
  - Code cells running analyze() on different questions
  - Display state["plan"], state["raw_data"] (truncated), state["report"]
  - Markdown commentary on each
- Polish workflow.py based on observations from 5 test questions
- Add error handling: if any agent throws, populate state["error"] gracefully and return partial results
- Final test pass — 5 questions, 5 clean reports

**Week 8 Checkpoint:** workflow.py runs 3-agent chain end-to-end. analyze() returns coherent reports for 5+ questions. Two demo notebooks exist. Latency acceptable (<20s per call).

## Week 8.5: Multi-Framework Extensions + Research Features — Days 54.5-56.5

**Day 54.5: Claude Agent SDK Demo (Framework Agnostic Positioning)**
- pip install claude-agent-sdk (verify availability, install if released)
- Create demos/claude_agent_sdk_demo.py:
  - Import Agent, MCPServer from claude_agent_sdk
  - Configure agent with model="claude-sonnet-4-6" and MCP server bridge
  - Demonstrate same 6 business questions using Claude Agent SDK orchestration
  - Show that agent achieves same results with different framework
- Test demo script: python demos/claude_agent_sdk_demo.py
- Document in README: "Framework-agnostic: works with LangGraph, Claude Agent SDK, CrewAI"
- This positions AgentKit as multi-framework compatible → major credibility lift

**Day 55: CrewAI Demo (Multi-Agent Collaboration Audience)**
- pip install crewai (already in requirements.txt from Week 0)
- Create demos/crewai_demo.py:
  - Define 3 CrewAI agents: Researcher (@tool for query_kpis), Analyst (@tool for detect_anomalies), Writer (synthesizes)
  - Wrap existing MCP tools as CrewAI @tool decorators
  - Define crew with sequential process: Researcher → Analyst → Writer
  - Run same business questions through CrewAI crew
  - Compare outputs vs LangGraph workflow (should be functionally equivalent)
- Test demo: python demos/crewai_demo.py
- Document CrewAI approach in README with code snippet (~80 lines)
- This captures clients who think in CrewAI's role abstractions

**Day 55.5: DSPy Experiment (Research Credential)**
- pip install dspy-ai (already in requirements.txt from Week 0)
- Create research/dspy_experiment.py:
  - Define BusinessAnalysis DSPy module with plan → analyze → report chain
  - Set up eval set: 50 business questions with expected outputs
  - Use DSPy BootstrapFewShot to optimize prompts on eval set
  - Log compilation runs: which prompt templates won, which examples chosen
  - Measure baseline vs optimized performance
- Run DSPy optimization: python research/dspy_experiment.py (may take 30-60 min)
- Document results: baseline accuracy ___%, optimized accuracy ___%
- Save optimized prompt templates for blog post + preprint
- This becomes research artifact: "DSPy-compiled agent workflow benchmarked"

**Day 56: MCP Resources + Prompts (2026 Best Practice)**
- Extend mcp_server.py beyond tools to include resources and prompts:
  - Add @mcp.resource("kpi://Finance/latest") — exposes latest Finance KPI snapshot as stable URI
  - Add @mcp.resource("kpi://People/latest") — same for People domain
  - Add @mcp.prompt("monthly_executive_briefing") — reusable prompt template for executive summaries
  - Add @mcp.prompt("risk_assessment") — reusable prompt for risk analysis
- Test resources: verify Claude can pin kpi://Finance/latest in context
- Test prompts: verify Claude can invoke monthly_executive_briefing without writing prompt text
- Update Claude Desktop config to include new resources/prompts
- Document MCP resources/prompts in README with examples
- This implements 2026 MCP best practice: tools + resources + prompts

**Day 56.5: Multi-LLM Configuration per Agent**
- Update workflow.py to use different LLM tiers per agent (from STRATEGY.md 2.10):
  - Planner agent: Claude Sonnet 4.6 (best for breaking down hard questions)
  - Analyst agent: Groq Llama 3.3 70B (high volume tool calls, speed matters)
  - Reporter agent: Claude Sonnet 4.6 (synthesis needs nuance)
- Configure via litellm with tier-based routing (already implemented in IntelAI llm_router.py pattern)
- Add env var controls: PLANNER_MODEL, ANALYST_MODEL, REPORTER_MODEL
- Test each agent with appropriate model, measure latency/quality tradeoffs
- Document multi-LLM strategy in README
- Update demos to show multi-LLM configuration in action

## Week 9: Distribution + Community + Blog Post 3 — Days 55-61

**Day 55: README + Demo Video**
- Write agentkit/README.md:
  - Title: "AgentKit — MCP Server for Business Intelligence Agents"
  - Hero: Claude Desktop screenshot showing tool list
  - Sections: What It Does, Tools Exposed (table), Quick Start, Claude Desktop Setup (JSON config), LangGraph Workflow, Architecture (ASCII), Roadmap
- Record 90-second demo:
  - 0:00–0:15: Show Claude Desktop with AgentKit tools listed
  - 0:15–0:45: Ask Claude a business question → watch it call 3 tools
  - 0:45–1:15: Show LangGraph workflow output (richer report)
  - 1:15–1:30: "Open source, MIT license. Link in description."
- Pre-review with 2-3 MCP-aware reviewers (DM Anthropic Discord folks)

**Day 56: Make Public + Submit to Lists**
- gh repo edit <yourname>/agentkit --visibility public
- Tag v0.1.0: git tag v0.1.0 && git push --tags
- Add LICENSE (MIT), CODE_OF_CONDUCT.md (GitHub standard template), CONTRIBUTING.md (how to add a tool)
- Submit to awesome-mcp listings:
  - github.com/punkpeye/awesome-mcp-servers
  - github.com/wong2/awesome-mcp-servers
  - Search GitHub for any other "awesome-mcp" lists
- Submit a PR to each — they usually merge fast

**Day 57: Community Posts**
- Anthropic Discord (#mcp channel): share repo with 2-3 lines: "AgentKit — MCP server exposing business analytics (KPIs, health score, forecasting, anomalies). 6 tools, works with Claude Desktop, Cursor, and LangChain agents. Open source: [link]"
- MCP-related Discords: similar message
- r/LocalLLaMA post (be useful, not promo):
  - Title: "Built an MCP server that lets Claude do business KPI analysis — 6 tools, open source"
  - Body: 2 paragraphs explaining use case + architecture, link to repo, link to demo video
- Respond to comments throughout the day

**Day 58: Blog Post 3 Draft**
- Title: "MCP Tool Design Patterns: From Database to AI Agent in 6 Tools"
- Outline:
  1. What MCP is, briefly (1 paragraph for newcomers)
  2. The 6 tools I built and why each one exists
  3. Tool description as the entire UX: Why "query_kpis" works but "get_data" doesn't. Parameter naming for LLM clarity. Returning structured data with metadata.
  4. Composability: why agentic workflows beat single tool calls (show LangGraph workflow example)
  5. What I'd build next (roadmap = invitation for contributors)
- Include 5-7 code snippets (real fastmcp decorators)
- Include the LangGraph state diagram

**Day 59: Blog Post 3 Polish + Save Draft (NOT PUBLISHED in 2026)**
- Send draft to 2 reviewers (1 MCP person, 1 tech-writing person)
- Apply feedback
- Save final draft to: agentkit/drafts/blog_post_3_mcp_patterns.md
- Save Hacker News "Show HN" draft to: writing_workspace/hn_drafts/ (Title: "MCP Tool Design Patterns: From Database to AI Agent (6 tools)")
- Save Reddit /r/LocalLLaMA + /r/MachineLearning drafts to: writing_workspace/reddit_drafts/
- Save LinkedIn cornerstone-supporting draft to: writing_workspace/linkedin_drafts/
- DO NOT publish anywhere public (Section 5.1). In Q1 2027 these go live in coordinated launch sequence.

**Day 60: MCP Proposals + Continue Volume**
- Search Upwork for: "MCP" "Model Context Protocol" "AI agent" "agentic AI" "LangGraph" "tool use"
- Send 5-10 MCP-specific proposals (Template 2). Lead with AgentKit GitHub link + Claude Desktop demo.
- Continue IntelAI + DocIntel niche proposals (5-10 today)
- Phase 3 metrics review:
  - AgentKit GitHub stars: ___ (target: 10+)
  - Demo video views: ___
  - Blog Post 3 traction: ___ HN points, ___ Medium claps
  - MCP-niche proposals sent: ___
  - Cold-email-worthy inbound DMs: ___
  - Phase 1-3 cumulative interviews/contracts: ___

**Day 61: Buffer + Phase 4 Prep**
- Fix anything broken from the week
- Respond to GitHub issues if AgentKit got some (this builds community)
- Open voiceflow/ repo — re-read STATUS.md
- Verify Whisper / faster-whisper installs cleanly (notorious dependency-hell project)
- Write Phase 4 TODO.md in voiceflow/
- Pre-stage audio test data: 2-3 short meeting recordings (yours or public domain podcasts), 1-2 sales call audio (public YouTube samples)

**Phase 3 Final Checkpoint:** AgentKit public on GitHub. 6 MCP tools working with Claude Desktop. LangGraph 3-agent workflow operational. Demo video recorded. Submitted to awesome-mcp lists. Posted in Anthropic Discord + MCP communities. Blog Post 3 drafted + HN/Reddit drafts saved. 10+ GitHub stars. 10+ MCP proposals sent. Phase 1-3 cumulative: 2-5 contracts, $5-15k earned.

---

# PHASE 4: VoiceFlow (Weeks 10–12, Days 62–78)

**Goal:** Voice-to-intelligence portfolio entry. Browser-recording demo is unique and memorable. Meeting analyzer / sales-call analyzer differentiates from generic transcription wrappers.

## Week 10: Voice Service + Meeting Analyzer — Days 62-66

**Day 62: Verify Whisper Install + Voice Service**
- Open the **VoiceFlow Studio** and `cd voiceflow` (deps already in base env — no venv)
- Re-read STATUS.md
- pip install -r requirements.txt (includes faster-whisper)
- python -c "from faster_whisper import WhisperModel; print('OK')"
- Download base model: WhisperModel("base", device="cpu", compute_type="int8") (~150MB first time — lands on the Studio disk and persists across sleeps; never on the laptop)
- Test transcribe on 30-second audio sample
- Measure latency. Aim for <2x realtime (30s audio → <60s transcribe)
- If bad: try "tiny" model first. For speed, **switch this Studio to a GPU instance** (Lightning free credits) and set `WHISPER_DEVICE=cuda` — dev only; production runs CPU on Railway.

**Day 63: Build services/voice_service.py**
- Implement transcribe_audio(audio_bytes, language="auto") → dict
  - Returns: {text, language, latency_seconds, method, segments}
  - Method = "faster-whisper" (Groq Whisper as fallback if API key set)
- Implement detect_language(audio_bytes) → str
- Optional: speaker_diarization (pyannote if available, fallback to None). Document fallback — pyannote install is notoriously fragile
- Test on 3 audio samples (English, French, mixed)

**Day 64: Build services/meeting_analyzer.py**
- Implement MeetingAnalyzer class:
  - analyze_meeting(transcript) → structured dict with: meeting_summary, duration_minutes, participants_mentioned, decisions, action_items: [{owner, action, due, priority}], key_numbers, open_questions, next_steps, sentiment, topics_covered
  - analyze_sales_call(transcript) → structured dict with: call_summary, prospect_company/contact/role, pain_points, objections: [{type, content}], buying_signals, budget_mentioned, deal_stage, crm_notes, overall_sentiment, likelihood_to_close
  - general_analysis(transcript) → structured dict
- All methods use litellm.acompletion with appropriate ANALYSIS_MODELS dict tier, temperature=0.2, return parsed JSON
- Test on 3 sample transcripts

**Day 65: Build api.py**
- Implement endpoints:
  - GET /health
  - POST /transcribe (audio file → {text, language, latency, method})
  - POST /tts (text + language → audio/mpeg streaming)
  - POST /analyze (JSON: {text, analysis_type} → dict)
  - POST /pipeline (audio file + analysis_type → transcribe + analyze)
  - POST /meeting/process (audio file → meeting notes JSON)
  - POST /call/analyze (audio file → sales call JSON)
  - WS /stream (optional)
- Serve demo/ at /demo
- Wire TTS service from services/tts_service.py (edge-tts)
- Test /tts: curl with text → returns audio bytes
- Test /pipeline: upload meeting.mp3 with analysis_type=meeting → full output

**Day 66: Test + Polish**
- Tests:
  - test_voice.py: 4 tests (transcribe, language detect, edge cases)
  - test_analyzer.py: 6 tests (meeting, sales, general, edge)
  - test_api.py: 5 tests (all endpoints)
  - test_pipeline.py: 2 end-to-end tests
- Run pytest, fix failures
- Polish: error handling for unsupported audio formats
- Build the Dockerfile **in the VoiceFlow Studio** (`docker build -t voiceflow:dev .`) — decide now: bundle the Whisper model into the image, or download at start (see Day 69). Never build on the laptop.

**Week 10 Checkpoint:** Whisper transcription works on 3 test files. MeetingAnalyzer + SalesCallAnalyzer return well-structured JSON. All 7 endpoints respond correctly. Tests pass.

## Week 10.5: 2026 Stack Upgrades — WhisperX + Multi-Provider + Real-Time Voice — Days 66.5-68.5

**Day 66.5: WhisperX Upgrade with Alignment and Diarization**
- pip install whisperx (upgrade from faster-whisper)
- Create services/whisperx_service.py:
  - Load WhisperX large-v3 model with GPU support if available
  - Implement forced alignment (word-level timestamps)
  - Implement pyannote diarization integration (who-spoke-when)
  - Add fallback chain: pyannote 3.x → NeMo built-in diarization → skip diarization
- Update transcribe_audio to use WhisperX when available:
  - Returns transcript with speaker labels and word timestamps
  - Fallback to faster-whisper if WhisperX fails
- Test WhisperX on sample audio with multiple speakers
- Document diarization fallback chain honestly in README
- This implements 2026 SOTA self-hosted transcription

**Day 67: Premium API Provider Integration (Deepgram + AssemblyAI)**
- pip install deepgram-sdk-python assemblyai
- Create services/transcription_router.py:
  - Implement TranscriptionProvider enum: LOCAL_WHISPERX, GROQ_WHISPER, DEEPGRAM, ASSEMBLYAI
  - Add provider-specific transcription methods
  - Configure per-client provider selection via env var or request parameter
- Implement Deepgram Nova-3 integration (best diarization quality)
- Implement AssemblyAI Universal-2 integration (strong streaming)
- Add Groq Whisper integration (already has Groq API, just add Whisper model)
- Update /transcribe endpoint to accept provider parameter
- Test each provider with sample audio, measure latency/quality/cost
- Document provider tradeoffs in README

**Day 67.5: Multi-LLM Analysis Layer Configuration**
- Update services/meeting_analyzer.py with per-analysis-type model selection:
  - meeting: Groq Llama 3.3 70B (speed, structured output)
  - sales_call: Claude Sonnet 4.6 (nuance critical for objections/sentiment)
  - support_call: Claude Haiku 4.5 (cheap, high-volume)
  - interview: Claude Sonnet 4.6 (quality matters)
  - general: Groq Llama 3.3 70B
- Add ANALYSIS_MODELS configuration dict with tier-based routing
- Update each analysis method to use appropriate model via LiteLLM
- Test each analysis type with appropriate model
- Measure quality differences (sales analysis should benefit from Claude Sonnet nuance)
- Document multi-LLM strategy in README

**Day 68: TTS Provider Upgrades (Kokoro TTS + ElevenLabs + OpenAI)**
- pip install kokoro-onnx elevenlabs (add to requirements.txt)
- Create services/tts_router.py:
  - Implement TTS providers: edge-tts (default), Kokoro TTS (self-host premium), ElevenLabs (paid premium), OpenAI tts-1-hd (paid alternative)
  - Add provider selection via env var or request parameter
- Implement Kokoro TTS integration (open-source, expressive)
- Implement ElevenLabs integration (best voice quality + cloning)
- Implement OpenAI tts-1-hd integration (reliable HD voice)
- Update /tts endpoint to accept provider parameter
- Test each TTS provider with sample text
- Measure voice quality and latency tradeoffs
- Document TTS options in README with cost/quality matrix

**Day 68.5: Real-Time Voice Agent Demo (OpenAI Realtime API)**
- Create demos/realtime_voice_agent.py:
  - Implement WebRTC server endpoint /realtime/ws
  - Bridge to OpenAI Realtime API (gpt-4o-realtime-preview)
  - Sub-second latency voice-in → model processing → voice-out
  - Integrate with AgentKit MCP tools for business intelligence queries
- Demo scenario: "Talk to your business analyst" — real-time KPI questions
- Test real-time voice agent with sample business questions
- Measure end-to-end latency (target <500ms)
- This demonstrates cutting-edge real-time voice AI + cross-project AgentKit synergy
- Document Realtime API setup in README

## Week 11: Browser Recording Demo + Deploy — Days 67-72

**Day 67: Build demo/record.html**
- Single-page browser recording demo (~200 lines vanilla JS):
  - Dark theme (#0f172a)
  - "Click to record" button (idle: purple, recording: red pulsing)
  - MediaRecorder API for microphone audio
  - On stop: send audio blob to /transcribe via fetch
  - Display transcript with fade-in animation
  - Then auto-call /analyze with selected analysis_type (radio: Meeting / Sales Call / General)
  - Display structured JSON with syntax highlighting
  - Final UI: transcript on left, JSON on right
- Mobile responsive (phone browsers)
- Test in Chrome, Firefox, Safari

**Day 68: Visual Polish + UX**
- Add 3-second countdown when user clicks record (reduces awkward pause)
- Add waveform visualization while recording (Web Audio API)
- Add prominent "stop and analyze" button
- Add 3 sample audio buttons ("Try with sample meeting", "Try with sample sales call", "Try with sample interview") for users who can't record their own
- Test on real users (DM 3 friends, ask to try for 60 seconds)
- Iterate based on what was confusing

**Day 69: Deploy**
- Deploy VoiceFlow to Railway or Fly.io (the platform builds the image on its builders; or push the image you built+pushed from the Studio on Day 66)
- IMPORTANT: Whisper model downloads on first container start. Pre-bake into the Docker image (build it in the Studio) OR mount a persistent volume
  - Cold-start without pre-baked model = 60+ seconds, will tank demos
- Test thoroughly in production:
  - Record from production URL with Chrome
  - Verify transcription works (Whisper alive in container)
  - Verify analysis works (Groq API key configured)
- Document any production-only failures, fix them

**Day 70: Demo Video + Pre-Review**
- Record 90-second Loom demo:
  - 0:00–0:10: "VoiceFlow — speech to structured intelligence"
  - 0:10–0:30: Click record, talk: "Let's discuss Q2 launch. Alice will own marketing, due May 15..."
  - 0:30–0:50: Stop → show transcript appearing → show JSON output: action items, owner=Alice, due=2026-05-15, etc.
  - 0:50–1:10: Switch to Sales Call analysis → repeat with sales script
  - 1:10–1:30: "Self-hosted, open source. Link in description."
- Pre-review with 3 testers
- Apply demo feedback, re-record if needed

**Day 71: README + GitHub Public**
- Write README.md:
  - Hero: GIF of someone speaking → JSON appearing (Loom GIF export)
  - What It Does (3 bullets: transcription, meeting notes, sales CRM)
  - Quick Start (3 commands)
  - Use Cases (table: meeting notes, sales call CRM, support QA)
  - Architecture (ASCII)
  - Tech: faster-whisper + Groq LLM + edge-tts
- Make GitHub repo public, tag v0.1.0, add LICENSE (MIT)

**Day 72: Phase 4 Halfway Review + Continue Volume**
- Add VoiceFlow as Upwork portfolio entry #4 (after AgentKit which was #3)
- Customize Section 26 Template 4 for voice/transcription jobs
- Send 5-10 voice-niche proposals:
  - Filter: "Whisper" "speech to text" "meeting notes AI" "sales call analysis" "transcription pipeline"
- Continue MCP / OCR / RAG niche volume
- Phase 4 halfway check: any inbound interest from Phase 1-3 ramping?

**Week 11 Checkpoint:** Browser recording demo works end-to-end. Deployed at public URL with Whisper preloaded. Demo video recorded. GitHub repo public.

## Week 12: Blog Post 4 + Distribution + Voice Proposals — Days 73-78

**Day 73: Blog Post 4 Draft**
- Title: "From Audio to Action Items: Speech-to-Intelligence Pipelines"
- Outline:
  1. The gap: transcription gives words, not insight. Real value is structured layer after transcript.
  2. Architecture: audio → Whisper → LLM analyzer → JSON
  3. Prompt design for meeting analysis: 8 fields and why each. Handling ambiguity (action items with no clear owner). Sentiment that isn't fake-empathetic.
  4. Sales call analysis: CRM-paste-ready format. Why this is different from meeting notes. Pain point detection, objection types, deal stage inference.
  5. Cost and latency reality: faster-whisper base model: ~2x realtime, free. Groq LLM analysis: ~$0.0005 per call, <2s. End-to-end: $0.001 per minute of audio.
  6. What I'd build next: real-time streaming, diarization (pyannote if you can install it)

**Day 74: Polish + Save Blog Post 4 Draft (NOT PUBLISHED in 2026)**
- Send draft to 2 reviewers (peers, not publication)
- Apply feedback
- Save final draft to: voiceflow/drafts/blog_post_4_speech_intelligence.md
- Save subreddit posts (r/LanguageTechnology, r/speech_recognition) to: writing_workspace/reddit_drafts/
- Save Discord/Slack drop-in messages (Whisper Discord, AI-in-business) to: writing_workspace/community_drafts/
- Save LinkedIn draft to: writing_workspace/linkedin_drafts/
- DO NOT publish anywhere public (Section 5.1)

**Day 75: Voice Proposals Volume**
- Send 15+ voice-niche proposals
- Lead with browser-recording demo (memorable hook)
- Mention 85%+ accuracy stat from DocIntel + structured-output capability from VoiceFlow
- Continue IntelAI / DocIntel / AgentKit niches (5+ each)
- Total proposals today: 25-30

**Day 76: Phase 4 Metrics + Phase 5 Prep**
- Phase 4 metrics:
  - VoiceFlow deployed: ___
  - Demo video views: ___
  - Blog Post 4 traction: ___
  - Voice-niche proposals sent: ___
  - Inbound DMs / cold-email replies: ___
  - Phase 1-4 cumulative interviews/contracts: ___
- Open rageval/ repo — re-read STATUS.md
- Write Phase 5 TODO.md
- Decide: SQLite default vs PostgreSQL? (Recommend SQLite default for drop-in deploy; Postgres as optional)
- Pre-stage: collect 5-10 query/answer pairs for testing scorers (synthesize from IntelAI chat logs)

**Day 77: Buffer + Continue Volume**
- Fix anything broken from the week
- Continue proposal volume
- Respond to DMs from Blog Post 4 / community posts
- Plan Phase 5 kickoff timing

**Day 78: Phase 5 Kickoff Prep**
- Full day off (Sunday) — protect this. Burnout in month 3 kills the plan.
- If you must work: read 1-2 LLMOps blog posts from competitors (Phoenix, Langfuse, TruLens, Helicone) — know what you're differentiating against

**Phase 4 Final Checkpoint:** VoiceFlow deployed at public URL. Browser recording demo works. GitHub repo public. Demo video recorded. Blog Post 4 drafted + community drafts saved. Upwork portfolio entry #4 added. 15+ voice-niche proposals sent. Phase 1-4 cumulative: 3-7 contracts, $10-25k earned.

---

# PHASE 5: RAGeval (Weeks 13–15, Days 79–96)

**Goal:** LLMOps observability tool published to PyPI. Highest research-value project — sets up arXiv preprint in Phase 6 and signals to research programs that you ship production observability.

## Week 13: Evaluator + Store — Days 79-83

**Day 79: Verify Repo + Build Evaluator (Part 1)**
- Open the **RAGeval Studio** and `cd rageval` (deps already in base env — no venv)
- Re-read STATUS.md
- pip install sentence-transformers scikit-learn numpy FlagEmbedding
- Verify: python -c "from sentence_transformers import SentenceTransformer"
- Build evaluator.py with RAGEvaluator class:
  - __init__: loads SentenceTransformer("BAAI/bge-large-en-v1.5") once
  - score_retrieval_relevance(query, retrieved_chunks) → float 0-1: cosine_similarity(query_embedding, chunk_embeddings).mean()
  - score_groundedness(answer, context_chunks, model) → float 0-1: LLM-as-judge with prompt "Is this answer supported by the context? Score 0-1."
- Test each scorer on 5 sample query/answer/chunks tuples

**Day 80: Build Evaluator (Part 2) — Multi-Judge Consensus**
- Add score_groundedness_consensus(answer, context) → dict:
  - JUDGE_MODELS = ["anthropic/claude-haiku-4-5", "groq/llama-3.3-70b-versatile", "openai/gpt-5-mini"]
  - For each model in JUDGE_MODELS: score = await llm_judge_groundedness(answer, context, model=model)
  - Returns: {consensus: mean, stdev: std, judges: [...], flag_for_review: stdev > 0.2}
- Add score_faithfulness(answer, context_chunks) → float 0-1 (embedding similarity NLI proxy)
- Add calculate_cost(tokens_used, model, input_ratio=0.7) → float (USD)
  - GROQ_PRICES, ANTHROPIC_PRICES, OPENAI_PRICES dicts
- Add score_interaction(query, answer, retrieved_chunks, tokens_used, latency_ms, model, persona=None) → dict
  - Runs all 4 scorers, computes overall_quality = 0.4*relevance + 0.4*groundedness + 0.2*faithfulness
  - Identifies flags: LOW_RETRIEVAL_RELEVANCE (relevance < 0.5), POTENTIAL_HALLUCINATION (groundedness < 0.6), HIGH_LATENCY (latency_ms > 5000)

**Day 81: Build store.py**
- SQLite-default (~/.rageval/rageval.db); Postgres+pgvector optional via RAGEVAL_STORE env
- Functions:
  - init_rageval_table() — creates rageval_log table with fields: id, timestamp, query, answer, persona, model, relevance, groundedness, faithfulness, cost_usd, latency_ms, tokens_used, flags, session_id, needs_review
  - async log_interaction(query, answer, persona, scores, session_id) → None
  - get_metrics(days=7) → dict: avg_relevance, avg_groundedness, avg_faithfulness, avg_latency_ms, total_queries, total_cost_usd, flagged_count, query_volume_by_hour
  - get_query_log(limit=50, needs_review=None) → list
  - get_cost_report(days=30) → daily_costs, total_cost, by_model
- Test: log 20 fake interactions, query metrics, verify aggregates

**Day 82: Build api.py**
- Endpoints:
  - GET /health
  - POST /eval/log (body: query, answer, chunks, tokens_used, latency_ms, model) — computes scores, stores
  - POST /eval/score (body: query, answer, chunks) — returns scores without storage
  - GET /eval/metrics?days=7
  - GET /eval/queries?limit=50&needs_review=true
  - GET /eval/cost-report?days=30
  - GET /eval/alerts (recent flagged queries)
  - POST /eval/retrieval-bench (A/B test retrieval strategies)
  - POST /eval/embedding-comparison (compare embedding models on relevance)
- Test all endpoints with curl + fake data
- Confirm SQLite file is created at first /eval/log call

**Day 83: Decorator API + Tests**
- Build rageval/decorator.py:
  - @track(model="...") decorator that wraps any function
  - Captures: input query (from first arg), output answer, latency
  - Auto-logs to RAGeval store via /eval/log
  - Drop-in usage: from rageval import track; @track(model="..."); def answer_question(query, context_chunks): ...
- Build rageval/otel_exporter.py — OpenTelemetry/OpenLLMetry export when RAGEVAL_OTEL_ENDPOINT is set
- Build rageval/dspy_integration.py — hook to log DSPy compilation runs
- Tests:
  - test_evaluator.py: 6 tests (each scorer + score_interaction)
  - test_store.py: 4 tests (init, log, get_metrics, get_query_log)
  - test_api.py: 5 tests (each endpoint)
  - test_decorator.py: 2 tests (sync + async function wrapping)

**Week 13 Checkpoint:** All 5 scorers (incl. cost + multi-judge consensus) return values. SQLite store logs and aggregates correctly. 9 API endpoints respond. @track decorator works on sample RAG function. 17+ tests pass.

## Week 13.5: Advanced 2026 Stack Features — OpenTelemetry + Multi-Embedding + DSPy — Days 83.5-85.5

**Day 83.5: OpenTelemetry / OpenLLMetry Export Implementation**
- Complete rageval/otel_exporter.py (started Day 83):
  - Implement OpenTelemetry tracer and metrics setup
  - Create export_interaction(interaction) function:
    - Sets span attributes: query, relevance, groundedness, cost_usd, persona
    - Creates metrics for: rag.query.count, rag.relevance, rag.groundedness, rag.cost_usd
  - Configure OTLP exporter for Datadog, Honeycomb, Jaeger, Grafana compatibility
  - Add env var: RAGEVAL_OTEL_ENDPOINT=http://localhost:4317
- Test OTEL export with local OTEL collector or mock
- Verify span and metric data flows correctly
- Document OTEL export configuration in README
- This implements enterprise observability standards (critical for research credibility)

**Day 84: Multi-Embedding Model Comparison**
- Extend evaluator.py to support multiple embedding models:
  - EMBEDDING_MODELS_AVAILABLE = [
    - "sentence-transformers/all-MiniLM-L6-v2" (legacy baseline)
    - "BAAI/bge-large-en-v1.5" (current open SOTA)
    - "BAAI/bge-m3" (multilingual)
    - "Snowflake/snowflake-arctic-embed-l" (2025-2026 strong open)
    - "jinaai/jina-embeddings-v3" (code-friendly)
  - ]
- Implement POST /eval/embedding-comparison endpoint:
  - Runs same query set against multiple embedding models
  - Returns per-embedding relevance scores, latency, cost
  - Recommends best embedding model for client's use case
- Create eval/embedding_models_benchmark.py:
  - 100-query benchmark across all embedding models
  - Measures: relevance@5, recall@10, latency, cost
  - Generates comparison table for blog post
- Run benchmark (may take 30-60 minutes depending on models)
- Document embedding model tradeoffs in README
- This helps clients choose optimal embedding models for their RAG systems

**Day 84.5: Retrieval Strategy Benchmark Endpoint**
- Implement POST /eval/retrieval-bench endpoint (started Day 82):
  - Accepts strategy name (dense, hybrid_dense_sparse, hybrid_with_reranker, graph_rag_lite)
  - Runs 200-query benchmark against configured retrieval strategy
  - Returns: precision@5, recall@10, MRR, latency, cost
  - Compares strategies side-by-side
- Create eval/retrieval_strategies.py:
  - Implement pure dense retrieval (baseline)
  - Implement hybrid retrieval (dense + BM25 + RRF)
  - Implement hybrid with BGE reranker
  - Implement GraphRAG-lite (entity-based retrieval from IntelAI)
- Test each retrieval strategy on standard eval set
- Generate comparison table for blog post + preprint
- Document retrieval strategy recommendations in README
- This positions RAGeval as A/B testing tool for retrieval strategies

**Day 85: DSPy Compilation Telemetry Integration**
- Complete rageval/dspy_integration.py (started Day 83):
  - Implement @dspy_compile_callback decorator:
    - Logs DSPy compilation runs: program_name, candidates, winner, eval_metric, eval_score
    - Stores in RAGeval store as dspy_compilation_log table
  - Create research/dspy_experiment.py:
    - Define BusinessAnalysis DSPy module (plan → analyze → report)
    - Use DSPy BootstrapFewShot to optimize on eval set
    - Log all compilation runs via RAGeval integration
  - Run DSPy optimization on 50-question business analysis eval set
  - Measure baseline vs optimized performance
  - Analyze which prompt templates won and why
- Document DSPy integration in README
- This positions RAGeval in DSPy community (research-active audience)
- Results become section in AgentKit + RAGeval preprint

**Day 85.5: pgvector Production Backend Option**
- Update store.py to support Postgres + pgvector for production scale:
  - Check RAGEVAL_STORE env var: "sqlite" (default) or "postgres"
  - If "postgres": use POSTGRES_URL for connection
  - Add pgvector for embedding storage (makes retrieval-relevance queries fast)
  - Create migration: rageval_log table with vector column for query embeddings
  - SQLite remains default for zero-config drop-in usage
- Test both SQLite and Postgres backends
- Document pgvector setup in README (connection string, schema)
- Add migration script: alembic upgrade head for Postgres users
- This enables RAGeval to store millions of interactions efficiently
- Critical for production deployments with high query volume

## Week 14: Dashboard + PyPI Publish — Days 84-90

**Day 84: Dashboard Build (React) (Part 1)** — runs on the LAPTOP (Node), backend in the RAGeval Studio
- On the laptop, in your local RAGeval clone: `npx create-vite dashboard --template react`
- cd dashboard && npm install recharts
- Configure proxy in vite.config.js: `server: { proxy: { '/eval': 'http://localhost:8003' } }` (8003 = RAGeval backend, forwarded from its Studio)
- Build App.jsx with 3 tabs: Overview | Query Log | Cost Report
- Implement Overview tab:
  - 3 metric cards (avg relevance, avg groundedness, avg latency)
  - LineChart: quality score over time (7 days)
  - BarChart: query volume by hour
  - Fetches from /eval/metrics?days=7

**Day 85: Dashboard Build (Part 2)**
- Implement Query Log tab:
  - Fetch from /eval/queries?limit=50
  - Table columns: time, query (truncated), relevance, groundedness, latency, cost, flags
  - Color-code rows: green (quality > 0.7), yellow (0.4-0.7), red (< 0.4)
  - Toggle: "Show flagged only" → re-fetch with needs_review=true
- Implement Cost Report tab:
  - Fetch from /eval/cost-report?days=30
  - LineChart: daily cost over 30 days
  - Summary: total cost, avg per query, projected monthly
  - Model breakdown table
- Polish: dark theme (#0f172a), consistent with IntelAI
- Manual test: generate 50 fake interactions, verify dashboard renders

**Day 86: PyPI Package Prep**
- Restructure into installable package:
  - rageval/__init__.py (exposes: track, RAGEvaluator, init_db)
  - rageval/evaluator.py, store.py, decorator.py, cli.py (rageval init / serve commands)
- pyproject.toml with [project] name="rageval", version="0.1.0", dependencies=[sentence-transformers, scikit-learn, ...] + [project.scripts] rageval = "rageval.cli:main"
- README.md (marketing surface — see Day 87)
- Test in the RAGeval Studio (base env, no venv): `pip install -e .`, `rageval init` → creates SQLite DB, `from rageval import track` → works. For a true clean-install check use `pip install --target /tmp/verify .` or a fresh Studio.

**Day 87: Polish README (Marketing-Critical)**
- RAGeval's README is its growth engine. Structure:
  - Title + badges (PyPI version, build status, license)
  - Hero: "Drop-in LLMOps observability for RAG systems. Self-hosted. SQLite-default. Persona-aware."
  - The 60-second pitch (decorator code example)
  - What It Measures (5 metrics with definitions)
  - Comparison table vs Phoenix, Langfuse, TruLens, Helicone (be honest):
    - RAGeval vs Phoenix vs Langfuse vs TruLens
    - Self-hosted, SQLite default, Drop-in decorator, Persona-aware, Cost tracking, Open source, Setup time
  - Quick Start (3 commands)
  - Integration Guide (FastAPI + LangChain)
  - Dashboard Preview (3 screenshots)
  - Roadmap

**Day 88: Publish to PyPI** (from the RAGeval Studio)
- python -m build
- python -m twine upload --repository testpypi dist/*
- Verify the test install **without a venv**: `pip install --target /tmp/verify -i https://test.pypi.org/simple/ rageval` then `PYTHONPATH=/tmp/verify rageval --help` — or test in a fresh Studio / `docker run python:3.11-slim`.
- python -m twine upload dist/*
- Verify: `pip install --target /tmp/verify2 rageval` (or a fresh Studio)
- Add PyPI badge to README
- Tag v0.1.0

**Day 89: Make GitHub Public + Submit to Lists**
- gh repo edit <yourname>/rageval --visibility public
- Add LICENSE (MIT), CODE_OF_CONDUCT.md, CONTRIBUTING.md
- Tag and release on GitHub with release notes
- Submit to:
  - awesome-llmops listings
  - awesome-rag listings
  - "Show HN: RAGeval — drop-in LLMOps observability (60-second setup)" — SAVE DRAFT, do not post in 2026
- Engage in AI engineering Discords (lurk first; reply to existing observability threads; don't blast spam)

**Day 90: Blog Post 5 Draft**
- Title: "Observability for RAG: Why I Built RAGeval (and Why Phoenix and Langfuse Are Great Too)"
- Outline:
  1. The state of LLMOps observability in 2026: Phoenix (Arize), Langfuse, TruLens, Helicone — all great
  2. The gap I felt: too much setup for hobby/freelance/small-team use. SQLite, decorator, 60-second-to-running.
  3. The 5 metrics and why each: retrieval relevance, groundedness (multi-judge consensus), faithfulness, latency, cost
  4. Persona-aware groundedness: Same query, different persona → different "right answer". Standard groundedness misses this. Our prompt: judge groundedness conditional on persona.
  5. Honest comparison: When to use Phoenix instead (high-volume, enterprise). When to use Langfuse (rich integrations, hosted option). When RAGeval (self-hosted, simple, fast setup).
  6. Future: this becomes the basis of an arXiv preprint on Persona-Conditioned Groundedness (Phase 6 work)

**Week 14 Checkpoint:** RAGeval on PyPI, pip install rageval works. Dashboard runs locally. GitHub repo public. README is marketing-grade with honest competitor table.

## Week 15: Save Blog Post 5 + LLMOps Proposals + Preprint Pre-Work — Days 91-96

**Day 91: Polish + Save Blog Post 5 Draft (NOT PUBLISHED in 2026)**
- Send draft to 2 reviewers (1 LLMOps person, 1 outside-tech for clarity)
- Apply feedback
- Save final draft to: rageval/drafts/blog_post_5_rageval_observability.md
- Save Show HN draft with pre-written title: "RAGeval — self-hosted LLMOps observability (60-second setup)"
- Save Reddit drafts for r/MachineLearning + r/LocalLLaMA
- Save Discord drop-ins for LangChain #observability, Anthropic, DataTalksClub
- Save LinkedIn cornerstone-supporting draft
- DO NOT publish anywhere public (Section 5.1)
- NOTE: RAGeval gets pip-installed in 2026 — PyPI publish is fine (artifact, not content channel). What you defer is marketing-content distribution (HN, Reddit, Medium, LinkedIn).

**Day 92: LLMOps Proposals + Dashboard Deploy**
- Deploy dashboard to Vercel (free) or Netlify — **the platform builds it on its own builders** (connect the GitHub repo; no `npm run build` needed on the laptop). If you do build locally, `npm run build` on the laptop is light enough.
  - Configure dashboard to point at a sample RAGeval API instance
- OR: keep dashboard local-only with great screenshots in README
- Add RAGeval as Upwork portfolio entry #5
- Customize Section 26 Template 5 for LLMOps jobs
- Send 10 LLMOps proposals:
  - Filter: "LLMOps" "RAG evaluation" "AI observability" "RAG monitoring" "hallucination detection"
  - Lead with comparison table + 60-second setup demo

**Day 93: Continue Volume + Inbound Response**
- Continue IntelAI / DocIntel / AgentKit / VoiceFlow niches (5 proposals each = 20 total)
- Respond to PyPI download spike notifications, GitHub issues, blog post comments
- Engage genuinely — RAGeval is your community-credibility project
- If anyone asks about persona-aware groundedness specifically, flag that DM — these are potential preprint co-discussions

**Day 94: arXiv Preprint Pre-Work**
- Start LaTeX skeleton for preprint:
  - Title: "Persona-Conditioned Groundedness for RAG Systems"
  - Abstract (200 words, draft): "Standard groundedness metrics in RAG evaluation assume a single 'correct' answer per query. In multi-persona systems, the same query retrieves different relevant context per persona. We propose persona-conditioned groundedness, an LLM-judge prompt that scores answer support conditional on persona's expected information scope. We implement this in RAGeval (open-source) and report results on a 9-persona enterprise analytics platform with [N] queries and [accuracy delta] vs unconditioned groundedness."
- Sections (skeleton):
  1. Introduction (the gap)
  2. Related work (Phoenix, Langfuse, TruLens, recent RAG eval papers)
  3. Method (the prompt, the integration)
  4. Experiments (your IntelAI data with 9 personas)
  5. Discussion (limitations, future work)
  6. Conclusion
- Identify 10-15 papers to cite (recent RAG eval literature)
- Use Overleaf (free) for collaborative editing

**Day 95: Phase 5 Metrics + Phase 6 Prep**
- Phase 5 metrics:
  - RAGeval on PyPI: ___ downloads
  - GitHub stars: ___
  - Blog Post 5 traction: ___
  - LLMOps proposals sent: ___
  - Cumulative blog post views (Posts 1-5): ___
  - Phase 1-5 cumulative interviews/contracts: ___
- Open streampulse/ — re-read STATUS.md
- Write Phase 6 TODO.md
- This is the last build phase before preprint focus
- Prepare cold email list: 20-30 data/ops directors at growing SaaS companies (LinkedIn search + Apollo trial)

**Day 96: Buffer**
- Half day: fix anything broken from the week, respond to community DMs / GitHub issues
- Half day off — burnout management is critical at month 4

**Phase 5 Final Checkpoint:** RAGeval on PyPI (pip install rageval works). GitHub repo public, 20+ stars. Dashboard demoed (locally or live). Blog Post 5 drafted + Show HN draft saved. 10+ LLMOps-niche proposals sent. arXiv preprint skeleton started (LaTeX, abstract draft). Phase 1-5 cumulative: 3-7 contracts, $15-35k earned.

---

# PHASE 6: StreamPulse + Polish + Preprint (Weeks 16–18, Days 97–118)

**Goal:** Final project shipped. All 6 portfolio entries reviewed and polished. arXiv preprint drafted to submittable state. Cold email push across all 6 projects.

Shorter on build work (1.5 weeks for StreamPulse), heavier on consolidation (portfolio polish, preprint, cold email).

## Week 16: StreamPulse Build — Days 97-101

**Day 97: Verify Repo + Build api.py**
- Open the **StreamPulse Studio** and `cd streampulse` (deps already in base env — no venv)
- Re-read STATUS.md
- pip install -r requirements.txt
- Verify imports work
- Build api.py with endpoints:
  - GET /health
  - POST /ingest/json (list of records)
  - POST /ingest/csv (CSV file upload)
  - POST /ingest/email (Gmail integration payload)
  - POST /webhook/{source_name} (generic, with HMAC verify)
  - POST /webhook/{source}/with-vision (composes with DocIntel classify-image)
  - GET /pipeline/status
  - GET /pipeline/history (last 100 processed records)
  - WS /live (WebSocket — broadcasts classified records real-time)
  - GET /live/sse (Server-Sent Events alternative)
- Test each with curl

**Day 98: Build connectors/webhook_receiver.py**
- WebhookReceiver class:
  - verify_signature(payload, signature, secret) → bool: HMAC-SHA256 verification of X-Signature-256 header
  - parse_payload(raw_json, source_name) → list of DataRecord
  - route_to_pipeline(records) → None: Calls DomainClassifier (already in classifier.py), validates with DataValidator, stores via store_kpi_metrics, broadcasts to WebSocket connections
- Test with simulated webhook calls from N8N and custom sources

**Day 99: Build dashboard/LiveDashboard.jsx** — runs on the LAPTOP (Node); backend in the StreamPulse Studio (forward port 8004; WS `/live` tunnels over the same SSH forward)
- React app for live dashboard:
  - WebSocket connection to /live endpoint (SSE fallback to /live/sse), proxied to the forwarded localhost:8004
  - State: records (last 50), volumeData (last 20 time buckets), domainDist
  - Recharts LineChart: records per minute (live updating)
  - Recharts PieChart: domain distribution (live updating)
  - Table: live record feed (time, domain, metric, value, source, confidence, image_category if available)
  - Domain colors: Finance=#6366f1, Growth=#22c55e, Operations=#f59e0b, People=#ec4899, ESG=#14b8a6, IT_Ops=#8b5cf6
  - Header: connection status (green/red dot), error count
  - Dark theme (#0f172a)
- Test by streaming fake events via /ingest/json — verify dashboard updates

**Day 100: Tests + Deploy**
- Tests:
  - test_classifier.py: 5 tests (6 domains, edge cases)
  - test_webhook.py: 4 tests (signature verify, payload parse, routing)
  - test_api.py: 6 tests (each ingest endpoint, pipeline status)
  - test_websocket.py: 2 tests (connect, broadcast)
- Run pytest, fix failures
- Deploy StreamPulse to Railway or Fly.io (cold-start tier OK — secondary demo; the platform builds the image, or push the one you build in the Studio). SQLite default is fine; only set `POSTGRES_URL` (Neon) if you wire the Postgres path.
- OR: ship as "docker compose up" in the README as a self-host option for *end users* — that runs on their machine, not yours (saves $5/mo on hosting)
- Either way: record 60-second demo video

**Day 101: README + GitHub Public + Portfolio**
- Write README.md:
  - Title: "StreamPulse — Real-Time Business Data Pipeline"
  - Hero: GIF of dashboard updating live
  - What It Does (3 bullets: ingestion, classification, dashboard)
  - Supported Sources table (JSON, CSV, webhook, Gmail, Sheets)
  - Quick Start (3 commands)
  - Architecture ASCII
  - n8n integration walkthrough
- Make GitHub repo public, tag v0.1.0
- Add StreamPulse as Upwork portfolio entry #6
- Customize Section 26 Template 6 for data pipeline jobs

**Week 16 Checkpoint:** StreamPulse api.py + dashboard work end-to-end. WebSocket live updates verified. Repo public, README ready. Portfolio entry #6 added on Upwork.

## Week 16.5: Advanced 2026 Stack Features — n8n + Prefect + Hybrid Classifier — Days 101.5-103.5

**Day 101.5: First-Class n8n Integration (Mandatory for Equipment Sourcing Job)**
- Create integrations/n8n/ directory structure:
  - README.md: how to plug StreamPulse into n8n workflows
  - n8n_node.json: custom n8n node definition (community node format)
  - workflows/: 3 ready-to-import n8n workflow demos
- Implement custom n8n node template:
  - Node exposes StreamPulse classification and ingestion capabilities
  - Drag-and-drop integration in n8n UI
  - Configuration: webhook URL, API key, classification parameters
- Create workflow examples:
  - auction_aggregator.json: equipment auction listings classification
  - invoice_intake.json: automated invoice processing pipeline
  - crm_sync.json: real-time CRM data synchronization
- Test n8n workflows with sample data
- Document n8n integration in README with screenshots
- This directly addresses Equipment Sourcing job's "n8n or similar workflow tools" requirement

**Day 102: Prefect 3 Orchestration Layer (Research-Strong Option)**
- pip install prefect (already in requirements.txt from Week 0)
- Create orchestration/prefect_flow.py:
  - Define @task(retries=3, retry_delay_seconds=30) async def ingest_source(source: str)
  - Define @task async def classify_record(record: dict) -> dict
  - Define @task async def store_kpi(record: dict) -> None
  - Define @flow(name="streampulse-realtime-pipeline") async def pipeline_flow(sources: list[str])
- Implement Prefect deployment configuration:
  - Local development: prefect dev
  - Production: prefect deploy (if needed for clients)
- Create workflow example that processes multiple sources in parallel
- Test Prefect flow with sample data sources
- Document Prefect integration in README
- This demonstrates modern Python orchestration patterns (research credibility)

**Day 102.5: Domain Classifier Upgrade (Hybrid Approach)**
- Update classifier.py with three-tier classification:
  - Fast path: keyword matching (existing, <1ms latency)
  - Confidence threshold: if keyword match confidence < 0.7
  - Fallback path 1: embedding similarity vs domain prototypes (BGE-large)
  - Fallback path 2: Claude Haiku 4.5 zero-shot classification
  - Cache classification results by content hash (avoid re-classify)
- Implement embedding-based classification:
  - Load BGE-large-en-v1.5 model
  - Create domain prototype embeddings (one per domain)
  - Cosine similarity comparison for domain assignment
- Implement LLM-based classification fallback:
  - Use LiteLLM with Claude Haiku 4.5 for uncertain cases
  - Type-specific prompts for each domain
  - Return classification with confidence and reasoning
- Add classification cache with content hash keys
- Test hybrid classifier on edge cases (ambiguous content)
- Measure latency: fast path vs fallback paths
- Document hybrid approach in README with latency/accuracy tradeoffs

**Day 103: dlt Declarative Source Ingestion**
- pip install dlt (already in requirements.txt from Week 0)
- Create ingestion/dlt_sources.py with declarative sources:
  - @dlt.source def gmail_source(): Gmail integration with incremental loading
  - @dlt.source def gsheet_source(): Google Sheets integration
  - @dlt.source def webhook_source(): Webhook-based ingestion
  - @dlt.source def api_source(): Generic API polling source
- Implement dlt pipeline configuration:
  - Pipeline = dlt.pipeline("streampulse")
  - Incremental loading, schema evolution, idempotency handled by dlt
- Create example pipelines for each source type
- Test dlt sources with real data (Gmail, Sheets, APIs)
- Document dlt integration in README
- This demonstrates modern declarative data pipeline patterns

**Day 103.5: Advanced Storage + Vision Integration**
- Update store.py to support pgvector for embedding cache:
  - Add pgvector for storing classification embeddings
  - Enables fast similarity searches for classification history
  - Configure via POSTGRES_URL env var (already has pgvector)
- Add DuckDB for analytics queries:
  - Create analytics/duckdb_queries.py for fast analytical queries
  - Export classified data to DuckDB for dashboard analytics
  - Support time-series analysis and aggregations
- Enhance /webhook/{source}/with-vision endpoint:
  - Accepts payload with text + image_url
  - Classifies domain from text (StreamPulse classifier)
  - Classifies image category (DocIntel /classify-image integration)
  - Combines → enriched record with both classifications
- Test vision integration with sample images and text
- Test pgvector and DuckDB functionality
- Document advanced storage options in README
- This demonstrates DocIntel + StreamPulse cross-project synergy

## Week 17: Cold Email Push + Blog Post 6 + Portfolio Polish — Days 102-108

**Day 102: Cold Email List Prep**
- Build list of 30 cold email targets:
  - Roles: Head of Data, VP Engineering, Director of Operations, CTO
  - Companies: Series A/B SaaS (50-300 employees), public data infrastructure pain (Reddit posts, hiring data engineers, etc.)
- Tools: LinkedIn Sales Navigator trial OR Apollo free tier (50 leads)
- For each target, find: Name, role, company, LinkedIn URL, work email (or guess pattern), 1 specific reason their company might need a real-time pipeline (recent funding, new data team hire, public scaling pain, etc.)
- Store in Notion or spreadsheet

**Day 103: Cold Email Templates + First 15 Sends**
- Write 2 cold email templates:
  - Template A (data infra angle) for VP Eng / Director of Data:
    - Subject: "Real-time domain classification for your data pipeline?"
    - Body (under 120 words): Personalized opener (1 sentence about their company). The pain you solve (1 sentence). StreamPulse demo link + 1-line description. Soft CTA: "Worth a 15-min look?"
  - Template B (BI angle) for COO / VP Operations:
    - Lead with IntelAI demo, soft offer to discuss analytics/BI overall
- Send 15 cold emails (mix of A and B)
- Track open rates, replies, ghosts in spreadsheet

**Day 104: Blog Post 6 Draft**
- Title: "Real-Time Domain Classification: From Webhook to KPI in 200ms"
- Outline:
  1. The problem: real-time data lands raw; classification is manual
  2. Architecture: webhook → classifier → store → dashboard
  3. Domain classifier design: 6 domains, 160+ keywords, confidence scoring. Why keyword-based instead of full ML (latency, explainability). When to upgrade to embeddings (future work).
  4. Webhook security: HMAC, replay protection, idempotency
  5. Building a live dashboard: WebSocket patterns, throttling
  6. Production reality: backpressure, retries, dead-letter queue

**Day 105: Polish + Save Blog Post 6 Draft + 15 More Emails**
- Polish blog post, send to 2 reviewers, apply feedback
- Save final draft to: streampulse/drafts/blog_post_6_realtime_classification.md
- Save Reddit drafts (r/dataengineering, r/Python) to writing_workspace/reddit_drafts/
- Save LinkedIn cornerstone-supporting draft to writing_workspace/linkedin_drafts/
- DO NOT publish anywhere public (Section 5.1)
- Send 15 more cold emails (cumulative 30) — cold email IS allowed in 2026 (direct outreach, not public publishing)
- Continue Upwork volume on all niches

**Day 106: Portfolio-Wide Polish (All 6 Projects)**
- Full day (these assets compound for years):
- For each of 6 projects:
  - [ ] Demo URL works in incognito browser (no broken images, no 500s)
  - [ ] README is < 250 lines, accurate, demo link in first 3 lines
  - [ ] LICENSE file present (MIT)
  - [ ] CI is green on main branch
  - [ ] Loom demo video URL is live (Loom doesn't expire on free tier for active videos)
  - [ ] GitHub repo description matches what README says
  - [ ] PyPI page (omnismart-personas + rageval) has clear description
  - [ ] DockerHub page (docintel) has README synced
  - [ ] Upwork portfolio entry has 3+ screenshots and clear bullets

**Day 107: All-Niche Volume + Inbound**
- Send proposals across all 6 niches (60 minutes per niche, 8-10 total)
- Respond to: Cold email replies, GitHub issues/PRs (build community = future references), Upwork inbound DMs
- Schedule 2-3 discovery calls if you have inbound interest

**Day 108: Buffer**
- Half day: fix anything broken from the week, update Notion with cumulative metrics
- Half day off (Sunday) — week 17 was heavy

**Week 17 Checkpoint:** All 6 projects polished and verified. 30 cold emails sent. Blog Post 6 drafted. All 6 blog drafts saved to drafts/.

## Week 18: arXiv Preprint Draft + Plan Q4 — Days 109-118

**Day 109: Preprint Section 1-2 (Intro + Related Work)**
- Open Overleaf project from Day 94
- Write Section 1 (Introduction, ~800 words):
  - Standard groundedness problem
  - Why multi-persona RAG is increasingly common (enterprise, healthcare, legal — cite 2-3 papers)
  - Your contribution (persona-conditioned groundedness scoring)
  - Roadmap of the paper
- Write Section 2 (Related Work, ~1000 words):
  - Cluster A: RAG evaluation metrics (RAGAS, ARES, TruLens-Eval)
  - Cluster B: LLM-as-judge methodology (LMSYS chatbot arena, MT-Bench)
  - Cluster C: Multi-persona / multi-agent systems
  - Position your work explicitly relative to each cluster

**Day 110: Preprint Section 3 (Method)**
- Section 3 (Method, ~1200 words):
  - Formal definition: groundedness(q, a, c) vs. groundedness(q, a, c, p)
  - The persona-conditioned prompt: exact prompt text, why persona context is added at this layer
  - Implementation in RAGeval: decorator wraps any LLM call, stores per-persona groundedness scores, aggregates dashboards by persona
  - Calibration: how you set scoring scale (0-1), few-shot examples

**Day 111: Preprint Section 4 (Experiments)**
- Section 4 (Experiments, ~1500 words):
  - Dataset: IntelAI with 9 personas
  - Generate 200-500 query-answer-context tuples (one big eval run): Use synthetic dataset (25,920 KPI records, 144 months, 5 domains). For each persona, generate 20-50 representative queries. Run RAG pipeline, capture (query, answer, retrieved chunks).
  - Score every tuple with both: Standard groundedness (no persona context) + Persona-conditioned groundedness
  - Report: Average score per persona (table), Score distribution (histogram or violin plot per persona), Cases where two metrics diverge (qualitative analysis)
  - Limitations: sample size, single LLM judge, no human eval (yet)

**Day 112: Preprint Section 5-6 (Discussion + Conclusion)**
- Section 5 (Discussion, ~800 words):
  - What divergent cases reveal about RAG eval blind spots
  - Implications for production RAG systems (especially enterprise)
  - Honest limitations (LLM judge calibration, generalization to other personas)
  - Future work: human eval, fine-tuned judge, real-time monitoring
- Section 6 (Conclusion, ~300 words): Restate contribution, results in 2 sentences, invitation to engage
- Polish abstract (rewrite based on actual results)
- Build figure list:
  - Figure 1: System diagram (RAG → RAGeval → persona-conditioned score)
  - Figure 2: Score distribution per persona
  - Figure 3: Divergence cases (scatter: standard vs persona-cond)
- Use TikZ or matplotlib exports (Overleaf supports both)

**Day 113: Send Preprint Draft for Review + Cold Email Round 3**
- Compile preprint PDF (Overleaf → Download → PDF)
- Send to 3-5 reviewers:
  - 1-2 academic contacts if you have any (LinkedIn outreach fine)
  - 2-3 RAG-eval practitioners from blog post comments
  - Subject: "Draft preprint on persona-conditioned groundedness — feedback before arXiv submission?"
  - Be explicit: "I'm not asking for endorsement, just a sanity check. I'll cite acknowledgment if useful to you."
- Send 15 more cold emails (cumulative 45)
- Send 20 more Upwork proposals across all 6 niches

**Day 114: Phase 6 Metrics + 18-Week Retrospective**
- Phase 6 metrics:
  - StreamPulse deployed: ___
  - All 6 portfolio entries polished: ___
  - 45 cold emails sent: ___
  - Cold email reply rate: ___%
  - Blog Post 6 drafted: ___
  - Preprint sent for review: ___
- Cumulative 18-week metrics:
  - 6 deployed projects: ___
  - 6 blog posts drafted: ___
  - 2 PyPI packages with users: ___
  - DockerHub image: ___
  - Total Upwork proposals sent: ___ (target: 300-450)
  - Total interviews: ___ (target: 20-40)
  - Total contracts: ___ (target: 3-7)
  - Total earned: $___ (target: $15-40k by end of week 18)
  - GitHub stars across all repos: ___
  - Cumulative LinkedIn connections: ___
  - Preprint drafted: ___
- 18-week retrospective questions:
  - Which project drove the most freelance interest?
  - Which project drove the most community/research interest?
  - Which niches converted on Upwork?
  - Which channel (Upwork / cold email / community) was strongest?
  - Where did you waste time? Where did you underinvest?
  - What would you change if you started over?
- Write up in 500-1000 words → "What I built in 2026" LinkedIn launch post (Q1 2027)

**Day 115: Q4 2026 Planning + 2027 Launch Prep**
- Plan weeks 19-30 (Q4 2026, post-build):
  - [ ] Continue weekly Upwork proposal volume (with reviews accumulating)
  - [ ] Maintain GitHub repos (issues, PRs, small features, dependabot)
  - [ ] Apply finishing pass to each blog draft once per month (add client-story sentence, real screenshots, updated numbers)
  - [ ] Polish arXiv preprint to fully-submittable form (still NOT submitted in 2026)
  - [ ] Build personal portfolio site (Astro/Hugo) — locally, NOT deployed
  - [ ] Build LinkedIn content library (20-30 short drafts written)
  - [ ] Draft LinkedIn cornerstone post: "What I Built In 2026 (And What I Learned)"
  - [ ] Start drafting research-program statements of purpose (outline only)
  - [ ] Identify 3 workshop deadlines in Q1 2027 (NeurIPS retrospective workshops, ICLR workshops, AAAI 2027)
- Plan 2027 (high-level — see PART X of STRATEGY.md):
  - January 2027: Multi-channel launch week. Personal site goes live. LinkedIn cornerstone published. All 6 blog posts published over 6 weeks. Show HN submissions spread across Q1. Reddit posts spread across Q1.
  - Feb-Mar 2027: arXiv preprint submitted (cs.IR), workshop submission
  - Q2 2027: Faculty outreach (informational chats with research-program profs)
  - Q3 2027: Application drafting (SOPs, recommendation requests, CV polish)
  - Q4 2027: Submit applications (PhD/MS/fellowships), start preprint #2

**Day 116: Final Preprint Polish (NOT submitted in 2026)**
- Apply review feedback from Day 113
- Polish formatting, figures, bibliography
- Final read-through: clarity, claims, citations
- Save polished preprint as: writing_workspace/preprint_v_final_2026.pdf
- Note in Q1 2027 launch calendar: "Submit preprint to arXiv — pick Tuesday morning UTC so European researchers see announcement"
- DO NOT submit in 2026 (Section 5.1 — all public publishing deferred)
- A Q1 2027 arXiv announcement timed alongside LinkedIn launch and personal site reveal compounds. Solo December 2026 submission gets lost in holiday news cycle.
- Quiet milestone. Sit with it.

**Day 117: Buffer + Final Sweep**
- Final hygiene pass on everything:
  - All 6 demos still respond
  - All 6 GitHub READMEs current
  - Upwork profile current with all 6 portfolio entries
  - Notion / Airtable proposal log archived and analyzed
  - secrets.md and .env files NOT committed anywhere
  - All 6 blog drafts and preprint draft saved to writing_workspace/
  - Personal site code committed (private repo) — ready to deploy 2027
  - LinkedIn cornerstone draft + 20+ short drafts in writing_workspace/
- Plan a real break: 3-5 days actually offline before Q4 ramp

**Day 118: Done (end of Week 18)**
- Take the day completely off. You earned it.
- Tomorrow Q4 begins, at a sustainable pace.
- Q1 2027 the multi-channel launch begins — see PART X of STRATEGY.md.

**Phase 6 Final Checkpoint (END of 18-week plan):**
- 6 deployed projects with live demos (where always-on tier applies)
- 6 technical blog posts DRAFTED + fact-checked (publish Q1 2027)
- 2 PyPI packages (omnismart-personas, rageval) with users
- 5 GitHub public repos (AgentKit, DocIntel, VoiceFlow, RAGeval, StreamPulse)
- 1 DockerHub image (DocIntel)
- 1 arXiv preprint POLISHED and review-ready (submitted Q1 2027)
- Upwork portfolio at 6 entries
- Cumulative: $15-40k earned (depending on conversion)
- 3-7 ongoing or completed client relationships
- 30-60 client reviews + recommendations starting to accumulate
- 150-300 LinkedIn connections (passively accumulated)
- Personal portfolio site coded (private), ready to deploy Q1 2027
- 20-30 short LinkedIn drafts written, ready to drip-feed in 2027
- 6 Show HN drafts, 6 Reddit drafts, LinkedIn cornerstone draft
- Material for 2027 multi-channel launch fully prepared
- Research-credential foundation set (deployed systems + preprint + community presence + client references)

---

# TASK CHECKLIST SUMMARY

**For each phase:**
- [ ] All day tasks completed and verified
- [ ] Tests passing (pytest)
- [ ] CI green on develop branch
- [ ] Demo functional (manual smoke test — frontend on laptop → backend in Studio)
- [ ] README accurate (<250 lines)
- [ ] Dockerfile valid (image builds on Railway/GitHub Actions, not locally)
- [ ] .env.example complete (every required var)
- [ ] Upwork portfolio entry added
- [ ] Proposals sent (per phase target)
- [ ] Blog post drafted (saved to drafts/)
- [ ] GitHub repo public OR private (per phase)
- [ ] Metrics logged in Notion/Airtable

**End of Week 18 Deliverables:**
- 6 deployed projects with live demos
- 6 blog posts drafted (not published in 2026)
- 2 PyPI packages (omnismart-personas, rageval) with users
- 1 DockerHub image (DocIntel)
- 5 public GitHub repos
- 1 arXiv preprint polished (not submitted in 2026)
- Cumulative 300-450 proposals sent
- Cumulative 20-40 interviews
- Cumulative 3-7 contracts
- Cumulative $15-40k earned
- Personal portfolio site coded (private)
- 20-30 LinkedIn drafts written
- All 6 Show HN + Reddit + LinkedIn drafts saved
