#!/usr/bin/env python3
"""
IntelAI Dynamic REST API Ingestion & Seeding Tool.

Iterates recursively over IntelAI/data/ (or user-specified file/directory paths)
and ingests datasets and documents via official IntelAI REST API endpoints.

Features:
  • 100% Zero-Trust: Environment-driven API endpoints & authentication.
  • Recursive Traversal: Recursively finds all files across subdirectories.
  • Multi-Format Support:
      - Datasets: .csv, .xlsx, .xls
      - Documents & Images: .pdf, .png, .jpg, .jpeg, .tiff, .bmp, .webp, .doc, .docx, .txt, .md, .json
      - Audio Recordings: .mp3, .wav, .m4a, .ogg, .flac, .aac
  • Flexible Modes:
      - Full Ingestion (default): Scans whole data folder.
      - Target Ingestion (--path): Ingests specific files or subfolders for incremental additions.
      - Dry Run (--dry-run): Previews discovery & category matching without HTTP calls.
      - Skip Scenario (--skip-scenario): Skips re-seeding base 78-month metrics when adding new files.

Environment Variables:
  INTELAI_API_URL : Base URL of the backend (default: http://localhost:8000)
  ADMIN_USERNAME : Admin username for JWT authentication (default: admin@company.com)
  ADMIN_PASSWORD : Admin password for JWT authentication (default: AdminPassword123!)

Usage Examples:
  # Ingest entire IntelAI/data/ recursively (default)
  python3 scripts/seed_via_api.py

  # Ingest specific file or directory
  python3 scripts/seed_via_api.py --path data/documents/AmazonWebServices.pdf

  # Ingest new incremental directory without re-seeding base scenario
  python3 scripts/seed_via_api.py --path data/new_finance_files/ --skip-scenario

  # Preview files to be ingested
  python3 scripts/seed_via_api.py --dry-run
"""

import argparse
import os
import sys
import mimetypes
from pathlib import Path
from typing import List, Tuple, Optional
import httpx

# ── Environment-Driven Defaults ───────────────────────────────────────────────
API_BASE_URL = os.getenv("INTELAI_API_URL", "http://localhost:8000").rstrip("/")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin@company.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "AdminPassword123!")

DEFAULT_DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# ── Extension Classifications ──────────────────────────────────────────────────
CSV_EXCEL_EXTS = {".csv", ".xlsx", ".xls"}
DOCUMENT_EXTS = {
    ".pdf", ".doc", ".docx", ".txt", ".md", ".json", ".html",
    ".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp",
    ".mp3", ".wav", ".m4a", ".ogg", ".flac", ".aac"
}


def parse_args():
    parser = argparse.ArgumentParser(description="IntelAI Dynamic REST API Ingestion Tool")
    parser.add_argument(
        "--path", nargs="+", type=str, default=None,
        help="One or more specific file or directory paths to ingest (default: IntelAI/data/)"
    )
    parser.add_argument(
        "--category", type=str, default=None,
        help="Override category for ingested files (e.g. Finance, HR, IT, Logistics, Operations, ESG, Growth)"
    )
    parser.add_argument(
        "--skip-scenario", action="store_true",
        help="Skip re-seeding the 78-month multi-domain historical base scenario"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Preview discovered files and target endpoints without sending HTTP requests"
    )
    parser.add_argument(
        "--ext", nargs="+", type=str, default=None,
        help="Filter file extensions (e.g. --ext .pdf .csv)"
    )
    return parser.parse_args()


def get_auth_token(client: httpx.Client, dry_run: bool = False) -> str:
    """Obtain JWT Bearer token via official login endpoint."""
    if dry_run:
        return "DRY_RUN_MOCK_TOKEN"
    url = f"{API_BASE_URL}/api/v1/auth/login"
    print(f"🔑 Authenticating via {url}...")
    try:
        resp = client.post(url, data={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD})
        if resp.status_code == 200:
            token = resp.json().get("access_token", "")
            print("   ✅ Authentication successful.")
            return token
        else:
            print(f"   ⚠️ Auth response ({resp.status_code}): {resp.text}")
            return ""
    except Exception as e:
        print(f"   ❌ Auth request failed: {e}")
        return ""


def seed_scenario(client: httpx.Client, headers: dict, dry_run: bool = False):
    """Seed multi-domain 78-month KPI scenario via official admin endpoint."""
    url = f"{API_BASE_URL}/api/v1/admin/scenario"
    print(f"\n📊 Seeding Core Multi-Domain Historical Scenario via {url}...")
    if dry_run:
        print("   [DRY RUN] Would POST /api/v1/admin/scenario {'scenario': 'healthy'}")
        return
    try:
        resp = client.post(url, json={"scenario": "healthy"}, headers=headers)
        if resp.status_code == 200:
            print(f"   ✅ Scenario seeded successfully: {resp.json()}")
        else:
            print(f"   ⚠️ Scenario seed note ({resp.status_code}): {resp.text}")
    except Exception as e:
        print(f"   ❌ Scenario seed error: {e}")


def infer_category(file_path: Path, override_cat: Optional[str] = None) -> str:
    """Infer domain category from override, parent folder name, or filename keywords."""
    if override_cat:
        return override_cat

    # Check parent folder name
    parent_name = file_path.parent.name.lower()
    if parent_name in ["hr", "people"]: return "HR"
    if parent_name in ["finance", "invoices", "billing"]: return "Finance"
    if parent_name in ["it", "tech", "security"]: return "IT"
    if parent_name in ["logistics", "supply_chain", "shipping"]: return "Logistics"
    if parent_name in ["operations", "production", "safety"]: return "Operations"
    if parent_name in ["esg", "sustainability", "environmental"]: return "ESG"
    if parent_name in ["growth", "sales", "marketing"]: return "Growth"

    # Check filename keywords
    fname_lower = file_path.name.lower()
    if any(k in fname_lower for k in ["aws", "invoice", "billing", "free_fiber", "saas", "financial"]):
        return "Finance"
    if any(k in fname_lower for k in ["hr", "employee", "payroll", "recruitment", "people"]):
        return "HR"
    if any(k in fname_lower for k in ["coolblue", "hosting", "it", "devops", "security", "ticket"]):
        return "IT"
    if any(k in fname_lower for k in ["flipkart", "shipping", "logistics", "supplier", "inventory"]):
        return "Logistics"
    if any(k in fname_lower for k in ["ops", "production", "safety", "quality", "injury"]):
        return "Operations"
    if any(k in fname_lower for k in ["esg", "emissions", "ghg", "eaton", "carbon"]):
        return "ESG"
    if any(k in fname_lower for k in ["growth", "mrr", "arr", "cac", "ltv"]):
        return "Growth"

    return "General"


def discover_files(input_paths: List[Path], ext_filter: Optional[List[str]] = None) -> List[Path]:
    """Recursively discover all files from input paths."""
    discovered: List[Path] = []
    ext_set = {e.lower() if e.startswith(".") else f".{e.lower()}" for e in ext_filter} if ext_filter else None

    for p in input_paths:
        if not p.exists():
            print(f"⚠️ Warning: Path not found: {p}")
            continue
        if p.is_file():
            if not p.name.startswith("."):
                if not ext_set or p.suffix.lower() in ext_set:
                    discovered.append(p.resolve())
        elif p.is_dir():
            for root, _, files in os.walk(p):
                for f in files:
                    if f.startswith("."):
                        continue
                    fp = Path(root) / f
                    if not ext_set or fp.suffix.lower() in ext_set:
                        discovered.append(fp.resolve())

    return sorted(list(set(discovered)))


def ingest_file(client: httpx.Client, headers: dict, file_path: Path, category: str, dry_run: bool = False):
    """Route file to correct endpoint based on file extension."""
    ext = file_path.suffix.lower()

    if ext in CSV_EXCEL_EXTS:
        url = f"{API_BASE_URL}/api/v1/ingest/csv"
        source_name = file_path.stem
        print(f"\n📈 Ingesting Dataset ({category}): {file_path.name} -> {url}")
        if dry_run:
            print(f"   [DRY RUN] Would POST {url} with file={file_path.name}, source_name={source_name}")
            return
        try:
            with open(file_path, "rb") as f:
                resp = client.post(
                    url,
                    files={"file": (file_path.name, f, "text/csv")},
                    data={"source_name": source_name},
                    headers=headers
                )
            if resp.status_code == 200:
                print(f"   ✅ Ingested dataset {file_path.name}: {resp.json()}")
            else:
                print(f"   ⚠️ Dataset ingest note ({resp.status_code}): {resp.text}")
        except Exception as e:
            print(f"   ❌ Dataset ingest error for {file_path.name}: {e}")

    elif ext in DOCUMENT_EXTS or ext in {".txt", ".md", ".json"}:
        url = f"{API_BASE_URL}/api/v1/ingest/document"
        mime_type, _ = mimetypes.guess_type(str(file_path))
        mime_type = mime_type or "application/octet-stream"

        file_type = "Audio" if ext in {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".aac"} else "Document/Image"
        print(f"\n📄 Ingesting {file_type} ({category}): {file_path.name} -> {url}")
        if dry_run:
            print(f"   [DRY RUN] Would POST {url} with file={file_path.name}, category={category}, mime={mime_type}")
            return
        try:
            with open(file_path, "rb") as f:
                resp = client.post(
                    url,
                    files={"file": (file_path.name, f, mime_type)},
                    data={"category": category},
                    headers=headers
                )
            if resp.status_code == 200:
                print(f"   ✅ Ingested {file_path.name}: {resp.json()}")
            else:
                print(f"   ⚠️ Ingest note ({resp.status_code}): {resp.text}")
        except Exception as e:
            print(f"   ❌ Ingest error for {file_path.name}: {e}")
    else:
        print(f"\n⏭️ Skipping unsupported file extension ({ext}): {file_path.name}")


def main():
    args = parse_args()

    print("==========================================================")
    print("🚀 INTELAI DYNAMIC REST API DATA INGESTION TOOL")
    print("==========================================================")
    print(f"🔗 Base API Endpoint: {API_BASE_URL}")
    print(f"🔒 Admin Account:     {ADMIN_USERNAME}")
    print(f"🧪 Dry Run Mode:       {'ENABLED' if args.dry_run else 'DISABLED'}")
    print(f"⏩ Skip Base Scenario: {'YES' if args.skip_scenario else 'NO'}\n")

    # Determine input target paths
    if args.path:
        target_paths = [Path(p) for p in args.path]
    else:
        target_paths = [DEFAULT_DATA_DIR]

    print(f"🔍 Discovering target files in: {[str(p) for p in target_paths]}...")
    discovered_files = discover_files(target_paths, ext_filter=args.ext)
    print(f"   📊 Discovered {len(discovered_files)} matching file(s) for ingestion.")

    if not discovered_files and not (not args.skip_scenario and not args.path):
        print("❌ No matching files found to ingest.")
        sys.exit(0)

    with httpx.Client(timeout=120.0) as client:
        token = get_auth_token(client, dry_run=args.dry_run)
        headers = {"Authorization": f"Bearer {token}"} if token else {}

        # 1. Base Scenario Seed (unless --skip-scenario or specific file path provided)
        if not args.skip_scenario and not args.path:
            seed_scenario(client, headers, dry_run=args.dry_run)

        # 2. Process discovered files
        for fp in discovered_files:
            category = infer_category(fp, override_cat=args.category)
            ingest_file(client, headers, fp, category=category, dry_run=args.dry_run)

    print("\n==========================================================")
    print("✨ DYNAMIC REST API INGESTION COMPLETED.")
    print("==========================================================")


if __name__ == "__main__":
    main()
