import uuid

from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class SessionBlock(Base):
    __tablename__ = "session_blocks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"), nullable=False)
    block_order = Column(Integer, nullable=False, default=0)
    original_block_id = Column(String, nullable=True)
    title = Column(String, nullable=True)
    type = Column(String, nullable=True)
    is_optional = Column(Boolean, nullable=True, default=False)
    content_mode = Column(String, nullable=True)
    raw_text = Column(Text, nullable=True)
    coach_notes = Column(Text, nullable=True)
    has_external_reference = Column(Boolean, nullable=False, default=False)
    external_reference_text = Column(Text, nullable=True)
    parsed_confidence = Column(Integer, nullable=True)

    session = relationship("Session", back_populates="blocks")
    exercises_raw = relationship("BlockExerciseRaw", back_populates="block", cascade="all, delete-orphan")
    items_canonical = relationship("BlockItemCanonical", back_populates="block", cascade="all, delete-orphan")
