#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 <SUPABASE_DB_URL> [ARTIFACT_DIR]"
  exit 1
fi

DB_URL="$1"
ARTIFACT_DIR="${2:-artifacts/2026-02-23}"
EVENTS_TABLE_NAME="${EVENTS_TABLE_NAME:-events}"
EMBEDDINGS_TABLE_NAME="${EMBEDDINGS_TABLE_NAME:-places_embeddings}"

mkdir -p "$ARTIFACT_DIR"
LOG_FILE="$ARTIFACT_DIR/events-hybrid-smoke.log"
SUMMARY_FILE="$ARTIFACT_DIR/events-hybrid-smoke-summary.json"

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

status="PASS"
skip_reason=""

DB_CHECK_ERROR=""
if ! DB_CHECK=$(run_sql_scalar "SELECT 1;" 2>&1); then
  status="FAIL"
  DB_CHECK_ERROR="$DB_CHECK"
fi

{
  echo "=== Events hybrid smoke test ==="
  echo "db_url: [REDACTED]"
  echo "events_table: $EVENTS_TABLE_NAME"
  echo "embeddings_table: $EMBEDDINGS_TABLE_NAME"
  echo

  echo "[1/3] SQL upcoming events for Bilbao/Bizkaia sorted by date"
  if [ "$status" = "FAIL" ] && [ -n "$DB_CHECK_ERROR" ]; then
    echo "FAIL: database connectivity check failed"
    echo "$DB_CHECK_ERROR"
  elif ! table_exists "$EVENTS_TABLE_NAME"; then
    echo "FAIL: events table '$EVENTS_TABLE_NAME' not found"
    status="FAIL"
  else
    CHECK1=$(run_sql_scalar "WITH rows AS (SELECT id, title, start_at FROM ${EVENTS_TABLE_NAME} WHERE status='scheduled' AND start_at >= NOW() AND (municipality ILIKE 'bilbao' OR region ILIKE 'bizkaia') ORDER BY start_at ASC LIMIT 20), ordered AS (SELECT start_at, LEAD(start_at) OVER (ORDER BY start_at) AS next_start FROM rows) SELECT COALESCE((SELECT COUNT(*) FROM rows),0)::text || ',' || COALESCE((SELECT BOOL_AND(next_start IS NULL OR start_at <= next_start) FROM ordered), true)::text;")
    UPCOMING_COUNT="${CHECK1%,*}"
    SORTED_OK="${CHECK1#*,}"

    echo "upcoming_count: $UPCOMING_COUNT"
    echo "sorted_ok: $SORTED_OK"

    if [ "${UPCOMING_COUNT:-0}" -le 0 ]; then
      echo "FAIL: no upcoming events found for Bilbao/Bizkaia"
      status="FAIL"
    elif [ "${SORTED_OK}" != "t" ] && [ "${SORTED_OK}" != "true" ]; then
      echo "FAIL: upcoming events query not sorted by date"
      status="FAIL"
    else
      echo "PASS: upcoming events found and sorted"
    fi
  fi

  echo
  echo "[2/3] Response-ready snippet transformation"
  if [ "$status" = "PASS" ]; then
    SNIPPET_COUNT=$(run_sql_scalar "WITH rows AS (SELECT title, description, start_at, COALESCE(location_text, municipality, region, 'Bilbao/Bizkaia') AS location_hint FROM ${EVENTS_TABLE_NAME} WHERE status='scheduled' AND start_at >= NOW() AND (municipality ILIKE 'bilbao' OR region ILIKE 'bizkaia') ORDER BY start_at ASC LIMIT 20), snippets AS (SELECT TRIM(title) || ' — ' || TO_CHAR(start_at AT TIME ZONE 'Europe/Madrid', 'YYYY-MM-DD HH24:MI') || ' (' || TRIM(location_hint) || ')' || CASE WHEN description IS NOT NULL AND LENGTH(TRIM(description)) > 0 THEN ': ' || LEFT(TRIM(description), 180) ELSE '' END AS snippet FROM rows) SELECT COUNT(*) FROM snippets WHERE LENGTH(snippet) >= 25;")

    SAMPLE_SNIPPET=$(run_sql_scalar "WITH rows AS (SELECT title, description, start_at, COALESCE(location_text, municipality, region, 'Bilbao/Bizkaia') AS location_hint FROM ${EVENTS_TABLE_NAME} WHERE status='scheduled' AND start_at >= NOW() AND (municipality ILIKE 'bilbao' OR region ILIKE 'bizkaia') ORDER BY start_at ASC LIMIT 20), snippets AS (SELECT TRIM(title) || ' — ' || TO_CHAR(start_at AT TIME ZONE 'Europe/Madrid', 'YYYY-MM-DD HH24:MI') || ' (' || TRIM(location_hint) || ')' || CASE WHEN description IS NOT NULL AND LENGTH(TRIM(description)) > 0 THEN ': ' || LEFT(TRIM(description), 180) ELSE '' END AS snippet FROM rows) SELECT snippet FROM snippets WHERE LENGTH(snippet) >= 25 LIMIT 1;")

    echo "snippet_ready_count: $SNIPPET_COUNT"
    if [ "${SNIPPET_COUNT:-0}" -le 0 ]; then
      echo "FAIL: no event could be transformed to response-ready snippet"
      status="FAIL"
    else
      echo "PASS: at least one response-ready snippet generated"
      echo "sample_snippet: ${SAMPLE_SNIPPET}"
    fi
  else
    echo "SKIP: step 1 failed"
  fi

  echo
  echo "[3/3] Semantic retrieval filtered by event metadata (type='event')"
  if [ -n "$DB_CHECK_ERROR" ]; then
    echo "SKIP: semantic check skipped because DB connection failed"
    skip_reason="db connectivity failed"
  elif ! table_exists "$EMBEDDINGS_TABLE_NAME"; then
    echo "SKIP: embeddings table '$EMBEDDINGS_TABLE_NAME' not found"
    skip_reason="embeddings table missing"
  else
    EVENT_EMBED_COUNT=$(run_sql_scalar "SELECT COUNT(*) FROM ${EMBEDDINGS_TABLE_NAME} WHERE source_type='event';")
    echo "event_embeddings_count: $EVENT_EMBED_COUNT"

    if [ "${EVENT_EMBED_COUNT:-0}" -le 0 ]; then
      echo "SKIP: no event embeddings found (source_type='event')"
      skip_reason="no event embeddings"
    else
      FUNC_EXISTS=$(run_sql_scalar "SELECT COUNT(*) FROM pg_proc WHERE proname='match_places_embeddings';")
      if [ "${FUNC_EXISTS:-0}" -eq 0 ]; then
        echo "SKIP: function match_places_embeddings not found"
        skip_reason="match function missing"
      else
        MATCH_COUNT=$(run_sql_scalar "WITH sample AS (SELECT embedding FROM ${EMBEDDINGS_TABLE_NAME} WHERE source_type='event' ORDER BY created_at DESC LIMIT 1) SELECT COUNT(*) FROM match_places_embeddings((SELECT embedding FROM sample), 5, '{\"type\":\"event\"}'::jsonb);")
        echo "event_filtered_match_count: $MATCH_COUNT"
        if [ "${MATCH_COUNT:-0}" -le 0 ]; then
          echo "FAIL: event embeddings exist but filtered semantic retrieval returned 0"
          status="FAIL"
        else
          echo "PASS: filtered semantic retrieval returned >=1 event candidate"
        fi
      fi
    fi
  fi

  echo
  if [ "$status" = "FAIL" ]; then
    echo "SMOKE_FAIL"
  elif [ -n "$skip_reason" ]; then
    echo "SMOKE_PASS_WITH_SKIP: $skip_reason"
  else
    echo "SMOKE_PASS"
  fi
} | tee "$LOG_FILE"

python3 - <<PY
import json
from pathlib import Path

summary = {
    "status": "${status}",
    "skip_reason": "${skip_reason}",
    "events_table": "${EVENTS_TABLE_NAME}",
    "embeddings_table": "${EMBEDDINGS_TABLE_NAME}",
    "log_file": "${LOG_FILE}",
}
Path("${SUMMARY_FILE}").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Summary written: ${SUMMARY_FILE}")
PY

if [ "$status" = "FAIL" ]; then
  exit 1
fi

exit 0
