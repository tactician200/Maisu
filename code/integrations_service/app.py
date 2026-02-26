import os
import re
import json
import time
import asyncio
import logging
import httpx
import pika
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException

# Load environment variables
load_dotenv()

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("integrations_service")
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


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "telegram_messages")
TELEGRAM_WEBHOOK_SECRET = os.getenv("TELEGRAM_WEBHOOK_SECRET", "super_secret_token")  # For validation


@app.on_event("startup")
async def startup_event():
    _log_event("rabbitmq_connecting", host=RABBITMQ_HOST, port=RABBITMQ_PORT)
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT))
        channel = connection.channel()
        channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
        app.state.rabbitmq_connection = connection
        app.state.rabbitmq_channel = channel
        _log_event("rabbitmq_connected", queue=RABBITMQ_QUEUE)
    except pika.exceptions.AMQPConnectionError as e:
        _log_event("rabbitmq_connection_failed", level=logging.WARNING, error=str(e))
        app.state.rabbitmq_connection = None
        app.state.rabbitmq_channel = None


@app.on_event("shutdown")
async def shutdown_event():
    if app.state.rabbitmq_connection:
        _log_event("rabbitmq_closing")
        app.state.rabbitmq_connection.close()


@app.post("/webhooks/telegram")
async def telegram_webhook(request: Request):
    if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != TELEGRAM_WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="Invalid secret token")

    update = await request.json()

    if "message" not in update:
        _log_event("telegram_update_skipped", reason="no_message")
        return {"message": "No message in update, skipping."}

    message = update["message"]
    chat_id = message["chat"]["id"]
    text = message.get("text")
    message_id = message.get("message_id")

    if not text:
        _log_event("telegram_update_skipped", message_id=message_id, chat_id=str(chat_id), reason="no_text")
        return {"message": "No text message found, skipping."}

    message_payload = {
        "platform": "telegram",
        "chat_id": str(chat_id),
        "text": text,
        "message_id": message_id,
    }

    if app.state.rabbitmq_channel:
        try:
            app.state.rabbitmq_channel.basic_publish(
                exchange='',
                routing_key=RABBITMQ_QUEUE,
                body=json.dumps(message_payload),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                ),
            )
            _log_event("telegram_message_published", message_id=message_id, chat_id=str(chat_id), retry_count=0)
        except Exception as e:
            _log_event(
                "telegram_publish_failed",
                level=logging.ERROR,
                message_id=message_id,
                chat_id=str(chat_id),
                error=str(e),
            )
    else:
        _log_event("telegram_publish_skipped", level=logging.WARNING, message_id=message_id, chat_id=str(chat_id), reason="rabbitmq_not_connected")

    return {"message": "Message received and processed."}


TELEGRAM_MAX_MESSAGE_LENGTH = 4096
TELEGRAM_MAX_SEND_RETRIES = 3


def split_telegram_message(text: str, max_length: int = TELEGRAM_MAX_MESSAGE_LENGTH) -> list[str]:
    if text is None:
        return []

    if len(text) <= max_length:
        return [text]

    tokens = re.findall(r"\S+\s*|\s+", text)
    chunks: list[str] = []
    current = ""

    for token in tokens:
        if not token:
            continue

        if len(token) > max_length:
            if current:
                chunks.append(current)
                current = ""

            for i in range(0, len(token), max_length):
                chunks.append(token[i:i + max_length])
            continue

        if len(current) + len(token) <= max_length:
            current += token
        else:
            if current:
                chunks.append(current)
            current = token

    if current:
        chunks.append(current)

    return [chunk for chunk in chunks if chunk]


async def _send_telegram_chunk(client: httpx.AsyncClient, url: str, payload: dict, headers: dict, *, message_id: str | int | None = None, chunk_index: int | None = None) -> tuple[dict | None, int]:
    for attempt in range(1, TELEGRAM_MAX_SEND_RETRIES + 1):
        start = time.perf_counter()
        try:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            latency_ms = round((time.perf_counter() - start) * 1000, 2)
            _log_event(
                "telegram_chunk_sent",
                message_id=message_id,
                chat_id=str(payload.get("chat_id")),
                chunk_index=chunk_index,
                latency_ms=latency_ms,
                retry_count=attempt - 1,
            )
            return response.json(), attempt - 1
        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code
            should_retry = status_code == 429 or 500 <= status_code < 600
            latency_ms = round((time.perf_counter() - start) * 1000, 2)
            _log_event(
                "telegram_chunk_http_error",
                level=logging.WARNING,
                message_id=message_id,
                chat_id=str(payload.get("chat_id")),
                chunk_index=chunk_index,
                latency_ms=latency_ms,
                retry_count=attempt,
                status_code=status_code,
            )

            if should_retry and attempt < TELEGRAM_MAX_SEND_RETRIES:
                await asyncio.sleep(0.5 * attempt)
                continue
            return None, attempt
        except httpx.RequestError as e:
            latency_ms = round((time.perf_counter() - start) * 1000, 2)
            _log_event(
                "telegram_chunk_request_error",
                level=logging.WARNING,
                message_id=message_id,
                chat_id=str(payload.get("chat_id")),
                chunk_index=chunk_index,
                latency_ms=latency_ms,
                retry_count=attempt,
                error=str(e),
            )
            if attempt < TELEGRAM_MAX_SEND_RETRIES:
                await asyncio.sleep(0.5 * attempt)
                continue
            return None, attempt


async def send_telegram_message(chat_id: str, text: str, message_id: str | int | None = None):
    if not TELEGRAM_BOT_TOKEN:
        _log_event("telegram_send_skipped", level=logging.WARNING, message_id=message_id, chat_id=str(chat_id), reason="missing_bot_token")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    headers = {"Content-Type": "application/json"}
    chunks = split_telegram_message(text)

    if not chunks:
        _log_event("telegram_send_skipped", level=logging.WARNING, message_id=message_id, chat_id=str(chat_id), reason="no_chunks")
        return

    responses = []
    async with httpx.AsyncClient() as client:
        for index, chunk in enumerate(chunks, start=1):
            payload = {
                "chat_id": chat_id,
                "text": chunk,
            }

            result, retry_count = await _send_telegram_chunk(
                client,
                url,
                payload,
                headers,
                message_id=message_id,
                chunk_index=index,
            )
            if result is None:
                _log_event(
                    "telegram_chunk_failed",
                    level=logging.ERROR,
                    message_id=message_id,
                    chat_id=str(chat_id),
                    chunk_index=index,
                    retry_count=retry_count,
                )
                return None

            responses.append(result)

    return responses[-1] if responses else None


@app.post("/reply")
async def receive_llm_reply(reply_data: dict):
    platform = reply_data.get("platform")
    chat_id = reply_data.get("chat_id")
    text = reply_data.get("reply")
    message_id = reply_data.get("message_id")

    if platform == "telegram" and chat_id and text:
        _log_event("llm_reply_received", message_id=message_id, chat_id=str(chat_id))
        await send_telegram_message(chat_id, text, message_id=message_id)
        return {"message": "Reply sent to Telegram."}
    raise HTTPException(status_code=400, detail="Invalid reply data")


@app.get("/")
async def health_check():
    return {"status": "ok"}
