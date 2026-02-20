# Maisu Changelog

## 2026-02-20
- Updated personalization v2 ops rollout runbook with preflight/deploy/post-deploy checks, override/fallback smoke steps, and rollback guidance.
- Added release notes entry for personalization v2 rollout package.
- Added Onboarding v1 rollout operator/product doc and onboarding smoke/rollback runbook section.
- Added `scripts/smoke-user-context-onboarding.sh` for fast operator verification of SQL-backed context + `/rag/query` onboarding behavior.
- Added `scripts/smoke.sh`, `Makefile` target `smoke`, and `docs/nightly-smoke.md` for automated smoke verification.
- Added `docs/daily-execution-protocol.md` and `docs/today-task-board.md` for the “Comencemos/Cerramos” team ritual.
- Aligned onboarding docs with actual runtime contract (`POST /rag/query` + optional `onboarding_next`).

## 2026-02-19
- Hardened `/rag/query` validation and aligned contracts/docs with current runtime behavior.
- Added ingestion audit artifacts: execution runbook and SQL verifier script for checks/rollback.
- Added minimal `historia_vasca` embeddings ingestion path and regression coverage.
- Added personalization user-context delivery: API endpoint, SQL table schema, and language fallback behavior.
- Final integration validation: backend test suite passing (`20 passed`).
- Integrated personalization v2 delivery: `/rag/query` now enforces request > stored-context > default precedence for tone/style/interests, with guardrail tests and an ops runbook for verification/rollback.
- Tuned retrieval relevance/citation quality with tokenized matching, deterministic scoring/order, optional history-table blend for historical queries, and added regression coverage (`27 passed`).
- Captured onboarding/personalization MVP product direction (full personalization + dynamic conversational onboarding) in `docs/onboarding-personalization-mvp.md`.
- Added product decisions: data-policy deferred, strict-vs-narrative answer rule by data type, and phased launch sequence (friends/family → internal commercial rep → tourism authorities).
- Added conversational onboarding ruleset in `docs/onboarding-conversational-rules.md` (critical/contextual/inferred data model + phased collection + UX constraints).

## 2026-02-18
- Reorganized repository structure (`docs/`, `n8n/`, `database/`, `scripts/`)
- Updated broken documentation paths
- Added `.env.example` and `.gitignore`
- Added segmented project context under `context/maisu/`
