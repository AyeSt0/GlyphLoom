# GlyphLoom · 字织�?· Roadmap（开发路线）

> README 写给外部读者；Roadmap 是写给自己与协作者的「施工图」�? 
> �?issue、记录进度、写 release note 都围绕本文件展开�?

---

## 0. 使用说明

### 0.1 阶段与版本映�?

| Stage | 版本区间 | 关键�?|
| ----- | -------- | ------ |
| 0     | `v0.0.x` | 项目骨架、工程环�?|
| 1 ~ 2 | `v0.1.x` | 模板闭环、占位符、QA |
| 3 ~ 4 | `v0.2.x` | 引擎探测、本�?LLM |
| 5 ~ 6 | `v0.3.x` | 插件体系、多语言 GUI |
| 7     | `v0.4.x` | TM、术语表、GUI 编辑 |

> 版本号仅作锚点，真正的范围以阶段描述为准�?

### 0.2 勾选标�?

- `[ ]` 未开�?
- `[x]` 已完�?
- `[-]` 部分完成 / 暂停

提交代码时顺手更新本文件，并�?commit message 里注明勾选内容，方便回溯�?

### 0.3 使用建议

1. 阶段末尾�?tag（`v0.1.0` 等）并整�?release note�? 
2. 大任务拆 issue，并引用本文件的章节编号；完成后同步勾选�? 
3. 若调整优先级，直接在此文档标注说明，避免遗忘�?

---

## 1. 全局工程任务（跨阶段�?

### 1.1 基础工程

- [ ] 配置 `pyproject.toml`
  - [ ] 定义 `glyphloom_core` / `glyphloom_gui` package
  - [ ] 配置 `[project.optional-dependencies]`（例�?`dev`�?
- [ ] 完善 `.gitignore`（venv、`__pycache__`、打包产物、IDE 缓存等）
- [ ] 仓库根目录包含：
  - [ ] `README.md`（WIP 声明�?
  - [ ] `LICENSE`（GPL-3.0-or-later�?
  - [ ] `docs/`（含 `project_overview.md`、`roadmap.md` 等）

### 1.2 规范与工具链

- [ ] Python 3.12+
- [ ] 格式化：`black` �?`ruff format`
- [ ] Lint：`ruff`
- [ ] 测试：`pytest`
- [ ] 编码约定�?
  - [ ] 全量 type hints
  - [ ] core �?import GUI
  - [ ] 使用 `logging`，禁止随�?`print`
  - [ ] 文档、issue、commit message 默认使用中文描述
  - [ ] 代码包含必要的中文注释，解释核心逻辑/约定

### 1.3 CI / 自动�?

- [ ] `.github/workflows/ci.yml`
  - [ ] Windows / Linux / macOS
  - [ ] 安装依赖
  - [ ] 运行 `python -m ruff check .`
  - [ ] 运行 `python -m black --check .`
  - [ ] 运行 `pytest`
- [ ] 后续再补缓存、打包、自定义环境�?
- 详细多平台约束见 [docs/design_notes/platforms.md](design_notes/platforms.md)�?

### 1.4 开发自动化

- [ ] `scripts/dev_setup.ps1`：一键创�?更新虚拟环境并执�?`pip install -e ".[dev]"`�?
- [ ] `scripts/check_quality.ps1`：统一入口依次执行 `ruff check`、`black --check`、`pytest -q`�?
- [ ] `tests/` 目录：至少包含一个冒烟测试，保证 `pytest` 随时可绿�?
- [ ] `scripts/auto_commit.py`：提交前自动跑质量检查，失败时阻�?VERSION 递增�?`git commit`�?
- [ ] Watcher（`scripts/watch_and_commit.ps1`）默认调�?`auto_commit.py`，保存即提交，但质量检查必须先通过�?

---

## 2. Stage 0 · 项目骨架 & 工程环境�?0.0.x�?

当前状态：�?Stage 0 骨架已完成（v0.0.x），core / GUI / 自动化均可运行�?

### 2.1 目标

- 建立 core / gui 的基础目录结构
- 实现“假翻译”的最�?pipeline
- GUI 能正常启动（空壳即可�?

### 2.2 任务列表

#### 2.2.1 Core 骨架

- [x] glyphloom_core/__init__.py
- [x] core/models.py：ProjectConfig、SourceConfig、PipelineResult（pydantic + dataclass�?
- [x] core/config_loader.py：读�?YAML/默认配置并返�?ProjectConfig
- [x] core/pipeline.py：实�?
un_project(config)，输�?summary
- [x] glyphloom_core/cli.py + __main__：python -m glyphloom_core 可运�?

#### 2.2.2 GUI 骨架

- [x] glyphloom_gui/main.py：入�?
- [x] glyphloom_gui/app.py：封�?QApplication
- [x] widgets/main_window.py：最简窗口
- [x] glyphloom_gui/__main__.py：python -m glyphloom_gui 可运�?

#### 2.2.3 文档与自动化

- [x] docs/project_overview.md / docs/roadmap.md / README（记�?Stage 0 状态）
- [x] pyproject.toml（依赖、extras、entry points�?
- [x] 自动化脚本：scripts/dev_setup.ps1、scripts/check_quality.ps1、scripts/auto_commit.py
- [x] 基础测试�?ests/test_pipeline.py + CI

### 2.3 验收标准

- python -m glyphloom_gui 弹出标题为“字织机 / GlyphLoom”的窗口
- python -m glyphloom_core 输出 demo 日志并生�?summary

---

## 3. Stage 1 · 模板闭环 + 云端 LLM（`v0.1.0`�?

### 3.1 目标

- 打通“Excel 模板 �?LLM 翻译 �?Excel 输出�?
- 提供最�?CLI & GUI 入口
- 完成核心数据模型、TableAdapter、OpenAI HTTP Translator

### 3.2 核心任务

#### 数据模型 & 配置

- [x] 补齐 `Line` / `ProjectConfig` / `TranslatorConfig`（必要时扩展 SheetResult 等统计模型）
- [x] `config_loader` 支持合并 CLI / GUI 配置
- [x] 可�?`validators.py`（通用校验�?

#### TableAdapter

- [x] 读取 Excel/CSV，列映射（原�?译文/备注/上下文）
- [x] 导出列：`translation`、`status`、`qa_flags`
- [x] 支持�?sheet

#### Translator（OpenAI HTTP�?

- [x] `openai_http.py`：chat/completion 封装
- [x] 配置：`api_key`、`model`、`base_url`、`temperature`、`max_tokens`
- [x] 支持批量请求、节流、prompt 模板

#### Pipeline（最小闭环）

- [x] 提取（TableAdapter）→ 翻译 �?导出
- [x] 日志 & 进度 hook
- [x] CLI：`python -m glyphloom_core.cli translate --config config.yaml`（或提供 `glyphloom-core` 命令�?

#### GUI 模板项目

- [x] 向导创建 Excel 项目
- [x] 表单填写 LLM 配置
- [x] 运行 pipeline 并展示日�?结果

### 3.3 验收

- Demo Excel 通过 CLI & GUI 翻译并导出成�?
- 导出文件包含翻译�?

---

## 4. Stage 2 · 占位符识�?& 基础 QA（`v0.1.5`�?

### 4.1 目标

- 保护占位符内�?
- 引入 QA 框架与报�?
- GUI 可查�?QA 结果

### 4.2 核心任务

#### 占位符识�?

- [ ] 支持 `{name}`、`%s`、`{{VALUE}}`、`<tag>` 等模�?
- [ ] 可配置白名单
- [ ] `extract_placeholders(text) -> Set[str]`
- [ ] 翻译流程中隐�?还原占位�?

#### QA 模块

- [ ] `qa/base.py`：`run(lines) -> List[Issue]`
- [ ] `placeholder_check.py`
- [ ] `length_check.py`（可配置上下限）
- [ ] 预留扩展�?

#### QA 报告 & 导出

- [ ] `qa/report.py`：导�?JSON + 表格文件（优�?Excel，也可提�?CSV�?
- [ ] TableAdapter 导出写入 QA 结果
- [ ] CLI 支持 `--qa-only`

#### GUI 支持

- [ ] QA 面板展示 Issue 列表 + 过滤
- [ ] 导出 QA 报告
- [ ] Pipeline 运行日志显示 QA 统计

### 4.3 验收

- Demo Excel 含多种占位符，QA 能准确标记错�?
- GUI 可读取并展示 QA 结果

---

## 5. Stage 3 · 引擎探测 & Ren’Py 文本挖掘（`v0.2.0`�?

### 5.1 目标

- �?pipeline 直接对接游戏资源
- 首个重点支持引擎：Ren’Py

### 5.2 核心任务

#### detector

- [ ] `engines/detector.py`：基于路径特征判�?Ren’Py / Unity / Unreal / Unknown
- [ ] 输出 `EngineGuess`（name、confidence、证据描述）

#### Ren’Py Miner

- [ ] 优先解析 `.rpy` 文本脚本，视情况再支�?`.rpyc`
- [ ] 输出统一结构：`line_id / speaker / text / context`
- [ ] 生成 TableAdapter 所需�?Excel / JSON

#### GUI 游戏向导

- [ ] 拖拽或选择游戏目录
- [ ] 展示 detector 结果，允许确�?修改
- [ ] 列出 miner 找到的文件，用户勾选后进入 pipeline

### 5.3 验收

- 提供 Ren’Py demo 项目
- 实现“一键扫�?�?Excel �?翻译 �?QA �?导出”流�?

---

## 6. Stage 4 · OpenAI 兼容 / 本地 LLM（`v0.2.5`�?

### 6.1 目标

- 支持 DeepSeek、Ollama、LM Studio �?OAI 兼容服务
- GUI 中可配置多套 LLM

### 6.2 核心任务

#### OpenAICompatibleTranslator

- [ ] 自定�?`base_url` / `api_version` / headers
- [ ] 支持 `gpt-4o`、`deepseek-chat`、`llama3` 等模�?
- [ ] 统一错误处理、兼容流�?

#### GUI LLM 设置增强

- [ ] Provider 下拉：OpenAI / DeepSeek / Custom
- [ ] `base_url`、`api_key`、`model` 表单
- [ ] “测试连接”显�?RTT、模型信�?
- [ ] 支持保存多套配置

#### 文档

- [ ] `docs/llm_guide.md`：接入指南与故障排查

### 6.3 验收

- 本地 OAI 兼容服务（如 LM Studio）可跑完�?pipeline
- GUI 能切换不�?LLM 配置

---

## 7. Stage 5 · 插件系统 & Pipeline 扩展（`v0.3.0`�?

### 7.1 目标

- core 可被注入 adapter / translator / qa / miner 插件
- 提供官方插件示例

### 7.2 核心任务

#### Registry 机制

- [ ] `registry.py`：维护注册表
- [ ] 支持 entry points 或配置引�?
- [ ] API：`register_adapter(name, cls)` �?

#### 官方示例插件

- [ ] `plugins/sample_adapter`（示�?adapter + QA�?
- [ ] README 解释如何开发插�?

#### Pipeline 扩展 Hook

- [ ] 提供 before/after 钩子（`before_extract`、`after_qa` 等）
- [ ] GUI 显示插件列表，允许启�?禁用

### 7.3 验收

- 示例插件�?CLI & GUI 中可加载
- 可通过配置切换启用状�?

---

## 8. Stage 6 · 国际�?GUI & 主题（`v0.3.5`�?

### 8.1 目标

- GUI 在中英文系统下体验一�?
- 内置字体与语言切换

### 8.2 核心任务

#### i18n 支持

- [ ] 提供 `t("key")`
- [ ] 扫描 UI 替换写死文案
- [ ] `zh_CN.json`、`en_US.json` 与一个示例语言

#### 字体内嵌

- [ ] `glyphloom_gui/fonts/`：Noto Sans / Noto Sans CJK
- [ ] `QFontDatabase.addApplicationFont`
- [ ] 默认字体配置、许可证说明

#### 语言切换

- [ ] 设置页提供语言下拉
- [ ] 保存用户选择，提示需重启

### 8.3 验收

- 中文 / 英文环境无乱�?
- 至少两种语言可切�?

---

## 9. Stage 7 · TM / 术语�?/ GUI 文本编辑（`v0.4.x`�?

### 9.1 目标

- 提升专业度：Translation Memory、Glossary、译文编辑器

### 9.2 核心任务

#### Translation Memory

- [ ] 本地存储（sqlite / JSON�?
- [ ] 翻译前查�?TM，命中跳�?LLM
- [ ] 翻译后写�?TM
- [ ] 提供 TM 导入 / 导出

#### Glossary

- [ ] 导入术语表（源词 + 译文�?
- [ ] Prompt / 后处理保证术语一�?
- [ ] QA 检查术语使�?

#### GUI 文本编辑

- [ ] 左原�?/ 右译�?
- [ ] 筛选：QA 问题、文件、状�?
- [ ] 支持修改并回�?Excel / 数据�?

### 9.3 验收

- Demo 项目使用 TM 明显减少 LLM 调用
- 术语一致性可�?QA 捕捉
- GUI 可浏览与编辑译文

---

## 10. 使用 Roadmap 的姿�?

1. �?Stage 拆成 milestone，子任务�?issue，issue 描述引用本文件编号�? 
2. 每完成一项勾�?Checklist，并�?commit 中提及�? 
3. 阶段末尾发布 tag + changelog，并视情况更�?`project_overview.md`�? 
4. 如果优先级变化，直接在本文档标注，提醒协作者同步�?

核心原则：先跑�?Stage 1~2 的模板闭环与 QA；只�?pipeline 稳定，任何时候都可以暂停迭代把现状当成可用工具，再逐步叠加引擎、GUI、专业功能�?

