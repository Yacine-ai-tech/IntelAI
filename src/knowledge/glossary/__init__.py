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
    GLOSSARY_FR,
)

# Default aliases (English)
GLOSSARY = GLOSSARY_EN

def get_term(term: str, lang: str = "en"):
    entry = get_term_en(term)
    if not entry:
        return None
    if lang.lower() == "fr":
        res = dict(entry)
        over = GLOSSARY_FR.get(term, {})
        res.update(over)
        return res
    return entry

def for_domain(domain=None, lang: str = "en"):
    terms = for_domain_en(domain)
    if lang.lower() == "fr":
        res = {}
        for t, data in terms.items():
            entry = dict(data)
            over = GLOSSARY_FR.get(t, {})
            entry.update(over)
            res[t] = entry
        return res
    return terms

def as_knowledge_docs(lang: str = "en"):
    docs = as_knowledge_docs_en()
    if lang.lower() == "fr":
        res = []
        for doc in docs:
            # overlay French if term matches
            term_name = doc.get("metadata", {}).get("term")
            if term_name and term_name in GLOSSARY_FR:
                over = GLOSSARY_FR[term_name]
                doc_copy = dict(doc)
                content = doc_copy.get("content", "")
                if "definition" in over:
                    content += f"\nDefinition (FR): {over['definition']}"
                doc_copy["content"] = content
                res.append(doc_copy)
            else:
                res.append(doc)
        return res
    return docs

__all__ = [
    "GLOSSARY",
    "GLOSSARY_EN",
    "GLOSSARY_FR",
    "get_term",
    "for_domain",
    "as_knowledge_docs",
]
