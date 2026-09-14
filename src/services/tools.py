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


METRIC_SYNONYMS = {
    # Cloud & IT
    "cloud": "Cloud Spend",
    "cloud spend": "Cloud Spend",
    "cloud_spend": "Cloud Spend",
    "cloud spend forecast": "Cloud Spend",
    "cloud cost": "Cloud Spend",
    "cloud costs": "Cloud Spend",
    "cloud expenses": "Cloud Spend",
    "cloud infrastructure": "Cloud Spend",
    "it spend": "Cloud Spend",
    "it cost": "Cloud Spend",
    "dépenses cloud": "Cloud Spend",
    "depenses cloud": "Cloud Spend",
    "coût cloud": "Cloud Spend",
    "cout cloud": "Cloud Spend",
    "dépenses informatiques": "Cloud Spend",
    "depenses informatiques": "Cloud Spend",
    "uptime": "System Uptime",
    "disponibilité": "Availability",
    "disponibilite": "Availability",
    "temps de fonctionnement": "System Uptime",
    "incidents critiques": "Critical Incidents",
    "vulnérabilités critiques": "Critical Vulnerabilities",
    "vulnerabilites critiques": "Critical Vulnerabilities",
    "score de sécurité": "Security Score",
    "score de securite": "Security Score",
    "fréquence de déploiement": "Deployment Frequency",
    "frequence de deploiement": "Deployment Frequency",

    # Finance
    "capex": "Capital Expenditure",
    "capital expenditure": "Capital Expenditure",
    "capital expenses": "Capital Expenditure",
    "dépenses d'investissement": "Capital Expenditure",
    "depenses dinvestissement": "Capital Expenditure",
    "opex": "Operating Expenses",
    "operating expenses": "Operating Expenses",
    "charges d'exploitation": "Operating Expenses",
    "charges dexploitation": "Operating Expenses",
    "dépenses d'exploitation": "Operating Expenses",
    "depenses dexploitation": "Operating Expenses",
    "cogs": "COGS",
    "cost of goods sold": "COGS",
    "coût des marchandises vendues": "COGS",
    "cout des marchandises vendues": "COGS",
    "mrr": "MRR",
    "arr": "ARR",
    "ebitda": "EBITDA",
    "ebitda margin": "EBITDA Margin",
    "marge ebitda": "EBITDA Margin",
    "revenue": "Revenue",
    "total revenue": "Revenue",
    "sales": "Revenue",
    "chiffre d'affaires": "Revenue",
    "chiffre d affaires": "Revenue",
    "chiffre d'affaires (xof)": "Chiffre d'affaires (XOF)",
    "ca": "Revenue",
    "revenu": "Revenue",
    "revenus": "Revenue",
    "gross margin": "Gross Margin",
    "marge brute": "Gross Margin",
    "gross profit": "Gross Profit",
    "bénéfice brut": "Gross Profit",
    "benefice brut": "Gross Profit",
    "net income": "Net Income",
    "net profit": "Net Income",
    "bénéfice net": "Net Income",
    "benefice net": "Net Income",
    "résultat net": "Net Income",
    "resultat net": "Net Income",
    "cash balance": "Cash Balance",
    "trésorerie": "Cash Balance",
    "tresorerie": "Cash Balance",
    "solde de trésorerie": "Cash Balance",
    "cash runway": "Cash Runway",
    "runway": "Cash Runway",
    "piste de trésorerie": "Cash Runway",
    "total debt": "Total Debt",
    "dette totale": "Total Debt",

    # People / HR
    "headcount": "Headcount",
    "effectif": "Headcount",
    "effectifs": "Headcount",
    "salariés": "Headcount",
    "salaries": "Headcount",
    "nombre d'employés": "Headcount",
    "nombre d employes": "Headcount",
    "turnover": "Annual Employee Turnover",
    "annual employee turnover": "Annual Employee Turnover",
    "taux de rotation": "Annual Employee Turnover",
    "rotation du personnel": "Annual Employee Turnover",
    "absenteeism": "Absenteeism Rate",
    "absenteeism rate": "Absenteeism Rate",
    "absentéisme": "Absenteeism Rate",
    "absenteisme": "Absenteeism Rate",
    "taux d'absentéisme": "Absenteeism Rate",
    "taux d absenteisme": "Absenteeism Rate",
    "cost per hire": "Cost Per Hire",
    "coût par embauche": "Cost Per Hire",
    "cout par embauche": "Cost Per Hire",
    "time to hire": "Time to Hire",
    "délai de recrutement": "Time to Hire",
    "delai de recrutement": "Time to Hire",
    "enps": "Employee Net Promoter Score",
    "training hours": "Training Hours per Employee",
    "heures de formation": "Training Hours per Employee",

    # Operations & Logistics
    "capacity utilization": "Capacity Utilization",
    "utilisation des capacités": "Capacity Utilization",
    "utilisation des capacites": "Capacity Utilization",
    "defect rate": "Defect Rate",
    "taux de défaut": "Defect Rate",
    "taux de defaut": "Defect Rate",
    "quality rate": "Quality Rate",
    "taux de qualité": "Quality Rate",
    "taux de qualite": "Quality Rate",
    "oee": "Overall Equipment Effectiveness",
    "overall equipment effectiveness": "Overall Equipment Effectiveness",
    "efficacité globale": "Overall Equipment Effectiveness",
    "efficacite globale": "Overall Equipment Effectiveness",
    "lead time": "Average Lead Time",
    "average lead time": "Average Lead Time",
    "délai moyen": "Average Lead Time",
    "delai moyen": "Average Lead Time",
    "total orders": "Total Orders",
    "commandes": "Total Orders",
    "commandes totales": "Total Orders",
    "on-time delivery": "On-Time Delivery Rate",
    "on time delivery": "On-Time Delivery Rate",
    "livraison à temps": "On-Time Delivery Rate",
    "livraison a temps": "On-Time Delivery Rate",
    "inventory turnover": "Inventory Turnover",
    "rotation des stocks": "Inventory Turnover",
    "stockout rate": "Stockout Rate",
    "taux de rupture": "Stockout Rate",

    # Growth
    "cac": "CAC",
    "ltv": "LTV",
    "churn": "Monthly Churn Rate",
    "churn rate": "Monthly Churn Rate",
    "taux d'attrition": "Monthly Churn Rate",
    "taux d attrition": "Monthly Churn Rate",
    "active users": "Active Users",
    "utilisateurs actifs": "Active Users",
    "new customers": "New Customers",
    "nouveaux clients": "New Customers",
    "arpu": "ARPU",

    # ESG
    "carbon footprint": "Total Carbon Footprint",
    "total carbon footprint": "Total Carbon Footprint",
    "empreinte carbone": "Total Carbon Footprint",
    "scope 1": "Scope 1 Emissions",
    "émissions scope 1": "Scope 1 Emissions",
    "emissions scope 1": "Scope 1 Emissions",
    "scope 2": "Scope 2 Emissions",
    "émissions scope 2": "Scope 2 Emissions",
    "emissions scope 2": "Scope 2 Emissions",
    "scope 3": "Scope 3 Emissions",
    "émissions scope 3": "Scope 3 Emissions",
    "emissions scope 3": "Scope 3 Emissions",
    "renewable energy": "Renewable Energy Ratio",
    "énergie renouvelable": "Renewable Energy Ratio",
    "energie renouvelable": "Renewable Energy Ratio",
    "water consumption": "Water Consumption",
    "consommation d'eau": "Water Consumption",
    "consommation d eau": "Water Consumption",
    "waste diverted": "Waste Diverted from Landfill",
    "déchets recyclés": "Waste Diverted from Landfill",
    "dechets recycles": "Waste Diverted from Landfill",
}


def _tool_forecast(args: Dict[str, Any]) -> Dict[str, Any]:
    metric = args.get("metric")
    if not metric:
        return {"error": "forecast requires a 'metric' argument"}
    
    norm = str(metric).strip().lower()
    target_metric = METRIC_SYNONYMS.get(norm, metric)
    
    df = _df(metrics=target_metric)
    if df.empty:
        # Try case-insensitive substring match across existing metrics
        all_kpis = _df()
        if not all_kpis.empty and "metric" in all_kpis.columns:
            matches = [m for m in all_kpis["metric"].unique() if norm == m.lower() or norm in m.lower() or m.lower() in norm]
            if matches:
                target_metric = matches[0]
                df = _df(metrics=target_metric)
    
    # Fallback for cloud/infrastructure if still empty
    if df.empty and any(k in norm for k in ["cloud", "infra", "it spend", "server"]):
        target_metric = "Capital Expenditure"
        df = _df(metrics=target_metric)
        
    if df.empty:
        return {"error": f"no data for metric '{metric}'"}

    from src.services.forecasting import ForecastEngine
    fdf = (df[["period", "value"]].rename(columns={"period": "month_tag", "value": "actual"})
           .groupby("month_tag").agg({"actual": "mean"}).reset_index().sort_values("month_tag"))
    res = ForecastEngine().time_series_forecast(fdf, periods=int(args.get("periods", 3)))
    return {"metric": target_metric,
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
