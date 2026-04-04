#!/usr/bin/env python3
import argparse
import json
import os
import sys
from typing import Any, Dict, List

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from pydantic import ValidationError  # noqa: E402

from app.schemas.program_day_import import ProgramDayImportSchema  # noqa: E402


def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def has_training_content(item: Dict[str, Any]) -> bool:
    if item.get("is_rest_day") or item.get("day_type") == "rest":
        return False
    flow = item.get("session_flow") or {}
    variants = flow.get("variants") or []
    for variant in variants:
        blocks = variant.get("blocks") or []
        for block in blocks:
            prescription = block.get("prescription") or {}
            sub_blocks = prescription.get("sub_blocks") or []
            for sub in sub_blocks:
                if sub.get("description"):
                    return True
                if sub.get("exercises"):
                    return True
        if variant.get("notes_literal"):
            return True
    if flow.get("shared_blocks"):
        return True
    if flow.get("general_warmup"):
        return True
    return False


def validate_item(idx: int, item: Dict[str, Any]) -> List[str]:
    issues: List[str] = []
    try:
        ProgramDayImportSchema.model_validate(item)
    except ValidationError as exc:
        issues.append(f"idx={idx} schema inválido: {exc}")
        return issues

    if not item.get("date"):
        issues.append(f"idx={idx} sin date")
    if not item.get("display_title"):
        issues.append(f"idx={idx} sin display_title")
    if not item.get("weekday"):
        issues.append(f"idx={idx} sin weekday")
    if not item.get("session_flow"):
        issues.append(f"idx={idx} sin session_flow")
    return issues


def main() -> None:
    parser = argparse.ArgumentParser(description="Valida JSON de program_days para importación.")
    parser.add_argument("path", help="Ruta al JSON a validar")
    args = parser.parse_args()

    data = load_json(args.path)
    if not isinstance(data, list):
        print("ERROR: el JSON debe ser una lista de program_days", file=sys.stderr)
        sys.exit(2)

    errors: List[str] = []
    warnings: List[str] = []
    no_training: List[str] = []

    for idx, item in enumerate(data):
        if not isinstance(item, dict):
            errors.append(f"idx={idx} no es un objeto JSON")
            continue
        issues = validate_item(idx, item)
        errors.extend(issues)
        if not has_training_content(item):
            no_training.append(item.get("date") or item.get("day_id") or f"idx={idx}")

        if item.get("schema_version", "").startswith("2."):
            if item.get("entity_type") != "program_day":
                warnings.append(f"idx={idx} entity_type distinto de program_day")

    print(f"Items totales: {len(data)}")
    print(f"Errores: {len(errors)}")
    print(f"Avisos: {len(warnings)}")
    print(f"Días sin entreno: {len(no_training)}")

    if warnings:
        print("\nAvisos:")
        for w in warnings:
            print(f"- {w}")

    if no_training:
        print("\nDías sin entreno:")
        for d in no_training:
            print(f"- {d}")

    if errors:
        print("\nErrores:")
        for e in errors:
            print(f"- {e}")
        sys.exit(1)

    print("\nOK: JSON válido para importación.")


if __name__ == "__main__":
    main()
