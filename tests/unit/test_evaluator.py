from rgb_ai.evaluator import evaluate_output


def test_open_ended_case_returns_not_evaluated_and_preserves_output() -> None:
    result = evaluate_output("freeform answer", None)

    assert result.status == "not_evaluated"
    assert result.passed is None
    assert result.score is None
    assert result.original_output == "freeform answer"


def test_exact_match_passes_and_fails() -> None:
    expected = {"type": "exact_match", "value": "SI", "strip": True}

    assert evaluate_output(" SI\n", expected).status == "passed"
    assert evaluate_output("NO", expected).status == "failed"


def test_semantic_punctuation_difference_is_format_only_failure() -> None:
    expected = {
        "type": "exact_match",
        "value": "no consta",
        "strip": True,
        "semantic": {
            "type": "normalized_match",
            "value": "no consta",
            "case_insensitive": True,
            "punctuation_insensitive": True,
            "whitespace_insensitive": True,
        },
    }

    result = evaluate_output("No consta.", expected)

    assert result.status == "failed"
    assert result.task_correct is True
    assert result.format_compliant is False
    assert result.failure_type == "format_only"


def test_semantic_capitalization_difference_is_format_only_failure() -> None:
    expected = {
        "type": "exact_match",
        "value": "si",
        "strip": True,
        "semantic": {
            "type": "normalized_match",
            "value": "si",
            "case_insensitive": True,
        },
    }

    result = evaluate_output("SI", expected)

    assert result.status == "failed"
    assert result.task_correct is True
    assert result.failure_type == "format_only"


def test_semantic_accent_difference_is_explicitly_allowed() -> None:
    expected = {
        "type": "exact_match",
        "value": "administracion",
        "strip": True,
        "semantic": {
            "type": "normalized_match",
            "value": "administracion",
            "accent_insensitive": True,
        },
    }

    result = evaluate_output("administración", expected)

    assert result.status == "failed"
    assert result.task_correct is True
    assert result.failure_type == "format_only"


def test_correct_fraction_inside_explanatory_text_is_task_correct() -> None:
    expected = {
        "type": "exact_match",
        "value": "1/2",
        "strip": True,
        "semantic": {"type": "fraction", "value": "1/2"},
    }

    result = evaluate_output("La probabilidad es 1/2.", expected)

    assert result.status == "failed"
    assert result.task_correct is True
    assert result.failure_type == "format_only"


def test_correct_code_expression_inside_markdown_fence_is_task_correct() -> None:
    expected = {
        "type": "exact_match",
        "value": "datos[0]",
        "strip": True,
        "semantic": {
            "type": "code_expression",
            "value": "datos[0]",
            "allow_markdown_code_fence": True,
            "whitespace_insensitive": True,
        },
    }

    result = evaluate_output("```python\ndatos[0]\n```", expected)

    assert result.status == "failed"
    assert result.task_correct is True
    assert result.failure_type == "format_only"


def test_semantic_wrong_answer_is_wrong_answer_failure() -> None:
    expected = {
        "type": "exact_match",
        "value": "1/2",
        "strip": True,
        "semantic": {"type": "fraction", "value": "1/2"},
    }

    result = evaluate_output("La probabilidad es 1/3.", expected)

    assert result.status == "failed"
    assert result.task_correct is False
    assert result.failure_type == "wrong_answer"


def test_strict_instruction_following_remains_strict() -> None:
    expected = {
        "type": "exact_match",
        "value": "SI",
        "strip": True,
        "semantic": {
            "type": "normalized_match",
            "value": "SI",
            "punctuation_insensitive": True,
        },
    }

    result = evaluate_output("SI.", expected)

    assert result.status == "failed"
    assert result.task_correct is True
    assert result.format_compliant is False


def test_contains_text_passes_and_fails() -> None:
    expected = {"type": "contains_text", "value": "azul", "case_sensitive": False}

    assert evaluate_output("El cielo es Azul.", expected).status == "passed"
    assert evaluate_output("El cielo es verde.", expected).status == "failed"


def test_json_valid_passes_and_fails_without_repair() -> None:
    expected = {"type": "json_valid"}

    assert evaluate_output('{"ok": true}', expected).status == "passed"
    assert evaluate_output('prefix {"ok": true}', expected).status == "failed"


def test_json_field_equals_passes_and_fails() -> None:
    expected = {"type": "json_field_equals", "field": "category", "value": "filosofia"}

    assert evaluate_output('{"category": "filosofia"}', expected).status == "passed"
    assert evaluate_output('{"category": "literatura"}', expected).status == "failed"


def test_json_field_equals_supports_nested_fields() -> None:
    expected = {"type": "json_field_equals", "field": "route.category", "value": "ciencia"}

    result = evaluate_output('{"route": {"category": "ciencia"}}', expected)

    assert result.status == "passed"


def test_json_field_equals_fails_on_invalid_json_without_repair() -> None:
    expected = {"type": "json_field_equals", "field": "category", "value": "filosofia"}

    result = evaluate_output('{"category": "filosofia"} extra', expected)

    assert result.status == "failed"
    assert result.original_output == '{"category": "filosofia"} extra'


def test_allowed_value_passes_and_fails_for_raw_output() -> None:
    expected = {
        "type": "allowed_value",
        "allowed_values": ["filosofia", "literatura"],
        "strip": True,
    }

    assert evaluate_output("filosofia\n", expected).status == "passed"
    assert evaluate_output("programacion", expected).status == "failed"


def test_allowed_value_passes_and_fails_for_json_field() -> None:
    expected = {
        "type": "allowed_value",
        "field": "category",
        "allowed_values": ["filosofia", "literatura"],
    }

    assert evaluate_output('{"category": "literatura"}', expected).status == "passed"
    assert evaluate_output('{"category": "programacion"}', expected).status == "failed"


def test_invalid_evaluator_config_returns_evaluation_error() -> None:
    result = evaluate_output("anything", {"type": "unknown"})

    assert result.status == "evaluation_error"
    assert result.passed is None
    assert "Unknown evaluator type" in result.details["error"]
