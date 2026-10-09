# Planner Review — Round 001-R2 (2026-10-09)

**Reviewed repository:** https://github.com/yujian777555/SciTransfer
**Reviewed main HEAD:** `65c425ac0509e1d612ac322f47e7172ea9b87c02`
**Executor evidence commit:** `12a6dfa902886f3a9c12ead5d6b25fc18f1f4e73`
**Planner verdict:** **NOT ACCEPTED — R3 EVALUATION VALIDITY REMEDIATION REQUIRED**
**Next plan:** `planner/plan_001_r3.md`; current round remains 001.
**Scope:** Source-code and committed-artifact review. Planner has NOT rerun the 55 tests and has NOT independently accessed the protected official ZIP on the executor's machine.

## 1. Git integration is closed

- `main` HEAD equals `65c425ac0509e1d612ac322f47e7172ea9b87c02`, whose only modified file is `.gitignore`.
- `.gitignore` includes `benchmarks/ScienceAgentBench-upstream/`, and the remote tracked tree has no files under the junction.
- Local cleanliness and `git check-ignore` behavior are executor-reported, not independently inspected on the user's PC. GitHub history confirms the ignore rule is committed.
- No force push or history rewrite seen in the commit lineage.

## 2. Credible progress

- `results/result_round_001_r2.json` records the 1,769,478,786 byte archive with SHA256 `46e715d3b2196d459d2dff52aa487f506a95ec44b44262e82208d086ea879610` and extraction. These checks are Executor-reported; archive stays local, not in Git.
- Six original Round 001 generated programs are enumerated with hashes. R2 reports no new LLM calls.
- Executor reports 55 passed / 0 failed / 0 skipped, including 12 downloader tests. This is NOT an independently rerun test result.
- Program attempts: #85 A and B = provisional 0/0; #16 A and B = provisional 0/0; #21 A and B = timeout / null. These are marked `official_evaluation=false`.
- Unmodified official Docker evaluator has **zero** accepted runs; Docker build blocked by network in executor report.

## 3. Blocking correctness defects verified in committed `scripts/r2_evaluate_all.py`

### P0-1: Manual scoring is NOT the original official evaluator function

- `score_85()` manually implements JSON comparison; #16 uses `gold_text == pred_text`; #21 also uses exact CSV-text comparison.
- Thus the script's description `All scoring logic is UNMODIFIED` is FALSE as a statement about the code path: scorer functions are reimplementations, not direct calls into unmodified scorer modules.
- Executor reports the protected upstream #16 scorer checks gold-set coverage with extra rows allowed, and #21 scorer checks relative error with tolerance. These rules have NOT been independently inspected by Planner in protected local benchmark files. They must be verified with exact upstream paths, hashes and executable parity tests before any claim of metric alignment.

### P0-2: Cross-arm output contamination

- `run_program(program, REPO_ROOT)` and `output_file = REPO_ROOT / "pred_results" / ...` share an output directory across arms.
- No per-arm clean workspace, no strict no-existing-output assertion, and no ownership proof. A stale A result could be read for B.
- Need independent workspaces, data read-only exposure, generated output isolated, hashes and fresh file evidence.

### P0-3: Hash check is advisory, not fail-closed

- Code computes 16-character `actual_sha` and `hash_match` but does NOT abort when false. Compare complete 64-hex hashes and reject before execution.
- The historical hash catalog itself must be retained unchanged.

### P0-4: Nonzero/timeout may still score stale files

- `run_program` returns exit code and text; next code checks output existence without first requiring successful execution.
- Timeouts should yield null score / explicit timeout with reliable process/child-tree termination, without reading outputs from any other run.
- `run_program` in this file sets `timeout=120` seconds whereas R2 summary says >600s for GIS. Could be separate attempts; require per-attempt timings/commands and no conflation.

### P1-5: Result labels and math are internally inconsistent

- JSON reports two source task pairs (#85 and #16) each with A and B numeric score 0, but limitations say `0/3 A/B pairs with both arms successfully scored`. Accurate language: **two pairs have provisional numbers, zero pairs have fully validated official parity**, one pair timed out. Do not report raw numeric zeroes as validated official scores.
- `scripts/r2_score_85_final.py` also contains a redefined `eval()` and a hardcoded arm, so its output cannot independently certify the official scorer.

### P1-6: Testing gap

- The 55 committed unit tests focus on downloader and prior evaluator wrapper. No demonstrated integration tests directly proving each A/B output isolation, hard hash rejection, scorer parity on counterexamples, no-stale-output, or timeout handling.
- Artifact checksum and HF verified split mapping continue to be important. Official scorer file contents and their SHA must be stored only as safe **metadata**, not redistributed protected data.

### P1-7: Scientific interpretation

- All six are retrospective **single-shot strategy-prompt code outputs**, not adaptive research policy, nor transfer from previously learned cross-domain trajectories.
- At seed label 0 and only one strategy, no causal cross-domain or performance generalization can be inferred.
- Timestamp `preregistered_at` in original config remains UNVERIFIED. Retain original records.

## 4. Planner R2 Gate review

| Gate | Verdict | Reason |
|---|---|---|
| R2-01 | REPORTED PASS | ZIP fully downloaded/verified per executor; read-only original not independently rehashed |
| R2-02 | PARTIAL | Pinned local 102-row split reported; original evaluator parity not independently run |
| R2-03 | BLOCKED | Zero original official Docker evaluations, modified evaluator used |
| R2-04 | FAIL | Shared outputs, advisory hash check, scorer mismatch and stale output risk |
| R2-05 | FAIL | Zero fully trustworthy 3-domain A/B pairs; raw 4 numeric values are not certified |
| R2-06 | REPORTED PASS / COVERAGE INCOMPLETE | 55 tests claimed; missing scoring integration tests |
| R2-07 | PARTIAL | Original runs reportedly unchanged; claims about scorer being UNMODIFIED require correction |
| R2-08 | GIT SYNC VERIFIED / NOT ACCEPTED | Git and R2 submission in main; Planner formally rejects current scientific scoring |

## 5. Decision

**Round 001-R2 is NOT ACCEPTED.** Continue with **Round 001-R3** to validate exact upstream scoring semantics and create truly isolated A/B execution for the six saved, hash-frozen programs. No new model inference, new strategy, training, or benchmark expansion. Separate **(a)** original official Docker results, **(b)** validated direct-official-scorer results, and **(c)** reimplemented exploratory results. Never promote (b)/(c) into (a).

If no end-to-end reliable evaluation is feasible after bounded R3 attempts, report a blocker and recommend a decision (environment repair vs switching to an accessible benchmark); do not continue remediation forever.

Planner acceptance of Phase 0 awaits credible evaluated paired outcomes and provenance. The experimental effect of cross-domain strategy transfer remains unmeasured.
