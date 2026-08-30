"""Analysis configuration, optionally loaded from TOML."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_INCLUDE: tuple[str, ...] = ("**/*.py",)
# Empty by default so behaviour matches the pre-rewrite engine, which walks
# every .py file it finds with no exclusions at all -- including .venv/,
# site-packages/ and __pycache__/ (see project brief Phase 5, item 8). That
# default changes deliberately in Phase 5; for now this only lets a caller
# opt in to excluding directories, it doesn't change what happens by
# default.
DEFAULT_EXCLUDE: tuple[str, ...] = ()


def _str_tuple(value: object, default: tuple[str, ...]) -> tuple[str, ...]:
    if value is None:
        return default
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise TypeError(f"expected a list of strings, got {value!r}")
    return tuple(value)


def _float_dict(value: object) -> dict[str, float]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise TypeError(f"expected a table, got {value!r}")
    result: dict[str, float] = {}
    for key, raw in value.items():
        if not isinstance(key, str) or not isinstance(raw, (int, float)):
            raise TypeError(f"expected {{metric abbreviation: number}}, got {{{key!r}: {raw!r}}}")
        result[key] = float(raw)
    return result


@dataclass(frozen=True, slots=True)
class AnalysisConfig:
    include: tuple[str, ...] = DEFAULT_INCLUDE
    exclude: tuple[str, ...] = DEFAULT_EXCLUDE
    thresholds: dict[str, float] = field(default_factory=dict)

    @classmethod
    def _from_section(cls, section: dict[str, object]) -> AnalysisConfig:
        return cls(
            include=_str_tuple(section.get("include"), DEFAULT_INCLUDE),
            exclude=_str_tuple(section.get("exclude"), DEFAULT_EXCLUDE),
            thresholds=_float_dict(section.get("thresholds")),
        )

    @classmethod
    def from_toml(cls, path: Path) -> AnalysisConfig:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        return cls._from_section(data)

    @classmethod
    def discover(cls, project_root: Path) -> AnalysisConfig:
        """Looks for `[tool.metrics_calculator]` in pyproject.toml, then a
        standalone metrics-calculator.toml, else falls back to defaults."""
        pyproject = project_root / "pyproject.toml"
        if pyproject.is_file():
            data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
            tool_section = data.get("tool", {})
            section = (
                tool_section.get("metrics_calculator") if isinstance(tool_section, dict) else None
            )
            if isinstance(section, dict):
                return cls._from_section(section)

        standalone = project_root / "metrics-calculator.toml"
        if standalone.is_file():
            return cls.from_toml(standalone)

        return cls()
