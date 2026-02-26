import json
import unittest
from unittest.mock import AsyncMock, Mock

import httpx

from app import _log_event, _send_telegram_chunk


class ObservabilityTests(unittest.IsolatedAsyncioTestCase):
    def test_log_event_redacts_sensitive_fields(self):
        with self.assertLogs("integrations_service", level="INFO") as captured:
            _log_event("test_event", api_key="abc123", chat_id="42")

        payload = json.loads(captured.output[0].split(":", 2)[2])
        self.assertEqual(payload["event"], "test_event")
        self.assertEqual(payload["api_key"], "[REDACTED]")
        self.assertEqual(payload["chat_id"], "42")

    async def test_send_chunk_emits_retry_count_and_chunk_index(self):
        client = AsyncMock()
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {"ok": True}
        client.post = AsyncMock(return_value=response)

        with self.assertLogs("integrations_service", level="INFO") as captured:
            result, retry_count = await _send_telegram_chunk(
                client,
                "https://example.invalid/send",
                {"chat_id": "55", "text": "hola"},
                {"Content-Type": "application/json"},
                message_id=999,
                chunk_index=2,
            )

        self.assertEqual(result, {"ok": True})
        self.assertEqual(retry_count, 0)

        event_payload = json.loads(captured.output[0].split(":", 2)[2])
        self.assertEqual(event_payload["event"], "telegram_chunk_sent")
        self.assertEqual(event_payload["message_id"], 999)
        self.assertEqual(event_payload["chat_id"], "55")
        self.assertEqual(event_payload["chunk_index"], 2)
        self.assertEqual(event_payload["retry_count"], 0)
        self.assertIn("latency_ms", event_payload)


if __name__ == "__main__":
    unittest.main()
