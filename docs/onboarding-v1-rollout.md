# Onboarding v1 Rollout (Operator + Product)

Status: ready for rollout
Date: 2026-02-20

## Goal (v1)
Capture the minimum critical context in <= 3 prompts while delivering immediate recommendations. No explicit “form” or blocking flow.

## Product behavior (concise)
- Ask at most 1 question per turn; total initial questions <= 3.
- Start with value: answer the user, then ask a single high-yield question.
- Prioritize critical fields first: `stay_duration_days`, `trip_type`, `first_time`.
- Infer when possible; only ask if uncertainty blocks a recommendation.

## Operator scope
In v1 we only guarantee:
- Conversational onboarding prompt selection.
- Profile patching for the three critical fields.
- Onboarding state stored per `session_id`.

Out of scope for v1:
- Full profile completion.
- Analytics dashboards.
- Data policy and long-term retention rules.

## API contract (minimal)
Endpoint: `POST /rag/query` (onboarding is embedded in this response)

Request (example):
```json
{
  "query": "Hola, venimos mi pareja y yo por 3 días",
  "session_id": "ops-onboarding-smoke-001"
}
```

Response (example):
```json
{
  "answer": "...",
  "citations": [],
  "latency_ms": 98,
  "fallback_used": false,
  "provider": "openai",
  "onboarding_next": {
    "field": "stay_duration",
    "question": "¿Cuántos días vas a estar en Bilbao?"
  }
}
```

Completion behavior:
- When onboarding is done, `onboarding_next` is omitted.
- Base response fields (`answer`, `citations`, `provider`, `fallback_used`) remain unchanged.

## Rollout/rollback
- Rollout: enable onboarding in the orchestration layer for new sessions only.
- Rollback: disable onboarding and route requests directly to `/rag/query`.
- If a session is mid-onboarding, allow it to complete or reset its onboarding state.

## Success signals
- <= 3 onboarding questions per new session.
- Users receive a useful answer before or alongside each onboarding question.
- `profile_patch` populates at least 2 of 3 critical fields for new sessions.
