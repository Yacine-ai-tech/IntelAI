"""
Unified chart library — Plotly visualisations for the OmniIntelOS.
Merges base charts + advanced charts into one module.
"""
from __future__ import annotations

from typing import Dict, List

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.core.i18n import I18N

# ── Palette ───────────────────────────────────────────────────────────────

COLORS = {
    "primary": "#2563EB",
    "secondary": "#14B8A6",
    "warning": "#F59E0B",
    "danger": "#EF4444",
    "muted": "#64748B",
    "actual": "#2E86AB",
    "plan": "#A23B72",
    "forecast": "#F18F01",
    "prediction": "#06D6A0",
    "positive": "#28A745",
    "negative": "#DC3545",
    "neutral": "#6C757D",
    "best_case": "#28A745",
    "worst_case": "#DC3545",
    "base_case": "#2E86AB",
}

_GRID = "rgba(148,163,184,0.3)"


def _lbl(en: str, fr: str) -> str:
    return fr if I18N.lang() == "fr" else en


# ── Base charts ───────────────────────────────────────────────────────────

def create_kpi_trend_chart(df: pd.DataFrame, metric_label: str, forecast_df: pd.DataFrame | None = None) -> go.Figure:
    fig = go.Figure()
    if not df.empty:
        fig.add_trace(go.Scatter(x=df["period"], y=df["value"], mode="lines+markers", name=metric_label, line=dict(color=COLORS["primary"], width=3)))
    if forecast_df is not None and not forecast_df.empty:
        fig.add_trace(go.Scatter(x=forecast_df["month_tag"], y=forecast_df["forecast"], mode="lines+markers", name=_lbl("Forecast", "Prévision"), line=dict(color=COLORS["secondary"], dash="dash")))
        fig.add_trace(go.Scatter(x=forecast_df["month_tag"], y=forecast_df["upper_bound"], mode="lines", line=dict(color=COLORS["secondary"], width=0), showlegend=False))
        fig.add_trace(go.Scatter(x=forecast_df["month_tag"], y=forecast_df["lower_bound"], mode="lines", fill="tonexty", fillcolor="rgba(20,184,166,0.2)", line=dict(color=COLORS["secondary"], width=0), showlegend=False))
    fig.update_layout(title=f"{metric_label} — {_lbl('Trend', 'Tendance')}", xaxis_title=_lbl("Period", "Période"), yaxis_title=_lbl("Value", "Valeur"), height=420, plot_bgcolor="white", hovermode="x unified")
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor=_GRID)
    return fig


def create_category_breakdown_chart(category_summary: pd.DataFrame) -> go.Figure:
    fig = go.Figure(data=[go.Bar(x=category_summary["category"], y=category_summary["value"], marker_color=COLORS["primary"])])
    fig.update_layout(title=_lbl("Category Contribution", "Contribution par catégorie"), xaxis_title=_lbl("Category", "Catégorie"), yaxis_title=_lbl("Value", "Valeur"), height=380, plot_bgcolor="white")
    fig.update_yaxes(showgrid=True, gridcolor=_GRID)
    return fig


def create_risk_radar_chart(risk: dict) -> go.Figure:
    cats = [_lbl("Volatility", "Volatilité"), _lbl("Anomalies", "Anomalies"), _lbl("Concentration", "Concentration"), _lbl("Liquidity", "Liquidité"), _lbl("Execution", "Exécution")]
    vals = [risk.get("volatility_score", 0), risk.get("anomaly_score", 0), risk.get("concentration_score", 0), risk.get("liquidity_score", 0), risk.get("execution_score", 0)]
    fig = go.Figure(data=[go.Scatterpolar(r=vals, theta=cats, fill="toself", line_color=COLORS["danger"])])
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False, height=400, title=_lbl("Risk Radar", "Radar de risque"))
    return fig


def create_health_gauge(health: dict) -> go.Figure:
    score = health.get("score", 0)
    fig = go.Figure(go.Indicator(mode="gauge+number", value=score, title={"text": f"{_lbl('Health Index', 'Indice de santé')} — {health.get('label', '')}"}, gauge={"axis": {"range": [0, 100]}, "bar": {"color": COLORS["primary"]}, "steps": [{"range": [0, 50], "color": "rgba(239,68,68,0.25)"}, {"range": [50, 75], "color": "rgba(245,158,11,0.25)"}, {"range": [75, 100], "color": "rgba(20,184,166,0.25)"}]}))
    fig.update_layout(height=360)
    return fig


# ── Advanced charts ───────────────────────────────────────────────────────

def create_forecast_chart(historical_df: pd.DataFrame, forecast_df: pd.DataFrame, title: str | None = None) -> go.Figure:
    if not title:
        title = _lbl("AI-Powered Forecast with Confidence Intervals", "Prévision IA avec intervalles de confiance")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=historical_df["month_tag"], y=historical_df["actual"], mode="lines+markers", name=_lbl("Historical", "Historique"), line=dict(color=COLORS["actual"], width=3), marker=dict(size=8)))
    fig.add_trace(go.Scatter(x=forecast_df["month_tag"], y=forecast_df["forecast"], mode="lines+markers", name=_lbl("Forecast", "Prévision"), line=dict(color=COLORS["prediction"], width=3, dash="dash"), marker=dict(size=8, symbol="diamond")))
    fig.add_trace(go.Scatter(x=forecast_df["month_tag"], y=forecast_df["upper_bound"], mode="lines", line=dict(color=COLORS["prediction"], width=0), showlegend=False, hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=forecast_df["month_tag"], y=forecast_df["lower_bound"], mode="lines", line=dict(color=COLORS["prediction"], width=0), fillcolor="rgba(6,214,160,0.2)", fill="tonexty", hoverinfo="skip", name=_lbl("Confidence Interval", "Intervalle de confiance")))
    fig.update_layout(title=title, xaxis_title=_lbl("Month", "Mois"), yaxis_title=_lbl("Value ($)", "Valeur ($)"), height=500, hovermode="x unified", plot_bgcolor="white")
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="LightGray")
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="LightGray")
    return fig


def create_scenario_chart(scenarios: Dict[str, float], title: str | None = None) -> go.Figure:
    if not title:
        title = _lbl("Scenario Analysis", "Analyse de scénarios")
    names = list(scenarios.keys())
    vals = list(scenarios.values())
    colors = []
    for n in names:
        nl = n.lower()
        if "best" in nl or "optimistic" in nl or "meilleur" in nl:
            colors.append(COLORS["best_case"])
        elif "worst" in nl or "pessimistic" in nl or "pire" in nl:
            colors.append(COLORS["worst_case"])
        else:
            colors.append(COLORS["base_case"])
    fig = go.Figure(data=[go.Bar(x=names, y=vals, marker_color=colors, text=[f"${v:,.0f}" for v in vals], textposition="outside")])
    fig.update_layout(title=title, xaxis_title=_lbl("Scenario", "Scénario"), yaxis_title=_lbl("Value ($)", "Valeur ($)"), height=450, plot_bgcolor="white", showlegend=False)
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="LightGray")
    return fig


def create_sensitivity_chart(sensitivity_df: pd.DataFrame, title: str | None = None) -> go.Figure:
    if not title:
        title = _lbl("Sensitivity Analysis", "Analyse de sensibilité")
    fig = go.Figure()
    for driver in sensitivity_df["driver"].unique():
        dd = sensitivity_df[sensitivity_df["driver"] == driver].sort_values("change_pct")
        fig.add_trace(go.Scatter(x=dd["new_value"], y=dd["change_pct"], mode="lines+markers", name=driver, line=dict(width=3), marker=dict(size=10)))
    base = sensitivity_df["base_value"].iloc[0]
    fig.add_vline(x=base, line_dash="dash", line_color="gray", annotation_text=_lbl("Base Case", "Cas de base"))
    fig.update_layout(title=title, xaxis_title=_lbl("Outcome Value ($)", "Valeur résultante ($)"), yaxis_title=_lbl("Driver Change (%)", "Variation du levier (%)"), height=500, hovermode="closest", plot_bgcolor="white")
    return fig


def create_anomaly_chart(df: pd.DataFrame, title: str | None = None) -> go.Figure:
    if not title:
        title = _lbl("Anomaly Detection", "Détection d'anomalies")
    fig = go.Figure()
    normal = df[~df["is_anomaly"]]
    fig.add_trace(go.Scatter(x=normal["month_tag"], y=normal["actual"], mode="lines+markers", name=_lbl("Normal", "Normal"), line=dict(color=COLORS["actual"], width=2), marker=dict(size=8)))
    anom = df[df["is_anomaly"]]
    if not anom.empty:
        fig.add_trace(go.Scatter(x=anom["month_tag"], y=anom["actual"], mode="markers", name=_lbl("Anomaly", "Anomalie"), marker=dict(size=15, color=COLORS["negative"], symbol="x", line=dict(width=2, color="DarkRed"))))
    fig.update_layout(title=title, xaxis_title=_lbl("Month", "Mois"), yaxis_title=_lbl("Value ($)", "Valeur ($)"), height=450, hovermode="closest", plot_bgcolor="white")
    return fig


def create_monte_carlo_chart(simulation_results: Dict, title: str | None = None) -> go.Figure:
    if not title:
        title = _lbl("Monte Carlo Simulation — Risk Distribution", "Simulation Monte Carlo — Distribution du risque")
    fig = make_subplots(rows=1, cols=2, subplot_titles=[_lbl("Price Path Scenarios", "Scénarios de trajectoire"), _lbl("Final Value Distribution", "Distribution finale")])
    paths = simulation_results["paths"]
    periods = paths.shape[1]
    x_axis = list(range(periods))
    for i in range(min(50, len(paths))):
        fig.add_trace(go.Scatter(x=x_axis, y=paths[i], mode="lines", line=dict(width=1, color="rgba(46,134,171,0.3)"), showlegend=False, hoverinfo="skip"), row=1, col=1)
    final = paths[:, -1]
    fig.add_trace(go.Histogram(x=final, nbinsx=50, marker_color=COLORS["actual"], showlegend=False), row=1, col=2)
    for pct, name in [(5, "P5"), (50, "Median"), (95, "P95")]:
        v = np.percentile(final, pct)
        fig.add_vline(x=v, line_dash="dash", annotation_text=f"{name}: ${v:,.0f}", row=1, col=2)
    fig.update_layout(title_text=title, height=450, showlegend=False, plot_bgcolor="white")
    return fig


def create_cash_runway_chart(runway_data: Dict, title: str | None = None) -> go.Figure:
    if not title:
        title = _lbl("Cash Runway Projection", "Projection de trésorerie")
    months = int(min(runway_data["runway_months"], 24))
    cash = runway_data["current_cash"]
    burn = runway_data["net_burn"]
    mr = list(range(months + 1))
    balance = [cash - burn * m for m in mr]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=mr, y=balance, mode="lines+markers", name=_lbl("Projected Cash", "Trésorerie projetée"), line=dict(color=COLORS["actual"], width=3), fill="tozeroy", fillcolor="rgba(46,134,171,0.2)"))
    if months >= 3:
        fig.add_vrect(x0=months - 3, x1=months, fillcolor="red", opacity=0.1, layer="below", line_width=0, annotation_text=_lbl("Danger Zone", "Zone de danger"))
    if months >= 6:
        fig.add_vrect(x0=months - 6, x1=months - 3, fillcolor="orange", opacity=0.1, layer="below", line_width=0, annotation_text=_lbl("Warning", "Attention"))
    fig.update_layout(title=title, xaxis_title=_lbl("Months from Now", "Mois à partir de maintenant"), yaxis_title=_lbl("Cash Balance ($)", "Solde ($)"), height=450, hovermode="x unified", plot_bgcolor="white")
    return fig


def create_health_score_gauge(score: float, rating: str, title: str | None = None) -> go.Figure:
    if not title:
        title = _lbl("Financial Health Score", "Score de santé financière")
    fig = go.Figure(go.Indicator(mode="gauge+number+delta", value=score, title={"text": title, "font": {"size": 24}}, delta={"reference": 75, "increasing": {"color": COLORS["positive"]}}, gauge={"axis": {"range": [None, 100]}, "bar": {"color": "darkblue"}, "steps": [{"range": [0, 60], "color": "rgba(220,53,69,0.3)"}, {"range": [60, 75], "color": "rgba(255,193,7,0.3)"}, {"range": [75, 90], "color": "rgba(40,167,69,0.3)"}, {"range": [90, 100], "color": "rgba(40,167,69,0.5)"}], "threshold": {"line": {"color": "red", "width": 4}, "thickness": 0.75, "value": 75}}))
    fig.add_annotation(text=f"<b>{rating}</b>", x=0.5, y=0.3, font=dict(size=20, color="darkblue"), showarrow=False)
    fig.update_layout(height=400, margin=dict(l=20, r=20, t=80, b=20))
    return fig


def create_executive_summary_chart(metrics: Dict[str, float], title: str | None = None) -> go.Figure:
    if not title:
        title = _lbl("Executive Summary — Key Metrics", "Résumé exécutif — Indicateurs clés")
    fig = make_subplots(rows=2, cols=2, subplot_titles=[_lbl("Revenue", "Revenu"), _lbl("Profit Margin %", "Marge bénéficiaire %"), _lbl("Cash Position", "Position de trésorerie"), _lbl("Plan Accuracy", "Précision du plan")], specs=[[{"type": "indicator"}, {"type": "indicator"}], [{"type": "indicator"}, {"type": "indicator"}]])
    fig.add_trace(go.Indicator(mode="number+delta", value=metrics.get("revenue", 0), number={"prefix": "$", "valueformat": ",.0f"}, delta={"reference": metrics.get("revenue_target", 0), "relative": True, "valueformat": ".1%"}), row=1, col=1)
    fig.add_trace(go.Indicator(mode="number+gauge", value=metrics.get("profit_margin_pct", 0), number={"suffix": "%"}, gauge={"axis": {"range": [None, 50]}, "bar": {"color": "darkblue"}}), row=1, col=2)
    fig.add_trace(go.Indicator(mode="number+delta", value=metrics.get("cash_balance", 0), number={"prefix": "$", "valueformat": ",.0f"}, delta={"reference": metrics.get("min_cash_required", 0)}), row=2, col=1)
    fig.add_trace(go.Indicator(mode="number+gauge", value=100 - abs(metrics.get("variance_vs_plan_pct", 0)), number={"suffix": "%"}, gauge={"axis": {"range": [None, 100]}, "bar": {"color": "green"}, "threshold": {"line": {"color": "red", "width": 4}, "thickness": 0.75, "value": 90}}), row=2, col=2)
    fig.update_layout(title_text=title, height=500, showlegend=False)
    return fig


def create_rolling_forecast_chart(df: pd.DataFrame, title: str | None = None) -> go.Figure:
    if not title:
        title = _lbl("Rolling Forecast View", "Vue glissante des prévisions")
    fig = go.Figure()
    for typ, name, color, dash in [("actual", _lbl("Actual", "Réel"), COLORS["actual"], "solid"), ("forecast", _lbl("Forecast", "Prévision"), COLORS["forecast"], "dash"), ("plan", _lbl("Plan", "Plan"), COLORS["plan"], "dot")]:
        sub = df[df["type"] == typ]
        fig.add_trace(go.Scatter(x=sub["period"], y=sub["value"], mode="lines+markers", name=name, line=dict(color=color, width=3, dash=dash)))
    fig.update_layout(title=title, xaxis_title=_lbl("Period", "Période"), yaxis_title=_lbl("Value ($)", "Valeur ($)"), height=500, hovermode="x unified", plot_bgcolor="white")
    return fig


def create_driver_heatmap(df: pd.DataFrame, title: str | None = None) -> go.Figure:
    if not title:
        title = _lbl("Performance Heatmap by Market & Driver", "Carte de chaleur par marché et levier")
    hm = df.pivot(index="market", columns="driver", values="variance_pct")
    fig = go.Figure(data=go.Heatmap(z=hm.values, x=hm.columns, y=hm.index, colorscale=[[0, "rgb(220,53,69)"], [0.5, "rgb(255,255,255)"], [1, "rgb(40,167,69)"]], zmid=0, text=hm.values, texttemplate="%{text:.1f}%", colorbar=dict(title=_lbl("Variance %", "Écart %"))))
    fig.update_layout(title=title, xaxis_title=_lbl("Driver", "Levier"), yaxis_title=_lbl("Market", "Marché"), height=500, plot_bgcolor="white")
    return fig
