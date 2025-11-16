from pathlib import Path

import pandas as pd

from glyphloom_core.core.config_loader import load_project_config
from glyphloom_core.core.pipeline import run_project


def test_pipeline_template_roundtrip(tmp_path: Path) -> None:
    """完整跑一遍“读表 -> 假翻译 -> 导出”，验证 translation 列被写入。"""

    base_config = load_project_config()
    # 默认配置已包含 table_adapter/translator 的基础字段
    assert base_config.table_adapter.source_column == "source_text"
    assert base_config.translator.provider == "openai"

    config = base_config.model_copy(update={"output_dir": tmp_path / "output"})
    result = run_project(config)
    assert result.success
    assert result.output_dir.exists()
    assert result.created_files, "应至少产出一个翻译后的表格文件"

    output_path = result.created_files[0]
    assert output_path.exists()

    # 读取导出的表格，检查 translation 列内容
    if output_path.suffix.lower() in {".xlsx", ".xls"}:
        df = pd.read_excel(output_path)
    else:
        df = pd.read_csv(output_path)

    source_col = config.table_adapter.source_column
    translation_col = config.table_adapter.translation_column
    assert translation_col in df.columns
    assert len(df[source_col]) == len(df[translation_col])
    assert (
        df[translation_col]
        .iloc[0]
        .startswith(f"[{config.translator.provider}:{config.translator.model}]")
    )
