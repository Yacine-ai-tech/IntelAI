"""
Logistics Service — Supply chain, inventory, shipping, delivery tracking.
Provides logistics and supply chain intelligence for IntelAI.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from src.core.logger import get_logger

log = get_logger(__name__)


class LogisticsService:
    """Supply chain and logistics analytics engine."""

    def get_supply_chain_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get comprehensive supply chain overview."""
        if df.empty:
            return self._default_summary()

        ops_df = self._filter_logistics(df)

        return {
            "total_orders": int(self._extract(ops_df, ["total orders", "order count", "orders"]) or 0),
            "on_time_delivery_rate": self._extract(ops_df, ["on time delivery", "otd", "delivery rate"]) or 0,
            "fill_rate": self._extract(ops_df, ["fill rate", "order fill"]) or 0,
            "avg_lead_time_days": self._extract(ops_df, ["lead time", "avg lead time"]) or 0,
            "inventory_turnover": self._extract(ops_df, ["inventory turnover", "stock turnover"]) or 0,
            "carrying_cost": self._extract(ops_df, ["carrying cost", "inventory cost", "holding cost"]) or 0,
            "stockout_rate": self._extract(ops_df, ["stockout", "stock out", "out of stock"]) or 0,
            "return_rate": self._extract(ops_df, ["return rate", "returns"]) or 0,
            "shipping_cost_per_unit": self._extract(ops_df, ["shipping cost", "freight cost"]) or 0,
            "warehouse_utilization": self._extract(ops_df, ["warehouse utilization", "storage utilization"]) or 0,
            "warehouses": self._get_warehouse_breakdown(ops_df),
            "trends": self._get_logistics_trends(ops_df),
        }

    def get_inventory_status(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get inventory health metrics."""
        ops_df = self._filter_logistics(df)

        return {
            "total_sku_count": int(self._extract(ops_df, ["sku count", "total sku", "product count"]) or 0),
            "inventory_value": self._extract(ops_df, ["inventory value", "stock value"]) or 0,
            "days_of_supply": self._extract(ops_df, ["days of supply", "dos"]) or 0,
            "inventory_turnover": self._extract(ops_df, ["inventory turnover"]) or 0,
            "slow_moving_pct": self._extract(ops_df, ["slow moving", "dead stock"]) or 0,
            "overstock_pct": self._extract(ops_df, ["overstock", "excess stock"]) or 0,
            "stockout_rate": self._extract(ops_df, ["stockout rate", "out of stock"]) or 0,
            "accuracy_rate": self._extract(ops_df, ["inventory accuracy", "count accuracy"]) or 0,
            "categories": self._get_inventory_categories(ops_df),
        }

    def get_shipping_analytics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get shipping and delivery performance."""
        ops_df = self._filter_logistics(df)

        return {
            "shipments_today": int(self._extract(ops_df, ["shipments today", "daily shipments"]) or 0),
            "shipments_month": int(self._extract(ops_df, ["monthly shipments", "shipments month"]) or 0),
            "on_time_rate": self._extract(ops_df, ["on time delivery", "otd rate"]) or 0,
            "damaged_rate": self._extract(ops_df, ["damage rate", "damaged shipments"]) or 0,
            "avg_transit_days": self._extract(ops_df, ["transit time", "avg transit"]) or 0,
            "cost_per_shipment": self._extract(ops_df, ["cost per shipment", "shipping cost"]) or 0,
            "carrier_performance": self._get_carrier_performance(ops_df),
        }

    def get_supplier_metrics(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Get supplier performance data."""
        ops_df = self._filter_logistics(df)

        suppliers = []
        if "segment" in ops_df.columns:
            for seg, group in ops_df.groupby("segment"):
                if any(k in seg.lower() for k in ["supplier", "vendor", "partner"]):
                    suppliers.append({
                        "supplier": seg,
                        "quality_score": self._extract(group, ["quality", "quality score"]) or 0,
                        "on_time_rate": self._extract(group, ["on time", "delivery rate"]) or 0,
                        "lead_time_days": self._extract(group, ["lead time"]) or 0,
                        "cost_variance": self._extract(group, ["cost variance", "price variance"]) or 0,
                    })

        if not suppliers:
            suppliers = self._default_suppliers()

        return suppliers

    def compute_logistics_health(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Compute logistics health score (0-100)."""
        summary = self.get_supply_chain_summary(df)
        score = 0
        factors = {}

        # On-time delivery — max 30 pts
        otd = summary["on_time_delivery_rate"]
        pts = min(30, max(0, int(otd * 0.3))) if otd else 15
        score += pts
        factors["on_time_delivery"] = pts

        # Fill rate — max 25 pts
        fill = summary["fill_rate"]
        pts = min(25, max(0, int(fill * 0.25))) if fill else 12
        score += pts
        factors["fill_rate"] = pts

        # Inventory turnover (higher is better, target 6-12) — max 25 pts
        turns = summary["inventory_turnover"]
        if turns >= 8:
            pts = 25
        elif turns >= 6:
            pts = 20
        elif turns >= 4:
            pts = 15
        elif turns >= 2:
            pts = 10
        else:
            pts = 5
        score += pts
        factors["inventory_efficiency"] = pts

        # Stockout rate (lower is better) — max 20 pts
        stockout = summary["stockout_rate"]
        if stockout <= 1:
            pts = 20
        elif stockout <= 3:
            pts = 15
        elif stockout <= 5:
            pts = 10
        else:
            pts = 5
        score += pts
        factors["stockout_control"] = pts

        rating = "Excellent" if score >= 85 else "Good" if score >= 70 else "Fair" if score >= 55 else "Needs Improvement"
        color = "#22c55e" if score >= 85 else "#eab308" if score >= 70 else "#f97316" if score >= 55 else "#ef4444"

        return {"score": score, "rating": rating, "color": color, "factors": factors}

    # ── Internal Helpers ──────────────────────────────────────────────

    def _filter_logistics(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty or "category" not in df.columns:
            return df
        mask = df["category"].str.lower().isin(["operations", "logistics", "supply chain"])
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

    def _get_warehouse_breakdown(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        if df.empty or "segment" not in df.columns:
            return []
        result = []
        for seg in df["segment"].unique():
            if any(k in seg.lower() for k in ["warehouse", "dc", "distribution"]):
                seg_df = df[df["segment"] == seg]
                result.append({
                    "warehouse": seg,
                    "utilization": self._extract(seg_df, ["utilization"]) or 0,
                    "throughput": self._extract(seg_df, ["throughput"]) or 0,
                })
        return result

    def _get_logistics_trends(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        if df.empty or "period" not in df.columns:
            return []
        trends = []
        for period in sorted(df["period"].unique()):
            p_df = df[df["period"] == period]
            trends.append({
                "period": period,
                "orders": int(self._extract(p_df, ["orders", "order count"]) or 0),
                "on_time_rate": self._extract(p_df, ["on time delivery", "otd"]) or 0,
                "cost": self._extract(p_df, ["shipping cost", "logistics cost"]) or 0,
            })
        return trends

    def _get_inventory_categories(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        return []

    def _get_carrier_performance(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        return []

    @staticmethod
    def _default_summary() -> Dict[str, Any]:
        return {
            "total_orders": 0, "on_time_delivery_rate": 0, "fill_rate": 0,
            "avg_lead_time_days": 0, "inventory_turnover": 0, "carrying_cost": 0,
            "stockout_rate": 0, "return_rate": 0, "shipping_cost_per_unit": 0,
            "warehouse_utilization": 0, "warehouses": [], "trends": [],
        }

    @staticmethod
    def _default_suppliers() -> List[Dict[str, Any]]:
        return [
            {"supplier": "No data", "quality_score": 0, "on_time_rate": 0, "lead_time_days": 0, "cost_variance": 0},
        ]
