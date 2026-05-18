"""
API V1 Router

Aggregates all v1 API route modules.
"""

from fastapi import APIRouter

from src.api.v1.verify import router as verify_router
from src.api.v1.batches import router as batches_router
from src.api.v1.recalls import router as recalls_router
from src.api.v1.auth import router as auth_router

api_router = APIRouter()

api_router.include_router(verify_router, prefix="/verify", tags=["Verification"])
api_router.include_router(batches_router, prefix="/batches", tags=["Batch Management"])
api_router.include_router(recalls_router, prefix="/recalls", tags=["Recalls"])
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
