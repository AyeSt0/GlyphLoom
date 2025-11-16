"""Stage 1 pipeline: load table, fake translate, export."""

from __future__ import annotations

import logging
from pathlib import Path
from time import perf_counter
from typing import Callable, List, Sequence

from glyphloom_core.adapters.table_adapter import TableAdapter
from glyphloom_core.core.models import PipelineResult, PipelineStep, ProjectConfig
from glyphloom_core.translators.openai_http import OpenAIHttpTranslator

logger = logging.getLogger("glyphloom.core.pipeline")


def run_project(config: ProjectConfig) -> PipelineResult:
    """对外入口：按“提取 -> 翻译 -> 导出”顺序执行流水线。"""

    steps: List[PipelineStep] = []
    adapter = _run_stage(
        name="extract",
        message="加载源表并补齐翻译需要的列",
        steps=steps,
        runner=lambda: _run_extract(config),
    )
    _run_stage(
        name="translate",
        message="使用假翻译填充 translation 列",
        steps=steps,
        runner=lambda: _run_translate(adapter, config),
    )
    created_files = _run_stage(
        name="export",
        message="导出翻译结果文件",
        steps=steps,
        runner=lambda: _run_export(adapter, config),
    )

    return PipelineResult(
        project_name=config.name,
        steps=steps,
        output_dir=config.output_dir,
        created_files=created_files,
    )


def _run_stage(
    name: str,
    message: str,
    steps: List[PipelineStep],
    runner: Callable[[], Sequence[Path] | TableAdapter | None],
) -> Sequence[Path] | TableAdapter | None:
    """统一的阶段执行包装，负责计时与记录结果。"""

    logger.info("[%s] %s", name, message)
    start = perf_counter()
    succeeded = True
    created: Sequence[Path] | TableAdapter | None = None
    try:
        created = runner()
        return created
    except Exception:
        succeeded = False
        raise
    finally:
        elapsed = perf_counter() - start
        steps.append(
            PipelineStep(
                name=name,
                description=f"{message} (elapsed {elapsed:.2f}s)",
                succeeded=succeeded,
            )
        )


def _run_extract(config: ProjectConfig) -> TableAdapter:
    """提取阶段：创建 TableAdapter，加载并补齐必需列。"""

    adapter = TableAdapter(config.source, config.table_adapter)
    adapter.load()
    adapter.ensure_columns()
    logger.info(
        "已加载源表 %s ，列数 %d",
        config.source.path,
        adapter._require_data().shape[1],  # noqa: SLF001 仅用于读取 DataFrame 维度
    )
    return adapter


def _run_translate(adapter: TableAdapter, config: ProjectConfig) -> None:
    """翻译阶段：调用 Translator 批量翻译源文本，并写回 translation 列。"""

    df = adapter._require_data()  # noqa: SLF001 直接复用适配器内部 DataFrame
    source_column = config.table_adapter.source_column
    translation_column = config.table_adapter.translation_column

    if source_column not in df.columns:
        raise ValueError(f"源文本列 {source_column} 不存在，无法翻译")

    translator = OpenAIHttpTranslator(config.translator)
    texts = df[source_column].fillna("").astype(str).tolist()
    translations = translator.translate_batch(texts)
    if len(translations) != len(texts):
        raise ValueError("翻译数量与源行数不一致，终止流水线")

    df[translation_column] = translations
    logger.info(
        "翻译完成，共处理 %d 行，写入列 %s",
        len(df),
        translation_column,
    )


def _run_export(adapter: TableAdapter, config: ProjectConfig) -> List[Path]:
    """导出阶段：将 DataFrame 写出到输出目录。"""

    output_dir = config.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    # 输出文件沿用输入文件名，便于对照
    output_path = output_dir / config.source.path.name
    adapter.save(output_path)
    logger.info("导出完成：%s", output_path)
    return [output_path]
