"""PySide6 desktop front-end for the metrics calculator.

This subpackage is the *only* part of the distribution that imports a UI
toolkit, and nothing under ``metrics_calculator`` outside ``gui`` imports
it back -- the core engine, the registry and the exporters stay
UI-agnostic (``import metrics_calculator`` pulls in no Qt). The app is one
consumer of :func:`metrics_calculator.analyze` among several; the CLI is
another.

PySide6 is an optional dependency (``pip install
metrics-calculator-python[gui]``); importing this package without it
raises a clear error rather than an obscure ``ModuleNotFoundError`` deep
in a widget module.
"""

from __future__ import annotations

try:
    import PySide6 as _PySide6  # noqa: F401
except ModuleNotFoundError as exc:  # pragma: no cover - import guard
    raise ModuleNotFoundError(
        "The desktop app needs PySide6. Install it with:\n"
        "    pip install 'metrics-calculator-python[gui]'"
    ) from exc

__all__ = ["main"]


def main(argv: list[str] | None = None) -> int:
    """Console-script entry point (``metrics-calculator-gui``)."""
    from .app import main as _main

    return _main(argv)
