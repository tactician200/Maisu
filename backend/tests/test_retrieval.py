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
