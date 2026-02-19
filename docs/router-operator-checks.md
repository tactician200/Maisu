# Router v1 — Quick Operator Checks

Use these prompts in webhook/chat tests to spot-check route behavior.

## Expected outcomes

| Sample query | Expected route | Why |
|---|---|---|
| "Dame 5 bares de pintxos en Casco Viejo con ambiente tranquilo." | `structured` | explicit count + location + filterable attributes |
| "Cuéntame la historia del Casco Viejo y cómo cambió en el último siglo." | `narrative` | historical/contextual explanation intent |
| "Recomiéndame 3 planes para hoy cerca del Guggenheim y explica por qué valen la pena." | `mixed` | constrained list + rationale/explanation |
| "¿Qué museos abren los lunes y cuál recomiendas para una primera visita?" | `mixed` | structured availability + personalized narrative judgment |
| "¿Qué significa ‘txikiteo’ y cómo vivirlo como local?" | `narrative` | cultural concept + behavioral guidance |

## Fast validation checklist

- `structured`: response should prioritize concrete entities/filters/counts.
- `narrative`: response should prioritize context, explanation, and historical/cultural framing.
- `mixed`: response should include concrete options **and** explicit rationale per option.
- If route seems wrong, re-run with clearer intent markers (e.g., add "lista de 3" for structured, "explica" for narrative).

## Operational note (v1)

Routing is LLM-mediated, so outcomes are probabilistic. Occasional `mixed -> structured` or `mixed -> narrative` drift is expected.
