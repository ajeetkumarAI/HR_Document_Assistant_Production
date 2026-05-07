"""Tests for Pydantic models."""

import pytest
from pydantic import ValidationError

from app.models import (
    HealthResponse,
    IngestResponse,
    QuestionRequest,
    QuestionResponse,
    SourceDoc,
    UploadResponse,
)


def test_question_request_requires_question():
    with pytest.raises(ValidationError):
        QuestionRequest(question="")


def test_question_request_valid():
    req = QuestionRequest(question="What is the leave policy?")
    assert req.question == "What is the leave policy?"


def test_question_response_with_sources():
    resp = QuestionResponse(
        answer="The leave policy allows 20 days.",
        sources=[SourceDoc(page=3, snippet="Annual leave is 20 days...")],
    )
    assert resp.answer == "The leave policy allows 20 days."
    assert len(resp.sources) == 1
    assert resp.sources[0].page == 3


def test_health_response_defaults():
    resp = HealthResponse()
    assert resp.status == "healthy"
    assert resp.vector_store_ready is False


def test_ingest_response():
    resp = IngestResponse(status="success", message="Done", num_chunks=42)
    assert resp.num_chunks == 42


def test_upload_response():
    resp = UploadResponse(
        status="uploaded", filename="test.pdf", file_path="data/uploads/test.pdf"
    )
    assert resp.filename == "test.pdf"
