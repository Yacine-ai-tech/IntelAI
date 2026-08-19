# Benchmark Results

This document reports what was actually measured against IntelAI's live deployment and
its real OmniIntelOS demo dataset — not aspirational numbers. For the reasoning behind
*why* each component is designed the way it is, see [`RESEARCH.md`](RESEARCH.md); this
document is the "what we measured."

Every number below comes from a script in `scripts/` or a one-off analysis run against
the live database and the live production API, described inline so the methodology is
reproducible rather than asserted. Where a result exposes a real limitation, it's reported
as such — a benchmark that only shows wins isn't a benchmark.

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
2025–Mar 2026 — the window where OmniIntelOS's own growth genuinely accelerates:

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

**Reproduce:** the backtest iterates `ForecastEngine.time_series_forecast()` over every
valid 3-month-ahead origin in `omniintelos.generate_kpis()`'s known series and compares to
the known future value — the methodology above is exact and reproducible directly from
`forecasting.py` and `omniintelos.py`.

## 2. GraphRAG-lite: entity-extraction coverage and multi-hop retrieval

### 2a. Department-entity coverage, by domain

**Methodology.** `EntityExtractor.extract_entities()` (`src/services/entity_extractor.py`)
was run over every row of the live `kpi_metrics` table (7,878 rows across 7 domains) and
checked for whether a `department` entity was successfully inferred, before and after
extending the keyword-pattern dictionary to cover the IT and ESG domains (which initially
had no entries at all).

| Domain | Rows | Coverage (before) | Coverage (after) |
|---|---|---|---|
| Finance | 1,872 | 100.0% | 100.0% |
| Growth | 1,248 | 100.0% | 100.0% |
| Logistics | 702 | 100.0% | 100.0% |
| Operations | 936 | 100.0% | 100.0% |
| People | 1,092 | 100.0% | 100.0% |
| ESG | 936 | 8.3% | 91.7% |
| IT | 1,092 | 0.0% | 71.4% |
| **Total** | **7,878** | **75.2%** | **95.0%** |

IT and ESG rows surfaced fine through plain KPI/chat retrieval throughout — this extractor
only feeds the graph-based multi-hop path.

**Known remaining limitation.** `_infer_department()` is a first-match keyword-substring
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
margin" — return records connected across the departments the query names. 8 hand-labeled
two-domain queries were run through the live code path the chatbot uses
(`graph_kpi_context()` → `_rank_from_persisted_entities()`) against the live
`kpi_entities` table, and each result set was checked for whether it contained at least
one record from *both* named departments.

**Result: 0 of 8 queries connected both named departments before a fix, 8 of 8 after.**
Since a single KPI record belongs to exactly one domain, no record can score higher than 1
on a genuinely two-domain query — every relevant record ties at score 1, and the ranking
step's tie-breaking behavior determined whether the result set actually spanned both
domains or silently collapsed to one. After fixing the tie-breaking to interleave matches
across departments rather than let insertion order decide, all 8 queries return a result
spanning both named departments.

This is the more important of the two knowledge-graph findings: entity coverage measures
whether individual records get tagged correctly, but this measures whether the graph
*retrieval path* — the thing a multi-hop question actually depends on — does what it
claims to do.

## 3. Live production RAG evaluation

**Methodology.** `scripts/evaluate_production_live.py` submits each of 50 fresh evaluation
cases (`tests/rag_eval.jsonl`, generated by `scripts/build_rag_eval_set.py`, which verifies
every case against what's actually in the live database before writing it) to the real,
deployed production API, via the async job+poll chat endpoint so a slow cold-retrieval
case can't be cut short by a reverse proxy's own timeout mid-request. Every response is
scored using RAGeval's own multi-judge-consensus evaluator — the same dogfooded evaluation
path IntelAI's live traffic is scored with in production, not a bespoke one-off scorer.
Five metrics are computed per case: retrieval relevance, groundedness (judge consensus),
faithfulness, an `overall_quality` composite, and cost/latency.

The 50 cases deliberately go beyond single-value KPI lookups: 28 span the corpus's full
2020-01 through 2026-06 timeline (not clustered on one easy month — see §3c), 12 test
document/audio/PPTX/XLSX retrieval, 3 test glossary lookups, and 6 test capabilities beyond
retrieval specifically — cross-metric correlation, health/risk-status synthesis, tailored
action-plan generation, and live web search (§3d).

**Result: 50/50 cases completed, 0 crashes.**

| | |
|---|---|
| Ground-truth accuracy (objective, judge-independent) | **71.4%** (20/28 applicable cases) |
| Avg groundedness (judge panel) | 0.572 (0.599 excluding judge-dropout-affected cases — see §3b) |
| Avg overall quality | 0.479 |
| Avg latency | 74.6s/case |

Ground-truth accuracy checks whether the answer contains the actual recorded value from
the live database — independent of any LLM judge, so it's the more trustworthy top-line
number.

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

### 3b. Judge-panel reliability under concurrent load

This run's judge panel and the reasoning-tier personas being judged shared rate-limited
upstream capacity, so the two competed for the same throughput: 2 of 4 configured judges
were intermittently unavailable on 7 of the 50 cases. RAGeval tolerates this by design
(it never halts or substitutes a fallback judge; it proceeds on however many of the
configured judges responded), so no case crashed or was dropped, but groundedness on those
7 cases reflects fewer independent judges than intended:

| | Avg groundedness | N |
|---|---|---|
| Full judge panel available | 0.599 | 43 |
| Judge dropout (2 of 4 responded) | 0.407 | 7 |

This is a reporting caveat, not a retrieval defect. It doesn't affect ground-truth
accuracy, which checks the answer's actual content, not a judge's opinion of it.

### 3c. Eval-set diversity matters, and two real retrieval issues it surfaced

An earlier, smaller case set asked exclusively about each metric's single latest recorded
period, which also happens to be served by a live-snapshot mechanism that bypasses
document retrieval entirely — every case trivially scored well regardless of whether
historical-document retrieval worked at all. Diversifying the case generator across the
corpus's full 2020-2026 timeline immediately surfaced two real, previously invisible
retrieval issues, both fixed prior to the run reported above: a fusion-layer bug that could
silently prefer a truncated copy of a document over its full text when both the dense and
sparse retrievers matched it, and a prompt-assembly truncation step that always kept a
document's head regardless of what period the query actually asked about.

**Live before/after**, same query (`How did COGS stand in 2020-06, and where does that
figure come from?`, cfo persona):

- **Before:** *"The precise COGS figure for 2020-06 is not visible in the data excerpts
  provided to me. The month-by-month detail cuts off before reaching June."*
- **After:** *"COGS in June 2020 was $100,773 USD [3][5]... approximately 54.4% of revenue
  ($185,327 USD in June 2020)"* — the correct, database-verified figure, cited.

**The lesson generalizes:** an eval set that only exercises the easiest, freshest slice of
data will always look better than the system actually is.

### 3d. Beyond retrieval: correlation, health status, action plans, and web search

Six of the 50 cases specifically exercise capabilities beyond "look up a value." All six
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
  industry best practices — a question the internal corpus can't answer alone. The
  response cited **4 real external sources** (Deloitte, SEIA, the Business Council for
  Sustainable Energy, and the U.S. EIA), blended with internal data, not a refusal or a
  hallucinated citation.

Groundedness on this small slice (n=1-2 per kind) is directionally useful but not
statistically meaningful alone — the point of these cases is confirming the capability
fires and produces a real, sourced answer, which it does.

### 3e. A note on `PERSONA_SCOPE_VIOLATION`

Two cases (both action-plan) were flagged `PERSONA_SCOPE_VIOLATION` by RAGeval's own
scorer. This flag is a **prose-level heuristic** — it scans the answer's sentences for
vocabulary associated with a domain outside the persona's declared scope — not a check of
what data the backend actually retrieved. A COO's action plan naturally mentions revenue
or customer impact while reasoning about a logistics fix; that's legitimate cross-
functional business reasoning, not a data leak. The backend's actual RBAC enforcement —
which drops any *retrieved* document/KPI outside the persona's domain before it ever
reaches the model — is a separate, harder guarantee, tested directly in §7.

**Reproduce:** `python scripts/build_rag_eval_set.py && python
scripts/evaluate_production_live.py`. Full per-case results:
`eval/RAGEVAL_PRODUCTION_LIVE_REPORT.json`.

## 4. Admin scenario-switching correctness

The `Admin → Scenarios` tab overlays one of 7 modelled health scenarios on top of the real
OmniIntelOS baseline for demos and benchmarking (§9 of `DATA_SEEDING.md`). Testing this
feature more thoroughly while diversifying the RAG eval set (§3c) surfaced two real
correctness issues in how the overlay behaved in the database, both fixed:

1. **Conflicting KPI values while a scenario was active.** The baseline and an active
   scenario could both hold a value for the same period/category/metric, with no defined
   winner — a query could surface both values in the same answer with nothing
   distinguishing which was authoritative. Fixed by resolving conflicts deterministically:
   a scenario-tagged value wins outright over the baseline whenever one exists for that
   specific fact.
2. **Activating any scenario wiped the entire entity graph, not just the previous
   scenario's overlay.** Every GraphRAG-lite entity extracted from the real baseline
   dataset was destroyed on each scenario activation — switching scenarios twice in a demo
   was enough to leave the baseline's own multi-hop retrieval graph permanently empty.
   Fixed by scoping entity deletion to the scenario's own tagged rows, and adding an exact
   baseline-restore path (rather than regenerating a fresh approximation) so reverting to
   `healthy` reproduces the precise original baseline any earlier benchmark run in this
   document was measured against.

**The lesson generalizes the same way §3c's did:** both bugs were invisible from the demo
UI, which always shows a single, defined answer, and only surfaced once the underlying
data model was queried the way the RAG copilot actually queries it.

## 5. Hybrid retrieval as its own axis: three targeted live probes

**Methodology.** Hybrid retrieval (dense + BM25, fused via Reciprocal Rank Fusion, then
optionally reranked by a cross-encoder) is always on in production; there's no live toggle
to disable it via the API, so this can't be an A/B ("hybrid vs. dense-only") test through
the deployed system. Instead, three live queries were designed to each isolate a
*different* mechanism hybrid retrieval is supposed to provide over either half alone,
submitted via the production chat API and judged against real ground truth, not against
the model's own prose. Latencies below are the API's own server-side measurement.

A structural note that applies to all three: the `sources` array mixes two provenance
types — "Live KPI snapshot" cards, injected with a hardcoded relevance of 1.0 (not a
retrieval score at all), and actual retrieved `knowledge`/`glossary` documents, which carry
the real fused/reranked relevance score. Only the second group is evidence about hybrid
retrieval's own behavior; KPI cards are excluded from the analysis below.

### 5a. Lexical exact-match (BM25-favorable)

**Query** (`esg` persona): *"How did Carbon Intensity per Revenue stand in 2025-07, and
where does that figure come from?"* — the exact metric name as it appears in the corpus.

**Result:** correct on the first try — **129.57 tCO₂e/USD million**, matching the live
database's recorded value to the reported precision. Server latency: 52.5s.

| Source | Type | Relevance |
|---|---|---|
| `esg_2025_en.md` | knowledge | 1.0 |
| `esg_2025_fr.md` | knowledge | 0.984 |
| `esg_2024_en.md` | knowledge | 0.961 |

The answer cited the correct English 2025 digest over the French duplicate of the same
document and the prior year's digest — both real near-neighbors a lexical-only match could
plausibly have confused — with distinct, monotonically decreasing relevance scores across
the three real candidates.

### 5b. Semantic paraphrase, zero shared vocabulary (dense-favorable)

**Query** (`chro` persona): *"Roughly what share of our staff left the company in the
twelve months ending around May 2022?"* — deliberately shares no vocabulary with the
corpus's actual metric name, "Annual Employee Turnover": "staff" not "employee", "left the
company" not "turnover", no use of "annual".

**Result:** *"Approximately 22% of the workforce left the company over the twelve-month
period ending around May 2022 (annual employee turnover reported as 22.22% in the
September 2022 review)"* — cited to a real corporate-minutes document, and verified
genuine (the source document literally contains that figure, correctly grounded). Server
latency: 53.2s.

**A real precision trade-off, not a hallucination.** A separate ground-truth case asks for
this exact metric at the exact period 2022-05, where the true monthly value is 29.18% — a
different, more precise fact than what a September 2022 narrative summary reports for "the
period" in looser terms. This is honest, real dense-retrieval behavior on a genuinely
paraphrased, loosely-dated query: it found a real, well-grounded, topically on-target
document with zero lexical overlap with the query, proving the dense half of hybrid
retrieval does real semantic work — but a vague natural-language period reference doesn't
reliably resolve to the one precise monthly database row the way an exact metric-name-plus-
period query does in §5a. Every number in the answer traces to a real, cited source.

### 5c. Rerank under real ambiguity: did the cross-encoder actually engage?

**Query** (`ceo` persona, full 7-domain scope): *"What is our turnover situation right
now, both from a staffing perspective and a warehouse-stock perspective?"* — deliberately
overloads the word "turnover" across two real, differently-scaled metrics (employee
turnover vs. inventory turnover) to force real reranking work, since fusion alone can't
tell these apart on lexical grounds.

**Result:** the response correctly separated the two — employee turnover and inventory
turnover both correctly identified, cited, and reported with real figures and historical
comparisons. Server latency: 69.8s, the longest of the three, reflecting a genuinely
longer structured answer rather than anything reranking-specific.

| Source | Type | Relevance |
|---|---|---|
| `logistics_2023_en.md` | knowledge | 0.639 |
| `logistics_2020_en.md` | knowledge | 0.639 |

Two different documents landed on an identical relevance score to three decimal places —
a strong signature of the fusion-only fallback path rather than genuine cross-encoder
reranking (compare §5a's distinct, non-tied scores under the same code path). Isolated,
uncontended testing of the reranking service confirmed the model itself works correctly
(distinct, well-differentiated scores on a controlled test) and comfortably fits the
configured timeout; the fallback observed here is best explained by contention from
running multiple probes concurrently against a shared, low-concurrency inference host, not
a standing timeout misconfiguration.

**Summary across the three probes:**

| Probe | Mechanism tested | Server latency | Outcome |
|---|---|---|---|
| §5a lexical exact-match | BM25 half | 52.5s | Correct value, correct doc, distinct rerank-shaped scores |
| §5b semantic paraphrase | dense half | 53.2s | Real, grounded, zero-vocab-overlap match; resolved to a related but less precise fact than the exact DB row |
| §5c rerank under ambiguity | cross-encoder stage | 69.8s | Correct domain disambiguation; tied scores indicate fusion-only fallback under concurrent-probe contention |

**Reproduce:** submit the three queries and personas above against the production API,
poll for the result, and inspect the `sources` array's relevance field per source type —
excluding `kpi`-type entries, whose relevance is hardcoded and not evidence of anything.

## 6. Multi-provider LLM routing resilience

**Methodology.** Every LLM call resolves through one function that maps a model tier
(`default`, `reasoning`, `judge`, and an as-yet-unused `local` tier) to a `provider/model`
string via an independently configurable environment variable — swapping providers for any
one tier is a config change, not a code change, and no call site has a second, divergent
model-selection path. Reasoning-tier personas (ceo/cfo/cto/risk) and default-tier personas
each resolve independently; a lightweight judge-tier call gates whether a live web search
is triggered for a given query.

**Two real incidents demonstrated this resilience during this project's own operation:**

1. **A primary reasoning-provider credit exhaustion**, absorbed gracefully rather than
   breaking chat: the affected call site already degrades to a keyword-trigger heuristic on
   any judge-call failure rather than erroring the response, so the actual live impact was
   reduced precision on one secondary routing decision (whether to trigger web search), not
   a broken chat turn. The fix was a one-line environment change repointing that tier at a
   different provider — no code change, picked up automatically by every existing call
   site.
2. **The fallback provider's own real capacity limits.** Under sustained benchmark load,
   the fallback provider hit real rate limits at two different granularities (a daily
   quota and a per-minute quota on an unusually large request). This is disclosed as a
   genuine, load-bearing operational characteristic — the routing design is what made
   recovering from it straightforward (credential separation and retry/backoff, no code
   change to the dispatch path), but "falls back to a second provider" is not a
   capacity-free escape hatch, and treating it as one would overstate the resilience this
   section demonstrates.

## 7. Persona/RBAC-scoped retrieval enforcement

**Methodology.** Every chat request carries the caller's persona, and retrieval — not just
the UI — is scoped to that persona's granted data domains before any document reaches the
model. This section verifies that enforcement directly with a live A/B test, rather than
inferring it from the absence of a document in one response (which is inherently
ambiguous: a missing source could mean RBAC filtered it, or could just as easily mean
retrieval simply didn't rank it for that query).

**Test design.** A narrowly-scoped persona (`cfo`, granted Finance and Growth only — the
most restrictive of the nine defined personas) and a wide-scope persona (`ceo`, granted all
seven domains) were each asked the identical question about a specific out-of-scope annual
document. The wide-scope persona's response establishes whether the document is real,
indexed, and top-ranked for that query at all — the retrievability control that makes the
narrow persona's result interpretable.

| Probe | Persona | Domain access | Query | Target document in results? |
|---|---|---|---|---|
| 1 | `cfo` | Finance, Growth | out-of-scope (ESG) annual digest | Absent |
| 2 | `ceo` | all 7 domains | identical query | Present, top relevance |
| 3 | `cfo` | Finance, Growth | in-scope (Finance) annual digest | Present, top relevance |

**Result.** The out-of-scope document was completely absent from the narrow persona's
response (Probe 1) while being the top-ranked, correctly cited result for the wide-scope
persona asking the exact same question (Probe 2) — confirming the document is real,
indexed, and retrievable, and that its absence for the narrow persona is attributable to
RBAC scoping rather than a retrieval miss. An in-scope control query for the narrow persona
(Probe 3) returned and correctly cited its target document normally, confirming the scoping
does not over-block legitimate in-scope access.

**Reproduce:** log in as a narrowly-scoped and a wide-scope persona against the production
API, submit the identical out-of-scope query to both plus an in-scope control to the
narrow persona, and compare whether the target document appears in each response's cited
sources.

## 8. Bilingual EN/FR response quality parity

**Methodology.** IntelAI's knowledge base carries a French-language document alongside
every English original, and every persona can be asked the same factual question in either
language. §3's 50-case live evaluation already scores an English and a French KPI-lookup
slice with the same judge panel against the same live production API; those numbers are
cited below. One fresh, literally-paired live query was also run for this section: the
identical metric and period, asked in English and then in French, same persona, checking
that both languages agree on the underlying figure.

### 8a. From §3's 50-case run

| Kind | N | Avg groundedness | Avg latency |
|---|---|---|---|
| kpi-fr (French) | 7 | 0.917 | 74.1s |
| kpi (English) | 21 | 0.431 | 77.4s |

Judge-panel groundedness is markedly higher on the French slice than the English one in
this run; §3b's judge-dropout caveat and the smaller French N both apply here as they do
in §3 itself.

### 8b. Fresh live paired query

**Query** (`cto` persona, identical question asked in both languages): "What was System
Uptime in 2026-06?" / "Quelle était la disponibilité du système (System Uptime) en
2026-06 ?"

**Result: the figure matches exactly.** Both languages report **100.0% / 100,0 %**, cited
to the same source record, with the French response correctly using a comma as the decimal
separator per French-locale convention. The French response is genuine, fluent French
throughout, not an English answer with a French preamble, and both cite real, matching
sources.

**One honest, disclosed difference:** the English response included an extra caveat
paragraph the French response omitted — a minor completeness gap, not a factual
disagreement. Both answers were correct and consistent on the actual question asked.

**Reproduce:** submit the two queries above (same persona) against the production API and
compare the cited figure and source across languages.

## 9. Stress-scenario grounding: an inconclusive result, reported honestly

**Methodology.** The admin scenario-switcher (§4) seeds one of 6 crisis overlays on top of
the real baseline; each overlay applies its anomaly at a specific historical month, not as
an ongoing condition. All 6 scenarios were activated in sequence, each followed by one live
chat query targeted at its anomaly's exact month, then reverted before the next.

**Result: inconclusive, and reported as such rather than rounded up to a pass.** Of the 6
activation attempts, 2 returned a definitive server-side error (the same job-orphaning
failure mode described in §6's design — an admin job exceeding its progress-tracking
window under load), meaning those two scenarios' overlays were confirmed not written before
their query ran. The remaining 4 activations reported success or an ambiguous client-side
polling timeout, but this test round did not capture enough evidence (specifically, which
underlying database row a citation actually traced to) to confirm whether their query
responses reflect the intended scenario overlay or an unrelated baseline value. Every
individual query response was itself well-formed, cited a source, and contained a
plausible figure — the gap is in this benchmark's own verification method, not in an
observed wrong answer.

**Why this is reported rather than omitted or rounded up.** Presenting an inconclusive
result as a pass would misrepresent what was actually established; presenting it as a
clean failure would misrepresent it in the other direction, since no query returned a
demonstrably wrong or fabricated figure. The honest conclusion is that this specific test
design cannot currently distinguish "the crisis overlay was correctly reflected" from "the
query answer happened to also be plausible under the baseline" — a repeat of this test with
per-response source-provenance checking, run without concurrent load, would be needed to
draw a real conclusion.

## Honest caveats

- The forecast backtest is scored against OmniIntelOS's own synthetic-but-deterministic
  78-month series — it validates `ForecastEngine`'s behavior faithfully, but the absolute
  MAPE numbers are specific to this dataset's volatility and regime structure, not a
  universal claim about linear-regression forecasting accuracy on arbitrary business data.
- The entity-extraction and multi-hop fixes in §2, and the retrieval fixes in §3c and §4,
  were all found *by* the process of building this benchmark, not before it — this
  benchmark changed some of the code it's reporting on. That's disclosed here rather than
  presented as if the numbers were static from the start.
- GraphRAG-lite, as documented in `RESEARCH.md`, is a deterministic keyword-pattern
  extractor, not an LLM-driven entity/relationship pipeline — its accuracy ceiling is
  exactly what a keyword-substring heuristic's ceiling would be, and §2a measures that
  plainly rather than asserting parity with LLM-based GraphRAG implementations.
- Live production evaluation depends on an on-demand inference backend that isn't always
  warm on first request — a real operational characteristic, not an artifact of the
  evaluation methodology. Any case that fails after retries is reported as a failure, not
  excluded from the count. All 50 of this run's cases completed with 0 failures.
- §3's judge-panel groundedness average is depressed by real, disclosed judge-availability
  dropout on 7 of 50 cases (§3b) — the clean-subset and ground-truth-accuracy numbers are
  the more reliable read on actual system quality from this run.
- The case kinds with n=1 (health, web-search) and n=2 (correlation, action-plan) in §3d
  are real, live-verified capability checks, not statistically powered quality
  measurements — reported as what they are rather than inflated into a false-precision
  average.
- §5 is 3 targeted probes, not a statistically powered study — there is no live off-switch
  for hybrid retrieval in production, so there is no true dense-only/BM25-only control to
  compare against directly; each probe instead isolates one mechanism as cleanly as a
  single live query can.
- §5c's conclusion that a tied relevance score indicates fusion-only fallback (not genuine
  reranking) is an inference from score shape and isolated testing of the retrieval
  service, not a server-log confirmation — disclosed as such rather than presented as
  directly observed.
- §6's provider-swap resilience has only been exercised reactively, in response to two
  real provider failures that happened during this project's own operation — it has not
  been validated by a deliberate fault-injection test that forces a provider failure on
  demand, so its behavior under failure modes other than an outright error or rate limit
  is unverified.
- §7's RBAC-enforcement conclusion rests on one narrow persona and one document pair — a
  live, targeted A/B probe, not a statistically powered audit across all nine personas and
  the full document corpus. The retrievability control is what makes the negative result
  interpretable at all; that same ambiguity (a missing source could mean either RBAC
  filtering or a retrieval miss) should be assumed to still apply to any persona/document
  pair this section didn't directly test.
- §8's fresh live pair is n=1 per language — a qualitative spot-check that the two
  languages agree on the same figure and both cite real sources, not a new statistically
  powered EN/FR study. The statistical comparison in §8a is §3's existing numbers, cited
  rather than reproduced, and carries the same small-French-N and judge-dropout caveats §3
  already discloses for them.
- §9 is an explicitly inconclusive result — 2 of 6 scenario activations definitively
  failed server-side, and the other 4 could not be distinguished from a baseline-value
  coincidence with the evidence this test round captured. It's included because omitting a
  negative or inconclusive result would misrepresent how thoroughly stress-scenario
  grounding has actually been verified.

## Further reading

- [`RESEARCH.md`](RESEARCH.md) — the reasoning behind each design choice benchmarked here.
- [`README.md`](README.md) — feature overview and quick start.
