from datetime import UTC, datetime

from rgb_ai.report import escape_markdown, generate_markdown_report


def _row(
    *,
    provider_model="qwen3:0.6b",
    model_id="mdl_qwen3_06b",
    run_id="run_1",
    test_id="INST|001",
    category="instruction_following",
    variant="baseline",
    status="passed",
    task_correct=None,
    failure_type=None,
    split=True,
    response_text="SI",
):
    if task_correct is None:
        task_correct = True if status == "passed" else False if status == "failed" else None
    return {
        "schema_version": 1,
        "provider_model": provider_model,
        "model_id": model_id,
        "run_id": run_id,
        "test_id": test_id,
        "category": category,
        "variant": variant,
        "response_text": response_text,
        "metrics": {
            "total_duration_ms": 1000.0,
            "prompt_tokens": 10,
            "output_tokens": 20,
            "output_tokens_per_second": 5.0,
        },
        "estimated_token_split": (
            {
                "available": True,
                "estimated_thinking_tokens": 15,
                "estimated_response_tokens": 5,
            }
            if split
            else {"available": False}
        ),
        "evaluation": {
            "status": status,
            "score": 1.0 if status == "passed" else 0.0,
            "task_correct": task_correct,
            "format_compliant": status == "passed",
            "failure_type": failure_type,
            "details": {"expected": "SI", "actual": response_text},
        },
        "error": None,
    }


def test_generate_markdown_report_includes_multi_model_comparison() -> None:
    markdown = generate_markdown_report(
        [
            _row(),
            _row(
                provider_model="gemma3:1b",
                model_id="mdl_gemma3_1b",
                run_id="run_2",
                category="routing",
                variant="instructions",
                status="failed",
                response_text="general",
            ),
        ],
        source_files=["results/qwen.jsonl", "C:/tmp/gemma.jsonl"],
        generated_at=datetime(2026, 8, 22, tzinfo=UTC),
    )

    assert "# RGB-AI Benchmark Results" in markdown
    assert "## Overall Comparison" in markdown
    assert "## Category Comparison" in markdown
    assert "## Variant Comparison" in markdown
    assert "## Efficiency" in markdown
    assert "qwen3:0.6b" in markdown
    assert "gemma3:1b" in markdown
    assert "results/qwen.jsonl" in markdown
    assert "gemma.jsonl" in markdown
    assert "No automatic production recommendation" in markdown
    assert "Strict pass rate measures" in markdown
    assert "Task accuracy measures" in markdown


def test_generate_markdown_report_failed_cases_and_markdown_escaping() -> None:
    markdown = generate_markdown_report(
        [
            _row(
                status="failed",
                task_correct=True,
                failure_type="format_only",
                test_id="TOOL|BAD",
                response_text="search_library | extra",
            )
        ],
        source_files=["results/qwen.jsonl"],
        generated_at=datetime(2026, 8, 22, tzinfo=UTC),
    )

    assert "TOOL\\|BAD" in markdown
    assert "search_library \\| extra" in markdown
    assert "format_only" in markdown


def test_generate_markdown_report_shows_strict_and_task_metrics() -> None:
    markdown = generate_markdown_report(
        [
            _row(test_id="PASS", status="passed", task_correct=True),
            _row(
                test_id="FORMAT",
                status="failed",
                task_correct=True,
                failure_type="format_only",
                response_text="SI.",
            ),
            _row(
                test_id="WRONG",
                status="failed",
                task_correct=False,
                failure_type="wrong_answer",
                response_text="NO",
            ),
        ],
        source_files=["results/qwen.jsonl"],
        generated_at=datetime(2026, 8, 22, tzinfo=UTC),
    )

    assert "33.3%" in markdown
    assert "66.7%" in markdown
    assert "Format-only" in markdown
    assert "Wrong answer" in markdown


def test_generate_markdown_report_handles_missing_estimated_split() -> None:
    markdown = generate_markdown_report(
        [_row(split=False)],
        source_files=["results/qwen.jsonl"],
        generated_at=datetime(2026, 8, 22, tzinfo=UTC),
    )

    assert "n/a" in markdown


def test_generate_markdown_report_handles_empty_results() -> None:
    markdown = generate_markdown_report(
        [],
        source_files=["results/empty.jsonl"],
        generated_at=datetime(2026, 8, 22, tzinfo=UTC),
    )

    assert "No benchmark results were found." in markdown
    assert "results/empty.jsonl" in markdown


def test_escape_markdown() -> None:
    assert escape_markdown("a|b\nc") == "a\\|b<br>c"
