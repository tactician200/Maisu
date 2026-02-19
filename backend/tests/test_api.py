from fastapi.testclient import TestClient

from app.main import app, provider, user_context_store
from app.providers import ProviderError, ProviderResult

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_rag_query_happy_path(monkeypatch) -> None:
    async def fake_generate(query: str, documents: list[dict], lang: str | None = None) -> ProviderResult:
        return ProviderResult(answer="Respuesta de prueba", provider="openai")

    monkeypatch.setattr(provider, "generate", fake_generate)

    payload = {"query": "¿Qué ver en Bilbao?", "session_id": "s1", "lang": "es"}
    response = client.post("/rag/query", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert set(data.keys()) == {"answer", "citations", "latency_ms", "fallback_used", "provider"}
    assert data["answer"] == "Respuesta de prueba"
    assert data["fallback_used"] is False
    assert data["provider"] == "openai"
    assert isinstance(data["citations"], list)


def test_rag_query_accepts_chatinput_alias(monkeypatch) -> None:
    observed: dict[str, str | None] = {}

    async def fake_generate(query: str, documents: list[dict], lang: str | None = None) -> ProviderResult:
        observed["query"] = query
        observed["lang"] = lang
        return ProviderResult(answer="ok", provider="openai")

    monkeypatch.setattr(provider, "generate", fake_generate)

    response = client.post(
        "/rag/query",
        json={"chatInput": "  Hola Bilbao  ", "sessionId": "abc", "lang": " ES "},
    )

    assert response.status_code == 200
    assert observed["query"] == "Hola Bilbao"
    assert observed["lang"] == "es"


def test_rag_query_rejects_blank_query() -> None:
    response = client.post("/rag/query", json={"query": "   "})

    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "invalid_request"
    assert "accepted_fields" in data
    assert data["accepted_fields"]["query"] == ["query", "chatInput"]


def test_rag_query_fallback_path(monkeypatch) -> None:
    async def failing_generate(query: str, documents: list[dict], lang: str | None = None):
        raise ProviderError("rate limited")

    docs = [
        {
            "id": "d1",
            "title": "Casco Viejo",
            "snippet": "Calles históricas y pintxos",
            "source": "supabase://places/d1",
        }
    ]

    monkeypatch.setattr(provider, "generate", failing_generate)
    monkeypatch.setattr("app.main.retrieve_documents", lambda query, top_k=3: docs)

    response = client.post("/rag/query", json={"query": "Plan para 1 día", "lang": "es"})

    assert response.status_code == 200
    data = response.json()
    assert data["fallback_used"] is True
    assert data["provider"] == "fallback"
    assert "1) Resumen" in data["answer"]
    assert data["citations"] == docs


def test_user_context_put_and_get_roundtrip() -> None:
    session_id = "ctx-s1"
    user_context_store._memory.pop(session_id, None)

    put_response = client.put(
        f"/user-context/{session_id}",
        json={
            "name": "Amaia",
            "language": "ES",
            "preferences": {"tone": "concise"},
            "user_id": "u-123",
        },
    )

    assert put_response.status_code == 200
    put_data = put_response.json()
    assert put_data == {
        "session_id": session_id,
        "name": "Amaia",
        "language": "es",
        "preferences": {"tone": "concise"},
        "user_id": "u-123",
    }

    get_response = client.get(f"/user-context/{session_id}")
    assert get_response.status_code == 200
    assert get_response.json() == put_data


def test_user_context_get_not_found() -> None:
    missing_session = "ctx-missing"
    user_context_store._memory.pop(missing_session, None)

    response = client.get(f"/user-context/{missing_session}")
    assert response.status_code == 404


def test_rag_query_uses_context_language_when_lang_missing(monkeypatch) -> None:
    session_id = "ctx-lang"
    user_context_store._memory[session_id] = {
        "session_id": session_id,
        "language": "eu",
    }

    observed: dict[str, str | None] = {}

    async def fake_generate(query: str, documents: list[dict], lang: str | None = None) -> ProviderResult:
        observed["lang"] = lang
        return ProviderResult(answer="ok", provider="openai")

    monkeypatch.setattr(provider, "generate", fake_generate)

    response = client.post("/rag/query", json={"query": "Kaixo", "session_id": session_id})

    assert response.status_code == 200
    assert observed["lang"] == "eu"


def test_rag_query_citations_invariant_across_provider_paths(monkeypatch) -> None:
    docs = [
        {
            "id": "p1",
            "title": "Guggenheim",
            "snippet": "Museo junto a la ría",
            "source": "supabase://places/p1",
        },
        {
            "id": "h1",
            "title": "Historia de Bilbao",
            "snippet": "Origen medieval y expansión portuaria",
            "source": "supabase://history/h1",
        },
    ]

    monkeypatch.setattr("app.main.retrieve_documents", lambda query, top_k=3: docs)

    async def ok_generate(query: str, documents: list[dict], lang: str | None = None) -> ProviderResult:
        return ProviderResult(answer="ok", provider="openai")

    monkeypatch.setattr(provider, "generate", ok_generate)
    ok_response = client.post("/rag/query", json={"query": "historia y arte"})

    assert ok_response.status_code == 200
    ok_data = ok_response.json()
    assert ok_data["fallback_used"] is False
    assert ok_data["provider"] == "openai"
    assert ok_data["citations"] == docs
    assert all(c["source"] for c in ok_data["citations"])

    async def fail_generate(query: str, documents: list[dict], lang: str | None = None):
        raise ProviderError("down")

    monkeypatch.setattr(provider, "generate", fail_generate)
    fb_response = client.post("/rag/query", json={"query": "historia y arte"})

    assert fb_response.status_code == 200
    fb_data = fb_response.json()
    assert fb_data["fallback_used"] is True
    assert fb_data["provider"] == "fallback"
    assert fb_data["citations"] == docs
    assert all(c["source"] for c in fb_data["citations"])


def test_user_context_put_then_get_roundtrip(monkeypatch) -> None:
    store: dict[str, dict] = {}

    def fake_upsert(session_id: str, data: dict) -> dict:
        saved = {"session_id": session_id, **data}
        store[session_id] = saved
        return saved

    def fake_get(session_id: str) -> dict | None:
        return store.get(session_id)

    monkeypatch.setattr(user_context_store, "upsert_context", fake_upsert)
    monkeypatch.setattr(user_context_store, "get_context", fake_get)

    payload = {
        "name": "Ane",
        "language": "es",
        "preferences": {"tone": "friendly", "likes": ["pintxos"]},
    }
    put_response = client.put("/user-context/sess-roundtrip", json=payload)
    assert put_response.status_code == 200
    assert put_response.json() == {"session_id": "sess-roundtrip", **payload, "user_id": None}

    get_response = client.get("/user-context/sess-roundtrip")
    assert get_response.status_code == 200
    assert get_response.json() == {"session_id": "sess-roundtrip", **payload, "user_id": None}


def test_user_context_get_unknown_session_returns_not_found_shape(monkeypatch) -> None:
    monkeypatch.setattr(user_context_store, "get_context", lambda session_id: None)

    response = client.get("/user-context/unknown-session")

    assert response.status_code == 404
    assert response.json() == {"detail": "user context not found"}


def test_rag_query_uses_stored_language_when_lang_missing(monkeypatch) -> None:
    observed: dict[str, str | None] = {}

    monkeypatch.setattr(user_context_store, "get_context", lambda session_id: {"session_id": session_id, "language": "eu"})

    async def fake_generate(query: str, documents: list[dict], lang: str | None = None) -> ProviderResult:
        observed["lang"] = lang
        return ProviderResult(answer="Kaixo", provider="openai")

    monkeypatch.setattr(provider, "generate", fake_generate)

    response = client.post("/rag/query", json={"query": "Kaixo", "session_id": "sess-lang"})

    assert response.status_code == 200
    assert observed["lang"] == "eu"


def test_rag_query_explicit_lang_overrides_stored_language(monkeypatch) -> None:
    observed: dict[str, str | None] = {}

    monkeypatch.setattr(user_context_store, "get_context", lambda session_id: {"session_id": session_id, "language": "eu"})

    async def fake_generate(query: str, documents: list[dict], lang: str | None = None) -> ProviderResult:
        observed["lang"] = lang
        return ProviderResult(answer="Hola", provider="openai")

    monkeypatch.setattr(provider, "generate", fake_generate)

    response = client.post("/rag/query", json={"query": "Kaixo", "session_id": "sess-lang", "lang": "es"})

    assert response.status_code == 200
    assert observed["lang"] == "es"
