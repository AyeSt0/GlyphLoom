"""Stage 1 GUI 主窗口，新增“新建 Excel 本地化项目”入口。"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QLabel,
    QMainWindow,
    QPushButton,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from .project_wizard import ProjectWizardDialog


class MainWindow(QMainWindow):
    """主窗口：展示 Banner，并提供“新建 Excel 本地化项目”入口。"""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("GlyphLoom Studio (Alpha)")
        self.resize(640, 360)

        label = QLabel("GlyphLoom Studio\nStage 1 模板闭环 (假翻译)", self)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        new_project_btn = QPushButton("新建 Excel 本地化项目", self)
        new_project_btn.clicked.connect(self.open_project_wizard)

        container = QWidget(self)
        layout = QVBoxLayout(container)
        layout.addWidget(label)
        layout.addWidget(new_project_btn)
        layout.addStretch()

        self.setCentralWidget(container)

        self._init_menu_toolbar()

    def _init_menu_toolbar(self) -> None:
        """初始化菜单和工具栏入口，触发项目向导。"""

        new_project_action = QAction("新建 Excel 本地化项目", self)
        new_project_action.triggered.connect(self.open_project_wizard)

        project_menu = self.menuBar().addMenu("项目(&P)")
        project_menu.addAction(new_project_action)

        toolbar = QToolBar("项目")
        toolbar.addAction(new_project_action)
        self.addToolBar(toolbar)

    def open_project_wizard(self) -> None:
        """弹出项目向导，收集配置并调用 core pipeline。"""

        dialog = ProjectWizardDialog(self)
        dialog.exec()
