import json

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.importer.program_day import ProgramDayImporter
from app.importer.v1_adapter import v1_payload_to_v2
from app.models.program_day import ProgramDay
from app.models.raw_import import RawImport


@pytest.fixture
def engine():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def db(engine):
    SessionLocal = sessionmaker(bind=engine, future=True)
    with SessionLocal() as session:
        yield session


V1_SAMPLE = {
    "workouts": [
        {
            "id": "oct-1",
            "date": "2025-10-07",
            "weekday": "martes",
            "title": "EMOM Clasico",
            "tags": ["metcon", "olympic"],
            "blocks": [
                {
                    "id": "block-EMOM",
                    "title": "Wod",
                    "type": "metcon",
                    "notes": "Mantener ritmo",
                    "exercises": [
                        {
                            "name": "Thruster",
                            "format": "AMRAP",
                            "notes": "Peso moderado",
                        }
                    ],
                }
            ],
            "warmup": {"mobility": "shoulder roll", "activation": "band pull aparts"},
        }
    ]
}


def test_v1_adapter_outputs_program_day_schema():
    payload = v1_payload_to_v2(V1_SAMPLE)
    assert isinstance(payload, list)
    assert payload[0]["entity_type"] == "program_day"
    assert payload[0]["schema_version"].startswith("2.")
    assert payload[0]["session_flow"]["variants"][0]["blocks"]


def test_program_day_importer_preserves_raw_payload(db: Session):
    payload_v2 = v1_payload_to_v2(V1_SAMPLE)
    importer = ProgramDayImporter(db)
    result = importer.import_payload(
        source_file="legacy.json",
        source_month="octubre",
        payload=payload_v2,
        raw_payload=V1_SAMPLE,
    )
    assert result["program_days_imported"] == 1
    assert db.query(ProgramDay).count() == 1
    raw = db.query(RawImport).first()
    assert raw
    assert json.dumps(raw.raw_json)
    assert raw.raw_json == V1_SAMPLE
