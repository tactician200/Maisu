# 🏔️ BILBOT / MAISU — Tourism AI MVP (Bilbao)

Chatbot turístico con personalidad local vasca usando **n8n + Supabase + Claude + RAG**.

## 🚀 Quick Start

1. Configura Supabase y crea schema:
   - `database/schema.sql`
   - `database/seed-data.sql`
   - `database/expresiones-vascas.sql`
   - `database/user_context.sql` (personalización por sesión/usuario)
   - `database/20260223_add_events_table_option_b.sql` (tabla `events`)
   - `database/seed-events.sql` (seed idempotente de 5 eventos)
2. Importa workflow principal en n8n:
   - `n8n/bilbot-main-conversation.json`
3. (Opcional) Importa workflow de data ingestion:
   - `n8n/data-ingestion-workflow.json`
4. Configura credenciales en n8n (Supabase, Anthropic, OpenAI).
5. Activa workflow y prueba webhook.
6. Test rápido por script:
   ```bash
   ./scripts/test-webhook.sh https://[tu-n8n].app.n8n.cloud/webhook/bilbot
   ```
7. Smoke test del endpoint RAG (opcional):
   ```bash
   ./scripts/rag-smoke-test.sh https://[tu-endpoint]/rag/query "Mejor bar de pintxos en Bilbao"
   ```
8. Levanta el backend FastAPI local (opcional, paralelo a n8n):
   ```bash
   cd backend
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   export SUPABASE_URL="https://[tu-proyecto].supabase.co"
   export SUPABASE_SERVICE_ROLE_KEY="[tu-service-role-key]"
   uvicorn app.main:app --reload --port 8000
   ```
   > Si no defines `SUPABASE_URL` + `SUPABASE_SERVICE_ROLE_KEY`, el retrieval usa documentos mock de fallback.
9. Smoke test del backend API local:
   ```bash
   ./scripts/rag-smoke-test-api.sh http://127.0.0.1:8000 "Mejor bar de pintxos en Bilbao"
   ```
10. Test rápido de backend:
   ```bash
   cd backend && pytest -q
   ```

11. (Opcional) Sincroniza embeddings de `events` -> `places_embeddings` (`source_type='event'`):
   ```bash
   export SUPABASE_DB_URL='postgresql://...'
   # Si OPENAI_API_KEY no está definido, el script entra en dry-run seguro automáticamente
   python scripts/sync_event_embeddings.py --db-url "$SUPABASE_DB_URL"
   ```
   Flags útiles:
   - `--dry-run` (fuerza modo simulación)
   - `--limit 50` (procesa solo N eventos)

Guía detallada: **`SETUP.md`**

---

## 📁 Estructura del Proyecto

```text
.
├── README.md
├── SETUP.md
├── docs/
│   ├── bilbot-proyecto-mvp.md
│   ├── system-prompt-aitor.md
│   ├── n8n-workflows-guide.md
│   └── ...
├── backend/
│   ├── app/
│   │   └── main.py
│   ├── tests/
│   └── requirements.txt
├── n8n/
│   └── bilbot-main-conversation.json
│   └── data-ingestion-workflow.json
├── database/
│   ├── schema.sql
│   ├── seed-data.sql
│   ├── expresiones-vascas.sql
│   ├── user_context.sql
│   ├── 20260223_add_events_table_option_b.sql
│   └── seed-events.sql
└── scripts/
    └── test-webhook.sh
    └── rag-smoke-test.sh
    └── rag-smoke-test-api.sh
```

---

## 📚 Documentación

- Setup técnico completo: `SETUP.md`
- Documento de producto / arquitectura MVP: `docs/bilbot-proyecto-mvp.md`
- Prompt del asistente (Aitor): `docs/system-prompt-aitor.md`
- Guía extendida de workflow n8n: `docs/n8n-workflows-guide.md`

### Personalización: `database/user_context.sql`

**Propósito**
- Guardar metadatos mínimos de personalización por sesión para adaptar respuestas (nombre, idioma y preferencias ligeras).

**Suposiciones de entorno**
- PostgreSQL 14+ (compatible con Supabase).
- Esquema `public` activo.
- Permisos para crear tabla, índices, función y trigger.

**Ejemplos de consultas**

```sql
-- Upsert de contexto por sesión
INSERT INTO public.user_context (session_id, user_id, name, language, preferences)
VALUES ('session-123', NULL, 'Ane', 'es', '{"tone":"friendly","likes":["pintxos"]}'::jsonb)
ON CONFLICT (session_id)
DO UPDATE SET
  user_id = EXCLUDED.user_id,
  name = EXCLUDED.name,
  language = EXCLUDED.language,
  preferences = EXCLUDED.preferences;

-- Leer contexto para personalizar una respuesta
SELECT session_id, user_id, name, language, preferences, updated_at
FROM public.user_context
WHERE session_id = 'session-123';

-- Buscar sesiones con preferencia concreta
SELECT session_id, preferences
FROM public.user_context
WHERE preferences ? 'tone';
```

**Privacidad**
- Almacenar solo metadatos de personalización (no PII sensible, no contenido completo de conversaciones).

---

## 📅 Seed de eventos (`database/seed-events.sql`)

Script versionado e idempotente para poblar 5 eventos iniciales en la tabla `events`.
Usa `ON CONFLICT (title, start_at) DO UPDATE`, por lo que se puede reejecutar sin duplicar filas.

**Supabase SQL Editor**
1. Ejecuta primero `database/20260223_add_events_table_option_b.sql`.
2. Ejecuta después `database/seed-events.sql`.

**CLI con `psql`**
```bash
psql "$SUPABASE_DB_URL" -v ON_ERROR_STOP=1 -f database/20260223_add_events_table_option_b.sql
psql "$SUPABASE_DB_URL" -v ON_ERROR_STOP=1 -f database/seed-events.sql
```

**Rollback rápido (solo seeds de eventos)**
```sql
DELETE FROM events
WHERE (title, start_at) IN (
  ('Aste Nagusia 2026 - Fuegos Artificiales', '2026-08-22T20:30:00Z'::timestamptz),
  ('Aste Nagusia 2026 - Concierto en Abandoibarra', '2026-08-24T19:00:00Z'::timestamptz),
  ('Mercado de la Ribera - Cata de producto local', '2026-03-14T11:00:00Z'::timestamptz),
  ('Visita guiada - Casco Viejo histórico', '2026-04-11T09:30:00Z'::timestamptz),
  ('Bilbao BBK Live 2026 - Jornada 1', '2026-07-09T16:00:00Z'::timestamptz)
);
```

---

## ✅ Estado actual del repo

Incluye:
- SQL de esquema y seed data
- Workflow principal de conversación
- Prompt y documentación de producto
- Script de test para webhook
- Workflow de data ingestion (places + historia_vasca + embeddings)
- Backend FastAPI mínimo para endpoint `/rag/query` con fallback

---

## 🧪 Test mínimo manual

```bash
curl -X POST "https://[tu-n8n].app.n8n.cloud/webhook/bilbot" \
  -H "Content-Type: application/json" \
  -d '{
    "chatInput": "Hola, recomiéndame un bar de pintxos",
    "sessionId": "test-session"
  }'
```

Si responde con contenido contextual (lugares/historia), el flujo base está OK.
