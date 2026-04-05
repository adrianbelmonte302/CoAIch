from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from .business import validate_business
from .calendar import validate_calendar
from .quality import validate_quality
from .report import Report
from .schema import validate_schema


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_program_days_json(path: str, strict: bool = False) -> Report:
    report = Report()
    report.meta["file"] = path
    file_path = Path(path)

    if not file_path.exists():
        report.error("archivo no encontrado")
        return report

    try:
        data = load_json(file_path)
    except json.JSONDecodeError as exc:
        report.error(f"JSON inválido: {exc}")
        return report

    if not isinstance(data, list):
        report.error("root JSON debe ser una lista")
        return report

    if not data:
        report.error("JSON vacío")
        return report

    items: List[Dict[str, Any]] = []
    for idx, item in enumerate(data):
        if not isinstance(item, dict):
            report.error("item no es objeto JSON", index=idx)
            continue
        items.append(item)

    if not items:
        return report

    _, schema_failed = validate_schema(items, report)
    if schema_failed:
        return report

    validate_calendar(items, report, strict)
    validate_business(items, report, strict)
    validate_quality(items, report)

    return report
