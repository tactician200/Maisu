# 🔧 BILBOT - Documentación de Workflows n8n

## Descripción

Este directorio contiene los workflows de n8n para BILBOT. Los workflows orquestan el flujo conversacional, búsqueda RAG, y generación de respuestas con Claude.

---

## 📁 Archivos

### `bilbot-main-conversation.json` ⭐ CRÍTICO
**Descripción:** Workflow principal de conversación

**Funcionalidad:**
- Recibe mensajes via Chat Trigger (webhook público)
- Detecta idioma (ES/EN/EU)
- Clasifica intención (search_place, history_query, recommendation, general_chat)
- Ejecuta búsqueda híbrida RAG (vector + SQL)
- Genera respuesta con Claude Sonnet 4.5
- Guarda en chat_history y analytics

**URL:** `https://[tu-n8n].app.n8n.cloud/webhook/bilbot`

---

### `data-ingestion-workflow.json` 🔄 OPCIONAL
**Descripción:** Pipeline de datos (Google Sheets → Supabase)

**Funcionalidad:**
- Lee lugares desde Google Sheets
- Valida y formatea datos
- Genera embeddings con OpenAI
- Inserta en places + places_embeddings
- Envía notificación de éxito/error

**Trigger:** Manual o programado (cron)

---

## 🏗️ Arquitectura del Workflow Principal

```
┌─────────────────────────┐
│   Chat Trigger          │  Webhook público
│   (Mensaje del usuario) │
└───────────┬─────────────┘
            ↓
┌─────────────────────────┐
│   Detect Language       │  ES / EN / EU
└───────────┬─────────────┘
            ↓
┌─────────────────────────┐
│   Extract Intent        │  search_place / history / recommendation / general
└───────────┬─────────────┘
            ↓
┌─────────────────────────┐
│   Switch by Intent      │  Router
└─┬─────┬─────┬─────┬─────┘
  │     │     │     │
  v     v     v     v
[search][hist][rec][gen]
  │     │     │     │
  └─────┴─────┴─────┘
            ↓
┌─────────────────────────┐
│   Aggregate Results     │  Combina datos RAG
└───────────┬─────────────┘
            ↓
┌─────────────────────────┐
│   Build Claude Prompt   │  System prompt + Context + Memory
└───────────┬─────────────┘
            ↓
┌─────────────────────────┐
│   Anthropic Claude      │  Genera respuesta
│   (Sonnet 4.5)          │
└───────────┬─────────────┘
            ↓
┌─────────────────────────┐
│   Save Chat History     │  Supabase insert
└───────────┬─────────────┘
            ↓
┌─────────────────────────┐
│   Log Analytics         │  Métricas
└───────────┬─────────────┘
            ↓
┌─────────────────────────┐
│   Return to Chat        │  Respuesta al usuario
└─────────────────────────┘
```

---

## 🔌 Nodos Críticos

### 1. Chat Trigger
**Tipo:** Webhook
**Configuración:**
- **Método:** POST
- **Path:** `/bilbot`
- **Mensaje inicial:** "Kaixo! Soy Aitor, tu guía local de Bilbao. ¿En qué puedo ayudarte hoy?"
- **Session ID:** Generado automáticamente o pasado en request

**Input esperado:**
```json
{
  "chatInput": "Recomiéndame un bar de pintxos",
  "sessionId": "optional-session-id"
}
```

---

### 2. Detect Language (Code Node)
**Lenguaje:** JavaScript
**Función:** Detectar idioma del mensaje

**Código ejemplo:**
```javascript
const userMessage = $input.item.json.chatInput.toLowerCase();

let language = 'es'; // default

if (/hello|hi|thank|please|museum|recommend/i.test(userMessage)) {
  language = 'en';
} else if (/kaixo|eskerrik|agur|non dago/i.test(userMessage)) {
  language = 'eu';
}

return {
  json: {
    language,
    original_message: $input.item.json.chatInput,
    session_id: $input.item.json.sessionId || `session-${Date.now()}`
  }
};
```

---

### 3. Extract Intent (Code Node)
**Lenguaje:** JavaScript
**Función:** Clasificar intención del usuario

**Intents:**
- `search_place`: Buscar restaurante, bar, museo
- `history_query`: Historia, cultura
- `recommendation`: Qué hacer, itinerario
- `general_chat`: Conversación casual

**Código ejemplo:**
```javascript
const userMessage = $input.item.json.original_message.toLowerCase();

const patterns = {
  search_place: [
    /dónde (puedo|comer|tomar|ir)/i,
    /recomienda(me)? (un|una) (restaurante|bar|café)/i,
    /busco (restaurante|bar|sitio|lugar)/i,
    /where (can i|to) (eat|drink|go)/i
  ],
  history_query: [
    /historia (de|del)/i,
    /cuéntame (sobre|acerca)/i,
    /tell me about/i,
    /history of/i
  ],
  recommendation: [
    /qué (hacer|ver|visitar)/i,
    /itinerario/i,
    /tengo (\\d+) (horas|días)/i,
    /what (to do|should i)/i
  ]
};

let intent = 'general_chat';
for (const [key, regexList] of Object.entries(patterns)) {
  if (regexList.some(regex => regex.test(userMessage))) {
    intent = key;
    break;
  }
}

// Extraer parámetros
const params = {
  tipo: null,
  barrio: null,
  precio_max: null
};

if (/restaurante/i.test(userMessage)) params.tipo = 'restaurante';
if (/bar|pintxos/i.test(userMessage)) params.tipo = 'bar';
if (/Casco Viejo/i.test(userMessage)) params.barrio = 'Casco Viejo';

return {
  json: {
    intent,
    params,
    ...$input.item.json
  }
};
```

---

### 4. Switch by Intent (Switch Node)
**Configuración:**
- **Output 0:** intent === 'search_place'
- **Output 1:** intent === 'history_query'
- **Output 2:** intent === 'recommendation'
- **Output 3:** Default (general_chat)

---

### 5. Supabase Vector Store (RAG Node)
**Tipo:** Postgres / Supabase
**Operación:** Query

**Query para search_place:**
```sql
SELECT * FROM search_places_hybrid(
    $1::vector,                     -- embedding del query
    $2,                              -- filter_barrio
    $3,                              -- filter_tipo
    4.0,                             -- min_rating
    999.99,                          -- max_precio
    0.7,                             -- similarity_threshold
    5                                -- result_limit
);
```

**Bindings:**
- `$1`: `{{ $node["Generate Embedding"].json.embedding }}`
- `$2`: `{{ $node["Extract Intent"].json.params.barrio }}`
- `$3`: `{{ $node["Extract Intent"].json.params.tipo }}`

---

### 6. Build Claude Prompt (Code Node)
**Función:** Construir prompt completo para Claude

**Estructura:**
```javascript
// Leer system prompt desde prompts/system-prompt-aitor.md
const systemPrompt = `[CONTENIDO DE system-prompt-aitor.md]`;

// Inyectar contexto RAG
const ragContext = $node["Vector Search"].json.results
  .map(r => `[${r.nombre}] ${r.descripcion}`)
  .join('\n\n');

// Obtener memoria conversacional
const chatMemory = $node["Get Memory"].json.messages
  .map(m => `${m.message_type}: ${m.content}`)
  .join('\n');

return {
  json: {
    systemPrompt: `${systemPrompt}\n\n=== CONTEXTO RAG ===\n${ragContext}\n\n=== CONVERSACIÓN PREVIA ===\n${chatMemory}\n\n=== FIN CONTEXTO ===`,
    messages: [
      {
        role: "user",
        content: $node["Extract Intent"].json.original_message
      }
    ]
  }
};
```

---

### 7. Anthropic Claude (AI Node)
**Configuración:**
- **Model:** claude-sonnet-4-5-20250929
- **Max Tokens:** 500
- **Temperature:** 0.7
- **System:** `{{ $node["Build Prompt"].json.systemPrompt }}`
- **Messages:** `{{ $node["Build Prompt"].json.messages }}`

---

### 8. Save Chat History (Postgres Node)
**Operación:** Insert

**Tabla:** `chat_history`

**Campos:**
```json
{
  "session_id": "{{ $node['Detect Language'].json.session_id }}",
  "message_type": "human",
  "content": "{{ $node['Extract Intent'].json.original_message }}",
  "metadata": {
    "language": "{{ $node['Detect Language'].json.language }}",
    "intent": "{{ $node['Extract Intent'].json.intent }}"
  }
}
```

Segundo insert para mensaje de AI:
```json
{
  "session_id": "{{ $node['Detect Language'].json.session_id }}",
  "message_type": "ai",
  "content": "{{ $node['Claude'].json.response }}",
  "tokens_used": "{{ $node['Claude'].json.usage.output_tokens }}",
  "latency_ms": "{{ $node['Claude'].json.latency }}"
}
```

---

### 9. Log Analytics (Postgres Node)
**Operación:** Insert

**Tabla:** `analytics`

**Campos:**
```json
{
  "session_id": "{{ $node['Detect Language'].json.session_id }}",
  "event_type": "query",
  "event_data": {
    "intent": "{{ $node['Extract Intent'].json.intent }}",
    "language": "{{ $node['Detect Language'].json.language }}"
  },
  "rag_retrieval_count": "{{ $node['Vector Search'].json.results.length }}",
  "rag_relevance_score": "{{ $node['Vector Search'].json.results[0].similarity }}",
  "response_time_ms": "{{ $node['Claude'].json.latency }}"
}
```

---

### 10. Return to Chat
**Tipo:** Respond to Webhook
**Configuración:**
```json
{
  "response": "{{ $node['Claude'].json.response }}",
  "session_id": "{{ $node['Detect Language'].json.session_id }}"
}
```

---

## 🔐 Credenciales Necesarias

### Supabase (PostgreSQL)
- **Host:** `db.[tu-proyecto].supabase.co`
- **Port:** `5432`
- **Database:** `postgres`
- **User:** `postgres`
- **Password:** [Tu contraseña]
- **SSL:** Activado

**Alternativa:** Supabase API
- **Project URL:** `https://[tu-proyecto].supabase.co`
- **Service Role Key:** [Tu key]

---

### Anthropic (Claude)
- **API Key:** `sk-ant-api03-[tu-key]`
- **Model:** `claude-sonnet-4-5-20250929`

---

### OpenAI (Embeddings)
- **API Key:** `sk-[tu-key]`
- **Model:** `text-embedding-3-small`

---

## 🧪 Testing del Workflow

### Test Manual en n8n
1. Ve a tu workflow en n8n
2. Haz clic en "Execute Workflow"
3. En el nodo Chat Trigger, simula input:
   ```json
   {
     "chatInput": "Recomiéndame un bar de pintxos",
     "sessionId": "test-123"
   }
   ```
4. Verifica que cada nodo se ejecute correctamente (verde)

### Test con Curl
```bash
curl -X POST "https://[tu-n8n].app.n8n.cloud/webhook/bilbot" \
  -H "Content-Type: application/json" \
  -d '{
    "chatInput": "Hola, recomiéndame un restaurante",
    "sessionId": "test-session"
  }'
```

### Test Automatizado
```bash
./tests/test-webhook.sh https://[tu-n8n].app.n8n.cloud/webhook/bilbot
```

---

## 📊 Monitoreo

### Ver Executions en n8n
1. Ve a **Executions** en el panel lateral
2. Filtra por: Success, Error, Waiting
3. Haz clic en una ejecución para ver detalles de cada nodo

### Métricas Clave
- **Success rate:** % de ejecuciones exitosas
- **Avg latency:** Tiempo promedio de ejecución
- **Error rate:** % de ejecuciones fallidas

### Logs de Supabase
```sql
-- Ver últimas conversaciones
SELECT * FROM chat_history
ORDER BY created_at DESC
LIMIT 20;

-- Ver analytics de latencia
SELECT
    AVG(response_time_ms) as avg_latency,
    MAX(response_time_ms) as max_latency,
    COUNT(*) as total_queries
FROM analytics
WHERE created_at >= NOW() - INTERVAL '24 hours';
```

---

## 🐛 Troubleshooting

### Error: "Workflow not found"
**Causa:** Workflow no está activado
**Solución:** Activa el workflow (toggle en esquina superior derecha)

### Error: "Invalid credentials"
**Causa:** Credenciales de Supabase/Anthropic/OpenAI incorrectas
**Solución:** Re-configura credenciales en n8n → Credentials

### Error: "Timeout"
**Causa:** Latencia alta (Claude o Supabase)
**Solución:** Aumenta timeout en configuración del nodo (default: 30s)

### Claude responde en inglés cuando debería ser español
**Causa:** Detección de idioma incorrecta o system prompt en inglés
**Solución:** Verifica nodo "Detect Language" y asegura que system prompt esté en español

### Vector search no devuelve resultados
**Causa:** No hay embeddings generados en `places_embeddings`
**Solución:** Ejecuta el workflow de data ingestion para generar embeddings

---

## 🚀 Despliegue

### Producción
1. Duplica el workflow (backup)
2. Cambia credenciales a producción (si aplica)
3. Activa el workflow
4. Monitorea executions durante 24h

### Rollback
1. Desactiva workflow actual
2. Activa workflow backup
3. Investiga el issue

---

## 📚 Referencias

- **n8n Docs:** [docs.n8n.io](https://docs.n8n.io/)
- **Claude API:** [docs.anthropic.com/claude](https://docs.anthropic.com/claude)
- **OpenAI Embeddings:** [platform.openai.com/docs/guides/embeddings](https://platform.openai.com/docs/guides/embeddings)

---

**¡Aupa! Tu workflow de BILBOT está listo. 🔧**
