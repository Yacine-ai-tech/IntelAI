# Persona-Routed Retrieval-Augmented Generation for Role-Scoped Enterprise Assistants

> **DRAFT preprint skeleton (2026) — submit 2027.** ~6 pages target. arXiv cs.CL / cs.IR.
> Author: Yacine. Artifact: IntelAI (github.com/Yacine-ai-tech/IntelAI).

## Abstract
We present *persona-routed RAG*, a pattern that conditions a single retrieval-augmented
generation system on the user's organizational role to enforce (a) data-access boundaries
and (b) response style, by filtering the retrieval corpus to a role's scope *prior* to
retrieval. We combine this with hybrid retrieval (dense + sparse + reranking) and a
lightweight entity-graph step (GraphRAG-lite) for multi-hop queries, and we evaluate
retrieval recall and answer groundedness across nine business personas on a deployed
multi-domain analytics assistant. *(State the headline delta: scoping eliminates X% of
cross-domain leakage; GraphRAG-lite improves groundedness on multi-hop queries by Y%.)*

## 1. Introduction
- Production copilots expose the same assistant/data to all users → leakage + tone mismatch.
- Contribution: (1) pre-retrieval, role-scoped corpus filtering as an authorization mechanism;
  (2) a declarative persona abstraction (prompt + scope + temperature); (3) GraphRAG-lite for
  multi-hop KPI queries; (4) a reproducible groundedness eval and gate.

## 2. Related Work
- RAG (Lewis et al.); hybrid retrieval / RRF; rerankers (BGE); GraphRAG (Microsoft);
  RBAC in IR; LLM-as-judge groundedness (cite Phoenix/TruLens/RAGAS landscape).
- Differentiator: authorization enforced at the *retrieval-set* level, role-conditioned.

## 3. Method
### 3.1 Persona abstraction
`Persona = (system_prompt, data_access ⊆ Domains, temperature)`; routing `role → persona`.
### 3.2 Pre-retrieval scoping
`scope(corpus, persona) = {d ∈ corpus : domain(d) ∈ persona.data_access}`; retrieval runs on
the scoped set, so generations cannot be grounded in out-of-scope data.
### 3.3 Hybrid retrieval
Dense (BGE-large) ⊕ BM25 → RRF → BGE reranker.
### 3.4 GraphRAG-lite
Ingest-time entity extraction `{department, category, period, metric}`; query-time
entity-overlap ranking when |query entities| ≥ 2; fall back to hybrid otherwise.

## 4. Experimental Setup
- System: IntelAI, 9 personas, 7 KPI domains, deterministic seed (24-month series).
- Eval set: `src/data/rag_eval.jsonl` (25 role-tagged queries; expand to ~100 for submission).
- Metrics: answer recall; groundedness (proxy + LLM-judge for the paper); leakage rate
  (fraction of out-of-scope domains appearing in retrieved sources).
- Conditions: vector-only · hybrid · hybrid+GraphRAG-lite; with/without scoping.

## 5. Results *(to fill)*
- Table 1: recall & groundedness per persona × condition.
- Table 2: cross-domain leakage with vs without pre-retrieval scoping.
- Finding: scoping → leakage ≈ 0; GraphRAG-lite → groundedness↑ on multi-hop subset.

## 6. Limitations
- Groundedness proxy is keyword-based (LLM-judge in final); GraphRAG-lite is entity-overlap,
  not full graph reasoning; single deployment; synthetic-but-realistic KPI data.

## 7. Conclusion
Role-scoped, persona-routed RAG is a simple, deployable pattern that makes enterprise
copilots safer (no cross-role leakage) and better (multi-hop groundedness), with a
reproducible eval gate.

## Reproducibility
Code, personas package, seed, and eval set are open: github.com/Yacine-ai-tech/IntelAI ·
`pip install omnismart-personas` · `make seed && make eval`.
