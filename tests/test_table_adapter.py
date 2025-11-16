import pandas as pd
from pathlib import Path

from glyphloom_core.core.config_loader import load_project_config
from glyphloom_core.adapters.table_adapter import TableAdapter


def test_table_adapter_roundtrip(tmp_path: Path) -> None:
    config = load_project_config()
    adapter = TableAdapter(config.source, config.table_adapter)
    adapter.load()
    adapter.ensure_columns()
    output_file = tmp_path / "table_output.xlsx"
    adapter.save(output_file)

    assert output_file.exists()
    df = pd.read_excel(output_file)
    for column_name in config.table_adapter.column_mapping.values():
        assert column_name in df.columns
