#!/usr/bin/env bash
# NinaMCP P0 — GitHub Relay Bus aliases
# Source this from ~/.bashrc:  source ~/nina/mcp/aliases.sh
# =============================================================================

# Guard against double-sourcing
[[ -n "$_NINA_MCP_LOADED" ]] && return 0
_NINA_MCP_LOADED=1

NINA_ROOT="${NINA_ROOT:-$HOME/nina}"
NINA_MCP_DIR="$NINA_ROOT/logs/nina_mcp_results"

_nina_mcp_push() {
  # Push results slot to GitHub (non-blocking, best-effort)
  local slot="$1"
  (
    cd "$NINA_ROOT"
    git add "$NINA_MCP_DIR/$slot" > /dev/null 2>&1
    git commit --no-verify -m "mcp: update $slot [skip ci]" > /dev/null 2>&1 || true
    GIT_PUSH_IN_FLIGHT=1 git push origin main --quiet > /dev/null 2>&1 || true
    echo "[nina_mcp] $slot pushed to GitHub (~3-5s propagation)"
  ) &
}

_nina_mcp_write() {
  local slot="$1"
  local content="$2"
  mkdir -p "$NINA_MCP_DIR"
  local ts
  ts=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
  # Wrap in envelope JSON
  printf '{"slot":"%s","ts":"%s","result":%s}\n' \
    "$slot" "$ts" "$content" > "$NINA_MCP_DIR/${slot}.json"
}

# -- nina_exec — run any shell command, capture output ------------------------
nina_exec() {
  if [[ -z "$*" ]]; then
    echo "Usage: nina_exec <command>" >&2
    return 1
  fi
  echo "[nina_mcp] Running: $*"
  local out exit_code
  out=$(cd "$NINA_ROOT" && bash -c "$*" 2>&1) && exit_code=0 || exit_code=$?
  # Escape for JSON
  local escaped
  escaped=$(printf '%s' "$out" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))')
  _nina_mcp_write "exec_result" \
    "{\"cmd\":\"$*\",\"exit_code\":$exit_code,\"output\":$escaped}"
  _nina_mcp_push "exec_result.json"
  echo "[nina_mcp] exec_result.json written (exit=$exit_code)"
}

# -- nina_tail — tail a log file (last N lines) -------------------------------
nina_tail() {
  local logname="${1:-nina_sync}"
  local lines="${2:-100}"
  local logfile="$NINA_ROOT/logs/${logname}.log"
  echo "[nina_mcp] Tailing $logfile (last $lines lines)"
  local out exit_code
  if [[ -f "$logfile" ]]; then
    out=$(tail -n "$lines" "$logfile" 2>&1) && exit_code=0 || exit_code=$?
  else
    out="ERROR: log file not found: $logfile"
    exit_code=1
  fi
  local escaped
  escaped=$(printf '%s' "$out" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))')
  _nina_mcp_write "tail_result" \
    "{\"log\":\"$logname\",\"lines\":$lines,\"exit_code\":$exit_code,\"output\":$escaped}"
  _nina_mcp_push "tail_result.json"
  echo "[nina_mcp] tail_result.json written"
}

# -- nina_diff — git diff (staged + unstaged) ---------------------------------
nina_diff() {
  local ref="${1:-HEAD}"
  echo "[nina_mcp] Git diff vs $ref"
  local out exit_code
  out=$(cd "$NINA_ROOT" && git diff "$ref" 2>&1 && echo '---STAGED---' && git diff --cached "$ref" 2>&1) \
    && exit_code=0 || exit_code=$?
  local escaped
  escaped=$(printf '%s' "$out" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))')
  _nina_mcp_write "diff_result" \
    "{\"ref\":\"$ref\",\"exit_code\":$exit_code,\"diff\":$escaped}"
  _nina_mcp_push "diff_result.json"
  echo "[nina_mcp] diff_result.json written"
}

# -- nina_search — semantic search via ollama ---------------------------------
nina_search() {
  local query="$*"
  if [[ -z "$query" ]]; then
    echo "Usage: nina_search <query>" >&2
    return 1
  fi
  echo "[nina_mcp] Semantic search: $query"
  local out exit_code
  if command -v ollama > /dev/null 2>&1; then
    out=$(cd "$NINA_ROOT" && python3 mcp/search_relay.py "$query" 2>&1) \
      && exit_code=0 || exit_code=$?
  else
    # Fallback: grep-based search
    out=$(cd "$NINA_ROOT" && grep -rn --include='*.py' --include='*.md' -i "$query" \
      --exclude-dir='.git' --exclude-dir='venv' --exclude-dir='logs' \
      | head -50 2>&1) && exit_code=0 || exit_code=$?
  fi
  local escaped_q escaped_o
  escaped_q=$(printf '%s' "$query" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))')
  escaped_o=$(printf '%s' "$out"   | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))')
  _nina_mcp_write "search_result" \
    "{\"query\":$escaped_q,\"exit_code\":$exit_code,\"results\":$escaped_o}"
  _nina_mcp_push "search_result.json"
  echo "[nina_mcp] search_result.json written"
}

# -- nina_status — full health snapshot ---------------------------------------
nina_status() {
  echo "[nina_mcp] Collecting full status snapshot..."
  local svc_active svc_status git_status sha open_prs dirty
  svc_active=$(systemctl --user is-active nina.service 2>/dev/null || echo "unknown")
  svc_status=$(systemctl --user status nina.service --no-pager --lines=20 2>&1 | head -25)
  git_status=$(cd "$NINA_ROOT" && git status --short 2>&1)
  sha=$(cd "$NINA_ROOT" && git rev-parse HEAD 2>/dev/null || echo "none")
  open_prs=$(cd "$NINA_ROOT" && gh pr list --state open --json number --jq 'length' 2>/dev/null || echo "0")
  dirty=$(cd "$NINA_ROOT" && git status --porcelain 2>/dev/null | wc -l | tr -d ' ')
  uptime_info=$(uptime 2>&1)
  disk_info=$(df -h "$NINA_ROOT" 2>&1 | tail -1)
  mem_info=$(free -h 2>&1 | grep Mem)

  local esc_svc esc_git esc_up esc_disk esc_mem
  esc_svc=$(printf '%s' "$svc_status" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))')
  esc_git=$(printf '%s' "$git_status" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))')
  esc_up=$(printf '%s' "$uptime_info" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))')
  esc_disk=$(printf '%s' "$disk_info" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))')
  esc_mem=$(printf '%s' "$mem_info" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))')

  _nina_mcp_write "status_result" \
    "{\"nina_service_active\":\"$svc_active\",\"open_prs\":$open_prs,\"dirty_files\":$dirty,\"sha\":\"$sha\",\"service_status\":$esc_svc,\"git_status\":$esc_git,\"uptime\":$esc_up,\"disk\":$esc_disk,\"mem\":$esc_mem}"
  _nina_mcp_push "status_result.json"
  echo "[nina_mcp] status_result.json written (svc=$svc_active, dirty=$dirty, sha=${sha:0:8})"
}

echo "[nina_mcp] P0 aliases loaded — nina_exec | nina_tail | nina_diff | nina_search | nina_status"
