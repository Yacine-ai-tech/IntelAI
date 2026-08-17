# SEV-1 incident bridge - INC-2023-0214

**Company:** OmniIntelOS S.A. - Niamey, Niger  
**Period:** 2023-02  
**Operating regime:** Cybersecurity breach and containment  
**Enterprise health:** 31.2/100 (Critical)  
**Attendees:** CEO, CFO, CTO, CISO, Chief People Officer

## Context

A credential-stuffing intrusion (13-14 Feb 2023) reaches a staging estate holding customer telemetry. Containment forces multi-day degradation; the churn and revenue consequences land over the next two quarters.

## Metrics reviewed

| Metric | Value |
|---|---|
| Monthly revenue | USD 656.7k |
| ARR | USD 5.89M |
| Gross margin | 50.5% |
| NRR | 97.3% |
| Logo churn | 2.78% |
| Uptime | 96.420% |
| Critical vulnerabilities | 31 |
| OEE | 50.0% |
| On-time delivery | 72.2% |
| Headcount | 97 |
| eNPS | +13 |
| Cash runway | 36.0 months |

## Domain analysis

Each line is computed from the month's data and compared against the thresholds published in the domain specification.

### Finance

- Gross Margin closed the period at 50.47% (average 50.47%), flat from 50.47% - below target (target >= 70%, risk at <= 25%).
- EBITDA Margin closed the period at -3.03% (average -3.03%), flat from -3.03% - in the risk band (target >= 25%, risk at <= 5%).
- Net Profit Margin closed the period at -9.23% (average -9.23%), flat from -9.23% - in the risk band (target >= 10%, risk at <= 0%).
- Cash Runway closed the period at 36 months (average 36 months), flat from 36 months - on target (target >= 12 months, risk at <= 4 months).
- Debt to Equity closed the period at 0.22x (average 0.22x), flat from 0.22x - on target (target <= 1.5x, risk at >= 3x).

### Growth

- Net Revenue Retention closed the period at 97.34% (average 97.34%), flat from 97.34% - below target (target >= 110%, risk at <= 90%).
- Monthly Churn Rate closed the period at 2.78% (average 2.78%), flat from 2.78% - above target (target <= 1.5%, risk at >= 5%).
- LTV to CAC Ratio closed the period at 1.57x (average 1.57x), flat from 1.57x - below target (target >= 3x, risk at <= 1.5x).
- CAC Payback Period closed the period at 22.22 months (average 22.22 months), flat from 22.22 months - above target (target <= 12 months, risk at >= 24 months).
- Rule of 40 closed the period at 47.31% (average 47.31%), flat from 47.31% - on target (target >= 40%, risk at <= 15%).

### People

- Annual Employee Turnover closed the period at 16.17% (average 16.17%), flat from 16.17% - above target (target <= 10%, risk at >= 20%).
- Time to Hire closed the period at 43.61 days (average 43.61 days), flat from 43.61 days - above target (target <= 35 days, risk at >= 65 days).
- Employee Net Promoter Score closed the period at 12.63 (average 12.63), flat from 12.63 - below target (target >= 30, risk at <= -10).
- Revenue per Employee closed the period at USD 81.1k (average USD 81.1k), flat from USD 81.1k - in the risk band (target >= 300000 USD, risk at <= 120000 USD).
- Offer Acceptance Rate closed the period at 55.81% (average 55.81%), flat from 55.81% - in the risk band (target >= 85%, risk at <= 60%).

### Operations

- Overall Equipment Effectiveness closed the period at 50.03% (average 50.03%), flat from 50.03% - in the risk band (target >= 85%, risk at <= 60%).
- Defect Rate closed the period at 9.90% (average 9.90%), flat from 9.90% - in the risk band (target <= 1%, risk at >= 4.5%).
- First Pass Yield closed the period at 84.80% (average 84.80%), flat from 84.80% - below target (target >= 92%, risk at <= 75%).
- Cycle Time Efficiency closed the period at 76.55% (average 76.55%), flat from 76.55% - in the risk band (target >= 95%, risk at <= 80%).

### Logistics

- On-Time Delivery Rate closed the period at 72.22% (average 72.22%), flat from 72.22% - in the risk band (target >= 95%, risk at <= 80%).
- Order Fulfillment Cycle Time closed the period at 57.42 hours (average 57.42 hours), flat from 57.42 hours - above target (target <= 48 hours, risk at >= 120 hours).
- Inventory Turnover closed the period at 3.93x (average 3.93x), flat from 3.93x - below target (target >= 6x, risk at <= 2.5x).
- Supplier Defect Rate closed the period at 0.83% (average 0.83%), flat from 0.83% - above target (target <= 0.5%, risk at >= 3%).
- Carrying Cost of Inventory closed the period at 26.72% (average 26.72%), flat from 26.72% - above target (target <= 25%, risk at >= 35%).

### IT

- System Uptime closed the period at 96.42% (average 96.42%), flat from 96.42% - in the risk band (target >= 99.95%, risk at <= 99%).
- Mean Time To Resolution closed the period at 3.78 hours (average 3.78 hours), flat from 3.78 hours - above target (target <= 0.5 hours, risk at >= 4 hours).
- Change Failure Rate closed the period at 15.50% (average 15.50%), flat from 15.50% - in the risk band (target <= 5%, risk at >= 15%).
- Critical Vulnerabilities closed the period at 31 (average 31), flat from 31 - in the risk band (target <= 0, risk at >= 5).
- API P99 Latency closed the period at 720.87 ms (average 720.87 ms), flat from 720.87 ms - above target (target <= 250 ms, risk at >= 1500 ms).

### ESG

- Renewable Energy Ratio closed the period at 33.06% (average 33.06%), flat from 33.06% - below target (target >= 60%, risk at <= 20%).
- Board Diversity Ratio closed the period at 29.94% (average 29.94%), flat from 29.94% - below target (target >= 40%, risk at <= 15%).
- Audit Compliance Score closed the period at 72% (average 72%), flat from 72% - in the risk band (target >= 98%, risk at <= 85%).
- Privacy Incident Count closed the period at 3 (average 3), flat from 3 - in the risk band (target <= 0, risk at >= 0.5).

## Decisions

- Isolate the staging estate from the transit VPC immediately, accepting customer-facing degradation.
- Retain external DFIR; begin forensic imaging.
- Enforce MFA across every environment without waiting for the post-mortem.
- Prepare regulator notification inside the 72-hour window.

## Actions

| Action | Owner | Due |
|---|---|---|
| Track the metrics above | Finance | 2023-02-28 |
| Report to the board | CEO | 2023-02-30 |

---

*OmniIntelOS S.A. is a fictional company; these minutes are generated for IntelAI demonstration purposes.*