#!/bin/bash
set -e

NINA_DIR="$HOME/nina"
BACKUP_DIR="$NINA_DIR/upgrades/backups"
mkdir -p "$BACKUP_DIR"

DATETIME=$(date +"%Y-%m-%d %H:%M:%S")
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# ==============================================================================
# TASK 1 — NINA Logbase Backup
# ==============================================================================
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

# ==============================================================================
# TASK 2 — NINA Docbase Backup
# ==============================================================================
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

# Collect all files
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

echo "NINA docbase backup saved to $DOCBASE_OUTPUT"

# ==============================================================================
# TASK 3 — NINA Codebase Backup
# ==============================================================================
CODEBASE_OUTPUT="$BACKUP_DIR/nina_codebase_backup_${TIMESTAMP}.md"

PY_COUNT=$(find "$NINA_DIR" -type f -name "*.py" ! -path "*/venv/*" ! -path "*/.venv/*" ! -path "*/__pycache__/*" ! -path "*/.git/*" ! -path "*/data/*" ! -path "*/upgrades/*" | wc -l)
SH_COUNT=$(find "$NINA_DIR" -type f -name "*.sh" ! -path "*/venv/*" ! -path "*/.venv/*" ! -path "*/__pycache__/*" ! -path "*/.git/*" ! -path "*/data/*" ! -path "*/upgrades/*" | wc -l)
GIT_HEAD=$(git -C "$NINA_DIR" rev-parse HEAD 2>/dev/null || echo "unknown")
GIT_BRANCH=$(git -C "$NINA_DIR" branch --show-current 2>/dev/null || echo "unknown")

echo "# NINA Codebase Backup" > "$CODEBASE_OUTPUT"
echo "Generated: $DATETIME" >> "$CODEBASE_OUTPUT"
echo "Total .py files: $PY_COUNT | Total .sh files: $SH_COUNT" >> "$CODEBASE_OUTPUT"
echo "Git HEAD: $GIT_HEAD" >> "$CODEBASE_OUTPUT"
echo "Git branch: $GIT_BRANCH" >> "$CODEBASE_OUTPUT"
echo "" >> "$CODEBASE_OUTPUT"

echo "## Directory Tree" >> "$CODEBASE_OUTPUT"
echo '```' >> "$CODEBASE_OUTPUT"
tree "$NINA_DIR/" -I "venv|.venv|__pycache__|*.pyc|*.log|data|upgrades|.git" --prune >> "$CODEBASE_OUTPUT" 2>/dev/null || true
echo '```' >> "$CODEBASE_OUTPUT"
echo "" >> "$CODEBASE_OUTPUT"

echo "## File Contents" >> "$CODEBASE_OUTPUT"

find "$NINA_DIR" -type f \( -name "*.py" -o -name "*.sh" \) \
    ! -path "*/venv/*" ! -path "*/.venv/*" ! -path "*/__pycache__/*" ! -path "*/.git/*" \
    ! -path "*/data/*" ! -path "*/upgrades/*" > /tmp/code_list.txt || true

for f in requirements.txt setup.py pyproject.toml; do
    if [ -f "$NINA_DIR/$f" ]; then
        echo "$NINA_DIR/$f" >> /tmp/code_list.txt
    fi
done

sort /tmp/code_list.txt | while read f; do
    [ -z "$f" ] && continue
    rel="${f#$NINA_DIR/}"
    mtime=$(stat -c "%y" "$f" | cut -d'.' -f1)
    size=$(stat -c "%s" "$f")
    
    echo "### $rel" >> "$CODEBASE_OUTPUT"
    echo "Last modified: $mtime" >> "$CODEBASE_OUTPUT"
    echo "Size: $size bytes" >> "$CODEBASE_OUTPUT"
    
    if [[ "$f" == *.py ]]; then
        echo '```python' >> "$CODEBASE_OUTPUT"
    elif [[ "$f" == *.sh ]]; then
        echo '```bash' >> "$CODEBASE_OUTPUT"
    else
        echo '```' >> "$CODEBASE_OUTPUT"
    fi
    cat "$f" >> "$CODEBASE_OUTPUT"
    echo '```' >> "$CODEBASE_OUTPUT"
    echo "" >> "$CODEBASE_OUTPUT"
done

echo "NINA codebase backup saved to $CODEBASE_OUTPUT"
echo ""
echo "All 3 NINA targeted backups complete:"
echo " - Logbase: $LOGBASE_OUTPUT"
echo " - Docbase: $DOCBASE_OUTPUT"
echo " - Codebase: $CODEBASE_OUTPUT"
