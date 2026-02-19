#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${1:-http://127.0.0.1:8000}"
URL="${BASE_URL%/}/rag/query"

post_json() {
  local payload="$1"
  curl -sS -w "\n%{http_code}" -H "Content-Type: application/json" -d "$payload" "$URL"
}

check_status() {
  local expected="$1"
  local response="$2"
  local body code
  body=$(printf '%s' "$response" | sed '$d')
  code=$(printf '%s' "$response" | tail -n1)

  if [ "$code" != "$expected" ]; then
    echo "Expected HTTP $expected but got $code"
    echo "$body"
    exit 1
  fi

  printf '%s' "$body"
}

echo "[1/3] invalid payload (missing query/chatInput)"
resp=$(post_json '{"sessionId":"smoke"}')
body=$(check_status "422" "$resp")
printf '%s\n' "$body" | head -c 400; printf '\n\n'

echo "[2/3] invalid payload (blank query)"
resp=$(post_json '{"query":"   "}')
body=$(check_status "422" "$resp")
printf '%s\n' "$body" | head -c 400; printf '\n\n'

echo "[3/3] valid payload using alias fields"
resp=$(post_json '{"chatInput":"Mejor bar de pintxos en Bilbao","sessionId":"smoke","lang":"ES"}')
body=$(check_status "200" "$resp")
printf '%s\n' "$body" | head -c 400; printf '\n\n'

echo "Validation smoke test OK: $URL"
