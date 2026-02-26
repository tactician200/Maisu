import os
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("llm_config")


class Config:
    LLM_PROVIDER_PRIMARY = os.getenv("LLM_PROVIDER_PRIMARY", "gemini")
    LLM_PROVIDER_FALLBACK = os.getenv("LLM_PROVIDER_FALLBACK", "openai")

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # Load System Prompt from file
    # Path is relative to this file: ../../config/system_prompt.md
    _base_dir = os.path.dirname(os.path.abspath(__file__))
    _prompt_path = os.path.join(_base_dir, "../../config/system_prompt.md")
    
    try:
        with open(_prompt_path, "r", encoding="utf-8") as f:
            SYSTEM_PROMPT = f.read().strip()
            logger.info("System prompt loaded from file")
    except FileNotFoundError:
        logger.warning("System prompt file not found; using fallback")
        SYSTEM_PROMPT = os.getenv(
            "LLM_SYSTEM_PROMPT",
            "You are MAISU, an intelligent assistant. Keep a warm, clear, concise tone and stay in-character as MAISU.",
        )
