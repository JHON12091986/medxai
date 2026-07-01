#!/bin/bash
NINA_DIR="$HOME/nina"
BACKUP_DIR="$NINA_DIR/upgrades/backups"
mkdir -p "$BACKUP_DIR"

DATETIME=$(date +"%Y-%m-%d %H:%M:%S")
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

LOGBASE_OUTPUT="$BACKUP_DIR/nina_logbase_backup_${TIMESTAMP}.md"

echo "# NINA Logbase Backup" > "$LOGBASE_OUTPUT"
echo "Generated: $DATETIME" >> "$LOGBASE_OUTPUT"
echo "" >> "$LOGBASE_OUTPUT"
echo "## Directory Tree" >> "$LOGBASE_OUTPUT"
echo '```' >> "$LOGBASE_OUTPUT"
tree "$NINA_DIR/logs/" >> "$LOGBASE_OUTPUT" 2>/dev/null || echo "No logs directory" >> "$LOGBASE_OUTPUT"
echo '```' >> "$LOGBASE_OUTPUT"
echo "" >> "$LOGBASE_OUTPUT"
echo "## File Contents" >> "$LOGBASE_OUTPUT"

find "$NINA_DIR/logs/" -type f 2>/dev/null | sort | while read f; do
    rel="${f#$NINA_DIR/}"
    mtime=$(stat -c "%y" "$f" | cut -d'.' -f1)
    size=$(stat -c "%s" "$f")
    total_lines=$(wc -l < "$f")
    
    echo "### $rel" >> "$LOGBASE_OUTPUT"
    echo "Last modified: $mtime" >> "$LOGBASE_OUTPUT"
    echo "Size: $size bytes" >> "$LOGBASE_OUTPUT"
    
    echo '```log' >> "$LOGBASE_OUTPUT"
    if [ "$total_lines" -gt 500 ]; then
        echo "[truncated — showing last 200 lines]" >> "$LOGBASE_OUTPUT"
        tail -n 200 "$f" >> "$LOGBASE_OUTPUT"
    else
        cat "$f" >> "$LOGBASE_OUTPUT"
    fi
    echo '```' >> "$LOGBASE_OUTPUT"
    echo "" >> "$LOGBASE_OUTPUT"
done

echo "NINA logbase backup saved to $LOGBASE_OUTPUT"
