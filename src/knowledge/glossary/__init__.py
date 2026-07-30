"""
Authoritative Enterprise Metric & Methodology Glossary Package.

Provides English and French metric definitions, GAAP/IFRS standards, formulas,
benchmarks, and domain mappings for anti-hallucination copilot grounding.
"""
from src.knowledge.glossary.en import (
    GLOSSARY as GLOSSARY_EN,
    get_term as get_term_en,
    for_domain as for_domain_en,
    as_knowledge_docs as as_knowledge_docs_en,
)
from src.knowledge.glossary.fr import (
    GLOSSARY as GLOSSARY_FR,
    get_term as get_term_fr,
    for_domain as for_domain_fr,
    as_knowledge_docs as as_knowledge_docs_fr,
)

# Default aliases (English)
GLOSSARY = GLOSSARY_EN

def get_term(term: str, lang: str = "en"):
    if lang.lower() == "fr":
        return get_term_fr(term)
    return get_term_en(term)

def for_domain(domain=None, lang: str = "en"):
    if lang.lower() == "fr":
        return for_domain_fr(domain)
    return for_domain_en(domain)

def as_knowledge_docs(lang: str = "en"):
    if lang.lower() == "fr":
        return as_knowledge_docs_fr()
    return as_knowledge_docs_en()

__all__ = [
    "GLOSSARY",
    "GLOSSARY_EN",
    "GLOSSARY_FR",
    "get_term",
    "for_domain",
    "as_knowledge_docs",
]
