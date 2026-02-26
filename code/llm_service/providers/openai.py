import os
import logging
from openai import OpenAI
from typing import List, Optional
from config import Config
from providers.base import LLMProvider, Message

logger = logging.getLogger("llm_provider_openai")

class OpenAIProvider(LLMProvider):
    def __init__(self):
        self.api_key = Config.OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables.")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4o-mini" 

    async def generate_response(self, prompt: str, history: List[Message], system_prompt: Optional[str] = None) -> str:
        try:
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            for msg in history:
                if msg.role == "system":
                    # Already injected as dedicated system_prompt.
                    continue
                role = "user" if msg.role == "user" else "assistant"
                messages.append({"role": role, "content": msg.content})
            
            messages.append({"role": "user", "content": prompt})

            # Run blocking call in executor
            import asyncio
            loop = asyncio.get_event_loop()
            
            # Helper for the synchronous call
            def call_openai():
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages
                )
                return completion.choices[0].message.content

            response = await loop.run_in_executor(None, call_openai)
            return response
        except Exception as e:
            logger.error("OpenAI generation failed: %s", e)
            raise
