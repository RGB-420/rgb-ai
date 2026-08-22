from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass
from fractions import Fraction
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
    task_correct: bool | None
    format_compliant: bool | None
    failure_type: Literal["format_only", "wrong_answer"] | None
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
            task_correct=None,
            format_compliant=None,
            failure_type=None,
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
            task_correct=None,
            format_compliant=None,
            failure_type=None,
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
        expected,
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
        expected,
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
        expected,
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
        expected,
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
    expected: dict[str, Any] | None = None,
) -> EvaluationResult:
    task_correct, semantic_details = _task_correctness(
        original_output,
        strict_passed=passed,
        expected=expected,
    )
    failure_type = None
    if not passed:
        failure_type = "format_only" if task_correct else "wrong_answer"

    return EvaluationResult(
        status="passed" if passed else "failed",
        passed=passed,
        score=1.0 if passed else 0.0,
        original_output=original_output,
        task_correct=task_correct,
        format_compliant=passed,
        failure_type=failure_type,
        details={**details, **semantic_details},
    )


def _task_correctness(
    output: str,
    *,
    strict_passed: bool,
    expected: dict[str, Any] | None,
) -> tuple[bool, dict[str, Any]]:
    if strict_passed:
        return True, {}
    if expected is None:
        return False, {}

    semantic = expected.get("semantic")
    if semantic is None:
        return False, {}
    if not isinstance(semantic, dict):
        raise EvaluatorConfigError("semantic evaluator config must be an object")

    semantic_type = _required_str(semantic, "type")
    if semantic_type == "normalized_match":
        matched = _semantic_normalized_match(output, semantic)
    elif semantic_type == "contains_text":
        matched = _semantic_contains_text(output, semantic)
    elif semantic_type == "fraction":
        matched = _semantic_fraction(output, semantic)
    elif semantic_type == "code_expression":
        matched = _semantic_code_expression(output, semantic)
    elif semantic_type == "allowed_value":
        matched = _semantic_allowed_value(output, semantic)
    else:
        raise EvaluatorConfigError(f"Unknown semantic evaluator type: {semantic_type}")

    return matched, {"semantic": {"type": semantic_type, "matched": matched}}


def _semantic_normalized_match(output: str, semantic: dict[str, Any]) -> bool:
    expected_value = _required_str(semantic, "value")
    return _normalize_text(output, semantic) == _normalize_text(expected_value, semantic)


def _semantic_contains_text(output: str, semantic: dict[str, Any]) -> bool:
    expected_value = _required_str(semantic, "value")
    return _normalize_text(expected_value, semantic) in _normalize_text(output, semantic)


def _semantic_fraction(output: str, semantic: dict[str, Any]) -> bool:
    expected_value = _required_str(semantic, "value")
    expected_fraction = _parse_fraction(expected_value)
    if expected_fraction is None:
        raise EvaluatorConfigError("fraction semantic value must be a simple fraction")
    return expected_fraction in _fractions_in_text(output)


def _semantic_code_expression(output: str, semantic: dict[str, Any]) -> bool:
    expected_value = _required_str(semantic, "value")
    candidates = [output]
    if _optional_bool(semantic, "allow_markdown_code_fence", default=False):
        candidates.extend(_markdown_code_blocks(output))

    expected_normalized = _normalize_code(expected_value, semantic)
    for candidate in candidates:
        normalized_candidate = _normalize_code(candidate, semantic)
        if normalized_candidate == expected_normalized:
            return True
        for line in candidate.splitlines():
            if _normalize_code(line, semantic) == expected_normalized:
                return True
    return False


def _semantic_allowed_value(output: str, semantic: dict[str, Any]) -> bool:
    allowed_values = semantic.get("allowed_values")
    if not isinstance(allowed_values, list) or not allowed_values:
        raise EvaluatorConfigError("allowed_value semantic requires non-empty allowed_values list")
    if any(not isinstance(value, str) for value in allowed_values):
        raise EvaluatorConfigError("allowed_value semantic values must be strings")

    actual = _normalize_text(output, semantic)
    return any(actual == _normalize_text(value, semantic) for value in allowed_values)


def _normalize_text(text: str, config: dict[str, Any]) -> str:
    normalized = text.strip() if _optional_bool(config, "strip", default=True) else text
    if _optional_bool(config, "whitespace_insensitive", default=False):
        normalized = " ".join(normalized.split())
    if _optional_bool(config, "case_insensitive", default=False):
        normalized = normalized.casefold()
    if _optional_bool(config, "accent_insensitive", default=False):
        normalized = "".join(
            char
            for char in unicodedata.normalize("NFKD", normalized)
            if not unicodedata.combining(char)
        )
    if _optional_bool(config, "punctuation_insensitive", default=False):
        normalized = "".join(
            char for char in normalized if not unicodedata.category(char).startswith("P")
        )
    return normalized


def _normalize_code(text: str, config: dict[str, Any]) -> str:
    normalized = text.strip()
    if _optional_bool(config, "whitespace_insensitive", default=False):
        normalized = re.sub(r"\s+", "", normalized)
    return normalized


def _parse_fraction(text: str) -> Fraction | None:
    match = re.fullmatch(r"\s*(-?\d+)\s*/\s*(-?\d+)\s*", text)
    if match is None:
        return None
    try:
        return Fraction(int(match.group(1)), int(match.group(2)))
    except ZeroDivisionError:
        return None


def _fractions_in_text(text: str) -> set[Fraction]:
    fractions: set[Fraction] = set()
    for match in re.finditer(r"(?<![\w/])(-?\d+)\s*/\s*(-?\d+)(?![\w/])", text):
        try:
            fractions.add(Fraction(int(match.group(1)), int(match.group(2))))
        except ZeroDivisionError:
            continue
    return fractions


def _markdown_code_blocks(text: str) -> list[str]:
    return [
        match.group(1).strip()
        for match in re.finditer(r"```(?:[^\n`]*)\n?(.*?)```", text, flags=re.DOTALL)
    ]


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
