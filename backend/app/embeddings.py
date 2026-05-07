"""OpenAI embedding model."""

from __future__ import annotations

from langchain_openai import OpenAIEmbeddings

from app.config import settings
from app.logging_config import get_logger

logger = get_logger(__name__)


def get_embedding_model() -> OpenAIEmbeddings:
    """Return an OpenAI embedding model instance.

    The API key is read automatically from the OPENAI_API_KEY
    environment variable by the LangChain client.
    """
    logger.debug("Initialising embedding model: %s", settings.embeddings.model)
    return OpenAIEmbeddings(model=settings.embeddings.model)
