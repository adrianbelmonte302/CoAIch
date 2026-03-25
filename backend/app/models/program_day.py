import uuid
from datetime import date

from sqlalchemy import Boolean, Column, Date, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.db.types import JSONBCompat


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
    classification = Column(JSONBCompat, nullable=True)
    related_workout_ids = Column(JSONBCompat, nullable=True)
    related_competition_ids = Column(JSONBCompat, nullable=True)
    source_integrity = Column(JSONBCompat, nullable=True)
    raw_content = Column(JSONBCompat, nullable=True)
    session_context = Column(JSONBCompat, nullable=True)
    session_flow = Column(JSONBCompat, nullable=True)
    execution_log = Column(JSONBCompat, nullable=True)
    athlete_feedback = Column(JSONBCompat, nullable=True)
    derived_metrics = Column(JSONBCompat, nullable=True)
    ai_annotations = Column(JSONBCompat, nullable=True)
    schema_version = Column(String, nullable=True)
    entity_type = Column(String, nullable=True)
    source_hash = Column(String, nullable=True)

    raw_import = relationship("RawImport", backref="program_days")
