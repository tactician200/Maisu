import json
import os
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, call, patch
from uuid import uuid4

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
LLM_SERVICE_DIR = os.path.dirname(CURRENT_DIR)
PROJECT_ROOT = os.path.dirname(LLM_SERVICE_DIR)
MAISU_ROOT = os.path.dirname(PROJECT_ROOT)
if LLM_SERVICE_DIR not in sys.path:
    sys.path.insert(0, LLM_SERVICE_DIR)

import app


class TestPersonalityPrompt(unittest.TestCase):
    def test_system_prompt_has_maisu_persona_contract(self):
        prompt_path = os.path.join(MAISU_ROOT, "config", "system_prompt.md")
        with open(prompt_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("You are MAISU", content)
        self.assertIn("Stay in character as MAISU", content)
        self.assertIn("helpful, harmless, and honest", content)


class TestConversationIngestionFlow(unittest.IsolatedAsyncioTestCase):
    async def test_process_message_persists_user_then_assistant(self):
        fake_conv_id = uuid4()
        fake_repo = MagicMock()
        fake_repo.get_or_create_conversation.return_value = fake_conv_id
        fake_repo.get_conversation_history.return_value = [{"role": "assistant", "content": "hola"}]

        fake_manager_instance = MagicMock()
        fake_manager_instance.generate_response = AsyncMock(return_value="respuesta MAISU")

        ch = MagicMock()
        method = SimpleNamespace(delivery_tag="tag-1")

        payload = {
            "platform": "telegram",
            "chat_id": "77",
            "text": "  hello there  ",
            "message_id": 101,
        }

        with patch.object(app, "conversation_repo", fake_repo), \
             patch.object(app, "LLMManager", return_value=fake_manager_instance), \
             patch.object(app, "send_reply_http", new=AsyncMock()):
            await app.process_message_async(ch, method, None, json.dumps(payload).encode("utf-8"))

        fake_repo.add_message.assert_has_calls(
            [
                call(fake_conv_id, "user", "hello there"),
                call(fake_conv_id, "assistant", "respuesta MAISU"),
            ]
        )
        self.assertEqual(fake_repo.add_message.call_count, 2)
        ch.basic_ack.assert_called_once_with(delivery_tag="tag-1")


if __name__ == "__main__":
    unittest.main()
