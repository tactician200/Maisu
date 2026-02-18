# 🚀 BILBOT - Guía de Setup e Instalación

**Versión:** 1.0
**Fecha:** 11 febrero 2026
**Tiempo estimado de setup:** 30-45 minutos

---

## 📋 Pre-requisitos

Antes de empezar, asegúrate de tener:

- ✅ **Cuenta n8n Cloud** (Starter Plan o superior)
- ✅ **Cuenta Supabase** (Free tier es suficiente para MVP)
- ✅ **API Key de Anthropic** (Claude Sonnet 4.5)
- ✅ **API Key de OpenAI** (para embeddings text-embedding-3-small)
- ✅ **PostgreSQL client** (psql) para ejecutar scripts SQL
- ⚠️ **Opcional:** Cuenta Google (para Google Sheets y workflow de data ingestion)

### Verificar Accesos

```bash
# Verificar que tienes psql instalado
psql --version

# Si no lo tienes, instala PostgreSQL client:
# macOS: brew install postgresql
# Ubuntu: sudo apt-get install postgresql-client
# Windows: Descarga desde postgresql.org
```

---

## 🗄️ Paso 1: Configurar Supabase

### 1.1 Crear Proyecto en Supabase

1. Ve a [supabase.com](https://supabase.com) e inicia sesión
2. Crea un nuevo proyecto:
   - **Nombre:** `bilbot-mvp` (o el que prefieras)
   - **Base de datos password:** Guarda esta contraseña de forma segura
   - **Región:** Elige la más cercana a tu ubicación (Europe West recomendado)
3. Espera 2-3 minutos mientras se aprovisiona el proyecto

### 1.2 Activar Extensión pgvector

Una vez creado el proyecto:

1. Ve a **SQL Editor** en el panel lateral de Supabase
2. Ejecuta este comando:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

3. Verifica que se activó correctamente:

```sql
SELECT * FROM pg_extension WHERE extname = 'vector';
```

Deberías ver una fila con `vector` en el resultado.

### 1.3 Obtener Credenciales de Supabase

Ve a **Settings → API** y copia:

- ✅ **Project URL:** `https://[tu-proyecto].supabase.co`
- ✅ **anon/public key:** (para client-side, opcional)
- ✅ **service_role key:** (para server-side, **IMPORTANTE** para n8n)

**⚠️ IMPORTANTE:** Nunca compartas tu `service_role` key públicamente. Tiene acceso total a tu base de datos.

### 1.4 Ejecutar Schema SQL

Desde tu terminal, conéctate a Supabase:

```bash
# Conectar a Supabase con psql
psql "postgresql://postgres:[TU-PASSWORD]@db.[TU-PROYECTO].supabase.co:5432/postgres"

# O usando la URL de conexión directa que puedes encontrar en Settings → Database
```

Una vez conectado, ejecuta el schema:

```sql
\i database/schema.sql
```

Deberías ver mensajes de éxito:
```
✅ Schema de BILBOT creado exitosamente
📊 Tablas creadas: 6
🔍 Índices creados: 11
⚡ Funciones creadas: 2
```

### 1.5 Cargar Datos Iniciales

Ejecuta los scripts de seed data:

```sql
-- Cargar lugares y artículos históricos
\i database/seed-data.sql

-- Cargar expresiones vascas
\i database/expresiones-vascas.sql
```

Deberías ver:
```
✅ Seed data cargado exitosamente
📍 Lugares insertados: 20
📚 Artículos históricos: 7
🗣️ Expresiones vascas insertadas: 30+
```

### 1.6 Verificar Instalación

Ejecuta estas queries para verificar:

```sql
-- Verificar tablas creadas
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;

-- Verificar datos en places
SELECT nombre, tipo, barrio FROM places LIMIT 5;

-- Verificar expresiones vascas
SELECT expresion, significado FROM expresiones_vascas WHERE frecuencia_uso = 'muy_común';
```

✅ **Paso 1 completado!** Tu base de datos Supabase está lista.

---

## 🔧 Paso 2: Configurar n8n Cloud

### 2.1 Acceder a n8n Cloud

1. Ve a [n8n.cloud](https://n8n.cloud) e inicia sesión
2. Asegúrate de tener un plan Starter o superior (necesitas webhooks públicos)

### 2.2 Crear Credenciales - Supabase

1. Ve a **Credentials → New**
2. Busca "Supabase" y selecciona
3. Configura:
   - **Host:** `db.[tu-proyecto].supabase.co`
   - **Database:** `postgres`
   - **User:** `postgres`
   - **Password:** [La contraseña que creaste en 1.1]
   - **Port:** `5432`
   - **SSL:** Activado (checked)
4. Haz clic en **Test** para verificar conexión
5. Guarda como "Supabase BILBOT"

**Alternativa usando Service Role:**

1. Busca "Supabase API" en credenciales
2. Configura:
   - **Project URL:** `https://[tu-proyecto].supabase.co`
   - **Service Role Key:** [La key que copiaste en 1.3]
3. Guarda como "Supabase BILBOT API"

### 2.3 Crear Credenciales - Anthropic (Claude)

1. Ve a **Credentials → New**
2. Busca "Anthropic" y selecciona
3. Configura:
   - **API Key:** [Tu API key de Anthropic]
4. Guarda como "Anthropic Claude"

### 2.4 Crear Credenciales - OpenAI (Embeddings)

1. Ve a **Credentials → New**
2. Busca "OpenAI" y selecciona
3. Configura:
   - **API Key:** [Tu API key de OpenAI]
4. Guarda como "OpenAI Embeddings"

### 2.5 Importar Workflow Principal

**Opción A: Crear manualmente (recomendado para aprendizaje)**

Sigue el tutorial en `README.md` y `docs/n8n-workflows-guide.md` para crear el workflow paso a paso.

**Opción B: Importar JSON (más rápido)**

1. Ve a **Workflows → Import from File**
2. Selecciona `n8n/bilbot-main-conversation.json`
3. Verifica que todas las credenciales estén asignadas correctamente
4. Activa el workflow

### 2.6 Activar Workflow y Obtener URL

1. Una vez importado, haz clic en **Active** (toggle en la esquina superior derecha)
2. Busca el nodo **Chat Trigger**
3. Copia la **Production URL**: `https://[tu-n8n].app.n8n.cloud/webhook/bilbot`

✅ **Paso 2 completado!** Tu workflow de n8n está activo.

---

## 🧪 Paso 3: Probar el Chatbot

### 3.1 Test Básico con Navegador

Abre la URL del webhook en tu navegador:
```
https://[tu-n8n].app.n8n.cloud/webhook/bilbot
```

Deberías ver una interfaz de chat con el mensaje:
```
Kaixo! Soy Aitor, tu guía local de Bilbao. ¿En qué puedo ayudarte hoy?
```

### 3.2 Test Conversacional

Envía estos mensajes de prueba:

1. **Test de búsqueda de lugar:**
   ```
   Hola, recomiéndame un restaurante de pintxos en el Casco Viejo
   ```

   ✅ **Esperado:** Aitor recomienda lugares reales de la BD (ej. Gure Toki) con detalles de precio, ubicación y personalidad.

2. **Test de historia:**
   ```
   Cuéntame la historia del Guggenheim
   ```

   ✅ **Esperado:** Respuesta con información del artículo histórico, tono de Aitor, contexto del "Efecto Guggenheim".

3. **Test de itinerario:**
   ```
   Tengo 2 días en Bilbao, ¿qué hago?
   ```

   ✅ **Esperado:** Plan día a día con lugares específicos, horarios, y consejos prácticos.

4. **Test multilingüe:**
   ```
   Hello, what are the best museums in Bilbao?
   ```

   ✅ **Esperado:** Respuesta en inglés manteniendo personalidad de Aitor.

### 3.3 Verificar Logs en n8n

1. Ve a **Executions** en n8n
2. Verifica que las ejecuciones sean exitosas (verde)
3. Revisa los datos que fluyen por cada nodo:
   - Intent Detection debería clasificar correctamente
   - Vector Search debería devolver lugares con similarity > 0.7
   - Claude debería generar respuestas coherentes
   - Chat History debería guardar mensajes en Supabase

### 3.4 Verificar Datos en Supabase

Conéctate a Supabase y verifica que se guarden las conversaciones:

```sql
-- Ver últimas conversaciones
SELECT session_id, message_type, content, created_at
FROM chat_history
ORDER BY created_at DESC
LIMIT 10;

-- Ver analytics
SELECT event_type, COUNT(*)
FROM analytics
GROUP BY event_type;
```

✅ **Paso 3 completado!** El chatbot funciona correctamente.

---

## 📊 Paso 4: Generar Embeddings (Opcional pero Recomendado)

Por ahora, los lugares en `places` no tienen embeddings asociados en `places_embeddings`. Para habilitar la búsqueda vectorial completa:

### 4.1 Workflow de Data Ingestion

1. Importa el workflow `n8n/data-ingestion-workflow.json`
2. Configura las credenciales (OpenAI para embeddings, Supabase Postgres para inserción)
3. (Opcional) Configura variables de entorno en n8n:
   - `MAISU_SHEETS_ID` y `MAISU_SHEETS_TAB` (si usas Google Sheets)
   - `OPENAI_API_KEY` (si usas el nodo HTTP de OpenAI)
4. Ejecuta manualmente el workflow para generar embeddings de los 20 lugares iniciales

### 4.2 Verificar Embeddings

```sql
-- Ver embeddings generados
SELECT pe.id, p.nombre, pe.source_type, pe.created_at
FROM places_embeddings pe
JOIN places p ON pe.source_id = p.id
ORDER BY pe.created_at DESC;
```

✅ **Paso 4 completado!** Búsqueda vectorial activada.

---

## 🔐 Paso 5: Variables de Entorno (Opcional)

Si vas a deployar el frontend o crear scripts auxiliares, crea un archivo `.env`:

```bash
cp .env.example .env
```

Edita `.env` y completa:

```env
# Supabase
SUPABASE_URL=https://[tu-proyecto].supabase.co
SUPABASE_ANON_KEY=[tu-anon-key]
SUPABASE_SERVICE_ROLE_KEY=[tu-service-role-key]

# n8n Webhook
N8N_WEBHOOK_URL=https://[tu-n8n].app.n8n.cloud/webhook/bilbot

# APIs
ANTHROPIC_API_KEY=[tu-api-key]
OPENAI_API_KEY=[tu-api-key]
```

**⚠️ NUNCA comitees el archivo `.env` a git.** Ya está incluido en `.gitignore`.

---

## 🧩 Backend FastAPI RAG (opcional, paralelo a n8n)

Este repo incluye un backend mínimo en `backend/` con:
- `GET /health` → `{ "status": "ok" }`
- `POST /rag/query` → contrato estable `{ answer, citations, latency_ms, fallback_used, provider }`

### Levantar en local

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Variables de entorno backend

```env
OPENAI_API_KEY=[tu-api-key]            # opcional para provider OpenAI
OPENAI_MODEL=gpt-4o-mini               # opcional
OPENAI_TIMEOUT_SECONDS=8               # opcional
SUPABASE_URL=https://[tu-proyecto].supabase.co          # requerido para retrieval real
SUPABASE_SERVICE_ROLE_KEY=[tu-service-role-key]         # requerido para retrieval real
```

Notas:
- Para retrieval real desde Supabase REST debes definir **ambas**: `SUPABASE_URL` y `SUPABASE_SERVICE_ROLE_KEY`.
- Si faltan esas variables o falla la consulta (timeout/error/0 resultados), el backend usa documentos mock de fallback.
- Si OpenAI no está disponible (timeout/rate-limit/credenciales), responde con fallback sin romper el endpoint.

### Test rápido backend

```bash
# tests unitarios
cd backend && pytest -q

# smoke del endpoint
cd .. && ./scripts/rag-smoke-test-api.sh http://127.0.0.1:8000 "Mejor bar de pintxos en Bilbao"
```

## ✅ Verificación Final

### Checklist de Completitud

**Base de Datos:**
- [ ] Extensión pgvector activada
- [ ] 6 tablas creadas (places, places_embeddings, historia_vasca, chat_history, analytics, expresiones_vascas)
- [ ] Índices HNSW y GIN funcionando
- [ ] Funciones `search_places_hybrid()` y `get_chat_memory()` creadas
- [ ] Al menos 20 lugares insertados en `places`
- [ ] Al menos 7 artículos en `historia_vasca`
- [ ] Al menos 30 expresiones en `expresiones_vascas`

**n8n Workflow:**
- [ ] Workflow principal importado y **activado**
- [ ] Credenciales configuradas (Supabase, Anthropic, OpenAI)
- [ ] Chat Trigger devuelve URL pública funcional
- [ ] Test manual: "Hola" → Respuesta de Aitor en < 3 segundos

**Testing Funcional:**
- [ ] Búsqueda de lugar → Recomienda lugar real con detalles
- [ ] Pregunta histórica → Responde con info de `historia_vasca`
- [ ] Solicitud de itinerario → Plan coherente con lugares específicos
- [ ] Conversación casual → Aitor responde con personalidad vasca
- [ ] Mensaje en inglés → Responde en inglés correctamente

**Métricas:**
- [ ] Latencia: < 3 segundos
- [ ] RAG similarity: > 0.7 (cuando esté activado vector search)
- [ ] Expresiones vascas: 1-2 por respuesta
- [ ] Sin errores 500 en n8n
- [ ] Chat history se guarda en Supabase
- [ ] Smoke test RAG ejecutado (opcional): `./scripts/rag-smoke-test.sh https://[tu-endpoint]/rag/query`

---

## 🐛 Troubleshooting

### Error: "Extension vector does not exist"

**Solución:** Ejecuta en Supabase SQL Editor:
```sql
CREATE EXTENSION vector;
```

### Error: "Could not connect to database" en n8n

**Posibles causas:**
1. **Firewall:** Supabase Free tier puede tener restricciones IP. Verifica en Settings → Database → Connection Pooling.
2. **Credenciales incorrectas:** Verifica host, user, password en n8n.
3. **SSL no habilitado:** En credenciales de n8n, activa SSL.

### Error: "Rate limit exceeded" de OpenAI

**Solución:** Reduce la frecuencia de generación de embeddings. El tier gratuito de OpenAI tiene límites bajos.

### Respuestas genéricas de Claude

**Posibles causas:**
1. **System prompt no está inyectado:** Verifica el nodo "Build Claude Prompt" en n8n.
2. **Contexto RAG vacío:** Verifica que el nodo Vector Search devuelva resultados.
3. **Temperature muy baja:** Ajusta temperature a 0.7 en el nodo de Claude.

### Chat history no se guarda

**Solución:** Verifica que el nodo "Save to Chat History" tenga credenciales correctas de Supabase y que la tabla `chat_history` exista.

---

## 📚 Siguientes Pasos

Una vez completado el setup:

1. **Prueba exhaustiva:** Haz al menos 20 conversaciones de prueba variadas
2. **Ajusta prompts:** Refina el system prompt según las respuestas de Claude
3. **Invita beta testers:** 5-10 personas para feedback real
4. **Monitorea analytics:** Revisa los logs en Supabase para identificar patrones
5. **Itera:** Ajusta similarity thresholds, añade más lugares, mejora intent detection

---

## 🆘 Soporte

- **Documentación completa:** `bilbot-proyecto-mvp.md`
- **n8n Docs:** [docs.n8n.io](https://docs.n8n.io/)
- **Supabase Vector Docs:** [supabase.com/docs/guides/ai/vector-embeddings](https://supabase.com/docs/guides/ai/vector-embeddings)
- **Claude API:** [docs.anthropic.com/claude](https://docs.anthropic.com/claude/reference/messages_post)

---

**¡Aupa! Tu BILBOT está listo para ayudar a turistas a descubrir el Bilbao auténtico. 🎉**
