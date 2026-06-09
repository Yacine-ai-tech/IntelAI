# IntelAI — Phase 1 Status

Phase 1 = "recreate IntelAI as the scoped cloud product" (per EXECUTION_PLAN.md §Phase 1).
Updated 2026-06-09.

## ✅ Code deliverables — DONE
- [x] **Scope-down** to IntelAI: removed monitoring/nginx/n8n/tunnels/OCR/voice + all
      out-of-scope routes (integrations, camera, n8n, bulk dataset ingestion) +
      modules/config. Backend `server_v2.py` 2479→1338 lines, **68 routes**.
- [x] **Recharts** on Analytics / Forecasting (CI bands) / Risk (radar) / Dashboard
      (sparklines) / Financial (bar).
- [x] **WebSocket streaming chat** wired (`/api/v1/ws/chat`), 9 personas.
- [x] **30+ tests** → `tests/test_api.py` in-process TestClient (41 tests) + smoke + e2e
      (guarded); CI green without a DB (graceful skips). `requirements-dev.txt` + CI updated.
- [x] **GraphRAG-lite** integrated behind `USE_GRAPH_RAG` (entity-graph ranking of KPI
      records for multi-hop queries; safe fallback).
- [x] **Hybrid retrieval** (BGE + BM25 + RRF + reranker) + **LiteLLM** multi-provider router.
- [x] **Robust deterministic seed** `src/data/seed.py` (replaces the old dataset): 7 domains,
      24 months, anomalies + knowledge docs. `make seed`. Verified: 1032 rows + 9 docs.
- [x] **Prompt-eval** (§1.4): `src/data/rag_eval.jsonl` (25 cases) + `make eval`
      (`src/data/rag_eval.py`) with a >20%-below-groundedness gate + structural test.
- [x] **README** rewritten (<200 lines); **`omnismart-personas`** extracted to
      `packages/` (PyPI-ready, 8 tests passing).
- [x] **Production**: single-app `Dockerfile` (non-root, healthcheck) + `.dockerignore` +
      `railway.toml`; startup creates tables idempotently; trimmed `.env.example`.
- [x] **Brand-new UI** (Indigo Nebula) + simplified Data page.

## ✅ Writing prepared (drafts/ — publish 2027, per §5.1)
- [x] Blog post 1 "Persona-Routed RAG" · preprint skeleton · 3-min demo script · 3 proposal templates.

## ⏳ Remaining — your actions (not code)
- [ ] Deploy to Railway/Fly (connect repo; set env vars; `railway.toml` ready) → record public URL.
- [ ] Deploy frontend (Vercel/Netlify) pointed at the backend URL.
- [ ] Record the 3-min Loom (script in `drafts/demo_script.md`); add link to README.
- [ ] Publish `omnismart-personas` to TestPyPI → PyPI; tag the repo release.
- [ ] Upwork profile + first proposals (templates in `drafts/`).
- [ ] Run `make eval` against the deployed stack and record the groundedness table for the blog.
