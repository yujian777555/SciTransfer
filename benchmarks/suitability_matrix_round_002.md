# Benchmark Suitability Matrix — Round 002

**Date:** 2026-10-09  
**Purpose:** Evaluate candidate scientific decision environments for Phase 0-B feasibility gate (plan_002.md Track 1).

## Evaluation Criteria

| Criterion | Description |
|-----------|-------------|
| **Runnable** | Can be installed and executed on current infrastructure |
| **Resettable** | Supports scenario reset with seed for reproducibility |
| **Multi-step actions** | Agent can observe → decide → act → receive evidence → decide again |
| **Scored reward** | Authentic evaluator with graded outcomes (not just 0/1) |
| **Distinct disciplines** | ≥3 genuinely distinct scientific domains (not just task variations) |
| **Low leakage** | Hidden answers not accessible to candidate programs |
| **Reproducibility** | Deterministic with seed, version-pinned |
| **Cost** | Local compute, no paid API required for environment |
| **Negative transfer measurable** | Can detect when strategy hurts performance |

---

## Candidate 1: DiscoveryWorld (allenai/discoveryworld)

**Source:** https://github.com/allenai/discoveryworld  
**License:** Apache-2.0  
**Stars:** 225 (active development, updated 2026-10-09)  
**Package:** `discoveryworld==0.0.2` (installed successfully via pip)

### Observed (tested on this machine)

| Criterion | Status | Evidence |
|-----------|--------|----------|
| **Runnable** | ✅ YES | `pip install discoveryworld` succeeded. Import OK. |
| **Resettable** | ✅ YES | `loadScenario(name, difficulty, seed, numAgents)` with `randomSeed` parameter |
| **Multi-step actions** | ✅ YES | 17 actions (move, pick up, use, activate, talk, etc.). Observation → Action → Evidence loop |
| **Scored reward** | ✅ YES | `getTaskScorecard()` returns detailed sub-task scores (e.g., 7 tasks, max 12 points for Combinatorial Chemistry) |
| **Distinct disciplines** | ✅ YES | Combinatorial Chemistry, Archaeology, Plant Nutrients, Reactor Lab, Space Sick, Proteomics, Rocket Science, Translation — genuinely different scientific fields |
| **Low leakage** | ⚠️ PARTIAL | Task scoring is server-side; but `criticalHypotheses` and `criticalQuestions` are exposed in scorecard |
| **Reproducibility** | ✅ YES | Seed-based scenario generation |
| **Cost** | ✅ $0 | Local Python package, no API required for environment |
| **Negative transfer measurable** | ✅ YES | Graded scores (0-12) allow detecting performance differences |

### Scenario examples (scientific domains)

| Scenario | Scientific Domain | Difficulty levels | Max Score |
|----------|------------------|-------------------|-----------|
| Combinatorial Chemistry | Chemistry / Materials | Easy/Normal/Challenge | 12 |
| Archaeology Dating | Archaeology / Geology | Easy/Normal/Challenge | varies |
| Plant Nutrients | Botany / Agriculture | Easy/Normal/Challenge | varies |
| Reactor Lab | Nuclear Physics | Easy/Normal/Challenge | varies |
| Space Sick | Medicine / Space Science | Easy/Normal/Challenge | varies |
| Proteomics | Biochemistry | Easy/Normal/Challenge | varies |
| It's (not) Rocket Science! | Aerospace Engineering | Easy/Normal/Challenge | varies |
| Lost in Translation | Linguistics / Archaeology | Easy/Normal/Challenge | varies |

### Verified test result (Combinatorial Chemistry, Easy, seed=42)

```
Loaded OK, steps=0, complete=False
Scorecard: 7 sub-tasks, max 12 points
Actions: 17
Observation: {errors, ui, vision}
Critical hypotheses: "If the key is placed in a mixture of pure Substance C, then the rust will be removed."
```

---

## Candidate 2: ScienceAgentBench (OSU-NLP-Group/ScienceAgentBench)

**Source:** https://github.com/OSU-NLP-Group/ScienceAgentBench  
**License:** MIT (code), CC-BY-4.0 (data)  
**Stars:** 175  
**Status:** Already integrated in Round 001

### Observed (from Round 001/R2/R3 experience)

| Criterion | Status | Evidence |
|-----------|--------|----------|
| **Runnable** | ⚠️ PARTIAL | ZIP downloaded & extracted; Docker evaluator blocked by network; direct scorer works |
| **Resettable** | ❌ NO | One-shot code generation; no reset/replay loop |
| **Multi-step actions** | ❌ NO | Single-shot: prompt → generated code → evaluate. No observe→act→observe loop |
| **Scored reward** | ✅ YES | Official evaluators (0/1 per task, some with tolerance) |
| **Distinct disciplines** | ✅ YES | Bioinformatics, Chemistry, GIS, Psychology (4 domains) |
| **Low leakage** | ⚠️ PARTIAL | Gold in protected ZIP; but junction exposed gold (R3 defect) |
| **Reproducibility** | ⚠️ PARTIAL | Parquet pinned; but agent model is stochastic |
| **Cost** | ✅ $0 | Local evaluation after setup |
| **Negative transfer measurable** | ⚠️ PARTIAL | Binary 0/1 scores; floor effects observed |

### Limitations for this research

- **Single-shot**: Cannot test multi-step research decisions (observe → decide → act → revise)
- **Floor effects**: All evaluated tasks scored 0 (R3) — no discriminative power
- **No interactive loop**: Generated code runs once; no feedback/iteration
- **Timeout issues**: GIS tasks too slow for practical evaluation

---

## Candidate 3: SciAgentGym

**Status:** ❌ NOT AVAILABLE  
**Evidence:** GitHub search returns 404 for `OSU-NLP-Group/SciAgentGym` and `scagentgym/SciAgentGym`  
**Decision:** Cannot evaluate without source access.

---

## Candidate 4: MLE-bench (OpenAI)

**Source:** https://github.com/OpenAI/mle-bench  
**License:** NOASSERTION  
**Stars:** 1,769

### Assessment

| Criterion | Status | Notes |
|-----------|--------|-------|
| **Runnable** | ⚠️ UNTESTED | Not tested this round |
| **Multi-step** | ⚠️ PARTIAL | ML engineering tasks with multiple steps, but not "scientific research decisions" |
| **Distinct disciplines** | ❌ NO | All ML/AI engineering, not distinct science domains |
| **Scientific decisions** | ❌ NO | Focused on ML pipeline optimization, not hypothesis testing |

**Decision:** Not suitable for cross-domain scientific strategy transfer research.

---

## Summary Comparison

| Criterion | DiscoveryWorld | ScienceAgentBench | SciAgentGym | MLE-bench |
|-----------|---------------|-------------------|-------------|-----------|
| Runnable | ✅ | ⚠️ | ❌ | ⚠️ |
| Resettable | ✅ | ❌ | — | — |
| Multi-step | ✅ | ❌ | — | ⚠️ |
| Graded scores | ✅ | ⚠️ | — | — |
| 3+ disciplines | ✅ | ✅ | — | ❌ |
| Low leakage | ⚠️ | ⚠️ | — | — |
| Reproducible | ✅ | ⚠️ | — | — |
| No API cost | ✅ | ✅ | — | — |
| Neg. transfer | ✅ | ⚠️ | — | — |

---

## Recommendation

**Primary: DiscoveryWorld** — Only candidate that supports genuine multi-step scientific research decisions with graded scoring across distinct scientific disciplines. Installable and testable on current infrastructure.

**Secondary reference: ScienceAgentBench** — Useful for single-shot code generation comparison, but cannot test multi-step strategy transfer.

**Not recommended:** MLE-bench (wrong domain), SciAgentGym (unavailable).

### Cross-domain transfer feasibility note

DiscoveryWorld's scenarios represent distinct scientific domains (chemistry, archaeology, botany, physics, medicine, biochemistry, aerospace, linguistics). However, **different themes within DiscoveryWorld are NOT automatically independent scientific disciplines** — they share the same game engine, action space, and UI conventions. For rigorous cross-domain transfer claims, we would need to:
1. Document the scientific methodological differences between domains (not just thematic)
2. Show that strategy rules learned in one domain apply to genuinely different reasoning patterns in another
3. Control for shared game mechanics (movement, pick up, use) vs domain-specific reasoning

This is a **feasibility** assessment only, not a claim of transfer validity.
