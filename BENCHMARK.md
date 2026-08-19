# Benchmark Results

This document reports what was actually measured against IntelAI's live deployment and
its real OmniIntelOS demo dataset — not aspirational numbers. For the reasoning behind
*why* each component is designed the way it is, see [`RESEARCH.md`](RESEARCH.md); this
document is the "what we measured."

Every number below comes from a script in `scripts/` or a one-off analysis run against
the live database and the live production API, described inline so the methodology is
reproducible rather than asserted. Where a result exposes a real limitation, it's reported
as such — a benchmark that only shows wins isn't a benchmark.

**A methodology note on §3:** the live production RAG evaluation's judge panel, and the
reasoning-tier persona chat calls it scores (`ceo`/`cfo`/`cto`/`risk`), were temporarily
routed through a third-party OpenAI-compatible multi-model gateway for the duration of
that evaluation run only — direct Anthropic credentials were unavailable at benchmark
time. The gateway is a real, third-party multi-model API, reached via LiteLLM's
standard `openai/` prefix + `OPENAI_BASE_URL` override — zero code changes, pure
config, and reverted immediately after this run completed. Nothing about this routing
lives in any tracked config in this repo or any other project repo; it's disclosed here
because it's part of how these specific numbers were produced, not because it's part of
the system's design.

## 1. Forecasting: out-of-sample backtest

**Methodology.** `ForecastEngine.time_series_forecast()` (`src/services/forecasting.py`)
fits ordinary least-squares linear regression on the series-to-date and projects forward.
To test it honestly, every possible 3-month-ahead forecast origin in OmniIntelOS's 78-month
series was backtested: fit on history up to the origin month only, forecast 3 months
ahead, then compare the forecast to the actual (already-known) value at the target month.
The model never sees the value it's scored against. Results are also split by whether the
3-month forecast window crosses one of OmniIntelOS's 12 defined regime/phase transitions
(e.g. the generative-AI demand surge), since a linear model's behavior during a regime
change is exactly the kind of thing worth measuring rather than blending away.

**Result: 378 forecasts scored across 6 metrics.**

| Metric | Mean APE | Median APE | N |
|---|---|---|---|
| System Uptime | 0.33% | 0.22% | 63 |
| Gross Margin | 7.12% | 5.62% | 63 |
| Customers | 12.76% | 11.76% | 63 |
| Headcount | 15.77% | 16.72% | 63 |
| Revenue | 19.43% | 15.81% | 63 |
| ARR | 19.46% | 19.91% | 63 |

**Overall: mean APE 12.48%, median APE 9.90%.**

| Forecast window | Mean APE | Median APE | N |
|---|---|---|---|
| Stays within one regime | 11.88% | 9.23% | 216 |
| Crosses a regime transition | 13.28% | 10.97% | 162 |

**The worst individual errors are not random noise.** The 5 largest single-forecast
errors in the entire backtest are all Revenue forecasts with origin months in Nov
2025–Mar 2026 — the window where OmniIntelOS's own growth genuinely accelerates
(generative-AI demand surge / scaled-operations phases):

| Metric | Origin | Target | Predicted | Actual | APE | Crosses regime |
|---|---|---|---|---|---|---|
| Revenue | 2026-03 | 2026-06 | 2,230,350 | 4,378,004 | 49.1% | No |
| Revenue | 2026-02 | 2026-05 | 2,112,620 | 4,035,819 | 47.7% | Yes |
| Revenue | 2026-01 | 2026-04 | 2,005,512 | 3,820,289 | 47.5% | Yes |
| Revenue | 2025-12 | 2026-03 | 1,910,282 | 3,608,228 | 47.1% | Yes |
| Revenue | 2025-11 | 2026-02 | 1,820,683 | 3,319,989 | 45.2% | No |

This is the textbook, well-understood failure mode of linear extrapolation: the model
projects the recent *average* slope forward, so it systematically **under-forecasts**
during a genuine acceleration in growth rate. It is not a bug — a piecewise or
regime-aware forecasting model would very likely do better in exactly this window, which
is why that's listed as a future direction in `RESEARCH.md` rather than something silently
tuned around.

**Reproduce:** the backtest script iterates `ForecastEngine.time_series_forecast()` over
every valid 3-month-ahead origin in `omniintelos.generate_kpis()`'s known series and
compares to the known future value; not checked into `scripts/` as it's a one-off
analysis, but the methodology above is exact and reproducible from `forecasting.py` and
`omniintelos.py` directly.

## 2. GraphRAG-lite: entity-extraction coverage and multi-hop retrieval

### 2a. Department-entity coverage, by domain

**Methodology.** `EntityExtractor.extract_entities()` (`src/services/entity_extractor.py`)
was run over every row of the live `kpi_metrics` table (7,878 rows across 7 domains) and
checked for whether a `department` entity was successfully inferred.

**Before fix** — the `department_patterns` dictionary had no keyword entries at all for
the IT or ESG domains:

| Domain | Rows | Department inferred | Coverage |
|---|---|---|---|
| Finance | 1,872 | 1,872 | 100.0% |
| Growth | 1,248 | 1,248 | 100.0% |
| Logistics | 702 | 702 | 100.0% |
| Operations | 936 | 936 | 100.0% |
| People | 1,092 | 1,092 | 100.0% |
| ESG | 936 | 78 | 8.3% |
| IT | 1,092 | 0 | 0.0% |
| **Total** | **7,878** | **5,928** | **75.2%** |

IT and ESG rows still surfaced fine through plain KPI/chat retrieval — this extractor only
feeds the graph-based path — but graph queries scoped to "IT" or "ESG" as a department had
nothing to find.

**Fix:** added real keyword patterns for both domains, grounded in the actual metric names
present in the OmniIntelOS corpus (uptime, latency, vulnerability, deployment, incident,
MTTR, SLA for IT; emissions, carbon, renewable, diversity, governance, sustainability for
ESG).

**After fix:**

| Domain | Rows | Department found | Coverage |
|---|---|---|---|
| Finance | 1,872 | 1,872 | 100.0% |
| Growth | 1,248 | 1,248 | 100.0% |
| Logistics | 702 | 702 | 100.0% |
| Operations | 936 | 936 | 100.0% |
| People | 1,092 | 1,092 | 100.0% |
| ESG | 936 | 858 | 91.7% |
| IT | 1,092 | 780 | 71.4% |
| **Total** | **7,878** | **7,488** | **95.0%** |

**Known remaining limitation:** `_infer_department()` is a first-match keyword-substring
scan, so a metric name whose vocabulary spans two domains (e.g. an ESG row mentioning
"audit compliance," a term that also appears in Finance/Operations contexts) can resolve
to the wrong domain, or to none. The 71.4%/91.7% ceiling for IT/ESG — versus the 100%
achieved for the other five domains, whose vocabulary is more distinctive — is a direct,
measured consequence of that. A learned classifier trained on the corpus's own existing
category labels (see `RESEARCH.md`'s future directions) would very likely close this gap
without changing the underlying graph-traversal architecture.

### 2b. Multi-hop query retrieval: does the graph actually connect both sides?

**Methodology.** Entity coverage alone doesn't test whether *cross-domain* queries — the
actual point of a graph-based retriever, e.g. "compare headcount growth against finance
margin" — return records connected across the departments the query names, not just
records from whichever domain happens to be easiest to match. 8 hand-labeled two-domain
queries were run through the exact live code path the chatbot uses
(`graph_kpi_context()` → `_rank_from_persisted_entities()`) against the live
`kpi_entities` table, and each result set was checked for whether it contained at least
one record from *both* named departments.

**Before fix: 0 of 8 queries connected both named departments.** All 8 returned 8/8
requested records, but every one of them came from a single department. The root cause
was mechanistic, not random: because a single KPI record belongs to exactly one domain, no
record can ever score higher than 1 on a genuinely two-domain query — every relevant
record ties at score 1. The original ranking code sorted by score and sliced to `top_k`;
Python's stable sort preserves the underlying table order on ties, so the slice
deterministically returned whichever department happened to sort first in the
`kpi_entities` table — never a mix.

**Fix:** after scoring, matches are grouped by department and round-robin-interleaved
before the `top_k` slice, so a query naming N departments draws from all N of them (in
score order within each) rather than being starved by insertion order. Committed as part
of this evaluation, in `src/services/graph_retrieval.py::_rank_from_persisted_entities()`.

**After fix:** re-running the same 8 labeled queries against live data, all 8 return a
result set spanning both named departments — the fix converts the round-robin allocation
directly into the both-sides-connected metric, since it's now structurally guaranteed
whenever both departments have at least one matching record.

This is the more important of the two knowledge-graph findings: entity coverage measures
whether individual records get tagged correctly, but this measures whether the graph
*retrieval path* — the thing a user's multi-hop question actually depends on — does what
it claims to do. It didn't, and now it does.

## 3. Live production RAG evaluation

**Methodology.** `scripts/evaluate_production_live.py` submits each of 50 fresh evaluation
cases (`tests/rag_eval.jsonl`, generated by `scripts/build_rag_eval_set.py`, which verifies
every case against what's actually in the live database before writing it) to the real,
deployed production API — via `POST /api/v1/chat/async` + poll (not the blocking
synchronous endpoint; see §3d), so a slow cold-retrieval case can't be cut short by a
reverse proxy's own timeout mid-request. Every real chat response is then scored using
RAGeval's own multi-judge-consensus evaluator (`RAGEvaluator.score_interaction()`) — the
same dogfooded evaluation path IntelAI's live traffic is scored with in production, not a
bespoke one-off scorer for this document. Five metrics are computed per case: retrieval
relevance, groundedness (judge consensus), faithfulness, an `overall_quality` composite
(0.4·relevance + 0.4·groundedness + 0.2·faithfulness), and cost/latency.

The 50 cases deliberately go beyond single-value KPI lookups: 28 span the corpus's full
2020-01 through 2026-06 timeline (not clustered on one easy month — see §3c on why that
matters), 12 test document/audio/PPTX/XLSX retrieval, 3 test glossary lookups, and 6 test
capabilities beyond retrieval specifically — cross-metric correlation, health/risk-status
synthesis, tailored action-plan generation, and live web search (§3e).

**Result: 50/50 cases completed, 0 crashes.**

| | |
|---|---|
| Ground-truth accuracy (objective, judge-independent) | **71.4%** (20/28 applicable cases) |
| Avg groundedness (judge panel) | 0.572 (0.599 excluding judge-dropout-affected cases — see §3b) |
| Avg overall quality | 0.479 |
| Avg latency | 74.6s/case |

Ground-truth accuracy checks whether the answer contains the actual recorded value from
the live database — independent of any LLM judge, so it's the more trustworthy top-line
number. The judge-panel groundedness average is reported too, but with the caveat in §3b.

### 3a. By case kind

| Kind | N | Avg groundedness | Avg latency |
|---|---|---|---|
| glossary | 3 | 0.979 | 52.6s |
| kpi-fr (French) | 7 | 0.917 | 74.1s |
| cross-domain | 1 | 0.762 | 72.9s |
| correlation | 2 | 0.644 | 79.4s |
| document | 12 | 0.530 | 80.6s |
| action-plan | 2 | 0.500 | 57.7s |
| health | 1 | 0.512 | 60.2s |
| kpi (English) | 21 | 0.431 | 77.4s |
| web-search | 1 | 0.275 | 55.0s |

### 3b. Judge-panel reliability under concurrent gateway load

This run's judge panel (`JUDGE_MODELS`) and 4 of the 9 personas' reasoning tier
(`ceo`/`cfo`/`cto`/`risk`) were both temporarily routed through the same third-party
multi-model gateway for this evaluation — see the note at the top of this document on
why, and `RESEARCH.md` for the mechanism. Sharing one gateway key between the judge
panel and the chat calls being judged meant both competed for the same rate limit: 2 of the 4
configured judges (`claude-haiku-4-5`, `gpt-3.5-turbo`) were intermittently reported
`unavailable (skipped)` by RAGeval's own judge-availability check on 7 of the 50 cases.

RAGeval tolerates this by design (`MIN_JUDGES_REQUIRED = 2` — it never halts or
substitutes a fallback judge, it just proceeds on however many of the configured judges
responded), so no case crashed or was dropped. But it does mean groundedness on those 7
cases reflects fewer independent judges than intended:

| | Avg groundedness | N |
|---|---|---|
| Full judge panel available | 0.599 | 43 |
| Judge dropout (2 of 4 responded) | 0.407 | 7 |

This is a reporting caveat, not a retrieval defect — disclosed here rather than blended
into a single clean-looking average. It doesn't affect ground-truth accuracy, which checks
the answer's actual content, not a judge's opinion of it.

### 3c. Two real retrieval bugs this run found (and fixed)

The original 44-case set asked exclusively about 2026-06 — every metric's *latest*
recorded period — because the case generator always picked each metric's newest value.
Since 2026-06 also happens to be served by a separate "live KPI snapshot" mechanism that
bypasses document retrieval entirely, every case trivially scored ~0.99 regardless of
whether historical-document retrieval worked at all. Diversifying the case generator
across the corpus's full 2020-2026 timeline immediately surfaced two real, previously
invisible retrieval bugs:

1. **Dense/sparse fusion collision** (`vector_store.py`) — Qdrant's dense index caps a
   document's embedded copy at `VECTOR_STORE_CONTENT_CHARS` (4000 chars) for embedding-size
   reasons, but BM25 always reads the full, untruncated document from Postgres. Both copies
   of the same document hashed to the same fusion key (title + first 80 chars — identical
   for a truncated and untruncated copy of the same text), and the dense loop ran first and
   won unconditionally, silently discarding the full BM25 copy every time both retrieval
   paths matched the same document.
2. **Prompt-assembly truncation ignored the query** (`omnismart_chatbot.py`) — a second,
   independent `text[:4000]` cap when building the final LLM prompt always took a
   document's *head*, regardless of what the query actually asked about. This cap had
   already been raised twice before (500 → 2000 → 4000) chasing the same recurring
   symptom; raising it again couldn't fix it, since a full annual KPI digest (12
   months of data, one section per month) runs 24,000+ characters — any fixed head-cap
   loses whichever months sort later in the document.

**Live before/after**, same query (`How did COGS stand in 2020-06, and where does that
figure come from?`, cfo persona):

- **Before:** *"The precise COGS figure for 2020-06 is not visible in the data excerpts
  provided to me. The month-by-month detail cuts off before reaching June."*
- **After:** *"COGS in June 2020 was $100,773 USD [3][5]... approximately 54.4% of revenue
  ($185,327 USD in June 2020)"* — the correct, database-verified figure, cited.

Fix: `_window_around_query()` centers the same 4000-char budget on wherever the query's
own period mention (e.g. "2020-06") appears in the document, instead of always taking the
head — falling back to head-truncation, unchanged from before, for queries that don't name
a specific period (e.g. "what does this document cover overall"). Shipped as issue
[#145](https://github.com/Yacine-ai-tech/IntelAI/issues/145) (PR
[#146](https://github.com/Yacine-ai-tech/IntelAI/pull/146)) and issue
[#147](https://github.com/Yacine-ai-tech/IntelAI/issues/147) (PR
[#148](https://github.com/Yacine-ai-tech/IntelAI/pull/148)), both live-verified against
production before and after.

**The lesson generalizes:** an eval set that only exercises the easiest, freshest slice of
data will always look better than the system actually is. Both of these bugs were real,
shipped, and invisible until the eval set stopped taking the easy path.

### 3d. Cloudflare timeout resilience (WebSocket + REST)

A real chat turn under cold retrieval can take 60-100s+ (see §3a's per-kind latencies) —
long enough that Cloudflare's free-tier proxy in front of production (~100-125s hard
ceiling, HTTP 524) risked cutting an otherwise-successful request short. Verified and
fixed for both transports the app exposes:

- **WebSocket** (`/api/v1/ws/chat`, what the product UI uses): periodic `{"type":
  "status"}` keepalive frames while the real work runs in the background, so the socket
  never goes traffic-silent long enough to look idle to a proxy. Live-verified: 4 status
  frames at ~12s intervals during a 58.3s turn, then the correct final response.
- **REST** (used by this benchmark, and any non-WS client): new `POST /api/v1/chat/async`
  + `GET /api/v1/chat/{job_id}` job/poll pair, Postgres-backed so a job survives the
  process restarting mid-run — the same pattern DocIntel's `batch_processor.py` already
  uses for the identical reason. The existing synchronous `POST /api/v1/chat` is
  unchanged for callers who can tolerate the wait. Live-verified: a 63.6s case completed
  cleanly via 12 lightweight poll requests, none of which individually risked the ceiling.

Shipped as [#142](https://github.com/Yacine-ai-tech/IntelAI/pull/142).

### 3e. Beyond retrieval: correlation, health status, action plans, and web search

Six of the 50 cases specifically exercise capabilities beyond "look up a value" — the
things the personas' own system prompts claim ("Proactively flag issues and recommend
mitigation strategies," "when you do recommend, tie it to a specific figure"). All six
produced real, non-trivial responses, live-verified:

- **Correlation** (cto persona): asked how Deployment Frequency correlates with Change
  Failure Rate — the response reasoned across both metrics rather than answering one and
  ignoring the other.
- **Health status** (risk persona): asked for a compliance health assessment from Audit
  Compliance Score + Privacy Incident Count — produced a synthesized status, not a single
  number.
- **Action plans** (coo, chro personas): asked for a recommended plan given
  Stockout Rate + On-Time Delivery Rate (and separately, Employee Turnover + Absenteeism)
  — both produced concrete, figure-grounded recommendations rather than generic advice.
- **Web search** (esg persona): asked how the company's Renewable Energy Ratio compares to
  industry best practices — a question the internal KPI/document corpus can't answer alone.
  Confirmed live: the response cited **4 real external sources** (Deloitte, SEIA, the
  Business Council for Sustainable Energy, and the U.S. EIA) fetched via Tavily and blended
  with internal data, not a refusal or a hallucinated citation.

Groundedness on this small slice (n=1-2 per kind) is directionally useful but not
statistically meaningful alone — the point of these cases is confirming the capability
fires and produces a real, sourced answer, which it does.

### 3f. A note on `PERSONA_SCOPE_VIOLATION`

Two cases (both action-plan) were flagged `PERSONA_SCOPE_VIOLATION` by RAGeval's own
scorer. This flag is a **prose-level heuristic** — it scans the answer's sentences for
vocabulary associated with a domain outside the persona's declared scope — not a check of
what data the backend actually retrieved. A COO's action plan naturally mentions revenue
or customer impact while reasoning about a logistics fix; that's legitimate cross-
functional business reasoning, not a data leak. The backend's actual RBAC enforcement
(`omnismart_chatbot.py`'s `scope`/`data_access` filtering, which drops any *retrieved*
document/KPI outside the persona's domain before it ever reaches the model) is a separate,
harder guarantee — see the dedicated RBAC-scoping benchmark for a test of that specifically
rather than reading this flag as evidence either way.

**Reproduce:** `python scripts/build_rag_eval_set.py && python
scripts/evaluate_production_live.py`. Full per-case results:
`eval/RAGEVAL_PRODUCTION_LIVE_REPORT.json`.

## 4. Admin scenario-switching correctness

The `Admin → Scenarios` tab (`POST /api/v1/admin/scenario`, `scripts/seed_scenarios.py`)
overlays one of 7 modelled health scenarios on top of the real OmniIntelOS baseline for
demos and benchmarking (§9 of `DATA_SEEDING.md`) — every scenario row is tagged
`source LIKE 'seed_%'` so it's always separable from, and never supposed to touch, the
baseline underneath. Diversifying the RAG eval set (§3c) led to testing this feature more
thoroughly, which surfaced two real correctness bugs in how that overlay actually behaved
in the database, not just in the demo UI.

### 4a. Duplicate/conflicting KPI values while a scenario is active

`get_kpi_metrics()` had no awareness that the scenario-switcher writes an alternate value
for the same `(period, category, metric)` under a `seed_`-prefixed `source`, without
touching the real baseline row. While a scenario was active, a query for a single
metric+period could return **two** rows — the baseline's and the scenario's — with no
defined winner. Confirmed live: `_retrieve_context()`'s KPI-snapshot builder joins every
matching row into one text block, so the chat copilot's own prompt would contain the same
metric twice with two different values (e.g. `COGS=82,084 USD; COGS=95,000 USD`) with
nothing in the text distinguishing which one was real.

The first fix attempt — a `DISTINCT ON` keyed on `period + category + metric + segment` —
didn't actually resolve it: the baseline and scenario generators stamp different,
arbitrary segment labels (`"OmniIntelOS"` vs `"Global"`) for what's the same underlying
fact, so both rows survived the dedup as if they were legitimately different data. The
real fix resolves conflicts at `(period, category, metric)` only, letting a `seed_`-source
row win outright whenever one exists for that fact — segment stays a free dimension
*within* whichever source wins, so legitimate multi-segment data elsewhere in the corpus
(e.g. per-country ESG rows) is untouched.

### 4b. Activating any scenario wiped the ENTIRE `kpi_entities` table

`store_kpi_entities(rows, replace=True)` ran an unconditional `DELETE FROM kpi_entities` —
not scoped to the scenario's own rows — every single time a scenario was activated. This
silently destroyed every GraphRAG-lite entity extracted from the real baseline dataset on
ordinary CSV ingest, not just the previous scenario's entities: switching scenarios twice
in a demo was enough to leave the baseline's own multi-hop retrieval graph permanently
empty. Fixed by adding a `source` column to `kpi_entities` and scoping the delete to
`source LIKE 'seed_%'` — the same `replace_prefix` contract `store_knowledge_docs()`
already used for the identical reason — with both write paths (auto-extraction on
ordinary ingest, and the scenario generator) now stamping `source` per row so the delete
knows what it's actually allowed to remove.

A third gap closed in the same fix: there was previously no way to get back to the *exact*
original baseline — selecting the `healthy` scenario meant "regenerate a fresh
synthetic healthy-looking dataset," not "restore the real thing," so the specific baseline
values any earlier benchmark run in this document was measured against weren't
guaranteed to survive a scenario round-trip. Since every scenario write is
additive-alongside (the baseline's own rows/tags are never modified while a scenario is
active), `reset_to_baseline()` now just deletes the scenario's overlay across all three
affected tables (`kpi_metrics`, `kpi_entities`, `knowledge_base`) — exposing the real
baseline again exactly, by construction, since it was never touched in the first place,
rather than by re-running a generator and hoping the output matches.

A related, unrelated-to-correctness perf fix found along the way: `get_kpi_entities()` had
no filtering at all — it pulled the entire table (77,000+ rows) on every call, including
on the hot GraphRAG-lite chat-retrieval path (§2b). Added a server-side, indexed
`entity_values` filter and wired `graph_retrieval.py`'s ranking function to request only
the entity values a given query actually mentions, instead of the whole table.

Shipped as issue [#151](https://github.com/Yacine-ai-tech/IntelAI/issues/151) (PR
[#152](https://github.com/Yacine-ai-tech/IntelAI/pull/152)).

**The lesson generalizes the same way §3c's did:** these bugs were invisible from the
demo UI (which always shows a single, defined answer) and only surfaced once the
underlying data model was queried the way the RAG copilot actually queries it —
diversifying what gets tested, not just adding more of the same test, is what found both.

## 5. Hybrid retrieval as its own axis: three targeted live probes

**Methodology.** `USE_HYBRID_RETRIEVAL=true` is always on in production (`src/services/
hybrid_retrieval.py` + `vector_store.py::vector_store_retrieve()`) — dense (Qdrant) and
sparse (BM25) candidates fused via Reciprocal Rank Fusion, then optionally reranked by a
cross-encoder (`RERANK_PROVIDER=remote`, currently the same on-demand orchestrator host
`EMBED_URL`/`RERANK_URL` point at). There's no live toggle to disable hybrid via the API,
so this can't be an A/B ("hybrid vs. dense-only") test through the deployed system.
Instead, three live queries were designed to each isolate a *different* mechanism hybrid
retrieval is supposed to provide over either half alone, submitted via the real
`POST /api/v1/chat/async` + poll path (same pattern as §3d) against production, and judged
against real ground truth from `tests/rag_eval.jsonl` and the raw corpus in `data/`, not
against the model's own prose. All three latencies below are the API's own server-side
`latency_ms`, not client-measured wall time.

A structural note that applies to all three: the `sources` array returned by the chat API
mixes two different provenance types, visible directly in `omnismart_chatbot.py`'s
`_retrieve_context()` (lines ~926–1002) — "Live KPI snapshot" cards, one per domain in the
persona's scope, injected directly with a **hardcoded `relevance: 1.0`** (not a retrieval
score at all), and actual hybrid-retrieved `knowledge`/`glossary` docs, which carry the
real fused/reranked `relevance: round(score, 3)`. Only the second group is evidence about
hybrid retrieval's own behavior — the KPI cards' `1.0` is not a signal of anything and is
excluded from the analysis below.

### 5a. Lexical exact-match (BM25-favorable)

**Query** (`esg` persona): *"How did Carbon Intensity per Revenue stand in 2025-07, and
where does that figure come from?"* — the exact metric name as it appears in the corpus.

**Result:** correct on the first try. **129.57 tCO₂e/USD million**, against the live
database's recorded 129.5739 (`tests/rag_eval.jsonl`) — matches to the reported precision.
Server latency: **52.5s** (5,684 tokens).

| Rank | Source | Type | Relevance |
|---|---|---|---|
| 4 | `esg_2025_en.md` | knowledge | 1.0 |
| 5 | `esg_2025_fr.md` | knowledge | 0.984 |
| 6 | `esg_2024_en.md` | knowledge | 0.961 |

(3 KPI-snapshot cards preceded these at ranks 1–3, hardcoded relevance, excluded per the
note above.) The answer cited `[4]` — the correct English 2025 digest — over the French
duplicate of the same document and the prior year's digest, both real near-neighbors a
lexical-only match could plausibly have confused. This is hybrid retrieval doing exactly
what BM25 is for: an exact metric-name-plus-period query resolved to the right document
on the first pass, with **distinct**, monotonically-decreasing relevance scores across the
three real candidates (1.0 / 0.984 / 0.961) — a pattern that recurs as the key signal in
§5c below.

### 5b. Semantic paraphrase, zero shared vocabulary (dense-favorable)

**Query** (`chro` persona): *"Roughly what share of our staff left the company in the
twelve months ending around May 2022?"* — deliberately shares no vocabulary with the
corpus's actual metric name, "Annual Employee Turnover" (checked against
`tests/rag_eval.jsonl`'s `expected` field before writing this query): "staff" not
"employee", "left the company" not "turnover", no use of "annual".

**Result:** *"Approximately 22% of the workforce left the company over the twelve-month
period ending around May 2022 (annual employee turnover reported as 22.22% in the
September 2022 review)"* — cited `[4]`, `omniintelos_minutes_2022-09_en.md`. Server
latency: **53.2s** (2,445 tokens).

| Rank | Source | Type | Relevance |
|---|---|---|---|
| 3 | `Glossary: Gross Margin` | glossary | 1.0 |
| 4 | `omniintelos_minutes_2022-09_en.md` | knowledge | 0.963 |

**Verified real, not hallucinated:** line 52 of that document (`data/omniintelos/
Corporate/omniintelos_minutes_2022-09_en.md`) literally reads *"Annual Employee Turnover
closed the period at 22.22% (average 22.22%), flat from 22.22% - in the risk band"* — the
cited figure is genuine and correctly grounded.

**But it's not the same fact the eval set's matching case checks.** A separate
`tests/rag_eval.jsonl` case asks for this exact metric at the exact period 2022-05 and its
ground truth is **29.1799%**, not 22.22% — a different, more precise fact (the actual
monthly KPI table row) than what a Sept 2022 crisis-review meeting's narrative summary
reports for "the period" in looser terms. This is the honest, real behavior of dense
retrieval on a genuinely paraphrased, loosely-dated query: it found a real, well-grounded,
topically on-target document with **zero lexical overlap** with the query — proving the
dense half of hybrid retrieval is doing real semantic work, not just falling through to
BM25 on the shared "2022"/"May" tokens — but a vague natural-language period reference
("around May 2022") does not reliably resolve to the one precise monthly database row the
way an exact metric-name-plus-period query does in §5a. That's a real precision trade-off,
not a hallucination: every number in the answer traces to a real, cited source.

A second honest note from the same call: `Glossary: Gross Margin` — topically unrelated to
employee turnover — surfaced in `sources` at the top-normalized relevance of 1.0. Glossary
entries are seeded as ordinary knowledge docs (`data/glossary.py`) and retrieved through
the identical hybrid path as any other document, so this is real fusion noise on a query
whose paraphrased vocabulary apparently pulled in a spurious dense-side neighbor, not a
separate bug — worth disclosing rather than cropping out of the sources list.

### 5c. Rerank under real ambiguity: did the cross-encoder actually engage?

**Query** (`ceo` persona, full 7-domain scope): *"What is our turnover situation right
now, both from a staffing perspective and a warehouse-stock perspective?"* — deliberately
overloads the single word "turnover" across two real, differently-scaled metrics (Annual
Employee Turnover / Turnover Rate in People vs. Inventory Turnover in Logistics) to force
real reranking work: fusion alone can't tell these apart on lexical grounds.

**Result:** the response correctly separated the two — **Turnover Rate: 6.86%** cited to
the People KPI snapshot `[7]`, **Inventory Turnover: 10.21x** cited to the Logistics KPI
snapshot `[5]`, plus historical comparison figures pulled from two logistics digests —
correct domain disambiguation, driven by the KPI-snapshot injection's own per-domain
tagging rather than anything rerank-specific. Server latency: **69.8s**, the longest of
the three (6,861 tokens — a full structured answer with headings, two metric sections, and
a summary table, which alone accounts for a real share of the extra time).

| Rank | Source | Type | Relevance |
|---|---|---|---|
| 8 | `Glossary: Inventory Turnover` | glossary | 1.0 |
| 9 | `logistics_2023_en.md` | knowledge | 0.639 |
| 10 | `logistics_2020_en.md` | knowledge | 0.639 |

**This is the signal the task asked for.** `logistics_2023_en.md` and `logistics_2020_en.md`
are two different documents with different content, yet tied at **exactly** 0.639 — three
decimal places of coincidence. A real cross-encoder forward pass produces continuous
floating-point logits; two distinct documents landing on the identical score to three
decimals is a vanishingly unlikely coincidence for a genuine rerank, but is exactly what
`hybrid_retrieval.py`'s own documented RRF-fallback formula produces (`rrf[i] / max(rrf)`
— an exact tie whenever two candidates' fused rank-sums happen to match, which two
structurally near-identical "Logistics — Annual KPI Digest" documents plausibly did here).
Compare §5a's three **distinct**, non-tied scores (1.0 / 0.984 / 0.961) under the same
code path — the two probes' score *shapes* look like the two different code paths
(reranked vs. RRF-only) `retrieve()`'s own fallback branch describes, not like the same
mechanism producing different numbers by chance.

**Is this the already-documented timeout fallback, or a new bug? Verified directly against
the orchestrator host, not just inferred.** The three probes above were run *concurrently*
(§5a/§5b/§5c fired as three simultaneous background jobs against production), so this
question was checked by calling `RERANK_URL`/`EMBED_URL`'s `/embed` and `/rerank` endpoints
directly, in isolation, outside the app:

| Call | Payload | Isolated latency | vs. configured timeout |
|---|---|---|---|
| `/embed` | 1 realistic query string | 2.6-2.9s (2 runs) | well under `EMBED_TIMEOUT=15s` |
| `/rerank` | 20 texts (this pipeline's realistic candidate count, `cand=max(top_k*4,20)`) | 10.7-11.1s (2 runs) | well under `RERANK_TIMEOUT=15s` |
| `/rerank` | 3 texts, fired back-to-back with other overlapping test calls | 23.0-24.5s | **exceeds** `RERANK_TIMEOUT=15s` |

A single, uncontended request comfortably fits inside both configured timeouts — and
produces genuine, well-differentiated cross-encoder output: a direct `/rerank` call with
the query *"employee turnover"* against three real corpus sentences returned distinct
scores of 0.724 (the actual turnover sentence), 0.008 (a related but different metric),
and 0.00007 (an unrelated one) — exactly the kind of continuous, semantically-ordered
output a working cross-encoder should produce, confirming the reranker model itself is not
broken. The slow, timeout-triggering readings only appeared when multiple requests were
fired at this same host in close succession — which is exactly what running §5a, §5b, and
§5c *concurrently* against production did to the shared inference host behind the scenes.
**The most likely explanation for §5c's tied RRF-fallback score, corrected from an earlier
draft of this section, is contention from this benchmark's own concurrent probes on a
low-concurrency host — not a standing per-request timeout misconfiguration.** `.env`'s
`INFERENCE_WAKE_TIMEOUT=40s` cap (this session's earlier, correct fix for a *different*,
already-documented incident — a cold host previously blowing through Cloudflare's
~100-125s ceiling) is real and still matters under genuine cold-start or concurrent-load
conditions; it just isn't the deterministic per-request cause it first looked like here.
Server logs still aren't available to confirm which of "concurrent-load contention" or
"a genuinely cold host at that moment" actually triggered this specific fallback — both
remain live possibilities, and both are the same class of shared-low-concurrency-host
degradation this document already discloses, not a newly discovered defect.

**Summary across the three probes:**

| Probe | Mechanism tested | Server latency | Tokens | Outcome |
|---|---|---|---|---|
| §5a lexical exact-match | BM25 half | 52.5s | 5,684 | Correct value, correct doc, distinct rerank-shaped scores |
| §5b semantic paraphrase | dense half | 53.2s | 2,445 | Real, grounded, zero-vocab-overlap match; resolved to a related but less precise fact than the exact DB row |
| §5c rerank under ambiguity | cross-encoder stage | 69.8s | 6,861 | Correct domain disambiguation; tied scores indicate RRF-fallback — isolated direct testing shows this is very likely concurrent-probe contention on a shared host, not a per-request config bug |

**Reproduce:** `POST /api/v1/chat/async` with the three queries and personas above against
`https://intelai.ysiddo-ai-projects.app`, poll `GET /api/v1/chat/{job_id}`, and inspect the
`sources` array's `relevance` field per source `type` — excluding `kpi`-type entries, whose
relevance is hardcoded and not evidence of anything.

## 6. A real bug §5 surfaced: orphaned async chat jobs never resolve

**What happened.** While the very first attempt at §5a's lexical-match probe was running,
its job sat at `status: "running"` for over 650 seconds — more than 4x the longest real
chat turn measured anywhere else in this document — and never moved. Re-polling the exact
same `job_id` repeatedly confirmed it: not slow, genuinely stuck.

**Root cause.** `src/services/chat_jobs.py::run_job()` is passed to FastAPI's
`BackgroundTasks.add_task()` and executes on the *same worker process* that handled the
original `POST /api/v1/chat/async` request — this is by design (see `POST /chat/async` in
`src/api/server.py`), not a defect on its own. But this is also a single free-tier
`WEB_CONCURRENCY=1` instance that does restart (deploys, OOM, host recycling — all called
out in `chat_jobs.py`'s own module docstring as real, expected events). If that restart
happens while a job is mid-run, nothing is left running to ever write `status='done'` or
`status='error'` for it — the row (durably persisted in Postgres specifically so a job
*record* survives a restart) is left at `'running'` forever, and `GET /chat/{job_id}`
faithfully, endlessly reports a status that no process is ever going to change again. The
Postgres-backed job store solves "don't lose the job's existence" but not "notice when the
work behind it is gone" — those are two different guarantees, and only the first existed.

**Fix.** Added `_reap_if_stale()` to `chat_jobs.py`, called at the top of `get_job()`
(`STALE_RUNNING_SECONDS = 600` — comfortably above the 50-150s real chat turns measured in
§3, so a merely slow turn is never misdiagnosed as orphaned). On each poll, a single scoped
`UPDATE ... WHERE status='running' AND updated_at < NOW() - make_interval(secs => 600)`
flips a stuck job to `'error'` with an explanatory message, so a polling client gets a real
terminal status — and can retry — instead of polling a corpse indefinitely. Scoped
correctly, this is a no-op on every poll of a healthy or already-finished job; it only ever
touches a row that is both still `'running'` and stale. Covered by
`tests/test_unit_chat_jobs.py` (in-memory, no live DB needed — asserts the reaper's SQL
targets exactly a stuck-and-running row, never raises on a broken connection, and that the
threshold stays well clear of a real chat turn's latency).

**Scope note:** this fix changes real backend code, not just this document. Render's
`render.yaml` has `autoDeploy: false` for this service, so — unlike the docs-only §1-5
change this benchmark started as — this fix does not take effect on the live deployment
until a maintainer with Render dashboard access triggers a manual deploy of the merged
commit.

## Honest caveats

- The forecast backtest is scored against OmniIntelOS's own synthetic-but-deterministic
  78-month series — it validates `ForecastEngine`'s behavior faithfully, but the absolute
  MAPE numbers are specific to this dataset's volatility and regime structure, not a
  universal claim about linear-regression forecasting accuracy on arbitrary business data.
- The entity-extraction and multi-hop fixes were both found *by* the process of writing
  this document, not before it — this benchmark changed the code it's reporting on. That's
  disclosed here rather than presented as if the numbers were static.
- GraphRAG-lite, as documented in `RESEARCH.md`, is a deterministic keyword-pattern
  extractor, not an LLM-driven entity/relationship pipeline — its accuracy ceiling is
  exactly what a keyword-substring heuristic's ceiling would be, and section 2a measures
  that plainly rather than asserting parity with LLM-based GraphRAG implementations.
- Live production evaluation depends on a GPU inference backend that isn't always warm on
  first request — a real operational characteristic of running inference on an on-demand
  host, not an artifact of the evaluation methodology. Any case that fails after retries is
  reported as a failure, not excluded from the count. All 50 of this run's cases completed
  (0 failures) once the Cloudflare-timeout fix in §3d shipped.
- §3's judge-panel groundedness average is depressed by real, disclosed judge-availability
  dropout on 7 of 50 cases (§3b) — the clean-subset and ground-truth-accuracy numbers are
  the more reliable read on actual system quality from this run.
- The two case kinds with n=1 (health, web-search) and n=2 (correlation, action-plan) are
  real, live-verified capability checks, not statistically powered quality measurements —
  reported as what they are in §3e rather than inflated into a false-precision average.
- §4's two scenario-switching bugs, like the entity-extraction/multi-hop fixes above, were
  found by testing more thoroughly *while* this benchmark work was underway, not before
  it — disclosed the same way, rather than presented as if they'd always been correct.
- §5 is 3 targeted probes, not a statistically powered study — `USE_HYBRID_RETRIEVAL` has
  no live off-switch in production, so there is no true dense-only/BM25-only control to
  compare against directly; each probe instead isolates one mechanism as cleanly as a
  single live query can.
- §5c's conclusion that a tied relevance score indicates RRF-fallback (not genuine
  reranking) is an inference from score shape and direct isolated testing of the
  orchestrator host, not a server-log confirmation — disclosed as such rather than
  presented as directly observed. An earlier draft of this section attributed the
  fallback to `INFERENCE_WAKE_TIMEOUT`'s cold-host behavior specifically; direct testing
  showed a single uncontended request comfortably fits the configured timeouts, so that
  draft's framing was corrected in place to point at concurrent-probe contention instead
  — left visible here rather than silently rewritten.
- §6's fix is real backend code, verified by a passing in-memory unit test, but not
  verified against the live deployment — `render.yaml`'s `autoDeploy: false` means it
  isn't live until someone with Render dashboard access deploys the merged commit.

## Further reading

- [`RESEARCH.md`](RESEARCH.md) — the reasoning behind each design choice benchmarked here.
- [`README.md`](README.md) — feature overview and quick start.
