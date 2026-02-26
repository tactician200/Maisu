import unittest
from unittest.mock import AsyncMock, Mock, patch

from app import TELEGRAM_MAX_MESSAGE_LENGTH, send_telegram_message, split_telegram_message


class SplitTelegramMessageTests(unittest.TestCase):
    def test_short_message_not_split(self):
        text = "hello world"
        chunks = split_telegram_message(text)
        self.assertEqual(chunks, [text])

    def test_long_message_splits_and_reconstructs(self):
        text = ("word " * 1200).strip()
        chunks = split_telegram_message(text)

        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(len(chunk) <= TELEGRAM_MAX_MESSAGE_LENGTH for chunk in chunks))
        self.assertEqual("".join(chunks), text)

    def test_single_overlong_word_is_hard_split(self):
        text = "x" * (TELEGRAM_MAX_MESSAGE_LENGTH + 10)
        chunks = split_telegram_message(text)

        self.assertEqual(len(chunks), 2)
        self.assertEqual(len(chunks[0]), TELEGRAM_MAX_MESSAGE_LENGTH)
        self.assertEqual("".join(chunks), text)


class SendTelegramMessageTests(unittest.IsolatedAsyncioTestCase):
    @patch("app.TELEGRAM_BOT_TOKEN", "token")
    @patch("app.httpx.AsyncClient")
    async def test_send_long_message_in_order(self, mock_client_cls):
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None

        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {"ok": True}
        mock_client.post = AsyncMock(return_value=response)
        mock_client_cls.return_value = mock_client

        text = ("hello " * 1000).strip()
        chunks = split_telegram_message(text)

        await send_telegram_message("123", text)

        self.assertEqual(mock_client.post.await_count, len(chunks))
        sent_texts = [call.kwargs["json"]["text"] for call in mock_client.post.await_args_list]
        self.assertEqual(sent_texts, chunks)


if __name__ == "__main__":
    unittest.main()
