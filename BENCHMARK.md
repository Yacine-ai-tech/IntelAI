# Benchmark Results

This document reports measured results against IntelAI's live deployment and its
OmniIntelOS demo dataset. For the reasoning behind each component's design, see
[`RESEARCH.md`](RESEARCH.md); this document reports what was measured. Every number below
comes from a script in `scripts/` or a documented analysis run against the live database and
production API, so the methodology is reproducible. Limitations are reported alongside
results rather than omitted.

## 1. Forecasting: Out-of-Sample Backtest

**Methodology.** `ForecastEngine.time_series_forecast()` (`src/services/forecasting.py`)
selects, per series, whichever of three candidate models — ordinary least-squares linear
regression, Holt's linear trend, or a degree-2 polynomial — backtests best on that series'
own recent history, rather than fitting a single model class uniformly. Every possible
3-month-ahead forecast origin in a 78-month synthetic series was backtested: fit on history up
to the origin month, forecast 3 months ahead, and compare to the actual value at the target
month. Results are also split by whether the forecast window crosses one of the dataset's 12
defined regime/phase transitions (for example, a demand surge).

**Result: 444 forecasts scored across 6 metrics.**

| Metric | Mean APE | Median APE | N |
|---|---|---|---|
| System Uptime | 0.33% | 0.17% | 74 |
| Gross Margin | 9.88% | 8.78% | 74 |
| Customers | 3.71% | 3.30% | 74 |
| Headcount | 1.74% | 1.72% | 74 |
| Revenue | 6.61% | 6.01% | 74 |
| ARR | 5.56% | 5.04% | 74 |

**Overall: mean APE 4.64%, median APE 2.77%.**

| Forecast window | Mean APE | N |
|---|---|---|
| Stays within one regime | 4.45% | 252 |
| Crosses a regime transition | 4.89% | 192 |

**Ablation: model auto-selection versus a single always-linear fit.** Forcing every series
through a single ordinary-least-squares linear fit, rather than the per-series model
selection described above, raises overall mean APE to 12.48% (median 9.90%) on the same
backtest. The largest gains from auto-selection concentrate in windows where a series
accelerates rather than trends linearly — for example, a five-forecast cluster of Revenue
predictions spanning origins November 2025 through March 2026 improves from a 45.2–49.1% APE
range under the linear-only fit to 3.75–9.95% under auto-selection, because a Holt's-trend or
polynomial fit tracks genuine acceleration instead of projecting the recent average slope
forward.

**Remaining limitation.** Gross Margin carries the largest individual forecast errors under
the current model (25–34% APE on a handful of forecasts, for example predicted 85.29% versus
actual 63.61% for one origin/target pair) — a specific, unresolved weak spot distinct from
the general accuracy reported above.

**Reproduce:** the backtest iterates `ForecastEngine.time_series_forecast()` over every valid
3-month-ahead origin in the seeded dataset's known series and compares against the known
future value.

## 2. GraphRAG-Lite: Entity-Extraction Coverage and Multi-Hop Retrieval

### 2a. Department-Entity Coverage by Domain

**Methodology.** `EntityExtractor.extract_entities()` (`src/services/entity_extractor.py`)
was run over every row of the live `kpi_metrics` table (7,878 rows across 7 domains) and
checked for whether a `department` entity was successfully inferred.

**Result:**

| Domain | Rows | Department inferred | Coverage |
|---|---|---|---|
| Finance | 1,872 | 1,872 | 100.0% |
| Growth | 1,248 | 1,248 | 100.0% |
| People | 1,092 | 1,092 | 100.0% |
| IT | 1,092 | 1,092 | 100.0% |
| Operations | 936 | 936 | 100.0% |
| ESG | 936 | 936 | 100.0% |
| Logistics | 702 | 702 | 100.0% |
| **Total** | **7,878** | **7,878** | **100.0%** |

**Ablation: category-field lookup and weighted vote versus a first-match keyword scan.** An
earlier department-inference approach — a first-match keyword-substring scan over
`metric_name` alone — scored 100% coverage on five of seven domains but only 91.7% (ESG) and
71.4% (IT) on the remaining two, for an overall 95.0% (7,488/7,878), because metric-name
vocabulary shared across domains (for example, "audit compliance" appearing in both ESG and
Finance/Operations contexts) could resolve to the wrong domain under a first-match rule. The
current approach resolves this in two tiers: trusting the already-known `category` field on
structured KPI records directly, and falling back to a weighted vote across all domains'
keyword lists (by total matched-term count) rather than a first match, so shared vocabulary
resolves to whichever domain has the strongest textual evidence.

### 2b. Multi-Hop Query Retrieval

**Methodology.** Eight hand-labeled two-domain queries (for example, "compare headcount
growth against finance margin") were run through the live retrieval path
(`graph_kpi_context()` → `_rank_from_persisted_entities()`) against the live `kpi_entities`
table, and each result set was checked for whether it contained at least one record from both
named departments.

**Result: 8 of 8 queries return a result set spanning both named departments.**

This is the more significant of the two knowledge-graph measurements: entity coverage
measures whether individual records are tagged correctly, while this measures whether the
graph retrieval path a multi-hop question actually depends on functions as intended.

## 3. Live Production RAG Evaluation

**Methodology.** `scripts/evaluate_production_live.py` submits 50 evaluation cases
(`tests/rag_eval.jsonl`, generated by `scripts/build_rag_eval_set.py`, which verifies each
case against the live database before writing it) to the deployed production API. Every
response is scored using RAGeval's multi-judge-consensus evaluator — the same evaluation path
production traffic is scored with. Five metrics are computed per case: retrieval relevance,
groundedness (judge consensus), faithfulness, an overall-quality composite, and cost/latency.

The 50 cases span the corpus's full timeline: 28 test KPI recall, 12 test document/audio/
PPTX/XLSX retrieval, 3 test glossary lookups, and 6 test capabilities beyond retrieval —
cross-metric correlation, health/risk-status synthesis, action-plan generation, and live web
search (§3c).

**Result: 50/50 cases completed, 0 crashes.**

| Metric | Value |
|---|---|
| Ground-truth accuracy (objective, judge-independent) | **71.4%** (20/28 applicable cases) |
| Avg. groundedness (judge panel) | 0.599 |
| Avg. overall quality | 0.479 |
| Avg. latency | 74.6 s/case |

Ground-truth accuracy checks whether the answer contains the actual recorded database value,
independent of any LLM judge, and is the more direct measure of retrieval correctness. The
judge-panel groundedness figure (0.599) reflects the full panel's score once all judges are
reliably available (§3b); a subset of cases scored during a period of reduced judge
availability is excluded from this figure and reported separately below.

### 3a. By Case Kind

| Kind | N | Avg. groundedness | Avg. latency |
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

### 3a-v2. Regression: Retrieval Returning No Context on a Subset of Queries

A later run of the same 50-case set, using symmetric English/French templates (§7),
measured ground-truth accuracy at **46.4%** (13/28 applicable cases) — a real regression
from the 71.4% reported above, not a difference attributable to the template change itself.
Judge-based groundedness could not be measured on this run at all (0 of 50 cases judged):
three of four configured judges route through a proxy account that is out of credits, and
the fourth (Groq) hit its own daily token-rate limit before the run completed.

**Root cause, confirmed.** Of the 15 incorrect cases, 13 show zero retrieved context —
retrieval returned nothing at all, not a wrong or lower-quality match. This occurred when
`EMBEDDING_PROVIDER=remote` and `RERANK_PROVIDER=remote` pointed to a decommissioned remote host
rather than the active server instance. Retrieval does not crash — the failure is caught and
logged as a quality warning, per `hybrid_retrieval.py`'s design — falling back to BM25-only
keyword search without dense embeddings or neural reranking.

The production architecture deploys self-hosted BGE-M3 (`BAAI/bge-m3` dense + sparse embedding)
and BGE-Reranker-v2-M3 (`BAAI/bge-reranker-v2-m3`) directly on the server instance
(`EMBEDDING_PROVIDER=local`, `RERANK_PROVIDER=local`), ensuring full 1024-dimensional semantic
retrieval and neural reranking without external third-party API dependencies.

The kpi/kpi-fr groundedness gap in the table above reflects a difference in question-template
design between the English and French evaluation cases, not a difference in retrieval
quality by language — see §7 for the isolated, template-matched comparison and the mechanism
behind this table's gap.

### 3b. Judge-Panel Availability Under Concurrent Load

On 7 of the 50 cases, the judge panel and the reasoning-tier personas being judged
temporarily competed for the same rate-limited upstream capacity, leaving 2 of 4 configured
judges intermittently unavailable and lowering those 7 cases' groundedness score to 0.407.
Re-scoring the same 7 cases with isolated judge execution (no concurrent competition)
recovers a groundedness score of 0.659, confirming the low score reflected judge
availability rather than the retrieval pipeline.

| Evaluation condition | Avg. groundedness | N |
|---|---|---|
| Full judge panel available | 0.599 | 43 |
| Reduced judge availability (2 of 4 responded) | 0.407 | 7 |
| Isolated re-scoring of the same 7 cases | 0.659 | 7 |

This affects the judge-panel groundedness figure only; ground-truth accuracy, which checks
answer content directly rather than a judge's opinion of it, is unaffected.

### 3c. Beyond Retrieval: Correlation, Health Status, Action Plans, and Web Search

Six of the 50 cases exercise capabilities beyond looking up a stored value:

- **Correlation** (CTO persona): asked how Deployment Frequency correlates with Change
  Failure Rate — the response reasoned across both metrics rather than answering one and
  ignoring the other.
- **Health status** (Risk persona): asked for a compliance health assessment from Audit
  Compliance Score and Privacy Incident Count — produced a synthesized status rather than a
  single number.
- **Action plans** (COO, CHRO personas): asked for a recommended plan given Stockout Rate and
  On-Time Delivery Rate, and separately Employee Turnover and Absenteeism — both produced
  concrete, figure-grounded recommendations.
- **Web search** (ESG persona): asked how the company's Renewable Energy Ratio compares to
  industry best practices, a question the internal corpus cannot answer alone. The response
  cited four external sources (Deloitte, SEIA, the Business Council for Sustainable Energy,
  and the U.S. EIA), blended with internal data.

Groundedness on this slice (n = 1–2 per kind) is directionally informative rather than
statistically powered.

### 3d. Persona-Scope Flags

Two cases (both action-plan) were flagged `PERSONA_SCOPE_VIOLATION` by RAGeval's scorer. This
flag is a prose-level heuristic — it scans the answer's sentences for vocabulary associated
with a domain outside the persona's declared scope — not a check of what data the backend
retrieved. A COO's action plan naturally mentions revenue or customer impact while reasoning
about a logistics fix; that is legitimate cross-functional business reasoning, not a data
leak. The backend's actual RBAC enforcement, which drops any retrieved document or KPI
outside the persona's domain before it reaches the model, is a separate guarantee tested
directly in §6.

**Reproduce:** `python scripts/build_rag_eval_set.py && python scripts/evaluate_production_live.py`.
Full per-case results: `eval/RAGEVAL_PRODUCTION_LIVE_REPORT.json`.

## 4. Hybrid Retrieval: Three Targeted Live Probes

**Methodology.** Hybrid retrieval (dense embedding search and BM25, fused via Reciprocal Rank
Fusion, then optionally reranked by a cross-encoder) is always on in production. Three live
queries were designed to each isolate a different mechanism hybrid retrieval provides over
either half alone, submitted via the production chat API and judged against ground truth.
Latencies are the API's own server-side measurement. The `sources` array mixes two provenance
types — live KPI-snapshot cards, which carry a fixed relevance of 1.0, and retrieved
knowledge/glossary documents, which carry the real fused/reranked relevance score; only the
second group is evidence about hybrid retrieval's behavior.

### 4a. Lexical Exact-Match (BM25-Favorable)

**Query** (ESG persona): "How did Carbon Intensity per Revenue stand in 2025-07, and where
does that figure come from?" — the exact metric name as it appears in the corpus.

**Result:** correct on the first attempt — 129.57 tCO₂e/USD million, matching the database's
recorded value to the reported precision. Server latency: 52.5s.

| Source | Type | Relevance |
|---|---|---|
| `esg_2025_en.md` | knowledge | 1.0 |
| `esg_2025_fr.md` | knowledge | 0.984 |
| `esg_2024_en.md` | knowledge | 0.961 |

The answer cited the correct English 2025 document over the French duplicate of the same
document and the prior year's document, with distinct, monotonically decreasing relevance
scores across the three candidates.

### 4b. Semantic Paraphrase, No Shared Vocabulary (Dense-Favorable)

**Query** (CHRO persona): "Roughly what share of our staff left the company in the twelve
months ending around May 2022?" — shares no vocabulary with the corpus's metric name, "Annual
Employee Turnover."

**Result:** "Approximately 22% of the workforce left the company over the twelve-month period
ending around May 2022 (annual employee turnover reported as 22.22% in the September 2022
review)" — cited to a real corporate-minutes document, genuinely grounded. Server latency:
53.2s. A separate ground-truth case asks for this metric at the exact period 2022-05, where
the true monthly value is 29.18% — a different, more precise fact than what a September 2022
narrative summary reports in looser terms. This is a real precision tradeoff between a vague
natural-language period reference and an exact metric-and-period query, not a hallucination:
every number in the answer traces to a real, cited source.

### 4c. Rerank Under Real Ambiguity

**Query** (CEO persona, full seven-domain scope): "What is our turnover situation right now,
both from a staffing perspective and a warehouse-stock perspective?" — overloads the word
"turnover" across two differently-scaled metrics (employee turnover and inventory turnover) to
force disambiguation that lexical matching alone cannot resolve.

**Result:** the response correctly separated the two, with both employee turnover and
inventory turnover identified, cited, and reported with figures and historical comparisons.
Server latency: 69.8s.

**Summary:**

| Probe | Mechanism tested | Server latency | Outcome |
|---|---|---|---|
| §4a lexical exact-match | BM25 half | 52.5s | Correct value, correct document, distinct relevance scores |
| §4b semantic paraphrase | Dense half | 53.2s | Grounded, zero-vocabulary-overlap match; resolved to a related but less precise fact than the exact database row |
| §4c rerank under ambiguity | Cross-encoder stage | 69.8s | Correct domain disambiguation |

**Reproduce:** submit the three queries and personas above against the production API and
inspect the `sources` array's relevance field per source type.

## 5. Multi-Provider LLM Routing

**Methodology.** Every LLM call resolves through one function that maps a model tier
(default, reasoning, judge, and an as-yet-unused local tier) to a provider/model string via an
independently configurable environment variable. Reasoning-tier personas (CEO, CFO, CTO,
Risk) and default-tier personas resolve independently; a lightweight judge-tier call gates
whether a live web search is triggered for a given query.

**Result.** Each active tier is swappable independently via configuration, with no code
change required to change which provider or model serves a given tier, and no tier's routing
affecting the others.

## 6. Persona/RBAC-Scoped Retrieval Enforcement

**Methodology.** Every chat request carries the caller's persona, and retrieval — not only the
UI — is scoped to that persona's granted data domains before any document reaches the model.
This section verifies that enforcement with a live A/B test rather than inferring it from a
document's absence in one response, which is inherently ambiguous on its own (a missing
source could mean RBAC filtered it, or simply that retrieval did not rank it for that query).

**Test design.** A narrowly-scoped persona (CFO, granted Finance and Growth only — the most
restrictive of the nine defined personas) and a wide-scope persona (CEO, granted all seven
domains) were each asked the identical question about a specific out-of-scope annual
document. The wide-scope persona's response establishes whether the document is real,
indexed, and top-ranked for that query at all — the control that makes the narrow persona's
result interpretable.

| Probe | Persona | Domain access | Query | Target document in results? |
|---|---|---|---|---|
| 1 | CFO | Finance, Growth | Out-of-scope (ESG) annual document | Absent |
| 2 | CEO | All 7 domains | Identical query | Present, top relevance |
| 3 | CFO | Finance, Growth | In-scope (Finance) annual document | Present, top relevance |

**Result.** The out-of-scope document was completely absent from the narrow persona's
response (Probe 1) while being the top-ranked, correctly cited result for the wide-scope
persona asking the identical question (Probe 2) — confirming the document is real, indexed,
and retrievable, and that its absence for the narrow persona is attributable to RBAC scoping
rather than a retrieval miss. An in-scope control query for the narrow persona (Probe 3)
returned and correctly cited its target document, confirming the scoping does not over-block
legitimate in-scope access.

**Reproduce:** log in as a narrowly-scoped and a wide-scope persona against the production
API, submit the identical out-of-scope query to both plus an in-scope control to the narrow
persona, and compare whether the target document appears in each response's cited sources.

## 7. Bilingual EN/FR Response Quality Parity

**Methodology.** IntelAI's knowledge base carries a French-language document alongside every
English original, and every persona can be asked the same factual question in either
language. §3's 50-case evaluation scores an English and a French KPI-lookup slice with the
same judge panel against the same production API. A further, literally paired live query was
run for this section: the identical metric and period, asked in English and then in French,
with the same persona.

### 7a. From §3's 50-Case Run

| Kind | N | Avg. groundedness | Avg. latency |
|---|---|---|---|
| kpi-fr (French) | 7 | 0.917 | 74.1s |
| kpi (English) | 21 | 0.431 | 77.4s |

This gap reflects a difference in question-template design rather than retrieval quality: the
English KPI templates in this evaluation set include a provenance sub-question ("...and where
does that figure come from?") that the French templates do not, so the judge panel scores
otherwise-correct English answers as only partially grounded when they state the value without
an explicit source-attribution sentence. The French templates ask only for the value itself, a
narrower, more consistently gradeable question. §7b isolates the two languages on a
template-matched query to control for this.

### 7b. Template-Matched Paired Query

**Query** (CTO persona, identical question in both languages): "What was System Uptime in
2026-06?" / "Quelle était la disponibilité du système (System Uptime) en 2026-06?"

**Result: the figure matches exactly.** Both languages report 100.0% / 100,0 %, cited to the
same source record, with the French response correctly using a comma as the decimal separator
per French-locale convention. The French response is fluent and both responses cite matching
sources.

**Reproduce:** submit the two queries above (same persona) against the production API and
compare the cited figure and source across languages.

## 8. Grounding Under Scenario-Switched (Crisis) Conditions

**Methodology.** The admin scenario switcher overlays one of six modeled crisis scenarios on
top of the baseline dataset, each anomaly applied at a specific historical month. Each
scenario was activated, its target metric confirmed present in the database at the expected
value for the anomaly month, then queried via the live chat API asking about that exact metric
and month, with the cited value compared against the database row.

**Result: 3 of 3 re-tested scenarios correctly grounded the historical crisis value.**

| Scenario | Target metric/period | DB value | Chat-reported value | Match |
|---|---|---|---|---|
| operational_meltdown | On-time Delivery, 2020-04 | 72.31% | 72.31% | Yes |
| talent_crisis | Turnover Rate, 2020-06 | 26.17% | 26.17% | Yes |
| cybersecurity_breach | Security Incidents, 2020-03 | 34.7 | 34.7 | Yes |

Each response cited a source document specific to the queried historical month, matching the
database value exactly. The remaining three scenarios (declining_financial, high_churn_crisis,
esg_compliance_failure) share the identical retrieval code path and were not independently
re-verified in this pass.

**Reproduce:** activate a scenario via `POST /api/v1/admin/scenario/async`, query the target
metric and month via chat, and compare the cited value and source to the database row tagged
for that scenario.

## Limitations

- The forecast backtest is scored against a synthetic-but-deterministic 78-month series; it
  validates `ForecastEngine`'s behavior faithfully, but the absolute error figures are
  specific to this dataset's volatility and regime structure, not a universal claim about
  forecasting accuracy on arbitrary business data.
- GraphRAG-lite, as documented in `RESEARCH.md`, is a deterministic keyword-pattern
  extractor, not an LLM-driven entity/relationship pipeline; its accuracy ceiling is that of a
  keyword-substring heuristic.
- Live production evaluation depends on an on-demand inference backend that is not always warm
  on first request. Any case failing after retries is reported as a failure, not excluded.
- The judge-panel groundedness figure in §3 is affected by real judge-availability variance on
  a subset of cases (§3b); ground-truth accuracy is the more reliable measure of system
  quality from this run.
- Case kinds with n = 1 (health, web-search) or n = 2 (correlation, action-plan) in §3c are
  live-verified capability checks, not statistically powered measurements.
- §4 comprises three targeted probes, not a statistically powered study; there is no live
  off-switch for hybrid retrieval in production, so no true dense-only or BM25-only control
  exists to compare against directly.
- §5's provider-routing independence has been exercised under real operating conditions but
  not validated by a deliberate fault-injection test forcing a provider failure on demand.
- §6's RBAC-enforcement conclusion rests on one narrow persona and one document pair — a
  targeted A/B probe, not a statistically powered audit across all nine personas and the full
  document corpus.
- §7's paired query is n = 1 per language, a qualitative check rather than a statistically
  powered study; the quantitative comparison in §7a is §3's existing data, cited rather than
  reproduced independently.
- §8's result is drawn from three of six scenarios tested directly; the other three use the
  identical retrieval code path but were not independently re-verified in this pass.

## Further Reading

- [`RESEARCH.md`](RESEARCH.md) — the reasoning behind each design choice benchmarked here
- [`README.md`](README.md) — feature overview and quick start
