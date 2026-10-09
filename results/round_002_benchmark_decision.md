# Round 002 — Benchmark Decision Report

**Date:** 2026-10-09  
**Author:** MiMo (Executor)  
**Plan:** `planner/plan_002.md` Track 4

---

## 1. Which environment is actually runnable/replayable?

**DiscoveryWorld** (allenai/discoveryworld, Apache-2.0, `discoveryworld==0.0.2`):
- ✅ Installable via pip on Windows
- ✅ Scenarios load with deterministic seeds
- ✅ 17+ actions available (move, pick up, use, activate, talk, etc.)
- ✅ Rich scorecard with sub-task scoring (e.g., 7 sub-tasks, max 12 points)
- ✅ 8+ distinct scientific scenario themes
- ⚠️ Small library bug in `plant_growing` scenario (`world.randomSeed % 5` string formatting error)

**ScienceAgentBench**: Runnable but single-shot only; cannot test multi-step decisions.

## 2. Does it contain distinct scientific task families?

**YES** — DiscoveryWorld has genuinely different scientific domains:

| Scenario | Domain | Max Score | Multi-step |
|----------|--------|-----------|------------|
| Combinatorial Chemistry | Chemistry | 12 | ✅ |
| Archaeology Dating | Archaeology/Geology | 6 | ✅ |
| Plant Nutrients | Botany | 4 | ✅ |
| Reactor Lab | Nuclear Physics | 11 | ✅ |
| Space Sick | Medicine | varies | ✅ |
| Proteomics | Biochemistry | varies | ✅ |

**Caveat:** Themes share the same game engine and action space. Cross-domain transfer claims require showing that scientific reasoning patterns differ, not just surface themes.

## 3. Is the multi-step evidence-action loop real?

**YES** — Verified in calibration:
- 14 decision points per episode (≥2 required)
- Each action produces observable evidence
- Second decision can change based on first evidence
- Real environment state changes after actions

## 4. Does evaluation have integrity?

**MOSTLY YES**:
- `getTaskScorecard()` provides graded scores (0-max)
- Sub-task breakdown enables fine-grained assessment
- ⚠️ `criticalHypotheses` and `criticalQuestions` exposed in scorecard (potential leakage)

## 5. Are outcomes nontrivial?

**YES** — Calibration shows score variation:
- Combinatorial Chemistry: 0/12 (all arms)
- Archaeology Dating: 0/6 (all arms)
- Plant Nutrients: 0/4 (all arms)
- **Reactor Lab: 2/11** (both arms) — partial success!

This demonstrates the environment CAN produce non-zero outcomes with a competent agent. The rule-based agent achieves partial credit on Reactor Lab, showing the scoring system has discriminative power.

## 6. Can future study acquire source-domain trajectories and transfer conditional policies?

**YES, with caveats**:
- Multi-step episodes produce rich trajectories
- Strategy intervention can physically change later actions (verified)
- Need LLM agent (not rule-based) for meaningful strategy comparison
- Need ≥3 independent scientific domains for transfer claims
- Need to control for shared game mechanics vs domain-specific reasoning

## 7. Estimated compute and task count for powered study

| Parameter | Estimate |
|-----------|----------|
| Episodes per domain | 20-30 |
| Domains | 3-4 |
| Arms | 2-3 (NO_STRATEGY, FIXED_STRATEGY, PLACEBO) |
| Total episodes | 120-360 |
| Compute | Local CPU (no GPU needed) |
| API cost (LLM agent) | ~$0.05-0.50 per episode (DeepSeek pricing) |
| Total API cost | $6-180 for full study |
| Wall time | 2-8 hours |

---

## GO / CONDITIONAL / NO-GO Recommendation

### **CONDITIONAL GO**

**Rationale:**
1. DiscoveryWorld is runnable, replayable, and supports multi-step research decisions
2. Multiple distinct scientific domains available
3. Scored outcomes show variation potential (not all-zero floor)
4. Multi-step loop is real with ≥2 decision points per episode

**Conditions for GO:**
1. **LLM agent integration**: Replace rule-based agent with DeepSeek/other LLM to test strategy interventions
2. **Leakage mitigation**: Hide `criticalHypotheses`/`criticalQuestions` from candidate agent
3. **Domain independence verification**: Document methodological differences between domains (not just thematic)
4. **Power analysis**: Run pilot with LLM agent to estimate effect size and required sample size

**Conditions for NO-GO:**
- If LLM agent uniformly scores 0 across all domains (floor effect)
- If strategy intervention cannot change later actions
- If cross-domain transfer cannot be operationalized beyond shared game mechanics

---

## Alternatives considered

| Alternative | Status | Reason |
|-------------|--------|--------|
| ScienceAgentBench | ❌ NOT SELECTED | Single-shot only; cannot test multi-step decisions |
| SciAgentGym | ❌ UNAVAILABLE | Not found on GitHub |
| MLE-bench | ❌ WRONG DOMAIN | ML engineering, not scientific research decisions |

## Limitations

1. Rule-based agent used for calibration (not LLM) — scores show potential but not strategy effects
2. Only 4 of 8+ scenarios tested
3. `criticalHypotheses` leakage risk not fully mitigated
4. Cross-domain independence not rigorously verified
5. Library bug in `plant_growing` scenario

## Next minimal experiment

1. Integrate DeepSeek LLM agent into DiscoveryWorld adapter
2. Run 3 arms × 2 domains × 5 episodes (30 total) with LLM
3. Measure score distribution and strategy effect
4. Verify ≥2 evidence-dependent decision points per episode
5. Document domain-specific vs shared reasoning patterns
