import json

import pytest

from rgb_ai.results import (
    BenchmarkResult,
    JsonlResultStore,
    ResultStorageError,
    load_jsonl_results,
)


def _result(result_id: str, response_text: str = "integración funcionando"):
    return BenchmarkResult(
        schema_version=1,
        result_id=result_id,
        run_id="run_1",
        timestamp="2026-08-22T00:00:00+00:00",
        test_id="TEST_001",
        category="instruction",
        variant="baseline",
        model_id="mdl_qwen3_06b",
        provider="ollama",
        provider_model="qwen3:0.6b",
        prompt="prompt",
        formatted_prompt="prompt",
        system_prompt=None,
        context=[],
        examples=[],
        generation_options={},
        response_text=response_text,
        raw_provider_response={"response": response_text},
        metrics={"total_duration_ms": 1.0},
        evaluation={"status": "passed", "score": 1.0, "details": {}},
        error=None,
    )


def test_jsonl_result_store_appends_and_preserves_unicode(tmp_path) -> None:
    path = tmp_path / "nested" / "results.jsonl"
    store = JsonlResultStore(path)

    store.append(_result("res_1"))

    rows = load_jsonl_results(path)
    assert rows[0]["response_text"] == "integración funcionando"
    assert path.parent.exists()


def test_jsonl_result_store_does_not_overwrite_existing_results(tmp_path) -> None:
    path = tmp_path / "results.jsonl"
    store = JsonlResultStore(path)

    store.append(_result("res_1", "uno"))
    store.append(_result("res_2", "dos"))

    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    assert [row["result_id"] for row in rows] == ["res_1", "res_2"]
    assert [row["response_text"] for row in rows] == ["uno", "dos"]


def test_jsonl_result_store_reports_write_failure(tmp_path) -> None:
    directory_path = tmp_path / "as_directory"
    directory_path.mkdir()
    store = JsonlResultStore(directory_path)

    with pytest.raises(ResultStorageError, match="Unable to append"):
        store.append(_result("res_1"))
