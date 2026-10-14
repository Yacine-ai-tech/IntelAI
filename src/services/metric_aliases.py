"""Metric-name aliases for retrieval.

KPI series are stored under their reporting names ("Board Diversity Ratio") while the
glossary defines the same measure under a shorter or differently worded term
("Board Diversity %"). A query that uses the reporting name shares few tokens with the
glossary entry, so the glossary term is appended to the query before retrieval. The
original wording is always kept, so exact-name matches against digests and reports are
unaffected.
"""
from __future__ import annotations

import re
import unicodedata
from typing import Dict, List

# normalised reporting name -> glossary terms that define it
METRIC_ALIASES: Dict[str, List[str]] = {
    "annual employee turnover": ["Turnover Rate"],
    "availability": ["System Uptime"],
    "average lead time": ["Avg Lead Time"],
    "board diversity ratio": ["Board Diversity %"],
    "cac payback period": ["CAC Payback"],
    "capital expenditure": ["Free Cash Flow"],
    "carbon intensity per revenue": ["Emissions Intensity"],
    "carrying cost of inventory": ["Carrying Cost"],
    "cash balance": ["Cash Runway"],
    "churned customers": ["Churn Rate"],
    "monthly churn rate": ["Churn Rate"],
    "critical vulnerabilities": ["Security Score", "Security Incidents"],
    "customers": ["Customer Count"],
    "new customers": ["Customer Count"],
    "cycle time efficiency": ["Cycle Time"],
    "order fulfillment cycle time": ["Cycle Time"],
    "downtime hours": ["Unplanned Downtime"],
    "mean time between failures": ["Unplanned Downtime"],
    "ebitda margin": ["EBITDA"],
    "employee net promoter score": ["Net Promoter Score", "Engagement Score"],
    "gross profit": ["Gross Margin"],
    "ltv to cac ratio": ["LTV:CAC"],
    "net income": ["Net Profit"],
    "net profit margin": ["Net Profit"],
    "offers accepted": ["Offer Acceptance Rate"],
    "operating expenses": ["Operating Costs"],
    "overall equipment effectiveness": ["Production Efficiency"],
    "privacy incident count": ["Security Incidents"],
    "renewable energy ratio": ["Renewable Energy %"],
    "safety incidents": ["Safety Incident Rate"],
    "supplier defect rate": ["Defect Rate"],
    "total carbon footprint": ["Carbon Emissions (tCO2)"],
    "total incidents": ["Critical Incidents"],
    "training hours per employee": ["Training Hours"],
    "waste diverted from landfill": ["Waste Recycled %"],
    "water consumption": ["Water Consumption (m3)"],
    "yoy revenue growth": ["Revenue"],
}

_NORM = re.compile(r"[^a-z0-9]+")


def _norm(text: str) -> str:
    """Lower-case, accent-free, punctuation-free form used to match phrases."""
    plain = unicodedata.normalize("NFKD", (text or "").lower())
    plain = "".join(c for c in plain if not unicodedata.combining(c))
    return _NORM.sub(" ", plain).strip()


# French wording for the same measures. Reporting names and digests use English metric names,
# so a French question gains the English term (and the glossary term) alongside its own words.
FRENCH_ALIASES: Dict[str, List[str]] = {
    "chiffre d'affaires": ["Revenue"],
    "chiffre d affaires": ["Revenue"],
    "revenus": ["Revenue"],
    "marge brute": ["Gross Margin", "Gross Profit"],
    "marge nette": ["Net Profit Margin", "Net Profit"],
    "benefice net": ["Net Profit", "Net Income"],
    "resultat net": ["Net Income", "Net Profit"],
    "tresorerie": ["Cash Balance", "Cash Runway"],
    "flux de tresorerie": ["Operating Cash Flow", "Free Cash Flow"],
    "charges d'exploitation": ["Operating Expenses", "Operating Costs"],
    "depenses d'exploitation": ["Operating Expenses", "Operating Costs"],
    "taux de desabonnement": ["Churn Rate", "Monthly Churn Rate"],
    "taux d'attrition": ["Churn Rate", "Annual Employee Turnover"],
    "taux de rotation": ["Turnover Rate", "Annual Employee Turnover"],
    "effectif": ["Headcount"],
    "effectifs": ["Headcount"],
    "cout d'acquisition": ["CAC"],
    "valeur vie client": ["LTV"],
    "taux d'engagement": ["Engagement Score"],
    "disponibilite": ["Availability", "System Uptime"],
    "temps d'arret": ["Downtime Hours", "Unplanned Downtime"],
    "incidents de securite": ["Security Incidents"],
    "delai moyen d'approvisionnement": ["Average Lead Time", "Avg Lead Time"],
    "rotation des stocks": ["Inventory Turnover"],
    "taux de service": ["Fill Rate"],
    "emissions de carbone": ["Total Carbon Footprint", "Carbon Emissions (tCO2)"],
    "intensite carbone": ["Carbon Intensity per Revenue", "Emissions Intensity"],
    "energie renouvelable": ["Renewable Energy Ratio", "Renewable Energy %"],
    "diversite du conseil": ["Board Diversity Ratio", "Board Diversity %"],
    "conformite des audits": ["Audit Compliance Score"],
    "score de conformite": ["Audit Compliance Score"],
    "latence api": ["API P99 Latency"],
    "heures de formation": ["Training Hours per Employee", "Training Hours"],
    "taux d'absenteisme": ["Absenteeism Rate"],
    "cout par embauche": ["Cost per Hire"],
    "dette": ["Total Debt"],
    "fonds propres": ["Shareholders Equity"],
}
for _fr_key, _terms in FRENCH_ALIASES.items():
    METRIC_ALIASES.setdefault(_fr_key, _terms)
METRIC_ALIASES = {_norm(k): v for k, v in METRIC_ALIASES.items()}

_PATTERNS = sorted(
    ((re.compile(rf"(?<![a-z0-9]){re.escape(k)}(?![a-z0-9])"), terms) for k, terms in METRIC_ALIASES.items()),
    key=lambda item: -len(item[0].pattern),
)


def expand_query(query: str) -> str:
    """Append the glossary terms for any reporting-name metric mentioned in the query."""
    text = _norm(query)
    extra: List[str] = []
    for pattern, terms in _PATTERNS:
        if pattern.search(text):
            for term in terms:
                if term not in extra and term.lower() not in query.lower():
                    extra.append(term)
    return f"{query} ({'; '.join(extra)})" if extra else query
