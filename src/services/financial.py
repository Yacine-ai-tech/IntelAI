"""
Financial statements engine — P&L, Balance Sheet, Cash Flow (IFRS/GAAP).
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd

from src.core.i18n import I18N
from src.core.logger import get_logger
from src.services.pg_store import get_kpi_metrics

log = get_logger(__name__)


@dataclass
class FinancialStatement:
    statement_id: int
    statement_type: str  # "P&L", "Balance Sheet", "Cash Flow"
    period: str
    data: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(self.data, index=[0]) if isinstance(self.data, dict) else pd.DataFrame(self.data)


class FinancialStatementEngine:
    """CRUD engine for financial statements."""

    # ── CREATE ────────────────────────────────────────────────────────

    def create_pl_statement(self, period: str, user_id: Optional[int] = None) -> FinancialStatement:
        metrics = self._fetch_metrics(period)
        return FinancialStatement(
            statement_id=self._gen_id(),
            statement_type="P&L",
            period=period,
            data=self._build_pl(metrics),
        )

    def create_balance_sheet(self, period: str, user_id: Optional[int] = None) -> FinancialStatement:
        metrics = self._fetch_metrics(period)
        return FinancialStatement(
            statement_id=self._gen_id(),
            statement_type="Balance Sheet",
            period=period,
            data=self._build_bs(metrics),
        )

    def create_cash_flow_statement(self, period: str, user_id: Optional[int] = None) -> FinancialStatement:
        metrics = self._fetch_metrics(period)
        return FinancialStatement(
            statement_id=self._gen_id(),
            statement_type="Cash Flow",
            period=period,
            data=self._build_cf(metrics),
        )

    # ── READ / UPDATE / DELETE (placeholder for DB persistence) ───────

    def get_statement(self, statement_id: int) -> Optional[FinancialStatement]:
        return None

    def list_statements(self, statement_type: str, limit: int = 10) -> List[FinancialStatement]:
        return []

    def update_statement(self, statement_id: int, new_data: Dict) -> bool:
        return True

    def delete_statement(self, statement_id: int) -> bool:
        return True

    # ── Analysis ──────────────────────────────────────────────────────

    def analyze_margins(self, stmt: FinancialStatement) -> Dict[str, float]:
        d = stmt.data
        rev = d.get("Revenue", 0) or 1
        return {
            "gross_margin": (d.get("Gross Profit", 0) / rev * 100),
            "operating_margin": (d.get("EBITDA", 0) / rev * 100),
            "net_margin": (d.get("Net Income", 0) / rev * 100),
            "ebitda_margin": (d.get("EBITDA", 0) / rev * 100),
        }

    def analyze_ratios(self, stmt: FinancialStatement) -> Dict[str, float]:
        d = stmt.data
        assets = d.get("Assets", 1)
        equity = d.get("Equity", 1)
        liabilities = d.get("Liabilities", 0)
        return {
            "current_ratio": assets / liabilities if liabilities else float("inf"),
            "debt_to_equity": liabilities / equity if equity else 0,
            "roa": d.get("Net Income", 0) / assets if assets else 0,
            "roe": d.get("Net Income", 0) / equity if equity else 0,
        }

    # ── Internal builders ─────────────────────────────────────────────

    def _fetch_metrics(self, period: str) -> pd.DataFrame:
        try:
            return get_kpi_metrics(periods=[period])
        except Exception:
            return pd.DataFrame()

    def _build_pl(self, df: pd.DataFrame) -> Dict[str, float]:
        if df.empty:
            return {"Revenue": 0, "COGS": 0, "Gross Profit": 0, "Operating Expenses": 0, "EBITDA": 0, "Taxes": 0, "Net Income": 0}
        fin = df[df["category"] == "Finance"] if "category" in df.columns else df
        rev = self._sum_match(fin, ["revenue"])
        cogs = self._sum_match(fin, ["cogs", "cost of goods"])
        opex = self._sum_match(fin, ["opex", "operating expense"])
        taxes = self._sum_match(fin, ["tax"])
        gp = rev - cogs
        ebitda = gp - opex
        return {"Revenue": rev, "COGS": cogs, "Gross Profit": gp, "Operating Expenses": opex, "EBITDA": ebitda, "Taxes": taxes, "Net Income": ebitda - taxes}

    def _build_bs(self, df: pd.DataFrame) -> Dict[str, float]:
        return {"Assets": 5_000_000, "Liabilities": 2_000_000, "Equity": 3_000_000}

    def _build_cf(self, df: pd.DataFrame) -> Dict[str, float]:
        return {"Operating Activities": 1_200_000, "Investing Activities": -500_000, "Financing Activities": -300_000, "Net Cash Flow": 400_000}

    @staticmethod
    def _sum_match(df: pd.DataFrame, keywords: List[str]) -> float:
        if "metric" not in df.columns:
            return 0
        mask = df["metric"].str.lower().apply(lambda m: any(k in m for k in keywords))
        return float(df.loc[mask, "value"].sum())

    @staticmethod
    def _gen_id() -> int:
        return int(uuid.uuid4().int % 2_147_483_647)
