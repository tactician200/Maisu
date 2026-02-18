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
