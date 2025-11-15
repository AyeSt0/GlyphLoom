# GlyphLoom · 字织机 · 项目总览（开发者视角）

> 面向玩家 / 汉化组 / 开发者的 **游戏文本本地化工具箱**  
> 一条统一、可编程、可扩展的静态本地化流水线，用 LLM 驱动高质量产出。

---

## 1. 产品定位与目标

### 1.1 Why

- 现有工具要么绑死在单一游戏/引擎，要么只是实时机翻叠加；我们要做的是 **离线、批量、可重复的本地化管线**。
- 目标受众：
  - **开发者**：拿到 `glyphloom_core` 作为 SDK / Pipeline，嵌入自己的自动化工具。
  - **玩家 / 汉化组**：使用 `glyphloom_gui` 拖拽游戏、配置流程、一键生成本地化包。

### 1.2 What

- 一条“提取 → 翻译 → QA → 导出”的标准流水线，可插拔扩展。
- GUI = 调度层；Core = 业务逻辑层。GUI 绝不写业务判断，Core 绝不依赖 Qt。

### 1.3 最低可接受标准

1. **核心逻辑只能写在 core**：任何抽取、翻译、QA、LLM 调用都在 core，GUI 仅负责 orchestrate。
2. **闭环优先**：Excel → Pipeline → Excel+QA 的完整链路必须在早期打通。
3. **LLM 后端可插拔**：云端、本地、自建服务全部通过统一 TranslatorConfig 接口。
4. **架构要有余量**：引擎适配、插件、TM/术语表、GUI 文本编辑都要预留挂点。

---

## 2. 核心设计原则

1. **Core = Library**  
   - `glyphloom_core` 必须可 `pip install`，可在 headless 环境使用，不依赖 GUI。
2. **Pipeline 驱动**  
   - 所有功能围绕阶段式 pipeline，阶段可配置/替换，CLI 与 GUI 共用同一套 API。
3. **配置优先**  
   - `config.yaml` + GUI 表单控制行为；开发者可直接写 YAML；配置模型（TranslatorConfig / AdapterConfig / QaConfig 等）必须直观。
4. **平台无关**  
   - 路径用 `pathlib`；
   - 全局统一 `UTF-8`；
   - 不用 Windows 特定 API；
   - 详细策略见 [docs/design_notes/platforms.md](design_notes/platforms.md)。
   - 全路径 `pathlib`，统一 UTF-8，不写 Windows 专属 API，将跨平台差异收敛在 GUI 打包层。

---

## 3. 技术栈速览

| 模块              | 技术/库                                           |
| ----------------- | ------------------------------------------------ |
| 核心语言          | Python 3.12+                                     |
| Core              | `pydantic`, `pandas`, `openpyxl`, `httpx`, `pyyaml`, `rich` |
| GUI               | `PySide6`，自研 JSON i18n                        |
| 工具 & 质量       | `pytest`, `ruff`, `black`（视需求）               |

---

## 4. 目录结构（规划稿）

```text
glyphloom/
  glyphloom_core/
    __init__.py
    api.py                  # 对 GUI / CLI 暴露的高阶接口
    core/
      models.py             # Line / Config 数据结构
      pipeline.py           # 主流水线 orchestrator
      config_loader.py      # 读写 YAML、合并 GUI 表单
      placeholders.py       # 占位符识别工具
    adapters/
      base.py
      table_adapter.py      # Excel / CSV
      json_adapter.py       # JSON / JSONL（后续）
      po_adapter.py         # gettext PO（后续）
    engines/
      detector.py           # 引擎识别
      renpy_miner.py
      unity_miner.py
      unreal_miner.py
    translators/
      base.py
      openai_http.py        # OpenAI / DeepSeek
      openai_compatible.py  # Ollama / 任意 OAI 兼容服务
      local_python.py       # llama-cpp / transformers（后期）
    qa/
      base.py
      placeholder_check.py
      length_check.py
  glyphloom_gui/
    __init__.py
    main.py                 # GUI 入口
    app.py                  # QApplication 包装
    viewmodels/             # GUI 状态与 Core 交互（业务调用集中在此）
    widgets/                # 自定义控件
    assets/                 # 图标、主题、字体等
    i18n/                   # 多语言 JSON 文案
  glyphloom_cli/            # （预留）命令行入口，后期实现
    __init__.py
    main.py
  docs/
    project_overview.md
    roadmap.md
    design_notes/
  templates/                # 官方示例模板（Excel 等）
  tests/                    # 单元 & 集成测试目录
```

---

## 5. 端到端流水线

### 5.1 Core Pipeline 阶段

1. **提取 Extract**  
   - 由 `engines/*` miner 定位游戏资源文件，再交给 adapter 转为统一数据模型。  
   - 早期优先 Excel/CSV（TableAdapter），后续 JSON/PO 等。
2. **翻译 Translate**  
   - `translators/*` 统一 `TranslatorConfig`，LLM 调用通过 HTTP（OpenAI 兼容）或本地 Python 引擎。
   - 支持批量/分段，且占位符保护、术语表应用、风格 prompt 等统一放在 translator 层处理。
3. **QA Validate**  
   - 多个检查器串联：占位符、长度、禁词、格式一致性等，规则可配置。
4. **导出 Export**  
   - 反向写回 Excel/JSON/PO，附带 QA 报告（表格文件，优先 Excel，也可支持 CSV）；未来加“生成游戏补丁”能力。

### 5.2 GUI 触发流程（GlyphLoom Studio）

1. **项目导航**：列举历史项目、创建新项目向导。
2. **引擎识别**：拖拽游戏目录 → `engines.detector` 给出猜测 → 选择/确认 → 进入文件扫描。
3. **文件 & Adapter 管理**：列出 miner 找到的文件类型，用户勾选，用适配器生成 pipeline 输入。
4. **配置阶段**：填写 LLM、术语表、批量策略；表单映射到 `config.yaml`。
5. **运行监控**：展示 pipeline 进度（`rich`/GUI 进度条），支持暂停/恢复。
6. **QA / 导出**：展示 QA 结果、导出路径，允许再次运行某一阶段。

---

## 6. GUI 交互要点

### 6.1 主界面

- **快速入口**：新建项目、打开最近项目、查看文档。
- **进度概览**：每个项目显示当前阶段、最新一次 QA 是否通过。

### 6.2 项目视图

- **文件树**：来源文件、适配器生成的中间文件、QA 报表。
- **流水线面板**：可单独运行 “提取/翻译/QA/导出”，展示日志。
- **QA 汇总**：表格化展示占位符、长度等问题；导出格式以 Excel 为主，并可追加 CSV。

### 6.3 设置面板

- **LLM 设置**：`provider/base_url/api_key/model`；测试连接按钮；并发、超时高级参数。
- **GUI 设置**：主题、语言、开机自启、缓存清理。
- **插件/高级**（预留）：路径映射、自定义脚本挂载点。

---

## 7. LLM & 本地模型支持

### 7.1 统一抽象

- 通过 `TranslatorConfig` 描述 provider、base_url、model、额外参数。
- Core 内部永远使用统一接口，具体实现可切换 `openai_http`、`openai_compatible`、`local_python`。
- 占位符保护 / 术语表在 translator 层统一实现，GUI 不关心细节。

### 7.2 使用场景

| 场景          | 配置要点                                                     |
| ------------- | ------------------------------------------------------------ |
| 云端 LLM      | 只要有 Key；GUI 中填入 base_url / api_key / model，直接跑。 |
| 本地 LLM      | 用户在本机/局域网部署 OAI 兼容服务（Ollama、LM Studio 等），配置 base_url、model；GUI 一律按 OpenAI 兼容调用。 |
| 自研 Python 推理 | `local_python` translator 负责调用 llama-cpp / transformers，GUI 仍用同一接口。 |

---

## 8. 开发流程与约定

### 8.1 环境

- Python 3.12+  
- 建议用 `uv` 或 `poetry`：`uv pip install -e ".[dev]"`。

### 8.2 代码风格

- 强制 type hints，模块边界清晰（core vs gui）。
- 逻辑与 IO 分离；core 避免 `print`，统一 logger。
- 配置模型与 pipeline 步骤保持可测试性。

### 8.3 测试策略

- 单元测试优先覆盖 `models/adapters/translators/qa`。
- 准备一个 demo 项目跑通集成测试：Excel → 翻译 → QA → 导出。
- GUI 层做最小化自动化测试，重点回归 pipeline API。

---

## 9. Roadmap（超精简）

1. **阶段 0：骨架**  
   - 搭出 core / gui 目录结构，CLI & GUI 可启动。
2. **阶段 1：模板闭环**  
   - TableAdapter、假翻译、QA 通路打通，GUI 可创建项目并跑模板任务。
3. **阶段 2：占位符 & QA**  
   - 占位符识别 + QA 报表，GUI 支持仅运行 QA。
4. **阶段 3：引擎检出 & 文本挖掘**  
   - `detector + renpy_miner` 优先完成，GUI 有游戏向导。
5. **阶段 4：OpenAI 兼容 / 本地 LLM**  
   - `openai_compatible` translator、GUI LLM 设置适配本地服务。
6. **阶段 5+**  
   - 插件系统、多语言 UI、翻译记忆、术语表管理、GUI 内联文本编辑等。

详尽任务拆解见 `docs/roadmap.md`。

---

## 10. 自我提醒

- README 写给公众；`docs/project_overview.md` 写给自己与协作者。  
- 所有实现都要回溯到本文件定义的骨架与底线，避免出现“越写越散”的副作用。  
- 随着阶段推进，适度更新此文档，保持核心设计决策可追溯。
## 11. ƽ̨֧�ֲ��ԣ�ժҪ��

- core (`glyphloom_core`)����ʹ�ÿ�ƽ̨������������ Windows / Linux / macOS ����Ϊһ�¡�
- GUI (`glyphloom_gui`)������ PySide6��Ŀ��֧����ƽ̨���У�������Կɰ�ƽ̨����ʵ�֡�
- �����ű���`scripts/*.ps1`��������Ϊ�ڲ����ߣ����� Windows-only��ֻҪ��Ӱ����İ���װ��

> ����˵���� [docs/design_notes/platforms.md](design_notes/platforms.md)��
