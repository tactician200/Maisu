import os
import sys
import unittest

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
LLM_SERVICE_DIR = os.path.dirname(CURRENT_DIR)
if LLM_SERVICE_DIR not in sys.path:
    sys.path.insert(0, LLM_SERVICE_DIR)

from history_utils import normalize_history_role
from providers.base import Message


class TestMemoryPersonaSmoke(unittest.TestCase):
    def test_normalize_history_role(self):
        self.assertEqual(normalize_history_role("user"), "user")
        self.assertEqual(normalize_history_role("assistant"), "model")
        self.assertEqual(normalize_history_role("model"), "model")
        self.assertEqual(normalize_history_role("maisu"), "model")
        self.assertEqual(normalize_history_role("system"), "system")
        self.assertEqual(normalize_history_role("unknown"), "user")

    def test_message_accepts_assistant_role(self):
        msg = Message(role="assistant", content="hola")
        self.assertEqual(msg.role, "assistant")


if __name__ == "__main__":
    unittest.main()
