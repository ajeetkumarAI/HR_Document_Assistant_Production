"""Tests for configuration loading."""

from app.config import AppSettings, load_settings


def test_load_settings_returns_defaults():
    settings = load_settings()
    assert isinstance(settings, AppSettings)
    assert settings.llm.model_name == "gpt-4o-mini"
    assert settings.llm.temperature == 0
    assert settings.embeddings.model == "text-embedding-3-small"
    assert settings.chunking.chunk_size == 1000
    assert settings.chunking.chunk_overlap == 300
    assert settings.retriever.search_type == "mmr"
    assert settings.retriever.k == 6
    assert settings.vector_store.persist_directory == "db"


def test_upload_config_defaults():
    settings = load_settings()
    assert ".pdf" in settings.upload.allowed_extensions
    assert settings.upload.max_file_size_mb == 50
