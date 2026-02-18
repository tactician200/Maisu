from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    query: str = Field(min_length=1)
    session_id: str | None = None
    lang: str | None = None


class Citation(BaseModel):
    id: str
    title: str
    snippet: str
    source: str


class QueryResponse(BaseModel):
    answer: str
    citations: list[Citation]
    latency_ms: int
    fallback_used: bool
    provider: str
