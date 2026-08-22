# rgb-ai

Local-first AI experimentation and orchestration platform.

## Current status

The project is currently implementing:

**MVP Phase 1 — Minimal Benchmark Engine**

The immediate goal is to run reproducible benchmarks against models served
remotely by Ollama.

## Architecture

Development machine:
- repository
- Python
- Codex
- tests

AI server:
- Ollama
- local models
- inference

Ollama is accessed through a configurable `OLLAMA_BASE_URL`.

## Documentation

Before implementing changes, read:

1. `AGENTS.md`
2. `docs/MVP_PLAN.md`
3. `docs/ARCHITECTURE.md`

Then read the specialized document relevant to the task:

- benchmarks → `docs/BENCHMARK_PLAN.md`
- environments → `docs/ENVIRONMENTS.md`
- data → `docs/DATA_MODEL.md`
- RAG → `docs/RAG_DESIGN.md`

## Current implementation target

Implement only Phase 1:

- Ollama client
- model registry
- benchmark test loading
- benchmark execution
- metric capture
- result storage
- tests

Do not implement RAG, agents, frontend, users or Qdrant yet.

## Phase 1 benchmark usage

Set runtime configuration through environment variables:

```bash
OLLAMA_BASE_URL=http://192.168.x.x:11434
RGB_AI_RESULTS_PATH=results/benchmark_results.jsonl
```

List registered models:

```bash
python -m rgb_ai models list
```

Compare the registry with models reported by Ollama:

```bash
python -m rgb_ai models check-installed
```

List benchmark cases:

```bash
python -m rgb_ai benchmark list
```

Run one model against one case:

```bash
python -m rgb_ai benchmark run --model mdl_qwen3_06b --test CONTEXT_FACT_001
```

Run one model against a category:

```bash
python -m rgb_ai benchmark run --model mdl_qwen3_06b --category context_use
```

Results are appended as UTF-8 JSONL. Raw provider responses are stored, but the
CLI prints only a compact summary.
