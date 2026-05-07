"""Tests for API key authentication."""

import os

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_no_auth_required():
    resp = client.get("/health")
    assert resp.status_code == 200


def test_ask_works_without_api_key_when_not_configured():
    if "APP_API_KEY" in os.environ:
        del os.environ["APP_API_KEY"]
    resp = client.post("/ask", json={"question": "test"})
    # Should get 400 (no vector store) not 401
    assert resp.status_code == 400


def test_ask_rejects_wrong_api_key_when_configured(monkeypatch):
    monkeypatch.setenv("APP_API_KEY", "correct-key")
    resp = client.post(
        "/ask",
        json={"question": "test"},
        headers={"X-API-Key": "wrong-key"},
    )
    assert resp.status_code == 401


def test_ask_accepts_correct_api_key_when_configured(monkeypatch):
    monkeypatch.setenv("APP_API_KEY", "correct-key")
    resp = client.post(
        "/ask",
        json={"question": "test"},
        headers={"X-API-Key": "correct-key"},
    )
    # Should get 400 (no vector store) not 401
    assert resp.status_code == 400
