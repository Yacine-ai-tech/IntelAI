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
# knowledge_base for the case to be emitted — kept in sync with the real
# OmniIntelOS corpus (PDF/PPTX/XLSX/WAV), not a leftover from an earlier dataset.
DOC_CASES = [
    ("omniintelos_annual_report_2025_en.pdf", "What does the 2025 annual report say about revenue and business risks?", "cfo"),
    ("omniintelos_esg_report_2025_en.pdf", "What does the 2025 ESG report cover?", "esg"),
    ("omniintelos_dc1_whitepaper_en.pdf", "What does the DC1 whitepaper describe about the new data center?", "cto"),
    ("omniintelos_incident_postmortem_INC-2023-0214_en.pdf", "What happened during incident INC-2023-0214, and what was the resolution?", "cto"),
    ("omniintelos_employee_handbook_2026_en.pdf", "What does the employee handbook say about company policy?", "chro"),
    ("omniintelos_employee_handbook_2026_fr.pdf", "Que dit le manuel de l'employé sur la politique de l'entreprise ?", "chro"),
    ("omniintelos_board_deck_2025Q4_en.pptx", "What was presented in the Q4 2025 board deck?", "ceo"),
    ("omniintelos_financial_model_2020_2026.xlsx", "What does the financial model project for the company?", "cfo"),
    ("omniintelos_ceo_allhands_2023-02_en.wav", "What did the CEO discuss in the February 2023 all-hands meeting?", "ceo"),
    ("omniintelos_comite_crise_2020-05_fr.wav", "Qu'a-t-on discuté lors du comité de crise de mai 2020 ?", "ceo"),
    ("omniintelos_dc1_commissioning_2024-07_en.wav", "What happened during the DC1 data center commissioning?", "cto"),
    ("omniintelos_hr_townhall_2022-09_en.wav", "What was discussed at the September 2022 HR town hall?", "chro"),
]

GLOSSARY_CASES = [
    ("Capacity Utilization", "What does capacity utilization mean?", "general"),
    ("Turnover Rate", "How is turnover rate defined?", "chro"),
    ("Revenue", "Define revenue as this system uses the term.", "general"),
]

# Beyond single-value lookups: the copilot is built to correlate metrics, assess
# health/risk status, produce grounded action plans, and pull in live web context
# when internal data alone can't answer (see PERSONA_TEMPLATES' "when you do
# recommend, tie it to a specific figure" instruction and _needs_web in
# omnismart_chatbot.py). Each entry names the real metric(s) it depends on so it's
# still checked against the live DB before being emitted, same discipline as the
# KPI cases above — this just exercises reasoning ACROSS data rather than a single
# value lookup.
CAPABILITY_CASES = [
    ("How does Deployment Frequency correlate with Change Failure Rate over the "
     "period we have on record, and what does that tell us about release risk?",
     "cto", "IT", "correlation", ["Deployment Frequency", "Change Failure Rate"]),
    ("How does Customer Acquisition Cost (CAC) correlate with Sales & Marketing Spend, "
     "and is our spend efficiency improving or worsening over time?",
     "analyst", "cross", "correlation", ["CAC", "Sales & Marketing Spend"]),
    ("Based on Audit Compliance Score and Privacy Incident Count, what is our current "
     "compliance health status, and are there any red flags?",
     "risk", "ESG", "health", ["Audit Compliance Score", "Privacy Incident Count"]),
    ("Given the current Stockout Rate and On-Time Delivery Rate, what action plan "
     "would you recommend to improve fulfillment reliability?",
     "coo", "Logistics", "action-plan", ["Stockout Rate", "On-Time Delivery Rate"]),
    ("Given the current Annual Employee Turnover and Absenteeism Rate, what action "
     "plan would you recommend to improve retention?",
     "chro", "People", "action-plan", ["Annual Employee Turnover", "Absenteeism Rate"]),
    ("How does our Renewable Energy Ratio compare to current industry best practices "
     "and benchmark standards for sustainability?",
     "esg", "ESG", "web-search", ["Renewable Energy Ratio"]),
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
        c.execute("""SELECT category, metric, period, unit, source, value FROM kpi_metrics""")
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
        # Group by metric, keeping every period each metric has (2020-01..2026-06 in
        # the real corpus) — previously this always picked each metric's single latest
        # period, and since every metric's latest period is the same month, the whole
        # eval set ended up asking about that one month regardless of what else existed.
        by_metric: dict[str, list[dict]] = {}
        for r in rows:
            by_metric.setdefault(r["metric"], []).append(r)
        metrics = sorted(by_metric)
        for i, metric in enumerate(metrics[:3]):
            periods_sorted = sorted(by_metric[metric], key=lambda r: r["period"])
            # Rotate the 3 sampled metrics per domain through the early / mid / recent
            # third of the timeline instead of all landing on the same month — real
            # timeline coverage, not three questions about the same period.
            third = max(len(periods_sorted) // 3, 1)
            buckets = [periods_sorted[:third], periods_sorted[third:2 * third], periods_sorted[2 * third:]]
            bucket = buckets[i % 3] or periods_sorted
            r = rng.choice(bucket)
            tpl = rng.choice(EN_TEMPLATES)
            cases.append({
                "query": tpl.format(metric=r["metric"], period=r["period"]),
                "expected": r["metric"].lower(),
                "persona": persona,
                "domain": domain,
                "provenance": r["source"],
                "kind": "kpi",
                # Real ground truth from the live DB, not a subjective judge score —
                # lets the eval check factual correctness (does the answer contain
                # the actual recorded value) independent of any LLM judge's
                # availability. See evaluate_production_live.py's ground-truth check.
                "expected_value": r["value"],
                "expected_unit": r["unit"],
            })
        # one French case per domain, also drawn from a random period rather than
        # always the latest, for the same timeline-diversity reason as above
        if metrics:
            r = rng.choice(by_metric[metrics[0]])
            cases.append({
                "query": rng.choice(FR_TEMPLATES).format(metric=r["metric"], period=r["period"]),
                "expected": r["metric"].lower(),
                "persona": persona,
                "domain": domain,
                "provenance": r["source"],
                "kind": "kpi-fr",
                "expected_value": r["value"],
                "expected_unit": r["unit"],
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

    # --- capability cases: correlation / health-status / action-plan / web-search ---
    all_metrics = {r["metric"] for r in kpis}
    for query, persona, domain, kind, required_metrics in CAPABILITY_CASES:
        missing = [m for m in required_metrics if m not in all_metrics]
        if missing:
            print(f"  skip ({kind}, metric(s) not in DB): {missing}")
            continue
        cases.append({"query": query, "expected": None, "persona": persona,
                      "domain": domain, "provenance": ",".join(required_metrics),
                      "kind": kind})

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
