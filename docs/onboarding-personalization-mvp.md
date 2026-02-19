# Bilbot — Onboarding & Personalization Variables (MVP)

Status: draft (user-approved direction)
Date: 2026-02-19

## Product decision captured
We will implement **full personalization** for Bilbot, including a **conversational, playful onboarding** for new users.

Goal: collect high-impact profile data with minimal friction (not a long questionnaire), using dynamic questioning + inference from conversation.

---

## 1) Perfil Básico (critical)
- Idioma principal
- Idioma secundario
- Nivel de español
- Tipo de viaje (solo/pareja/amigos/familia/trabajo)
- Edades relevantes (niños / mayores)
- Duración de estancia
- Primera vez en Bilbao (sí/no)

## 2) Gastronomía
- Presupuesto por comida (rango)
- Restricciones alimentarias
- Preferencias gastronómicas (pintxos, alta cocina, sidrería, etc.)
- Interés en experiencias gastronómicas (sí/no)

## 3) Estilo de experiencia
- Preferencia outdoor vs indoor (escala)
- Ritmo de viaje (relax / equilibrado / intenso)
- Intereses principales (historia, arquitectura, naturaleza, deporte, arte, vida nocturna, etc.)
- Sensibilidad a trampas turísticas (alta/media/baja)

## 4) Prioridades del viaje
- Lugares “imprescindibles” (abierto)
- Profundidad cultural deseada (breve/detallado)
- Apertura a recomendaciones sorpresa (sí/no)

## 5) Logística
- Zona de alojamiento
- Medio de transporte preferido
- Limitaciones de movilidad
- Viaja con mascota (sí/no)

## 6) Contexto dinámico (inferencia interna)
- Nivel de gasto estimado
- Categorías más consultadas
- Tiempo de interacción
- Clima actual (impacto en recomendaciones)
- Feedback implícito/explicito del usuario

---

## Conversational collection strategy (MVP)

### Principle
Ask **few high-yield questions first**, infer the rest from natural conversation, and only ask follow-ups when uncertainty impacts recommendation quality.

### Flow
1. **Welcome + mini framing (1 message)**
   - playful tone + explain benefit: “I can tailor recommendations quickly.”
2. **Critical seed capture (2–3 prompts max)**
   - language, trip type, stay duration, first-time status.
3. **Adaptive branch (1 prompt)**
   - detect user intent (food / culture / logistics / nightlife) and ask one focused question.
4. **Progressive profiling**
   - fill missing fields passively from regular chat.
5. **Micro-confirmation**
   - “I got X/Y/Z right, want to adjust anything?”
6. **Continuous refresh**
   - preferences update from explicit corrections + behavior.

### Don’t-do list
- No long form with many questions in a row.
- No repeated questions if confidence already high.
- No blocking recommendations while profile is incomplete.

---

## Data confidence model (recommended)
Store each field with:
- `value`
- `confidence` (low/medium/high)
- `source` (`explicit_user`, `inferred`, `behavior`)
- `updated_at`

This allows safe inference while preferring explicit user input.

---

## Priority for implementation

### Phase 1 (now)
- Persist critical profile + food + experience basics.
- Add onboarding conversational script with max 3 initial prompts.
- Add profile confidence metadata.

### Phase 2
- Dynamic context inference loop (behavior + query categories).
- Lightweight profile edit command ("update my preferences").

### Phase 3
- Personalization analytics and recommendation lift tracking.

---

## Immediate implementation tasks (next sprint)
1. Add `onboarding_state` and `profile_fields` model in backend.
2. Add endpoint(s) for onboarding state progression.
3. Add dynamic question selector (rule-based first).
4. Add profile confidence + source tracking.
5. Add tests for:
   - max initial question limit
   - explicit override precedence
   - no-repeat question behavior
   - recommendation generation with incomplete profile
