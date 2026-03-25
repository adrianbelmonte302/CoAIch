import uuid

from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.db.base import Base


class WorkoutDefinition(Base):
    __tablename__ = "workout_definitions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    slug = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    workout_type = Column(String, nullable=True)
    source = Column(String, nullable=True)
    metadata = Column(JSONB, nullable=True)
