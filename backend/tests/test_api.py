"""Tests for FastAPI endpoints."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert "vector_store_ready" in data
    assert "version" in data


def test_ask_without_vector_store():
    resp = client.post("/ask", json={"question": "What is the leave policy?"})
    assert resp.status_code == 400
    assert "No documents have been ingested" in resp.json()["detail"]


def test_ask_empty_question():
    resp = client.post("/ask", json={"question": ""})
    assert resp.status_code == 422


def test_upload_non_pdf():
    resp = client.post(
        "/upload",
        files={"file": ("test.txt", b"hello", "text/plain")},
    )
    assert resp.status_code == 400
    assert "not allowed" in resp.json()["detail"]


def test_ingest_nonexistent_file():
    resp = client.post("/ingest", params={"file_path": "/nonexistent/file.pdf"})
    assert resp.status_code == 404
