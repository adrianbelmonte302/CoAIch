from __future__ import annotations

import json
from datetime import date
from typing import Any, Dict, Iterable, List, Optional

from dateutil.parser import parse as parse_datetime


def is_v2_payload(payload: object) -> bool:
    if isinstance(payload, list) and payload:
        head = payload[0]
        if isinstance(head, dict):
            return head.get("entity_type") == "program_day"
    return False


def extract_sessions(payload: Dict[str, Any] | List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if isinstance(payload, list):
        return payload
    for candidate in ("sessions", "workouts", "data", "records"):
        records = payload.get(candidate)
        if isinstance(records, list):
            return records
    return []


def normalize_tags(value: Any) -> List[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if item]
    if isinstance(value, str):
        return [tag.strip() for tag in value.split(",") if tag.strip()]
    return []


def safe_parse_date(value: Any) -> Optional[date]:
    if not value:
        return None
    try:
        parsed = parse_datetime(value)
        return parsed.date()
    except Exception:
        return None


def infer_weekday(session_date: Optional[date]) -> Optional[str]:
    if not session_date:
        return None
    return session_date.strftime("%A")


def session_payload_to_program_day(
    payload: Dict[str, Any],
    default_source: str = "legacy_v1_import",
) -> Dict[str, Any]:
    session_date = safe_parse_date(payload.get("date") or payload.get("fecha"))
    date_str = session_date.isoformat() if session_date else payload.get("date") or payload.get("fecha")
    tags = normalize_tags(payload.get("tags") or payload.get("session_tags"))
    blocks = payload.get("blocks") or []

    warmup_payload = payload.get("warmup") or {}
    warmup_obj = None
    if warmup_payload:
        warmup_obj = {
            "quote": warmup_payload.get("quote"),
            "literal_day_text": None,
            "raw_text": warmup_payload.get("raw_text") or warmup_payload.get("text"),
            "mobility": warmup_payload.get("mobility"),
            "activation": warmup_payload.get("activation"),
        }

    variant_blocks = []
    for order, block in enumerate(blocks, start=1):
        exercises = []
        for idx, exercise in enumerate(block.get("exercises") or [], start=1):
            exercises.append(
                {
                    "exercise_id": f"{order}.{idx}",
                    "name": exercise.get("name"),
                    "movement_category": None,
                    "modality": None,
                    "format": exercise.get("format"),
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
                    "notes": exercise.get("notes"),
                }
            )

        sub_block = {
            "sub_block_id": f"{order}-1",
            "title": block.get("title"),
            "format": block.get("content_mode") or block.get("prescription"),
            "duration_min": None,
            "time_cap_min": None,
            "rest_sec": None,
            "description": block.get("raw_text") or block.get("prescription") or block.get("notes"),
            "exercises": exercises,
        }

        variant_blocks.append(
            {
                "block_id": block.get("id") or f"block-{order}",
                "title": block.get("title"),
                "block_type": block.get("type"),
                "sequence_order": order,
                "focus": [],
                "prescription": {
                    "format": block.get("content_mode") or block.get("prescription"),
                    "time_cap_min": None,
                    "duration_min": None,
                    "rest_between_subblocks_sec": None,
                    "sub_blocks": [sub_block],
                },
                "standards": [],
                "targets": [],
                "alternatives": [],
                "coach_notes_literal": block.get("coach_notes") or block.get("notes"),
                "coach_notes_structured": None,
            }
        )

    return {
        "schema_version": "2.0.0",
        "entity_type": "program_day",
        "day_id": date_str or payload.get("id") or payload.get("session_id") or "unknown",
        "date": date_str,
        "weekday": payload.get("weekday") or infer_weekday(session_date),
        "display_title": payload.get("title") or payload.get("name") or "Programa del día",
        "is_rest_day": bool(payload.get("rest_day") or payload.get("is_rest_day")),
        "day_type": "rest" if payload.get("rest_day") or payload.get("is_rest_day") else "training",
        "deload_week": bool(payload.get("deload") or payload.get("deload_week")),
        "program_source": default_source,
        "athlete_ref": None,
        "classification": {
            "session_archetype": "training",
            "primary_modalities": [],
            "movement_patterns": [],
            "energy_systems": [],
        },
        "related_workout_ids": [],
        "related_competition_ids": [],
        "source_integrity": {
            "data_complete": True,
            "parser_confidence": "legacy",
            "missing_sections": [],
            "detection_subject": None,
            "source_type": "legacy_v1",
        },
        "raw_content": {
            "quote": warmup_payload.get("quote") if warmup_payload else None,
            "literal_day_text": payload.get("raw_text")
            or payload.get("prescription")
            or None,
        },
        "session_context": {
            "tags": tags,
            "estimated_duration_min": payload.get("estimated_duration_min")
            or payload.get("duration_minutes")
            or payload.get("duration"),
            "priority": None,
            "intended_stimulus": [],
            "recording_requests": [],
        },
        "session_flow": {
            "general_warmup": warmup_obj,
            "variants": [
                {
                    "variant_id": "A",
                    "title": None,
                    "modality": None,
                    "selection_rule": None,
                    "warmup": None,
                    "blocks": variant_blocks,
                    "cooldown": None,
                    "notes_literal": None,
                }
            ],
            "shared_blocks": [],
            "cooldown": None,
            "mobility_flow": None,
        },
        "execution_log": None,
        "athlete_feedback": None,
        "derived_metrics": None,
        "ai_annotations": None,
    }


def v1_payload_to_v2(payload: Dict[str, Any] | List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    sessions = extract_sessions(payload)
    return [session_payload_to_program_day(item) for item in sessions]


def to_debug_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def session_model_to_program_day(session: "SessionModel") -> Dict[str, Any]:
    from app.models.session import Session as SessionModel  # noqa: WPS433

    if not isinstance(session, SessionModel):
        raise TypeError("expected SessionModel")

    date_str = session.date.isoformat() if session.date else None
    warmup_obj = None
    if session.warmup:
        warmup_obj = {
            "quote": session.warmup.quote,
            "literal_day_text": None,
            "raw_text": session.warmup.raw_text,
            "mobility": session.warmup.mobility,
            "activation": session.warmup.activation,
        }

    variant_blocks = []
    for order, block in enumerate(session.blocks or [], start=1):
        exercises = []
        for idx, exercise in enumerate(block.exercises_raw or [], start=1):
            exercises.append(
                {
                    "exercise_id": f"{order}.{idx}",
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

        variant_blocks.append(
            {
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
        )

    return {
        "schema_version": "2.0.0",
        "entity_type": "program_day",
        "day_id": date_str or str(session.id),
        "date": date_str,
        "weekday": session.weekday,
        "display_title": session.title or "Programa del día",
        "is_rest_day": session.is_rest_day,
        "day_type": "rest" if session.is_rest_day else "training",
        "deload_week": session.deload_week,
        "program_source": "legacy_db_sessions",
        "athlete_ref": None,
        "classification": {
            "session_archetype": "training",
            "primary_modalities": [],
            "movement_patterns": [],
            "energy_systems": [],
        },
        "related_workout_ids": [],
        "related_competition_ids": [],
        "source_integrity": {
            "data_complete": True,
            "parser_confidence": "legacy_db",
            "missing_sections": [],
            "detection_subject": None,
            "source_type": "legacy_db",
        },
        "raw_content": {
            "quote": session.warmup.quote if session.warmup else None,
            "literal_day_text": None,
        },
        "session_context": {
            "tags": session.session_tags or [],
            "estimated_duration_min": session.estimated_duration_min,
            "priority": None,
            "intended_stimulus": [],
            "recording_requests": [],
        },
        "session_flow": {
            "general_warmup": warmup_obj,
            "variants": [
                {
                    "variant_id": "A",
                    "title": None,
                    "modality": None,
                    "selection_rule": None,
                    "warmup": None,
                    "blocks": variant_blocks,
                    "cooldown": None,
                    "notes_literal": None,
                }
            ],
            "shared_blocks": [],
            "cooldown": None,
            "mobility_flow": None,
        },
        "execution_log": None,
        "athlete_feedback": None,
        "derived_metrics": None,
        "ai_annotations": None,
    }
