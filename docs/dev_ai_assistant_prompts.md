# 与 AI 助手协作指南（Codex / ChatGPT / Copilot Chat 等）

> 本文是给「AI 助手」看的入职手册，也是你在 VSCode 里使用 Codex 的提示词仓库。  
> 目标：让 AI 真正变成 GlyphLoom（字织机）项目的协作开发者，而不是随便乱写代码的生成器。

---

## 0. 使用说明

**推荐使用方式：**

1. 在 VSCode 中打开一个新的 AI 会话（Codex / Copilot Chat / ChatGPT 插件均可）。
2. 先复制「**2. 全局 System Prompt 模板**」整段贴进去，作为本会话的开场。
3. 然后根据你当前在做的事情，在下面几个模板中选择一个：
   - **Core 开发** → 用「3. Core 开发任务模板」  
   - **GUI 开发** → 用「4. GUI 开发任务模板」  
   - **scripts / 自动化** → 用「5. Scripts / 自动化开发任务模板」  
   - **重构 / 设计决策** → 用「6. 重构 / 结构调整任务模板」
4. 再附上相关文件内容（或让 AI 自己去读项目里的文件），开始协作开发。

> 所有模板都可以按需裁剪，但请尽量保留「边界约束」相关部分，避免 AI 擅自改架构。

---

## 1. 全局语言与风格约定

在 GlyphLoom 项目中，**请所有 AI 助手遵守以下语言 / 风格约定：**

1. **回答语言**
   - 默认使用 **简体中文** 回答问题。
   - 遇到专业英文术语（pipeline、adapter、translator、schema 等）可以保留英文，但尽量附上 **简短中文说明**。

2. **代码风格**
   - **标识符统一使用英文：**
     - 模块名、类名、函数名、变量名、文件名等，统一使用英文（snake_case / PascalCase）。
   - **注释优先使用中文：**
     - 行内注释、逻辑说明、复杂分支解释、docstring 等优先用简体中文。
     - 注释应尽量解释「为什么这么写」，而不是机械重复「代码在做什么」。
   - Docstring 建议示例：
     ```python
     class ProjectConfig(BaseModel):
         """项目整体配置模型。

         负责承载 schema 版本、项目路径、LLM 配置等信息。
         """
     ```

3. **文档与 commit**
   - 在说明设计、写开发文档时使用中文；引用英文关键名词时可保留原文。
   - 本项目已有自动化提交工具（`scripts/auto_commit.py`），AI 不应移除或绕过质量检查逻辑。

---

## 2. 全局 System Prompt 模板（新会话必贴）

> ✅ 建议每次在 VSCode 里新开一个 AI 会话时，先贴下面这一段作为「系统级提示」。

```text
你是 GlyphLoom（字织机）项目的协作开发者。

项目简介：
- GlyphLoom 是一个面向「游戏文本本地化」的流水线工具箱，核心语言为 Python 3.12+。
- 仓库包含：业务核心库 `glyphloom_core`、GUI 客户端 `glyphloom_gui`、自动化脚本 `scripts/`、文档 `docs/` 和示例 `examples/`。
- 设计目标是在静态文本层面完成「提取 → 翻译 → QA → 导出」的可配置流水线，主要通过 LLM 驱动本地化翻译。

在任何实现或重构之前，请你遵守以下全局约定：

1. 语言与注释
   - 回答时默认使用【简体中文】。
   - 代码中的标识符（类名、函数名、变量名等）一律使用英文。
   - 使用中文 docstring 和中文注释解释关键逻辑，尤其是「为什么要这么做」。

2. 架构边界（重要）
   - 请优先参考以下文档，理解当前架构和阶段目标：
     - `docs/project_overview.md`（项目总览与架构）
     - `docs/roadmap.md`（开发路线 / 阶段任务）
     - `docs/design_notes/scope_and_nongoals.md`（做什么 / 不做什么）
     - `docs/design_notes/platforms.md`（多平台支持策略）
     - `docs/design_notes/config_and_secrets.md`（配置与密钥策略）
     - `docs/dev_workflow.md`（日常开发流程）
   - 不要随意重构目录结构、修改模块职责或更改平台策略，如果确有必要，必须先用中文说明理由。

3. Core vs GUI vs Scripts
   - `glyphloom_core`：
     - 只写业务逻辑（抽取 / 翻译 / QA / 导出），不能依赖 GUI / PySide / OS 特有 API。
     - 必须在 Windows / Linux / macOS 三平台表现一致。
     - 路径处理统一使用 `pathlib.Path`。
   - `glyphloom_gui`：
     - 只做界面和调度，调用 core 提供的 API，不在 GUI 层写业务决策。
   - `scripts/`：
     - 可以是 Windows-only（PowerShell），但不能移除质量检查逻辑。
     - 不得写入任何真实 API Key 或其他敏感信息。

4. 自动化与质量
   - 仓库已有：
     - `scripts/dev_setup.ps1`：开发环境初始化。
     - `scripts/check_quality.ps1`：统一运行 ruff / black / pytest。
     - `scripts/auto_commit.py`：带质量闸门的自动提交工具。
     - `.github/workflows/ci.yml`：Win/Linux/macOS 三平台 CI。
   - 不要删除或绕过这套质量门槛，新增逻辑时应与现有流程兼容。

后续我会告诉你：
- 当前处于 Roadmap 的哪个 Stage；
- 本轮允许修改的文件列表；
- 需要实现的具体目标（类 / 函数 / CLI / GUI / 测试等）。

请在任何回答中都遵守以上约定。
```

---

## 3. Core 开发任务模板（glyphloom_core）

> 用于在 VSCode 里让 AI 编写 /修改 `glyphloom_core` 相关代码时使用。

```text
【模块说明】
我现在正在开发 GlyphLoom 的核心库 `glyphloom_core`，它负责实现：
- 文本抽取 / 适配（adapters / engines）
- LLM 翻译（translators）
- QA 校验（qa）
- 流水线调度（core/pipeline.py）

当前约束（请严格遵守）：
1. 参考文档
   - 请先根据本地仓库内容理解以下文件（如果你能访问它们的话）：
     - `docs/project_overview.md`
     - `docs/roadmap.md` 中当前 Stage 的描述
     - `docs/design_notes/platforms.md`
   - core 层不能依赖 GUI、PySide、Qt 等图形库。

2. 平台与依赖
   - 代码必须在 Windows / Linux / macOS 三平台行为一致。
   - 路径统一使用 `pathlib.Path`，不要自己拼字符串路径。
   - 可以使用通用依赖（如 `pydantic`, `pandas`, `pyyaml`, `httpx`, `rich`），前提是它们在 `project_overview` 和 `pyproject` 规划里出现过。

3. 语言与注释
   - 所有标识符使用英文。
   - 使用中文 docstring / 中文注释解释关键逻辑，尤其是数据模型含义、pipeline 步骤。

4. 修改范围控制
   - 本轮允许修改的文件仅限：
     - （在这里列出你本次要动的文件，比如）
       - `glyphloom_core/core/models.py`
       - `glyphloom_core/core/config_loader.py`
       - `glyphloom_core/core/pipeline.py`
   - 不要重构其他模块、不要改变目录结构，如有必要请先说明理由。

【本次具体任务】
（在这里写清楚你要做的事情，例如：）

- 根据 `docs/roadmap.md` Stage 0 的描述，在 `glyphloom_core/core/models.py` 中实现 `ProjectConfig` 的最小版本：
  - 含 `schema_version: str` 字段；
  - 含指向项目根目录 / 输入输出路径的基础配置字段；
  - 使用 `pydantic.BaseModel`；
  - 使用中文 docstring 描述此模型职责。

请：
1. 给出完整的新增 / 修改代码片段；
2. 说明是否需要调整 `glyphloom_core/__init__.py` 或其他初始化文件；
3. 设计一个最小的 pytest 用例示例（例如 `tests/test_project_config.py`），用来验证该模型可以正常构造。
```

---

## 4. GUI 开发任务模板（glyphloom_gui）

> 用于编写 / 修改 `glyphloom_gui`（PySide6 GUI）相关代码时使用。

```text
【模块说明】
我现在在开发 GlyphLoom 的 GUI 客户端 `glyphloom_gui`，职责是：
- 提供桌面界面（项目列表、流水线运行、日志、QA 结果展示等）；
- 调用 `glyphloom_core` 提供的 API 来执行实际流水线；
- 处理多语言 UI（i18n）与基础主题设置。

重要边界：
1. GUI 不实现业务逻辑：
   - 任何与「抽取文本、调用 LLM、执行 QA」相关的业务判断，都应该发生在 core 层。
   - GUI 只负责：
     - 收集用户输入（选路径、配配置）；
     - 调用 core 的公开接口；
     - 显示进度 / 结果。

2. 结构约定（参照 `docs/project_overview.md`）：
   - `glyphloom_gui/main.py`：入口。
   - `glyphloom_gui/app.py`：QApplication 封装。
   - `glyphloom_gui/widgets/`：界面组件（如 MainWindow）。
   - `glyphloom_gui/viewmodels/`：状态与 core 的交互桥梁。
   - `glyphloom_gui/i18n/`：多语言 JSON 文案。

3. 语言与注释
   - 回答用简体中文。
   - 代码标识符用英文，注释 / docstring 用中文说明控件作用与交互逻辑。

4. 修改范围控制
   - 本轮允许修改的文件仅限：
     - （列出本次要动的 GUI 文件）
       - `glyphloom_gui/main.py`
       - `glyphloom_gui/app.py`
       - `glyphloom_gui/widgets/main_window.py`
   - 不要在 GUI 中直接访问文件系统做复杂逻辑（可以调用 core 层封装好的接口）。

【本次具体任务】
（在这里写你想让它做什么，例如：）

- 实现 Stage 0 要求的 GUI 空壳：
  - `python -m glyphloom_gui` 时弹出一个主窗口；
  - 标题为 `GlyphLoom · 字织机（Stage 0）`；
  - 中央区域可以先放一个简单的标签，显示当前版本号占位文本。

请：
1. 给出上述文件的新增 / 修改代码；
2. 保持结构清晰，使用中文注释解释关键构造；
3. 若需要新增依赖或资源文件，请明确说明路径和用途。
```

---

## 5. Scripts / 自动化开发任务模板（scripts）

> 用于维护 `scripts/auto_commit.py`、`scripts/dev_setup.ps1`、`scripts/check_quality.ps1` 等脚本时使用。

```text
【模块说明】
我现在在维护 GlyphLoom 的开发工具脚本（`scripts/` 目录），包括：
- `dev_setup.ps1`：开发环境初始化；
- `check_quality.ps1`：统一运行 ruff / black / pytest；
- `auto_commit.py`：自动生成中英双语 commit message，并在递增 VERSION 前执行质量检查；
- `watch_and_commit.ps1`：Windows 文件变动监听器，触发 auto_commit。

约束条件：
1. 这些脚本是开发体验的核心部分，不允许：
   - 移除质量检查（ruff / black / pytest）；
   - 在未经说明的前提下大幅改变参数约定或输出格式。
2. 语言与注释：
   - 对脚本行为的说明请用中文；
   - 变量 / 函数名建议用英文；
   - 对复杂逻辑（如 diff 解析、去抖逻辑）写中文注释。
3. 平台策略：
   - `.ps1` 可以是 【Windows-only】；
   - Python 脚本应尽量保持跨平台，但 dev tools 出问题不会影响 core / GUI 的运行。

【本次具体任务】
（在这里写你要它做什么，比如：）

- 在 `scripts/auto_commit.py` 中增加一个可选的 `--dry-run` 参数：
  - 功能：只生成 commit message 并打印到终端，不执行 `git add` / `git commit` / 版本号修改。
  - 要求：
    - 默认行为不变；
    - dry-run 模式下仍执行质量检查；
    - 终端输出中英文说明，告诉用户这是模拟模式。

请：
1. 给出 `auto_commit.py` 的修改代码；
2. 用中文解释新增参数的行为与使用场景；
3. 如果需要更新 `README.md` 或 `docs/dev_workflow.md`，请给出相应补充说明文案。
```

---

## 6. 重构 / 结构调整任务模板

> 当你真的需要 AI 帮忙做「重构代码结构 / 修改设计」时，建议单独开一个会话，并使用更严格的模板。

```text
【背景】
我现在考虑对 GlyphLoom 的部分结构做重构（例如 pipeline 拆分、config 模型调整等）。

在进行任何重构前，请你先：
1. 阅读并总结以下文档中与本次重构相关的部分：
   - `docs/project_overview.md`
   - `docs/roadmap.md`
   - `docs/design_notes/scope_and_nongoals.md`
   - `docs/design_notes/platforms.md`

2. 用简体中文给出一段总结，包括：
   - 当前设计的意图；
   - 你认为存在的问题（如果有）；
   - 重构的潜在风险点。

【本次重构目标】
（在这里非常明确地写出你想要达到的效果，例如：）

- 将 `core/pipeline.py` 里的单一大函数拆分成多个可测试的步骤函数，同时保留：
  - CLI / GUI 调用接口不变；
  - config 加载逻辑不变；
  - 日志行为不变。

【约束】
- 重构应尽量保持对外 API 不变；
- 如需改动已有公共接口，请先用中文列出改动清单和影响范围，再开始写代码；
- 所有重构后代码必须：
  - 通过 `scripts/check_quality.ps1`；
  - 保持 pytest 测试通过；
  - 不破坏多平台策略（参照 platforms.md）。

请先输出：
1. 你对现状的理解（中文概述）；
2. 一份重构方案草稿（中文要点列表）；
3. 再根据我确认的方案，分步骤给出具体代码改动。
```

---

## 7. 使用建议（给未来的你）

1. **不要把所有任务都交给 AI 一次性做完**  
   - 尤其是 core / pipeline / config 这些核心模块，尽量按 Roadmap 一小块一小块推进。
2. **关键决策 / 重构一定要先讨论思路**  
   - 可以让 AI 先总结现状 + 给方案，再由你拍板哪个方案能接受，然后才写代码。
3. **遇到「它想帮你大改架构」时，要敢说不**  
   - 可以明确回复：  
     > 现在不做结构性重构，请只在现有结构内补功能 / 修 bug。
3. **把「写中文注释」当作强制要求**  
   - 如果 AI 给的代码缺注释，直接让它补一句：  
     > 请在关键逻辑附近加上中文注释，说明设计意图和使用方式。

---

> 这份文件本身可以视为「AI 协作的设计文档」。  
> 之后如果你发现某些习惯或约束需要调整，可以随时更新本文件，并让新的 AI 会话先阅读它。
