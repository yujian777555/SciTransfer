# SciTransfer

**Research question:** Do scientific research strategies improve research decisions when transferred across scientific domains? Under which conditions is transfer harmful?

**Goal:** A reproducible, outcome-grounded study of process-level scientific strategy transfer, including strategy abstraction, paired intervention experiments, negative transfer, and selective abstention. Novelty is a hypothesis to test, not a claim of being first.

## Collaboration

- **Planner:** ChatGPT. Owns research direction, formal plans, acceptance reviews, and decisions.
- **Executor:** MiMo (or an equivalent coding agent). Owns implementation, tests, benchmark execution, logs, and result commits.
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

## Setup (Round 001)

```bash
# 1. Clone this repository
git clone https://github.com/yujian777555/SciTransfer.git
cd SciTransfer

# 2. Install (Python 3.10+)
pip install -e ".[dev]"

# 3. Download the ScienceAgentBench verified split metadata (129 KB)
#    (already at benchmarks/data/verified-00000-of-00001.parquet in this repo)

# 4. Clone the upstream evaluator code
git clone https://github.com/OSU-NLP-Group/ScienceAgentBench.git ../ScienceAgentBench-upstream

# 5. Download benchmark artifacts (1.77 GB, required for official evaluation)
python scripts/download_sab_artifacts.py ../sab-artifacts
# Unzip with password: scienceagentbench
# Place contents under: benchmarks/ScienceAgentBench/benchmark/

# 6. Set your LLM API key (DeepSeek is the pinned model for this round)
export DEEPSEEK_API_KEY=sk-...
```

## Run experiments

```bash
# Audit the benchmark and evaluator readiness
PYTHONPATH=src python -m scitransfer.cli audit

# Run one A/B pair (arm A = no strategy, arm B = fixed preregistered strategy)
PYTHONPATH=src python -m scitransfer.cli run-pair --task-id 85 --seed 0 \
  --results-dir results/round_001_runs --model deepseek-v4-pro

# Summarize all runs
PYTHONPATH=src python -m scitransfer.cli summarize --results-dir results/round_001_runs

# Run safeguard tests
python -m pytest tests/test_round_001_safeguards.py -v
```

## Round 001 status

| Item | Status |
|------|--------|
| Verified split (102 tasks) | Downloaded, SHA256 recorded |
| Upstream evaluator code | Cloned at commit `c26e151` |
| 3 domains × A/B pairs (6 runs) | Generated with DeepSeek, full traces |
| Official evaluation | **BLOCKED** — `benchmark_verified.zip` download incomplete |
| Safeguard tests | 24/24 pass |
| Total agent cost | $0.047 USD |

### Limitations

- Official evaluation requires the password-protected `benchmark_verified.zip` from the official SharePoint link (see upstream README). Until extracted, all run scores are `null` and status is `BLOCKED` — no synthetic scores are produced.
- One paired seed per domain (seed 0). Not statistically powered.
- `OPENAI_API_KEY` in this environment is not a valid OpenAI key; GPT-4o visual judge is unavailable. Selected tasks use non-visual outputs (JSON/text/CSV) to avoid this dependency.
- Agent model is `deepseek-v4-pro` (OpenAI-compatible API), not one of the original SAB engines (OpenAI/Bedrock). Model identity is recorded in every trace.

## Intended directories

`src/`, `tests/`, `benchmarks/`, `experiments/`, `results/`, `paper/`; executor creates folders as needed.
