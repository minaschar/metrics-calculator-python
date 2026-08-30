"""Diagnostics surfaced to callers instead of being printed and dropped."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

Severity = Literal["warning", "error"]


@dataclass(frozen=True, slots=True)
class Diagnostic:
    path: Path
    message: str
    severity: Severity = "warning"

    def __str__(self) -> str:
        return f"[{self.severity}] {self.path}: {self.message}"
