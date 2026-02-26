#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 <SUPABASE_DB_URL>"
  exit 1
fi

DB_URL="$1"
HISTORY_TABLE_NAME="${HISTORY_TABLE_NAME:-historia_vasca}"
EMBEDDINGS_TABLE_NAME="${EMBEDDINGS_TABLE_NAME:-places_embeddings}"

run_sql_scalar() {
  local sql="$1"
  if command -v psql >/dev/null 2>&1; then
    psql "$DB_URL" -Atc "$sql"
    return
  fi

  local py_cmd="python3"
  if [ -x "$(dirname "$0")/../backend/.venv/bin/python" ]; then
    py_cmd="$(dirname "$0")/../backend/.venv/bin/python"
  fi

  PY_DB_URL="$DB_URL" PY_SQL="$sql" "$py_cmd" - <<'PY'
import os
import psycopg

conn = psycopg.connect(os.environ["PY_DB_URL"])
try:
    with conn.cursor() as cur:
        cur.execute(os.environ["PY_SQL"])
        row = cur.fetchone()
        print(row[0] if row else "")
finally:
    conn.close()
PY
}

table_exists() {
  local tname="$1"
  local count
  count=$(run_sql_scalar "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public' AND table_name='${tname}';")
  [ "${count:-0}" -gt 0 ]
}

echo "[1/2] Checking history embedding coverage"
if ! table_exists "$HISTORY_TABLE_NAME"; then
  echo "SKIP: history table '$HISTORY_TABLE_NAME' does not exist (set HISTORY_TABLE_NAME to override)"
  exit 0
fi
if ! table_exists "$EMBEDDINGS_TABLE_NAME"; then
  echo "SKIP: embeddings table '$EMBEDDINGS_TABLE_NAME' does not exist (set EMBEDDINGS_TABLE_NAME to override)"
  exit 0
fi

COUNTS=$(run_sql_scalar "SELECT COUNT(*) || ',' || (SELECT COUNT(*) FROM ${EMBEDDINGS_TABLE_NAME} WHERE source_type='history') FROM ${HISTORY_TABLE_NAME};")
HISTORIA_COUNT="${COUNTS%,*}"
HISTORY_EMBED_COUNT="${COUNTS#*,}"

echo "${HISTORY_TABLE_NAME} rows: $HISTORIA_COUNT"
echo "history embeddings (${EMBEDDINGS_TABLE_NAME}): $HISTORY_EMBED_COUNT"

if [ "$HISTORIA_COUNT" -gt 0 ] && [ "$HISTORY_EMBED_COUNT" -eq 0 ]; then
  echo "FAIL: No history embeddings found"
  exit 1
fi

echo "[2/2] Checking retrieval reachability via match_places_embeddings(filter=history)"
FUNC_EXISTS=$(run_sql_scalar "SELECT COUNT(*) FROM pg_proc WHERE proname='match_places_embeddings';")
if [ "${FUNC_EXISTS:-0}" -eq 0 ]; then
  echo "SKIP: function match_places_embeddings not found"
  exit 0
fi

MATCH_COUNT=$(run_sql_scalar "WITH sample AS (SELECT embedding FROM ${EMBEDDINGS_TABLE_NAME} WHERE source_type='history' ORDER BY created_at DESC LIMIT 1) SELECT COUNT(*) FROM match_places_embeddings((SELECT embedding FROM sample), 3, '{\"source_type\":\"history\"}'::jsonb);")

echo "history matches returned: $MATCH_COUNT"

if [ "$HISTORY_EMBED_COUNT" -gt 0 ] && [ "$MATCH_COUNT" -eq 0 ]; then
  echo "FAIL: history embeddings exist but retrieval returned 0"
  exit 1
fi

echo "History embeddings smoke test OK"
