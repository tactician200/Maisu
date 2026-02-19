import httpx

from app import retrieval


def test_retrieve_documents_without_env_returns_mock(monkeypatch) -> None:
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)

    docs = retrieval.retrieve_documents(query="bilbao", top_k=2)

    assert len(docs) == 2
    assert docs[0]["id"].startswith("mock-")


def test_retrieve_documents_supabase_error_falls_back_to_mock(monkeypatch) -> None:
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "test-key")

    def fake_get(*args, **kwargs):
        raise httpx.ConnectError("boom")

    monkeypatch.setattr(httpx.Client, "get", fake_get)

    docs = retrieval.retrieve_documents(query="bilbao", top_k=3)

    assert len(docs) == 3
    assert docs[0]["id"].startswith("mock-")


def test_retrieve_documents_supabase_empty_falls_back_to_mock(monkeypatch) -> None:
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "test-key")

    class FakeResponse:
        status_code = 200

        @staticmethod
        def raise_for_status() -> None:
            return None

        @staticmethod
        def json():
            return []

    monkeypatch.setattr(httpx.Client, "get", lambda *args, **kwargs: FakeResponse())

    docs = retrieval.retrieve_documents(query="bilbao", top_k=1)

    assert len(docs) == 1
    assert docs[0]["id"] == "mock-1"


def test_retrieve_documents_supabase_success(monkeypatch) -> None:
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "test-key")

    class FakeResponse:
        status_code = 200

        @staticmethod
        def raise_for_status() -> None:
            return None

        @staticmethod
        def json():
            return [
                {
                    "id": "p1",
                    "nombre": "Azkuna Zentroa",
                    "descripcion": "Centro cultural en Bilbao",
                    "slug": "azkuna-zentroa",
                }
            ]

    monkeypatch.setattr(httpx.Client, "get", lambda *args, **kwargs: FakeResponse())

    docs = retrieval.retrieve_documents(query="cultura", top_k=3)

    assert len(docs) == 1
    assert docs[0] == {
        "id": "p1",
        "title": "Azkuna Zentroa",
        "snippet": "Centro cultural en Bilbao",
        "source": "azkuna-zentroa",
    }


def test_supabase_retrieval_places_defaults_remain_intact(monkeypatch) -> None:
    captured: dict[str, object] = {}

    class FakeResponse:
        @staticmethod
        def raise_for_status() -> None:
            return None

        @staticmethod
        def json():
            return [
                {
                    "id": "p1",
                    "nombre": "Casco Viejo",
                    "descripcion": "Casco histórico",
                    "slug": "casco-viejo",
                }
            ]

    def fake_get(self, url, headers=None, params=None):
        captured["url"] = url
        captured["headers"] = headers
        captured["params"] = params
        return FakeResponse()

    monkeypatch.setattr(httpx.Client, "get", fake_get)

    docs = retrieval._supabase_retrieval(
        query="casco",
        top_k=2,
        supabase_url="https://example.supabase.co/",
        supabase_key="test-key",
    )

    assert captured["url"] == "https://example.supabase.co/rest/v1/places"
    assert captured["params"] == {
        "select": "id,nombre,descripcion,slug",
        "limit": 2,
        "or": (
            "nombre.ilike.%2Acasco%2A,descripcion.ilike.%2Acasco%2A,"
            "title.ilike.%2Acasco%2A,snippet.ilike.%2Acasco%2A"
        ),
    }
    assert docs[0]["source"] == "casco-viejo"


def test_retrieve_documents_history_source_empty_is_graceful(monkeypatch) -> None:
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "test-key")
    monkeypatch.setenv("SUPABASE_RETRIEVAL_TABLE", "places_embeddings")
    monkeypatch.setenv("SUPABASE_RETRIEVAL_SELECT", "id,title,snippet,source")

    class FakeResponse:
        @staticmethod
        def raise_for_status() -> None:
            return None

        @staticmethod
        def json():
            return []

    monkeypatch.setattr(httpx.Client, "get", lambda *args, **kwargs: FakeResponse())

    docs = retrieval.retrieve_documents(query="history of bilbao", top_k=2)

    assert len(docs) == 2
    assert docs[0]["id"] == "mock-1"


def test_historical_query_balances_places_and_history(monkeypatch) -> None:
    monkeypatch.setenv("SUPABASE_HISTORY_TABLE", "history")

    class FakeResponse:
        def __init__(self, payload):
            self._payload = payload

        @staticmethod
        def raise_for_status() -> None:
            return None

        def json(self):
            return self._payload

    def fake_get(self, url, headers=None, params=None):
        if url.endswith("/places"):
            return FakeResponse(
                [
                    {
                        "id": "p1",
                        "nombre": "Casco Viejo",
                        "descripcion": "Barrio con plazas y bares.",
                        "slug": "casco-viejo",
                    }
                ]
            )
        if url.endswith("/history"):
            return FakeResponse(
                [
                    {
                        "id": "h1",
                        "title": "Historia del Casco Viejo",
                        "snippet": "Origen medieval de Bilbao y sus siete calles.",
                        "source": "history://casco-viejo",
                    }
                ]
            )
        return FakeResponse([])

    monkeypatch.setattr(httpx.Client, "get", fake_get)

    docs = retrieval._supabase_retrieval(
        query="historia del casco viejo",
        top_k=2,
        supabase_url="https://example.supabase.co",
        supabase_key="test-key",
    )

    assert [doc["id"] for doc in docs] == ["h1", "p1"]


def test_stable_ordering_and_snippet_normalization(monkeypatch) -> None:
    class FakeResponse:
        @staticmethod
        def raise_for_status() -> None:
            return None

        @staticmethod
        def json():
            return [
                {
                    "id": "b",
                    "title": "B title",
                    "snippet": "  same    words   ",
                    "source": "s2",
                },
                {
                    "id": "a",
                    "title": "A title",
                    "snippet": "same words",
                    "source": "s1",
                },
            ]

    monkeypatch.setattr(httpx.Client, "get", lambda *args, **kwargs: FakeResponse())

    docs = retrieval._supabase_retrieval(
        query="none",
        top_k=2,
        supabase_url="https://example.supabase.co",
        supabase_key="test-key",
    )

    assert [doc["id"] for doc in docs] == ["a", "b"]
    assert docs[0]["snippet"] == "same words"


def test_missing_source_uses_deterministic_fallback(monkeypatch) -> None:
    class FakeResponse:
        @staticmethod
        def raise_for_status() -> None:
            return None

        @staticmethod
        def json():
            return [
                {
                    "id": "h2",
                    "title": "Bilbao industrial",
                    "snippet": "Transformación de la ría.",
                }
            ]

    monkeypatch.setattr(httpx.Client, "get", lambda *args, **kwargs: FakeResponse())

    docs = retrieval._supabase_retrieval(
        query="historia bilbao",
        top_k=1,
        supabase_url="https://example.supabase.co",
        supabase_key="test-key",
    )

    assert docs[0]["source"] == "supabase://places/h2"
