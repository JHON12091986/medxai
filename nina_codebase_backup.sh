#!/bin/bash
NINA_DIR="$HOME/nina"
BACKUP_DIR="$NINA_DIR/upgrades/backups"
mkdir -p "$BACKUP_DIR"

DATETIME=$(date +"%Y-%m-%d %H:%M:%S")
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

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
rm -f /tmp/code_list.txt

echo "NINA codebase backup saved to $CODEBASE_OUTPUT"
