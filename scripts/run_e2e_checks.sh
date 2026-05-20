#!/usr/bin/env bash
# Lightweight end-to-end smoke checks for the OmniIntelOS stack
# Checks: backend health, auth login, frontend index, postgres table list

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$ROOT_DIR/logs"
mkdir -p "$LOG_DIR"

if [[ -f "$ROOT_DIR/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$ROOT_DIR/.env"
  set +a
fi

AUTH_USER="${BOOTSTRAP_ADMIN_USERNAME:-admin}"
AUTH_PASS="${BOOTSTRAP_ADMIN_PASSWORD:-admin123}"

OK=0
FAIL=0

echo "E2E CHECKS - $(date -u)" | tee "$LOG_DIR/e2e_checks.log"

run_check() {
  name="$1"; shift
  echo -n "- $name... " | tee -a "$LOG_DIR/e2e_checks.log"
  if "$@" >> "$LOG_DIR/e2e_checks.log" 2>&1; then
    echo "OK" | tee -a "$LOG_DIR/e2e_checks.log"
    OK=$((OK+1))
  else
    echo "FAIL" | tee -a "$LOG_DIR/e2e_checks.log"
    FAIL=$((FAIL+1))
  fi
}

service_running() {
  local name="$1"
  docker compose -f "$ROOT_DIR/docker-compose.yml" ps --status running --services 2>/dev/null | grep -qx "$name"
}

# Backend health
run_check "Backend health (http://127.0.0.1:8000/health)" curl -fsS -m 5 http://127.0.0.1:8000/health

# Auth login
run_check "Auth login (${AUTH_USER})" curl -fsS -m 5 -X POST http://127.0.0.1:8000/api/v1/auth/login -H 'Content-Type: application/json' -d "{\"username\":\"${AUTH_USER}\",\"password\":\"${AUTH_PASS}\"}"

# Frontend index (Vite)
run_check "Frontend index (http://127.0.0.1:5173/)" curl -fsS -m 5 http://127.0.0.1:5173/

# Static asset quick fetch (check for JS asset)
run_check "Frontend asset fetch (favicon or main.js)" curl -fsS -m 5 http://127.0.0.1:5173/favicon.ico || true

# Postgres table count
run_check "Postgres tables list (container)" docker exec omnitel-postgres psql -U omniintel -d omniintelos -c '\dt'

# Automation framework programmatic checks (only when n8n is active)
if service_running "n8n"; then
  run_check "Automation E2E (n8n workflows/webhooks)" python3 "$ROOT_DIR/scripts/automation_e2e.py"
else
  echo "- Automation E2E (n8n workflows/webhooks)... SKIP" | tee -a "$LOG_DIR/e2e_checks.log"
fi

echo
echo "RESULT: $OK passed, $FAIL failed" | tee -a "$LOG_DIR/e2e_checks.log"

if [ "$FAIL" -gt 0 ]; then
  exit 2
else
  exit 0
fi
