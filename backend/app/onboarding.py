from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

CRITICAL_FIELDS: list[dict[str, Any]] = [
    {
        "key": "stay_duration",
        "questions": {
            "es": "¿Cuántos días vas a estar en Bilbao?",
            "en": "How many days will you stay in Bilbao?",
            "eu": "Zenbat egun egongo zara Bilbon?",
        },
    },
    {
        "key": "trip_type",
        "questions": {
            "es": "¿Viajas solo, en pareja, con amigos, en familia o por trabajo?",
            "en": "Are you traveling solo, as a couple, with friends, family, or for work?",
            "eu": "Bakarrik, bikotean, lagunekin, familian ala lanagatik bidaiatzen duzu?",
        },
    },
    {
        "key": "dominant_interest",
        "questions": {
            "es": "¿Qué te interesa más ahora: cultura, gastronomía, naturaleza o un poco de todo?",
            "en": "What interests you most right now: culture, food, nature, or a mix?",
            "eu": "Zer interesatzen zaizu gehien: kultura, gastronomia, natura ala denetarik?",
        },
    },
]


def _normalize_lang(lang: str | None) -> str:
    if lang in {"es", "en", "eu"}:
        return lang
    return "es"


def _extract_profile(preferences: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(preferences, dict):
        return {}
    profile = preferences.get("profile")
    if isinstance(profile, dict):
        return profile
    return {}


def _extract_onboarding_state(preferences: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(preferences, dict):
        return {}
    state = preferences.get("onboarding")
    if isinstance(state, dict):
        return state
    return {}


def _extract_field_value(raw_value: Any) -> Any:
    if isinstance(raw_value, dict):
        if "value" in raw_value:
            return raw_value.get("value")
        if "val" in raw_value:
            return raw_value.get("val")
    return raw_value


def _is_value_present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set, dict)):
        return len(value) > 0
    return True


def build_onboarding_next(
    *,
    preferences: dict[str, Any] | None,
    lang: str | None,
) -> tuple[dict[str, str] | None, dict[str, Any] | None]:
    profile = _extract_profile(preferences)
    onboarding_state = _extract_onboarding_state(preferences)

    asked_raw = onboarding_state.get("asked")
    asked = {item for item in asked_raw if isinstance(item, str)} if isinstance(asked_raw, list) else set()

    for field in CRITICAL_FIELDS:
        key = field["key"]
        raw_value = profile.get(key)
        value = _extract_field_value(raw_value)
        if _is_value_present(value):
            continue
        if key in asked:
            continue

        selected_lang = _normalize_lang(lang)
        question = field["questions"].get(selected_lang) or field["questions"]["es"]

        updated_state = dict(onboarding_state)
        updated_state["last_question"] = key
        updated_state["asked"] = sorted({*asked, key})
        updated_state["updated_at"] = datetime.now(timezone.utc).isoformat()

        return {"field": key, "question": question}, updated_state

    return None, None
