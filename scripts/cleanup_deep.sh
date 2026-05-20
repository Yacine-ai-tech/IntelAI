#!/usr/bin/env bash
set -euo pipefail

# Deep cleanup for low-storage environments.
# Usage:
#   ./scripts/cleanup_deep.sh
#   ./scripts/cleanup_deep.sh --with-volumes   # destructive for Docker volumes

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WITH_VOLUMES="${1:-}"

cd "$ROOT_DIR"

echo "=== OmniIntelOS Deep Cleanup ==="
echo "Workspace: $ROOT_DIR"

echo
echo "[1/7] Disk status before cleanup"
df -h /
du -sh . 2>/dev/null || true
docker system df || true

echo
echo "[2/7] Cleaning Python caches and test artifacts"
find . -type d -name "__pycache__" -prune -exec rm -rf {} + 2>/dev/null || true
find . -type d -name ".pytest_cache" -prune -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true

echo
echo "[3/7] Cleaning local logs and temporary artifacts"
find logs -type f -name "*.log" -delete 2>/dev/null || true
find . -type f -name "*.tmp" -delete 2>/dev/null || true
find . -type f -name "*.swp" -delete 2>/dev/null || true

echo
echo "[4/7] Cleaning frontend dependencies cache (safe to regenerate)"
rm -rf frontend/node_modules 2>/dev/null || true
if command -v npm >/dev/null 2>&1; then
  npm cache clean --force >/dev/null 2>&1 || true
fi

echo
echo "[5/7] Cleaning pip cache"
if command -v pip >/dev/null 2>&1; then
  pip cache purge >/dev/null 2>&1 || true
fi

echo
echo "[6/7] Docker prune (containers/images/build cache/networks)"
docker container prune -f || true
docker image prune -af || true
docker builder prune -af || true
docker network prune -f || true

if [[ "$WITH_VOLUMES" == "--with-volumes" ]]; then
  echo
  echo "[6b/7] Volume prune requested -- removing unused Docker volumes"
  docker volume prune -f || true
fi

echo
echo "[7/7] Disk status after cleanup"
df -h /
du -sh . 2>/dev/null || true
docker system df || true

echo
echo "Cleanup completed."
