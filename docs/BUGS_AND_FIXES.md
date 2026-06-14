# IntelAI — Bugs, Fixes, Side Effects & Challenges

A detailed engineering log of every defect found and fixed while bringing IntelAI from the
post-split scaffold to a verified Phase-1 product, plus the side effects each fix produced
and the environment challenges encountered along the way.

**How to read this:** each entry has **Symptom → Root cause → Fix → Files → Side effects →
Challenge/notes**. Severity: 🔴 ship-blocker · 🟠 user-visible · 🟡 quality/robustness.

Verified state at the time of writing: pytest **50 passed**, package tests **8/8**, RAG
groundedness eval **25/25**, every domain endpoint returns real data, cited chat works,
`vite build` clean. 3-way synced (laptop = GitHub = Studio).

---

## 1. RAG, retrieval, context & embeddings

This is the cluster that most affected answer quality. Treat it as the "how grounding can
silently break" case study.

### 1.1 🟡 Retrieval returned near-random results with a flat relevance of 1.0
- **Symptom:** natural-language questions ("what is our latest revenue?") retrieved
  near-random documents, and every result carried the same relevance score (1.0). The
  groundedness eval sat at ~22/25.
- **Root cause:** two problems compounding. (a) BM25 ranked on the *boilerplate* words in a
  question — "what", "is", "our", "how" — which appear in nearly every document, so over a
  uniform corpus (the glossary) the ranking was essentially noise. (b) The fusion step
  returned a constant score, so nothing downstream could tell a strong hit from a weak one.
- **Fix:** in [hybrid_retrieval.py](../src/services/hybrid_retrieval.py) — added a stopword
  set + `_tokenize(drop_stop=True)` so only content terms drive BM25; switched to
  **normalized Reciprocal Rank Fusion** (top result = 1.0, the rest scale down); and
  weighted the title 2× by indexing each doc as `"title. title. content"` so a query for a
  metric name (e.g. "NRR") surfaces that metric's doc instead of any doc that merely mentions
  the word.
- **Side effects:** scores are now meaningful 0–1 values that flow straight into the citation
  `relevance` field shown in the UI. Eval rose to 25/25.
- **Challenge:** the failure was subtle — retrieval "worked" (returned docs) but returned the
  *wrong* docs, which only a recall/groundedness eval exposes. This is why the eval gate
  exists.

### 1.2 🔴 Installed-but-broken reranker → 0 sources → copilot answered "I don't have that data"
- **Symptom:** after a fresh container + re-seed, the eval showed `recall=1.0` (retrieval
  found the docs) yet `ground=0.0` for **every** query, and a direct copilot call returned
  **0 sources** with *"I don't have any specific information… in my current knowledge base."*
- **Root cause (a chain):**
  1. The fresh container had the heavy ML extras installed, so `USE_HYBRID_RETRIEVAL`
     activated the full **BGE embedder + BGE reranker**.
  2. The installed reranker was broken by a library version skew —
     `XLMRobertaTokenizer has no attribute prepare_for_model` — so the rerank step threw.
  3. `retrieve()` let that exception escape, so `hybrid_doc_retrieve` caught it and returned
     `[]`.
  4. The caller then fell back to the *dense vector* path — but the seeded knowledge docs
     store an **empty embedding** (`embedding=""`), so that path had nothing to search and
     returned 0 results → no context → the model correctly said it had no data.
  The module *claimed* graceful degradation but only handled a **missing** reranker, not an
  **installed-but-broken** one.
- **Fix:** in [hybrid_retrieval.py](../src/services/hybrid_retrieval.py) — wrapped the
  reranker call in `try/except` inside `retrieve()`. On failure it sets a one-shot
  `_reranker_failed` flag and **falls back to dense + BM25 + RRF fusion** (still strong)
  instead of failing the whole retrieval.
- **Side effects:** grounding restored (eval back to 25/25) and now on full fusion rather
  than the old BM25-only path — a net retrieval-quality *improvement*. The reranker remains
  effectively off in this environment until its deps are pinned.
- **Challenge:** distinguishing "retrieval found the docs" (recall) from "the model received
  the docs as context" (groundedness). They diverged here, which is exactly the signal that
  pointed at the source-assembly step rather than the corpus.
- **Open follow-up:** pin compatible `transformers`/`FlagEmbedding` versions in the ML extra
  to re-enable reranking, then re-run the eval to confirm no regression.

### 1.3 🟡 Eval groundedness read the wrong field after a rename
- **Symptom:** after standardizing the citation field name `preview → snippet`, the eval
  scored groundedness as 0 because it still read `preview`.
- **Fix:** [rag_eval.py](../src/data/rag_eval.py) now reads `snippet` (with a `preview`
  fallback).
- **Side effect:** the eval is now resilient to either field name.
- **Challenge:** a pure rename rippled into a test gate — a reminder to grep the eval/tests
  whenever a public field name changes.

### 1.4 🔴 Knowledge-base search is non-functional (`search_vectors` does not exist)
- **Symptom:** the "Search the knowledge base" feature on [KnowledgePage.jsx](../frontend/src/pages/KnowledgePage.jsx)
  and [DataHubPage.jsx](../frontend/src/pages/DataHubPage.jsx) always returns nothing.
- **Root cause:** the endpoint `/api/v1/knowledge/search` in [server.py](../src/api/server.py)
  (still labeled `# VECTOR SEARCH (ChromaDB)`) does `from src.services.pg_store import
  search_vectors` — **but `search_vectors` was never defined in `pg_store`** (it was an
  OmniIntelOS/Chroma function lost in the scope-down). The import raises, the broad
  `try/except` swallows it, and the endpoint returns `{"results": [], "error": ...}`.
- **Status:** ✅ **Fixed** in the RAG-core PR. `/api/v1/knowledge/search` now calls the shared
  retriever (`_get_shared_rag()._retrieve_documents`), which covers the persistent vector
  store (chroma/pgvector/qdrant) and the in-process hybrid path; the missing `search_vectors`
  import and the stale "ChromaDB" label are gone. Verified live (KnowledgePage + DataHub).
- **Challenge:** it's invisible in normal testing because the error is swallowed and the UI
  just shows "no results" — only an import-vs-definition diff (or clicking the feature)
  reveals it.

### 1.5 ℹ️ Context assembly (how grounding actually works now — for reference)
Not a bug, but documenting the contract the above fixes protect: the copilot answer is built
from **(a)** a role-scoped **live KPI snapshot** (deterministic, from the catalog, RBAC-
filtered) **plus (b)** retrieved knowledge docs (per-metric facts + glossary definitions),
assembled with the stable persona prompt first and the volatile data/question last (for
Groq prompt-cache reuse). Sources are normalized through `normalize_sources()` into
`{id,title,type,relevance,snippet,source}` and cited inline as `[n]`. If retrieval returns
nothing (as in §1.2), the snapshot still grounds basic numbers but doc-specific questions
degrade — which is why §1.2 mattered.

---

## 2. Data layer & seeding

### 2.1 🔴 Neon dropped the connection while seeding 3,024 rows
- **Symptom:** `python -m src.data.seed` failed with `psycopg.OperationalError: consuming
  input failed: server closed the connection unexpectedly`, mid-insert. The old 1,032-row
  seed had worked.
- **Root cause:** `store_kpi_metrics` wrote rows **one `INSERT` at a time** inside a single
  long transaction — ~3,024 sequential round-trips to a serverless (Neon free-tier) Postgres
  that scales to zero and drops a long-running cold-start transaction.
- **Fix:** [pg_store.py](../src/services/pg_store.py) — rewrote `store_kpi_metrics` to build
  all rows once and write them with a single batched `executemany`, wrapped in a **3-attempt
  cold-start retry** (fresh connection each try).
- **Side effects:** one round-trip instead of thousands — also speeds up CSV ingestion, which
  shares this function. The retry makes seeding robust to Neon waking up.
- **Challenge:** the first symptom looked like an OOM (an earlier monitor exited 137); only
  capturing the full traceback revealed it was a *connection* failure, not memory.

### 2.2 🟡 Net Revenue Retention was clamped to 100%
- **Symptom:** NRR seeded at ~112% but the dashboard would have capped it at 100%.
- **Root cause:** the seed clamps all `%` metrics to 0–100, but NRR is legitimately >100%.
- **Fix:** a `PCT_OVER_100` exemption set in [seed.py](../src/data/seed.py).
- **Side effect:** the clamp logic is now metric-aware; other ratio-style percentages can opt
  out the same way.

### 2.3 🟠 The three-way metric fragmentation (dashboards full of zeros)
- **Symptom:** IT/HR/Ops/Logistics pages showed many `0`s; the copilot's data snapshot was
  thin.
- **Root cause:** three sources disagreed about "the metrics" — the seeded `KPI_SPEC` (~43),
  the domain endpoints (which *expected* far more via keyword extraction), and a 64-term
  glossary that defined metrics with no data behind them. The domain services are keyword
  extractors over the seeded table, so any metric the seed didn't produce resolved to 0.
- **Fix:** unified on one catalog in [seed.py](../src/data/seed.py) — `STRATEGIC_KPIS` (89,
  all glossary-backed + benchmarked) + `OPERATIONAL_DETAIL` (37) = 126 metrics across 7
  domains, feeding pages, copilot and analytics from the same `kpi_metrics` table; glossary
  grown 64 → 101 terms.
- **Side effects:** the knowledge-doc corpus grew (≈110 → 236 docs) and entity count grew
  (≈4,920 → 14,664), which is what *exposed* §1.2 (the reranker path) on the next full run.
- **Challenge:** deciding the boundary between "strategic, glossary-backed" metrics and
  "operational detail" so the catalog stays a credible exec set without bloating the glossary.

### 2.4 🟠 Extractor keyword/hyphen mismatches (zeros even for metrics that existed)
- **Symptom:** even seeded metrics resolved to 0 on the dashboards.
- **Root cause:** substring keyword matching missed real names — `"on-time delivery"` ≠
  `"on time delivery"` (hyphen), `"Mean Time to Resolution"` vs keyword `"mttr"`,
  `"Safety Incident Rate"` vs `"safety incidents"` (plural), `"Production Efficiency"` vs
  `"oee"`, `"Phishing Attempts Blocked"` vs `"phishing blocked"`, `"Damaged Rate"` vs
  `"damage rate"`, OpEx vs `"operating cost"`, and the ESG `water/waste/diversity` synonyms.
- **Fix:** made every extractor **hyphen-insensitive** (normalize `-`→space before matching)
  and corrected the specific keyword lists across [it_ops.py](../src/services/it_ops.py),
  [hr.py](../src/services/hr.py), [operations.py](../src/services/operations.py),
  [logistics.py](../src/services/logistics.py), [financial.py](../src/services/financial.py),
  and the ESG block in [server.py](../src/api/server.py).
- **Side effect:** retrieval of dashboard fields is now tolerant of naming style; verified
  live that every *displayed* field is non-zero.
- **Note:** a couple of counts (`lost_time_incidents`, the `safety_incidents` summary field)
  legitimately floor to 0 from a sub-1 rate — these are correct/positive values, not
  unresolved fields, and the summary one isn't rendered.

---

## 3. Frontend ↔ backend contract

### 3.1 🟠 FinancialPage rendered a single bogus stat
- **Symptom:** the Financial page showed one nonsensical card instead of the Finance KPIs.
- **Root cause:** the page grouped `/kpis` rows by `k.metric_name || k.name`, but the API
  returns the field as **`metric`** — so every row collapsed under one `undefined` key.
- **Fix:** [FinancialPage.jsx](../frontend/src/pages/FinancialPage.jsx) keys on `k.metric`
  and formats each value by its declared `unit` (%, USD, days, months, ratio, score) so the
  new Finance metrics (Rule of 40, DSO, runway) render correctly.
- **Side effect:** the page now scales to any number of Finance metrics with correct units.
- **Challenge:** the bug predated this work and was masked because the page still "rendered" —
  it just rendered one wrong card; cross-checking the actual `/kpis` row shape revealed it.

### 3.2 🟡 Dead client methods pointing at removed endpoints
- **Symptom:** leftover API client functions referenced endpoints deleted in the scope-down.
- **Fix:** removed `getMonitoringStats`, `explainTerm`, `knowledgeSearch` (dup) from
  [api.js](../frontend/src/api.js); kept the live REST surface.
- **Related:** `searchKnowledge` is still wired (KnowledgePage/DataHubPage) but the *backend*
  it calls is broken — see §1.4.

---

## 4. i18n / UX

### 4.1 🟠 Missing translation keys rendered as raw slugs
- **Symptom:** UI text like `dataSubtitle` or `uploadKpiCsv` appeared literally on screen.
- **Root cause:** `t()` returns the **key itself** when a translation is missing, so any
  referenced-but-undefined key shows up verbatim.
- **Fix:** added the ~21 missing EN/FR keys to
  [translations.js](../frontend/src/i18n/translations.js) and ran a missing-key detector to
  confirm none remained.
- **Challenge:** there's no compile-time check for missing keys; a detector script is the only
  guard, so it must be re-run whenever new `t('...')` calls are added.

---

## 5. Scope-down fallout

### 5.1 🟡 `PyPDF2` import vs shipped `pypdf`
- **Symptom:** document ingestion could fail on import.
- **Fix:** [server.py](../src/api/server.py) imports `from pypdf import PdfReader`
  (`pypdf` is the maintained successor and the one in `requirements.txt`).

### 5.2 🟡 A test asserted a removed endpoint
- **Symptom:** `test_prometheus_metrics` exercised `/metrics`, deleted during scope-down.
- **Fix:** removed the obsolete test — this is why the suite count is **50**, not the older 51.

### 5.3 ℹ️ Residual references to removed tech (cosmetic, low risk)
- `# VECTOR SEARCH (ChromaDB)` comment in [server.py](../src/api/server.py) (the endpoint is
  broken — §1.4) and `chromadb` in the noisy-logger suppression list in
  [logger.py](../src/core/logger.py). Harmless but misleading; cleanup recommended.

---

## 6. Environment & process challenges (not code defects, but they cost real time)

- **Lightning Studio sleeps (free tier).** When idle it powers down, producing SSH
  `Permission denied (publickey)` and tunnel exit 255. Recovery: wake from the dashboard,
  wait ~10s, `docker compose up -d`, run one clean tunnel. (`pkill -f "ssh -N lightning"`
  self-kills the running command — avoid.)
- **`rsync` is not installed on the Studio.** Switched to a `tar`-over-SSH pipe + `docker cp`
  to ship code into the container for testing.
- **The container only mounts `./src`,** not the repo root — test/diagnostic scripts must be
  `docker cp`'d into `/app`, not just dropped in the repo.
- **BGE embedder cold-load (~2 min).** The first chat/eval in a process loads the embedder,
  which blew a 60s smoke-test client timeout. Fix: longer timeout + a warm-up call; the
  embedder loads once per process and is reused.
- **Neon cold start** (see §2.1) — the first connection after idle can drop; the retry added
  there absorbs it.

---

## 7. Cross-cutting side effects to keep in mind

- **Bigger corpus exposed latent retrieval bugs.** Growing the catalog (§2.3) is what surfaced
  the reranker chain (§1.2) — more docs meant the rerank path actually ran at scale.
- **Field renames ripple into the eval/tests** (§1.3). Public field names (`snippet`, `metric`)
  are contracts; grep the eval + frontend before renaming.
- **Swallowed exceptions hide broken features** (§1.4). The `try/except` that keeps the chat
  path alive also hid a completely dead endpoint. Broad excepts should at least log loudly.

---

## 8. Lessons / guardrails

1. **Keep the eval gate honest and run it on the real corpus** — recall vs groundedness
   divergence is the fastest way to catch context-assembly breakage.
2. **Graceful degradation must cover "installed but broken," not just "missing."**
3. **One source of truth for data** removes a whole class of "disagreeing layers" bugs.
4. **Treat field names as contracts**; a rename is an API change.
5. **Audit imports vs definitions** after a big deletion — §1.4 was a missing function an
   `import` happily referenced until called.
