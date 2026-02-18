# Checkpoint — 2026-02-18

## Current Status
- Working:
  - FastAPI RAG core implemented (`/health`, `/rag/query`)
  - Retrieval integration with Supabase REST + graceful fallback to mock docs
  - Test coverage for API and retrieval paths
  - Smoke runbook aligned with real API contract
- In progress:
  - Public deploy exposure (`BASE_URL` externally reachable)
  - Production smoke evidence capture (latency/fallback/provider)
- Blocked:
  - External validation gated by AWS Security Group / reverse-proxy exposure

## Key Changes Since Last Checkpoint
- Added backend core and tests under `backend/app/*` and `backend/tests/*`
- Added API smoke script (`scripts/rag-smoke-test-api.sh`)
- Updated `README.md` and `SETUP.md` for FastAPI + Supabase vars
- Updated runbook `04-runbooks/rag-smoke-test.md` with real response contract and observed evidence
- Added `ADR-0002-fastapi-primary-n8n-optional.md`

## Validation Evidence (local)
- `python3 -m venv .venv && pip install -r requirements.txt`
- `PYTHONPATH=. pytest -q` → `7 passed`
- `/health` → `{"status":"ok"}`
- `/rag/query` normal path:
  - `provider=openai`
  - `fallback_used=false`
  - `latency_ms=3401`
  - `citations=3`
- `/rag/query` forced contingency:
  - `provider=fallback`
  - `fallback_used=true`
  - `latency_ms=0`
  - `citations=3`

## Risks
- API not externally reachable until network exposure is completed
- Inconsistent provider behavior if OPENAI credentials are absent/invalid in deploy env
- Docs drift risk if Notion sync is skipped after milestones

## Next 5 Actions
1. Configure stable HTTPS reverse proxy (443) to internal FastAPI (`127.0.0.1:8000`)
2. Add request auth/rate limit for public endpoint path
3. Record prod evidence in Notion (latency, fallback, provider)
4. Define cutover checklist and rollback path (FastAPI primary, n8n backup)
5. Resume Discord ingestion fix (`guildId` + allowlist/mention policy)

## Start Tomorrow
- Objective: secure external serving path and leave cutover checklist ready.
- First 3 commands:
  1. `curl -sS http://127.0.0.1:8000/health`
  2. `curl -sS -H "Content-Type: application/json" -d '{"query":"Plan rápido Bilbao","session_id":"tomorrow","lang":"es"}' http://127.0.0.1:8000/rag/query`
  3. `git log --oneline -n 5`
- Success signal: API healthy, query contract stable, and deployment hardening tasks started.
