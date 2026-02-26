from app.providers import _extract_response_text


def test_extract_response_text_prefers_output_text_when_present() -> None:
    payload = {
        "output_text": "Respuesta directa",
        "output": [
            {
                "content": [
                    {"type": "output_text", "text": "Contenido estructurado"},
                ]
            }
        ],
    }

    assert _extract_response_text(payload) == "Respuesta directa"


def test_extract_response_text_reads_structured_output_content() -> None:
    payload = {
        "output": [
            {
                "type": "message",
                "content": [
                    {"type": "output_text", "text": "1) Resumen: Bilbao cultural."},
                    {"type": "output_text", "text": "2) Plan recomendado: Guggenheim y ría."},
                ],
            }
        ]
    }

    assert _extract_response_text(payload) == (
        "1) Resumen: Bilbao cultural.\n"
        "2) Plan recomendado: Guggenheim y ría."
    )


def test_extract_response_text_ignores_non_text_and_blank_chunks() -> None:
    payload = {
        "output": [
            {
                "content": [
                    {"type": "reasoning", "summary": "..."},
                    {"type": "output_text", "text": "   "},
                    {"type": "output_text", "text": "Respuesta útil"},
                ]
            },
            "unexpected-item",
        ]
    }

    assert _extract_response_text(payload) == "Respuesta útil"


def test_extract_response_text_returns_none_when_no_text_available() -> None:
    payload = {
        "output": [
            {"type": "message", "content": [{"type": "reasoning", "summary": "sin texto"}]},
        ]
    }

    assert _extract_response_text(payload) is None
