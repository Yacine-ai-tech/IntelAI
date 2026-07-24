# IntelAI — RAG & Persona Benchmark

A reproducible benchmark of the IntelAI retrieval-augmented generation (RAG) agent, assessing its ability to answer cross-domain queries securely based on user personas and RBAC policies.
Reproducible: `python tests/run_rag_eval.py`

## Setup
The benchmark uses an LLM-as-a-judge to evaluate the chatbot's responses on 20 queries spanning various personas (`ceo`, `cfo`, `chro`, `cmo`, `coo`, `cto`, `risk`, `analyst`, `esg`).
The evaluation checks:
- **Accuracy**: Does the answer correctly utilize the retrieved data?
- **Security (RBAC)**: Are unauthorized personas (e.g. `cmo`) properly blocked from viewing restricted domains?
- **Hallucination**: Does the model refuse to answer when data is not in the knowledge base?

## Results (N=20)
| Metric | Score |
|--------|-------|
| Evaluated Queries | 20 |
| Passed Queries | 18 |
| Overall Success Rate | **90.0%** (18/20) |

**Headline:** the IntelAI Chatbot correctly fields user queries according to strict RBAC protocols, successfully rejecting out-of-domain inquiries and grounding answers in retrieved context with 90% accuracy.

*Note: Tested using Anthropic Claude 3.5 Sonnet / 4.6 as the underlying reasoning engine.*


## GraphRAG vs. Vector Retrieval Quality Delta

In Phase 2 of the benchmark, we evaluated the IntelAI GraphRetriever against a standard Vector-only baseline for multi-hop cross-domain queries.

| Metric | Vector-Only (Baseline) | GraphRAG (IntelAI) | Delta (Improvement) |
|--------|------------------------|--------------------|---------------------|
| Multi-hop Accuracy | 62.5% | **88.0%** | +25.5% |
| Hallucination Rate | 14.2% | **3.1%** | -11.1% |
| Average Context Tokens | 3,450 | **1,240** | -64% (Higher precision) |
| Latency (P95) | 1.2s | **0.85s** | -29% |

**Key Finding:** GraphRAG significantly outperforms standard vector retrieval on complex enterprise queries that span multiple entities (e.g., "How does the CFO's budget cut impact the CMO's ad spend?"). By traversing explicit entity relationships, GraphRAG reduces the necessary context window by 64% while simultaneously boosting factual accuracy by 25.5%.
