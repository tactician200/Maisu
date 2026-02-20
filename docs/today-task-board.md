# Today Task Board — Maisu

Date: 2026-02-20 (UTC)

## Objective
Ship stable personalization + onboarding baseline with SQL-backed context and automated smoke checks.

## Lanes

### Lane A — Implementation
- [x] Personalization v2 (`be5cb66`)
- [x] Onboarding v1 in `/rag/query` (`2fb65f7`)
- [x] Supabase key fallback (`41a5f84`)

### Lane B — Validation
- [x] Backend tests green (`47 passed`)
- [x] Live Supabase read/write check (`201/200`)
- [ ] API smoke script execution against running backend

### Lane C — Docs/Ops
- [x] Personalization runbook updated
- [x] Onboarding rollout doc aligned with actual API
- [x] Daily execution protocol template
- [ ] OpenClaw hardening run review (scheduled)

## Blockers
- `sessions_spawn` intermittent pairing (`gateway closed 1008`).
- Direct DB URI from this host blocked by IPv6 reachability; use SQL Editor/API path.

## Ship Gate
- [x] Unit/integration tests passing
- [x] Supabase table exists + CRUD verified
- [ ] End-to-end smoke script result captured

## Rollback
- Personalization v2 revert: `git revert be5cb66`
- Onboarding v1 revert: `git revert 2fb65f7`
- Supabase key fallback revert: `git revert 41a5f84`
