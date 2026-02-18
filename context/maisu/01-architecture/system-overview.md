# System Overview — Maisu

## Core Stack
- n8n (workflow orchestration)
- Supabase Postgres + pgvector (storage + retrieval)
- Claude (response generation)
- OpenAI embeddings (vectorization)

## High-Level Flow
1. Webhook receives message
2. Language + intent detection
3. Hybrid retrieval (vector + SQL)
4. Prompt assembly with retrieved context + memory
5. LLM response generation
6. Persist chat history + analytics
