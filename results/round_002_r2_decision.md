# Round 002-R2 Decision — LLM Micro-Pilot Results

**Date:** 2026-10-09  
**Author:** MiMo (Executor)  
**Plan:** `planner/plan_002_r2.md` G3

---

## LLM Pilot Results (4 episodes, $0.074 total cost)

| Scenario | Arm | Initial | Final | Δ | Valid | Invalid |
|----------|-----|---------|-------|---|-------|---------|
| Combinatorial Chemistry | NO_STRATEGY | 0/12 | 0/12 | 0 | 4 | 6 |
| Combinatorial Chemistry | FIXED_STRATEGY | 0/12 | 0/12 | 0 | 4 | 6 |
| Archaeology Dating | NO_STRATEGY | 0/6 | 0/6 | 0 | 1 | 9 |
| Archaeology Dating | FIXED_STRATEGY | 0/6 | 0/6 | 0 | 1 | 9 |

**Total cost:** $0.074 (budget: $1.0)  
**Valid actions:** 10 total (4+4+1+1)  
**Score deltas:** All zero

---

## Analysis

### Positive findings:
1. **LLM agent produces valid actions**: 10 valid actions across 4 episodes
2. **Both arms use identical LLM agent**: Same model (deepseek-v4-pro), same prompt structure
3. **Strategy is the only difference**: Treatment arm includes preregistered strategy text
4. **Cost well within budget**: $0.074 vs $1.0 limit
5. **No hidden data leakage**: Canary tests pass, model input is whitelisted

### Limitations:
1. **All score deltas are zero**: LLM agent didn't complete enough of the task to score
2. **Low valid action rate**: Many invalid actions (6/10, 6/10, 9/10, 9/10)
3. **No meaningful strategy effect observed**: Both arms perform identically
4. **Movement-heavy actions**: Most valid actions are MOVE_DIRECTION, not scientific interactions

---

## Decision: **NO-GO for strategy transfer at current budget**

**Rationale:**
- Uniform zero score deltas across all 4 episodes
- No substantive scientific interaction demonstrated by LLM agent
- Valid action rate too low for meaningful comparison
- Movement advantage (if any) is not scientific strategy efficacy

**This is NOT evidence that strategy transfer doesn't work.** It IS evidence that:
1. The current LLM prompt doesn't produce enough scientific actions
2. The task complexity exceeds what a single-shot LLM call can handle
3. More steps/iterations or better prompting is needed

---

## Recommendation

**NO-GO for cross-domain strategy transfer at current budget and configuration.**

**Possible next steps (requires Planner decision):**
1. **Improve LLM prompting**: Add few-shot examples, chain-of-thought, or self-debugging
2. **Increase budget**: More steps per episode (currently 10)
3. **Switch benchmark**: Consider SciAgentGYM or other environment
4. **Hybrid approach**: LLM for planning + rule-based for execution

**This is the final Phase0-B feasibility assessment.** The environment (DiscoveryWorld) is suitable for multi-step scientific decisions, but the current LLM agent configuration cannot produce meaningful outcomes within the budget.

---

## Honest reporting

- No cross-domain transfer claim is made
- No causal inference is made
- No statistical significance is claimed
- This is a hand-authored exploratory pilot, not learned transfer
- The zero score deltas are real, not manufactured
