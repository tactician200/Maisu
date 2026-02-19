# API Contracts

## POST `/rag/query`

Grounded tourism answer endpoint using retrieval + provider generation with graceful fallback.

### Request schema
`Content-Type: application/json`

```json
{
  "query": "¿Qué ver en Bilbao?",
  "session_id": "s1",
  "lang": "es"
}
```

| Field | Type | Required | Notes |
|---|---|---:|---|
| `query` | string | yes | Minimum length `1` (`Field(min_length=1)`). |
| `session_id` | string \| null | no | Accepted but currently not used by runtime logic. |
| `lang` | string \| null | no | Passed to provider and fallback formatter (e.g. `en` returns English fallback text). |

### Success response (`200`)

```json
{
  "answer": "1) Resumen...",
  "citations": [
    {
      "id": "mock-1",
      "title": "Bilbao Casco Viejo",
      "snippet": "Zona ideal para pintxos y ambiente local.",
      "source": "mock://places/casco-viejo"
    }
  ],
  "latency_ms": 123,
  "fallback_used": false,
  "provider": "openai"
}
```

#### Response fields
- `answer` (`string`): Generated text from provider, or fallback text if provider fails.
- `citations` (`Citation[]`): Documents returned by retrieval step (currently `top_k=3` internally).
  - `Citation`: `{ id: string, title: string, snippet: string, source: string }`
- `latency_ms` (`integer`): End-to-end handler latency in milliseconds.
- `fallback_used` (`boolean`): `true` only when provider generation raises `ProviderError`.
- `provider` (`string`): Provider label from generation path (`"openai"`) or `"fallback"`.

### Validation error schema (`422`)

FastAPI/Pydantic validation errors are returned as:

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "query"],
      "msg": "Field required",
      "input": {}
    }
  ]
}
```

Example: empty `query`:

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "query"],
      "msg": "String should have at least 1 character",
      "input": "",
      "ctx": { "min_length": 1 }
    }
  ]
}
```

### Runtime behavior notes

#### Fallback behavior
- Trigger condition: provider generation throws `ProviderError` (e.g., missing API key, upstream timeout/status error).
- Effect:
  - `fallback_used = true`
  - `provider = "fallback"`
  - `answer` built from local fallback template using top retrieved document titles.
- Non-trigger case: if provider returns a successful payload without `output_text`, runtime still returns `fallback_used = false` with default answer text (`"No he podido generar una respuesta en este momento."`).

#### Citation behavior
- `citations` always come from retrieval output, not from model output.
- Current endpoint calls retrieval with fixed `top_k=3`.
- Retrieval may use Supabase when configured; if unavailable/error/empty, runtime falls back to bundled mock documents, so citations are usually non-empty.

#### Router visibility (v1)
- SQL/RAG/Hybrid route selection is handled upstream (conversation orchestration/tool-use layer), not inside `/rag/query`.
- Therefore this API contract does not expose `route_type`, route confidence, or route trace.
- Operational implication: validate routing from orchestrator logs/observability, not from this endpoint response alone.

## QA acceptance checklist (compact)

- [ ] `POST /rag/query` with valid body returns `200` and keys: `answer`, `citations`, `latency_ms`, `fallback_used`, `provider`.
- [ ] Missing `query` returns `422` with `detail[0].type = "missing"` and `loc = ["body","query"]`.
- [ ] Empty `query` returns `422` with `detail[0].type = "string_too_short"`.
- [ ] Forced provider failure (e.g., mock `ProviderError`) returns `200` with `fallback_used=true`, `provider="fallback"`, and 3-section fallback answer.
- [ ] Happy path returns `fallback_used=false`, `provider="openai"`, and `citations` array populated from retrieval docs.
- [ ] `citations[*]` objects contain exactly `id`, `title`, `snippet`, `source`.
