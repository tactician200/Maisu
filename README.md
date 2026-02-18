# 🏔️ BILBOT / MAISU — Tourism AI MVP (Bilbao)

Chatbot turístico con personalidad local vasca usando **n8n + Supabase + Claude + RAG**.

## 🚀 Quick Start

1. Configura Supabase y crea schema:
   - `database/schema.sql`
   - `database/seed-data.sql`
   - `database/expresiones-vascas.sql`
2. Importa workflow principal en n8n:
   - `n8n/bilbot-main-conversation.json`
3. Configura credenciales en n8n (Supabase, Anthropic, OpenAI).
4. Activa workflow y prueba webhook.
5. Test rápido por script:
   ```bash
   ./scripts/test-webhook.sh https://[tu-n8n].app.n8n.cloud/webhook/bilbot
   ```

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
├── n8n/
│   └── bilbot-main-conversation.json
├── database/
│   ├── schema.sql
│   ├── seed-data.sql
│   └── expresiones-vascas.sql
└── scripts/
    └── test-webhook.sh
```

---

## 📚 Documentación

- Setup técnico completo: `SETUP.md`
- Documento de producto / arquitectura MVP: `docs/bilbot-proyecto-mvp.md`
- Prompt del asistente (Aitor): `docs/system-prompt-aitor.md`
- Guía extendida de workflow n8n: `docs/n8n-workflows-guide.md`

---

## ✅ Estado actual del repo

Incluye:
- SQL de esquema y seed data
- Workflow principal de conversación
- Prompt y documentación de producto
- Script de test para webhook

No incluye (todavía):
- `n8n/data-ingestion-workflow.json` (puede añadirse como workflow opcional)

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
