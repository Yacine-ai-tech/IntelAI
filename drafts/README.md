# IntelAI — Writing & Go-to-Market Drafts

> **Status: DRAFTS — internal.** Per STRATEGY §5.1, draft in 2026, publish in 2027.
> Do not post these externally (Medium/HN/LinkedIn/arXiv) yet. They are prepared here so
> the writing is ready when the timing is right.

| File | Purpose |
|---|---|
| [blog_post_1_persona_rag.md](blog_post_1_persona_rag.md) | Technical blog post #1 — "Persona-Routed RAG" (Project 1 research artifact) |
| [preprint_persona_routed_rag.md](preprint_persona_routed_rag.md) | arXiv-style preprint skeleton (6 pages) of the same idea |
| [demo_script.md](demo_script.md) | 3-minute Loom demo walkthrough script |
| [upwork_proposal_templates.md](upwork_proposal_templates.md) | 3 vertical proposal templates (RAG / FastAPI / BI) |

All are grounded in the actual IntelAI implementation: 9 role-scoped personas
(`omnismart-personas`), hybrid retrieval (BGE + BM25 + RRF + reranker), GraphRAG-lite
(`USE_GRAPH_RAG`), and the prompt-eval set (`src/data/rag_eval.jsonl`, `make eval`).
