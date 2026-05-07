"""Application configuration loaded from YAML."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml


def _project_root() -> Path:
    """Return the project root (two levels above this file)."""
    return Path(__file__).resolve().parent.parent.parent


def _config_path() -> Path:
    env = os.getenv("CONFIG_PATH")
    if env:
        return Path(env)
    return _project_root() / "config" / "config.yaml"


@dataclass(frozen=True)
class LLMConfig:
    model_name: str = "gpt-4o-mini"
    temperature: float = 0


@dataclass(frozen=True)
class EmbeddingsConfig:
    model: str = "text-embedding-3-small"


@dataclass(frozen=True)
class ChunkingConfig:
    chunk_size: int = 1000
    chunk_overlap: int = 300
    separators: list[str] = field(
        default_factory=lambda: ["\n\n", "\n", "(?<=. )", " ", ""]
    )


@dataclass(frozen=True)
class RetrieverConfig:
    search_type: str = "mmr"
    k: int = 6


@dataclass(frozen=True)
class VectorStoreConfig:
    persist_directory: str = "db"


@dataclass(frozen=True)
class UploadConfig:
    allowed_extensions: list[str] = field(default_factory=lambda: [".pdf"])
    max_file_size_mb: int = 50
    upload_directory: str = "data/uploads"


@dataclass(frozen=True)
class LoggingConfig:
    level: str = "INFO"
    format: str = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"


@dataclass(frozen=True)
class ServerConfig:
    host: str = "0.0.0.0"
    port: int = 8000


@dataclass(frozen=True)
class AppSettings:
    llm: LLMConfig = field(default_factory=LLMConfig)
    embeddings: EmbeddingsConfig = field(default_factory=EmbeddingsConfig)
    chunking: ChunkingConfig = field(default_factory=ChunkingConfig)
    retriever: RetrieverConfig = field(default_factory=RetrieverConfig)
    vector_store: VectorStoreConfig = field(default_factory=VectorStoreConfig)
    upload: UploadConfig = field(default_factory=UploadConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    server: ServerConfig = field(default_factory=ServerConfig)


def load_settings() -> AppSettings:
    """Load settings from config.yaml, falling back to defaults."""
    path = _config_path()
    if not path.exists():
        return AppSettings()

    with open(path) as f:
        raw = yaml.safe_load(f) or {}

    return AppSettings(
        llm=LLMConfig(**raw.get("llm", {})),
        embeddings=EmbeddingsConfig(**raw.get("embeddings", {})),
        chunking=ChunkingConfig(**raw.get("chunking", {})),
        retriever=RetrieverConfig(**raw.get("retriever", {})),
        vector_store=VectorStoreConfig(**raw.get("vector_store", {})),
        upload=UploadConfig(**raw.get("upload", {})),
        logging=LoggingConfig(**raw.get("logging", {})),
        server=ServerConfig(**raw.get("server", {})),
    )


# Singleton instance
settings = load_settings()
