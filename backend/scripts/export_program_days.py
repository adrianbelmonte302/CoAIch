import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import date
from typing import Any, Dict, List

from sqlalchemy import select

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.db.session import SessionLocal  # noqa: E402
from app.models.program_day import ProgramDay  # noqa: E402


MONTH_NAMES = [
    "ENERO",
    "FEBRERO",
    "MARZO",
    "ABRIL",
    "MAYO",
    "JUNIO",
    "JULIO",
    "AGOSTO",
    "SEPTIEMBRE",
    "OCTUBRE",
    "NOVIEMBRE",
    "DICIEMBRE",
]


def serialize_date(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def program_day_to_payload(row: ProgramDay) -> Dict[str, Any]:
    return {
        "schema_version": row.schema_version,
        "entity_type": row.entity_type,
        "day_id": row.day_id,
        "date": serialize_date(row.date),
        "weekday": row.weekday,
        "display_title": row.display_title,
        "is_rest_day": row.is_rest_day,
        "day_type": row.day_type,
        "deload_week": row.deload_week,
        "program_source": row.program_source,
        "athlete_ref": row.athlete_ref,
        "classification": row.classification,
        "related_workout_ids": row.related_workout_ids or [],
        "related_competition_ids": row.related_competition_ids or [],
        "source_integrity": row.source_integrity,
        "raw_content": row.raw_content,
        "session_context": row.session_context,
        "session_flow": row.session_flow,
        "execution_log": row.execution_log,
        "athlete_feedback": row.athlete_feedback,
        "derived_metrics": row.derived_metrics,
        "ai_annotations": row.ai_annotations,
    }


def month_key_from_date(value: Any) -> tuple[int, int] | None:
    if isinstance(value, date):
        return (value.year, value.month)
    try:
        parsed = date.fromisoformat(str(value))
        return (parsed.year, parsed.month)
    except Exception:
        return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Exporta program_days a JSON por mes.")
    parser.add_argument("--out-dir", default="exports", help="Carpeta destino (relativa a backend).")
    args = parser.parse_args()

    out_dir = args.out_dir
    if not os.path.isabs(out_dir):
        out_dir = os.path.join(BACKEND_DIR, out_dir)
    os.makedirs(out_dir, exist_ok=True)

    errors: List[str] = []
    buckets: Dict[tuple[int, int], List[Dict[str, Any]]] = defaultdict(list)

    with SessionLocal() as db:
        rows = db.scalars(select(ProgramDay).order_by(ProgramDay.date.asc().nullslast())).all()
        for row in rows:
            key = month_key_from_date(row.date)
            if not key:
                errors.append(f"ProgramDay sin fecha válida: id={row.id}")
                continue
            buckets[key].append(program_day_to_payload(row))

    for (year, month), items in buckets.items():
        month_name = MONTH_NAMES[month - 1] if 1 <= month <= 12 else f"MES{month}"
        filename = f"workouts_{month_name}_{year}.json"
        path = os.path.join(out_dir, filename)
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(items, handle, ensure_ascii=False, indent=2)
        print(f"exported {len(items)} -> {path}")

    if errors:
        print("Errores encontrados:", file=sys.stderr)
        for err in errors:
            print(f"- {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
