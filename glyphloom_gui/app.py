"""Utilities for creating GlyphLoom GUI applications."""

from __future__ import annotations

import sys
from typing import Optional

try:
    from PySide6.QtWidgets import QApplication
except ImportError as exc:  # pragma: no cover - import guard
    raise ImportError(
        "PySide6 is required for glyphloom_gui. Install with `pip install glyphloom[gui]`."
    ) from exc


def create_application() -> QApplication:
    """Return a shared QApplication instance."""

    app: Optional[QApplication] = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app
