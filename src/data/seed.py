"""IntelAI demo-data seed — robust, deterministic, DB-direct.

Replaces the old file-based ``enhanced_synthetic_dataset`` + generator. Generates a
reproducible (seeded) multi-domain KPI time series aligned with the domain pages and
personas (Finance, Growth, People, Operations, IT, Logistics, ESG), injects a few
controlled anomalies (so Risk/anomaly detection has signal), and seeds narrative
knowledge-base docs so the RAG copilot has grounded context + citations.

Idempotent: writes directly to Postgres via ``pg_store`` (replace=True).

Run standalone:  python -m src.data.seed         (uses POSTGRES_URL from env/.env)
Or from code:    from src.data.seed import seed_database; seed_database()
"""
from __future__ import annotations

import math
import random
from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple

SEED = 42
MONTHS = 24
SEGMENT = "Global"

# category -> list of (metric, unit, base_value, monthly_drift, direction)
# drift is the average month-over-month relative change in the "good" direction.
KPI_SPEC: Dict[str, List[Tuple[str, str, float, float, str]]] = {
    "Finance": [
        ("Revenue", "USD", 2_400_000, 0.018, "up"),
        ("Gross Margin", "%", 58, 0.004, "up"),
        ("EBITDA", "USD", 540_000, 0.020, "up"),
        ("Operating Costs", "USD", 1_300_000, -0.006, "down"),
        ("Net Profit", "USD", 360_000, 0.022, "up"),
        ("Operating Cash Flow", "USD", 480_000, 0.015, "up"),
    ],
    "Growth": [
        ("MRR", "USD", 410_000, 0.025, "up"),
        ("ARR", "USD", 4_900_000, 0.024, "up"),
        ("Customer Count", "count", 1_250, 0.018, "up"),
        ("Churn Rate", "%", 4.8, -0.010, "down"),
        ("CAC", "USD", 1_100, -0.008, "down"),
        ("LTV", "USD", 9_800, 0.014, "up"),
        ("Net Promoter Score", "score", 42, 0.006, "up"),
    ],
    "People": [
        ("Headcount", "count", 240, 0.012, "up"),
        ("Turnover Rate", "%", 12.5, -0.012, "down"),
        ("Engagement Score", "score", 74, 0.004, "up"),
        ("Time to Hire", "days", 38, -0.008, "down"),
        ("Training Hours", "hours", 22, 0.010, "up"),
        ("Open Positions", "count", 28, -0.004, "down"),
    ],
    "Operations": [
        ("On-time Delivery", "%", 93, 0.003, "up"),
        ("Cycle Time", "days", 14, -0.009, "down"),
        ("Defect Rate", "%", 2.1, -0.013, "down"),
        ("Capacity Utilization", "%", 78, 0.004, "up"),
        ("Production Efficiency", "%", 84, 0.004, "up"),
        ("Safety Incident Rate", "rate", 1.4, -0.015, "down"),
    ],
    "IT": [
        ("System Uptime", "%", 99.4, 0.0006, "up"),
        ("Mean Time to Resolution", "hours", 6.5, -0.012, "down"),
        ("Security Incidents", "count", 7, -0.018, "down"),
        ("Cloud Cost per User", "USD", 180, -0.006, "down"),
        ("Deployment Frequency", "per_month", 18, 0.020, "up"),
        ("IT Satisfaction", "score", 7.6, 0.005, "up"),
    ],
    "Logistics": [
        ("Inventory Turnover", "ratio", 6.2, 0.012, "up"),
        ("Order Accuracy", "%", 97.5, 0.002, "up"),
        ("Freight Cost per Unit", "USD", 18, -0.007, "down"),
        ("Warehouse Utilization", "%", 72, 0.005, "up"),
        ("Last Mile Delivery Time", "days", 3.2, -0.010, "down"),
        ("Returns Rate", "%", 6.5, -0.009, "down"),
    ],
    "ESG": [
        ("Carbon Emissions (tCO2)", "tonnes_CO2e", 8_400, -0.014, "down"),
        ("Renewable Energy %", "%", 38, 0.012, "up"),
        ("Water Consumption (m3)", "cubic_meters", 12_000, -0.008, "down"),
        ("Waste Recycled %", "%", 61, 0.008, "up"),
        ("Diversity Score", "score", 68, 0.005, "up"),
        ("Board Diversity %", "%", 33, 0.010, "up"),
    ],
}

# Deterministic anomalies: (category, metric, month_index, multiplier) — give Risk a signal.
ANOMALIES: List[Tuple[str, str, int, float]] = [
    ("Finance", "Revenue", 17, 0.78),            # revenue dip
    ("Growth", "Churn Rate", 14, 1.9),           # churn spike
    ("Operations", "Defect Rate", 11, 2.4),      # quality incident
    ("IT", "Security Incidents", 20, 3.2),        # security spike
    ("People", "Turnover Rate", 9, 1.8),          # attrition spike
]


def _periods(months: int) -> List[str]:
    base = datetime.utcnow().replace(day=1) - timedelta(days=30 * (months - 1))
    return [(base + timedelta(days=30 * i)).strftime("%Y-%m") for i in range(months)]


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
                    out = max(0.0, min(100.0, out))
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
    docs_df = pd.DataFrame([
        {"doc_id": f"seed-{i}", "title": d["title"], "content": d["content"],
         "source": d["source"], "embedding": "", "language": "en"}
        for i, d in enumerate(docs)
    ])
    try:
        store_knowledge_docs(docs_df)
        kb = len(docs_df)
    except Exception:
        kb = 0
    return {"kpi_rows": len(rows), "knowledge_docs": kb, "kpi_entities": n_entities}


def main() -> None:
    from dotenv import load_dotenv
    from pathlib import Path
    load_dotenv(Path(__file__).resolve().parents[2] / ".env")
    counts = seed_database(replace=True)
    print(f"✅ Seeded {counts['kpi_rows']} KPI rows + {counts['kpi_entities']} entities + "
          f"{counts['knowledge_docs']} knowledge docs across {len(KPI_SPEC)} domains "
          f"({MONTHS} months, deterministic seed={SEED}).")


if __name__ == "__main__":
    main()
