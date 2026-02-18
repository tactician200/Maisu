# MVP Scope and Acceptance — MAISU v1

## In Scope (MVP v1)
1. Tourism recommendations for Bilbao based on approved sources.
2. Basic history/culture Q&A grounded in retrievable context.
3. Simple itinerary suggestions (1-day / half-day level).
4. Retrieval-backed responses with citations when evidence exists.
5. Safe fallback when confidence is low or evidence is missing.
6. Basic multilingual handling (input language detection + response in user language when possible).

## Out of Scope (MVP)
1. Multi-city recommendation support beyond Bilbao.
2. Personalized long-term user profiles and preference memory.
3. Full admin panel for content/operations.
4. Real-time booking/transaction integrations.
5. Guaranteed expert-level legal/safety advice.

## Acceptance Criteria (Given / When / Then)
1. **Given** a Bilbao attractions question with indexed evidence, **when** user queries, **then** response includes at least one relevant citation.
2. **Given** a cultural/history question covered by sources, **when** user queries, **then** answer is grounded and avoids unsupported claims.
3. **Given** retrieval returns no relevant chunks, **when** user queries, **then** fallback response is returned with a clarifying question.
4. **Given** retrieval score is below threshold, **when** generation is requested, **then** system avoids hallucination and triggers fallback mode.
5. **Given** user asks for a basic itinerary, **when** enough source context exists, **then** response provides ordered suggestions and cites source material.
6. **Given** malformed/empty input, **when** request reaches API, **then** API returns standardized validation error.
7. **Given** duplicate chunks from same source dominate retrieval, **when** assembling context, **then** dedupe/limits keep context diverse.
8. **Given** conflicting source evidence, **when** confidence is insufficient to resolve, **then** response states uncertainty and asks for refinement.
9. **Given** successful response generation, **when** request completes, **then** system logs query, latency, and fallback/citation metadata.
10. **Given** out-of-scope city request, **when** user asks, **then** response clearly states scope limitation and offers Bilbao-focused assistance.

## Out-of-scope request examples + expected fallback behavior
1. **Request:** “Plan my trip to Madrid and Barcelona.”  
   **Fallback:** State current scope is Bilbao MVP; offer Bilbao alternatives or request scope change.
2. **Request:** “Book tickets and complete payment for me.”  
   **Fallback:** Explain booking/transactions are not supported; suggest official channels.
3. **Request:** “Use my previous visits and preferences from last year.”  
   **Fallback:** Clarify persistent personalization is not enabled in MVP; ask for current preferences in-session.
4. **Request:** “Give legal guarantees about travel insurance compliance.”  
   **Fallback:** Provide non-legal general guidance and recommend consulting official/legal sources.
5. **Request:** “Compare Bilbao vs Lisbon vs Porto and choose best city.”  
   **Fallback:** State multi-city comparison is outside MVP; offer Bilbao-focused recommendation.
