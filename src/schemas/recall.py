"""
Recall Schemas

Pydantic models for batch recall operations.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


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


class RecallResponse(BaseModel):
    """Response schema for recall operations."""

    recall_id: UUID
    asset_code: str
    status: str = Field(
        ...,
        description="Recall status: initiated, in_progress, completed, failed",
    )
    reason: str
    transaction_hash: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
