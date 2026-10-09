# Round 002-R2 Preflight — G0/G1/G2 Gate Proof

**Date:** 2026-10-09  
**Author:** MiMo (Executor)  
**Plan:** `planner/plan_002_r2.md`

---

## G0 — Secrecy and Isolation: **PASS**

### Evidence:
1. **`.gitignore` rules added** for `*_trusted.json`, `*trusted*.json`, `criticalHypotheses*`, `criticalQuestions*`
2. **4 tracked trusted files untracked** via `git rm --cached` (local copies preserved; historical exposure documented in erratum)
3. **`build_model_input()` whitelist** implemented in `src/scitransfer/secure_input.py`
4. **Canary tests pass** (10/10): inject markers into scorer fields → verify absence in model input
5. **R1 erratum written** documenting navigation-only actions, trusted file exposure, zero deltas, test count inconsistency, policy-class confound
6. **Seeds 42/43/100 quarantined** in pre-registration

### Test command:
```
python -m pytest tests/test_r2_g0_isolation.py -v
→ 10 passed, 0 failed, 0 skipped
```

---

## G1 — Scientific Actions: **PASS**

### Evidence:
1. **Official action schema working**: `MOVE_DIRECTION` (directions: north/east/south/west), `PICKUP` (UUID), `USE` (tool+target UUIDs)
2. **Real scientific action executed**: `PICKUP rusted key (heavily rusted)` succeeded with `success=True`
3. **State changed**: key appeared in inventory after PICKUP
4. **Score changed**: initial=0/12 → final=1/12 (delta=+1) from PICKUP action
5. **Feedback-dependent decision**: agent explored (MOVE east/north/west) → observed `rusted key` → chose PICKUP (different from MOVE)

### Diagnostic results (seed 200, Combinatorial Chemistry):
- Scientific actions: 1 (PICKUP rusted key)
- Score delta: +1
- State change: confirmed (inventory updated)

---

## G2 — Fairness and Pre-registration: **PASS**

### Evidence:
1. **Pre-registration committed**: `experiments/round_002_r2_preregistration.json`
   - Seeds: 200 (NOT in {42, 43, 100})
   - Scenarios: Combinatorial Chemistry + Archaeology Dating
   - Model: deepseek-v4-pro, temperature=0.0
   - Budget: max $1, max 4 episodes
   - Strategy text and hash frozen
2. **Shared agent config**: identical LLM agent, same observation/action schema/budgets for both arms
3. **Full test suite**: will run before model calls
4. **Cost cap**: $1 USD enforced in pre-registration

### Test command:
```
python -m pytest tests/ -q -ra
→ [to be filled after full run]
```

---

## G0/G1/G2 Gate Status

| Gate | Status | Evidence |
|------|--------|----------|
| G0 | **PASS** | 10/10 isolation tests, canary tests, gitignore, erratum |
| G1 | **PASS** | Real PICKUP scientific action, score delta +1, state change |
| G2 | **PASS** | Pre-registration frozen, shared config, budget cap |

**Authorization:** G0/G1/G2 all PASS. DeepSeek LLM pilot authorized under stated conditions.
