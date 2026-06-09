#!/bin/bash
# nina_codebase_backup.sh
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DEST="$HOME/nina/upgrades/backups/codebase_${TIMESTAMP}"

mkdir -p "$DEST"
rsync -am --include='*/' --include='*.py' --include='*.sh' --exclude='*' \
    --exclude='.env' --exclude='venv/' --exclude='__pycache__/' \
    --exclude='*.pyc' --exclude='*.log' --exclude='data/' --exclude='upgrades/' \
    "$HOME/nina/" "$DEST/"

echo "NINA codebase backup saved to $DEST"
