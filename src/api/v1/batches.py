"""
Batch Management API Routes

Handles manufacturer batch registration, parent-child mapping, and batch queries.
"""

from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status

from src.schemas.batch import BatchCreate, BatchResponse, ParentChildMapRequest
from src.services.batch_service import BatchService
from src.core.security import verify_api_key

router = APIRouter()


@router.post("", response_model=BatchResponse, status_code=status.HTTP_201_CREATED)
async def create_batch(
    request: BatchCreate,
    api_key: str = Depends(verify_api_key),
):
    """
    Register a new drug batch on the Stellar blockchain.

    Creates a unique Stellar asset for the batch with AUTH_CLAWBACK_ENABLED flag.
    """
    batch_service = BatchService()
    try:
        batch = await batch_service.create_batch(
            asset_code=request.asset_code,
            manufacturer_name=request.manufacturer_name,
            total_units=request.total_units,
            expiry_date=request.expiry_date,
        )
        return batch
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create batch: {str(e)}",
        )


@router.get("/{batch_id}", response_model=BatchResponse)
async def get_batch(
    batch_id: UUID,
    api_key: str = Depends(verify_api_key),
):
    """
    Get batch details by ID.
    """
    batch_service = BatchService()
    batch = await batch_service.get_batch(batch_id=batch_id)

    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found",
        )

    return batch


@router.post("/{batch_id}/map", status_code=status.HTTP_200_OK)
async def map_parent_child(
    batch_id: UUID,
    request: ParentChildMapRequest,
    api_key: str = Depends(verify_api_key),
):
    """
    Map parent-child relationships for nested scanning.

    Example: 1 Carton (parent) = 50 Bottles (children).
    Scanning the carton updates all child bottles on-chain.
    """
    batch_service = BatchService()
    try:
        result = await batch_service.map_parent_child(
            batch_id=batch_id,
            parent_id=request.parent_id,
            child_ids=request.child_ids,
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to map parent-child: {str(e)}",
        )
