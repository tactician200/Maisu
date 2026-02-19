# Maisu Changelog

## 2026-02-19
- Hardened `/rag/query` validation and aligned contracts/docs with current runtime behavior.
- Added ingestion audit artifacts: execution runbook and SQL verifier script for checks/rollback.
- Added minimal `historia_vasca` embeddings ingestion path and regression coverage.
- Added personalization user-context delivery: API endpoint, SQL table schema, and language fallback behavior.
- Final integration validation: backend test suite passing (`20 passed`).
- Integrated personalization v2 delivery: `/rag/query` now enforces request > stored-context > default precedence for tone/style/interests, with guardrail tests and an ops runbook for verification/rollback.
- Tuned retrieval relevance/citation quality with tokenized matching, deterministic scoring/order, optional history-table blend for historical queries, and added regression coverage (`27 passed`).
- Captured onboarding/personalization MVP product direction (full personalization + dynamic conversational onboarding) in `docs/onboarding-personalization-mvp.md`.

## 2026-02-18
- Reorganized repository structure (`docs/`, `n8n/`, `database/`, `scripts/`)
- Updated broken documentation paths
- Added `.env.example` and `.gitignore`
- Added segmented project context under `context/maisu/`
