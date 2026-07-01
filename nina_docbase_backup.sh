#!/bin/bash
NINA_DIR="$HOME/nina"
BACKUP_DIR="$NINA_DIR/upgrades/backups"
mkdir -p "$BACKUP_DIR"

DATETIME=$(date +"%Y-%m-%d %H:%M:%S")
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

DOCBASE_OUTPUT="$BACKUP_DIR/nina_docbase_backup_${TIMESTAMP}.md"

echo "# NINA Docbase Backup" > "$DOCBASE_OUTPUT"
echo "Generated: $DATETIME" >> "$DOCBASE_OUTPUT"
echo "" >> "$DOCBASE_OUTPUT"
echo "## Directory Tree" >> "$DOCBASE_OUTPUT"
echo '```' >> "$DOCBASE_OUTPUT"
tree "$NINA_DIR/docs/" >> "$DOCBASE_OUTPUT" 2>/dev/null || echo "No docs directory" >> "$DOCBASE_OUTPUT"
echo '```' >> "$DOCBASE_OUTPUT"
echo "" >> "$DOCBASE_OUTPUT"
echo "Included Root Files:" >> "$DOCBASE_OUTPUT"
for f in nina_context.md nina_update_log.md nina_latest.md AGENTS.md README.md juleslock.txt jules_lock.txt; do
    if [ -f "$NINA_DIR/$f" ]; then
        echo "- $f" >> "$DOCBASE_OUTPUT"
    fi
done
echo "" >> "$DOCBASE_OUTPUT"
echo "## File Contents" >> "$DOCBASE_OUTPUT"

DOC_FILES=$(find "$NINA_DIR/docs/" -type f 2>/dev/null | sort)
ROOT_FILES=""
for f in nina_context.md nina_update_log.md nina_latest.md AGENTS.md README.md juleslock.txt jules_lock.txt; do
    if [ -f "$NINA_DIR/$f" ]; then
        ROOT_FILES="$ROOT_FILES $NINA_DIR/$f"
    fi
done

echo "$DOC_FILES" | grep -v '^$' > /tmp/doc_list.txt || true
for f in $ROOT_FILES; do
    echo "$f" >> /tmp/doc_list.txt
done

sort /tmp/doc_list.txt | while read f; do
    [ -z "$f" ] && continue
    rel="${f#$NINA_DIR/}"
    mtime=$(stat -c "%y" "$f" | cut -d'.' -f1)
    size=$(stat -c "%s" "$f")
    
    echo "### $rel" >> "$DOCBASE_OUTPUT"
    echo "Last modified: $mtime" >> "$DOCBASE_OUTPUT"
    echo "Size: $size bytes" >> "$DOCBASE_OUTPUT"
    echo '```markdown' >> "$DOCBASE_OUTPUT"
    cat "$f" >> "$DOCBASE_OUTPUT"
    echo '```' >> "$DOCBASE_OUTPUT"
    echo "" >> "$DOCBASE_OUTPUT"
done
rm -f /tmp/doc_list.txt

echo "NINA docbase backup saved to $DOCBASE_OUTPUT"
