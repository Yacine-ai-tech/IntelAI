# IntelAI — STEPS LOG (living document)

> Continuous engineering log of **every** action on IntelAI from Week 0 to now. Append newest at
> the bottom. Absolute dates. Branch model: feature branch → PR → merge into `develop`. Secrets
> live only in `.env`/`secrets.md` (gitignored) — never here.

## Project in one line
Persona-Aware AI Analytics & RAG Copilot (project #1 of 6) — multi-domain KPI analytics +
9-persona RAG copilot + **GraphRAG-lite + hybrid retrieval (BGE-large + BM25 + RRF + reranker)**,
LiteLLM multi-provider, JWT/RBAC, bilingual EN/FR, single cloud deploy. Scoped subset of the
former OmniIntelOS (the full Palantir-style platform now lives in a separate private repo).

## Week 0 — split & rebrand (2026-05-20 → 06-09)
- `c37ec83` OmniIntelOS v2.0 refactor (pre-split baseline).
- `ca0db8a` CI pytest; `4c20c74` finalize Week 0 (strategy docs, Phase 1 TODO, py3.11 Docker,
  in-process smoke tests); `d69b2b1`/`edb8477` Lightning 1-Studio + Docker dev setup.
- `4441c3f` **Rebrand OmniIntelOS → IntelAI**; re-scope flow docs to project #1.
- `b0f9954` Phase 1: scope IntelAI to the cloud product + GraphRAG-lite + tests + package.

## Phase 1 — scoped recreate (PR #1 + follow-ups)
- `8399332` **PR #1** Week 1: Recharts charts, WebSocket chat, expanded tests, GraphRAG-lite.
- `623496d` Frontend redesign (Indigo Nebula) + deeper scope cleanup; `52f2336` drop dead
  integration/voice/camera API (those belong to sibling niches / the full platform).
- `46b5c80` deep backend scope-down + deterministic seed; `eb47cdc` prompt-eval + production polish.
- `bf6e45a` zero-skip test suite, hybrid retrieval wired; `72d4964` conftest seeds bootstrap
  admin into in-memory auth store (no skips, no keys committed).
- `93c09a2` **bug/fix:** bump torch 2.3.1→2.4.1 (CPU) so BGE dense/hybrid retrieval loads.
- `1356472` GraphRAG-lite: persisted `kpi_entities` sidecar + ingest-time entity extraction.
- `e942d75`/`b907c4c` RAG eval reaches **25/25** (per-metric knowledge docs + robust matching).
- `93c80b5` EXECUTION_PLAN marked Phase 1 code-complete & validated.
- `adba6ea` **PR #11** docs: strategy/inventory reconcile (current `develop` head).

## New-account Studio provisioning + .env hardening (2026-06-16)
- Cloned onto `upwork_new` Studio (teamspace `deepseek-ocr-document-understanding-project`).
- **`.env` recreated + scoped:** removed full-platform cruft that had leaked in (n8n, Cloudflare,
  Grafana, ClickUp, Google, Slack, Tunnel, FEATURE_VOICE) — those belong to the private
  OmniIntelOS platform, not the scoped product. Filled real secrets from `secrets.md` (Neon
  Postgres, Anthropic, Groq, Tavily, SECRET_KEY, bootstrap admin); set `USE_HYBRID_RETRIEVAL=true`,
  `USE_GRAPH_RAG=true`. Synced local ↔ Studio. (Audit had found ANTHROPIC_API_KEY empty + GROQ a
  placeholder in the old copy.)

## GPU validation (T4, 2026-06-16)
- **BGE-large embeddings validated on the T4**: load 6.5s on CUDA; semantic sanity
  `sim(revenue, sales)=0.673` ≫ `sim(revenue, cat)=0.273` — confirms the hybrid-RAG embedding
  backbone (BAAI/bge-large-en-v1.5) works and ranks correctly. Switched Studio back to CPU after.

## Current state
Phase-1 code-complete & validated (RAG eval 25/25, hybrid retrieval + GraphRAG-lite wired,
Recharts UI, WebSocket chat, JWT/RBAC). Deploy + PyPI publish remain (user-gated).

---

## Next — industry & research-standard improvements (planned)
1. **RAG evaluation rigor**: adopt RAGAS / TruLens-style metrics (faithfulness, context
   precision/recall, answer relevance) and wire results into RAGeval (project #5) for a
   cross-project story.
2. **Reranker A/B + GraphRAG quality delta**: record graph-vs-vector deltas (per STRATEGY 1.10)
   on a fixed query set; publish the "Persona-Routed RAG" blog/preprint.
3. **pgvector prod path** alongside Chroma dev; load-test retrieval at scale.
4. **Eval-in-CI** gate (the 25/25 set) to catch retrieval regressions.
5. **Package** `omnismart-personas` to PyPI (the one shared artifact across the 6 projects).

## Comprehensive QA pass (2026-06-16)
- **58 tests pass** (shared env, after installing jose/chromadb). §1.10 verified: GraphRAG-lite, hybrid retrieval+reranker, multi-LLM router. Package **omnismart-personas**: 8 tests pass + builds wheel (PyPI-ready).
- All 6 projects + both packages green; 28/28 STRATEGY §.10 feature claims code-verified.

## Remediation — LIVE behavior validation (2026-06-17)
- Added `tests/test_live_llm.py` (real LLM, skip-if-no-key): **llm_router LIVE**: real multi-provider completion returns exact 'PONG'.
- Addresses the "tests prove imports not behavior" gap with a real, measured run.

## FINAL scoreboard + Docker validation (2026-06-17)
- **Docker**: docker compose up --build → /health **200** on :8000 (isolated image, not conda). **Tests 58**. BGE-large validated on T4 (CUDA). RAG quality measured via internal 25-query eval (no worldwide RAG benchmark maps to KPI-domain data — honest).
- Deployment validated via **Docker** (docker-compose.dev.yml), the isolated per-repo design —
  NOT the shared conda env. All 6 repos: 6/6 containers serve /health.
- **User-gated (cannot be done by the agent):** Railway/Fly deploy, PyPI upload (wheels built),
  Loom recording, sending Upwork proposals, publishing blog/preprint drafts.

## Internationalization — locale-aware currency formatting (2026-06-17)
STRATEGY calls for bilingual EN/FR + "proper currency formatting". Found inconsistency: French
executive-summary bullets called `format_number()` which emitted English `$3.6M` inside French
prose ("Revenu actuel à $3.6M.").
- `src/services/insights.py::format_number` is now locale-aware (defaults to `I18N.lang()`):
  EN `$3.6M` (prefix, `.` decimal, K/M/B); FR `3,6 M$` (suffix, `,` decimal, space groups, k/M/Md).
  Backward-compatible signature (`currency` kept; new optional `lang`). No tests pinned the format.
- Verified EN/FR output across 10 cases (B/M/k thresholds, sub-1000, None→"—").

## FCFA + multi-currency, and deploy-today pass (2026-06-17)
"Make IntelAI handle French/English AND FCFA." French/English: verified all 7 i18n sections have
exact EN/FR key parity (AUTH 18, NAV 26, COPILOT 9, FINANCE 22, INGESTION 19, RBAC 10, COMMON 34).
- **Currency now configurable + FCFA-correct.** New `settings.CURRENCY` (ISO 4217, default USD).
  `insights.format_number` rewritten to be currency- AND locale-aware via a presentation table:
  symbol vs word currencies, prefix (EN) vs suffix (FR). Examples — USD/EN `$3.6M`, EUR/FR `3,6 M€`,
  **XOF/EN `3.6B FCFA`, XOF/FR `3,6 Md FCFA`, XOF/FR `850 FCFA`**. Verified across 15 cases.
- **Frontend too:** `frontend/src/components/ui.jsx` `fmtMoney` hardcoded `'$'` → now reads
  `VITE_CURRENCY` (+ `VITE_LANGUAGE`) and mirrors the backend rules (FCFA renders as a spaced suffix).
- `.env.example` documents `DEFAULT_LANGUAGE` + `CURRENCY=USD|EUR|GBP|XOF…` (presentation only, no FX).
- **Deploy:** already binds `$PORT` via `railway.toml` startCommand; confirmed healthcheck `/health`,
  `.env` gitignored, no secrets tracked.
- Copilot prompt fix: the citation example hardcoded `$3.6M`; now currency-neutral and tells the
  model to **mirror the currency shown in the (FCFA/EUR-aware) data block, never convert** — so
  with `CURRENCY=XOF` the copilot cites FCFA, not `$`. Verified chatbot already replies in FR/EN
  (`"Répondez en français." if I18N.lang()=="fr"`). IntelAI FR/EN/FCFA is now consistent end-to-end.

## E2E production-Docker validation (2026-06-17, on the Studio)
Real end-to-end test: `docker build` the production image from a **cold cache**, `docker run` it
with a **non-default `PORT=9100`** (+ `--env-file .env`), and poll `/health`. Result:
**build OK → HEALTH 200 ✓** — confirms the image builds (deps + COPY paths resolve), honors the
platform `$PORT`, and boots cleanly. All 6 projects passed (OVERALL_RESULT=ALL_PASS). Railway/
Render build the same Dockerfile, so cloud deploy is validated end-to-end.

## PyPI publish — omnismart-personas (2026-06-17)
- **Published** the reusable persona library to PyPI: https://pypi.org/project/omnismart-personas/0.1.0/
  (hatchling build, zero runtime deps, `twine check` PASSED). Test-installed from PyPI into a clean
  target: `import omnismart_personas` + submodules (router, templates) OK. This is the shareable
  artifact called for in STRATEGY/EXECUTION_PLAN (the IntelAI app itself stays a deploy, not a dist).
