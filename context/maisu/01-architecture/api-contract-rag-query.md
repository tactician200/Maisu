# API Contract — `POST /rag/query` (FastAPI parallel path)

## Purpose
Return a grounded Bilbao-focused answer using retrieval + LLM, with explicit fallback when evidence is weak.

## Request schema
`Content-Type: application/json`

```json
{
  "query": "Mejor bar de pintxos en Bilbao",
  "top_k": 3,
  "session_id": "smoke-local-001"
}
```

### Fields
- `query` **required**: string, non-empty
- `top_k` optional: integer `1..10` (default: `3`)
- `session_id` optional: string for tracing

### Validation / 4xx
- Empty or missing `query` → `400 invalid_input`
- Malformed JSON body → `400 invalid_json`
- Missing/invalid auth (if enabled) → `401 unauthorized` / `403 forbidden`
- Rate limit exceeded → `429 rate_limited`

## Success response (`200`)
```json
{
  "ok": true,
  "answer": "Empieza por Plaza Nueva y luego prueba...",
  "citations": [
    {
      "id": "src_012#chunk_03",
      "title": "Bilbao Family Guide",
      "url": "https://example.org/bilbao",
      "snippet": "..."
    }
  ],
  "confidence": 0.81,
  "fallback": false,
  "fallback_reason": null,
  "meta": {
    "retrieval_k": 3,
    "latency_ms": 840,
    "path": "parallel",
    "request_id": "req_abc123",
    "trace_id": "trc_abc123"
  }
}
```

## Fallback behavior (`200` with `fallback=true`)
Trigger fallback when retrieval is empty, confidence is below threshold, scope is out of Bilbao MVP, or retrieval/LLM quality is insufficient.

```json
{
  "ok": true,
  "answer": "No tengo suficiente evidencia fiable todavía. ¿Prefieres Casco Viejo o Abando?",
  "citations": [],
  "confidence": 0.24,
  "fallback": true,
  "fallback_reason": "low_retrieval_confidence",
  "meta": {
    "retrieval_k": 0,
    "latency_ms": 410,
    "path": "parallel",
    "request_id": "req_def456"
  }
}
```

## Error model (non-2xx)
```json
{
  "ok": false,
  "error": {
    "code": "rate_limited",
    "message": "Too many requests",
    "retry_after_ms": 1000
  },
  "meta": {
    "request_id": "req_xyz789",
    "path": "parallel"
  }
}
```

### Error codes
- `invalid_input` (`400`)
- `invalid_json` (`400`)
- `unauthorized` (`401`)
- `forbidden` (`403`)
- `rate_limited` (`429`)
- `timeout` (`504`)
- `upstream_error` (`502`)
- `internal_error` (`500`)

## Latency objective + observability
- **SLO target (p95):** `<= 2.5s`
- **Hard timeout:** `<= 8s` end-to-end
- Emit/track per request (logs + metrics):
  - `request_id`, `trace_id`, `session_id`
  - `path` (`parallel`)
  - `latency_ms`
  - `retrieval_k`, `confidence`, `fallback`, `fallback_reason`
  - HTTP `status_code`, `error.code` (if any)
