"""ChromaDB vector store management."""

from __future__ import annotations

import os

from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_openai import OpenAIEmbeddings

from app.config import settings
from app.logging_config import get_logger

logger = get_logger(__name__)


def _persist_dir() -> str:
    return settings.vector_store.persist_directory


def create_vector_store(
    chunks: list[Document],
    embeddings: OpenAIEmbeddings,
) -> Chroma:
    """Create and persist a Chroma vector store from document chunks."""
    persist_dir = _persist_dir()
    logger.info("Creating vector store with %d chunks at %s", len(chunks), persist_dir)
    return Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_dir,
    )


def load_vector_store(embeddings: OpenAIEmbeddings) -> Chroma:
    """Load an existing Chroma vector store from disk."""
    persist_dir = _persist_dir()
    logger.info("Loading vector store from %s", persist_dir)
    return Chroma(
        embedding_function=embeddings,
        persist_directory=persist_dir,
    )


def vector_store_exists() -> bool:
    """Check whether a persisted vector store exists."""
    return os.path.isdir(_persist_dir())


def get_retriever(vector_store: Chroma) -> VectorStoreRetriever:
    """Return an MMR-based retriever from the vector store."""
    cfg = settings.retriever
    return vector_store.as_retriever(
        search_type=cfg.search_type,
        search_kwargs={"k": cfg.k},
    )
