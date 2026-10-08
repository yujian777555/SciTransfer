# SciTransfer

**Research question:** Do scientific research strategies improve research decisions when transferred across scientific domains? Under which conditions is transfer harmful?

**Goal:** A reproducible, outcome-grounded study of process-level scientific strategy transfer, including strategy abstraction, paired intervention experiments, negative transfer, and selective abstention. Novelty is a hypothesis to test, not a claim of being first.

## Collaboration

- **Planner:** ChatGPT. Owns research direction, formal plans, acceptance reviews, and decisions.
- **Executor:** Kimi (or an equivalent coding agent). Owns implementation, tests, benchmark execution, logs, and result commits.
- **Source of truth:** GitHub `main` branch content and recorded raw artifacts, **not** chat assertions.
- **Current work:** [Round 001](planner/latest_plan.md) — real benchmark integration and paired-run feasibility.

Read [Project Charter](planner/PROJECT_CHARTER.md), [Latest Plan](planner/latest_plan.md), [Executor Instructions](planner/EXECUTOR_HANDOFF.md), and [Status Protocol](planner/STATUS_PROTOCOL.md).

### Rules

1. Executor reads `status.json` and `planner/latest_plan.md` before starting; do not infer progress from chat.
2. Executor commits code/tests/actual evidence, writes `results/result_round_001.json`, then marks status `AWAITING_PLANNER_REVIEW`.
3. Planner reviews raw evidence and commit SHA and writes the next plan or a correction; executor cannot self-approve.
4. Simulated/mock runs are infrastructure tests, **not scientific evidence**; official verified evaluators remain authoritative.
5. No claims of cross-domain generalization, causality, significance, or paper-readiness without corresponding completed experiments.
6. Keep credentials, tokens, raw proprietary datasets, and benchmark answers out of Git.

## Intended directories

`src/`, `tests/`, `benchmarks/`, `experiments/`, `results/`, `paper/`; executor creates folders as needed.
