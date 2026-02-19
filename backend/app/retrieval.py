import os
import re
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

_HISTORY_HINTS = {
    "history",
    "historical",
    "historic",
    "historia",
    "histórico",
    "historia",
    "origen",
    "origins",
    "pasado",
    "before",
    "antigu",
}


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


def _tokenize_query(query: str) -> list[str]:
    tokens: list[str] = []
    seen: set[str] = set()
    for raw in re.findall(r"\w+", query.lower(), flags=re.UNICODE):
        token = raw.strip()
        if len(token) < 2 or token in seen:
            continue
        seen.add(token)
        tokens.append(token)
    return tokens


def _is_historical_query(query: str, tokens: list[str]) -> bool:
    lowered = query.lower()
    if any(hint in lowered for hint in _HISTORY_HINTS):
        return True
    return any(token in _HISTORY_HINTS for token in tokens)


def _build_search_filter(query: str, tokens: list[str]) -> str:
    clauses: list[str] = []
    sanitized = query.strip().replace("%", "")
    if sanitized:
        needle = quote(f"*{sanitized}*")
        clauses.extend(
            [
                f"nombre.ilike.{needle}",
                f"descripcion.ilike.{needle}",
                f"title.ilike.{needle}",
                f"snippet.ilike.{needle}",
            ]
        )

    for token in tokens[:6]:
        token_needle = quote(f"*{token}*")
        clauses.extend(
            [
                f"nombre.ilike.{token_needle}",
                f"descripcion.ilike.{token_needle}",
                f"title.ilike.{token_needle}",
                f"snippet.ilike.{token_needle}",
            ]
        )

    unique_clauses: list[str] = []
    seen: set[str] = set()
    for clause in clauses:
        if clause in seen:
            continue
        seen.add(clause)
        unique_clauses.append(clause)
    return ",".join(unique_clauses)


def _score_row(
    row: dict[str, Any],
    query: str,
    tokens: list[str],
    *,
    is_history_source: bool,
    historical_query: bool,
) -> int:
    title = str(row.get("title") or row.get("nombre") or "").lower()
    snippet = str(row.get("snippet") or row.get("descripcion") or "").lower()
    haystack = f"{title} {snippet}".strip()

    if not haystack:
        return 0

    score = 0
    query_lower = query.strip().lower()
    if query_lower and query_lower in haystack:
        score += 8

    for token in tokens:
        if token in title:
            score += 4
        if token in snippet:
            score += 2

    if is_history_source:
        score += 1
        if historical_query:
            score += 4

    return score


def _normalize_row(row: dict[str, Any], *, table: str) -> dict[str, Any] | None:
    row_id = str(row.get("id") or row.get("slug") or "").strip()
    title = str(row.get("title") or row.get("nombre") or "").strip()
    snippet_raw = str(row.get("snippet") or row.get("descripcion") or "").strip()
    snippet = " ".join(snippet_raw.split())

    if not title or not snippet:
        return None

    source = str(row.get("source") or "").strip()
    if not source:
        slug = str(row.get("slug") or "").strip()
        if slug:
            source = slug
        elif row_id:
            source = f"supabase://{table}/{row_id}"
        else:
            source = f"supabase://{table}"

    return {
        "id": row_id or f"supabase-{table}",
        "title": title,
        "snippet": snippet,
        "source": source,
    }


def _fetch_rows(
    client: httpx.Client,
    *,
    base: str,
    table: str,
    select: str,
    headers: dict[str, str],
    search_filter: str,
    limit: int,
) -> list[dict[str, Any]]:
    params: dict[str, str | int] = {"select": select, "limit": limit}
    if search_filter:
        params["or"] = search_filter

    url = f"{base}/rest/v1/{table}"
    response = client.get(url, headers=headers, params=params)
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, list):
        return []
    return [row for row in payload if isinstance(row, dict)]


def _supabase_retrieval(
    query: str,
    top_k: int,
    supabase_url: str,
    supabase_key: str,
) -> list[dict[str, Any]]:
    base = supabase_url.rstrip("/")
    table = os.getenv("SUPABASE_RETRIEVAL_TABLE", "places")
    history_table = os.getenv("SUPABASE_HISTORY_TABLE", "").strip()
    select = os.getenv("SUPABASE_RETRIEVAL_SELECT", "id,nombre,descripcion,slug")
    timeout = float(os.getenv("SUPABASE_RETRIEVAL_TIMEOUT_SECONDS", "2.5"))

    limit = max(1, top_k)
    tokens = _tokenize_query(query)
    historical_query = _is_historical_query(query, tokens)
    search_filter = _build_search_filter(query, tokens)

    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Accept": "application/json",
    }

    candidates: list[tuple[int, int, dict[str, Any]]] = []

    with httpx.Client(timeout=timeout) as client:
        place_rows = _fetch_rows(
            client,
            base=base,
            table=table,
            select=select,
            headers=headers,
            search_filter=search_filter,
            limit=limit,
        )

        for idx, row in enumerate(place_rows):
            normalized = _normalize_row(row, table=table)
            if not normalized:
                continue
            score = _score_row(
                row,
                query,
                tokens,
                is_history_source=False,
                historical_query=historical_query,
            )
            candidates.append((score, idx, normalized))

        if history_table:
            history_rows = _fetch_rows(
                client,
                base=base,
                table=history_table,
                select=select,
                headers=headers,
                search_filter=search_filter,
                limit=limit,
            )
            for idx, row in enumerate(history_rows):
                normalized = _normalize_row(row, table=history_table)
                if not normalized:
                    continue
                score = _score_row(
                    row,
                    query,
                    tokens,
                    is_history_source=True,
                    historical_query=historical_query,
                )
                candidates.append((score, idx + limit, normalized))

    # Deterministic ranking by relevance, then title/id as stable tie-breakers.
    ranked = sorted(
        candidates,
        key=lambda item: (
            -item[0],
            item[2]["title"].lower(),
            item[2]["id"],
            item[1],
        ),
    )

    docs: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for _, _, candidate in ranked:
        cid = str(candidate["id"])
        if cid in seen_ids:
            continue
        seen_ids.add(cid)
        docs.append(candidate)
        if len(docs) >= top_k:
            break

    return docs
