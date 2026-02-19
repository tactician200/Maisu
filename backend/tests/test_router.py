from app.router import classify_query_route


def test_classify_structured_query() -> None:
    assert classify_query_route("¿Cuál es el horario del Guggenheim?") == "structured"


def test_classify_narrative_query() -> None:
    assert classify_query_route("Cuéntame la historia del Casco Viejo") == "narrative"


def test_classify_hybrid_query() -> None:
    assert classify_query_route("Explica la historia y horario del Mercado de la Ribera") == "hybrid"
