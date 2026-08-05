# IntelAI Data Seeding Guide

> **Disclaimer**: IntelAI is a completely **company-agnostic** AI analytics copilot. NexaCore Technologies is a fictional reference dataset provided exclusively for demonstration, testing, and illustration purposes. You can (and should) replace this data with your own company's real data.

## Overview
This repository contains a realistic, deterministically generated dataset representing 78 months (2020-01 to 2026-06) of operations for NexaCore Technologies. 
The data spans 7 core business domains and embeds overlapping crises to demonstrate IntelAI's causal reasoning engines.

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
    └── (Existing PDF and reference documents)
```

## Dataset Characteristics
- **Long Format**: CSVs follow the schema `period,category,segment,metric,value,unit,direction,source`
- **78 Months**: 2020-01 through 2026-06.
- **Deterministic**: Data follows specific scenario multipliers rather than random distributions.

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

## Timeline and Scenario Epochs
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

## Cross-Domain Correlations
IntelAI thrives on detecting correlations. Example causality paths embedded in the data:
1. **Supply Chain Crisis (2021-2022)**: Freight costs rise (Logistics) → Margins pressured (Finance)
2. **Talent Crisis (2024)**: Turnover spikes (People) → Hiring costs increase (Finance OPEX)
3. **Cyber Breach (2024-2025)**: API Latency/Incidents spike (IT) → Customer dissatisfaction (Growth NPS)
4. **Ops Meltdown (2025)**: Defect rate spikes (Operations) → Order Fulfillment delays (Logistics)

## How to Add Your Own Data
1. Preserve the `data/` folder structure.
2. Remove or overwrite the NexaCore demonstration CSV files.
3. Export your real metrics using the exact CSV schema: `period,category,segment,metric,value,unit,direction,source`
4. Use the ingestion script (see below) to load the data into IntelAI.

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
