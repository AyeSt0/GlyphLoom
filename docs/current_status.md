# GlyphLoom 当前进度快照（Stage 1）

> 本文件用于让人类/AI 进入项目时，快速了解：做到哪了、还能做什么。

最后更新：请填写日期（例如：2025-11-16）

---

## 1. 当前所处阶段

- 当前大阶段：**Stage 1（模板闭环 + 云端 LLM）**
- 子任务完成情况：
  - ✅ 1.1 配置模型与加载扩展
  - ✅ 1.2 TableAdapter 数据读写骨架
  - ✅ 1.3 OpenAI HTTP Translator 最小实现（假翻译）
  - ✅ 1.4 Pipeline/CLI 模板闭环整合
  - ⏳ 1.5 GUI 模板项目向导（尚未开始）

---

## 2. 已完成内容摘录

### 2.1 配置模型与加载（1.1）

- `glyphloom_core/core/models.py`
  - 已定义：`ProjectConfig` / `SourceConfig` / `TableAdapterConfig` / `TranslatorConfig`
  - `ProjectConfig` 设置：
    - `extra = "forbid"`，防止 YAML 出现未知字段
    - `output_dir` 使用 `default_factory=lambda: Path("output")`
- `glyphloom_core/core/config_loader.py`
  - 能解析 YAML：
    - `project.source`
    - `project.table_adapter`
    - `project.translator`
  - 并合并默认值

### 2.2 TableAdapter（1.2）

- `glyphloom_core/adapters/base.py`
  - 定义 `BaseAdapter` 抽象基类
  - 内部维护 `_data: pd.DataFrame`
  - 提供只读属性 `data` 供上层安全访问
- `glyphloom_core/adapters/table_adapter.py`
  - 支持：
    - 按 `SourceConfig.path` 读取 Excel/CSV（支持 `sheet_name`）
    - CSV 读取使用 `SourceConfig.encoding`
    - 校验 `TableAdapterConfig.source_column` 存在，否则抛 `ValueError`（含文件路径）
    - 根据 `TableAdapterConfig.column_mapping` 自动补齐：
      - `translation`
      - `status`
      - `qa_flags`
  - `save(output_path)`：
    - `.xlsx/.xls` → `to_excel(index=False)`
    - `.csv` → `to_csv(index=False)`
- `tests/test_table_adapter.py`
  - 使用 examples 模板文件完成“读取 → 补列 → 导出”闭环
  - 断言所有需要的列存在

### 2.3 Translator（OpenAI HTTP）（1.3）

- `glyphloom_core/translators/base.py`
  - 定义 `BaseTranslator`
    - 构造函数保存 `TranslatorConfig`
    - 抽象方法 `translate_batch(self, texts: list[str]) -> list[str]`
- `glyphloom_core/translators/openai_http.py`
  - 定义 `OpenAIHttpTranslator(BaseTranslator)`
    - 从 `TranslatorConfig` 读取 `provider`/`model`/`base_url`/`api_key_env`
    - 当前为「假翻译」：`translate_batch` 为每条文本加前缀 `"[{provider}:{model}] " + text`，不访问网络
    - TODO：后续可接入 `glyphloom_core.core.secrets.get()` 统一加载密钥
- `tests/test_translator_openai_http.py`
  - 手动构造 `TranslatorConfig`
  - 调用 `translate_batch(["你好", "世界"])`
  - 断言长度一致且带 `[provider:model]` 前缀

### 2.4 Pipeline & CLI 闭环（1.4）

- `glyphloom_core/core/pipeline.py`
  - 对外入口：`run_project(config: ProjectConfig) -> PipelineResult`
  - 阶段函数：
    - `_run_extract(config)`：构造 `TableAdapter`，`load()` + `ensure_columns()`，日志记录列数
    - `_run_translate(adapter, config)`：从 `adapter.data` 读取 `source_column`，用 `OpenAIHttpTranslator` 假翻译并写入 `translation_column`，校验数量一致
    - `_run_export(adapter, config)`：确保 `output_dir` 存在，输出文件名沿用源文件名，调用 `adapter.save` 并返回路径
  - `_run_stage(...)`：统一计时 & 日志，异常也会在 `PipelineStep` 中记录 `succeeded` 和耗时
- `glyphloom_core/cli.py`
  - `build_parser()`：子命令仅支持 `"translate"`（默认）；`-c/--config` 指定 YAML；`--dry-run` 只加载配置
  - `main(...)`：加载配置并输出项目信息；`dry-run` 直接退出；`translate` 时调用 `run_project`，输出 success/failed 与产物列表
- `tests/test_pipeline.py`
  - 使用默认 `load_project_config()`，将 `output_dir` 指向 pytest 的 `tmp_path`
  - 断言：
    - `result.success` 为 True
    - 输出目录与产物存在
    - 读取输出文件后，`translation` 列存在且行数匹配，首行带 `[provider:model]` 前缀
  - 说明：当前 Pipeline 使用假翻译（前缀 echo），无网络依赖

---

## 3. 尚未完成 / 下一步计划

### 3.1 Stage 1.5 GUI 模板项目向导（未完成）

计划目标（尚未实现）：

- 在 `glyphloom_gui` 中增加“新建 Excel 本地化项目”入口
- 配置向导：
  - 选择 Excel/CSV 源文件
  - 配置输出目录
  - 填写 LLM 配置（provider/model/api_key_env 等，可带默认值）
- 点击“开始翻译”后：
  - 基于用户输入构造 ProjectConfig
  - 调用 `core.pipeline.run_project(config)`
  - 在 GUI 展示执行结果（成功/失败、输出文件路径、各阶段状态）

当前状态：**尚未开始实现 GUI 部分**

---

## 4. 快速验证与命令

- 运行最小闭环（假翻译）：`python -m glyphloom_core.cli translate --config examples/config.yaml`
- 运行测试：`python -m pytest`

---

## 5. 对未来会话的使用说明

当你在新的对话窗口加载本项目时，可以：

1. 上传以下文件：
   - `docs/project_overview.md`
   - `docs/roadmap.md`
   - `docs/dev_ai_assistant_prompts.md`
   - `docs/design_notes/scope_and_nongoals.md`
   - 本文件：`docs/current_status.md`
2. 告诉 AI：
   - “你是 GlyphLoom 的 PM + 指令工程师 + Reviewer，不写代码，只帮我写 Codex 子任务指令、做代码 review、并同步 roadmap。”
3. 继续从当前的 Stage 1.5 或之后的 Stage 开发。

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
    main_window.py           # 主窗口
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
