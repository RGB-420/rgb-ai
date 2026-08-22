import json

import pytest

from rgb_ai.cases import parse_benchmark_case
from rgb_ai.reevaluate import ReEvaluationError, reevaluate_results


def _case():
    return parse_benchmark_case(
        {
            "test_id": "REASON_PROB_001",
            "category": "reasoning",
            "prompt": "Probability?",
            "expected": {
                "type": "exact_match",
                "value": "1/2",
                "strip": True,
                "semantic": {"type": "fraction", "value": "1/2"},
            },
        }
    )


def _row(response_text="La probabilidad es 1/2.", error=None):
    return {
        "schema_version": 1,
        "result_id": "res_1",
        "run_id": "run_1",
        "test_id": "REASON_PROB_001",
        "response_text": response_text,
        "thinking_text": "short reasoning",
        "raw_provider_response": {"response": response_text, "done": True},
        "metrics": {"total_duration_ms": 100.0, "output_tokens": 10},
        "evaluation": {"status": "failed", "score": 0.0, "details": {}},
        "error": error,
    }


def test_reevaluate_preserves_raw_response_metrics_and_source_file(tmp_path) -> None:
    output = tmp_path / "derived.jsonl"
    source = tmp_path / "source.jsonl"
    source.write_text(json.dumps(_row()) + "\n", encoding="utf-8")

    derived = reevaluate_results(
        [_row()],
        [_case()],
        source_file=source,
        output_path=output,
    )

    stored = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
    assert derived == stored
    assert stored[0]["result_id"] == "res_1"
    assert stored[0]["run_id"] == "run_1"
    assert stored[0]["raw_provider_response"] == {"response": "La probabilidad es 1/2.", "done": True}
    assert stored[0]["metrics"]["total_duration_ms"] == 100.0
    assert stored[0]["thinking_text"] == "short reasoning"
    assert stored[0]["evaluation"]["status"] == "failed"
    assert stored[0]["evaluation"]["task_correct"] is True
    assert stored[0]["evaluation"]["failure_type"] == "format_only"
    assert stored[0]["reevaluation"]["schema_version"] == 2
    assert stored[0]["reevaluation"]["source_file"] == "source.jsonl"


def test_reevaluate_does_not_modify_source_jsonl(tmp_path) -> None:
    output = tmp_path / "derived.jsonl"
    source = tmp_path / "source.jsonl"
    original = json.dumps(_row()) + "\n"
    source.write_text(original, encoding="utf-8")

    reevaluate_results([_row()], [_case()], source_file=source, output_path=output)

    assert source.read_text(encoding="utf-8") == original


def test_reevaluate_infrastructure_error_is_not_fabricated(tmp_path) -> None:
    output = tmp_path / "derived.jsonl"
    row = _row(
        response_text=None,
        error={"type": "OllamaConnectionError", "message": "network down"},
    )

    derived = reevaluate_results([row], [_case()], source_file="source.jsonl", output_path=output)

    assert derived[0]["evaluation"]["status"] == "not_evaluated"
    assert derived[0]["evaluation"]["task_correct"] is None
    assert derived[0]["error"]["type"] == "OllamaConnectionError"


def test_reevaluate_requires_matching_case_definition(tmp_path) -> None:
    with pytest.raises(ReEvaluationError, match="No benchmark case"):
        reevaluate_results([_row()], [], source_file="source.jsonl", output_path=tmp_path / "x.jsonl")
