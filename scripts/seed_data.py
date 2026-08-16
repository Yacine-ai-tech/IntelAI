#!/usr/bin/env python3
"""IntelAI — the one script that builds and seeds this deployment's dataset.

The virtual company this data describes: a West African telecom group,
headquartered in Senegal (Sonatel/Orange Group's own real, published figures are
its Finance anchor), operating bilingually in French and English.

Every stage that actually writes data goes through IntelAI's real public API
(POST /api/v1/ingest/csv, /api/v1/ingest/document, /api/v1/ingest/audio) — the
exact same endpoints, auth, validation and audit trail a real user's UI upload
hits. Nothing here writes to Postgres behind the application's back. The only
direct-DB step is the optional --purge cleanup before a full re-seed, which has
no public API equivalent (a bulk-delete endpoint would be a genuinely dangerous
thing to expose).

Nothing here generates, extrapolates, or smooths a value. Every KPI row carries
the identifier of the real published series it came from; where a publisher has
no observation for a period, no row is written for that period. Real series do
not all share one frequency: FRED's series are monthly/quarterly, World Bank ESG
is annual, the HR survey and Sonatel's communiqués are single/half-year
cross-sections. The output reflects that unevenness rather than hiding it.

Stages (run in order by default; select a subset with --only):
  fetch     download raw sources to data/<Domain>/ (skipped if already present;
            --refetch forces a re-download)
  build     turn the raw sources into per-domain CSVs in data/real_kpis/
  seed-kpis POST each CSV to /api/v1/ingest/csv (global_scope=true)
  digests   write bilingual EN/FR knowledge-base text of the KPI series, so the
            retrieval index (which searches knowledge_base, not kpi_metrics) can
            actually answer "what was X in period Y"
  corpus    POST every real document/image/audio file under data/<Domain>/, plus
            the digests just written, through /api/v1/ingest/{document,audio}

Run:
  python scripts/seed_data.py                       # everything, using cached raw data
  python scripts/seed_data.py --refetch              # re-download from source first
  python scripts/seed_data.py --only build,seed-kpis # rebuild + reseed KPIs only
  python scripts/seed_data.py --purge --only corpus  # wipe + re-ingest the document corpus
  python scripts/seed_data.py --dry-run              # describe every stage, write/POST nothing

Environment variables (no hardcoded secrets or URLs):
  INTELAI_API_URL       Base URL of a running IntelAI backend (default: http://localhost:8000)
  SEED_ADMIN_USERNAME   Real login username (optional — falls back to demo-login)
  SEED_ADMIN_PASSWORD   Real login password
  OMNIINTEL_INTERNAL_TOKEN  Cross-project gateway token, if the target deployment requires one
"""
from __future__ import annotations

import argparse
import csv
import io
import json
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

API_BASE_URL = os.getenv("INTELAI_API_URL", "http://localhost:8000").rstrip("/")
ADMIN_USERNAME = os.getenv("SEED_ADMIN_USERNAME", "").strip()
ADMIN_PASSWORD = os.getenv("SEED_ADMIN_PASSWORD", "").strip()
INTERNAL_TOKEN = os.getenv("OMNIINTEL_INTERNAL_TOKEN", "").strip()

CSV_COLUMNS = ["period", "category", "segment", "metric_name", "value", "unit", "direction", "source"]

# Real series this company's own systems don't publish — genuinely useful macro
# context a real operator tracks, but not the company's own measured output. No
# West African equivalent exists at FRED's free monthly frequency, so this is
# kept as real, honestly-labeled external context rather than either fabricated
# for the company's own home region or silently presented as if it were.
EXTERNAL_MARKET_SEGMENT = "External — US Market Context"

FRED_CATALOG: dict[str, dict[str, tuple[str, str]]] = {
    "Finance": {
        "CP": ("Corporate Profits After Tax", "USD bn"),
        "FEDFUNDS": ("Federal Funds Effective Rate", "%"),
        "CPIAUCSL": ("Consumer Price Index (All Urban)", "index"),
        "GDP": ("Gross Domestic Product", "USD bn"),
    },
    "Growth": {
        "RSXFS": ("Retail Sales (ex Food Services)", "USD mn"),
        "ECOMSA": ("E-Commerce Retail Sales", "USD mn"),
        "UMCSENT": ("Consumer Sentiment Index", "index"),
    },
    "People": {
        "UNRATE": ("Unemployment Rate", "%"),
        "JTSQUR": ("Quits Rate", "%"),
        "JTSJOL": ("Job Openings", "thousands"),
        "CES0500000003": ("Average Hourly Earnings", "USD/hour"),
    },
    "IT": {
        "CES5051200001": ("Software Publishers Employment", "thousands"),
        "CES6054150001": ("Computer Systems Design Employment", "thousands"),
    },
    "Operations": {
        "INDPRO": ("Industrial Production Index", "index"),
        "TCU": ("Capacity Utilization", "%"),
    },
    "Logistics": {
        "BUSINV": ("Business Inventories", "USD mn"),
        "TSIFRGHTC": ("Freight Transportation Services Index", "index"),
    },
    "ESG": {
        "EMISSCO2TOTVTTTOUSA": ("CO2 Emissions, Transport Sector", "Mt CO2"),
    },
}

WORLDBANK_INDICATORS = {
    "EN.GHG.CO2.MT.CE.AR5": "CO2 Emissions (excl. LULUCF)",
    "EG.FEC.RNEW.ZS": "Renewable Energy Share of Final Consumption",
    "EG.USE.PCAP.KG.OE": "Energy Use per Capita",
    "EN.GHG.ALL.MT.CE.AR5": "Total Greenhouse Gas Emissions",
}

# Real World Bank regional/country aggregates matching the company's own footprint
# (Senegal-headquartered, West African) plus "World" as external benchmark context
# only — not a second, competing home geography. See the module docstring.
WORLDBANK_SEGMENTS = {"World", "Senegal", "Africa Western and Central"}

WORLDBANK_METRICS = {
    "EN.GHG.CO2.MT.CE.AR5": ("CO2 Emissions (excl. LULUCF)", "tonnes_CO2e", "down"),
    "EN.GHG.ALL.MT.CE.AR5": ("Total Greenhouse Gas Emissions", "tonnes_CO2e", "down"),
    "EG.FEC.RNEW.ZS": ("Renewable Energy Share", "%", "up"),
    "EG.USE.PCAP.KG.OE": ("Energy Use per Capita", "count", "down"),
}

FRED_SERIES = {
    "CP": ("Finance", "Corporate Profits After Tax", "USD", "up"),
    "FEDFUNDS": ("Finance", "Federal Funds Effective Rate", "%", "down"),
    "CPIAUCSL": ("Finance", "Consumer Price Index", "index", "down"),
    "GDP": ("Finance", "Gross Domestic Product", "USD", "up"),
    "RSXFS": ("Growth", "Retail Sales", "USD", "up"),
    "ECOMSA": ("Growth", "E-Commerce Retail Sales", "USD", "up"),
    "UMCSENT": ("Growth", "Consumer Sentiment Index", "index", "up"),
    "UNRATE": ("People", "Unemployment Rate", "%", "down"),
    "JTSQUR": ("People", "Quits Rate", "%", "down"),
    "JTSJOL": ("People", "Job Openings", "count", "up"),
    "CES0500000003": ("People", "Average Hourly Earnings", "USD", "up"),
    "CES5051200001": ("IT", "Software Publishers Employment", "count", "up"),
    "CES6054150001": ("IT", "Computer Systems Design Employment", "count", "up"),
    "INDPRO": ("Operations", "Industrial Production Index", "index", "up"),
    "TCU": ("Operations", "Capacity Utilization", "%", "up"),
    "BUSINV": ("Logistics", "Business Inventories", "USD", "down"),
    "TSIFRGHTC": ("Logistics", "Freight Transportation Index", "index", "up"),
    "EMISSCO2TOTVTTTOUSA": ("ESG", "CO2 Emissions, Transport", "tonnes_CO2e", "down"),
}

CHART_IMAGES = {
    "Finance": ["CPIAUCSL", "FEDFUNDS"],
    "Growth": ["RSXFS"],
    "People": ["UNRATE"],
    "Operations": ["INDPRO"],
    "Logistics": ["TSIFRGHTC"],
}

DOC_EXT = {".pdf", ".txt", ".md", ".csv", ".json", ".xml", ".yaml", ".yml", ".tsv"}
IMG_EXT = {".png", ".jpg", ".jpeg", ".webp", ".tiff", ".bmp"}
AUDIO_EXT = {".mp3", ".wav", ".m4a", ".flac", ".ogg"}
SKIP_DIRS = {"real_kpis"}
CONTAINER_DIRS = {"kpi_digests"}
SKIP_PREFIXES = ("fred_", "worldbank_", "nvd_")


# ─────────────────────────────────────────────────────────────────────────────
# Stage 1: fetch — download raw published sources to data/<Domain>/
# ─────────────────────────────────────────────────────────────────────────────

def _get(url: str, tries: int = 4, timeout: int = 90) -> bytes:
    """requests, not urllib: on this network urllib's opener reliably times out
    against FRED while requests/curl both return 200 for the same URL."""
    last = None
    for attempt in range(tries):
        try:
            r = requests.get(url, headers={"User-Agent": "IntelAI-data/1.0"}, timeout=timeout)
            if r.status_code != 200:
                raise RuntimeError(f"HTTP {r.status_code}")
            return r.content
        except Exception as e:  # noqa: BLE001 - retried below, reported if final
            last = e
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"failed after {tries} tries: {last}")


def stage_fetch(refetch: bool, dry_run: bool) -> int:
    print("== fetch: FRED ==")
    for domain, series in FRED_CATALOG.items():
        outdir = DATA / domain
        outdir.mkdir(parents=True, exist_ok=True)
        for sid, (name, unit) in series.items():
            dest = outdir / f"fred_{sid}.csv"
            if dest.exists() and not refetch:
                print(f"  -- {domain:11} {sid:22} cached")
                continue
            if dry_run:
                print(f"  [dry-run] would fetch {domain}/{sid}")
                continue
            try:
                raw = _get(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}")
            except RuntimeError as e:
                print(f"  !! {domain:11} {sid:22} {e}")
                continue
            rows = list(csv.reader(io.StringIO(raw.decode("utf-8"))))
            body = [r for r in rows[1:] if len(r) == 2 and r[1] not in ("", ".")]
            if not body:
                print(f"  !! {domain:11} {sid:22} no usable observations")
                continue
            dest.write_bytes(raw)
            print(f"  ok {domain:11} {sid:22} {len(body):>5} obs  {body[0][0]}..{body[-1][0]}  {name}")

    print("== fetch: World Bank (ESG) ==")
    outdir = DATA / "ESG"
    outdir.mkdir(parents=True, exist_ok=True)
    for code, name in WORLDBANK_INDICATORS.items():
        dest = outdir / f"worldbank_{code}.json"
        if dest.exists() and not refetch:
            print(f"  -- {code:24} cached")
            continue
        if dry_run:
            print(f"  [dry-run] would fetch worldbank/{code}")
            continue
        url = (f"https://api.worldbank.org/v2/country/all/indicator/{code}"
               f"?format=json&per_page=20000&date=2015:2024")
        try:
            payload = json.loads(_get(url, tries=3, timeout=90))
        except (RuntimeError, json.JSONDecodeError) as e:
            print(f"  !! {code:24} {e}")
            continue
        records = payload[1] if isinstance(payload, list) and len(payload) > 1 else []
        usable = [r for r in records if r.get("value") is not None]
        if not usable:
            print(f"  !! {code:24} no observations")
            continue
        dest.write_text(json.dumps(payload))
        print(f"  ok {code:24} {len(usable):>6} obs  {name}")

    print("== fetch: NVD (IT) ==")
    nvd_dest = DATA / "IT" / "nvd_cves_dated.json"
    if nvd_dest.exists() and not refetch:
        print("  -- cached")
    elif dry_run:
        print("  [dry-run] would fetch NVD CVE sample")
    else:
        _fetch_nvd(nvd_dest)

    print("== fetch: FRED chart images ==")
    for domain, series in CHART_IMAGES.items():
        outdir = DATA / domain
        outdir.mkdir(parents=True, exist_ok=True)
        for sid in series:
            dest = outdir / f"fred_chart_{sid}.png"
            if dest.exists() and not refetch:
                print(f"  -- {domain:11} {sid:14} cached")
                continue
            if dry_run:
                print(f"  [dry-run] would fetch chart {domain}/{sid}")
                continue
            try:
                raw = _get(f"https://fred.stlouisfed.org/graph/fredgraph.png?id={sid}")
            except RuntimeError as e:
                print(f"  !! {domain:11} {sid:14} {e}")
                continue
            if not raw.startswith(b"\x89PNG"):
                print(f"  !! {domain:11} {sid:14} not a PNG")
                continue
            dest.write_bytes(raw)
            print(f"  ok {domain:11} {sid:14} {len(raw):>7} bytes")
    return 0


def _date_windows(start: date, end: date, span_days: int) -> list[tuple[str, str]]:
    out, cur = [], start
    while cur <= end:
        stop = min(cur + timedelta(days=span_days - 1), end)
        out.append((cur.isoformat(), stop.isoformat()))
        cur = stop + timedelta(days=1)
    return out


def _fetch_nvd(dest: Path, per_window: int = 400) -> None:
    """A real, dated sample of published CVEs — comparable between months only
    because every window is sampled identically; the stored metric is named
    "Published CVEs (sampled)" for that reason, not the full population."""
    base = ("https://services.nvd.nist.gov/rest/json/cves/2.0"
            "?pubStartDate={start}T00:00:00.000&pubEndDate={end}T23:59:59.999"
            "&resultsPerPage={per}&startIndex={idx}")
    windows = _date_windows(date(2025, 1, 1), date.today(), span_days=90)
    collected: list[dict] = []
    for start, end in windows:
        got_here, idx = 0, 0
        while got_here < per_window:
            per = min(per_window - got_here, 2000)
            url = base.format(start=start, end=end, per=per, idx=idx)
            try:
                payload = json.loads(_get(url, tries=3, timeout=90))
            except RuntimeError as e:
                print(f"  !! NVD {start}..{end} idx={idx}: {e}")
                break
            vulns = payload.get("vulnerabilities", [])
            collected.extend(vulns)
            got_here += len(vulns)
            total = payload.get("totalResults", 0)
            print(f"  ok NVD {start}..{end} idx={idx:>5} got {len(vulns):>4} ({got_here}/{per_window} of {total})")
            idx += per
            if idx >= total or not vulns:
                break
            time.sleep(6)
        time.sleep(6)
    if collected:
        dest.write_text(json.dumps({"vulnerabilities": collected}, indent=1))
    print(f"  total {len(collected)} CVEs collected")


# ─────────────────────────────────────────────────────────────────────────────
# Stage 2: build — raw sources -> per-domain CSVs in data/real_kpis/
# ─────────────────────────────────────────────────────────────────────────────

LEGACY_ALIASES = {
    "INDPRO": "Operations/fred_industrial_production_index.csv",
    "TCU": "Operations/fred_capacity_utilization.csv",
    "BUSINV": "Logistics/fred_business_inventories.csv",
    "TSIFRGHTC": "Logistics/fred_freight_transportation_index.csv",
}


def _find_fred_csv(sid: str) -> Optional[Path]:
    hits = list(DATA.glob(f"*/fred_{sid}.csv"))
    if hits:
        return hits[0]
    alias = LEGACY_ALIASES.get(sid)
    if alias and (DATA / alias).exists():
        return DATA / alias
    return None


def _from_fred(since: str) -> list[dict]:
    rows: list[dict] = []
    for sid, (domain, metric, unit, direction) in FRED_SERIES.items():
        path = _find_fred_csv(sid)
        if path is None:
            print(f"  -- {sid:22} MISSING (not downloaded)")
            continue
        kept = 0
        with path.open() as fh:
            for rec in csv.reader(fh):
                if len(rec) != 2 or rec[0] == "observation_date" or rec[1] in ("", "."):
                    continue
                period = rec[0][:7]
                if period < since:
                    continue
                try:
                    value = float(rec[1])
                except ValueError:
                    continue
                rows.append({
                    "period": period, "category": domain, "segment": EXTERNAL_MARKET_SEGMENT,
                    "metric_name": metric, "value": value, "unit": unit,
                    "direction": direction, "source": f"fred:{sid}",
                })
                kept += 1
        print(f"  ok {sid:22} {kept:>4} obs >= {since}  {domain}/{metric}")
    return rows


def _from_worldbank() -> list[dict]:
    esg = DATA / "ESG"
    paths = sorted(set(esg.glob("worldbank_*.json")))
    rows: list[dict] = []
    seen: set[tuple] = set()
    for path in paths:
        try:
            payload = json.loads(path.read_text())
        except json.JSONDecodeError:
            print(f"  !! {path.name} unreadable")
            continue
        records = payload[1] if isinstance(payload, list) and len(payload) > 1 else []
        kept = 0
        for rec in records:
            if rec.get("value") is None or rec["country"]["value"] not in WORLDBANK_SEGMENTS:
                continue
            code = rec["indicator"]["id"]
            metric, unit, direction = WORLDBANK_METRICS.get(
                code, (rec["indicator"]["value"][:60], "count", "down"))
            key = (code, rec["country"]["value"], rec["date"])
            if key in seen:
                continue
            seen.add(key)
            rows.append({
                "period": f"{rec['date']}-01", "category": "ESG",
                "segment": rec["country"]["value"], "metric_name": metric,
                "value": float(rec["value"]), "unit": unit, "direction": direction,
                "source": f"worldbank:{code}",
            })
            kept += 1
        print(f"  ok {path.name:38} {kept:>5} obs")
    return rows


def _from_nvd() -> list[dict]:
    candidates = [DATA / "IT" / "nvd_cves_dated.json", DATA / "IT" / "nvd_recent_cves.json",
                  DATA / "IT" / "nvd_critical_cves.json"]
    vulns: list[dict] = []
    used = []
    for path in candidates:
        if path.exists():
            vulns.extend(json.loads(path.read_text()).get("vulnerabilities", []))
            used.append(path.name)
    if not vulns:
        print("  -- NVD MISSING")
        return []
    seen: set[str] = set()
    per_month: Counter = Counter()
    per_month_sev: dict[tuple[str, str], int] = defaultdict(int)
    per_month_cvss: dict[str, list[float]] = defaultdict(list)
    for item in vulns:
        cve = item.get("cve", item)
        cid = cve.get("id")
        if not cid or cid in seen:
            continue
        seen.add(cid)
        published = cve.get("published", "")
        if len(published) < 7:
            continue
        month = published[:7]
        per_month[month] += 1
        metrics = cve.get("metrics", {})
        sev = None
        score = None
        for key in ("cvssMetricV31", "cvssMetricV40", "cvssMetricV2"):
            entries = metrics.get(key) or []
            if entries:
                d = entries[0].get("cvssData", {})
                sev = d.get("baseSeverity") or entries[0].get("baseSeverity")
                score = d.get("baseScore")
                if sev:
                    break
        if sev:
            per_month_sev[(month, sev.capitalize())] += 1
        if isinstance(score, (int, float)):
            per_month_cvss[month].append(float(score))
    rows = [{
        "period": m, "category": "IT", "segment": "Global",
        "metric_name": "Published CVEs (sampled)", "value": float(n), "unit": "count",
        "direction": "down", "source": "nvd:cve-2.0",
    } for m, n in sorted(per_month.items())]
    rows += [{
        "period": m, "category": "IT", "segment": "Global",
        "metric_name": f"Published CVEs (sampled) — {sev} Severity", "value": float(n),
        "unit": "count", "direction": "down", "source": "nvd:cve-2.0",
    } for (m, sev), n in sorted(per_month_sev.items())]
    # Security Score: inverted average real CVSS base score for that month's published
    # CVEs (0-10, higher=more severe) rescaled to 0-100 where higher=better — a standard
    # "security posture index" convention, computed purely from real published NVD scores,
    # not invented. Feeds ITOpsService's "security score"/"security rating" keyword match.
    rows += [{
        "period": m, "category": "IT", "segment": "Global",
        "metric_name": "Security Score", "value": round((10.0 - sum(scores) / len(scores)) * 10.0, 2),
        "unit": "/100", "direction": "up", "source": "nvd:cve-2.0",
    } for m, scores in sorted(per_month_cvss.items()) if scores]
    print(f"  ok NVD ({'+'.join(used)}) {len(seen)} unique CVEs -> {len(rows)} rows over {len(per_month)} months")
    return rows


def _ibm_hr_aggregates(records: list[dict], segment: str, period: str) -> list[dict]:
    """Real per-employee IBM HR Analytics fields, reduced to honest aggregates for one
    group (company-wide or one department) — no invented numbers, only counts/averages
    computed directly from the real records. Two are deliberately reframed (not
    fabricated) to match fields the HR service/frontend already expect:
      - Job Satisfaction Score: the dataset's real 1-4 Likert scale, min-max rescaled to
        0-100 (documented linear transform, same real per-employee responses) so it's
        meaningful next to a UI label that reads "/100".
      - Training Completion Rate: % of employees with >=1 training session last year —
        a real, directly-computed percentage from TrainingTimesLastYear, relabeled from
        "participation" to "completion" since the dataset has no finer completion signal
        than "did/didn't train"; still the real per-employee count, not invented.
    """
    n = len(records)
    if n == 0:
        return []
    attrition = sum(1 for r in records if (r.get("Attrition") or "").strip().lower() == "yes")
    trained = sum(1 for r in records if (r.get("TrainingTimesLastYear") or "0").strip() not in ("", "0"))

    def _avg(field: str) -> Optional[float]:
        vals = []
        for r in records:
            try:
                vals.append(float(r[field]))
            except (KeyError, TypeError, ValueError):
                continue
        return sum(vals) / len(vals) if vals else None

    out = [
        {"period": period, "category": "People", "segment": segment,
         "metric_name": "Headcount", "value": float(n), "unit": "count",
         "direction": "up", "source": "ibm-hr:attrition-survey"},
        {"period": period, "category": "People", "segment": segment,
         "metric_name": "Attrition Rate", "value": round(100.0 * attrition / n, 2),
         "unit": "%", "direction": "down", "source": "ibm-hr:attrition-survey"},
        {"period": period, "category": "People", "segment": segment,
         "metric_name": "Training Completion Rate", "value": round(100.0 * trained / n, 2),
         "unit": "%", "direction": "up", "source": "ibm-hr:attrition-survey"},
    ]
    js = _avg("JobSatisfaction")
    if js is not None:
        rescaled = round((js - 1.0) / 3.0 * 100.0, 2)  # real 1-4 Likert -> 0-100
        out.append({"period": period, "category": "People", "segment": segment,
                     "metric_name": "Job Satisfaction Score", "value": rescaled,
                     "unit": "/100", "direction": "up", "source": "ibm-hr:attrition-survey"})
    for field, metric, unit, direction in [
        ("MonthlyIncome", "Average Monthly Income", "USD", "up"),
        ("MonthlyIncome", "Average Salary", "USD", "up"),  # same real figure, relabeled to match the "salary" keyword the department table matches on
        ("YearsAtCompany", "Average Tenure", "count", "up"),
        ("Age", "Average Employee Age", "count", "up"),
    ]:
        v = _avg(field)
        if v is not None:
            out.append({
                "period": period, "category": "People", "segment": segment,
                "metric_name": metric, "value": round(v, 2), "unit": unit,
                "direction": direction, "source": "ibm-hr:attrition-survey",
            })
    return out


def _from_ibm_hr() -> list[dict]:
    path = DATA / "People" / "ibm_hr_attrition.csv"
    if not path.exists():
        print("  -- IBM HR MISSING")
        return []
    with path.open(encoding="utf-8-sig") as fh:
        records = list(csv.DictReader(fh))
    if not records:
        return []

    period = "2024-01"
    out = _ibm_hr_aggregates(records, "IBM Sample", period)

    # Real per-department breakdown — the same real employee records, grouped by their
    # actual Department column, not a separate/invented dataset. Feeds the HR page's
    # department table, which previously had nothing to group by at this granularity.
    by_dept: dict[str, list[dict]] = defaultdict(list)
    for r in records:
        d = (r.get("Department") or "").strip()
        if d:
            by_dept[d].append(r)
    for dept, dept_records in by_dept.items():
        out += _ibm_hr_aggregates(dept_records, dept, period)

    print(f"  ok IBM HR survey         {len(out):>4} aggregates from {len(records)} employees "
          f"across {len(by_dept)} departments (cross-section, single period)")
    return out


def _from_sonatel() -> list[dict]:
    """The one real per-company data source in this corpus — Sonatel/Orange
    Group's own published result communiqués, in FCFA, the company's Finance
    anchor and the source of its West African identity."""
    path = DATA / "Finance" / "sonatel_resultats_fcfa_verified.md"
    if not path.exists():
        print("  -- Sonatel MISSING")
        return []
    rows = [
        {"period": "2025-06", "category": "Finance", "segment": "Sonatel Group",
         "metric_name": "Chiffre d'affaires", "value": 960.2e9, "unit": "FCFA",
         "direction": "up", "source": "sonatel:s1-2025"},
        {"period": "2025-06", "category": "Finance", "segment": "Sonatel Group",
         "metric_name": "EBITDAaL", "value": 458.0e9, "unit": "FCFA",
         "direction": "up", "source": "sonatel:s1-2025"},
        {"period": "2025-09", "category": "Finance", "segment": "Sonatel Group",
         "metric_name": "Chiffre d'affaires", "value": 1432.5e9, "unit": "FCFA",
         "direction": "up", "source": "sonatel:9m-2025"},
    ]
    print(f"  ok Sonatel (FCFA)        {len(rows):>4} published figures")
    return rows


def _from_bls_safety() -> list[dict]:
    """Real, published U.S. Bureau of Labor Statistics / OSHA annual Survey of
    Occupational Injuries and Illnesses — Total Recordable Case (TRC) rate per 100
    full-time-equivalent private-industry workers. External market context (same
    framing as FRED), not this company's own measured safety record — OperationsService
    has no field distinguishing "our own" from "external benchmark" data, so this is
    used the same way FRED's national Job Openings figure already stands in for
    People's open_positions. Two metric names carry the identical real annual figure
    (singular/plural) because OperationsService's several safety-related endpoints
    each match on a slightly different literal substring ("safety incident" vs
    "safety incidents", "total recordable" vs "total incidents") — not two different
    numbers, the same one twice under both wordings so real substring-keyword matching
    actually finds it instead of falling back to zero everywhere the wording differs.
    Source: BLS/OSHA Survey of Occupational Injuries and Illnesses annual releases,
    https://www.bls.gov/iif/ — 2020-2022 releases (all 2.7), osh_04182024 (2023: 2.4),
    OSHA news release 2025-04-17 (2024: 2.3)."""
    series = {"2020-12": 2.7, "2021-12": 2.7, "2022-12": 2.7, "2023-12": 2.4, "2024-12": 2.3}
    rows = []
    for period, rate in series.items():
        for metric_name in ("Total Recordable Safety Incident Rate", "Total Safety Incidents Rate"):
            rows.append({
                "period": period, "category": "Operations", "segment": "External — US Safety Benchmark",
                "metric_name": metric_name, "value": rate, "unit": "per 100 FTE",
                "direction": "down", "source": "bls-osha:osh-annual-survey",
            })
    print(f"  ok BLS/OSHA safety        {len(rows):>4} rows ({len(series)} years, private industry TRC rate)")
    return rows


def _from_logistics_benchmark() -> list[dict]:
    """One real, published, cross-industry supply-chain benchmark figure — global
    median inventory turnover ratio, 2025, from Netstock's 2025 State of Supply Chain
    Planning benchmark report. External market context, same framing as the other
    benchmark sources in this pipeline, not this company's own measured turnover."""
    rows = [
        {"period": "2025-12", "category": "Logistics", "segment": "External — Supply Chain Benchmark",
         "metric_name": "Inventory Turnover", "value": 3.9, "unit": "x/year",
         "direction": "up", "source": "netstock:2025-supply-chain-planning-report"},
    ]
    print(f"  ok Logistics benchmark    {len(rows):>4} row (median inventory turnover, 2025)")
    return rows


def _from_saas_benchmark() -> list[dict]:
    """One real, published, cross-industry SaaS benchmark figure — median revenue
    churn rate, 2025, from an aggregate report synthesizing 2,000+ SaaS companies
    (Benchmarkit 2025 SaaS Performance Metrics; corroborated by High Alpha's 2025 SaaS
    Benchmarks Report). External market context, not this company's own measured churn
    — same framing as FRED/BLS elsewhere in this pipeline. Deliberately does NOT
    include MRR/ARR/CAC/LTV: those are absolute dollar figures, and no real external
    benchmark can honestly stand in for a specific company's own revenue/cost scale
    the way a rate or percentage can — inventing a plausible-looking dollar amount
    would be fabrication, not sourced data, so those fields are left as an honest gap
    rather than filled with an invented number."""
    rows = [
        {"period": "2024-12", "category": "Growth", "segment": "External — SaaS Industry Benchmark",
         "metric_name": "Churn Rate", "value": 11.34, "unit": "%",
         "direction": "down", "source": "benchmarkit:2025-saas-performance-metrics"},
        {"period": "2025-12", "category": "Growth", "segment": "External — SaaS Industry Benchmark",
         "metric_name": "Churn Rate", "value": 12.50, "unit": "%",
         "direction": "down", "source": "benchmarkit:2025-saas-performance-metrics"},
    ]
    print(f"  ok SaaS benchmark         {len(rows):>4} rows (median revenue churn, 2024-2025)")
    return rows


def stage_build(since: str, dry_run: bool) -> int:
    print("== build: FRED ==")
    rows = _from_fred(since)
    print("== build: World Bank ==")
    rows += _from_worldbank()
    print("== build: NVD ==")
    rows += _from_nvd()
    print("== build: IBM HR ==")
    rows += _from_ibm_hr()
    print("== build: Sonatel ==")
    rows += _from_sonatel()
    print("== build: BLS/OSHA safety ==")
    rows += _from_bls_safety()
    print("== build: SaaS benchmark ==")
    rows += _from_saas_benchmark()
    print("== build: Logistics benchmark ==")
    rows += _from_logistics_benchmark()

    if dry_run:
        print(f"[dry-run] would write {len(rows)} rows across "
              f"{len({r['category'] for r in rows})} domains")
        return 0 if rows else 1

    outdir = DATA / "real_kpis"
    outdir.mkdir(parents=True, exist_ok=True)
    for f in outdir.glob("*.csv"):
        f.unlink()

    by_domain: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_domain[r["category"]].append(r)

    print("== written ==")
    for domain, drows in sorted(by_domain.items()):
        dest = outdir / f"{domain.lower()}_real.csv"
        with dest.open("w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=CSV_COLUMNS)
            w.writeheader()
            w.writerows(drows)
        metrics = len({r["metric_name"] for r in drows})
        periods = len({r["period"] for r in drows})
        print(f"  {domain:11} {len(drows):>6} rows  {metrics:>3} metrics  {periods:>3} periods -> "
              f"{dest.relative_to(ROOT)}")

    print(f"\ntotal {len(rows)} rows across {len(by_domain)} domains")
    print("provenance:", dict(Counter(r["source"].split(":")[0] for r in rows)))
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
        headers["X-OmniIntel-Internal-Token"] = INTERNAL_TOKEN
    return headers


# ─────────────────────────────────────────────────────────────────────────────
# Stage 3: seed-kpis — POST each CSV to /api/v1/ingest/csv
# ─────────────────────────────────────────────────────────────────────────────

def stage_seed_kpis(dry_run: bool, purge: bool = False) -> int:
    srcdir = DATA / "real_kpis"
    files = sorted(srcdir.glob("*_real.csv"))
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
    "fred": "https://fred.stlouisfed.org/series/{sid}",
    "worldbank": "https://data.worldbank.org/indicator/{sid}",
    "nvd": "https://nvd.nist.gov/vuln/search",
    "ibm-hr": "IBM HR Analytics Employee Attrition dataset",
    "sonatel": "https://sonatel.sn (communiqués de résultats)",
    "bls-osha": "https://www.bls.gov/iif/ (Survey of Occupational Injuries and Illnesses)",
    "benchmarkit": "https://www.benchmarkit.ai/2025benchmarks",
    "netstock": "https://www.netstock.com/research/supply-chain-planning-report/",
}

LABELS = {
    "en": {
        "title": "{domain} — Real KPI Digest ({period})",
        "intro": ("Recorded values for {domain} metrics in {period}. Each figure is "
                   "reproduced exactly as published by its source; the source identifier "
                   "follows each line."),
        "series": "Series covered",
        "sources": "Sources",
        "external_note": ("Rows marked external / market-context are published statistics this "
                           "West African operator tracks as planning context (US/global rates, "
                           "employment, demand) — they are not this company's own measured output."),
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
        "external_note": ("Les lignes marquées contexte externe / marché sont des statistiques "
                           "publiées que cet opérateur ouest-africain suit à titre de contexte de "
                           "planification (taux américains/mondiaux, emploi, demande) — elles ne "
                           "représentent pas la performance propre de l'entreprise."),
        "note": ("Il s'agit d'observations issues de séries statistiques publiées, et non "
                  "d'objectifs, de prévisions ou de comptes internes."),
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
    from src.services.pg_store import _get_conn

    conn = _get_conn()
    with conn.cursor() as c:
        # owner_user_id IS NULL only — this writes a document into the SHARED
        # knowledge base, so a query with no scope filter here would bake any
        # user's own privately-uploaded rows into text every other visitor's
        # chat can retrieve. Confirmed live: a leftover single-row test fixture
        # scoped to one throwaway user_id ended up in a real digest document
        # before this filter existed.
        c.execute("""SELECT period, category, metric, value, unit, segment, source
                     FROM kpi_metrics WHERE owner_user_id IS NULL
                     ORDER BY category, period, metric""")
        rows = [dict(r) for r in c.fetchall()]
    conn.close()
    if not rows:
        print("kpi_metrics is empty — run --only seed-kpis first")
        return 1

    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in rows:
        grouped[(r["category"], r["period"])].append(r)

    per_domain: dict[str, list[str]] = defaultdict(list)
    for domain, period in grouped:
        per_domain[domain].append(period)
    keep = {(d, p) for d, ps in per_domain.items() for p in sorted(ps)[-months:]}

    # A sparse source (a handful of real published data points — a survey cross-section,
    # a one-off benchmark report) contributes to only a few periods total. Mixed into a
    # domain that also carries a long continuous monthly series (FRED runs 90+ months),
    # the windowing above silently squeezes its one real period out — no digest document
    # ever gets written for it, so the data is correctly seeded and API-queryable but
    # unreachable through chat/RAG. Confirmed live: the IBM HR survey's real
    # per-department breakdown existed in kpi_metrics but had no digest at all, so a
    # natural-language question about it retrieved raw, unaggregated CSV rows instead
    # and produced a materially wrong answer. Any source contributing to <=6 distinct
    # periods anywhere is treated as sparse and kept in full, regardless of recency.
    by_source_periods: dict[str, set[str]] = defaultdict(set)
    for r in rows:
        by_source_periods[r["source"]].add(r["period"])
    keep |= {(r["category"], r["period"]) for r in rows if len(by_source_periods[r["source"]]) <= 6}

    out = DATA / "kpi_digests"
    if dry_run:
        print(f"[dry-run] would write digests for {len(keep)} (domain, period) pairs to {out}")
        return 0

    out.mkdir(parents=True, exist_ok=True)
    for f in out.rglob("*.md"):
        f.unlink()

    written = 0
    for (domain, period), items in sorted(grouped.items()):
        if (domain, period) not in keep:
            continue
        has_external = any(r["segment"] == EXTERNAL_MARKET_SEGMENT for r in items)
        for lang in ("en", "fr"):
            L = LABELS[lang]
            lines = [f"# {L['title'].format(domain=domain, period=period)}", "",
                     L["intro"].format(domain=domain, period=period), "", f"## {L['series']}"]
            for r in sorted(items, key=lambda x: x["metric"]):
                name = FR_METRIC.get(r["metric"], r["metric"]) if lang == "fr" else r["metric"]
                seg = f" [{r['segment']}]" if r["segment"] else ""
                lines.append(f"- {name}{seg}: {_fmt(r['value'], r['unit'])}  (source: {r['source']})")
            lines.append("")
            lines.append(f"## {L['sources']}")
            for src in sorted({r["source"] for r in items}):
                lines.append(f"- {src} — {_source_url(src)}")
            lines.append("")
            if has_external:
                lines.append(L["external_note"])
                lines.append("")
            lines.append(L["note"])

            dest_dir = out / domain
            dest_dir.mkdir(parents=True, exist_ok=True)
            (dest_dir / f"{domain.lower()}_{period}_{lang}.md").write_text("\n".join(lines), encoding="utf-8")
            written += 1

    print(f"wrote {written} digest documents to {out}")
    return 0


# ─────────────────────────────────────────────────────────────────────────────
# Stage 5: corpus — POST real documents/images/audio + digests via the API
# ─────────────────────────────────────────────────────────────────────────────

def _is_raw_series(path: Path) -> bool:
    name = path.name.lower()
    if name.startswith("fred_chart_"):
        return False
    return name.startswith(SKIP_PREFIXES)


def _discover_corpus() -> list[tuple[Path, str, str]]:
    out = []
    roots: list[Path] = []
    for d in sorted(p for p in DATA.iterdir() if p.is_dir()):
        if d.name in SKIP_DIRS:
            continue
        if d.name in CONTAINER_DIRS:
            roots.extend(sorted(s for s in d.iterdir() if s.is_dir()))
        else:
            roots.append(d)
    for domain_dir in roots:
        for path in sorted(domain_dir.rglob("*")):
            if not path.is_file() or _is_raw_series(path):
                continue
            ext = path.suffix.lower()
            if ext in AUDIO_EXT:
                kind = "audio"
            elif ext in IMG_EXT:
                kind = "image"
            elif ext in DOC_EXT:
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
    "fetch": lambda a: stage_fetch(a.refetch, a.dry_run),
    "build": lambda a: stage_build(a.since, a.dry_run),
    "seed-kpis": lambda a: stage_seed_kpis(a.dry_run, a.purge),
    "digests": lambda a: stage_digests(a.months, a.dry_run),
    "corpus": lambda a: stage_corpus(a.purge, a.only_file, a.dry_run, a.timeout),
}
STAGE_ORDER = ["fetch", "build", "seed-kpis", "digests", "corpus"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", default="", help="comma-separated subset of: " + ",".join(STAGE_ORDER))
    ap.add_argument("--refetch", action="store_true", help="re-download raw sources even if cached")
    ap.add_argument("--since", default="2019-01", help="earliest period to keep from long-running series")
    ap.add_argument("--months", type=int, default=18, help="recent periods per domain in digests")
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
