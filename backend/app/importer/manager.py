import json
import logging
from datetime import date
from typing import Any, Dict, Iterable, List, Optional

from dateutil.parser import parse as parse_datetime
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.importer.variants import OctoberAdapter, NovDecAdapter, VariantAdapter
from app.models.raw_import import RawImport
from app.models.session import Session as SessionModel
from app.models.warmup import Warmup

logger = logging.getLogger(__name__)


class SessionImporter:
    def __init__(self, db: Session, adapters: Optional[List[VariantAdapter]] = None):
        self.db = db
        self.settings = get_settings()
        self.adapters = adapters or [OctoberAdapter(), NovDecAdapter()]

    def import_payload(
        self, source_file: str, source_month: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        sessions_data = self.extract_sessions(payload)
        adapter = self.choose_adapter(sessions_data)
        raw_import = RawImport(
            source_file=source_file,
            source_month=source_month,
            raw_json=payload,
            parser_version=self.settings.PARSER_VERSION,
        )
        self.db.add(raw_import)
        self.db.flush()

        warnings: List[str] = []
        created = 0
        for idx, session_payload in enumerate(sessions_data):
            try:
                session_model = self.transform_session(session_payload, raw_import.id, adapter)
                self.db.add(session_model)
                created += 1
            except Exception as exc:  # noqa: BLE001
                warning = f"session idx={idx} skipped: {exc}"
                warnings.append(warning)
                logger.warning(warning)

        self.db.commit()
        return {
            "raw_import_id": str(raw_import.id),
            "sessions_imported": created,
            "warnings": warnings,
            "variant": adapter.name,
        }

    def transform_session(
        self, data: Dict[str, Any], raw_import_id: Any, adapter: VariantAdapter
    ) -> SessionModel:
        session_date = self.safe_parse_date(data.get("date") or data.get("fecha"))
        tags = self.normalize_tags(data.get("tags") or data.get("session_tags"))
        session = SessionModel(
            raw_import_id=raw_import_id,
            source_session_id=data.get("id")
            or data.get("session_id")
            or data.get("workout_id"),
            date=session_date,
            weekday=data.get("weekday") or self.infer_weekday(session_date),
            title=data.get("title") or data.get("name"),
            is_rest_day=bool(data.get("rest_day") or data.get("is_rest_day")),
            deload_week=bool(data.get("deload") or data.get("deload_week")),
            data_status="complete",
            estimated_duration_min=data.get("estimated_duration_min")
            or data.get("duration_minutes")
            or data.get("duration"),
            session_tags=tags,
            source_ref_file=data.get("source_ref_file") or data.get("reference"),
        )

        warmup_payload = data.get("warmup") or {}
        if warmup_payload:
            session.warmup = Warmup(
                quote=warmup_payload.get("quote"),
                mobility=warmup_payload.get("mobility"),
                activation=warmup_payload.get("activation"),
                raw_text=warmup_payload.get("raw_text") or warmup_payload.get("text"),
            )

        blocks = data.get("blocks") or []
        block_models = []
        for order, block_payload in enumerate(blocks, start=1):
            block = adapter.build_block(block_payload, block_order=order)
            block_models.append(block)

        session.blocks = block_models
        if any(block.has_external_reference for block in block_models):
            session.data_status = "external_reference"
        return session

    def choose_adapter(self, sessions: Iterable[Dict[str, Any]]) -> VariantAdapter:
        blocks = [block for session in sessions for block in (session.get("blocks") or [])]
        for adapter in self.adapters:
            if adapter.matches(blocks):
                return adapter
        return self.adapters[-1]

    @staticmethod
    def extract_sessions(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        if isinstance(payload, list):
            return payload
        for candidate in ("sessions", "workouts", "data", "records"):
            records = payload.get(candidate)
            if isinstance(records, list):
                return records
        return []

    @staticmethod
    def safe_parse_date(value: Any) -> Optional[date]:
        if not value:
            return None
        try:
            parsed = parse_datetime(value)
            return parsed.date()
        except Exception:
            logger.warning("no se pudo parsear la fecha %s", value)
            return None

    @staticmethod
    def infer_weekday(session_date: Optional[date]) -> Optional[str]:
        if not session_date:
            return None
        return session_date.strftime("%A")

    @staticmethod
    def normalize_tags(value: Any) -> Optional[List[str]]:
        if isinstance(value, list):
            return [str(item).strip() for item in value if item]
        if isinstance(value, str):
            return [tag.strip() for tag in value.split(",") if tag.strip()]
        return None
