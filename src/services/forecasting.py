"""
AI forecasting — time-series, Monte-Carlo, cash runway, health scoring.
CPU-friendly: uses scikit-learn LinearRegression (no GPU needed).
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LinearRegression

from src.core.i18n import I18N
from src.core.logger import get_logger

log = get_logger(__name__)


def _fit_linear(y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """OLS on the whole series. In-sample fit + a forecast(h)->array closure."""
    X = np.arange(len(y)).reshape(-1, 1)
    model = LinearRegression().fit(X, y)
    fitted = model.predict(X)

    def forecast(h: int) -> np.ndarray:
        future_idx = np.arange(len(y), len(y) + h).reshape(-1, 1)
        return model.predict(future_idx)

    return fitted, forecast


def _fit_holt_linear(y: np.ndarray, alpha: float = 0.5, beta: float = 0.35) -> Tuple[np.ndarray, np.ndarray]:
    """Holt's linear (double exponential smoothing) trend method. Unlike OLS over the
    whole series, the level/trend state is updated recursively with recency weighting,
    so it tracks a recent acceleration in growth rate instead of averaging it away
    against months of slower-growth history."""
    level = float(y[0])
    trend = float(y[1] - y[0]) if len(y) > 1 else 0.0
    fitted = [level]
    for t in range(1, len(y)):
        last_level = level
        level = alpha * float(y[t]) + (1 - alpha) * (level + trend)
        trend = beta * (level - last_level) + (1 - beta) * trend
        fitted.append(level)
    fitted = np.array(fitted)
    final_level, final_trend = level, trend

    def forecast(h: int) -> np.ndarray:
        return np.array([final_level + (i + 1) * final_trend for i in range(h)])

    return fitted, forecast


def _fit_quadratic(y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Degree-2 polynomial trend — captures curvature (d^2y/dt^2 != 0) directly, which a
    linear fit structurally cannot. Only useful with enough points to constrain 3
    coefficients without overfitting; callers should prefer this only when validated."""
    x = np.arange(len(y))
    coeffs = np.polyfit(x, y, deg=2)
    poly = np.poly1d(coeffs)
    fitted = poly(x)

    def forecast(h: int) -> np.ndarray:
        return poly(np.arange(len(y), len(y) + h))

    return fitted, forecast


_CANDIDATES = {
    "linear": _fit_linear,
    "holt_linear": _fit_holt_linear,
    "quadratic": _fit_quadratic,
}


def _select_model(y: np.ndarray, holdout: int = 3):
    """Auto-select the candidate model with the lowest backtested APE on the last
    `holdout` points of THIS series alone (no peeking at the actual forecast target) —
    fit on y[:-holdout], predict holdout steps, score against the real y[-holdout:].
    Falls back to linear when there isn't enough history to hold anything out."""
    if len(y) < holdout + 3:
        return "linear", _CANDIDATES["linear"]

    train, truth = y[:-holdout], y[-holdout:]
    best_name, best_err = "linear", float("inf")
    for name, fit_fn in _CANDIDATES.items():
        if name == "quadratic" and len(train) < 5:
            continue  # degree-2 fit needs enough points to not just overfit noise
        try:
            _, forecast_fn = fit_fn(train)
            pred = forecast_fn(holdout)
            ape = np.mean(np.abs((truth - pred) / np.where(truth == 0, 1, truth)))
        except Exception:
            continue
        if ape < best_err:
            best_err, best_name = ape, name
    return best_name, _CANDIDATES[best_name]


class ForecastEngine:
    """Time-series forecasts with confidence intervals. Auto-selects between OLS,
    Holt's linear trend, and a quadratic trend per call, based on which one backtests
    best on that series' own recent history — replaces a single always-linear OLS fit,
    which systematically under-forecasts during compounding growth acceleration
    (see BENCHMARK.md §1)."""

    def time_series_forecast(
        self,
        df: pd.DataFrame,
        periods: int = 3,
        confidence_level: float = 0.95,
    ) -> pd.DataFrame:
        if df.empty or len(df) < 2:
            return pd.DataFrame()

        df = df.sort_values("month_tag").copy()
        df["time_index"] = range(len(df))
        y = df["actual"].values.astype(float)

        _, chosen_fit = _select_model(y)
        fitted, forecast_fn = chosen_fit(y)
        residual_std = np.std(y - fitted)
        future_preds = forecast_fn(periods)

        z = stats.norm.ppf((1 + confidence_level) / 2)
        # Widening margin with forecast horizon (same shape as the old OLS prediction
        # interval) — a fixed per-point residual_std alone understates uncertainty
        # further out regardless of which point-forecast model produced the mean.
        horizon = np.arange(1, periods + 1)
        margin = z * residual_std * np.sqrt(1 + horizon / max(1, len(y)))

        last_month = datetime.strptime(df["month_tag"].iloc[-1], "%Y-%m")
        # Calendar-month arithmetic, not a fixed 30-day step — the old `timedelta(days=30*i)`
        # drifts (e.g. +60 days from June 1 lands July 31, not Aug 1), producing duplicate or
        # skipped month labels for periods spanning 31-day months.
        future_months = [
            (pd.Timestamp(last_month) + pd.DateOffset(months=i)).strftime("%Y-%m")
            for i in range(1, periods + 1)
        ]

        forecast_df = pd.DataFrame({
            "month_tag": future_months,
            "forecast": future_preds,
            "lower_bound": future_preds - margin,
            "upper_bound": future_preds + margin,
            "confidence_level": confidence_level,
        })

        return forecast_df

    def explain_forecast(self, df: pd.DataFrame) -> Dict[str, float]:
        if df.empty or len(df) < 2:
            return {"r_squared": 0.0, "slope": 0.0, "intercept": 0.0}
        df = df.sort_values("month_tag").copy()
        df["time_index"] = range(len(df))
        X, y = df[["time_index"]].values, df["actual"].values
        model = LinearRegression().fit(X, y)
        return {"r_squared": model.score(X, y), "slope": model.coef_[0], "intercept": model.intercept_}


class ScenarioEngine:
    """Monte-Carlo simulation for scenario planning with advanced models."""

    def monte_carlo_simulation(
        self,
        base_value: float,
        growth_rate: float,
        std_dev: float,
        iterations: int = 1000,
        periods: int = 12,
        correlation: float = 0.3,
    ) -> Dict[str, Any]:
        """
        Advanced Monte-Carlo with correlation, shocks, and confidence bands.
        - Correlated random walk (not independent periods)
        - Jump diffusion (sudden 20% moves at 10% probability)
        - Multiple confidence levels (10th, 50th, 90th percentile)
        """
        results = np.zeros((iterations, periods))
        shocks = np.random.normal(0, 1, (iterations, periods))
        
        for i in range(iterations):
            value = base_value
            for t in range(periods):
                # Correlated random walk
                if t > 0:
                    prev_shock = shocks[i, t-1]
                    current_shock = correlation * prev_shock + np.sqrt(1 - correlation**2) * shocks[i, t]
                else:
                    current_shock = shocks[i, t]
                
                # Growth with stochastic component
                drift = growth_rate / 12  # Monthly drift
                volatility = std_dev / np.sqrt(12)  # Monthly volatility
                
                # Occasional large shocks (10% probability of 20% move)
                if np.random.random() < 0.1:
                    current_shock *= 2
                
                value = value * (1 + drift + volatility * current_shock)
                results[i, t] = max(0, value)  # Prevent negative values
        
        mean_path = np.mean(results, axis=0)
        p10_path = np.percentile(results, 10, axis=0)
        p50_path = np.percentile(results, 50, axis=0)
        p90_path = np.percentile(results, 90, axis=0)
        
        worst_case = np.min(results[:, -1])
        best_case = np.max(results[:, -1])
        probability_positive = np.mean(results[:, -1] > base_value) * 100
        
        return {
            "mean_path": mean_path.tolist(),
            "p10_path": p10_path.tolist(),
            "p50_path": p50_path.tolist(),
            "p90_path": p90_path.tolist(),
            "worst_case": float(worst_case),
            "best_case": float(best_case),
            "probability_positive": float(probability_positive),
            "iterations": iterations,
            "periods": periods,
        }

    def simulate_business_event(
        self,
        current_data: pd.DataFrame,
        event_impact: float,
        category: str,
        recovery_months: int = 6,
    ) -> pd.DataFrame:
        """
        Simulate impact of business event (market downturn, product launch, etc).
        - Applies shock at midpoint
        - Recovers gradually over recovery_months
        """
        data = current_data.sort_values("period").copy() if "period" in current_data.columns else current_data.copy()
        data["scenario_value"] = data.get("value", data.get("actual", 1))
        
        shock_point = len(data) // 2
        for idx in range(shock_point, len(data)):
            months_since_shock = idx - shock_point
            if months_since_shock == 0:
                # Apply initial shock
                data.iloc[idx, data.columns.get_loc("scenario_value")] *= (1 + event_impact)
            else:
                # Recover gradually (exponential recovery)
                recovery_factor = 1 - (event_impact * np.exp(-months_since_shock / recovery_months))
                data.iloc[idx, data.columns.get_loc("scenario_value")] *= recovery_factor
        
        return data

    def sensitivity_analysis(
        self,
        base_forecast: pd.DataFrame,
        variables: Dict[str, Tuple[float, float]],
    ) -> Dict[str, Any]:
        """
        Sensitivity analysis: which variables drive forecast most?
        Tests ±10% change in each variable and measures impact.
        """
        sensitivity = {}
        base_value = base_forecast["forecast"].iloc[-1] if not base_forecast.empty else 1
        
        for var, (min_val, max_val) in variables.items():
            mid = (min_val + max_val) / 2
            change_pct = 0.1  # Test ±10% change
            
            impact_up = (mid * (1 + change_pct) - base_value) / base_value * 100
            impact_down = (mid * (1 - change_pct) - base_value) / base_value * 100
            
            sensitivity[var] = {
                "impact_up_pct": float(impact_up),
                "impact_down_pct": float(impact_down),
                "elasticity": float((impact_up - impact_down) / 20),  # % output change / % input change
            }
        
        return sensitivity


# ── Standalone helpers ────────────────────────────────────────────────────

def calculate_cash_runway(
    current_cash: float,
    monthly_burn: float,
    monthly_revenue: float = 0,
) -> Dict[str, Any]:
    net_burn = monthly_burn - monthly_revenue
    if net_burn <= 0:
        runway_months = float("inf")
        runway_date = None
    else:
        runway_months = current_cash / net_burn
        runway_date = datetime.now() + timedelta(days=30 * runway_months)

    fr = I18N.lang() == "fr"
    return {
        "current_cash": current_cash,
        "monthly_burn": monthly_burn,
        "monthly_revenue": monthly_revenue,
        "net_burn": net_burn,
        "runway_months": runway_months,
        "runway_date": runway_date.strftime("%Y-%m-%d") if runway_date else ("Indéfini" if fr else "Indefinite"),
        "is_healthy": runway_months > 12 or runway_months == float("inf"),
    }


def calculate_financial_health_score(metrics: Dict[str, float]) -> Dict[str, Any]:
    score = 0
    max_score = 0
    details: Dict[str, int] = {}

    def _score_bucket(value: float, thresholds: List[tuple]) -> int:
        for threshold, pts in thresholds:
            if value >= threshold:
                return pts
        return thresholds[-1][1]

    if "revenue_growth_pct" in metrics:
        pts = _score_bucket(metrics["revenue_growth_pct"], [(20, 25), (10, 20), (0, 15)])
        if metrics["revenue_growth_pct"] < 0:
            pts = max(0, int(15 + metrics["revenue_growth_pct"]))
        score += pts
        max_score += 25
        details["revenue_growth"] = pts

    if "profit_margin_pct" in metrics:
        pts = _score_bucket(metrics["profit_margin_pct"], [(20, 25), (10, 20), (0, 15)])
        if metrics["profit_margin_pct"] < 0:
            pts = max(0, int(15 + metrics["profit_margin_pct"]))
        score += pts
        max_score += 25
        details["profitability"] = pts

    if "cash_runway_months" in metrics:
        pts = _score_bucket(metrics["cash_runway_months"], [(18, 25), (12, 20), (6, 15), (3, 10)])
        score += pts
        max_score += 25
        details["cash_position"] = pts

    if "variance_vs_plan_pct" in metrics:
        var = abs(metrics["variance_vs_plan_pct"])
        pts = _score_bucket(-var, [(-5, 25), (-10, 20), (-15, 15), (-25, 10)])
        score += pts
        max_score += 25
        details["operational_efficiency"] = pts

    final = (score / max_score * 100) if max_score else 0

    fr = I18N.lang() == "fr"
    if final >= 90:
        rating, color = ("Excellent", "🟢")
    elif final >= 75:
        rating, color = ("Bon" if fr else "Good", "🟡")
    elif final >= 60:
        rating, color = ("Passable" if fr else "Fair", "🟠")
    else:
        rating, color = ("Faible" if fr else "Poor", "🔴")

    return {"score": final, "rating": rating, "color": color, "details": details, "max_score": max_score}
