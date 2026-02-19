# MAISU Ingestion Runbook (Execute in <30 min)

**Goal:** Run ingestion now and verify both coverage gates: **`places` and `historia_vasca` must be represented in `places_embeddings`** (`source_type='place'` and `source_type='history'`).

## 1) Prerequisites / env vars

- Access to **n8n** instance with workflow imported: `n8n/data-ingestion-workflow.json`
- Access to **Supabase SQL Editor** (or `psql`) with write permissions
- n8n credentials configured for:
  - Postgres/Supabase
  - OpenAI embeddings
  - (Optional) Google Sheets

Required env vars (n8n):

```bash
OPENAI_API_KEY=...
MAISU_SHEETS_ID=...        # optional; if missing, workflow uses Mock Row
MAISU_SHEETS_TAB=places    # optional
```

Optional local DB vars (if using `psql`):

```bash
SUPABASE_DB_URL='postgresql://postgres:<password>@db.<project-ref>.supabase.co:5432/postgres?sslmode=require'
```

---

## 2) Run commands (primary + fallback)

## A. Primary path (n8n, recommended)

> This workflow has a **Manual Trigger** (no webhook trigger path configured).

1. Open n8n → workflow **“MAISU - Data Ingestion (Places + Embeddings)”**.
2. Confirm env vars present in n8n.
3. Click **Execute workflow**.
4. Wait for green execution; capture execution ID/time in handoff notes.

Expected behavior:
- If `MAISU_SHEETS_ID` exists: reads Google Sheet rows.
- If not: runs Mock Row path.
- Upserts into `places`, then inserts embeddings into `places_embeddings` with `source_type='place'`.

## B. Fallback/manual SQL path (if n8n unavailable)

Use this to bootstrap tables/content only (does **not** generate embeddings):

```bash
psql "$SUPABASE_DB_URL" -f database/schema.sql
psql "$SUPABASE_DB_URL" -f database/seed-data.sql
psql "$SUPABASE_DB_URL" -f database/expresiones-vascas.sql
```

Then proceed to verification section to quantify remaining embedding gap.

---

## 3) Verification SQL (counts + spot checks)

Run in Supabase SQL editor or `psql`.

### 3.1 Coverage gate (P0)

```sql
-- Global counts
SELECT
  (SELECT COUNT(*) FROM places) AS places_count,
  (SELECT COUNT(*) FROM places_embeddings WHERE source_type = 'place') AS place_embeddings_count,
  (SELECT COUNT(*) FROM historia_vasca) AS historia_count,
  (SELECT COUNT(*) FROM places_embeddings WHERE source_type = 'history') AS history_embeddings_count;
```

**Pass criteria:** `place_embeddings_count >= places_count` **and** (`historia_count = 0` or `history_embeddings_count > 0`).

### 3.2 Direct gap list (places without embedding)

```sql
SELECT p.id, p.nombre, p.updated_at
FROM places p
LEFT JOIN places_embeddings pe
  ON pe.source_id = p.id
 AND pe.source_type = 'place'
WHERE pe.id IS NULL
ORDER BY p.updated_at DESC;
```

**Pass criteria:** 0 rows.

### 3.3 Duplicate embedding check (quality guard)

```sql
SELECT source_id, COUNT(*) AS embeddings_per_place
FROM places_embeddings
WHERE source_type = 'place'
GROUP BY source_id
HAVING COUNT(*) > 1
ORDER BY embeddings_per_place DESC;
```

### 3.4 Spot check recent inserts (content sanity)

```sql
SELECT
  pe.created_at,
  pe.source_type,
  p.nombre,
  LEFT(pe.content, 140) AS content_preview
FROM places_embeddings pe
LEFT JOIN places p ON p.id = pe.source_id
ORDER BY pe.created_at DESC
LIMIT 10;
```

### 3.5 Explicit audit gap note (history)

```sql
SELECT
  COUNT(*) AS historia_rows,
  (SELECT COUNT(*) FROM places_embeddings WHERE source_type='history') AS historia_embeddings
FROM historia_vasca;
```

If `historia_rows > 0` and `historia_embeddings = 0`, ingestion did not populate history embeddings and should be treated as failed coverage.

### 3.6 One-command verification (read-only)

Use the helper script to run the key checks above in one command and print a compact summary.

```bash
SUPABASE_DB_URL='postgresql://postgres:<password>@db.<project-ref>.supabase.co:5432/postgres?sslmode=require' \
  ./scripts/verify-ingestion-sql.sh
```

Behavior and assumptions:
- Uses `SUPABASE_DB_URL` (or `DATABASE_URL` fallback).
- Requires local `psql` in PATH.
- Runs inside a `READ ONLY` transaction and executes `SELECT` checks only.
- Exit code `0` when core checks pass; exit code `2` when coverage/missing/duplicate checks fail.
- History gap is reported as indicator (`OK` / `GAP`) and does not fail the script by itself.

---

## 4) Rollback steps

Use the smallest rollback possible.

### 4.1 Rollback this ingestion run (by time window)

```sql
-- Replace timestamp with run start time (UTC)
BEGIN;

DELETE FROM places_embeddings
WHERE source_type = 'place'
  AND created_at >= TIMESTAMPTZ '2026-02-19 00:00:00+00';

DELETE FROM places
WHERE created_by IN ('n8n-ingestion', 'n8n-mock')
  AND updated_at >= TIMESTAMPTZ '2026-02-19 00:00:00+00';

COMMIT;
```

### 4.2 Emergency full reset (only if explicitly approved)

```sql
TRUNCATE TABLE places_embeddings RESTART IDENTITY;
TRUNCATE TABLE places RESTART IDENTITY CASCADE;
-- then re-seed
-- psql "$SUPABASE_DB_URL" -f database/seed-data.sql
```

---

## 5) Owner handoff checklist

- [ ] Ingestion executed (n8n execution ID + UTC timestamp recorded)
- [ ] Coverage SQL pasted in ticket/PR (`places_count` vs `place_embeddings_count`)
- [ ] Gap query shows **0 places missing embeddings**
- [ ] Duplicate check reviewed (or accepted with reason)
- [ ] Spot-check query confirms recent rows are correct
- [ ] `historia_vasca` vs `source_type='history'` status recorded (coverage confirmed)
- [ ] Rollback SQL window prepared and tested (dry-run by SELECT)
- [ ] Monitoring owner assigned for next scheduled run
- [ ] Backend owner informed if `fallback_used=true` observed in API logs
- [ ] Next task created: add history embedding ingestion path

---

## 6) 30-minute execution plan

1. (5 min) Validate creds/env in n8n + DB access.
2. (5–10 min) Execute ingestion workflow once.
3. (5 min) Run coverage + gap SQL; ensure `places` fully embedded.
4. (5 min) Run spot checks + duplicates.
5. (5 min) Record handoff checklist + open follow-up for history embeddings.
