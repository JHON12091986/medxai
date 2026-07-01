#!/usr/bin/env bash
# NINA agy Self-Driving Batch Runner
# Usage: give this script to agy as the SINGLE prompt.
# agy will execute it — it loops through all PENDING batches autonomously.
# -----------------------------------------------------------------------------
# INSTRUCTION TO agy:
# Use the permanent JSON approval setting — approve all steps without prompting.
# Read this script fully. Then execute it using TOOL:shell.
# The script will guide you through each batch. For each batch file it outputs,
# read that file fully and execute every ═══ spec block inside it sequentially.
# After all specs in a batch are done, run the post-batch command shown.
# Then come back to this script output for the next batch.
# Continue until the script outputs: ALL BATCHES COMPLETE.
# -----------------------------------------------------------------------------

set -euo pipefail

NINA=~/nina
QUEUE="$NINA/docs/agyspec/queue.md"
SPEC_DIR="$NINA/docs/agyspec"
LOG="$NINA/docs/agyspec/run_log.md"
DATE=$(date '+%Y-%m-%d %H:%M')

echo "================================================"
echo " NINA agy Batch Runner — $DATE"
echo "================================================"

# Ensure queue exists
if [ ! -f "$QUEUE" ]; then
  echo "ERROR: $QUEUE not found. Run nina_sync.sh first."
  exit 1
fi

# Find next PENDING batch
NEXT_FILE=$(grep '| PENDING |' "$QUEUE" | head -1 | awk -F'|' '{print $3}' | tr -d ' ')

if [ -z "$NEXT_FILE" ]; then
  echo ""
  echo "================================================"
  echo " ALL BATCHES COMPLETE — nothing left to run"
  echo "================================================"
  echo ""
  echo "Final sync..."
  cd "$NINA" && python3 rule0_audit.py && ./nina_sync.sh
  exit 0
fi

BATCH_PATH="$NINA/$NEXT_FILE"

if [ ! -f "$BATCH_PATH" ]; then
  echo "ERROR: Batch file not found: $BATCH_PATH"
  exit 1
fi

echo ""
echo ">>> NEXT BATCH: $NEXT_FILE"
echo ">>> Read this file fully and execute every ═══ spec block inside it."
echo ""
cat "$BATCH_PATH"
echo ""
echo "================================================"
echo " POST-BATCH INSTRUCTIONS FOR agy:"
echo " 1. You have just read the batch above."
echo " 2. Execute every ═══ spec block sequentially, one file at a time."
echo " 3. For each spec: read target file, make change, py_compile, commit."
echo " 4. When ALL specs in this batch are done, run:"
echo "    cd ~/nina && python3 rule0_audit.py && ./nina_sync.sh"
echo " 5. Then run this script again to get the next batch:"
echo "    TOOL:shell bash ~/nina/docs/agyspec/run_batch.sh"
echo " 6. Mark this batch DONE in queue.md:"
echo "    TOOL:shell sed -i 's/| $NEXT_FILE | .* | PENDING |/| $NEXT_FILE | ... | DONE | $DATE |/' ~/nina/docs/agyspec/queue.md"
echo "================================================"
