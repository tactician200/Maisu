from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator


class QueryRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    query: str = Field(min_length=1, validation_alias=AliasChoices("query", "chatInput"))
    session_id: str | None = Field(default=None, validation_alias=AliasChoices("session_id", "sessionId"))
    lang: str | None = None

    @field_validator("query")
    @classmethod
    def normalize_query(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("query must not be blank")
        return cleaned

    @field_validator("lang")
    @classmethod
    def normalize_lang(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip().lower()
        return cleaned or None


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
