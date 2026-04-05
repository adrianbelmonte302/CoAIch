from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class Issue:
    level: str  # "error" | "warning"
    message: str
    date: Optional[str] = None
    index: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        payload = {"level": self.level, "message": self.message}
        if self.date:
            payload["date"] = self.date
        if self.index is not None:
            payload["index"] = self.index
        return payload


class Report:
    def __init__(self) -> None:
        self.issues: List[Issue] = []
        self.meta: Dict[str, Any] = {}

    def add(self, level: str, message: str, date: Optional[str] = None, index: Optional[int] = None) -> None:
        self.issues.append(Issue(level=level, message=message, date=date, index=index))

    def error(self, message: str, date: Optional[str] = None, index: Optional[int] = None) -> None:
        self.add("error", message, date=date, index=index)

    def warning(self, message: str, date: Optional[str] = None, index: Optional[int] = None) -> None:
        self.add("warning", message, date=date, index=index)

    @property
    def errors(self) -> List[Issue]:
        return [issue for issue in self.issues if issue.level == "error"]

    @property
    def warnings(self) -> List[Issue]:
        return [issue for issue in self.issues if issue.level == "warning"]

    @property
    def result(self) -> str:
        if self.errors:
            return "FAIL"
        if self.warnings:
            return "PASS WITH WARNINGS"
        return "PASS"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "result": self.result,
            "errors": [issue.to_dict() for issue in self.errors],
            "warnings": [issue.to_dict() for issue in self.warnings],
            "meta": self.meta,
        }

    def to_text(self) -> str:
        lines = []
        lines.append(f"Validation report for {self.meta.get('file', '')}")
        if "month" in self.meta:
            lines.append(f"Detected month: {self.meta['month']}")
        if "expected_days" in self.meta and "actual_days" in self.meta:
            lines.append(
                f"Expected days: {self.meta['expected_days']} | Actual days: {self.meta['actual_days']}"
            )
        lines.append(f"Errors: {len(self.errors)}")
        lines.append(f"Warnings: {len(self.warnings)}")
        lines.append(f"Result: {self.result}")

        if self.errors:
            lines.append("")
            lines.append("ERRORS")
            for issue in self.errors:
                prefix = f"{issue.date}: " if issue.date else ""
                lines.append(f"- {prefix}{issue.message}")

        if self.warnings:
            lines.append("")
            lines.append("WARNINGS")
            for issue in self.warnings:
                prefix = f"{issue.date}: " if issue.date else ""
                lines.append(f"- {prefix}{issue.message}")

        return "\n".join(lines)
