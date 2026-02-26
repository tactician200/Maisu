
import os
import logging
import psycopg2
from typing import List, Dict, Optional
from uuid import UUID

logger = logging.getLogger("llm_repository")


class ConversationRepository:
    def __init__(self):
        self.db_host = os.getenv("DB_HOST", "localhost")
        self.db_port = os.getenv("DB_PORT", "5432")
        self.db_name = os.getenv("DB_NAME", "maisu_db")
        self.db_user = os.getenv("DB_USER", "user")
        self.db_password = os.getenv("DB_PASSWORD", "password")
        self.max_content_chars = int(os.getenv("DB_MESSAGE_MAX_CONTENT_CHARS", "8000"))

    def _get_connection(self):
        return psycopg2.connect(
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
            user=self.db_user,
            password=self.db_password
        )

    def get_or_create_conversation(self, platform: str, user_id: str) -> UUID:
        conn = None
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            cur.execute(
                "SELECT id FROM conversations WHERE platform = %s AND user_id = %s",
                (platform, user_id)
            )
            result = cur.fetchone()
            if result:
                return result[0] if isinstance(result[0], UUID) else UUID(str(result[0]))
            else:
                cur.execute(
                    "INSERT INTO conversations (platform, user_id) VALUES (%s, %s) RETURNING id",
                    (platform, user_id)
                )
                raw_id = cur.fetchone()[0]
                conversation_id = raw_id if isinstance(raw_id, UUID) else UUID(str(raw_id))
                conn.commit()
                return conversation_id
        except Exception as e:
            logger.error("Error in get_or_create_conversation: %s", e)
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()

    def add_message(self, conversation_id: UUID, role: str, content: str, embedding: Optional[List[float]] = None):
        self.add_messages(
            conversation_id,
            [{"role": role, "content": content, "embedding": embedding}],
        )

    def _normalize_content(self, content: str) -> str:
        value = (content or "").replace("\x00", "").strip()
        if len(value) > self.max_content_chars:
            logger.warning(
                "Truncating overlong message content for storage",
                extra={"max_chars": self.max_content_chars},
            )
            value = value[: self.max_content_chars]
        return value

    def add_messages(self, conversation_id: UUID, messages: List[Dict]):
        conn = None
        try:
            conn = self._get_connection()
            cur = conn.cursor()

            for msg in messages:
                role = msg["role"]
                content = self._normalize_content(msg.get("content", ""))
                embedding = msg.get("embedding")

                if not content:
                    continue

                if embedding is not None:
                    cur.execute(
                        "INSERT INTO messages (conversation_id, role, content, embedding) VALUES (%s, %s, %s, %s)",
                        (str(conversation_id), role, content, embedding),
                    )
                else:
                    cur.execute(
                        "INSERT INTO messages (conversation_id, role, content) VALUES (%s, %s, %s)",
                        (str(conversation_id), role, content),
                    )

            conn.commit()
        except Exception as e:
            logger.error("Error in add_messages: %s", e)
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()

    def get_conversation_history(self, conversation_id: UUID) -> List[Dict[str, str]]:
        conn = None
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            cur.execute(
                "SELECT role, content FROM messages WHERE conversation_id = %s ORDER BY created_at ASC",
                (str(conversation_id),)
            )
            history = [{"role": row[0], "content": row[1]} for row in cur.fetchall()]
            return history
        except Exception as e:
            logger.error("Error in get_conversation_history: %s", e)
            raise
        finally:
            if conn:
                conn.close()

if __name__ == '__main__':
    # Example Usage (for testing purposes)
    repo = ConversationRepository()
    platform = "test_platform"
    user_id = "test_user_123"

    try:
        conv_id = repo.get_or_create_conversation(platform, user_id)
        print(f"Conversation ID: {conv_id}")

        repo.add_message(conv_id, "user", "Hello there!")
        repo.add_message(conv_id, "assistant", "Hi, how can I help you?")

        history = repo.get_conversation_history(conv_id)
        print("Conversation History:")
        for msg in history:
            print(f"- {msg['role']}: {msg['content']}")

    except Exception as e:
        print(f"An error occurred during example usage: {e}")
