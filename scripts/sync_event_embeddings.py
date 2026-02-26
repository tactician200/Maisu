#!/usr/bin/env python3
"""Sync `events` rows into `places_embeddings` with source_type='event'.

Features:
- Deterministic content builder from event fields.
- Metadata payload for event retrieval filters.
- Safe dry-run mode when embedding provider keys are missing.
- Idempotent upsert semantics (delete existing event embedding, then insert current one).

Usage examples:
  python scripts/sync_event_embeddings.py --db-url "postgresql://user:pass@host:5432/db"
  python scripts/sync_event_embeddings.py --db-url "postgresql://..." --dry-run
  python scripts/sync_event_embeddings.py --db-url "postgresql://..." --limit 50
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from typing import Any

DEFAULT_MODEL = "text-embedding-3-small"


@dataclass
class EventRow:
    id: str
    title: str
    description: str | None
    event_type: str | None
    municipality: str | None
    region: str | None
    status: str | None
    start_at: datetime | None
    end_at: datetime | None
    tags: list[str] | None
    source_url: str | None
    place_id: str | None


def normalize_text(value: str | None) -> str:
    if not value:
        return ""
    return " ".join(value.split())


def iso(value: datetime | None) -> str:
    return value.isoformat() if value else ""


def build_content(event: EventRow) -> str:
    """Deterministic, stable content used to generate embeddings."""
    tags = ", ".join(event.tags or [])
    lines = [
        f"Title: {normalize_text(event.title)}",
        f"Description: {normalize_text(event.description)}",
        f"Municipality: {normalize_text(event.municipality)}",
        f"Region: {normalize_text(event.region)}",
        f"Start: {iso(event.start_at)}",
        f"End: {iso(event.end_at)}",
        f"Tags: {normalize_text(tags)}",
    ]
    return "\n".join(lines)


def build_metadata(event: EventRow) -> dict[str, Any]:
    return {
        "type": "event",
        "event_id": str(event.id),
        "event_type": event.event_type,
        "municipality": event.municipality,
        "region": event.region,
        "status": event.status,
        "start_at": iso(event.start_at) or None,
        "end_at": iso(event.end_at) or None,
        "source_url": event.source_url,
    }


def fetch_embedding(text: str, api_key: str, model: str) -> list[float]:
    payload = json.dumps({"input": text, "model": model}).encode("utf-8")
    req = urllib.request.Request(
        "https://api.openai.com/v1/embeddings",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"Embedding API HTTP {e.code}: {body}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Embedding API request failed: {e}") from e

    vector = data.get("data", [{}])[0].get("embedding")
    if not vector or not isinstance(vector, list):
        raise RuntimeError("Embedding API response missing data[0].embedding")
    return vector


def upsert_event_embedding(conn: Any, event: EventRow, content: str, metadata: dict[str, Any], embedding: list[float]) -> None:
    embedding_literal = "[" + ",".join(str(x) for x in embedding) + "]"
    with conn.cursor() as cur:
        cur.execute(
            """
            WITH deleted AS (
                DELETE FROM places_embeddings
                WHERE source_type = 'event'
                  AND metadata->>'event_id' = %s
            )
            INSERT INTO places_embeddings (
                content,
                embedding,
                metadata,
                source_type,
                source_id
            ) VALUES (
                %s,
                %s::vector,
                %s::jsonb,
                'event',
                %s::uuid
            )
            """,
            (
                str(event.id),
                content,
                embedding_literal,
                json.dumps(metadata),
                event.place_id,
            ),
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync event embeddings into places_embeddings")
    parser.add_argument("--db-url", default=os.getenv("SUPABASE_DB_URL") or os.getenv("DATABASE_URL"), help="Postgres connection URL")
    parser.add_argument("--limit", type=int, default=0, help="Optional max number of events to process (0 = no limit)")
    parser.add_argument("--dry-run", action="store_true", help="Process rows without calling embedding API or writing DB")
    parser.add_argument("--openai-api-key", default=os.getenv("OPENAI_API_KEY"), help="OpenAI API key for live embedding generation")
    parser.add_argument("--model", default=os.getenv("EMBEDDING_MODEL", DEFAULT_MODEL), help="Embedding model (default: text-embedding-3-small)")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        import psycopg
    except Exception as exc:  # pragma: no cover
        print(f"ERROR: psycopg is required to run this script ({exc}).", file=sys.stderr)
        return 2

    if not args.db_url:
        print("ERROR: --db-url is required (or set SUPABASE_DB_URL / DATABASE_URL)", file=sys.stderr)
        return 2

    auto_dry_run = not bool(args.openai_api_key)
    dry_run = args.dry_run or auto_dry_run

    if auto_dry_run and not args.dry_run:
        print("INFO: OPENAI_API_KEY not found -> running in SAFE DRY-RUN mode.")
    if dry_run:
        print("INFO: Dry-run enabled. No embedding API calls. No DB writes.")

    where = "WHERE title IS NOT NULL"
    limit_sql = ""
    params: list[Any] = []
    if args.limit and args.limit > 0:
        limit_sql = " LIMIT %s"
        params.append(args.limit)

    query = f"""
        SELECT
            id,
            title,
            description,
            event_type,
            municipality,
            region,
            status,
            start_at,
            end_at,
            tags,
            source_url,
            place_id
        FROM events
        {where}
        ORDER BY updated_at DESC, id ASC
        {limit_sql}
    """

    processed = 0
    upserted = 0

    with psycopg.connect(args.db_url) as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            rows = cur.fetchall()

        for row in rows:
            event = EventRow(*row)
            content = build_content(event)
            metadata = build_metadata(event)
            processed += 1

            if dry_run:
                if processed <= 3:
                    print(f"DRY-RUN sample event_id={event.id} title={event.title!r}")
                continue

            try:
                embedding = fetch_embedding(content, args.openai_api_key, args.model)
                upsert_event_embedding(conn, event, content, metadata, embedding)
                upserted += 1
            except Exception as exc:
                print(f"WARN: event_id={event.id} failed: {exc}", file=sys.stderr)

        if not dry_run:
            conn.commit()

    print("---")
    print(f"processed={processed}")
    print(f"upserted={upserted}")
    if dry_run:
        print("mode=dry-run")
    else:
        print("mode=live")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
