import uuid
from datetime import date

from sqlalchemy import Boolean, Column, Date, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class ProgramDay(Base):
    __tablename__ = "program_days"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    raw_import_id = Column(UUID(as_uuid=True), ForeignKey("raw_imports.id"), nullable=False)
    day_id = Column(String, nullable=False)
    date = Column(Date, nullable=True)
    weekday = Column(String, nullable=True)
    display_title = Column(String, nullable=True)
    is_rest_day = Column(Boolean, nullable=True, default=False)
    day_type = Column(String, nullable=True)
    deload_week = Column(Boolean, nullable=True, default=False)
    program_source = Column(String, nullable=True)
    athlete_ref = Column(String, nullable=True)
    classification = Column(JSONB, nullable=True)
    related_workout_ids = Column(JSONB, nullable=True)
    related_competition_ids = Column(JSONB, nullable=True)
    source_integrity = Column(JSONB, nullable=True)
    raw_content = Column(JSONB, nullable=True)
    session_context = Column(JSONB, nullable=True)
    session_flow = Column(JSONB, nullable=True)
    execution_log = Column(JSONB, nullable=True)
    athlete_feedback = Column(JSONB, nullable=True)
    derived_metrics = Column(JSONB, nullable=True)
    ai_annotations = Column(JSONB, nullable=True)
    schema_version = Column(String, nullable=True)
    entity_type = Column(String, nullable=True)
    source_hash = Column(String, nullable=True)

    raw_import = relationship("RawImport", backref="program_days")
