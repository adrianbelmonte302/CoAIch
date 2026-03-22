import uuid

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class Session(Base):
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    raw_import_id = Column(UUID(as_uuid=True), ForeignKey("raw_imports.id"), nullable=False)
    source_session_id = Column(String, nullable=True)
    date = Column(Date, nullable=True)
    weekday = Column(String, nullable=True)
    title = Column(String, nullable=True)
    is_rest_day = Column(Boolean, nullable=True, default=False)
    deload_week = Column(Boolean, nullable=True, default=False)
    data_status = Column(String, nullable=True, default="complete")
    estimated_duration_min = Column(Integer, nullable=True)
    session_tags = Column(JSONB, nullable=True)
    source_ref_file = Column(String, nullable=True)
    source_hash = Column(String, nullable=True)

    raw_import = relationship("RawImport", back_populates="sessions")
    warmup = relationship("Warmup", back_populates="session", uselist=False)
    blocks = relationship("SessionBlock", back_populates="session", cascade="all, delete-orphan")
