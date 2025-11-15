# GlyphLoom

> 游戏文本本地化工具箱（开发中）。核心目标：构建一条“提取 → 翻译 → QA → 导出”的可编程流水线，用 LLM 驱动高质量产出。

## 当前状态

- 仍处于 alpha 阶段，主要面向内部开发与协作。
- Python 版本要求：**3.12+**。
- core / GUI 架构、自动化与文档基础已经准备就绪，接下来进入 Stage 0（项目骨架）实现。

## 快速上手

```powershell
# 1. 初始化开发环境（创建/更新 .venv + 安装依赖）
pwsh -ExecutionPolicy Bypass -File scripts/dev_setup.ps1

# 2. 启动自动监听（保存即 lint/test/commit，可随时关闭）
pwsh -ExecutionPolicy Bypass -File scripts/watch_and_commit.ps1

# 3. 手动运行质量检查（ruff + black --check + pytest）
pwsh -ExecutionPolicy Bypass -File scripts/check_quality.ps1
```

> `auto_commit.py` 会在 bump VERSION 之前自动执行质量检查；若需临时跳过，可设置 `GL_SKIP_QUALITY=1`。

## 📚 文档索引

- 项目总览 · 架构与设计：[docs/project_overview.md](docs/project_overview.md)
- Roadmap · 阶段任务与版本规划：[docs/roadmap.md](docs/roadmap.md)
- 开发工作流 · 日常操作与自动化：[docs/dev_workflow.md](docs/dev_workflow.md)
- 设计说明（Design Notes）
  - 范围与不做什么：[docs/design_notes/scope_and_nongoals.md](docs/design_notes/scope_and_nongoals.md)
  - 配置与密钥策略：[docs/design_notes/config_and_secrets.md](docs/design_notes/config_and_secrets.md)
  - 多平台支持策略：[docs/design_notes/platforms.md](docs/design_notes/platforms.md)
- 示例资产 · Excel 模板与 Ren’Py Demo：[examples/README.md](examples/README.md)

## 常见问题

- **质量检查太慢？**  
  默认脚本会串行执行 `ruff` / `black --check` / `pytest`；可通过缓存、分阶段运行或设置 `GL_SKIP_QUALITY=1`（不推荐）来临时绕过。

- **没有改动却触发脚本？**  
  `auto_commit.py` 会在检测到没有差异时立即退出，不会生成空 commit，也不会修改版本号。

- **不同类型的改动会混在一个 commit 里吗？**  
  自动提交会聚合一次保存周期的所有文件，并按类别生成标题；正文会逐文件列出“类别 + 状态 + 行数 + 亮点”，如需更细粒度可手动运行脚本并自行 `git add` 控制。

- **非 Windows 如何使用？**  
  直接运行 `python scripts/auto_commit.py` 即可；监听可以用 `entr`、`watchman`、`nodemon` 等工具自行接管。core/GUI 代码遵循跨平台设计，详见 [platforms.md](docs/design_notes/platforms.md)。

更多细节、设计背景与阶段性任务，请查阅上方文档。*** End Patch
