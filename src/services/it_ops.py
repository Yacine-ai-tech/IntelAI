"""
IT Operations Service — System uptime, tickets, infrastructure, security.
Provides IT operations and infrastructure intelligence for OmniIntelOS.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from src.core.logger import get_logger

log = get_logger(__name__)


class ITOpsService:
    """IT operations and infrastructure analytics engine."""

    def get_it_overview(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get comprehensive IT operations overview."""
        if df.empty:
            return self._default_overview()

        it_df = self._filter_it(df)

        return {
            "system_uptime": self._extract(it_df, ["uptime", "system uptime", "availability"]) or 0,
            "open_tickets": int(self._extract(it_df, ["open tickets", "pending tickets", "ticket backlog"]) or 0),
            "resolved_today": int(self._extract(it_df, ["resolved today", "closed today"]) or 0),
            "mttr_hours": self._extract(it_df, ["mttr", "mean time to resolve", "resolution time"]) or 0,
            "incidents_month": int(self._extract(it_df, ["incidents", "total incidents"]) or 0),
            "critical_incidents": int(self._extract(it_df, ["critical incidents", "p1 incidents", "severity 1"]) or 0),
            "sla_compliance": self._extract(it_df, ["sla compliance", "sla met"]) or 0,
            "security_score": self._extract(it_df, ["security score", "security rating"]) or 0,
            "server_count": int(self._extract(it_df, ["server count", "servers", "total servers"]) or 0),
            "cloud_spend": self._extract(it_df, ["cloud spend", "cloud cost", "infrastructure cost"]) or 0,
            "deployment_frequency": self._extract(it_df, ["deployment frequency", "deployments"]) or 0,
            "change_failure_rate": self._extract(it_df, ["change failure rate", "failed deployments"]) or 0,
            "infrastructure": self._get_infra_breakdown(it_df),
            "trends": self._get_it_trends(it_df),
        }

    def get_ticket_analytics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get support ticket analytics."""
        it_df = self._filter_it(df)

        return {
            "total_open": int(self._extract(it_df, ["open tickets", "pending"]) or 0),
            "total_in_progress": int(self._extract(it_df, ["in progress", "active tickets"]) or 0),
            "total_resolved": int(self._extract(it_df, ["resolved tickets", "closed tickets"]) or 0),
            "avg_resolution_hours": self._extract(it_df, ["avg resolution time", "mttr"]) or 0,
            "first_response_hours": self._extract(it_df, ["first response", "response time"]) or 0,
            "escalation_rate": self._extract(it_df, ["escalation rate", "escalations"]) or 0,
            "satisfaction_score": self._extract(it_df, ["ticket satisfaction", "csat"]) or 0,
            "by_priority": {
                "critical": int(self._extract(it_df, ["critical tickets", "p1"]) or 0),
                "high": int(self._extract(it_df, ["high tickets", "p2"]) or 0),
                "medium": int(self._extract(it_df, ["medium tickets", "p3"]) or 0),
                "low": int(self._extract(it_df, ["low tickets", "p4"]) or 0),
            },
            "by_category": self._get_ticket_categories(it_df),
        }

    def get_security_dashboard(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get security metrics and posture."""
        it_df = self._filter_it(df)

        return {
            "security_score": self._extract(it_df, ["security score", "security rating"]) or 0,
            "vulnerabilities_open": int(self._extract(it_df, ["open vulnerabilities", "vulnerabilities"]) or 0),
            "vulnerabilities_critical": int(self._extract(it_df, ["critical vulnerabilities", "critical vuln"]) or 0),
            "patches_pending": int(self._extract(it_df, ["patches pending", "unpatched"]) or 0),
            "phishing_attempts_blocked": int(self._extract(it_df, ["phishing blocked", "blocked attacks"]) or 0),
            "failed_logins": int(self._extract(it_df, ["failed logins", "failed auth"]) or 0),
            "compliance_score": self._extract(it_df, ["compliance score", "compliance"]) or 0,
            "last_pen_test_score": self._extract(it_df, ["pen test score", "penetration test"]) or 0,
            "backup_success_rate": self._extract(it_df, ["backup success", "backup rate"]) or 0,
        }

    def get_infrastructure_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get infrastructure utilization metrics."""
        it_df = self._filter_it(df)

        return {
            "cpu_utilization": self._extract(it_df, ["cpu utilization", "cpu usage"]) or 0,
            "memory_utilization": self._extract(it_df, ["memory utilization", "ram usage"]) or 0,
            "disk_utilization": self._extract(it_df, ["disk utilization", "storage usage"]) or 0,
            "network_throughput_gbps": self._extract(it_df, ["network throughput", "bandwidth"]) or 0,
            "active_users": int(self._extract(it_df, ["active users", "concurrent users"]) or 0),
            "api_latency_ms": self._extract(it_df, ["api latency", "response time ms"]) or 0,
            "error_rate": self._extract(it_df, ["error rate", "5xx rate"]) or 0,
            "uptime_pct": self._extract(it_df, ["uptime", "availability"]) or 0,
        }

    def get_devops_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get DORA metrics and DevOps performance."""
        it_df = self._filter_it(df)

        return {
            "deployment_frequency": self._extract(it_df, ["deployment frequency", "deploy freq"]) or 0,
            "lead_time_hours": self._extract(it_df, ["lead time for changes", "deployment lead time"]) or 0,
            "change_failure_rate": self._extract(it_df, ["change failure rate"]) or 0,
            "mttr_hours": self._extract(it_df, ["mttr", "time to restore"]) or 0,
            "code_coverage": self._extract(it_df, ["code coverage", "test coverage"]) or 0,
            "build_success_rate": self._extract(it_df, ["build success", "ci success"]) or 0,
            "releases_month": int(self._extract(it_df, ["releases", "monthly releases"]) or 0),
        }

    def compute_it_health(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Compute IT operations health score (0-100)."""
        overview = self.get_it_overview(df)
        score = 0
        factors = {}

        # System uptime — max 30 pts
        uptime = overview["system_uptime"]
        if uptime >= 99.9:
            pts = 30
        elif uptime >= 99.5:
            pts = 25
        elif uptime >= 99:
            pts = 20
        elif uptime >= 95:
            pts = 15
        else:
            pts = 5
        score += pts
        factors["uptime"] = pts

        # SLA compliance — max 25 pts
        sla = overview["sla_compliance"]
        pts = min(25, max(0, int(sla * 0.25))) if sla else 12
        score += pts
        factors["sla_compliance"] = pts

        # Security — max 25 pts
        sec = overview["security_score"]
        pts = min(25, max(0, int(sec * 0.25))) if sec else 12
        score += pts
        factors["security"] = pts

        # Incident control (fewer critical = better) — max 20 pts
        critical = overview["critical_incidents"]
        if critical == 0:
            pts = 20
        elif critical <= 2:
            pts = 15
        elif critical <= 5:
            pts = 10
        else:
            pts = 5
        score += pts
        factors["incident_control"] = pts

        rating = "Excellent" if score >= 85 else "Good" if score >= 70 else "Fair" if score >= 55 else "Needs Improvement"
        color = "#22c55e" if score >= 85 else "#eab308" if score >= 70 else "#f97316" if score >= 55 else "#ef4444"

        return {"score": score, "rating": rating, "color": color, "factors": factors}

    # ── Internal Helpers ──────────────────────────────────────────────

    def _filter_it(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty or "category" not in df.columns:
            return df
        mask = df["category"].str.lower().isin(["it", "technology", "infrastructure", "operations"])
        filtered = df[mask]
        return filtered if not filtered.empty else df

    @staticmethod
    def _extract(df: pd.DataFrame, keywords: List[str]) -> Optional[float]:
        if df.empty or "metric" not in df.columns:
            return None
        mask = df["metric"].str.lower().apply(lambda m: any(k in m for k in keywords))
        matched = df[mask]
        if matched.empty:
            return None
        return float(matched.sort_values("period", ascending=False).iloc[0]["value"])

    def _get_infra_breakdown(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        return []

    def _get_it_trends(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        if df.empty or "period" not in df.columns:
            return []
        trends = []
        for period in sorted(df["period"].unique()):
            p_df = df[df["period"] == period]
            trends.append({
                "period": period,
                "uptime": self._extract(p_df, ["uptime", "availability"]) or 0,
                "tickets": int(self._extract(p_df, ["tickets", "open tickets"]) or 0),
                "incidents": int(self._extract(p_df, ["incidents"]) or 0),
            })
        return trends

    def _get_ticket_categories(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        return [
            {"category": "Hardware", "count": 0},
            {"category": "Software", "count": 0},
            {"category": "Network", "count": 0},
            {"category": "Access", "count": 0},
        ]

    @staticmethod
    def _default_overview() -> Dict[str, Any]:
        return {
            "system_uptime": 0, "open_tickets": 0, "resolved_today": 0,
            "mttr_hours": 0, "incidents_month": 0, "critical_incidents": 0,
            "sla_compliance": 0, "security_score": 0, "server_count": 0,
            "cloud_spend": 0, "deployment_frequency": 0, "change_failure_rate": 0,
            "infrastructure": [], "trends": [],
        }
