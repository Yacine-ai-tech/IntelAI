# Persona-Routed RAG: Role-Based Data Scoping for Production AI Assistants

> **DRAFT (2026) — publish 2027.** ~1,800 words. Audience: senior engineers / CTOs
> evaluating production RAG. Grounded in IntelAI (github.com/Yacine-ai-tech/IntelAI).

## TL;DR
Most "AI copilot" demos give every user the same assistant over the same data. In a real
company that's both wrong and unsafe: a CFO and a CHRO should not get the same answer, the
same tone, or the same data. **Persona-routed RAG** runs one retrieval system through
different *role-conditioned prompts and data-access filters*. This post shows the pattern,
the failure modes it fixes, and how I measured it in a deployed 9-persona analytics copilot.

## The problem
A generic RAG assistant over company KPIs has three problems in production:
1. **Data leakage by default.** The retriever happily surfaces Finance numbers to an HR
   user because relevance is computed on text similarity, not authorization.
2. **One voice for everyone.** A board summary and an ops standup need different altitude,
   length, and framing. A single system prompt can't be all of them.
3. **Multi-hop blindness.** "How did Engineering headcount track Finance margin?" returns
   disjoint snippets because pure vector search has no notion of entities or relationships.

## The pattern: persona = prompt + data scope
A *persona* is a small, declarative object: a system prompt, a sampling temperature, and —
critically — a **data-access scope** (which business domains it may see). Routing is a pure
function of the user's role:

```python
from omnismart_personas import persona_for_role, scope_records, build_rag_prompt

persona = persona_for_role("cfo")          # scope: Finance, Growth
rows = scope_records(persona, all_kpi_rows) # drop out-of-scope domains BEFORE retrieval
prompt = build_rag_prompt(persona, query, [fmt(r) for r in rows])
```

The key move: **filter the corpus to the persona's scope before retrieval**, not after
generation. Authorization becomes a property of the retrieval set, so the model literally
cannot ground an answer in data the role shouldn't see. (I open-sourced the persona layer as
[`omnismart-personas`](https://pypi.org/project/omnismart-personas/) — zero-dependency, 9
personas: CEO, CFO, CTO, COO, CHRO, ESG, Risk, Analyst, Assistant.)

## Retrieval stack
On top of scoping, IntelAI uses a hybrid retriever:
- **Dense** (BGE-large-en-v1.5) + **sparse** (BM25), fused with **Reciprocal Rank Fusion**,
  then re-ranked with **BGE-reranker-v2-m3**. Opt-in via `USE_HYBRID_RETRIEVAL`.
- **GraphRAG-lite** for multi-hop queries: at ingest, each KPI record is decomposed into
  entities `{department, category, period, metric}`; at query time, if the query mentions
  ≥2 entities, an entity-overlap graph ranks records and those are injected into context
  (`USE_GRAPH_RAG`). This is the cheap 80% of GraphRAG without a full graph database.

## Measuring it (the part most demos skip)
A copilot that sounds confident but isn't grounded is a liability. I keep a small,
version-controlled eval set (`tests/rag_eval.jsonl`, 25 cases) and a runner (`make eval`)
that scores two things per query:
- **Answer recall**: did the response mention the expected terms?
- **Groundedness proxy**: are those terms supported by the *retrieved sources*?

The gate (borrowed from the prompt-eval discipline): if >20% of cases fall below their
groundedness threshold, fix before shipping. This turns "the chatbot feels worse" into a
number you can regress against in CI.

*(Insert table: per-persona recall/groundedness, vector-only vs hybrid vs +GraphRAG-lite.)*

## Failure modes it fixed
- **Cross-domain leakage** → eliminated by pre-retrieval scoping (CHRO can't surface Finance).
- **Multi-hop "disjoint snippets"** → GraphRAG-lite lifted groundedness on the 2 cross-domain
  queries in the eval set.
- **Tone mismatch** → per-persona temperature + prompt; the CFO answers are terse and
  numeric, the Assistant is exploratory.

## What I'd tell a team adopting this
1. Make authorization a property of the **retrieval set**, not a post-hoc filter.
2. Keep personas **declarative and tested** — a frozen dataclass with an explicit scope.
3. Ship an **eval gate** from day one; groundedness is the metric that matters.
4. Add GraphRAG-lite only where queries are genuinely multi-hop; don't pay for a graph DB
   until vector + entities stop being enough.

## Links
- Code: github.com/Yacine-ai-tech/IntelAI
- Package: `pip install omnismart-personas`
- Live demo: *(insert Railway URL)* · Loom: *(insert link)*

---
*Outline for the 2027 publish: add the eval results table, an architecture diagram, and a
short "limitations" section (no full graph reasoning; groundedness proxy is keyword-based).*
