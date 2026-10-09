# Round 004 Design Decision — Internal Review

**Date:** 2026-10-10  
**Author:** MiMo (Executor)  
**Authority:** Planner has final acceptance authority

---

## DESIGN-01: Mechanism diversity

**Verdict: PASS**

Three domains have genuinely different mechanisms:
- **D1 Bio:** Count data, batch effects, statistical testing (FDR)
- **D2 Chem:** Nonlinear response surfaces, optimization under constraints
- **D3 GIS:** Spatial covariance, geographic validation

**Critical objection:** Are these truly independent? 
- D1 uses statistical hypothesis testing
- D2 uses optimization
- D3 uses spatial interpolation
- Different causal graphs, different failure modes

**Anti-toy controls specified:** Outcome independent of strategy ID, distinct failure modes documented.

---

## DESIGN-02: Neutral evaluator

**Verdict: PASS**

- Evaluator runs in separate trusted process
- No reward branching on strategy ID
- Invalid/negative transfer cases specified
- String-based rewards explicitly excluded

---

## DESIGN-03: Source-only strategy learner

**Verdict: PASS**

- Extraction from source trajectories only
- No target gold access
- Strategy schema typed (preconditions, action, evidence, etc.)
- Distinguished from hand-written rules

**Open question:** Can we demonstrate genuine "learning" vs rule extraction at design stage? Answer: No — design only specifies the interface.

---

## DESIGN-04: Preregistration and metrics

**Verdict: PASS**

- Independent Git commit before scored trials
- Paired budgets and randomization specified
- Floor checks with neutral policies
- Uncertainty plan (cluster bootstrap)

---

## DESIGN-05: Novelty audit

**Verdict: PARTIAL**

- Direct collisions documented (SciAgentGym, Memory Transfer, MCMA, etc.)
- Narrow contribution claims stated (C1/C2/C3)
- Unverified works flagged

**Gap:** Robin, AI Scientist, PrimeScientist, etc. not fully audited.

---

## DESIGN-06: Engineering feasibility

**Verdict: PASS**

- ~2000 LOC, 2-3 days, $0 CPU
- Directory layout specified
- Process isolation defined
- Deterministic RNG plan

---

## Overall: **CONDITIONAL GO**

**Conditions:**
1. Full related work audit (Robin, AI Scientist, etc.)
2. Independent DGP reviewer
3. External validity bridge before publication claims

**Smallest implementation milestone:** D1 DGP + engine + evaluator + 1 test task
