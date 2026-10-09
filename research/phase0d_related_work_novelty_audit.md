# Phase 0-D — Related Work, Collision Risks and Proposed Contribution Boundary

**Date checked:** 2026-10-10. **Level:** targeted source-based preflight, NOT exhaustive systematic review. Full bibliographic/claim verification is a separate Executor deliverable before implementing/publishing.

## Direct collisions — do NOT claim first

1. **SciAgentGym/SciForge**, Shen et al., ICML 2026: multistep science tool benchmarking and dependency-graph action trajectory training; paper explicitly discusses cross-domain transfer of tool-use. This means “cross-domain scientific agent tool-use transfer” is NOT novel. https://proceedings.mlr.press/v306/shen26aa.html
2. **Memory Transfer Learning**, Kim et al., arXiv 2604.14004 (April 2026): heterogeneous coding agents, four memory abstraction levels, mean uplift and negative transfer of specific low-level traces. Therefore neither “abstract memories transfer better” nor “negative transfer exists” is novel. https://arxiv.org/abs/2604.14004
3. **MCMA: Learning How to Remember**, ACL Findings 2026: hierarchical abstraction selection and transfer of a memory-management copilot across ALFWorld, ScienceWorld, BabyAI. Do not claim invention of abstraction-controlled memory. https://aclanthology.org/2026.findings-acl.1535/
4. **Metacognitive Steering**, arXiv 2609.16245: learns dynamic scientific judgment control from interaction traces, explores process-level exploration/reassessment control. Do not claim first to learn scientific process-control regimes. https://arxiv.org/abs/2609.16245
5. **Co-Scientist**, Nature 2026: structured AI scientific hypothesis generation and critique with experimental validation; differentiated by outcome-grounded paired *process strategy transfer*, not generic science autonomy. https://doi.org/10.1038/s41586-026-10644-y
6. **ResearchClawBench**, arXiv 2606.07591: 40 real-science re-discovery tasks across 10 scientific domains, primarily rubric/judge evaluation. Differentiator, if established, is controlled repeatable scientific-process interventions and deterministic objective score, not first science evaluation. https://arxiv.org/abs/2606.07591
7. **Prior project charter requires further inspection:** Robin, AI Scientist, PrimeScientist, COGTRL, EvoScientist, MARS, ScienceAgentBench, DiscoveryWorld. These references were not independently exhaustively checked in THIS preflight. Executor must add accurate citations and identify overlap/no-overlap rather than making unsupported summaries.

## Plausible narrow scientific contribution — HYPOTHESIS, NOT NOVELTY CERTIFICATE

C1. **Causally identifiable cross-domain process interventions** using matched source-learned conditional strategy on held-out mechanistically different science tasks with immutable external outcome scoring, rather than trajectory-memorization similarity or a single raw prompt improvement.
C2. **Outcome-calibrated selective transfer**: confidence-aware abstention measured by negative-transfer risk, risk–coverage curves and paired task utility, benchmark leakage controlled.
C3. **Scientific-mechanism sensitivity analysis**: test why strategies help or harm under explicit shifts in noise, confounding, interaction and covariate/spatial dependence across scientifically different simulators; derive failure boundaries rather than claim universal transfer.

C1/C2/C3 must be compared to nearest baselines. All are subject to being unoriginal or not effective once full related work is audited. Avoid “first”, “SOTA”, “general scientific discovery” without new source-supported evidence.

## Major validity threats and falsification tests

- **Self-confirming toy simulator:** DGP rewards the proposed rule because author hardcoded it. Mitigation: outcome function independent of strategy ID, adversarial perturbations, baseline algorithms, independent DGP reviewer, and optional real-data external test.
- **Identical latent mechanism reskinned:** 3 domains share same bandit process; cross-domain transfer becomes cosmetic. Mitigation: causal diagrams, tool/measurement structures and distinct failure modes, true leave-one-domain-out.
- **Source leakage / oracle privilege:** candidate sees hidden DGP config or target labels. Mitigation: separate process, allowlists, nested canaries, audit filesystem/network/provenance.
- **Convenience of conditional rule instead of learned policy:** hand-written if-then heuristics not learned from source. Mitigation: provenance-traceable source-only extraction and a strong equal-budget manually designed comparator.
- **Outcome drift:** task-local normalized scores disguise raw effect and unequal cost. Mitigation: raw metrics, separate utility penalties, paired differences and uncertainty.
- **Selective overfitting to heldout shift:** tuning abstention on test domains. Mitigation: nested source/DEV/test split; independently committed preregistration before opening target run outputs.
- **Algorithm vs environment co-design:** policy and reward tuned together. Mitigation: frozen engine commit ahead of policy design, blinded condition family tests, alternative baselines, independent verification.
- **Simulator to real-science jump:** publication claim too broad. Mitigation: precise scope statement and small authentic scientific reference layer if feasible.

## Feasibility decision now

**RECOMMEND DESIGN-GO only** for a separate Phase0D controlled measurement specification. This preflight DOES NOT authorize executing simulations, calling models or fitting a utility gate. Scientific publication feasibility remains conditional on independent reward validity, genuine source strategy acquisition, non-floor outcome signal and at least one external reference evaluation.
