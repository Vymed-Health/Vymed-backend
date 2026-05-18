"""
Verification Schemas

Pydantic models for verification request/response data.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class VerifyRequest(BaseModel):
    """Request schema for medication verification."""

    unit_id: str = Field(
        ...,
        description="GS1 DataMatrix Unit ID from the scanned medication",
        min_length=1,
        max_length=128,
    )
    device_id: str = Field(
        ...,
        description="Unique device identifier for rate limiting",
        min_length=1,
        max_length=64,
    )


class VerifyResponse(BaseModel):
    """Response schema for medication verification result."""

    status: str = Field(
        ...,
        description="Verification status: verified, warning, recalled, or counterfeit",
    )
    message: str = Field(
        ...,
        description="Human-readable verification message",
    )
    batch_id: Optional[str] = Field(
        None,
        description="Batch identifier if found",
    )
    manufacturer: Optional[str] = Field(
        None,
        description="Manufacturer name if verified",
    )
    handoffs: Optional[int] = Field(
        None,
        description="Number of supply chain handoffs",
    )
    expiry_date: Optional[str] = Field(
        None,
        description="Medication expiry date",
    )
    transaction_hash: Optional[str] = Field(
        None,
        description="Stellar transaction hash for on-chain proof",
    )
    scan_count: Optional[int] = Field(
        None,
        description="Number of scans for this unit in the current window",
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Verification timestamp",
    )
