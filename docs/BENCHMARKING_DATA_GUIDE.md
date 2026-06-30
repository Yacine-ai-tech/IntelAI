# IntelAI Benchmarking Data Guide

## Overview

IntelAI includes a comprehensive benchmarking system with diverse business health scenarios based on real-world industry standards. The seeding system generates synthetic but realistic KPI data following established benchmarks from S&P 500 companies, SaaS industry reports, and operational excellence standards.

## Available Scenarios

### 1. **Healthy** (Default)
A baseline healthy company with strong performance across all domains, based on S&P 500 healthy company benchmarks:
- Finance: 72% gross margin, 15% net profit margin, healthy cash flow
- Growth: 110% Net Revenue Retention, 4.8% churn rate, 18-22% growth
- People: <10% turnover, 74+ engagement score
- Operations: >90% on-time delivery, <3% defect rate
- IT: >99.7% uptime, <8 hours MTTR, <15% change failure rate
- Logistics: >95% fill rate, efficient inventory turnover
- ESG: 75+ ESG score, decreasing emissions

### 2. **Declining Financial**
Financial distress scenario simulating:
- Major revenue decline (35% drop)
- Margin compression (25% reduction)
- Profit collapse (60% drop)
- Cash runway crisis (50% reduction)
- Debt explosion (250% increase in debt-to-equity)

### 3. **High Churn Crisis**
Customer retention crisis scenario:
- Churn rate explosion (350% increase)
- Customer loss (15% reduction)
- NRR collapse (15% drop below 100%)
- CAC spike (80% increase)
- Unit economics breakdown (LTV:CAC drops to 0.6)

### 4. **Operational Meltdown**
Operations failure scenario:
- Delivery failure (30% reduction in on-time delivery)
- Quality crisis (450% increase in defect rate)
- Major slowdown (220% increase in cycle time)
- Major outage (350% increase in unplanned downtime)
- Waste spike (280% increase in scrap rate)

### 5. **Talent Crisis**
HR/talent crisis scenario:
- Talent exodus (280% increase in turnover)
- Hiring freeze (220% increase in time to hire)
- Engagement collapse (35% drop in engagement score)
- Unfilled roles explosion (250% increase in open positions)
- Hiring quality drop (30% reduction in quality of hire)

### 6. **Cybersecurity Breach**
Security incident scenario:
- Major breach (500% increase in security incidents)
- Critical escalation (400% increase in critical incidents)
- Availability hit (uptime drops to 92%)
- SLA breach (compliance drops to 88%)
- Security score collapse (40% reduction)

### 7. **ESG Compliance Failure**
ESG compliance issues scenario:
- ESG rating drop (35% reduction)
- Emissions spike (180% increase)
- Privacy breach (500% increase in data privacy incidents)
- Supply chain issues (30% reduction in supplier compliance)
- Governance failure (40% reduction in board diversity)

## Benchmark Sources

The healthy baseline benchmarks are derived from:

### Financial Benchmarks
- **S&P 500 Performance**: Net profit margins 10-15% for healthy companies
- **SaaS Industry Standards**: Gross margins 79% (Bessemer Venture Partners, 2024)
- **Rule of 40**: Growth rate + profit margin >40% (Meritech Capital benchmarks)

### Growth Metrics
- **SaaS Benchmarks 2024**: NRR 110% (Benchmarkit, High Alpha)
- **Churn Rate**: <5% for healthy SaaS companies
- **LTV:CAC Ratio**: >3:1 for healthy unit economics

### People Metrics
- **HR Industry Standards**: <10% turnover for healthy companies
- **Engagement Scores**: 70+ indicates healthy workplace culture
- **Time to Hire**: <45 days for healthy talent acquisition

### Operations Metrics
- **Manufacturing Excellence**: >90% on-time delivery (industry standard)
- **Quality Standards**: <3% defect rate (Six Sigma baseline)
- **OEE Standards**: >85% indicates world-class operations

### IT & Security
- **DORA Metrics**: <15% change failure rate (elite performers)
- **Uptime Standards**: >99.9% for production systems
- **MTTR**: <8 hours for critical incident resolution

### ESG Metrics
- **ESG Ratings**: 70+ indicates strong ESG performance
- **Emissions Reduction**: Science-based targets require ongoing reduction
- **Governance Standards**: >30% board diversity indicates strong governance

## Using the Scenarios

### Command Line Usage

```bash
# Default healthy scenario
python -m src.data.seed

# Specific scenario
python -m src.data.seed declining_financial

# Generate all scenarios
./scripts/generate_all_scenarios.sh
```

### Programmatic Usage

```python
from src.data.seed import seed_database

# Seed with specific scenario
counts = seed_database(replace=True, scenario="high_churn_crisis")
print(f"Seeded {counts['kpi_rows']} KPI rows for crisis scenario")
```

## Data Characteristics

Each scenario generates:
- **36 months** of historical data (3 years)
- **134 metrics** across 7 domains
- **Deterministic generation** (same seed = same data)
- **Domain-specific anomalies** tailored to each scenario
- **Realistic seasonality** and noise patterns
- **Industry-validated base values** and trends

## Benchmarking Applications

The scenarios support:

1. **Risk Detection Testing**: Verify anomaly detection algorithms across different failure modes
2. **Forecast Validation**: Test ML forecasting models on different trend patterns
3. **Persona Testing**: Validate role-scoped access and insights across business conditions
4. **Demo Scenarios**: Show different business states for presentations
5. **Research Benchmarking**: Standardized test scenarios for academic/commercial benchmarking

## Research Integration

The benchmarking system supports research objectives by:
- Providing reproducible test scenarios (deterministic seeding)
- Grounding data in real industry benchmarks (citations available)
- Supporting multiple failure modes for robust testing
- Enabling cross-scenario comparison studies
- Facilitating standardized evaluation methodologies

## Citation

When using IntelAI benchmarking data in research or publications, please cite:

```
IntelAI Benchmarking System, 2026. Multi-domain KPI benchmarking 
with diverse business health scenarios based on S&P 500, SaaS industry 
standards, and operational excellence benchmarks. 
https://github.com/Yacine-ai-tech/IntelAI
```

## Contributing New Scenarios

To add new benchmarking scenarios:

1. Define the scenario in `UNHEALTHY_SCENARIOS` in `src/data/seed.py`
2. Research industry benchmarks for the specific failure mode
3. Add anomaly tuples with realistic multipliers
4. Document the benchmark sources
5. Test the scenario generation
6. Update this documentation

## References

- Bessemer Venture Partners. (2024). State of the Cloud 2024.
- Benchmarkit. (2024). 2024 SaaS Performance Metrics Benchmarks.
- FactSet. (2024). S&P 500 Profit Margin Analysis.
- High Alpha & OpenView. (2024). SaaS Benchmarks Report.
- Meritech Capital. (2024). Rule of 40 Analysis.
- DORA. (2024). Accelerate State of DevOps Report.
- GRI. (2024). Sustainability Reporting Standards.
