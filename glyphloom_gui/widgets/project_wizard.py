"""Stage 1 GUI 项目向导：收集配置并调用 core pipeline。"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from glyphloom_core.core.config_loader import load_project_config
from glyphloom_core.core.models import PipelineResult, ProjectConfig
from glyphloom_core.core.pipeline import run_project

# 记忆用户最近选择的路径，提升后续体验（不持久化到文件，只在会话内记忆）
_LAST_SOURCE_DIR: Optional[Path] = None
_LAST_OUTPUT_DIR: Optional[Path] = None


class _PipelineWorker(QThread):
    """后台线程执行 pipeline，避免阻塞 UI。"""

    success = Signal(PipelineResult)
    error = Signal(Exception)

    def __init__(self, config: ProjectConfig) -> None:
        super().__init__()
        self._config = config

    def run(self) -> None:
        try:
            result = run_project(self._config)
            self.success.emit(result)
        except Exception as exc:  # noqa: BLE001 简化线程内异常处理
            self.error.emit(exc)


class ProjectWizardDialog(QDialog):
    """简易项目向导：选择源表 + 输出目录 + LLM 配置，然后调用 pipeline。"""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("新建 Excel 本地化项目")
        self.resize(520, 340)

        # 预加载默认配置，后续仅对用户覆盖的字段做最小更新
        self._base_config: ProjectConfig = load_project_config()
        self._worker: Optional[_PipelineWorker] = None

        self.source_edit = QLineEdit(str(self._base_config.source.path))
        self.output_edit = QLineEdit(str(self._base_config.output_dir))
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["openai"])
        self.provider_combo.setCurrentText(self._base_config.translator.provider)
        self.model_edit = QLineEdit(self._base_config.translator.model)
        self.api_key_env_edit = QLineEdit(self._base_config.translator.api_key_env)
        self.status_label = QLabel("")

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("请选择源表文件、输出目录和基础 LLM 配置："))
        layout.addLayout(self._build_form())
        layout.addLayout(self._build_buttons())
        layout.addWidget(self.status_label)

    def _build_form(self) -> QFormLayout:
        """构建表单区：源表、输出目录、LLM 配置。"""

        form = QFormLayout()

        form.addRow(
            "源文件路径（Excel/CSV）",
            self._with_browse(self.source_edit, self._choose_source),
        )
        form.addRow(
            "输出目录（可留空默认）",
            self._with_browse(self.output_edit, self._choose_output),
        )
        form.addRow("LLM Provider", self.provider_combo)
        form.addRow("模型（model）", self.model_edit)
        form.addRow("api_key_env", self.api_key_env_edit)
        return form

    def _build_buttons(self) -> QHBoxLayout:
        """底部操作按钮：取消/开始翻译。"""

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)

        self.start_btn = QPushButton("开始翻译")
        self.start_btn.clicked.connect(self._start_pipeline)

        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(self.start_btn)
        return btn_layout

    def _with_browse(self, line_edit: QLineEdit, chooser) -> QWidget:
        """封装带浏览按钮的输入行。"""

        container = QWidget(self)
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(line_edit)
        browse_btn = QPushButton("浏览…", container)
        browse_btn.clicked.connect(chooser)
        layout.addWidget(browse_btn)
        return container

    def _choose_source(self) -> None:
        """选择 Excel/CSV 源文件。"""

        start_dir = _LAST_SOURCE_DIR or self._base_config.source.path.parent
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择 Excel/CSV 源文件",
            str(start_dir),
            "表格文件 (*.xlsx *.xls *.csv)",
        )
        if file_path:
            path = Path(file_path)
            self.source_edit.setText(file_path)
            self._remember_source(path)

    def _choose_output(self) -> None:
        """选择输出目录。"""

        start_dir = _LAST_OUTPUT_DIR or self._base_config.output_dir
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "选择输出目录",
            str(start_dir),
        )
        if dir_path:
            path = Path(dir_path)
            self.output_edit.setText(dir_path)
            self._remember_output(path)

    def _build_config(self) -> ProjectConfig:
        """根据用户输入构造 ProjectConfig（在默认配置上做最小覆盖）。"""

        source_path = Path(self.source_edit.text()).expanduser()
        if not source_path.exists():
            raise FileNotFoundError(f"源文件不存在：{source_path}")

        output_dir_text = self.output_edit.text().strip()
        output_dir = (
            Path(output_dir_text) if output_dir_text else self._base_config.output_dir
        )

        translator_update = {
            "provider": self.provider_combo.currentText(),
            "model": self.model_edit.text().strip()
            or self._base_config.translator.model,
            "api_key_env": self.api_key_env_edit.text().strip()
            or self._base_config.translator.api_key_env,
        }

        config = self._base_config.model_copy(
            update={
                "source": self._base_config.source.model_copy(
                    update={"path": source_path}
                ),
                "output_dir": output_dir,
                "translator": self._base_config.translator.model_copy(
                    update=translator_update
                ),
            }
        )
        return config

    def _start_pipeline(self) -> None:
        """在后台线程执行 core 流水线，展示结果或错误信息。"""

        if self._worker is not None and self._worker.isRunning():
            return
        try:
            config = self._build_config()
            self._remember_source(config.source.path)
            self._remember_output(config.output_dir)
        except Exception as exc:  # noqa: BLE001 简化 GUI 异常提示
            self._show_error(exc)
            return

        self._set_running(True)
        self._worker = _PipelineWorker(config)
        self._worker.success.connect(self._on_success)
        self._worker.error.connect(self._on_error)
        self._worker.finished.connect(lambda: self._set_running(False))
        self._worker.start()

    def _on_success(self, result) -> None:
        """流水线成功完成后的提示。"""

        files_text = "\n".join(str(p) for p in result.created_files) or "无输出文件"
        steps_text = "\n".join(f"- {s.name}: {s.description}" for s in result.steps)
        QMessageBox.information(
            self,
            "流水线完成",
            f"执行成功！\n输出目录：{result.output_dir}\n输出文件：\n{files_text}\n\n步骤：\n{steps_text}",
        )
        self.accept()

    def _on_error(self, exc: Exception) -> None:
        """流水线执行失败，展示友好错误。"""

        self._show_error(exc)

    def _set_running(self, running: bool) -> None:
        """控制按钮状态与状态提示，避免 UI 阻塞无反馈。"""

        self.start_btn.setEnabled(not running)
        self.status_label.setText("正在执行，请稍候…" if running else "")

    def _remember_source(self, path: Path) -> None:
        """记忆上次选择的源文件目录。"""

        global _LAST_SOURCE_DIR
        _LAST_SOURCE_DIR = path.parent

    def _remember_output(self, path: Path) -> None:
        """记忆上次选择的输出目录。"""

        global _LAST_OUTPUT_DIR
        _LAST_OUTPUT_DIR = path

    def _show_error(self, exc: Exception) -> None:
        """友好展示常见错误，并提示可能的检查点。"""

        hint = ""
        if isinstance(exc, FileNotFoundError):
            hint = "\n请确认源文件路径是否正确。"
        elif isinstance(exc, ValueError):
            hint = "\n检查配置的列名是否存在于 Excel/CSV 中。"

        QMessageBox.critical(self, "执行失败", f"发生错误：\n{exc}{hint}")
