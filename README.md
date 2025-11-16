# GlyphLoom

> 游戏文本本地化流水线工具（Stage 1）。当前实现：配置/Adapter/Translator 假翻译 + Pipeline/CLI/GUI 骨架。

## 特性概览
- Python 3.12+
- pydantic 配置模型（ProjectConfig/SourceConfig/TableAdapterConfig/TranslatorConfig）
- TableAdapter：读取 Excel/CSV，补齐 translation/status/qa_flags 列
- Translator（假实现）：为每行文本添加 `[provider:model]` 前缀
- Pipeline：extract -> translate -> export，CLI `python -m glyphloom_core.cli translate --config config.yaml`
- GUI：`python -m glyphloom_gui` 打开向导，选择 Excel/CSV 后一键跑假翻译

## 快速开始
1) 安装（核心 + GUI 依赖）：
```bash
pip install -e ".[dev]"  # 或手动安装 PySide6 以运行 GUI
```
2) 运行 CLI 假翻译：
```bash
python -m glyphloom_core.cli translate --config examples/config.yaml
```
3) 运行 GUI 向导：
```bash
python -m glyphloom_gui
```

## 文档
- `docs/project_overview.md`：项目概览与设计意图
- `docs/roadmap.md`：阶段目标与勾选进度
- `docs/dev_ai_assistant_prompts.md`：AI 协作规则

## 许可
GPL-3.0-or-later
