from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from pydantic.config import ConfigDict


class ORMSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ProgramDaySummarySchema(ORMSchema):
    id: UUID
    day_id: str
    date: Optional[date]
    weekday: Optional[str]
    display_title: Optional[str]
    is_rest_day: Optional[bool]
    day_type: Optional[str]
    deload_week: Optional[bool]
    program_source: Optional[str]
    athlete_ref: Optional[str]
    session_context: Optional[dict] = None


class ProgramDayDetailSchema(ProgramDaySummarySchema):
    schema_version: Optional[str]
    entity_type: Optional[str]
    classification: Optional[dict]
    related_workout_ids: Optional[list]
    related_competition_ids: Optional[list]
    source_integrity: Optional[dict]
    raw_content: Optional[dict]
    session_context: Optional[dict]
    session_flow: Optional[dict]
    execution_log: Optional[dict]
    athlete_feedback: Optional[dict]
    derived_metrics: Optional[dict]
    ai_annotations: Optional[dict]
    raw_import_id: UUID
