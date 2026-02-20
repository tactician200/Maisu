#!/usr/bin/env bash
set -euo pipefail

API_BASE="${API_BASE:-http://127.0.0.1:8000}"
SESSION_ID="${SESSION_ID:-ops-smoke-$(date +%s)}"

echo "[1/5] PUT /user-context/$SESSION_ID"
curl -fsS -X PUT "$API_BASE/user-context/$SESSION_ID" \
  -H "Content-Type: application/json" \
  -d '{"name":"Ane","language":"es","preferences":{"tone":"concise","style":"paragraph","interests":["pintxos"]}}' | jq .

echo "[2/5] GET /user-context/$SESSION_ID"
curl -fsS "$API_BASE/user-context/$SESSION_ID" | jq .

echo "[3/5] POST /rag/query (inherits stored context, includes onboarding_next if profile incomplete)"
curl -fsS -X POST "$API_BASE/rag/query" \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"Recomiéndame 2 planes en Bilbao\",\"session_id\":\"$SESSION_ID\"}" | jq '{provider,fallback_used,latency_ms,citations_count:(.citations|length),onboarding_next,answer}'

echo "[4/5] POST /rag/query (explicit override: name/lang/tone)"
curl -fsS -X POST "$API_BASE/rag/query" \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"Recomiéndame algo cultural\",\"session_id\":\"$SESSION_ID\",\"name\":\"Iker\",\"lang\":\"en\",\"tone\":\"detailed\"}" | jq '{provider,fallback_used,onboarding_next,answer}'

echo "[5/5] POST /rag/query (control without session_id)"
curl -fsS -X POST "$API_BASE/rag/query" \
  -H "Content-Type: application/json" \
  -d '{"query":"Recomiéndame 2 planes en Bilbao"}' | jq '{provider,fallback_used,latency_ms,citations_count:(.citations|length),answer}'

echo "SMOKE_OK session_id=$SESSION_ID"
