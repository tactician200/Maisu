#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BASE_URL="${SMOKE_BASE_URL:-http://127.0.0.1:8000}"
QUERY_TEXT="${SMOKE_QUERY_TEXT:-Mejor bar de pintxos en Bilbao}"
RUN_VALIDATION="${SMOKE_VALIDATION:-1}"
RUN_ONBOARDING="${SMOKE_ONBOARDING:-0}"
DB_URL="${SMOKE_DB_URL:-}"

if [ -z "$BASE_URL" ]; then
  echo "SMOKE_BASE_URL is required"
  exit 1
fi

echo "[smoke] RAG query: $BASE_URL"
"$ROOT_DIR/scripts/rag-smoke-test-api.sh" "$BASE_URL" "$QUERY_TEXT"

if [ "$RUN_VALIDATION" = "1" ]; then
  echo "[smoke] RAG validation: $BASE_URL"
  "$ROOT_DIR/scripts/rag-smoke-test-api-validation.sh" "$BASE_URL"
else
  echo "[smoke] Skipping RAG validation (SMOKE_VALIDATION=$RUN_VALIDATION)"
fi

if [ "$RUN_ONBOARDING" = "1" ]; then
  echo "[smoke] Onboarding/user-context: $BASE_URL"
  API_BASE="$BASE_URL" "$ROOT_DIR/scripts/smoke-user-context-onboarding.sh"
else
  echo "[smoke] Skipping onboarding/user-context (SMOKE_ONBOARDING=$RUN_ONBOARDING)"
fi

if [ -n "$DB_URL" ]; then
  echo "[smoke] History embeddings: $DB_URL"
  "$ROOT_DIR/scripts/history-embeddings-smoke.sh" "$DB_URL"
else
  echo "[smoke] Skipping history embeddings (SMOKE_DB_URL not set)"
fi

echo "SMOKE_PASS"
