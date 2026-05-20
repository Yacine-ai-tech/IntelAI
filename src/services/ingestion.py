"""
Service for bulk ingestion of documents and data.
"""
from __future__ import annotations

import os
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from src.core.config import settings
from src.core.logger import get_logger
from src.services.pg_store import store_knowledge_docs, store_kpi_metrics

log = get_logger(__name__)


# ── helpers ──────────────────────────────────────────────────────────────────

def _parse_pdf(content: bytes) -> str:
    try:
        import pypdf
        reader = pypdf.PdfReader(BytesIO(content))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as e:
        log.warning(f"PDF parse failed: {e}")
        return ""


def _map_category(metric: str) -> str:
    m = str(metric).lower()
    if any(x in m for x in ["revenue", "profit", "margin", "ebitda", "cost", "expense"]):
        return "Finance"
    if any(x in m for x in ["customer", "mrr", "arr", "churn", "cac", "ltv"]):
        return "Growth"
    if any(x in m for x in ["carbon", "emissions", "diversity", "waste", "energy", "esg"]):
        return "ESG"
    if any(x in m for x in ["headcount", "turnover", "engagement"]):
        return "People"
    return "Operations"


# ── public API ────────────────────────────────────────────────────────────────

def process_bulk_csv(df: pd.DataFrame, source_name: str) -> bool:
    """Process a CSV of KPI metrics — handles wide and long formats."""
    try:
        if "Date" in df.columns:
            df["period"] = df["Date"]

        required_cols = {"period", "metric", "value", "category", "segment"}

        if not required_cols.issubset(df.columns):
            # Wide format → melt to long
            id_vars = [c for c in ["Date", "Company", "Sector"] if c in df.columns]
            value_vars = [c for c in df.columns if c not in id_vars and c != "period"]
            melted = df.melt(id_vars=id_vars, value_vars=value_vars, var_name="metric", value_name="value")
            if "Date" in melted.columns:
                melted["period"] = melted["Date"]
            melted["category"] = melted["metric"].apply(_map_category)
            melted["segment"] = melted["Company"] if "Company" in melted.columns else "Global"
            df = melted

        if "unit" not in df.columns:
            df["unit"] = ""
        if "direction" not in df.columns:
            df["direction"] = "up"

        store_kpi_metrics(df[["period", "metric", "value", "category", "segment", "unit", "direction"]], source_name=source_name, replace=True)
        return True
    except Exception as e:
        log.error(f"Bulk CSV error for {source_name}: {e}")
        return False


def process_bulk_file(file_name: str, file_content: bytes, category: str = "Misc") -> bool:
    """Process a single file (PDF, TXT) into the Knowledge Base."""
    try:
        ext = Path(file_name).suffix.lower()

        if ext == ".txt":
            content_str = file_content.decode("utf-8", errors="replace")
        elif ext == ".pdf":
            content_str = _parse_pdf(file_content)
        else:
            log.warning(f"Unsupported file type for bulk ingest: {ext}")
            return False

        if not content_str.strip():
            return False

        store_knowledge_docs([{
            "title": Path(file_name).stem,
            "content": content_str,
            "source": f"Bulk/{category}",
            "doc_type": ext.lstrip("."),
            "created_at": datetime.utcnow().isoformat(),
        }])
        return True
    except Exception as e:
        log.error(f"Bulk file error for {file_name}: {e}")
        return False


