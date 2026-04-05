from __future__ import annotations

from calendar import monthrange
from datetime import date
from typing import Any, Dict, List, Tuple

from .report import Report


WEEKDAYS_ES = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]


def parse_date(value: Any) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(str(value))
    except Exception:
        return None


def weekday_label(value: date) -> str:
    return WEEKDAYS_ES[value.weekday()]


def validate_calendar(items: List[Dict[str, Any]], report: Report, strict: bool) -> Tuple[str | None, int | None]:
    dates: List[date] = []
    for idx, item in enumerate(items):
        d = parse_date(item.get("date"))
        if not d:
            report.error("fecha inválida o ausente", date=item.get("date"), index=idx)
            continue
        dates.append(d)

        if item.get("day_id") and item.get("day_id") != item.get("date"):
            report.error("day_id no coincide con date", date=item.get("date"), index=idx)

        if item.get("weekday"):
            expected = weekday_label(d)
            if str(item.get("weekday")) != expected:
                msg = f"weekday incorrecto (esperado {expected}, recibido {item.get('weekday')})"
                if strict:
                    report.error(msg, date=item.get("date"), index=idx)
                else:
                    report.warning(msg, date=item.get("date"), index=idx)

    if not dates:
        return None, None

    first = dates[0]
    month_key = f"{first.year:04d}-{first.month:02d}"
    for idx, item in enumerate(items):
        d = parse_date(item.get("date"))
        if not d:
            continue
        if d.year != first.year or d.month != first.month:
            report.error("archivo contiene más de un mes/año", date=item.get("date"), index=idx)

    expected_days = monthrange(first.year, first.month)[1]
    report.meta["month"] = month_key
    report.meta["expected_days"] = expected_days
    report.meta["actual_days"] = len(items)

    if len(items) != expected_days:
        report.error("número de días no coincide con el calendario")

    seen = {}
    for idx, item in enumerate(items):
        day = item.get("date")
        if day in seen:
            report.error("fecha duplicada", date=day, index=idx)
        else:
            seen[day] = idx

    missing = []
    for day in range(1, expected_days + 1):
        key = f"{first.year:04d}-{first.month:02d}-{day:02d}"
        if key not in seen:
            missing.append(key)
    if missing:
        report.error(f"días faltantes: {', '.join(missing)}")

    sorted_dates = sorted(dates)
    if dates != sorted_dates:
        msg = "fechas no están en orden cronológico"
        if strict:
            report.error(msg)
        else:
            report.warning(msg)

    return month_key, expected_days
