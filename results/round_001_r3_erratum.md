# Round 001-R3 Evidence Erratum (ADDITIVE — does NOT modify historical records)

**Date:** 2026-10-09  
**Author:** MiMo (Executor)  
**Purpose:** Document known evidence integrity defects in Round 001-R3 results as required by `planner/plan_002.md` Track 0. This is an additive note only; original files under `results/round_001_r3_*` remain byte-for-byte unchanged.

---

## 1. Hardcoded GIS timeout values

**Observation:** `scripts/r3_finalize.py` (lines ~38-39) hardcodes `duration_s: 601.3` and `"Timeout after 600s"` for Task 21 A/B entries. However, `src/scitransfer/r3_eval.py` defines `TIMEOUT_SECONDS = 300` and `evaluate_one()` uses that default.

**Actual execution evidence:** Two separate diagnostic runs were made with `timeout_s=600` (not the default 300):
- `r3_21_no_strategy_s0`: `run_program_isolated(workdir, staged, timeout_s=600)` → `timed_out=True, duration=601.3s`
- `r3_21_fixed_strategy_s0`: same → `timed_out=True, duration=601.3s`

The 601.3s values correspond to the **diagnostic runs** (600s cap + overhead), not the core `evaluate_one()` default (300s). The finalize script hardcodes these values rather than deriving them from immutable logs. This is a documentation provenance defect.

**Impact:** The timeout facts are consistent with actual diagnostic runs but lack immutable log provenance in the committed summary.

## 2. CSV row count mismatch (8 vs 6)

**Observation:** `results/round_001_r3_evaluation_matrix.csv` contains 8 data rows, while `results/round_001_r3_runs/r3_all_results.json` contains 6 entries.

**Cause:** During iterative script development, intermediate results (including 2 orphan entries with `status=NO_OUTPUT` and missing `instance_id`/`arm` fields) were written to the CSV before cleanup. The JSON was cleaned to 6 entries by `scripts/r3_cleanup.py`, but the CSV was not regenerated.

**Impact:** The CSV is inconsistent with the JSON. The JSON (6 entries) is the authoritative record.

## 3. Task 85 scorer exceptions coerced to SUCCESS/0

**Observation:** `src/scitransfer/r3_eval.py` `evaluate_one()` catches `Exception` from the scorer and returns `status=SUCCESS, score=0`. Both Task 85 arms hit `KeyError('argmax')` (missing key in predicted JSON).

**Reasoning:** The official upstream `compute_scores.py` also catches scorer exceptions and returns `success=0`. The executor matched this behavior. However, the Planner notes this is **not independently verified** against the protected original grading wrapper.

**Proper labeling:** These should be `SCORER_EXCEPTION` with `score=null` as the validated direct-return score, and `assumed_failure_score=0` only if validated against upstream semantics. The current `status=SUCCESS` label is misleading.

## 4. Task 16 empty outputs

**Observation:** Both Task 16 arms produced `overlap: 0.0` from the official scorer, indicating empty or non-overlapping prediction files.

**Cause:** The predicted `compound_filter.py` programs ran (exit_code=0) but produced empty or incorrect output files.

**Impact:** Score of 0 is genuine (direct scorer return), but reflects a floor effect, not a meaningful scientific outcome.

## 5. Hidden gold access via benchmark junction

**Observation:** `prepare_isolated_workdir()` creates a junction from `workdir/benchmark` to the entire `benchmarks/ScienceAgentBench/benchmark/` tree, which includes `eval_programs/gold_results/` (gold answer files).

**Risk:** Candidate programs have a potential read path to hidden evaluation material. The six committed scripts do not appear to exploit this, but the harness is not safe for rigorous future trials.

**Required fix (future):** Candidate-facing sandbox with task input datasets ONLY; scorer runs in a separate trusted context.

## 6. Test independence

**Status:** 69 tests were run by the executor. The Planner has **not independently rerun** them. Results are executor-reported.

---

## Summary

| Defect | Severity | Historical record modified? |
|--------|----------|---------------------------|
| Hardcoded 601.3s timeout | P0 (provenance) | No — documented here |
| CSV 8 rows vs JSON 6 | P0 (consistency) | No — documented here |
| Exception coerced to SUCCESS/0 | P0 (labeling) | No — documented here |
| Task 16 empty outputs | P1 (floor effect) | No — genuine result |
| Hidden gold junction | P0 (isolation) | No — documented here |
| Tests not independently run | P1 | No — executor-reported |

**All original R3 files remain unchanged. This erratum is purely additive.**
