#!/usr/bin/env python3
import argparse
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.validators.program_days import validate_program_days_json  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Valida JSON de program_days para importación.")
    parser.add_argument("path", help="Ruta al JSON a validar")
    parser.add_argument("--strict", action="store_true", help="convierte algunos warnings en errores")
    parser.add_argument("--json-report", action="store_true", help="salida JSON en stdout")
    args = parser.parse_args()

    report = validate_program_days_json(args.path, strict=args.strict)

    if args.json_report:
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(report.to_text())

    if report.result == "PASS":
        sys.exit(0)
    if report.result == "PASS WITH WARNINGS":
        sys.exit(1)
    sys.exit(2)


if __name__ == "__main__":
    main()
