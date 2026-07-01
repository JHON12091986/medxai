#!/usr/bin/env bash
# tools/jules_dedup_guard.sh — Jules pre-flight: abort if open PR already exists for this branch or task ID
# Usage: bash tools/jules_dedup_guard.sh [task_id]

TASK_ID="$1"

if [ -z "$TASK_ID" ]; then
    echo "Usage: $0 [task_id]"
    exit 0 # Safe fallback: no ID provided, skip check
fi

echo "Jules Dedup Guard: Checking if open PR exists for task: $TASK_ID"

# Query open PRs via GitHub CLI
if ! command -v gh &> /dev/null; then
    echo "gh CLI not found. Skipping check."
    exit 0
fi

# Fetch list of open PR titles, bodies, and head branches
PRS=$(gh pr list --state open --json title,body,headRefName 2>/dev/null)
if [ $? -ne 0 ]; then
    echo "Failed to query GitHub PRs. Proceeding with caution."
    exit 0
fi

# Search for the Task ID in the JSON response
DUPLICATE=$(echo "$PRS" | grep -F "$TASK_ID")

if [ -n "$DUPLICATE" ]; then
    echo "⚠️ ABORT: A Pull Request for task $TASK_ID already exists."
    # We exit with code 0 or 1 depending on whether we want to hard-abort the command pipeline.
    # To stop Jules execution cleanly, we can exit with a non-zero code.
    exit 1
else
    echo "No duplicate PR found. Proceeding."
    exit 0
fi
