# RAG Pipeline (Observed Runtime)

This describes the live behavior implemented in `backend/app/main.py`, `retrieval.py`, and `providers.py`.

## Endpoint flow: `POST /rag/query`

1. **Validate request body** (`QueryRequest`)
   - Requires `query` (min length 1)
   - Optional: `session_id`, `lang`
   - Invalid input returns FastAPI validation error (`422`, `detail[]`).

2. **Retrieve documents**
   - Handler calls `retrieve_documents(query=request.query, top_k=3)`.
   - Retrieval behavior:
     - If Supabase env vars are missing (`SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`) ⇒ return mock docs.
     - If Supabase request errors or returns empty list ⇒ return mock docs.
     - If Supabase returns rows, rows are normalized into citation shape (`id/title/snippet/source`).

3. **Generate answer (provider path)**
   - Tries `OpenAIProvider.generate(query, documents, lang)`.
   - Provider builds prompt from retrieved docs and calls OpenAI Responses API.
   - On success:
     - `answer = result.answer`
     - `provider = result.provider` (currently `openai`)
     - `fallback_used = false`

4. **Fallback on provider failure**
   - If generation raises `ProviderError`:
     - Build answer with `build_fallback_answer(query, documents, lang)`.
     - `provider = "fallback"`
     - `fallback_used = true`
   - Fallback text format is fixed 3 sections:
     - Spanish: `1) Resumen`, `2) Plan recomendado`, `3) Consejos útiles`
     - English when `lang` starts with `en`.

5. **Return response** (`QueryResponse`)
   - Includes:
     - `answer`
     - `citations` (the retrieved docs used as context)
     - `latency_ms` (integer elapsed handler time)
     - `fallback_used`
     - `provider`

## Concrete response contracts

### Success (`200`)

```json
{
  "answer": "...",
  "citations": [
    {
      "id": "mock-1",
      "title": "Bilbao Casco Viejo",
      "snippet": "Zona ideal para pintxos y ambiente local.",
      "source": "mock://places/casco-viejo"
    }
  ],
  "latency_ms": 42,
  "fallback_used": false,
  "provider": "openai"
}
```

### Validation error (`422`)

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

## Fallback and citations: clarifications

- Fallback is **provider-failure based**, not confidence based.
- `citations` are **retrieval output only**; they do not depend on provider text content.
- Because retrieval has mock fallback, citation arrays are typically non-empty even during provider failures.
- Endpoint does **not** expose `top_k` in request schema; it is fixed internally at 3 for now.

## QA acceptance checklist (compact)

- [ ] Invalid body (`{}`) returns `422` with `detail` array and missing `query` location.
- [ ] Empty query (`{"query":""}`) returns `422` string length validation error.
- [ ] Provider success path returns `provider="openai"`, `fallback_used=false`.
- [ ] Forced provider error returns `provider="fallback"`, `fallback_used=true`, and fallback 3-section answer.
- [ ] Both success and fallback responses include `citations` array with `id/title/snippet/source` fields.
- [ ] `latency_ms` is present and integer in `200` responses.
