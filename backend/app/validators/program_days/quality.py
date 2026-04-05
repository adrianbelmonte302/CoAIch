from __future__ import annotations

from collections import Counter
from typing import Any, Dict, List

from .report import Report


def validate_quality(items: List[Dict[str, Any]], report: Report) -> None:
    training_days = [item for item in items if not item.get("is_rest_day")]
    if not training_days:
        return

    missing_literal = 0
    missing_detection = 0
    titles = []
    low_conf = 0

    for item in training_days:
        raw_content = item.get("raw_content") or {}
        if raw_content.get("literal_day_text") is None:
            missing_literal += 1
        source_integrity = item.get("source_integrity") or {}
        if not source_integrity.get("detection_subject"):
            missing_detection += 1
        if str(source_integrity.get("parser_confidence")).lower() in {"low", "none"}:
            low_conf += 1
        if item.get("display_title"):
            titles.append(item.get("display_title"))

    if missing_literal / len(training_days) > 0.3:
        report.warning("muchos días sin literal_day_text")
    if missing_detection / len(training_days) > 0.3:
        report.warning("muchos días sin detection_subject")
    if low_conf == len(training_days):
        report.warning("parser_confidence bajo en todos los días")

    counts = Counter(titles)
    for title, count in counts.items():
        if count >= 5:
            report.warning(f"título repetido {count} veces: {title}")

    for item in training_days:
        session_flow = item.get("session_flow") or {}
        variants = session_flow.get("variants") or []
        if not variants and not session_flow.get("shared_blocks"):
            report.warning("día de entrenamiento sin blocks ni variants", date=item.get("date"))
