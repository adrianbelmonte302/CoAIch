import uuid

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class CompetitionWorkout(Base):
    __tablename__ = "competition_workouts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    competition_id = Column(UUID(as_uuid=True), ForeignKey("competitions.id"), nullable=False)
    workout_definition_id = Column(UUID(as_uuid=True), ForeignKey("workout_definitions.id"), nullable=True)
    label = Column(String, nullable=True)
    metadata_json = Column("metadata", JSONB, nullable=True)

    competition = relationship("Competition", backref="workouts")
    workout_definition = relationship("WorkoutDefinition", backref="competition_instances")
