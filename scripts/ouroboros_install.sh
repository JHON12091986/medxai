#!/usr/bin/env bash
# =============================================================================
# NINA OUROBOROS INSTALL — scripts/ouroboros_install.sh
# =============================================================================
# One-time setup script. Run once to make the Ouroboros loop permanent.
# After this, it starts automatically on every login while the laptop is on.
#
# Usage:
#   bash ~/nina/scripts/ouroboros_install.sh
# =============================================================================

set -euo pipefail

NINA_DIR="${HOME}/nina"
SERVICE_SRC="${NINA_DIR}/deploy/ouroboros.service"
SERVICE_DST="${HOME}/.config/systemd/user/nina-ouroboros.service"

echo "[ouroboros-install] Setting up NINA Ouroboros permanent loop..."

# 1. Make scripts executable
chmod +x "${NINA_DIR}/scripts/ouroboros_loop.sh"
chmod +x "${NINA_DIR}/scripts/ouroboros_watchdog.sh"
echo "[ouroboros-install] ✓ Scripts made executable."

# 2. Create required directories
mkdir -p "${NINA_DIR}/logs" "${NINA_DIR}/data"
echo "[ouroboros-install] ✓ Directories created."

# 3. Install systemd --user service
mkdir -p "$(dirname ${SERVICE_DST})"
cp "${SERVICE_SRC}" "${SERVICE_DST}"
systemctl --user daemon-reload
systemctl --user enable nina-ouroboros.service
echo "[ouroboros-install] ✓ systemd --user service installed and enabled."

# 4. Enable lingering so service survives logout (optional — comment out if not wanted)
# loginctl enable-linger "${USER}"
# echo "[ouroboros-install] ✓ loginctl linger enabled."

# 5. Start now
systemctl --user start nina-ouroboros.service
echo "[ouroboros-install] ✓ Service started."

# 6. Show status
echo ""
echo "=== OUROBOROS STATUS ==="
systemctl --user status nina-ouroboros.service --no-pager || true
echo ""
echo "[ouroboros-install] DONE."
echo "Loop logs : ${NINA_DIR}/logs/ouroboros_loop.log"
echo "Watchdog  : ${NINA_DIR}/logs/ouroboros_watchdog.log"
echo "Digest    : ${NINA_DIR}/data/ouroboros_digest.md"
echo ""
echo "To suspend the loop:"
echo "  echo 'MANUAL_SUSPEND' > ${NINA_DIR}/data/ouroboros_suspended.flag"
echo "To resume:"
echo "  rm ${NINA_DIR}/data/ouroboros_suspended.flag"
echo "To stop permanently:"
echo "  systemctl --user stop nina-ouroboros.service"
echo "  systemctl --user disable nina-ouroboros.service"
