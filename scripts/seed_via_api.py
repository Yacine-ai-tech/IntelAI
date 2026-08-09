#!/usr/bin/env python3
"""
IntelAI — real REST API data seeding.

`src/data/seed.py`'s `seed_database()` writes the generated KPI catalog straight to
Postgres — fast, and what the server itself calls on first boot / Admin scenario
switching. This script delivers the *exact same* dataset (same `generate_kpi_rows()`
catalog — one source of truth, see src/data/seed.py) through the real, public ingestion
API instead: per-domain CSVs, `POST /api/v1/auth/{login,demo-login}` then
`POST /api/v1/ingest/csv` for each one. Two reasons to use this path instead:

  1. It exercises the actual self-hoster-facing upload flow end-to-end (auth, CSV
     parsing, the metric_name->metric column mapping, RBAC) rather than bypassing it.
  2. It's a template for feeding IntelAI real company data: point --path at your own
     exported CSVs (same period/category/segment/metric_name/value/unit/direction
     columns) instead of the generated catalog, and this script ingests those instead.

Environment variables (no hardcoded secrets or URLs — see .env.example):
  INTELAI_API_URL          Base URL of a running IntelAI backend (default: http://localhost:8000)
  SEED_ADMIN_USERNAME      Real login username (optional — falls back to demo-login)
  SEED_ADMIN_PASSWORD      Real login password (optional — falls back to demo-login)
  OMNIINTEL_INTERNAL_TOKEN Sent as X-OmniIntel-Internal-Token if REQUIRE_INTERNAL_TOKEN
                            is enabled on the target server (empty = header omitted)

Usage:
  python scripts/seed_via_api.py                        # healthy scenario, generated catalog
  python scripts/seed_via_api.py declining_financial     # a specific scenario
  python scripts/seed_via_api.py --path data/Finance/    # ingest your own CSVs instead
  python scripts/seed_via_api.py --dry-run               # preview without HTTP calls
"""
from __future__ import annotations

import argparse
import csv
import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional

import httpx

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

API_BASE_URL = os.getenv("INTELAI_API_URL", "http://localhost:8000").rstrip("/")
ADMIN_USERNAME = os.getenv("SEED_ADMIN_USERNAME", "").strip()
ADMIN_PASSWORD = os.getenv("SEED_ADMIN_PASSWORD", "").strip()
INTERNAL_TOKEN = os.getenv("OMNIINTEL_INTERNAL_TOKEN", "").strip()

CSV_COLUMNS = ["period", "category", "segment", "metric_name", "value", "unit", "direction", "source"]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("scenario", nargs="?", default="healthy",
                    help="healthy | declining_financial | high_churn_crisis | operational_meltdown | "
                         "talent_crisis | cybersecurity_breach | esg_compliance_failure")
    p.add_argument("--path", type=str, default=None,
                    help="Ingest CSVs from this file/directory instead of generating the seed catalog "
                         "(each CSV needs at least metric_name,value columns; period/category/segment/"
                         "unit/direction recommended)")
    p.add_argument("--dry-run", action="store_true", help="Preview without sending any HTTP requests")
    p.add_argument("--keep-csv", action="store_true",
                    help="Keep the generated per-domain CSVs under data/<Domain>/ instead of using a temp dir")
    return p.parse_args()


def write_domain_csvs(scenario: str, out_dir: Path) -> List[Path]:
    """Generate the seed catalog and write one CSV per domain — the shape
    POST /api/v1/ingest/csv expects (metric_name, not metric — see server.py)."""
    from src.data.seed import generate_kpi_rows

    rows = generate_kpi_rows(scenario=scenario)
    by_category: Dict[str, List[dict]] = defaultdict(list)
    for r in rows:
        by_category[r["category"]].append(r)

    paths: List[Path] = []
    for category, cat_rows in by_category.items():
        domain_dir = out_dir / category
        domain_dir.mkdir(parents=True, exist_ok=True)
        csv_path = domain_dir / f"intelai_seed_{scenario}.csv"
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
            writer.writeheader()
            for r in cat_rows:
                writer.writerow({
                    "period": r["period"], "category": r["category"], "segment": r["segment"],
                    "metric_name": r["metric"], "value": r["value"], "unit": r["unit"],
                    "direction": r["direction"], "source": f"seed_via_api_{scenario}",
                })
        paths.append(csv_path)
    return paths


def discover_csvs(path: Path) -> List[Path]:
    if path.is_file():
        return [path]
    return sorted(p for p in path.rglob("*.csv") if not p.name.startswith("."))


def get_auth_token(client: httpx.Client) -> Optional[str]:
    if ADMIN_USERNAME and ADMIN_PASSWORD:
        try:
            resp = client.post(f"{API_BASE_URL}/api/v1/auth/login",
                                json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD})
            if resp.status_code == 200:
                print(f"authenticated as {ADMIN_USERNAME}")
                return resp.json().get("access_token")
            print(f"login failed ({resp.status_code}): {resp.text[:200]} — trying demo-login")
        except httpx.HTTPError as e:
            print(f"login request failed ({e}) — trying demo-login")

    try:
        resp = client.post(f"{API_BASE_URL}/api/v1/auth/demo-login", params={"role": "admin"})
        if resp.status_code == 200:
            print("authenticated via demo-login (role=admin)")
            return resp.json().get("access_token")
        print(f"demo-login failed ({resp.status_code}): {resp.text[:300]}")
    except httpx.HTTPError as e:
        print(f"demo-login request failed: {e}")
    return None


def ingest_csv(client: httpx.Client, headers: dict, csv_path: Path) -> tuple[bool, str]:
    try:
        with open(csv_path, "rb") as f:
            resp = client.post(
                f"{API_BASE_URL}/api/v1/ingest/csv",
                files={"file": (csv_path.name, f, "text/csv")},
                data={"source_name": csv_path.stem},
                headers=headers,
            )
        if resp.status_code == 200:
            body = resp.json()
            return True, f"{body.get('rows_inserted', '?')} rows"
        return False, f"HTTP {resp.status_code}: {resp.text[:200]}"
    except httpx.HTTPError as e:
        return False, str(e)


def main() -> None:
    args = parse_args()
    print(f"IntelAI API-based seeding — target: {API_BASE_URL}")

    if args.path:
        csv_paths = discover_csvs(Path(args.path))
        source_desc = f"custom path {args.path}"
    else:
        import tempfile
        out_dir = (ROOT_DIR / "data") if args.keep_csv else Path(tempfile.mkdtemp(prefix="intelai_seed_"))
        csv_paths = write_domain_csvs(args.scenario, out_dir)
        source_desc = f"generated catalog (scenario={args.scenario}) -> {out_dir}"

    print(f"source: {source_desc}")
    print(f"discovered {len(csv_paths)} CSV file(s)")
    if not csv_paths:
        print("nothing to ingest.")
        sys.exit(0)

    if args.dry_run:
        for p in csv_paths:
            print(f"  [dry-run] would POST {p} -> {API_BASE_URL}/api/v1/ingest/csv")
        return

    with httpx.Client(timeout=60.0) as client:
        token = get_auth_token(client)
        if not token:
            print("could not authenticate — aborting (server unreachable, or DEMO_MODE=false "
                  "with no SEED_ADMIN_USERNAME/PASSWORD set)")
            sys.exit(1)

        headers = {"Authorization": f"Bearer {token}"}
        if INTERNAL_TOKEN:
            headers["X-OmniIntel-Internal-Token"] = INTERNAL_TOKEN

        results = []
        for p in csv_paths:
            ok, detail = ingest_csv(client, headers, p)
            status = "OK" if ok else "FAILED"
            print(f"  [{status}] {p.relative_to(p.parents[1])} — {detail}")
            results.append(ok)

    succeeded = sum(results)
    print(f"\n{succeeded}/{len(results)} files ingested successfully.")
    if succeeded < len(results):
        sys.exit(1)


if __name__ == "__main__":
    main()
