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
Endpoint: `POST /onboarding/next`

Request (example):
```json
{
  "session_id": "ops-onboarding-smoke-001",
  "message": "Hola, venimos mi pareja y yo por 3 días"
}
```

Response (example):
```json
{
  "session_id": "ops-onboarding-smoke-001",
  "onboarding_next": {
    "ask": "¿Es vuestra primera vez en Bilbao?",
    "fields": ["first_time"],
    "phase": "activation",
    "done": false
  },
  "profile_patch": {
    "trip_type": "couple",
    "stay_duration_days": 3
  }
}
```

Completion behavior:
- When onboarding is done, return `onboarding_next.done=true` or omit `onboarding_next`.
- The response may still include `profile_patch` updates on the final turn.

## Rollout/rollback
- Rollout: enable onboarding in the orchestration layer for new sessions only.
- Rollback: disable onboarding and route requests directly to `/rag/query`.
- If a session is mid-onboarding, allow it to complete or reset its onboarding state.

## Success signals
- <= 3 onboarding questions per new session.
- Users receive a useful answer before or alongside each onboarding question.
- `profile_patch` populates at least 2 of 3 critical fields for new sessions.
