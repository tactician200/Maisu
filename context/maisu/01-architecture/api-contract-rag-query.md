# API Contract — `POST /rag/query`

## Purpose
Return a grounded tourism answer for Bilbao using retrieval context and explicit citation/fallback behavior.

## Request
```json
{
  "query": "What are the best family activities in Bilbao?",
  "locale": "en",
  "max_citations": 3,
  "session_id": "optional-session-id"
}
```

### Validation Rules
- `query` required, non-empty string (3..1000 chars)
- `locale` optional (default: auto-detect)
- `max_citations` optional, integer (1..5), default `3`
- unknown fields ignored (MVP) or rejected by strict mode

## Success Response (grounded answer)
```json
{
  "ok": true,
  "answer": "You can start with the Guggenheim area...",
  "citations": [
    {
      "id": "src_012#chunk_03",
      "title": "Bilbao Family Guide",
      "url": "https://example.org/bilbao-family-guide",
      "snippet": "Family-friendly activities include..."
    }
  ],
  "confidence": 0.82,
  "fallback": false,
  "meta": {
    "retrieval_k": 6,
    "latency_ms": 1840
  }
}
```

## Fallback Response (low confidence / missing evidence)
```json
{
  "ok": true,
  "answer": "I don’t have enough reliable context yet. Do you want indoor or outdoor options in Bilbao?",
  "citations": [],
  "confidence": 0.24,
  "fallback": true,
  "fallback_reason": "low_retrieval_confidence",
  "meta": {
    "retrieval_k": 0,
    "latency_ms": 920
  }
}
```

## Error Response (standard)
```json
{
  "ok": false,
  "error": {
    "code": "invalid_input",
    "message": "query is required"
  }
}
```

## Error Codes (MVP)
- `invalid_input` — malformed request
- `upstream_error` — embedding/LLM/retrieval provider failure
- `timeout` — pipeline exceeded timeout budget
- `internal_error` — unclassified backend error
