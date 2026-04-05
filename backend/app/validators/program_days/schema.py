from __future__ import annotations

from typing import Any, Dict, List, Tuple

from pydantic import ValidationError

from app.schemas.program_day_import import ProgramDayImportSchema

from .report import Report


def validate_schema(items: List[Dict[str, Any]], report: Report) -> Tuple[List[ProgramDayImportSchema], bool]:
    valid: List[ProgramDayImportSchema] = []
    has_fatal = False
    for idx, item in enumerate(items):
        try:
            model = ProgramDayImportSchema.model_validate(item)
            valid.append(model)
        except ValidationError as exc:
            report.error(f"schema inválido: {exc}", date=item.get("date"), index=idx)
            has_fatal = True
    return valid, has_fatal
