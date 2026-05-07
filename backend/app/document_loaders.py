"""PDF document loading."""

from __future__ import annotations

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents import Document

from app.logging_config import get_logger

logger = get_logger(__name__)


def load_documents(file_path: str) -> list[Document]:
    """Load pages from a PDF file and return them as LangChain Documents."""
    logger.info("Loading PDF: %s", file_path)
    loader = PyMuPDFLoader(file_path)
    docs = loader.load()
    logger.info("Loaded %d pages from %s", len(docs), file_path)
    return docs
