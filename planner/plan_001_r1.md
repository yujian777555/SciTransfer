# SciTransfer Planner — Round 001-R1: Evaluator Integrity & Real Score Recovery

**Issued:** 2026-10-08  
**Planner:** ChatGPT  
**Executor:** Kimi / MiMo (actual runtime must be recorded)  
**Branch:** main  
**Phase:** Phase 0 / Round 001 remediation, **not Round 002**  
**Base HEAD reviewed:** `9417ae767cda079db7c170c5f3054325d7608cb4`  
**Review:** `planner/reviews/review_001.md`  
**Status:** ISSUED / REPLAN_REQUIRED  
**Scientific scope:** repair infra, produce 3 valid official A/B score pairs; **no trained model, no novelty claim**.

## A. First: read repo & freeze evidence

Read `status.json`, this plan, review, source and original results. Before changes: `git pull --ff-only`, record HEAD, `git status`. Retain original `results/result_round_001.json` and `results/round_001_runs/` exactly unchanged. Write new results to `results/round_001_r1_runs/`; do **not** overwrite original logs or backdate the original preregistration config. Do not modify charter or research direction without Planner approval.

Before new paid API calls, run static/offline tests and calculate remaining benchmark/credential/infrastructure blockers. Do not trigger more code generation just to test evaluator invocation; **first evaluate previously generated code**.

## B. P0 — fix official harness and score parser

1. Pin upstream ScienceAgentBench to commit `c26e151ed601ba109dc4d35e057ff8e73fec469d`; pin HF verified dataset commit `9c6e96c9e74572e979b0930ee735041cef528cb7`. Explicitly pass `--split verified` and document split revision + dataset row-index order. Check whether upstream's API honors an HF revision argument, or use a pinned local verified source; ensure evaluation and task selector are **identical immutable dataset versions**.
2. On invocation resolve all benchmark, upstream, program folder, output log paths to **absolute paths** before switching `cwd`. Make configurable via CLI and environment; no assumptions that local upstream clone is inside `benchmarks/`. Verify actual program filename and mounted folder are what official test spec expects.
3. Fix JSONL parsing: upstream writes **one JSONL line per dataset row**, with placeholder records for unevaluated rows. Map `instance_id` to the exact zero-based row index of the same verified split, select ONLY that row; validate row count, target actually selected/executed, source of raw log, and lack of ambiguity. Explicitly reject a placeholder score (including placeholder zero) as genuine evaluation. Do not assume `success_rate=0` is placeholder: use test-execution evidence to distinguish valid failed score from dummy filler.
4. `official_evaluation=true` requires: correct pinned split, valid task selection, evaluator actually launched/completed, expected target execution evidence, correct JSONL row, and populated official score. Return ERROR/BLOCKED with **null** score if any invariant fails. Log both process stdout/stderr and raw official JSONL, checksums, run_id, task index, Docker/container metadata.
5. Unit-test against **fixtures following upstream output format**: 102 rows with filler and target at a nonzero index, target failure score 0, missing/malformed/short log, nonzero exit, command with `--split verified`, absolute path resolution, and stale log reuse. An integration smoke command must exercise *actual official CLI* with at least one task when resources ready.
6. Inspect upstream `resource` dependency / OS assumptions. Run official evaluator under WSL2 Linux or Linux container with functioning Docker and exact versions. Native Windows executor is unsupported unless a documented, clearly labeled compatibility adaptation is validated. Do not patch upstream evaluation logic without explicit disclosure and comparison.

## C. P0 — dataset artifacts and credentials

1. **Do not use current `scripts/start_download.ps1` as written:** it executes `Remove-Item` on the incomplete ZIP. Replace with non-destructive, retryable, resume-safe script and automated tests.
2. Use only a **tool-allowed workspace** (e.g. `C:\\Users\\于舰\\Documents\\SciTransfer` / Desktop in the user's environment) for executor file operations, or request access approval. `Access denied - path outside allowed directories` is a sandbox permission violation, not a missing OS permission; do not bypass security.
3. Check current ZIP file size/location and log before any restart; do not infer a running background download from `Start-Process` or `ChildProcess.kill`. Explicitly verify process existence and file growth. Prefer supervised foreground run or a valid supported background job that survives tool timeouts.
4. Resume via HTTP Range ONLY when status 206 and `Content-Range` start exactly matches local size; on status 200, explicitly restart safely using temporary file, not silently append corrupt bytes. Validate `Content-Length`, full expected byte count, ZIP central directory and extraction integrity (password available in upstream README). Report SHA256 **after full download**. Store large/protected upstream artifacts outside Git; respect upstream **DO NOT redistribute unzipped files online**.
5. If download remains unreasonably slow or inaccessible, verify official alternative source/link or ask user for manual official ZIP placement; never substitute public guesses or fabricate data.
6. Evaluate actual upstream credential initialization: pinned `run_evaluation.py` enforces an OpenAI/Azure credential preflight even for nonvisual tasks. A valid credential may be a prerequisite for **unmodified** harness; ask the user to configure one locally if so, without exposing keys in chat or Git. Do not use DashScope key as OpenAI key or pass fake placeholder credentials. If safely adapting a nonvisual-only evaluator, publish a labeled *modified evaluation* fork/diff and its validation; never label it unmodified official.
7. Record whether Docker/Linux environments have required network/build dependencies and exact error messages rather than continuing expensive retries.

## D. Strategy integrity / data provenance

1. Address the conflicting `preregistered_at=2026-10-08T22:00:00Z` vs observed run timestamps ~14:44Z. Do not change history or claim that the original preregistration was proven. Explain timezone if evidence exists; otherwise mark `UNVERIFIED`.
2. Prospective repeat runs require a registration committed **before model invocation**, with UTC timestamp, plan commit SHA, strategy text+hash, fixed arm prompts, target task IDs, model config, planned seeds, stopping criteria and budget.
3. Explicitly relabel current A/B as `single-shot strategy prompt ablation`, **not** learned or executed research policy. Any `baseline-first iterative execution` claim requires actual code execution/feedback steps in future round and equal accessible tools across arms. Round R1 may score stored programs without new LLM generation; if doing so, flag it as retrospective scoring of Round 001 generations, not new pre-registered trial.
4. Report DeepSeek sampler randomness even with temperature 0: `seed=0` is a pairing label, not a guaranteed provider RNG seed. Do not claim same stochastic noise without provider support.
5. Ensure unmodified 001 inputs remain available and every R1 score references exact artifact hash and earlier run ID.

## E. Required minimal execution order and artifacts

**E0 Offline correctness before large download / API call:** correct code, pass unit tests, inspect all hard dependencies; write `results/round_001_r1_preflight.md` summarizing upstream behavior, expected evaluator command and credential strategy.

**E1 Artifacts:** complete verified ZIP, verify file length (1,769,478,786 bytes), SHA, ZIP integrity, extract into authorized workspace, respect no-redistribution. Save `benchmarks/manifest_r1.json` recording exact local tree, versions and checksums without uploading restricted inputs.

**E2 Evaluator smoke:** select instance 85 (or first available selected task). Evaluate **existing generated code only**, ensuring official program execution, correct split, row mapping and score provenance; commit raw evaluator stdout/stderr/logs and sanitized trace. If blocked, record root cause and stop to avoid unnecessary new model calls.

**E3 Complete 3 genuine official paired scores:** same three tasks 85/16/21, both stored A/B generated programs per task, total 6 actual evaluations. Store distinct per-arm run_id, unambiguous score and logs in `results/round_001_r1_runs/`. Do not silently rerun generation, use hidden answers, or skip failure cases.

**E4 Consolidate:** `results/result_round_001_r1.json`, `results/round_001_r1_environment_audit.md`, `results/round_001_r1_evaluation_matrix.csv`, test outputs and updated `status.json`. Include script to reproduce score association, source program hashes, true 0/1 outcomes, and comparison limitations. Create a schema for R1 result if needed, or extend existing schema without breaking old results.

## F. R1 acceptance gates

- **R1-01** Identical pinned `verified` split in task loader and official evaluator; test proves `--split verified` on actual command.
- **R1-02** Absolute-path resolution and actual upstream CLI execution validated (under supported Linux/WSL2 container).
- **R1-03** Correct per-instance score association; unit tests catch bogus first-row placeholder and do not misclassify real failure score 0.
- **R1-04** ZIP verified and extraction documented, or status explicitly BLOCKED with verified cause; no destructive resume or unauthorized workspace.
- **R1-05** Three real 1-seed A/B score pairs (6 actual evaluator executions) each has an official raw log and matched program hash; any missing => PARTIAL/BLOCKED, not ACCEPTED.
- **R1-06** Safeguard tests pass + new integration parser/path/split/resume tests; exact counts and skipped tests reported.
- **R1-07** Credentials handled safely; no fake key/hidden patch; Docker/Linux environment disclosed.
- **R1-08** No retrospective preregistration claim; distinguish original prompt-ablation from active strategy policy; no inflated science findings.
- **R1-09** New results committed and pushed, `status.json` set to AWAITING_PLANNER_REVIEW/PARTIAL/BLOCKED; Planner alone accepts.

## G. Stop / report rather than conceal

- If tool denies `C:\\Users\\于舰\\XiaomiMiMoProjects\\SciTransfer`, move/reclone into allowed workspace only with user authorization; do not repeatedly run prohibited paths.
- `ChildProcess.kill` may indicate execution wrapper killed a child. Diagnose current PID/process and file size; it does not establish that download continued.
- If a valid OpenAI/Azure key is required by original evaluator, do NOT reuse DashScope keys or request secrets in chat. Provide user-safe local environment configuration instructions and pause as BLOCKED.
- If SharePoint ZIP cannot complete, pause and request user assistance placing official file; do not broaden model experiments or switch benchmarks unilaterally.
- No extra paid GPU/API runs without documented user approval for substantial cost.

## H. Executor response format

1. Final pushed SHA, platform, actual path (sanitize personal details), and repo status.
2. Per-task table for 85/16/21 with old A/B program hashes, official evaluator scores, log paths, provenance and run IDs.
3. Tests: passed/failed/skipped; exact commands and new tests for split/path/instance mapping/download.
4. R1-01…R1-09 with PASS / BLOCKED / FAIL.
5. Remaining blockers (with exact command/error evidence), available ZIP bytes, credential requirements, and minimal next action.
6. Update status and result files. Do **not** claim Planner acceptance.

**No Round 002 will be issued until Phase 0 is honestly reviewable.**
