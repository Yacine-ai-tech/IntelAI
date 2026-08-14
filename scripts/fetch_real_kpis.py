#!/usr/bin/env python3
"""Download the real, public time series that back IntelAI's KPI layer.

Every series here is a published statistical series with a stable public
identifier, so any number in the database can be traced back to its origin and
re-checked by a third party. Nothing in this file generates, extrapolates, or
smooths a value: what the publisher released is what gets stored.

Sources
  FRED (Federal Reserve Bank of St. Louis)  https://fred.stlouisfed.org/series/<ID>
  World Bank Open Data                      https://data.worldbank.org
  NVD (NIST National Vulnerability Database) https://nvd.nist.gov

Run:  python scripts/fetch_real_kpis.py
"""
from __future__ import annotations

import csv
import io
import json
import os
import sys
import time
from datetime import date, timedelta
from pathlib import Path

import requests

DATA = Path(__file__).resolve().parent.parent / "data"
FRED_CSV = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}"

# domain -> series id -> (human metric name, unit)
# Chosen so each of the seven domains is backed by a real published series at
# monthly or quarterly frequency, not by a generator.
FRED_CATALOG: dict[str, dict[str, tuple[str, str]]] = {
    "Finance": {
        "CP":        ("Corporate Profits After Tax", "USD bn"),
        "FEDFUNDS":  ("Federal Funds Effective Rate", "%"),
        "CPIAUCSL":  ("Consumer Price Index (All Urban)", "index"),
        "GDP":       ("Gross Domestic Product", "USD bn"),
    },
    "Growth": {
        "RSXFS":     ("Retail Sales (ex Food Services)", "USD mn"),
        "ECOMSA":    ("E-Commerce Retail Sales", "USD mn"),
        "UMCSENT":   ("Consumer Sentiment Index", "index"),
    },
    "People": {
        "UNRATE":            ("Unemployment Rate", "%"),
        "JTSQUR":            ("Quits Rate", "%"),
        "JTSJOL":            ("Job Openings", "thousands"),
        "CES0500000003":     ("Average Hourly Earnings", "USD/hour"),
    },
    "IT": {
        "CES5051200001":     ("Software Publishers Employment", "thousands"),
        "CES6054150001":     ("Computer Systems Design Employment", "thousands"),
    },
    "Operations": {
        "INDPRO":    ("Industrial Production Index", "index"),
        "TCU":       ("Capacity Utilization", "%"),
    },
    "Logistics": {
        "BUSINV":    ("Business Inventories", "USD mn"),
        "TSIFRGHTC": ("Freight Transportation Services Index", "index"),
    },
    "ESG": {
        "EMISSCO2TOTVTTTOUSA": ("CO2 Emissions, Transport Sector", "Mt CO2"),
    },
}


def _get(url: str, tries: int = 4, timeout: int = 90) -> bytes:
    """Fetch with retries.

    Uses requests rather than urllib: on this network urllib's opener reliably
    times out against FRED while requests and curl both return 200 for the same
    URL, so the stdlib client would have reported real series as unreachable.
    Transient failures are retried — a dropped connection must not be mistaken
    for 'the series does not exist'.
    """
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


def fetch_fred() -> list[dict]:
    """Download each catalogued FRED series to data/<Domain>/fred_<id>.csv."""
    report = []
    for domain, series in FRED_CATALOG.items():
        outdir = DATA / domain
        outdir.mkdir(parents=True, exist_ok=True)
        for sid, (name, unit) in series.items():
            dest = outdir / f"fred_{sid}.csv"
            try:
                raw = _get(FRED_CSV.format(sid=sid))
            except RuntimeError as e:
                report.append({"domain": domain, "series": sid, "ok": False, "detail": str(e)})
                print(f"  !! {domain:11} {sid:22} {e}")
                continue

            rows = list(csv.reader(io.StringIO(raw.decode("utf-8"))))
            header, body = rows[0], [r for r in rows[1:] if len(r) == 2 and r[1] not in ("", ".")]
            if not body:
                report.append({"domain": domain, "series": sid, "ok": False, "detail": "no observations"})
                print(f"  !! {domain:11} {sid:22} returned no usable observations")
                continue

            dest.write_bytes(raw)
            report.append({
                "domain": domain, "series": sid, "ok": True, "metric": name, "unit": unit,
                "rows": len(body), "first": body[0][0], "last": body[-1][0],
                "url": f"https://fred.stlouisfed.org/series/{sid}",
            })
            print(f"  ok {domain:11} {sid:22} {len(body):>5} obs  {body[0][0]}..{body[-1][0]}  {name}")
    return report


# World Bank indicators. ESG is the one domain with almost no free monthly series,
# so its depth comes from breadth of indicator instead of frequency — these are
# annual, which is the frequency at which the data genuinely exists.
WORLDBANK_INDICATORS = {
    "EN.GHG.CO2.MT.CE.AR5": "CO2 Emissions (excl. LULUCF)",
    "EG.FEC.RNEW.ZS":       "Renewable Energy Share of Final Consumption",
    "EG.USE.PCAP.KG.OE":    "Energy Use per Capita",
    "EN.GHG.ALL.MT.CE.AR5": "Total Greenhouse Gas Emissions",
}


def fetch_worldbank(start_year: int = 2015, end_year: int = 2024) -> list[dict]:
    """Download the ESG indicators from the World Bank Open Data API."""
    outdir = DATA / "ESG"
    outdir.mkdir(parents=True, exist_ok=True)
    report = []
    for code, name in WORLDBANK_INDICATORS.items():
        url = (f"https://api.worldbank.org/v2/country/all/indicator/{code}"
               f"?format=json&per_page=20000&date={start_year}:{end_year}")
        try:
            payload = json.loads(_get(url, tries=3, timeout=90))
        except (RuntimeError, json.JSONDecodeError) as e:
            print(f"  !! {code:24} {e}")
            report.append({"indicator": code, "ok": False, "detail": str(e)})
            continue
        records = payload[1] if isinstance(payload, list) and len(payload) > 1 else []
        usable = [r for r in records if r.get("value") is not None]
        if not usable:
            print(f"  !! {code:24} no observations")
            report.append({"indicator": code, "ok": False, "detail": "no observations"})
            continue
        dest = outdir / f"worldbank_{code}.json"
        dest.write_text(json.dumps(payload))
        years = sorted({r["date"] for r in usable})
        print(f"  ok {code:24} {len(usable):>6} obs  {years[0]}..{years[-1]}  {name}")
        report.append({"indicator": code, "ok": True, "metric": name,
                       "rows": len(usable), "first": years[0], "last": years[-1],
                       "url": f"https://data.worldbank.org/indicator/{code}"})
    return report


def _date_windows(start: date, end: date, span_days: int) -> list[tuple[str, str]]:
    """Split [start, end] into consecutive windows of at most span_days."""
    out, cur = [], start
    while cur <= end:
        stop = min(cur + timedelta(days=span_days - 1), end)
        out.append((cur.isoformat(), stop.isoformat()))
        cur = stop + timedelta(days=1)
    return out


def fetch_nvd(per_window: int = 400) -> dict:
    """Pull a real, dated sample of CVEs from the NVD 2.0 API.

    The previously stored files held 45 records out of the ~48k the API reports,
    which is far too thin to describe a trend. The API pages 2000 at a time and
    asks unauthenticated clients to stay under ~1 request per 6 seconds.

    The budget is per time window, not global: a single global cap is filled
    entirely by the first window, which yields a monthly count series only four
    months long. Sampling every window instead gives a series that actually spans
    the period. Counts are therefore comparable *between* months only because each
    window is sampled the same way — they are a sample of published CVEs, not the
    full population, and the stored metric is named accordingly.
    """
    outdir = DATA / "IT"
    outdir.mkdir(parents=True, exist_ok=True)
    base = ("https://services.nvd.nist.gov/rest/json/cves/2.0"
            "?pubStartDate={start}T00:00:00.000&pubEndDate={end}T23:59:59.999"
            "&resultsPerPage={per}&startIndex={idx}")
    # NVD rejects any range wider than 120 days with a bare 404 — not a validation
    # message — so hand-written quarters silently failed whenever a quarter ran to
    # 122 or 123 days. Generating 90-day windows keeps every request comfortably
    # inside the limit regardless of month lengths.
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
            print(f"  ok NVD {start}..{end} idx={idx:>5} got {len(vulns):>4} "
                  f"({got_here}/{per_window} of {total} available)")
            idx += per
            if idx >= total or not vulns:
                break
            time.sleep(6)
        time.sleep(6)

    if collected:
        dest = outdir / "nvd_cves_dated.json"
        dest.write_text(json.dumps({"vulnerabilities": collected}, indent=1))
    return {"count": len(collected)}


# Chart images for the same series already in the KPI layer. These are real
# published figures, not decorative stock images: each is the publisher's own
# rendering of a series stored in the database, so an image-understanding result
# can be checked against the numbers. Their captions and axis labels give the
# vision/OCR path genuine text to extract.
CHART_IMAGES = {
    "Finance":    ["CPIAUCSL", "FEDFUNDS"],
    "Growth":     ["RSXFS"],
    "People":     ["UNRATE"],
    "Operations": ["INDPRO"],
    "Logistics":  ["TSIFRGHTC"],
}


def fetch_chart_images() -> list[dict]:
    """Download FRED's published chart PNG for selected series."""
    report = []
    for domain, series in CHART_IMAGES.items():
        outdir = DATA / domain
        outdir.mkdir(parents=True, exist_ok=True)
        for sid in series:
            dest = outdir / f"fred_chart_{sid}.png"
            try:
                raw = _get(f"https://fred.stlouisfed.org/graph/fredgraph.png?id={sid}")
            except RuntimeError as e:
                print(f"  !! {domain:11} {sid:14} {e}")
                report.append({"domain": domain, "series": sid, "ok": False, "detail": str(e)})
                continue
            if not raw.startswith(b"\x89PNG"):
                print(f"  !! {domain:11} {sid:14} not a PNG ({len(raw)} bytes)")
                report.append({"domain": domain, "series": sid, "ok": False, "detail": "not a PNG"})
                continue
            dest.write_bytes(raw)
            print(f"  ok {domain:11} {sid:14} {len(raw):>7} bytes -> {dest.name}")
            report.append({"domain": domain, "series": sid, "ok": True, "bytes": len(raw),
                           "url": f"https://fred.stlouisfed.org/series/{sid}"})
    return report


def main() -> int:
    print("== FRED ==")
    fred = fetch_fred()
    print("\n== NVD ==")
    nvd = fetch_nvd()

    ok = [r for r in fred if r["ok"]]
    bad = [r for r in fred if not r["ok"]]
    manifest = DATA / "REAL_SOURCES.json"
    manifest.write_text(json.dumps({"fred": fred, "nvd": nvd}, indent=2))

    print(f"\nFRED series ok: {len(ok)}  failed: {len(bad)}")
    print(f"NVD CVEs collected: {nvd['count']}")
    print(f"manifest -> {manifest}")
    for b in bad:
        print(f"  FAILED {b['domain']}/{b['series']}: {b['detail']}")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
