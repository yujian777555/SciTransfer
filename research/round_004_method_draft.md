# Round 004 Method Draft — Outcome-Calibrated Scientific Strategy Transfer

**Version:** design-v1, 2026-10-10  
**Status:** PROPOSAL / NOT IMPLEMENTED / NOT VALIDATED  
**Authority:** `planner/PROJECT_CHARTER.md` (unchanged)

---

## 1. Problem formalism

### 1.1 Source trajectories

Let $D_s = \{(x_i^s, a_{i,1:T}^s, o_{i,1:T}^s, U_i^s)\}$ be source-domain trajectories where:
- $x_i^s$ = public task instance
- $a_{i,t}^s$ = action at step $t$ (typed scientific intervention)
- $o_{i,t}^s$ = observation/evidence returned
- $U_i^s$ = outcome-grounded utility score

### 1.2 Conditional abstract strategy

A strategy $s$ is a typed tuple:
```
s = (preconditions, research_action, expected_evidence, 
     adaptation_rule, invalidity_conditions, provenance, cost)
```

**NOT** a tool name or fixed prompt text. Must be extracted from source trajectories only.

### 1.3 Outcome-grounded paired interventions

For task $i$ in target domain $d_t$:
$$\Delta_i(s) = U_i(\pi + s) - U_i(\pi_{\text{no-strategy}})$$

where $\pi$ is the base agent policy, same model/tools/budget for both arms.

### 1.4 Selective risk-aware abstention

Selector $g(s, \text{context})$ predicts distribution of $\Delta$. Transfer only if:
$$\text{LCB}_{q}[\hat{\Delta}] > \tau_{\text{risk}}$$

Otherwise abstain (use $\pi_{\text{no-strategy}}$).

---

## 2. Source-only strategy extraction (pseudocode)

```python
def extract_strategy(source_trajectories, source_tasks):
    """Extract conditional strategies from source domain only."""
    # 1. Identify successful vs unsuccessful pairs
    pairs = find_contrastive_pairs(source_trajectories)
    
    # 2. Generate candidate strategies
    candidates = []
    for success, failure in pairs:
        diff = extract_action_diff(success, failure)
        candidate = abstract_to_strategy(diff)
        candidates.append(candidate)
    
    # 3. Validate on source DEV tasks
    validated = []
    for c in candidates:
        if validate_on_source(c, source_tasks):
            validated.append(c)
    
    # 4. Freeze before transfer
    return freeze_strategies(validated)
```

**Constraints:**
- No access to target hidden states or gold
- No LLM training at design stage
- Provenance: source domain, extraction algorithm version

---

## 3. Algorithm constraints

| Constraint | Specification |
|------------|--------------|
| Base agent | Same LLM/model for all arms |
| Tools | Same legal action schema for all arms |
| Budget | Same max steps, tokens, cost per arm |
| Initial state | Same public task instance |
| Strategy | Only difference between arms |
| Placebo | Length-matched neutral context |

---

## 4. Information boundary

| Component | Access |
|-----------|--------|
| Candidate agent | Public task, tools, observations only |
| Trusted evaluator | Hidden DGP $\theta$, held-out noise, scorer |
| Strategy extractor | Source trajectories only |

**Critical:** Candidate cannot see $\theta$, hidden targets, reward code, or target templates.

---

## 5. Complexity

| Operation | Complexity |
|-----------|------------|
| Strategy extraction | $O(|D_s| \cdot T)$ |
| Paired evaluation | $O(|D_t| \cdot |S| \cdot T)$ |
| Selector calibration | $O(|D_s|^2)$ (if using kernel methods) |

---

## 6. What this is NOT

- NOT a learned policy (strategies extracted, not trained)
- NOT a real-science claim (controlled simulator only)
- NOT novel in general (see novelty matrix)
- NOT validated (zero experimental results)
