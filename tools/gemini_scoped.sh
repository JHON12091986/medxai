#!/usr/bin/env bash
TARGET_FILE="$1"
PROMPT="$2"
TIMEOUT_SEC="${GEMINI_TIMEOUT:-120}"
LOG_FILE="${HOME}/nina/logs/gemini_wrapper.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
if [ -z "$TARGET_FILE" ] || [ -z "$PROMPT" ]; then echo "Usage: $0 <file> 'prompt'" >&2; exit 1; fi
if [ ! -f "$TARGET_FILE" ]; then echo "Error: not found: $TARGET_FILE" >&2; exit 1; fi
echo "[$TIMESTAMP] Scoped run — $TARGET_FILE" >> "$LOG_FILE"
TMPDIR_SCOPE=$(mktemp -d)
cp "$TARGET_FILE" "$TMPDIR_SCOPE/"
BASENAME=$(basename "$TARGET_FILE")
cd "$TMPDIR_SCOPE" || exit 1
timeout --kill-after=10 "$TIMEOUT_SEC" gemini -p "$PROMPT $BASENAME"
EXIT_CODE=$?
cd - > /dev/null
rm -rf "$TMPDIR_SCOPE"
if [ "$EXIT_CODE" -eq 124 ] || [ "$EXIT_CODE" -eq 137 ]; then
  echo "[$TIMESTAMP] SCOPED STALL: killed" >> "$LOG_FILE"
  echo "GEMINI SCOPED STALL. Switch to Qwen Code." >&2
  exit 1
fi
echo "[$TIMESTAMP] Scoped done — exit $EXIT_CODE" >> "$LOG_FILE"
exit "$EXIT_CODE"
