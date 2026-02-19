import os
from typing import Any
from urllib.parse import quote

import httpx

_ALLOWED_TONES = {"concise", "detailed"}
_ALLOWED_STYLES = {"bullets", "paragraph"}


def normalize_preferences(preferences: Any) -> dict[str, Any]:
    if not isinstance(preferences, dict):
        return {}

    normalized: dict[str, Any] = {}

    tone = preferences.get("tone")
    if isinstance(tone, str):
        cleaned_tone = tone.strip().lower()
        if cleaned_tone in _ALLOWED_TONES:
            normalized["tone"] = cleaned_tone

    style = preferences.get("style")
    if isinstance(style, str):
        cleaned_style = style.strip().lower()
        if cleaned_style in _ALLOWED_STYLES:
            normalized["style"] = cleaned_style

    interests = preferences.get("interests")
    if isinstance(interests, list):
        cleaned_interests = [item.strip() for item in interests if isinstance(item, str) and item.strip()]
        if cleaned_interests:
            normalized["interests"] = cleaned_interests

    return normalized


class UserContextStore:
    def __init__(self) -> None:
        self._memory: dict[str, dict[str, Any]] = {}

    def get_context(self, session_id: str) -> dict[str, Any] | None:
        if not session_id:
            return None

        remote = self._get_context_supabase(session_id)
        if remote is not None:
            self._memory[session_id] = remote
            return remote

        return self._memory.get(session_id)

    def upsert_context(self, session_id: str, data: dict[str, Any]) -> dict[str, Any]:
        current = self.get_context(session_id) or {"session_id": session_id}

        incoming = dict(data)
        if "preferences" in incoming:
            incoming["preferences"] = normalize_preferences(incoming.get("preferences")) or None

        merged = {**current, **incoming, "session_id": session_id}
        merged_preferences = normalize_preferences(merged.get("preferences"))
        merged["preferences"] = merged_preferences or None

        remote = self._upsert_context_supabase(session_id, merged)
        stored = remote or merged
        self._memory[session_id] = stored
        return stored

    def _get_context_supabase(self, session_id: str) -> dict[str, Any] | None:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        if not supabase_url or not supabase_key:
            return None

        table = os.getenv("SUPABASE_USER_CONTEXT_TABLE", "user_context")
        timeout = float(os.getenv("SUPABASE_USER_CONTEXT_TIMEOUT_SECONDS", "2.0"))
        base = supabase_url.rstrip("/")
        url = f"{base}/rest/v1/{table}"

        headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Accept": "application/json",
        }
        params = {
            "select": "session_id,name,language,preferences,user_id",
            "session_id": f"eq.{quote(session_id)}",
            "limit": 1,
        }

        try:
            with httpx.Client(timeout=timeout) as client:
                response = client.get(url, headers=headers, params=params)
            response.raise_for_status()
            payload = response.json()
            if isinstance(payload, list) and payload:
                first = payload[0]
                if isinstance(first, dict):
                    return first
        except Exception:
            return None
        return None

    def _upsert_context_supabase(self, session_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        if not supabase_url or not supabase_key:
            return None

        table = os.getenv("SUPABASE_USER_CONTEXT_TABLE", "user_context")
        timeout = float(os.getenv("SUPABASE_USER_CONTEXT_TIMEOUT_SECONDS", "2.0"))
        base = supabase_url.rstrip("/")
        url = f"{base}/rest/v1/{table}?on_conflict=session_id"

        payload = {
            "session_id": session_id,
            "name": data.get("name"),
            "language": data.get("language"),
            "preferences": data.get("preferences"),
            "user_id": data.get("user_id"),
        }

        headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Prefer": "resolution=merge-duplicates,return=representation",
        }

        try:
            with httpx.Client(timeout=timeout) as client:
                response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            body = response.json()
            if isinstance(body, list) and body:
                first = body[0]
                if isinstance(first, dict):
                    return first
            if isinstance(body, dict):
                return body
        except Exception:
            return None
        return None
