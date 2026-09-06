"""`python -m metrics_calculator` and the installed `metrics-calculator`
script both land here."""

from __future__ import annotations

from .cli.app import app

if __name__ == "__main__":
    app()
