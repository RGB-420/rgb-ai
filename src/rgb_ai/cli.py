from __future__ import annotations

import argparse
import sys
from time import perf_counter
from pathlib import Path

from rgb_ai.analysis import (
    ResultAnalysisError,
    failed_cases,
    load_result_files,
    summarize_by_category,
    summarize_by_run,
    summarize_by_variant,
)
from rgb_ai.cases import BenchmarkCase, load_benchmark_cases
from rgb_ai.config import ConfigError, load_config
from rgb_ai.models import (
    ModelRegistryEntry,
    load_model_registry,
    validate_registry_against_ollama,
)
from rgb_ai.ollama import OllamaClient, OllamaError
from rgb_ai.report import generate_markdown_report, write_markdown_report
from rgb_ai.reevaluate import ReEvaluationError, reevaluate_results
from rgb_ai.results import JsonlResultStore, ResultStorageError
from rgb_ai.runner import ModelNotRunnableError, new_run_id, run_benchmark_case


def main(argv: list[str] | None = None) -> int:
    _configure_stdio()
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        return args.func(args)
    except (ResultAnalysisError, ReEvaluationError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
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
    run_parser.add_argument("--model")
    run_parser.add_argument("--all-models", action="store_true")
    selector = run_parser.add_mutually_exclusive_group(required=True)
    selector.add_argument("--test")
    selector.add_argument("--category")
    selector.add_argument("--all-tests", action="store_true")
    run_parser.set_defaults(func=_benchmark_run)

    results = subparsers.add_parser("results")
    results_subparsers = results.add_subparsers(dest="results_command", required=True)
    summarize_parser = results_subparsers.add_parser("summarize")
    _add_result_file_args(summarize_parser)
    summarize_parser.set_defaults(func=_results_summarize)
    failures_parser = results_subparsers.add_parser("failures")
    _add_result_file_args(failures_parser)
    failures_parser.set_defaults(func=_results_failures)
    report_parser = results_subparsers.add_parser("report")
    _add_result_file_args(report_parser)
    report_parser.add_argument("--output", required=True)
    report_parser.set_defaults(func=_results_report)
    reevaluate_parser = results_subparsers.add_parser("reevaluate")
    reevaluate_parser.add_argument("--file", required=True)
    reevaluate_parser.add_argument("--output", required=True)
    reevaluate_parser.set_defaults(func=_results_reevaluate)

    return parser


def _add_result_file_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--file",
        action="append",
        required=True,
        dest="files",
        help="Benchmark result JSONL file. May be provided more than once.",
    )


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

    if args.all_models:
        if not args.all_tests:
            raise ValueError("--all-models requires --all-tests")
        if args.model is not None:
            raise ValueError("--all-models cannot be combined with --model")
        return _benchmark_run_all_models(config, registry, cases)

    if args.model is None:
        raise ValueError("--model is required unless --all-models is used")

    model = _find_model(registry, args.model)
    selected_cases = _select_cases(
        cases,
        test_id=args.test,
        category=args.category,
        all_tests=args.all_tests,
    )

    run_id = new_run_id()
    result_store = JsonlResultStore(config.results_path)
    exit_code = 0
    results = []
    started = perf_counter()
    with OllamaClient(config.ollama_base_url, config.request_timeout_seconds) as client:
        for index, case in enumerate(selected_cases, start=1):
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

            results.append(result)
            if args.all_tests:
                _print_progress_line(index, len(selected_cases), result)
            else:
                _print_result_summary(result, config.results_path)
            if result.error is not None:
                exit_code = 3

    if args.all_tests:
        _print_batch_summary(
            run_id=run_id,
            model=model,
            results=results,
            duration_seconds=perf_counter() - started,
            results_path=config.results_path,
        )

    return exit_code


def _benchmark_run_all_models(config, registry, cases: list[BenchmarkCase]) -> int:
    models = [
        model
        for model in registry
        if model.enabled and model.benchmark_eligible
    ]
    if not models:
        raise ValueError("No enabled benchmark-eligible models found")

    experiment_started = perf_counter()
    total_results = []
    completed_models = 0
    result_paths: list[Path] = []
    exit_code = 0

    with OllamaClient(config.ollama_base_url, config.request_timeout_seconds) as client:
        for model_index, model in enumerate(models, start=1):
            run_id = new_run_id()
            result_path = _result_path_for_model_run(config.results_path, model, run_id)
            result_paths.append(result_path)
            result_store = JsonlResultStore(result_path)
            model_results = []
            model_started = perf_counter()

            print(f"MODEL {model_index}/{len(models)}: {model.provider_model}")
            print()
            for case_index, case in enumerate(cases, start=1):
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
                    exit_code = 2
                    break

                model_results.append(result)
                total_results.append(result)
                _print_progress_line(case_index, len(cases), result)
                if result.error is not None:
                    exit_code = 3

            if len(model_results) == len(cases):
                completed_models += 1

            print()
            print("MODEL SUMMARY")
            print(f"Passed: {_count_status(model_results, 'passed')}")
            print(f"Failed: {_count_status(model_results, 'failed')}")
            print(f"Not evaluated: {_count_status(model_results, 'not_evaluated')}")
            print(f"Infrastructure errors: {sum(1 for result in model_results if result.error is not None)}")
            print(f"Duration: {perf_counter() - model_started:.2f}s")
            print(f"Results: {result_path}")
            print()

    print("EXPERIMENT SUMMARY")
    print(f"Models attempted: {len(models)}")
    print(f"Models completed: {completed_models}")
    print(f"Total benchmark executions: {len(total_results)}")
    print(f"Passes: {_count_status(total_results, 'passed')}")
    print(f"Failures: {_count_status(total_results, 'failed')}")
    print(f"Infrastructure errors: {sum(1 for result in total_results if result.error is not None)}")
    print(f"Total wall-clock duration: {perf_counter() - experiment_started:.2f}s")
    print("Results:")
    for path in result_paths:
        print(f"- {path}")
    return exit_code


def _results_summarize(args: argparse.Namespace) -> int:
    rows = load_result_files(args.files)
    if not rows:
        print("No benchmark results found.")
        return 0

    run_summaries = summarize_by_run(rows)
    category_summaries = summarize_by_category(rows)
    variant_summaries = summarize_by_variant(rows)

    print("Overall")
    for summary in run_summaries:
        _print_overall_summary(summary)

    print()
    print("By category")
    _print_group_table(category_summaries)

    print()
    print("By variant")
    _print_group_table(variant_summaries)
    print()
    print("Estimated thinking metrics are non-authoritative (character_ratio_v1).")
    return 0


def _results_failures(args: argparse.Namespace) -> int:
    rows = load_result_files(args.files)
    failures = failed_cases(rows)
    if not failures:
        print("No failed benchmark cases found.")
        return 0

    for failure in failures:
        print(f"TEST: {failure.test_id}")
        print(f"CATEGORY: {failure.category}")
        print(f"VARIANT: {failure.variant}")
        print(f"EXPECTED: {failure.expected}")
        print(f"ACTUAL: {_compact_text(failure.response_text)}")
        print(f"DETAILS: {failure.evaluation_details}")
        print()
    return 0


def _results_report(args: argparse.Namespace) -> int:
    rows = load_result_files(args.files)
    markdown = generate_markdown_report(rows, source_files=args.files)
    write_markdown_report(markdown, args.output)
    print(f"Wrote report: {args.output}")
    return 0


def _results_reevaluate(args: argparse.Namespace) -> int:
    config = load_config()
    cases = load_benchmark_cases(config.benchmark_cases_path)
    rows = load_result_files([args.file])
    reevaluated = reevaluate_results(
        rows,
        cases,
        source_file=args.file,
        output_path=args.output,
    )
    print(f"Re-evaluated results: {len(reevaluated)}")
    print(f"Wrote derived results: {args.output}")
    return 0


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
    all_tests: bool = False,
) -> list[BenchmarkCase]:
    if all_tests:
        return cases

    if test_id is not None:
        selected = [case for case in cases if case.test_id == test_id]
        if not selected:
            raise ValueError(f"Unknown test_id: {test_id}")
        return selected

    selected = [case for case in cases if case.category == category]
    if not selected:
        raise ValueError(f"No benchmark cases found for category: {category}")
    return selected


def _display_status(result) -> str:
    status = result.evaluation["status"].upper()
    if status == "PASSED":
        return "PASS"
    if status == "FAILED":
        return "FAIL"
    return status


def _print_progress_line(index: int, total: int, result) -> None:
    print(f"[{index:02d}/{total:02d}] {result.test_id:<28} {_display_status(result)}")


def _print_batch_summary(
    *,
    run_id: str,
    model: ModelRegistryEntry,
    results: list,
    duration_seconds: float,
    results_path: Path,
) -> None:
    passed = sum(1 for result in results if result.evaluation["status"] == "passed")
    failed = sum(1 for result in results if result.evaluation["status"] == "failed")
    not_evaluated = sum(
        1 for result in results if result.evaluation["status"] == "not_evaluated"
    )
    infrastructure_errors = sum(1 for result in results if result.error is not None)

    print()
    print(f"RUN: {run_id}")
    print(f"MODEL: {model.provider_model}")
    print()
    print(f"Tests: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Not evaluated: {not_evaluated}")
    print(f"Infrastructure errors: {infrastructure_errors}")
    print()
    print(f"Duration: {duration_seconds:.2f}s")
    print(f"Results: {results_path}")


def _count_status(results: list, status: str) -> int:
    return sum(1 for result in results if result.evaluation["status"] == status)


def _result_path_for_model_run(
    configured_path: Path,
    model: ModelRegistryEntry,
    run_id: str,
) -> Path:
    directory = configured_path if configured_path.suffix == "" else configured_path.parent
    return directory / f"{_safe_result_name(model.provider_model)}_{run_id}.jsonl"


def _safe_result_name(provider_model: str) -> str:
    safe = []
    for char in provider_model.lower():
        if char.isalnum():
            safe.append(char)
        else:
            safe.append("_")
    return "_".join("".join(safe).strip("_").split("_"))


def _print_overall_summary(summary) -> None:
    print(f"MODEL: {summary.provider_model} ({summary.model_id})")
    print(f"RUN: {summary.run_id}")
    print(f"Tests: {summary.tests}")
    print(f"Passed: {summary.passed}")
    print(f"Failed: {summary.failed}")
    print(f"Not evaluated: {summary.not_evaluated}")
    print(f"Infrastructure errors: {summary.infrastructure_errors}")
    print(f"Pass rate: {_percent(summary.pass_rate)}")
    print(f"Task correct: {summary.task_correct}")
    print(f"Task incorrect: {summary.task_incorrect}")
    print(f"Task accuracy: {_percent(summary.task_accuracy)}")
    print(f"Format-only failures: {summary.format_only_failures}")
    print(f"Wrong-answer failures: {summary.wrong_answer_failures}")
    print(f"Total duration: {summary.total_duration_ms:.2f} ms")
    print(f"Average duration/test: {_number(summary.average_duration_ms)} ms")
    print(f"Total prompt tokens: {summary.total_prompt_tokens}")
    print(f"Total output tokens: {summary.total_output_tokens}")
    print(f"Average output tokens/test: {_number(summary.average_output_tokens)}")
    print(f"Average output tokens/sec: {_number(summary.average_output_tokens_per_second)}")
    print(
        "Estimated thinking tokens: "
        f"{_optional_int(summary.estimated_thinking_tokens)}"
    )
    print(
        "Estimated response tokens: "
        f"{_optional_int(summary.estimated_response_tokens)}"
    )
    print(f"Estimated thinking share: {_percent(summary.estimated_thinking_share)}")


def _print_group_table(summaries) -> None:
    print(
        f"{'GROUP':<24} {'PASS':>8} {'STRICT':>8} {'TASK':>8} {'FMT':>5} "
        f"{'WRONG':>6} {'AVG_MS':>10} {'AVG_OUT':>9} {'OUT_TPS':>9}"
    )
    for summary in summaries:
        print(
            f"{summary.key:<24} "
            f"{summary.passed}/{summary.tests:>5} "
            f"{_percent(summary.pass_rate):>8} "
            f"{_percent(summary.task_accuracy):>8} "
            f"{summary.format_only_failures:>5} "
            f"{summary.wrong_answer_failures:>6} "
            f"{_number(summary.average_duration_ms):>10} "
            f"{_number(summary.average_output_tokens):>9} "
            f"{_number(summary.average_output_tokens_per_second):>9}"
        )


def _compact_text(text: str | None, limit: int = 160) -> str:
    if text is None:
        return ""
    single_line = " ".join(text.split())
    if len(single_line) <= limit:
        return single_line
    return f"{single_line[: limit - 3]}..."


def _percent(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value * 100:.1f}%"


def _number(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.2f}"


def _optional_int(value: int | None) -> str:
    return str(value) if value is not None else "n/a"


def _print_result_summary(result, results_path: Path) -> None:
    print(f"TEST: {result.test_id}")
    print(f"MODEL: {result.provider_model}")
    print(f"VARIANT: {result.variant}")
    print(f"RESULT: {_display_status(result)}")
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


def _configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        if stream.isatty():
            continue
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="strict")


if __name__ == "__main__":
    raise SystemExit(main())
