#!/usr/bin/env python3
"""IntelAI - the one script that builds and seeds this deployment's dataset.

THE DATASET IS A GENERATED VIRTUAL COMPANY: **OmniIntelOS S.A.**, an applied-AI
SaaS group headquartered in Niamey, Niger, operating across the Sahel, wider
Africa, Europe and the Americas, bilingual French/English. Its full profile,
78-month operating history (Jan 2020 - Jun 2026) and KPI model live in
`scripts/omniintelos.py`; its document estate is built by
`scripts/omniintelos_corpus.py`. Those are libraries - THIS is the only script
you run.

Why generated rather than scavenged from public sources: the metrics enterprise
dashboards actually need (SLA compliance, MTTR, ticket volume, MRR/ARR/CAC/LTV,
recruiting funnel, OEE) are a specific company's private internal systems. No
publisher reports them for an arbitrary company, so a dataset built only from
public series ends up mostly external macro context that says nothing about the
company being asked about.

What makes the generated data trustworthy is that it is internally verifiable:
  - Only primitives are modelled; every ratio is COMPUTED from them with the
    standard formula, so Gross Margin really does equal (Revenue - COGS)/Revenue
    for every one of the 78 months, and OEE really is Availability x Performance
    x Quality. A reader can re-derive any figure from other rows.
  - The frameworks are real and citable: GHG Protocol Scope 1/2/3, Google DORA,
    CVSS v3.1 bands, OEE, SaaS Rule of 40 / NRR / LTV:CAC, OHADA accounting, the
    BCEAO XOF/EUR peg of 655.957.
  - The history is one causal narrative across 12 distinct health regimes, not
    seven independent random walks: the February 2023 breach degrades uptime,
    which degrades delivery, which spikes churn a quarter later, which
    compresses revenue and runway after that.
  - It is deterministic: the same (metric, period) always produces the same
    value, so a re-seed never silently rewrites history.
  - Documents quote the same numbers the KPI tables hold, so any figure in a
    board pack can be checked against `kpi_metrics` for that period.

Every stage that writes data goes through IntelAI's real public API
(POST /api/v1/ingest/csv, /api/v1/ingest/document, /api/v1/ingest/audio) - the
same endpoints, auth, validation and audit trail a real UI upload hits. The only
direct-DB steps are the optional --purge cleanups, which have no public API
equivalent (a bulk-delete endpoint would be a genuinely dangerous thing to
expose).

Stages (run in order by default; select a subset with --only):
  build     generate the OmniIntelOS KPI series -> per-domain CSVs, and the
            document estate (PDF/XLSX/PPTX/PNG/Markdown) under data/omniintelos/
  seed-kpis POST each CSV to /api/v1/ingest/csv (global_scope=true)
  digests   write bilingual EN/FR knowledge-base text of the KPI series, so the
            retrieval index (which searches knowledge_base, not kpi_metrics) can
            answer "what was X in period Y"
  corpus    POST every generated document through /api/v1/ingest/{document,audio}

Run:
  python scripts/seed_data.py                        # everything
  python scripts/seed_data.py --only build,seed-kpis # rebuild + reseed KPIs only
  python scripts/seed_data.py --purge                # wipe existing global rows first
  python scripts/seed_data.py --dry-run              # describe every stage, write nothing

Environment variables (no hardcoded secrets or URLs):
  INTELAI_API_URL       Base URL of a running IntelAI backend (default: http://localhost:8000)
  SEED_ADMIN_USERNAME   Real login username (optional - falls back to demo-login)
  SEED_ADMIN_PASSWORD   Real login password
  INTELAI_INTERNAL_TOKEN  Cross-project gateway token, if the deployment requires one
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import os
import sys
import time
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

import httpx
import requests

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

API_BASE_URL = os.getenv("INTELAI_API_URL", "http://localhost:8000").rstrip("/")
ADMIN_USERNAME = os.getenv("SEED_ADMIN_USERNAME", "").strip()
ADMIN_PASSWORD = os.getenv("SEED_ADMIN_PASSWORD", "").strip()
INTERNAL_TOKEN = os.getenv("INTELAI_INTERNAL_TOKEN", "").strip()

CSV_COLUMNS = ["period", "category", "segment", "metric_name", "value", "unit", "direction", "source"]

AUDIO_EXT = {".mp3", ".wav", ".m4a", ".ogg", ".flac"}
IMG_EXT = {".png", ".jpg", ".jpeg", ".webp"}
DOC_EXT = {".pdf", ".txt", ".md", ".csv", ".json", ".xml", ".yaml", ".yml", ".tsv"}


# ─────────────────────────────────────────────────────────────────────────────
# Stage 1: build — generate the OmniIntelOS KPI series and document estate
# ─────────────────────────────────────────────────────────────────────────────

def stage_build(since: str, dry_run: bool) -> int:
    """Generate the OmniIntelOS KPI series and document estate."""
    from omniintelos import COMPANY, generate_kpis, months as om_months
    from omniintelos_corpus import build_corpus

    ms = om_months()
    rows = generate_kpis()
    print(f"== build: {COMPANY} ==")
    print(f"  {len(rows):,} KPI rows | {len(ms)} months {ms[0]} .. {ms[-1]} | "
          f"{len({r['category'] for r in rows})} domains")

    if dry_run:
        by_domain_dry: dict[str, int] = defaultdict(int)
        for r in rows:
            by_domain_dry[r["category"]] += 1
        for dom, n in sorted(by_domain_dry.items()):
            print(f"  [dry-run] {dom:11} {n:>6} rows")
        print(f"  [dry-run] would also generate the document corpus under {DATA / 'omniintelos'}")
        return 0

    outdir = DATA / "omniintelos_kpis"
    outdir.mkdir(parents=True, exist_ok=True)
    for f in outdir.glob("*.csv"):
        f.unlink()

    by_domain: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_domain[r["category"]].append(r)

    print("== KPI CSVs ==")
    for domain, drows in sorted(by_domain.items()):
        dest = outdir / f"{domain.lower()}.csv"
        with dest.open("w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=CSV_COLUMNS)
            w.writeheader()
            w.writerows(drows)
        metrics = len({r["metric_name"] for r in drows})
        periods = len({r["period"] for r in drows})
        print(f"  {domain:11} {len(drows):>6} rows  {metrics:>3} metrics  {periods:>3} periods -> "
              f"{dest.relative_to(ROOT)}")

    print("== document corpus ==")
    man = build_corpus(DATA / "omniintelos")
    for bucket, files in sorted(man["files"].items()):
        print(f"  {bucket:9} {len(files):>3} files")
    if man["skipped"]:
        for sk in man["skipped"]:
            print(f"  !! SKIPPED {sk}")
    print(f"  {man['count']} files, {man['bytes']:,} bytes -> {(DATA / 'omniintelos').relative_to(ROOT)}")

    print(f"\ntotal {len(rows)} KPI rows across {len(by_domain)} domains, "
          f"{man['count']} documents")
    return 0 if rows else 1


# ─────────────────────────────────────────────────────────────────────────────
# Shared: auth against the real API
# ─────────────────────────────────────────────────────────────────────────────

def _get_auth_token(client: httpx.Client) -> Optional[str]:
    if ADMIN_USERNAME and ADMIN_PASSWORD:
        try:
            r = client.post(f"{API_BASE_URL}/api/v1/auth/login",
                             json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD})
            if r.status_code == 200:
                return r.json().get("access_token")
            print(f"  login failed ({r.status_code}), falling back to demo-login")
        except httpx.HTTPError as e:
            print(f"  login error ({e}), falling back to demo-login")
    r = client.post(f"{API_BASE_URL}/api/v1/auth/demo-login", params={"role": "admin"})
    r.raise_for_status()
    return r.json().get("access_token")


def _auth_headers(token: str) -> dict:
    headers = {"Authorization": f"Bearer {token}"}
    if INTERNAL_TOKEN:
        headers["X-IntelAI-Internal-Token"] = INTERNAL_TOKEN
    return headers


# ─────────────────────────────────────────────────────────────────────────────
# Stage 3: seed-kpis — POST each CSV to /api/v1/ingest/csv
# ─────────────────────────────────────────────────────────────────────────────

def stage_seed_kpis(dry_run: bool, purge: bool = False) -> int:
    srcdir = DATA / "omniintelos_kpis"
    files = sorted(srcdir.glob("*.csv"))
    if not files:
        print(f"no CSVs in {srcdir} — run --only build first")
        return 1

    print(f"API: {API_BASE_URL}")
    if purge and not dry_run:
        # /api/v1/ingest/csv always appends (replace=False, since a re-seed must never
        # touch another visitor's own uploads that share a source name) — so re-running
        # this stage without a purge duplicates every row it already wrote last time.
        # Same deliberate direct-DB maintenance exception as corpus's --purge.
        from src.services.pg_store import _get_conn
        conn = _get_conn()
        with conn.cursor() as c:
            c.execute("DELETE FROM kpi_metrics WHERE owner_user_id IS NULL")
            print(f"purged {c.rowcount} existing global kpi_metrics rows")
            conn.commit()
        conn.close()
    if dry_run:
        total = 0
        for path in files:
            with path.open() as fh:
                n = sum(1 for _ in csv.DictReader(fh))
            print(f"  [dry-run] would POST {path.name} ({n} rows) global_scope=true")
            total += n
        print(f"files={len(files)} rows={total}")
        return 0

    with httpx.Client(timeout=180) as client:
        token = _get_auth_token(client)
        if not token:
            print("could not obtain an admin token")
            return 1
        headers = _auth_headers(token)
        ok, failed = 0, 0
        for path in files:
            with path.open("rb") as fh:
                r = client.post(f"{API_BASE_URL}/api/v1/ingest/csv", headers=headers,
                                 data={"global_scope": "true"},
                                 files={"file": (path.name, fh, "text/csv")})
            if r.status_code == 200:
                body = r.json()
                print(f"  ok {path.name:24} rows_inserted={body.get('rows_inserted')} scope={body.get('scope')}")
                ok += 1
            else:
                print(f"  !! {path.name:24} HTTP {r.status_code}: {r.text[:150]}")
                failed += 1
    print(f"seeded ok={ok} failed={failed}")
    return 0 if not failed else 1


# ─────────────────────────────────────────────────────────────────────────────
# Stage 4: digests — bilingual EN/FR knowledge-base text of the KPI series
# ─────────────────────────────────────────────────────────────────────────────

SOURCE_URLS = {
    # OmniIntelOS is generated, so its "source" resolves to the module that
    # produced it rather than to a publisher URL. Saying so plainly in every
    # digest is the point: a reader must never mistake it for a disclosed figure.
    "omniintelos": "generated by scripts/omniintelos.py - fictional company, internally consistent model",
}

LABELS = {
    "en": {
        "title": "{domain} — KPI Digest ({period}) — OmniIntelOS S.A.",
        "intro": ("Recorded values for {domain} metrics in {period} for OmniIntelOS S.A., a "
                   "FICTIONAL applied-AI company headquartered in Niamey, Niger. These figures "
                   "are generated by an internally consistent model, not disclosed by a real "
                   "company: every ratio is computed from the primitives in this same period, so "
                   "Gross Margin equals (Revenue - COGS) / Revenue exactly. The source identifier "
                   "follows each line."),
        "series": "Series covered",
        "sources": "Sources",
        "external_note": ("Rows marked external / market-context are published statistics this "
                           "West African operator tracks as planning context (US/global rates, "
                           "employment, demand) — they are not this company's own measured output."),
        "generated_note": ("Rows marked [Company Model] (source starting `generated:`) are NOT "
                            "published anywhere — they are internally generated, formula-derived from "
                            "this company's own real headcount/attrition/salary/security data, for "
                            "internal-systems metrics (ticket volume, SLA/MTTR, infrastructure "
                            "utilization, MRR/ARR/CAC/LTV, recruiting funnel) that no real external "
                            "publisher reports for a specific company. Treat them as a plausible, "
                            "correlated operating model, not a measured or disclosed figure."),
        "note": ("OmniIntelOS S.A. is a fictional company. These values are a generated, "
                  "internally consistent operating model for IntelAI demonstration and "
                  "evaluation - not targets, forecasts, or any real company's accounts."),
    },
    "fr": {
        "title": "{domain} — Synthèse des indicateurs ({period}) — OmniIntelOS S.A.",
        "intro": ("Valeurs enregistrées pour les indicateurs {domain} en {period} pour "
                   "OmniIntelOS S.A., entreprise FICTIVE d'intelligence artificielle appliquée "
                   "basée à Niamey, Niger. Ces chiffres sont produits par un modèle interne "
                   "cohérent et ne sont pas publiés par une entreprise réelle : chaque ratio est "
                   "calculé à partir des primitives de la même période, la marge brute valant "
                   "exactement (Chiffre d'affaires - Coût des ventes) / Chiffre d'affaires. "
                   "L'identifiant de la source suit chaque ligne."),
        "series": "Séries couvertes",
        "sources": "Sources",
        "external_note": ("Les lignes marquées contexte externe / marché sont des statistiques "
                           "publiées que cet opérateur ouest-africain suit à titre de contexte de "
                           "planification (taux américains/mondiaux, emploi, demande) — elles ne "
                           "représentent pas la performance propre de l'entreprise."),
        "generated_note": ("Les lignes marquées [Company Model] (source commençant par `generated:`) "
                            "ne sont PAS publiées — elles sont générées en interne, calculées à partir "
                            "des données réelles de l'entreprise (effectif, attrition, salaire, "
                            "sécurité), pour des indicateurs de systèmes internes (volume de tickets, "
                            "SLA/MTTR, utilisation de l'infrastructure, MRR/ARR/CAC/LTV, recrutement) "
                            "qu'aucune source externe ne publie pour une entreprise donnée. À "
                            "considérer comme un modèle opérationnel plausible et corrélé, non comme "
                            "un chiffre mesuré ou communiqué."),
        "note": ("OmniIntelOS S.A. est une entreprise fictive. Ces valeurs constituent un "
                  "modèle opérationnel généré et cohérent, destiné à la démonstration et à "
                  "l'évaluation d'IntelAI - ni objectifs, ni prévisions, ni comptes réels."),
    },
}

FR_METRIC = {
    "Unemployment Rate": "Taux de chômage", "Quits Rate": "Taux de démission",
    "Job Openings": "Offres d'emploi", "Average Hourly Earnings": "Salaire horaire moyen",
    "Consumer Price Index": "Indice des prix à la consommation",
    "Federal Funds Effective Rate": "Taux directeur effectif",
    "Corporate Profits After Tax": "Bénéfices des sociétés après impôt",
    "Gross Domestic Product": "Produit intérieur brut", "Retail Sales": "Ventes au détail",
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
    "Attrition Rate": "Taux d'attrition", "Average Monthly Income": "Revenu mensuel moyen",
    "Average Tenure": "Ancienneté moyenne", "Job Satisfaction Score": "Score de satisfaction au travail",
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


def stage_digests(months: int, dry_run: bool) -> int:
    """Write one ANNUAL digest per (domain, year, language), each carrying that
    year's full month-by-month table.

    Deliberately annual, not monthly. 78 monthly periods x 7 domains x 2 languages
    is 1,092 near-identical documents; hybrid retrieval then returns six adjacent
    months of the same domain for almost any query, which is worse than useless -
    it crowds out the narrative documents (board packs, post-mortems, handbooks)
    that actually let the copilot reason. Rolling up to the year keeps every exact
    monthly figure retrievable as text while cutting the corpus to 98 digests, and
    exact period lookups are additionally served directly from kpi_metrics by
    _retrieve_context()'s period detection, which does not depend on these files.
    """
    from src.services.pg_store import _get_conn

    conn = _get_conn()
    with conn.cursor() as c:
        # owner_user_id IS NULL only — this writes into the SHARED knowledge base,
        # so an unscoped query here would bake one visitor's private uploads into
        # text every other visitor can retrieve.
        c.execute("""SELECT period, category, metric, value, unit, segment, source
                     FROM kpi_metrics WHERE owner_user_id IS NULL
                     ORDER BY category, period, metric""")
        rows = [dict(r) for r in c.fetchall()]
    conn.close()
    if not rows:
        print("kpi_metrics is empty — run --only seed-kpis first")
        return 1

    # (domain, year) -> {period -> {metric -> row}}
    grouped: dict[tuple[str, str], dict[str, dict[str, dict]]] = defaultdict(lambda: defaultdict(dict))
    for r in rows:
        grouped[(r["category"], r["period"][:4])][r["period"]][r["metric"]] = r

    out = DATA / "kpi_digests"
    if dry_run:
        print(f"[dry-run] would write {len(grouped) * 2} annual digests "
              f"({len(grouped)} domain-years x 2 languages) to {out}")
        return 0

    out.mkdir(parents=True, exist_ok=True)
    for f in out.rglob("*.md"):
        f.unlink()

    written = 0
    for (domain, year), per_period in sorted(grouped.items()):
        periods = sorted(per_period)
        metrics = sorted({m for p in periods for m in per_period[p]})
        for lang in ("en", "fr"):
            L = LABELS[lang]
            fr = lang == "fr"
            head = (f"{domain} — Synthèse annuelle {year} — OmniIntelOS S.A." if fr
                    else f"{domain} — Annual KPI Digest {year} — OmniIntelOS S.A.")
            lines = [f"# {head}", "",
                     L["intro"].format(domain=domain, period=year), "",
                     ("## Résumé de l'année" if fr else "## Year summary"), ""]
            # Opening and closing level per metric, so the year reads as a trajectory.
            first_p, last_p = periods[0], periods[-1]
            lines.append(("| Indicateur | Début (%s) | Fin (%s) | Unité |" % (first_p, last_p)) if fr
                         else ("| Metric | Start (%s) | End (%s) | Unit |" % (first_p, last_p)))
            lines.append("|---|---|---|---|")
            for m in metrics:
                a = per_period[first_p].get(m)
                b = per_period[last_p].get(m)
                if not b:
                    continue
                name = FR_METRIC.get(m, m) if fr else m
                lines.append(f"| {name} | {_fmt(a['value'], a['unit']) if a else '-'} | "
                             f"{_fmt(b['value'], b['unit'])} | {b['unit']} |")
            lines += ["", ("## Détail mensuel" if fr else "## Month-by-month detail"), ""]
            for p in periods:
                lines.append(f"### {p}")
                for m in metrics:
                    r = per_period[p].get(m)
                    if not r:
                        continue
                    name = FR_METRIC.get(m, m) if fr else m
                    seg = f" [{r['segment']}]" if r["segment"] else ""
                    lines.append(f"- {name}{seg}: {_fmt(r['value'], r['unit'])}  (source: {r['source']})")
                lines.append("")
            srcs = sorted({r["source"] for p in periods for r in per_period[p].values()})
            lines += [f"## {L['sources']}"]
            for src in srcs:
                lines.append(f"- {src} — {_source_url(src)}")
            lines += ["", L["note"]]

            dest_dir = out / domain
            dest_dir.mkdir(parents=True, exist_ok=True)
            (dest_dir / f"{domain.lower()}_{year}_{lang}.md").write_text("\n".join(lines), encoding="utf-8")
            written += 1

    print(f"wrote {written} annual digest documents to {out}")
    return 0


# ─────────────────────────────────────────────────────────────────────────────
# Stage 5: corpus — POST real documents/images/audio + digests via the API
# ─────────────────────────────────────────────────────────────────────────────

def _discover_corpus() -> list[tuple[Path, str, str]]:
    """Walk the generated OmniIntelOS estate. The immediate subdirectory name is
    the ingest category, matching the KPI domains so a retrieved document and the
    KPI rows it quotes land in the same domain scope."""
    # Two roots: the generated document estate, and the annual KPI digests. Both are
    # laid out as <root>/<Domain>/<file>, so the immediate parent directory is the
    # ingest category either way. Omitting kpi_digests here silently shipped a corpus
    # with no KPI text in it at all - exactly the retrieval gap this dataset exists
    # to close.
    out: list[tuple[Path, str, str]] = []
    domain_dirs: list[Path] = []
    for root in (DATA / "omniintelos", DATA / "kpi_digests"):
        if root.exists():
            domain_dirs.extend(sorted(q for q in root.iterdir() if q.is_dir()))
    for domain_dir in domain_dirs:
        for path in sorted(domain_dir.rglob("*")):
            if not path.is_file():
                continue
            ext = path.suffix.lower()
            if ext in AUDIO_EXT:
                kind = "audio"
            elif ext in IMG_EXT:
                kind = "image"
            elif ext in DOC_EXT or ext in (".xlsx", ".pptx"):
                kind = "document"
            else:
                continue
            out.append((path, domain_dir.name, kind))
    return out


def stage_corpus(purge: bool, only: str, dry_run: bool, timeout: float) -> int:
    items = _discover_corpus()
    if only:
        items = [i for i in items if only.lower() in i[0].name.lower()]
    if not items:
        print("no corpus files found")
        return 1

    by_kind: dict[str, int] = {}
    for _, _, k in items:
        by_kind[k] = by_kind.get(k, 0) + 1
    print(f"corpus: {len(items)} files {by_kind}")
    print(f"API: {API_BASE_URL}")

    if dry_run:
        for path, cat, kind in items:
            print(f"  [dry-run] {kind:9} {cat:12} {path.name} ({path.stat().st_size:,}b)")
        return 0

    if purge:
        # No public API for a bulk category wipe — this one step is direct DB
        # access, a deliberate maintenance operation, not part of the seeding
        # path itself (which is entirely POST /api/v1/ingest/*, same as this
        # script's other stages and the same as a real UI upload).
        from src.services.pg_store import _get_conn
        conn = _get_conn()
        with conn.cursor() as c:
            c.execute("DELETE FROM knowledge_base WHERE source NOT LIKE 'glossary%%'")
            print(f"purged {c.rowcount} existing non-glossary rows")
            conn.commit()
        conn.close()

    ok, failed, chars = 0, 0, 0
    with httpx.Client(timeout=timeout) as client:
        token = _get_auth_token(client)
        if not token:
            print("could not obtain an admin token")
            return 1
        headers = _auth_headers(token)
        for path, category, kind in items:
            endpoint = "audio" if kind == "audio" else "document"
            data = {"category": category, "global_scope": "true"}
            if kind == "audio":
                data["analysis_type"] = "meeting"
            try:
                with path.open("rb") as fh:
                    r = client.post(f"{API_BASE_URL}/api/v1/ingest/{endpoint}", headers=headers,
                                     data=data, files={"file": (path.name, fh, "application/octet-stream")})
            except httpx.HTTPError as e:
                print(f"  !! {kind:9} {path.name[:42]:44} transport: {str(e)[:70]}")
                failed += 1
                continue
            if r.status_code == 200:
                n = r.json().get("chars", 0)
                chars += n
                ok += 1
                print(f"  ok {kind:9} {category:12} {path.name[:38]:40} {n:>8,} chars")
            else:
                failed += 1
                print(f"  !! {kind:9} {category:12} {path.name[:38]:40} HTTP {r.status_code}: {r.text[:120]}")

    print(f"\ningested ok={ok} failed={failed}  total {chars:,} chars")
    return 0 if not failed else 1


# ─────────────────────────────────────────────────────────────────────────────

STAGES = {
    "build": lambda a: stage_build(a.since, a.dry_run),
    "seed-kpis": lambda a: stage_seed_kpis(a.dry_run, a.purge),
    "digests": lambda a: stage_digests(a.months, a.dry_run),
    "corpus": lambda a: stage_corpus(a.purge, a.only_file, a.dry_run, a.timeout),
}
STAGE_ORDER = ["build", "seed-kpis", "digests", "corpus"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", default="", help="comma-separated subset of: " + ",".join(STAGE_ORDER))
    ap.add_argument("--refetch", action="store_true", help="re-download raw sources even if cached")
    ap.add_argument("--since", default="2019-01", help="earliest period to keep from long-running series")
    ap.add_argument("--months", type=int, default=78,
                    help="recent periods per domain in digests (default 78 = the full OmniIntelOS history)")
    ap.add_argument("--purge", action="store_true", help="wipe existing global rows first (seed-kpis: kpi_metrics; corpus: non-glossary knowledge_base)")
    ap.add_argument("--only-file", default="", help="substring filter on filename (corpus stage)")
    ap.add_argument("--timeout", type=float, default=900.0)
    ap.add_argument("--dry-run", action="store_true", help="describe every stage, write/POST nothing")
    args = ap.parse_args()

    stages = [s.strip() for s in args.only.split(",") if s.strip()] if args.only else STAGE_ORDER
    unknown = set(stages) - set(STAGE_ORDER)
    if unknown:
        print(f"unknown stage(s): {unknown} — valid: {STAGE_ORDER}")
        return 1

    for stage in stages:
        print(f"\n{'='*70}\n{stage}\n{'='*70}")
        rc = STAGES[stage](args)
        if rc != 0:
            print(f"\nstage '{stage}' failed (exit {rc}) — stopping")
            return rc
    return 0


if __name__ == "__main__":
    sys.exit(main())
