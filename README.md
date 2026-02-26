# 🏔️ BILBOT / MAISU — Tourism AI MVP (Bilbao)

Chatbot turístico con personalidad local vasca usando **n8n + Supabase + Claude + RAG**.

## 🚀 Quick Start

1. Configura Supabase y crea schema:
   - `database/schema.sql`
   - `database/seed-data.sql`
   - `database/expresiones-vascas.sql`
   - `database/user_context.sql` (personalización por sesión/usuario)
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

Guía detallada: **`SETUP.md`**

### Deploy script (2-service architecture)

Para entornos con runtime separado (repo → runtime), usa:

```bash
./scripts/deploy_from_repo.sh [repo_dir] [runtime_dir]
```

El script valida y prioriza el layout de 2 servicios:
- `code/integrations_service` (puerto `8000`)
- `code/llm_service` (puerto `8001`)

También preserva `.env`/`.venv` en runtime, reinicia ambos `uvicorn` y ejecuta health checks con logs accionables en caso de fallo.

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
│   └── user_context.sql
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
