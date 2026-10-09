# Benchmark Suitability Matrix — Round 002 R1 Correction

**Date:** 2026-10-09  
**Type:** ADDITIVE correction to `suitability_matrix_round_002.md`  
**Purpose:** Correct factual errors identified in `planner/reviews/review_002.md`

---

## Correction 1: SciAgentGYM availability

**Previous claim:** "SciAgentGYM: NOT FOUND (404)"  
**Corrected status:** **AVAILABLE_REPO / RUNTIME_NOT_EVALUATED**

**Evidence:**
- Actual public repo: https://github.com/CMarsRover/SciAgentGYM
- GitHub API confirms repository exists
- Not yet installed or tested in this project

**Impact on recommendation:** DiscoveryWorld remains primary candidate (tested and working). SciAgentGYM is now listed as available but untested alternative.

---

## Correction 2: Domain independence

**Previous claim:** "Genuinely different scientific domains"  
**Corrected status:** **Science-themed scenarios within one game engine**

**Evidence:**
- All DiscoveryWorld scenarios share the same `DiscoveryWorldAPI`, `World`, `UserInterface` classes
- Action space is identical across scenarios (MOVE_DIRECTION, PICKUP, USE, etc.)
- UI structure is identical
- Scenarios differ in task content and scoring, not in fundamental reasoning patterns

**Impact:** Cross-domain transfer claims require showing that scientific reasoning patterns differ, not just surface themes. This is a methodological limitation.

---

## Updated comparison table

| Criterion | DiscoveryWorld | ScienceAgentBench | SciAgentGYM | MLE-bench |
|-----------|---------------|-------------------|-------------|-----------|
| Runnable | ✅ | ⚠️ | ⚠️ (not tested) | ⚠️ |
| Resettable | ✅ | ❌ | — | — |
| Multi-step | ✅ | ❌ | — | ⚠️ |
| Graded scores | ✅ | ⚠️ | — | — |
| Distinct themes | ✅ | ✅ | — | ❌ |
| **Domain independence** | **⚠️ Shared engine** | **✅ True domains** | — | — |
| Low leakage | ⚠️ | ⚠️ | — | — |
| Reproducible | ✅ | ⚠️ | — | — |
| No API cost | ✅ | ✅ | — | — |

---

## Recommendation update

**Primary: DiscoveryWorld** — Only candidate with verified multi-step loop and graded scoring. Suitable for testing observation-dependent decisions within a single game engine.

**Important caveat:** Cross-domain scientific strategy transfer claims require additional validation that reasoning patterns differ across domains, not just task themes.

**Alternative: SciAgentGYM** (https://github.com/CMarsRover/SciAgentGYM) — Available but untested. Could be investigated in future rounds.
