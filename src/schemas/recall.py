"""
Recall Schemas (VH-B07)

Pydantic v2 models for batch recall operations with OpenAPI response examples.
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RecallCreate(BaseModel):
    """Request schema for initiating a batch recall."""

    asset_code: str = Field(
        ...,
        description="Stellar asset code of the batch to recall",
        min_length=4,
        max_length=12,
    )
    reason: str = Field(
        ...,
        description="Reason for the recall",
        min_length=10,
        max_length=1000,
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "asset_code": "AMOX500B01",
                "reason": "Routine stability testing revealed chemical degradation beyond acceptable shelf-life tolerances.",
            }
        }
    )


class RecallResponse(BaseModel):
    """Response schema for recall operations."""

    recall_id: UUID = Field(..., description="Unique UUID for this recall operation")
    asset_code: str = Field(..., description="Target asset code recalled")
    status: str = Field(
        ...,
        description="Recall status: initiated, in_progress, completed, failed",
    )
    reason: str = Field(..., description="Reason for the recall")
    transaction_hash: Optional[str] = Field(None, description="Stellar clawback transaction hash")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp of recall event",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "recall_id": "c71a39fd-9f8d-4a1e-8422-5401a75f1bd1",
                "asset_code": "AMOX500B01",
                "status": "initiated",
                "reason": "Routine stability testing revealed chemical degradation beyond acceptable shelf-life tolerances.",
                "transaction_hash": "e9310bc941a54b39174092a83701bf4918491028340192841029384019238401",
                "created_at": "2026-09-10T14:30:00Z",
            }
        }
    )
