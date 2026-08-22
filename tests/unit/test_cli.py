import json

import pytest

import rgb_ai.cli as cli
from rgb_ai.ollama import OllamaConnectionError, OllamaModel

try:
    from helpers import make_generate_response
except ImportError:  # pragma: no cover
    from tests.unit.helpers import make_generate_response


def _write_registry(path, *, enabled=True, eligible=True) -> None:
    path.write_text(
        json.dumps(
            {
                "models": [
                    {
                        "model_id": "mdl_qwen3_06b",
                        "provider": "ollama",
                        "provider_model": "qwen3:0.6b",
                        "role": "small_generalist_candidate",
                        "enabled": enabled,
                        "benchmark_eligible": eligible,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )


def _write_multi_model_registry(path) -> None:
    path.write_text(
        json.dumps(
            {
                "models": [
                    {
                        "model_id": "mdl_qwen3_06b",
                        "provider": "ollama",
                        "provider_model": "qwen3:0.6b",
                        "role": "small_generalist_candidate",
                        "enabled": True,
                        "benchmark_eligible": True,
                    },
                    {
                        "model_id": "mdl_gemma3_1b",
                        "provider": "ollama",
                        "provider_model": "gemma3:1b",
                        "role": "generalist_candidate",
                        "enabled": True,
                        "benchmark_eligible": True,
                    },
                    {
                        "model_id": "mdl_embeddinggemma_latest",
                        "provider": "ollama",
                        "provider_model": "embeddinggemma:latest",
                        "role": "embedding_candidate",
                        "enabled": True,
                        "benchmark_eligible": False,
                    },
                ]
            }
        ),
        encoding="utf-8",
    )


def _write_cases(path) -> None:
    path.write_text(
        '{"test_id":"INSTRUCT_EXACT_001","category":"instruction_following",'
        '"variant":"baseline","prompt":"Say SI",'
        '"expected":{"type":"exact_match","value":"SI"}}\n'
        '{"test_id":"INSTRUCT_EXACT_002","category":"instruction_following",'
        '"variant":"baseline","prompt":"Say OK",'
        '"expected":{"type":"exact_match","value":"OK"}}\n'
        '{"test_id":"CONTEXT_FACT_001","category":"context_use",'
        '"variant":"context","system_prompt":"Use context.",'
        '"context":[{"text":"Marcelo nació en Terrassa.","source_id":"s","chunk_id":"c"}],'
        '"prompt":"Where?","expected":{"type":"contains_text","value":"Terrassa"}}\n',
        encoding="utf-8",
    )


def _configure_paths(monkeypatch, tmp_path):
    registry = tmp_path / "models.json"
    cases = tmp_path / "cases.jsonl"
    results = tmp_path / "results.jsonl"
    _write_registry(registry)
    _write_cases(cases)
    monkeypatch.setenv("RGB_AI_MODEL_REGISTRY", str(registry))
    monkeypatch.setenv("RGB_AI_BENCHMARK_CASES", str(cases))
    monkeypatch.setenv("RGB_AI_RESULTS_PATH", str(results))
    return registry, cases, results


def _configure_multi_model_paths(monkeypatch, tmp_path):
    registry, cases, results = _configure_paths(monkeypatch, tmp_path)
    _write_multi_model_registry(registry)
    return registry, cases, results


class FakeOllamaClient:
    response_text = "SI"
    error: Exception | None = None
    response_queue = []
    error_queue = []
    generated_calls = []

    def __init__(self, *args, **kwargs) -> None:
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args) -> None:
        pass

    def list_models(self):
        return [
            OllamaModel(
                name="qwen3:0.6b",
                modified_at=None,
                size_bytes=123,
                digest="abc",
                details={"family": "qwen3"},
            )
        ]

    def generate(self, **kwargs):
        self.__class__.generated_calls.append(kwargs)
        error = self.__class__.error
        if self.__class__.error_queue:
            error = self.__class__.error_queue.pop(0)
        if error is not None:
            raise error
        response_text = self.__class__.response_text
        if self.__class__.response_queue:
            response_text = self.__class__.response_queue.pop(0)
        return make_generate_response(response_text)


@pytest.fixture(autouse=True)
def reset_fake_client() -> None:
    FakeOllamaClient.response_text = "SI"
    FakeOllamaClient.error = None
    FakeOllamaClient.response_queue = []
    FakeOllamaClient.error_queue = []
    FakeOllamaClient.generated_calls = []


def test_cli_models_list(monkeypatch, tmp_path, capsys) -> None:
    _configure_paths(monkeypatch, tmp_path)

    exit_code = cli.main(["models", "list"])

    assert exit_code == 0
    assert "mdl_qwen3_06b" in capsys.readouterr().out


def test_cli_models_check_installed(monkeypatch, tmp_path, capsys) -> None:
    _configure_paths(monkeypatch, tmp_path)
    monkeypatch.setattr(cli, "OllamaClient", FakeOllamaClient)

    exit_code = cli.main(["models", "check-installed"])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "installed" in output


def test_cli_benchmark_list(monkeypatch, tmp_path, capsys) -> None:
    _configure_paths(monkeypatch, tmp_path)

    exit_code = cli.main(["benchmark", "list"])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "INSTRUCT_EXACT_001" in output
    assert "CONTEXT_FACT_001" in output


def test_cli_benchmark_run_single_test_with_mocked_ollama(
    monkeypatch,
    tmp_path,
    capsys,
) -> None:
    _, _, results = _configure_paths(monkeypatch, tmp_path)
    monkeypatch.setattr(cli, "OllamaClient", FakeOllamaClient)

    exit_code = cli.main(
        [
            "benchmark",
            "run",
            "--model",
            "mdl_qwen3_06b",
            "--test",
            "INSTRUCT_EXACT_001",
        ]
    )

    output = capsys.readouterr().out
    stored = [json.loads(line) for line in results.read_text(encoding="utf-8").splitlines()]
    assert exit_code == 0
    assert "RESULT: PASS" in output
    assert stored[0]["test_id"] == "INSTRUCT_EXACT_001"
    assert FakeOllamaClient.generated_calls[0]["prompt"] == "TASK:\nSay SI"
    assert "Response:" in output


def test_cli_benchmark_run_category_with_mocked_ollama(
    monkeypatch,
    tmp_path,
    capsys,
) -> None:
    _, _, results = _configure_paths(monkeypatch, tmp_path)
    monkeypatch.setattr(cli, "OllamaClient", FakeOllamaClient)
    FakeOllamaClient.response_text = "Terrassa"

    exit_code = cli.main(
        [
            "benchmark",
            "run",
            "--model",
            "mdl_qwen3_06b",
            "--category",
            "context_use",
        ]
    )

    output = capsys.readouterr().out
    stored = [json.loads(line) for line in results.read_text(encoding="utf-8").splitlines()]
    assert exit_code == 0
    assert "CONTEXT_FACT_001" in output
    assert stored[0]["variant"] == "context"
    assert "CONTEXT:" in FakeOllamaClient.generated_calls[0]["prompt"]


def test_cli_benchmark_run_all_tests_uses_shared_run_id_and_unique_result_ids(
    monkeypatch,
    tmp_path,
    capsys,
) -> None:
    _, _, results = _configure_paths(monkeypatch, tmp_path)
    monkeypatch.setattr(cli, "OllamaClient", FakeOllamaClient)
    FakeOllamaClient.response_queue = ["SI", "OK", "Terrassa"]

    exit_code = cli.main(
        [
            "benchmark",
            "run",
            "--model",
            "mdl_qwen3_06b",
            "--all-tests",
        ]
    )

    output = capsys.readouterr().out
    stored = [json.loads(line) for line in results.read_text(encoding="utf-8").splitlines()]
    assert exit_code == 0
    assert len(stored) == 3
    assert len({row["run_id"] for row in stored}) == 1
    assert len({row["result_id"] for row in stored}) == 3
    assert "[01/03] INSTRUCT_EXACT_001" in output
    assert "[03/03] CONTEXT_FACT_001" in output
    assert "RUN: run_" in output
    assert "Tests: 3" in output
    assert "Passed: 3" in output
    assert "Failed: 0" in output
    assert "Not evaluated: 0" in output
    assert "Infrastructure errors: 0" in output
    assert "Response:" not in output


def test_cli_benchmark_run_all_tests_continues_after_evaluator_fail(
    monkeypatch,
    tmp_path,
    capsys,
) -> None:
    _, _, results = _configure_paths(monkeypatch, tmp_path)
    monkeypatch.setattr(cli, "OllamaClient", FakeOllamaClient)
    FakeOllamaClient.response_queue = ["SI", "NO", "Terrassa"]

    exit_code = cli.main(
        [
            "benchmark",
            "run",
            "--model",
            "mdl_qwen3_06b",
            "--all-tests",
        ]
    )

    output = capsys.readouterr().out
    stored = [json.loads(line) for line in results.read_text(encoding="utf-8").splitlines()]
    assert exit_code == 0
    assert len(stored) == 3
    assert stored[1]["evaluation"]["status"] == "failed"
    assert stored[2]["test_id"] == "CONTEXT_FACT_001"
    assert "Failed: 1" in output
    assert "[02/03] INSTRUCT_EXACT_002" in output


def test_cli_benchmark_run_all_tests_continues_after_recoverable_execution_error(
    monkeypatch,
    tmp_path,
    capsys,
) -> None:
    _, _, results = _configure_paths(monkeypatch, tmp_path)
    monkeypatch.setattr(cli, "OllamaClient", FakeOllamaClient)
    FakeOllamaClient.response_queue = ["SI", "Terrassa"]
    FakeOllamaClient.error_queue = [
        None,
        OllamaConnectionError("temporary network issue"),
        None,
    ]

    exit_code = cli.main(
        [
            "benchmark",
            "run",
            "--model",
            "mdl_qwen3_06b",
            "--all-tests",
        ]
    )

    output = capsys.readouterr().out
    stored = [json.loads(line) for line in results.read_text(encoding="utf-8").splitlines()]
    assert exit_code == 3
    assert len(stored) == 3
    assert stored[1]["error"]["type"] == "OllamaConnectionError"
    assert stored[2]["test_id"] == "CONTEXT_FACT_001"
    assert "Infrastructure errors: 1" in output
    assert "[02/03] INSTRUCT_EXACT_002" in output
    assert "EVALUATION_ERROR" in output


def test_cli_benchmark_run_all_tests_stops_on_result_storage_failure(
    monkeypatch,
    tmp_path,
    capsys,
) -> None:
    _configure_paths(monkeypatch, tmp_path)
    monkeypatch.setattr(cli, "OllamaClient", FakeOllamaClient)
    FakeOllamaClient.response_queue = ["SI", "OK", "Terrassa"]

    class FailingStore:
        calls = 0

        def __init__(self, path) -> None:
            self.path = path

        def append(self, result) -> None:
            self.__class__.calls += 1
            if self.__class__.calls == 2:
                raise cli.ResultStorageError("disk full")

    monkeypatch.setattr(cli, "JsonlResultStore", FailingStore)

    exit_code = cli.main(
        [
            "benchmark",
            "run",
            "--model",
            "mdl_qwen3_06b",
            "--all-tests",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 4
    assert FailingStore.calls == 2
    assert len(FakeOllamaClient.generated_calls) == 2
    assert "[01/03] INSTRUCT_EXACT_001" in captured.out
    assert "[02/03]" not in captured.out
    assert "disk full" in captured.err


def test_cli_benchmark_run_all_models_all_tests_excludes_ineligible_and_separates_runs(
    monkeypatch,
    tmp_path,
    capsys,
) -> None:
    _, _, results = _configure_multi_model_paths(monkeypatch, tmp_path)
    monkeypatch.setattr(cli, "OllamaClient", FakeOllamaClient)
    FakeOllamaClient.response_queue = ["SI", "OK", "Terrassa", "SI", "OK", "Terrassa"]

    exit_code = cli.main(["benchmark", "run", "--all-models", "--all-tests"])

    output = capsys.readouterr().out
    result_files = sorted(
        path for path in results.parent.glob("*.jsonl") if path.name != "cases.jsonl"
    )
    rows = [
        json.loads(line)
        for path in result_files
        for line in path.read_text(encoding="utf-8").splitlines()
    ]
    qwen_rows = [row for row in rows if row["provider_model"] == "qwen3:0.6b"]
    gemma_rows = [row for row in rows if row["provider_model"] == "gemma3:1b"]
    assert exit_code == 0
    assert len(result_files) == 2
    assert len(rows) == 6
    assert len(qwen_rows) == 3
    assert len(gemma_rows) == 3
    assert len({row["run_id"] for row in qwen_rows}) == 1
    assert len({row["run_id"] for row in gemma_rows}) == 1
    assert qwen_rows[0]["run_id"] != gemma_rows[0]["run_id"]
    assert len({row["result_id"] for row in rows}) == 6
    assert "embeddinggemma" not in output
    assert "MODEL 1/2: qwen3:0.6b" in output
    assert "MODEL 2/2: gemma3:1b" in output
    assert "Models attempted: 2" in output
    assert "Models completed: 2" in output
    assert "Total benchmark executions: 6" in output


def test_cli_benchmark_run_all_models_continues_after_model_infrastructure_errors(
    monkeypatch,
    tmp_path,
    capsys,
) -> None:
    _, _, results = _configure_multi_model_paths(monkeypatch, tmp_path)
    monkeypatch.setattr(cli, "OllamaClient", FakeOllamaClient)
    FakeOllamaClient.error_queue = [
        OllamaConnectionError("first model unavailable"),
        OllamaConnectionError("first model unavailable"),
        OllamaConnectionError("first model unavailable"),
        None,
        None,
        None,
    ]
    FakeOllamaClient.response_queue = ["SI", "OK", "Terrassa"]

    exit_code = cli.main(["benchmark", "run", "--all-models", "--all-tests"])

    output = capsys.readouterr().out
    rows = [
        json.loads(line)
        for path in sorted(
            path for path in results.parent.glob("*.jsonl") if path.name != "cases.jsonl"
        )
        for line in path.read_text(encoding="utf-8").splitlines()
    ]
    assert exit_code == 3
    assert len(rows) == 6
    assert sum(1 for row in rows if row["error"] is not None) == 3
    assert "MODEL 2/2: gemma3:1b" in output
    assert "Infrastructure errors: 3" in output


def test_cli_benchmark_run_all_models_stops_on_result_storage_failure(
    monkeypatch,
    tmp_path,
    capsys,
) -> None:
    _configure_multi_model_paths(monkeypatch, tmp_path)
    monkeypatch.setattr(cli, "OllamaClient", FakeOllamaClient)

    class FailingStore:
        calls = 0

        def __init__(self, path) -> None:
            self.path = path

        def append(self, result) -> None:
            self.__class__.calls += 1
            if self.__class__.calls == 2:
                raise cli.ResultStorageError("disk full")

    monkeypatch.setattr(cli, "JsonlResultStore", FailingStore)

    exit_code = cli.main(["benchmark", "run", "--all-models", "--all-tests"])

    captured = capsys.readouterr()
    assert exit_code == 4
    assert FailingStore.calls == 2
    assert "MODEL 2/2" not in captured.out
    assert "disk full" in captured.err


def test_cli_benchmark_run_all_models_requires_all_tests(monkeypatch, tmp_path, capsys) -> None:
    _configure_multi_model_paths(monkeypatch, tmp_path)

    exit_code = cli.main(["benchmark", "run", "--all-models", "--test", "INSTRUCT_EXACT_001"])

    assert exit_code == 2
    assert "--all-models requires --all-tests" in capsys.readouterr().err


def test_cli_results_summarize(monkeypatch, tmp_path, capsys) -> None:
    result_file = tmp_path / "results.jsonl"
    result_file.write_text(
        json.dumps(
            {
                "test_id": "A",
                "model_id": "mdl_qwen3_06b",
                "provider_model": "qwen3:0.6b",
                "run_id": "run_1",
                "category": "routing",
                "variant": "baseline",
                "metrics": {
                    "total_duration_ms": 1000.0,
                    "prompt_tokens": 10,
                    "output_tokens": 20,
                    "output_tokens_per_second": 5.0,
                },
                "estimated_token_split": {
                    "available": True,
                    "estimated_thinking_tokens": 15,
                    "estimated_response_tokens": 5,
                },
                "evaluation": {"status": "passed", "score": 1.0, "details": {}},
                "error": None,
            }
        )
        + "\n",
        encoding="utf-8",
    )

    exit_code = cli.main(["results", "summarize", "--file", str(result_file)])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Overall" in output
    assert "MODEL: qwen3:0.6b" in output
    assert "By category" in output
    assert "routing" in output
    assert "Estimated thinking metrics are non-authoritative" in output


def test_cli_results_failures(tmp_path, capsys) -> None:
    result_file = tmp_path / "results.jsonl"
    result_file.write_text(
        json.dumps(
            {
                "test_id": "FAIL_001",
                "category": "routing",
                "variant": "baseline",
                "response_text": "general",
                "evaluation": {
                    "status": "failed",
                    "score": 0.0,
                    "details": {"expected": "biblioteca", "actual": "general"},
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )

    exit_code = cli.main(["results", "failures", "--file", str(result_file)])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "FAIL_001" in output
    assert "EXPECTED: biblioteca" in output
    assert "ACTUAL: general" in output


def test_cli_results_report(tmp_path, capsys) -> None:
    result_file = tmp_path / "results.jsonl"
    output_file = tmp_path / "report.md"
    result_file.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "test_id": "A",
                "model_id": "mdl_qwen3_06b",
                "provider_model": "qwen3:0.6b",
                "run_id": "run_1",
                "category": "routing",
                "variant": "baseline",
                "metrics": {
                    "total_duration_ms": 1000.0,
                    "prompt_tokens": 10,
                    "output_tokens": 20,
                    "output_tokens_per_second": 5.0,
                },
                "estimated_token_split": {
                    "available": True,
                    "estimated_thinking_tokens": 15,
                    "estimated_response_tokens": 5,
                },
                "evaluation": {"status": "passed", "score": 1.0, "details": {}},
                "error": None,
            }
        )
        + "\n",
        encoding="utf-8",
    )

    exit_code = cli.main(
        [
            "results",
            "report",
            "--file",
            str(result_file),
            "--output",
            str(output_file),
        ]
    )

    assert exit_code == 0
    assert "Wrote report" in capsys.readouterr().out
    markdown = output_file.read_text(encoding="utf-8")
    assert "# RGB-AI Benchmark Results" in markdown
    assert "qwen3:0.6b" in markdown


def test_cli_results_report_returns_nonzero_for_malformed_result_file(
    tmp_path,
    capsys,
) -> None:
    result_file = tmp_path / "broken.jsonl"
    output_file = tmp_path / "report.md"
    result_file.write_text("{not json}\n", encoding="utf-8")

    exit_code = cli.main(
        [
            "results",
            "report",
            "--file",
            str(result_file),
            "--output",
            str(output_file),
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "Malformed JSONL" in captured.err
    assert "line 1" in captured.err
    assert not output_file.exists()


def test_cli_returns_nonzero_for_unknown_model(monkeypatch, tmp_path, capsys) -> None:
    _configure_paths(monkeypatch, tmp_path)

    exit_code = cli.main(
        [
            "benchmark",
            "run",
            "--model",
            "missing",
            "--test",
            "INSTRUCT_EXACT_001",
        ]
    )

    assert exit_code == 2
    assert "Unknown model_id" in capsys.readouterr().err


def test_cli_returns_nonzero_for_ollama_infrastructure_error(
    monkeypatch,
    tmp_path,
    capsys,
) -> None:
    _, _, results = _configure_paths(monkeypatch, tmp_path)
    monkeypatch.setattr(cli, "OllamaClient", FakeOllamaClient)
    FakeOllamaClient.error = OllamaConnectionError("network down")

    exit_code = cli.main(
        [
            "benchmark",
            "run",
            "--model",
            "mdl_qwen3_06b",
            "--test",
            "INSTRUCT_EXACT_001",
        ]
    )

    stored = [json.loads(line) for line in results.read_text(encoding="utf-8").splitlines()]
    assert exit_code == 3
    assert stored[0]["error"]["type"] == "OllamaConnectionError"
    assert "RESULT: EVALUATION_ERROR" in capsys.readouterr().out
