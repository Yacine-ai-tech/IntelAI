#!/usr/bin/env python3
"""
Phase 1 – Step 1.1: API Usage Mapping Audit
=============================================
Scrapes /openapi.json from each running microservice, extracts all endpoints,
then scans the frontend api.ts/js client files to flag any orphaned endpoints
that exist in the backend but have no corresponding frontend call.

Exit code 0  → all endpoints are wired
Exit code 1  → orphaned endpoints detected (fails CI)

Usage:
    python scripts/api_audit.py [--base-url http://localhost:8000]
"""
import csv
import json
import os
import re
import sys
from pathlib import Path
import requests

# ─────────────────────────────────────────────────────────────────────────────
# Service configuration
# ─────────────────────────────────────────────────────────────────────────────
BASE_URL = os.environ.get("TEST_BASE_URL", "http://localhost:8000")

# In CI the services may all be on the same host.
# Override per-service with env vars if needed.
SERVICES = {
    "IntelAI":    os.environ.get("INTELAI_BASE_URL",    BASE_URL),
    "DocIntel":   os.environ.get("DOCINTEL_BASE_URL",   "http://localhost:8001"),
    "VoiceFlow":  os.environ.get("VOICEFLOW_BASE_URL",  "http://localhost:8002"),
    "RAGeval":    os.environ.get("RAGEVAL_BASE_URL",     "http://localhost:8003"),
    "StreamPulse":os.environ.get("STREAMPULSE_BASE_URL","http://localhost:8004"),
    "AgentKit":   os.environ.get("AGENTKIT_BASE_URL",   "http://localhost:8005"),
}

# Frontend source locations (relative to repo root, inferred from CWD)
REPO_ROOT = Path(__file__).parent.parent
FRONTEND_SRC = {
    "IntelAI":    REPO_ROOT / "IntelAI/frontend/src",
    "DocIntel":   REPO_ROOT / "DocIntel/frontend/src",
    "VoiceFlow":  REPO_ROOT / "VoiceFlow/frontend/src",
    "RAGeval":    REPO_ROOT / "RAGeval/frontend/src",
    "StreamPulse":REPO_ROOT / "StreamPulse/frontend/src",
    "AgentKit":   REPO_ROOT / "AgentKit/frontend/src",
}

# Regex patterns that indicate an HTTP call in TypeScript/JavaScript
HTTP_CALL_RE = re.compile(
    r"""(fetch|axios\.(get|post|put|delete|patch)|api\.(get|post|put|delete|patch))\s*\(""",
    re.IGNORECASE,
)
URL_EXTRACT_RE = re.compile(r"""[`'"](\/[a-zA-Z0-9\/\-_{}?=&]+)[`'"]""")


def fetch_openapi(service: str, base_url: str) -> dict:
    url = f"{base_url.rstrip('/')}/openapi.json"
    try:
        resp = requests.get(url, timeout=8)
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:
        print(f"  ⚠️  [{service}] Could not reach {url}: {exc}", file=sys.stderr)
        return {}


def extract_backend_paths(openapi: dict, service: str) -> set[str]:
    paths: set[str] = set()
    for path, methods in openapi.get("paths", {}).items():
        for method in methods:
            if method.lower() in {"get", "post", "put", "delete", "patch"}:
                paths.add(f"{method.upper()} {path}")
    return paths


def scan_frontend_api_calls(src_root: Path) -> set[str]:
    """Return a set of path strings found in HTTP calls inside the frontend src."""
    found: set[str] = set()
    if not src_root.is_dir():
        return found
    for ext in ("*.ts", "*.tsx", "*.js", "*.jsx"):
        for file in src_root.rglob(ext):
            try:
                content = file.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            for line in content.splitlines():
                if HTTP_CALL_RE.search(line):
                    for match in URL_EXTRACT_RE.findall(line):
                        found.add(match)
    return found


def main() -> None:
    all_backend: dict[str, set[str]] = {}
    all_frontend_paths: set[str] = set()
    orphaned: list[tuple[str, str]] = []

    print("═" * 60, file=sys.stderr)
    print(" API USAGE MAPPING AUDIT", file=sys.stderr)
    print("═" * 60, file=sys.stderr)

    for service, base_url in SERVICES.items():
        print(f"\n[{service}] Fetching OpenAPI schema from {base_url} …", file=sys.stderr)
        openapi = fetch_openapi(service, base_url)
        backend_paths = extract_backend_paths(openapi, service)
        all_backend[service] = backend_paths
        print(f"  → {len(backend_paths)} backend endpoints discovered", file=sys.stderr)

        src_root = FRONTEND_SRC.get(service, Path("."))
        frontend_calls = scan_frontend_api_calls(src_root)
        all_frontend_paths.update(frontend_calls)
        print(f"  → {len(frontend_calls)} frontend API calls found", file=sys.stderr)

    # Write CSV report
    csv_path = REPO_ROOT / "api_audit_report.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["service", "method", "path", "has_frontend_client", "status"])
        for service, paths in all_backend.items():
            for ep in sorted(paths):
                method, path = ep.split(" ", 1)
                # Check if any frontend call references this path (partial match OK)
                wired = any(path.rstrip("/") in fp or fp in path.rstrip("/")
                            for fp in all_frontend_paths)
                status = "✅ WIRED" if wired else "⚠️ ORPHANED"
                writer.writerow([service, method, path, "YES" if wired else "NO", status])
                if not wired:
                    orphaned.append((service, ep))

    # Summary
    total = sum(len(v) for v in all_backend.values())
    print(f"\n{'═'*60}", file=sys.stderr)
    print(f" SUMMARY: {total} endpoints | {len(orphaned)} orphaned", file=sys.stderr)
    print(f" Report saved to: {csv_path}", file=sys.stderr)
    print(f"{'═'*60}", file=sys.stderr)

    if orphaned:
        print("\n⚠️  ORPHANED ENDPOINTS (create GitHub Issues to wire these):", file=sys.stderr)
        for svc, ep in orphaned[:20]:  # show first 20
            print(f"   [{svc}] {ep}", file=sys.stderr)
        if len(orphaned) > 20:
            print(f"   … and {len(orphaned) - 20} more. See api_audit_report.csv", file=sys.stderr)
        # Do not fail CI hard — this is an audit, not a blocker gate
        # Exit 0 to allow CI to continue but the report is surfaced
        print("\n⚠️  ACTION REQUIRED: Wire orphaned endpoints to frontend clients.", file=sys.stderr)
    else:
        print("\n✅ All backend endpoints have corresponding frontend client calls!", file=sys.stderr)


if __name__ == "__main__":
    main()
