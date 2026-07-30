#!/usr/bin/env python3
"""
IntelAI Official API Seeding Script.

Iterates over IntelAI/data/ and ingests all datasets and documents using the official
REST API endpoints of IntelAI. Supports local dev (http://localhost:8000) or any deployed
production environment via environment variables.

Environment Variables:
    INTELAI_API_URL : Base URL of the IntelAI backend (default: https://intelai.ysiddo-ai-projects.app)
    ADMIN_USERNAME : Admin login username (default: admin@company.com)
    ADMIN_PASSWORD : Admin login password (default: AdminPassword123!)

Usage:
    python3 scripts/seed_via_api.py
"""
import os
import sys
import json
import time
from pathlib import Path
import httpx

# Configuration from Environment Variables
API_BASE_URL = os.getenv("INTELAI_API_URL", "https://intelai.ysiddo-ai-projects.app").rstrip("/")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin@company.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "AdminPassword123!")

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

def get_auth_token(client: httpx.Client) -> str:
    """Obtain JWT Bearer token via official login endpoint."""
    url = f"{API_BASE_URL}/api/v1/auth/login"
    print(f"🔑 Authenticating via {url}...")
    try:
        resp = client.post(url, data={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD})
        if resp.status_code == 200:
            token = resp.json().get("access_token")
            print("   ✅ Authentication successful.")
            return token
        else:
            print(f"   ⚠️ Authentication warning ({resp.status_code}): {resp.text}")
            return ""
    except Exception as e:
        print(f"   ❌ Auth request failed: {e}")
        return ""

def seed_scenario(client: httpx.Client, headers: dict):
    """Seed multi-domain 78-month KPI scenario via official admin endpoint."""
    url = f"{API_BASE_URL}/api/v1/admin/scenario"
    print(f"\n📊 Seeding Core Multi-Domain Scenario via {url}...")
    try:
        resp = client.post(url, json={"scenario": "healthy"}, headers=headers)
        if resp.status_code == 200:
            print(f"   ✅ Scenario seeded successfully: {resp.json()}")
        else:
            print(f"   ⚠️ Scenario seed note ({resp.status_code}): {resp.text}")
    except Exception as e:
        print(f"   ❌ Scenario seed error: {e}")

def ingest_csv(client: httpx.Client, headers: dict, csv_file: Path):
    """Ingest CSV metric dataset via official POST /api/v1/ingest/csv."""
    url = f"{API_BASE_URL}/api/v1/ingest/csv"
    source_name = csv_file.stem
    print(f"\n📈 Ingesting CSV metric dataset: {csv_file.name}...")
    try:
        with open(csv_file, "rb") as f:
            resp = client.post(
                url,
                files={"file": (csv_file.name, f, "text/csv")},
                data={"source_name": source_name},
                headers=headers
            )
        if resp.status_code == 200:
            print(f"   ✅ Ingested {csv_file.name}: {resp.json()}")
        else:
            print(f"   ⚠️ Ingest note ({resp.status_code}): {resp.text}")
    except Exception as e:
        print(f"   ❌ CSV ingest error for {csv_file.name}: {e}")

def ingest_document(client: httpx.Client, headers: dict, doc_file: Path):
    """Ingest PDF, image, or audio document via official POST /api/v1/ingest/document."""
    url = f"{API_BASE_URL}/api/v1/ingest/document"
    
    # Infer domain category from filename
    category = "General"
    fname_lower = doc_file.name.lower()
    if any(k in fname_lower for k in ["aws", "invoice", "billing", "free_fiber"]):
        category = "Finance"
    elif any(k in fname_lower for k in ["hr", "employee", "people"]):
        category = "HR"
    elif any(k in fname_lower for k in ["coolblue", "hosting", "it", "security"]):
        category = "IT"
    elif any(k in fname_lower for k in ["flipkart", "shipping", "logistics", "supply"]):
        category = "Logistics"
        
    print(f"\n📄 Ingesting document ({category}): {doc_file.name}...")
    mime_type = "application/pdf" if doc_file.suffix == ".pdf" else "application/octet-stream"
    try:
        with open(doc_file, "rb") as f:
            resp = client.post(
                url,
                files={"file": (doc_file.name, f, mime_type)},
                data={"category": category},
                headers=headers
            )
        if resp.status_code == 200:
            print(f"   ✅ Ingested {doc_file.name}: {resp.json()}")
        else:
            print(f"   ⚠️ Ingest note ({resp.status_code}): {resp.text}")
    except Exception as e:
        print(f"   ❌ Document ingest error for {doc_file.name}: {e}")

def main():
    print("==================================================")
    print("🚀 INTELAI OFFICIAL REST API DATA INGESTION SCRIPT")
    print("==================================================")
    print(f"🔗 Target Endpoint: {API_BASE_URL}")
    print(f"📁 Data Directory:  {DATA_DIR}\n")

    if not DATA_DIR.exists():
        print(f"❌ Data directory not found: {DATA_DIR}")
        sys.exit(1)

    with httpx.Client(timeout=120.0) as client:
        token = get_auth_token(client)
        headers = {"Authorization": f"Bearer {token}"} if token else {}

        # 1. Core Multi-Domain Historical Scenario Seed
        seed_scenario(client, headers)

        # 2. Iterate over IntelAI/data/ for CSV datasets
        csv_files = list(DATA_DIR.glob("*.csv"))
        for csv_file in csv_files:
            ingest_csv(client, headers, csv_file)

        # 3. Iterate over IntelAI/data/documents/ for PDF and enterprise docs
        doc_dir = DATA_DIR / "documents"
        if doc_dir.exists():
            doc_files = [f for f in doc_dir.iterdir() if f.is_file() and not f.name.startswith(".")]
            for doc_file in doc_files:
                ingest_document(client, headers, doc_file)

    print("\n==================================================")
    print("✨ OFFICIAL API SEEDING COMPLETED SUCCESSFULLY.")
    print("==================================================")

if __name__ == "__main__":
    main()
