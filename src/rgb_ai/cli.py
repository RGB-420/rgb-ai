from __future__ import annotations

import argparse
import sys
from pathlib import Path

from rgb_ai.cases import BenchmarkCase, load_benchmark_cases
from rgb_ai.config import ConfigError, load_config
from rgb_ai.models import (
    ModelRegistryEntry,
    load_model_registry,
    validate_registry_against_ollama,
)
from rgb_ai.ollama import OllamaClient, OllamaError
from rgb_ai.results import JsonlResultStore, ResultStorageError
from rgb_ai.runner import ModelNotRunnableError, new_run_id, run_benchmark_case


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        return args.func(args)
    except ResultStorageError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 4
    except (ConfigError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except OllamaError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 3


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m rgb_ai")
    subparsers = parser.add_subparsers(dest="command", required=True)

    models = subparsers.add_parser("models")
    model_subparsers = models.add_subparsers(dest="models_command", required=True)
    model_subparsers.add_parser("list").set_defaults(func=_models_list)
    model_subparsers.add_parser("check-installed").set_defaults(func=_models_check_installed)

    benchmark = subparsers.add_parser("benchmark")
    benchmark_subparsers = benchmark.add_subparsers(
        dest="benchmark_command",
        required=True,
    )
    benchmark_subparsers.add_parser("list").set_defaults(func=_benchmark_list)
    run_parser = benchmark_subparsers.add_parser("run")
    run_parser.add_argument("--model", required=True)
    selector = run_parser.add_mutually_exclusive_group(required=True)
    selector.add_argument("--test")
    selector.add_argument("--category")
    run_parser.set_defaults(func=_benchmark_run)

    return parser


def _models_list(args: argparse.Namespace) -> int:
    config = load_config()
    registry = load_model_registry(config.model_registry_path)
    for model in registry:
        enabled = "enabled" if model.enabled else "disabled"
        eligible = "eligible" if model.benchmark_eligible else "not-eligible"
        print(
            f"{model.model_id}\t{model.provider_model}\t{model.role}\t{enabled}\t{eligible}"
        )
    return 0


def _models_check_installed(args: argparse.Namespace) -> int:
    config = load_config()
    registry = load_model_registry(config.model_registry_path)
    with OllamaClient(config.ollama_base_url, config.request_timeout_seconds) as client:
        discovered = client.list_models()

    statuses = validate_registry_against_ollama(registry, discovered)
    for status in statuses:
        state = "installed" if status.installed else "missing"
        print(f"{status.model_id}\t{status.provider_model}\t{state}")
    return 0


def _benchmark_list(args: argparse.Namespace) -> int:
    config = load_config()
    cases = load_benchmark_cases(config.benchmark_cases_path)
    for case in cases:
        print(f"{case.test_id}\t{case.category}\t{case.variant}")
    return 0


def _benchmark_run(args: argparse.Namespace) -> int:
    config = load_config()
    registry = load_model_registry(config.model_registry_path)
    cases = load_benchmark_cases(config.benchmark_cases_path)
    model = _find_model(registry, args.model)
    selected_cases = _select_cases(cases, test_id=args.test, category=args.category)

    run_id = new_run_id()
    result_store = JsonlResultStore(config.results_path)
    exit_code = 0
    with OllamaClient(config.ollama_base_url, config.request_timeout_seconds) as client:
        for case in selected_cases:
            try:
                result = run_benchmark_case(
                    model=model,
                    case=case,
                    client=client,
                    result_store=result_store,
                    run_id=run_id,
                )
            except ModelNotRunnableError as exc:
                print(f"ERROR: {exc}", file=sys.stderr)
                return 2
            except ResultStorageError:
                raise

            _print_result_summary(result, config.results_path)
            if result.error is not None:
                exit_code = 3

    return exit_code


def _find_model(
    registry: list[ModelRegistryEntry],
    model_id: str,
) -> ModelRegistryEntry:
    for model in registry:
        if model.model_id == model_id:
            return model
    raise ValueError(f"Unknown model_id: {model_id}")


def _select_cases(
    cases: list[BenchmarkCase],
    *,
    test_id: str | None,
    category: str | None,
) -> list[BenchmarkCase]:
    if test_id is not None:
        selected = [case for case in cases if case.test_id == test_id]
        if not selected:
            raise ValueError(f"Unknown test_id: {test_id}")
        return selected

    selected = [case for case in cases if case.category == category]
    if not selected:
        raise ValueError(f"No benchmark cases found for category: {category}")
    return selected


def _print_result_summary(result, results_path: Path) -> None:
    status = result.evaluation["status"].upper()
    if status == "PASSED":
        status = "PASS"
    elif status == "FAILED":
        status = "FAIL"

    print(f"TEST: {result.test_id}")
    print(f"MODEL: {result.provider_model}")
    print(f"VARIANT: {result.variant}")
    print(f"RESULT: {status}")
    print()
    print("Response:")
    print(result.response_text or "")
    print()
    print("Metrics:")
    print(f"prompt_tokens: {result.metrics.get('prompt_tokens')}")
    print(f"output_tokens: {result.metrics.get('output_tokens')}")
    print(f"total_duration_ms: {result.metrics.get('total_duration_ms')}")
    print(
        "output_tokens_per_second: "
        f"{result.metrics.get('output_tokens_per_second')}"
    )
    print()
    print(f"Stored: {results_path}")


if __name__ == "__main__":
    raise SystemExit(main())
