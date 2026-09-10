"""
Verification Schemas (VH-B07)

Pydantic v2 models for medication verification request/response data with OpenAPI examples.
"""

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class VerifyRequest(BaseModel):
    """Request schema for medication verification."""

    unit_id: str = Field(
        ...,
        description="GS1 DataMatrix Unit ID or full barcode payload from scanned medication",
        min_length=1,
        max_length=256,
    )
    device_id: str = Field(
        ...,
        description="Unique device identifier for rate limiting",
        min_length=1,
        max_length=64,
    )
    latitude: Optional[float] = Field(
        None,
        description="GPS latitude coordinate where scan was performed (for counterfeit anomaly detection)",
        ge=-90.0,
        le=90.0,
    )
    longitude: Optional[float] = Field(
        None,
        description="GPS longitude coordinate where scan was performed",
        ge=-180.0,
        le=180.0,
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "unit_id": "(01)00301234567896(21)SER982341(17)281231(10)LOT7732",
                "device_id": "clinic-scanner-mobile-04",
                "latitude": 6.5244,
                "longitude": 3.3792,
            }
        }
    )


class VerifyResponse(BaseModel):
    """Response schema for medication verification result."""

    status: str = Field(
        ...,
        description="Verification status: verified, warning, recalled, counterfeit, or expired",
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
        description="Stellar transaction hash for on-chain proof (sponsored via Fee-Bump)",
    )
    cryptographic_hash: Optional[str] = Field(
        None,
        description="GS1 canonical SHA-256 hash verified against smart contract registry",
    )
    scan_count: Optional[int] = Field(
        None,
        description="Number of scans for this unit in the current rate limiting window",
    )
    is_anomaly: Optional[bool] = Field(
        default=False,
        description="True if geographic speed/proximity counterfeit anomaly was triggered",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Verification timestamp",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "verified",
                "message": "Medication verified as authentic on Stellar blockchain",
                "batch_id": "AMOX500B01",
                "manufacturer": "Novartis Global Pharmaceuticals",
                "handoffs": 3,
                "expiry_date": "2028-12-31",
                "transaction_hash": "6f9b2d3c5e8a1f4b7a9c0d2e4f6a8b0c2d4e6f8a0b2c4d6e8f0a2b4c6d8e0f2a",
                "cryptographic_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "scan_count": 1,
                "is_anomaly": False,
                "timestamp": "2026-09-10T15:00:00Z",
            }
        }
    )
