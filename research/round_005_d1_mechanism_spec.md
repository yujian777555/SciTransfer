# D1 Mathematical Mechanism Specification — Batch-Aware Differential Expression

**Version:** frozen-v1, 2026-10-10  
**Status:** SPECIFICATION FROZEN BEFORE IMPLEMENTATION  
**Scope:** Synthetic expression modeling (NOT validated biological mechanism, NOT GEO reanalysis)

---

## 1. Generative model

### 1.1 Notation

- $g \in \{1, \ldots, G\}$: gene index
- $j \in \{1, \ldots, N\}$: sample index
- $t_j \in \{0, 1\}$: treatment indicator (0=control, 1=treatment)
- $b_j \in \{1, \ldots, B\}$: batch indicator
- $s_j > 0$: sequencing depth / size factor

### 1.2 Negative Binomial observation model

$$Y_{gj} \sim \text{NegativeBinomial}(\mu_{gj}, \phi_g)$$

**Parameterization** (mean-dispersion):
- $E[Y_{gj}] = \mu_{gj}$
- $\text{Var}[Y_{gj}] = \mu_{gj} + \mu_{gj}^2 / \phi_g$
- $\phi_g \sim \text{Gamma}(\alpha_\phi, \beta_\phi)$: gene-specific dispersion

### 1.3 Linear predictor

$$\log \mu_{gj} = \log s_j + \alpha_g + \beta_g \cdot t_j + \gamma_{g,b_j}$$

- $\alpha_g \sim N(\mu_\alpha, \sigma_\alpha^2)$: baseline expression
- $\beta_g \sim \pi_0 \cdot \delta_0 + (1-\pi_0) \cdot N(\mu_\beta, \sigma_\beta^2)$: treatment effect (sparse)
- $\gamma_{g,b} \sim N(0, \sigma_\gamma^2)$: batch effect (gene-specific)

### 1.4 Parameter distributions

| Parameter | Distribution | Default |
|-----------|-------------|---------|
| $G$ | Fixed | 1000 |
| $N$ | Fixed per task | 20–40 |
| $s_j$ | $\text{LogNormal}(0, \sigma_s)$ | $\sigma_s = 0.5$ |
| $\alpha_g$ | $N(5, 1)$ | — |
| $\phi_g$ | $\text{Gamma}(2, 0.5)$ | mean=4 |
| $\pi_0$ | Fixed | 0.8 (20% non-null) |
| $\mu_\beta$ | $N(0, 1)$ or $N(0, 2)$ | mechanism-dependent |
| $\sigma_\gamma$ | Mechanism-dependent | 0 (M1) or 1 (M2) |

---

## 2. Mechanism variants (at least two)

### M1: Unconfounded, homoscedastic
- $\sigma_\gamma = 0$ (no batch effect)
- $\phi_g = \phi_0$ (constant dispersion)
- Treatment randomly assigned within batches

### M2: Partially confounded, heteroscedastic
- $\sigma_\gamma = 1$ (batch effects present)
- $\phi_g \sim \text{Gamma}(2, 0.5)$ (variable dispersion)
- Treatment partially correlated with batch (identifiability check required)

### Identifiability check
Compute design matrix rank for $[\mathbf{1}, \mathbf{t}, \mathbf{B}]$ where $\mathbf{B}$ is batch dummy matrix. **Reject task if rank < 1 + 1 + (B-1)** (perfect confounding). Record rank and overlap diagnostics.

---

## 3. Hidden truth and candidate interface

### Hidden $\theta$ (never accessible to candidate):
- True non-null genes: $\mathcal{G}_1 = \{g : \beta_g \neq 0\}$
- True $\beta_g$ values
- Dispersion $\phi_g$
- Batch effects $\gamma_{g,b}$
- Master seed for reproducibility

### Candidate public interface:
- Task text (describe experiment goal)
- Legal action schema (typed)
- Observations: aggregate statistics (mean, var, QC metrics per group)
- Budget: max samples, max actions

---

## 4. Action types and consequences

| Action | Parameters | Effect | Cost |
|--------|-----------|--------|------|
| `ALLOCATE_REPLICATE` | n_reps, group | Adds samples to group | 1 per sample |
| `MEASURE_QC` | gene_subset | Returns mean/var/CV per group | 1 |
| `ADD_CONTROL` | control_type | Adds negative control genes | 1 |
| `FIT_MODEL` | method | Returns model fit summary | 2 |
| `COMMIT_HITS` | gene_list | Final submission | 0 |

**Invalid actions** fail closed with typed error (not silent default).

---

## 5. Scoring

### 5.1 Metrics

- **FDP** (False Discovery Proportion): $V / \max(R, 1)$
  - $V$ = false positives (reported but truly null)
  - $R$ = total reported
- **Power** (realized): $S / \max(|\mathcal{G}_1|, 1)$
  - $S$ = true positives (reported and truly non-null)
  - $|\mathcal{G}_1|$ = number of true alternatives
- **All-null handling**: If $|\mathcal{G}_1| = 0$, power is undefined; report `null_power`
- **Sample cost**: total samples allocated
- **Declared FDR** vs **realized FDP**: distinguish expected FDR over repeated datasets from single-task FDP

### 5.2 Utility (if scalar needed)

$$U = w_1 \cdot (1 - \text{FDP}) + w_2 \cdot \text{Power} - w_3 \cdot \text{Cost}$$

**Weights frozen before evaluation.** Report raw FDP/power/cost alongside.

### 5.3 Strategy-identity invariance

Score depends ONLY on committed gene list and hidden truth. **No reward branching by strategy ID/name/prompt text.**

---

## 6. Causal DAG

```
Batch (b_j) --> Expression (Y_gj) <-- Treatment (t_j)
                     ^                      |
                     |                      v
              Size Factor (s_j)      True Effect (β_g)
                     ^                      |
                     |                      v
              Depth/Noise              Observed Data
```

**Testable consequence of replication:** Reduces variance of $\hat{\beta}_g$, improving power at fixed FDP.

---

## 7. Pseudorandom protocol

- Master task seed $S_{\text{task}}$ (cryptographic derivation)
- Sample/measurement IDs: $H(S_{\text{task}} \| \text{action\_seq})$
- **Independent RNG streams** per component:
  - $\text{RNG}_{\text{data}}$: expression values
  - $\text{RNG}_{\text{noise}}$: measurement noise
  - $\text{RNG}_{\text{action}}$: action ordering
- Adaptive action order does NOT alter common random conditions for paired comparison
- **Limitation:** When actions request different measurements, paired comparison is imperfect — report honestly

---

## 8. Assumptions

1. This is **synthetic expression modeling**, not a validated biological mechanism
2. Not a reanalysis of GEO or any real dataset
3. NB parameterization is standard but simplified
4. Batch effects are additive on log scale (not multiplicative)
5. Genes are independent (no co-expression structure)
