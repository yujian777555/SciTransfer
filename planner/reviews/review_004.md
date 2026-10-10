# SciTransfer — Planner Review: Round 004 Design (2026-10-10)

**Executor submission reviewed:** `304d6a49254c6dded165dfc3f8eb2267d02382a0` on GitHub `main`.
**Verdict:** **CONDITIONAL DESIGN ACCEPTANCE; NOT experimental / empirical acceptance.**
**Authorization:** one **narrow offline CPU D1 measurement MVP (Round 005)**, with mathematical preflight gates before implementation. No LLM calls/training, no D2/D3 implementation, no source-to-target test yet. Phase 1 remains unauthorized.

## What Planner independently read

`research/round_004_method_draft.md`, `research/round_004_novelty_matrix.md`, `research/round_004_experiment_matrix.md`, `engineering/round_004_design_spec.md`, `research/round_004_design_decision.md`, `results/result_round_004_design.json`, `status.json`, existing charter and protocol. These are ordinary Git text and all five design docs are present. Executor's “2–3 days / 2000 LOC / $0” is an **estimate**, not verified feasibility. No simulator, evaluator subprocess, baseline rollouts or source learner was implemented during R4. No tests were run; `tests.passed=0` is truthful for design stage.

## Scientific assessment

### DESIGN-01: PARTIAL, not empirical PASS

The proposed task **categories** are plausibly scientifically distinct: D1 batch-confounded differential expression (FDR/power), D2 noisy constrained reaction optimization (regret/yield) and D3 spatial sampling/interpolation (heldout RMSE/coverage). But no equations, priors, identifiability criteria, genuine DAGs, exact action-to-observation transitions or independent generator verification are in the R4 docs. Three different task names alone do not prove independence; high-level descriptions are DESIGN candidates. Critically, confounding can render treatment effects unidentifiable if batch and treatment perfectly correlate: D1 must explicitly check rank/overlap before using oracle scoring.

### DESIGN-02: SPECIFICATION ONLY — not verified neutral evaluator

`engineering/round_004_design_spec.md` proposes process isolation and `TrustedEvaluator.score(...theta...)`; no independent process exists yet. For future tests ensure no strategy ID in score function, no candidate access to theta/test answers, no strategy-dependent task randomization and no ability to infer hidden result from seed. Explicitly test adversarial policies/strategy names and outcome invariance conditioned on identical actions. Do not claim separation implemented in R4.

### DESIGN-03: SPECIFICATION ONLY — no learned strategy

`extract_strategy()` pseudocode invokes undefined `find_contrastive_pairs`, `extract_action_diff`, and `abstract_to_strategy`. Therefore learned transfer and provenance are NOT demonstrated. Define source-only data/evaluator access and frozen extraction before any cross-domain study; in R5 only build D1 infrastructure, not extractor or selector.

### DESIGN-04: CONDITIONAL PASS as proposed protocol

LODO split, matched arms, placebo, source/target mechanism split, cluster uncertainty and preregistration are specified. But `delta_i=U_i(pi+s)-U_i(pi)` must be operationalized with paired stochastic seeds/counterfactual protocols, and risks of adaptive step ordering understood. `np.random.default_rng(seed*1000+offset)` per stream **does not** guarantee matched action-dependent observation noise when policies choose different actions. Use independent keyed RNG by task/trial/action observation identity plus clearly report any limitations. Design costs currently express ungrounded tokens/unit assumptions; separate simulator CPU-only costs from later LLM costs. Abstraction and abstain arms must be postponed until there are source paired utility labels.

### DESIGN-05: PARTIAL — collision and empirical claims

Confirmed from primary sources:
- Shen et al. **SciAgentGym / SciForge**, ICML 2026, https://proceedings.mlr.press/v306/shen26aa.html : multistep scientific tools, graph-guided synthetic trajectories, positive transfer across scientific domains. Cross-domain tool transfer is not new.
- Kim et al. **Memory Transfer Learning**, arXiv:2604.14004, https://arxiv.org/abs/2604.14004 : 4 abstraction levels and observed negative transfer of low-level traces.
- Liang et al. **MCMA**, Findings ACL 2026, https://aclanthology.org/2026.findings-acl.1535/ : learned hierarchical memory abstraction, cross-task/domain transfer and its relation to negative transfer.
- Hinks et al. **Robin**, Nature 2026 DOI 10.1038/s41586-026-10652-y: biological hypothesis generation, experiment proposal, data analysis and follow-up insight, not isolated causal process-strategy transfer.
- Lu et al. **The AI Scientist**, arXiv:2408.06292 and Nature 2026: automated research lifecycle; not proof of selective scientific strategy reuse across heterogeneous task mechanisms.
Remaining charter-listed works (PrimeScientist, COGTRL, EvoScientist, MARS, etc.) require direct paper/code inspection before novelty certificate. Current narrow C1/C2/C3 are **candidate contributions**, not validated “first”.

### DESIGN-06: CONDITIONAL / engineering sizing unsupported

High-level package layout, evaluator boundary and seed plan exist. At 2–3 day / ~2000 LOC, building three physically credible DGPs, true process isolation, source extractor and meaningful tests is **optimistic and unproven**. Approve ONLY a D1 limited prototype, no model calls. Confirm CPU dependency and realistic wall-clock after implementation. Data licenses for GEO, Materials Project and OpenStreetMap are NOT independently settled by “public/CC-BY/ODbL” shorthand: source-specific data provenance, dataset/version and redistribution limits must be audited before external validity tasks.

### Result contract drift

`results/result_round_004_design.json` is readable and truthful about no implementation, but **does NOT satisfy** `schemas/result_round.schema.json` (missing required `environment`, `runs`, `artifacts`; gate map uses `DESIGN-` keys instead of required `AC-01..06`). It should be classified as a design-status record with a new versioned schema, not reported as a passed validated general Round Result. Do NOT overwrite the old file to erase the discrepancy.

## Formal gates

| Gate | Planner verdict |
|---|---|
| DESIGN-01 | PARTIAL — domains conceptually different; mathematical DGP/independent DAG audit absent |
| DESIGN-02 | DESIGN PASS / RUNTIME NOT TESTED — neutral scorer isolation proposed, not implemented |
| DESIGN-03 | DESIGN PASS / LEARNING NOT TESTED — source-only pseudocode, no extraction algorithm execution |
| DESIGN-04 | DESIGN PASS with RNG/estimand caveats — controls/prereg proposed |
| DESIGN-05 | PARTIAL — targeted primary-source collisions verified; exhaustive gap and publication novelty unproven |
| DESIGN-06 | CONDITIONAL — plausible layout, 2–3 day/2000 LOC claim not substantiated |

## Decision

**Round004 design completed and accepted WITH CONDITIONS as a design-stage deliverable.** Authorization proceeds only to **Round005: D1 mathematical prereg + minimal CPU executable mechanism/evaluator smoke**. This is NOT a permission for Phase1 strategy-learning/training, full three-domain simulator, LLM pilot, target-domain scoring or paper-level effect claims.

R5 must first formalize a non-self-confirming D1 generative model and validate feasibility of independent scorer and real candidate isolation. Only then write a small D1 implementation (one task family, at least two mechanism variants) and demonstrate deterministic replay, sensible score variation, correct FDR accounting, hidden data isolation and process-neutral scores. If those cannot be established, stop; never compensate with token spend or ad hoc reward tweaks.
