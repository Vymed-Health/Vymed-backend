"""
Distributor Alias Model

SQLAlchemy model for mapping distributor Stellar public keys to masked aliases.
This protects trade secrets while maintaining a verifiable chain of custody.
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID

from src.core.database import Base


class DistributorAlias(Base):
    """
    Maps Stellar public keys to human-readable aliases.

    On the public ledger, distributors appear as "Verified Distributor 08"
    instead of their actual Stellar public key.
    """

    __tablename__ = "distributor_aliases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    stellar_public_key = Column(String(56), unique=True, nullable=False, index=True)
    alias = Column(String(64), unique=True, nullable=False)
    organization_name = Column(String(256), nullable=True)
    is_active = Column(String(1), default="Y", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<DistributorAlias(alias='{self.alias}')>"
