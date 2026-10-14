"""Language detection for user messages and queries (English / French).

The embedding and reranking models are multilingual, so retrieval works across languages;
the detected language is used to prefer same-language documents and to set the reply
language, not to restrict what can be found.
"""
from __future__ import annotations

import re

_FR_ACCENTS = "àâçéèêëîïôûùüœ"

_FR_WORDS = {
    "le", "la", "les", "des", "du", "de", "un", "une", "et", "est", "sont", "était", "etait",
    "été", "au", "aux", "ce", "cette", "ces", "qui", "que", "quoi", "quel", "quelle", "quels",
    "quelles", "pourquoi", "comment", "combien", "où", "ou", "nos", "notre", "votre", "vos",
    "pour", "avec", "sur", "dans", "par", "sans", "chez", "entre", "depuis", "donnez",
    "donne", "montre", "montrez", "affiche", "liste", "valeur", "chiffre", "résumé",
    "resume", "prévision", "prevision", "bonjour", "merci", "salut", "s'il", "svp",
    "mois", "année", "annee", "trimestre", "semaine", "enregistré", "enregistre", "au",
    "d'une", "d'un", "l'", "qu'", "n'est", "c'est", "j'ai", "il", "elle", "nous", "vous",
}

_EN_WORDS = {
    "the", "is", "are", "was", "were", "what", "why", "how", "our", "show", "give", "which",
    "and", "for", "with", "hello", "hi", "please", "summary", "summarize", "forecast",
    "should", "can", "could", "of", "to", "in", "on", "by", "from", "value", "recorded",
    "report", "provide", "month", "year", "quarter", "week", "tell", "list", "does", "did",
}

_TOKEN = re.compile(r"[a-zàâçéèêëîïôûùüœ']+", re.IGNORECASE)


def detect_language(text: str, default: str = "en") -> str:
    """Return "fr" or "en" for a message. Accented characters and French function words
    weigh toward French; ties fall back to ``default``."""
    t = (text or "").lower().strip()
    if not t:
        return default if default in ("fr", "en") else "en"
    tokens = _TOKEN.findall(t)
    fr = sum(1 for w in tokens if w in _FR_WORDS)
    en = sum(1 for w in tokens if w in _EN_WORDS)
    fr += 2 * sum(1 for c in t if c in _FR_ACCENTS)
    # elisions such as l'équipe, d'une, qu'est
    fr += len(re.findall(r"\b(?:l|d|qu|n|j|c|s)'", t))
    if fr > en:
        return "fr"
    if en > fr:
        return "en"
    return default if default in ("fr", "en") else "en"
