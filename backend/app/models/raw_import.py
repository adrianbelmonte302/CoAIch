import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, JSON, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class RawImport(Base):
    __tablename__ = "raw_imports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_file = Column(String, nullable=False)
    source_month = Column(String, nullable=False)
    raw_json = Column(JSON, nullable=False)
    parser_version = Column(String, nullable=False)
    imported_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    sessions = relationship("Session", back_populates="raw_import")
