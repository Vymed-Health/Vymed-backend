"""
Recall Management API Routes

Handles batch recall operations using Stellar's clawback mechanism.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.schemas.recall import RecallCreate, RecallResponse
from src.services.stellar_service import StellarService
from src.core.security import verify_api_key

router = APIRouter()


@router.post("", response_model=RecallResponse, status_code=status.HTTP_201_CREATED)
async def initiate_recall(
    request: RecallCreate,
    api_key: str = Depends(verify_api_key),
):
    """
    Initiate a batch recall using Stellar's clawback mechanism.

    This will revoke all outstanding units of the specified batch asset.
    Patients scanning recalled units will see a Red alert.
    """
    stellar_service = StellarService()
    try:
        result = await stellar_service.execute_recall(
            asset_code=request.asset_code,
            reason=request.reason,
        )
        return RecallResponse(
            recall_id=result["recall_id"],
            asset_code=request.asset_code,
            status="initiated",
            reason=request.reason,
            transaction_hash=result["transaction_hash"],
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Recall failed: {str(e)}",
        )


@router.get("/{recall_id}", response_model=RecallResponse)
async def get_recall_status(
    recall_id: UUID,
    api_key: str = Depends(verify_api_key),
):
    """
    Get the status of a recall operation.
    """
    stellar_service = StellarService()
    recall = await stellar_service.get_recall_status(recall_id=recall_id)

    if not recall:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recall not found",
        )

    return recall
