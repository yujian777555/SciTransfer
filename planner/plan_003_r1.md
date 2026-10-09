# SciTransfer — Planner Round 003-R1: One-Time SciAgentGYM Offline Runtime Unblock

**Issued:** 2026-10-09
**Decision authorized by user:** Proceed with option A, **one bounded SciAgentGYM source/runtime verification**, before considering alternative research-method design.
**Planner:** ChatGPT
**Executor:** Kimi/MiMo
**SciTransfer repo/branch:** https://github.com/yujian777555/SciTransfer / `main`
**Reviewed base HEAD:** `abe6aa2a7d511859fd164a82287238177abdca2f`
**Prior review:** `planner/reviews/review_003.md`
**Upstream repo:** https://github.com/CMarsRover/SciAgentGYM
**UPSTREAM PIN (mandatory):** `e9dbbea4369d67694e38bf8be67bedbcaf9e9300`
**Known repo-level license:** Apache-2.0, `LICENSE`; inspect dataset/tool/dependency terms separately.
**Phase:** PHASE0-C, Round 003-R1; NOT Round004 / Phase1.
**Total wall-clock installation+verification timebox:** maximum **2 hours**. **Zero paid model/API calls; no LLM judge.** No new strategy/agent training.

## Research question (do not silently change)

SciTransfer asks whether a process-level scientific strategy extracted from source disciplines **causally** improves outcome-grounded scientific task performance in target disciplines, and whether an agent can abstain to avoid negative transfer. The current task is only to find a VALID measurement environment. Do NOT turn task-tool counts or answer-matching into evidence of learned transfer.

## Step 0 — repo/host preflight and full stop rules

1. `git fetch origin && git pull --ff-only origin main`. Confirm this plan, `status.json`, and clean worktree. Keep Round001–003 files unchanged.
2. Record host OS, Python/conda versions, disk and free space, network diagnostics, existing local SciAgentGYM checkout/caches, timestamp, target `UPSTREAM PIN`, and bounded attempt log. Never record tokens, proxies with credentials, or gold answers.
3. Work in an **external directory**, not inside tracked SciTransfer. Do not vendor the upstream source, datasets, private env, or results containing gold into the public SciTransfer Git tree.
4. **Hard stop**: no lawful source access; dependency installation requires major downloads/network not approved; >2h total; hidden gold cannot be withheld from candidate; scorer triggers paid judge; or invalid/unsafe tool calls. Stop with `BLOCKED` / `NO_GO` and reason. Do not keep trying retries overnight.

## Step 1 — acquire pinned source, fail fast on network

Attempt in order, **no more than two source-access routes**:
- Check a local existing verified checkout or cached source archive (sha and file tree must match pin).
- Otherwise ONE bounded HTTPS Git clone+checkout, and optionally ONE equivalent GitHub commit-specific archive/approved mirror if git transport is blocked. Suggested `git clone --filter=blob:none --no-checkout https://github.com/CMarsRover/SciAgentGYM.git <external_dir>` then `git checkout ${upstream}` as network permits; record `git rev-parse HEAD`. An archive without .git needs its URL/commit + checksum manifest and spot-checked file hashes.
- No indefinite proxy workarounds. If this also fails: `BLOCKED_SOURCE_ACCESS`, report exact command/error/elapsed; **STOP** (do not pretend access).
- A valid GitHub API static read is not an actual local checkout.

## Step 2 — verify installed runtime, do not build huge stacks blindly

Inspect `README.md`, `LICENSE`, `install.sh`, `environment.yml`, `requirements.txt`, `gym/env.py`, `gym/core/evaluator.py`, `gym/core/tool_loader.py`, `gym/test_querys.py`, dataset metadata and any third-party license.
- Pin source SHA and hashes of code actually used; Python 3.11 or project-documented runtime is preferred.
- Timebox dependency creation; determine whether a MINIMAL subset of text-only toolkit imports works BEFORE full conda install. Avoid uncontrolled 1,780-tool loading, APIs, full benchmark suites, proprietary datasets, or multi-GB downloads.
- If dependencies fail, report precise blocker and availability of a deterministic next step, **NO-GO for runtime at current conditions**; do not count a mocked scientific tool as upstream execution.

## Step 3 — two authentic sequential scientific actions

Select one publicly documented small DEV case and its real toolkit(s), no secret score keys exposed to the candidate. Demonstrate:
1. `env.reset()` with tool registry, a typed `ToolCall` and actual `env.step()` result (tool A), record arguments, outcome, source tool path and hash;
2. A distinct second tool invocation **whose input choice depends on the first public result** (not two pre-scripted calls), with the original environment's observation returned;
3. Failure/invalid-tool control; successful result semantics with no model calls; state-reset/replay with same dev inputs.
4. If one scientific task requires only one meaningful tool, search no more than 2 small documented DEV cases and stop; do not fabricate dependency or claim a research decision from string concatenation.

If the first science discipline is executable, attempt exactly one analogous small DEV task from a genuinely different discipline; distinguish domain subject label from independent scientific methodology. Each call must be a real upstream tool, not custom synthetic substitute.

## Step 4 — hidden answer + scorer integrity (non-negotiable)

- Separate candidate-facing `question + approved tool schemas + public observations` from trusted evaluator-only fields `answer`, `golden_answer`, `solution_steps`, `tool_expected`, `refined_versions[*].final_answer` and other solution metadata. Note: `usage_tool_protocol` is potentially permitted as tool schema but should be checked for answer leaks.
- Use dynamic canary fields nested within reference data to assert that neither tool request, candidate view, trace, context nor any Git-staged artifact contains hidden reference text. Only non-sensitive verifier outcomes go to public evidence.
- Upstream `gym/core/evaluator.py::calculate_answer_score()` calls `secondary_verification_with_llm` on certain mismatch paths; `is_answer_correct()` also invokes an LLM judge. **Do not assume it is a pure offline scorer.**
- For DEV cases, run perfect / wrong / missing / near-correct outputs through the actual pinned evaluator with a **zero-network judge-denial monitor** (e.g. monkeypatch judge+network client to throw on access in a test harness, with explicit disclosure). If a mismatch attempts a judge call, record `JUDGE_REQUIRED` or `OFFLINE_SCORER_NOT_EQUIVALENT` and do NOT report an authentic original official offline score for that path. A separately designed deterministic scorer is a **different evaluator** and would require Planner acceptance.
- Require both an executable scientific tool chain AND a validated, nonleaking outcome evaluation path before a GO decision. Stop when judge dependency prevents reproducible all-arm comparison.

## Step 5 — evidence artifacts and decision

Commit **safe metadata only** under SciTransfer:
- `results/round_003_r1_preflight.md`: source and runtime route, measured errors/cost/time, SHA checks and bounded attempts.
- `benchmarks/round_003_r1_sciagentgym_runtime.md`: 2 actual science tool calls, dependency on evidence from call 1, second discipline where available, official code paths or explicit blocker.
- `results/round_003_r1_scorer_integrity.md`: evaluator perfect/wrong/missing/near-correct judge-denial findings and field-allowlist canary audit, preserving original upstream source.
- `results/result_round_003_r1.json`: per-gate PASS/PARTIAL/BLOCKED, cost ($0), source pinned revision, test counts and exact validation limits.
- `status.json`, updated for this result; optionally small code/tests to reproduce allowed probes. **Do not upload gold/solution material.**

Run relevant SciTransfer tests and newly introduced offline tests, record actual passed/failed/skipped, commands and sanitized output. Do not claim prior 114 tests if not executed here. If local runtime unavailable, report BLOCKED and which existing tests could/couldn't be run.

### One-off acceptance gates (Planner decides)

- **R3R1-01:** Pinned source locally available and SHA verified, legal use inspected; else documented BLOCKED.
- **R3R1-02:** Real upstream tool A → observation → evidence-based tool B, valid result/log; no synthetic substitute.
- **R3R1-03:** Second genuinely different discipline runtime touched or honest scoped PARTIAL.
- **R3R1-04:** Candidate-vs-grader hidden gold isolation demonstrated by dynamic canary and safe export.
- **R3R1-05:** Actual original scoring behavior inspected under no-LLM-judge firewall; all scorer fallbacks disclosed.
- **R3R1-06:** Replay/reset/step inputs, runtime fingerprint, bounded provenance and actual tests/cost.
- **R3R1-07:** Honest GO / CONDITIONAL / NO-GO for measurement validity, not invented scientific strategy efficacy.
- **R3R1-08:** Result, traces (safe only), status pushed; **Planner alone** decides ACCEPTED.

## Outcome logic

**GO for later small paired pilot ONLY IF** actual tools across >=2 science disciplines and a trustworthy, safe, reproducible scorer are proven. If any critical condition remains unverified => `CONDITIONAL` or `NO_GO`; keep Phase1 blocked. If source/network fails => `BLOCKED`; **do not automatically start method redesign**. Instead request Planner+user decision to authorize a distinct controlled environment.

**No paid model calls, no Phase1 training, no open-ended R3R1-R2/R3 repair chain.**
