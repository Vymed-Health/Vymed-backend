"""
Batch Service

Handles batch management business logic including creation,
parent-child mapping, and metadata storage.
"""

from datetime import date
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.database import async_session_factory
from src.models.batch import Batch
from src.services.stellar_service import StellarService


class BatchService:
    """
    Service for managing drug batches on and off the blockchain.

    Handles:
    - Batch creation with Stellar asset minting
    - Parent-child relationship mapping
    - Batch metadata queries
    """

    async def create_batch(
        self,
        asset_code: str,
        manufacturer_name: str,
        total_units: int,
        expiry_date: date,
    ) -> Dict:
        """
        Create a new drug batch.

        Mints a Stellar asset and stores metadata in PostgreSQL.

        Args:
            asset_code: Stellar asset code for the batch.
            manufacturer_name: Name of the manufacturer.
            total_units: Total number of units.
            expiry_date: Batch expiry date.

        Returns:
            Dict containing batch details.
        """
        # Mint asset on Stellar
        stellar_service = StellarService()
        mint_result = await stellar_service.mint_batch_asset(
            asset_code=asset_code,
            amount=total_units,
        )

        # Store metadata in PostgreSQL
        async with async_session_factory() as session:
            batch = Batch(
                asset_code=asset_code,
                manufacturer_name=manufacturer_name,
                manufacturer_public_key=settings.MANUFACTURER_PUBLIC_KEY,
                total_units=total_units,
                expiry_date=expiry_date,
                transaction_hash=mint_result.get("transaction_hash"),
            )
            session.add(batch)
            await session.commit()
            await session.refresh(batch)

            return {
                "batch_id": batch.id,
                "asset_code": batch.asset_code,
                "manufacturer_name": batch.manufacturer_name,
                "total_units": batch.total_units,
                "expiry_date": batch.expiry_date.isoformat(),
                "transaction_hash": batch.transaction_hash,
                "created_at": batch.created_at.isoformat(),
                "status": batch.status,
            }

    async def get_batch(self, batch_id: UUID) -> Optional[Dict]:
        """
        Get batch details by ID.

        Args:
            batch_id: The batch UUID.

        Returns:
            Dict containing batch details, or None if not found.
        """
        async with async_session_factory() as session:
            result = await session.execute(
                select(Batch).where(Batch.id == batch_id)
            )
            batch = result.scalar_one_or_none()

            if not batch:
                return None

            return {
                "batch_id": batch.id,
                "asset_code": batch.asset_code,
                "manufacturer_name": batch.manufacturer_name,
                "total_units": batch.total_units,
                "expiry_date": batch.expiry_date.isoformat(),
                "transaction_hash": batch.transaction_hash,
                "created_at": batch.created_at.isoformat(),
                "status": batch.status,
            }

    async def map_parent_child(
        self,
        batch_id: UUID,
        parent_id: str,
        child_ids: List[str],
    ) -> Dict:
        """
        Map parent-child relationships for nested scanning.

        Example: 1 Carton (parent) = 50 Bottles (children).
        Scanning the carton updates all child bottles on-chain.

        Args:
            batch_id: The batch UUID.
            parent_id: Parent unit ID (e.g., carton).
            child_ids: List of child unit IDs (e.g., bottles).

        Returns:
            Dict containing the mapping result.
        """
        # TODO: Store parent-child mapping in database
        # TODO: Update Stellar trustlines for all child units

        return {
            "batch_id": str(batch_id),
            "parent_id": parent_id,
            "child_count": len(child_ids),
            "status": "mapped",
        }
