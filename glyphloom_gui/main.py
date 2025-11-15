"""Entry point for launching the GlyphLoom GUI."""

from __future__ import annotations

import sys

from .app import create_application
from .widgets.main_window import MainWindow


def main() -> int:
    app = create_application()
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
