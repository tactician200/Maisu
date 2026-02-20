# Nightly Smoke Checks

## One-command runner

From the repo root:

```bash
make smoke
```

## Cron-ready command

Example (runs daily at 02:30, logs output, fails on non-zero exit):

```cron
30 2 * * * cd /path/to/maisu-repo && SMOKE_BASE_URL="https://api.example.com" SMOKE_VALIDATION=1 SMOKE_ONBOARDING=0 make smoke >> /var/log/maisu/nightly-smoke.log 2>&1
```

Optional DB verification (requires `psql`):

```cron
30 2 * * * cd /path/to/maisu-repo && SMOKE_BASE_URL="https://api.example.com" SMOKE_DB_URL="postgresql://user:pass@host:5432/db" make smoke >> /var/log/maisu/nightly-smoke.log 2>&1
```

## Exit semantics

- PASS: exit code `0` with `SMOKE_PASS` in the output.
- FAIL: any non-zero exit code. The runner stops at the first failed check.

## Inputs

- `SMOKE_BASE_URL`: API base URL (default `http://127.0.0.1:8000`).
- `SMOKE_QUERY_TEXT`: RAG query text (default `Mejor bar de pintxos en Bilbao`).
- `SMOKE_VALIDATION`: run request validation checks (`1`/`0`, default `1`).
- `SMOKE_ONBOARDING`: run onboarding/user-context smoke (`1`/`0`, default `0`).
- `SMOKE_DB_URL`: optional Postgres connection URL for history embedding checks.

## Prerequisites

- `curl` for API checks.
- `jq` for onboarding/user-context smoke output.
- `psql` if `SMOKE_DB_URL` is set.
