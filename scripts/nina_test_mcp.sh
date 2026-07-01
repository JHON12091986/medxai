#!/bin/bash
BASE="http://localhost:8080"
echo "═══════════════════════════════════════"
echo " NinaGate MCP Test — $(date '+%H:%M:%S')"
echo "═══════════════════════════════════════"

echo -e "\n[1] /health"
curl -s "$BASE/health" | python3 -m json.tool

echo -e "\n[2] /v1/models"
curl -s "$BASE/v1/models" | python3 -m json.tool

echo -e "\n[3] /v1/chat/completions"
curl -s "$BASE/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{"model":"auto","messages":[{"role":"user","content":"say hi from ninagate in one sentence"}]}' \
  | python3 -m json.tool

echo -e "\n═══════════════════════════════════════"
