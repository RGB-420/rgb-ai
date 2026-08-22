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


def _write_cases(path) -> None:
    path.write_text(
        '{"test_id":"INSTRUCT_EXACT_001","category":"instruction_following",'
        '"variant":"baseline","prompt":"Say SI",'
        '"expected":{"type":"exact_match","value":"SI"}}\n'
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


class FakeOllamaClient:
    response_text = "SI"
    error: Exception | None = None
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
        if self.__class__.error is not None:
            raise self.__class__.error
        return make_generate_response(self.__class__.response_text)


@pytest.fixture(autouse=True)
def reset_fake_client() -> None:
    FakeOllamaClient.response_text = "SI"
    FakeOllamaClient.error = None
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
