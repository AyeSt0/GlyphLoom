from pathlib import Path

from glyphloom_core.core.config_loader import load_project_config
from glyphloom_core.core.pipeline import run_project


def test_pipeline_run(tmp_path: Path) -> None:
    base_config = load_project_config()
    config = base_config.model_copy(update={"output_dir": tmp_path / "output"})
    result = run_project(config)
    assert result.success
    assert result.output_dir.exists()
    assert result.created_files
    assert any(path.suffix == ".txt" for path in result.created_files)
