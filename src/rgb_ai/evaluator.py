from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Literal


EvaluationStatus = Literal["passed", "failed", "not_evaluated", "evaluation_error"]


class EvaluatorConfigError(ValueError):
    """Raised when evaluator configuration is invalid."""


@dataclass(frozen=True)
class EvaluationResult:
    status: EvaluationStatus
    passed: bool | None
    score: float | None
    original_output: str
    details: dict[str, Any]


def evaluate_output(
    output: str,
    expected: dict[str, Any] | None,
) -> EvaluationResult:
    if expected is None:
        return EvaluationResult(
            status="not_evaluated",
            passed=None,
            score=None,
            original_output=output,
            details={"reason": "No evaluator configured"},
        )

    try:
        evaluator_type = _required_str(expected, "type")
        if evaluator_type == "exact_match":
            return _exact_match(output, expected)
        if evaluator_type == "contains_text":
            return _contains_text(output, expected)
        if evaluator_type == "json_valid":
            return _json_valid(output)
        if evaluator_type == "json_field_equals":
            return _json_field_equals(output, expected)
        if evaluator_type == "allowed_value":
            return _allowed_value(output, expected)
        raise EvaluatorConfigError(f"Unknown evaluator type: {evaluator_type}")
    except EvaluatorConfigError as exc:
        return EvaluationResult(
            status="evaluation_error",
            passed=None,
            score=None,
            original_output=output,
            details={"error": str(exc)},
        )


def _exact_match(output: str, expected: dict[str, Any]) -> EvaluationResult:
    expected_value = _required_str(expected, "value")
    actual = _maybe_strip(output, expected)
    passed = actual == expected_value
    return _pass_fail(
        output,
        passed,
        {
            "expected": expected_value,
            "actual": actual,
        },
    )


def _contains_text(output: str, expected: dict[str, Any]) -> EvaluationResult:
    expected_value = _required_str(expected, "value")
    case_sensitive = _optional_bool(expected, "case_sensitive", default=True)
    haystack = output if case_sensitive else output.lower()
    needle = expected_value if case_sensitive else expected_value.lower()
    passed = needle in haystack
    return _pass_fail(
        output,
        passed,
        {
            "expected_text": expected_value,
            "case_sensitive": case_sensitive,
        },
    )


def _json_valid(output: str) -> EvaluationResult:
    try:
        parsed = json.loads(output)
    except json.JSONDecodeError as exc:
        return _pass_fail(output, False, {"error": exc.msg})
    return _pass_fail(output, True, {"parsed_type": type(parsed).__name__})


def _json_field_equals(output: str, expected: dict[str, Any]) -> EvaluationResult:
    field = _required_str(expected, "field")
    expected_value = expected.get("value")

    parsed, error = _parse_json_object(output)
    if error is not None:
        return _pass_fail(output, False, {"error": error})

    actual = _get_field(parsed, field)
    passed = actual == expected_value
    return _pass_fail(
        output,
        passed,
        {
            "field": field,
            "expected": expected_value,
            "actual": actual,
        },
    )


def _allowed_value(output: str, expected: dict[str, Any]) -> EvaluationResult:
    allowed_values = expected.get("allowed_values")
    if not isinstance(allowed_values, list) or not allowed_values:
        raise EvaluatorConfigError("allowed_value requires non-empty allowed_values list")

    field = expected.get("field")
    if field is not None:
        if not isinstance(field, str) or not field:
            raise EvaluatorConfigError("allowed_value field must be a non-empty string")
        parsed, error = _parse_json_object(output)
        if error is not None:
            return _pass_fail(output, False, {"error": error})
        actual = _get_field(parsed, field)
    else:
        actual = _maybe_strip(output, expected)

    passed = actual in allowed_values
    return _pass_fail(
        output,
        passed,
        {
            "allowed_values": allowed_values,
            "actual": actual,
            "field": field,
        },
    )


def _parse_json_object(output: str) -> tuple[dict[str, Any], str | None]:
    try:
        parsed = json.loads(output)
    except json.JSONDecodeError as exc:
        return {}, exc.msg
    if not isinstance(parsed, dict):
        return {}, "JSON output must be an object"
    return parsed, None


def _get_field(data: dict[str, Any], field: str) -> Any:
    current: Any = data
    for part in field.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def _pass_fail(
    original_output: str,
    passed: bool,
    details: dict[str, Any],
) -> EvaluationResult:
    return EvaluationResult(
        status="passed" if passed else "failed",
        passed=passed,
        score=1.0 if passed else 0.0,
        original_output=original_output,
        details=details,
    )


def _maybe_strip(output: str, expected: dict[str, Any]) -> str:
    if _optional_bool(expected, "strip", default=False):
        return output.strip()
    return output


def _required_str(data: dict[str, Any], field: str) -> str:
    value = data.get(field)
    if not isinstance(value, str) or not value:
        raise EvaluatorConfigError(f"Evaluator missing required string field {field}")
    return value


def _optional_bool(data: dict[str, Any], field: str, *, default: bool) -> bool:
    value = data.get(field, default)
    if not isinstance(value, bool):
        raise EvaluatorConfigError(f"Evaluator field {field} must be a boolean")
    return value
