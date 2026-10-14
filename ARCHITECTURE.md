# IntelAI Architecture

How IntelAI turns a question into a grounded, cited answer. This page complements
[`README.md`](README.md) (what it is and how to run it), [`RESEARCH.md`](RESEARCH.md) (the
retrieval and governance reasoning) and [`BENCHMARK.md`](BENCHMARK.md) (measured results). An
interactive version is in the application under **Architecture**.

## 1. System overview

```
 question ─▶ persona (role-scoped) ─▶ plan ─┬─▶ internal retrieval: KPIs · documents · glossary
                                            └─▶ live web search (when the question needs it)
                                   merge ─▶ prompt ─▶ model (streamed) ─▶ answer with sources
```

Around the copilot sit the analytics modules (financial, growth, people, IT, logistics, operations,
ESG, risk), forecasting with Monte Carlo intervals, anomaly detection, a glossary, a knowledge
graph, board reports, a data hub for CSV, documents, audio and webhooks, and administration.

## 2. Components

| Component | Role |
|---|---|
| Personas | nine role-scoped personas (CEO, CFO, CTO, COO, CHRO, ESG, Risk, Analyst, Assistant) with data-access scopes; the server maps each role to the personas it may use |
| Retrieval | dense embeddings + BM25 fused by reciprocal rank fusion; optional cross-encoder; GraphRAG-lite expansion |
| Web search | live search for external companies, people and current events; decided by rules in microseconds and run in parallel with retrieval |
| Model router | tiers (default, reasoning, judge, local), key rotation, fallback models, streaming |
| Session store | chat history with the sources of every answer |
| Data hub | ingestion of CSV, documents (through the document service), audio (through the speech service) and signed webhooks |
| Analytics | KPI queries, health, anomalies, forecasts, domain dashboards, reports |

## 3. One chat turn

1. **Understand**: detect the language, resolve the persona, decide (by rules) whether the web is
   needed. Small talk skips retrieval.
2. **Gather in parallel**: internal retrieval and, when planned, the web search start together, so
   the web adds no waiting time of its own. An explicit request ("search the web", "verify online")
   always waits for the results; an automatic search is cut off after a short budget rather than
   delaying the answer.
3. **Prompt**: a stable persona prefix, then the live data and the question. The prompt states what
   was found: web results present, a search that returned nothing relevant, or none needed.
4. **Generate**: tokens are streamed as the model produces them; a rate-limited key is parked and
   the next one is used immediately; a model that fails before producing text is replaced by the
   tier's fallback.
5. **Finish**: sources (knowledge base and web, listed separately) and the answer structure are
   returned and the turn is stored.

The interface shows these steps live (understanding, searching the knowledge base, searching the
web, writing), lists sources as soon as they are known, and reveals the answer progressively.

## 4. Retrieval

| Stage | Detail |
|---|---|
| Dense | multilingual embedding model; top-N by similarity |
| Lexical | BM25 over title-weighted text; top-N |
| Fusion | reciprocal rank fusion of the two lists |
| Language | same-language documents are preferred, other languages remain eligible |
| Cross-encoder | optional; skipped when dense and lexical agree on a clear leader |
| Progressive | the knowledge search shows the fused ranking at once and refines it when the cross-encoder finishes |

Chat answers from the fused ranking because it is fast and, in the project's evaluation, as good as
the reranked order; the cross-encoder is used by the progressive search view.

## 5. Design decisions

| Decision | Reason |
|---|---|
| Rules, not a model, decide on web search | no added latency; behaviour is predictable and testable |
| Search in parallel, with a budget | the web never makes an internal answer slower |
| Soft language preference | models are multilingual; filtering by language hides relevant documents |
| Stable prompt prefix | provider-side prompt caching reduces cost and latency |
| Stream and rotate | a rate limit moves to another key at once instead of sleeping |
| Sources grouped by origin | users can tell internal evidence from web evidence |
| Role-scoped personas | a persona can only see the data its role is entitled to |

## 6. Interfaces

| Route group | Purpose |
|---|---|
| `POST /api/v1/chat/stream`, `/chat/async`, `/chat`, `WS /ws/chat` | copilot (streaming, polled job, blocking, socket) |
| `GET /api/v1/knowledge/search`, `POST /knowledge/search/async` | knowledge search (progressive) |
| `GET /api/v1/kpis*`, `/insights/*`, `POST /forecast` | KPIs, health, anomalies, forecasts |
| `/api/v1/financial`, `/growth`, `/hr`, `/it`, `/logistics`, `/operations`, `/esg` | domain analytics |
| `POST /api/v1/ingest/*`, `/webhook/{source}` | data hub |
| `GET /api/v1/glossary`, `/personas`, `/chat/sessions*` | glossary, personas, history |
| `GET /api/v1/admin/*` | administration |
| `GET /health`, `GET /ready` | liveness; readiness |

## 7. Configuration

Everything is environment-driven; [`.env.example`](.env.example) lists every variable with its
purpose. Groups: model tiers and fallbacks, retrieval and embeddings, web search, access and
sessions, document and audio services, storage, telemetry, frontend build.

## 8. Privacy and security

Web searches contain only the question text. Access is controlled by tokens and roles, history is
scoped to its owner, and the optional startup ping carries only service name, version and a random
installation id (disable with `TELEMETRY_OPT_OUT=true` or `DO_NOT_TRACK=1`).
