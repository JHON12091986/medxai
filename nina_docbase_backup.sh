#!/bin/bash
# nina_docbase_backup.sh
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DEST="$HOME/nina/upgrades/backups/docbase_${TIMESTAMP}"

mkdir -p "$DEST"
if [ -d "$HOME/nina/docs" ]; then
    cp -r "$HOME/nina/docs/"* "$DEST/" 2>/dev/null || true
fi

for f in nina_context.md nina_update_log.md nina_error_register.md; do
    if [ -f "$HOME/nina/$f" ]; then
        cp "$HOME/nina/$f" "$DEST/"
    fi
done

echo "NINA docbase backup saved to $DEST"
