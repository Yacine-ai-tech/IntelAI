# Real Data Ingestion Strategy – IntelAI

> **Purpose**: Define exactly what real enterprise data to collect, in what quantity, and in what format, to fully replace the synthetic seed data with production-grade corporate content that stress-tests IntelAI across all 7 business health domains and all 78 KPI metrics.

---

## Why Real Data Matters

The synthetic seed data (62,144 rows) was generated from random distributions. It has zero correlation between domains, zero narrative coherence across months, and no document-level complexity. This makes it impossible to:

1. Meaningfully test RAG retrieval quality (there are no real multi-page documents to retrieve from).
2. Benchmark the multi-judge LLM scoring pipeline (synthetic KPI trends have no ground truth to compare against).
3. Demonstrate the system to investors or enterprise clients (the data looks obviously fake).

Real data must be correlated, narratively coherent, span 78 months (January 2020 – June 2026), and cover all 7 domains simultaneously using a single fictional company profile.

---

## Fictional Company Profile

**Company**: **Arion Manufacturing Group** (privately held, B2B industrial supplier)
- Industry: Industrial equipment & components manufacturing
- Headcount: 2,340 employees (peak), ~1,800 (current post-restructuring)
- Revenue: $480M ARR at peak, $320M ARR current
- Geography: 3 plants (Ohio, Germany, Malaysia), HQ in Chicago
- Key events:
  - **Q1 2020**: COVID supply chain shock
  - **Q3 2021**: ERP migration (SAP → Oracle)
  - **Q1 2022**: Acquisition of Vertex Components Ltd (UK)
  - **Q2 2023**: Workforce restructuring (420 layoffs)
  - **Q4 2024**: ISO 14001 ESG certification
  - **Q1 2026**: Leadership change (new CFO, CPO)

This fictional profile enables correlated, realistic data with explainable anomalies across every domain.

---

## Domain 1 — Finance & Revenue

### What to collect

| # | Document | Format | Pages | Source |
|---|----------|--------|-------|--------|
| 1 | Annual Financial Report 2023 (real 10-K proxy) | PDF | 180–220 | SEC EDGAR (public companies: AMETEK, Roper Technologies) |
| 2 | Quarterly Earnings Release Q1–Q4 2024 | PDF | 8–12 each | Same source |
| 3 | Budget vs. Actuals spreadsheet (48 months) | XLSX | n/a | Create from real SEC revenue lines |
| 4 | Auditor's Report (Big 4 format) | PDF | 6–8 | Real audit report template (KPMG, Deloitte public samples) |
| 5 | Cash Flow Statement (5 years) | PDF or XLSX | 4–6 | SEC EDGAR |
| 6 | Revenue by segment breakdown memo | PDF | 3–4 | Manual creation from real data |

### KPI metrics covered
- `revenue_growth_rate`, `gross_margin`, `ebitda_margin`, `operating_cash_flow`,
  `net_profit_margin`, `revenue_per_employee`, `accounts_receivable_days`

### Data sources
- **SEC EDGAR** (free, public): `https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&type=10-K`
  - Target: AMETEK Inc. (AME), Roper Technologies (ROP), Parker Hannifin (PH)
  - Download their 10-K PDFs directly — these are 180–300 pages each
- **IBM HR Analytics Dataset**: `https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset`

### Quantity target
- **6 PDFs** (total ~800 pages of financial text)
- **2 XLSX files** (budget/actuals + cash flow)

---

## Domain 2 — People & HR

### What to collect

| # | Document | Format | Pages | Source |
|---|----------|--------|-------|--------|
| 1 | Employee Handbook (full) | PDF | 60–80 | Open-source HR templates (SHRM) |
| 2 | HR Analytics Dataset (1,470 employees) | CSV | n/a | IBM HR Dataset (Kaggle) |
| 3 | Annual Engagement Survey Results 2022–2024 | PDF | 20–30 each | Real survey report template |
| 4 | Compensation Bands Memo | PDF | 8–12 | Manual from real industry benchmarks |
| 5 | Restructuring Plan — Q2 2023 | PDF | 15–20 | Manual (references real industry patterns) |
| 6 | Onboarding Process Documentation | PDF | 25–30 | SHRM template |
| 7 | Performance Review Cycle Report | PDF | 12–15 | Manual |

### KPI metrics covered
- `employee_turnover_rate`, `voluntary_attrition`, `time_to_hire`, `training_hours_per_employee`,
  `engagement_score`, `absenteeism_rate`, `headcount_growth`, `cost_per_hire`

### Data sources
- **IBM HR Attrition Dataset**: `https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset`
  - 1,470 real-world HR records with 35 attributes
- **SHRM HR Templates**: `https://www.shrm.org/resourcesandtools/tools-and-samples/hr-forms/pages/cms_000516.aspx`
- **US BLS Occupational Employment Data**: `https://www.bls.gov/oes/current/oes_nat.htm`

### Quantity target
- **1 CSV** (IBM HR dataset, 1,470 rows)
- **6 PDFs** (total ~200 pages of HR documentation)

---

## Domain 3 — Operations & Supply Chain

### What to collect

| # | Document | Format | Pages | Source |
|---|----------|--------|-------|--------|
| 1 | Supply Chain Disruption Report (COVID impact) | PDF | 40–60 | ISM / McKinsey public reports |
| 2 | Production Capacity Utilization Report (monthly, 48 months) | XLSX | n/a | ISM Manufacturing PMI data |
| 3 | Supplier Scorecard (top 20 suppliers, 3 years) | XLSX | n/a | Manual from real industry format |
| 4 | Operations Process Manual | PDF | 80–120 | ISO 9001 template |
| 5 | Inventory Turnover Analysis | PDF | 10–15 | Manual |
| 6 | Plant Safety Incident Log | XLSX | n/a | OSHA public records format |
| 7 | ERP Migration Project Report (SAP → Oracle) | PDF | 30–40 | Gartner ERP case study (public) |

### KPI metrics covered
- `inventory_turnover`, `supplier_on_time_delivery`, `production_yield_rate`,
  `equipment_downtime_hours`, `defect_rate`, `capacity_utilization`, `on_time_shipment_rate`

### Data sources
- **ISM Report on Business (Manufacturing PMI)**: `https://www.ismworld.org/supply-management-news-and-reports/reports/ism-report-on-business/`
- **OSHA Injury/Illness data**: `https://www.osha.gov/data`
- **Gartner ERP Case Studies**: via public Google Scholar search

### Quantity target
- **5 PDFs** (~350 pages combined)
- **3 XLSX** (production data, supplier scorecard, safety log)

---

## Domain 4 — IT & Technology

### What to collect

| # | Document | Format | Pages | Source |
|---|----------|--------|-------|--------|
| 1 | IT Infrastructure Audit Report | PDF | 25–35 | ISACA public templates |
| 2 | Cybersecurity Incident Log (2020–2024) | XLSX | n/a | Sanitized real format (NIST) |
| 3 | Cloud Migration Project Report | PDF | 20–30 | AWS/Azure case study (public) |
| 4 | Software License Inventory | XLSX | n/a | Manual |
| 5 | IT Helpdesk Ticket Volume Report (monthly) | CSV | n/a | Manual with realistic patterns |
| 6 | API Uptime & SLA Compliance Report | PDF | 10–15 | Synthetic but based on real SLA formats |

### KPI metrics covered
- `system_uptime_percent`, `mean_time_to_resolve_incidents`, `cybersecurity_incidents`,
  `it_cost_as_percent_of_revenue`, `software_license_utilization`

### Data sources
- **ISACA IT Audit Templates**: `https://www.isaca.org/resources/audit-and-assurance`
- **NIST Cybersecurity Framework**: `https://www.nist.gov/cyberframework`
- **AWS Case Studies**: `https://aws.amazon.com/solutions/case-studies/`

### Quantity target
- **4 PDFs** (~110 pages combined)
- **3 data files** (XLSX/CSV)

---

## Domain 5 — Customer & Growth

### What to collect

| # | Document | Format | Pages | Source |
|---|----------|--------|-------|--------|
| 1 | Customer Satisfaction Survey Summary Report | PDF | 20–25 | Real NPS report format |
| 2 | Sales Pipeline Report (CRM export, 3 years) | CSV | n/a | Synthetic but structured like Salesforce export |
| 3 | Customer Churn Analysis Report | PDF | 15–20 | Manual |
| 4 | Market Expansion Strategy Deck | PDF | 35–40 | Manual from real BCG-style format |
| 5 | Product Lifecycle Report | PDF | 20–25 | Manual |

### KPI metrics covered
- `customer_satisfaction_score`, `net_promoter_score`, `customer_churn_rate`,
  `customer_acquisition_cost`, `lifetime_value_to_cac_ratio`, `revenue_concentration_risk`

### Data sources
- **Bain NPS Research**: `https://www.bain.com/consulting-services/customer-strategy-and-marketing/net-promoter-score-system/`
- **Salesforce State of Sales Report** (free download): `https://www.salesforce.com/resources/research-reports/state-of-sales/`

### Quantity target
- **4 PDFs** (~100 pages combined)
- **1 CSV** (CRM pipeline)

---

## Domain 6 — Financial Risk & Compliance

### What to collect

| # | Document | Format | Pages | Source |
|---|----------|--------|-------|--------|
| 1 | Enterprise Risk Register | XLSX | n/a | ISO 31000 template |
| 2 | Compliance Audit Report (SOX-adjacent) | PDF | 40–60 | AICPA SOC 2 Type II template |
| 3 | Legal Dispute Summary | PDF | 10–15 | Manual |
| 4 | Insurance Policy Coverage Summary | PDF | 8–12 | Manual |
| 5 | Regulatory Filing (EPA / OSHA annual) | PDF | 20–30 | Real EPA annual report format |

### KPI metrics covered
- `debt_to_equity_ratio`, `interest_coverage_ratio`, `regulatory_compliance_rate`,
  `audit_findings_open`, `insurance_claims_count`

### Data sources
- **AICPA SOC 2 Templates**: `https://www.aicpa-cima.com/resources/download/soc-2-examination`
- **EPA Emission Inventories**: `https://www.epa.gov/ghgemissions/inventory-us-greenhouse-gas-emissions-and-sinks`

### Quantity target
- **4 PDFs** (~130 pages combined)
- **1 XLSX** (risk register)

---

## Domain 7 — ESG & Sustainability

### What to collect

| # | Document | Format | Pages | Source |
|---|----------|--------|-------|--------|
| 1 | ESG Annual Report 2022 & 2023 | PDF | 80–100 each | Real public ESG reports (Eaton Corp, Parker Hannifin) |
| 2 | Carbon Emissions Tracker (Scope 1, 2, 3) | XLSX | n/a | GHG Protocol template |
| 3 | ISO 14001 Certification Report | PDF | 15–20 | ISO public template |
| 4 | Diversity & Inclusion Report | PDF | 25–30 | Real D&I report format |
| 5 | Supplier Sustainability Audit | PDF | 20–25 | Manual |

### KPI metrics covered
- `carbon_emissions_intensity`, `renewable_energy_percentage`, `waste_recycling_rate`,
  `gender_pay_gap`, `diversity_ratio`, `esg_score`, `community_investment_percent`

### Data sources
- **Eaton Corporation ESG Report** (free): `https://www.eaton.com/us/en-us/company/news-insights/esg.html`
- **Parker Hannifin ESG Report** (free): `https://www.parker.com/content/dam/parker/esg/`
- **GHG Protocol Templates**: `https://ghgprotocol.org/calculation-tools`

### Quantity target
- **4 PDFs** (~270 pages combined)
- **1 XLSX** (carbon tracker)

---

## Total Ingestion Target

| Domain | PDFs | XLSX/CSV | Approx. Total Pages |
|--------|------|----------|---------------------|
| Finance & Revenue | 6 | 2 | ~800 |
| People & HR | 6 | 1 | ~220 |
| Operations | 5 | 3 | ~350 |
| IT & Technology | 4 | 3 | ~110 |
| Customer & Growth | 4 | 1 | ~100 |
| Financial Risk | 4 | 1 | ~130 |
| ESG | 4 | 1 | ~270 |
| **TOTAL** | **33 PDFs** | **12 data files** | **~1,980 pages** |

---

## Data Correlation Requirements

All datasets must be internally consistent with the Arion Manufacturing Group profile:

1. **Timeline**: All KPIs must be tagged with `period_month` spanning Jan 2020 – Jun 2026 (78 months).
2. **Event correlation**:
   - COVID shock (Mar 2020): Supply chain KPIs drop, revenue dips 18%, hiring freeze visible in HR data.
   - ERP migration (Sep 2021): IT downtime spike, production dips 6%, compliance audit findings increase.
   - Acquisition (Mar 2022): Headcount +380, revenue +$40M, integration cost spike.
   - Restructuring (Jun 2023): Headcount -420, turnover spike, engagement score drops.
   - ESG certification (Dec 2024): Carbon intensity improvement, recycling rate improves.
3. **Cross-domain correlation**: Finance and HR data must reconcile (e.g., revenue per employee = revenue / headcount = consistent number).
4. **Anomaly scenarios**: Data must contain at least 7 detectable anomaly windows where IntelAI's health scoring should flag `critical` or `warning` status.

---

## Ingestion Pipeline

### Step 1 — Collect raw documents
- Download SEC 10-K PDFs from EDGAR using `sec-edgar-downloader` pip package.
- Download IBM HR CSV from Kaggle.
- Download real ESG PDFs from Eaton / Parker Hannifin public websites.
- Download ISM PMI data (monthly CSV).

### Step 2 — Adapt to Arion profile
- Strip company names using `pdfplumber` + `re.sub()` to replace real company names with "Arion Manufacturing Group".
- Adjust revenue figures to $320M–$480M range using a scaling factor.
- Ensure all dates fall within Jan 2020 – Jun 2026.

### Step 3 — Ingest into IntelAI
- Use `IntelAI/scripts/ingest_real_enterprise_data.py` (already written).
- Insert `kpi_metrics` rows by parsing XLSX tables.
- Insert `knowledge_base` rows by chunking PDFs (512 tokens, 50 overlap).
- Re-embed all chunks into Qdrant `company_knowledge` collection.

### Step 4 — Validate
- Run `python3 global_scripts/wipe_intelai_db.py` to confirm count returns 0 first.
- Then run `python3 IntelAI/scripts/ingest_real_enterprise_data.py`.
- Run `python3 IntelAI/scripts/evaluate_with_rageval_package.py` to verify RAG quality.
- Check `kpi_metrics` row count ≥ 5,000 (78 months × 7 domains × avg 9 KPIs).

---

## Commands to Run

```bash
# 1. Install dependencies
pip install sec-edgar-downloader pdfplumber openpyxl psycopg[binary] qdrant-client

# 2. Download SEC 10-K filings (real data, public)
python3 -c "
from sec_edgar_downloader import Downloader
dl = Downloader('ArionGroup', 'admin@arion.com')
dl.get('10-K', 'AME', limit=3)   # AMETEK
dl.get('10-K', 'ROP', limit=3)   # Roper Technologies
"

# 3. Download IBM HR dataset from Kaggle
# kaggle datasets download pavansubhasht/ibm-hr-analytics-attrition-dataset

# 4. Wipe existing DB
POSTGRES_URL=<neon_url> python3 global_scripts/wipe_intelai_db.py

# 5. Run ingestion
POSTGRES_URL=<neon_url> python3 IntelAI/scripts/ingest_real_enterprise_data.py

# 6. Validate
POSTGRES_URL=<neon_url> python3 IntelAI/scripts/evaluate_with_rageval_package.py
```

---

## Notes

- All public SEC filings, ISM data, EPA reports, and open-source HR templates are **freely available** with no licensing restrictions for internal use.
- Real company names (AMETEK, Roper Technologies, Parker Hannifin) must be **stripped** before ingestion — use `Arion Manufacturing Group` as the replacement.
- Never ingest real PII (real employee names, real SSNs). Use IBM HR dataset which is already anonymized.
- The DB wipe must happen before any ingestion run to avoid duplicate rows.

---

## IntelAI Full Capability Map — Data Requirements Per Feature

> This section maps every IntelAI feature to the data it consumes, so the ingestion strategy can be verified to cover 100% of capabilities.

### 1. Multi-Persona RAG Copilot (`/api/v1/chat`)
**What it needs**: `knowledge_base` table populated with embeddings. Documents ingested via `/ingest/document`.
**Data requirement**: At minimum 50 documents across all 7 domains (≥ 7/domain) for meaningful persona routing. The Arion PDFs (annual reports, HR handbooks, ESG certifications) cover this directly.
**Test**: Ask each persona a domain-specific question and verify RAG sources are cited.

### 2. Business Health Score (`/api/v1/insights/health`)
**What it needs**: `kpi_metrics` rows with `category` and `value` for at least 3 periods.
**Data requirement**: 78 months × 7 domains × avg 9 metrics/domain = ~4,900 rows minimum. Full 62K rows (from real ingestion) gives the score statistical validity.
**Test**: Health score should be non-zero and ≠ 50.0 (the fallback default).

### 3. Risk Radar (`/api/v1/insights/risk` + `/insights/anomalies`)
**What it needs**: Enough historical variance in `kpi_metrics` to trigger Z-score anomaly detection (needs ≥ 12 periods per metric for std dev to be meaningful).
**Data requirement**: The 78-month span (Jan 2020 – Jun 2026) provides this. COVID shock in Q1 2020 and restructuring in Q2 2023 should produce detectable anomalies.
**Test**: At least 3 anomalies should appear in the anomaly watchlist for the Finance and HR domains.

### 4. Monte-Carlo Forecasting (`/api/v1/forecast`)
**What it needs**: ≥ 12 historical data points per metric (LinearRegression needs sample size for meaningful confidence intervals).
**Data requirement**: 78 monthly rows per metric. The ISM manufacturing index data covers Operations metrics; SEC filing revenue lines cover Finance metrics.
**Test**: Run forecast on `revenue_growth` — R² should be > 0.5 for a well-trended metric.

### 5. Financial Statement Generation (`/api/v1/financial/statement`)
**What it needs**: Finance-domain KPI metrics (`gross_margin`, `net_income`, `ebitda`, `revenue`, `operating_expenses`, `capex`).
**Data requirement**: At least 8 quarters of Finance KPIs. The SEC 10-K data covers exactly this.
**Test**: Generate a P&L for 2024 — should return structured statement with real values, not fallback zeros.

### 6. Domain Pages (HR / IT / Ops / Logistics / ESG / Growth / Finance)
Each domain page calls multiple sub-endpoints. Required KPI categories:

| Domain | Required `category` values in `kpi_metrics` | Key metrics |
|--------|---------------------------------------------|-------------|
| Finance | `Finance`, `Revenue` | gross_margin, net_income, ebitda, revenue |
| Growth | `Growth` | mrr, arr, cac, ltv, churn_rate |
| HR/People | `People`, `HR` | headcount, turnover_rate, time_to_hire, engagement_score |
| Operations | `Operations` | oee, throughput, defect_rate, cycle_time |
| IT | `IT`, `IT_Ops` | uptime, mttr, incident_count, deployment_freq |
| Logistics | `Logistics`, `Supply Chain` | inventory_turns, on_time_delivery, supplier_reliability |
| ESG | `ESG` | carbon_emissions, esg_score, energy_consumption, diversity_index |

### 7. Knowledge Graph (`/knowledge-graph` page)
**What it needs**: Populated `knowledge_base` with documents that have entity relationships (companies, metrics, events, people).
**Data requirement**: Rich PDF documents where named entities can be extracted. Annual reports naturally contain entity mentions (product names, exec names, facility names).
**Test**: Search for "Arion" or "Ohio plant" — should return a visible graph with connected nodes.

### 8. Analytics KPI Explorer (`/api/v1/kpis`, `/api/v1/kpis/metrics`)
**What it needs**: A wide variety of distinct metric names to make the explorer useful.
**Data requirement**: The strategy targets 78 distinct metrics across 7 domains. Each domain contributes ~11 metrics. The SEC + IBM HR + ISM + EPA data covers all of these.
**Test**: The metric dropdown in Analytics should show ≥ 78 unique metric names.

### 9. Organization Chart (`/organization` page)
**What it needs**: HR department data from `/hr/departments`.
**Data requirement**: HR KPIs must include department-level breakdowns. The IBM HR dataset provides this (Department column maps to sub-department KPIs).
**Test**: Organization page should render a visual hierarchy with ≥ 5 departments.

### 10. Glossary (`/api/v1/glossary`)
**What it needs**: Static — built into IntelAI's i18n system. No DB data required.
**Status**: ✅ Always works regardless of ingestion state.

### 11. Board Report PDF Export (`/data/export?format=pdf`)
**What it needs**: All KPI and insight data populated (health score, risk score, domain summaries).
**Data requirement**: Same as items 2–6 above. Full ingestion unlocks meaningful PDF output.
**Test**: Export a board report — should be > 4 pages with real charts, not empty placeholders.

### 12. Agent Tool Runner (`/api/v1/agent/run`)
**What it needs**: KPI data for tool calls (get_kpi_trend, get_domain_health, run_forecast, search_knowledge).
**Data requirement**: Same as above — full KPI + knowledge_base population.
**Test**: As CEO persona, run `get_kpi_trend` for `revenue_growth` — should return a 78-point series.

### 13. Admin Audit Log (`/api/v1/admin/audit`)
**What it needs**: User activity (auto-populated by login events).
**Status**: ✅ Works without ingestion — populated by normal app usage.

---

## Ingestion Completeness Checklist

Run this after ingestion to confirm all capabilities are covered:

```python
# IntelAI/scripts/validate_ingestion.py
import psycopg, os

conn = psycopg.connect(os.environ['POSTGRES_URL'])
cur = conn.cursor()

checks = {
    'Total KPI rows': 'SELECT COUNT(*) FROM kpi_metrics',
    'Distinct metrics': 'SELECT COUNT(DISTINCT metric) FROM kpi_metrics',
    'Distinct categories': 'SELECT COUNT(DISTINCT category) FROM kpi_metrics',
    'Distinct periods': 'SELECT COUNT(DISTINCT period) FROM kpi_metrics',
    'Knowledge base docs': 'SELECT COUNT(*) FROM knowledge_base',
    'Finance rows': "SELECT COUNT(*) FROM kpi_metrics WHERE category ILIKE '%finance%' OR category ILIKE '%revenue%'",
    'HR rows': "SELECT COUNT(*) FROM kpi_metrics WHERE category ILIKE '%people%' OR category ILIKE '%hr%'",
    'ESG rows': "SELECT COUNT(*) FROM kpi_metrics WHERE category ILIKE '%esg%'",
}

print('=== Ingestion Validation ===')
for label, sql in checks.items():
    cur.execute(sql)
    val = cur.fetchone()[0]
    status = '✅' if val > 0 else '❌'
    print(f'{status} {label}: {val}')
```

**Minimum acceptable thresholds:**
- Total KPI rows: ≥ 30,000
- Distinct metrics: ≥ 70
- Distinct categories: ≥ 7
- Distinct periods: ≥ 60 (months)
- Knowledge base docs: ≥ 40
