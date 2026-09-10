"""
Verification API Routes (VH-B01, VH-B02, VH-B05, VH-B06, VH-B07)

Handles medication unit verification requests:
- GS1 DataMatrix parsing and cryptographic SHA-256 validation.
- Token-bucket and scan rate-limiting.
- Geographic counterfeit anomaly detection with webhook alerting.
- Zero-cost verification transactions via sponsored Fee-Bumps.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from src.schemas.common import ErrorResponse
from src.schemas.verify import VerifyRequest, VerifyResponse
from src.services.anomaly_detector import GeographicAnomalyDetector
from src.services.gs1_service import GS1ParserService
from src.services.rate_limiter import RateLimiter, verify_rate_limit_dependency
from src.services.stellar_service import StellarService
from src.core.security import verify_api_key

router = APIRouter()
anomaly_detector = GeographicAnomalyDetector()


@router.post(
    "",
    response_model=VerifyResponse,
    dependencies=[Depends(verify_rate_limit_dependency)],
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request or Invalid Barcode"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def verify_medication(
    request: VerifyRequest,
    api_key: str = Depends(verify_api_key),
):
    """
    Verify a medication unit by its GS1 DataMatrix Unit ID.

    Features:
    1. Checks token-bucket and Redis rate limit for unit_id + device_id.
    2. Parses GS1 Application Identifiers (GTIN, Serial, Expiration, Batch).
    3. Analyzes scan coordinates for geographic counterfeit anomalies.
    4. Constructs and submits verification transaction with Stellar Fee Bump sponsorship.
    """
    rate_limiter = RateLimiter()
    stellar_service = StellarService()

    # Check scan rate limit
    is_throttled, scan_count = await rate_limiter.check_rate_limit(
        unit_id=request.unit_id,
        device_id=request.device_id,
    )

    if is_throttled:
        return VerifyResponse(
            status="warning",
            message="Scan limit reached. Security warning triggered for excessive scans.",
            scan_count=scan_count,
        )

    # Parse GS1 Barcode
    gs1_result = GS1ParserService.parse_barcode(request.unit_id)
    batch_identifier = gs1_result.batch_number or gs1_result.gtin or request.unit_id

    # Check geographic anomalies if coordinates provided
    is_anomaly = False
    if request.latitude is not None and request.longitude is not None:
        anomaly_eval = await anomaly_detector.record_and_evaluate_scan(
            unit_id=request.unit_id,
            latitude=request.latitude,
            longitude=request.longitude,
        )
        is_anomaly = anomaly_eval["is_anomaly"]

    # If barcode explicitly expired
    if gs1_result.is_expired:
        return VerifyResponse(
            status="expired",
            message=f"Medication expired on {gs1_result.expiry_date.isoformat() if gs1_result.expiry_date else 'recorded date'}. Do not dispense.",
            batch_id=batch_identifier,
            expiry_date=gs1_result.expiry_date.isoformat() if gs1_result.expiry_date else None,
            cryptographic_hash=gs1_result.cryptographic_hash,
            scan_count=scan_count + 1,
            is_anomaly=is_anomaly,
        )

    # Verify on Stellar blockchain
    try:
        result = await stellar_service.verify_unit(
            unit_id=request.unit_id,
        )

        # Increment scan counter
        await rate_limiter.increment_scan_count(
            unit_id=request.unit_id,
            device_id=request.device_id,
        )

        final_status = "counterfeit" if is_anomaly else result.get("status", "verified")
        final_message = (
            "Warning: Geographic counterfeit anomaly detected across scan locations."
            if is_anomaly
            else result.get("message", "Medication verified as authentic")
        )

        return VerifyResponse(
            status=final_status,
            message=final_message,
            batch_id=result.get("batch_id") or batch_identifier,
            manufacturer=result.get("manufacturer"),
            handoffs=result.get("handoffs"),
            expiry_date=(
                gs1_result.expiry_date.isoformat()
                if gs1_result.expiry_date
                else result.get("expiry_date")
            ),
            transaction_hash=result.get("transaction_hash"),
            cryptographic_hash=gs1_result.cryptographic_hash,
            scan_count=scan_count + 1,
            is_anomaly=is_anomaly,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Verification failed: {str(e)}",
        )


@router.get(
    "/{unit_id}",
    response_model=VerifyResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Unit not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
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
