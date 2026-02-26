import os
import logging
import google.generativeai as genai
from typing import List, Optional
from config import Config
from providers.base import LLMProvider, Message

logger = logging.getLogger("llm_provider_gemini")

class GeminiProvider(LLMProvider):
    def __init__(self):
        self.api_key = Config.GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables.")
        
        genai.configure(api_key=self.api_key)
        # We define the model name here, but instantiate the model object later
        # to inject the system prompt dynamically.
        self.model_name = 'gemini-2.5-flash'

    async def generate_response(self, prompt: str, history: List[Message], system_prompt: Optional[str] = None) -> str:
        try:
            # 1. Instantiate model with native system_instruction
            # This is the "Native Personality Implant"
            model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=system_prompt
            )

            # 2. Construct history in Gemini format
            gemini_history = []
            for msg in history:
                # System instruction is injected natively; skip system turns from history.
                if msg.role == "system":
                    continue
                role = "user" if msg.role == "user" else "model"
                gemini_history.append({'role': role, 'parts': [msg.content]})

            # 3. Start Chat Session
            chat = model.start_chat(history=gemini_history)
            
            # 4. Generate Response (Blocking I/O in Executor)
            import asyncio
            loop = asyncio.get_event_loop()
            
            # Note: We send just the prompt. System instruction is already in the model context.
            response = await loop.run_in_executor(None, chat.send_message, prompt)
            return response.text
            
        except Exception as e:
            logger.error("Gemini generation failed: %s", e)
            raise
