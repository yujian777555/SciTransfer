# Round 002-R1 Evidence Erratum (ADDITIVE — does NOT modify historical records)

**Date:** 2026-10-09  
**Author:** MiMo (Executor)  
**Purpose:** Document validity defects in Round 002-R1 as required by `planner/plan_002_r2.md` G0.

---

## 1. Navigation-only "valid actions"

**Observation:** The 4 valid actions in Combinatorial Chemistry FIXED_STRATEGY were all `MOVE_DIRECTION east` (navigation). The baseline's 0 valid actions were `PICKUP wall` attempts and `MOVE_DIRECTION north` (blocked by wall).

**Impact:** 4-vs-0 reflects navigation success vs wall-pickup failure, NOT scientific experimentation or strategy benefit.

## 2. Trusted scorecards committed publicly

**Observation:** All 4 `*_trusted.json` files containing `criticalHypotheses` and `criticalQuestions` were tracked in Git.

**Status:** Now untracked via `git rm --cached`. `.gitignore` rules added. **Historical Git content remains accessible** — deletion from index does not remove historical exposure.

## 3. Zero score deltas

**Observation:** All 4 episodes show `score_delta=0.0`. No evidence of improved scientific outcome.

## 4. Test count inconsistency

**Observation:** `result_round_002_r1.json` reports `21 passed / 0 failed / 1 skipped` for R1 subset. Chat claimed `104 passed / 0 skipped`. These are inconsistent without a full suite log.

## 5. Missing neutral control

**Observation:** No matched no-action/tick-only controls were run. Reactor Lab seed 42 ambient-credit question remains unresolved.

## 6. Policy-class confound

**Observation:** A/B used different policy classes (`NoStrategyAgent` vs `EvidencePolicyAgent`). Any action difference is confounded with base policy capability.

---

## Quarantine notice

**Seeds 42, 43, 100 are QUARANTINED** from future held-out evaluations and training. These scenarios' hidden evaluator information has been exposed in public Git history.

**Affected scenarios:**
- Combinatorial Chemistry (seeds 42, 43, 100)
- Archaeology Dating (seeds 42, 43, 100)
- Plant Nutrients (seed 42)
- Reactor Lab (seed 42)

**Future pre-registration must use fresh seeds NOT in {42, 43, 100}.**

---

## Summary

| Defect | Severity | Status |
|--------|----------|--------|
| Navigation-only valid actions | P0 | Documented |
| Trusted scorecards in Git | P0 | Untracked; historical exposure remains |
| Zero score deltas | P1 | Documented |
| Test count inconsistency | P1 | Documented |
| Missing neutral control | P1 | Documented |
| Policy-class confound | P0 | Documented; R2 uses identical LLM agent |

**All original Round 002-R1 files remain unchanged. This erratum is purely additive.**
