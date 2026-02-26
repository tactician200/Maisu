import json
import os
import sys
import unittest
from unittest.mock import AsyncMock

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
LLM_SERVICE_DIR = os.path.dirname(CURRENT_DIR)
if LLM_SERVICE_DIR not in sys.path:
    sys.path.insert(0, LLM_SERVICE_DIR)

from manager import LLMManager
from providers.base import Message


class TestLLMObservability(unittest.IsolatedAsyncioTestCase):
    async def test_generate_response_logs_telemetry_fields(self):
        manager = LLMManager()
        manager.primary_provider = AsyncMock()
        manager.primary_provider.generate_response = AsyncMock(return_value="ok")
        manager.fallback_provider = None

        telemetry = {"message_id": 123, "chat_id": "999", "chunk_index": 1}

        with self.assertLogs("llm_manager", level="INFO") as captured:
            output = await manager.generate_response("hello", [Message(role="user", content="hi")], telemetry=telemetry)

        self.assertEqual(output, "ok")
        payload = json.loads(captured.output[0].split(":", 2)[2])
        self.assertEqual(payload["event"], "llm_primary_success")
        self.assertEqual(payload["message_id"], 123)
        self.assertEqual(payload["chat_id"], "999")
        self.assertEqual(payload["chunk_index"], 1)
        self.assertEqual(payload["retry_count"], 0)
        self.assertIn("latency_ms", payload)


if __name__ == "__main__":
    unittest.main()
