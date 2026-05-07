"""FastAPI application entry point."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.auth import require_api_key
from app.config import settings
from app.logging_config import get_logger, setup_logging
from app.models import (
    HealthResponse,
    IngestResponse,
    QuestionRequest,
    QuestionResponse,
    UploadResponse,
)
from app.rag_pipeline import get_answer, indexing_pipeline
from app.vectorstore import vector_store_exists

load_dotenv()
setup_logging()
logger = get_logger(__name__)

app = FastAPI(
    title="HR Document Assistant API",
    version="1.0.0",
    description="Production-ready RAG API for HR policy document Q&A",
)

# CORS — allow all origins in dev; restrict in production via env var
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health ───────────────────────────────────────────────────────────
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    """Return service health and readiness status."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        vector_store_ready=vector_store_exists(),
    )


# ── Upload ───────────────────────────────────────────────────────────
@app.post(
    "/upload",
    response_model=UploadResponse,
    tags=["Documents"],
    dependencies=[require_api_key],
)
async def upload_document(file: UploadFile = File(...)) -> UploadResponse:
    """Upload a PDF document for later ingestion."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    ext = Path(file.filename).suffix.lower()
    if ext not in settings.upload.allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{ext}' not allowed. Allowed: {settings.upload.allowed_extensions}",
        )

    safe_name = Path(file.filename).name
    upload_dir = Path(settings.upload.upload_directory)
    upload_dir.mkdir(parents=True, exist_ok=True)
    dest = upload_dir / safe_name

    logger.info("Saving uploaded file to %s", dest)
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)

    return UploadResponse(
        status="uploaded",
        filename=safe_name,
        file_path=str(dest),
    )


# ── Ingest ───────────────────────────────────────────────────────────
@app.post(
    "/ingest",
    response_model=IngestResponse,
    tags=["Documents"],
    dependencies=[require_api_key],
)
async def ingest_document(file_path: str) -> IngestResponse:
    """Index an uploaded PDF into the vector store."""
    if not Path(file_path).exists():
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")

    try:
        num_chunks = indexing_pipeline(file_path)
    except Exception as exc:
        logger.exception("Ingestion failed for %s", file_path)
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return IngestResponse(
        status="success",
        message=f"Document indexed successfully ({num_chunks} chunks)",
        num_chunks=num_chunks,
    )


# ── Ask ──────────────────────────────────────────────────────────────
@app.post(
    "/ask",
    response_model=QuestionResponse,
    tags=["Q&A"],
    dependencies=[require_api_key],
)
async def ask_question(body: QuestionRequest) -> QuestionResponse:
    """Ask a question about the ingested HR policy documents."""
    try:
        answer, sources = get_answer(body.question)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Error answering question")
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return QuestionResponse(answer=answer, sources=sources)
