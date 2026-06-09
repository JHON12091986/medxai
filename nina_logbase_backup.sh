#!/bin/bash
# nina_logbase_backup.sh
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DEST="$HOME/nina/upgrades/backups/logbase_${TIMESTAMP}"

mkdir -p "$DEST"
if [ -d "$HOME/nina/logs" ]; then
    cp -r "$HOME/nina/logs/"* "$DEST/" 2>/dev/null || true
fi

echo "NINA logbase backup saved to $DEST"
