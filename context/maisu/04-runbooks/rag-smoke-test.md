# Runbook — RAG Smoke Test (MVP Vertical Slice)

## Purpose
Validate ingestion + retrieval + response behavior with minimum reproducible checks.

## Preconditions
- Supabase schema and vector index available
- Embedding + LLM credentials configured
- At least one approved Bilbao source ingested

## Dataset (minimum)
Use one small curated corpus (5–20 docs/chunks) from approved tourism sources.

## Test Cases

### Case A — Known answer
- Query: "What are top family activities in Bilbao?"
- Expected:
  - `ok=true`
  - `fallback=false`
  - `citations.length >= 1`

### Case B — Ambiguous request
- Query: "Plan me something nice this weekend"
- Expected:
  - either grounded answer with assumptions + citation, or fallback clarifying question
  - no fabricated specifics

### Case C — Out-of-scope
- Query: "Best itinerary for Lisbon and Porto"
- Expected:
  - scope fallback (Bilbao-only statement)
  - no fake non-Bilbao citations

## Execution Steps
1. Confirm ingestion status for target source IDs.
2. Execute test queries against `/rag/query`.
3. Capture: answer, citations count, confidence, fallback reason, latency.
4. Record evidence in latest checkpoint file.

## Pass/Fail Criteria
- Pass if all three cases match expected behavior.
- Fail if any case hallucinates unsupported facts or misses mandatory fallback.

## Rollback / Recovery
- If retrieval quality is poor, lower scope and re-ingest high-quality sources only.
- If confidence is unstable, tighten threshold and force fallback.
