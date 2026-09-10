"""
Common API Schemas & Error Models (VH-B07)

Standardized error schemas with OpenAPI examples for robust client integration.
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field


class ErrorResponse(BaseModel):
    """Standard error response model for API endpoints."""

    error: str = Field(..., description="Error classification code")
    message: str = Field(..., description="Human-readable error details")
    details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Detailed contextual debug or validation data",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "error": "NOT_FOUND",
                    "message": "The requested batch or unit was not found",
                    "details": {"resource_id": "BATCH-001"},
                },
                {
                    "error": "RATE_LIMIT_EXCEEDED",
                    "message": "Too many requests. Token bucket limit reached.",
                    "details": {"retry_after_seconds": 10},
                },
            ]
        }
    )
