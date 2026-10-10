# Round 006 Experiment Identification — Causal Design

**Status:** DESIGN ONLY

---

## 1. Target estimand

For independent task unit $i$:
$$\Delta_i = \text{RMSE}_i(\text{no strategy}) - \text{RMSE}_i(\text{source strategy})$$

**Sign convention:** Positive $\Delta$ = strategy helps (lower RMSE is better).

---

## 2. Independent task units

| Domain | Unit | Expected n | Status |
|--------|------|-----------|--------|
| Chemistry | Scaffold clusters (Bemis-Murcko) | ~10-20 | TBD |
| Spatial | Region/year blocks | ~5-10 | TBD |

**Critical:** Random seeds on same dataset are NOT independent units.

---

## 3. Frozen splits

| Split | Chemistry | Spatial |
|-------|-----------|---------|
| Train | 60% scaffolds | 60% stations |
| DEV | 20% scaffolds | 20% stations |
| Test | 20% scaffolds (private) | 20% stations (private) |

**Test labels hidden until final submission.**

---

## 4. Arms

| Arm | Description |
|-----|-------------|
| A | No strategy (baseline) |
| B | Source-learned conditional strategy |
| C | Placebo (length-matched neutral) |
| D | Strong domain-default pipeline |
| E | Mismatched strategy (negative transfer control) |

---

## 5. Metrics

| Metric | Chemistry | Spatial |
|--------|-----------|---------|
| Primary | RMSE on test | RMSE on test |
| Secondary | MAE, R² | MAE, spatial coverage |
| Cost | Compute time | Compute time |

---

## 6. Statistical analysis

- Paired deltas per task unit
- Cluster bootstrap at scaffold/region level
- Report CIs and exact n
- **No significance claims with small n**

---

## 7. Negative transfer definition

$$\Delta_i < -\tau \quad \text{(strategy makes things worse)}$$

NOT inferred from "chemistry strategy used on spatial."

---

## 8. External validity layer

**Beyond train/test score:**
- Transfer across molecular families (not just scaffolds)
- Transfer across climate regimes (not just spatial blocks)
- Requires ≥2 genuinely distinct task populations
