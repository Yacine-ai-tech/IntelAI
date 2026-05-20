"""
Data processing — file parsing, sample data generation, macro KPIs.
"""
from __future__ import annotations

from datetime import datetime
from io import BytesIO
from typing import Dict, List

import numpy as np
import pandas as pd
import requests

from src.core.logger import get_logger

log = get_logger(__name__)

REQUIRED_COLUMNS = ["period", "metric", "value"]

CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "Finance": ["revenue", "gross", "margin", "ebitda", "cash", "opex", "expense", "profit"],
    "Growth": ["mrr", "arr", "pipeline", "bookings", "leads", "conversion"],
    "Customer": ["churn", "retention", "nps", "customers", "ticket"],
    "Operations": ["cycle", "throughput", "utilization", "on-time", "downtime", "quality"],
    "People": ["headcount", "attrition", "engagement", "hiring"],
    "ESG": ["carbon", "emission", "diversity", "safety", "injury"],
}


def _standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = df.columns.str.lower().str.strip().str.replace(" ", "_")
    return df


def _infer_category(metric: str) -> str:
    ml = metric.lower()
    for cat, kws in CATEGORY_KEYWORDS.items():
        if any(k in ml for k in kws):
            return cat
    return "Other"


def _normalize_period(value: str) -> str:
    try:
        return pd.to_datetime(value).strftime("%Y-%m")
    except Exception:
        return str(value)


def parse_metrics_file(file_content: BytesIO, file_name: str) -> pd.DataFrame:
    """Parse CSV/Excel into long-format KPI DataFrame."""
    if file_name.lower().endswith(".csv"):
        df = pd.read_csv(file_content)
    else:
        df = pd.read_excel(file_content)

    df = _standardize_columns(df)

    aliases = {
        "date": "period", "month": "period", "period": "period",
        "metric": "metric", "kpi": "metric", "measure": "metric",
        "value": "value", "amount": "value",
        "category": "category", "segment": "segment", "unit": "unit", "direction": "direction",
    }
    df = df.rename(columns={c: aliases.get(c, c) for c in df.columns})

    if "metric" in df.columns and "value" in df.columns:
        long_df = df.copy()
    else:
        period_col = "period" if "period" in df.columns else df.columns[0]
        if period_col != "period":
            df = df.rename(columns={period_col: "period"})
        value_cols = [c for c in df.columns if c != "period"]
        long_df = df.melt(id_vars=["period"], value_vars=value_cols, var_name="metric", value_name="value")

    long_df["period"] = long_df["period"].apply(_normalize_period)
    long_df["metric"] = long_df["metric"].astype(str)
    long_df["value"] = pd.to_numeric(long_df["value"], errors="coerce")
    long_df = long_df.dropna(subset=["value"])

    for col, default in [("category", long_df["metric"].apply(_infer_category)), ("segment", "Global"), ("unit", ""), ("direction", "higher_is_better")]:
        if col not in long_df.columns:
            long_df[col] = default

    return long_df[["period", "metric", "value", "category", "segment", "unit", "direction"]]


# ── Sample data ───────────────────────────────────────────────────────────

def generate_sample_kpi_data(periods: int = 14) -> pd.DataFrame:
    base_date = datetime(2025, 1, 1)
    period_list = [(base_date + pd.DateOffset(months=i)).strftime("%Y-%m") for i in range(periods)]

    metrics = {
        "Revenue": (1_200_000, 0.04, "Finance"),
        "Gross Margin": (540_000, 0.035, "Finance"),
        "Operating Expense": (620_000, 0.02, "Finance"),
        "Cash": (3_500_000, 0.01, "Finance"),
        "MRR": (420_000, 0.05, "Growth"),
        "New Customers": (180, 0.03, "Growth"),
        "Churn Rate": (0.045, -0.02, "Customer"),
        "NPS": (48, 0.01, "Customer"),
        "On-time Delivery": (0.92, 0.005, "Operations"),
        "Cycle Time (days)": (6.5, -0.01, "Operations"),
        "Headcount": (240, 0.01, "People"),
        "Engagement Score": (78, 0.006, "People"),
        "Carbon Intensity": (0.42, -0.015, "ESG"),
        "Diversity Index": (0.46, 0.01, "ESG"),
        "Safety Incidents": (3, -0.03, "ESG"),
    }

    rng = np.random.default_rng(42)
    records: List[dict] = []
    for metric, (base, growth, category) in metrics.items():
        current = base
        for period in period_list:
            noise = rng.normal(0, abs(current) * 0.03)
            current = max(0, current * (1 + growth) + noise)
            records.append({
                "period": period, "metric": metric, "value": round(current, 2),
                "category": category, "segment": "Global",
                "unit": "" if current > 1 else "ratio",
                "direction": "higher_is_better" if growth >= 0 else "lower_is_better",
            })
    return pd.DataFrame(records)


# ── Public macro KPIs (World Bank) ────────────────────────────────────────

def load_public_macro_kpis(years: int = 8) -> pd.DataFrame:
    indicators = {"GDP (USD)": "NY.GDP.MKTP.CD", "CPI Index": "FP.CPI.TOTL"}
    records: List[dict] = []
    for name, code in indicators.items():
        url = f"https://api.worldbank.org/v2/country/USA/indicator/{code}?format=json&per_page={years}"
        try:
            resp = requests.get(url, timeout=20)
            if resp.status_code != 200:
                continue
            data = resp.json()
            if not isinstance(data, list) or len(data) < 2:
                continue
            for entry in data[1]:
                if entry.get("value") is None:
                    continue
                records.append({
                    "period": f"{entry['date']}-01", "metric": name,
                    "value": float(entry["value"]), "category": "Macro",
                    "segment": "USA", "unit": "USD" if "GDP" in name else "index",
                    "direction": "higher_is_better",
                })
        except Exception as exc:
            log.warning("World Bank fetch failed for %s: %s", name, exc)
    return pd.DataFrame(records)
