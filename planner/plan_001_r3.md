# SciTransfer — Planner Round 001-R3: Scoring Parity, Arm Isolation, Evidence Integrity

**Issued:** 2026-10-09
**Planner:** ChatGPT
**Executor:** Kimi/MiMo (actual runtime to be disclosed)
**Repo:** https://github.com/yujian777555/SciTransfer
**Reviewed base HEAD:** `65c425ac0509e1d612ac322f47e7172ea9b87c02`
**Phase/Round:** PHASE0 / 001-R3 — **NOT Round 002**
**Required review:** `planner/reviews/review_001_r2.md`
**Status:** ISSUED, awaiting executor work

## Objective and hard scope

Repair the **validity** of evaluating the six previously generated Round 001 programs, using exact upstream scoring semantics, independent A/B workspaces, and immutable provenance. The current provisional scores (#85 A/B=0; #16 A/B=0; #21 both timeout) are **NOT accepted scientific evidence**.

No fresh LLM calls or program generation, no training, no broad new datasets, no alteration of research goals or accepted metric definitions. Retain all historical `results/round_001_runs/`, `results/round_001_r1_runs/`, `results/round_001_r2_runs/` and original round results unchanged. New outputs go ONLY in `results/round_001_r3_runs/` and new result/metadata files.

### Preflight

1. `git pull --ff-only`; inspect `status.json`, `planner/latest_plan.md`, `planner/reviews/review_001_r2.md`, `results/result_round_001_r2.json`, `results/round_001_r1_program_hashes.json`, and scripts.
2. Confirm junction `benchmarks/ScienceAgentBench-upstream/` is ignored and not tracked; do not alter Git history.
3. Timestamp and record the current ZIP integrity, upstream pinned commit `c26e151ed601ba109dc4d35e057ff8e73fec469d`, verified parquet SHA `c6f937863a220bd1762a00c20a0f79cc8dfca900b819bdb552150310731ae147`, runtime, Docker access, protected artifact directory. Do not push raw/secret data.
4. Zero API regeneration budget this round; runtime resource budget for local scoring should be declared before execution.

## Track A — Verify actual upstream scorer semantics (P0, before any new score)

1. Locate the exact **protected** official scoring scripts from downloaded `benchmark_verified.zip` for IDs 85,16,21, from their verified task metadata. Record their relative paths, byte SHA256, file version and callable interfaces. **Do not check protected files into Git or print gold answer contents.**
2. Confirm by reading/executing actual scorer functions what the metrics and accepted output structures are. In particular test executor's allegations for #16 (gold-set coverage vs strict text equality), #21 (numerical tolerance vs CSV byte equality), and #85 (JSON keys/types/tolerance). Document code-path facts separately from allegations and guesses.
3. **Prefer direct import/invocation of the actual official scoring function** on isolated artifact paths, preserving original code byte-for-byte. If the scorer uses a script/CLI rather than importable callable, invoke it as shipped within a validated test harness with documented cwd/env/arguments. Do not paraphrase the algorithm into a new scorer and claim original implementation.
4. Build a small cross-check suite: perfect output, allowed benign extra row (#16 if officially accepted), output with harmless numeric formatting perturbation (#21 if accepted), incorrect output, missing file, corrupted file. Record observed outcomes from actual original scorer. Fixtures should not include protected gold data in Git; tests in public repo can use synthetic/pseudodata.
5. Formal provenance category in EVERY result: `ORIGINAL_OFFICIAL_DOCKER`, `DIRECT_ORIGINAL_SCORER_MODIFIED_RUNNER`, or `REIMPLEMENTED_EXPLORATORY`. `official_evaluation=true` ONLY for `ORIGINAL_OFFICIAL_DOCKER` with proper upstream run evidence; direct import stays false but may be scientifically informative if parity tested.

## Track B — Strict A/B isolation and integrity (P0)

1. For each (task, arm) create a **brand-new distinct run workdir**, with `pred_results/`, temporary HOME, sanitized environment, captured stdout/stderr, explicit start/end timestamps, and unique run_id. **Never use REPO_ROOT/pred_results/** or output from another arm; fail if run dir/output pre-exists unless intentionally creating a new unique run.
2. Give candidate programs access to **task-only allowed datasets** via a documented local read-only path/mount matching the original benchmark's expected relative `benchmark/datasets/...` layout, while keeping protected gold/eval scripts out of candidate's writable/readable sandbox where possible. No hidden-answer leakage.
3. Before copying/launching, compare candidate program byte SHA256 **all 64 characters** to frozen catalog and error out on mismatch. Exact expected script filename, task ID and arm must match. Keep old programs byte-identical. Re-hash staged copy before running.
4. On nonzero exit, timeout or no fresh output in this run directory, record status `EXECUTION_FAILED`/`TIMEOUT` with `score:null`; do not inspect pre-existing global paths or fallback to stale output. Kill timed-out process trees reliably and record final status.
5. Prevent B from reusing A output: automated test deliberately places a stale A output in a different directory; B must not see or score it. Test no-score-on-hash-mismatch, no-score-on-failed-exit, no-score-on-timeout, output belongs to run, and correct program staging.
6. Pin program interpreter/package versions per task. If official scorer requires special environment or prior setup, record exact commands and limitations. No guessing based on generated program success.

## Track C — Re-evaluate six ORIGINAL programs only

1. Smoke test task #85 A end-to-end in isolated workdir with **direct original scorer**, save stdout/stderr, program hash, scorer hash, data provenance and validated output. If blocked, stop and provide exact blocker.
2. Evaluate #85 B, #16 A/B, #21 A/B using same protocol. Run IDs distinct. For GIS #21 inspect performance bottleneck in a separate controlled diagnostics run; do not modify program semantics to get a score. Record actual per-arm timeout from tool logs (the existing r2_evaluate_all.py has `timeout=120` while R2 summary reports >600s, possibly across attempts). If cost acceptable, permit one documented bounded timeout extension, same limit for A and B, with a cap chosen before running. If infeasible, keep score null, provide comparable timeout outcome; do not substitute a different task without Planner approval.
3. Preserve all genuine zeros. Never report a scorer mismatch or program failure as a genuine official zero without confirmed upstream evaluator semantics and program execution evidence.
4. Produce `results/round_001_r3_evaluation_matrix.csv` with task/arm/seed, full program SHA, scorer SHA, interpreter, environment fingerprint, run_id, exit code, actual duration, output SHA, provenance category, numeric score or null, log paths, failure reason and source commit. Compute paired differences ONLY when each pair has two validated comparable scores and same allowed runtime budgets.
5. Report separate metrics `n_attempted`, `n_executed`, `n_scored_direct_original`, `n_scored_official_docker`, `n_valid_pairs`, `n_timeouts`. Do not contradict numeric pair counts and validated pair counts. Never call a direct-scorer score official.

## Track D — Original Docker path decision (bounded)

- Diagnose Docker build network issue with exact command and 1-2 bounded attempts; prefer already-built images/offline environment if documented and reproducible.
- No fake OPENAI_API_KEY or substitution of DashScope as OpenAI. For unmodified original harness, use genuine local credentials if required (do not ask for secrets in chat).
- If original Docker remains blocked after bounded attempts, declare `ORIGINAL_OFFICIAL_DOCKER_BLOCKED` and keep direct-original-scorer results separate. Do not wait forever; return an actionable decision point to Planner.
- Do not modify original upstream scorer to force scores; if any setup adapter is necessary, disclose diff+reason.

## Track E — Tests, documentation, exit gates

Add tests for:
- original scorer invocation via appropriate stubs/fixtures, byte-hash provenance, executable parity corner cases for #16/#21/#85;
- full SHA mismatch hard rejection, corrupt/missing output, failed exit, stale output, path traversal;
- A/B isolation, no cross-arm contamination and no fallback to repository pred_results;
- timeout and process tree cleanup; scorer exceptions return null rather than invented zero;
- no official flag for direct-original-scorer or reimplementation; matched budgets and artifact provenance.

Run existing 55 tests + additions; report real pass/fail/skip totals and exact commands. Existing original protected artifacts must stay outside Git. Update documentation to withdraw or qualify previous `All eval() functions are UNMODIFIED` claim in R2 report **without rewriting old history**: use an R3 erratum/new review explaining R2 was reimplemented.

**Deliverables:** `results/round_001_r3_preflight.md`, `results/round_001_r3_evaluation_matrix.csv`, `results/round_001_r3_runs/`, `results/result_round_001_r3.json`, code/tests and `status.json`; include optional `results/round_001_r3_erratum.md`.

### R3 acceptance gates (Planner alone)

- **R3-01:** Verified exact upstream scorer functions and SHA for all three selected tasks; no protected answers committed.
- **R3-02:** 6/6 source programs verified by FULL SHA and executed in separately isolated A/B workspaces with tests proving no stale output use.
- **R3-03:** Official scorer parity demonstrated on targeted corner cases; reimplemented R2 results clearly labeled invalid/provisional.
- **R3-04:** Six attempts with original scorer or correct explicit null/timeout/error reasons; at least 3 comparable A/B pairs for full acceptance, else PARTIAL and a bounded blocker/decision.
- **R3-05:** Original Docker vs direct original scorer provenance separated; honest platform, credential and network disclosures.
- **R3-06:** All prior tests + new integration tests pass (actual recorded counts), no skipped failures.
- **R3-07:** Historical evidence and program artifacts unchanged; no new model calls and no overstated research conclusions.
- **R3-08:** Result + status committed and pushed to main; Executor may mark `AWAITING_PLANNER_REVIEW`, `PARTIAL` or `BLOCKED` but not ACCEPTED.

**STOP RULE:** If direct original scorer cannot be correctly invoked, or if GIS cannot finish within one reasonable shared timeout cap, STOP and report proof. Planner will then decide environment repair or a genuinely accessible benchmark. Do not loop endlessly through R4/R5 without explicit new evidence.

## Executor final handoff

Report final git SHA, worktree state, Docker status, six per-arm outputs with full source/scorer hash and scorer origin, actual timings/errors, validated pair count, tests, R3-01..08, artifact locations, critical blockers, expected next cost. Do NOT claim a SciTransfer transfer effect from this pilot.
