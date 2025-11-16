# GlyphLoom · dev_ai_assistant_prompts.md  
> 本文件既是「给未来的我」的使用说明，也是「给 AI」的协作规则。

---

## 0. 如何使用本文件（给未来的我）

每次在 VSCode / ChatGPT / 其它对话界面中让 AI 参与开发时，都按下面两步来用：

### 0.1 新开会话：全局启动咒语

**只要是新对话，第一条消息统一用这个：**

请先阅读仓库里的以下文档：

- docs/dev_ai_assistant_prompts.md
- docs/project_overview.md
- docs/roadmap.md
- docs/design_notes/scope_and_nongoals.md
- docs/design_notes/platforms.md

把它们当成本仓库的「协作规则 / System Prompt」。

不要修改这些文档的内容。

看完后请用 3～5 条要点总结你理解的关键规则（尤其是 core vs gui 的边界、Python 版本、平台策略和小步安全改动原则），然后等待我给你具体任务。

等 AI 总结完再继续后面的任务。  
如果它总结得不对，直接指出来，让它重读文件再总结一遍。

---

### 0.2 同一会话里的每个「子任务」怎么发指令

在同一个会话里，每做一个具体任务，都要：

1. 提醒它遵守本文件规则；
2. 写清这次的目标；
3. **列出允许修改的文件清单**（非常重要）；
4. 要求先说计划再贴代码。

**通用子任务模板：**

记得遵守 `docs/dev_ai_assistant_prompts.md` 和相关设计文档里的规则。

本次任务只有一个，请按「小步、安全变更」来做。

目标：
- （这里写清这次要做什么，例如：实现 TableAdapter 的基础 Excel 读取）

允许修改的文件：
- path/to/file_1.py
- path/to/file_2.py
- （如有测试文件，一起写上）

除上述文件外，其他文件一律不要改动（除非我在这条消息里明确写出来）。

请按下面步骤输出：
1. 先用 3～5 条要点说明你打算怎么修改这些文件；
2. 然后给出修改后的完整代码块（只包含允许改动的文件）；
3. 最后告诉我如何在本地验证（例如 pytest 命令、手动运行方式）。

代码里请使用中文注释解释关键逻辑。

---

### 0.3 「Roadmap 同步子任务」通用模板

现在请你同步更新 docs/roadmap.md：根据你刚刚完成并通过测试的子任务，自动识别对应的 Roadmap checklist 条目并将其从 [ ] 改为 [x]。不要修改任何文案或其它条目。请严格遵守 dev_ai_assistant_prompts.md：只允许修改 docs/roadmap.md。输出流程：分析你准备勾选的条目 → 给出修改后的 roadmap → 给出本地验证方式。

---

**如果是只读不改的任务（例如 review / 讲解）：**

记得遵守 `docs/dev_ai_assistant_prompts.md` 里的规则。

本次任务是代码 review，只能阅读、分析下面这些文件，不要修改任何文件，也不要虚构不存在的文件：

需要阅读的文件：
- path/to/file_1.py
- path/to/file_2.py

请先列出你会重点检查哪些方面（例如：边界情况、异常处理、命名一致性、是否符合 project_overview 的设计），然后再开始给出分析。

---

## 1. 通用协作规则（给 AI 看的）

> 这一节是写给 AI 的「行为约束」，人和 AI 都可以看。

1. **遵守项目文档优先于你自己的习惯**  
   - 任何时候，如果你的直觉和以下文档有冲突，以文档为准：  
     - `docs/project_overview.md`  
     - `docs/roadmap.md`  
     - `docs/dev_workflow.md`  
     - `docs/design_notes/scope_and_nongoals.md`  
     - `docs/design_notes/platforms.md`  
     - `docs/design_notes/config_and_secrets.md`  

2. **Core 与 GUI 的边界**  
   - `glyphloom_core` 是可被安装为库的核心模块：  
     - 不允许依赖 GUI / PySide6；  
     - 逻辑与 IO 分离，优先使用 logger，不随意 `print`。  
   - `glyphloom_gui` 只负责界面与交互：  
     - 不写业务流水线逻辑；  
     - 通过 core 暴露的 API 调度 pipeline。

3. **语言与风格**  
   - 代码：Python 3.12+，尽量使用 type hints、pydantic 等现代写法；  
   - 注释与 docstring：可以使用中文说明关键逻辑，保证未来的我一眼能看明白；  
   - commit message 与自动化脚本由仓库内现有规范负责，你只需要保证代码通过 `ruff/black/pytest`。

4. **小步、安全、可回滚**  
   - 每次改动尽量集中在少量文件中；  
   - 保持 `tests/` 能跑、CI 能通过；  
   - 避免「顺手」大改没有在目标中声明的模块。

5. **不要碰的东西（除非我明确说允许）**  
   - 不要擅自修改：  
     - `docs/dev_ai_assistant_prompts.md` 本文件；  
     - 其它设计文档的宏观结构（除非我说要更新）；  
     - 自动化脚本（`scripts/auto_commit.py` 等）和 GitHub Actions 工作流。  
   - 发现现有文档/脚本有明显问题时，可以先给出「改进建议」，再等我确认是否允许你改。

---

## 2. Stage 0 / Stage 1 的角色定位

> 目前 Stage 0 已完成骨架：core/gui 目录结构、基本 pipeline、CLI/GUI 入口、最小测试与 CI。  
> 现在进入 **Stage 1：模板闭环 + 云端 LLM（v0.1.x）**，你需要按 roadmap 来推进。

### 2.1 Stage 1 的目标（给 AI 的简写版）

参考 `docs/roadmap.md` 中 Stage 1：  

- 打通 “Excel 模板 → LLM 翻译 → Excel 输出” 的最小闭环；  
- 实现 TableAdapter 基本读写模型（读取 Excel/CSV、写出翻译列、QA 列占位）；  
- 实现 OpenAI HTTP Translator 的最小调用（可以是假翻译 / echo，后续再接真实 LLM）；  
- 提供最小 CLI & GUI 入口能驱动这条流水线。

你的任务是：  

- **先提出 Stage 1 的子任务拆分与文件改动建议**；  
- 再按照我选择的子任务，一步一步落地实现。

---

## 3. Stage 1：设计优先的协作流程（给人 + AI）

### 3.1 第一步：只做「设计 / 拆任务」，不写代码

当我准备开始 Stage 1 时，我会发出类似下面的指令（这是模板，未来我可以直接复制用）：

记得遵守 `docs/dev_ai_assistant_prompts.md` 和其它设计文档的规则。

现在我们要进入 `docs/roadmap.md` 里的 Stage 1（模板闭环 + 云端 LLM）。

这一步「只做设计，不写代码」，请你：

1. 基于 roadmap 的 Stage 1 描述，将本阶段拆成 3～6 个子任务（按 “1.1, 1.2, 1.3 …” 编号）；
2. 对每个子任务，列出：
   - 需要修改的文件路径列表（以仓库根目录为基准），
   - 每个文件准备新增或修改哪些类 / 函数 / 流程，用一行说明目的；
3. 标明建议的实现顺序（先做哪个子任务、哪个可以延后）。

要求：
- 此轮完全不要写任何代码实现；
- 暂时不要新增 tests 以外的文件；
- 保证每个子任务修改的文件数量尽量少（建议不超过 3 个文件）。

AI 回答后，我只需要做「选择题」：

- 哪些子任务命名合适；
- 有无越权修改的文件（比如动 GUI 或脚本）；
- 确定先做哪一个（例如 “先做 1.1 TableAdapter 读写”）。

---

## 4. Stage 1：实现子任务的通用模板

当设计确认后，每个子任务就用下面的模板来落地实现。

### 4.1 实现类/函数的模板

记得遵守 `docs/dev_ai_assistant_prompts.md` 和你刚刚输出的 Stage 1 设计清单。

现在只实现你设计里的「1.1 子任务」（例如：TableAdapter 基础读写）。

本次任务的目标：
- （简要重复 AI 自己设计里 1.1 子任务的目标）

允许修改的文件：
- glyphloom_core/adapters/base.py
- glyphloom_core/adapters/table_adapter.py
- tests/test_table_adapter.py

严格限制：
- 只允许修改以上文件；
- 不要新建其它模块或文件；
- 不要修改 docs/、scripts/、CI 配置。

请按以下步骤输出结果：
1. 先简要回顾你在「1.1 子任务设计」中对这三个文件的计划（用 3～5 条说明）；
2. 然后给出修改后的完整代码块（每个文件一个代码块，标明路径）；
3. 最后给出本地验证步骤，例如：
   - 要运行的 pytest 命令；
   - 如果有示例 Excel，可以说明放在哪个目录、如何运行。

请在关键逻辑处添加中文注释，方便我之后阅读和二次调整。

### 4.2 自我 review 模板（让 AI 自己找坑）

实现提交后，再发一个附加指令，让它先自查：

请对你刚刚提交的改动做一次自我 review，回答以下问题：

1. 列出你最担心的 3 个潜在问题或边界情况（例如：空表、列名缺失、大文件性能等）；
2. 说明还缺哪些测试用例（按「优先级高/中/低」简单分级）；
3. 检查是否有任何地方可能违反：
   - core 与 gui 的边界；
   - `docs/roadmap.md` 中 Stage 1 的设计意图；
   - `docs/design_notes/platforms.md` 的多平台约束。

只需要文字说明，不需要再贴代码。

我只需要在这个基础上再看一眼 diff / pytest 报告，有问题就再缩小范围重新让它改。

---

## 5. 针对 Codex / VSCode 集成的特别提醒

> 如果你是在 VSCode 里用 Copilot Chat / 类似「在当前仓库上下文」的 AI：

1. 第一条消息一定要是「0.1 全局启动咒语」，让它先读文档；  
2. 之后的所有任务，都尽量说明「允许修改的文件列表」，避免它乱动；  
3. 如果我觉得生成代码量太大、超出我能 review 的范围，就把子任务拆得更细一些（比如只改一个文件）。

---

## 6. 总结（给未来的我）

- 这份文件的核心作用是：  
  - **把「怎么用 AI」这件事标准化**；  
  - 让 AI 自己负责设计和拆任务，你负责选子任务和验收结果；  
  - 用「允许修改的文件」这条红线，防止它乱改。

- Stage 1 之后，等我们开始做引擎探测 / Ren’Py miner / 插件系统，还可以在本文件底部继续加专用模板，照着这个模式扩展就行。

> 记住一点就够：  
> **新会话先读文档、每个子任务都要写文件白名单。**  
> 剩下的，就让 AI 多干点活。
