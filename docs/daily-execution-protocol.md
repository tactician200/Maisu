# Maisu Daily Execution Protocol (Team + Agents)

## 1) Comencemos el día (10–15 min)

Use this exact checklist at start:

1. Yesterday checkpoint
   - Done (commits + test result)
   - In progress
   - Blocked
2. Production/safety quick scan
   - API health
   - latest smoke status
   - open risks
3. Today objective (single sentence)
4. Top 3 tasks (ship-focused)
5. Agent lane assignment
   - Lane A: implementation
   - Lane B: tests/validation
   - Lane C: docs/ops
6. Gate definition (mandatory before QA release)
   - one-command gate: `make qa-release` (default release gate workflow; alias: `make qa-gate`)
   - required tests
   - smoke checks
   - rollback command

### Prompt template (ES)
"Comencemos el día: resume lo hecho, lo en curso y bloqueado; define objetivo de hoy, top 3 tareas, asignación de lanes (impl/tests/docs), gate de validación y rollback."

### Prompt template (EN)
"Start the day: summarize done/in-progress/blocked, define today objective, top 3 tasks, lane allocation (impl/tests/docs), validation gate, and rollback."

---

## 2) Cierre intradía (per milestone)

- What changed (files + commit)
- Test/smoke result
- Risk notes
- Decision needed (if any)

### Implementation -> QA Release handoff (operator one-command)
1. From repo root run: `make qa-release`
2. Confirm terminal ends with: `QA_GATE_PASS`
3. Only then mark the item as ready for QA release/handoff

---

## 3) Cerramos el día (10 min)

1. Delivered today
2. Validation evidence
3. Open issues/blockers
4. Exact next starting point for tomorrow
5. Rollback references

### Prompt template (ES)
"Cerramos el día: entregado, validación, pendientes/bloqueos, primer paso de mañana y rollback."

### Prompt template (EN)
"Close the day: delivered work, validation, pending/blockers, first step tomorrow, and rollback references."
