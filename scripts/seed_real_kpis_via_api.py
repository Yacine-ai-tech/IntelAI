#!/usr/bin/env python3
"""Seed the real KPI baseline through IntelAI's own public API.

Loads the per-domain CSVs written by build_real_kpis.py and POSTs each one to
/api/v1/ingest/csv, so the data arrives the same way a customer's data would —
through authentication, validation and the audit trail — rather than by writing
to Postgres behind the application's back.

Rows are written as the global baseline (owner_user_id NULL), which the endpoint
allows only for an admin token. Each row keeps the provenance it was built with
(fred:INDPRO, worldbank:..., nvd:cve-2.0, ibm-hr:..., sonatel:...).

Run:  python scripts/seed_real_kpis_via_api.py [--dry-run] [--replace]
"""
from __future__ import annotations

import argparse
import csv
import os
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
API_BASE_URL = os.getenv("INTELAI_API_URL", "http://localhost:8000").rstrip("/")
ADMIN_USERNAME = os.getenv("SEED_ADMIN_USERNAME", "").strip()
ADMIN_PASSWORD = os.getenv("SEED_ADMIN_PASSWORD", "").strip()
INTERNAL_TOKEN = os.getenv("OMNIINTEL_INTERNAL_TOKEN", "").strip()


def get_auth_token(client: httpx.Client) -> str | None:
    """Real credentials if configured, otherwise the demo admin login."""
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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--src", default="data/real_kpis")
    args = ap.parse_args()

    srcdir = ROOT / args.src
    files = sorted(srcdir.glob("*_real.csv"))
    if not files:
        print(f"no CSVs in {srcdir} — run scripts/build_real_kpis.py first")
        return 1

    print(f"API: {API_BASE_URL}")
    total_rows = 0

    if args.dry_run:
        # Deliberately does not authenticate: a dry run should describe what would
        # be sent even when the API is not up yet.
        for path in files:
            with path.open() as fh:
                n = sum(1 for _ in csv.DictReader(fh))
            print(f"  [dry-run] would POST {path.name} ({n} rows) global_scope=true")
            total_rows += n
        print(f"\nfiles={len(files)}  rows={total_rows}")
        return 0

    with httpx.Client(timeout=180) as client:
        token = get_auth_token(client)
        if not token:
            print("could not obtain an admin token")
            return 1
        headers = {"Authorization": f"Bearer {token}"}
        # The portfolio's shared gate: services behind it reject calls that carry
        # only a bearer token, so send both when it is configured.
        if INTERNAL_TOKEN:
            headers["X-OmniIntel-Internal-Token"] = INTERNAL_TOKEN

        ok, failed = 0, 0
        for path in files:
            with path.open() as fh:
                n = sum(1 for _ in csv.DictReader(fh))
            if args.dry_run:
                print(f"  [dry-run] would POST {path.name} ({n} rows) global_scope=true")
                total_rows += n
                continue
            with path.open("rb") as fh:
                r = client.post(
                    f"{API_BASE_URL}/api/v1/ingest/csv",
                    headers=headers,
                    files={"file": (path.name, fh, "text/csv")},
                    data={"source_name": "real-public-data", "global_scope": "true"},
                )
            if r.status_code == 200:
                body = r.json()
                print(f"  ok {path.name:24} {body.get('rows_inserted'):>5} rows "
                      f"scope={body.get('scope')}")
                total_rows += body.get("rows_inserted", 0)
                ok += 1
            else:
                print(f"  !! {path.name:24} HTTP {r.status_code}: {r.text[:160]}")
                failed += 1

    print(f"\nfiles ok={ok if not args.dry_run else len(files)} failed={failed if not args.dry_run else 0}  rows={total_rows}")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
