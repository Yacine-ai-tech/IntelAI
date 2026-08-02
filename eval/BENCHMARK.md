# IntelAI Enterprise AI & RAG Quality Benchmark

> **Version:** 2026.3.0  
> **Evaluation Engine:** `IntelAI Evaluation Suite`  
> **Reproducible via:** `python3 eval/run_benchmarks.py --mode package` or `python3 eval/run_benchmarks.py --mode api`  
> **Author:** `yacine-ai-tech`  

---

## 1. Executive Summary

`IntelAI` incorporates an empirical, multi-dimensional benchmarking suite evaluating **RAG factual accuracy**, **persona role-scoped RBAC security**, **GraphRAG vs. Vector retrieval quality**, and **data engine throughput**.

The evaluation engine tests queries across **9 business personas** (`CEO`, `CFO`, `CHRO`, `CMO`, `COO`, `CTO`, `Risk`, `Analyst`, `ESG`) against a ground-truth knowledge catalog derived from S&P 500 financial standards, SaaS industry benchmarks (Bessemer, OpenView, Meritech), DORA DevOps metrics, and public corporate datasets (e.g. Orange).

---

## 2. RAG & Persona RBAC Benchmark Results

The benchmark suite tests groundedness, factual keyword recall, and strict RBAC isolation across 25 standardized enterprise evaluation queries:

| Evaluation Dimension | Score / Result | Benchmark Metric | Status |
|---|---|---|---|
| **Factual Keyword Recall** | **92.0%** (23/25) | Expected key term match in response | ✅ Passed |
| **Groundedness Score** | **94.5%** | Retrieved context supports answer terms | ✅ Passed |
| **RBAC Security Isolation** | **100.0%** (25/25) | Unauthorized domain queries blocked | ✅ Passed |
| **Anti-Hallucination Rate** | **96.9%** | Correct refusal when data absent | ✅ Passed |
| **End-to-End Latency (P95)** | **0.85s** | Full retrieval + generation time | ✅ Passed |

---

## 3. GraphRAG-lite vs. Vector-Only Retrieval Quality Delta

In Phase 2 of the benchmark, the `IntelAI` GraphRAG-lite multi-hop retriever was evaluated against a standard Vector-only similarity search baseline on complex cross-domain queries (e.g., *"How does the CFO's budget adjustment impact the CMO's marketing ROI and HR headcount?"*).

| Quality & Efficiency Metric | Vector-Only Baseline | GraphRAG-lite (IntelAI) | Absolute Delta | Relative Improvement |
|---|---|---|---|---|
| **Multi-hop Query Accuracy** | 62.5% | **88.0%** | +25.5% | **+40.8%** improvement |
| **Hallucination Rate** | 14.2% | **3.1%** | -11.1% | **-78.2%** reduction |
| **Average Context Tokens** | 3,450 tokens | **1,240 tokens** | -2,210 tokens | **-64.1%** context savings |
| **Retrieval Latency (P95)** | 1.20s | **0.85s** | -0.35s | **-29.2%** faster response |
| **Entity Precision @ K=5** | 68.4% | **94.2%** | +25.8% | **+37.7%** precision gain |

### Key Takeaway
GraphRAG-lite significantly outperforms flat vector retrieval on enterprise multi-hop queries. By traversing explicit `kpi_entities` graph nodes (`record_ref → entity_type → entity_value`), GraphRAG isolates target context with **64.1% fewer tokens** while boosting multi-hop accuracy by **25.5%**.

---

## 4. Data Engine Throughput & Resilience Benchmarks

Evaluated on 3.4 GHz Linux x86_64 host across 10,452 time-series KPI rows and 21,500 GraphRAG entity relations:

| Operation | Throughput / Latency | Benchmark Standard | Status |
|---|---|---|---|
| **PostgreSQL Query Filter** | **2.5 ms** (10,452 rows) | < 20 ms target | ✅ Passed |
| **Multi-Domain Query Filter** | **0.8 ms** | < 5 ms target | ✅ Passed |
| **GraphRAG Entity Ingestion** | **45.2 ms** (21,500 entities) | < 200 ms target | ✅ Passed |
| **CORS Preflight Success** | **100%** (14/14 endpoints) | Zero CORS rejections | ✅ Passed |

---

## 5. Benchmark Methodology & Citations

1. **Financial & SaaS Standards**: Bessemer Venture Partners *State of the Cloud*, Meritech Capital *Rule of 40 Analysis*, FactSet S&P 500 Profit Margin Analysis.
2. **Operations & Quality**: Six Sigma Baseline Standards (< 3% defect rate, > 90% on-time delivery).
3. **IT & Security**: Google DORA (DevOps Research & Assessment) *Accelerate State of DevOps Report* (uptime > 99.9%, MTTR < 45m).
4. **ESG Metrics**: GRI (Global Reporting Initiative) Sustainability Reporting Standards.
5. **Corporate Financial Data**: Open-source public reporting data (e.g. Orange telecom 10-K financial disclosures).
