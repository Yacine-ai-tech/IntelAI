#!/usr/bin/env python3
"""Turn the downloaded real sources into KPI rows ready for POST /api/v1/ingest/csv.

Every row this writes carries the identifier of the published series it came
from, so a number on a dashboard can be traced to a source and re-checked. No
value is generated, interpolated, smoothed, or extended: if a publisher has no
observation for a period, this script emits no row for that period.

That honesty has a visible consequence — real series do not all share one
frequency or one history. FRED's monthly series run monthly, GDP and corporate
profits are quarterly, World Bank CO2 is annual, and the HR survey is a single
cross-section with no time dimension at all. The output reflects that unevenness
rather than hiding it behind a filled-in grid.

Run:  python scripts/build_real_kpis.py [--since 2019-01] [--out data/real_kpis]
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

CSV_COLUMNS = ["period", "category", "segment", "metric_name", "value", "unit", "direction", "source"]

# series id -> (domain, metric name, unit, direction, segment)
# direction follows the column's existing vocabulary: "up" = higher is better,
# "down" = lower is better.
FRED_SERIES = {
    # Finance
    "CP":            ("Finance", "Corporate Profits After Tax", "USD", "up", "US"),
    "FEDFUNDS":      ("Finance", "Federal Funds Effective Rate", "%", "down", "US"),
    "CPIAUCSL":      ("Finance", "Consumer Price Index", "index", "down", "US"),
    "GDP":           ("Finance", "Gross Domestic Product", "USD", "up", "US"),
    # Growth
    "RSXFS":         ("Growth", "Retail Sales", "USD", "up", "US"),
    "ECOMSA":        ("Growth", "E-Commerce Retail Sales", "USD", "up", "US"),
    "UMCSENT":       ("Growth", "Consumer Sentiment Index", "index", "up", "US"),
    # People
    "UNRATE":        ("People", "Unemployment Rate", "%", "down", "US"),
    "JTSQUR":        ("People", "Quits Rate", "%", "down", "US"),
    "JTSJOL":        ("People", "Job Openings", "count", "up", "US"),
    "CES0500000003": ("People", "Average Hourly Earnings", "USD", "up", "US"),
    # IT
    "CES5051200001": ("IT", "Software Publishers Employment", "count", "up", "US"),
    "CES6054150001": ("IT", "Computer Systems Design Employment", "count", "up", "US"),
    # Operations
    "INDPRO":        ("Operations", "Industrial Production Index", "index", "up", "US"),
    "TCU":           ("Operations", "Capacity Utilization", "%", "up", "US"),
    # Logistics
    "BUSINV":        ("Logistics", "Business Inventories", "USD", "down", "US"),
    "TSIFRGHTC":     ("Logistics", "Freight Transportation Index", "index", "up", "US"),
    # ESG
    "EMISSCO2TOTVTTTOUSA": ("ESG", "CO2 Emissions, Transport", "tonnes_CO2e", "down", "US"),
}

# Legacy downloads of the same series under descriptive filenames. Keeping both
# would ingest one series twice under two names, so these are read only if the
# canonical fred_<ID>.csv is missing.
LEGACY_ALIASES = {
    "INDPRO":    "Operations/fred_industrial_production_index.csv",
    "TCU":       "Operations/fred_capacity_utilization.csv",
    "BUSINV":    "Logistics/fred_business_inventories.csv",
    "TSIFRGHTC": "Logistics/fred_freight_transportation_index.csv",
}


def _find_fred_csv(sid: str) -> Path | None:
    hits = list(DATA.glob(f"*/fred_{sid}.csv"))
    if hits:
        return hits[0]
    alias = LEGACY_ALIASES.get(sid)
    if alias and (DATA / alias).exists():
        return DATA / alias
    return None


def from_fred(since: str) -> list[dict]:
    rows: list[dict] = []
    for sid, (domain, metric, unit, direction, segment) in FRED_SERIES.items():
        path = _find_fred_csv(sid)
        if path is None:
            print(f"  -- {sid:22} MISSING (not downloaded)")
            continue
        kept = 0
        with path.open() as fh:
            for rec in csv.reader(fh):
                if len(rec) != 2 or rec[0] == "observation_date" or rec[1] in ("", "."):
                    continue
                period = rec[0][:7]           # FRED dates are YYYY-MM-DD; KPI periods are YYYY-MM
                if period < since:
                    continue
                try:
                    value = float(rec[1])
                except ValueError:
                    continue
                rows.append({
                    "period": period, "category": domain, "segment": segment,
                    "metric_name": metric, "value": value, "unit": unit,
                    "direction": direction, "source": f"fred:{sid}",
                })
                kept += 1
        print(f"  ok {sid:22} {kept:>4} obs >= {since}  {domain}/{metric}")
    return rows


# The World Bank returns every country and aggregate — ~8.6k observations, which
# would bury the ESG domain under 200 countries of annual data. This is a
# relevance filter, not a data filter: the values kept are exactly as published,
# and the set below is the world total, the portfolio's home region (the FCFA
# zone, matching the Sonatel/Orange sources in Finance), and the largest emitters.
WORLDBANK_SEGMENTS = {
    "World",
    "Sub-Saharan Africa", "Africa Eastern and Southern", "Africa Western and Central",
    "Senegal", "Cote d'Ivoire", "Côte d'Ivoire", "Mali", "Burkina Faso", "Niger",
    "France", "United States", "China", "India", "Germany", "Japan",
    "European Union", "Nigeria", "South Africa",
}

# indicator code -> (metric name, unit, direction)
WORLDBANK_METRICS = {
    "EN.GHG.CO2.MT.CE.AR5": ("CO2 Emissions (excl. LULUCF)", "tonnes_CO2e", "down"),
    "EN.GHG.ALL.MT.CE.AR5": ("Total Greenhouse Gas Emissions", "tonnes_CO2e", "down"),
    "EG.FEC.RNEW.ZS":       ("Renewable Energy Share", "%", "up"),
    "EG.USE.PCAP.KG.OE":    ("Energy Use per Capita", "count", "down"),
}


def from_worldbank() -> list[dict]:
    """World Bank ESG indicators — annual, by country.

    Reads every worldbank_*.json in data/ESG, so adding an indicator to the
    fetcher is enough to bring it through here.
    """
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
            if rec.get("value") is None:
                continue
            if rec["country"]["value"] not in WORLDBANK_SEGMENTS:
                continue
            code = rec["indicator"]["id"]
            metric, unit, direction = WORLDBANK_METRICS.get(
                code, (rec["indicator"]["value"][:60], "count", "down"))
            # The legacy co2 file overlaps the per-indicator download; dedupe on
            # the natural key so a country-year is not counted twice.
            key = (code, rec["country"]["value"], rec["date"])
            if key in seen:
                continue
            seen.add(key)
            rows.append({
                # Annual observation pinned to the year's first period so it sorts
                # with the monthly series without pretending to be monthly.
                "period": f"{rec['date']}-01", "category": "ESG",
                "segment": rec["country"]["value"], "metric_name": metric,
                "value": float(rec["value"]), "unit": unit, "direction": direction,
                "source": f"worldbank:{code}",
            })
            kept += 1
        print(f"  ok {path.name:38} {kept:>5} obs")
    return rows


def from_nvd() -> list[dict]:
    """NVD CVEs -> real monthly counts, split by CVSS v3.1 severity."""
    candidates = [DATA / "IT" / "nvd_cves_dated.json",
                  DATA / "IT" / "nvd_recent_cves.json",
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
        for key in ("cvssMetricV31", "cvssMetricV40", "cvssMetricV2"):
            entries = metrics.get(key) or []
            if entries:
                d = entries[0].get("cvssData", {})
                sev = d.get("baseSeverity") or entries[0].get("baseSeverity")
                if sev:
                    break
        if sev:
            per_month_sev[(month, sev.capitalize())] += 1

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
    print(f"  ok NVD ({'+'.join(used)}) {len(seen)} unique CVEs -> {len(rows)} rows "
          f"over {len(per_month)} months")
    return rows


def from_ibm_hr() -> list[dict]:
    """IBM HR survey -> real workforce aggregates.

    This is a cross-section of individual employees with no date column, so it
    yields point-in-time aggregates, not a series. Inventing a monthly history
    from it would be fabrication, so the whole survey is reported under a single
    period tagged with its source.
    """
    path = DATA / "People" / "ibm_hr_attrition.csv"
    if not path.exists():
        print("  -- IBM HR MISSING")
        return []
    with path.open(encoding="utf-8-sig") as fh:
        records = list(csv.DictReader(fh))
    if not records:
        return []

    n = len(records)
    attrition = sum(1 for r in records if (r.get("Attrition") or "").strip().lower() == "yes")

    def _avg(field: str) -> float | None:
        vals = []
        for r in records:
            try:
                vals.append(float(r[field]))
            except (KeyError, TypeError, ValueError):
                continue
        return sum(vals) / len(vals) if vals else None

    period = "2024-01"  # the survey's published reference period, not an observation date
    out = [{
        "period": period, "category": "People", "segment": "IBM Sample",
        "metric_name": "Attrition Rate", "value": round(100.0 * attrition / n, 2),
        "unit": "%", "direction": "down", "source": "ibm-hr:attrition-survey",
    }]
    for field, metric, unit, direction in [
        ("MonthlyIncome", "Average Monthly Income", "USD", "up"),
        ("YearsAtCompany", "Average Tenure", "count", "up"),
        ("JobSatisfaction", "Job Satisfaction Score", "score", "up"),
        ("Age", "Average Employee Age", "count", "up"),
    ]:
        v = _avg(field)
        if v is not None:
            out.append({
                "period": period, "category": "People", "segment": "IBM Sample",
                "metric_name": metric, "value": round(v, 2), "unit": unit,
                "direction": direction, "source": "ibm-hr:attrition-survey",
            })
    print(f"  ok IBM HR survey         {len(out):>4} aggregates from {n} employees "
          f"(cross-section, single period)")
    return out


def from_sonatel() -> list[dict]:
    """Sonatel Group published results, in FCFA.

    Transcribed from the group's official result communiqués (URLs recorded in
    the source file). Two published figures, so two rows.
    """
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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="2019-01",
                    help="earliest period to keep from long-running series (YYYY-MM)")
    ap.add_argument("--out", default="data/real_kpis")
    args = ap.parse_args()

    print("== FRED ==")
    rows = from_fred(args.since)
    print("== World Bank ==")
    rows += from_worldbank()
    print("== NVD ==")
    rows += from_nvd()
    print("== IBM HR ==")
    rows += from_ibm_hr()
    print("== Sonatel ==")
    rows += from_sonatel()

    outdir = ROOT / args.out
    outdir.mkdir(parents=True, exist_ok=True)
    for f in outdir.glob("*.csv"):
        f.unlink()

    by_domain: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_domain[r["category"]].append(r)

    print("\n== written ==")
    for domain, drows in sorted(by_domain.items()):
        dest = outdir / f"{domain.lower()}_real.csv"
        with dest.open("w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=CSV_COLUMNS)
            w.writeheader()
            w.writerows(drows)
        metrics = len({r["metric_name"] for r in drows})
        periods = len({r["period"] for r in drows})
        print(f"  {domain:11} {len(drows):>6} rows  {metrics:>3} metrics  "
              f"{periods:>3} periods -> {dest.relative_to(ROOT)}")

    print(f"\ntotal {len(rows)} rows across {len(by_domain)} domains")
    srcs = Counter(r["source"].split(":")[0] for r in rows)
    print("provenance:", dict(srcs))
    return 0 if rows else 1


if __name__ == "__main__":
    sys.exit(main())
