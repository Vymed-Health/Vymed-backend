"""
Alias Manager Service

Handles distributor identity masking on the Stellar public ledger.
Distributors appear as "Verified Distributor 08" instead of their actual
Stellar public key, protecting trade secrets while maintaining audit trails.
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import async_session_factory
from src.models.distributor_alias import DistributorAlias


class AliasManager:
    """
    Manages distributor identity masking.

    Maps Stellar public keys to human-readable aliases for privacy.
    """

    async def get_or_create_alias(
        self,
        stellar_public_key: str,
        organization_name: Optional[str] = None,
    ) -> str:
        """
        Get an existing alias or create a new one for a distributor.

        Args:
            stellar_public_key: The distributor's Stellar public key.
            organization_name: Optional organization name for internal reference.

        Returns:
            The masked alias string (e.g., "Verified Distributor 08").
        """
        async with async_session_factory() as session:
            # Check if alias already exists
            result = await session.execute(
                select(DistributorAlias).where(
                    DistributorAlias.stellar_public_key == stellar_public_key
                )
            )
            alias_record = result.scalar_one_or_none()

            if alias_record:
                return alias_record.alias

            # Create new alias with next available number
            next_number = await self._get_next_alias_number(session)
            alias = f"Verified Distributor {next_number:02d}"

            new_alias = DistributorAlias(
                stellar_public_key=stellar_public_key,
                alias=alias,
                organization_name=organization_name,
            )
            session.add(new_alias)
            await session.commit()

            return alias

    async def register_verified_alias(
        self,
        stellar_public_key: str,
        challenge: str,
        signature: str,
        organization_name: Optional[str] = None,
    ) -> dict:
        """
        Register a verified distributor alias with cryptographic signature verification (VH-B04).

        Verifies that the caller owns the Stellar private key for `stellar_public_key`
        by checking the Ed25519 signature over the provided challenge message.
        """
        from stellar_sdk import Keypair
        import base64

        try:
            keypair = Keypair.from_public_key(stellar_public_key)
            try:
                sig_bytes = bytes.fromhex(signature)
            except ValueError:
                sig_bytes = base64.b64decode(signature)

            keypair.verify(challenge.encode("utf-8"), sig_bytes)
        except Exception as e:
            raise ValueError(f"Invalid cryptographic signature for public key: {str(e)}")

        alias = await self.get_or_create_alias(
            stellar_public_key=stellar_public_key,
            organization_name=organization_name,
        )

        return {
            "stellar_public_key": stellar_public_key,
            "alias": alias,
            "verified": True,
            "organization_name": organization_name,
        }


    async def resolve_alias(
        self,
        alias: str,
    ) -> Optional[str]:
        """
        Resolve a masked alias back to the Stellar public key.

        Args:
            alias: The masked alias string.

        Returns:
            The Stellar public key, or None if not found.
        """
        async with async_session_factory() as session:
            result = await session.execute(
                select(DistributorAlias).where(
                    DistributorAlias.alias == alias,
                    DistributorAlias.is_active == "Y",
                )
            )
            alias_record = result.scalar_one_or_none()

            if alias_record:
                return alias_record.stellar_public_key

            return None

    async def _get_next_alias_number(self, session: AsyncSession) -> int:
        """
        Get the next available alias number.

        Args:
            session: Database session.

        Returns:
            The next available number.
        """
        result = await session.execute(
            select(DistributorAlias).order_by(DistributorAlias.created_at.desc())
        )
        latest = result.scalar_one_or_none()

        if latest:
            # Extract number from alias "Verified Distributor XX"
            try:
                number = int(latest.alias.split()[-1])
                return number + 1
            except (ValueError, IndexError):
                return 1

        return 1

    async def deactivate_alias(self, stellar_public_key: str) -> bool:
        """
        Deactivate a distributor alias.

        Args:
            stellar_public_key: The distributor's Stellar public key.

        Returns:
            True if deactivated, False if not found.
        """
        async with async_session_factory() as session:
            result = await session.execute(
                select(DistributorAlias).where(
                    DistributorAlias.stellar_public_key == stellar_public_key
                )
            )
            alias_record = result.scalar_one_or_none()

            if alias_record:
                alias_record.is_active = "N"
                await session.commit()
                return True

            return False
