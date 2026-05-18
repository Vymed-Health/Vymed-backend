"""
Vymed Backend — FastAPI Application Entry Point

Pharmaceutical provenance platform built on the Stellar Blockchain.
Provides zero-cost verification through manufacturer-sponsored Fee Bump transactions.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.core.database import engine, create_tables
from src.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan handler.
    Handles startup and shutdown events.
    """
    # Startup
    print(f"Starting Vymed API — Environment: {settings.ENVIRONMENT}")
    print(f"Stellar Network: {settings.STELLAR_NETWORK}")
    await create_tables()

    yield

    # Shutdown
    print("Shutting down Vymed API...")
    await engine.dispose()


app = FastAPI(
    title="Vymed API",
    description="Pharmaceutical Provenance on the Stellar Blockchain",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Router
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "0.1.0",
        "environment": settings.ENVIRONMENT,
        "stellar_network": settings.STELLAR_NETWORK,
    }
