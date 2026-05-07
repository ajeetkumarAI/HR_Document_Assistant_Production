"""Pydantic request/response models."""

from __future__ import annotations

from pydantic import BaseModel, Field


class IngestRequest(BaseModel):
    file_path: str = Field(..., description="Path to the uploaded PDF on the server")


class IngestResponse(BaseModel):
    status: str
    message: str
    num_chunks: int = 0


class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=1, description="The question to ask")


class SourceDoc(BaseModel):
    page: int | str = "N/A"
    snippet: str = ""


class QuestionResponse(BaseModel):
    answer: str
    sources: list[SourceDoc] = []


class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str = "1.0.0"
    vector_store_ready: bool = False


class UploadResponse(BaseModel):
    status: str
    filename: str
    file_path: str
