# Phase 0-D — Falsifiable Evaluation and Pre-registration Protocol (DESIGN)

**Scope:** methodology design only; NO tasks or samples have been generated or scored.

## Candidate target populations and mechanism shifts

- D1 bioinformatics: strong/weak treatment effect, batch confounding yes/no, low/high measurement noise and replicate budgets.
- D2 chemistry: unimodal/multimodal response, noise variance, reagent side-effect constraint, interaction/confounding patterns.
- D3 GIS: anisotropic or isotropic spatial covariance, covariate shift/drift, geographic cluster shift, random versus blocked sampling.

Make all factors explicit via DGP settings hidden from agent. These are proposed task strata for later independent audit, not authorized generated data now.

## Protocol and outcome definition

- Per episode budget: same action budget B for all arms; same permitted tool calls. Separately meter tokens and dollars if model used. Equal clocks/timeouts and restart policies.
- Domain-specific *raw primary science quality*: D1 true-effects discovery FDR and power (or validated score), D2 achieved constrained experimental utility/regret, D3 spatial heldout RMSE and interval coverage.
- Across-domain primary analytic estimand: matched, within-task normalized utility **difference**, paired against no-strategy (not pooled raw scores). Freeze weights and units before target evaluation. Report raw primary quality and cost alongside.
- Arms (future, not yet approved to run):
  A zero strategy, B source-learned conditional strategy, C length-matched placebo, D source-learned local tactic, E mismatched source strategy, F selector with explicit abstention *only after enough source paired labels*. Strong additional comparators: generic static scientific checklist and independently tuned baseline policy. No privileged oracle policies as standard baselines; oracle used only for bounded simulator validation.
- Abstraction tests: raw trace, task lesson, subtask tactic, conditional scientific strategy, matching prompt length and tool rights.
- Evidence-dependency check: replay a genuine observed step with a counterfactual legal observation at same decision state, verify action selection or allocations respond; track effect on final outcome, not just message text.
- Negative transfer: predefined tau on paired utility difference, validated after out-of-sample outcomes; report incidence and uncertainty. A domain-label mismatch is NOT proof of negative transfer.
- Abstention: fallback runs same A policy under same budget; account for extra selection tokens and cost. Report risk-coverage, regret and false-apply/false-abstain frequencies and reliability calibration.

## Data partition and falsifiability

Leave-one-domain-out is proposed (train on 2, target third); with only three families, interpret between-domain variance cautiously. Additionally split scenario generators by **mechanism/template identity**, not just random seed. Freeze unseen target tasks before policy fitting; prevent prompt lookup of hidden reward scripts. Distinct family variants must be accepted before production trials. Never use prior exposed seed IDs 42/43/100/200 as future heldout claims.

Calibration/generator smoke (future first implementation phase) uses unscored-or-dev episodes and *multiple* neutral reference policies to ensure non-degenerate score distribution (not always zero/full) before target hypothesis tests. Do not adjust holdout tasks after seeing B vs A results.

## Statistical analysis plan and sample size

- Prototype **CPU-only environment** first. Do not use paid LLM or A800 resources merely to produce simulator data.
- Unpowered dev smoke: propose up to 12 independent task instances per domain and 3 reference policies, budgeted separately, to detect floors, leaks and hidden mechanism bias. These are proposals pending Planner approval, not run counts.
- Once measurement valid: a separate prospective pilot may consider >=20 independently generated target tasks per target domain, matched arms and multiple seeds. Final sample count requires a *power/precision simulation based on independently estimated variance*; do not treat this example as sufficient significance.
- Primary unit of inference is an independent task template/instance. Repeated stochastic seeds are nested within task; do not miscount them as independent samples. Use within-instance paired deltas with cluster bootstrap at template/family level and hierarchical sensitivity. Report CIs/variance and exact n for each domain.
- Confirm that A/B intervention hash, task IDs, RNG scheme, DGP SHA and evaluator SHA are in an **independent preregistration Git commit before scored trials**; prereg commit SHA must be included in subsequent results and never self-referenced. Run trials only after remote prereg SHA is visible.

## Security / replay controls

- Trusted private generator/evaluator separate from candidate runtime. Only allowlisted public observations to LLM/harness. Set explicit files/network allowlists and dynamic nested canary tests in real loader and tool returns, not synthetic hand-constructed dict.
- Reproducibility: pinned scientific packages, deterministic seed protocol with independent hidden RNG, test scoring of known good/wrong/near/absent answers, blinded change-of-mechanism tests, tamper-evident event traces and scorer hash. No reward branching by strategy ID.
- Distinct data types for official external published-benchmark, simulator ground-truth, hand-authored feasibility and judge-derived results. Never label simulator outputs “original official”.
- Resolve prior schema drift before future result submission: every result must conform to `schemas/result_round.schema.json` or must receive a new versioned design-status schema; current AC-01..06 required fields are incompatible with R3R2 free-form gate payloads. Any schema update needs targeted tests and an explicit migration plan, not silent output rewriting.

## Readiness gates and fail-fast

DESIGN-01: three mechanism designs and causal structures genuinely different, clear physical/stats/verifier references.
DESIGN-02: testbed interface and opponent-neutral deterministic evaluator defined, includes invalid/negative transfer cases without string-based rewards.
DESIGN-03: verifiable source-only strategy learner, control arms and abstention plan, no target gold.
DESIGN-04: preregistration split, metrics, matched budgets, credible uncertainty plan and simulator floor checks.
DESIGN-05: targeted novelty collision matrix and scope-limited external-validity claim.
DESIGN-06: engineering feasibility timeline, smallest CPU viable prototype, bounded experiment/API estimate, dependencies and stop conditions.

No actual Phase1 is authorized until all these DESIGN gates are independently approved and a separate executable implementation plan is issued.
