"""``QApplication`` bootstrap for the desktop front-end."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from .. import __version__
from .main_window import MainWindow

_HELP = (
    "Usage: metrics-calculator-gui [PROJECT_DIR]\n\n"
    "Opens the desktop app. If PROJECT_DIR is given it is loaded ready to analyse.\n\n"
    "  --version   print the version and exit\n"
    "  --help      show this message and exit"
)

# When set, main() builds the window, pumps the event queue once and
# returns 0 instead of entering the event loop. Used to smoke-test the
# packaged executable in CI, where the app is a windowed (no-console)
# binary that cannot report anything over stdout.
_SELFTEST_ENV = "MC_GUI_SELFTEST"


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv if argv is None else argv)

    if "--version" in args[1:]:
        print(f"metrics-calculator {__version__}")
        return 0
    if "--help" in args[1:] or "-h" in args[1:]:
        print(_HELP)
        return 0

    app = QApplication.instance() or QApplication(args)
    app.setApplicationName("Metrics Calculator")
    app.setOrganizationName("metrics-calculator-python")

    window = MainWindow()

    positional = [a for a in args[1:] if not a.startswith("-")]
    if positional:
        candidate = Path(positional[0])
        if candidate.is_dir():
            window.open_project(candidate)

    window.show()

    if os.environ.get(_SELFTEST_ENV):
        app.processEvents()
        window.close()
        return 0

    return app.exec()


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
