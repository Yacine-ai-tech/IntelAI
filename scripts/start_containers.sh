#!/usr/bin/env bash
set -euo pipefail

# Start Docker containers for OmniIntelOS.
# Usage: ./scripts/start_containers.sh [minimal|core|automation|full|all] [tunnel]

MODE="${1:-minimal}"
WITH_TUNNEL="${2:-}"

if [[ ! -f .env && -f .env.example ]]; then
  cp .env.example .env
  echo "Created .env from .env.example. Update secrets before production deployment."
fi

case "$MODE" in
  minimal|core)
    PROFILE_ARGS=()
    SERVICES=(postgres fastapi frontend)
    ;;
  automation)
    PROFILE_ARGS=(--profile automation)
    SERVICES=(postgres fastapi frontend n8n)
    ;;
  full|all)
    PROFILE_ARGS=(--profile automation --profile monitoring --profile ai)
    SERVICES=(postgres fastapi frontend n8n prometheus grafana omnitel-ocr omnitel-voice)
    ;;
  *)
    echo "Invalid mode: $MODE"
    echo "Usage: $0 [minimal|core|automation|full|all] [tunnel]"
    exit 1
    ;;
esac

if [[ "$WITH_TUNNEL" == "tunnel" ]]; then
  PROFILE_ARGS+=(--profile tunnel)
  SERVICES+=(cloudflare-tunnel)
fi

echo "Starting services (${MODE}): ${SERVICES[*]}"
docker compose -f docker-compose.yml "${PROFILE_ARGS[@]}" up -d "${SERVICES[@]}"
echo "Services started. Run ./scripts/status.sh to check health."
