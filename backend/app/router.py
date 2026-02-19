import re
from typing import Literal

Route = Literal["structured", "narrative", "hybrid"]

_STRUCTURED_HINTS = {
    "where",
    "donde",
    "dónde",
    "address",
    "dirección",
    "hours",
    "horario",
    "open",
    "abierto",
    "price",
    "precio",
    "cost",
    "entry",
    "ticket",
    "phone",
    "contact",
    "web",
    "website",
    "near",
    "cerca",
    "top",
    "best",
}

_NARRATIVE_HINTS = {
    "history",
    "histor",
    "culture",
    "cultura",
    "story",
    "origen",
    "why",
    "por qué",
    "explain",
    "explica",
    "tradition",
    "tradición",
    "background",
    "context",
}


def classify_query_route(query: str) -> Route:
    lowered = query.strip().lower()
    if not lowered:
        return "narrative"

    tokens = re.findall(r"\w+", lowered, flags=re.UNICODE)
    has_structured = any(hint in lowered for hint in _STRUCTURED_HINTS)
    has_narrative = any(hint in lowered for hint in _NARRATIVE_HINTS)

    if has_structured and has_narrative:
        return "hybrid"
    if has_structured:
        return "structured"
    if has_narrative:
        return "narrative"

    minimal_tokens = {"plan", "ideas", "help", "ayuda", "recommend", "recomienda"}
    if any(token in minimal_tokens for token in tokens):
        return "narrative"

    return "narrative"
