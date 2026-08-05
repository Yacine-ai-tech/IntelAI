# NexaCore Technologies (Demonstration Profile)

> **Disclaimer**: IntelAI is a completely **company-agnostic** AI analytics copilot. NexaCore Technologies is a fictional reference dataset provided exclusively for demonstration, testing, and illustration purposes. You can (and should) replace this data with your own company's real data.

## Overview
**NexaCore Technologies** is a mid-market hybrid enterprise operating in both the B2B SaaS and light manufacturing sectors. Founded in 2012, the company provides cloud-connected industrial equipment and the accompanying software orchestration platform.

- **Business Model**: Hardware-enabled SaaS (Annual Recurring Revenue from software, plus hardware sales)
- **Geography**: Global (HQ in Chicago, IL, with secondary hubs in London and Singapore)
- **Target Market**: Enterprise and mid-market manufacturing, logistics, and supply chain operators.

## Data Structure
The demonstration dataset spans 78 months (January 2020 to June 2026) and embeds realistic business cycles and crises, providing a robust testbed for IntelAI's causal reasoning and correlation engines. 

The data is distributed across 7 core domains:

1. **[Finance](nexacore_finance_kpis.csv)**: Revenue, Margins, Cash Flow
2. **[Growth](nexacore_growth_kpis.csv)**: MRR, ARR, NRR, Churn, CAC
3. **[People](nexacore_people_kpis.csv)**: Headcount, Turnover, eNPS, Hiring
4. **[Operations](nexacore_operations_kpis.csv)**: OEE, Defect Rate, Yield
5. **[Logistics](nexacore_logistics_kpis.csv)**: OTD, Cycle Time, Freight
6. **[IT](nexacore_it_kpis.csv)**: Uptime, MTTR, Security, Deployments
7. **[ESG](nexacore_esg_kpis.csv)**: Carbon Footprint, Diversity, Compliance

## Replacing with Your Data
To use IntelAI with your own organization's data:
1. Clear the contents of the `data/` subdirectories (leaving the folder structure intact).
2. Export your KPIs into the required long-format CSV schema: `period,category,segment,metric,value,unit,direction,source`
3. Use the provided ingestion script to seed your database.

*See [DATA_SEEDING.md](../DATA_SEEDING.md) for full instructions on data preparation and ingestion.*
