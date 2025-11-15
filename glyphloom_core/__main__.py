"""允许使用 `python -m glyphloom_core` 直接运行 CLI。"""

from __future__ import annotations

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
