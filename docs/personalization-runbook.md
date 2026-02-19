# Personalization Rollout Runbook (Ops)

Goal: enable per-session personalization using `user_context`, then verify end-to-end behavior in API.

## 1) Enabling checklist

- [ ] Apply DB migration: `database/user_context.sql` on the target Supabase project.
- [ ] Confirm backend env vars are set:
  - `SUPABASE_URL`
  - `SUPABASE_SERVICE_ROLE_KEY`
  - `SUPABASE_USER_CONTEXT_TABLE=user_context` (optional, default already `user_context`)
- [ ] Restart backend service after env changes.
- [ ] Confirm health endpoint: `curl -fsS "$API_BASE/health"` returns `{\"status\":\"ok\"}`.

## 2) SQL verification (`user_context` population)

Run in Supabase SQL editor (`$SESSION_ID` = test id used below).

```sql
-- 2.1 Table exists
SELECT to_regclass('public.user_context') AS table_name;

-- 2.2 Row exists for session after PUT
SELECT session_id, name, language, preferences, user_id, updated_at
FROM public.user_context
WHERE session_id = 'ops-personalization-smoke-001';

-- 2.3 Fresh update check (should be recent)
SELECT session_id, now() - updated_at AS age
FROM public.user_context
WHERE session_id = 'ops-personalization-smoke-001';

-- 2.4 Optional: quick distribution snapshot
SELECT language, COUNT(*)
FROM public.user_context
GROUP BY language
ORDER BY COUNT(*) DESC;
```

Pass signal: session row exists; `language`/`preferences` match PUT payload; `updated_at` changes on each update.

## 3) API smoke commands (GET/PUT + `/rag/query`)

```bash
API_BASE="http://127.0.0.1:8000"
SESSION_ID="ops-personalization-smoke-001"

# 3.1 Upsert user context
curl -sS -X PUT "$API_BASE/user-context/$SESSION_ID" \
  -H "Content-Type: application/json" \
  -d '{"name":"Ane","language":"eu","preferences":{"tone":"friendly","likes":["pintxos"]}}' | jq

# 3.2 Read user context
curl -sS "$API_BASE/user-context/$SESSION_ID" | jq

# 3.3 RAG query using session context (no lang in request; should inherit stored language)
curl -sS -X POST "$API_BASE/rag/query" \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"Recomiéndame 2 planes en Bilbao\",\"session_id\":\"$SESSION_ID\"}" | jq '{provider,fallback_used,latency_ms,citations_count:(.citations|length),answer}'

# 3.4 Control query without session context
curl -sS -X POST "$API_BASE/rag/query" \
  -H "Content-Type: application/json" \
  -d '{"query":"Recomiéndame 2 planes en Bilbao"}' | jq '{provider,fallback_used,latency_ms,citations_count:(.citations|length),answer}'
```

Pass signal:
- `PUT`/`GET` return the same `session_id` and payload fields.
- `/rag/query` returns `200` with `answer`, `citations`, `provider`, `fallback_used`.
- With valid provider keys, `fallback_used=false`; without keys/upstream error, `fallback_used=true` and fallback answer still returns.

## 4) Troubleshooting (short)

- `GET /user-context/{session_id}` returns 404: run PUT first; verify exact `session_id` string.
- Context not persisted in DB: check `SUPABASE_URL`/`SUPABASE_SERVICE_ROLE_KEY`; app silently falls back to in-memory store when Supabase is unavailable.
- PUT appears OK but SQL row missing: confirm backend points to the same Supabase project/environment you are querying.
- `/rag/query` always fallback: verify provider credentials/config; inspect backend logs for `ProviderError`.
- `citations` empty/unexpected: verify retrieval data source (Supabase availability); test with known seeded data.