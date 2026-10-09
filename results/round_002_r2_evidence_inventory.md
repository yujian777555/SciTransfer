# Round 002-R2 Evidence Inventory

**Date:** 2026-10-09  
**Purpose:** Catalog all evidence from R2-R2 with verification status.

---

## Tracked artifacts

| File | Status | Verification |
|------|--------|-------------|
| `results/result_round_002_r2.json` | Tracked | Summary only; no raw traces |
| `results/round_002_r2_pilot/r2_llm_pilot_results.json` | Tracked | 4 summary objects; no per-step data |
| `results/round_002_r2_preflight.md` | Tracked | Contains `[to be filled]` placeholder |
| `results/round_002_r2_decision.md` | Tracked | Analysis document |
| `experiments/round_002_r2_preregistration.json` | Tracked | Timestamp contradictory (see erratum) |
| `src/scitransfer/secure_input.py` | Tracked | Canary tests exist; not used in actual runner |
| `tests/test_r2_g0_isolation.py` | Tracked | 10 unit tests pass |

## Missing evidence (not committed)

| Evidence | Status | Impact |
|----------|--------|--------|
| Per-step model request/response | NOT COMMITTED | Cannot verify actual API calls |
| HTTP response metadata | NOT COMMITTED | Cannot verify provider usage |
| Token counts per call | NOT COMMITTED | Cost estimate unverifiable |
| Action parsing errors | NOT COMMITTED | Fallback concealment unverified |
| Full pytest output | NOT COMMITTED | Test verification incomplete |
| Provider billing record | NOT COMMITTED | Actual spend unverified |
| Neutral control runs | NOT RUN | No baseline comparison |

## Historical exposure (Git history)

| Data | Exposure | Status |
|------|----------|--------|
| `criticalHypotheses` in `*_trusted.json` | 4 files tracked in R1 commit | Untracked in R2; history retains |
| Seeds 42, 43, 100 | Used in R1/R2 diagnostics | Quarantined |
| Seed 200 | Used in G1 diagnostic + R2 target | Quarantined |

---

## Summary

R2-R2 provides **summary-level results** (4 episodes, cost estimate, test count) but lacks the **raw evidence** needed for independent verification. All scientific conclusions are labeled `UNVERIFIED_*` per the erratum.
