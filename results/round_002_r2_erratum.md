# Round 002-R2 Evidence Erratum (ADDITIVE — does NOT modify historical records)

**Date:** 2026-10-09  
**Author:** MiMo (Executor)  
**Purpose:** Document evidence validity defects in Round 002-R2 as required by `planner/plan_003.md` Track A. Original files remain byte-for-byte unchanged.

---

## 1. Preregistration timestamp contradiction

**Observation:** `experiments/round_002_r2_preregistration.json` has `timestamp_utc: "2026-10-09T22:00:00Z"`. The final commit `b05c446` has Git timestamp `2026-10-09T13:42:28Z`. The declared registration timestamp is **~8 hours AFTER the commit**, not before.

**Impact:** Preregistration cannot be verified as prospective. Label: `UNVERIFIED_PROSPECTIVE_REGISTRATION`.

## 2. Same-commit first appearance

**Observation:** The preregistration file first appears in the same commit as the results. No separate pre-run registration commit exists.

**Impact:** No independent proof of preregistration before target evaluations. Label: `UNVERIFIED_PROSPECTIVE_REGISTRATION`.

## 3. Configuration mismatch

**Observation:** `r2_llm_pilot_v2.py` differs from preregistration:
- Strategy text: v2 uses shortened text vs registered full text
- `max_tokens`: v2 uses 1024 vs registered 2048
- Steps: v2 uses 10 vs registered 15
- Arm order: v2 uses fixed order vs registered randomized

**Impact:** Treatment configuration diverges from preregistration. Label: `CONFIGURATION_MISMATCH`.

## 4. Seed contamination

**Observation:** G1 diagnostic (`r2_g1_diagnostic.py`) tested Combinatorial Chemistry seed 200. The pilot reuses the same seed 200 as target.

**Impact:** Seed 200 is not genuinely held-out. Label: `UNVERIFIED_EPISODE_TRACE`.

## 5. Missing raw traces

**Observation:** Only summary JSON is committed. No per-step model/tool/observation traces, no HTTP metadata, no token counts, no action parsing errors.

**Impact:** Episode-level evidence cannot be independently verified. Label: `UNVERIFIED_EPISODE_TRACE`.

## 6. Cost is estimate, not bill

**Observation:** Cost $0.074 is computed from token counts × fixed coefficients. No authenticated provider billing record.

**Impact:** Actual API spend unverified. Label: `UNVERIFIED_API_USAGE_COST`.

## 7. Test log placeholder

**Observation:** `results/round_002_r2_preflight.md` contains literal `[to be filled after full run]` where full pytest output should be.

**Impact:** Test verification incomplete. Label: `UNVERIFIED_EPISODE_TRACE`.

## 8. Fallback concealment

**Observation:** Invalid LLM responses silently fall back to `MOVE_DIRECTION east`. API errors returned as content instead of fail-closed.

**Impact:** Model/action parsing failures concealed. Label: `CONFIGURATION_MISMATCH`.

## 9. Canary not used in actual runner

**Observation:** `r2_llm_pilot_v2.py` does not import or call `build_model_input()`. Canary tests exist but are not exercised in the real runner.

**Impact:** Live model-input isolation not demonstrated. Label: `CONFIGURATION_MISMATCH`.

## 10. Missing neutral control

**Observation:** No matched no-action/tick-only controls were run.

**Impact:** Cannot distinguish agent progress from ambient score changes. Label: `NO_VALID_SCIENTIFIC_TRANSFER_COMPARISON`.

---

## Labels applied

| Label | Applied to |
|-------|-----------|
| `UNVERIFIED_PROSPECTIVE_REGISTRATION` | Preregistration timing |
| `UNVERIFIED_EPISODE_TRACE` | Raw traces, seed contamination, test log |
| `UNVERIFIED_API_USAGE_COST` | Cost estimate |
| `CONFIGURATION_MISMATCH` | Strategy text, tokens, steps, arm order, canary bypass, fallback |
| `NO_VALID_SCIENTIFIC_TRANSFER_COMPARISON` | Overall R2-R2 scientific conclusion |

---

## Quarantine

- Seeds 42, 43, 100, **200** are quarantined (exposed in diagnostics or contaminated)
- Historical `*_trusted.json` exposure remains in Git history
- No retroactive repair of timestamps or evidence

**All original Round 002-R2 files remain unchanged. This erratum is purely additive.**
