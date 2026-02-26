import os
import re
import unicodedata
from dataclasses import dataclass
from typing import Any

import httpx


class ProviderError(Exception):
    pass


@dataclass
class ProviderResult:
    answer: str
    provider: str


_LOW_VALUE_PATTERNS = [
    "no he podido generar una respuesta en este momento",
    "no puedo generar una respuesta en este momento",
    "no se ha podido generar una respuesta en este momento",
    "no se puede generar una respuesta en este momento",
    "estoy en modo de contingencia con precision limitada",
    "i couldnt generate a response at this time",
    "i couldnt generate a response at the moment",
    "i cant generate a response at this time",
    "i cannot generate a response at this time",
    "i am unable to generate a response at this time",
    "i was unable to generate a response at this time",
    "i am running in fallback mode with limited precision",
]


_APOSTROPHE_RE = re.compile(r"[’']")
_NON_WORD_RE = re.compile(r"[^\w\s]")
_WHITESPACE_RE = re.compile(r"\s+")


def _normalize_guardrail_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    normalized = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    normalized = normalized.lower()
    normalized = _APOSTROPHE_RE.sub("", normalized)
    normalized = _NON_WORD_RE.sub(" ", normalized)
    normalized = _WHITESPACE_RE.sub(" ", normalized).strip()
    return normalized


_NORMALIZED_LOW_VALUE_PATTERNS = tuple(
    pattern for pattern in (_normalize_guardrail_text(p) for p in _LOW_VALUE_PATTERNS) if pattern
)


def _extract_response_text(payload: dict[str, Any]) -> str | None:
    output_text = payload.get("output_text")
    if isinstance(output_text, str) and output_text.strip():
        return output_text.strip()

    output_items = payload.get("output")
    if not isinstance(output_items, list):
        return None

    chunks: list[str] = []
    for item in output_items:
        if not isinstance(item, dict):
            continue
        content = item.get("content")
        if not isinstance(content, list):
            continue
        for part in content:
            if not isinstance(part, dict):
                continue
            text_value = part.get("text")
            if isinstance(text_value, str) and text_value.strip():
                chunks.append(text_value.strip())

    if chunks:
        return "\n".join(chunks)
    return None


def is_low_value_answer(answer: str) -> bool:
    if not answer:
        return False
    normalized = _normalize_guardrail_text(answer)
    if not normalized:
        return False
    for pattern in _NORMALIZED_LOW_VALUE_PATTERNS:
        if pattern in normalized:
            return True
    return False


class OpenAIProvider:
    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.timeout_seconds = float(os.getenv("OPENAI_TIMEOUT_SECONDS", "8"))

    def _build_prompts(
        self,
        query: str,
        documents: list[dict[str, Any]],
        lang: str | None = None,
        name: str | None = None,
        tone: str | None = None,
        style: str | None = None,
        interests: list[str] | None = None,
    ) -> tuple[str, str]:
        context_lines = []
        for idx, d in enumerate(documents, start=1):
            context_lines.append(
                f"[{idx}] {d.get('title', 'Sin título')} | {d.get('snippet', 'Sin detalle')} | source: {d.get('source', 'n/a')}"
            )

        lang_hint = (lang or "es").lower()
        if lang_hint.startswith("en"):
            insufficient_note = "Insufficient information in the references."
        elif lang_hint.startswith("eu"):
            insufficient_note = "Erreferentzietan informazio nahikorik ez."
        else:
            insufficient_note = "Información insuficiente en las referencias."

        system_prompt = (
            "You are a concise Bilbao tourism assistant. "
            "Use only the provided references and do not add places or facts not present. "
            "Respond with exactly 3 short sections in the user's language: "
            "'1) Resumen', '2) Plan recomendado', '3) Consejos útiles'. "
            "Keep each section 1-3 sentences. "
            "Avoid filler, apologies, or generic fallback language. "
            f"If references are insufficient, say '{insufficient_note}' in the Summary and still provide the best possible plan grounded in what is available."
        )

        personalization_rules: list[str] = []
        if tone == "concise":
            personalization_rules.append("Keep the response very brief and practical.")
        elif tone == "detailed":
            personalization_rules.append("Provide a bit more detail while staying grounded in references.")

        if style == "bullets":
            personalization_rules.append("Format each section as bullet points.")
        elif style == "paragraph":
            personalization_rules.append("Format each section as short paragraphs.")

        if interests:
            personalization_rules.append(
                "When relevant, prioritize suggestions connected to these interests: " + ", ".join(interests[:5]) + "."
            )

        if name:
            personalization_rules.append(f"Address the user as {name} once when appropriate.")

        if personalization_rules:
            system_prompt = system_prompt + " Personalization: " + " ".join(personalization_rules)

        user_prompt = (
            f"Language: {lang_hint}\n"
            f"Question: {query}\n\n"
            "References:\n"
            + "\n".join(context_lines)
            + "\n\nQuality rules:\n"
            "- Use details from at least 2 references when available.\n"
            "- Mention source titles in each section.\n"
            "- Keep output under 140 words."
        )

        return system_prompt, user_prompt

    async def generate(
        self,
        query: str,
        documents: list[dict[str, Any]],
        lang: str | None = None,
        name: str | None = None,
        tone: str | None = None,
        style: str | None = None,
        interests: list[str] | None = None,
    ) -> ProviderResult:
        if not self.api_key:
            raise ProviderError("OPENAI_API_KEY is missing")

        system_prompt, user_prompt = self._build_prompts(
            query=query,
            documents=documents,
            lang=lang,
            name=name,
            tone=tone,
            style=style,
            interests=interests,
        )

        payload = {
            "model": self.model,
            "input": [
                {
                    "role": "system",
                    "content": [{"type": "input_text", "text": system_prompt}],
                },
                {
                    "role": "user",
                    "content": [{"type": "input_text", "text": user_prompt}],
                },
            ],
            "max_output_tokens": 240,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post("https://api.openai.com/v1/responses", headers=headers, json=payload)
            if response.status_code in (401, 403, 429, 500, 502, 503, 504):
                raise ProviderError(f"OpenAI unavailable ({response.status_code})")
            response.raise_for_status()
        except (httpx.TimeoutException, httpx.HTTPError) as exc:
            raise ProviderError(str(exc)) from exc

        data = response.json()
        answer = _extract_response_text(data)
        if not answer:
            answer = "No he podido generar una respuesta en este momento."

        return ProviderResult(answer=answer.strip(), provider="openai")


def build_fallback_answer(
    query: str,
    documents: list[dict[str, Any]],
    lang: str | None = None,
    name: str | None = None,
    tone: str | None = None,
    style: str | None = None,
    interests: list[str] | None = None,
) -> str:
    top_titles = [d.get("title", "") for d in documents[:2] if d.get("title")]
    docs_summary = ", ".join(top_titles) if top_titles else "referencias locales"

    is_en = (lang or "").lower().startswith("en")

    if is_en:
        greeting = f"Hi {name}. " if name else ""
        lines = [
            f"1) Summary: {greeting}I am running in fallback mode with limited precision.",
            f"2) Recommended plan: Start with {docs_summary} and continue on foot nearby.",
            "3) Useful tips: Go early, book popular spots, and verify opening hours.",
        ]
        if tone == "detailed":
            lines.append("4) Extra detail: Build your route around walking distance and opening times.")
        if interests:
            lines.append("5) Interest note: Prioritize places related to " + ", ".join(interests[:3]) + ".")
    else:
        greeting = f"Hola {name}. " if name else ""
        lines = [
            f"1) Resumen: {greeting}Estoy en modo de contingencia con precisión limitada.",
            f"2) Plan recomendado: Empieza por {docs_summary} y sigue a pie por la zona.",
            "3) Consejos útiles: Ve pronto, reserva locales populares y confirma horarios.",
        ]
        if tone == "detailed":
            lines.append("4) Detalle extra: Organiza la ruta por distancia a pie y horarios de apertura.")
        if interests:
            lines.append("5) Nota de interés: Prioriza lugares relacionados con " + ", ".join(interests[:3]) + ".")

    if style == "paragraph":
        return " ".join(line.split(") ", 1)[1] if ") " in line else line for line in lines)

    if style == "bullets":
        return "\n".join(f"- {(line.split(') ', 1)[1] if ') ' in line else line)}" for line in lines)

    return "\n".join(lines)
