import asyncio
import json
import logging
import time
from typing import List, Optional

from config import Config
from providers.base import LLMProvider, Message
from providers.gemini import GeminiProvider
from providers.openai import OpenAIProvider

logger = logging.getLogger("llm_manager")


def _log_manager_event(event: str, level: int = logging.INFO, **fields):
    payload = {"event": event, **fields}
    logger.log(level, json.dumps(payload, ensure_ascii=False))


class LLMManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMManager, cls).__new__(cls)
            cls._instance._initialize_providers()
        return cls._instance

    def _initialize_providers(self):
        self.primary_provider: Optional[LLMProvider] = None
        self.fallback_provider: Optional[LLMProvider] = None
        self.system_prompt: str = Config.SYSTEM_PROMPT

        primary_name = Config.LLM_PROVIDER_PRIMARY.lower()
        if primary_name == "gemini":
            try:
                self.primary_provider = GeminiProvider()
                _log_manager_event("provider_initialized", provider="gemini", role="primary")
            except ValueError as e:
                _log_manager_event("provider_init_failed", level=logging.WARNING, provider="gemini", role="primary", error=str(e))
        elif primary_name == "openai":
            try:
                self.primary_provider = OpenAIProvider()
                _log_manager_event("provider_initialized", provider="openai", role="primary")
            except ValueError as e:
                _log_manager_event("provider_init_failed", level=logging.WARNING, provider="openai", role="primary", error=str(e))
        else:
            _log_manager_event("provider_unknown", level=logging.WARNING, provider=primary_name, role="primary")

        fallback_name = Config.LLM_PROVIDER_FALLBACK.lower()
        if fallback_name == "gemini":
            try:
                self.fallback_provider = GeminiProvider()
                _log_manager_event("provider_initialized", provider="gemini", role="fallback")
            except ValueError as e:
                _log_manager_event("provider_init_failed", level=logging.WARNING, provider="gemini", role="fallback", error=str(e))
        elif fallback_name == "openai":
            try:
                self.fallback_provider = OpenAIProvider()
                _log_manager_event("provider_initialized", provider="openai", role="fallback")
            except ValueError as e:
                _log_manager_event("provider_init_failed", level=logging.WARNING, provider="openai", role="fallback", error=str(e))
        else:
            _log_manager_event("provider_unknown", level=logging.WARNING, provider=fallback_name, role="fallback")

        if not self.primary_provider and not self.fallback_provider:
            _log_manager_event("provider_unavailable", level=logging.ERROR)

    async def generate_response(self, prompt: str, history: List[Message], telemetry: Optional[dict] = None) -> str:
        telemetry = telemetry or {}

        if self.primary_provider:
            try:
                started = time.perf_counter()
                response = await self.primary_provider.generate_response(prompt, history, self.system_prompt)
                latency_ms = round((time.perf_counter() - started) * 1000, 2)
                _log_manager_event("llm_primary_success", latency_ms=latency_ms, retry_count=0, **telemetry)
                return response
            except Exception as e:
                _log_manager_event("llm_primary_failed", level=logging.WARNING, retry_count=0, error=str(e), **telemetry)

        if self.fallback_provider:
            try:
                started = time.perf_counter()
                response = await self.fallback_provider.generate_response(prompt, history, self.system_prompt)
                latency_ms = round((time.perf_counter() - started) * 1000, 2)
                _log_manager_event("llm_fallback_success", latency_ms=latency_ms, retry_count=1, **telemetry)
                return response
            except Exception as e:
                _log_manager_event("llm_fallback_failed", level=logging.ERROR, retry_count=1, error=str(e), **telemetry)

        return "Lo siento, mis cerebros (Gemini y OpenAI) no están disponibles en este momento."
