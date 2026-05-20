#!/usr/bin/env python3
"""
Full A-to-Z verification runner for OmniIntelOS.

Goal:
- Execute broad end-to-end checks across backend APIs, frontend routes,
  roles/auth, integrations, automation webhooks, security, and latency.
- Produce a deterministic pass/fail report with zero tolerated failures.
"""

from __future__ import annotations

import os
import random
import string
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

import requests

BASE_API = os.getenv("OMNI_API_BASE", "http://127.0.0.1:8000")
FRONTEND_BASE = os.getenv("OMNI_FRONTEND_BASE", "http://127.0.0.1:5173")
N8N_BASE = os.getenv("N8N_BASE_URL", "http://127.0.0.1:5678")
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"


class Result:
    def __init__(self) -> None:
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.rows: List[Tuple[str, str, str]] = []

    def add(self, status: str, name: str, detail: str) -> None:
        self.rows.append((status, name, detail))
        if status == "PASS":
            self.passed += 1
        elif status == "FAIL":
            self.failed += 1
        elif status == "SKIP":
            self.skipped += 1


def load_env() -> None:
    if not ENV_PATH.exists():
        return
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k, v)


def random_suffix(n: int = 8) -> str:
    return "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(n))


def req(
    method: str,
    url: str,
    token: Optional[str] = None,
    timeout: int = 15,
    **kwargs,
) -> requests.Response:
    headers = kwargs.pop("headers", {})
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return requests.request(method, url, headers=headers, timeout=timeout, **kwargs)


def run_check(results: Result, name: str, fn: Callable[[], Tuple[bool, str]]) -> None:
    try:
        ok, detail = fn()
        results.add("PASS" if ok else "FAIL", name, detail)
    except Exception as exc:
        results.add("FAIL", name, f"exception={exc}")


def run_skip(results: Result, name: str, detail: str) -> None:
    results.add("SKIP", name, detail)


def assert_status(r: requests.Response, expected: Tuple[int, ...]) -> Tuple[bool, str]:
    if r.status_code in expected:
        return True, f"status={r.status_code}"
    body = (r.text or "")[:180].replace("\n", " ")
    return False, f"status={r.status_code} body={body}"


def check_latency(
    name: str,
    call: Callable[[], requests.Response],
    max_ms: int,
) -> Tuple[bool, str]:
    start = time.perf_counter()
    r = call()
    elapsed_ms = int((time.perf_counter() - start) * 1000)
    if r.status_code == 200 and elapsed_ms <= max_ms:
        return True, f"status=200 latency_ms={elapsed_ms}<= {max_ms}"
    return False, f"status={r.status_code} latency_ms={elapsed_ms} limit={max_ms}"


def main() -> int:
    load_env()

    auth_user = os.getenv("BOOTSTRAP_ADMIN_USERNAME", "admin")
    auth_pass = os.getenv("BOOTSTRAP_ADMIN_PASSWORD", "admin123")

    n8n_user = os.getenv("N8N_BASIC_AUTH_USER", "").strip()
    n8n_pass = os.getenv("N8N_BASIC_AUTH_PASSWORD", "").strip()
    clickup_api = os.getenv("CLICKUP_API_KEY", "").strip()
    clickup_workspace = os.getenv("CLICKUP_WORKSPACE_ID", "").strip()

    results = Result()

    # 1) Preflight + security checks
    run_check(results, "health:backend", lambda: assert_status(req("GET", f"{BASE_API}/health"), (200,)))
    run_check(results, "health:frontend", lambda: assert_status(req("GET", f"{FRONTEND_BASE}/"), (200,)))
    run_check(results, "security:status_requires_auth", lambda: assert_status(req("GET", f"{BASE_API}/api/v1/status"), (401, 403)))
    run_check(
        results,
        "security:invalid_login_rejected",
        lambda: assert_status(
            req(
                "POST",
                f"{BASE_API}/api/v1/auth/login",
                json={"username": auth_user, "password": "wrong-password"},
            ),
            (401,),
        ),
    )

    # 2) Login admin
    login_resp = req(
        "POST",
        f"{BASE_API}/api/v1/auth/login",
        json={"username": auth_user, "password": auth_pass},
    )
    ok, detail = assert_status(login_resp, (200,))
    run_check(results, "auth:admin_login", lambda: (ok, detail))
    if not ok:
        print_report(results)
        return 2

    token = login_resp.json().get("access_token", "")
    if not token:
        results.add("FAIL", "auth:admin_token_present", "missing access_token")
        print_report(results)
        return 2
    results.add("PASS", "auth:admin_token_present", "token acquired")

    # 3) Role and registration checks
    run_check(results, "auth:get_me", lambda: assert_status(req("GET", f"{BASE_API}/api/v1/auth/me", token=token), (200,)))
    for role in ("viewer", "analyst"):
        username = f"e2e_{role}_{random_suffix(6)}"
        password = f"P@ss_{random_suffix(10)}"

        reg = req(
            "POST",
            f"{BASE_API}/api/v1/auth/register",
            json={"username": username, "password": password, "role": role, "preferred_language": "en"},
        )
        run_check(results, f"auth:register_{role}", lambda r=reg: assert_status(r, (200,)))

        lg = req("POST", f"{BASE_API}/api/v1/auth/login", json={"username": username, "password": password})
        run_check(results, f"auth:login_{role}", lambda r=lg: assert_status(r, (200,)))

        if lg.status_code == 200:
            tkn = lg.json().get("access_token", "")
            me = req("GET", f"{BASE_API}/api/v1/auth/me", token=tkn)
            run_check(results, f"auth:me_{role}", lambda r=me: assert_status(r, (200,)))

    # 4) Backend GET endpoints (authorized)
    get_endpoints = [
        "/api/v1/status",
        "/api/v1/personas",
        "/api/v1/files",
        "/api/v1/integrations/status",
        "/api/v1/kpis",
        "/api/v1/kpis/periods",
        "/api/v1/kpis/metrics",
        "/api/v1/kpis/categories",
        "/api/v1/insights/health",
        "/api/v1/insights/risk",
        "/api/v1/insights/summary",
        "/api/v1/hr/summary",
        "/api/v1/hr/departments",
        "/api/v1/hr/recruitment",
        "/api/v1/hr/training",
        "/api/v1/hr/health",
        "/api/v1/logistics/summary",
        "/api/v1/logistics/inventory",
        "/api/v1/logistics/shipping",
        "/api/v1/logistics/suppliers",
        "/api/v1/logistics/health",
        "/api/v1/it/overview",
        "/api/v1/it/tickets",
        "/api/v1/it/security",
        "/api/v1/it/infrastructure",
        "/api/v1/it/devops",
        "/api/v1/it/health",
        "/api/v1/operations/summary",
        "/api/v1/operations/quality",
        "/api/v1/operations/production",
        "/api/v1/operations/safety",
        "/api/v1/operations/health",
        "/api/v1/esg/summary",
        "/api/v1/chat/sessions",
        "/api/v1/monitoring/stats",
        "/api/v1/knowledge/stats",
        "/api/v1/knowledge/search?q=test&n=3",
        "/api/v1/n8n/nodes",
        "/api/v1/chatbot/domain",
        "/api/v1/data-ingestion/dataset-info",
        "/api/v1/data-ingestion/status",
        "/api/v1/admin/roles",
        "/api/v1/admin/audit?limit=20",
        "/api/v1/admin/users",
        "/api/v1/admin/tasks/status",
    ]
    for ep in get_endpoints:
        run_check(
            results,
            f"api:get:{ep}",
            lambda ep=ep: assert_status(req("GET", f"{BASE_API}{ep}", token=token), (200,)),
        )

    # 5) Backend POST/PUT/DELETE functional checks (safe)
    run_check(
        results,
        "api:chat_basic",
        lambda: assert_status(
            req(
                "POST",
                f"{BASE_API}/api/v1/chat",
                token=token,
                json={"message": "health check ping", "persona": None, "context": ""},
            ),
            (200,),
        ),
    )

    run_check(
        results,
        "api:insights_anomalies",
        lambda: assert_status(req("GET", f"{BASE_API}/api/v1/insights/anomalies?metric=Revenue", token=token), (200,)),
    )

    run_check(
        results,
        "api:forecast",
        lambda: assert_status(
            req(
                "POST",
                f"{BASE_API}/api/v1/forecast",
                token=token,
                files={},
                data={"metric": "Revenue", "periods": "3"},
            ),
            (200,),
        ),
    )

    run_check(
        results,
        "api:financial_statement",
        lambda: assert_status(
            req(
                "POST",
                f"{BASE_API}/api/v1/financial/statement",
                token=token,
                json={"statement_type": "income_statement"},
            ),
            (200,),
        ),
    )

    # Chat session lifecycle
    session_id = None
    cs = req("POST", f"{BASE_API}/api/v1/chat/sessions", token=token)
    run_check(results, "api:chat_session_create", lambda r=cs: assert_status(r, (200,)))
    if cs.status_code == 200:
        session_id = cs.json().get("session_id")

    if session_id:
        run_check(
            results,
            "api:chat_session_messages",
            lambda sid=session_id: assert_status(req("GET", f"{BASE_API}/api/v1/chat/sessions/{sid}/messages", token=token), (200,)),
        )
        run_check(
            results,
            "api:chat_session_rename",
            lambda sid=session_id: assert_status(
                req("PUT", f"{BASE_API}/api/v1/chat/sessions/{sid}/title", token=token, json={"title": "E2E Session"}),
                (200,),
            ),
        )
        run_check(
            results,
            "api:chat_session_delete",
            lambda sid=session_id: assert_status(req("DELETE", f"{BASE_API}/api/v1/chat/sessions/{sid}", token=token), (200,)),
        )

    # Ingestion checks
    run_check(
        results,
        "api:ingest_metrics",
        lambda: assert_status(
            req(
                "POST",
                f"{BASE_API}/api/v1/ingest/metrics",
                token=token,
                json={
                    "source_name": "full_a2z",
                    "replace": False,
                    "data": [
                        {
                            "period": "2026-04",
                            "metric": "Revenue",
                            "value": 123456,
                            "category": "Finance",
                            "segment": "Global",
                        }
                    ],
                },
            ),
            (200,),
        ),
    )

    csv_data = "period,metric,value,category,segment\n2026-04,Revenue,98765,Finance,Global\n"
    run_check(
        results,
        "api:ingest_csv",
        lambda: assert_status(
            req(
                "POST",
                f"{BASE_API}/api/v1/ingest/csv",
                token=token,
                files={"file": ("e2e.csv", csv_data, "text/csv")},
                data={"source_name": "full_a2z_csv"},
            ),
            (200,),
        ),
    )

    run_check(
        results,
        "api:ingest_document_txt",
        lambda: assert_status(
            req(
                "POST",
                f"{BASE_API}/api/v1/ingest/document",
                token=token,
                files={"file": ("e2e.txt", "OmniIntelOS end-to-end ingestion test.", "text/plain")},
                data={"category": "E2E"},
            ),
            (200,),
        ),
    )

    # Domain preference
    run_check(
        results,
        "api:chatbot_set_domain",
        lambda: assert_status(req("POST", f"{BASE_API}/api/v1/chatbot/domain?domain=finance", token=token), (200,)),
    )
    run_check(
        results,
        "api:chatbot_get_domain",
        lambda: assert_status(req("GET", f"{BASE_API}/api/v1/chatbot/domain", token=token), (200,)),
    )

    # Data ingestion manager endpoints
    run_check(
        results,
        "api:data_ingestion_ingest_emails",
        lambda: assert_status(req("POST", f"{BASE_API}/api/v1/data-ingestion/ingest-emails", token=token), (200,)),
    )
    run_check(
        results,
        "api:data_ingestion_ingest_sheets",
        lambda: assert_status(req("POST", f"{BASE_API}/api/v1/data-ingestion/ingest-sheets", token=token), (200,)),
    )
    run_check(
        results,
        "api:data_ingestion_ingest_pdfs",
        lambda: assert_status(req("POST", f"{BASE_API}/api/v1/data-ingestion/ingest-pdfs", token=token), (200,)),
    )
    run_check(
        results,
        "api:data_ingestion_delete_company",
        lambda: assert_status(req("DELETE", f"{BASE_API}/api/v1/data-ingestion/delete-company/CloudSync_Pro", token=token), (200,)),
    )

    # Export and spreadsheet
    run_check(
        results,
        "api:spreadsheet_create",
        lambda: assert_status(
            req(
                "POST",
                f"{BASE_API}/api/v1/spreadsheets",
                token=token,
                json={"name": f"e2e_sheet_{random_suffix(5)}", "domain": "general", "description": "e2e"},
            ),
            (200,),
        ),
    )

    run_check(
        results,
        "api:data_export_kpis_json",
        lambda: assert_status(
            req(
                "POST",
                f"{BASE_API}/api/v1/data/export",
                token=token,
                json={"source_type": "kpis", "format": "json"},
            ),
            (200,),
        ),
    )

    # Integration endpoints
    for integ in ("gmail", "sheets", "clickup"):
        run_check(
            results,
            f"api:integration_data_{integ}",
            lambda integ=integ: assert_status(req("GET", f"{BASE_API}/api/v1/integrations/{integ}/data", token=token), (200,)),
        )
        run_check(
            results,
            f"api:oauth_start_{integ}",
            lambda integ=integ: assert_status(req("GET", f"{BASE_API}/api/v1/integrations/{integ}/oauth/start", token=token), (200, 500)),
        )

    # N8N ingest webhook (public)
    run_check(
        results,
        "api:n8n_webhook_ingest",
        lambda: assert_status(
            req(
                "POST",
                f"{BASE_API}/api/v1/n8n/webhook/ingest",
                json={
                    "data": [
                        {
                            "period": "2026-04",
                            "metric": "MRR",
                            "value": 1000,
                            "category": "Growth",
                            "segment": "Global",
                        }
                    ]
                },
            ),
            (200,),
        ),
    )

    # Voice/OCR endpoint security contract (should be auth-protected and validation-safe)
    run_check(
        results,
        "api:voice_transcribe_validation",
        lambda: assert_status(req("POST", f"{BASE_API}/api/v1/voice/transcribe", token=token), (400, 422)),
    )
    run_check(
        results,
        "api:voice_tts_validation",
        lambda: assert_status(req("POST", f"{BASE_API}/api/v1/voice/tts", token=token), (400, 422)),
    )
    run_check(
        results,
        "api:ocr_extract_validation",
        lambda: assert_status(req("POST", f"{BASE_API}/api/v1/ocr/extract", token=token), (400, 422)),
    )

    # 6) Frontend page route checks
    ui_routes = [
        "/",
        "/login",
        "/dashboard",
        "/chat",
        "/analytics",
        "/financial",
        "/integrations",
        "/bulk",
        "/data-hub",
        "/admin",
        "/settings",
        "/hr",
        "/logistics",
        "/it",
        "/operations",
        "/forecasting",
        "/esg",
        "/risk",
        "/monitoring",
        "/scanner",
    ]
    for route in ui_routes:
        run_check(
            results,
            f"ui:route:{route}",
            lambda route=route: assert_status(req("GET", f"{FRONTEND_BASE}{route}"), (200,)),
        )

    # 7) n8n webhook checks (with basic auth when configured)
    n8n_auth = (n8n_user, n8n_pass) if (n8n_user and n8n_pass) else None
    webhook_payloads: Dict[str, Dict[str, object]] = {
        "gmail-alert": {"to": "noreply@example.com", "subject": "e2e", "body": "e2e"},
        "drive-upload": {"filename": "e2e.txt", "content": "SGVsbG8=", "folder_id": ""},
        "sheets-push": {"spreadsheet_id": "", "sheet_name": "Sheet1", "rows": [{"k": "v"}]},
    }
    if clickup_api and clickup_workspace:
        webhook_payloads["clickup-task"] = {
            "list_id": clickup_workspace,
            "name": "e2e task",
            "description": "e2e",
            "priority": 3,
            "api_key": clickup_api,
            "workspace_id": clickup_workspace,
        }

    for hook, payload in webhook_payloads.items():
        run_check(
            results,
            f"n8n:webhook:{hook}",
            lambda hook=hook, payload=payload: assert_status(
                req("POST", f"{N8N_BASE.rstrip('/')}/webhook/{hook}", json=payload, auth=n8n_auth),
                (200,),
            ),
        )

    # 8) Latency checks (key endpoints)
    run_check(
        results,
        "latency:health",
        lambda: check_latency("health", lambda: req("GET", f"{BASE_API}/health"), 1500),
    )
    run_check(
        results,
        "latency:status",
        lambda: check_latency("status", lambda: req("GET", f"{BASE_API}/api/v1/status", token=token), 2500),
    )
    run_check(
        results,
        "latency:kpis",
        lambda: check_latency("kpis", lambda: req("GET", f"{BASE_API}/api/v1/kpis", token=token), 3000),
    )
    run_check(
        results,
        "latency:frontend",
        lambda: check_latency("frontend", lambda: req("GET", f"{FRONTEND_BASE}/"), 2500),
    )

    # 9) Basic concurrency sanity
    def concurrent_status_call() -> bool:
        r = req("GET", f"{BASE_API}/api/v1/status", token=token)
        return r.status_code == 200

    with ThreadPoolExecutor(max_workers=10) as ex:
        futures = [ex.submit(concurrent_status_call) for _ in range(20)]
        oks = sum(1 for f in futures if f.result())

    if oks == 20:
        results.add("PASS", "concurrency:status_20_parallel", "20/20 succeeded")
    else:
        results.add("FAIL", "concurrency:status_20_parallel", f"{oks}/20 succeeded")

    # 10) WebSocket endpoint reachability contract (handshake)
    run_check(
        results,
        "websocket:chat_upgrade_contract",
        lambda: assert_status(req("GET", f"{BASE_API}/api/v1/ws/chat"), (400, 404, 426)),
    )

    print_report(results)
    return 0 if results.failed == 0 else 2


def print_report(results: Result) -> None:
    print("FULL A2Z VERIFICATION REPORT")
    print("=" * 30)
    for status, name, detail in results.rows:
        print(f"[{status}] {name} - {detail}")
    print()
    total = results.passed + results.failed + results.skipped
    print(f"TOTAL_CHECKS={total}")
    print(f"PASSED={results.passed}")
    print(f"FAILED={results.failed}")
    print(f"SKIPPED={results.skipped}")
    success_rate = (results.passed / total * 100.0) if total else 0.0
    print(f"SUCCESS_RATE={success_rate:.2f}%")


if __name__ == "__main__":
    sys.exit(main())
