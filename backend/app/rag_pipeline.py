"""RAG pipeline: indexing and question-answering orchestration."""

from __future__ import annotations

from app.chunking import chunk_documents
from app.document_loaders import load_documents
from app.embeddings import get_embedding_model
from app.llm import get_llm
from app.logging_config import get_logger
from app.models import SourceDoc
from app.prompts import build_prompt
from app.vectorstore import (
    create_vector_store,
    get_retriever,
    load_vector_store,
    vector_store_exists,
)

logger = get_logger(__name__)


def indexing_pipeline(file_path: str) -> int:
    """Load a PDF, chunk it, embed it, and store in a vector database.

    Returns the number of chunks created.
    """
    logger.info("Starting indexing pipeline for %s", file_path)
    documents = load_documents(file_path)
    chunks = chunk_documents(documents)
    embedding_model = get_embedding_model()
    create_vector_store(chunks, embedding_model)
    logger.info("Indexing complete: %d chunks stored", len(chunks))
    return len(chunks)


def get_answer(question: str) -> tuple[str, list[SourceDoc]]:
    """Retrieve relevant context and return an LLM-generated answer.

    Returns (answer_text, list_of_source_docs).
    Raises FileNotFoundError if no documents have been ingested.
    """
    if not vector_store_exists():
        raise FileNotFoundError(
            "No documents have been ingested yet. "
            "Please upload and process a document first."
        )

    logger.info("Answering question: %.80s...", question)

    embedding_model = get_embedding_model()
    vs = load_vector_store(embedding_model)
    retriever = get_retriever(vs)

    relevant_docs = retriever.invoke(question)
    context = "\n\n".join(
        f"(Page {doc.metadata.get('page', 'N/A')}) {doc.page_content}"
        for doc in relevant_docs
    )

    sources = [
        SourceDoc(
            page=doc.metadata.get("page", "N/A"),
            snippet=doc.page_content[:200],
        )
        for doc in relevant_docs
    ]

    prompt = build_prompt(context, question)
    llm = get_llm()
    response = llm.invoke(prompt)
    logger.info("Answer generated successfully")

    return response.content, sources
