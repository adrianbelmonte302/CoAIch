import argparse
import json
import logging
from pathlib import Path

from sqlalchemy.exc import SQLAlchemyError

from app.db.session import SessionLocal
from app.importer.manager import SessionImporter

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")


def infer_month_from_filename(filename: str) -> str:
    parts = filename.lower().replace("-", "_").split("_")
    for part in parts:
        if part in {"octubre", "noviembre", "diciembre"}:
            return part
    return "unknown"


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def import_file(db, path: Path, overwrite: bool, only_new: bool, dry_run: bool, limit: int | None):
    importer = SessionImporter(db)
    payload = load_json(path)
    month = infer_month_from_filename(path.name)
    result = importer.import_payload(
        path.name,
        month,
        payload,
        overwrite=overwrite,
        only_new=only_new,
        dry_run=dry_run,
        limit=limit,
    )
    logger.info(
        "imported %s (%s) total=%s created=%s dup_file=%s dup_db=%s overwritten=%s warnings=%s",
        path.name,
        month,
        result["sessions_total"],
        result["sessions_imported"],
        result["duplicates_in_file"],
        result["duplicates_in_db"],
        result["overwritten"],
        result["variant"],
        len(result["warnings"]),
    )
    for warning in result["warnings"]:
        logger.warning("warning: %s", warning)


def main():
    parser = argparse.ArgumentParser(description="Importa archivos JSON de entrenamientos CoAIch")
    parser.add_argument("paths", nargs="+", help="archivos JSON o carpetas con archivos JSON")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="reescribe sesiones duplicadas (mismo contenido) en la base de datos",
    )
    parser.add_argument(
        "--only-new",
        action="store_true",
        help="solo importa sesiones nuevas (ignora overwrite)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="simula la importacion sin escribir en la base de datos",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="limita el numero de sesiones importadas por archivo",
    )
    args = parser.parse_args()

    resolved_paths = []
    for raw in args.paths:
        candidate = Path(raw)
        if candidate.is_dir():
            resolved_paths.extend(sorted(candidate.glob("*.json")))
        else:
            resolved_paths.append(candidate)

    if not resolved_paths:
        logger.error("no se encontraron archivos para importar")
        return

    with SessionLocal() as db:
        for path in resolved_paths:
            if not path.exists():
                logger.warning("archivo no encontrado: %s", path)
                continue

            try:
                import_file(
                    db,
                    path,
                    overwrite=args.overwrite,
                    only_new=args.only_new,
                    dry_run=args.dry_run,
                    limit=args.limit,
                )
            except SQLAlchemyError as exc:
                logger.error("error al importar %s: %s", path, exc)


if __name__ == "__main__":
    main()
