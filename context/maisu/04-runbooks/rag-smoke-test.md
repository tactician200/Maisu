# Runbook — RAG Smoke Test (`POST /rag/query`)

Quick verification for FastAPI core (`backend/app/main.py`).

## Endpoint contract (actual)
`POST /rag/query` returns:
- `answer` (string)
- `citations` (array)
- `latency_ms` (int)
- `fallback_used` (bool)
- `provider` (`openai` | `fallback`)

## 1) Local health check
```bash
curl -sS http://127.0.0.1:8000/health
# expected: {"status":"ok"}
```

## 2) Local smoke (normal path)
```bash
curl -sS -X POST "http://127.0.0.1:8000/rag/query" \
  -H "Content-Type: application/json" \
  -d '{"query":"Mejor bar de pintxos en Bilbao","session_id":"smoke","lang":"es"}'
```

Expected:
- HTTP `200`
- JSON with all contract fields
- `citations` length `>= 1`

## 3) Forced fallback smoke (provider contingency)
Run API with empty OpenAI key to validate graceful fallback:
```bash
OPENAI_API_KEY='' SUPABASE_URL='' SUPABASE_SERVICE_ROLE_KEY='' \
PYTHONPATH=. uvicorn app.main:app --host 127.0.0.1 --port 8001
```
Then:
```bash
curl -sS -X POST "http://127.0.0.1:8001/rag/query" \
  -H "Content-Type: application/json" \
  -d '{"query":"Ruta rápida por Bilbao","session_id":"smoke","lang":"es"}'
```
Expected:
- HTTP `200`
- `fallback_used: true`
- `provider: "fallback"`

## 4) Deployed smoke template
```bash
BASE_URL="https://<your-host>"
curl -sS -X POST "$BASE_URL/rag/query" \
  -H "Content-Type: application/json" \
  -d '{"query":"Plan gastronómico en Bilbao para hoy","session_id":"smoke-prod-001","lang":"es"}'
```

If deployment requires auth, add:
```bash
-H "Authorization: Bearer <API_KEY>"
```

## 5) Evidence captured (2026-02-18)
Local validation:
- `python3 -m venv .venv && pip install -r requirements.txt`
- `PYTHONPATH=. pytest -q` → `7 passed`

Observed responses:
- Path A (default env):
  - `provider: "openai"`
  - `fallback_used: false`
  - `latency_ms: 3401`
  - `citations: 3`
- Path B (forced contingency env):
  - `provider: "fallback"`
  - `fallback_used: true`
  - `latency_ms: 0`
  - `citations: 3`
- Path C (external temporary smoke):
  - `GET http://3.83.97.23:8000/health` → `HTTP 200`
  - `POST /rag/query` → `provider: "openai"`, `fallback_used: false`, `latency_ms: 3632`, `citations: 3`
  - Temporary public exposure was closed after validation.

## 6) Pass criteria
Smoke passes when `/rag/query` returns HTTP 200 and:
- contract fields are present,
- citations are returned,
- contingency mode works (`fallback_used=true`) when provider is unavailable.
