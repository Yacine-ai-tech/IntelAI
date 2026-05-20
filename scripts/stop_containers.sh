#!/usr/bin/env bash
set -euo pipefail

# Stop all Docker services for OmniIntelOS.

echo "Stopping OmniIntelOS services..."
docker compose -f docker-compose.yml down --remove-orphans
echo "All services stopped."
