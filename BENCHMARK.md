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

## Further reading

- [`RESEARCH.md`](RESEARCH.md) — the reasoning behind each design choice benchmarked here.
- [`README.md`](README.md) — feature overview and quick start.
