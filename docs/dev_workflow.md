# GlyphLoom 开发日常工作流

> 记录“写代码时怎么做”的约定，方便未来协作者快速上手。

## 基础步骤

1. **初始化环境**
   ```powershell
   pwsh -ExecutionPolicy Bypass -File scripts/dev_setup.ps1
   ```
   - 会创建/更新 `.venv`，并安装 `.[dev]` 依赖或基础工具（ruff/black/pytest）。

2. **启动自动提交监听器**（可选）
   ```powershell
   pwsh -ExecutionPolicy Bypass -File scripts/watch_and_commit.ps1
   ```
   - 保存文件 → `auto_commit.py` 自动运行 `ruff/black/pytest` → 递增 `VERSION` → git commit。
   - 若质量检查失败，脚本会终止并提示，历史记录不会混入脏提交。

3. **查看质量结果**
   - 任意时刻可手动运行：
     ```powershell
     pwsh -ExecutionPolicy Bypass -File scripts/check_quality.ps1
     ```
   - 与 CI 使用同一命令集合，保持一致。

4. **推送/打 tag**
   - 完成阶段性工作后：
     ```powershell
     git push
     git tag v0.0.1  # 视 Roadmap 阶段而定
     git push origin v0.0.1
     ```
   - 里程碑版本应附带简要 release note，并更新 Roadmap 勾选状态。

## Commit 风格

- **自动提交**：由 `auto_commit.py` 生成，适合频繁保存、细粒度的改动。标题会自动包含类别 + 版本号，正文按文件拆解。
- **手动提交**：对于架构设计、API 变更、发布版本等重要改动，推荐关闭 watcher，自行撰写 commit message（可使用 `feat: ...`、`refactor: ...` 等约定）。
- **版本号策略**：
  - `VERSION` 仅记录开发期 `alpha.N`，由脚本维护。
  - Git tag 按 Roadmap 阶段使用 `v0.y.z`（如 `v0.0.1`、`v0.1.0`）；需要正式预览版时再考虑 `v0.2.0a1` 等标识。

## 分支建议

- `main`：保持可运行状态，自动提交可以直接进入 `main`，但在合并前需确保 CI 绿灯。
- 功能/尝试性改动：创建 feature 分支（如 `feature/pipeline-refactor`），完成后通过 PR 合并。
- 对外发布前：在 `main` 打断点 tag；若需要临时热修，可考虑 `release/v0.1.x` 分支。

## TODO

- [ ] GUI 中加入“启动/停止 watcher”快捷入口。
- [ ] 在 `scripts/watch_and_commit.ps1` 中检测虚拟环境（自动使用 `.venv/Scripts/python.exe`）。
- [ ] 为重要阶段（Stage 1、Stage 2…）编写标准 release note 模板。

只要遵守上述流程，自动化提交与质量检查就会成为“默认安全网”，让我们专注在真正的功能开发上。*** End Patch
