# AGENTS.md

# 1. Purpose

This file defines how coding agents must work inside the `rgb-ai` repository.

Before making meaningful changes, agents must understand the project architecture,
current development phase, and constraints.

The goal is not to build the entire platform immediately.

The goal is to build `rgb-ai` incrementally, measurably, and safely.


# 2. Project Overview

`rgb-ai` is a local-first AI experimentation and orchestration platform.

Its long-term purpose is to manage and evaluate:

- local LLMs;
- specialized models;
- embeddings;
- RAG;
- agents;
- tool use;
- routing;
- environments;
- benchmarks;
- user profiles;
- document workflows.

The project is intentionally modular.

Models and components must be replaceable and benchmarkable.


# 3. Read Documentation First

Before implementing a new feature, read the relevant documentation inside:

```text
docs/
```

Important documents include:

```text
docs/ARCHITECTURE.md
docs/MVP_PLAN.md
docs/BENCHMARK_PLAN.md
docs/ENVIRONMENTS.md
docs/DATA_MODEL.md
docs/RAG_DESIGN.md
docs/IDEAS.md
```

Do not assume the architecture from filenames or existing code alone.

The documentation represents the intended system design.


# 4. Source of Truth

When deciding what to implement, use this priority:

```text
explicit current user request
        ↓
MVP_PLAN.md
        ↓
ARCHITECTURE.md
        ↓
specialized design documents
        ↓
existing implementation
        ↓
IDEAS.md
```

`IDEAS.md` contains future possibilities.

An idea is NOT automatically a requirement.


# 5. Current Development Philosophy

The project follows this progression:

```text
manual experiments
        ↓
reproducible benchmarks
        ↓
controlled environments
        ↓
sandboxed real tasks
        ↓
RAG
        ↓
specialized agents
        ↓
real-world workflows
        ↓
adaptive platform
```

Do not skip stages without explicit instruction.


# 6. MVP Discipline

Always identify the current phase in:

```text
docs/MVP_PLAN.md
```

Implement ONLY:

- the current requested phase;
- dependencies strictly necessary for that phase;
- minimal interfaces required for future compatibility.

Do NOT implement future phases preemptively.


# 7. Current Initial Target

Unless explicitly instructed otherwise, the initial implementation target is:

```text
MVP_PLAN.md
Phase 1 — Minimal Benchmark Engine
```

The first system should approximately support:

```text
registered model
        ↓
test case
        ↓
Ollama request
        ↓
model response
        ↓
metrics
        ↓
stored benchmark result
```


# 8. Do Not Build Yet

During the initial Benchmark Engine phase, do NOT implement:

- RAG;
- Qdrant;
- frontend;
- authentication;
- user profiles;
- persistent user memory;
- production agents;
- real document movement;
- OCR;
- complex databases;
- fine-tuning;
- reinforcement learning;
- autonomous workflows;
- complex distributed infrastructure.

These features are documented for future phases.


# 9. Remote Inference Architecture

LLMs run on a dedicated AI server.

Development may happen on another machine.

Conceptually:

```text
Development Machine
├── repository
├── Python
├── Codex
└── tests
        |
        | HTTP / private network
        v
AI Server
├── Ollama
└── local models
```

Do not assume Ollama runs on the development machine.


# 10. Ollama Configuration

Never hardcode:

```text
http://localhost:11434
```

or a private IP such as:

```text
http://192.168.x.x:11434
```

Use configuration.

Preferred environment variable:

```text
OLLAMA_BASE_URL
```

Example:

```text
OLLAMA_BASE_URL=http://192.168.x.x:11434
```

A sensible local default may exist if appropriate, but remote configuration must
always be supported.


# 11. Ollama Client

Communication with Ollama must be centralized.

Preferred architecture:

```text
application
    ↓
OllamaClient
    ↓
HTTP
    ↓
Ollama
```

Do not scatter direct Ollama HTTP requests throughout the codebase.

The client should eventually support:

- model selection;
- prompt submission;
- options;
- response parsing;
- metrics parsing;
- errors;
- timeout handling.


# 12. Provider Independence

Avoid coupling core benchmark logic tightly to Ollama-specific implementation.

The first provider is Ollama.

Future providers may include:

- another local runtime;
- remote inference server;
- external API;
- GPU machine.

Do not implement those providers now.

Simply avoid architecture that makes them unnecessarily difficult later.


# 13. Model Independence

Never assume one model permanently owns a task.

Bad:

```python
if task == "reasoning":
    model = "deepseek-r1:1.5b"
```

Preferred concept:

```text
task
↓
configuration / registry
↓
selected model
```

Models must remain replaceable and benchmarkable.


# 14. Model Registry

Models should be represented through structured configuration.

The registry may initially use:

- YAML;
- JSON;

or another simple format.

Avoid creating database infrastructure unless required.


# 15. Model Metadata

Where relevant, model metadata may include:

- model_id;
- runtime name;
- family;
- parameter count;
- specialization;
- disk size;
- context size;
- notes.

Runtime benchmark results should not be confused with static model metadata.


# 16. Known Initial Model Laboratory

The current local laboratory includes models such as:

```text
qwen3:0.6b
qwen3:1.7b
llama3.2:1b
gemma3:1b
qwen2.5:1.5b
qwen2.5-coder:1.5b
deepseek-r1:1.5b
phi3.5:3.8b
granite4:350m-h
embeddinggemma
```

These are experimental candidates.

Do not assume any is permanently assigned to production.


# 17. Model Roles Are Hypotheses

Current possible roles include:

```text
small generalist → routing / simple tasks
coder            → programming
reasoning        → reasoning tasks
agentic          → tool selection / agent tasks
embedding        → semantic retrieval
larger model     → escalation
```

These are hypotheses.

Benchmarks determine actual assignments.


# 18. Specialized Does Not Automatically Mean Better

Do not assume:

```text
specialized model > general model
```

for every task.

The project explicitly exists to test these assumptions.

A generalist model may outperform a specialized model in a specific environment.


# 19. Benchmark-First Development

Every important model decision should eventually be supported by benchmark data.

Prefer:

```text
measure
↓
compare
↓
decide
```

over:

```text
assume
↓
hardcode
```


# 20. Benchmark Reproducibility

A benchmark result should contain enough information to understand how it was
produced.

Where possible record:

- test case;
- model;
- model configuration;
- prompt;
- response;
- timing;
- token counts;
- throughput;
- evaluator/verifier result;
- timestamp.


# 21. Raw Data Preservation

Preserve raw model output whenever practical.

Do not store only a final score.

Future analysis may need to inspect:

- formatting failures;
- hallucinations;
- reasoning patterns;
- repeated output;
- malformed JSON;
- tool-selection mistakes.


# 22. Structured Output

When a benchmark expects structured output:

- validate it;
- do not silently repair it before evaluation;
- preserve the original response.

Example:

If a model is instructed to return JSON and returns prose, the benchmark should
record a format failure.

A parser may attempt recovery for diagnostics, but recovered output must not be
confused with strict compliance.


# 23. Separate Capabilities

Avoid combining unrelated capabilities into one score.

For agentic tasks, distinguish:

- semantic decision correctness;
- tool selection;
- argument correctness;
- schema compliance;
- instruction following;
- unnecessary actions;
- completion behavior.

Example:

A model may select the correct tool but fail to output valid JSON.

That is not equivalent to choosing the wrong tool.


# 24. Evaluation Strategy

Prefer deterministic verification when possible.

Examples:

```text
classification
→ expected label

JSON
→ schema validation

math
→ known answer

code
→ automated tests

routing
→ expected destination

tool use
→ expected tool + arguments
```

Use LLM-as-judge only when deterministic evaluation is insufficient.


# 25. Environments

Tasks should eventually become reproducible environments.

An environment defines:

- task;
- input;
- allowed actions;
- expected output;
- verifier;
- metrics;
- termination conditions.

Read:

```text
docs/ENVIRONMENTS.md
```

before implementing environment infrastructure.


# 26. Real-World Tasks Become Tests

When the system fails on a real task:

```text
real task
↓
failure
↓
human correction
↓
benchmark candidate
↓
review
↓
dataset
```

The goal is for the benchmark suite to become increasingly representative of
actual usage.


# 27. RAG

Do not implement RAG until its phase is reached.

Before working on RAG, read:

```text
docs/RAG_DESIGN.md
```

The RAG architecture separates:

```text
ingestion
↓
chunking
↓
embeddings
↓
retrieval
↓
reranking
↓
context building
↓
generation
```


# 28. Retrieval vs Generation

Never treat RAG as a single opaque score.

Measure separately:

```text
Did retrieval find the correct evidence?
```

and:

```text
Did the LLM correctly use the evidence?
```

This distinction is fundamental to the project.


# 29. Embeddings

The initial embedding candidate is:

```text
embeddinggemma
```

Observed initial behavior:

```text
dimensions: 768
```

This is not a permanent architectural dependency.

Embedding models must remain replaceable and benchmarkable.


# 30. Vector Store

Qdrant is the current future candidate.

Do NOT install or integrate Qdrant during the initial Benchmark Engine phase.


# 31. Reranking

A reranker may be introduced later.

Current candidate:

```text
BAAI/bge-reranker-v2-m3
```

Do not implement it until retrieval benchmarks show that reranking is useful.


# 32. Agents

An agent should eventually be understood as a composition of:

```text
model
+
system prompt
+
tools
+
permissions
+
optional RAG
+
environment
```

Do not equate:

```text
one agent = one installed model
```

Multiple agents may share the same model.


# 33. Tool Calling

Tool-use benchmarks should distinguish between:

- choosing the correct tool;
- generating correct arguments;
- following output schema;
- sequencing calls;
- stopping correctly.

Do not consider a tool-use task successful solely because the correct tool name
appears somewhere in the response.


# 34. Escalation

The long-term architecture may use model escalation.

Conceptually:

```text
small model
↓
can solve confidently?
├── yes → finish
└── no
     ↓
larger/specialized model
```

Do not implement confidence-based escalation until it can be evaluated properly.


# 35. Hardware Awareness

The current AI server is resource constrained.

Favor efficient designs.

Important metrics include:

- RAM;
- CPU;
- latency;
- tokens per second;
- model load time;
- disk usage.

Do not optimize exclusively for model quality.


# 36. Efficiency Matters

The best model is not necessarily the highest-scoring model.

Selection may depend on:

```text
quality
+
latency
+
RAM
+
throughput
+
reliability
```

A smaller model meeting the required quality threshold may be preferable.


# 37. Avoid Premature Optimization

Do not add:

- caching layers;
- queues;
- distributed workers;
- microservices;
- elaborate concurrency;

until measurements show they are needed.


# 38. Simplicity First

Prefer:

```text
simple Python module
```

over:

```text
large framework
```

when both solve the current problem.

The codebase should remain understandable by one developer.


# 39. Dependencies

Minimize dependencies.

Before adding a dependency, consider:

1. Is it necessary?
2. Is the standard library sufficient?
3. Is it actively maintained?
4. Does it substantially simplify the implementation?

Do not add libraries merely for convenience if they introduce unnecessary
complexity.


# 40. Python

Python is the primary backend and experimentation language unless a future
requirement justifies otherwise.

Prefer modern, readable Python.

Use:

- type hints where useful;
- small functions;
- clear names;
- explicit data structures.


# 41. Project Structure

Do not create a huge directory hierarchy before it is needed.

A reasonable early structure may resemble:

```text
rgb-ai/
├── AGENTS.md
├── docs/
├── src/
│   └── rgb_ai/
├── tests/
├── configs/
└── pyproject.toml
```

This is guidance, not a requirement to create every directory immediately.


# 42. Configuration

Runtime-specific values should live in:

- environment variables;
- configuration files;

not source code.

Examples:

```text
OLLAMA_BASE_URL
RESULTS_PATH
REQUEST_TIMEOUT
```

Do not commit secrets.


# 43. Environment Files

If `.env` is used:

```text
.env
```

must be ignored by Git.

Provide:

```text
.env.example
```

with safe example values when useful.


# 44. Security

Never:

- expose secrets in source code;
- execute arbitrary model-generated shell commands;
- allow unrestricted filesystem paths;
- trust model output as authorization;
- expose Ollama directly to the public Internet.

Security boundaries must be enforced in code.


# 45. Filesystem Safety

When real file tools are eventually implemented:

- restrict operations to configured roots;
- resolve paths safely;
- prevent path traversal;
- avoid overwrite by default;
- avoid deletion by default.

Models must not receive unrestricted filesystem authority.


# 46. Network Safety

Ollama may be reachable over:

- LAN;
- private VPN;
- controlled backend network.

Do not assume the Ollama API itself provides the application's final authentication
or authorization layer.


# 47. Testing

Every implemented phase should include tests.

Tests should cover:

- happy path;
- malformed input;
- unavailable model;
- timeout;
- invalid response;
- storage failure where relevant.


# 48. Tests Before Completion

Before considering a task complete:

1. run relevant tests;
2. inspect failures;
3. fix regressions;
4. report any remaining limitation.

Do not claim success if tests are failing unless the failure is explicitly
documented and outside the requested scope.


# 49. Do Not Modify Tests to Hide Failures

Never weaken a test simply to make the suite pass.

If requirements changed legitimately, explain why the test must change.


# 50. Integration Tests

Where practical, distinguish:

```text
unit tests
```

from:

```text
integration tests requiring Ollama
```

The test suite should not unnecessarily require the AI server for every test.


# 51. Mocking

Mock Ollama for unit tests when testing application logic.

Use the real Ollama server for explicit integration tests and benchmarks.


# 52. Failure Handling

Failures should be explicit.

Examples:

- connection refused;
- unknown model;
- timeout;
- malformed Ollama response;
- empty response.

Do not silently convert infrastructure errors into model failures.


# 53. Logging

Use structured, useful logs.

Avoid excessive logging.

Never log secrets.

Benchmark outputs belong in benchmark result storage, not only console logs.


# 54. Data Storage

Use the simplest storage appropriate to the current phase.

Possible initial options:

```text
JSONL
SQLite
```

Do not introduce PostgreSQL merely because it may be useful eventually.


# 55. Schema Evolution

Data structures will evolve.

Prefer versionable schemas and migrations when persistence becomes important.

During early experimentation, keep the system easy to change.


# 56. IDs

Use stable identifiers for entities such as:

- models;
- test cases;
- benchmark runs;
- environments;
- documents;
- chunks.

Do not use display names as the only identifier.


# 57. Timestamps

Use consistent machine-readable timestamps.

Prefer UTC internally when persistence is implemented.


# 58. Documentation Updates

If implementation changes an architectural assumption:

- update the relevant documentation;
- explain the reason.

Do not allow code and documentation to silently diverge.


# 59. Architectural Changes

Do not make major architectural changes merely because another design appears more
elegant.

If documentation and implementation conflict:

1. identify the conflict;
2. determine whether it blocks the current task;
3. prefer the documented architecture unless explicitly instructed otherwise;
4. propose a change before performing a major redesign.


# 60. Decision Records

For significant decisions that are not already covered by documentation, record:

- problem;
- options;
- chosen approach;
- reason;
- trade-offs.

Do not create bureaucracy for trivial decisions.


# 61. Git Discipline

Keep changes focused.

Avoid mixing unrelated refactors with feature implementation.

Prefer commits that correspond to coherent functionality.


# 62. Generated Data

Do not commit large generated benchmark outputs unless explicitly intended.

Generated results should normally live in ignored runtime directories.

Small fixtures and curated benchmark datasets should be version controlled.


# 63. Benchmark Datasets

Curated test cases are project assets.

They should be:

- deterministic where possible;
- versioned;
- reviewable;
- independent from generated runtime results.


# 64. Avoid Benchmark Contamination

Do not train or optimize directly against the final test set.

As the project matures, maintain separation between:

```text
development cases
validation cases
test cases
```


# 65. User Corrections

User corrections are valuable data.

Do not automatically turn every correction into training data.

Store or propose it as a benchmark candidate first.

Human review should determine whether it enters a dataset.


# 66. Fine-Tuning

Fine-tuning is a future optimization.

Do not recommend or implement it merely because a model fails a few prompts.

First investigate:

- prompt;
- task definition;
- retrieval;
- model selection;
- verifier;
- escalation.


# 67. Reinforcement Learning

RL is a future experimental phase.

Do not implement until the project has:

- stable environments;
- reliable verifiers;
- meaningful rewards;
- sufficient datasets.


# 68. Frontend

Do not build the dashboard before useful backend data exists.

The frontend should visualize a functioning system, not define the architecture.


# 69. Personal Profiles

Future profiles may include:

```text
owner
member
guest
```

Do not implement profile logic during the initial benchmark phase.


# 70. Guest Mode

Future guest access must be:

- isolated;
- temporary where appropriate;
- permission restricted;
- unable to access private RAG collections or tools.

Do not implement until its phase is reached.


# 71. Code Quality

Favor code that is:

- explicit;
- readable;
- testable;
- replaceable;
- boring when possible.

Avoid clever abstractions without demonstrated benefit.


# 72. Comments

Comments should explain:

- why;
- constraints;
- non-obvious decisions.

Do not comment obvious syntax.


# 73. Error Messages

Errors should help diagnose the problem.

Good:

```text
Unable to connect to Ollama at configured OLLAMA_BASE_URL
```

Less useful:

```text
Request failed
```


# 74. CLI

The initial project may use a CLI.

Keep commands predictable.

Example conceptual interface:

```bash
python -m rgb_ai benchmark run \
  --model qwen3:0.6b \
  --test factual_001
```

Exact syntax may evolve.


# 75. No Hidden Magic

Avoid systems where behavior depends on undocumented implicit state.

Configuration and model assignments should be inspectable.


# 76. Reproducibility Over Convenience

A benchmark that can be reproduced tomorrow is more valuable than a one-off manual
result that cannot be reconstructed.


# 77. Performance Measurement

Do not infer performance from subjective impressions.

Record measurements.

Examples:

```text
total_duration
prompt_tokens
output_tokens
prompt_tokens_per_second
output_tokens_per_second
RAM
CPU
```


# 78. Model Load State

When relevant, distinguish:

```text
cold start
```

from:

```text
warm inference
```

Model loading time can materially affect user experience.


# 79. Hardware Results

Benchmark results are hardware-specific.

Do not assume a latency measured on the current server applies to future hardware.

Where relevant, store hardware/environment identity with results.


# 80. Confidence

Do not treat model self-reported confidence as calibrated probability.

If confidence-based routing is implemented later, it must be evaluated empirically.


# 81. Human-in-the-Loop

For uncertain or destructive operations, prefer escalation or human confirmation.

The system should be able to say:

```text
pending_classification
```

rather than force an unreliable decision.


# 82. Destructive Actions

Models must never directly decide to perform destructive operations without
backend-enforced safeguards.

Examples:

- delete file;
- overwrite file;
- expose private information;
- execute shell command.


# 83. Development Workflow

For each requested implementation:

```text
1. Read relevant docs
2. Inspect existing code
3. Identify current MVP phase
4. Define minimal change
5. Implement
6. Add/update tests
7. Run tests
8. Report what changed
9. Report limitations
```

Do not begin with a large refactor unless necessary.


# 84. Before Writing Code

Before implementing a substantial feature, briefly determine:

- which phase it belongs to;
- which documents govern it;
- what the minimum implementation is;
- what should explicitly remain unimplemented.

This protects the project from scope creep.


# 85. After Writing Code

After implementation, report:

- files changed;
- behavior implemented;
- tests run;
- results;
- known limitations;
- recommended next step.

Do not claim future functionality exists.


# 86. When Requirements Are Ambiguous

Prefer the smallest interpretation consistent with:

- the user's request;
- `MVP_PLAN.md`;
- architecture.

Ask for clarification only when the ambiguity materially affects implementation.


# 87. Do Not Overengineer

If Phase 1 requires:

```text
OllamaClient
+
registry
+
test loader
+
result storage
```

do not create:

```text
12 microservices
+
message broker
+
Kubernetes
+
distributed event bus
```

The system is currently an experimental local-first platform.


# 88. Current Hardware Constraint

The current AI server is CPU-based and relatively limited.

Observed model behavior shows that larger models can become substantially slower.

Therefore architecture should favor:

- specialized small models;
- efficient routing;
- retrieval;
- escalation;
- measurable trade-offs.


# 89. Current Strategic Hypothesis

A central project hypothesis is:

```text
multiple small specialized components
+
good retrieval
+
routing
+
escalation
```

may provide better local performance than:

```text
one large model doing everything
```

This is a hypothesis to test, not a truth to hardcode.


# 90. Final Principle

`rgb-ai` is an experimentation system before it is an automation system.

Every major component should answer:

```text
What problem does this solve?
How do we measure whether it works?
What is the smallest implementation?
Can we replace it later?
```

When uncertain, choose the solution that makes the next experiment easier to
measure and understand.
