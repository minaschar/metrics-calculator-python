"""Test-wide setup.

Forces Qt onto the offscreen platform plugin so the GUI smoke tests run
without a display (CI, headless dev boxes). Must happen before PySide6 is
imported anywhere.
"""

from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
