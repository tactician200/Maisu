# Runbook — Fallback Decision Matrix (`POST /rag/query`)

## Objective
Ensure predictable behavior when evidence quality is insufficient.

## Decision Matrix
| Condition | Signal | Action | Response Style |
|---|---|---|---|
| No retrieved chunks | `retrieval_k=0` | Trigger fallback | Transparent limitation + 1 clarifying question |
| Low confidence | `confidence < threshold` | Trigger fallback | Avoid specific claims; ask narrowing question |
| Conflicting sources | high disagreement / no tie-breaker | Trigger fallback | State uncertainty; ask user preference/scope |
| Out-of-scope request | city/domain outside MVP | Scope fallback | State Bilbao-only scope; offer in-scope alternative |
| Upstream provider error | embeddings/LLM failure | Technical fallback | Short apology + retry suggestion |

## Thresholds (initial)
- `confidence_threshold`: 0.55
- `min_citations_for_grounded_answer`: 1
- `max_duplicate_chunks_per_source`: 2

## Fallback Templates
1. **No evidence**
   - “I don’t have enough reliable information yet for that request. Can you narrow it to Bilbao neighborhood, budget, or dates?”
2. **Low confidence**
   - “I’m not confident enough to answer precisely yet. Do you want family-friendly, cultural, or food-focused options in Bilbao?”
3. **Out of scope**
   - “Current MVP scope is Bilbao. I can still help with Bilbao alternatives if you want.”
4. **Technical issue**
   - “I’m having a temporary retrieval issue right now. Please retry in a moment.”

## Logging Requirements
On every fallback, log:
- `fallback=true`
- `fallback_reason`
- `confidence`
- `retrieval_k`
- `query_hash/session_id`
