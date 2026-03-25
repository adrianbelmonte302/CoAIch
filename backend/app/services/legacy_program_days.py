from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.session import Session as SessionModel
from app.models.session_block import SessionBlock
from app.schemas.program_day import ProgramDayDetailSchema, ProgramDaySummarySchema


def legacy_program_day_summaries(db: Session) -> List[ProgramDaySummarySchema]:
    stmt = (
        select(SessionModel)
        .options(selectinload(SessionModel.blocks))
        .order_by(SessionModel.date.desc().nullslast(), SessionModel.title)
    )
    sessions = db.scalars(stmt).all()
    return [session_to_program_day_summary(session) for session in sessions]


def legacy_program_day_detail(session: SessionModel) -> ProgramDayDetailSchema:
    session_flow = build_session_flow(session)
    return ProgramDayDetailSchema(
        id=session.id,
        day_id=session.date.isoformat() if session.date else str(session.id),
        date=session.date,
        weekday=session.weekday,
        display_title=session.title or "Programa del día",
        is_rest_day=session.is_rest_day,
        day_type="rest" if session.is_rest_day else "training",
        deload_week=session.deload_week,
        program_source="legacy_sessions",
        athlete_ref=None,
        schema_version="legacy-1.0.0",
        entity_type="program_day",
        classification=None,
        related_workout_ids=None,
        related_competition_ids=None,
        source_integrity=None,
        raw_content=None,
        session_context={
            "tags": session.session_tags or [],
            "estimated_duration_min": session.estimated_duration_min,
        },
        session_flow=session_flow,
        execution_log=None,
        athlete_feedback=None,
        derived_metrics=None,
        ai_annotations=None,
        raw_import_id=session.raw_import_id,
    )


def session_to_program_day_summary(session: SessionModel) -> ProgramDaySummarySchema:
    return ProgramDaySummarySchema(
        id=session.id,
        day_id=session.date.isoformat() if session.date else str(session.id),
        date=session.date,
        weekday=session.weekday,
        display_title=session.title or "Programa del día",
        is_rest_day=session.is_rest_day,
        day_type="rest" if session.is_rest_day else "training",
        deload_week=session.deload_week,
        program_source="legacy_sessions",
        athlete_ref=None,
        session_context={
            "tags": session.session_tags or [],
            "estimated_duration_min": session.estimated_duration_min,
        },
    )


def build_session_flow(session: SessionModel) -> Optional[dict]:
    if not session.blocks and not session.warmup:
        return None

    warmup = None
    if session.warmup:
        warmup = {
            "quote": session.warmup.quote,
            "mobility": session.warmup.mobility,
            "activation": session.warmup.activation,
            "raw_text": session.warmup.raw_text,
        }

    blocks = [block_to_program_block(block, order) for order, block in enumerate(session.blocks, start=1)]

    return {
        "general_warmup": warmup,
        "variants": [
            {
                "variant_id": "A",
                "title": None,
                "modality": None,
                "selection_rule": None,
                "warmup": None,
                "blocks": blocks,
                "cooldown": None,
                "notes_literal": None,
            }
        ],
        "shared_blocks": [],
        "cooldown": None,
        "mobility_flow": None,
    }


def block_to_program_block(block: SessionBlock, order: int) -> dict:
    exercises = []
    for idx, exercise in enumerate(block.exercises_raw or [], start=1):
        exercises.append(
            {
                "exercise_id": exercise.id.hex if hasattr(exercise.id, "hex") else str(exercise.id),
                "name": exercise.name,
                "movement_category": None,
                "modality": None,
                "format": exercise.format,
                "set_structure": [],
                "equipment": [],
                "rx_options": None,
                "scaled_options": None,
                "intermediate_options": None,
                "women_options": None,
                "men_options": None,
                "alternatives": [],
                "standards": [],
                "targets": [],
                "score_format": None,
                "notes": exercise.notes,
            }
        )

    sub_block = {
        "sub_block_id": f"{order}-1",
        "title": block.title,
        "format": block.content_mode,
        "duration_min": None,
        "time_cap_min": None,
        "rest_sec": None,
        "description": block.raw_text,
        "exercises": exercises,
    }

    return {
        "block_id": block.original_block_id or str(block.id),
        "title": block.title,
        "block_type": block.type,
        "sequence_order": order,
        "focus": [],
        "prescription": {
            "format": block.content_mode,
            "time_cap_min": None,
            "duration_min": None,
            "rest_between_subblocks_sec": None,
            "sub_blocks": [sub_block],
        },
        "standards": [],
        "targets": [],
        "alternatives": [],
        "coach_notes_literal": block.coach_notes,
        "coach_notes_structured": None,
    }
