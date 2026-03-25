import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class AthleteExecution(Base):
    __tablename__ = "athlete_executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    program_day_id = Column(UUID(as_uuid=True), ForeignKey("program_days.id"), nullable=False)
    athlete_ref = Column(String, nullable=True)
    data = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    program_day = relationship("ProgramDay", backref="athlete_executions")
