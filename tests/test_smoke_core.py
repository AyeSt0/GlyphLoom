"""最小冒烟测试：确保基础脚本可导入。"""

import importlib


def test_import_scripts_module():
    """导入 auto_commit 模块，保证基础依赖存在。"""
    module = importlib.import_module("scripts.auto_commit")
    assert module.REPO_ROOT.is_dir()
