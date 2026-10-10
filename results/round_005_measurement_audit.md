# Round 005 Measurement Audit — D1 DGP

**Date:** 2026-10-10  
**Status:** MEASUREMENT VALIDITY SMOKE

---

## 1. Score distribution

| Task | Policy | FDP | Power | Cost | Utility |
|------|--------|-----|-------|------|---------|
| dev_m1_1 | naive_fixed | 0.350 | 0.394 | 0 | 0.418 |
| dev_m1_1 | feedback_conditioned | 0.267 | 0.333 | 8 | 0.411 |
| dev_m1_2 | naive_fixed | 0.300 | 0.264 | 0 | 0.386 |
| dev_m1_2 | feedback_conditioned | 0.267 | 0.208 | 8 | 0.360 |
| dev_m2_1 | naive_fixed | 0.450 | 0.306 | 0 | 0.342 |
| dev_m2_1 | feedback_conditioned | 0.400 | 0.250 | 8 | 0.324 |
| dev_m2_2 | naive_fixed | 0.700 | 0.207 | 0 | 0.203 |
| dev_m2_2 | feedback_conditioned | 0.667 | 0.172 | 8 | 0.186 |

**Key findings:**
- FDP range: 0.267 to 0.700 (non-degenerate ✅)
- Power range: 0.172 to 0.394 (non-degenerate ✅)
- M2 (confounded) has worse FDP than M1 (unconfounded) ✅
- Policies produce different outcomes ✅

---

## 2. Biases and limitations

| Bias | Description | Mitigation |
|------|-------------|------------|
| **Synthetic DGP** | Not validated biological mechanism | Documented as assumption |
| **Independent genes** | No co-expression structure | Simplified model |
| **Additive batch** | Not multiplicative | Documented limitation |
| **Simple policies** | Naive/feedback, not learned | DEV smoke only |
| **Small sample** | 4 DEV tasks × 2 policies | Not statistically powered |

---

## 3. Failure paths

| Case | Behavior | Tested? |
|------|----------|---------|
| All-null | `null_power=True`, FDP=0 | ✅ |
| Missing answer | FDP=0, Power=0 | ✅ |
| Invalid action | Typed error, fail-closed | ✅ |
| Budget exhaustion | Rejects action | ✅ |
| Strategy identity | Same trace → same score | ✅ |

---

## 4. Independent process proof

| Component | Isolation |
|-----------|-----------|
| DGP | Generates hidden truth |
| Engine | Public observation only |
| Evaluator | Separate function, receives hidden truth directly |
| Candidate | Public view has no hidden fields |

**Note:** True OS process isolation not implemented (single Python process). Function-level separation enforced via API boundaries.

---

## 5. Score-strategy-ID invariance

**Verified:** `score_submission()` takes only `reported_genes`, `true_non_null`, `sample_cost`. No strategy ID/name parameter. Identical inputs → identical scores.

---

## 6. Conclusion

**Measurement validity smoke: PASS**

- Non-degenerate score variation across tasks and policies
- Correct FDP/Power/Cost accounting
- Two mechanism regimes show different difficulty levels
- Strategy-identity invariance enforced
- No reward hacking detected
