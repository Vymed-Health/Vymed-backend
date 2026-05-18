"""
Batch Schemas

Pydantic models for batch management data.
"""

from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class BatchCreate(BaseModel):
    """Request schema for creating a new drug batch."""

    asset_code: str = Field(
        ...,
        description="Stellar asset code for the batch (4-12 alphanumeric characters)",
        min_length=4,
        max_length=12,
        pattern=r"^[A-Z0-9]+$",
    )
    manufacturer_name: str = Field(
        ...,
        description="Name of the manufacturer",
        min_length=1,
        max_length=256,
    )
    total_units: int = Field(
        ...,
        description="Total number of units in this batch",
        gt=0,
        le=1_000_000,
    )
    expiry_date: date = Field(
        ...,
        description="Batch expiry date",
    )


class BatchResponse(BaseModel):
    """Response schema for batch details."""

    batch_id: UUID
    asset_code: str
    manufacturer_name: str
    total_units: int
    expiry_date: date
    transaction_hash: Optional[str] = None
    created_at: datetime
    status: str = "active"


class ParentChildMapRequest(BaseModel):
    """Request schema for mapping parent-child relationships."""

    parent_id: str = Field(
        ...,
        description="Parent unit ID (e.g., carton QR code)",
    )
    child_ids: List[str] = Field(
        ...,
        description="List of child unit IDs (e.g., individual bottle codes)",
        min_length=1,
        max_length=1000,
    )
