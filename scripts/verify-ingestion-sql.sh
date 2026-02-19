#!/usr/bin/env bash
set -euo pipefail

# One-command verification for ingestion SQL checks.
# Safe mode: read-only transaction, SELECT-only queries.

DB_URL="${SUPABASE_DB_URL:-${DATABASE_URL:-}}"

if [ -z "$DB_URL" ]; then
  cat <<'EOF'
Usage:
  SUPABASE_DB_URL='postgresql://...' scripts/verify-ingestion-sql.sh

Environment:
  SUPABASE_DB_URL   Preferred Postgres connection string
  DATABASE_URL      Fallback connection string (used if SUPABASE_DB_URL is unset)

Assumptions:
  - The target DB contains tables: places, places_embeddings, historia_vasca
  - places_embeddings uses source_type values: 'place' and 'history'
  - psql is installed and network access to the DB is available
EOF
  exit 1
fi

if ! command -v psql >/dev/null 2>&1; then
  echo "ERROR: psql is required but not found in PATH." >&2
  exit 1
fi

SQL=$(cat <<'SQL_EOF'
SET TRANSACTION READ ONLY;

WITH
counts AS (
  SELECT
    (SELECT COUNT(*) FROM places) AS places_count,
    (SELECT COUNT(*) FROM places_embeddings WHERE source_type = 'place') AS place_embeddings_count,
    (SELECT COUNT(*) FROM historia_vasca) AS historia_count,
    (SELECT COUNT(*) FROM places_embeddings WHERE source_type = 'history') AS history_embeddings_count
),
missing AS (
  SELECT COUNT(*) AS missing_count
  FROM places p
  LEFT JOIN places_embeddings pe
    ON pe.source_id = p.id
   AND pe.source_type = 'place'
  WHERE pe.id IS NULL
),
duplicates AS (
  SELECT
    COUNT(*) AS duplicate_source_ids,
    COALESCE(MAX(embeddings_per_place), 0) AS max_duplicate_count
  FROM (
    SELECT source_id, COUNT(*) AS embeddings_per_place
    FROM places_embeddings
    WHERE source_type = 'place'
    GROUP BY source_id
    HAVING COUNT(*) > 1
  ) d
)
SELECT
  c.places_count,
  c.place_embeddings_count,
  m.missing_count,
  d.duplicate_source_ids,
  d.max_duplicate_count,
  c.historia_count,
  c.history_embeddings_count,
  CASE WHEN c.historia_count > c.history_embeddings_count THEN 1 ELSE 0 END AS history_gap_indicator
FROM counts c
CROSS JOIN missing m
CROSS JOIN duplicates d;
SQL_EOF
)

RESULT=$(psql "$DB_URL" -X -v ON_ERROR_STOP=1 -At -F '|' <<SQL_EOF
BEGIN;
${SQL}
COMMIT;
SQL_EOF
)

IFS='|' read -r PLACES_COUNT PLACE_EMBEDDINGS_COUNT MISSING_COUNT DUP_SOURCE_IDS MAX_DUP HISTORIA_COUNT HISTORY_EMBEDDINGS_COUNT HISTORY_GAP_INDICATOR <<< "$RESULT"

coverage_status="PASS"
missing_status="PASS"
duplicates_status="PASS"
history_status="OK"
overall_status="PASS"

if [ "$PLACE_EMBEDDINGS_COUNT" -lt "$PLACES_COUNT" ]; then
  coverage_status="FAIL"
  overall_status="FAIL"
fi

if [ "$MISSING_COUNT" -ne 0 ]; then
  missing_status="FAIL"
  overall_status="FAIL"
fi

if [ "$DUP_SOURCE_IDS" -ne 0 ]; then
  duplicates_status="FAIL"
  overall_status="FAIL"
fi

if [ "$HISTORY_GAP_INDICATOR" -eq 1 ]; then
  history_status="GAP"
fi

printf 'Ingestion verification summary\n'
printf '--------------------------------\n'
printf '[%s] coverage (places vs place embeddings): %s vs %s\n' "$coverage_status" "$PLACES_COUNT" "$PLACE_EMBEDDINGS_COUNT"
printf '[%s] missing embeddings rows: %s\n' "$missing_status" "$MISSING_COUNT"
printf '[%s] duplicate place embeddings (source_id): %s (max dup count: %s)\n' "$duplicates_status" "$DUP_SOURCE_IDS" "$MAX_DUP"
printf '[%s] history coverage gap indicator: %s (historia rows: %s, history embeddings: %s)\n' "$history_status" "$HISTORY_GAP_INDICATOR" "$HISTORIA_COUNT" "$HISTORY_EMBEDDINGS_COUNT"
printf '--------------------------------\n'
printf 'OVERALL: %s\n' "$overall_status"

if [ "$overall_status" != "PASS" ]; then
  exit 2
fi
