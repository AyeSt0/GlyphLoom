# GlyphLoom

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![License: GPL v3](https://img.shields.io/badge/License-GPL--3.0-orange.svg)](LICENSE)

游戏文本本地化流水线工具（阶段：模板闭环 + 占位符识别/基础 QA 进行中），核心与 GUI 解耦，开箱即用的 Excel → 假翻译 → 导出体验。

## 现阶段快照
- ✅ Stage 1：配置/Adapter/Translator/CLI/GUI 最小闭环完成（假翻译）
- ✅ Stage 2.1：占位符提取（解析器 + 动态模式注册，支持多括号/嵌套/空格）
- ⏳ Stage 2.2+：QA 模型/规则/导出/CLI 开关 按 roadmap 推进中
- 路线图：见 `docs/roadmap.md`（内部详版），公开概览如下：
  - 占位符识别：已完成提取/白名单
  - QA 框架：Issue/QAResult 模型已建，占位符一致性规则待接入
  - 导出/CLI 开关：后续集成，默认不开启 QA

## 功能亮点
- **核心解耦**：Python 3.12+，配置使用 pydantic，core 与 GUI 独立。
- **占位符提取**：解析器支持 `{name}`、`%s`、`{{VALUE}}`、`<tag>` 等，多括号/嵌套/空格，动态模式可注册。
- **表格适配器**：读取 Excel/CSV，自动补齐 `translation` / `status` / `qa_flags` 列。
- **Translator（假实现）**：为每行文本添加 `[provider:model]` 前缀，不访问网络。
- **Pipeline**：`extract -> translate -> export`，CLI 一条命令跑通。
- **GUI 向导**：选择 Excel/CSV、输出目录、LLM 配置，一键假翻译。

## 快速开始
1) 安装（含开发/GUI 依赖）：
```bash
pip install -e ".[dev]"   # 仅核心可用 pip install -e .
```
2) 运行 CLI 假翻译：
```bash
python -m glyphloom_core.cli translate --config examples/config.yaml
```
3) 运行 GUI 向导：
```bash
python -m glyphloom_gui
```
选择 `examples/template_basic.xlsx`，点击“开始翻译”，输出写入 `output/`。

## 验证与测试
- 全量测试：`python -m pytest`
- 占位符提取单测：`python -m pytest tests/test_qa_placeholders.py`

## 项目结构（摘录）
```
glyphloom_core/      # 核心：配置/Adapter/Translator/Pipeline
glyphloom_gui/       # GUI 壳层：项目向导
examples/            # 示例模板与样例
docs/                # 文档（overview / roadmap / prompts）
tests/               # 测试用例合集
```

## 更多文档
- `docs/project_overview.md`：项目概览与设计意图
- `docs/roadmap.md`：阶段目标与勾选进度
- `docs/dev_ai_assistant_prompts.md`：AI 协作规则

## 许可证
GPL-3.0-or-later
