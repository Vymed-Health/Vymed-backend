"""
Security & Rate Limiting Module

Handles API key authentication and Redis-based scan throttling.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from src.core.config import settings

# API Key header extraction
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str = Depends(api_key_header)) -> str:
    """
    Verify the API key from the request header.
    In development, allows requests without API key.
    """
    if settings.ENVIRONMENT == "development" and not api_key:
        return "dev-mode"

    if not api_key or api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )

    return api_key
