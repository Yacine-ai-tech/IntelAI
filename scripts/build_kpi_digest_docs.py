#!/usr/bin/env python3
"""Write knowledge-base digests of the real KPI series, in English and French.

The retrieval index searches knowledge_base, not kpi_metrics, so without a text
representation the assistant cannot answer "what was unemployment in June 2026"
even though the number is sitting in the database. This script generates that
text — and only that text.

Every sentence here is a restatement of a stored value together with the series
it came from. There is no commentary, no target, no explanation of *why* a number
moved, and no claim of audit or approval: the fabricated digests these replace
asserted things like "audited by the internal compliance team" above numbers that
were themselves generated, which is precisely what must not happen. If a figure
appears in a digest, it is in kpi_metrics with the same provenance string.

Run:  python scripts/build_kpi_digest_docs.py [--out data/kpi_digests] [--months 18]
"""
from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

SOURCE_URLS = {
    "fred": "https://fred.stlouisfed.org/series/{sid}",
    "worldbank": "https://data.worldbank.org/indicator/{sid}",
    "nvd": "https://nvd.nist.gov/vuln/search",
    "ibm-hr": "IBM HR Analytics Employee Attrition dataset",
    "sonatel": "https://sonatel.sn (communiqués de résultats)",
}

LABELS = {
    "en": {
        "title": "{domain} — Real KPI Digest ({period})",
        "intro": ("Recorded values for {domain} metrics in {period}. Each figure is "
                  "reproduced exactly as published by its source; the source identifier "
                  "follows each line."),
        "series": "Series covered",
        "sources": "Sources",
        "note": ("These are observations from published statistical series, not targets, "
                 "forecasts or internal accounts."),
    },
    "fr": {
        "title": "{domain} — Synthèse des indicateurs réels ({period})",
        "intro": ("Valeurs enregistrées pour les indicateurs {domain} en {period}. Chaque "
                  "chiffre est reproduit tel que publié par sa source ; l'identifiant de "
                  "la source suit chaque ligne."),
        "series": "Séries couvertes",
        "sources": "Sources",
        "note": ("Il s'agit d'observations issues de séries statistiques publiées, et non "
                 "d'objectifs, de prévisions ou de comptes internes."),
    },
}

# Metric names that already read naturally in French (the FCFA figures are
# published in French) are left alone rather than machine-translated.
FR_METRIC = {
    "Unemployment Rate": "Taux de chômage",
    "Quits Rate": "Taux de démission",
    "Job Openings": "Offres d'emploi",
    "Average Hourly Earnings": "Salaire horaire moyen",
    "Consumer Price Index": "Indice des prix à la consommation",
    "Federal Funds Effective Rate": "Taux directeur effectif",
    "Corporate Profits After Tax": "Bénéfices des sociétés après impôt",
    "Gross Domestic Product": "Produit intérieur brut",
    "Retail Sales": "Ventes au détail",
    "E-Commerce Retail Sales": "Ventes au détail en ligne",
    "Consumer Sentiment Index": "Indice de confiance des consommateurs",
    "Industrial Production Index": "Indice de production industrielle",
    "Capacity Utilization": "Taux d'utilisation des capacités",
    "Business Inventories": "Stocks des entreprises",
    "Freight Transportation Index": "Indice du transport de marchandises",
    "Software Publishers Employment": "Emploi dans l'édition de logiciels",
    "Computer Systems Design Employment": "Emploi en conception de systèmes informatiques",
    "CO2 Emissions (excl. LULUCF)": "Émissions de CO2 (hors UTCATF)",
    "Total Greenhouse Gas Emissions": "Émissions totales de gaz à effet de serre",
    "Renewable Energy Share": "Part des énergies renouvelables",
    "Energy Use per Capita": "Consommation d'énergie par habitant",
    "Attrition Rate": "Taux d'attrition",
    "Average Monthly Income": "Revenu mensuel moyen",
    "Average Tenure": "Ancienneté moyenne",
    "Job Satisfaction Score": "Score de satisfaction au travail",
    "Average Employee Age": "Âge moyen des employés",
}


def _fmt(value: float, unit: str) -> str:
    if unit in ("USD", "FCFA"):
        return f"{value:,.0f} {unit}"
    if unit == "%":
        return f"{value:,.2f} %"
    return f"{value:,.2f} {unit}".strip()


def _source_url(source: str) -> str:
    kind, _, sid = source.partition(":")
    tpl = SOURCE_URLS.get(kind)
    if not tpl:
        return source
    return tpl.format(sid=sid) if "{sid}" in tpl else tpl


def build(months: int, out: Path) -> int:
    from src.services.pg_store import _get_conn

    conn = _get_conn()
    with conn.cursor() as c:
        c.execute("""SELECT period, category, metric, value, unit, segment, source
                     FROM kpi_metrics ORDER BY category, period, metric""")
        rows = [dict(r) for r in c.fetchall()]
    conn.close()
    if not rows:
        print("kpi_metrics is empty — seed the real KPIs first")
        return 1

    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in rows:
        grouped[(r["category"], r["period"])].append(r)

    # Most recent N periods per domain, so digests describe current data rather
    # than every period ever recorded.
    per_domain: dict[str, list[str]] = defaultdict(list)
    for domain, period in grouped:
        per_domain[domain].append(period)
    keep = {(d, p) for d, ps in per_domain.items() for p in sorted(ps)[-months:]}

    out.mkdir(parents=True, exist_ok=True)
    for f in out.rglob("*.md"):
        f.unlink()

    written = 0
    for (domain, period), items in sorted(grouped.items()):
        if (domain, period) not in keep:
            continue
        for lang in ("en", "fr"):
            L = LABELS[lang]
            lines = [f"# {L['title'].format(domain=domain, period=period)}", ""]
            lines.append(L["intro"].format(domain=domain, period=period))
            lines.append("")
            lines.append(f"## {L['series']}")
            for r in sorted(items, key=lambda x: x["metric"]):
                name = FR_METRIC.get(r["metric"], r["metric"]) if lang == "fr" else r["metric"]
                seg = f" [{r['segment']}]" if r["segment"] and r["segment"] != "US" else ""
                lines.append(f"- {name}{seg}: {_fmt(r['value'], r['unit'])}  "
                             f"(source: {r['source']})")
            lines.append("")
            lines.append(f"## {L['sources']}")
            for src in sorted({r["source"] for r in items}):
                lines.append(f"- {src} — {_source_url(src)}")
            lines.append("")
            lines.append(L["note"])

            # One directory per domain: the corpus ingester reads the directory
            # name as the row's category, so this is what files each digest
            # under Finance, People, ESG and so on.
            dest_dir = out / domain
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest = dest_dir / f"{domain.lower()}_{period}_{lang}.md"
            dest.write_text("\n".join(lines), encoding="utf-8")
            written += 1

    print(f"wrote {written} digest documents to {out}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--months", type=int, default=18,
                    help="how many recent periods per domain to describe")
    ap.add_argument("--out", default="data/kpi_digests")
    args = ap.parse_args()
    return build(args.months, ROOT / args.out)


if __name__ == "__main__":
    sys.exit(main())
