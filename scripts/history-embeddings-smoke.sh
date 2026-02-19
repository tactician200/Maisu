#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 <SUPABASE_DB_URL>"
  exit 1
fi

DB_URL="$1"

echo "[1/2] Checking history embedding coverage"
COUNTS=$(psql "$DB_URL" -Atc "SELECT COUNT(*) || ',' || (SELECT COUNT(*) FROM places_embeddings WHERE source_type='history') FROM historia_vasca;")
HISTORIA_COUNT="${COUNTS%,*}"
HISTORY_EMBED_COUNT="${COUNTS#*,}"

echo "historia_vasca rows: $HISTORIA_COUNT"
echo "history embeddings: $HISTORY_EMBED_COUNT"

if [ "$HISTORIA_COUNT" -gt 0 ] && [ "$HISTORY_EMBED_COUNT" -eq 0 ]; then
  echo "FAIL: No history embeddings found"
  exit 1
fi

echo "[2/2] Checking retrieval reachability via match_places_embeddings(filter=history)"
MATCH_COUNT=$(psql "$DB_URL" -Atc "WITH sample AS (SELECT embedding FROM places_embeddings WHERE source_type='history' ORDER BY created_at DESC LIMIT 1) SELECT COUNT(*) FROM match_places_embeddings((SELECT embedding FROM sample), 3, '{\"source_type\":\"history\"}'::jsonb);")

echo "history matches returned: $MATCH_COUNT"

if [ "$HISTORY_EMBED_COUNT" -gt 0 ] && [ "$MATCH_COUNT" -eq 0 ]; then
  echo "FAIL: history embeddings exist but retrieval returned 0"
  exit 1
fi

echo "History embeddings smoke test OK"
