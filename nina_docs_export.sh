#!/bin/bash
# nina_docs_export.sh
# Collects all Space doc files and produces a timestamped docs backup
# Output: ~/nina/exports/nina_docs_backup_YYYYMMDD_HHMMSS.md
# Run manually after any docs/space edit, then upload output to Perplexity Space

set -e

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
EXPORT_DIR="$HOME/nina/exports"
OUTPUT="$EXPORT_DIR/nina_docs_backup${TIMESTAMP}.md"
SPACE_DIR="$HOME/nina/docs/space"
AGENTS_FILE="$HOME/nina/AGENTS.md"

mkdir -p "$EXPORT_DIR"

echo "# NINA Docs Backup — ${TIMESTAMP}" > "$OUTPUT"
echo "# Upload this file to Perplexity NINA DEV Space" >> "$OUTPUT"
echo "" >> "$OUTPUT"

for filepath in "$SPACE_DIR"/*.md; do
    filename=$(basename "$filepath")
    echo "=== FILE: ${filename} ===" >> "$OUTPUT"
    echo "" >> "$OUTPUT"
    cat "$filepath" >> "$OUTPUT"
    echo "" >> "$OUTPUT"
    echo "" >> "$OUTPUT"
done

if [ -f "$AGENTS_FILE" ]; then
    echo "=== FILE: AGENTS.md ===" >> "$OUTPUT"
    echo "" >> "$OUTPUT"
    cat "$AGENTS_FILE" >> "$OUTPUT"
    echo "" >> "$OUTPUT"
fi

echo "✅ Docs backup created: $OUTPUT"
