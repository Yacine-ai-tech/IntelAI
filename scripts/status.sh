#!/usr/bin/env bash
set -euo pipefail

# Show service status and basic health checks.

if [[ ! -f .env ]]; then
  echo "No .env found. Create one from .env.example for full runtime checks."
fi

check_http() {
  local name="$1"
  local url="$2"
  local timeout="${3:-5}"
  if curl -fsS -m "$timeout" "$url" >/dev/null 2>&1; then
    echo "[OK]   $name ($url)"
  else
    echo "[FAIL] $name ($url)"
  fi
}

check_http_retry() {
  local name="$1"
  local url="$2"
  local timeout="${3:-5}"
  local attempts="${4:-8}"
  local i
  for i in $(seq 1 "$attempts"); do
    if curl -fsS -m "$timeout" "$url" >/dev/null 2>&1; then
      echo "[OK]   $name ($url)"
      return 0
    fi
  done
  echo "[FAIL] $name ($url)"
  return 1
}

service_running() {
  local name="$1"
  docker compose -f docker-compose.yml ps --status running --services 2>/dev/null | grep -qx "$name"
}

echo "=== Docker Compose Status ==="
docker compose -f docker-compose.yml ps

echo
echo "=== HTTP Health Checks ==="
check_http "API health" "http://127.0.0.1:8000/health"
check_http "Frontend" "http://127.0.0.1:5173/"

if service_running "n8n"; then
  check_http_retry "n8n" "http://127.0.0.1:5678/healthz" 10 12
else
  echo "[SKIP] n8n (service not running)"
fi

if service_running "prometheus"; then
  check_http "Prometheus" "http://127.0.0.1:9090/-/healthy"
else
  echo "[SKIP] Prometheus (service not running)"
fi

if service_running "grafana"; then
  check_http "Grafana" "http://127.0.0.1:3000/api/health"
else
  echo "[SKIP] Grafana (service not running)"
fi
