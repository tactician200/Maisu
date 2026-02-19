# MAISU Ingestion Readiness Audit

Date: 2026-02-19  
Scope reviewed: `database/*.sql`, `n8n/data-ingestion-workflow.json`, `n8n/bilbot-main-conversation.json`, `backend/app/retrieval.py`, `README.md`, `SETUP.md`, `docs/n8n-workflows-guide.md`.

## Current corpus + pipeline assumptions (as-is)

- Canonical data today is SQL-seeded content:
  - `database/seed-data.sql` → `places` (20 rows), `historia_vasca` (7 rows)
  - `database/expresiones-vascas.sql` → `expresiones_vascas`
- Vector retrieval for n8n assumes `places_embeddings` exists and is populated via `match_places_embeddings`.
- Ingestion workflow (`n8n/data-ingestion-workflow.json`) currently ingests **places only** (Google Sheets or mock row), then writes one embedding per place to `places_embeddings`.
- Backend API retrieval (`backend/app/retrieval.py`) is **not vector**: it does REST `ilike` query on `places` and falls back to mock docs if missing creds/error/0 results.
- No active ingestion path found for:
  - `historia_vasca` embeddings
  - `expresiones_vascas` updates via workflow
  - product docs (`docs/*.md`) as RAG corpus

## Readiness table

| Source | Format | Status | Blocker | Owner suggestion | Next action |
|---|---|---|---|---|---|
| `database/seed-data.sql` (`places`, `historia_vasca`) | SQL seed | **Ready (bootstrap)** | Static/manual refresh only | Data owner + Backend | Define refresh cadence (weekly) and owner for SQL updates. |
| `database/expresiones-vascas.sql` | SQL seed | **Ready (bootstrap)** | Not connected to ingestion automation | Content owner | Add monthly update checklist + reviewer. |
| `n8n/data-ingestion-workflow.json` (Google Sheets→places+embeddings) | n8n JSON workflow | **Partially ready** | Optional/manual; depends on `MAISU_SHEETS_ID`, OpenAI key, Postgres creds; no runbook evidence of scheduled production run | Automation owner (n8n) | Run once in target env, capture execution ID + row counts, then schedule daily/weekly trigger. |
| `places_embeddings` population | DB vector table | **Not ready for reliable prod** | Seed does not populate embeddings; requires ingestion run; no freshness SLA | Backend + Automation | Add post-run verification SQL gate (count embeddings >= places count). |
| `historia_vasca` for semantic retrieval | SQL table | **Not ready** | No ingestion/embedding path for history content | Backend + Data | Add minimal workflow branch: history row -> embedding -> `places_embeddings` (source_type=`history`) or dedicated history embedding table. |
| `docs/Web app inteligente Turismo IA.docx.md` and other docs | Markdown docs | **Not ready** | No parser/chunker/indexing path connected | Data/PM | Decide include/exclude list; if included, add simple markdown-to-embedding batch script/workflow. |
| `backend/app/retrieval.py` source path | Supabase REST (`places`) + mock fallback | **Partially ready** | No vector retrieval; silent fallback can hide data issues | Backend | Add explicit health signal when fallback is used and expose retrieval mode in response/log. |

## Prioritized action list

### P0 (today)
1. Execute ingestion workflow in real environment and verify:
   - `SELECT COUNT(*) FROM places;`
   - `SELECT COUNT(*) FROM places_embeddings WHERE source_type='place';`
   - target: embeddings count >= places count.
2. Add a one-page runbook (`docs/`) with exact “ingest + verify + rollback” commands and responsible owner.
3. Disable silent ambiguity in backend ops: log/alert when `fallback_used=true` (already in API response contract, enforce in monitoring).

### P1 (tomorrow)
1. Add minimal ingestion for `historia_vasca` embeddings (same model `text-embedding-3-small`, tagged `source_type='history'`).
2. Add scheduled trigger (daily or weekly) for ingestion workflow and store last successful run timestamp.
3. Add freshness check script (fails if embeddings lag behind places/history updates).

### P2 (next)
1. Decide whether `docs/*.md` is in-scope corpus; if yes, ingest only approved docs list.
2. Add simple ownership matrix (Data/Automation/Backend) to avoid stalled updates.
3. Add smoke test asserting retrieval returns non-mock sources for known query.

## Practical “done” criteria for tomorrow

- Ingestion run executed successfully at least once in target env.
- `places_embeddings` coverage for places is complete and verified by SQL.
- History ingestion path exists (even if minimal/manual).
- One runbook and one freshness check are committed and usable by another teammate without tribal knowledge.
