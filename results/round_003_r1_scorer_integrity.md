# Round 003-R1 Scorer Integrity Report

**Date:** 2026-10-09  
**Method:** Judge-denial firewall (monkeypatch LLM judge to throw)

---

## 1. Scorer components

| Function | Type | Judge-free? | Notes |
|----------|------|-------------|-------|
| `extract_boxed_answer` | Pure regex | ✅ Yes | Extracts `\boxed{}` content |
| `calculate_answer_score` | Mixed | ⚠️ Partial | Pure for exact match; LLM judge for mismatches |
| `is_answer_correct` | LLM judge | ❌ No | Always calls JUDGE_MODEL |
| `secondary_verification_with_llm` | LLM judge | ❌ No | Called on mismatch fallback |
| `template_match_with_llm` | LLM judge | ❌ No | For strings >7 chars |

## 2. Judge-denial test results

| Test case | Score | Judge called? | Label |
|-----------|-------|---------------|-------|
| Perfect match `{42.0}` vs `{42.0}` | 100% | No | OFFLINE_OK |
| Wrong `{99.0}` vs `{42.0}` | — | **YES** | JUDGE_REQUIRED |
| Missing field `{42.0}` vs `{42.0, "label"}` | — | — | — |
| Near-correct `{42.01}` vs `{42.0}` | — | — | — |

**Key finding:** `calculate_answer_score` calls `secondary_verification_with_llm` when values don't match. This is NOT a pure offline scorer.

## 3. Implications

| Use case | Offline? | Authentic score? |
|----------|----------|------------------|
| Exact match scoring | ✅ Yes | ✅ Yes |
| Mismatch scoring | ❌ Needs LLM judge | ❌ JUDGE_REQUIRED |
| `is_answer_correct` | ❌ Needs LLM judge | ❌ JUDGE_REQUIRED |

## 4. Disclosure

Per plan: "If a mismatch attempts a judge call, record `JUDGE_REQUIRED` or `OFFLINE_SCORER_NOT_EQUIVALENT` and do NOT report an authentic original official offline score for that path."

**Applied:** Mismatch paths are labeled `JUDGE_REQUIRED`. No authentic offline score claimed for mismatches.

## 5. Canary isolation test

| Test | Result |
|------|--------|
| Canary injected into `answer`, `golden_answer`, `solution_steps` | Present in hidden data |
| Canary in candidate-facing view | **NOT PRESENT** ✅ |
| Canary in tool request | **NOT PRESENT** ✅ |

**Conclusion:** Hidden answer isolation works at the data structure level. Runtime enforcement needed for full protection.
