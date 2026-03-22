import json

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.importer.manager import SessionImporter
from app.models.raw_import import RawImport
from app.models.session import Session as SessionModel


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


OCTOBER_SAMPLE = {
    "workouts": [
        {
            "id": "oct-1",
            "date": "2025-10-07",
            "weekday": "martes",
            "title": "EMOM Clásico",
            "tags": ["metcon", "olympic"],
            "blocks": [
                {
                    "id": "block-EMOM",
                    "title": "Wod",
                    "type": "metcon",
                    "notes": "Mantener ritmo constante",
                    "exercises": [
                        {
                            "name": "Thruster",
                            "format": "AMRAP",
                            "notes": "Peso moderado",
                            "intensity": {"rpe": 9},
                            "sets": 5,
                            "reps": "3-3-3-3-3",
                        }
                    ],
                }
            ],
            "warmup": {"mobility": "shoulder roll", "activation": "band pull aparts"},
        }
    ]
}

NOVEMBER_SAMPLE = {
    "sessions": [
        {
            "session_id": "nov-1",
            "date": "2025-11-11",
            "title": "Fuerza Parte I",
            "blocks": [
                {
                    "id": "block-strength",
                    "title": "Squat",
                    "type": "strength",
                    "prescription": "4 sets x 5 reps @ 80%",
                    "coach_notes": "add tempo on the descend",
                }
            ],
        }
    ]
}

DECEMBER_SAMPLE = {
    "records": [
        {
            "id": "dec-1",
            "date": "2025-12-02",
            "title": "Sesión externa",
            "tags": "recuperación",
            "blocks": [
                {
                    "id": "block-ext",
                    "title": "Cardio",
                    "type": "conditioning",
                    "prescription": "ver datos completos en TrueCoach",
                }
            ],
        }
    ]
}


def test_importer_preserves_raw(db: Session):
    importer = SessionImporter(db)
    result = importer.import_payload("test_oct.json", "octubre", OCTOBER_SAMPLE)
    raw = db.query(RawImport).first()
    assert raw.source_file == "test_oct.json"
    assert raw.source_month == "octubre"
    assert json.dumps(raw.raw_json)  # ensure JSON serializable
    assert result["sessions_imported"] == 1


def test_october_variant_creates_exercises_and_canonical(db: Session):
    importer = SessionImporter(db)
    importer.import_payload("oct.json", "octubre", OCTOBER_SAMPLE)
    session = db.query(SessionModel).first()
    assert session
    assert session.blocks
    block = session.blocks[0]
    assert block.content_mode == "exercise_notes"
    assert block.exercises_raw
    assert block.items_canonical


def test_november_variant_uses_prescription_mode(db: Session):
    importer = SessionImporter(db)
    importer.import_payload("nov.json", "noviembre", NOVEMBER_SAMPLE)
    session = db.query(SessionModel).filter_by(source_session_id="nov-1").first()
    assert session
    block = session.blocks[0]
    assert block.content_mode == "prescription"
    assert block.raw_text == "4 sets x 5 reps @ 80%"
    assert not block.exercises_raw
    assert block.items_canonical


def test_external_reference_flagged_and_raw_available(db: Session):
    importer = SessionImporter(db)
    importer.import_payload("dec.json", "diciembre", DECEMBER_SAMPLE)
    session = db.query(SessionModel).filter_by(source_session_id="dec-1").first()
    assert session
    block = session.blocks[0]
    assert block.has_external_reference
    assert "truecoach" in (block.raw_text or "").lower()
    assert session.data_status == "external_reference"


def test_duplicate_sessions_are_skipped_by_default(db: Session):
    importer = SessionImporter(db)
    importer.import_payload("oct.json", "octubre", OCTOBER_SAMPLE)
    importer.import_payload("oct.json", "octubre", OCTOBER_SAMPLE)
    assert db.query(SessionModel).count() == 1


def test_duplicate_sessions_overwrite_when_flag_enabled(db: Session):
    importer = SessionImporter(db)
    importer.import_payload("oct.json", "octubre", OCTOBER_SAMPLE)
    importer.import_payload("oct.json", "octubre", OCTOBER_SAMPLE, overwrite=True)
    assert db.query(SessionModel).count() == 1


def test_duplicate_sessions_only_new_ignores_overwrite(db: Session):
    importer = SessionImporter(db)
    importer.import_payload("oct.json", "octubre", OCTOBER_SAMPLE)
    importer.import_payload("oct.json", "octubre", OCTOBER_SAMPLE, overwrite=True, only_new=True)
    assert db.query(SessionModel).count() == 1


def test_dry_run_does_not_write(db: Session):
    importer = SessionImporter(db)
    result = importer.import_payload("oct.json", "octubre", OCTOBER_SAMPLE, dry_run=True)
    assert result["sessions_imported"] == 1
    assert db.query(SessionModel).count() == 0


def test_limit_restricts_import_count(db: Session):
    importer = SessionImporter(db)
    payload = {"workouts": OCTOBER_SAMPLE["workouts"] * 2}
    result = importer.import_payload("oct.json", "octubre", payload, limit=1)
    assert result["sessions_imported"] == 1
