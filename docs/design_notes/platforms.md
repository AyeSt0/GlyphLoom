# 平台支持策略（Platforms & OS Support）

> 目标：即使主要在 Windows 上开发，也要确保 core/GUI 可以在 Windows / Linux / macOS 上一致运行。

## 1. 运行目标

| 层级 | 支持策略 |
| --- | --- |
| Core (`glyphloom_core`) | **必须**在 Windows 10/11、主流 Linux（Ubuntu 等）、macOS（Intel & Apple Silicon）上行为一致。 |
| GUI (`glyphloom_gui`) | 依赖 PySide6，设计上支持三平台；打包策略可按平台不同实现（Win: PyInstaller/zip，macOS: app bundle，Linux: AppImage/源码运行）。 |
| 开发工具 (`scripts/*.ps1`) | 只面向开发者，用于自动化/便捷脚本；允许 Windows-only，只要不影响用户安装核心包。 |

## 2. 代码约定

1. **路径与编码**
   - 全局使用 `pathlib.Path`，禁止硬编码反斜杠。
   - 文件读写统一 `encoding="utf-8"`。
2. **禁止 Win-only API**
   - core 层禁止使用 `os.startfile`、`win32api` 等。
   - 如需平台特定功能，必须放在 GUI 或独立工具层。
3. **Subprocess**
   - 尽量传递数组形式，不依赖 shell 内置命令（`dir` 等）。
4. **依赖管理**
   - 默认依赖只包含纯 Python / 跨平台库。
   - 本地推理库（`llama-cpp-python` 等）放在可选 extras 中。

## 3. 本地 LLM / Linux 场景

- `openai_http` / `openai_compatible` translator 通过 HTTP 接口访问云端或本地服务（Ollama、LM Studio、vLLM 等），无需区分平台。
- 未来若实现 `local_python` translator，依赖放在 `[local-llm]` extras，可让仅使用云端的用户避免安装繁重包。

## 4. CI / 验证

- GitHub Actions 使用矩阵：`windows-latest`、`ubuntu-latest`、`macos-latest`，统一运行 `ruff` / `black --check` / `pytest`。
- 本地只在 Windows 开发也没问题，CI 会代替我们发现 Linux/macOS 特有问题。

## 5. 自动化脚本的定位

- `scripts/watch_and_commit.ps1` 等 PowerShell 工具仅用于加速日常开发，不应在 `pip install glyphloom` 后被自动执行。
- 如果需要跨平台版本（例如 shell / Python watcher），可额外提供，但不是 core 的强制要求。

只要遵守上述原则，即使主要在 Windows 上开发，也能在早期阶段保持多平台一致性。*** End Patch
