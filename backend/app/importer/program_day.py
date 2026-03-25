import hashlib
import json
from datetime import date
from typing import Any, Dict, List, Optional

from dateutil.parser import parse as parse_datetime
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.program_day import ProgramDay
from app.models.raw_import import RawImport
from app.schemas.program_day_import import ProgramDayImportSchema


class ProgramDayImporter:
    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()

    def import_payload(
        self,
        source_file: str,
        source_month: str,
        payload: List[Dict[str, Any]],
        overwrite: bool = False,
        only_new: bool = False,
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        raw_import_id = None
        if not dry_run:
            raw_import = RawImport(
                source_file=source_file,
                source_month=source_month,
                raw_json=payload,
                parser_version=self.settings.PARSER_VERSION,
            )
            self.db.add(raw_import)
            self.db.flush()
            raw_import_id = raw_import.id

        created = 0
        duplicates_in_db = 0
        overwritten = 0
        warnings: List[str] = []

        for idx, item in enumerate(payload):
            try:
                parsed = ProgramDayImportSchema.model_validate(item)
            except ValidationError as exc:
                warnings.append(f"program_day idx={idx} skipped: {exc}")
                continue

            source_hash = self.compute_hash(item)
            existing = (
                self.db.query(ProgramDay)
                .filter(ProgramDay.source_hash == source_hash)
                .first()
            )
            if existing and (only_new or not overwrite):
                duplicates_in_db += 1
                continue
            if existing and overwrite and not only_new:
                overwritten += 1
                if not dry_run:
                    self.db.delete(existing)

            if not dry_run:
                program_day = ProgramDay(
                    raw_import_id=raw_import_id,
                    day_id=parsed.day_id,
                    date=self.safe_parse_date(parsed.date),
                    weekday=parsed.weekday,
                    display_title=parsed.display_title,
                    is_rest_day=parsed.is_rest_day,
                    day_type=parsed.day_type,
                    deload_week=parsed.deload_week,
                    program_source=parsed.program_source,
                    athlete_ref=parsed.athlete_ref,
                    classification=parsed.classification.model_dump()
                    if parsed.classification
                    else None,
                    related_workout_ids=parsed.related_workout_ids,
                    related_competition_ids=parsed.related_competition_ids,
                    source_integrity=parsed.source_integrity.model_dump()
                    if parsed.source_integrity
                    else None,
                    raw_content=parsed.raw_content.model_dump() if parsed.raw_content else None,
                    session_context=parsed.session_context.model_dump()
                    if parsed.session_context
                    else None,
                    session_flow=parsed.session_flow.model_dump()
                    if parsed.session_flow
                    else None,
                    execution_log=parsed.execution_log,
                    athlete_feedback=parsed.athlete_feedback,
                    derived_metrics=parsed.derived_metrics,
                    ai_annotations=parsed.ai_annotations,
                    schema_version=parsed.schema_version,
                    entity_type=parsed.entity_type,
                    source_hash=source_hash,
                )
                self.db.add(program_day)
            created += 1

        if not dry_run:
            self.db.commit()

        return {
            "raw_import_id": str(raw_import_id) if raw_import_id else None,
            "program_days_imported": created,
            "program_days_total": len(payload),
            "duplicates_in_db": duplicates_in_db,
            "overwritten": overwritten,
            "warnings": warnings,
            "dry_run": dry_run,
        }

    @staticmethod
    def safe_parse_date(value: Optional[str]) -> Optional[date]:
        if not value:
            return None
        try:
            parsed = parse_datetime(value)
            return parsed.date()
        except Exception:
            return None

    @staticmethod
    def compute_hash(data: Dict[str, Any]) -> str:
        raw = json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()
