# Runbook — Daily Close Protocol (trigger: "cerremos por el día")

Purpose: finish the day with a clean repo, updated operations context, and a reliable next-day start point.

## Trigger
User message contains: `cerremos por el día`.

## 1) Code & Validation
1. Check pending changes (`git status --short`).
2. Run minimum validation for touched scope (tests/smoke).
3. Fix only critical breakages; defer non-critical refactors.

## 2) Git Hygiene
4. Stage only relevant files.
5. Create 1..N clear commits by scope.
6. Push to agreed branch (`main` by default).
7. Record commit hashes in the daily checkpoint.

## 3) Technical Docs (repo)
8. Update daily checkpoint (`06-checkpoints/checkpoint-YYYY-MM-DD.md`).
9. Update/append ADRs if architectural decisions changed.
10. Update runbooks/README/SETUP only if behavior changed.

## 4) Operational Sync (Notion)
11. Add Daily Session Log summary:
   - outcomes
   - evidence
   - blockers
12. Update Tasks/Backlog statuses (Done / In Progress / Blocked).
13. Add Decision Log item when applicable.
14. Prepare "Top 3 for tomorrow".

## 5) Temporary Artifacts
15. Save useful temp outputs under `artifacts/<date>/` (logs, smoke JSON, evidence).
16. Remove disposable temp files that should not persist.
17. Reference artifact paths in the checkpoint.

## 6) Secure End-of-Day State
18. Close temporary network exposure (ports/SG exceptions).
19. List what remains running intentionally.
20. Confirm no secrets were committed.

## 7) Handover for Tomorrow
21. Add `Start Tomorrow` block in checkpoint:
   - Objective
   - First 3 commands
   - Success signal
22. Post concise end-of-day summary to user:
   - what was completed
   - progress %
   - next day plan
   - week-1 plan

## Acceptance Criteria
- Repo pushed with validated state.
- Checkpoint up-to-date and actionable.
- Notion synced.
- Artifacts preserved.
- Security exposure reset.
