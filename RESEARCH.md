# IntelAI: Autonomous Dual-Loop RAG & Multi-Modal Context Reranking Engine

## Abstract
IntelAI presents an autonomous dual-loop Retrieval-Augmented Generation (RAG) architecture engineered for role-scoped enterprise analytics. By combining dense vector similarity with knowledge graph PageRank adjacency metrics, IntelAI performs multi-hop context retrieval and claim verification. The engine implements an outer loop for dynamic query decomposition and an inner loop for micro-claim grounding verification, reducing hallucination rates while ensuring strict active citation attribution.

---

## 1. System Architecture & Context Pipeline

IntelAI integrates dense vector search, lexical BM25 indexing, and GraphRAG-lite multi-hop entity traversal behind a persona-conditioned role scoping filter.

```
Query q (Persona: CFO / CHRO / CTO / ...)
   |
   +---> Outer Loop: Query Decomposition & Subgraph Expansion
   |
   +---> Hybrid Reranking Pipeline
   |      - Dense Vector Similarity (bge-large / Qdrant)
   |      - BM25 Lexical Keyword Matching
   |      - GraphRAG-lite PageRank Entity Adjacency
   |
   +---> Inner Loop: Token Micro-Verification & Citation Grounding
   |
   v
Grounded Response + Source Citation Map [(doc_id, chunk_id, offset)]
```

---

## 2. Mathematical Formulation

### Hybrid Graph-Dense Reranking
For a document chunk $d_j$ and query $q$ with extracted entity set $\mathcal{E}_q$, the hybrid retrieval score $S_{hybrid}(d_j, q)$ combines normalized dense vector cosine distance with PageRank centrality over the knowledge graph:

$$S_{hybrid}(d_j, q) = \alpha \cdot \frac{\mathbf{e}_q \cdot \mathbf{e}_{d_j}}{\|\mathbf{e}_q\| \|\mathbf{e}_{d_j}\|} + (1 - \alpha) \cdot \text{PageRank}_{KG}(d_j \mid \mathcal{E}_q)$$

where $\alpha \in [0, 1]$ controls the weight balance between semantic vector similarity and structural entity connectivity.

### Claim Grounding Verification Index
Each generated sentence $s_k$ in response $R$ is verified against retrieved text passages $K$:

$$\text{GroundingScore}(s_k, K) = \max_{p \in K} \cos(\mathbf{e}_{s_k}, \mathbf{e}_p)$$

Sentences satisfying $\text{GroundingScore}(s_k, K) \ge \tau_{threshold}$ are tagged with explicit passage citations; ungrounded assertions are flagged for self-correction.

---

## 3. Reproducibility & Empirical Benchmarking Protocol

The codebase includes an automated benchmark evaluation script. To execute empirical verification locally:

```bash
python3 eval/run_benchmarks.py --seed 42
```

### Empirical Baseline Results
- **Evaluation Queries**: $250$
- **Recall@3**: $0.9280$
- **Recall@5**: $0.9880$
- **MRR@5**: $0.7733$
- **NDCG@5**: $0.8303$
- **Faithfulness Score**: $0.9393$
- **Hallucination Mitigation Rate**: $97.6\%$
- **Mean Retrieval Latency**: $42.5\text{ ms}$

---

## 4. Technical Citation

```bibtex
@techreport{siddo2026intelai,
  author      = {Yacine Seybou Siddo},
  title       = {IntelAI: Autonomous Dual-Loop RAG and Multi-Modal Context Reranking Engine},
  institution = {GitHub Repository},
  year        = {2026},
  url         = {https://github.com/Yacine-ai-tech/IntelAI}
}
```
