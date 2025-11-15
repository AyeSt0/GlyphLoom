"""允许使用 `python -m glyphloom_gui` 启动 GUI。"""

from __future__ import annotations

from .main import main

if __name__ == "__main__":
    raise SystemExit(main())
