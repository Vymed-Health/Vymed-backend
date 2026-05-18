"""
Verification API Routes

Handles medication unit verification requests.
Patients scan GS1 DataMatrix codes and the system verifies provenance on-chain.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from src.schemas.verify import VerifyRequest, VerifyResponse
from src.services.stellar_service import StellarService
from src.services.rate_limiter import RateLimiter
from src.core.security import verify_api_key

router = APIRouter()


@router.post("", response_model=VerifyResponse)
async def verify_medication(
    request: VerifyRequest,
    api_key: str = Depends(verify_api_key),
):
    """
    Verify a medication unit by its GS1 DataMatrix Unit ID.

    This endpoint:
    1. Checks Redis rate limit for the unit_id + device_id combination
    2. Constructs a Stellar transaction to verify provenance
    3. Signs it with the Manufacturer's Fee Bump key
    4. Submits to the Stellar network
    5. Returns the verification result

    Rate Limit: Max 3 scans per 10 minutes per unique bottle.
    """
    # Initialize services
    rate_limiter = RateLimiter()
    stellar_service = StellarService()

    # Check rate limit
    is_throttled, scan_count = await rate_limiter.check_rate_limit(
        unit_id=request.unit_id,
        device_id=request.device_id,
    )

    if is_throttled:
        return VerifyResponse(
            status="warning",
            message="Scan limit reached. Security warning triggered.",
            scan_count=scan_count,
        )

    # Verify on Stellar blockchain
    try:
        result = await stellar_service.verify_unit(
            unit_id=request.unit_id,
        )

        # Increment rate limit counter
        await rate_limiter.increment_scan_count(
            unit_id=request.unit_id,
            device_id=request.device_id,
        )

        return VerifyResponse(
            status=result["status"],
            message=result["message"],
            batch_id=result.get("batch_id"),
            manufacturer=result.get("manufacturer"),
            handoffs=result.get("handoffs"),
            expiry_date=result.get("expiry_date"),
            transaction_hash=result.get("transaction_hash"),
            scan_count=scan_count + 1,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Verification failed: {str(e)}",
        )


@router.get("/{unit_id}", response_model=VerifyResponse)
async def get_verification_history(
    unit_id: str,
    api_key: str = Depends(verify_api_key),
):
    """
    Get verification history for a specific unit.
    """
    stellar_service = StellarService()
    history = await stellar_service.get_unit_history(unit_id=unit_id)

    return VerifyResponse(
        status=history.get("status", "unknown"),
        message=history.get("message", "No verification history found"),
        batch_id=history.get("batch_id"),
        handoffs=history.get("handoffs"),
        transaction_hash=history.get("transaction_hash"),
    )
