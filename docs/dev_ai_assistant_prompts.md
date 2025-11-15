# 与 AI 助手协作指南（Codex / ChatGPT / Copilot Chat 等）

## 0. 语言与注释风格（全局约定）

在本项目中，请你遵守以下语言习惯：

1. 回答语言  
   - 所有解释、说明、分析、错误信息 **优先使用简体中文**。  
   - 如需引用英文专业术语，请保留英文原文，并在旁边加简短中文说明。  

2. 代码风格  
   - **标识符统一用英文**：类名、函数名、变量名、文件名等一律使用英文（snake_case / PascalCase）。  
   - **注释优先用中文**：  
     - 行内注释、逻辑说明、复杂分支的解释全部用简体中文。  
     - 例如：  
       ```python
       def load_project_config(path: Path) -> ProjectConfig:
           """加载项目配置文件（YAML），并进行基本校验。"""
           # 这里先检查文件是否存在，避免后面打开时报错
           ...
       ```
   - 如果需要写 docstring，可以用简体中文描述行为，必要时附英文关键术语（如 pipeline、adapter、translator 等）。

## 1. 全局 System Prompt 模板（新会话时用）

> 你是 GlyphLoom（字织机）项目的协作开发者……  
> （把那段“入职宣言”版本贴这里）

## 2. Core 开发任务模板

> 我现在在开发 `glyphloom_core` ……  
> （限制修改范围、提醒多平台、禁止 GUI/OS 特有 API）

## 3. GUI 开发任务模板

> 我现在在开发 `glyphloom_gui` ……  
> （只调度、不写业务逻辑）

## 4. scripts / 自动化任务模板

> 我现在在维护 `scripts/auto_commit.py` ……  
> （不能移除质量检查、不写死 Key）

## 5. 使用建议

- 每次新开 AI 会话，先贴 System Prompt  
- 做具体 feature 时，用对应模块的模板包一层  
- 遇到架构级改动，先看 `docs/project_overview.md` / `docs/roadmap.md`
