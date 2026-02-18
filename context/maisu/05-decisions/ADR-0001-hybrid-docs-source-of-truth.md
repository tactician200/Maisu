# ADR-0001: Hybrid Documentation Source of Truth

- Date: 2026-02-18
- Status: Accepted
- Owners: MAISU core team

## Context
Project execution requires both fast operational coordination and durable versioned technical artifacts.

## Decision
Adopt hybrid model:
- **Notion** for daily operations (tasks, priorities, session logs, quick decisions)
- **Repository (`context/maisu`)** for stable technical context, runbooks, and ADRs

## Alternatives Considered
- Option A: Notion-only (rejected: poor versioning for technical artifacts)
- Option B: Repo-only (rejected: weak daily operational visibility)

## Consequences
- Positive: clear split of responsibilities, better continuity after pauses
- Tradeoff: requires session-close discipline to keep both in sync

## Follow-up
- Add minimum runbooks and templates in `context/maisu`
- Require checkpoint update at least weekly or per milestone
