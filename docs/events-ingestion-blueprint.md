# Events Ingestion Blueprint (Scraper + Validation Queue)

## Goal
Deliver a reliable ingestion flow for events with fast auto-publish of high-confidence items and human review for risky/ambiguous items.

## Pipeline (end-to-end)
1. **Source adapters** (official APIs, ICS, websites via scraper)
2. **Normalize** (map to canonical event schema)
3. **Dedupe** (strict + fuzzy matching)
4. **Confidence score** (0–1 quality/trust score)
5. **Review queue** (only low/medium confidence or policy-flagged)
6. **Publish** (approved events to production table/index)
7. **Embeddings sync** (new/changed published events -> vector index)

---

## Stage contracts

### 1) Source adapters -> Raw event
**Input:** source config (`source_id`, fetch mode, auth, selectors)

**Output contract (`raw_event`)**
```json
{
  "source_id": "bilbao_turismo_web",
  "source_type": "html|api|ics",
  "external_id": "optional-source-id",
  "fetched_at": "2026-02-23T20:00:00Z",
  "source_url": "https://...",
  "payload": {},
  "content_hash": "sha256:..."
}
```

### 2) Normalize -> Canonical candidate
**Output contract (`event_candidate`)**
```json
{
  "candidate_id": "uuid",
  "title": "...",
  "description": "...",
  "start_at": "ISO8601",
  "end_at": "ISO8601|null",
  "timezone": "Europe/Madrid",
  "venue_name": "...",
  "address": "...",
  "lat": 43.26,
  "lon": -2.93,
  "category": "music|culture|family|sports|other",
  "price": "free|paid|unknown",
  "language": "es|eu|en|...",
  "images": ["https://..."],
  "ticket_url": "https://...|null",
  "organizer": "...|null",
  "source_ref": {
    "source_id": "...",
    "source_url": "...",
    "external_id": "...|null"
  },
  "provenance": [{
    "step": "normalize",
    "at": "ISO8601",
    "version": "normalizer:v1"
  }]
}
```

### 3) Dedupe -> Merge decision
**Output contract (`dedupe_result`)**
```json
{
  "candidate_id": "uuid",
  "duplicate_of": "event_id|null",
  "match_type": "none|strict|fuzzy",
  "match_score": 0.0,
  "merge_patch": {},
  "provenance": [{"step":"dedupe","rule":"title+date+venue"}]
}
```

### 4) Confidence score -> Routing
**Output contract (`scored_candidate`)**
```json
{
  "candidate_id": "uuid",
  "confidence": 0.0,
  "signals": {
    "source_trust": 0.0,
    "field_completeness": 0.0,
    "date_validity": 0.0,
    "dedupe_risk": 0.0,
    "staleness": 0.0
  },
  "route": "auto_publish|review_queue|reject"
}
```

### 5) Review queue -> Human decision
**Queue item contract (`review_item`)**
```json
{
  "review_id": "uuid",
  "candidate_id": "uuid",
  "reason_codes": ["LOW_CONFIDENCE", "FUZZY_DUPLICATE"],
  "sla_hours": 24,
  "status": "pending|approved|rejected|needs_changes",
  "review_notes": "..."
}
```

### 6) Publish -> Production event
**Rules:** only `auto_publish` or `approved` items; upsert by stable `event_id`.

### 7) Embeddings sync
**Trigger:** publish/create/update/delete.

**Output contract (`embedding_job`)**
```json
{
  "event_id": "uuid",
  "action": "upsert|delete",
  "text_version": "hash",
  "queued_at": "ISO8601",
  "status": "pending|done|failed"
}
```

---

## Scheduling plan
- **Daily full pass (02:00 UTC):** fetch all active sources, normalize, dedupe, score.
- **Near-event refresh (every 2h):** events starting in next 72h; re-fetch critical fields (time/status/cancelled/venue).
- **Hot refresh (every 30 min, optional for top trusted sources):** high-traffic sources during weekends/holidays.

Priority order: near-event updates > new ingestion from low-priority sources.

---

## Failure handling, retries, anti-duplication, provenance

### Failure + retry policy
- Adapter/network errors: retry with exponential backoff (1m, 5m, 15m), max 3 attempts.
- 4xx permanent errors: no retry; mark source unhealthy.
- Parse/normalize errors: send to `ingestion_dead_letter` with raw payload + parser version.
- Embedding failures: retry async up to 5 attempts; keep event published even if embeddings lag.

### Anti-duplication rules
1. **Strict key:** (`external_id`, `source_id`) exact match.
2. **Deterministic fallback:** normalized title + local date + venue slug.
3. **Fuzzy safety:** title similarity + time window (+/- 3h) + geo distance threshold.
4. Never create a new event when fuzzy score > threshold and human marked as duplicate previously.

### Provenance tracking
Each stage appends immutable provenance entries:
- `step`, `timestamp`, `component_version`, `input_hash`, `decision`, `operator` (`system|human:<id>`).
- Keep full lineage from raw payload to published record for audits.

---

## 1-week MVP implementation plan

### Day 1–2
- Implement source adapter interface + 2 adapters (1 API, 1 scraper).
- Create `raw_events`, `event_candidates`, `review_queue` tables.

### Day 3
- Implement normalizer + validation rules (required fields, date sanity).
- Store provenance at normalize step.

### Day 4
- Implement dedupe service (strict + basic fuzzy) and confidence scoring v1.
- Route logic: auto-publish vs review.

### Day 5
- Build minimal review queue UI/API (list, approve, reject, notes).
- Publish upsert flow.

### Day 6
- Embeddings sync worker (publish-triggered queue + retries).
- Daily + near-event schedulers.

### Day 7
- End-to-end dry run, metrics dashboard, runbook updates, safe-mode test.

MVP success criteria:
- >=80% of trusted-source events auto-publish without manual edits.
- <5% duplicate rate in published events.
- Review SLA visible and actionable.

---

## Rollback / safe-mode strategy
- **Safe mode toggle:** disable auto-publish globally; force all candidates to review queue.
- **Per-source kill switch:** disable faulty source adapter without stopping pipeline.
- **Versioned scoring rules:** revert confidence thresholds to previous known-good config.
- **Publish rollback:** keep event version history; restore previous published snapshot by `event_id`.
- **Embeddings decoupled:** if vector sync unstable, pause embeddings worker while keeping canonical publish running.

Operational default during incidents: `ingest ON`, `auto-publish OFF`, `review-only` until quality recovers.