import uuid

from sqlalchemy import Column, ForeignKey, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class BlockExerciseRaw(Base):
    __tablename__ = "block_exercises_raw"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    block_id = Column(UUID(as_uuid=True), ForeignKey("session_blocks.id"), nullable=False)
    name = Column(Text, nullable=True)
    format = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    raw_payload = Column(JSON, nullable=False)

    block = relationship("SessionBlock", back_populates="exercises_raw")
