# Round 004 Experiment Matrix — Design

**Status:** DESIGN ONLY — no tasks generated or scored

---

## 1. Factorial mechanism shifts

| Domain | Factor | Levels | DGP parameter |
|--------|--------|--------|---------------|
| D1 Bio | Treatment effect | Strong/Weak | $\beta$ |
| D1 Bio | Batch confound | Yes/No | $\gamma$ |
| D1 Bio | Noise level | Low/High | $\sigma$ |
| D2 Chem | Response shape | Unimodal/Multimodal | $f(x)$ |
| D2 Chem | Noise variance | Low/High | $\sigma$ |
| D2 Chem | Constraint | Tight/Loose | $c$ |
| D3 GIS | Covariance | Isotropic/Anisotropic | $\ell$ |
| D3 GIS | Covariate shift | Yes/No | $\delta$ |
| D3 GIS | Sampling | Random/Blocked | — |

---

## 2. Source-target splits (LODO)

| Split | Source domains | Target domain |
|-------|---------------|---------------|
| S1 | D1 + D2 | D3 |
| S2 | D1 + D3 | D2 |
| S3 | D2 + D3 | D1 |

**Mechanism-level split:** Within each domain, split by template/mechanism identity (not just seed).

---

## 3. Arms (4+ baselines)

| Arm | Description | Length-matched? |
|-----|-------------|-----------------|
| A | No strategy | — |
| B | Source-learned conditional strategy | — |
| C | Placebo (neutral text) | ✅ |
| D | Source-learned local tactic | — |
| E | Mismatched source strategy | — |
| F | Selector with abstention | — |
| G | Generic scientific checklist | ✅ |
| H | Independently tuned baseline | — |

---

## 4. Outcome metrics

| Metric | Domain | Type |
|--------|--------|------|
| D1 | FDR, Power, Sample cost | Raw science quality |
| D2 | Yield/Selectivity, Regret, Cost | Raw science quality |
| D3 | Spatial RMSE, Coverage, Cost | Raw science quality |
| All | Paired $\Delta$ vs no-strategy | Normalized utility |
| All | Risk-coverage, Regret | Abstention quality |

---

## 5. Statistical plan

| Item | Specification |
|------|--------------|
| Unit of inference | Task template/instance |
| Repeated seeds | Nested within task (not independent) |
| CI method | Cluster bootstrap at template level |
| Sample size | Power simulation from independent variance |
| Floor check | Multiple neutral policies first |
| Preregistration | Independent Git commit before scored trials |

---

## 6. Cost model (formula)

$$\text{Cost}_{\text{total}} = N_{\text{tasks}} \times N_{\text{arms}} \times N_{\text{seeds}} \times (C_{\text{LLM}} \cdot T_{\text{avg}} + C_{\text{compute}})$$

**Assumptions:**
- $C_{\text{LLM}}$: price per token (varies by provider)
- $T_{\text{avg}}$: average tokens per episode
- $C_{\text{compute}}$: CPU time for simulator
- **Zero actual prices claimed** (formula only)

---

## 7. Anti-toy controls

| Threat | Control |
|--------|---------|
| Self-confirming simulator | Outcome independent of strategy ID |
| Identical mechanism | Causal DAG comparison, distinct failure modes |
| Source leakage | Separate process, canary tests |
| Floor effects | Neutral policy smoke first |
| Outcome drift | Raw metrics + normalized utility |
