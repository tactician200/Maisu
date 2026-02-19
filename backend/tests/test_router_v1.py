from fastapi.testclient import TestClient

from app.main import app, provider
from app.providers import ProviderResult
from app.router import classify_query_route

client = TestClient(app)


def _stub_provider(monkeypatch, answer: str = "ok", provider_name: str = "openai") -> None:
    async def fake_generate(
        query: str,
        documents: list[dict],
        lang: str | None = None,
        tone: str | None = None,
        style: str | None = None,
        interests: list[str] | None = None,
    ) -> ProviderResult:
        return ProviderResult(answer=answer, provider=provider_name)

    monkeypatch.setattr(provider, "generate", fake_generate)


def test_router_v1_structured_query_routes_sql_first(monkeypatch) -> None:
    hits = {"sql": 0, "rag": 0}

    monkeypatch.setattr("app.main.classify_query_route", lambda query: "structured")
    monkeypatch.setattr("app.main.retrieve_sql_facts", lambda query, top_k=3: hits.__setitem__("sql", hits["sql"] + 1) or [])
    monkeypatch.setattr("app.main.retrieve_documents", lambda query, top_k=3: hits.__setitem__("rag", hits["rag"] + 1) or [])
    _stub_provider(monkeypatch)

    response = client.post("/rag/query", json={"query": "Where is the Guggenheim and what are opening hours?"})

    assert response.status_code == 200
    assert hits == {"sql": 1, "rag": 0}


def test_router_v1_narrative_query_routes_rag(monkeypatch) -> None:
    hits = {"sql": 0, "rag": 0}

    monkeypatch.setattr("app.main.classify_query_route", lambda query: "narrative")
    monkeypatch.setattr("app.main.retrieve_sql_facts", lambda query, top_k=3: hits.__setitem__("sql", hits["sql"] + 1) or [])
    monkeypatch.setattr("app.main.retrieve_documents", lambda query, top_k=3: hits.__setitem__("rag", hits["rag"] + 1) or [])
    _stub_provider(monkeypatch)

    response = client.post("/rag/query", json={"query": "Explain the history of Bilbao"})

    assert response.status_code == 200
    assert hits == {"sql": 0, "rag": 1}


def test_router_v1_mixed_query_routes_hybrid(monkeypatch) -> None:
    hits = {"sql": 0, "rag": 0}

    monkeypatch.setattr("app.main.classify_query_route", lambda query: "hybrid")
    monkeypatch.setattr("app.main.retrieve_sql_facts", lambda query, top_k=3: hits.__setitem__("sql", hits["sql"] + 1) or [{"id": "s1", "title": "T", "snippet": "S", "source": "sql://1"}])
    monkeypatch.setattr("app.main.retrieve_documents", lambda query, top_k=3: hits.__setitem__("rag", hits["rag"] + 1) or [{"id": "r1", "title": "T2", "snippet": "S2", "source": "rag://1"}])
    _stub_provider(monkeypatch)

    response = client.post("/rag/query", json={"query": "Where is this historical place and explain its origins"})

    assert response.status_code == 200
    assert hits == {"sql": 1, "rag": 1}


def test_router_v1_output_invariants_preserved(monkeypatch) -> None:
    docs = [{"id": "p1", "title": "A", "snippet": "B", "source": "mock://p1"}]

    monkeypatch.setattr("app.main.classify_query_route", lambda query: "narrative")
    monkeypatch.setattr("app.main.retrieve_documents", lambda query, top_k=3: docs)
    _stub_provider(monkeypatch, answer="Invariant answer", provider_name="openai")

    response = client.post("/rag/query", json={"query": "A narrative question"})

    assert response.status_code == 200
    body = response.json()
    assert {"answer", "citations", "provider", "fallback_used"}.issubset(body.keys())
    assert body["answer"] == "Invariant answer"
    assert body["citations"] == docs
    assert body["provider"] == "openai"
    assert body["fallback_used"] is False


def test_router_v1_low_confidence_keeps_backward_compatible_rag(monkeypatch) -> None:
    hits = {"sql": 0, "rag": 0}

    monkeypatch.setattr("app.main.classify_query_route", lambda query: "narrative")
    monkeypatch.setattr("app.main.retrieve_sql_facts", lambda query, top_k=3: hits.__setitem__("sql", hits["sql"] + 1) or [])
    monkeypatch.setattr("app.main.retrieve_documents", lambda query, top_k=3: hits.__setitem__("rag", hits["rag"] + 1) or [])
    _stub_provider(monkeypatch)

    response = client.post("/rag/query", json={"query": "Bilbao"})

    assert response.status_code == 200
    assert hits == {"sql": 0, "rag": 1}


def test_router_v1_classifier_detects_structured_query() -> None:
    assert classify_query_route("Where is the museum and what are opening hours?") == "structured"


def test_router_v1_classifier_detects_narrative_query() -> None:
    assert classify_query_route("Explain the history and culture of Bilbao") == "narrative"


def test_router_v1_classifier_detects_hybrid_query() -> None:
    assert classify_query_route("Where is this place and explain its history") == "hybrid"


def test_router_v1_classifier_low_confidence_defaults_to_narrative() -> None:
    assert classify_query_route("Bilbao") == "narrative"
