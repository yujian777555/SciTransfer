# D1 Corrective Specification — Measurement Integrity Fix

**Version:** corrective-v1, 2026-10-10  
**Status:** FROZEN BEFORE IMPLEMENTATION  
**Supersedes:** Selected parts of `round_005_d1_mechanism_spec.md` (original preserved)

---

## 1. Critical defects identified

| Defect | Impact | Fix |
|--------|--------|-----|
| All actions inert (no data change) | No information gain | Actions must modify observable state |
| Caller sets action cost | Budget exploit | Server-side cost enforcement |
| Truth accessible in same process | No isolation | OS process boundary |
| Empty submission gets 0.4 utility | Incentive exploit | Neutral utility baseline |
| M1 dispersion not constant | Spec mismatch | Fix to `phi_g = phi0` |
| No evidence-dependent decisions | No sequential science | Observation must change next action |

---

## 2. Corrected DGP

### 2.1 M1: Unconfounded, homoscedastic
$$\phi_g = \phi_0 \quad \forall g$$ (constant dispersion)

### 2.2 M2: Partially confounded, heteroscedastic
$$\phi_g \sim \text{Gamma}(\alpha_\phi, \beta_\phi)$$ (gene-specific)

### 2.3 Batch-treatment assignment
- **Within-batch randomization**: treatment randomly assigned within each batch
- **Overlap requirement**: Each batch must have both treated and control samples
- **Identifiability**: Design matrix rank = $1 + 1 + (B-1)$ AND within-batch overlap > 0
- **Reject** tasks failing rank or overlap checks

---

## 3. Sequential observation acquisition

**Initial state:** Only aggregate group sizes and global QC summary. **NO per-gene statistics.**

| Action | Effect | What agent sees | Server cost |
|--------|--------|----------------|-------------|
| `ALLOCATE_REPLICATE(n, group)` | Adds n new samples to group | Updated group size | n × 1 |
| `MEASURE_QC(gene_subset)` | Returns mean/var for requested genes | Subset statistics | 1 per 10 genes |
| `FIT_MODEL(genes)` | Runs t-test on specified genes | p-values for those genes | 2 |
| `COMMIT_HITS(gene_list)` | Terminal submission | Confirmation | 0 |

**REMOVED:** `ADD_CONTROL` (no realistic implementation in scope)

**Key principle:** Each action provides NEW information not available at reset.

---

## 4. Server-side cost enforcement

```python
ACTION_COSTS = {
    "ALLOCATE_REPLICATE": lambda p: p["n_reps"],  # 1 per sample
    "MEASURE_QC": lambda p: max(1, len(p["gene_subset"]) // 10),
    "FIT_MODEL": lambda p: 2,
    "COMMIT_HITS": lambda p: 0,
}
```

- `Action` contains ONLY `action_type` and `parameters` (no cost field)
- Server computes and enforces cost
- Budget check before execution

---

## 5. Valid discovery set semantics

- Gene IDs must be unique integers in $[0, G)$
- Reject: bool, negative, out-of-range, duplicates
- Empty set is valid (no discoveries)
- All-null: `power` is undefined (`null_power=True`)

---

## 6. Neutral utility (corrected)

**Problem:** Empty submission with cost=0 gets $w_1 \times (1-0) = 0.4$.

**Fix:** Use **regret-based utility** with explicit baseline:
$$U = \frac{\text{Power} - \text{FDP}}{\max(\text{Cost}, 1)}$$

- Empty submission: $U = 0$ (no power, no FDP, but also no discovery)
- Perfect: $U = 1/C$ (high power, no FDP)
- All-null: $U = 0$ (undefined power)

**Alternative (if simpler):** Report vector `(FDP, Power, Cost)` only. No scalar utility.

---

## 7. OS process boundary

```
[Candidate Process]          [Trusted Process]
- Public loader              - DGP generator
- Action execution           - Hidden truth
- Observation display        - Scorer
- Artifact submission        - Evaluation
```

- Candidate CANNOT import `HiddenTruth` or access `engine.truth`
- Filesystem: candidate can read `benchmark/datasets/` only
- Canary test: inject marker into hidden truth, verify absent in candidate view

---

## 8. RNG protocol (corrected)

- Private master seed (never exposed to candidate)
- Component keys: `SHA256(master_seed:task_key:component)`
- **Keyed by sample identity**: noise for sample $j$ is `RNG(master_seed, task_key, sample_id)`
- Adaptive action order does NOT alter noise for already-measured samples

---

## 9. Scoring (pure function)

```python
def score(reported: set[int], truth: set[int], cost: int) -> ScoreResult:
    R = len(reported)  # unique
    S = len(reported & truth)
    V = R - S
    fdp = V / max(R, 1)
    power = S / len(truth) if truth else None
    return ScoreResult(fdp=fdp, power=power, cost=cost, ...)
```

**No strategy ID parameter. Identical inputs → identical outputs.**
