# Maisu Changelog

## 2026-02-19
- Integrated RAG validation hardening for `/rag/query` (strict payload checks + structured 422 response guidance).
- Aligned API/RAG contract docs to current runtime request/response behavior and accepted alias fields.
- Added ingestion readiness audit with prioritized gaps and follow-up actions.
- Verified integration with backend test suite (`9 passed`) and API validation smoke script.

## 2026-02-18
- Reorganized repository structure (`docs/`, `n8n/`, `database/`, `scripts/`)
- Updated broken documentation paths
- Added `.env.example` and `.gitignore`
- Added segmented project context under `context/maisu/`
