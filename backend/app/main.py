import time

from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.providers import OpenAIProvider, ProviderError, build_fallback_answer
from app.retrieval import retrieve_documents
from app.schemas import QueryRequest, QueryResponse, UserContextResponse, UserContextUpsertRequest
from app.user_context import UserContextStore, normalize_preferences

app = FastAPI(title="MAISU/BILBOT RAG API", version="0.1.0")
provider = OpenAIProvider()
user_context_store = UserContextStore()


def _normalize_lang_preference(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip().lower()
    if not cleaned:
        return None
    if cleaned in {"es", "en", "eu"}:
        return cleaned
    return None


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/user-context/{session_id}", response_model=UserContextResponse)
async def get_user_context(session_id: str) -> UserContextResponse:
    context = user_context_store.get_context(session_id)
    if not context:
        raise HTTPException(status_code=404, detail="user context not found")
    return UserContextResponse(**context)


@app.put("/user-context/{session_id}", response_model=UserContextResponse)
async def put_user_context(session_id: str, payload: UserContextUpsertRequest) -> UserContextResponse:
    data = payload.model_dump(exclude_none=True)
    stored = user_context_store.upsert_context(session_id=session_id, data=data)
    return UserContextResponse(**stored)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    if request.url.path != "/rag/query":
        return JSONResponse(status_code=422, content={"detail": jsonable_encoder(exc.errors())})

    return JSONResponse(
        status_code=422,
        content={
            "error": "invalid_request",
            "message": "Invalid payload for /rag/query. Provide at least a non-empty 'query' field.",
            "accepted_fields": {
                "query": ["query", "chatInput"],
                "session_id": ["session_id", "sessionId"],
                "lang": ["lang"],
                "tone": ["tone"],
                "style": ["style"],
                "interests": ["interests"],
            },
            "detail": jsonable_encoder(exc.errors()),
        },
    )


@app.post("/rag/query", response_model=QueryResponse)
async def rag_query(request: QueryRequest) -> QueryResponse:
    started = time.perf_counter()
    docs = retrieve_documents(query=request.query, top_k=3)

    context = user_context_store.get_context(request.session_id) if request.session_id else None
    context_preferences = normalize_preferences(context.get("preferences") if context else None)

    effective_lang = _normalize_lang_preference(request.lang)
    if not effective_lang and context:
        candidate_lang = context.get("language")
        effective_lang = _normalize_lang_preference(candidate_lang if isinstance(candidate_lang, str) else None)

    default_preferences = {"tone": "concise", "style": "paragraph", "interests": []}
    effective_tone = request.tone or context_preferences.get("tone") or default_preferences["tone"]
    effective_style = request.style or context_preferences.get("style") or default_preferences["style"]
    effective_interests = request.interests or context_preferences.get("interests") or default_preferences["interests"]

    fallback_used = False
    provider_name = "openai"

    try:
        result = await provider.generate(
            query=request.query,
            documents=docs,
            lang=effective_lang,
            tone=effective_tone,
            style=effective_style,
            interests=effective_interests,
        )
        answer = result.answer
        provider_name = result.provider
    except ProviderError:
        answer = build_fallback_answer(
            query=request.query,
            documents=docs,
            lang=effective_lang,
            tone=effective_tone,
            style=effective_style,
            interests=effective_interests,
        )
        fallback_used = True
        provider_name = "fallback"

    latency_ms = int((time.perf_counter() - started) * 1000)
    return QueryResponse(
        answer=answer,
        citations=docs,
        latency_ms=latency_ms,
        fallback_used=fallback_used,
        provider=provider_name,
    )
