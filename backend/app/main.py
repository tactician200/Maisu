import time

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.providers import OpenAIProvider, ProviderError, build_fallback_answer
from app.retrieval import retrieve_documents
from app.schemas import QueryRequest, QueryResponse

app = FastAPI(title="MAISU/BILBOT RAG API", version="0.1.0")
provider = OpenAIProvider()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


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
            },
            "detail": jsonable_encoder(exc.errors()),
        },
    )


@app.post("/rag/query", response_model=QueryResponse)
async def rag_query(request: QueryRequest) -> QueryResponse:
    started = time.perf_counter()
    docs = retrieve_documents(query=request.query, top_k=3)

    fallback_used = False
    provider_name = "openai"

    try:
        result = await provider.generate(query=request.query, documents=docs, lang=request.lang)
        answer = result.answer
        provider_name = result.provider
    except ProviderError:
        answer = build_fallback_answer(query=request.query, documents=docs, lang=request.lang)
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
