#!/usr/bin/env bash
set -euo pipefail

# Build Docker images without starting containers.
# Usage: ./scripts/start_all.sh [minimal|core|automation|full|all]

MODE="${1:-minimal}"

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
    echo "Usage: $0 [minimal|core|automation|full|all]"
    exit 1
    ;;
esac

COMPOSE_ARGS=(-f docker-compose.yml)

echo "Building images (${MODE}): ${SERVICES[*]}"
DOCKER_BUILDKIT=1 COMPOSE_DOCKER_CLI_BUILD=1 docker compose "${COMPOSE_ARGS[@]}" "${PROFILE_ARGS[@]}" build --parallel "${SERVICES[@]}"
echo "Build completed successfully."
