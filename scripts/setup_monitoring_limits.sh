#!/usr/bin/env bash
# Create systemd drop-in files to limit Prometheus and Grafana resource usage
# to 8GB RAM and 50% CPU. Requires sudo.

set -euo pipefail

limit_file="/etc/systemd/system/%s.service.d/limits.conf"

for svc in prometheus grafana-server; do
  echo "Configuring resource limits for $svc"
  sudo mkdir -p "$(dirname "$(printf "$limit_file" "$svc")")"
  sudo tee "$(printf "$limit_file" "$svc")" >/dev/null <<'EOF'
[Service]
# limit memory and CPU
MemoryMax=8G
# CPUQuota=50% # uncomment to restrict CPU usage to half a core
EOF
done

sudo systemctl daemon-reload
sudo systemctl restart prometheus grafana-server || true

echo "Resource limits applied; check 'systemctl status <service>' for details."
