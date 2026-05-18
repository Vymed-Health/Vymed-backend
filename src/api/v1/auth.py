"""
Authentication API Routes

Handles manufacturer and distributor authentication.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from src.core.security import verify_api_key

router = APIRouter()


class LoginRequest(BaseModel):
    """Authentication request schema."""
    public_key: str
    signature: str


class LoginResponse(BaseModel):
    """Authentication response schema."""
    access_token: str
    token_type: str = "bearer"
    alias: str | None = None


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Authenticate a manufacturer or distributor using Stellar keypair signature.

    The client signs a challenge with their Stellar secret key,
    and the server verifies the signature against the public key.
    """
    # TODO: Implement Stellar-based challenge-response authentication
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Stellar-based authentication not yet implemented",
    )


@router.get("/me")
async def get_current_user(api_key: str = Depends(verify_api_key)):
    """
    Get the currently authenticated user's details.
    """
    return {
        "authenticated": True,
        "role": "manufacturer",
    }
