import json

import pytest

from rgb_ai.analysis import (
    ResultAnalysisError,
    failed_cases,
    load_result_files,
    summarize_by_category,
    summarize_by_run,
    summarize_by_variant,
)


def _row(
    *,
    test_id="TEST_001",
    model_id="mdl_qwen3_06b",
    provider_model="qwen3:0.6b",
    run_id="run_1",
    category="routing",
    variant="baseline",
    status="passed",
    error=None,
    duration=1000.0,
    prompt_tokens=10,
    output_tokens=20,
    output_tps=5.0,
    split=True,
    response_text="biblioteca",
    details=None,
):
    return {
        "test_id": test_id,
        "model_id": model_id,
        "provider_model": provider_model,
        "run_id": run_id,
        "category": category,
        "variant": variant,
        "response_text": response_text,
        "metrics": {
            "total_duration_ms": duration,
            "prompt_tokens": prompt_tokens,
            "output_tokens": output_tokens,
            "output_tokens_per_second": output_tps,
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
            "details": details or {"expected": "biblioteca", "actual": response_text},
        },
        "error": error,
    }


def test_load_result_files_reads_multiple_files(tmp_path) -> None:
    first = tmp_path / "first.jsonl"
    second = tmp_path / "second.jsonl"
    first.write_text(json.dumps(_row(test_id="A")) + "\n", encoding="utf-8")
    second.write_text(json.dumps(_row(test_id="B")) + "\n", encoding="utf-8")

    rows = load_result_files([first, second])

    assert [row["test_id"] for row in rows] == ["A", "B"]


def test_load_result_files_rejects_malformed_jsonl(tmp_path) -> None:
    path = tmp_path / "bad.jsonl"
    path.write_text('{"test_id": "A"\n', encoding="utf-8")

    with pytest.raises(ResultAnalysisError, match="line 1"):
        load_result_files([path])


def test_load_result_files_allows_empty_input(tmp_path) -> None:
    path = tmp_path / "empty.jsonl"
    path.write_text("", encoding="utf-8")

    assert load_result_files([path]) == []


def test_overall_summary_multiple_models_and_runs() -> None:
    rows = [
        _row(test_id="A", status="passed", duration=1000.0, output_tokens=20),
        _row(test_id="B", status="failed", duration=2000.0, output_tokens=30),
        _row(
            test_id="C",
            model_id="mdl_other",
            provider_model="other:1b",
            run_id="run_2",
            status="not_evaluated",
            duration=500.0,
            output_tokens=10,
        ),
    ]

    summaries = summarize_by_run(rows)

    assert len(summaries) == 2
    first = next(summary for summary in summaries if summary.run_id == "run_1")
    assert first.tests == 2
    assert first.passed == 1
    assert first.failed == 1
    assert first.pass_rate == 0.5
    assert first.total_duration_ms == 3000.0
    assert first.average_duration_ms == 1500.0
    assert first.total_output_tokens == 50
    assert first.average_output_tokens == 25


def test_category_grouping_and_estimated_thinking_aggregation() -> None:
    rows = [
        _row(category="routing", status="passed"),
        _row(category="routing", status="failed"),
        _row(category="coding", status="passed", output_tokens=10),
    ]

    summaries = summarize_by_category(rows)

    routing = next(summary for summary in summaries if summary.key == "routing")
    assert routing.tests == 2
    assert routing.passed == 1
    assert routing.failed == 1
    assert routing.estimated_thinking_tokens == 30
    assert routing.estimated_response_tokens == 10
    assert routing.estimated_thinking_share == 0.75


def test_variant_grouping_with_missing_estimated_split() -> None:
    rows = [
        _row(variant="baseline", split=False),
        _row(variant="instructions", split=True),
    ]

    summaries = summarize_by_variant(rows)

    baseline = next(summary for summary in summaries if summary.key == "baseline")
    instructions = next(summary for summary in summaries if summary.key == "instructions")
    assert baseline.estimated_thinking_tokens is None
    assert baseline.estimated_thinking_share is None
    assert instructions.estimated_thinking_tokens == 15


def test_infrastructure_error_count() -> None:
    rows = [
        _row(error={"type": "OllamaConnectionError", "message": "network down"}),
        _row(status="passed"),
    ]

    summary = summarize_by_run(rows)[0]

    assert summary.infrastructure_errors == 1


def test_failed_case_extraction_is_compact_data() -> None:
    rows = [
        _row(test_id="PASS", status="passed"),
        _row(
            test_id="FAIL",
            category="classification",
            variant="instructions",
            status="failed",
            response_text="programacion",
            details={"expected": "filosofia", "actual": "programacion"},
        ),
    ]

    failures = failed_cases(rows)

    assert len(failures) == 1
    assert failures[0].test_id == "FAIL"
    assert failures[0].category == "classification"
    assert failures[0].expected == "filosofia"
    assert failures[0].response_text == "programacion"
