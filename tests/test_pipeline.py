from pathlib import Path

from glyphloom_core.core.config_loader import load_project_config
from glyphloom_core.core.pipeline import run_project


def test_pipeline_run(tmp_path: Path) -> None:
    base_config = load_project_config()
    # 新增断言：默认配置应包含 table_adapter/translator 信息
    assert base_config.table_adapter.source_column == "source_text"
    assert base_config.translator.provider == "openai"

    config = base_config.model_copy(update={"output_dir": tmp_path / "output"})
    result = run_project(config)
    assert result.success
    assert result.output_dir.exists()
    assert result.created_files
    assert any(path.suffix == ".txt" for path in result.created_files)
