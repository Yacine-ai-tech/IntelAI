"""
HR Service — Employee analytics, headcount, turnover, satisfaction, training.
Provides comprehensive human resources intelligence for OmniIntelOS.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from src.core.logger import get_logger

log = get_logger(__name__)


class HRService:
    """Human Resources analytics engine."""

    def get_workforce_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get comprehensive workforce overview from KPI data."""
        if df.empty:
            return self._default_workforce_summary()

        hr_df = df[df["category"].str.lower() == "people"] if "category" in df.columns else df

        headcount = self._extract_metric(hr_df, ["headcount", "employee count", "total employees"])
        turnover = self._extract_metric(hr_df, ["turnover rate", "attrition", "churn rate"])
        satisfaction = self._extract_metric(hr_df, ["satisfaction", "engagement", "enps", "employee nps"])
        avg_tenure = self._extract_metric(hr_df, ["tenure", "avg tenure", "average tenure"])
        open_positions = self._extract_metric(hr_df, ["open positions", "vacancies", "job openings"])
        training_hours = self._extract_metric(hr_df, ["training hours", "learning hours"])
        cost_per_hire = self._extract_metric(hr_df, ["cost per hire", "recruitment cost"])
        absenteeism = self._extract_metric(hr_df, ["absenteeism", "absence rate", "sick days"])

        return {
            "headcount": headcount or 0,
            "turnover_rate": turnover or 0,
            "satisfaction_score": satisfaction or 0,
            "avg_tenure_years": avg_tenure or 0,
            "open_positions": int(open_positions or 0),
            "training_hours_per_employee": training_hours or 0,
            "cost_per_hire": cost_per_hire or 0,
            "absenteeism_rate": absenteeism or 0,
            "departments": self._get_department_breakdown(hr_df),
            "trends": self._get_hr_trends(hr_df),
        }

    def get_department_analytics(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Get per-department metrics."""
        if df.empty:
            return self._default_departments()

        hr_df = df[df["category"].str.lower() == "people"] if "category" in df.columns else df

        departments = []
        if "segment" in hr_df.columns:
            for dept, group in hr_df.groupby("segment"):
                departments.append({
                    "department": dept,
                    "headcount": self._extract_metric(group, ["headcount", "employee count"]) or 0,
                    "satisfaction": self._extract_metric(group, ["satisfaction", "engagement"]) or 0,
                    "turnover": self._extract_metric(group, ["turnover", "attrition"]) or 0,
                    "avg_salary": self._extract_metric(group, ["salary", "compensation", "avg salary"]) or 0,
                    "training_completion": self._extract_metric(group, ["training completion", "training"]) or 0,
                })

        if not departments:
            departments = self._default_departments()

        return departments

    def get_recruitment_pipeline(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get recruitment funnel data."""
        hr_df = df[df["category"].str.lower() == "people"] if "category" in df.columns and not df.empty else df

        return {
            "open_positions": int(self._extract_metric(hr_df, ["open positions", "vacancies"]) or 0),
            "applications_received": int(self._extract_metric(hr_df, ["applications", "applicants"]) or 0),
            "interviews_scheduled": int(self._extract_metric(hr_df, ["interviews", "interview"]) or 0),
            "offers_extended": int(self._extract_metric(hr_df, ["offers extended", "offers"]) or 0),
            "offers_accepted": int(self._extract_metric(hr_df, ["offers accepted", "hires"]) or 0),
            "avg_time_to_fill_days": self._extract_metric(hr_df, ["time to fill", "time to hire"]) or 0,
            "cost_per_hire": self._extract_metric(hr_df, ["cost per hire"]) or 0,
        }

    def get_training_overview(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get training and development metrics."""
        hr_df = df[df["category"].str.lower() == "people"] if "category" in df.columns and not df.empty else df

        return {
            "total_training_hours": self._extract_metric(hr_df, ["total training hours"]) or 0,
            "hours_per_employee": self._extract_metric(hr_df, ["training hours per employee", "training hours"]) or 0,
            "completion_rate": self._extract_metric(hr_df, ["training completion", "completion rate"]) or 0,
            "programs_active": int(self._extract_metric(hr_df, ["active programs", "training programs"]) or 0),
            "satisfaction_with_training": self._extract_metric(hr_df, ["training satisfaction"]) or 0,
            "budget_utilization": self._extract_metric(hr_df, ["training budget", "l&d budget"]) or 0,
        }

    def compute_hr_health_score(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Compute overall HR health score (0-100)."""
        summary = self.get_workforce_summary(df)
        score = 0
        factors = {}

        # Turnover (lower is better) — max 25 pts
        turnover = summary["turnover_rate"]
        if turnover <= 5:
            pts = 25
        elif turnover <= 10:
            pts = 20
        elif turnover <= 15:
            pts = 15
        elif turnover <= 25:
            pts = 10
        else:
            pts = 5
        score += pts
        factors["turnover"] = pts

        # Satisfaction (higher is better) — max 25 pts
        sat = summary["satisfaction_score"]
        if sat >= 80:
            pts = 25
        elif sat >= 70:
            pts = 20
        elif sat >= 60:
            pts = 15
        elif sat >= 50:
            pts = 10
        else:
            pts = 5
        score += pts
        factors["satisfaction"] = pts

        # Training hours (higher is better) — max 25 pts
        training = summary["training_hours_per_employee"]
        if training >= 40:
            pts = 25
        elif training >= 30:
            pts = 20
        elif training >= 20:
            pts = 15
        elif training >= 10:
            pts = 10
        else:
            pts = 5
        score += pts
        factors["training"] = pts

        # Absenteeism (lower is better) — max 25 pts
        absent = summary["absenteeism_rate"]
        if absent <= 2:
            pts = 25
        elif absent <= 4:
            pts = 20
        elif absent <= 6:
            pts = 15
        elif absent <= 10:
            pts = 10
        else:
            pts = 5
        score += pts
        factors["absenteeism"] = pts

        rating = "Excellent" if score >= 85 else "Good" if score >= 70 else "Fair" if score >= 55 else "Needs Improvement"
        color = "#22c55e" if score >= 85 else "#eab308" if score >= 70 else "#f97316" if score >= 55 else "#ef4444"

        return {"score": score, "rating": rating, "color": color, "factors": factors}

    # ── Internal Helpers ──────────────────────────────────────────────

    @staticmethod
    def _extract_metric(df: pd.DataFrame, keywords: List[str]) -> Optional[float]:
        if df.empty or "metric" not in df.columns:
            return None
        mask = df["metric"].str.lower().apply(lambda m: any(k in m for k in keywords))
        matched = df[mask]
        if matched.empty:
            return None
        return float(matched.sort_values("period", ascending=False).iloc[0]["value"])

    def _get_department_breakdown(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        if df.empty or "segment" not in df.columns:
            return []
        result = []
        for seg in df["segment"].unique():
            seg_df = df[df["segment"] == seg]
            hc = self._extract_metric(seg_df, ["headcount", "employee count"])
            result.append({"department": seg, "headcount": hc or 0})
        return result

    def _get_hr_trends(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        if df.empty or "period" not in df.columns:
            return []
        trends = []
        for period in sorted(df["period"].unique()):
            p_df = df[df["period"] == period]
            trends.append({
                "period": period,
                "headcount": self._extract_metric(p_df, ["headcount", "employee count"]) or 0,
                "turnover": self._extract_metric(p_df, ["turnover", "attrition"]) or 0,
                "satisfaction": self._extract_metric(p_df, ["satisfaction", "engagement"]) or 0,
            })
        return trends

    @staticmethod
    def _default_workforce_summary() -> Dict[str, Any]:
        return {
            "headcount": 0, "turnover_rate": 0, "satisfaction_score": 0,
            "avg_tenure_years": 0, "open_positions": 0,
            "training_hours_per_employee": 0, "cost_per_hire": 0,
            "absenteeism_rate": 0, "departments": [], "trends": [],
        }

    @staticmethod
    def _default_departments() -> List[Dict[str, Any]]:
        return [
            {"department": "Engineering", "headcount": 0, "satisfaction": 0, "turnover": 0, "avg_salary": 0, "training_completion": 0},
            {"department": "Sales", "headcount": 0, "satisfaction": 0, "turnover": 0, "avg_salary": 0, "training_completion": 0},
            {"department": "Marketing", "headcount": 0, "satisfaction": 0, "turnover": 0, "avg_salary": 0, "training_completion": 0},
            {"department": "Operations", "headcount": 0, "satisfaction": 0, "turnover": 0, "avg_salary": 0, "training_completion": 0},
            {"department": "Finance", "headcount": 0, "satisfaction": 0, "turnover": 0, "avg_salary": 0, "training_completion": 0},
        ]
