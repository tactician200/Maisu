from abc import ABC, abstractmethod
from typing import List, Literal, Optional
from dataclasses import dataclass

@dataclass
class Message:
    # Internal role set used across providers.
    # "assistant" is accepted because SQL persistence stores assistant turns with that role.
    role: Literal["user", "model", "assistant", "system"]
    content: str

class LLMProvider(ABC):
    @abstractmethod
    async def generate_response(self, prompt: str, history: List[Message], system_prompt: Optional[str] = None) -> str:
        pass
