# Runbook — Supabase Schema Migration (MVP-safe)

## Purpose
Apply DB changes with minimum risk and quick recovery.

## Preconditions
- Migration SQL reviewed
- Backup/export point available
- Staging test executed when possible

## Steps
1. Review migration SQL (idempotent where possible).
2. Apply in staging (if available) and run retrieval smoke test.
3. Schedule low-traffic window for production.
4. Apply migration in production.
5. Run immediate checks:
   - required tables/functions exist
   - vector retrieval query works
   - write path still succeeds

## Validation Signals
- No SQL errors during apply
- Retrieval endpoint returns expected rows
- Application logs show no DB regression

## Rollback
- Execute rollback SQL (if prepared), or
- restore from backup/snapshot, then
- re-run smoke tests before reopening traffic
