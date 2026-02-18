# Runbook — RAG Smoke Test (`POST /rag/query`)

Quick verification for the FastAPI parallel path.

## 1) Local endpoint (exact command)
```bash
curl -sS -i -X POST "http://127.0.0.1:8000/rag/query" \
  -H "Content-Type: application/json" \
  -d '{"query":"Mejor bar de pintxos en Bilbao","top_k":3,"session_id":"smoke-local-001"}'
```

## 2) Deployed endpoint (exact command)
Without auth:
```bash
curl -sS -i -X POST "https://<your-host>/rag/query" \
  -H "Content-Type: application/json" \
  -d '{"query":"Plan gastronómico en Bilbao para hoy","top_k":3,"session_id":"smoke-prod-001"}'
```

With API key:
```bash
curl -sS -i -X POST "https://<your-host>/rag/query" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <API_KEY>" \
  -d '{"query":"Plan gastronómico en Bilbao para hoy","top_k":3,"session_id":"smoke-prod-001"}'
```

## 3) Expected outputs
- HTTP `200`
- JSON body not empty
- Core fields present:
  - `ok` (bool)
  - `answer` (string)
  - `fallback` (bool)
  - `meta.latency_ms` (number)
- If `fallback=false`: expect `citations.length >= 1`
- If `fallback=true`: expect `fallback_reason` and usually `citations=[]`

## 4) Fast checks with jq
```bash
# body shape
curl -sS -X POST "http://127.0.0.1:8000/rag/query" \
  -H "Content-Type: application/json" \
  -d '{"query":"Qué ver en Bilbao en 1 día","top_k":3}' | jq '{ok, fallback, citations: (.citations|length), latency_ms: .meta.latency_ms, error: .error.code}'
```

## 5) Failure diagnosis checklist

### A) Empty body
- Check service is up and route exists (`/rag/query`)
- Verify reverse proxy is not stripping response body
- Inspect app logs for serialization/panic after status write

### B) `429 rate_limited`
- Confirm rate limit policy for smoke IP/token
- Retry with backoff (e.g., 1s → 2s → 4s)
- Validate `retry_after`/`retry_after_ms` if present

### C) Timeout (`504` / client timeout)
- Increase client timeout (`--max-time 15` for smoke)
- Check upstream latency (retrieval/LLM)
- Confirm parallel path is enabled and not falling back to slow serial flow

### D) Bad key (`401`/`403`)
- Confirm `Authorization: Bearer <API_KEY>` format
- Ensure key is valid for target environment
- Verify no extra spaces/newlines in injected secret

## 6) One-line pass criteria
Smoke test passes when endpoint returns HTTP 200 with valid JSON and either:
- grounded answer (`fallback=false` + citations), or
- explicit safe fallback (`fallback=true` + reason).
