# Round 004 Engineering Design Spec

**Status:** DESIGN ONLY — no implementation

---

## 1. Directory layout

```
src/scitransfer/
├── simulator/
│   ├── dgp/                    # Data-generating processes
│   │   ├── bio_expression.py   # D1: batch-affected differential expression
│   │   ├── chem_optimization.py # D2: reaction-condition optimization
│   │   └── gis_sampling.py     # D3: spatial sampling
│   ├── engine.py               # State transitions, observations
│   └── evaluator.py            # Trusted scoring (isolated process)
├── strategy/
│   ├── extractor.py            # Source-only strategy extraction
│   ├── selector.py             # Outcome-calibrated abstention
│   └── schema.py               # Strategy type definitions
├── runner/
│   ├── paired.py               # Paired A/B execution
│   └── trace.py                # Immutable event logging
└── cli.py                      # Entry points
```

---

## 2. Interface definitions

```python
# simulator/engine.py
class ExperimentEngine:
    def reset(self, task_id: int, seed: int) -> Observation
    def step(self, action: Action) -> tuple[Observation, float, bool, dict]
    
# strategy/schema.py
@dataclass
class Strategy:
    preconditions: str
    research_action: str
    expected_evidence: str
    adaptation_rule: str
    invalidity_conditions: str
    provenance: Provenance
    cost: CostConstraints

# simulator/evaluator.py (TRUSTED)
class TrustedEvaluator:
    def score(self, y_hat: Artifact, theta: HiddenState) -> ScoreVector
```

---

## 3. Process isolation

| Process | Access | Data |
|---------|--------|------|
| Candidate agent | Public observations, tools | Read-only task input |
| Trusted evaluator | Hidden DGP, scorer | Read-write |
| Strategy extractor | Source trajectories | Read-only |

**Boundary:** Filesystem + network allowlists; nested canary tests.

---

## 4. Deterministic RNG plan

```python
# Independent RNG streams
rng_task = np.random.default_rng(seed * 1000 + 1)    # Task generation
rng_action = np.random.default_rng(seed * 1000 + 2)  # Action ordering
rng_noise = np.random.default_rng(seed * 1000 + 3)   # Observation noise
rng_eval = np.random.default_rng(seed * 1000 + 4)    # Evaluator
```

**Critical:** Adaptive action order must NOT break coupling between arms.

---

## 5. Reuse from SciTransfer

| Component | Reuse? | Notes |
|-----------|--------|-------|
| Trace logging | ✅ | Adapt for simulator |
| Paired runner | ✅ | Extend for multi-arm |
| Budget types | ✅ | Keep |
| DiscoveryWorld adapter | ❌ | Failing environment |
| SciAgentGYM tools | ❌ | Not outcome-grounded |

---

## 6. Smallest offline CPU pilot

| Item | Estimate |
|------|----------|
| DGP implementation | 3 × 200 LOC |
| Engine + evaluator | 400 LOC |
| Strategy extractor | 300 LOC |
| Tests | 500 LOC |
| **Total** | **~2000 LOC** |
| **Time** | **2-3 days** |
| **Cost** | **$0 (CPU only)** |

---

## 7. Real scientific reference (optional)

| Source | License | Risk |
|--------|---------|------|
| GEO datasets (bio) | Public | Low |
| Materials Project (chem) | CC-BY | Low |
| OpenStreetMap (GIS) | ODbL | Low |

**Requirement:** Independent evaluator distinct from simulator.
