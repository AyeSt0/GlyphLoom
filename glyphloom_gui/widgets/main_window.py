"""Main window placeholder for Stage 0."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QMainWindow, QVBoxLayout, QWidget


class MainWindow(QMainWindow):
    """Minimal window that presents the GlyphLoom banner."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("GlyphLoom Studio (Alpha)")
        self.resize(640, 360)

        label = QLabel("GlyphLoom Studio\nStage 0 Skeleton", self)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        container = QWidget(self)
        layout = QVBoxLayout(container)
        layout.addWidget(label)

        self.setCentralWidget(container)
