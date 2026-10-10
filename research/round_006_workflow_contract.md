# Round 006 Workflow Contract — Real Analysis Sequential Decisions

**Status:** DESIGN ONLY — no implementation

---

## 1. Chemistry (ESOL) action grammar

| Action | Effect | Observation | Cost |
|--------|--------|-------------|------|
| `STANDARDIZE_SMILES` | Canonicalize molecular structures | Canonical SMILES, duplicates removed | 1 |
| `COMPUTE_DESCRIPTORS` | Calculate RDKit descriptors | Descriptor matrix (train only) | 2 |
| `INSPECT_SCAFFOLDS` | Group by Bemis-Murcko scaffold | Scaffold size distribution | 1 |
| `FIT_MODEL(method)` | Train Ridge/RF on train split | DEV RMSE/MAE | 2 |
| `INSPECT_RESIDUALS` | Examine DEV prediction errors | Residual summary (DEV only) | 1 |
| `COMPARE_SPLITS` | Random vs scaffold split comparison | Both DEV metrics | 2 |
| `COMMIT_PREDICTIONS` | Submit final test predictions | Confirmation | 0 |

**Key constraint:** Only DEV labels visible during selection. Test labels hidden until final scoring.

---

## 2. Spatial (NOAA GHCN) action grammar

| Action | Effect | Observation | Cost |
|--------|--------|-------------|------|
| `FILTER_QC_FLAGS` | Remove low-quality measurements | Clean station set, sample count | 1 |
| `AGGREGATE_TEMPORAL` | Daily → weekly/monthly | Aggregated series | 1 |
| `SELECT_REGION` | Define spatial extent | Station map summary | 1 |
| `INSPECT_SPATIAL_AUTOCORRELATION` | Moran's I, variogram | Spatial structure metrics | 2 |
| `FIT_INTERPOLATOR(method)` | IDW/Kriging/mean on train | DEV RMSE on blocked holdout | 2 |
| `INSPECT_RESIDUALS` | Spatial residual patterns | Residual map summary (DEV) | 1 |
| `COMPARE_SPLITS` | Random vs spatial block | Both DEV metrics | 2 |
| `COMMIT_PREDICTIONS` | Submit final test predictions | Confirmation | 0 |

---

## 3. Shared conditional process strategy (source-extracted)

```
preconditions: "When selecting a validation procedure for model comparison"
research_action: "First compare leakage-resistant grouped split vs random split; 
                  if grouped split shows substantially worse performance, 
                  use grouped split for model selection"
expected_evidence: "DEV metric under grouped split differs materially from random split"
adaptation_rule: "If grouped split is much worse, investigate group structure 
                  before trusting model; if similar, random split may suffice"
invalidity_conditions: "If no natural grouping exists, skip grouping check"
provenance: "Extracted from source-domain analysis trajectories"
```

**CRITICAL:** This is a PROCESS strategy (how to validate), NOT a domain-specific tool call.

---

## 4. Candidate vs Trusted separation

| Component | Access | Data |
|-----------|--------|------|
| Candidate agent | Train + DEV labels | Public tools |
| Trusted scorer | Test labels | Private |

**Network:** Candidate blocked from fetching test labels.
**Filesystem:** Test labels in separate unmounted directory.

---

## 5. Evidence-dependence requirement

At the **same decision state**, changing one observable (e.g., DEV residual pattern) must change the next legal action. NOT step-counter-based.

---

## 6. What this is NOT

- NOT new chemical synthesis (retrospective analysis only)
- NOT new weather observation (existing data only)
- NOT a novel method (standard leakage-safe validation)
