#!/usr/bin/env bash
# deploy_services.sh — Install/reload all NINA systemd user services from deploy/
# Run after any service file change, or after a fresh clone.
# Usage: bash scripts/deploy_services.sh

set -euo pipefail

NINA="$HOME/nina"
DEPLOY="$NINA/deploy"
SYSTEMD_USER="$HOME/.config/systemd/user"

mkdir -p "$SYSTEMD_USER"

SERVICES=(nina.service ninajulesgithub.service)

echo "=== NINA Service Deployer ==="
for svc in "${SERVICES[@]}"; do
    SRC="$DEPLOY/$svc"
    DST="$SYSTEMD_USER/$svc"
    if [ ! -f "$SRC" ]; then
        echo "  SKIP: $svc (not found in deploy/)";
        continue
    fi
    if diff -q "$SRC" "$DST" >/dev/null 2>&1; then
        echo "  OK (unchanged): $svc"
    else
        cp "$SRC" "$DST"
        echo "  INSTALLED: $svc"
    fi
done

systemctl --user daemon-reload
echo "  daemon-reload: done"

for svc in "${SERVICES[@]}"; do
    if systemctl --user is-enabled "$svc" >/dev/null 2>&1; then
        systemctl --user restart "$svc"
        sleep 1
        STATUS=$(systemctl --user is-active "$svc" 2>/dev/null || echo "unknown")
        echo "  $svc: $STATUS"
    fi
done

echo "=== Done. Check: systemctl --user status nina ninajulesgithub --no-pager ==="
