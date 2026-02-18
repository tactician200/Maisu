import os
from dataclasses import dataclass
from typing import Any

import httpx


class ProviderError(Exception):
    pass


@dataclass
class ProviderResult:
    answer: str
    provider: str


class OpenAIProvider:
    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.timeout_seconds = float(os.getenv("OPENAI_TIMEOUT_SECONDS", "8"))

    async def generate(self, query: str, documents: list[dict[str, Any]], lang: str | None = None) -> ProviderResult:
        if not self.api_key:
            raise ProviderError("OPENAI_API_KEY is missing")

        context_lines = []
        for idx, d in enumerate(documents, start=1):
            context_lines.append(
                f"[{idx}] {d.get('title', 'Sin título')} | {d.get('snippet', 'Sin detalle')} | source: {d.get('source', 'n/a')}"
            )

        lang_hint = (lang or "es").lower()
        system_prompt = (
            "You are a concise Bilbao tourism assistant. "
            "Use only the provided references. "
            "If info is missing, state uncertainty briefly. "
            "Respond with exactly 3 short sections: '\n'"
            "1) Resumen\n2) Plan recomendado\n3) Consejos útiles. "
            "Do not invent citations or places not present in references."
        )

        user_prompt = (
            f"Language: {lang_hint}\n"
            f"Question: {query}\n\n"
            "References:\n"
            + "\n".join(context_lines)
            + "\n\nKeep output under 140 words."
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
        answer = data.get("output_text")
        if not answer:
            answer = "No he podido generar una respuesta en este momento."

        return ProviderResult(answer=answer.strip(), provider="openai")


def build_fallback_answer(query: str, documents: list[dict[str, Any]], lang: str | None = None) -> str:
    top_titles = [d.get("title", "") for d in documents[:2] if d.get("title")]
    docs_summary = ", ".join(top_titles) if top_titles else "referencias locales"

    if (lang or "").lower().startswith("en"):
        return (
            "1) Summary: I am running in fallback mode with limited precision.\n"
            f"2) Recommended plan: Start with {docs_summary} and continue on foot nearby.\n"
            "3) Useful tips: Go early, book popular spots, and verify opening hours."
        )

    return (
        "1) Resumen: Estoy en modo de contingencia con precisión limitada.\n"
        f"2) Plan recomendado: Empieza por {docs_summary} y sigue a pie por la zona.\n"
        "3) Consejos útiles: Ve pronto, reserva locales populares y confirma horarios."
    )
