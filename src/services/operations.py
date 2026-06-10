"""
Operations Service — Process efficiency, quality, capacity, production metrics.
Provides operational excellence intelligence for IntelAI.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from src.core.logger import get_logger

log = get_logger(__name__)


class OperationsService:
    """Operations and process analytics engine."""

    def get_operations_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get comprehensive operations overview."""
        if df.empty:
            return self._default_summary()

        ops_df = self._filter_ops(df)

        return {
            "overall_efficiency": self._extract(ops_df, ["overall efficiency", "oee", "efficiency"]) or 0,
            "capacity_utilization": self._extract(ops_df, ["capacity utilization", "capacity"]) or 0,
            "quality_rate": self._extract(ops_df, ["quality rate", "defect-free rate", "yield"]) or 0,
            "defect_rate": self._extract(ops_df, ["defect rate", "reject rate", "scrap rate"]) or 0,
            "throughput": self._extract(ops_df, ["throughput", "production rate", "output"]) or 0,
            "cycle_time": self._extract(ops_df, ["cycle time", "process time"]) or 0,
            "downtime_hours": self._extract(ops_df, ["downtime", "unplanned downtime"]) or 0,
            "cost_per_unit": self._extract(ops_df, ["cost per unit", "unit cost"]) or 0,
            "on_time_completion": self._extract(ops_df, ["on time completion", "schedule adherence"]) or 0,
            "safety_incidents": int(self._extract(ops_df, ["safety incident", "workplace incidents"]) or 0),
            "energy_consumption": self._extract(ops_df, ["energy consumption", "kwh", "energy usage"]) or 0,
            "waste_reduction": self._extract(ops_df, ["waste reduction", "waste rate"]) or 0,
            "process_areas": self._get_process_areas(ops_df),
            "trends": self._get_ops_trends(ops_df),
        }

    def get_quality_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get quality control and assurance metrics."""
        ops_df = self._filter_ops(df)

        return {
            "overall_quality_rate": self._extract(ops_df, ["quality rate", "yield rate"]) or 0,
            "defect_rate_ppm": self._extract(ops_df, ["defect rate", "ppm"]) or 0,
            "first_pass_yield": self._extract(ops_df, ["first pass yield", "fpy"]) or 0,
            "rework_rate": self._extract(ops_df, ["rework rate", "rework"]) or 0,
            "customer_complaints": int(self._extract(ops_df, ["customer complaints", "complaints"]) or 0),
            "cost_of_quality": self._extract(ops_df, ["cost of quality", "coq"]) or 0,
            "inspection_pass_rate": self._extract(ops_df, ["inspection pass", "inspection rate"]) or 0,
            "nonconformance_count": int(self._extract(ops_df, ["nonconformance", "ncr"]) or 0),
        }

    def get_production_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get production and manufacturing metrics."""
        ops_df = self._filter_ops(df)

        return {
            "daily_output": self._extract(ops_df, ["daily output", "daily production"]) or 0,
            "capacity_utilization": self._extract(ops_df, ["capacity utilization"]) or 0,
            "oee": self._extract(ops_df, ["oee", "overall equipment", "production efficiency"]) or 0,
            "planned_vs_actual": self._extract(ops_df, ["planned vs actual", "plan adherence"]) or 0,
            "changeover_time": self._extract(ops_df, ["changeover time", "setup time"]) or 0,
            "scrap_rate": self._extract(ops_df, ["scrap rate", "waste rate"]) or 0,
            "maintenance_compliance": self._extract(ops_df, ["maintenance compliance", "pm compliance"]) or 0,
            "labor_productivity": self._extract(ops_df, ["labor productivity", "output per worker"]) or 0,
        }

    def get_safety_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get workplace safety metrics."""
        ops_df = self._filter_ops(df)

        return {
            "total_incidents": int(self._extract(ops_df, ["safety incidents", "total incidents"]) or 0),
            "lost_time_incidents": int(self._extract(ops_df, ["lost time", "lti"]) or 0),
            "near_misses": int(self._extract(ops_df, ["near misses", "near miss"]) or 0),
            "days_without_incident": int(self._extract(ops_df, ["days without incident", "safe days"]) or 0),
            "safety_training_completion": self._extract(ops_df, ["safety training", "safety completion"]) or 0,
            "trir": self._extract(ops_df, ["trir", "total recordable", "safety incident rate"]) or 0,
            "severity_rate": self._extract(ops_df, ["severity rate"]) or 0,
        }

    def compute_ops_health(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Compute operations health score (0-100)."""
        summary = self.get_operations_summary(df)
        score = 0
        factors = {}

        # Overall efficiency — max 25 pts
        eff = summary["overall_efficiency"]
        if eff >= 90:
            pts = 25
        elif eff >= 80:
            pts = 20
        elif eff >= 70:
            pts = 15
        elif eff >= 60:
            pts = 10
        else:
            pts = 5
        score += pts
        factors["efficiency"] = pts

        # Quality rate — max 25 pts
        qual = summary["quality_rate"]
        if qual >= 99:
            pts = 25
        elif qual >= 97:
            pts = 20
        elif qual >= 95:
            pts = 15
        elif qual >= 90:
            pts = 10
        else:
            pts = 5
        score += pts
        factors["quality"] = pts

        # On-time completion — max 25 pts
        otc = summary["on_time_completion"]
        pts = min(25, max(0, int(otc * 0.25))) if otc else 12
        score += pts
        factors["on_time"] = pts

        # Safety (fewer incidents = better) — max 25 pts
        incidents = summary["safety_incidents"]
        if incidents == 0:
            pts = 25
        elif incidents <= 2:
            pts = 20
        elif incidents <= 5:
            pts = 15
        elif incidents <= 10:
            pts = 10
        else:
            pts = 5
        score += pts
        factors["safety"] = pts

        rating = "Excellent" if score >= 85 else "Good" if score >= 70 else "Fair" if score >= 55 else "Needs Improvement"
        color = "#22c55e" if score >= 85 else "#eab308" if score >= 70 else "#f97316" if score >= 55 else "#ef4444"

        return {"score": score, "rating": rating, "color": color, "factors": factors}

    # ── Internal Helpers ──────────────────────────────────────────────

    def _filter_ops(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty or "category" not in df.columns:
            return df
        mask = df["category"].str.lower().isin(["operations", "production", "manufacturing", "quality"])
        filtered = df[mask]
        return filtered if not filtered.empty else df

    @staticmethod
    def _extract(df: pd.DataFrame, keywords: List[str]) -> Optional[float]:
        if df.empty or "metric" not in df.columns:
            return None
        norm = df["metric"].str.lower().str.replace("-", " ", regex=False)
        mask = norm.apply(lambda m: any(k in m for k in keywords))
        matched = df[mask]
        if matched.empty:
            return None
        return float(matched.sort_values("period", ascending=False).iloc[0]["value"])

    def _get_process_areas(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        if df.empty or "segment" not in df.columns:
            return []
        result = []
        for seg in df["segment"].unique():
            seg_df = df[df["segment"] == seg]
            result.append({
                "area": seg,
                "efficiency": self._extract(seg_df, ["efficiency"]) or 0,
                "quality": self._extract(seg_df, ["quality"]) or 0,
            })
        return result

    def _get_ops_trends(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        if df.empty or "period" not in df.columns:
            return []
        trends = []
        for period in sorted(df["period"].unique()):
            p_df = df[df["period"] == period]
            trends.append({
                "period": period,
                "efficiency": self._extract(p_df, ["efficiency", "oee"]) or 0,
                "quality": self._extract(p_df, ["quality rate", "yield"]) or 0,
                "output": self._extract(p_df, ["throughput", "output"]) or 0,
            })
        return trends

    @staticmethod
    def _default_summary() -> Dict[str, Any]:
        return {
            "overall_efficiency": 0, "capacity_utilization": 0, "quality_rate": 0,
            "defect_rate": 0, "throughput": 0, "cycle_time": 0,
            "downtime_hours": 0, "cost_per_unit": 0, "on_time_completion": 0,
            "safety_incidents": 0, "energy_consumption": 0, "waste_reduction": 0,
            "process_areas": [], "trends": [],
        }
