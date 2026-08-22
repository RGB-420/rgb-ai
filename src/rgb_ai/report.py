from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from rgb_ai.analysis import (
    failed_cases,
    summarize_by_category,
    summarize_by_run,
    summarize_by_variant,
)

CATEGORY_COLUMNS = [
    ("instruction_following", "Instructions"),
    ("structured_output", "JSON"),
    ("routing", "Routing"),
    ("classification", "Classification"),
    ("context_use", "Context"),
    ("reasoning", "Reasoning"),
    ("coding", "Coding"),
    ("tool_selection", "Tools"),
]


def generate_markdown_report(
    rows: list[dict[str, Any]],
    *,
    source_files: list[str],
    generated_at: datetime | None = None,
) -> str:
    generated = generated_at or datetime.now(UTC)
    run_summaries = summarize_by_run(rows)
    lines = [
        "# RGB-AI Benchmark Results",
        "",
        "## Experiment Overview",
        "",
        "Raw JSONL files are the source of truth. Estimated thinking metrics are non-authoritative and use `character_ratio_v1` when available.",
        "",
        "Strict pass rate measures whether the complete benchmark requirement was satisfied, including required output format.",
        "Task accuracy measures whether the underlying task answer was correct according to deterministic semantic rules configured for that benchmark case.",
        "",
    ]

    if not rows:
        lines.extend(
            [
                "No benchmark results were found.",
                "",
                "## Reproducibility",
                "",
            ]
        )
        lines.extend(_reproducibility_lines(rows, source_files, generated))
        return "\n".join(lines) + "\n"

    lines.extend(
        _table(
            [
                "Model",
                "Model ID",
                "Run ID",
                "Tests",
                "Pass",
                "Fail",
                "Pass rate",
                "Task accuracy",
                "Format-only",
                "Wrong answer",
                "Total duration",
                "Avg time/test",
                "Prompt tokens",
                "Output tokens",
                "Output tok/s",
                "Est. thinking",
            ],
            [
                [
                    summary.provider_model,
                    summary.model_id,
                    summary.run_id,
                    str(summary.tests),
                    str(summary.passed),
                    str(summary.failed),
                    _percent(summary.pass_rate),
                    _percent(summary.task_accuracy),
                    str(summary.format_only_failures),
                    str(summary.wrong_answer_failures),
                    _ms(summary.total_duration_ms),
                    _ms(summary.average_duration_ms),
                    str(summary.total_prompt_tokens),
                    str(summary.total_output_tokens),
                    _number(summary.average_output_tokens_per_second),
                    _percent(summary.estimated_thinking_share),
                ]
                for summary in run_summaries
            ],
        )
    )

    lines.extend(["", "## Overall Comparison", ""])
    lines.extend(
        _table(
            [
                "Model",
                "Strict pass",
                "Strict pass rate",
                "Task accuracy",
                "Format-only",
                "Wrong answer",
                "Avg time/test",
                "Output tok/s",
                "Est. thinking",
            ],
            [
                [
                    summary.provider_model,
                    f"{summary.passed}/{summary.tests}",
                    _percent(summary.pass_rate),
                    _percent(summary.task_accuracy),
                    str(summary.format_only_failures),
                    str(summary.wrong_answer_failures),
                    _ms(summary.average_duration_ms),
                    _number(summary.average_output_tokens_per_second),
                    _percent(summary.estimated_thinking_share),
                ]
                for summary in run_summaries
            ],
        )
    )
    lines.append("")
    lines.append("No automatic production recommendation is made from these measurements.")

    lines.extend(["", "## Category Comparison", ""])
    lines.extend(_category_table(rows))

    lines.extend(["", "## Variant Comparison", ""])
    lines.append("Current variant groups are not necessarily balanced and should not be interpreted causally yet.")
    lines.append("")
    lines.extend(_variant_table(rows))

    lines.extend(["", "## Efficiency", ""])
    lines.extend(
        _table(
            [
                "Model",
                "Avg time/test",
                "Total output tokens",
                "Output tok/s",
                "Est. thinking tokens",
                "Est. response tokens",
                "Est. thinking share",
            ],
            [
                [
                    summary.provider_model,
                    _ms(summary.average_duration_ms),
                    str(summary.total_output_tokens),
                    _number(summary.average_output_tokens_per_second),
                    _optional_int(summary.estimated_thinking_tokens),
                    _optional_int(summary.estimated_response_tokens),
                    _percent(summary.estimated_thinking_share),
                ]
                for summary in run_summaries
            ],
        )
    )

    lines.extend(["", "## Failed Cases", ""])
    lines.extend(_failed_case_sections(rows))

    lines.extend(["", "## Per-Category Observations", ""])
    lines.append("This report exposes measurements only. It does not generate subjective recommendations or production routing decisions.")

    lines.extend(["", "## Reproducibility", ""])
    lines.extend(_reproducibility_lines(rows, source_files, generated))
    return "\n".join(lines) + "\n"


def write_markdown_report(markdown: str, output_path: str | Path) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")


def _category_table(rows: list[dict[str, Any]]) -> list[str]:
    by_model = _rows_by_model(rows)
    table_rows = []
    for model, model_rows in sorted(by_model.items()):
        category_summaries = {
            summary.key: summary for summary in summarize_by_category(model_rows)
        }
        table_rows.append(
            [model]
            + [
                _percent(category_summaries[column_key].pass_rate)
                + " / "
                + _percent(category_summaries[column_key].task_accuracy)
                if column_key in category_summaries
                else "n/a"
                for column_key, _ in CATEGORY_COLUMNS
            ]
        )
    return [
        "Cells show `strict pass rate / task accuracy`.",
        "",
        *_table(["Model"] + [label for _, label in CATEGORY_COLUMNS], table_rows),
    ]


def _variant_table(rows: list[dict[str, Any]]) -> list[str]:
    variants = sorted({str(row.get("variant", "unknown")) for row in rows})
    by_model = _rows_by_model(rows)
    table_rows = []
    for model, model_rows in sorted(by_model.items()):
        variant_summaries = {
            summary.key: summary for summary in summarize_by_variant(model_rows)
        }
        table_rows.append(
            [model]
            + [
                _percent(variant_summaries[variant].pass_rate)
                + " / "
                + _percent(variant_summaries[variant].task_accuracy)
                if variant in variant_summaries
                else "n/a"
                for variant in variants
            ]
        )
    return [
        "Cells show `strict pass rate / task accuracy`.",
        "",
        *_table(["Model"] + variants, table_rows),
    ]


def _failed_case_sections(rows: list[dict[str, Any]]) -> list[str]:
    by_model = _rows_by_model(rows)
    lines: list[str] = []
    for model, model_rows in sorted(by_model.items()):
        failures = failed_cases(model_rows)
        lines.extend([f"### {escape_markdown(model)}", ""])
        if not failures:
            lines.extend(["No failed deterministic cases.", ""])
            continue
        lines.extend(
            _table(
                [
                    "Test ID",
                    "Category",
                    "Variant",
                    "Failure type",
                    "Expected",
                    "Actual response",
                ],
                [
                    [
                        failure.test_id,
                        failure.category,
                        failure.variant,
                        failure.evaluation_details.get("failure_type", ""),
                        str(failure.expected),
                        _compact(failure.response_text),
                    ]
                    for failure in failures
                ],
            )
        )
        lines.append("")
    return lines


def _reproducibility_lines(
    rows: list[dict[str, Any]],
    source_files: list[str],
    generated_at: datetime,
) -> list[str]:
    schema_versions = sorted({str(row.get("schema_version", "unknown")) for row in rows})
    case_count = len({str(row.get("test_id", "")) for row in rows if row.get("test_id")})
    return [
        f"- Generated at: `{generated_at.isoformat()}`",
        f"- Benchmark result schema versions: `{', '.join(schema_versions) if schema_versions else 'n/a'}`",
        f"- Benchmark cases represented: `{case_count}`",
        "- Source result files:",
        *[f"  - `{_relative_source(path)}`" for path in source_files],
        "- Raw JSONL result files are the source of truth.",
    ]


def _rows_by_model(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get("provider_model", "unknown"))].append(row)
    return grouped


def _table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    escaped_headers = [escape_markdown(str(header)) for header in headers]
    lines = [
        "| " + " | ".join(escaped_headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(escape_markdown(str(value)) for value in row) + " |")
    return lines


def escape_markdown(text: str) -> str:
    return text.replace("\\", "\\\\").replace("|", "\\|").replace("\n", "<br>")


def _relative_source(path: str) -> str:
    path_obj = Path(path)
    if not path_obj.is_absolute():
        return path_obj.as_posix()
    try:
        return path_obj.relative_to(Path.cwd()).as_posix()
    except ValueError:
        return path_obj.name


def _percent(value: float | None) -> str:
    return "n/a" if value is None else f"{value * 100:.1f}%"


def _number(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.2f}"


def _ms(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.2f} ms"


def _optional_int(value: int | None) -> str:
    return "n/a" if value is None else str(value)


def _compact(text: str | None, limit: int = 140) -> str:
    if text is None:
        return ""
    single_line = " ".join(text.split())
    if len(single_line) <= limit:
        return single_line
    return f"{single_line[: limit - 3]}..."
