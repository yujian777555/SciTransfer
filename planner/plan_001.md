# SciTransfer — Planner Round 001: Real Benchmark Integration

**Issued:** 2026-10-08  
**Planner:** ChatGPT  
**Executor:** Kimi  
**Repository:** https://github.com/yujian777555/SciTransfer  
**Branch:** main  
**Phase:** 0 — feasibility/infrastructure  
**Status:** ISSUED / AWAITING_EXECUTOR  
**Base commit inspected:** `37dcc8623ccdc3291cac1c08c76a365b7cc55be0` (initial README-only commit)

## 0. Mission, non-goals, and decision boundary

Establish the *minimum real, reproducible* infrastructure needed to ask whether a scientific strategy changes an AI research agent's behavior and benchmark outcome in different domains. **This round is NOT meant to demonstrate positive transfer, train a new model, or claim a paper contribution.**

Do not introduce an elaborate multi-agent architecture. Use one pinned agent/model harness, bounded actions, and the benchmark's official evaluator. Keep scope tight; report blockers honestly. Planner alone decides round acceptance and future direction.

## 1. Mandatory first-step reconnaissance (submit artifacts)

1. Read repo `status.json`, this plan, README, charter, and status protocol. Record starting HEAD and working-tree changes; never overwrite unexpected work.
2. Verify exact upstream ScienceAgentBench source repository, commit/tag, **verified task split**, task schema, evaluator, dependencies, dataset/license and runnable instructions. Prefer verified evaluator over outdated evaluation. Do not claim availability without actual download/inspection.
3. Select **one public and executable task from each of three domains**, prioritizing bioinformatics, computational chemistry, and geographical information science. If official split lacks an accessible domain or task, log the blocker and propose an evidence-based substitute; **do not silently substitute**.
4. Record provenance in `benchmarks/manifest.json`: source URLs, upstream SHA/version, task identifiers, domain labels, licenses (if available), package/image digests, evaluator commands and dataset checksums when permitted. Exclude answer keys and unnecessary raw benchmark contents.
5. Write concise `results/round_001_environment_audit.md` with reproducible shell commands, exact versions, whether evaluator is runnable, limitations, and estimated API/GPU resource requirement.

## 2. Minimal interfaces

Implement a small Python package under `src/scitransfer/`:
- `core/types.py`: typed `ResearchState`, `ScientificAction`, `ScientificStrategy`, `StepRecord`, `RunResult`, `Budget` objects. Strategy must have `preconditions`, `action/recommendation`, `expected_evidence`, `invalidity_conditions`, `source_provenance`. Stable IDs are required.
- `benchmarks/scienceagentbench.py`: load task metadata and invoke **official** verified evaluation. Must fail closed on missing evaluator or output.
- `runner/paired.py`: paired A/B execution on identical task and initial environment; pinned model/tool/prompt except added strategy. Maintain separate run directories and deterministic dataset state. A=No Strategy; B=Fixed, preregistered Scientific Strategy. Optional C=matched-length neutral context / placebo if practical.
- `runner/trace.py`: append per-action records: task_id, domain, agent/model ID+version, environment SHA, prompt/strategy hash, seed, timestamps, action, tool calls, observations, artifact paths, status, budget/tokens/cost, evaluator raw output, exit reason. No secrets.
- `metrics.py`: parse official score and paired difference; report raw per-run results. Never compute claimed scientific significance from tiny pilot.

Implement stable CLI: `python -m scitransfer.cli audit`, `... run-pair --task-id ... --seed ... --strategy ...`, `... summarize --results-dir ...`. Document exact actual usage, even if implementation differs in flags. Do not pretend available commands run unless executed.

## 3. Real pilot

- **Minimum acceptance goal:** 3 authentic benchmark tasks, one per distinct domain, each with A and B runs under matched inputs and budgets, with genuine official evaluator outputs attached; any inability must be explicitly marked BLOCKED, not PASS.
- Keep first pilot resource-bounded: document projected cost and get user confirmation **before** incurring substantial paid API/GPU expense, and before any large task expansion. Do not default to expensive multi-seed sweeps. After smoke run, prefer 2 paired seeds per domain if affordable, but do not treat this as an acceptance requirement or as statistically powered evidence.
- Strategy B is fixed **before** any target-task outcome is observed. Strategy should express a generic tactic (e.g., validate a baseline before escalation), not a solution hint, domain-specific answer or access to hidden evaluation keys.
- Ensure both arms have equivalent tools, model, state, allowed time and budget. If B uses extra tokens, explicitly report added cost; avoid claiming budget equivalence when strategy intervention itself adds overhead.
- If execution depends on inaccessible resources, document reproducible evidence and halt as `BLOCKED`; never replace real evaluator outputs with synthetic scores.

## 4. Mandatory verification tests

- Initial-state parity; task/source split isolation; prompt/strategy hash and provenance; consistent budget handling; missing-evaluator fail-closed; no answer-key leakage; reproducible trace schema and run-folder isolation; explicit failure statuses; official evaluator output parsing.
- Include one test showing synthetic tasks are never counted as official benchmark success.
- Run a documented test command; report exact pass/fail/skip totals. Do not silently skip flaky/failed cases.

## 5. Required deliverables

- `src/` and `tests/` implementing audited interfaces, with a minimal `pyproject.toml` or pinned requirements.
- `benchmarks/manifest.json` with verified metadata; `experiments/round_001_config.*` with strategy A/B and model settings.
- `results/round_001_environment_audit.md`.
- `results/round_001_runs/` with per-run JSON, official scores/raw evaluator logs, sanitized trace and provenance. If huge, publish manifest + checksums + durable externally accessible artifact references; never fabricate artifacts.
- `results/result_round_001.json` that validates against `schemas/result_round.schema.json` and explicitly lists blockers, executed tests, missing tasks and hashes.
- `status.json` updated by Executor only to `AWAITING_PLANNER_REVIEW` (not ACCEPTED), with implementation commit SHA if already determinable; otherwise provide commit SHA in result/PR and explain any circularity.
- Short `README.md` update with real reproducible setup/run commands and limitations.

## 6. Hard acceptance conditions (Planner-controlled)

**AC-01**: Third-party benchmark provenance and verified official evaluation are explicitly documented.  
**AC-02**: Three different scientific domains, with >=1 truly executed official evaluation per domain, not mock.  
**AC-03**: Each selected task has A/B arms with matched configurations and stored raw evidence (at least one pair per domain).  
**AC-04**: Trace, scores, cost, failures, seeds, software versions and task IDs can be independently reviewed.  
**AC-05**: Core safeguards tested, test totals recorded; no silent skipping, fabricated runs, or hidden-answer contamination.  
**AC-06**: Work committed and pushed; `status.json` and result path coherent; user can hand the repo back to Planner for review.

If any AC is not satisfied, report `PARTIAL` or `BLOCKED`, including concrete next action. Infrastructure-only unit test success ≠ Round 001 accepted.

## 7. Communication and handoff protocol

- Executor may implement/restructure within this plan, but **must not alter central research question, metrics, domain selection principles, or gate criteria** without Planner review.
- If blocked by costs, inaccessible benchmark, unsupported OS, or license: stop; log error, command, environment, and alternatives. Do not invent a substitute benchmark.
- Push progress to `main` (or create a PR if branch protection requires); never force-push. Retain raw evidence.
- On completion, respond with: HEAD SHA; paths/URLs for result JSON and audit; task IDs/domains; number of genuine A/B pairs; official evaluator outcomes; actual tests; unmet ACs; estimated next cost.
- Planner will then issue a review and Round 002 or remediation plan based *only* on actual repo contents.
