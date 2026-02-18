#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${1:-http://127.0.0.1:8000}"
QUERY_TEXT="${2:-Mejor bar de pintxos en Bilbao}"
URL="${BASE_URL%/}/rag/query"

if command -v jq >/dev/null 2>&1; then
  PAYLOAD=$(jq -nc --arg q "$QUERY_TEXT" '{query:$q,session_id:"smoke",lang:"es"}')
else
  SAFE_QUERY=$(printf '%s' "$QUERY_TEXT" | sed 's/"/\\"/g')
  PAYLOAD=$(printf '{"query":"%s","session_id":"smoke","lang":"es"}' "$SAFE_QUERY")
fi

RESP=$(curl -sS -w "\n%{http_code}" -H "Content-Type: application/json" -d "$PAYLOAD" "$URL")
BODY=$(printf '%s' "$RESP" | sed '$d')
CODE=$(printf '%s' "$RESP" | tail -n1)

if [ "$CODE" != "200" ]; then
  echo "Smoke test failed: HTTP $CODE"
  echo "$BODY"
  exit 1
fi

echo "Smoke test OK: $URL"
echo "$BODY" | head -c 500
printf '\n'
