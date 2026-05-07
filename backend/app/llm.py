"""ChatOpenAI LLM wrapper."""

from __future__ import annotations

from langchain_openai import ChatOpenAI

from app.config import settings
from app.logging_config import get_logger

logger = get_logger(__name__)


def get_llm() -> ChatOpenAI:
    """Return a ChatOpenAI LLM instance.

    The API key is read automatically from the OPENAI_API_KEY
    environment variable by the LangChain client.
    """
    cfg = settings.llm
    logger.debug("Initialising LLM: %s (temp=%s)", cfg.model_name, cfg.temperature)
    return ChatOpenAI(model_name=cfg.model_name, temperature=cfg.temperature)
