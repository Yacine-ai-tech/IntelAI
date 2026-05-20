#!/usr/bin/env bash
set -euo pipefail

# Start backend, frontend and n8n for local development (WSL)
# Run from project root: ./scripts/start_services.sh

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT_DIR"

mkdir -p logs

# Common resource limits (8GB RAM, lower CPU priority)
MAX_VIRT=$((8 * 1024 * 1024))   # 8GB in KB for ulimit -v
NICE_LEVEL=10                  # nice priority
NODE_MEM=7000                  # max-old-space-size in MB for Node

# helper to run a command with limits
run_limited() {
  # usage: run_limited "name" command args...
  name="$1"; shift
  echo "Starting $name with nice $NICE_LEVEL and vmem ${MAX_VIRT}KB"
  # shellcheck disable=SC2086
  (ulimit -v $MAX_VIRT; nice -n $NICE_LEVEL "$@") &
}

# start backend (use uvicorn directly from venv)
if [ -x .venv/bin/uvicorn ]; then
  echo "Starting backend (uvicorn from venv)"
  run_limited backend .venv/bin/uvicorn src.api.server_v2:app \
    --host 0.0.0.0 --port 8000 --reload \
    --log-config=./src/api/logging.yaml >>logs/backend.log 2>&1
  echo "Backend started (logs/backend.log)"
else
  echo ".venv/uvicorn not found; please create or populate your virtualenv"
fi

# start frontend
if [ -d frontend ]; then
  echo "Starting frontend (npm run dev)"
  # use NODE_OPTIONS to limit memory
  (cd frontend && \
     NODE_OPTIONS=\"--max-old-space-size=$NODE_MEM\" \
     run_limited frontend npm run dev) >>logs/frontend.log 2>&1
  echo "Frontend started (logs/frontend.log)"
else
  echo "No frontend directory found"
fi

# start n8n
echo "Starting n8n via npx (development mode)"
NODE_OPTIONS="--max-old-space-size=$NODE_MEM" \
  run_limited n8n npx --yes n8n start >>logs/n8n.log 2>&1
echo "n8n started (logs/n8n.log)"

# optionally start Prometheus/Grafana if binaries exist
if command -v prometheus >/dev/null; then
  echo "Prometheus binary found; starting with limits"
  run_limited prometheus prometheus \
    --config.file=$ROOT_DIR/monitoring/prometheus.yml \
    --storage.tsdb.path=$ROOT_DIR/monitoring/prom-data >>logs/prometheus.log 2>&1
  echo "Prometheus started (logs/prometheus.log)"
else
  echo "prometheus binary not in PATH; install it to start automatically"
fi

if command -v grafana-server >/dev/null; then
  echo "Grafana binary found; starting with limits"
  run_limited grafana grafana-server --homepath=/usr/share/grafana >>logs/grafana.log 2>&1
  echo "Grafana started (logs/grafana.log)"
else
  echo "grafana-server not in PATH; install it to start automatically"
fi

# final instructions
echo "All start commands issued. Use 'tail -f logs/*.log' to follow logs."
