from typing import Any

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator

_ALLOWED_TONES = {"concise", "detailed"}
_ALLOWED_STYLES = {"bullets", "paragraph"}


class QueryRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    query: str = Field(min_length=1, validation_alias=AliasChoices("query", "chatInput"))
    session_id: str | None = Field(default=None, validation_alias=AliasChoices("session_id", "sessionId"))
    lang: str | None = None
    tone: str | None = None
    style: str | None = None
    interests: list[str] | None = None

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

    @field_validator("tone")
    @classmethod
    def normalize_tone(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip().lower()
        return cleaned if cleaned in _ALLOWED_TONES else None

    @field_validator("style")
    @classmethod
    def normalize_style(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip().lower()
        return cleaned if cleaned in _ALLOWED_STYLES else None

    @field_validator("interests", mode="before")
    @classmethod
    def normalize_interests(cls, value: Any) -> list[str] | None:
        if value is None:
            return None
        if not isinstance(value, list):
            return None
        cleaned_items: list[str] = []
        for item in value:
            if isinstance(item, str):
                cleaned = item.strip()
                if cleaned:
                    cleaned_items.append(cleaned)
        return cleaned_items or None


class UserContextUpsertRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str | None = None
    language: str | None = None
    preferences: dict[str, Any] | None = None
    user_id: str | None = None

    @field_validator("name", "language", "user_id")
    @classmethod
    def normalize_text_fields(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None

    @field_validator("language")
    @classmethod
    def normalize_language(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.lower()


class UserContextResponse(BaseModel):
    session_id: str
    name: str | None = None
    language: str | None = None
    preferences: dict[str, Any] | None = None
    user_id: str | None = None


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
