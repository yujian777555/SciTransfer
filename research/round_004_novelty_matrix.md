# Round 004 Novelty Matrix — Collision Audit

**Date:** 2026-10-10  
**Level:** Targeted source-based preflight  
**Status:** NOT exhaustive systematic review

---

## Direct collisions (DO NOT claim first)

| Work | Citation | Overlap | Defensible gap |
|------|----------|---------|----------------|
| **SciAgentGym/SciForge** | Shen et al., ICML 2026 | Multi-step science tool benchmarking; cross-domain tool-use transfer | Controlled process-strategy interventions with paired outcome scoring |
| **Memory Transfer Learning** | Kim et al., arXiv 2604.14004 | Memory abstraction levels; negative transfer | Outcome-grounded paired interventions (not memory similarity) |
| **MCMA** | ACL Findings 2026 | Hierarchical abstraction selection; cross-domain memory transfer | Selective abstention based on predicted outcome utility |
| **Metacognitive Steering** | arXiv 2609.16245 | Scientific judgment control from traces | Causal identification with matched paired interventions |
| **Co-Scientist** | Nature 2026 | Hypothesis generation + experimental validation | Process strategy transfer (not hypothesis generation) |
| **ResearchClawBench** | arXiv 2606.07591 | 40 real-science tasks across 10 domains | Controlled repeatable interventions + deterministic scoring |
| **ScienceAgentBench** | ICLR 2025 | Scientific code generation benchmark | Multi-step process decisions (not single-shot code) |
| **DiscoveryWorld** | Allen AI | Interactive science environment | Cross-domain strategy transfer testing |

---

## Unverified (charter-listed)

| Work | Status | Action needed |
|------|--------|---------------|
| Robin | UNVERIFIED | Check claims before publication |
| AI Scientist | UNVERIFIED | Check claims |
| PrimeScientist | UNVERIFIED | Check claims |
| COGTRL | UNVERIFIED | Check claims |
| EvoScientist | UNVERIFIED | Check claims |
| MARS | UNVERIFIED | Check claims |

---

## Narrow contribution claims (HYPOTHESIS, not certificate)

**C1:** Causally identifiable cross-domain process interventions using matched source-learned conditional strategy on held-out mechanistically different tasks with immutable external scoring.

**C2:** Outcome-calibrated selective transfer with confidence-aware abstention measured by negative-transfer risk and risk-coverage curves.

**C3:** Scientific-mechanism sensitivity analysis — why strategies help/harm under explicit shifts in noise, confounding, interaction patterns.

---

## Novelty verdict

**CONDITIONAL GO** — narrow contribution possible if:
1. Full related work audit confirms C1/C2/C3 gaps
2. Genuine mechanism diversity across domains is proven
3. External validity bridge is established

**DO NOT claim:** "first", "SOTA", "general scientific discovery"
