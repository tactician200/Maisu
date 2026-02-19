from fastapi.testclient import TestClient

from app.main import app, provider
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
