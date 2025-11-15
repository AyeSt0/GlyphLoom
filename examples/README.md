# Examples

- `template_basic.xlsx`：最小 Excel 模板示例，包含 id / speaker / source / notes 四列，可用于 Stage 1 的表格 pipeline。
- `template_with_placeholders.xlsx`：演示 `{player_name}`、`%s`、`[cityName]` 等多种占位符，为 Stage 2 QA 测试准备。
- `renpy_demo/`：仿照标准 Ren'Py 目录，仅包含 `game/script.rpy`，可用于 engine detector / miner 的最小输入。

开发/测试时尽量复用这些文件，避免每个人都手撸一份不同结构的 demo。*** End Patch
