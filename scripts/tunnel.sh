#!/usr/bin/env bash
set -euo pipefail

# Cloudflare tunnel helper for OmniIntelOS.
# Uses stable domain names under CLOUDFLARE_DOMAIN.
#
# Usage:
#   ./scripts/tunnel.sh configure
#   ./scripts/tunnel.sh up
#   ./scripts/tunnel.sh down

ACTION="${1:-configure}"
ENV_FILE=".env"
DOMAIN_DEFAULT="ysiddo-ai-projects.app"
DOMAIN="${CLOUDFLARE_DOMAIN:-$DOMAIN_DEFAULT}"
SINGLE_HOSTNAME="${OMNI_SINGLE_HOSTNAME:-}"
FRONTEND_HOST="${FRONTEND_TUNNEL_HOSTNAME:-app.${DOMAIN}}"
API_HOST="${API_TUNNEL_HOSTNAME:-api.${DOMAIN}}"
N8N_HOST="${N8N_TUNNEL_HOSTNAME:-workflows.${DOMAIN}}"

ensure_env_key() {
  local key="$1"
  local value="$2"
  if [[ -f "$ENV_FILE" ]] && grep -q "^${key}=" "$ENV_FILE"; then
    sed -i "s|^${key}=.*|${key}=${value}|" "$ENV_FILE"
  else
    echo "${key}=${value}" >> "$ENV_FILE"
  fi
}

configure_env() {
  touch "$ENV_FILE"
  ensure_env_key "CLOUDFLARE_DOMAIN" "$DOMAIN"

  if [[ -n "$SINGLE_HOSTNAME" ]]; then
    ensure_env_key "N8N_WEBHOOK_HOST_OVERRIDE" "$SINGLE_HOSTNAME"
    ensure_env_key "PUBLIC_API_URL" "https://${SINGLE_HOSTNAME}/api"
    ensure_env_key "PUBLIC_FRONTEND_URL" "https://${SINGLE_HOSTNAME}"
    ensure_env_key "PUBLIC_N8N_URL" "https://${SINGLE_HOSTNAME}"
    ensure_env_key "TUNNEL_URL" "https://${SINGLE_HOSTNAME}"
  else
    ensure_env_key "N8N_WEBHOOK_HOST_OVERRIDE" "$N8N_HOST"
    ensure_env_key "PUBLIC_API_URL" "https://${API_HOST}"
    ensure_env_key "PUBLIC_FRONTEND_URL" "https://${FRONTEND_HOST}"
    ensure_env_key "PUBLIC_N8N_URL" "https://${N8N_HOST}"
  fi

  echo "Updated ${ENV_FILE} with stable Cloudflare domain settings for ${DOMAIN}."
}

case "$ACTION" in
  configure)
    configure_env
    ;;
  up)
    configure_env
    echo "Starting Cloudflare tunnel profile..."
    docker compose -f docker-compose.yml --profile tunnel up -d cloudflare-tunnel
    ;;
  down)
    echo "Stopping Cloudflare tunnel profiles..."
    docker compose -f docker-compose.yml --profile tunnel down || true
    docker compose -f docker-compose.yml --profile tunnel-permanent down || true
    ;;
  *)
    echo "Invalid action: $ACTION"
    echo "Usage: $0 [configure|up|down]"
    exit 1
    ;;
esac
