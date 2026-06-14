"""Persona tool layer — a whitelisted, executable set of tools per persona.

Each persona template declares ``allowed_tools``. ``run_tool()`` ENFORCES that whitelist:
a persona can only invoke a tool that appears in its own list (on top of role RBAC, which
the API layer applies). Tools wrap existing services (KPI query, health, risk, anomalies,
forecast, executive summary, board report) and return JSON-safe dicts.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from src.core.logger import get_logger

log = get_logger(__name__)


def _df(categories=None, metrics=None, periods=None):
    from src.services.pg_store import get_kpi_metrics
    return get_kpi_metrics(
        categories=[categories] if isinstance(categories, str) else categories,
        metrics=[metrics] if isinstance(metrics, str) else metrics,
        periods=[periods] if isinstance(periods, str) else periods,
    )


def _tool_kpi_query(args: Dict[str, Any]) -> Dict[str, Any]:
    df = _df(categories=args.get("category"), metrics=args.get("metric"), periods=args.get("period"))
    if df.empty:
        return {"rows": [], "count": 0}
    latest = args.get("period") or sorted(df["period"].unique())[-1]
    ld = df[df["period"] == latest]
    rows = [{"metric": r.metric, "value": float(r.value), "unit": r.unit, "category": r.category}
            for r in ld.itertuples()]
    return {"period": latest, "rows": rows[:50], "count": len(rows)}


def _tool_company_health(args: Dict[str, Any]) -> Dict[str, Any]:
    from src.services.insights import compute_health_index
    return compute_health_index(_df())


def _tool_risk_analysis(args: Dict[str, Any]) -> Dict[str, Any]:
    from src.services.insights import compute_risk_score
    return compute_risk_score(_df())


def _tool_anomaly_detection(args: Dict[str, Any]) -> Dict[str, Any]:
    from src.services.insights import detect_anomalies
    an = detect_anomalies(_df())
    if an is None or an.empty:
        return {"anomalies": [], "count": 0}
    aw = an[an["is_anomaly"] == True] if "is_anomaly" in an.columns else an  # noqa: E712
    rows = [{"metric": getattr(r, "metric", ""), "period": getattr(r, "period", ""),
             "value": float(getattr(r, "value", 0))} for r in aw.head(20).itertuples()]
    return {"anomalies": rows, "count": len(rows)}


def _tool_forecast(args: Dict[str, Any]) -> Dict[str, Any]:
    metric = args.get("metric")
    if not metric:
        return {"error": "forecast requires a 'metric' argument"}
    df = _df(metrics=metric)
    if df.empty:
        return {"error": f"no data for metric '{metric}'"}
    from src.services.forecasting import ForecastEngine
    fdf = (df[["period", "value"]].rename(columns={"period": "month_tag", "value": "actual"})
           .groupby("month_tag").agg({"actual": "mean"}).reset_index().sort_values("month_tag"))
    res = ForecastEngine().time_series_forecast(fdf, periods=int(args.get("periods", 3)))
    return {"metric": metric,
            "forecast": res.to_dict(orient="records") if res is not None and not res.empty else []}


def _tool_executive_summary(args: Dict[str, Any]) -> Dict[str, Any]:
    from src.services.insights import (
        build_executive_summary, compute_health_index, compute_risk_score, extract_key_metrics,
    )
    df = _df()
    h, rk, km = compute_health_index(df), compute_risk_score(df), extract_key_metrics(df)
    s = build_executive_summary(df, h, rk, km)
    return {"summary": " ".join(s) if isinstance(s, list) else s, "health": h, "risk": rk}


def _tool_report_generate(args: Dict[str, Any]) -> Dict[str, Any]:
    return {"available": True, "format": "pdf", "endpoint": "/api/v1/data/export",
            "note": "POST /api/v1/data/export {source_type:'kpis', format:'pdf'} for the board PDF."}


# Canonical, implemented tools.
TOOLS = {
    "kpi_query": _tool_kpi_query,
    "company_health": _tool_company_health,
    "risk_analysis": _tool_risk_analysis,
    "anomaly_detection": _tool_anomaly_detection,
    "forecast": _tool_forecast,
    "executive_summary": _tool_executive_summary,
    "report_generate": _tool_report_generate,
}

# Domain-specific persona tool names → (canonical tool, implicit args).
_ALIASES = {
    "people_metrics": ("kpi_query", {"category": "People"}),
    "engagement_analysis": ("kpi_query", {"category": "People"}),
    "ops_metrics": ("kpi_query", {"category": "Operations"}),
    "supply_chain": ("kpi_query", {"category": "Logistics"}),
    "esg_metrics": ("kpi_query", {"category": "ESG"}),
    "tech_metrics": ("kpi_query", {"category": "IT"}),
    "technology_metrics": ("kpi_query", {"category": "IT"}),
    "financial_statements": ("kpi_query", {"category": "Finance"}),
    "budget_analysis": ("kpi_query", {"category": "Finance"}),
    "sustainability_report": ("executive_summary", {}),
    "sustain_rpt": ("executive_summary", {}),
    "market_analysis": ("executive_summary", {}),
    "data_analysis": ("executive_summary", {}),
    "report": ("report_generate", {}),
    "alerts": ("anomaly_detection", {}),
    "basic_query": ("kpi_query", {}),
}


def list_persona_tools(persona_name: str) -> List[str]:
    from src.services.omnismart_chatbot import PERSONA_TEMPLATES
    t = PERSONA_TEMPLATES.get(persona_name)
    return list(t.get("allowed_tools", [])) if t else []


def run_tool(persona_name: str, tool_name: str, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Execute ``tool_name`` for ``persona_name``, enforcing the persona's whitelist.

    Returns ``{"error": ...}`` (never raises) when the tool is outside the whitelist or not
    implemented, so the API/UI gets a clean, role-appropriate message."""
    args = args or {}
    allowed = list_persona_tools(persona_name)
    if not allowed:
        return {"error": f"Unknown persona '{persona_name}'"}
    if tool_name not in allowed:
        return {"error": f"Tool '{tool_name}' is not in the '{persona_name}' persona's whitelist",
                "allowed_tools": allowed}
    canonical, implicit = _ALIASES.get(tool_name, (tool_name, {}))
    handler = TOOLS.get(canonical)
    if handler is None:
        return {"error": f"Tool '{tool_name}' is whitelisted but not implemented yet",
                "allowed_tools": allowed}
    try:
        return {"persona": persona_name, "tool": tool_name, "result": handler({**implicit, **args})}
    except Exception as e:  # noqa: BLE001
        log.warning("Tool '%s' failed: %s", tool_name, e)
        return {"error": f"Tool '{tool_name}' failed: {str(e)[:160]}"}
