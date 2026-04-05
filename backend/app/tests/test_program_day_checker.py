import json
from datetime import date, timedelta
from pathlib import Path

from app.validators.program_days import validate_program_days_json


def build_month(month_start: date) -> list[dict]:
    items = []
    for i in range(30):
        d = month_start + timedelta(days=i)
        weekday = d.strftime("%A")
        is_rest = weekday == "Sunday"
        item = {
            "schema_version": "2.1.0",
            "entity_type": "program_day",
            "day_id": d.isoformat(),
            "date": d.isoformat(),
            "weekday": weekday,
            "display_title": None if is_rest else "Training Day",
            "is_rest_day": is_rest,
            "day_type": "rest" if is_rest else "training",
            "deload_week": False,
            "program_source": "truecoach",
            "athlete_ref": "adrian_belmonte",
            "classification": {
                "session_archetype": None,
                "primary_modalities": [],
                "movement_patterns": [],
                "energy_systems": [],
            },
            "related_workout_ids": [],
            "related_competition_ids": [],
            "source_integrity": {
                "data_complete": True,
                "parser_confidence": "high",
                "missing_sections": [],
                "detection_subject": "subject",
                "source_type": "gmail",
            },
            "raw_content": {"quote": None, "literal_day_text": None if is_rest else "text"},
            "session_context": {
                "tags": [],
                "estimated_duration_min": None,
                "priority": None,
                "intended_stimulus": [],
                "recording_requests": [],
            },
            "session_flow": {
                "general_warmup": None,
                "variants": [],
                "shared_blocks": [],
                "cooldown": None,
                "mobility_flow": None,
            },
            "execution_log": None,
            "athlete_feedback": None,
            "derived_metrics": None,
            "ai_annotations": None,
        }
        if not is_rest:
            item["session_flow"]["variants"] = [
                {
                    "variant_id": "A",
                    "title": "Main",
                    "modality": None,
                    "selection_rule": None,
                    "warmup": None,
                    "blocks": [
                        {
                            "block_id": "A",
                            "title": "Block A",
                            "block_type": "strength",
                            "sequence_order": 1,
                            "focus": [],
                            "prescription": {
                                "format": None,
                                "time_cap_min": None,
                                "duration_min": None,
                                "rest_between_subblocks_sec": None,
                                "sub_blocks": [
                                    {
                                        "sub_block_id": "A1",
                                        "title": "Sub A1",
                                        "format": None,
                                        "duration_min": None,
                                        "time_cap_min": None,
                                        "rest_sec": None,
                                        "description": "Do work",
                                        "exercises": [],
                                    }
                                ],
                            },
                            "standards": [],
                            "targets": [],
                            "alternatives": [],
                            "coach_notes_literal": None,
                            "coach_notes_structured": {
                                "stimulus": [],
                                "strategy": [],
                                "pacing": [],
                                "breathing": [],
                                "technical_cues": [],
                                "common_errors": [],
                                "recovery_guidance": [],
                                "what_to_record": [],
                                "purpose": [],
                            },
                        }
                    ],
                    "cooldown": None,
                    "notes_literal": None,
                }
            ]
        items.append(item)
    return items


def write_json(path: Path, payload: list[dict]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def test_valid_file(tmp_path: Path):
    payload = build_month(date(2025, 4, 1))
    file_path = tmp_path / "workouts_ABRIL_2025.json"
    write_json(file_path, payload)
    report = validate_program_days_json(str(file_path))
    assert report.result in {"PASS", "PASS WITH WARNINGS"}


def test_duplicate_date_fails(tmp_path: Path):
    payload = build_month(date(2025, 4, 1))
    payload[1]["date"] = payload[0]["date"]
    file_path = tmp_path / "dup.json"
    write_json(file_path, payload)
    report = validate_program_days_json(str(file_path))
    assert report.result == "FAIL"


def test_missing_day_fails(tmp_path: Path):
    payload = build_month(date(2025, 4, 1))
    payload.pop()
    file_path = tmp_path / "missing.json"
    write_json(file_path, payload)
    report = validate_program_days_json(str(file_path))
    assert report.result == "FAIL"


def test_rest_day_on_non_sunday_fails(tmp_path: Path):
    payload = build_month(date(2025, 4, 1))
    payload[0]["is_rest_day"] = True
    payload[0]["day_type"] = "rest"
    file_path = tmp_path / "rest.json"
    write_json(file_path, payload)
    report = validate_program_days_json(str(file_path))
    assert report.result == "FAIL"


def test_wrong_weekday_warns(tmp_path: Path):
    payload = build_month(date(2025, 4, 1))
    payload[0]["weekday"] = "Sunday"
    file_path = tmp_path / "weekday.json"
    write_json(file_path, payload)
    report = validate_program_days_json(str(file_path))
    assert report.result in {"PASS WITH WARNINGS", "FAIL"}


def test_training_day_empty_content_fails(tmp_path: Path):
    payload = build_month(date(2025, 4, 1))
    payload[1]["session_flow"]["variants"] = []
    file_path = tmp_path / "empty.json"
    write_json(file_path, payload)
    report = validate_program_days_json(str(file_path))
    assert report.result == "FAIL"
