"""
Batch Schemas (VH-B07)

Pydantic v2 models for batch management data with comprehensive OpenAPI examples.
"""

from datetime import date, datetime
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


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

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "asset_code": "AMOX500B01",
                "manufacturer_name": "Novartis Global Pharmaceuticals",
                "total_units": 50000,
                "expiry_date": "2028-12-31",
            }
        }
    )


class BatchResponse(BaseModel):
    """Response schema for batch details."""

    batch_id: UUID = Field(..., description="Unique UUID identifier for the batch record")
    asset_code: str = Field(..., description="Stellar asset code")
    manufacturer_name: str = Field(..., description="Registered manufacturer name")
    total_units: int = Field(..., description="Total unit count")
    expiry_date: date = Field(..., description="Expiry date of batch")
    transaction_hash: Optional[str] = Field(None, description="Stellar on-chain transaction hash")
    created_at: datetime = Field(..., description="UTC creation timestamp")
    status: str = Field(default="active", description="Status: active, recalled, completed")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "batch_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
                "asset_code": "AMOX500B01",
                "manufacturer_name": "Novartis Global Pharmaceuticals",
                "total_units": 50000,
                "expiry_date": "2028-12-31",
                "transaction_hash": "a4f89d10e5bc5312384913210452391038592384910238401923841029384012",
                "created_at": "2026-09-10T12:00:00Z",
                "status": "active",
            }
        }
    )


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

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "parent_id": "CARTON-AMOX-2026-001",
                "child_ids": [
                    "BOTTLE-AMOX-2026-001-A",
                    "BOTTLE-AMOX-2026-001-B",
                    "BOTTLE-AMOX-2026-001-C",
                ],
            }
        }
    )
