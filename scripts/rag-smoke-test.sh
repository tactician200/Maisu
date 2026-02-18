#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 <QUERY_ENDPOINT_URL> [query]"
  echo "Example: $0 https://[your-host]/rag/query 'Mejor bar de pintxos en Bilbao'"
  exit 1
fi

QUERY_URL="$1"
QUERY_TEXT="${2:-Mejor bar de pintxos en Bilbao}"

if command -v jq >/dev/null 2>&1; then
  PAYLOAD=$(jq -nc --arg q "$QUERY_TEXT" '{query:$q, top_k:3}')
else
  SAFE_QUERY=$(printf '%s' "$QUERY_TEXT" | sed 's/"/\\"/g')
  PAYLOAD=$(printf '{"query":"%s","top_k":3}' "$SAFE_QUERY")
fi

RESP=$(curl -sS -w "\n%{http_code}" -H "Content-Type: application/json" -d "$PAYLOAD" "$QUERY_URL")
BODY=$(printf '%s' "$RESP" | sed '$d')
CODE=$(printf '%s' "$RESP" | tail -n1)

if [ "$CODE" != "200" ]; then
  echo "Smoke test failed: HTTP $CODE"
  echo "Response body: $BODY"
  exit 1
fi

if command -v jq >/dev/null 2>&1; then
  echo "$BODY" | jq -e . >/dev/null || {
    echo "Smoke test failed: response is not valid JSON"
    echo "Response body: $BODY"
    exit 1
  }
fi

if [ -z "$BODY" ]; then
  echo "Smoke test failed: empty response body"
  exit 1
fi

echo "Smoke test OK: $QUERY_URL"
echo "Response (truncated):"
echo "$BODY" | head -c 400
printf '\n'
