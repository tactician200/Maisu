# 🧠 Bilbot — Reglas de Onboarding Conversacional

Status: draft (captured from product direction)
Date: 2026-02-19

## 1. Principio Base
- No hacer “formulario”.
- No hacer onboarding explícito.
- Iniciar ayudando.
- Preguntar solo lo necesario para generar valor inmediato.
- El resto se recolecta progresivamente y en contexto.

---

## 2. Datos Críticos (Primer Minuto)
Recolectar como máximo 3–4 variables iniciales:
- Duración de estancia
- Tipo de viaje (solo/pareja/amigos/familia/trabajo)
- Interés dominante (cultura / gastronomía / naturaleza / mixto)
- Zona de alojamiento (opcional)

Objetivo: poder generar una primera recomendación relevante de inmediato.

---

## 3. Datos Contextuales (Recolectar Durante Conversación)
Preguntar solo cuando la recomendación lo requiera:
- Presupuesto gastronómico
- Restricciones alimentarias
- Preferencia formal vs informal
- Transporte disponible
- Limitaciones de movilidad
- Ritmo del viaje
- Nivel de profundidad cultural deseado

Nunca preguntar estos datos sin necesidad contextual.

---

## 4. Datos Inferidos (Sin Preguntar Directamente)
Recolectar mediante análisis de comportamiento:
- Nivel de gasto estimado
- Preferencia por lugares turísticos vs locales
- Categorías más consultadas
- Nivel cultural (según tipo de preguntas)
- Apertura a recomendaciones nuevas
- Sensibilidad al clima

Estos datos deben alimentar el sistema de personalización y ranking RAG.

---

## 5. Flujo de Recolección por Fases
### Fase 1 – Activación
Recolectar solo variables críticas.
Entregar valor inmediato.

### Fase 2 – Contextualización
Preguntar micro-variables solo cuando impactan una decisión.

### Fase 3 – Aprendizaje Adaptativo
Actualizar perfil dinámicamente con cada interacción.

---

## 6. Reglas de Experiencia
- Máximo 1–2 preguntas seguidas.
- Cada pregunta debe estar ligada a una recomendación concreta.
- Evitar bloques largos de preguntas.
- Priorizar conversación natural sobre completitud de datos.
- Siempre responder algo útil antes o después de preguntar.

---

## 7. Modelo Técnico Recomendado
- Perfil de usuario incremental (JSON dinámico).
- Actualización automática tras cada respuesta relevante.
- Persistencia en Supabase asociada a `session_id`.
- Uso del perfil como input prioritario en el prompt del LLM.
- Integración del perfil en filtros SQL y ranking vectorial.

---

## 8. Filosofía Operativa
- Conversación primero, datos después.
- Personalización progresiva.
- Valor inmediato > precisión absoluta inicial.
- Perfil completo no es requisito para empezar a ayudar.
