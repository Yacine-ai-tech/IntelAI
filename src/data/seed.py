"""IntelAI demo-data seed — robust, deterministic, DB-direct, single source of truth.

Generates a reproducible (seeded) multi-domain KPI time series that is the ONE catalog
feeding everything: the domain dashboards (via the keyword extractors in the domain
services), the cross-domain analytics, the persona RAG copilot (per-metric + per-domain
knowledge docs), and the glossary-grounded explainer. Adding a metric here is the only
step needed for it to appear across the whole product — no schema change, no migration.

The catalog is split for clarity (both halves are seeded into the same ``kpi_metrics``
table, so there is still exactly one source):

  * ``STRATEGIC_KPIS``    — the board/exec "metrics that matter" per domain. Every one of
                            these has a sourced, benchmarked definition in ``glossary.py``
                            so the copilot can explain and cite it.
  * ``OPERATIONAL_DETAIL``— the operational counters each domain dashboard also displays
                            (ticket/vuln counts, recruitment funnel, inventory sub-stats…).
                            Self-explanatory, so they are not all glossary-backed.

Coverage is intentionally a curated, credible set — NOT every metric a company could
track. The long tail is handled by user uploads (CSV ingest writes arbitrary
``(category, metric, value)`` rows into the same table, scoped by category/RBAC).

Idempotent: writes directly to Postgres via ``pg_store`` (replace=True).

Run standalone:  python -m src.data.seed         (uses POSTGRES_URL from env/.env)
Or from code:    from src.data.seed import seed_database; seed_database()
"""
from __future__ import annotations

import math
import random
from datetime import datetime, timedelta
from itertools import chain
from typing import Any, Dict, List, Tuple

SEED = 42
MONTHS = 36
SEGMENT = "Global"

# Tuple schema per metric: (metric, unit, base_value, monthly_drift, direction)
#   drift     = average month-over-month relative change in the "good" direction
#   direction = "up" (higher is better) | "down" (lower is better)

# ── STRATEGIC: the "metrics that matter" — every one is defined in glossary.py ──
STRATEGIC_KPIS: Dict[str, List[Tuple[str, str, float, float, str]]] = {
    "Finance": [
        ("Revenue", "USD", 2_400_000, 0.018, "up"),
        ("Gross Margin", "%", 58, 0.004, "up"),
        ("EBITDA", "USD", 540_000, 0.020, "up"),
        ("Operating Costs", "USD", 1_300_000, -0.006, "down"),
        ("Net Profit", "USD", 360_000, 0.022, "up"),
        ("Operating Cash Flow", "USD", 480_000, 0.015, "up"),
        ("Free Cash Flow", "USD", 300_000, 0.016, "up"),
        ("COGS", "USD", 1_008_000, 0.009, "down"),
        ("Taxes", "USD", 95_000, 0.010, "down"),
        ("Working Capital", "USD", 2_100_000, 0.008, "up"),
        ("Rule of 40", "%", 46, 0.003, "up"),
        ("Days Sales Outstanding", "days", 45, -0.006, "down"),
        ("Cash Runway", "months", 19, 0.004, "up"),
    ],
    "Growth": [
        ("MRR", "USD", 410_000, 0.025, "up"),
        ("ARR", "USD", 4_900_000, 0.024, "up"),
        ("Customer Count", "count", 1_250, 0.018, "up"),
        ("Churn Rate", "%", 4.8, -0.010, "down"),
        ("CAC", "USD", 1_100, -0.008, "down"),
        ("LTV", "USD", 9_800, 0.014, "up"),
        ("LTV:CAC", "ratio", 4.2, 0.010, "up"),
        ("Net Promoter Score", "score", 42, 0.006, "up"),
        ("Net Revenue Retention", "%", 112, 0.003, "up"),
        ("CAC Payback", "months", 14, -0.008, "down"),
        ("ARPU", "USD", 320, 0.010, "up"),
        ("Active Users", "count", 9_800, 0.020, "up"),
    ],
    "People": [
        ("Headcount", "count", 240, 0.012, "up"),
        ("Turnover Rate", "%", 12.5, -0.012, "down"),
        ("Engagement Score", "score", 74, 0.004, "up"),
        ("Time to Hire", "days", 38, -0.008, "down"),
        ("Training Hours", "hours", 22, 0.010, "up"),
        ("Open Positions", "count", 28, -0.004, "down"),
        ("Average Tenure", "years", 4.1, 0.006, "up"),
        ("Cost per Hire", "USD", 4_200, -0.006, "down"),
        ("Absenteeism Rate", "%", 3.2, -0.010, "down"),
        ("Quality of Hire", "score", 78, 0.005, "up"),
        ("Offer Acceptance Rate", "%", 84, 0.004, "up"),
        ("Internal Mobility Rate", "%", 18, 0.010, "up"),
        ("Revenue per Employee", "USD", 235_000, 0.012, "up"),
    ],
    "Operations": [
        ("On-time Delivery", "%", 93, 0.003, "up"),
        ("Cycle Time", "days", 14, -0.009, "down"),
        ("Defect Rate", "%", 2.1, -0.013, "down"),
        ("Capacity Utilization", "%", 78, 0.004, "up"),
        ("Production Efficiency", "%", 84, 0.004, "up"),
        ("Safety Incident Rate", "rate", 1.4, -0.015, "down"),
        ("First Pass Yield", "%", 95.5, 0.002, "up"),
        ("Quality Rate", "%", 97, 0.002, "up"),
        ("Throughput", "units", 5_200, 0.010, "up"),
        ("Unplanned Downtime", "hours", 42, -0.010, "down"),
        ("Cost per Unit", "USD", 12.5, -0.007, "down"),
        ("Schedule Adherence", "%", 91, 0.003, "up"),
        ("Scrap Rate", "%", 3.1, -0.011, "down"),
    ],
    "IT": [
        ("System Uptime", "%", 99.4, 0.0006, "up"),
        ("Mean Time to Resolution", "hours", 6.5, -0.012, "down"),
        ("Security Incidents", "count", 7, -0.018, "down"),
        ("Critical Incidents", "count", 2, -0.020, "down"),
        ("Cloud Cost per User", "USD", 180, -0.006, "down"),
        ("Cloud Spend", "USD", 240_000, -0.004, "down"),
        ("Deployment Frequency", "per_month", 18, 0.020, "up"),
        ("Lead Time for Changes", "hours", 9, -0.012, "down"),
        ("Change Failure Rate", "%", 12, -0.015, "down"),
        ("SLA Compliance", "%", 96.5, 0.002, "up"),
        ("Security Score", "score", 82, 0.005, "up"),
        ("IT Satisfaction", "score", 7.6, 0.005, "up"),
    ],
    "Logistics": [
        ("Inventory Turnover", "ratio", 6.2, 0.012, "up"),
        ("Order Accuracy", "%", 97.5, 0.002, "up"),
        ("Perfect Order Rate", "%", 94, 0.003, "up"),
        ("On-Time Delivery Rate", "%", 95, 0.003, "up"),
        ("Fill Rate", "%", 96, 0.002, "up"),
        ("Stockout Rate", "%", 2.5, -0.011, "down"),
        ("Freight Cost per Unit", "USD", 18, -0.007, "down"),
        ("Carrying Cost", "USD", 320_000, -0.005, "down"),
        ("Warehouse Utilization", "%", 72, 0.005, "up"),
        ("Avg Lead Time", "days", 6.5, -0.008, "down"),
        ("Last Mile Delivery Time", "days", 3.2, -0.010, "down"),
        ("Days Inventory Outstanding", "days", 58, -0.006, "down"),
        ("Returns Rate", "%", 6.5, -0.009, "down"),
    ],
    "ESG": [
        ("ESG Score", "score", 71, 0.004, "up"),
        ("Carbon Emissions (tCO2)", "tonnes_CO2e", 8_400, -0.014, "down"),
        ("Scope 1 Emissions", "tonnes_CO2e", 1_200, -0.012, "down"),
        ("Scope 2 Emissions", "tonnes_CO2e", 2_100, -0.013, "down"),
        ("Scope 3 Emissions", "tonnes_CO2e", 5_100, -0.010, "down"),
        ("Emissions Intensity", "tCO2e/$M", 3.5, -0.012, "down"),
        ("Renewable Energy %", "%", 38, 0.012, "up"),
        ("Water Consumption (m3)", "cubic_meters", 12_000, -0.008, "down"),
        ("Waste Recycled %", "%", 61, 0.008, "up"),
        ("Diversity Score", "score", 68, 0.005, "up"),
        ("Board Diversity %", "%", 33, 0.010, "up"),
        ("Gender Pay Gap", "%", 8.5, -0.010, "down"),
        ("Community Investment", "USD", 180_000, 0.012, "up"),
    ],
}

# ── OPERATIONAL DETAIL: counters the domain dashboards display (not all glossary-backed) ──
OPERATIONAL_DETAIL: Dict[str, List[Tuple[str, str, float, float, str]]] = {
    "People": [
        ("Applications Received", "count", 320, 0.010, "up"),
        ("Interviews Scheduled", "count", 90, 0.008, "up"),
        ("Offers Extended", "count", 32, 0.006, "up"),
        ("Offers Accepted", "count", 27, 0.006, "up"),
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
        ("Critical Vulnerabilities", "count", 3, -0.020, "down"),
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
        ("Damaged Rate", "%", 1.2, -0.010, "down"),
        ("Avg Transit Days", "days", 4.5, -0.008, "down"),
        ("Cost per Shipment", "USD", 22, -0.006, "down"),
    ],
    "ESG": [
        ("Ethics Training", "%", 92, 0.003, "up"),
        ("Supplier ESG Compliance", "%", 88, 0.004, "up"),
        ("Data Privacy Incidents", "count", 1, -0.020, "down"),
    ],
}

# Merged catalog — the single source generated into kpi_metrics.
KPI_SPEC: Dict[str, List[Tuple[str, str, float, float, str]]] = {
    cat: list(chain(STRATEGIC_KPIS[cat], OPERATIONAL_DETAIL.get(cat, [])))
    for cat in STRATEGIC_KPIS
}

# Percentages that legitimately exceed 100 (must NOT be clamped to [0, 100]).
PCT_OVER_100 = {"Net Revenue Retention"}

# Deterministic anomalies: (category, metric, month_index, multiplier) — give Risk a signal.
ANOMALIES: List[Tuple[str, str, int, float]] = [
    ("Finance", "Revenue", 17, 0.78),            # revenue dip
    ("Growth", "Churn Rate", 14, 1.9),           # churn spike
    ("Operations", "Defect Rate", 11, 2.4),      # quality incident
    ("IT", "Security Incidents", 20, 3.2),       # security spike
    ("People", "Turnover Rate", 9, 1.8),         # attrition spike
]


def _periods(months: int) -> List[str]:
    base = datetime(2024, 1, 1)
    return [(base + timedelta(days=31 * i)).replace(day=1).strftime("%Y-%m") for i in range(months)]


def generate_kpi_rows(months: int = MONTHS, seed: int = SEED) -> List[Dict[str, Any]]:
    """Deterministic multi-domain KPI time series with trend, seasonality, noise, anomalies."""
    rng = random.Random(seed)
    periods = _periods(months)
    anomaly_map = {(c, m): (i, mult) for c, m, i, mult in ANOMALIES}
    rows: List[Dict[str, Any]] = []

    for category, metrics in KPI_SPEC.items():
        for metric, unit, base, drift, direction in metrics:
            value = base
            for i, period in enumerate(periods):
                seasonal = 1.0 + 0.03 * math.sin((i % 12) / 12 * 2 * math.pi)
                noise = 1.0 + rng.gauss(0, 0.02)
                value = value * (1 + drift) * seasonal * noise
                out = value
                ann = anomaly_map.get((category, metric))
                if ann and ann[0] == i:
                    out = value * ann[1]
                if unit == "%":
                    out = max(0.0, out)
                    if metric not in PCT_OVER_100:
                        out = min(100.0, out)
                rows.append({
                    "period": period,
                    "metric": metric,
                    "value": round(out, 2),
                    "category": category,
                    "segment": SEGMENT,
                    "unit": unit,
                    "direction": direction,
                })
    return rows


def generate_knowledge_docs(rows: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Narrative knowledge-base docs (per domain + cross-domain) for RAG grounding."""
    import pandas as pd
    df = pd.DataFrame(rows)
    latest = sorted(df["period"].unique())[-1]
    docs: List[Dict[str, str]] = []

    for category in KPI_SPEC:
        cdf = df[(df["category"] == category) & (df["period"] == latest)]
        lines = [f"- {r.metric}: {r.value} {r.unit}".rstrip() for r in cdf.itertuples()]
        docs.append({
            "title": f"{category} KPI Summary — {latest}",
            "content": f"{category} domain key metrics for {latest}:\n" + "\n".join(lines),
            "source": f"seed/{category.lower()}_{latest}.md",
        })

    # Per-metric docs (latest period) so specific-metric queries retrieve a precise,
    # dedicated source (improves groundedness vs. burying the metric in a domain summary).
    for r in df[df["period"] == latest].itertuples():
        unit = f" {r.unit}".rstrip()
        slug = str(r.metric).lower().replace(" ", "_").replace("/", "_")
        docs.append({
            "title": f"{r.metric} ({r.category}) — {latest}",
            "content": f"{r.metric} for the {r.category} domain in {latest}: {r.value}{unit}.",
            "source": f"seed/{r.category.lower()}_{slug}_{latest}.md",
        })

    # Cross-domain narrative for multi-hop / GraphRAG demo queries
    docs.append({
        "title": "Cross-Domain Insight — People vs Finance",
        "content": (
            "Engineering and Operations headcount (People domain) trended up while Finance "
            "gross margin improved, indicating efficient scaling. Watch the People turnover "
            "spike and the Finance revenue dip in recent periods for correlation."
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
    return docs


def generate_entity_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """GraphRAG-lite ingest-time extraction → kpi_entities rows (record_ref + entity)."""
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
            })
    return out


def seed_database(replace: bool = True) -> Dict[str, int]:
    """Generate + write KPIs, GraphRAG-lite entities, and knowledge docs to Postgres."""
    import pandas as pd
    from src.services.pg_store import store_kpi_metrics, store_knowledge_docs, store_kpi_entities

    rows = generate_kpi_rows()
    store_kpi_metrics(pd.DataFrame(rows), source_name="seed", replace=replace)

    # GraphRAG-lite: extract entities at ingest and persist them (kpi_entities sidecar table).
    try:
        n_entities = store_kpi_entities(generate_entity_rows(rows), replace=replace)
    except Exception:
        n_entities = 0

    docs = generate_knowledge_docs(rows)
    # Glossary docs: authoritative, sourced definitions so the copilot cites a vetted
    # source when explaining a metric/term (anti-hallucination — STRATEGY §grounding).
    try:
        from src.data.glossary import as_knowledge_docs
        docs += as_knowledge_docs()
    except Exception:
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
        pass

    return {"kpi_rows": len(rows), "knowledge_docs": kb, "kpi_entities": n_entities}


def main() -> None:
    from dotenv import load_dotenv
    from pathlib import Path
    load_dotenv(Path(__file__).resolve().parents[2] / ".env")
    counts = seed_database(replace=True)
    n_metrics = sum(len(v) for v in KPI_SPEC.values())
    print(f"✅ Seeded {counts['kpi_rows']} KPI rows ({n_metrics} metrics across "
          f"{len(KPI_SPEC)} domains) + {counts['kpi_entities']} entities + "
          f"{counts['knowledge_docs']} knowledge docs ({MONTHS} months, deterministic seed={SEED}).")


if __name__ == "__main__":
    main()
