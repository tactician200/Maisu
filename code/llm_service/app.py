import os
import json
import asyncio
import logging
import threading
import time

import httpx
import pika
from fastapi import FastAPI
from dotenv import load_dotenv

# Absolute imports (assuming running from llm_service root)
from manager import LLMManager
from providers.base import Message as LLMMessage
from repository import ConversationRepository
from history_utils import normalize_history_role

load_dotenv()

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("llm_service")
SENSITIVE_KEYS = {"token", "authorization", "password", "secret", "api_key"}


def _sanitize_fields(fields: dict) -> dict:
    sanitized = {}
    for key, value in fields.items():
        key_lower = str(key).lower()
        if any(secret_key in key_lower for secret_key in SENSITIVE_KEYS):
            sanitized[key] = "[REDACTED]"
        else:
            sanitized[key] = value
    return sanitized


def _log_event(event: str, level: int = logging.INFO, **fields):
    payload = {"event": event, **_sanitize_fields(fields)}
    logger.log(level, json.dumps(payload, ensure_ascii=False))


# Config
INTEGRATIONS_SERVICE_URL = os.getenv("INTEGRATIONS_SERVICE_URL", "http://localhost:8000")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "telegram_messages")

conversation_repo = ConversationRepository()


def run_consumer():
    _log_event("consumer_starting", rabbitmq_host=RABBITMQ_HOST, rabbitmq_port=RABBITMQ_PORT)

    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=RABBITMQ_HOST,
                    port=RABBITMQ_PORT,
                    heartbeat=600,
                    blocked_connection_timeout=300,
                )
            )
            channel = connection.channel()
            channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(
                queue=RABBITMQ_QUEUE,
                on_message_callback=process_message_wrapper,
                auto_ack=False,
            )

            _log_event("consumer_connected", queue=RABBITMQ_QUEUE)
            channel.start_consuming()

        except pika.exceptions.AMQPConnectionError as e:
            _log_event("consumer_connection_error", level=logging.WARNING, error=str(e))
            time.sleep(5)
        except Exception as e:
            _log_event("consumer_unexpected_error", level=logging.ERROR, error=str(e))
            time.sleep(5)


def process_message_wrapper(ch, method, properties, body):
    message_id = None
    chat_id = None
    try:
        try:
            parsed_body = json.loads(body.decode("utf-8"))
            message_id = parsed_body.get("message_id")
            chat_id = parsed_body.get("chat_id")
        except Exception:
            pass

        asyncio.run(process_message_async(ch, method, properties, body))
    except Exception as e:
        _log_event("message_wrapper_error", level=logging.ERROR, message_id=message_id, chat_id=chat_id, error=str(e))
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


async def process_message_async(ch, method, properties, body):
    process_start = time.perf_counter()
    message_id = None
    chat_id = None
    try:
        body_str = body.decode("utf-8")
        payload = json.loads(body_str)
        platform = payload.get("platform")
        chat_id = payload.get("chat_id")
        text = (payload.get("text") or payload.get("message") or "").strip()
        message_id = payload.get("message_id")

        _log_event("message_received", message_id=message_id, chat_id=chat_id, chunk_index=1, retry_count=0)

        if not text:
            _log_event("message_skipped", level=logging.WARNING, message_id=message_id, chat_id=chat_id, reason="empty_text")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        conv_id = conversation_repo.get_or_create_conversation(platform, str(chat_id))
        history_dicts = conversation_repo.get_conversation_history(conv_id)
        llm_history = [
            LLMMessage(role=normalize_history_role(msg.get("role", "user")), content=msg["content"])
            for msg in history_dicts
        ]

        # Persist user turn before generation so failures still keep a complete interaction trail.
        conversation_repo.add_message(conv_id, "user", text)

        llm_manager = LLMManager()
        llm_start = time.perf_counter()
        response_text = await llm_manager.generate_response(
            text,
            llm_history,
            telemetry={"message_id": message_id, "chat_id": str(chat_id), "chunk_index": 1},
        )
        llm_latency_ms = round((time.perf_counter() - llm_start) * 1000, 2)
        _log_event("llm_response_generated", message_id=message_id, chat_id=chat_id, chunk_index=1, latency_ms=llm_latency_ms, retry_count=0)

        conversation_repo.add_message(conv_id, "assistant", response_text)

        await send_reply_http(platform, chat_id, response_text, message_id=message_id)

        total_latency_ms = round((time.perf_counter() - process_start) * 1000, 2)
        _log_event("message_processed", message_id=message_id, chat_id=chat_id, chunk_index=1, latency_ms=total_latency_ms, retry_count=0)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        total_latency_ms = round((time.perf_counter() - process_start) * 1000, 2)
        _log_event(
            "message_processing_error",
            level=logging.ERROR,
            message_id=message_id,
            chat_id=chat_id,
            chunk_index=1,
            latency_ms=total_latency_ms,
            retry_count=0,
            error=str(e),
        )
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


async def send_reply_http(platform, chat_id, text, *, message_id=None):
    url = f"{INTEGRATIONS_SERVICE_URL}/reply"
    payload = {"platform": platform, "chat_id": chat_id, "reply": text, "message_id": message_id}
    start = time.perf_counter()
    async with httpx.AsyncClient() as client:
        try:
            await client.post(url, json=payload, timeout=10.0)
            latency_ms = round((time.perf_counter() - start) * 1000, 2)
            _log_event("reply_forwarded", message_id=message_id, chat_id=chat_id, chunk_index=1, latency_ms=latency_ms, retry_count=0)
        except Exception as e:
            latency_ms = round((time.perf_counter() - start) * 1000, 2)
            _log_event(
                "reply_forward_failed",
                level=logging.WARNING,
                message_id=message_id,
                chat_id=chat_id,
                chunk_index=1,
                latency_ms=latency_ms,
                retry_count=0,
                error=str(e),
            )


@app.on_event("startup")
async def startup_event():
    t = threading.Thread(target=run_consumer, daemon=True)
    t.start()
    _log_event("consumer_thread_started")


@app.get("/")
def health():
    return {"status": "ok", "service": "llm_service"}
