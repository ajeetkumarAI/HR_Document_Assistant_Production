"""Document chunking for embedding."""

from __future__ import annotations

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import settings
from app.logging_config import get_logger

logger = get_logger(__name__)


def chunk_documents(docs: list[Document]) -> list[Document]:
    """Split documents into smaller chunks for embedding."""
    cfg = settings.chunking
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=cfg.chunk_size,
        chunk_overlap=cfg.chunk_overlap,
        separators=cfg.separators,
    )
    chunks = text_splitter.split_documents(docs)
    logger.info("Split %d pages into %d chunks", len(docs), len(chunks))
    return chunks
