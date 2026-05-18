"""
Batch Model

SQLAlchemy model for storing batch metadata and Stellar asset information.
"""

import uuid
from datetime import date, datetime

from sqlalchemy import Column, Date, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID

from src.core.database import Base


class Batch(Base):
    """Represents a drug batch registered on the Stellar blockchain."""

    __tablename__ = "batches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_code = Column(String(12), unique=True, nullable=False, index=True)
    manufacturer_name = Column(String(256), nullable=False)
    manufacturer_public_key = Column(String(56), nullable=False)
    total_units = Column(Integer, nullable=False)
    expiry_date = Column(Date, nullable=False)
    transaction_hash = Column(String(64), nullable=True)
    status = Column(String(20), default="active", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Batch(asset_code='{self.asset_code}', status='{self.status}')>"
