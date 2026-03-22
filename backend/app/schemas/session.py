from datetime import date
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel
from pydantic.config import ConfigDict


class ORMSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class BlockExerciseRawSchema(ORMSchema):
    id: UUID
    name: Optional[str]
    format: Optional[str]
    notes: Optional[str]
    raw_payload: dict


class BlockItemCanonicalSchema(ORMSchema):
    id: UUID
    movement_name: Optional[str]
    movement_family: Optional[str]
    pattern_primary: Optional[str]
    pattern_secondary: Optional[str]
    modality: Optional[str]
    sets: Optional[int]
    reps: Optional[str]
    intensity_type: Optional[str]
    intensity_value_json: Optional[dict]
    execution_notes: Optional[str]
    raw_origin_text: Optional[str]


class SessionBlockSchema(ORMSchema):
    id: UUID
    block_order: int
    original_block_id: Optional[str]
    title: Optional[str]
    type: Optional[str]
    is_optional: Optional[bool]
    content_mode: Optional[str]
    raw_text: Optional[str]
    coach_notes: Optional[str]
    has_external_reference: bool
    external_reference_text: Optional[str]
    parsed_confidence: Optional[int]
    exercises_raw: List[BlockExerciseRawSchema] = []
    items_canonical: List[BlockItemCanonicalSchema] = []


class WarmupSchema(ORMSchema):
    quote: Optional[str]
    mobility: Optional[str]
    activation: Optional[str]
    raw_text: Optional[str]


class SessionSummarySchema(ORMSchema):
    id: UUID
    date: Optional[date]
    weekday: Optional[str]
    title: Optional[str]
    is_rest_day: Optional[bool]
    deload_week: Optional[bool]
    data_status: Optional[str]
    estimated_duration_min: Optional[int]
    session_tags: Optional[List[str]]
    source_ref_file: Optional[str]


class SessionDetailSchema(SessionSummarySchema):
    warmup: Optional[WarmupSchema]
    blocks: List[SessionBlockSchema] = []
    raw_import_id: UUID
