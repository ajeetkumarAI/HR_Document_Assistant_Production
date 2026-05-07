"""API key authentication middleware."""

from __future__ import annotations

import os

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


def _get_api_key() -> str | None:
    """Read the expected API key from the environment."""
    return os.getenv("APP_API_KEY")


async def verify_api_key(
    api_key: str | None = Security(API_KEY_HEADER),
) -> str:
    """Validate the request API key against the configured key.

    If APP_API_KEY is not set, authentication is disabled (development mode).
    """
    expected = _get_api_key()
    if expected is None:
        return "dev-mode"
    if api_key is None or api_key != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
    return api_key


# Reusable dependency
require_api_key = Depends(verify_api_key)
