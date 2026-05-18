"""
Scan Log Model

SQLAlchemy model for auditing verification attempts.
Used for security analytics and fraud detection.
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import UUID

from src.core.database import Base


class ScanLog(Base):
    """
    Audit log for medication verification attempts.

    Tracks every scan for security analytics and fraud detection.
    """

    __tablename__ = "scan_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    unit_id = Column(String(128), nullable=False, index=True)
    device_id = Column(String(64), nullable=False)
    ip_address = Column(String(45), nullable=True)
    status = Column(String(20), nullable=False)
    transaction_hash = Column(String(64), nullable=True)
    scan_count = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<ScanLog(unit_id='{self.unit_id}', status='{self.status}')>"
