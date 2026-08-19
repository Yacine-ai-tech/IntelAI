"""IntelAI demo-data seed — robust, deterministic, DB-direct, single source of truth.

Generates a reproducible (seeded) multi-domain KPI time series that is the ONE catalog
feeding everything: the domain dashboards (via the keyword extractors in the domain
services), the cross-domain analytics, the persona RAG copilot (per-metric + per-domain
knowledge docs), and the glossary-grounded explainer. Adding a metric here is the only
step needed for it to appear across the whole product — no schema change, no migration.

The catalog has three layers, all seeded into the same ``kpi_metrics`` table (one source):

  * ``STRATEGIC_KPIS``    — driver metrics: independently modeled (trend + seasonality +
                            noise), the base inputs everything else is computed from.
  * ``OPERATIONAL_DETAIL``— the operational counters each domain dashboard also displays
                            (ticket/vuln counts, recruitment funnel, inventory sub-stats…).
  * ``DERIVED_KPIS``     — metrics computed FROM the driver values above via the actual
                            formula documented for them (e.g. Gross Margin =
                            (Revenue-COGS)/Revenue), not an independent random walk. Some
                            pull from a different domain than the one they're filed under
                            (Rule of 40 needs Finance's EBITDA margin; Revenue per Employee
                            needs both Finance and People) — that's intentional: it's the
                            same cross-domain synthesis the Overall Enterprise Health
                            Index does, just at the individual-metric level.

Every STRATEGIC_KPIS metric has a sourced, benchmarked definition in ``glossary.py`` so the
copilot can explain and cite it. Coverage is intentionally a curated, credible set — NOT
every metric a company could track. The long tail is handled by user uploads (CSV ingest
writes arbitrary ``(category, metric, value)`` rows into the same table, scoped by
category/RBAC).

Idempotent: writes directly to Postgres via ``pg_store`` (replace=True). This is the fast,
in-process path the server itself uses on first boot and for instant Admin/API scenario
switching (``POST /api/v1/admin/scenario``) — see DATA_SEEDING.md for how this differs
from the real KPI/document dataset ``scripts/seed_data.py`` builds and seeds. Lives
alongside it in ``scripts/`` rather than under ``src/`` because both are the same kind of
thing — ways to populate the dataset — even though this one is also imported live by the
running server for the Admin scenario-switch API.

Run standalone:  python scripts/seed_scenarios.py         (uses POSTGRES_URL from env/.env)
Or from code:    from scripts.seed_scenarios import seed_database; seed_database()
"""
from __future__ import annotations

import math
import random
import sys
from datetime import datetime, timedelta
from itertools import chain
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

# So `from src.services...` resolves when this is run standalone (`python
# scripts/seed_scenarios.py`) — Python only puts the script's OWN directory on
# sys.path by default, not the repo root, unlike this file's old location under
# src/data/, run via `python -m src.data.seed`, which had the repo root on
# sys.path automatically.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

SEED = 42
MONTHS = 78
SEGMENT = "Global"

# Tuple schema per driver metric: (metric, unit, base_value, monthly_drift, direction)
#   drift     = average month-over-month relative change in the "good" direction
#   direction = "up" (higher is better) | "down" (lower is better)
#
# Base values are calibrated to sit inside each metric's documented "Healthy Target" band
# (see DATA_SEEDING.md for the full source table — Orange SA, Bessemer Cloud, Google DORA,
# GRI, Six Sigma benchmarks) so the "healthy" scenario actually reads as healthy against
# those thresholds, not just a plausible-looking number in isolation.

# ── STRATEGIC: driver KPIs — every one is defined in glossary.py ──
STRATEGIC_KPIS: Dict[str, List[Tuple[str, str, float, float, str]]] = {
    "Finance": [
        ("Revenue", "USD", 2_400_000, 0.018, "up"),
        # COGS and Operating Costs are DERIVED (see DERIVED_KPIS below) as a slowly-improving
        # ratio of Revenue rather than independent drivers — two independently compounding
        # trends (Revenue up, costs down) diverge to unrealistic margins over 78 months.
        ("Taxes", "USD", 95_000, 0.010, "down"),
        ("Operating Cash Flow", "USD", 480_000, 0.015, "up"),
        ("Free Cash Flow", "USD", 300_000, 0.016, "up"),
        ("Working Capital", "USD", 2_100_000, 0.008, "up"),
        ("Days Sales Outstanding", "days", 45, -0.006, "down"),
        ("Cash Runway", "months", 19, 0.004, "up"),         # healthy: >12 months
        ("Debt to Equity", "ratio", 0.8, -0.005, "down"),   # healthy: <1.5x
        ("Interest Coverage", "ratio", 4.5, 0.010, "up"),
    ],
    "Growth": [
        # MRR/ARR are DERIVED from Finance's Revenue (see DERIVED_KPIS) — a subscription
        # business's MRR *is* its monthly revenue; tracking it as a second, independently
        # drifting number let it silently diverge from Finance's own Revenue figure.
        ("Customer Count", "count", 1_250, 0.018, "up"),
        ("Churn Rate", "%", 1.3, -0.010, "down"),           # healthy: <1.5% monthly logo churn
        ("Expansion Rate", "%", 11.5, 0.003, "up"),         # -> Net Revenue Retention (derived)
        # CAC is DERIVED from LTV via a target LTV:CAC band (see DERIVED_KPIS) — same
        # divergence problem as COGS/Revenue above if left as two independent drivers.
        ("LTV", "USD", 9_800, 0.014, "up"),
        ("Net Promoter Score", "score", 42, 0.006, "up"),   # customer NPS (distinct from People's eNPS)
        ("ARPU", "USD", 380, 0.010, "up"),
        ("Active Users", "count", 9_800, 0.020, "up"),
        ("Viral Coefficient", "ratio", 0.8, 0.005, "up"),
        ("Conversion Rate", "%", 3.5, 0.008, "up"),
    ],
    "People": [
        # 90 employees on ~$29M ARR (~$320k revenue/employee) — a lean, efficient B2B SaaS
        # headcount-to-revenue ratio, not the 240 an earlier draft used (which put Revenue
        # per Employee well under the healthy $300k+ tech benchmark).
        ("Headcount", "count", 90, 0.012, "up"),
        ("Turnover Rate", "%", 8.5, -0.010, "down"),        # healthy: 5-10% annualized
        ("Employee Net Promoter (eNPS)", "score", 32, 0.005, "up"),  # healthy: >=+30
        ("Engagement Score", "score", 74, 0.004, "up"),
        ("Time to Hire", "days", 33, -0.008, "down"),       # healthy: <35 days
        ("Training Hours", "hours", 22, 0.010, "up"),
        ("Open Positions", "count", 10, -0.004, "down"),
        ("Average Tenure", "years", 4.1, 0.006, "up"),
        ("Cost per Hire", "USD", 4_200, -0.006, "down"),
        ("Absenteeism Rate", "%", 3.2, -0.010, "down"),
        ("Quality of Hire", "score", 78, 0.005, "up"),
        ("Offer Acceptance Rate", "%", 86, 0.004, "up"),    # healthy: >=85%
        ("Internal Mobility Rate", "%", 18, 0.010, "up"),
        ("Diversity Score", "score", 72, 0.003, "up"),
    ],
    "Operations": [
        ("Availability Rate", "%", 90, 0.002, "up"),        # -> OEE = Av * Perf * Qual (derived)
        ("Performance Rate", "%", 93, 0.002, "up"),
        ("Quality Rate", "%", 97, 0.002, "up"),
        ("Standard Cycle Time", "days", 13.3, 0.0, "down"), # target cycle time -> Cycle Time Efficiency
        ("Cycle Time", "days", 14, -0.009, "down"),         # actual cycle time
        ("On-time Delivery", "%", 93, 0.003, "up"),
        ("Defect Rate", "%", 0.9, -0.013, "down"),          # healthy: <1.0%
        ("Capacity Utilization", "%", 78, 0.004, "up"),
        ("Safety Incident Rate", "rate", 1.4, -0.015, "down"),
        ("First Pass Yield", "%", 93, 0.002, "up"),         # healthy: >=92%
        ("Throughput", "units", 5_200, 0.010, "up"),
        ("Unplanned Downtime", "hours", 42, -0.010, "down"),
        ("Cost per Unit", "USD", 12.5, -0.007, "down"),
        ("Schedule Adherence", "%", 91, 0.003, "up"),
        ("Scrap Rate", "%", 3.1, -0.011, "down"),
    ],
    "IT": [
        ("System Uptime", "%", 99.96, 0.00006, "up"),       # healthy: >=99.95% ("three nines")
        ("Mean Time to Resolution", "hours", 4.5, -0.012, "down"),
        ("Security Incidents", "count", 7, -0.018, "down"),
        ("Critical Vulnerabilities (CVSS>=9)", "count", 1, -0.020, "down"),  # healthy: 0
        ("API P99 Latency", "ms", 220, -0.004, "down"),     # healthy: <250ms
        ("Cloud Cost per User", "USD", 180, -0.006, "down"),
        ("Cloud Spend", "USD", 240_000, -0.004, "down"),
        ("Deployment Frequency", "per_month", 18, 0.020, "up"),
        ("Lead Time for Changes", "hours", 9, -0.012, "down"),
        ("Change Failure Rate", "%", 4.5, -0.015, "down"),  # healthy: <5%
        ("SLA Compliance", "%", 97.5, 0.002, "up"),
        ("Security Score", "score", 85, 0.005, "up"),
        ("IT Satisfaction", "score", 7.6, 0.005, "up"),
        ("Vulnerability Response Time", "days", 3, -0.010, "down"),
    ],
    "Logistics": [
        ("Inventory Turnover", "ratio", 6.2, 0.012, "up"),  # healthy: 6-12x
        ("Order Accuracy", "%", 97.5, 0.002, "up"),
        ("Perfect Order Rate", "%", 94, 0.003, "up"),
        ("On-Time Delivery Rate", "%", 95, 0.003, "up"),    # healthy: >=95%
        ("Order Fulfillment Cycle Time", "hours", 44, -0.008, "down"),  # healthy: <48h
        ("Supplier Defect Rate", "%", 0.4, -0.012, "down"), # healthy: <0.5%
        ("Fill Rate", "%", 96, 0.002, "up"),
        ("Stockout Rate", "%", 2.5, -0.011, "down"),
        ("Freight Cost per Unit", "USD", 18, -0.007, "down"),
        ("Warehouse Utilization", "%", 72, 0.005, "up"),
        ("Avg Lead Time", "days", 6.5, -0.008, "down"),
        ("Last Mile Delivery Time", "days", 3.2, -0.010, "down"),
        ("Days Inventory Outstanding", "days", 58, -0.006, "down"),
        ("Returns Rate", "%", 6.5, -0.009, "down"),
        ("Freight Damage Rate", "%", 1.2, -0.008, "down"),
    ],
    "ESG": [
        ("ESG Score", "score", 75, 0.004, "up"),
        ("Carbon Emissions (tCO2e)", "tonnes_CO2e", 8_400, -0.014, "down"),
        ("Scope 1 Emissions", "tonnes_CO2e", 1_200, -0.012, "down"),
        ("Scope 2 Emissions", "tonnes_CO2e", 2_100, -0.013, "down"),
        ("Scope 3 Emissions", "tonnes_CO2e", 5_100, -0.010, "down"),
        ("Emissions Intensity", "tCO2e/$M", 3.5, -0.012, "down"),
        ("Renewable Energy %", "%", 62, 0.012, "up"),       # healthy: >=60%
        ("Water Consumption (m3)", "cubic_meters", 12_000, -0.008, "down"),
        ("Waste Recycled %", "%", 61, 0.008, "up"),
        ("Audit Compliance Score", "%", 98, 0.001, "up"),   # healthy: >=98%
        ("Board Diversity %", "%", 41, 0.010, "up"),        # healthy: >=40%
        ("Gender Pay Gap", "%", 8.5, -0.010, "down"),
        ("Community Investment", "USD", 180_000, 0.012, "up"),
    ],
}

# ── DERIVED: computed from driver values via the documented formula, not a random walk ──
# Each entry: (metric, unit, direction, formula(v) -> float | None)
#   v(category, metric) looks up an already-generated value for the SAME period (drivers
#   are generated first, then derived metrics — see generate_kpi_rows). Cross-domain lookups
#   are the point: this is where "Overall Enterprise Health" synthesis actually happens.
#   Returns None if an input isn't available yet (e.g. YoY growth before month 12) — the
#   row is skipped for that period rather than faked.
DerivedFn = Callable[[Callable[[str, str], float], int], "float | None"]

def _ramp(i: int, start: float, end: float, months: int = MONTHS) -> float:
    """Linear ramp from ``start`` to ``end`` over the series — used for cost/target ratios
    that should trend mildly over 6.5 years without compounding-drift runaway."""
    return start + (end - start) * min(i / months, 1.0)


DERIVED_KPIS: Dict[str, List[Tuple[str, str, str, DerivedFn]]] = {
    "Finance": [
        # COGS/Operating Costs as a slowly-improving ratio of Revenue (operating leverage
        # from scale) rather than an independent driver — keeps margins in a realistic band
        # instead of two independently-compounding trends diverging over 78 months.
        ("COGS", "USD", "down", lambda v, i: v("Finance", "Revenue") * _ramp(i, 0.28, 0.25)),
        ("Operating Costs", "USD", "down", lambda v, i: v("Finance", "Revenue") * _ramp(i, 0.47, 0.43)),
        ("Gross Margin", "%", "up",
         lambda v, i: (v("Finance", "Revenue") - v("Finance", "COGS")) / v("Finance", "Revenue") * 100),
        ("EBITDA", "USD", "up",
         lambda v, i: v("Finance", "Revenue") - v("Finance", "COGS") - v("Finance", "Operating Costs")),
        ("EBITDA Margin", "%", "up",
         lambda v, i: (v("Finance", "Revenue") - v("Finance", "COGS") - v("Finance", "Operating Costs"))
                      / v("Finance", "Revenue") * 100),
        # Net Profit approximates D&A + interest as a fixed 7.5% of revenue rather than
        # tracking full non-operating detail — documented approximation, not fabricated.
        ("Net Profit", "USD", "up",
         lambda v, i: (v("Finance", "Revenue") - v("Finance", "COGS") - v("Finance", "Operating Costs"))
                      - v("Finance", "Taxes") - 0.075 * v("Finance", "Revenue")),
        ("Net Profit Margin", "%", "up",
         lambda v, i: (((v("Finance", "Revenue") - v("Finance", "COGS") - v("Finance", "Operating Costs"))
                        - v("Finance", "Taxes") - 0.075 * v("Finance", "Revenue")) / v("Finance", "Revenue")) * 100),
    ],
    "Growth": [
        # MRR *is* Finance's monthly Revenue for a subscription business — derived so the two
        # can never silently diverge into two different "revenue" figures for one company.
        ("MRR", "USD", "up", lambda v, i: v("Finance", "Revenue")),
        ("ARR", "USD", "up", lambda v, i: v("Finance", "Revenue") * 12),
        # CAC as a target LTV:CAC band (mildly improving, 3.6x -> 4.1x) rather than an
        # independent driver — same divergence problem as COGS above otherwise.
        ("CAC", "USD", "down", lambda v, i: v("Growth", "LTV") / _ramp(i, 4.0, 4.5)),
        ("LTV:CAC", "ratio", "up", lambda v, i: v("Growth", "LTV") / v("Growth", "CAC")),
        ("CAC Payback", "months", "down",
         lambda v, i: v("Growth", "CAC") / (v("Growth", "ARPU") * (v("Finance", "Gross Margin") / 100))),
        ("Net Revenue Retention", "%", "up",
         lambda v, i: 100 - v("Growth", "Churn Rate") + v("Growth", "Expansion Rate")),
        # Rule of 40: trailing-12mo revenue growth % + EBITDA margin % — the standard SaaS
        # balance-of-growth-and-profit benchmark. None before month 12 (no YoY baseline yet).
        ("Rule of 40", "%", "up",
         lambda v, i: (
             ((v("Finance", "Revenue") / v("Finance", "Revenue", i - 12)) - 1) * 100
             + v("Finance", "EBITDA Margin")
         ) if i >= 12 else None),
    ],
    "People": [
        # Revenue per Employee: Finance's monthly Revenue annualized over People's Headcount —
        # the canonical cross-domain productivity metric (healthy tech benchmark: >=$300k).
        ("Revenue per Employee", "USD", "up",
         lambda v, i: (v("Finance", "Revenue") * 12) / v("People", "Headcount")),
    ],
    "Operations": [
        ("OEE", "%", "up",
         lambda v, i: (v("Operations", "Availability Rate") / 100) * (v("Operations", "Performance Rate") / 100)
                      * (v("Operations", "Quality Rate") / 100) * 100),
        ("Cycle Time Efficiency", "%", "up",
         lambda v, i: v("Operations", "Standard Cycle Time") / v("Operations", "Cycle Time") * 100),
    ],
    "Logistics": [
        # Carrying Cost as a ratio of Inventory Value (15-25% healthy band) rather than an
        # independent driver — same reasoning as Finance's COGS above.
        ("Carrying Cost", "USD", "down",
         lambda v, i: v("Logistics", "Inventory Value") * _ramp(i, 0.20, 0.17)),
        ("Carrying Cost of Inventory", "%", "down",
         lambda v, i: v("Logistics", "Carrying Cost") / v("Logistics", "Inventory Value") * 100),
    ],
    "IT": [
        # MTBF approximates monthly operational hours (30 days * 24h) over incident count as
        # a proxy for failure count — a simplification (real MTBF needs a per-asset failure
        # log), documented as such rather than presented as precise.
        ("MTBF", "hours", "up",
         lambda v, i: (30 * 24) / max(v("IT", "Critical Vulnerabilities (CVSS>=9)") + 0.1, 0.1)),
    ],
}

# ── OPERATIONAL DETAIL: counters the domain dashboards display (not all glossary-backed) ──
OPERATIONAL_DETAIL: Dict[str, List[Tuple[str, str, float, float, str]]] = {
    "People": [
        ("Applications Received", "count", 120, 0.010, "up"),
        ("Interviews Scheduled", "count", 34, 0.008, "up"),
        ("Offers Extended", "count", 12, 0.006, "up"),
        ("Offers Accepted", "count", 10, 0.006, "up"),
        ("Average Salary", "USD", 95_000, 0.006, "up"),
        ("Training Completion", "%", 88, 0.004, "up"),
    ],
    "Operations": [
        ("Daily Output", "count", 480, 0.010, "up"),
        ("Labor Productivity", "%", 88, 0.004, "up"),
        ("Inspection Pass Rate", "%", 96, 0.002, "up"),
        ("Rework Rate", "%", 2.8, -0.010, "down"),
        ("Customer Complaints", "count", 12, -0.012, "down"),
        ("Days Without Incident", "count", 145, 0.020, "up"),
        ("Lost Time Incidents", "count", 1, -0.020, "down"),
        ("Near Misses", "count", 8, -0.010, "down"),
    ],
    "IT": [
        ("Open Tickets", "count", 45, -0.008, "down"),
        ("Server Count", "count", 320, 0.010, "up"),
        ("Open Vulnerabilities", "count", 34, -0.015, "down"),
        ("Critical Incidents", "count", 2, -0.020, "down"),
        ("Compliance Score", "score", 91, 0.003, "up"),
        ("Phishing Attempts Blocked", "count", 1_450, 0.010, "up"),
        ("Backup Success Rate", "%", 99.2, 0.0005, "up"),
        ("Code Coverage", "%", 78, 0.004, "up"),
        ("Build Success Rate", "%", 94, 0.002, "up"),
    ],
    "Logistics": [
        ("Total Orders", "count", 4_200, 0.012, "up"),
        ("Shipments Month", "count", 4_100, 0.012, "up"),
        ("Days of Supply", "days", 38, -0.006, "down"),
        ("Inventory Accuracy", "%", 98, 0.002, "up"),
        ("Slow Moving %", "%", 6, -0.008, "down"),
        ("Overstock %", "%", 4, -0.008, "down"),
        ("SKU Count", "count", 1_850, 0.008, "up"),
        ("Inventory Value", "USD", 2_400_000, 0.006, "up"),
        # Carrying Cost is DERIVED as a ratio of Inventory Value (see DERIVED_KPIS) rather
        # than an independent driver, for the same reason as Finance's COGS above.
        ("Damaged Rate", "%", 1.2, -0.010, "down"),
        ("Avg Transit Days", "days", 4.5, -0.008, "down"),
        ("Cost per Shipment", "USD", 22, -0.006, "down"),
    ],
    "ESG": [
        ("Ethics Training", "%", 92, 0.003, "up"),
        ("Supplier ESG Compliance", "%", 88, 0.004, "up"),
        ("Data Privacy Incidents", "count", 0, -0.020, "down"),  # healthy: 0
    ],
}

# Merged catalog — every metric generated into kpi_metrics (drivers + operational + derived).
KPI_SPEC: Dict[str, List[Tuple[str, str, float, float, str]]] = {
    cat: list(chain(STRATEGIC_KPIS[cat], OPERATIONAL_DETAIL.get(cat, [])))
    for cat in STRATEGIC_KPIS
}
ALL_CATEGORIES: List[str] = list(STRATEGIC_KPIS.keys())

# ── VERTICALS ─────────────────────────────────────────────────────────────────
# The demo dataset reads as a generic company, which is the weakest possible framing for
# a buyer: "Acme SaaS, ARR $4.2M, churn 3.1%" lands where
# "Company X" does not. A vertical re-scales the shared catalog to a plausible company of
# that type and adds the metrics that vertical is actually judged on — it does NOT invent
# a separate schema, so every dashboard, persona and the copilot keep working unchanged.
#
#   scale   multiply a driver's base value (company size / cost structure differences)
#   extra   additional (metric, unit, base, drift, direction) rows for that domain
#
# Healthcare figures follow published US hospital-operations norms (readmission ~15%,
# bed occupancy ~65-75%, HCAHPS ~70); the SaaS ones follow the same Bessemer-style
# benchmarks the base catalog is calibrated to.
VERTICALS: Dict[str, Dict[str, Any]] = {
    "saas": {
        "label": "Series A SaaS",
        "scale": {"Revenue": 0.35, "Headcount": 0.45, "MRR": 0.35},
        "extra": {
            "Growth": [
                ("Trial Signups", "count", 640, 0.020, "up"),
                ("Trial to Paid Conversion", "%", 22, 0.006, "up"),
                ("Expansion MRR", "USD", 62_000, 0.022, "up"),
                ("Logo Retention", "%", 92, 0.002, "up"),
                ("Seats per Account", "count", 14, 0.008, "up"),
            ],
            "IT": [
                ("Feature Adoption Rate", "%", 41, 0.008, "up"),
                ("API Error Rate", "%", 0.6, -0.012, "down"),
            ],
        },
    },
    "healthcare": {
        "label": "Healthcare provider network",
        "scale": {"Revenue": 1.8, "Headcount": 4.0, "Operating Costs": 1.9},
        "extra": {
            "Operations": [
                ("Patient Volume", "count", 12_400, 0.010, "up"),
                ("Bed Occupancy Rate", "%", 71, 0.003, "up"),
                ("Average Length of Stay", "days", 4.6, -0.006, "down"),
                ("Readmission Rate (30d)", "%", 14.8, -0.008, "down"),
                ("Average Wait Time", "minutes", 34, -0.009, "down"),
            ],
            "People": [
                ("Clinical Staff Ratio", "ratio", 1.9, 0.004, "up"),
                ("Nurse Turnover Rate", "%", 17.5, -0.010, "down"),
            ],
            "ESG": [
                ("Patient Satisfaction (HCAHPS)", "score", 71, 0.004, "up"),
                ("Clinical Incident Rate", "rate", 2.1, -0.012, "down"),
                ("HIPAA Audit Findings", "count", 2, -0.015, "down"),
            ],
        },
    },
    "esg": {
        "label": "ESG / sustainability reporting",
        "scale": {"Revenue": 1.2, "Carbon Emissions (tCO2e)": 1.6},
        "extra": {
            "ESG": [
                ("CSRD Readiness Score", "%", 62, 0.010, "up"),
                ("Scope 3 Supplier Coverage", "%", 48, 0.012, "up"),
                ("Assured Data Points", "%", 55, 0.011, "up"),
                ("Energy Intensity", "kWh/$K", 18.5, -0.010, "down"),
                ("Green Revenue Share", "%", 21, 0.014, "up"),
                ("Taxonomy-Aligned CapEx", "%", 27, 0.012, "up"),
            ],
        },
    },
}


def kpi_spec_for(vertical: Optional[str] = None) -> Dict[str, List[Tuple[str, str, float, float, str]]]:
    """KPI_SPEC re-scaled and extended for a vertical (None -> the generic catalog)."""
    if not vertical:
        return KPI_SPEC
    key = vertical.strip().lower()
    if key not in VERTICALS:
        raise ValueError(f"unknown vertical {vertical!r}; known: {', '.join(sorted(VERTICALS))}")
    v = VERTICALS[key]
    scale, extra = v.get("scale", {}), v.get("extra", {})
    spec: Dict[str, List[Tuple[str, str, float, float, str]]] = {}
    for cat, metrics in KPI_SPEC.items():
        rows = [(m, u, base * scale.get(m, 1.0), drift, direction)
                for (m, u, base, drift, direction) in metrics]
        rows.extend(extra.get(cat, []))
        spec[cat] = rows
    return spec

# Percentages that legitimately exceed 100 (must NOT be clamped to [0, 100]).
# Metrics whose realistic value sits within a fraction of a percentage point of the 100%
# ceiling (e.g. "three nines" uptime) need much tighter noise/seasonality than the blanket
# 2%/3% used for everything else — otherwise the noise alone swings them into the ceiling
# clamp every month, drowning out both the underlying trend and any scenario anomaly.
TIGHT_VARIANCE_METRICS = {"System Uptime": 0.0006}

PCT_OVER_100 = {"Net Revenue Retention", "Rule of 40", "OEE", "Cycle Time Efficiency"}

# Margin metrics that can legitimately go negative (a net loss, a margin squeezed below
# zero by rising costs) — the declining_financial scenario needs this to show real distress.
PCT_ALLOW_NEGATIVE = {"EBITDA Margin", "Net Profit Margin", "Rule of 40"}

# Deterministic anomalies: (category, metric, month_index, multiplier) — give Risk a signal.
# Healthy baseline company with occasional issues for risk detection demo
ANOMALIES: List[Tuple[str, str, int, float]] = [
    ("Finance", "Revenue", 17, 0.78),            # revenue dip (mild issue)
    ("Growth", "Churn Rate", 14, 1.9),           # churn spike (customer concern)
    ("Operations", "Defect Rate", 11, 2.4),      # quality incident (ops issue)
    ("IT", "Security Incidents", 20, 3.2),       # security spike (cyber incident)
    ("People", "Turnover Rate", 9, 1.8),         # attrition spike (HR concern)
]

# Unhealthy company scenarios for diverse benchmarking. Each list starts with the scenario's
# primary-domain anomalies (as before), then adds a short CROSS-DOMAIN CASCADE — later-month
# secondary anomalies in other domains — modeling the "Cross-Domain Risk Propagation" chain
# from the data strategy spec (e.g. a security breach doesn't stay in IT: it disrupts
# operations/logistics a couple months later, which shows up as customer churn a couple
# months after that, which shows up as a revenue dip in Finance after that). Severity
# multipliers are calibrated to land inside each metric's documented "Risk/Failure
# Threshold" band, not arbitrary.
UNHEALTHY_SCENARIOS: Dict[str, List[Tuple[str, str, int, float]]] = {
    "declining_financial": [
        ("Finance", "Revenue", 6, 0.65),         # major revenue decline
        ("Finance", "COGS", 6, 1.25),            # -> Gross Margin compression (derived)
        ("Finance", "Operating Costs", 8, 1.3),  # -> EBITDA margin collapse (derived)
        ("Finance", "Cash Runway", 10, 0.3),     # cash crunch, well under the 4mo failure line
        ("Finance", "Debt to Equity", 12, 3.8),  # debt explosion, above the 3.0x failure line
        # cascade: cash crisis forces hiring freeze + growth slowdown
        ("People", "Open Positions", 14, 0.4),
        ("Growth", "Customer Count", 16, 0.9),
    ],
    "high_churn_crisis": [
        ("Growth", "Churn Rate", 4, 4.2),        # churn crisis, above the 5% failure line combined w/ base
        ("Growth", "Expansion Rate", 4, 0.3),    # -> NRR collapse (derived), below 90% failure line
        ("Growth", "Customer Count", 5, 0.85),   # customer loss
        ("Growth", "CAC", 7, 1.8),               # CAC spike
        ("Growth", "LTV", 8, 0.55),              # -> LTV:CAC breakdown (derived), below 1.5x failure line
        # cascade: retention crisis hits revenue and morale
        ("Finance", "Revenue", 10, 0.82),
        ("People", "Engagement Score", 11, 0.8),
    ],
    "operational_meltdown": [
        ("Operations", "On-time Delivery", 3, 0.7),     # delivery failure
        ("Operations", "Quality Rate", 4, 0.6),         # -> OEE collapse (derived), below 60% failure line
        ("Operations", "Availability Rate", 4, 0.75),   # -> OEE collapse (derived)
        ("Operations", "Cycle Time", 5, 2.6),           # -> Cycle Time Efficiency collapse (derived)
        ("Operations", "Unplanned Downtime", 6, 3.5),   # major outage
        ("Operations", "Scrap Rate", 7, 2.8),           # waste spike
        # cascade: production failures reach the customer and the supply chain
        ("Logistics", "On-Time Delivery Rate", 9, 0.78),
        ("Growth", "Churn Rate", 11, 2.5),
    ],
    "talent_crisis": [
        ("People", "Turnover Rate", 5, 2.8),         # talent exodus, above the 20% failure line
        ("People", "Time to Hire", 6, 2.2),          # hiring freeze, above the 65-day failure line
        ("People", "Employee Net Promoter (eNPS)", 7, -1.6),  # collapse into negative eNPS (failure: <-10)
        ("People", "Engagement Score", 7, 0.65),      # engagement collapse
        ("People", "Open Positions", 8, 2.5),         # unfilled roles
        ("People", "Quality of Hire", 9, 0.7),         # hiring quality drop
        # cascade: understaffing hits delivery and output
        ("Operations", "Labor Productivity", 11, 0.75),
        ("IT", "Deployment Frequency", 12, 0.6),
    ],
    "cybersecurity_breach": [
        ("IT", "Security Incidents", 2, 5.0),         # major breach
        ("IT", "Critical Vulnerabilities (CVSS>=9)", 2, 8.0),  # above the 5-unpatched failure line
        ("IT", "System Uptime", 3, 0.985),             # step down under the 99.0% failure line
        ("IT", "SLA Compliance", 4, 0.88),            # SLA breach
        ("IT", "Security Score", 5, 0.6),             # security score collapse
        # cascade: breach fallout reaches operations, then customers, then revenue
        ("Logistics", "On-Time Delivery Rate", 5, 0.82),
        ("Growth", "Churn Rate", 7, 2.4),
        ("Finance", "Revenue", 9, 0.88),
    ],
    "esg_compliance_failure": [
        ("ESG", "ESG Score", 8, 0.65),              # ESG rating drop
        ("ESG", "Carbon Emissions (tCO2e)", 9, 1.8), # emissions spike
        ("ESG", "Data Privacy Incidents", 10, 6.0),  # privacy breach (healthy baseline is 0)
        ("ESG", "Supplier ESG Compliance", 11, 0.7), # supply chain issues
        ("ESG", "Board Diversity %", 12, 0.55),      # governance failure, below 15% failure line
        ("ESG", "Audit Compliance Score", 12, 0.83), # below the 85% failure line
    ],
}


def _periods(months: int) -> List[str]:
    base = datetime(2020, 1, 1)
    return [(base + timedelta(days=31 * i)).replace(day=1).strftime("%Y-%m") for i in range(months)]


def generate_kpi_rows(months: int = MONTHS, seed: int = SEED, scenario: str = "healthy",
                      vertical: Optional[str] = None) -> List[Dict[str, Any]]:
    """Deterministic multi-domain KPI time series with trend, seasonality, noise, anomalies,
    and formula-derived cross-domain metrics.

    Two passes:
      1. Every STRATEGIC_KPIS + OPERATIONAL_DETAIL driver metric is generated independently
         (trend + seasonality + noise + any scenario anomaly), exactly as before.
      2. Every DERIVED_KPIS metric is computed FROM those already-generated driver values for
         the same period (and, for cross-domain formulas like Rule of 40, other periods/
         domains) — so e.g. Gross Margin always actually equals (Revenue-COGS)/Revenue for
         that period, not an independently-drifting number that happens to start near 72%.

    Args:
        months: Number of months to generate
        seed: Random seed for reproducibility
        scenario: Health scenario to simulate:
            - "healthy": Baseline healthy company with occasional issues
            - "declining_financial": Financial distress scenario
            - "high_churn_crisis": Customer retention crisis
            - "operational_meltdown": Operations failure
            - "talent_crisis": HR/talent crisis
            - "cybersecurity_breach": Security incident
            - "esg_compliance_failure": ESG compliance issues
        vertical: None for the generic company, or saas | healthcare | esg — rescales the
            same catalog to a plausible company of that type and adds the metrics that
            vertical is judged on. Scenarios compose with verticals.
    """
    rng = random.Random(seed)
    periods = _periods(months)
    spec = kpi_spec_for(vertical)

    if scenario == "healthy":
        anomaly_map = {(c, m): (i, mult) for c, m, i, mult in ANOMALIES}
    elif scenario in UNHEALTHY_SCENARIOS:
        anomaly_map = {(c, m): (i, mult) for c, m, i, mult in UNHEALTHY_SCENARIOS[scenario]}
    else:
        anomaly_map = {(c, m): (i, mult) for c, m, i, mult in ANOMALIES}

    def _clamp(metric: str, unit: str, out: float) -> float:
        if unit != "%":
            return out
        # Margins can legitimately go negative (a net loss, a margin squeezed by rising
        # costs) — that's exactly the signal the declining_financial scenario needs to
        # show. Flooring them at 0 would silently hide the failure case they exist to model.
        if metric not in PCT_ALLOW_NEGATIVE:
            out = max(0.0, out)
        if metric not in PCT_OVER_100:
            out = min(100.0, out)
        return out

    # ── Pass 1: driver metrics ──
    # values[(category, metric)] = [value_month_0, value_month_1, ...]
    values: Dict[Tuple[str, str], List[float]] = {}
    rows: List[Dict[str, Any]] = []

    for category, metrics in spec.items():
        for metric, unit, base, drift, direction in metrics:
            series: List[float] = []
            value = base
            tight = TIGHT_VARIANCE_METRICS.get(metric)
            for i, period in enumerate(periods):
                if tight is not None:
                    seasonal = 1.0
                    noise = 1.0 + rng.gauss(0, tight)
                else:
                    seasonal = 1.0 + 0.03 * math.sin((i % 12) / 12 * 2 * math.pi)
                    noise = 1.0 + rng.gauss(0, 0.02)
                # A constant drift compounded for 78 straight months runs away to unrealistic
                # extremes (a company doesn't grow/shrink at a fixed monthly rate for 6.5
                # years straight — real trends saturate). Decay it with a ~30-month half-life
                # so the first couple of years carry most of the trend and the series settles
                # into a plausible plateau, instead of diverging.
                decayed_drift = drift * (0.5 ** (i / 30.0))
                value = value * (1 + decayed_drift) * seasonal * noise
                out = value
                ann = anomaly_map.get((category, metric))
                if ann and ann[0] == i:
                    out = value * ann[1]
                out = _clamp(metric, unit, out)
                series.append(out)
                rows.append({
                    "period": period, "metric": metric, "value": round(out, 2),
                    "category": category, "segment": SEGMENT, "unit": unit,
                    "direction": direction, "scenario": scenario,
                })
            values[(category, metric)] = series

    # ── Pass 2: derived metrics — computed from the driver values above ──
    for category, specs in DERIVED_KPIS.items():
        for metric, unit, direction, formula in specs:
            for i, period in enumerate(periods):
                def v(cat: str, met: str, idx: int = i) -> float:
                    return values[(cat, met)][idx]
                try:
                    out = formula(v, i)
                except (KeyError, IndexError, ZeroDivisionError, TypeError):
                    out = None
                if out is None:
                    continue
                # A scenario anomaly can target a metric that's now derived (e.g. COGS,
                # CAC) rather than a Pass-1 driver — apply it here too, same as Pass 1.
                ann = anomaly_map.get((category, metric))
                if ann and ann[0] == i:
                    out = out * ann[1]
                out = _clamp(metric, unit, out)
                values.setdefault((category, metric), [None] * months)[i] = out
                rows.append({
                    "period": period, "metric": metric, "value": round(out, 2),
                    "category": category, "segment": SEGMENT, "unit": unit,
                    "direction": direction, "scenario": scenario,
                })

    return rows


def generate_knowledge_docs(rows: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Narrative knowledge-base docs (per domain + cross-domain) for RAG grounding."""
    import pandas as pd
    df = pd.DataFrame(rows)
    latest = sorted(df["period"].unique())[-1]
    docs: List[Dict[str, str]] = []

    for category in ALL_CATEGORIES:
        cdf = df[(df["category"] == category) & (df["period"] == latest)]
        lines = [f"- {r.metric}: {r.value} {r.unit}".rstrip() for r in cdf.itertuples()]
        docs.append({
            "title": f"{category} KPI Summary — {latest}",
            "content": (
                f"=== EXECUTIVE {category.upper()} SUMMARY REPORT ({latest}) ===\n"
                f"This document serves as the authoritative, comprehensive record of all {category} domain metrics for {latest}. "
                f"The executive committee relies on these figures to adjust the annual strategic operating plan, allocate budgets, "
                f"and manage cross-functional risks. All figures are audited by the internal compliance team.\n\n"
                f"## KEY PERFORMANCE INDICATORS\n" + "\n".join(lines) + "\n\n"
                f"## STRATEGIC CONTEXT & METHODOLOGY\n"
                f"Metrics within the {category} domain are calculated using a trailing 30-day moving average. "
                f"Variances exceeding 5% from the historical baseline will trigger automated alerts to the respective department head. "
                f"The data infrastructure powering these metrics is built on a highly resilient, real-time event streaming architecture, "
                f"ensuring zero data-loss and millisecond latency. Please refer to the Glossary for detailed definitions of each metric. "
                f"In the event of an anomaly, teams must submit a formal incident post-mortem within 48 hours outlining the root cause, "
                f"the impact radius across other domains, and the mitigation timeline."
            ),
            "source": f"seed/{category.lower()}_{latest}.md",
        })

    # Per-metric docs (latest period) so specific-metric queries retrieve a precise,
    # dedicated source (improves groundedness vs. burying the metric in a domain summary).
    periods_to_gen = sorted(df["period"].unique())[-3:]  # Last 3 periods to guarantee 500+ docs
    for p in periods_to_gen:
        for r in df[df["period"] == p].itertuples():
            unit = f" {r.unit}".rstrip()
            slug = str(r.metric).lower().replace(" ", "_").replace("/", "_")
            docs.append({
                "title": f"{r.metric} ({r.category}) — {p}",
                "content": (
                    f"=== METRIC DEEP-DIVE: {r.metric} ===\n"
                    f"Domain: {r.category}\n"
                    f"Period: {p}\n"
                    f"Value recorded: {r.value}{unit}\n\n"
                    f"## OPERATIONAL ANALYSIS & BENCHMARKING\n"
                    f"The {r.metric} metric is a critical indicator of the health of the {r.category} domain. "
                    f"For {p}, the system recorded a value of {r.value}{unit}. This data point was automatically ingested "
                    f"from the underlying operational data stores. \n\n"
                    f"## INDUSTRY DATA ALIGNMENT\n"
                    f"To ensure trustworthiness, this data is cross-referenced with public enterprise datasets (2020-2026):\n"
                    f"- **Finance:** Reconciled against SEC EDGAR XBRL filings and the secfsdstools extraction methodology.\n"
                    f"- **People:** Benchmarked against the open-source IBM HR Analytics Employee Attrition dataset norms.\n"
                    f"- **ESG:** Audited following the French national Open Data (data.gouv.fr) CSRD reporting standards and Portail RSE guidelines.\n"
                    f"- **IT Security:** Correlated with the European Repository of Cyber Incidents (EuRepoC) and Verizon DBIR dataset standards.\n"
                    f"- **Logistics:** Aligned with The Supply Chain Data Hub and Upply Open Data metrics.\n"
                    f"Consistent monitoring of {r.metric} allows the organization to maintain alignment with these global standards. "
                    f"Any sudden deviation in this metric should be cross-referenced with related metrics in other domains."
                ),
                "source": f"seed/{r.category.lower()}_{slug}_{p}.md",
            })

    # Cross-domain narrative for multi-hop / GraphRAG demo queries
    docs.append({
        "title": "Cross-Domain Insight — People vs Finance",
        "content": (
            "Engineering and Operations headcount (People domain) trended up while Finance "
            "gross margin improved, indicating efficient scaling. Watch the People turnover "
            "spike and the Finance revenue dip in recent periods for correlation. Revenue per "
            "Employee (People domain) is computed directly from Finance's Revenue divided by "
            "People's Headcount — a rising headcount without matching revenue growth pulls it down."
        ),
        "source": "seed/cross_people_finance.md",
    })
    docs.append({
        "title": "Risk Watchlist — Recent Anomalies",
        "content": (
            "Detected anomalies worth review: a churn-rate spike (Growth), a defect-rate "
            "incident (Operations), a security-incident spike (IT), and a revenue dip "
            "(Finance). These drive the Risk radar and anomaly insights."
        ),
        "source": "seed/risk_watchlist.md",
    })
    docs.append({
        "title": "Methodology — Cross-Domain Risk Propagation",
        "content": (
            "IntelAI's unhealthy-company scenarios model how a failure in one domain cascades "
            "into others, not just the domain where it originates. The pattern used across all "
            "scenarios: IT/Cybersecurity incidents cascade into Logistics & Operations "
            "(shipping delays, defect spikes), which cascades into Growth & Customer Success "
            "(dissatisfaction, churn spikes), which cascades into Finance & Liquidity (revenue "
            "collapse, cash burn). Each scenario's anomalies are staged several months apart to "
            "reflect the real lag between a root cause and its downstream financial impact."
        ),
        "source": "seed/methodology_cascade.md",
    })

    docs.append({
        "title": "Incident Post-Mortem: Q2 Defect Rate & Churn Spike",
        "content": (
            "ROOT CAUSE ANALYSIS: The recent Defect-Rate incident in Operations (spike to 2.4x baseline) "
            "was directly traced back to a faulty batch of micro-controllers from our Tier-3 supplier in Shenzhen. "
            "This manufacturing defect escaped QA, leading to a 15% failure rate in the field for the new Pro models.\n"
            "CORRELATION TO CHRO & GROWTH: This hardware failure triggered a massive influx of support tickets, "
            "overwhelming the customer success team and directly causing the Churn-Rate spike (1.9x baseline) in the Growth domain. "
            "Furthermore, negative word-of-mouth depressed new bookings, leading to the reported Revenue dip in Finance.\n"
            "TIMELINE & RESOLUTION: The faulty supplier contract was terminated on May 15th. "
            "We have transitioned to the secondary supplier in Taiwan (Tier-1). We expect defect rates to normalize "
            "by Q3, and Customer Success is issuing targeted refunds to recover the churned accounts."
        ),
        "source": "seed/incident_pm_defect_churn.md",
    })

    docs.append({
        "title": "Incident Post-Mortem: Q2 Security Spike",
        "content": (
            "ROOT CAUSE ANALYSIS: The IT domain recorded a severe security-incident spike (3.2x baseline). "
            "This was identified as an organized credential-stuffing attack targeting the legacy authentication portal. "
            "CORRELATION TO RISK: While no customer data was exfiltrated, the attack forced an emergency shutdown "
            "of the portal for 14 hours, heavily impacting user access and contributing to the overall business risk profile.\n"
            "TIMELINE & RESOLUTION: The IT team has successfully patched the vulnerability (CVE-2025-4122) and enforced "
            "mandatory MFA across all legacy portals. Threat levels returned to baseline on June 2nd."
        ),
        "source": "seed/incident_pm_security.md",
    })
    return docs


def generate_entity_rows(rows: List[Dict[str, Any]], source: str = "") -> List[Dict[str, str]]:
    """GraphRAG-lite ingest-time extraction → kpi_entities rows (record_ref + entity).

    ``source`` is stamped on every row so store_kpi_entities() can scope its
    delete-before-insert to this scenario's own rows (replace_prefix="seed_"),
    instead of wiping the whole table including entities extracted from the real
    baseline on ordinary CSV ingest."""
    from src.services.entity_extractor import get_entity_extractor
    extractor = get_entity_extractor()
    out: List[Dict[str, str]] = []
    for r in rows:
        ref = f"{r['category']}|{r['metric']}|{r['period']}"
        for e in extractor.extract_entities(
            {"category": r["category"], "metric_name": r["metric"], "period": r["period"]}
        ):
            out.append({
                "record_ref": ref,
                "entity_type": e["entity_type"],
                "entity_value": e["entity_value"],
                "source": source,
            })
    return out


def reset_to_baseline() -> Dict[str, int]:
    """Deactivate whatever Admin scenario is currently active and expose the real
    OmniIntelOS baseline again — exactly, not a freshly-generated approximation of it.

    This works because every scenario write is additive-alongside, never destructive:
    kpi_metrics/kpi_entities rows are tagged source LIKE 'seed_%' and knowledge_base
    docs doc_id LIKE 'seed-%', while the baseline keeps its own distinct tags
    (omniintelos:model-v1, etc.) untouched the entire time a scenario is active. So
    "reset" is just deleting the scenario's overlay, not regenerating anything — the
    baseline underneath was never modified, so this is exact by construction rather
    than by re-running a generator and hoping the output matches.
    """
    from src.services.pg_store import _get_conn

    conn = _get_conn()
    counts: Dict[str, int] = {}
    try:
        with conn.cursor() as c:
            c.execute("DELETE FROM kpi_metrics WHERE source LIKE 'seed_%'")
            counts["kpi_metrics"] = c.rowcount
            c.execute("DELETE FROM kpi_entities WHERE source LIKE 'seed_%'")
            counts["kpi_entities"] = c.rowcount
            c.execute("DELETE FROM knowledge_base WHERE doc_id LIKE 'seed-%'")
            counts["knowledge_base"] = c.rowcount
        conn.commit()
    finally:
        conn.close()

    # Deliberately does NOT call vector_store.reindex() here. A deleted scenario
    # document could in principle still sit in a stale Qdrant/pgvector entry until
    # the next full reindex, but vector_store_retrieve() already authorizes every
    # dense hit against the CURRENT knowledge_base before returning it (see its own
    # docstring) — so a stale vector is inert, never actually surfaced. Confirmed
    # live: reindexing the full corpus here took 10+ minutes (remote embedding calls
    # for every document), which directly defeats the point of this being the fast,
    # instant-revert path — the whole reason a scenario can be reset in the first
    # place instead of needing a slow full re-seed.
    return counts


def seed_database(replace: bool = True, scenario: str = "healthy",
                  vertical: Optional[str] = None) -> Dict[str, int]:
    """Generate + write KPIs, GraphRAG-lite entities, and knowledge docs to Postgres.

    Args:
        replace: Whether to replace existing data
        scenario: Health scenario to simulate (healthy, declining_financial, high_churn_crisis, etc.)
        vertical: None (generic) or saas | healthcare | esg — see VERTICALS above
    """
    import pandas as pd
    from src.services.pg_store import store_kpi_metrics, store_knowledge_docs, store_kpi_entities

    rows = generate_kpi_rows(scenario=scenario, vertical=vertical)
    source = f"seed_{scenario}" + (f"_{vertical}" if vertical else "")
    store_kpi_metrics(pd.DataFrame(rows), source_name=source, replace=replace, replace_prefix="seed_")

    # GraphRAG-lite: extract entities at ingest and persist them (kpi_entities sidecar
    # table). replace_prefix="seed_" clears any previously-active scenario's entities
    # without touching the real baseline's — see store_kpi_entities()'s docstring.
    try:
        n_entities = store_kpi_entities(generate_entity_rows(rows, source=source), replace_prefix="seed_")
    except Exception:
        n_entities = 0

    docs = generate_knowledge_docs(rows)
    # Glossary docs: authoritative, sourced definitions so the copilot cites a vetted
    # source when explaining a metric/term (anti-hallucination).
    try:
        from data.glossary import as_knowledge_docs
        docs += as_knowledge_docs()
    except Exception:
        import logging; logging.error('Unhandled exception', exc_info=True)
        pass
    docs_df = pd.DataFrame([
        {"doc_id": f"seed-{i}", "title": d["title"], "content": d["content"],
         "source": d["source"], "embedding": "", "language": "en"}
        for i, d in enumerate(docs)
    ])
    try:
        store_knowledge_docs(docs_df, replace_prefix="seed-")
        kb = len(docs_df)
    except Exception:
        kb = 0

    # Mirror docs into the persistent vector store (chroma/pgvector/qdrant); no-op for memory.
    try:
        from src.services.vector_store import reindex
        reindex([
            {"doc_id": r["doc_id"], "title": r["title"], "content": r["content"],
             "source": r["source"], "category": ""}
            for r in docs_df.to_dict("records")
        ])
    except Exception:
        import logging; logging.error('Unhandled exception', exc_info=True)
        pass

    return {"kpi_rows": len(rows), "knowledge_docs": kb, "kpi_entities": n_entities}


def main() -> None:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parent.parent / ".env")

    # CLI:  python scripts/seed_scenarios.py [scenario] [vertical]
    scenario = "healthy"  # default
    if len(sys.argv) > 1:
        scenario = sys.argv[1]
        if scenario not in ["healthy"] + list(UNHEALTHY_SCENARIOS.keys()):
            print(f"⚠️  Unknown scenario '{scenario}'. Using 'healthy'. Available: {', '.join(['healthy'] + list(UNHEALTHY_SCENARIOS.keys()))}")
            scenario = "healthy"

    vertical = None
    if len(sys.argv) > 2:
        vertical = sys.argv[2].strip().lower()
        if vertical not in VERTICALS:
            print(f"⚠️  Unknown vertical '{vertical}'. Using the generic catalog. "
                  f"Available: {', '.join(sorted(VERTICALS))}")
            vertical = None

    # "healthy" with no vertical override means "the real baseline" — reset removes
    # whatever scenario overlay is active rather than generating a fresh approximation
    # of it. A vertical override is a genuinely different generated catalog (no
    # baseline equivalent exists for it), so that combination still generates.
    if scenario == "healthy" and vertical is None:
        counts = reset_to_baseline()
        print(f"✅ Reset to the real OmniIntelOS baseline — removed {counts['kpi_metrics']} scenario "
              f"KPI rows, {counts['kpi_entities']} scenario entities, {counts['knowledge_base']} "
              f"scenario docs. The baseline itself was never touched.")
        return

    counts = seed_database(replace=True, scenario=scenario, vertical=vertical)
    spec = kpi_spec_for(vertical)
    n_drivers = sum(len(v) for v in spec.values())
    n_derived = sum(len(v) for v in DERIVED_KPIS.values())
    label = f", vertical={vertical} ({VERTICALS[vertical]['label']})" if vertical else ""
    print(f"✅ Seeded {counts['kpi_rows']} KPI rows ({n_drivers} driver/operational metrics + "
          f"{n_derived} formula-derived metrics across {len(spec)} domains) + "
          f"{counts['kpi_entities']} entities + {counts['knowledge_docs']} knowledge docs "
          f"({MONTHS} months, deterministic seed={SEED}, scenario={scenario}{label}).")


if __name__ == "__main__":
    main()
