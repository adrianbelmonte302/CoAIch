import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class CompetitionResult(Base):
    __tablename__ = "competition_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    competition_workout_id = Column(UUID(as_uuid=True), ForeignKey("competition_workouts.id"), nullable=False)
    athlete_ref = Column(String, nullable=True)
    result = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    competition_workout = relationship("CompetitionWorkout", backref="results")
