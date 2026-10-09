# SciTransfer Transfer Experiment Protocol — Round 003 Design

**Date:** 2026-10-09  
**Author:** MiMo (Executor)  
**Plan:** `planner/plan_003.md` Track C  
**Status:** DESIGN ONLY — no scored target runs in this round

---

## 1. Scientific hypothesis

**Central question:** Can process-level scientific research strategies learned in one domain causally improve research outcomes in another domain, and can an agent abstain when transfer is predicted to be harmful?

**Falsifiable predictions:**
1. **H1 (Transfer):** A strategy learned from source domain A improves outcomes on held-out target domain B compared to no-strategy baseline
2. **H2 (Negative transfer):** A strategy from domain A degrades outcomes on domain C (mismatched domain)
3. **H3 (Abstention):** An agent that abstains when transfer is predicted harmful outperforms ungated transfer

---

## 2. Source-target split

### Source domains (for strategy learning):
- **Chemistry**: Experimental design, compound identification, reaction optimization
- **Physics**: Measurement, hypothesis testing, model validation

### Target domains (for transfer evaluation):
- **Materials Science**: Crystallography, spectroscopy analysis
- **Life Science**: Structural biology, mass spectrometry

### Held-out (for negative transfer):
- **Astronomy**: Observation planning, data analysis

### Isolation requirements:
- Task templates disjoint between source and target
- Hidden solutions separated (source solutions never in target context)
- Tool sets may overlap but task objectives differ

---

## 3. Strategy representation

Extracted from **source domain traces**, not from hidden gold:

```json
{
  "id": "strategy_v1",
  "source_domain": "chemistry",
  "preconditions": "When facing an unknown compound identification task",
  "research_action": "First measure physical properties (melting point, solubility), then run spectroscopy, then compare against reference database",
  "expected_evidence": "Consistent physical properties + matching spectral peaks + database hit",
  "invalidity_conditions": "If physical properties contradict spectral data, re-measure",
  "cost_constraints": "Use cheapest discriminating measurement first"
}
```

---

## 4. Experimental arms

### Arm A: No strategy (baseline)
- Task description + observation only
- Same agent, model, tools, budget

### Arm B: Source-learned conditional strategy
- Task description + observation + strategy from source domain
- Same agent, model, tools, budget

### Arm C: Length-matched placebo (optional)
- Task description + observation + neutral text of same length as strategy
- Controls for prompt length effects

### Arm D: Abstention gate (when labels exist)
- Strategy + abstention rule: "If strategy predicts harm, abstain"
- Requires utility predictor (Phase 2 only)

---

## 5. Outcome measurement

### Task-local scientific process verifier:
- Did the agent take meaningful scientific actions? (not just movement)
- Did the agent observe consequences and adjust?
- Did the agent perform measurement/hypothesis testing?

### Official outcome verifier:
- Final score from trusted evaluator (not visible to agent)
- Score delta (initial → final)
- Normalized within-scenario score

### Evidence chain:
```
action → observable_feedback → revised_decision → final_outcome
```

---

## 6. Preregistration protocol

### Before any scored target runs:
1. **Independent commit** of experiment plan + config + hashes
2. **UTC timestamp** (verified, not backdated)
3. **Frozen strategy text** + SHA256
4. **Frozen task IDs** + seeds (NOT in {42, 43, 100, 200})
5. **Frozen model params** + budget limits
6. **Stopping rules** declared

### Registration file:
```json
{
  "registration_id": "round_XXX_prereg",
  "timestamp_utc": "YYYY-MM-DDTHH:MM:SSZ",
  "git_commit": "<commit_SHA>",
  "source_domains": ["chemistry", "physics"],
  "target_domains": ["materials_science", "life_science"],
  "heldout_domains": ["astronomy"],
  "strategy_text_hash": "<sha256>",
  "task_ids": [...],
  "seeds": [...],
  "model_config": {...},
  "budget": {...},
  "stopping_rules": [...]
}
```

---

## 7. Negative transfer detection

### Mismatched strategy control:
- Apply chemistry strategy to astronomy task (mismatched)
- Compare to no-strategy baseline
- If mismatched < baseline → negative transfer detected

### Abstention gate:
- Train utility predictor on source data (Phase 2)
- Predict transfer utility for target
- If predicted utility < threshold → abstain
- Compare to ungated transfer

---

## 8. Feasibility thresholds

### Floor effects:
- If all arms score 0 → task too hard, redesign
- If all arms score max → task too easy, redesign

### Ceiling effects:
- If strategy arm scores max → no headroom for improvement
- Need harder tasks or more fine-grained scoring

### Minimum sample:
- ≥3 domains for cross-domain claims
- ≥5 episodes per arm per domain (not powered, but exploratory)
- ≥1 matched pair with score difference

---

## 9. Stopping rules

1. **Stop if**: No score variation after 10 episodes per arm
2. **Stop if**: Cost exceeds budget
3. **Stop if**: Hidden answer leakage detected
4. **Stop if**: Tool execution unreliable (>50% failures)

---

## 10. What this protocol does NOT claim

- NOT a learned policy (strategies are hand-authored or extracted from source traces)
- NOT statistical significance (sample too small)
- NOT causal proof (without proper controls)
- NOT cross-domain generalization (unless 3+ domains tested)

---

## 11. Next steps (requires Planner authorization)

1. Verify SciAgentGYM installation (or use DiscoveryWorld with improved prompting)
2. Implement source-domain strategy extraction
3. Pre-register experiment (independent commit)
4. Run pilot: 2 domains × 2 arms × 5 episodes
5. Analyze score variation and strategy effect
6. Report GO / CONDITIONAL / NO-GO
