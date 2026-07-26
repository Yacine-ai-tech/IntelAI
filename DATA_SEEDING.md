# IntelAI Data Seeding, Ingestion & Multi-Domain Data Model Specification

> **Version:** 2026.3.0  
> **Author:** `yacine-ai-tech`  
> **Status:** Production Reference Specification  

---

## 1. Overview & Data Layer Architecture

`IntelAI` operates a **unified, multi-domain KPI data architecture** as the single source of truth for executive dashboards, ML forecasting, GraphRAG entity linking, and persona-scoped AI copilots.

The data layer uses an **idempotent, deterministic seed engine** (`src/data/seed.py`) with `SEED = 42`. It generates a **78-month (6.5 years, 2020-01 to 2026-06)** continuous time-series dataset containing **10,452 KPI metric rows** across 7 business domains.

```
                    ┌──────────────────────────────────────────────┐
                    │          IntelAI Data Access Layer           │
                    │         (src/services/pg_store.py)           │
                    └──────────────────────┬───────────────────────┘
                                           │
                    ┌──────────────────────┴───────────────────────┐
                    │                                              │
        ┌───────────▼────────────┐                     ┌───────────▼────────────┐
        │  Primary Data Store    │                     │   Resilient Fallback   │
        │   Neon PostgreSQL      │                     │ Seed Engine (SEED=42)  │
        │  (kpi_metrics table)   │                     │  (10,452 In-Mem Rows)  │
        └────────────────────────┘                     └────────────────────────┘
```

---

## 2. How Data is Seeded, Collected & Sourced

### 2.1 Seed Engine Execution (`src/data/seed.py`)
Data seeding is fully reproducible via command line or code:

```bash
# Seed default healthy baseline into PostgreSQL:
python3 -m src.data.seed

# Seed a specific scenario (e.g. declining_financial, high_churn_crisis):
python3 -m src.data.seed declining_financial
```

Programmatic invocation:
```python
from src.data.seed import seed_database, generate_kpi_rows

# Generate 10,452 rows in-memory:
rows = generate_kpi_rows(scenario="healthy")

# Seed database:
counts = seed_database(replace=True, scenario="healthy")
```

### 2.2 Corporate Data Sources & Real Industry Benchmarks

The metric catalog is compiled from public corporate filings and audited industry benchmarks:

1. **Orange SA Public Telecom & Financial Disclosures (10-K / Annual Reports 2020-2025)**:
   - Used for realistic revenue structures, operating costs, CAPEX/OPEX allocations, customer ARPU, and network infrastructure uptime models.
2. **FactSet & S&P 500 Profit Margin Analysis (2024)**:
   - Net profit margins (10-15%) and operating cost ratios for healthy enterprise baselines.
3. **Bessemer Venture Partners State of the Cloud (2024)**:
   - SaaS Gross Margin baseline ~79%, Cash Runway > 12 months.
4. **Meritech Capital Rule of 40 Benchmarks**:
   - Combined Growth Rate + EBITDA Margin target > 40%.
5. **High Alpha & OpenView 2024 SaaS Benchmarks**:
   - Net Revenue Retention (NRR) baseline 110%, Monthly Churn < 4.8%, LTV:CAC Ratio > 4.2x, CAC Payback < 14 months.
6. **Google DORA (DevOps Research and Assessment) Accelerate Report (2024)**:
   - System Uptime > 99.95%, Change Failure Rate < 15%, Mean Time to Resolve (MTTR) < 45m.
7. **Six Sigma Manufacturing & Operations Standards**:
   - Defect Rate < 2.1%, On-Time Delivery > 93%, Overall Equipment Effectiveness (OEE) > 84%.
8. **GRI (Global Reporting Initiative) & TCFD ESG Standards**:
   - Carbon Footprint (tCO2e), Renewable Energy %, Audit Compliance Score.

---

## 3. How Data is Imported & Ingested (CSV / Data Hub Pipeline)

External data files (CSVs, Excel, JSON) are imported into `IntelAI` via the Data Hub pipeline (`POST /api/v1/data-hub/upload`):

```
User / API Upload ──► Schema Normalization ──► Entity Extraction ──► PostgreSQL kpi_metrics
 (CSV / JSON)        (Period, Metric, Value)   (GraphRAG Sidecar)      (& Vector Index)
```

### 3.1 Database Table Schema (`kpi_metrics`)
```sql
CREATE TABLE IF NOT EXISTS kpi_metrics (
    id SERIAL PRIMARY KEY,
    period VARCHAR(10) NOT NULL,         -- e.g. '2026-03'
    category VARCHAR(50) NOT NULL,       -- Finance, Growth, People, Operations, IT, Logistics, ESG
    segment VARCHAR(100) DEFAULT 'Global',
    metric VARCHAR(100) NOT NULL,        -- Revenue, Churn Rate, Headcount...
    value NUMERIC(18,4) NOT NULL,
    unit VARCHAR(20) DEFAULT 'USD',
    direction VARCHAR(10) DEFAULT 'up',  -- 'up' (higher is better) | 'down' (lower is better)
    source VARCHAR(100) DEFAULT 'user_upload',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT kpi_unique_entry UNIQUE (period, category, segment, metric)
);
```

### 3.2 GraphRAG Entity Linking Sidecar (`kpi_entities`)
During ingestion, `src.services.entity_extractor` automatically extracts domain entities (`record_ref → entity_type → entity_value`) into the `kpi_entities` table to enable multi-hop cross-domain graph queries.

---

## 4. The 7 Business Health Scenarios

`IntelAI` includes 7 pre-configured health scenarios simulating diverse corporate conditions:

| Scenario Name | Key Multipliers & Anomaly Trajectory | Trigger Command |
|---|---|---|
| **1. Healthy** (Default) | Standard S&P 500 baseline: Gross Margin 72%, NRR 110%, Churn 4.8%, Turnover 8.5%, Uptime 99.95%, On-Time Delivery 93%. | `python3 -m src.data.seed healthy` |
| **2. Declining Financial** | Revenue drops -35%, Gross Margin compresses -25%, Net Profit drops -60%, Cash Runway reduces -50%, Debt-to-Equity spikes +250%. | `python3 -m src.data.seed declining_financial` |
| **3. High Churn Crisis** | Monthly Churn spikes +350% (to 16.8%), NRR drops below 100% (to 85%), CAC increases +80%, LTV:CAC collapses to 0.6x. | `python3 -m src.data.seed high_churn_crisis` |
| **4. Operational Meltdown** | On-Time Delivery drops -30% (to 65%), Defect Rate spikes +450% (to 9.4%), Cycle Time increases +220%, Scrap Rate spikes +280%. | `python3 -m src.data.seed operational_meltdown` |
| **5. Talent Crisis** | Employee Turnover spikes +280% (to 23.8%), Time to Hire increases +220%, Engagement Score drops -35%, Open Positions spike +250%. | `python3 -m src.data.seed talent_crisis` |
| **6. Cybersecurity Breach** | Security Incidents spike +500%, Critical Vulnerabilities increase +400%, System Uptime drops to 92%, SLA Compliance drops to 88%. | `python3 -m src.data.seed cybersecurity_breach` |
| **7. ESG Compliance Failure** | ESG Rating drops -35%, Carbon Footprint increases +180%, Privacy Incidents spike +500%, Supplier Non-Compliance increases +30%. | `python3 -m src.data.seed esg_compliance_failure` |

---

## 5. High Availability Fallback Architecture

If Neon PostgreSQL is unreachable or throttled due to quota limits (`ERROR: Your project has exceeded the data transfer quota`):

1. **Automatic Failover**: `get_kpi_metrics()` in `src/services/pg_store.py` catches database connection errors.
2. **In-Memory Seed Cache**: Instantly loads `_get_seeded_fallback_df()` containing the 10,452-row seed dataset in-memory (< 1.0 ms latency).
3. **Continuous Score Calculation**: `HRService` and `calculate_financial_health_score` continue evaluating metrics at **95 / 100 ("Excellent")**, preventing health scores from dropping to `0`.
