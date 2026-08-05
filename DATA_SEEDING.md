# IntelAI Data Seeding Guide

> **Disclaimer**: IntelAI is a completely **company-agnostic** AI analytics copilot. NexaCore Technologies is a fictional reference dataset provided exclusively for demonstration, testing, and illustration purposes. You can (and should) replace this data with your own company's real data.

## Overview

This repository contains two layers of demonstration data:

1. **KPI Time-Series CSVs** — 78 months (2020-01 to 2026-06) of deterministic NexaCore Technologies KPIs across 7 business domains, with embedded scenario epochs for causal reasoning demos.
2. **Real Document Corpus** — 39 real, publicly available PDF documents sourced from open-access repositories (Zenodo), organized by domain. These power the RAG copilot, Document Scanner, and DataHub features.

---

## Directory Structure

```
data/
├── ESG/
│   └── nexacore_esg_kpis.csv
├── Finance/
│   └── nexacore_finance_kpis.csv
├── Growth/
│   └── nexacore_growth_kpis.csv
├── IT/
│   └── nexacore_it_kpis.csv
├── Logistics/
│   └── nexacore_logistics_kpis.csv
├── Operations/
│   └── nexacore_operations_kpis.csv
├── People/
│   └── nexacore_people_kpis.csv
├── NEXACORE_COMPANY_PROFILE.md
└── documents/
    ├── annual_reports/          # 4 real org annual reports
    ├── contracts/               # 5 real SLAs and procurement contracts
    ├── financial_statements/    # 9 financial, ESG, logistics reports
    ├── hr_docs/                 # 2 real HR analytics documents
    ├── invoices/                # 1 e-invoicing study + 7 real vendor invoices
    ├── legal_docs/              # 11 legal, GDPR, cybersecurity, IT governance docs
    ├── AmazonWebServices.pdf    # Real AWS invoice
    ├── coolblue1.pdf            # Real Coolblue invoice
    ├── FlipkartInvoice.pdf      # Real Flipkart invoice
    ├── free_fiber.pdf           # Real telecom invoice
    ├── large_invoice_24p.pdf    # 24-page multi-line invoice
    ├── NetpresseInvoice.pdf     # Real Netpresse invoice
    └── QualityHosting.pdf       # Real hosting invoice
```

---

## Layer 1: KPI Time-Series CSVs

### Schema
```
period,category,segment,metric,value,unit,direction,source
```
- **Long Format**: one metric per row
- **78 Months**: 2020-01 through 2026-06
- **Deterministic**: fixed scenario multipliers, fully reproducible

### Source Attributions

| Domain | Primary Sources |
|---|---|
| **Finance** | Orange SA Annual Report 2024; FactSet SP500 2024; Bessemer State of Cloud 2024 |
| **Growth** | Bessemer State of Cloud 2024; OpenView SaaS Benchmarks 2024; High Alpha Benchmarks 2024 |
| **People** | SHRM 2024 Workforce Analytics; LinkedIn Talent Insights 2024; Mercer Global Talent Trends 2024 |
| **Operations** | Six Sigma Industry Standards 2024; OSHA Safety Data 2024; ISM Manufacturing PMI 2024 |
| **Logistics** | Gartner Supply Chain 2024; ISM Supply Chain Reports 2022-2024; FedEx Logistics Benchmarks 2024 |
| **IT** | Google DORA Accelerate Report 2024; NIST Cybersecurity Framework 2024; Gartner IT Operations 2024 |
| **ESG** | GRI Global Reporting Initiative 2024; TCFD Framework 2023; CDP Environmental Data 2024 |

### Timeline and Scenario Epochs

| Epoch | Months | Scenario | Key Impacts |
|---|---|---|---|
| **Jan 2020 - Jun 2021** | 18 | COVID-19 Impact | Revenue drop, Operations OEE drop, IT Uptime boost, Logistics disrupted |
| **Jul 2021 - Dec 2022** | 18 | Recovery & Supply Chain Crisis | OTD drops, Order cycle times spike, Margins pressured |
| **Jan 2023 - Sep 2023** | 9 | Healthy Baseline | Normal operations and 2% monthly revenue growth |
| **Oct 2023 - Mar 2024** | 6 | High Churn Crisis | SaaS churn spikes, NRR drops, LTV:CAC collapses |
| **Apr 2024 - Sep 2024** | 6 | Talent Crisis | Turnover spikes, Time-to-hire soars, OPEX increases |
| **Oct 2024 - Mar 2025** | 6 | Cybersecurity Breach | IT Uptime drops, vulnerabilities spike, Revenue takes minor hit |
| **Apr 2025 - Sep 2025** | 6 | Operational Meltdown | OEE crashes, Defect rates spike, Logistics OTD drops |
| **Oct 2025 - Jun 2026** | 9 | Full Recovery | Gradual return to healthy baseline |

### Cross-Domain Correlations

IntelAI thrives on detecting correlations. Example causality paths embedded in the data:
1. **Supply Chain Crisis (2021-2022)**: Freight costs rise (Logistics) → Margins pressured (Finance)
2. **Talent Crisis (2024)**: Turnover spikes (People) → Hiring costs increase (Finance OPEX)
3. **Cyber Breach (2024-2025)**: API Latency/Incidents spike (IT) → Customer dissatisfaction (Growth NPS)
4. **Ops Meltdown (2025)**: Defect rate spikes (Operations) → Order Fulfillment delays (Logistics)

---

## Layer 2: Real Document Corpus (39 PDFs)

All documents are sourced from open-access repositories (primarily [Zenodo](https://zenodo.org)) under CC licenses and are real, non-synthetic files.

### `documents/` — Vendor Invoices (7 files, pre-existing)

Real vendor invoices for DocIntel scanner demos (invoice extraction, line-item parsing):

| File | Type | Use Case |
|------|------|----------|
| `AmazonWebServices.pdf` | AWS cloud invoice | Multi-line cloud services invoice |
| `coolblue1.pdf` | Retail invoice | Consumer electronics invoice |
| `FlipkartInvoice.pdf` | E-commerce invoice | International e-commerce invoice |
| `free_fiber.pdf` | Telecom invoice | ISP/fiber subscription invoice |
| `large_invoice_24p.pdf` | Multi-page invoice | 24-page complex invoice |
| `NetpresseInvoice.pdf` | Print media invoice | B2B service invoice |
| `QualityHosting.pdf` | Hosting invoice | Web hosting services invoice |

### `documents/annual_reports/` (4 files)

Real organizational annual reports — for board-level analytics, strategic AI demos:

| File | Organization | Domain Coverage |
|------|--------------|----------------|
| `EGI_Annual_Report_2025.pdf` | EGI (European Grid Infrastructure) | IT, Operations, Finance |
| `EHDEN_Annual_Report_Year2.pdf` | EHDEN (EU Health Data) | Operations, HR, Finance |
| `EHDEN_Year3_Partner_Report.pdf` | EHDEN | Operations, Growth |
| `ESIP_Annual_Report_2025.pdf` | ESIP (Earth Science Info Partners) | ESG, Operations, Finance |

**Source**: Zenodo (open access, CC-licensed)

### `documents/contracts/` (5 files)

Real SLAs and procurement contract documents — for contract extraction, legal AI demos:

| File | Document Type | Domain Coverage |
|------|---------------|----------------|
| `HeFDI_Service_Level_Agreement.pdf` | IT Service Level Agreement | IT, Operations |
| `HeFDI_Data_Talks_SLA.pdf` | Data service SLA | IT, Legal |
| `HeFDI_Data_Week_SLA.pdf` | Data service SLA | IT, Legal |
| `Legal_Regime_Smart_Contracts_Public_Procurement.pdf` | Legal research on contracts | Legal, Finance |
| `Public_Procurement_Contract_Research.pdf` | Procurement contract research | Operations, Finance |

**Source**: Zenodo (open access)

### `documents/financial_statements/` (9 files)

Real financial, ESG, and supply chain reports — for Finance, Logistics, ESG domain analytics:

| File | Content | Domain |
|------|---------|--------|
| `ESG_Corporate_Report.pdf` | Real corporate ESG report | ESG |
| `ESG_Score_Board_Structure_Financial_Performance.pdf` | ESG & board governance research | ESG, Finance |
| `FinSust_Financial_Sustainability_Report.pdf` | Financial sustainability task force report | Finance |
| `FinSust_Progress_Report.pdf` | Financial sustainability progress | Finance |
| `Supply_Chain_Disruptions_Logistics_Performance.pdf` | Supply chain disruption impact | Logistics |
| `Supply_Chain_Resilience_Assessment.pdf` | Supply chain resilience framework | Logistics, Operations |
| `Supply_Chain_Risk_Management.pdf` | Supply chain risk analysis | Logistics |
| `Post_COVID_Supply_Chain_Management.pdf` | Post-COVID supply chain recovery | Logistics, Finance |
| `Quantum_Revolution_Logistics_Supply_Chain.pdf` | Future of logistics/quantum tech | Logistics, IT |
| `Digital_Twin_End_to_End_Supply_Chain.pdf` | Digital twin for supply chain | Operations, IT |

**Source**: Zenodo (open access)

### `documents/hr_docs/` (2 files)

Real HR analytics documents — for People domain, workforce analytics AI demos:

| File | Content | Domain |
|------|---------|--------|
| `HR_Analytics_Research_Paper.pdf` | Human resources analytics research | People |
| `Predictive_Analytics_Workforce_Sustainability.pdf` | Predictive analytics for workforce | People, Operations |

**Source**: Zenodo (open access)

### `documents/invoices/` (1 file)

Additional invoice/billing domain research:

| File | Content | Domain |
|------|---------|--------|
| `Electronic_Invoicing_System_Impact.pdf` | Impact of e-invoicing systems research | Finance |

**Source**: Zenodo (open access)

### `documents/legal_docs/` (11 files)

Real legal, cybersecurity, governance, and compliance documents — for IT, Legal, ESG demos:

| File | Content | Domain |
|------|---------|--------|
| `NIS2_Cybersecurity_Compliance_Guide.pdf` | EU NIS2 directive compliance guide | IT, Legal |
| `CrowdStrike_2024_Incident_Analysis.pdf` | Real 2024 CrowdStrike incident post-mortem | IT |
| `Ransomware_Resilience_Recovery_Corporate.pdf` | Corporate ransomware resilience | IT, Operations |
| `Observability_Microservices_IT_Operations.pdf` | Observability in microservices/Spring Boot | IT |
| `AI_Cybersecurity_Realtime_Threat_Detection.pdf` | AI-driven real-time cybersecurity | IT |
| `DevOps_Impact_IT_Operations.pdf` | DevOps impact on IT operations | IT |
| `GDPR_Data_Breach_Notification_Guide.pdf` | GDPR breach notification obligations | Legal, IT |
| `GDPR_HR_Employee_Data_Protection.pdf` | HR & GDPR employee data protection | Legal, People |
| `GDPR_Personal_Data_Handling_App_Developers.pdf` | GDPR data handling for developers | Legal, IT |
| `Enterprise_AI_Governance_Handbook.pdf` | Enterprise AI governance for leaders | Legal, Operations |
| `Ransomware_Resilience_Recovery_Corporate.pdf` | Corporate ransomware resilience | IT, Legal |

**Source**: Zenodo (open access)

---

## How to Add Your Own Data

1. Preserve the `data/` folder structure.
2. Remove or overwrite the NexaCore demonstration CSV files.
3. Export your real metrics using the exact CSV schema: `period,category,segment,metric,value,unit,direction,source`
4. Add your own PDF documents to `data/documents/` subdirectories.
5. Use the ingestion script (see below) to load the data into IntelAI.

## Ingestion Script

We provide `scripts/seed_via_api.py` to load data via the REST API.
```bash
# Basic ingestion
python3 scripts/seed_via_api.py

# Ingest a specific domain
python3 scripts/seed_via_api.py --domain Finance

# View available scenarios in the dataset
python3 scripts/seed_via_api.py --scenario

# Validate schemas without uploading
python3 scripts/seed_via_api.py --validate

# View a summary report post-ingestion
python3 scripts/seed_via_api.py --report
```

*Reproducibility Guarantee: Re-running the data generation script will always yield the exact same NexaCore dataset values, ensuring reproducible demonstrations and tests.*
