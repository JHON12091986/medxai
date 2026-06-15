#!/usr/bin/env bash
# tools/agy_quota_monitor.sh
# ──────────────────────────────────────────────────────────────────────────────
# Reads agy model usage from its terminal output and writes structured JSON
# to data/agy_quota.json for use by TokenGuard, HybridRouter, and NinaUI.
#
# USAGE:
#   ./tools/agy_quota_monitor.sh              # one-shot update
#   ./tools/agy_quota_monitor.sh --watch      # poll every 60s (run as systemd timer or background job)
#   ./tools/agy_quota_monitor.sh --exhausted  # manually mark quota as exhausted
#
# OUTPUT FORMAT (data/agy_quota.json):
# {
#   "flash_pct": 51,
#   "flash_lite_pct": 3,
#   "pro_pct": 85,
#   "flash_reset_minutes": 365,
#   "pro_reset_minutes": 220,
#   "exhausted": false,
#   "recommended_model": "GEMINI_FLASH_LITE",
#   "updated_at": "2026-06-15T17:26:00+06:00"
# }
# ──────────────────────────────────────────────────────────────────────────────

DATA_FILE="data/agy_quota.json"
mkdir -p data

# ── Manual exhausted flag ─────────────────────────────────────────────────────
if [[ "$1" == "--exhausted" ]]; then
  python3 - <<PYEOF
import json, datetime, pathlib
p = pathlib.Path("$DATA_FILE")
data = json.loads(p.read_text()) if p.exists() else {}
data["exhausted"] = True
data["updated_at"] = datetime.datetime.now().astimezone().isoformat()
p.write_text(json.dumps(data, indent=2))
print("✓ Marked agy quota as exhausted in $DATA_FILE")
PYEOF
  exit 0
fi

# ── Parse current quota from agy output ──────────────────────────────────────
parse_quota() {
  # agy outputs quota info when you run: agy --quota (or similar)
  # We scrape it with a lightweight Python parser
  python3 - <<'PYEOF'
import subprocess, re, json, datetime, pathlib, sys

DATA_FILE = "data/agy_quota.json"

# Try to get quota from agy
try:
    result = subprocess.run(
        ["agy", "--quota"],
        capture_output=True, text=True, timeout=10
    )
    raw = result.stdout + result.stderr
except Exception as e:
    # agy not available or no --quota flag — try reading last known state
    p = pathlib.Path(DATA_FILE)
    if p.exists():
        print(f"agy unavailable ({e}), keeping last known quota state")
        sys.exit(0)
    # Write zeros as safe default
    raw = ""

# Parse percentage lines: "Flash  ...  51%  Resets: 8:21 PM (6h 5m)"
flash_pct      = 0
flash_lite_pct = 0
pro_pct        = 0
flash_reset_m  = 9999
pro_reset_m    = 9999

for line in raw.splitlines():
    pct_m = re.search(r"(\d+)%", line)
    reset_m = re.search(r"\((\d+)h\s*(\d+)m\)", line)
    if not pct_m:
        continue
    pct = int(pct_m.group(1))
    mins = (int(reset_m.group(1)) * 60 + int(reset_m.group(2))) if reset_m else 9999
    line_lower = line.lower()
    if "flash lite" in line_lower:
        flash_lite_pct = pct
    elif "flash" in line_lower:
        flash_pct = pct
        flash_reset_m = mins
    elif "pro" in line_lower:
        pro_pct = pct
        pro_reset_m = mins

# Determine recommended model
if pro_pct < 50:
    recommended = "AGY_PRO"
elif flash_pct < 70:
    recommended = "AGY_FLASH"
elif flash_lite_pct < 80:
    recommended = "AGY_FLASH_LITE"
else:
    recommended = "NINAGATE_CLOUD"  # agy quotas tight → use NinaGate

exhausted = (flash_pct >= 95 and flash_lite_pct >= 95 and pro_pct >= 95)

out = {
    "flash_pct":         flash_pct,
    "flash_lite_pct":    flash_lite_pct,
    "pro_pct":           pro_pct,
    "flash_reset_minutes":  flash_reset_m,
    "pro_reset_minutes":    pro_reset_m,
    "exhausted":         exhausted,
    "recommended_model": recommended,
    "updated_at":        datetime.datetime.now().astimezone().isoformat(),
}

pathlib.Path(DATA_FILE).write_text(json.dumps(out, indent=2))
print(json.dumps(out, indent=2))
PYEOF
}

# ── Watch mode ────────────────────────────────────────────────────────────────
if [[ "$1" == "--watch" ]]; then
  echo "agy_quota_monitor: watching (polling every 60s) → $DATA_FILE"
  while true; do
    parse_quota
    sleep 60
  done
else
  parse_quota
fi
