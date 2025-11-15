# 配置与密钥管理策略

GlyphLoom 从第一天起就要把“显式配置 vs. 隐私密钥”的边界划清楚，避免后期返工。

## 目标

1. **配置可追踪**：项目行为主要由 `config.yaml`（或 GUI 表单导出的 YAML）决定，方便版本控制与 code review。
2. **密钥不入库**：OpenAI/DeepSeek/Ollama 等 Key 永远不出现在仓库，统一通过环境变量/外部秘钥管理器提供。
3. **加载方式一致**：core 层提供 `secrets.get("ENV_NAME")` 之类的辅助方法，所有 translator/adapter 从同一入口读取。

## 最佳实践

### 1. config.yaml 示例（片段）

```yaml
translator:
  provider: openai
  base_url: https://api.openai.com/v1
  model: gpt-4o
  api_key_env: OPENAI_API_KEY   # 指定要读取的环境变量名称
```

含义：

- `api_key_env` 告诉 core/translator 使用 `os.getenv("OPENAI_API_KEY")` 获取真正的 Key；
- GUI 里也显示“请在系统环境或 .env 中设置 OPENAI_API_KEY”；
- 不允许直接把 Key 写进 YAML。

### 2. 环境变量与 `.env`

- 在仓库根目录提供 `env.example`（不包含真实值）：

  ```env
  # 示例：复制为 .env 或加到系统环境变量中
  OPENAI_API_KEY=your-api-key-here
  DEEPSEEK_API_KEY=
  ```

- `.gitignore` 中明确忽略 `.env`，由用户本地创建。
- 推荐在 README / dev_setup 中提醒开发者：`pip install python-dotenv` 后可自动加载 `.env`。

### 3. secrets loader（核心代码建议）

```python
# glyphloom_core/core/secrets.py
import os

def get_secret(env_name: str) -> str | None:
    return os.getenv(env_name)
```

translator 内部统一调用 `get_secret(config.api_key_env)`。如需更复杂的管理（Vault/Azure Key Vault 等），可以在这里扩展。

### 4. GUI/CLI 提示

- GUI：在 LLM 设置页中展示“请在环境变量 `OPENAI_API_KEY` 中注入 Key”，并提供“检测环境变量”按钮。
- CLI：启动时若发现 `api_key_env` 对应的变量为空，需要给出明确错误信息并退出。

## TODO

- [ ] 在 core 中落地 `glyphloom_core/core/secrets.py`（或同等辅助函数）。
- [ ] 在 dev_setup/README 中加入 `env.example` 使用说明。
- [ ] GUI LLM 配置表单增加“api_key_env”字段选择器或明确提示。

只要大家始终遵守“配置进 YAML，密钥走 env”的原则，就能避免后期出现散落的 hardcode key。*** End Patch
