# GlyphLoom 当前进度快照（Stage 1）

> 便于人类/AI 快速了解：做到哪了、还能做什么。

最后更新：2025-11-16

---

## 1. 当前所处阶段

- 当前大阶段：**Stage 1（模板闭环 + 云端 LLM）**
- 子任务完成情况：
  - ✅ 1.1 配置模型与加载扩展
  - ✅ 1.2 TableAdapter 数据读写骨架
  - ✅ 1.3 OpenAI HTTP Translator 最小实现（假翻译）
  - ✅ 1.4 Pipeline/CLI 模板闭环整合
  - ✅ 1.5 GUI 模板项目向导（含 1.5.x 异步/体验优化）

---

## 2. 已完成内容摘录

### 2.1 配置模型与加载（1.1）

- `glyphloom_core/core/models.py`
  - 定义：`ProjectConfig` / `SourceConfig` / `TableAdapterConfig` / `TranslatorConfig`
  - `ProjectConfig`：`extra="forbid"`；`output_dir` 使用 `default_factory=lambda: Path("output")`
- `glyphloom_core/core/config_loader.py`
  - 解析 YAML：`project.source` / `project.table_adapter` / `project.translator`，并合并默认值

### 2.2 TableAdapter（1.2）

- `glyphloom_core/adapters/base.py`：抽象基类，内部 `_data` + 只读属性 `data`
- `glyphloom_core/adapters/table_adapter.py`：
  - 读取 Excel/CSV（支持 `sheet_name`，CSV 使用 `encoding`）
  - 校验 `source_column`，缺失抛 `ValueError`（含文件路径）
  - 补齐列：`translation` / `status` / `qa_flags`
  - 保存为 Excel/CSV（复用输入文件名）
- `tests/test_table_adapter.py`：验证“读取 → 补列 → 导出”闭环

### 2.3 Translator（OpenAI HTTP）（1.3）

- `glyphloom_core/translators/base.py`：抽象 `BaseTranslator`
- `glyphloom_core/translators/openai_http.py`：
  - 假翻译：`translate_batch` 为每行添加 `[provider:model]` 前缀，不访问网络
  - 从 `TranslatorConfig` 读取 `provider`/`model`/`base_url`/`api_key_env`
- `tests/test_translator_openai_http.py`：长度一致、前缀校验

### 2.4 Pipeline & CLI 闭环（1.4）

- `glyphloom_core/core/pipeline.py`：
  - `run_project` 串联 `extract -> translate -> export`
  - `_run_stage` 记录耗时/成功；`PipelineResult` 返回 `created_files`
  - 翻译阶段校验行数一致，写入 `translation` 列
- `glyphloom_core/cli.py`：
  - 子命令：`translate`（默认）
  - 参数：`-c/--config`、`--dry-run`
  - 调用 `run_project`，输出 success/failed 与产物列表
- `tests/test_pipeline.py`：默认配置下跑假翻译，校验 translation 列前缀与行数

### 2.5 GUI 模板项目向导（1.5 + 1.5.x 体验优化）

- `glyphloom_gui/widgets/main_window.py`：按钮/菜单/工具栏入口 → 项目向导
- `glyphloom_gui/widgets/project_wizard.py`：
  - 表单：源文件浏览、输出目录浏览（可留空）、LLM 配置（provider/model/api_key_env 默认取配置）
  - 配置构造：基于 `load_project_config()`，仅覆盖 `source.path` / `output_dir` / `translator`
  - 执行：QThread 后台调用 `run_project`，避免 UI 卡顿；状态提示“正在执行，请稍候…”
  - 体验：会话内记住上次源/输出目录；FileNotFoundError/ValueError 提示友好检查点
  - 结果：成功弹窗列出输出目录/文件与 PipelineStep 描述；异常弹窗提示错误

---

## 3. 尚未完成 / 下一步计划

- 转向 Stage 2：占位符识别 + 基础 QA
- 后续 GUI 可再迭代（进度条/日志面板/多任务队列）放入 Stage 2+ 规划

---

## 4. 快速验证与命令

- CLI 假翻译：`python -m glyphloom_core.cli translate --config examples/config.yaml`
- GUI 向导：`python -m glyphloom_gui`，选择 `examples/template_basic.xlsx`，点击“开始翻译”
- 测试：`python -m pytest`

---

## 5. 对未来会话的使用说明

在新对话加载本项目时：

1. 提供关键文件：
   - `docs/project_overview.md`
   - `docs/roadmap.md`
   - `docs/dev_ai_assistant_prompts.md`
   - `docs/design_notes/scope_and_nongoals.md`
   - `docs/current_status.md`
2. 说明角色：
   - “你是 GlyphLoom 的 PM + 指令工程师 + Reviewer，不写代码，只帮我写 Codex 子任务指令、做代码 review、同步 roadmap。”
3. 继续从当前阶段（Stage 2 起）推进。

---

## 6. 当前目录结构（截取深度 3，便于对照与找文件）

```
.github/                     # CI 配置目录
  workflows/
    ci.yml                   # GitHub Actions：ruff/black/pytest
docs/                        # 文档目录
  design_notes/
    config_and_secrets.md    # 配置与密钥管理约定
    platforms.md             # 跨平台约束与策略
    scope_and_nongoals.md    # 范围与非目标
  current_status.md          # 当前进度快照（本文件）
  dev_ai_assistant_prompts.md# AI 协作规则/System Prompt
  dev_workflow.md            # 开发流程与常用命令
  project_overview.md        # 项目概览
  roadmap.md                 # 开发路线图
examples/                    # 示例资源
  renpy_demo/
    game/
      script.rpy             # Ren'Py 示例脚本
    README.md                # Ren'Py 示例说明
  README.md                  # 示例总览
  template_basic.xlsx        # 基础表格模板
  template_with_placeholders.xlsx # 含占位符表格模板
glyphloom_core/              # 核心逻辑（CLI/Adapter/Translator/Pipeline）
  adapters/
    base.py                  # Adapter 抽象基类
    table_adapter.py         # 表格适配器实现
  core/
    __init__.py
    config_loader.py         # YAML -> ProjectConfig 解析
    models.py                # 配置/结果模型
    pipeline.py              # 核心流水线（extract/translate/export）
  translators/
    base.py                  # Translator 抽象基类
    openai_http.py           # OpenAI HTTP 假翻译实现
  __init__.py
  __main__.py                # 支持 python -m glyphloom_core
  cli.py                     # CLI 入口（translate/dry-run）
glyphloom_gui/               # GUI 壳层（不含业务逻辑）
  widgets/
    __init__.py
    main_window.py           # 主窗口（入口按钮/菜单）
    project_wizard.py        # 项目向导对话框
  __init__.py
  __main__.py                # 支持 python -m glyphloom_gui
  app.py                     # QApplication 封装
  main.py                    # GUI 启动入口
local_notes/                 # 本地笔记（不随发行）
  ai_prompts.local.md        # 本地 AI Prompt 备忘
scripts/                     # 自动化脚本
  __init__.py
  auto_commit.py             # 提交前自动检查/递增版本
  check_quality.ps1          # 统一质量检查入口
  dev_setup.ps1              # 开发环境初始化
  watch_and_commit.ps1       # 监听保存自动提交
tests/                       # 测试用例
  __init__.py
  test_pipeline.py           # Pipeline 闭环测试
  test_smoke_core.py         # Core 冒烟
  test_table_adapter.py      # TableAdapter 测试
  test_translator_openai_http.py # Translator 假翻译测试
.gitignore                   # Git 忽略配置
env.example                  # 环境变量示例
LICENSE                      # 许可证
pyproject.toml               # 项目/依赖配置
README.md                    # 项目门面说明
VERSION                      # 版本号记录
```
