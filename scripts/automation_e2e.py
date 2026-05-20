#!/usr/bin/env python3
"""
Programmatic automation validation for OmniIntelOS.

Checks:
- Backend health and auth
- n8n health
- n8n node catalog endpoint
- Workflow import (API key mode or docker exec fallback)
- Webhook trigger smoke tests for all shipped automation workflows
- Optional n8n credentials inventory check (API key mode)
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path
from typing import Dict, List, Tuple
from urllib.parse import urlparse

import requests

ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT / ".env"
WORKFLOW_DIR = ROOT / "n8n_workflows"

BASE_API = os.getenv("OMNI_API_BASE", "http://127.0.0.1:8000")
N8N_BASE = os.getenv("N8N_BASE_URL", "http://127.0.0.1:5678")


def _load_env() -> None:
    if not ENV_PATH.exists():
        return
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k, v)


def _print(label: str, ok: bool, detail: str = "") -> None:
    status = "OK" if ok else "FAIL"
    suffix = f" - {detail}" if detail else ""
    print(f"[{status}] {label}{suffix}")


def _request(method: str, url: str, **kwargs):
    timeout = kwargs.pop("timeout", 15)
    return requests.request(method, url, timeout=timeout, **kwargs)


def _run(cmd: List[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True)


def _n8n_api_v1_available() -> bool:
    api_key = os.getenv("N8N_API_KEY", "").strip()
    if not api_key:
        return False
    try:
        resp = _request("GET", f"{N8N_BASE.rstrip('/')}/api/v1/workflows?limit=1", headers=_n8n_headers())
        return resp.status_code == 200
    except Exception:
        return False


def _cli_list_workflows(container: str) -> Dict[str, str]:
    proc = _run(["docker", "exec", container, "n8n", "list:workflow"])
    if proc.returncode != 0:
        return {}
    out: Dict[str, str] = {}
    for line in proc.stdout.splitlines():
        if "|" not in line:
            continue
        wf_id, name = line.split("|", 1)
        wf_id = wf_id.strip()
        name = name.strip()
        if wf_id and name:
            out[name] = wf_id
    return out


def _wait_for_n8n_ready(timeout_s: int = 90) -> bool:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            r = _request("GET", f"{N8N_BASE.rstrip('/')}/healthz", timeout=5)
            if r.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(2)
    return False


def check_backend_and_auth() -> Tuple[bool, str, Dict[str, str]]:
    username = os.getenv("BOOTSTRAP_ADMIN_USERNAME", "admin")
    password = os.getenv("BOOTSTRAP_ADMIN_PASSWORD", "admin123")

    health = _request("GET", f"{BASE_API}/health", timeout=10)
    if health.status_code != 200:
        return False, "backend health failed", {}

    login = _request(
        "POST",
        f"{BASE_API}/api/v1/auth/login",
        json={"username": username, "password": password},
        timeout=10,
    )
    if login.status_code != 200:
        return False, f"auth login failed: {login.status_code}", {}

    token = login.json().get("access_token")
    if not token:
        return False, "auth token missing", {}

    headers = {"Authorization": f"Bearer {token}"}
    nodes = _request("GET", f"{BASE_API}/api/v1/n8n/nodes", headers=headers, timeout=10)
    if nodes.status_code != 200:
        return False, f"n8n nodes endpoint failed: {nodes.status_code}", headers

    payload = nodes.json()
    node_count = len(payload.get("nodes", [])) if isinstance(payload, dict) else 0
    return True, f"auth + n8n nodes endpoint ({node_count} nodes)", headers


def check_n8n_health() -> Tuple[bool, str]:
    if _wait_for_n8n_ready(timeout_s=90):
        return True, "status=200"
    return False, "health endpoint unavailable within timeout"


def _n8n_headers() -> Dict[str, str]:
    api_key = os.getenv("N8N_API_KEY", "").strip()
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["X-N8N-API-KEY"] = api_key
    return headers


def import_workflows() -> Tuple[bool, str]:
    if not _wait_for_n8n_ready(timeout_s=90):
        return False, "n8n not ready before workflow import"

    files = sorted([p for p in WORKFLOW_DIR.glob("*.json") if p.is_file()])
    if not files:
        return False, "no workflow files found"

    imported = 0

    if _n8n_api_v1_available():
        headers = _n8n_headers()
        list_resp = _request("GET", f"{N8N_BASE.rstrip('/')}/api/v1/workflows?limit=250", headers=headers)
        if list_resp.status_code != 200:
            return False, f"unable to list workflows via API ({list_resp.status_code})"

        data = list_resp.json()
        existing = {w.get("name") for w in data.get("data", []) if isinstance(w, dict)}

        for wf_file in files:
            wf = json.loads(wf_file.read_text(encoding="utf-8"))
            wf_name = wf.get("name", wf_file.stem)
            if wf_name in existing:
                continue

            # Remove placeholder IDs to avoid invalid ID references at import time.
            for node in wf.get("nodes", []):
                creds = node.get("credentials", {})
                for cred_cfg in creds.values():
                    if isinstance(cred_cfg, dict) and str(cred_cfg.get("id", "")).startswith("REPLACE_WITH"):
                        cred_cfg.pop("id", None)

            create_resp = _request(
                "POST",
                f"{N8N_BASE.rstrip('/')}/api/v1/workflows",
                headers=headers,
                json=wf,
                timeout=30,
            )
            if create_resp.status_code not in (200, 201):
                return False, f"workflow import failed for {wf_file.name}: {create_resp.status_code}"
            imported += 1

        return True, f"API mode: imported {imported}, total files {len(files)}"

    # Fallback: import/publish workflows via n8n CLI for versions without /api/v1 endpoints.
    container = "omnitel-n8n"
    check = _run(["docker", "ps", "--format", "{{.Names}}"])
    if check.returncode != 0 or container not in check.stdout.splitlines():
        return False, "n8n container not running for CLI workflow import"

    existing = _cli_list_workflows(container)

    for wf_file in files:
        wf = json.loads(wf_file.read_text(encoding="utf-8"))
        wf_name = wf.get("name", wf_file.stem)
        if wf_name in existing:
            continue

        # n8n CLI import requires workflow IDs in current versions.
        wf["id"] = str(uuid.uuid4())
        wf["versionId"] = str(uuid.uuid4())
        wf.setdefault("settings", {})

        for node in wf.get("nodes", []):
            creds = node.get("credentials", {})
            for cred_cfg in creds.values():
                if isinstance(cred_cfg, dict) and str(cred_cfg.get("id", "")).startswith("REPLACE_WITH"):
                    cred_cfg.pop("id", None)

        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as tf:
            json.dump(wf, tf)
            tmp_file = tf.name

        copy_proc = _run(["docker", "cp", tmp_file, f"{container}:/tmp/{Path(tmp_file).name}"])
        os.unlink(tmp_file)
        if copy_proc.returncode != 0:
            return False, f"docker copy failed for {wf_file.name}: {copy_proc.stderr.strip()[:180]}"

        proc = _run([
            "docker",
            "exec",
            container,
            "n8n",
            "import:workflow",
            f"--input=/tmp/{Path(tmp_file).name}",
        ])
        if proc.returncode != 0:
            detail = (proc.stderr or proc.stdout).strip()
            return False, f"docker import failed for {wf_file.name}: {detail[:180]}"
        imported += 1

    published = 0
    workflow_map = _cli_list_workflows(container)
    for wf_name, wf_id in workflow_map.items():
        if wf_name.startswith("OmniIntelOS - "):
            proc = _run(["docker", "exec", container, "n8n", "publish:workflow", f"--id={wf_id}"])
            if proc.returncode == 0:
                published += 1

    return True, f"CLI mode: imported {imported}, published {published} OmniIntelOS workflows"


def check_credentials_inventory() -> Tuple[bool, str]:
    api_key = os.getenv("N8N_API_KEY", "").strip()
    if not api_key:
        return True, "skipped (N8N_API_KEY not set)"

    if not _n8n_api_v1_available():
        return True, "skipped (/api/v1 credentials endpoint not available in this n8n build)"

    resp = _request("GET", f"{N8N_BASE.rstrip('/')}/api/v1/credentials", headers=_n8n_headers())
    if resp.status_code != 200:
        return False, f"cannot read credentials inventory: {resp.status_code}"

    data = resp.json().get("data", [])
    types = {item.get("type") for item in data if isinstance(item, dict)}

    required = {
        "gmailOAuth2",
        "googleDriveOAuth2Api",
        "googleSheetsOAuth2Api",
        "clickUpApi",
    }
    missing = sorted(required - types)
    if missing:
        return False, f"missing credential types: {', '.join(missing)}"

    return True, "all required credential types present"


def trigger_webhooks() -> Tuple[bool, str]:
    base = N8N_BASE.rstrip("/")
    host_override = os.getenv("N8N_WEBHOOK_HOST_OVERRIDE", "").strip()
    if not host_override:
        public_url = os.getenv("PUBLIC_N8N_URL", "").strip()
        if public_url:
            host_override = urlparse(public_url).netloc or urlparse(public_url).path

    if not _wait_for_n8n_ready(timeout_s=90):
        return False, "n8n not ready before webhook trigger checks"

    payloads = {
        "gmail-alert": {"to": os.getenv("GMAIL_PRIMARY", ""), "subject": "OmniIntelOS E2E", "body": "automation test"},
        "drive-upload": {"filename": "e2e.txt", "content": "SGVsbG8gT21uaUludGVsT1M=", "folder_id": ""},
        "sheets-push": {
            "spreadsheet_id": os.getenv("E2E_SPREADSHEET_ID", ""),
            "sheet_name": os.getenv("E2E_SHEET_NAME", "Sheet1"),
            "rows": [{"source": "automation_e2e", "value": 1}],
        },
    }

    clickup_api_key = os.getenv("CLICKUP_API_KEY", "").strip()
    clickup_workspace_id = os.getenv("CLICKUP_WORKSPACE_ID", "").strip()
    clickup_enabled = bool(clickup_api_key and clickup_workspace_id)
    if clickup_enabled:
        payloads["clickup-task"] = {
            "list_id": clickup_workspace_id,
            "name": "OmniIntelOS E2E Task",
            "description": "Automation validation",
            "priority": 3,
            "api_key": clickup_api_key,
            "workspace_id": clickup_workspace_id,
        }

    ok = 0
    fail_msgs: List[str] = []
    headers = {"Content-Type": "application/json"}
    auth = None
    if host_override:
        headers["Host"] = host_override

    n8n_user = os.getenv("N8N_BASIC_AUTH_USER", "").strip()
    n8n_pass = os.getenv("N8N_BASIC_AUTH_PASSWORD", "").strip()
    if n8n_user and n8n_pass:
        auth = (n8n_user, n8n_pass)

    for hook, payload in payloads.items():
        last_status = None
        success = False
        for _ in range(8):
            r = _request(
                "POST",
                f"{base}/webhook/{hook}",
                json=payload,
                headers=headers,
                auth=auth,
                timeout=20,
            )
            last_status = r.status_code
            if 200 <= r.status_code < 300:
                success = True
                break
            if r.status_code not in (404, 503):
                break
            time.sleep(1)

        if success:
            ok += 1
        else:
            fail_msgs.append(f"{hook}:{last_status}")

    total = len(payloads)
    if fail_msgs:
        return False, f"{ok}/{total} webhooks passed; failures: {', '.join(fail_msgs)}"

    if clickup_enabled:
        return True, f"{total}/{total} webhooks passed"
    return True, f"{total}/{total} webhooks passed (ClickUp skipped: CLICKUP_API_KEY/CLICKUP_WORKSPACE_ID not set)"


def main() -> int:
    _load_env()

    global BASE_API, N8N_BASE
    BASE_API = os.getenv("OMNI_API_BASE", BASE_API)
    N8N_BASE = os.getenv("N8N_BASE_URL", N8N_BASE)

    checks: List[Tuple[str, bool, str]] = []

    try:
        ok, detail, _ = check_backend_and_auth()
        checks.append(("Backend + auth + n8n nodes", ok, detail))
    except Exception as exc:
        checks.append(("Backend + auth + n8n nodes", False, str(exc)))

    try:
        ok, detail = check_n8n_health()
        checks.append(("n8n health", ok, detail))
    except Exception as exc:
        checks.append(("n8n health", False, str(exc)))

    try:
        ok, detail = import_workflows()
        checks.append(("Workflow import", ok, detail))
    except Exception as exc:
        checks.append(("Workflow import", False, str(exc)))

    try:
        ok, detail = check_credentials_inventory()
        checks.append(("Credentials inventory", ok, detail))
    except Exception as exc:
        checks.append(("Credentials inventory", False, str(exc)))

    try:
        ok, detail = trigger_webhooks()
        checks.append(("Webhook triggers", ok, detail))
    except Exception as exc:
        checks.append(("Webhook triggers", False, str(exc)))

    failed = 0
    print("Automation E2E Validation")
    print("=" * 28)
    for label, ok, detail in checks:
        _print(label, ok, detail)
        if not ok:
            failed += 1

    print()
    if failed:
        print(f"Result: {len(checks) - failed} passed, {failed} failed")
        return 2

    print(f"Result: {len(checks)} passed, 0 failed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
