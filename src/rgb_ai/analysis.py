from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


class ResultAnalysisError(ValueError):
    """Raised when benchmark result analysis input is invalid."""


@dataclass(frozen=True)
class AggregateSummary:
    key: str
    model_id: str | None
    provider_model: str | None
    run_id: str | None
    tests: int
    passed: int
    failed: int
    not_evaluated: int
    infrastructure_errors: int
    pass_rate: float | None
    task_correct: int
    task_incorrect: int
    task_accuracy: float | None
    format_only_failures: int
    wrong_answer_failures: int
    total_duration_ms: float
    average_duration_ms: float | None
    total_prompt_tokens: int
    total_output_tokens: int
    average_output_tokens: float | None
    average_output_tokens_per_second: float | None
    estimated_thinking_tokens: int | None
    estimated_response_tokens: int | None
    estimated_thinking_share: float | None


@dataclass(frozen=True)
class FailedCase:
    test_id: str
    category: str
    variant: str
    expected: Any
    response_text: str | None
    evaluation_details: dict[str, Any]


def load_result_files(paths: Iterable[str | Path]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for path_value in paths:
        path = Path(path_value)
        for line_number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(),
            start=1,
        ):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ResultAnalysisError(
                    f"Malformed JSONL in {path} at line {line_number}: {exc.msg}"
                ) from exc
            if not isinstance(row, dict):
                raise ResultAnalysisError(
                    f"Malformed JSONL in {path} at line {line_number}: result must be an object"
                )
            results.append(row)
    return results


def summarize_by_run(results: list[dict[str, Any]]) -> list[AggregateSummary]:
    return _summarize_groups(
        results,
        lambda row: (
            str(row.get("model_id")),
            str(row.get("provider_model")),
            str(row.get("run_id")),
        ),
        lambda key: "|".join(key),
    )


def summarize_by_category(results: list[dict[str, Any]]) -> list[AggregateSummary]:
    return _summarize_groups(
        results,
        lambda row: (str(row.get("category", "unknown")),),
        lambda key: key[0],
    )


def summarize_by_variant(results: list[dict[str, Any]]) -> list[AggregateSummary]:
    return _summarize_groups(
        results,
        lambda row: (str(row.get("variant", "unknown")),),
        lambda key: key[0],
    )


def failed_cases(results: list[dict[str, Any]]) -> list[FailedCase]:
    failures: list[FailedCase] = []
    for row in results:
        evaluation = _dict_value(row.get("evaluation"))
        if evaluation.get("status") != "failed":
            continue
        details = _dict_value(evaluation.get("details"))
        failure_type = evaluation.get("failure_type")
        if failure_type in {"format_only", "wrong_answer"}:
            details = {**details, "failure_type": failure_type}
        failures.append(
            FailedCase(
                test_id=str(row.get("test_id", "")),
                category=str(row.get("category", "")),
                variant=str(row.get("variant", "")),
                expected=details.get("expected", row.get("expected")),
                response_text=row.get("response_text")
                if isinstance(row.get("response_text"), str)
                else None,
                evaluation_details=details,
            )
        )
    return failures


def _summarize_groups(
    results: list[dict[str, Any]],
    key_func,
    display_key_func,
) -> list[AggregateSummary]:
    grouped: dict[tuple[str, ...], list[dict[str, Any]]] = {}
    for row in results:
        grouped.setdefault(key_func(row), []).append(row)

    return [
        _summarize_rows(display_key_func(key), rows)
        for key, rows in sorted(grouped.items(), key=lambda item: display_key_func(item[0]))
    ]


def _summarize_rows(key: str, rows: list[dict[str, Any]]) -> AggregateSummary:
    tests = len(rows)
    passed = sum(1 for row in rows if _status(row) == "passed")
    failed = sum(1 for row in rows if _status(row) == "failed")
    not_evaluated = sum(1 for row in rows if _status(row) == "not_evaluated")
    infrastructure_errors = sum(1 for row in rows if row.get("error") is not None)
    task_correct = sum(1 for row in rows if _task_correct(row) is True)
    task_incorrect = sum(1 for row in rows if _task_correct(row) is False)
    format_only_failures = sum(1 for row in rows if _failure_type(row) == "format_only")
    wrong_answer_failures = sum(1 for row in rows if _failure_type(row) == "wrong_answer")
    task_total = task_correct + task_incorrect
    total_duration_ms = sum(_float_metric(row, "total_duration_ms") for row in rows)
    total_prompt_tokens = sum(_int_metric(row, "prompt_tokens") for row in rows)
    total_output_tokens = sum(_int_metric(row, "output_tokens") for row in rows)
    output_tps_values = [
        value
        for value in (_float_metric_or_none(row, "output_tokens_per_second") for row in rows)
        if value is not None
    ]

    estimated_thinking_tokens = 0
    estimated_response_tokens = 0
    split_available = False
    for row in rows:
        split = _dict_value(row.get("estimated_token_split"))
        if not split.get("available"):
            continue
        thinking_tokens = split.get("estimated_thinking_tokens")
        response_tokens = split.get("estimated_response_tokens")
        if isinstance(thinking_tokens, int) and isinstance(response_tokens, int):
            estimated_thinking_tokens += thinking_tokens
            estimated_response_tokens += response_tokens
            split_available = True

    estimated_total = estimated_thinking_tokens + estimated_response_tokens
    estimated_thinking_share = (
        estimated_thinking_tokens / estimated_total
        if split_available and estimated_total > 0
        else None
    )

    first = rows[0] if rows else {}
    return AggregateSummary(
        key=key,
        model_id=first.get("model_id") if isinstance(first.get("model_id"), str) else None,
        provider_model=first.get("provider_model")
        if isinstance(first.get("provider_model"), str)
        else None,
        run_id=first.get("run_id") if isinstance(first.get("run_id"), str) else None,
        tests=tests,
        passed=passed,
        failed=failed,
        not_evaluated=not_evaluated,
        infrastructure_errors=infrastructure_errors,
        pass_rate=passed / tests if tests else None,
        task_correct=task_correct,
        task_incorrect=task_incorrect,
        task_accuracy=task_correct / task_total if task_total else None,
        format_only_failures=format_only_failures,
        wrong_answer_failures=wrong_answer_failures,
        total_duration_ms=total_duration_ms,
        average_duration_ms=total_duration_ms / tests if tests else None,
        total_prompt_tokens=total_prompt_tokens,
        total_output_tokens=total_output_tokens,
        average_output_tokens=total_output_tokens / tests if tests else None,
        average_output_tokens_per_second=(
            sum(output_tps_values) / len(output_tps_values) if output_tps_values else None
        ),
        estimated_thinking_tokens=estimated_thinking_tokens if split_available else None,
        estimated_response_tokens=estimated_response_tokens if split_available else None,
        estimated_thinking_share=estimated_thinking_share,
    )


def _status(row: dict[str, Any]) -> str | None:
    evaluation = _dict_value(row.get("evaluation"))
    status = evaluation.get("status")
    return status if isinstance(status, str) else None


def _task_correct(row: dict[str, Any]) -> bool | None:
    if row.get("error") is not None:
        return None
    evaluation = _dict_value(row.get("evaluation"))
    task_correct = evaluation.get("task_correct")
    if isinstance(task_correct, bool):
        return task_correct
    status = _status(row)
    if status == "passed":
        return True
    if status == "failed":
        return False
    return None


def _failure_type(row: dict[str, Any]) -> str | None:
    evaluation = _dict_value(row.get("evaluation"))
    failure_type = evaluation.get("failure_type")
    if failure_type in {"format_only", "wrong_answer"}:
        return failure_type
    if _status(row) == "failed":
        return "wrong_answer"
    return None


def _dict_value(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _float_metric(row: dict[str, Any], key: str) -> float:
    value = _float_metric_or_none(row, key)
    return value if value is not None else 0.0


def _float_metric_or_none(row: dict[str, Any], key: str) -> float | None:
    value = _dict_value(row.get("metrics")).get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def _int_metric(row: dict[str, Any], key: str) -> int:
    value = _dict_value(row.get("metrics")).get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        return 0
    return value
