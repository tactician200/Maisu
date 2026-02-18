import os
from typing import Any
from urllib.parse import quote

import httpx


DEFAULT_DOCS = [
    {
        "id": "mock-1",
        "title": "Bilbao Casco Viejo",
        "snippet": "Zona ideal para pintxos y ambiente local.",
        "source": "mock://places/casco-viejo",
    },
    {
        "id": "mock-2",
        "title": "Museo Guggenheim",
        "snippet": "Referente cultural moderno junto a la ría.",
        "source": "mock://places/guggenheim",
    },
    {
        "id": "mock-3",
        "title": "Mercado de la Ribera",
        "snippet": "Mercado histórico con gastronomía vasca.",
        "source": "mock://places/ribera",
    },
]


def retrieve_documents(query: str, top_k: int = 3) -> list[dict[str, Any]]:
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not supabase_url or not supabase_key:
        return _mock_docs(top_k=top_k)

    try:
        docs = _supabase_retrieval(
            query=query,
            top_k=top_k,
            supabase_url=supabase_url,
            supabase_key=supabase_key,
        )
        return docs if docs else _mock_docs(top_k=top_k)
    except Exception:
        return _mock_docs(top_k=top_k)


def _mock_docs(top_k: int) -> list[dict[str, Any]]:
    return DEFAULT_DOCS[:top_k]


def _supabase_retrieval(
    query: str,
    top_k: int,
    supabase_url: str,
    supabase_key: str,
) -> list[dict[str, Any]]:
    base = supabase_url.rstrip("/")
    table = os.getenv("SUPABASE_RETRIEVAL_TABLE", "places")
    select = os.getenv("SUPABASE_RETRIEVAL_SELECT", "id,nombre,descripcion,slug")
    timeout = float(os.getenv("SUPABASE_RETRIEVAL_TIMEOUT_SECONDS", "2.5"))

    params: dict[str, str | int] = {
        "select": select,
        "limit": max(1, top_k),
    }
    sanitized = query.strip().replace("%", "")
    if sanitized:
        needle = quote(f"*{sanitized}*")
        params["or"] = f"nombre.ilike.{needle},descripcion.ilike.{needle}"

    url = f"{base}/rest/v1/{table}"
    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Accept": "application/json",
    }

    with httpx.Client(timeout=timeout) as client:
        response = client.get(url, headers=headers, params=params)

    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, list):
        return []

    docs: list[dict[str, Any]] = []
    for row in payload[:top_k]:
        if not isinstance(row, dict):
            continue
        row_id = str(row.get("id") or row.get("slug") or "")
        title = str(row.get("title") or row.get("nombre") or "").strip()
        snippet = str(row.get("snippet") or row.get("descripcion") or "").strip()
        source = str(row.get("source") or row.get("slug") or "supabase://places")
        if not title or not snippet:
            continue
        docs.append(
            {
                "id": row_id or f"supabase-{len(docs)+1}",
                "title": title,
                "snippet": snippet,
                "source": source,
            }
        )

    return docs
