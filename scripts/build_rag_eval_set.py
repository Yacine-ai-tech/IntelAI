#!/usr/bin/env python3
"""Generate tests/rag_eval.jsonl from what is actually in the database.

An evaluation set is only meaningful if its questions are answerable from the
corpus under test. The previous set asked about gross margin, EBITDA and net
profit — metrics that belonged to the generated seed data. Against the real
corpus those questions have no answer, so every score would measure the
mismatch rather than the system.

So the questions are derived here rather than written by hand: each one names a
metric that is in kpi_metrics for a period that exists, or a document that is in
knowledge_base, and every case is verified against the database before it is
written out. A case that cannot be verified is dropped, not shipped.

Run:  python scripts/build_rag_eval_set.py [--out tests/rag_eval.jsonl]
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# Which persona owns which domain, using the nine personas the app implements.
DOMAIN_PERSONA = {
    "Finance": "cfo",
    "People": "chro",
    "IT": "cto",
    "Operations": "coo",
    "Logistics": "coo",
    "ESG": "esg",
    "Growth": "analyst",
}

EN_TEMPLATES = [
    "What was {metric} in {period}?",
    "Report the recorded value of {metric} for {period}.",
    "How did {metric} stand in {period}, and where does that figure come from?",
]
FR_TEMPLATES = [
    "Quelle était la valeur de {metric} en {period} ?",
    "Donnez le chiffre enregistré pour {metric} au titre de {period}.",
]

# Document questions. Each names a document that must be present in
# knowledge_base for the case to be emitted.
DOC_CASES = [
    ("salesforce_10K_2026.txt", "What does Salesforce's annual report say about its revenue and business risks?", "cfo"),
    ("salesforce_10Q_2026Q1.txt", "Summarise the most recent Salesforce quarterly results.", "cfo"),
    ("salesforce_q1fy27_earnings_release.txt", "What did Salesforce report in its latest earnings release?", "analyst"),
    ("sonatel_resultats_fcfa_verified.md", "Quel chiffre d'affaires le Groupe Sonatel a-t-il publié, et en quelle devise ?", "cfo"),
    ("sonatel_resultats_fcfa_verified.md", "What revenue did Sonatel Group report in FCFA?", "cfo"),
    ("dora_2024_report_findings.md", "What do the DORA findings say about software delivery performance?", "cto"),
    ("ibm_hr_attrition.csv", "What does the HR attrition data show about employees who left?", "chro"),
    ("hr_employee_churn.csv", "What factors appear in the employee churn dataset?", "chro"),
    ("richmond_fed_family_transfers_2026.mp3", "What was discussed in the Richmond Fed recording about family transfers?", "ceo"),
]

GLOSSARY_CASES = [
    ("Capacity Utilization", "What does capacity utilization mean?", "general"),
    ("Attrition", "How is attrition defined?", "chro"),
    ("Revenue", "Define revenue as this system uses the term.", "general"),
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="tests/rag_eval.jsonl")
    ap.add_argument("--seed", type=int, default=11,
                    help="fixed so the set is reproducible between runs")
    args = ap.parse_args()
    rng = random.Random(args.seed)

    from src.services.pg_store import _get_conn
    conn = _get_conn()
    with conn.cursor() as c:
        c.execute("""SELECT category, metric, period, unit, source FROM kpi_metrics""")
        kpis = [dict(r) for r in c.fetchall()]
        c.execute("""SELECT title, source FROM knowledge_base""")
        docs = [dict(r) for r in c.fetchall()]
    conn.close()

    if not kpis:
        print("kpi_metrics is empty — nothing to build an evaluation set from")
        return 1

    titles = {d["title"] for d in docs}
    have_digest = {d["title"] for d in docs if "Digest" in str(d["title"])
                   or "Synthèse" in str(d["title"])}
    cases: list[dict] = []

    # --- KPI questions, drawn from metric/period pairs that exist -------------
    by_domain: dict[str, list[dict]] = {}
    for r in kpis:
        by_domain.setdefault(r["category"], []).append(r)

    for domain, rows in sorted(by_domain.items()):
        persona = DOMAIN_PERSONA.get(domain, "analyst")
        # latest period per metric, so the question targets current data
        latest: dict[str, dict] = {}
        for r in rows:
            k = r["metric"]
            if k not in latest or r["period"] > latest[k]["period"]:
                latest[k] = r
        picks = sorted(latest.values(), key=lambda r: r["metric"])
        for r in picks[:3]:
            tpl = rng.choice(EN_TEMPLATES)
            cases.append({
                "query": tpl.format(metric=r["metric"], period=r["period"]),
                "expected": r["metric"].lower(),
                "persona": persona,
                "domain": domain,
                "provenance": r["source"],
                "kind": "kpi",
            })
        # one French case per domain, mirroring the bilingual digests
        if picks:
            r = picks[0]
            cases.append({
                "query": rng.choice(FR_TEMPLATES).format(metric=r["metric"], period=r["period"]),
                "expected": r["metric"].lower(),
                "persona": persona,
                "domain": domain,
                "provenance": r["source"],
                "kind": "kpi-fr",
            })

    # --- document questions, only for documents actually present -------------
    for title, query, persona in DOC_CASES:
        if title in titles:
            cases.append({"query": query, "expected": title.split(".")[0].lower(),
                          "persona": persona, "domain": "document",
                          "provenance": title, "kind": "document"})
        else:
            print(f"  skip (not ingested): {title}")

    for term, query, persona in GLOSSARY_CASES:
        if any(str(t).lower() == f"glossary: {term.lower()}" for t in titles):
            cases.append({"query": query, "expected": term.lower(), "persona": persona,
                          "domain": "glossary", "provenance": f"glossary:{term}",
                          "kind": "glossary"})
        else:
            print(f"  skip (no glossary entry): {term}")

    # --- cross-domain, for the executive personas ----------------------------
    domains = sorted(by_domain)
    if len(domains) >= 2:
        a, b = domains[0], domains[1]
        cases.append({
            "query": f"Give an overview of how {a} and {b} indicators are tracking.",
            "expected": a.lower(), "persona": "ceo", "domain": "cross",
            "provenance": "multiple", "kind": "cross-domain",
        })

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fh:
        for case in cases:
            fh.write(json.dumps(case, ensure_ascii=False) + "\n")

    kinds: dict[str, int] = {}
    personas: dict[str, int] = {}
    for c_ in cases:
        kinds[c_["kind"]] = kinds.get(c_["kind"], 0) + 1
        personas[c_["persona"]] = personas.get(c_["persona"], 0) + 1
    print(f"wrote {len(cases)} cases -> {out}")
    print(f"  by kind:    {kinds}")
    print(f"  by persona: {personas}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
