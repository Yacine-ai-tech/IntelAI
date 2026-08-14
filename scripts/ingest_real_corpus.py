#!/usr/bin/env python3
"""Ingest the real document/image/audio corpus through IntelAI's public API.

Walks data/<Domain>/ and posts each file to the endpoint that matches its type:

  documents & images -> POST /api/v1/ingest/document  (delegated to the configured
                        document processor; IntelAI itself does no extraction)
  audio              -> POST /api/v1/ingest/audio     (delegated to the configured
                        audio processor)

The domain directory name becomes the row's category, so a file's location is
what files it under Finance, People, ESG and so on.

Existing rows for the same category are not cleared automatically — pass --purge
to drop previously ingested non-glossary rows first, which is what you want when
re-ingesting the whole corpus rather than adding to it.

Run:  python scripts/ingest_real_corpus.py [--purge] [--only PATTERN] [--dry-run]
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
API_BASE_URL = os.getenv("INTELAI_API_URL", "http://localhost:8000").rstrip("/")
ADMIN_USERNAME = os.getenv("SEED_ADMIN_USERNAME", "").strip()
ADMIN_PASSWORD = os.getenv("SEED_ADMIN_PASSWORD", "").strip()
INTERNAL_TOKEN = os.getenv("OMNIINTEL_INTERNAL_TOKEN", "").strip()

# .log is deliberately absent: raw server logs are machine data, like the
# statistical series below. 10k lines of Apache access entries chunk into
# thousands of near-identical passages that crowd out real answers.
DOC_EXT = {".pdf", ".txt", ".md", ".csv", ".json", ".xml", ".yaml", ".yml", ".tsv"}
IMG_EXT = {".png", ".jpg", ".jpeg", ".webp", ".tiff", ".bmp"}
AUDIO_EXT = {".mp3", ".wav", ".m4a", ".flac", ".ogg"}

# Directories under data/ that are domains. Anything else (build output, the
# generated KPI CSVs) is not part of the document corpus.
SKIP_DIRS = {"real_kpis"}

# Directories that hold per-domain subfolders rather than files of their own, so
# the category comes from the subfolder ("kpi_digests/Finance/..." is Finance,
# not "kpi_digests").
CONTAINER_DIRS = {"kpi_digests"}

# Raw statistical downloads are the *source* of the KPI rows, not knowledge-base
# documents. A CSV of 90 numbers or a 16MB CVE dump retrieves badly and only
# restates data the KPI tables already hold precisely, so the corpus keeps the
# narrative material — filings, reports, transcripts, charts — and leaves the
# series to kpi_metrics. build_real_kpis.py is what reads these files.
SKIP_PREFIXES = ("fred_", "worldbank_", "nvd_")


def _is_raw_series(path: Path) -> bool:
    name = path.name.lower()
    # the published chart images are narrative, not raw series
    if name.startswith("fred_chart_"):
        return False
    return name.startswith(SKIP_PREFIXES)


def get_auth_token(client: httpx.Client) -> str | None:
    if ADMIN_USERNAME and ADMIN_PASSWORD:
        try:
            r = client.post(f"{API_BASE_URL}/api/v1/auth/login",
                            json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD})
            if r.status_code == 200:
                return r.json().get("access_token")
        except httpx.HTTPError:
            pass
    r = client.post(f"{API_BASE_URL}/api/v1/auth/demo-login", params={"role": "admin"})
    r.raise_for_status()
    return r.json().get("access_token")


def discover() -> list[tuple[Path, str, str]]:
    """(path, category, kind) for every corpus file."""
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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--purge", action="store_true",
                    help="delete existing non-glossary knowledge_base rows first")
    ap.add_argument("--only", default="", help="substring filter on filename")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--timeout", type=float, default=900.0)
    args = ap.parse_args()

    items = discover()
    if args.only:
        items = [i for i in items if args.only.lower() in i[0].name.lower()]
    if not items:
        print("no corpus files found")
        return 1

    by_kind: dict[str, int] = {}
    for _, _, k in items:
        by_kind[k] = by_kind.get(k, 0) + 1
    print(f"corpus: {len(items)} files {by_kind}")
    print(f"API: {API_BASE_URL}")

    if args.dry_run:
        for path, cat, kind in items:
            print(f"  [dry-run] {kind:9} {cat:12} {path.name} ({path.stat().st_size:,}b)")
        return 0

    if args.purge:
        sys.path.insert(0, str(ROOT))
        from src.services.pg_store import _get_conn
        conn = _get_conn()
        with conn.cursor() as c:
            c.execute("DELETE FROM knowledge_base WHERE source NOT LIKE 'glossary%%'")
            print(f"purged {c.rowcount} existing non-glossary rows")
            conn.commit()
        conn.close()

    ok, failed, chars = 0, 0, 0
    with httpx.Client(timeout=args.timeout) as client:
        token = get_auth_token(client)
        if not token:
            print("could not obtain an admin token")
            return 1
        headers = {"Authorization": f"Bearer {token}"}
        if INTERNAL_TOKEN:
            headers["X-OmniIntel-Internal-Token"] = INTERNAL_TOKEN

        for path, category, kind in items:
            endpoint = "audio" if kind == "audio" else "document"
            data = {"category": category}
            if kind == "audio":
                data["analysis_type"] = "meeting"
            try:
                with path.open("rb") as fh:
                    r = client.post(
                        f"{API_BASE_URL}/api/v1/ingest/{endpoint}",
                        headers=headers, data=data,
                        files={"file": (path.name, fh, "application/octet-stream")},
                    )
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
                print(f"  !! {kind:9} {category:12} {path.name[:38]:40} "
                      f"HTTP {r.status_code}: {r.text[:120]}")

    print(f"\ningested ok={ok} failed={failed}  total {chars:,} chars")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
