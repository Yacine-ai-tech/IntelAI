"""Decide, without a model call, whether a chat question should also use live web search.

The decision costs microseconds, so the web lookup can start in parallel with internal
retrieval and add no waiting time of its own. Three outcomes:

* ``explicit``  the user asked for a search, or to verify or confirm something online;
* ``auto``      the question is about something outside the organisation's own data
                (a named company or person, current events, prices, definitions of
                external things), so the web is consulted alongside the knowledge base;
* ``skip``      a question about the organisation's own metrics or a pleasantry.

Rules are word lists in English and French; nothing here is specific to one deployment.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional, Sequence

_EXPLICIT = re.compile(
    r"\b(?:web\s*search|search\s+(?:the\s+)?(?:web|internet|net|online)|search\s+online|"
    r"(?:on|from|via|using|use)\s+(?:the\s+)?(?:web|internet|google)|google\s+(?:it|this|that)|"
    r"look\s+(?:it|this|that|them)?\s*up|look\s+online|browse|check\s+online|verify\s+online|"
    r"confirm\s+(?:it\s+)?online|find\s+online|do\s+a\s+(?:web\s+)?search|"
    r"cherche[rz]?\s+(?:sur\s+)?(?:le\s+)?(?:web|internet|en\s+ligne)|"
    r"recherche[rz]?\s+(?:sur\s+)?(?:le\s+)?(?:web|internet|en\s+ligne)|"
    r"v[ée]rifie[rz]?\s+(?:en\s+ligne|sur\s+(?:le\s+)?(?:web|internet))|"
    r"(?:sur|avec)\s+(?:le\s+)?(?:web|internet)|va\s+sur\s+internet|"
    r"fais\s+(?:une\s+)?recherche)\b",
    re.I,
)

_EXTERNAL_WORDS = (
    "latest", "news", "today", "yesterday", "this week", "this year", "currently", "right now",
    "recent", "recently", "current price", "stock", "share price", "market cap", "ceo of",
    "founder", "founded", "headquarter", "who is", "who are", "who owns", "what is",
    "what are", "what does", "tell me about", "information about", "info on", "competitor",
    "competition", "industry", "benchmark", "regulation", "law ", "gdpr", "csrd", "sec filing",
    "inflation", "interest rate", "exchange rate", "weather", "population", "gdp",
    "dernières", "derniers", "actualité", "actualités", "aujourd'hui", "hier", "cette semaine",
    "cette année", "en ce moment", "récent", "cours de bourse", "capitalisation", "qui est",
    "qui sont", "c'est quoi", "qu'est-ce que", "qu'est ce que", "parle-moi de", "parle moi de",
    "informations sur", "concurrent", "secteur", "réglementation", "taux de change",
    "inflation", "benchmark",
)

_COMPANY_SUFFIX = re.compile(r"\b(?:inc|corp|corporation|ltd|llc|plc|gmbh|ag|sa|sas|sarl|co|group|holdings?)\b\.?", re.I)

_INTERNAL_MARKERS = (
    "our ", "my ", "we ", "notre ", "nos ", "mon ", "ma ", "mes ", "nous ", "this quarter",
    "last quarter", "this month", "last month", "ce trimestre", "ce mois", "kpi", "dashboard",
    "tableau de bord", "headcount", "effectif", "turnover", "churn", "ebitda", "mrr", "arr",
    "gross margin", "marge brute", "revenue", "revenu", "chiffre d'affaires", "uptime",
    "emissions", "émissions", "forecast", "prévision", "anomal", "health score", "risk score",
    "on-time delivery", "defect rate", "time to hire", "engagement",
)

_SMALLTALK = re.compile(r"^\s*(?:hi|hello|hey|thanks|thank you|merci|bonjour|salut|ok|okay|cool|great)\b[\s!.?]*$", re.I)

# A capitalised token that is not the first word and not a common sentence word.
_PROPER = re.compile(r"(?<![.!?]\s)(?<!^)\b([A-Z][a-zA-Z0-9&'\-]{2,})\b")
_COMMON_CAPS = {
    "I", "The", "What", "Who", "How", "Why", "When", "Where", "Which", "Can", "Could", "Would",
    "Should", "Do", "Does", "Is", "Are", "Please", "Tell", "Show", "Give", "Compare", "Explain",
    "Summarize", "Quelle", "Quel", "Quels", "Quelles", "Qui", "Comment", "Pourquoi", "Quand",
    "Où", "Est", "Peux", "Pouvez", "Donne", "Montre", "KPI", "KPIs", "CEO", "CFO", "CTO",
    "COO", "CHRO", "ESG", "IT", "HR", "Q1", "Q2", "Q3", "Q4", "EBITDA", "MRR", "ARR",
    "January", "February", "March", "April", "May", "June", "July", "August", "September",
    "October", "November", "December",
}


@dataclass(frozen=True)
class WebPlan:
    mode: str                      # explicit | auto | skip
    reasons: List[str] = field(default_factory=list)
    query: str = ""

    @property
    def enabled(self) -> bool:
        return self.mode in ("explicit", "auto")


def _strip_search_request(text: str) -> str:
    """Remove the 'please search the web for' framing so the search engine gets the topic."""
    t = _EXPLICIT.sub(" ", text)
    t = re.sub(r"\b(?:please|can you|could you|pouvez-vous|peux-tu|s'il (?:te|vous) pla[iî]t|and|et|for|pour|about|sur|on|the|le|la|les)\b",
               " ", t, flags=re.I)
    t = re.sub(r"\s+", " ", t).strip(" ,.?!;:")
    return t


def plan_web(message: str, history: Optional[Sequence[dict]] = None) -> WebPlan:
    text = (message or "").strip()
    if not text or _SMALLTALK.match(text):
        return WebPlan("skip", ["smalltalk"], text)
    low = text.lower()
    reasons: List[str] = []
    query = text

    explicit = bool(_EXPLICIT.search(text))
    if explicit:
        reasons.append("explicit_request")
        stripped = _strip_search_request(text)
        if len(stripped.split()) >= 2:
            query = stripped
        elif history:
            # "search the web" with no topic: use the previous user question as the topic.
            for turn in reversed(list(history)):
                if turn.get("role") == "user" and turn.get("content"):
                    query = str(turn["content"])[:300]
                    break

    external = [w for w in _EXTERNAL_WORDS if w in low]
    if external:
        reasons.append("external_terms")
    proper = [m.group(1) for m in _PROPER.finditer(text) if m.group(1) not in _COMMON_CAPS]
    if proper or _COMPANY_SUFFIX.search(text):
        reasons.append("named_entity")

    internal = [w for w in _INTERNAL_MARKERS if w in low]
    def _follow_up(q: str) -> str:
        # Terse follow-ups ("and their revenue?") need the previous topic to be searchable.
        if len(text.split()) <= 3 and history:
            for turn in reversed(list(history)):
                if turn.get("role") == "user" and turn.get("content"):
                    return f"{str(turn['content'])[:200]} {q}"
        return q

    if explicit:
        return WebPlan("explicit", reasons, query)
    if "named_entity" in reasons and not (internal and not external):
        return WebPlan("auto", reasons, _follow_up(query))
    if external and not internal:
        return WebPlan("auto", reasons, _follow_up(query))
    if external and internal and any(w in low for w in ("industry", "benchmark", "competitor", "concurrent", "secteur", "market", "marché")):
        return WebPlan("auto", reasons, _follow_up(query))
    return WebPlan("skip", reasons or ["internal"], query)
