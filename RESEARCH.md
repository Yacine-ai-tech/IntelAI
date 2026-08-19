# Research Background

This document explains the reasoning behind IntelAI's core retrieval, evaluation, graph
and forecasting design choices, and situates each one relative to the relevant 2023–2026
research and industry landscape. For the empirical numbers behind these claims — a real
backtest, a live-production RAG evaluation, and a live entity-coverage measurement — see
[`BENCHMARK.md`](BENCHMARK.md). This document is the "why"; that one is the "what we
measured."

IntelAI is a practical, applied platform. It draws on established ideas from the
information-retrieval, RAG-evaluation, access-control and time-series-forecasting
literature and applies them to persona-scoped enterprise analytics — it does not claim to
introduce novel methodology of its own.

## Why hybrid retrieval (dense + BM25 + reciprocal rank fusion), not dense alone

A dense embedding retriever finds semantically similar text well but is a known poor fit
for exact-match lookups — a metric name, a period string like `2023-02`, an entity ID —
where a sparse lexical method like BM25 (Robertson & Zaragoza, *The Probabilistic
Relevance Framework: BM25 and Beyond*, 2009) is often more reliable precisely because it
scores exact term overlap rather than learned similarity. The reverse also holds: BM25
misses a paraphrase with no shared vocabulary that a dense retriever finds immediately.
Combining both and fusing the two rank lists with Reciprocal Rank Fusion — RRF, `score =
Σ 1/(k + rank)` (Cormack, Clarke & Buettcher, *Reciprocal Rank Fusion Outperforms
Condorcet and Individual Rank Learning Methods*, SIGIR 2009) — is a long-established,
low-variance way to combine heterogeneous rankers without learning a weighting, which is
why it's the fusion method used here (`src/services/hybrid_retrieval.py`) rather than a
learned re-ranking of the two lists.

A cross-encoder reranker is applied on top of the fused candidates for the same reason
it's standard practice across retrieval pipelines in this period: a bi-encoder (embedding
similarity) and a cross-encoder (query and candidate encoded jointly) trade off recall for
precision differently, and running a cheap bi-encoder first to narrow candidates, then a
more expensive cross-encoder to re-order the shortlist, is the standard two-stage pattern
in both academic IR and production RAG deployments as of 2026.

## Grounding numeric conversions via glossary, not model recall

An LLM asked to convert a dollar figure into another currency will produce a plausible-
looking number from its own training-data recall of typical exchange rates — fine for a
rough approximation, wrong for a system whose whole premise is citing the dataset's own
recorded figures. OmniIntelOS is modelled as headquartered in Niamey, Niger, in the West
African CFA franc (XOF) zone, and keeps its statutory books in XOF while reporting
externally in USD (`data/glossary.py`'s `"XOF Exchange Rate"` entry) — so every USD figure
elsewhere in the corpus is itself a conversion of an XOF-native transaction, at a specific,
recorded internal rate (1 USD ≈ 607.37 XOF, derived from the real, fixed BCEAO/Eurozone
peg of 655.957 XOF/EUR and the dataset's own 1.08 USD/EUR planning assumption). A model
asked "what's that in FCFA" has no way to know this specific dataset uses that specific
rate rather than whatever floating market rate it last saw in training — it would
hallucinate a plausible-sounding but wrong number, silently disagreeing with the dataset's
own recorded XOF rows.

The fix follows the same pattern as every other domain term in this glossary: the
conversion rate is written down once, as a seeded, cited knowledge-base entry the RAG
pipeline retrieves and grounds against, rather than left to model recall. This is a small
instance of a general principle this codebase applies wherever a claim is checkable
against the dataset's own facts rather than general knowledge — the retrieval layer's
job is to make the checkable fact available, not to trust the model to already know it.

## Why an external, dogfooded evaluator rather than an in-process one

IntelAI does not implement its own groundedness scoring. Every live chat interaction is
fire-and-forget logged to a RAGeval-compatible evaluation endpoint
(`omnismart_chatbot.py::_dogfood_to_rageval`), and the same multi-judge-consensus
methodology — at least two independently configured LLM judges scoring every answer, no
single-judge fallback, disagreement (stdev) surfaced rather than hidden — is what
`scripts/evaluate_*.py` uses for the offline benchmark runs in this repo. The reasoning
for that design (verbosity bias, self-preference bias, and position bias as documented
failure modes of single-judge LLM-as-judge scoring, and why a panel mitigates but does not
eliminate that noise) is the same reasoning laid out in RAGeval's own
[RESEARCH.md](https://github.com/Yacine-ai-tech/RAGeval/blob/main/RESEARCH.md) — this
project treats evaluation as someone else's well-scoped job rather than reimplementing it,
which is also why `requirements-dev.txt` notes IntelAI has no *import-time* dependency on
the `rageval` package; it's opt-in for anyone running the benchmark scripts locally.

## Persona/RBAC-scoped retrieval: a distinctive angle, honestly scoped

Every chat request carries the caller's role, and retrieval — not just the UI — is scoped
to that role's granted data categories (`get_user_data_categories`, enforced in
`src/api/server.py` before any KPI row or document reaches the model, not filtered
after the fact). The underlying idea — checking retrieved content against an
authorization boundary before it becomes part of a generated answer — borrows from
role-based access control (RBAC), a decades-old access-control model (Ferraiolo & Kuhn,
*Role-Based Access Control*, 1992) applied here to what an LLM is allowed to *see* during
retrieval, not only to what a data store returns.

This needs the same honest scoping RAGeval gives its own persona-scope detector: the
general-purpose RAG-evaluation frameworks and observability platforms most commonly cited
in 2026 (RAGAS, ARES, TruLens, Phoenix, Langfuse) do not ship an authorization-scoped
retrieval layer as a first-class concept — retrieval-time RBAC is IntelAI's own design
choice, not a reimplementation of prior art. This project's own security review found and
closed a cross-domain leak where one endpoint returned every domain's data regardless of
role while a sibling endpoint scoped correctly — direct evidence that retrieval-time
enforcement, applied consistently everywhere data leaves the system, not UI-level hiding,
is the thing that actually has to be correct. §7 of `BENCHMARK.md` verifies this
enforcement directly with a live test.

## GraphRAG-lite: a real scoping distinction worth stating plainly

`src/services/graph_retrieval.py` and `src/services/entity_extractor.py` are named after,
and inspired by, the graph-augmented-retrieval line of work popularized by Microsoft's
GraphRAG (Edge et al., *From Local to Global: A Graph RAG Approach to Query-Focused
Summarization*, 2024) — using entity relationships to answer multi-hop questions a
single-chunk retriever handles poorly. It is important to be precise about what IntelAI's
implementation actually is: a lightweight, deterministic, keyword-pattern entity extractor
(`EntityExtractor._infer_department`, matching known substrings against a category/metric
name) feeding a co-occurrence-ranked graph traversal, not an LLM-driven entity/relationship
extraction and community-summarization pipeline like the reference GraphRAG
implementation. It is explainable and cheap to run at ingestion time; it is not a learned
or LLM-graded extractor, and its accuracy is exactly what a keyword-substring heuristic's
accuracy would be — measured directly in [`BENCHMARK.md`](BENCHMARK.md) rather than
asserted. Calling it "GraphRAG-lite" throughout this codebase is meant as an honest
qualifier, not a marketing shorthand for the full technique.

## Forecasting: classical statistics, not a novel model, measured honestly

`src/services/forecasting.py::ForecastEngine` fits ordinary least-squares linear
regression per metric and reports a confidence interval from the residual standard
deviation — deliberately the simplest model that produces a defensible interval, chosen
for the same reason many production BI tools default to it: it is CPU-only, needs no
training data beyond the series itself, is trivially explainable to a non-technical
stakeholder ("the trend continues at its recent slope"), and its failure mode is
predictable rather than mysterious. That failure mode is real and is measured directly
rather than hidden: a linear model systematically **under-forecasts** a metric during a
genuine acceleration in growth rate, because by construction it extrapolates the recent
*average* slope forward, not a changing one. [`BENCHMARK.md`](BENCHMARK.md) reports exactly
this — the worst individual forecast errors in a 378-forecast backtest cluster entirely in
the accelerating-growth tail of the test period, a textbook, well-understood limitation of
linear extrapolation (see e.g. Hyndman & Athanasopoulos, *Forecasting: Principles and
Practice*, 3rd ed., 2021, on trend-model failure under regime change) rather than an
unexplained anomaly.

## Where IntelAI sits in the landscape

IntelAI is one of a large and fast-growing category of "enterprise analytics copilot"
tools as of 2026 — LLM-based chat interfaces over structured business metrics and
unstructured documents, typically combining retrieval-augmented generation with
role-based access. It does not attempt to be a general-purpose RAG framework (that is
RAGAS's, ARES's and TruLens's job, referenced above) or a general LLMOps observability
platform (that is RAGeval's own stated scope, alongside Phoenix and Langfuse) — those are
components IntelAI's evaluation and monitoring approach deliberately delegates to,
documented above, rather than reimplements. Its own distinctive combination is: hybrid
KPI-plus-document retrieval, retrieval-time RBAC enforcement across nine personas, a
lightweight entity graph for cross-domain questions, and classical, explainable
forecasting — each chosen for being well-understood and auditable over being
state-of-the-art, which is a defensible tradeoff for a system whose answers inform real
business decisions and need to be explainable when they're wrong, not just accurate when
they're right.

## Future directions

Three extensions follow from what's already implemented and measured, not from a
departure from it:

- **Learned entity extraction.** The keyword-pattern approach in `entity_extractor.py` is
  cheap and explainable but has a measured ceiling (see `BENCHMARK.md`) — a small
  classifier trained on the KPI corpus's own category labels (which already exist as
  ground truth for every row) would very likely outperform substring matching on the
  cases where a metric name spans two domains' vocabulary, without giving up the
  underlying graph-traversal architecture.
- **Regime-aware forecasting.** The measured under-forecasting during accelerating growth
  motivates testing a model that can represent a change in trend rather than only a fixed
  one — a piecewise-linear or Bayesian structural time-series approach — evaluated
  against the exact same backtest methodology already in `BENCHMARK.md`, so any claimed
  improvement is measured the same way the current baseline is, not a different metric
  that isn't directly comparable.
- **Multi-hop graph evaluation with labels.** The graph-retrieval path is exercised by
  the live RAG evaluation today but not scored as its own axis — a small labeled set of
  genuinely multi-hop questions (spanning two or more domains, only answerable by
  traversing entity relationships rather than a single chunk) would let cross-domain
  retrieval quality be reported with the same rigor as the groundedness numbers in
  `BENCHMARK.md`, rather than folded into the general RAG score.

None of these is committed or scheduled here — they're the honest next steps that follow
from being specific about what today's numbers do and don't establish.

## Further reading

- [`BENCHMARK.md`](BENCHMARK.md) — the actual live-production RAG evaluation, the
  forecast backtest, the entity-extraction coverage measurement, and honest caveats about
  what those numbers do and don't establish.
- [`README.md`](README.md) — feature overview and quick start.
- [RAGeval's RESEARCH.md](https://github.com/Yacine-ai-tech/RAGeval/blob/main/RESEARCH.md) —
  the multi-judge-consensus reasoning IntelAI's own evaluation methodology relies on.
