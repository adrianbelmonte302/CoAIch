import argparse
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session import SessionLocal
from app.importer.program_day import ProgramDayImporter
from app.importer.v1_adapter import session_model_to_program_day
from app.models.session import Session as SessionModel
from app.models.session_block import SessionBlock


def main() -> None:
    parser = argparse.ArgumentParser(description="Migra sesiones v1 a program_days v2")
    parser.add_argument("--overwrite", action="store_true", help="reescribe duplicados en program_days")
    parser.add_argument("--only-new", action="store_true", help="solo importa nuevos (ignora overwrite)")
    parser.add_argument("--dry-run", action="store_true", help="simula sin escribir en DB")
    parser.add_argument("--limit", type=int, default=None, help="limita cantidad de sesiones migradas")
    args = parser.parse_args()

    with SessionLocal() as db:
        stmt = (
            select(SessionModel)
            .options(
                selectinload(SessionModel.warmup),
                selectinload(SessionModel.blocks).selectinload(SessionBlock.exercises_raw),
            )
            .order_by(SessionModel.date.desc().nullslast())
        )
        sessions = db.scalars(stmt).all()
        if args.limit is not None:
            sessions = sessions[: max(0, args.limit)]

        payload = [session_model_to_program_day(session) for session in sessions]
        importer = ProgramDayImporter(db)
        result = importer.import_payload(
            source_file="legacy_db_migration",
            source_month="legacy",
            payload=payload,
            overwrite=args.overwrite,
            only_new=args.only_new,
            dry_run=args.dry_run,
        )
        print(result)


if __name__ == "__main__":
    main()
