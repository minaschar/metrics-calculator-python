"""Frozen-app entry point.

PyInstaller needs a script to bootstrap; this is it. Keeping it out of the
importable package means the console-script entry point and the bundled
app share exactly one code path -- ``metrics_calculator.gui.app.main``.
"""

from __future__ import annotations

import sys

from metrics_calculator.gui.app import main

if __name__ == "__main__":
    sys.exit(main())
