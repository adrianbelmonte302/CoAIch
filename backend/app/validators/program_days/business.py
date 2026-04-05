from __future__ import annotations

from typing import Any, Dict, List, Set

from .calendar import parse_date, weekday_label
from .report import Report


KNOWN_BLOCK_TYPES = {
    "strength",
    "metcon",
    "conditioning",
    "skill",
    "accessory",
    "warmup",
    "cooldown",
}


def _as_list(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def validate_business(items: List[Dict[str, Any]], report: Report, strict: bool) -> None:
    for idx, item in enumerate(items):
        date_str = item.get("date")
        weekday = item.get("weekday")
        actual_date = parse_date(date_str)
        actual_weekday = weekday_label(actual_date) if actual_date else None

        is_rest = bool(item.get("is_rest_day"))
        day_type = item.get("day_type")

        if is_rest and actual_weekday and actual_weekday != "Domingo":
            report.error("rest day solo puede ser Domingo", date=date_str, index=idx)
        if day_type == "rest" and actual_weekday and actual_weekday != "Domingo":
            report.error("day_type=rest solo puede ser Domingo", date=date_str, index=idx)
        if is_rest and day_type != "rest":
            report.error("is_rest_day=true requiere day_type=rest", date=date_str, index=idx)
        if day_type == "rest" and not is_rest:
            report.error("day_type=rest requiere is_rest_day=true", date=date_str, index=idx)

        session_flow = item.get("session_flow") or {}
        if is_rest:
            if session_flow.get("general_warmup") is not None:
                report.error("rest day no debe tener warmup", date=date_str, index=idx)
            if session_flow.get("variants"):
                report.error("rest day no debe tener variants", date=date_str, index=idx)
            if session_flow.get("shared_blocks"):
                report.error("rest day no debe tener shared_blocks", date=date_str, index=idx)
            if session_flow.get("cooldown") is not None:
                report.error("rest day no debe tener cooldown", date=date_str, index=idx)
            if session_flow.get("mobility_flow") is not None:
                report.error("rest day no debe tener mobility_flow", date=date_str, index=idx)
            if item.get("execution_log") is not None:
                report.error("rest day no debe tener execution_log", date=date_str, index=idx)
            if item.get("athlete_feedback") is not None:
                report.error("rest day no debe tener athlete_feedback", date=date_str, index=idx)
            if item.get("derived_metrics") is not None:
                report.error("rest day no debe tener derived_metrics", date=date_str, index=idx)
            if item.get("ai_annotations") is not None:
                report.error("rest day no debe tener ai_annotations", date=date_str, index=idx)
            if (item.get("session_context") or {}).get("tags"):
                report.error("rest day no debe tener tags", date=date_str, index=idx)
            if (item.get("session_context") or {}).get("estimated_duration_min") is not None:
                report.error("rest day no debe tener estimated_duration_min", date=date_str, index=idx)
            continue

        variants = _as_list(session_flow.get("variants"))
        shared_blocks = _as_list(session_flow.get("shared_blocks"))
        has_content = bool(variants) or bool(shared_blocks)
        if not has_content:
            report.error("training day sin variants/shared_blocks", date=date_str, index=idx)

        if not item.get("display_title"):
            msg = "training day sin display_title"
            if strict:
                report.error(msg, date=date_str, index=idx)
            else:
                report.warning(msg, date=date_str, index=idx)

        source_integrity = item.get("source_integrity") or {}
        if not source_integrity.get("detection_subject"):
            report.warning("detection_subject faltante", date=date_str, index=idx)
        if source_integrity.get("data_complete") is False:
            report.warning("data_complete=false", date=date_str, index=idx)

        raw_content = item.get("raw_content") or {}
        if raw_content.get("literal_day_text") is None:
            report.warning("literal_day_text faltante", date=date_str, index=idx)

        variant_ids: Set[str] = set()
        for v_idx, variant in enumerate(variants):
            variant_id = variant.get("variant_id")
            if not variant_id:
                report.error("variant sin variant_id", date=date_str, index=idx)
            elif variant_id in variant_ids:
                report.error("variant_id duplicado", date=date_str, index=idx)
            else:
                variant_ids.add(variant_id)

            blocks = _as_list(variant.get("blocks"))
            if not blocks and not variant.get("warmup") and not variant.get("notes_literal"):
                msg = f"variant {variant_id or v_idx} vacía"
                if strict:
                    report.error(msg, date=date_str, index=idx)
                else:
                    report.warning(msg, date=date_str, index=idx)

            seen_sequence: Set[int] = set()
            for block in blocks:
                if not block.get("block_id"):
                    report.error("block sin block_id", date=date_str, index=idx)
                block_type = block.get("block_type")
                if block_type is not None and block_type not in KNOWN_BLOCK_TYPES:
                    report.warning(f"block_type desconocido: {block_type}", date=date_str, index=idx)
                seq = block.get("sequence_order")
                if seq is None or not isinstance(seq, int):
                    report.warning("sequence_order inválido", date=date_str, index=idx)
                else:
                    if seq in seen_sequence:
                        report.warning("sequence_order duplicado", date=date_str, index=idx)
                    seen_sequence.add(seq)

                prescription = block.get("prescription") or {}
                sub_blocks = _as_list(prescription.get("sub_blocks"))
                for sub in sub_blocks:
                    exercises = _as_list(sub.get("exercises"))
                    if exercises:
                        for ex in exercises:
                            if not ex.get("exercise_id"):
                                report.warning("exercise sin exercise_id", date=date_str, index=idx)
                            if not ex.get("name"):
                                report.warning("exercise sin name", date=date_str, index=idx)
                            if "set_structure" in ex and not isinstance(ex.get("set_structure"), list):
                                report.error("set_structure debe ser array", date=date_str, index=idx)
                            for set_entry in _as_list(ex.get("set_structure")):
                                load = set_entry.get("load") if isinstance(set_entry, dict) else None
                                if load and not isinstance(load, dict):
                                    report.error("load con formato inválido", date=date_str, index=idx)
                                if isinstance(load, dict):
                                    for key in (
                                        "prescribed_kg",
                                        "prescribed_kg_min",
                                        "prescribed_kg_max",
                                        "percent_1rm_min",
                                        "percent_1rm_max",
                                        "rpe",
                                        "rir",
                                    ):
                                        if key in load and load[key] is not None and not isinstance(load[key], (int, float)):
                                            report.error(f"load.{key} debe ser numérico", date=date_str, index=idx)

                    if not exercises and not sub.get("description"):
                        report.warning("sub_block sin exercises ni description", date=date_str, index=idx)

                notes_structured = block.get("coach_notes_structured") or {}
                has_structured = any(
                    isinstance(value, list) and value for value in notes_structured.values()
                )
                if has_structured and not block.get("coach_notes_literal"):
                    report.warning("coach_notes_structured sin coach_notes_literal", date=date_str, index=idx)
