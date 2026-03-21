import uuid

from sqlalchemy import Column, ForeignKey, JSON, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class BlockItemCanonical(Base):
    __tablename__ = "block_items_canonical"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    block_id = Column(UUID(as_uuid=True), ForeignKey("session_blocks.id"), nullable=False)
    movement_name = Column(String, nullable=True)
    movement_family = Column(String, nullable=True)
    pattern_primary = Column(String, nullable=True)
    pattern_secondary = Column(String, nullable=True)
    modality = Column(String, nullable=True)
    sets = Column(Integer, nullable=True)
    reps = Column(String, nullable=True)
    intensity_type = Column(String, nullable=True)
    intensity_value_json = Column(JSON, nullable=True)
    execution_notes = Column(Text, nullable=True)
    raw_origin_text = Column(Text, nullable=True)

    block = relationship("SessionBlock", back_populates="items_canonical")
