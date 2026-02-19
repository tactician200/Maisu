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
     - Query text is tokenized and matched against `nombre/descripcion/title/snippet` to improve lexical recall.
     - Results are scored deterministically (phrase + token matches, with optional historical boost).
     - If `SUPABASE_HISTORY_TABLE` is configured, retrieval also queries that table and can interleave history/place citations for history-oriented queries.
     - Rows are normalized into citation shape (`id/title/snippet/source`) with stable tie-break ordering.

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

## Router v1 (SQL/RAG/Hybrid) behavior

`/rag/query` itself always executes the same backend pipeline (retrieve docs + generate/fallback). Query routing decisions for SQL vs RAG vs Hybrid are made in the conversational layer (n8n agent/tool selection), not by the FastAPI endpoint.

### Route types

- **Structured route (`structured`)**: factual/filtered requests where tabular fields dominate (e.g., neighborhood, budget, opening hours, “top N”).
- **Narrative route (`narrative`)**: explanatory/open-ended requests (history, culture, context, storytelling, comparisons with nuance).
- **Mixed route (`mixed`)**: requests combining constraints + explanation (e.g., “3 bars in Casco Viejo and explain why each”).

### Decision rules (high-level, v1)

- If the user intent is primarily **lookup/filter/list**, prefer **structured** (SQL tool first).
- If intent is primarily **explain/describe/contextualize**, prefer **narrative** (RAG/vector retrieval first).
- If both are explicit in one prompt, prefer **mixed** (combine SQL facts + RAG context, then synthesize).
- On uncertainty, v1 tends to start with one tool and may or may not call the second tool depending on LLM judgment.

### Behavior per route

| Route | Primary source | Typical output | Strengths | Failure pattern |
|---|---|---|---|---|
| `structured` | SQL (`places`-style fields) | concise lists, filters, attributes | precision on explicit constraints | thin cultural/context detail |
| `narrative` | RAG/vector + generated synthesis | explanatory paragraphs/bullets | richer context and storytelling | may miss hard constraints/counts |
| `mixed` | SQL + RAG + synthesis | ranked/curated list with rationale | best balance of precision + context | higher latency, occasional tool under-use |

### Known limitations (v1)

- Route choice is **implicit** (LLM/tool-use behavior), not an explicit deterministic classifier.
- No route label is returned in API responses (`QueryResponse` has no `route_type` field).
- Mixed queries can degrade to single-route behavior if the agent decides to call only one tool.
- No confidence score/trace for route decisions in public contract.
- SQL and RAG retrieval can diverge in coverage/recency, yielding occasional inconsistency between facts and narrative.

## QA acceptance checklist (compact)

- [ ] Invalid body (`{}`) returns `422` with `detail` array and missing `query` location.
- [ ] Empty query (`{"query":""}`) returns `422` string length validation error.
- [ ] Provider success path returns `provider="openai"`, `fallback_used=false`.
- [ ] Forced provider error returns `provider="fallback"`, `fallback_used=true`, and fallback 3-section answer.
- [ ] Both success and fallback responses include `citations` array with `id/title/snippet/source` fields.
- [ ] `latency_ms` is present and integer in `200` responses.
