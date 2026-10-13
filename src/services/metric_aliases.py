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
    return _NORM.sub(" ", (text or "").lower()).strip()


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
