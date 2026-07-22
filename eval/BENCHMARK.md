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
