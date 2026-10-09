# Round 002 Evidence Erratum (ADDITIVE — does NOT modify historical records)

**Date:** 2026-10-09  
**Author:** MiMo (Executor)  
**Purpose:** Document known validity defects in Round 002 results as required by `planner/plan_002_r1.md` Track A. Original files under `results/round_002_calibration/` and `results/result_round_002.json` remain byte-for-byte unchanged.

---

## 1. Invalid DiscoveryWorld action schema

**Observation:** `SimplePolicyAgent.decide` in `src/scitransfer/discoveryworld_adapter.py` (lines ~127-141) emits:
- `{"action": "moveAgentForward"}`
- `{"action": "pickupObject", "objectName": "key"}`
- `{"action": "useObject", "objectName": "jar"}`

**Actual upstream schema:** `DiscoveryWorldAPI.listKnownActions()` and `ActionHistory.ActionType` use uppercase enum values: `MOVE_DIRECTION`, `PICKUP`, `USE`, with `arg1`/`arg2` for direction/UUID.

**Impact:** All 12 episodes may have produced invalid actions that were silently ignored (environment tick proceeded regardless). `n_valid_actions` was never measured.

## 2. Decision count is step-count proxy, not observation-dependent

**Observation:** `is_decision_point = action_count >= 2` (line ~157). `SimplePolicyAgent.decide` does not inspect `observation` or `task_description` — it branches solely on `self.action_count`.

**Impact:** `n_decision_points=14` is meaningless as evidence of scientific decision-making. Two identical observations at the same step produce identical actions.

## 3. Serialized episodes have zero observations and actions

**Observation:** `EpisodeTrace.to_dict()` returns `n_observations=len(self.observations)` and `n_actions=len(self.actions)`, but `run_episode()` never populates these lists — only `scorecard` is set. All 12 episode JSON files show `n_observations=0, n_actions=0` despite `steps_taken=15`.

**Impact:** No replayable step-by-step evidence. Scores alone cannot prove actual decisions.

## 4. Hidden evaluator information in committed traces

**Observation:** `run_episode()` calls `getTaskScorecard()` which returns `criticalHypotheses` and `criticalQuestions`. These are saved in episode JSON files (e.g., Reactor Lab traces contain `"criticalHypotheses": ["If the key is placed in a mixture of pure Substance C, then the rust will be removed."]`).

**Impact:** Evaluation-relevant hidden answers are present in stored artifacts. While the rule-based policy only received `taskDescription`, this is a leakage risk for future agent contexts.

## 5. Reactor Lab 2/11 may be initial/ambient score

**Observation:** Both arms of seed 42 show identical 2/11. The script does not record initial score before agent actions. Sub-task breakdown shows `Reactors On: 2/3` while all other sub-tasks are 0.

**Impact:** The 2/11 score may reflect environment initial state, not agent progress. Requires initial-score control to verify.

## 6. SUCCESS label despite completedSuccessfully=false

**Observation:** `RunStatus.SUCCESS` assigned when `final_score > 0`, even though `completedSuccessfully=false` for Reactor Lab episodes.

**Impact:** Confuses partial progress with task completion.

## 7. SciAgentGYM incorrectly marked unavailable

**Observation:** Suitability matrix states SciAgentGYM is "NOT AVAILABLE" based on GitHub search of wrong URLs. Actual public repo: `https://github.com/CMarsRover/SciAgentGYM`.

**Impact:** Factual error in candidate assessment.

---

## Quarantine notice

**All Round 002 calibration episodes (seeds 42/43, all 12 files) are QUARANTINED from future held-out evaluations and training.** They contain hidden evaluator information (`criticalHypotheses`/`criticalQuestions`) and were produced with invalid action schemas. They are preserved as historical records only.

**Affected files:**
- `results/round_002_calibration/r2b_*.json` (all 12 episode files)
- `results/round_002_calibration/calibration_summary.json`
- `results/result_round_002.json`

---

## Summary

| Defect | Severity | Historical record modified? |
|--------|----------|---------------------------|
| Invalid action schema | P0 | No — documented here |
| Decision count is step proxy | P0 | No — documented here |
| Zero serialized observations/actions | P0 | No — documented here |
| Hidden evaluator info in traces | P0 | No — documented here |
| Reactor Lab 2/11 unproven attribution | P0 | No — documented here |
| SUCCESS label misleading | P1 | No — documented here |
| SciAgentGYM URL wrong | P1 | No — documented here |

**All original Round 002 files remain unchanged. This erratum is purely additive.**
