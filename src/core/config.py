"""
Application Configuration

Uses pydantic-settings to load environment variables with validation.
"""

from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Supports .env file for local development.
    """

    # App
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: List[str] = ["*"]

    # Stellar Configuration
    STELLAR_NETWORK: str = "TESTNET"
    STELLAR_HORIZON_URL: str = "https://horizon-testnet.stellar.org"
    MANUFACTURER_SECRET_KEY: str = ""
    MANUFACTURER_PUBLIC_KEY: str = ""

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/vymed"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security
    RATE_LIMIT_MAX_SCANS: int = 3
    RATE_LIMIT_WINDOW_SECONDS: int = 600
    API_KEY: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
