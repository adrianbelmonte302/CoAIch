from typing import List, Optional

from pydantic import BaseModel, Field
from pydantic.config import ConfigDict


class StrictBase(BaseModel):
    model_config = ConfigDict(extra="forbid")


class LoadSchema(StrictBase):
    prescribed_kg: Optional[float] = None
    prescribed_kg_min: Optional[float] = None
    prescribed_kg_max: Optional[float] = None
    percent_1rm_min: Optional[float] = None
    percent_1rm_max: Optional[float] = None
    rpe: Optional[float] = None
    rir: Optional[float] = None
    load_notes: Optional[str] = None


class SetStructureSchema(StrictBase):
    sets: Optional[int] = None
    rounds: Optional[int] = None
    reps: Optional[int] = None
    reps_per_side: Optional[int] = None
    duration_sec: Optional[int] = None
    duration_min: Optional[int] = None
    distance_m: Optional[float] = None
    calories: Optional[int] = None
    rest_sec: Optional[int] = None
    load: Optional[LoadSchema] = None
    tempo: Optional[str] = None
    target: Optional[str] = None
    notes: Optional[str] = None


class ExerciseSchema(StrictBase):
    exercise_id: str
    name: Optional[str] = None
    movement_category: Optional[str] = None
    modality: Optional[str] = None
    format: Optional[str] = None
    set_structure: List[SetStructureSchema] = []
    equipment: List[str] = []
    rx_options: Optional[str] = None
    scaled_options: Optional[str] = None
    intermediate_options: Optional[str] = None
    women_options: Optional[str] = None
    men_options: Optional[str] = None
    alternatives: List[str] = []
    standards: List[str] = []
    targets: List[str] = []
    score_format: Optional[str] = None
    notes: Optional[str] = None


class SubBlockSchema(StrictBase):
    sub_block_id: str
    title: Optional[str] = None
    format: Optional[str] = None
    duration_min: Optional[int] = None
    time_cap_min: Optional[int] = None
    rest_sec: Optional[int] = None
    description: Optional[str] = None
    exercises: List[ExerciseSchema] = []


class PrescriptionSchema(StrictBase):
    format: Optional[str] = None
    time_cap_min: Optional[int] = None
    duration_min: Optional[int] = None
    rest_between_subblocks_sec: Optional[int] = None
    sub_blocks: List[SubBlockSchema] = []


class CoachNotesStructuredSchema(StrictBase):
    stimulus: List[str] = []
    strategy: List[str] = []
    pacing: List[str] = []
    breathing: List[str] = []
    technical_cues: List[str] = []
    common_errors: List[str] = []
    recovery_guidance: List[str] = []
    what_to_record: List[str] = []
    purpose: List[str] = []


class BlockSchema(StrictBase):
    block_id: str
    title: Optional[str] = None
    block_type: Optional[str] = None
    sequence_order: int
    focus: List[str] = []
    prescription: Optional[PrescriptionSchema] = None
    standards: List[str] = []
    targets: List[str] = []
    alternatives: List[str] = []
    coach_notes_literal: Optional[str] = None
    coach_notes_structured: Optional[CoachNotesStructuredSchema] = None


class VariantSchema(StrictBase):
    variant_id: str
    title: Optional[str] = None
    modality: Optional[str] = None
    selection_rule: Optional[str] = None
    warmup: Optional[dict] = None
    blocks: List[BlockSchema] = []
    cooldown: Optional[dict] = None
    notes_literal: Optional[str] = None


class SessionFlowSchema(StrictBase):
    general_warmup: Optional[dict] = None
    variants: List[VariantSchema] = []
    shared_blocks: List[BlockSchema] = []
    cooldown: Optional[dict] = None
    mobility_flow: Optional[dict] = None


class ClassificationSchema(StrictBase):
    session_archetype: Optional[str] = None
    primary_modalities: List[str] = []
    movement_patterns: List[str] = []
    energy_systems: List[str] = []


class SourceIntegritySchema(StrictBase):
    data_complete: Optional[bool] = None
    parser_confidence: Optional[str] = None
    missing_sections: List[str] = []
    detection_subject: Optional[str] = None
    source_type: Optional[str] = None


class RawContentSchema(StrictBase):
    quote: Optional[str] = None
    literal_day_text: Optional[str] = None


class SessionContextSchema(StrictBase):
    tags: List[str] = []
    estimated_duration_min: Optional[int] = None
    priority: Optional[str] = None
    intended_stimulus: List[str] = []
    recording_requests: List[str] = []


class ProgramDayImportSchema(StrictBase):
    schema_version: str = Field(..., pattern=r"^2\.")
    entity_type: str = Field(..., pattern=r"^program_day$")
    day_id: str
    date: str
    weekday: Optional[str] = None
    display_title: Optional[str] = None
    is_rest_day: Optional[bool] = False
    day_type: Optional[str] = None
    deload_week: Optional[bool] = False
    program_source: Optional[str] = None
    athlete_ref: Optional[str] = None
    classification: Optional[ClassificationSchema] = None
    related_workout_ids: List[str] = []
    related_competition_ids: List[str] = []
    source_integrity: Optional[SourceIntegritySchema] = None
    raw_content: Optional[RawContentSchema] = None
    session_context: Optional[SessionContextSchema] = None
    session_flow: Optional[SessionFlowSchema] = None
    execution_log: Optional[dict] = None
    athlete_feedback: Optional[dict] = None
    derived_metrics: Optional[dict] = None
    ai_annotations: Optional[dict] = None
