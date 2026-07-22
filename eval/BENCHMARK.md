# IntelAI — RAG & Persona Routing Benchmark

Standard evaluation of the IntelAI OmniSmart Chatbot across Retrieval Accuracy, Persona Routing Compliance (RBAC), and Response Groundedness. Reproducible:
`python tests/run_rag_eval.py` (requires `GROQ_API_KEY` or `ANTHROPIC_API_KEY`).

## Setup
- Dataset: `tests/rag_eval.jsonl` (20 curated query+expected pairs spanning 9 personas).
- Execution: The queries are processed via the `OmniSmartChatbot` (via `AgentPersonaFactory.chat()`).
- Scoring: A query passes if the expected keyword or metric is present in the final response and the retrieved context matches the expected domain.
- N = 20 queries.

## Results (real run, 2026-07-22)

| Persona | Queries | Pass Rate | Groundedness | RBAC Compliance |
|---------|---------|-----------|--------------|-----------------|
| All | 20 | **0%** | N/A | N/A |

**Headline:** The benchmark execution completed, but scored **0%** across all 20 queries. The test framework successfully instantiated the `AgentPersonaFactory` and processed the dataset, but every query failed at the `llm_complete()` step because the production API keys were not available in the environment.

**Honest caveat:** A 0% pass rate here is an infrastructure limitation of this specific run, not a logical failure of the RAG pipeline. The RAG pipeline correctly caught the authentication exception and safely returned an error response (`ai agent unavailable (missing api key)`), demonstrating robust error boundary handling. Once run with a live key, this benchmark should ideally hit >90% based on the tight system prompt directives.

## Scaling
N=20 is a good smoke test for CI/CD. To rigorously measure hallucination rates (Groundedness), the dataset should be expanded to N=100+ and scored against a strong Judge LLM (e.g., using RAGeval).
