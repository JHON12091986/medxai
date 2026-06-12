#!/usr/bin/env bash
TIMEOUT_SEC="${GEMINI_TIMEOUT:-120}"
LOG_FILE="${HOME}/nina/logs/gemini_wrapper.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
if [ -z "$1" ]; then echo "Usage: $0 'prompt'" >&2; exit 1; fi
echo "[$TIMESTAMP] Starting gemini with ${TIMEOUT_SEC}s timeout" >> "$LOG_FILE"
timeout --kill-after=10 "$TIMEOUT_SEC" gemini "$@"
EXIT_CODE=$?
if [ "$EXIT_CODE" -eq 124 ] || [ "$EXIT_CODE" -eq 137 ]; then
  echo "[$TIMESTAMP] STALL: gemini killed after ${TIMEOUT_SEC}s" >> "$LOG_FILE"
  echo "GEMINI STALL: killed. Switch to Qwen Code." >&2
  exit 1
fi
echo "[$TIMESTAMP] gemini exit $EXIT_CODE" >> "$LOG_FILE"
exit "$EXIT_CODE"
