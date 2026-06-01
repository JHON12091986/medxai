#!/bin/bash
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DATETIME=$(date +"%Y-%m-%d %H:%M:%S")
OUTPUT=~/Downloads/nina_backup_${TIMESTAMP}.md
NINA_DIR=~/nina

echo "# NINA Codebase Backup" > "$OUTPUT"
echo "" >> "$OUTPUT"
echo "**Generated:** ${DATETIME}" >> "$OUTPUT"
echo "**Host:** $(hostname)" >> "$OUTPUT"
echo "**User:** $(whoami)" >> "$OUTPUT"
echo "" >> "$OUTPUT"

echo "## File Index" >> "$OUTPUT"
echo "" >> "$OUTPUT"

find "$NINA_DIR" \( -name "*.py" -o -name "*.sh" \) ! -path "*/.venv/*" ! -path "*/venv/*" ! -path "*/upgrades/backups/*" | sort | while read f; do
    rel="${f#$NINA_DIR/}"
    size=$(wc -l < "$f")
    mtime=$(stat -c "%y" "$f" | cut -d'.' -f1)
    echo "- \`$rel\` — ${size} lines — last modified: ${mtime}" >> "$OUTPUT"
done

echo "" >> "$OUTPUT"
echo "---" >> "$OUTPUT"
echo "" >> "$OUTPUT"
echo "## Source Files" >> "$OUTPUT"
echo "" >> "$OUTPUT"

find "$NINA_DIR" \( -name "*.py" -o -name "*.sh" \) ! -path "*/.venv/*" ! -path "*/venv/*" ! -path "*/upgrades/backups/*" | sort | while read f; do
    rel="${f#$NINA_DIR/}"
    mtime=$(stat -c "%y" "$f" | cut -d'.' -f1)
    size=$(wc -l < "$f")
    echo "### \`$rel\`" >> "$OUTPUT"
    echo "" >> "$OUTPUT"
    echo "> Last modified: ${mtime} | Lines: ${size}" >> "$OUTPUT"
    echo "" >> "$OUTPUT"

    case "$f" in
        *.py) echo '```python' >> "$OUTPUT" ;;
        *.sh) echo '```bash'   >> "$OUTPUT" ;;
        *)    echo '```'       >> "$OUTPUT" ;;
    esac

    cat "$f" >> "$OUTPUT"
    echo "" >> "$OUTPUT"
    echo '```' >> "$OUTPUT"
    echo "" >> "$OUTPUT"
    echo "---" >> "$OUTPUT"
    echo "" >> "$OUTPUT"
done

echo "Backup saved to: $OUTPUT"
echo "Files: $(find "$NINA_DIR" \( -name "*.py" -o -name "*.sh" \) ! -path "*/.venv/*" ! -path "*/venv/*" ! -path "*/upgrades/backups/*" | wc -l)"
