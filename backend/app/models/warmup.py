import uuid

from sqlalchemy import Column, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class Warmup(Base):
    __tablename__ = "warmups"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"), nullable=False)
    quote = Column(Text, nullable=True)
    mobility = Column(Text, nullable=True)
    activation = Column(Text, nullable=True)
    raw_text = Column(Text, nullable=True)

    session = relationship("Session", back_populates="warmup")
