# context/maisu

Segmented technical context for the Maisu project.

## Structure
- `00-foundation/` Stable project bases (scope, goals, constraints)
- `01-architecture/` System architecture and data flow
- `02-guidelines/` Engineering and delivery guidelines
- `03-environments/` Environment map (dev/staging/prod)
- `04-runbooks/` Operational procedures
- `05-decisions/` ADRs (Architecture Decision Records)
- `06-checkpoints/` Periodic project status snapshots

## Update rules
- Stable docs: update only when fundamentals change.
- Decisions: always record as ADR in `05-decisions/`.
- Checkpoints: add a new file per milestone/week.

## Quick entrypoints
- API contract (`POST /rag/query`): `01-architecture/api-contract-rag-query.md`
- RAG smoke test runbook: `04-runbooks/rag-smoke-test.md`
