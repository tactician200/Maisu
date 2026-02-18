# ADR-0002 — FastAPI as Primary RAG Path, n8n as Optional Orchestration

- Status: Accepted (technical)
- Date: 2026-02-18
- Owners: MAISU engineering

## Context
MAISU required a reliable, testable core for `/rag/query` with clear fallback behavior and low operational ambiguity.

Existing n8n assets are useful for orchestration and automations, but not ideal as the primary runtime core for deterministic API contracts and backend testing loops.

## Decision
Adopt **FastAPI (Python)** as the **primary RAG backend path**.
Keep **n8n** as an **optional orchestration/backup layer**.

## Why
1. Deterministic contract and tests (`pytest`, smoke scripts)
2. Cleaner handling of provider errors and fallback behavior
3. Easier CI/CD and observability hardening for API runtime
4. Lower coupling between workflow automation and core serving path

## Evidence (2026-02-18)
- Local test suite: `7 passed`
- `/health` and `/rag/query` validated locally
- Path A (provider available): `provider=openai`, `fallback_used=false`, citations present
- Path B (forced provider unavailable): `provider=fallback`, `fallback_used=true`, graceful answer

## Consequences
### Positive
- Better reliability envelope for product API
- Faster iteration for retrieval/provider modules
- Explicit contingency behavior

### Trade-offs
- Need deployment exposure hardening (public URL, auth, SG/proxy)
- Need follow-up for production observability and latency baselines

## Guardrails
- No DB schema/migration changes in this phase
- No secret commits
- Existing n8n assets preserved

## Next actions
1. Expose deploy endpoint safely (proxy or SG + auth)
2. Run remote smoke against public `BASE_URL`
3. Capture prod evidence (latency/fallback/provider)
4. Publish cutover go/no-go checklist
